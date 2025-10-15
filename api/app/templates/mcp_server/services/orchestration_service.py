"""
Orchestration Service for handling composite MCP tools that require AI-driven 
coordination of multiple API endpoints.
"""
import json
import logging
from typing import Dict, Any, List, Callable
from mcp.types import TextContent
from anthropic import Anthropic
from services.api_service import APIService

logger = logging.getLogger(__name__)


class OrchestrationService:
    """Service for handling composite multi-endpoint tools using AI orchestration"""
    
    def __init__(self, api_service: APIService, anthropic_api_key: str = ""):
        self.api_service = api_service
        self.anthropic_api_key = anthropic_api_key
        self.anthropic_client = None
        
        if anthropic_api_key:
            self.anthropic_client = Anthropic(api_key=anthropic_api_key)
    
    async def execute_composite_tool(
        self, 
        tool: Dict[str, Any], 
        arguments: dict, 
        standard_tools: List[Dict[str, Any]],
        progress_callback: Callable[[str, str], None] = None
    ) -> List[TextContent]:
        """Execute a composite multi-endpoint tool using AI orchestration"""
        
        if not self.anthropic_client:
            return [TextContent(
                type="text", 
                text="Error: Composite tools require ANTHROPIC_API_KEY to be set. "
                     "This tool orchestrates multiple MCP tool calls using an LLM agent."
            )]
        
        orchestration_logic = tool.get("orchestration_logic", "")
        use_case = tool.get("use_case_description", "")
        
        if progress_callback:
            await progress_callback(f"🚀 Starting composite tool: {tool['name']}", "info")
            await progress_callback(f"📋 Use case: {use_case}", "info")
            await progress_callback(f"🔧 Orchestration strategy: {orchestration_logic[:100]}...", "info")
        
        logger.info(f"Executing composite tool: {tool['name']}")
        logger.debug(f"Use case: {use_case}")
        logger.debug(f"Orchestration: {orchestration_logic[:100]}...")
        
        # Build MCP tool definitions for the agent
        mcp_tools = []
        for standard_tool in standard_tools:
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
        
        messages = []
        
        if progress_callback:
            await progress_callback(f"🤖 Initializing AI orchestration agent...", "info")
        logger.info("Starting MCP orchestration agent")
        
        try:
            # Agentic loop with MCP tool calls
            max_iterations = 20
            iteration = 0
            
            while iteration < max_iterations:
                iteration += 1
                if progress_callback:
                    await progress_callback(f"🔄 Agent iteration {iteration}/{max_iterations}", "info")
                logger.debug(f"Agent iteration {iteration}/{max_iterations}")
                
                # Call Claude with MCP tools
                response = self.anthropic_client.messages.create(
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
                    
                    if progress_callback:
                        await progress_callback(f"✅ Orchestration completed successfully in {iteration} iterations", "info")
                    logger.info(f"Agent completed successfully in {iteration} iterations")
                    
                    return [TextContent(type="text", text=final_text)]
                
                # Process MCP tool calls
                if response.stop_reason == "tool_use":
                    tool_results = []
                    
                    for block in response.content:
                        if block.type == "tool_use":
                            tool_name = block.name
                            tool_input = block.input
                            tool_use_id = block.id
                            
                            # Send progress notification about the tool call
                            if progress_callback:
                                await progress_callback(f"  🔧 Calling: {tool_name}({json.dumps(tool_input, indent=2)})", "info")
                            logger.debug(f"Calling MCP tool: {tool_name} with args: {json.dumps(tool_input)}")
                            
                            # Find and execute the MCP tool (which calls the actual API)
                            tool_found = False
                            for standard_tool in standard_tools:
                                if standard_tool["name"] == tool_name:
                                    # Execute via our API service (which makes the API call)
                                    result = await self.api_service.execute_tool(standard_tool, tool_input)
                                    tool_result_text = result[0].text if result else "No response"
                                    
                                    # Send progress notification about the result
                                    result_preview = tool_result_text[:150] + "..." if len(tool_result_text) > 150 else tool_result_text
                                    if progress_callback:
                                        await progress_callback(f"  ✓ Result from {tool_name}: {result_preview}", "info")
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
                                if progress_callback:
                                    await progress_callback(f"  ❌ {error_msg}", "error")
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
                    if progress_callback:
                        await progress_callback(f"⚠️ {error_msg}", "warning")
                    
                    return [TextContent(type="text", text=error_msg)]
            
            # Max iterations reached
            error_msg = f"Orchestration failed: Maximum iterations ({max_iterations}) reached without completion"
            if progress_callback:
                await progress_callback(f"❌ {error_msg}", "error")
            
            return [TextContent(type="text", text=error_msg)]
        
        except Exception as e:
            error_msg = f"Orchestration error: {str(e)}"
            if progress_callback:
                await progress_callback(f"❌ {error_msg}", "error")
            logger.error(f"Orchestration error: {str(e)}", exc_info=True)
            
            return [TextContent(type="text", text=error_msg)]