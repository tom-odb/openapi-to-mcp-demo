"""
Generic MCP Server that reads tool definitions from a tools.json file.
Supports both standard tools and composite tools.
"""
import asyncio
import httpx
import json
import os
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from typing import Dict, Any, List


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
        
        print(f"[MCP] Starting server for API: {self.api_name}")
        print(f"[MCP] Base URL: {self.base_url}")
        print(f"[MCP] Standard tools: {len(self.tools)} | Composite tools: {len(self.composite_tools)}")
        if self.api_key:
            print("[MCP] API_KEY is set (env)")
        else:
            print("[MCP] API_KEY is not set (env)")
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
        """Handle a composite multi-endpoint tool"""
        endpoint_mappings = tool.get("endpoint_mappings", [])
        orchestration_logic = tool.get("orchestration_logic", "")
        
        results = []
        async with httpx.AsyncClient() as client:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            # Execute each endpoint in sequence
            for idx, endpoint in enumerate(endpoint_mappings, 1):
                method = endpoint["method"].upper()
                path = endpoint["path"]
                purpose = endpoint.get("purpose", "N/A")
                
                # Replace path parameters
                for key, value in arguments.items():
                    path = path.replace(f"{{{key}}}", str(value))
                
                url = f"{self.base_url}{path}"
                
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
                        results.append({
                            "endpoint": f"{method} {path}",
                            "purpose": purpose,
                            "status": "error",
                            "data": f"Unsupported method: {method}"
                        })
                        continue
                    
                    # Parse response
                    try:
                        data = response.json()
                    except:
                        data = response.text
                    
                    results.append({
                        "endpoint": f"{method} {path}",
                        "purpose": purpose,
                        "status": response.status_code,
                        "data": data
                    })
                
                except Exception as e:
                    results.append({
                        "endpoint": f"{method} {path}",
                        "purpose": purpose,
                        "status": "error",
                        "data": str(e)
                    })
        
        # Combine results
        combined_output = f"Composite Tool: {tool['name']}\n"
        combined_output += f"Orchestration: {orchestration_logic}\n\n"
        combined_output += "=" * 80 + "\n\n"
        
        for idx, result in enumerate(results, 1):
            combined_output += f"Call {idx}: {result['endpoint']}\n"
            combined_output += f"Purpose: {result['purpose']}\n"
            combined_output += f"Status: {result['status']}\n"
            combined_output += f"Data: {json.dumps(result['data'], indent=2) if isinstance(result['data'], dict) else result['data']}\n\n"
            combined_output += "-" * 80 + "\n\n"
        
        return [TextContent(type="text", text=combined_output)]
    
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
