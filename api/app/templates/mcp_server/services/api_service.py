"""
API Service for handling standard MCP tools that map to single API endpoints.
"""
import httpx
import json
import logging
from typing import Dict, Any, List
from mcp.types import TextContent

logger = logging.getLogger(__name__)


class APIService:
    """Service for handling API tool calls"""

    def __init__(self, base_url: str, api_key: str = ""):
        self.base_url = base_url
        self.api_key = api_key
    
    async def execute_tool(self, tool: Dict[str, Any], arguments: dict) -> List[TextContent]:
        """Execute a standard single-endpoint tool"""
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