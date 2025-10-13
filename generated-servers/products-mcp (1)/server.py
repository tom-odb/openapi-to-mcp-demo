"""
Generic MCP Server that reads tool definitions from a tools.json file.
Supports both standard tools and composite tools.
Composite tools use MCP client to orchestrate calls to standard tools.
"""
import asyncio
import httpx
import json
import os
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from typing import Dict, Any, List, Optional
from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class GenericMCPServer:
    def __init__(self, tools_config_path: str):
        """Initialize server with tools configuration"""
        print(f"[MCP] Loading tools config from: {tools_config_path}")
        self.config = self._load_config(tools_config_path)
        self.api_name = self.config.get("api_name", "api")
        self.base_url = self.config.get("base_url", "")
        self.tools = self.config.get("tools", [])
        self.composite_tools = self.config.get("composite_tools", [])
        self.api_key = os.getenv("API_KEY", "")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        
        print(f"[MCP] Starting server for API: {self.api_name}")
        print(f"[MCP] Base URL: {self.base_url}")
        print(f"[MCP] Standard tools: {len(self.tools)} | Composite tools: {len(self.composite_tools)}")
        print(f"[MCP] To connect, set TOOLS_CONFIG_PATH={tools_config_path} and run: python server.py")
        if self.api_key:
            print("[MCP] API_KEY is set (env)")
        else:
            print("[MCP] API_KEY is not set (env)")
        if self.anthropic_api_key and len(self.composite_tools) > 0:
            print("[MCP] ANTHROPIC_API_KEY is set - composite tools will use LLM orchestration")
        elif len(self.composite_tools) > 0:
            print("[MCP] WARNING: Composite tools found but ANTHROPIC_API_KEY not set - they may not work correctly")
        print("[MCP] Server is initializing...\n")
        self.app = Server(f"{self.api_name}-mcp-server")
        self._register_handlers()
    
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
        async def call_tool(name: str, arguments: dict) -> List[TextContent]:
            """Execute a tool by making API request(s)"""
            
            # Check if it's a standard tool
            for tool in self.tools:
                if tool["name"] == name:
                    return await self._handle_standard_tool(tool, arguments)
            
            # Check if it's a composite tool
            for tool in self.composite_tools:
                if tool["name"] == name:
                    return await self._handle_composite_tool(tool, arguments)
            
            raise ValueError(f"Unknown tool: {name}")
    
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
        
        print(f"[MCP] Executing composite tool: {tool['name']}")
        print(f"[MCP] Use case: {use_case}")
        print(f"[MCP] Orchestration: {orchestration_logic[:100]}...")
        
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
        
        print("[MCP] Starting MCP orchestration agent...")
        
        try:
            # Agentic loop with MCP tool calls
            max_iterations = 20
            iteration = 0
            
            while iteration < max_iterations:
                iteration += 1
                print(f"[MCP] Agent iteration {iteration}/{max_iterations}")
                
                # Call Claude with MCP tools
                response = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
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
                    
                    print(f"[MCP] Agent completed successfully in {iteration} iterations")
                    return [TextContent(type="text", text=final_text)]
                
                # Process MCP tool calls
                if response.stop_reason == "tool_use":
                    tool_results = []
                    
                    for block in response.content:
                        if block.type == "tool_use":
                            tool_name = block.name
                            tool_input = block.input
                            tool_use_id = block.id
                            
                            print(f"[MCP]   → Calling MCP tool: {tool_name}({json.dumps(tool_input)})")
                            
                            # Find and execute the MCP tool (which calls the actual API)
                            tool_found = False
                            for standard_tool in self.tools:
                                if standard_tool["name"] == tool_name:
                                    # Execute via our standard tool handler (which makes the API call)
                                    result = await self._handle_standard_tool(standard_tool, tool_input)
                                    tool_result_text = result[0].text if result else "No response"
                                    
                                    print(f"[MCP]   ← MCP tool result: {tool_result_text[:100]}...")
                                    
                                    tool_results.append({
                                        "type": "tool_result",
                                        "tool_use_id": tool_use_id,
                                        "content": tool_result_text
                                    })
                                    tool_found = True
                                    break
                            
                            if not tool_found:
                                tool_results.append({
                                    "type": "tool_result",
                                    "tool_use_id": tool_use_id,
                                    "content": f"Error: MCP tool {tool_name} not found",
                                    "is_error": True
                                })
                    
                    # Add tool results to messages
                    messages.append({"role": "user", "content": tool_results})
                else:
                    # Unexpected stop reason
                    return [TextContent(
                        type="text",
                        text=f"Orchestration stopped unexpectedly: {response.stop_reason}"
                    )]
            
            # Max iterations reached
            return [TextContent(
                type="text",
                text=f"Orchestration failed: Maximum iterations ({max_iterations}) reached without completion"
            )]
        
        except Exception as e:
            print(f"[MCP] Orchestration error: {str(e)}")
            return [TextContent(type="text", text=f"Orchestration error: {str(e)}")]
    
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
    
    if not Path(tools_config_path).exists():
        print(f"[MCP] Error: Tools configuration file not found: {tools_config_path}")
        print("[MCP] Please set TOOLS_CONFIG_PATH environment variable or ensure tools.json exists in current directory")
        return
    print(f"[MCP] Booting Generic MCP Server...\n")
    server = GenericMCPServer(tools_config_path)
    print(f"[MCP] Server is now running. Waiting for MCP client connection...\n")
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
