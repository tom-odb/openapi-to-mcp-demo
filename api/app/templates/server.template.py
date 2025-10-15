"""
Generic MCP Server that reads tool definitions from a tools.json file.
Supports both standard tools and composite tools.
Composite tools use MCP client to orchestrate calls to standard tools.
"""
import asyncio
import httpx
import json
import logging
import os
import sys
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, LoggingLevel
from typing import Dict, Any, List, Optional
from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv
from contextvars import ContextVar

# Configure logging to use stderr (stdout is reserved for MCP JSON-RPC)
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Context variable to store the current request context
_request_context: ContextVar[Optional[Any]] = ContextVar('request_context', default=None)

load_dotenv()

class GenericMCPServer:
    def __init__(self, tools_config_path: str):
        """Initialize server with tools configuration"""
        logger.info(f"Loading tools config from: {tools_config_path}")
        self.config = self._load_config(tools_config_path)
        self.api_name = self.config.get("api_name", "api")
        self.base_url = self.config.get("base_url", "")
        self.tools = self.config.get("tools", [])
        self.composite_tools = self.config.get("composite_tools", [])
        self.api_key = os.getenv("API_KEY", "")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.progress_messages = []  # Store progress messages to include in result
        
        logger.info(f"Starting server for API: {self.api_name}")
        logger.info(f"Base URL: {self.base_url}")
        logger.info(f"Standard tools: {len(self.tools)} | Composite tools: {len(self.composite_tools)}")
            
        if self.anthropic_api_key and len(self.composite_tools) > 0:
            logger.info("ANTHROPIC_API_KEY is configured - composite tools enabled")
        elif len(self.composite_tools) > 0:
            logger.warning("Composite tools found but ANTHROPIC_API_KEY not set - they may not work correctly")
            
        self.app = Server(f"{self.api_name}-mcp-server")
        self._register_handlers()
        logger.info("Server initialization complete")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load tools configuration from JSON file"""
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def _register_handlers(self):
        """Register MCP handlers"""
        
        @self.app.list_tools()
        async def list_tools() -> List[Tool]:
            """List all available tools"""
            mcp_tools = []
            
            # Add standard tools
            for tool in self.tools:
                mcp_tools.append(Tool(
                    name=tool["name"],
                    description=tool["description"],
                    inputSchema=tool["input_schema"]
                ))
            
            # Add composite tools
            for tool in self.composite_tools:
                mcp_tools.append(Tool(
                    name=tool["name"],
                    description=tool["description"],
                    inputSchema=tool["input_schema"]
                ))
            
            return mcp_tools
        
        @self.app.call_tool()
        async def call_tool(name: str, arguments: dict, request_context: Any = None) -> List[TextContent]:
            """Execute a tool by making API request(s)"""
            
            # Store request context for logging and attach progress messages list
            if request_context:
                request_context.progress_messages = []
            _request_context.set(request_context)
            
            # Check if it's a standard tool
            for tool in self.tools:
                if tool["name"] == name:
                    return await self._handle_standard_tool(tool, arguments)
            
            # Check if it's a composite tool
            for tool in self.composite_tools:
                if tool["name"] == name:
                    return await self._handle_composite_tool(tool, arguments)
            
            raise ValueError(f"Unknown tool: {name}")
    
    async def _send_progress(self, message: str, level: str = "info"):
        """Store progress message and send log notification to MCP client"""
        # Store the message for inclusion in the final result
        ctx = _request_context.get()
        if ctx and hasattr(ctx, 'progress_messages'):
            ctx.progress_messages.append(message)
        
        # Also try to send as log message (for debugging/console output)
        if ctx and hasattr(ctx, 'session'):
            try:
                # Map string level to LoggingLevel enum
                log_level = {
                    "debug": LoggingLevel.DEBUG,
                    "info": LoggingLevel.INFO,
                    "warning": LoggingLevel.WARNING,
                    "error": LoggingLevel.ERROR
                }.get(level.lower(), LoggingLevel.INFO)
                
                await ctx.session.send_log_message(
                    level=log_level,
                    data=message
                )
            except Exception as e:
                logger.debug(f"Could not send progress notification: {e}")
        
        # Also log to stderr
        logger.debug(message)
    
    def _get_progress_summary(self) -> str:
        """Get formatted progress summary from request context"""
        ctx = _request_context.get()
        if ctx and hasattr(ctx, 'progress_messages') and ctx.progress_messages:
            return "\n\n--- Progress Log ---\n" + "\n".join(ctx.progress_messages) + "\n--- End Progress Log ---\n\n"
        return ""

    
    async def _handle_standard_tool(self, tool: Dict[str, Any], arguments: dict) -> List[TextContent]:
        """Handle a standard single-endpoint tool"""
        endpoint_mapping = tool["endpoint_mapping"]
        method = endpoint_mapping["method"].upper()
        path = endpoint_mapping["path"]
        
        # Replace path parameters
        for key, value in arguments.items():
            path = path.replace(f"{{{key}}}", str(value))
        
        url = f"{self.base_url}{path}"
        
        # Prepare headers
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        async with httpx.AsyncClient() as client:
            try:
                if method == "GET":
                    response = await client.get(url, headers=headers, params=arguments)
                elif method == "POST":
                    response = await client.post(url, headers=headers, json=arguments)
                elif method == "PUT":
                    response = await client.put(url, headers=headers, json=arguments)
                elif method == "DELETE":
                    response = await client.delete(url, headers=headers)
                elif method == "PATCH":
                    response = await client.patch(url, headers=headers, json=arguments)
                else:
                    return [TextContent(type="text", text=f"Unsupported method: {method}")]
                
                # Format response
                result = f"Status: {response.status_code}\n\n"
                try:
                    result += json.dumps(response.json(), indent=2)
                except:
                    result += response.text
                
                return [TextContent(type="text", text=result)]
            
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def _handle_composite_tool(self, tool: Dict[str, Any], arguments: dict) -> List[TextContent]:
        """Handle a composite multi-endpoint tool using MCP-to-MCP orchestration"""
        
        if not self.anthropic_api_key:
            return [TextContent(
                type="text", 
                text="Error: Composite tools require ANTHROPIC_API_KEY to be set. "
                     "This tool orchestrates multiple MCP tool calls using an LLM agent."
            )]
        
        orchestration_logic = tool.get("orchestration_logic", "")
        use_case = tool.get("use_case_description", "")
        
        await self._send_progress(f"🚀 Starting composite tool: {tool['name']}")
        await self._send_progress(f"📋 Use case: {use_case}")
        await self._send_progress(f"🔧 Orchestration strategy: {orchestration_logic[:100]}...")
        
        logger.info(f"Executing composite tool: {tool['name']}")
        logger.debug(f"Use case: {use_case}")
        logger.debug(f"Orchestration: {orchestration_logic[:100]}...")
        
        # Build MCP tool definitions for the agent
        mcp_tools = []
        for standard_tool in self.tools:
            mcp_tools.append({
                "name": standard_tool["name"],
                "description": standard_tool["description"],
                "input_schema": standard_tool["input_schema"]
            })
        
        # System prompt for the orchestration agent
        system_prompt = f"""You are an MCP orchestration agent. Your job is to execute a complex workflow by calling multiple MCP tools in the correct order and combining their results.

TASK: {tool['description']}

USE CASE: {use_case}

ORCHESTRATION LOGIC: {orchestration_logic}

AVAILABLE MCP TOOLS: You have access to the following MCP tools (these call the actual API):
{json.dumps(mcp_tools, indent=2)}

INSTRUCTIONS:
1. Call the MCP tools in the correct order based on the orchestration logic
2. Extract data from responses to use in subsequent calls (e.g., IDs, values)
3. Handle data flow between calls properly
4. Aggregate and combine results as needed
5. Return a final consolidated response

USER INPUT: {json.dumps(arguments)}

Execute the workflow step by step, calling MCP tools as needed. Each tool call will be executed via MCP protocol."""
        
        # Initialize Anthropic client
        client = Anthropic(api_key=self.anthropic_api_key)
        messages = []
        
        await self._send_progress(f"🤖 Initializing AI orchestration agent...")
        logger.info("Starting MCP orchestration agent")
        
        try:
            # Agentic loop with MCP tool calls
            max_iterations = 20
            iteration = 0
            
            while iteration < max_iterations:
                iteration += 1
                await self._send_progress(f"🔄 Agent iteration {iteration}/{max_iterations}")
                logger.debug(f"Agent iteration {iteration}/{max_iterations}")
                
                # Call Claude with MCP tools
                response = client.messages.create(
                    model="claude-3-7-sonnet-latest",
                    max_tokens=4096,
                    system=system_prompt,
                    messages=messages if messages else [{"role": "user", "content": "Execute the workflow using MCP tools."}],
                    tools=mcp_tools
                )
                
                # Add assistant response to messages
                messages.append({"role": "assistant", "content": response.content})
                
                # Check if we're done (no tool use)
                if response.stop_reason == "end_turn":
                    # Extract final text response
                    final_text = ""
                    for block in response.content:
                        if hasattr(block, 'text'):
                            final_text += block.text
                    
                    await self._send_progress(f"✅ Orchestration completed successfully in {iteration} iterations")
                    logger.info(f"Agent completed successfully in {iteration} iterations")
                    
                    # Include progress log in the result
                    progress_summary = self._get_progress_summary()
                    result_text = progress_summary + final_text if progress_summary else final_text
                    
                    return [TextContent(type="text", text=result_text)]
                
                # Process MCP tool calls
                if response.stop_reason == "tool_use":
                    tool_results = []
                    
                    for block in response.content:
                        if block.type == "tool_use":
                            tool_name = block.name
                            tool_input = block.input
                            tool_use_id = block.id
                            
                            # Send progress notification about the tool call
                            await self._send_progress(f"  🔧 Calling: {tool_name}({json.dumps(tool_input, indent=2)})")
                            logger.debug(f"Calling MCP tool: {tool_name} with args: {json.dumps(tool_input)}")
                            
                            # Find and execute the MCP tool (which calls the actual API)
                            tool_found = False
                            for standard_tool in self.tools:
                                if standard_tool["name"] == tool_name:
                                    # Execute via our standard tool handler (which makes the API call)
                                    result = await self._handle_standard_tool(standard_tool, tool_input)
                                    tool_result_text = result[0].text if result else "No response"
                                    
                                    # Send progress notification about the result
                                    result_preview = tool_result_text[:150] + "..." if len(tool_result_text) > 150 else tool_result_text
                                    await self._send_progress(f"  ✓ Result from {tool_name}: {result_preview}")
                                    logger.debug(f"MCP tool result: {tool_result_text[:200]}...")
                                    
                                    tool_results.append({
                                        "type": "tool_result",
                                        "tool_use_id": tool_use_id,
                                        "content": tool_result_text
                                    })
                                    tool_found = True
                                    break
                            
                            if not tool_found:
                                error_msg = f"Error: MCP tool {tool_name} not found"
                                await self._send_progress(f"  ❌ {error_msg}", "error")
                                tool_results.append({
                                    "type": "tool_result",
                                    "tool_use_id": tool_use_id,
                                    "content": error_msg,
                                    "is_error": True
                                })
                    
                    # Add tool results to messages
                    messages.append({"role": "user", "content": tool_results})
                else:
                    # Unexpected stop reason
                    error_msg = f"Orchestration stopped unexpectedly: {response.stop_reason}"
                    await self._send_progress(f"⚠️ {error_msg}", "warning")
                    
                    progress_summary = self._get_progress_summary()
                    result_text = progress_summary + error_msg if progress_summary else error_msg
                    
                    return [TextContent(
                        type="text",
                        text=result_text
                    )]
            
            # Max iterations reached
            error_msg = f"Orchestration failed: Maximum iterations ({max_iterations}) reached without completion"
            await self._send_progress(f"❌ {error_msg}", "error")
            
            progress_summary = self._get_progress_summary()
            result_text = progress_summary + error_msg if progress_summary else error_msg
            
            return [TextContent(
                type="text",
                text=result_text
            )]
        
        except Exception as e:
            error_msg = f"Orchestration error: {str(e)}"
            await self._send_progress(f"❌ {error_msg}", "error")
            logger.error(f"Orchestration error: {str(e)}", exc_info=True)
            
            progress_summary = self._get_progress_summary()
            result_text = progress_summary + error_msg if progress_summary else error_msg
            
            return [TextContent(type="text", text=result_text)]
    
    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.app.run(
                read_stream, 
                write_stream, 
                self.app.create_initialization_options()
            )


async def main():
    # Get tools config path from environment or use default
    tools_config_path = os.getenv("TOOLS_CONFIG_PATH", "tools.json")
    script_dir = Path(__file__).parent

    # Resolve path relative to current working directory
    config_path = Path(tools_config_path)

    if not config_path.is_absolute():
        config_path = script_dir / config_path

    if not config_path.exists():
        logger.error("Please set TOOLS_CONFIG_PATH environment variable or ensure tools.json exists")
        return

    logger.info("Booting Generic MCP Server")
    server = GenericMCPServer(str(config_path))
    logger.info("Server is now running. Waiting for MCP client connection...")
    await server.run()



if __name__ == "__main__":
    asyncio.run(main())
