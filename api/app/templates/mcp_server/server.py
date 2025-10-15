"""
Generic MCP Server that reads tool definitions from a tools.json file.
Supports both standard tools and composite tools.
Composite tools use MCP client to orchestrate calls to standard tools.
"""
import asyncio
import logging
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from typing import Any, List
from dotenv import load_dotenv

from services.api_service import APIService
from services.orchestration_service import OrchestrationService
from entities.request_context import RequestContext, set_current_context, get_current_context
from utils.config_loader import ConfigLoader
from utils.logger_utils import setup_logging, ProgressLogger

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

load_dotenv()


class GenericMCPServer:
    """Generic MCP Server with modular architecture"""
    
    def __init__(self, tools_config_path: str):
        """Initialize server with tools configuration"""
        self.config = ConfigLoader.load_tools_config(tools_config_path)
        self.env_config = ConfigLoader.get_environment_config()
        
        # Extract configuration
        self.api_name = self.config.get("api_name", "api")
        self.base_url = self.config.get("base_url", "")
        self.tools = self.config.get("tools", [])
        self.composite_tools = self.config.get("composite_tools", [])
        
        # Initialize services
        self.api_service = APIService(
            base_url=self.base_url,
            api_key=self.env_config["api_key"]
        )
        
        self.orchestration_service = OrchestrationService(
            api_service=self.api_service,
            anthropic_api_key=self.env_config["anthropic_api_key"]
        )
        
        logger.info(f"Starting server for API: {self.api_name}")
        logger.info(f"Base URL: {self.base_url}")
        logger.info(f"Standard tools: {len(self.tools)} | Composite tools: {len(self.composite_tools)}")
            
        if self.env_config["anthropic_api_key"] and len(self.composite_tools) > 0:
            logger.info("ANTHROPIC_API_KEY is configured - composite tools enabled")
        elif len(self.composite_tools) > 0:
            logger.warning("Composite tools found but ANTHROPIC_API_KEY not set - they may not work correctly")
            
        self.app = Server(f"{self.api_name}-mcp-server")
        self._register_handlers()
        logger.info("Server initialization complete")
    
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
            
            # Setup request context
            ctx = RequestContext()
            if request_context:
                # Copy any relevant data from the MCP request context
                if hasattr(request_context, 'session'):
                    ctx.session = request_context.session
            set_current_context(ctx)
            
            try:
                # Check if it's a standard tool
                for tool in self.tools:
                    if tool["name"] == name:
                        result = await self.api_service.execute_tool(tool, arguments)
                        return self._add_progress_to_result(result)
                
                # Check if it's a composite tool
                for tool in self.composite_tools:
                    if tool["name"] == name:
                        result = await self.orchestration_service.execute_composite_tool(
                            tool, 
                            arguments, 
                            self.tools,
                            progress_callback=ProgressLogger.send_progress
                        )
                        return self._add_progress_to_result(result)
                
                raise ValueError(f"Unknown tool: {name}")
            
            finally:
                # Clean up context
                set_current_context(None)
    
    def _add_progress_to_result(self, result: List[TextContent]) -> List[TextContent]:
        """Add progress summary to the result if available"""
        ctx = get_current_context()
        if ctx and result:
            progress_summary = ctx.get_progress_summary()
            if progress_summary:
                # Prepend progress to the first text content
                original_text = result[0].text
                result[0] = TextContent(
                    type="text", 
                    text=progress_summary + original_text
                )
        return result
    
    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.app.run(
                read_stream, 
                write_stream, 
                self.app.create_initialization_options()
            )


async def main():
    """Main entry point"""
    env_config = ConfigLoader.get_environment_config()
    tools_config_path = env_config["tools_config_path"]
    
    # Resolve path relative to current working directory
    config_path = Path(tools_config_path)
    if not config_path.is_absolute():
        script_dir = Path(__file__).parent
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