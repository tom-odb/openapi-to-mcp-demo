from typing import List, Dict, Any
from ..models.schemas import Endpoint, MCPTool, ToolModel, HTTPMethod

class ToolGenerator:
    def generate_tools(self, endpoints: List[Endpoint], api_name: str, base_url: str) -> ToolModel:
        """Convert enriched endpoints into MCP tool definitions"""

        tools = []
        for endpoint in endpoints:
            tool = self._endpoint_to_tool(endpoint)
            if tool:
                tools.append(tool)

        return ToolModel(
            api_name=api_name,
            base_url=base_url,
            tools=tools
        )

    def _endpoint_to_tool(self, endpoint: Endpoint) -> MCPTool:
        """Convert a single endpoint to an MCP tool"""

        # Generate tool name from operation_id or path
        tool_name = endpoint.operation_id or self._path_to_tool_name(endpoint.path, endpoint.method)

        # Build description
        description = endpoint.enriched_description or endpoint.description or endpoint.summary or f"{endpoint.method.value.upper()} {endpoint.path}"

        if endpoint.business_context:
            description += f"\n\nBusiness Context: {endpoint.business_context}"

        # Build input schema from parameters and request body
        input_schema = self._build_input_schema(endpoint)

        return MCPTool(
            name=tool_name,
            description=description,
            input_schema=input_schema,
            endpoint_mapping={
                "path": endpoint.path,
                "method": endpoint.method.value
            }
        )

    def _path_to_tool_name(self, path: str, method: HTTPMethod) -> str:
        """Convert path to a tool name"""
        # Remove leading slash and replace path params
        clean_path = path.lstrip("/").replace("{", "").replace("}", "")
        parts = clean_path.split("/")

        # Build name: method_resource_action
        method_prefix = method.value
        resource = parts[0] if parts else "resource"

        return f"{method_prefix}_{resource}"

    def _build_input_schema(self, endpoint: Endpoint) -> Dict[str, Any]:
        """Build JSON schema for tool input from endpoint parameters"""

        properties = {}
        required = []

        # Add path and query parameters
        for param in endpoint.parameters:
            param_schema = param.schema_.copy() if param.schema_ else {"type": "string"}

            if param.description:
                param_schema["description"] = param.description

            properties[param.name] = param_schema

            if param.required:
                required.append(param.name)

        # Add request body if present
        if endpoint.request_body:
            content = endpoint.request_body.get("content", {})
            json_content = content.get("application/json", {})
            schema = json_content.get("schema", {})

            if schema:
                # Flatten request body properties into top level
                body_props = schema.get("properties", {})
                properties.update(body_props)

                body_required = schema.get("required", [])
                required.extend(body_required)

        return {
            "type": "object",
            "properties": properties,
            "required": required
        }
