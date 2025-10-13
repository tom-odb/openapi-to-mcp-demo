# OpenAPI to MCP Converter - Build Instructions

## Original context
We have a working group in our company (about 10.000 employees, subdivided among smaller companies (20-50 employees on average) to inform and inspire about AI. I am giving a small presentation on building bespoke MCP tools. Our angle is to demonstrate how quickly you can get from an existing API to an MCP server with useful tooling.
This is a luncheon session, so we have about 40-45 minutes for the presentation and some questions.
I'll describe what I have in mind below. I need you to give me some constructive but critical feedback on the idea, the planning and execution. Ask me questions to get into the nitty gritty. Then help me prep the presentation.
The plan:
I want to set up a small demo to grab an existing OpenAPI spec and convert it into a usable MCP server. This includes reading the spec, interpreting each endpoint with the help of an LLM, augmented with user input (since I assume a lot of endpoints and models will be missing proper descriptions), deciding on a list of useful tools for the server (either automatically or based on user input), to eventually receive a declarative model (in JSON or YAML) of all tools the server should include. We will then use this model to set up the necessary code to implement the server.
I want the core message to be:
- this is not hard or magic, anyone can build this and it will accelerate development for a lot of use cases
- this is not a silver bullet solution, we want to combine user input (i.e. domain knowledge and technical expertise) with the power of (reasoning) LLM's to take this one step further than a proof of concept
- using existing tools, like API documentation, and some lightweight coding, we can build demo's and production ready tools quickly

### Clarification on approach

- Have you already prototyped this conversion tool? If not, that's your first priority.
    - No, I plan on vibe coding this part
- What specific OpenAPI spec are you planning to use?
    - No real preference, will be using the latest version or the version that works best with the code. This is more about showing the concepts, not so much about the technical details.
- What's your backup plan if the live demo fails?
    - I will prep screenshots to use in the slides in case the demo seems to risky
- Who exactly is in the audience? (roles, technical comfort level)
    - this is the challenge: it will be a mix of tech, business and sales. So we'll need to explain some concepts high-level and keep the demo lightweight
- What do you want them to DO after the presentation? Try it themselves? Request budget? Just be inspired?
    - Try it themselves, know the option exists and can accelerate both their internal workflows as well as work they perform for their clients
- How will you demonstrate the "user augmentation" part without it being boring or taking 15 minutes?
    - I will prep an OpenAPI spec to use, as well as some descriptions and business use cases I can easily copy paste. These should be short and clear so the audience can follow along so I will have to pick an API that is easy to understand (like a webshop or CRM).

All code and specs will be prepared up-front, with screenshots as back up in case the demo is too risky.

## Project Overview
Build a tool that converts OpenAPI specifications into working MCP (Model Context Protocol) servers. The system should analyze API specs, allow for human enrichment of endpoint descriptions, generate a declarative tool model, and produce a functioning MCP server.

## Tech Stack
- **Backend**: Python 3.11+ with FastAPI
- **MCP Server**: Python with FastMCP library
- **Frontend**: Vue 3 with Composition API, Vite
- **LLM Integration**: Anthropic Claude API (for analyzing and enriching specs)

---

## Part 1: Project Structure

Create the following directory structure:

```
openapi-to-mcp/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py           # API endpoints
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── openapi_parser.py   # Parse OpenAPI specs
│   │   │   ├── llm_enricher.py     # Claude API integration
│   │   │   ├── tool_generator.py   # Generate MCP tool definitions
│   │   │   ├── server_generator.py # Generate MCP server code
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── schemas.py          # Pydantic models
│   ├── requirements.txt
│   ├── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── SpecUploader.vue
│   │   │   ├── EndpointList.vue
│   │   │   ├── EnrichmentEditor.vue
│   │   │   ├── ToolPreview.vue
│   │   │   ├── ServerGenerator.vue
│   │   ├── views/
│   │   │   ├── HomeView.vue
│   │   ├── stores/
│   │   │   ├── converter.js        # Pinia store
│   │   ├── App.vue
│   │   ├── main.js
│   ├── package.json
├── generated_servers/              # Output directory for MCP servers
├── examples/
│   ├── ecommerce_openapi.yaml      # Demo OpenAPI spec
├── README.md
```

---

## Part 2: Backend Implementation

### Step 1: Setup Backend Dependencies

Create `backend/requirements.txt`:
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0
anthropic==0.18.1
pyyaml==6.0.1
jinja2==3.1.3
python-multipart==0.0.6
python-dotenv==1.0.0
mcp==0.9.0
httpx==0.26.0
```

### Step 2: Define Data Models

Create `backend/app/models/schemas.py`:

```python
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
    name: str
    in_: str = Field(alias="in")
    description: Optional[str] = None
    required: bool = False
    schema_: Dict[str, Any] = Field(alias="schema")

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

class MCPTool(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]
    endpoint_mapping: Dict[str, str]  # Maps to original API endpoint

class ToolModel(BaseModel):
    api_name: str
    base_url: str
    tools: List[MCPTool]

class ServerGenerationRequest(BaseModel):
    tool_model: ToolModel
    server_name: str
```

### Step 3: OpenAPI Parser Service

Create `backend/app/services/openapi_parser.py`:

```python
import yaml
import json
from typing import Dict, Any, List
from ..models.schemas import OpenAPISpec, Endpoint, Parameter, HTTPMethod

class OpenAPIParser:
    def parse_spec(self, spec_content: str, file_type: str = "yaml") -> OpenAPISpec:
        """Parse OpenAPI spec from YAML or JSON string"""
        if file_type == "yaml":
            raw_spec = yaml.safe_load(spec_content)
        else:
            raw_spec = json.loads(spec_content)
        
        endpoints = self._extract_endpoints(raw_spec)
        
        return OpenAPISpec(
            openapi_version=raw_spec.get("openapi", "3.0.0"),
            info=raw_spec.get("info", {}),
            servers=raw_spec.get("servers", []),
            endpoints=endpoints,
            raw_spec=raw_spec
        )
    
    def _extract_endpoints(self, spec: Dict[str, Any]) -> List[Endpoint]:
        """Extract all endpoints from OpenAPI spec"""
        endpoints = []
        paths = spec.get("paths", {})
        
        for path, methods in paths.items():
            for method, operation in methods.items():
                if method.lower() not in ["get", "post", "put", "delete", "patch"]:
                    continue
                
                # Check if endpoint needs enrichment (missing description)
                needs_enrichment = not operation.get("description") or len(operation.get("description", "")) < 20
                
                endpoint = Endpoint(
                    path=path,
                    method=HTTPMethod(method.lower()),
                    operation_id=operation.get("operationId"),
                    summary=operation.get("summary"),
                    description=operation.get("description"),
                    parameters=self._extract_parameters(operation.get("parameters", [])),
                    request_body=operation.get("requestBody"),
                    responses=operation.get("responses", {}),
                    needs_enrichment=needs_enrichment
                )
                endpoints.append(endpoint)
        
        return endpoints
    
    def _extract_parameters(self, params: List[Dict[str, Any]]) -> List[Parameter]:
        """Extract parameters from endpoint definition"""
        return [
            Parameter(
                name=p.get("name"),
                in_=p.get("in"),
                description=p.get("description"),
                required=p.get("required", False),
                schema_=p.get("schema", {})
            )
            for p in params
        ]
```

### Step 4: LLM Enrichment Service

Create `backend/app/services/llm_enricher.py`:

```python
import anthropic
import os
from typing import Dict, Any
from ..models.schemas import Endpoint

class LLMEnricher:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    async def enrich_endpoint(self, endpoint: Endpoint, user_context: str = "") -> Dict[str, str]:
        """Use Claude to generate enriched description for an endpoint"""
        
        prompt = self._build_enrichment_prompt(endpoint, user_context)
        
        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text
        
        # Parse the response (expecting structured format)
        lines = response_text.strip().split("\n")
        enriched_description = ""
        business_context = ""
        
        current_section = None
        for line in lines:
            if "DESCRIPTION:" in line.upper():
                current_section = "description"
                continue
            elif "BUSINESS CONTEXT:" in line.upper():
                current_section = "business"
                continue
            
            if current_section == "description":
                enriched_description += line + "\n"
            elif current_section == "business":
                business_context += line + "\n"
        
        return {
            "enriched_description": enriched_description.strip(),
            "business_context": business_context.strip()
        }
    
    def _build_enrichment_prompt(self, endpoint: Endpoint, user_context: str) -> str:
        """Build prompt for Claude to enrich endpoint"""
        
        params_str = "\n".join([
            f"  - {p.name} ({p.in_}): {p.description or 'No description'}"
            for p in endpoint.parameters
        ])
        
        prompt = f"""Analyze this API endpoint and provide a comprehensive description:

Endpoint: {endpoint.method.value.upper()} {endpoint.path}
Current Summary: {endpoint.summary or 'None'}
Current Description: {endpoint.description or 'None'}
Parameters:
{params_str or '  None'}

User Context: {user_context or 'No additional context provided'}

Please provide:
1. DESCRIPTION: A clear, technical description of what this endpoint does (2-3 sentences)
2. BUSINESS CONTEXT: When and why someone would use this endpoint (1-2 sentences)

Format your response exactly as:
DESCRIPTION:
[your description]

BUSINESS CONTEXT:
[your business context]
"""
        return prompt
    
    async def suggest_tools(self, endpoints: list[Endpoint]) -> Dict[str, Any]:
        """Suggest which endpoints should become MCP tools"""
        
        prompt = self._build_tool_suggestion_prompt(endpoints)
        
        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Return suggestions for frontend to display
        return {"suggestions": message.content[0].text}
    
    def _build_tool_suggestion_prompt(self, endpoints: list[Endpoint]) -> str:
        endpoints_str = "\n".join([
            f"{i+1}. {ep.method.value.upper()} {ep.path} - {ep.summary or 'No summary'}"
            for i, ep in enumerate(endpoints)
        ])
        
        return f"""Given these API endpoints, suggest which ones would make the most useful MCP tools for an AI assistant:

{endpoints_str}

Consider:
- Read operations (GET) are generally useful for information retrieval
- Write operations (POST, PUT, DELETE) should be included if they represent common actions
- List/search endpoints are valuable
- Avoid redundant or overly administrative endpoints

Provide a prioritized list of 5-8 recommended tools with brief reasoning.
"""
```

### Step 5: Tool Generator Service

Create `backend/app/services/tool_generator.py`:

```python
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
```

### Step 6: Server Generator Service

Create `backend/app/services/server_generator.py`:

```python
from jinja2 import Template
from pathlib import Path
from typing import Dict, Any
from ..models.schemas import ToolModel
import os

class ServerGenerator:
    def __init__(self):
        self.template_dir = Path(__file__).parent.parent.parent.parent / "templates"
    
    def generate_server(self, tool_model: ToolModel, server_name: str, output_dir: str) -> str:
        """Generate a complete MCP server from tool model"""
        
        output_path = Path(output_dir) / server_name
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate server.py
        server_code = self._generate_server_code(tool_model)
        (output_path / "server.py").write_text(server_code)
        
        # Generate README
        readme = self._generate_readme(tool_model, server_name)
        (output_path / "README.md").write_text(readme)
        
        # Generate pyproject.toml
        pyproject = self._generate_pyproject(server_name)
        (output_path / "pyproject.toml").write_text(pyproject)
        
        # Generate .env.example
        env_example = self._generate_env_example(tool_model)
        (output_path / ".env.example").write_text(env_example)
        
        return str(output_path)
    
    def _generate_server_code(self, tool_model: ToolModel) -> str:
        """Generate the MCP server Python code"""
        
        template = Template('''
import asyncio
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from pydantic import AnyUrl
import os

# API Configuration
API_BASE_URL = "{{ base_url }}"
API_KEY = os.getenv("API_KEY", "")

app = Server("{{ api_name }}-mcp-server")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools"""
    return [
{% for tool in tools %}
        Tool(
            name="{{ tool.name }}",
            description="{{ tool.description | replace('"', '\\"') | replace('\\n', ' ') }}",
            inputSchema={{ tool.input_schema | tojson }}
        ),
{% endfor %}
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a tool by making API request"""
    
{% for tool in tools %}
    if name == "{{ tool.name }}":
        return await {{ tool.name }}_handler(arguments)
{% endfor %}
    
    raise ValueError(f"Unknown tool: {name}")

{% for tool in tools %}
async def {{ tool.name }}_handler(arguments: dict) -> list[TextContent]:
    """Handler for {{ tool.name }}"""
    
    # Build request
    method = "{{ tool.endpoint_mapping.method }}".upper()
    path = "{{ tool.endpoint_mapping.path }}"
    
    # Replace path parameters
    for key, value in arguments.items():
        path = path.replace(f"{{{key}}}", str(value))
    
    url = f"{API_BASE_URL}{path}"
    
    # Prepare request
    headers = {}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    
    async with httpx.AsyncClient() as client:
        if method == "GET":
            response = await client.get(url, headers=headers, params=arguments)
        elif method == "POST":
            response = await client.post(url, headers=headers, json=arguments)
        elif method == "PUT":
            response = await client.put(url, headers=headers, json=arguments)
        elif method == "DELETE":
            response = await client.delete(url, headers=headers)
        else:
            return [TextContent(type="text", text=f"Unsupported method: {method}")]
    
    return [TextContent(
        type="text",
        text=f"Status: {response.status_code}\\n\\n{response.text}"
    )]

{% endfor %}

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
''')
        
        return template.render(
            api_name=tool_model.api_name,
            base_url=tool_model.base_url,
            tools=tool_model.tools
        )
    
    def _generate_readme(self, tool_model: ToolModel, server_name: str) -> str:
        """Generate README for the MCP server"""
        
        tools_list = "\n".join([f"- `{tool.name}`: {tool.description[:100]}..." for tool in tool_model.tools])
        
        return f"""# {server_name} MCP Server

MCP server for {tool_model.api_name} API.

## Available Tools

{tools_list}

## Installation

```bash
pip install -e .
```

## Configuration

Copy `.env.example` to `.env` and configure:
- `API_KEY`: Your API key for {tool_model.api_name}

## Usage

Add to your Claude Desktop config:

```json
{{
  "mcpServers": {{
    "{server_name}": {{
      "command": "python",
      "args": ["/path/to/{server_name}/server.py"],
      "env": {{
        "API_KEY": "your-api-key-here"
      }}
    }}
  }}
}}
```

## Generated by OpenAPI to MCP Converter
"""
    
    def _generate_pyproject(self, server_name: str) -> str:
        """Generate pyproject.toml"""
        
        return f"""[project]
name = "{server_name}"
version = "0.1.0"
description = "MCP server generated from OpenAPI spec"
requires-python = ">=3.10"
dependencies = [
    "mcp>=0.9.0",
    "httpx>=0.26.0",
    "python-dotenv>=1.0.0"
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
"""
    
    def _generate_env_example(self, tool_model: ToolModel) -> str:
        """Generate .env.example"""
        
        return f"""# API Configuration for {tool_model.api_name}
API_KEY=your-api-key-here
API_BASE_URL={tool_model.base_url}
"""
```

### Step 7: FastAPI Routes

Create `backend/app/api/routes.py`:

```python
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from ..services.openapi_parser import OpenAPIParser
from ..services.llm_enricher import LLMEnricher
from ..services.tool_generator import ToolGenerator
from ..services.server_generator import ServerGenerator
from ..models.schemas import (
    OpenAPISpec, EnrichmentRequest, Endpoint, 
    ToolModel, ServerGenerationRequest
)
from typing import Dict, Any
import tempfile
import shutil
from pathlib import Path

router = APIRouter()

# Service instances
parser = OpenAPIParser()
enricher = LLMEnricher()
tool_generator = ToolGenerator()
server_generator = ServerGenerator()

# In-memory storage (replace with DB in production)
specs_store: Dict[str, OpenAPISpec] = {}
enrichments_store: Dict[str, Dict[str, Any]] = {}

@router.post("/upload-spec", response_model=OpenAPISpec)
async def upload_spec(file: UploadFile = File(...)):
    """Upload and parse an OpenAPI specification"""
    
    content = await file.read()
    file_type = "yaml" if file.filename.endswith(('.yaml', '.yml')) else "json"
    
    try:
        spec = parser.parse_spec(content.decode(), file_type)
        
        # Store in memory
        spec_id = file.filename
        specs_store[spec_id] = spec
        enrichments_store[spec_id] = {}
        
        return spec
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse spec: {str(e)}")

@router.post("/enrich-endpoint")
async def enrich_endpoint(request: EnrichmentRequest, spec_id: str):
    """Enrich an endpoint with LLM-generated context"""
    
    if spec_id not in specs_store:
        raise HTTPException(status_code=404, detail="Spec not found")
    
    spec = specs_store[spec_id]
    
    # Find the endpoint
    endpoint = next(
        (ep for ep in spec.endpoints 
         if ep.path == request.endpoint_path and ep.method == request.endpoint_method),
        None
    )
    
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    
    try:
        enrichment = await enricher.enrich_endpoint(endpoint, request.user_context)
        
        # Store enrichment
        key = f"{request.endpoint_path}:{request.endpoint_method.value}"
        enrichments_store[spec_id][key] = enrichment
        
        # Update endpoint
        endpoint.enriched_description = enrichment["enriched_description"]
        endpoint.business_context = enrichment["business_context"]
        endpoint.needs_enrichment = False
        
        return enrichment
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enrichment failed: {str(e)}")

@router.post("/suggest-tools")
async def suggest_tools(spec_id: str):
    """Get LLM suggestions for which endpoints to convert to tools"""
    
    if spec_id not in specs_store:
        raise HTTPException(status_code=404, detail="Spec not found")
    
    spec = specs_store[spec_id]
    
    try:
        suggestions = await enricher.suggest_tools(spec.endpoints)
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Suggestion failed: {str(e)}")

@router.post("/generate-tools", response_model=ToolModel)
async def generate_tools(spec_id: str, api_name: str, base_url: str):
    """Generate MCP tool definitions from enriched spec"""
    
    if spec_id not in specs_store:
        raise HTTPException(status_code=404, detail="Spec not found")
    
    spec = specs_store[spec_id]
    
    # Apply stored enrichments
    for endpoint in spec.endpoints:
        key = f"{endpoint.path}:{endpoint.method.value}"
        if key in enrichments_store[spec_id]:
            enrichment = enrichments_store[spec_id][key]
            endpoint.enriched_description = enrichment["enriched_description"]
            endpoint.business_context = enrichment["business_context"]
    
    try:
        tool_model = tool_generator.generate_tools(spec.endpoints, api_name, base_url)
        return tool_model
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool generation failed: {str(e)}")

@router.post("/generate-server")
async def generate_server(request: ServerGenerationRequest):
    """Generate a complete MCP server from tool model"""
    
    try:
        output_dir = Path("generated_servers")
        output_dir.mkdir(exist_ok=True)
        
        server_path = server_generator.generate_server(
            request.tool_model,
            request.server_name,
            str(output_dir)
        )
        
        # Create a zip file
        zip_path = shutil.make_archive(
            str(output_dir / request.server_name),
            'zip',
            server_path
        )
        
        return {"server_path": server_path, "download_url": f"/download-server/{request.server_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server generation failed: {str(e)}")

@router.get("/download-server/{server_name}")
async def download_server(server_name: str):
    """Download generated server as zip file"""
    
    zip_path = Path("generated_servers") / f"{server_name}.zip"
    
    if not zip_path.exists():
        raise HTTPException(status_code=404, detail="Server not found")
    
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=f"{server_name}.zip"
    )
```

### Step 8: Main FastAPI Application

Create `backend/app/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="OpenAPI to MCP Converter",
    description="Convert OpenAPI specifications to MCP servers",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api", tags=["converter"])

@app.get("/")
async def root():
    return {"message": "OpenAPI to MCP Converter API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

---

## Part 3: Frontend Implementation

### Step 1: Setup Vue 3 Project

Create `frontend/package.json`:

```json
{
  "name": "openapi-to-mcp-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "pinia": "^2.1.7",
    "axios": "^1.6.0",
    "vue-router": "^4.2.5"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.0.0"
  }
}
```

### Step 2: Pinia Store

Create `frontend/src/stores/converter.js`:

```javascript
import { defineStore } from 'pinia'
import axios from 'axios'

const API_BASE = 'http://localhost:8000/api'

export const useConverterStore = defineStore('converter', {
  state: () => ({
    currentSpec: null,
    specId: null,
    endpoints: [],
    enrichments: {},
    toolModel: null,
    loading: false,
    error: null
  }),
  
  actions: {
    async uploadSpec(file) {
      this.loading = true
      this.error = null
      
      try {
        const formData = new FormData()
        formData.append('file', file)
        
        const response = await axios.post(`${API_BASE}/upload-spec`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        
        this.currentSpec = response.data
        this.specId = file.name
        this.endpoints = response.data.endpoints
        
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to upload spec'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async enrichEndpoint(endpoint, userContext) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.post(
          `${API_BASE}/enrich-endpoint?spec_id=${this.specId}`,
          {
            endpoint_path: endpoint.path,
            endpoint_method: endpoint.method,
            user_context: userContext
          }
        )
        
        const key = `${endpoint.path}:${endpoint.method}`
        this
        ...