from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum

class HTTPMethod(str, Enum):
    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"
    PATCH = "patch"

class Parameter(BaseModel):
    model_config = {"populate_by_name": True}
    
    name: str
    in_: str = Field(alias="in")
    description: Optional[str] = None
    required: bool = False
    schema_: Dict[str, Any] = Field(alias="schema", default={})

class Endpoint(BaseModel):
    path: str
    method: HTTPMethod
    operation_id: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    parameters: List[Parameter] = []
    request_body: Optional[Dict[str, Any]] = None
    responses: Dict[str, Any] = {}
    needs_enrichment: bool = False
    enriched_description: Optional[str] = None
    business_context: Optional[str] = None

class OpenAPISpec(BaseModel):
    openapi_version: str
    info: Dict[str, Any]
    servers: List[Dict[str, Any]] = []
    endpoints: List[Endpoint]
    raw_spec: Dict[str, Any]

class EnrichmentRequest(BaseModel):
    endpoint_path: str
    endpoint_method: HTTPMethod
    user_context: str

class EndpointReference(BaseModel):
    """Reference to an endpoint for composite tools"""
    path: str
    method: HTTPMethod
    
class MCPTool(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]
    endpoint_mapping: Dict[str, str]  # Maps to original API endpoint
    is_composite: bool = False  # Flag for composite tools

class CompositeTool(BaseModel):
    """A tool that combines multiple API endpoints"""
    name: str
    description: str
    use_case_description: str
    input_schema: Dict[str, Any]
    endpoint_mappings: List[Dict[str, Any]]  # List of endpoints to call in sequence
    orchestration_logic: str  # LLM-generated logic for combining calls
    is_composite: bool = True

class CompositeToolRequest(BaseModel):
    """Request to create a composite tool"""
    use_case_description: str
    selected_endpoints: List[EndpointReference]

class ToolModel(BaseModel):
    api_name: str
    base_url: str
    tools: List[MCPTool]
    composite_tools: List[CompositeTool] = []

class ServerGenerationRequest(BaseModel):
    tool_model: ToolModel
    server_name: str
