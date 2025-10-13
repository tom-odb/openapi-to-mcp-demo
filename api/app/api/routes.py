from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from ..services.openapi_parser import OpenAPIParser
from ..services.llm_enricher import LLMEnricher
from ..services.tool_generator import ToolGenerator
from ..services.server_generator import ServerGenerator
from ..models.schemas import (
    OpenAPISpec, EnrichmentRequest, Endpoint,
    ToolModel, ServerGenerationRequest, CompositeToolRequest,
    CompositeTool
)
from typing import Dict, Any
import tempfile
import shutil
from pathlib import Path

router = APIRouter()

# Service instances
parser = OpenAPIParser()
enricher = None  # Lazy-loaded to ensure env vars are loaded first
tool_generator = ToolGenerator()
server_generator = ServerGenerator()

def get_enricher():
    """Lazy-load enricher to ensure environment variables are loaded"""
    global enricher
    if enricher is None:
        enricher = LLMEnricher()
    return enricher

# In-memory storage (replace with DB in production)
specs_store: Dict[str, OpenAPISpec] = {}
enrichments_store: Dict[str, Dict[str, Any]] = {}
composite_tools_store: Dict[str, list[CompositeTool]] = {}

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
        composite_tools_store[spec_id] = []

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
        enrichment = await get_enricher().enrich_endpoint(endpoint, request.user_context)

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
        suggestions = await get_enricher().suggest_tools(spec.endpoints)
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Suggestion failed: {str(e)}")

@router.post("/create-composite-tool")
async def create_composite_tool(request: CompositeToolRequest, spec_id: str):
    """Create a composite tool that combines multiple endpoints"""
    
    if spec_id not in specs_store:
        raise HTTPException(status_code=404, detail="Spec not found")
    
    spec = specs_store[spec_id]
    
    try:
        composite_tool = await get_enricher().generate_composite_tool(
            request.use_case_description,
            request.selected_endpoints,
            spec.endpoints
        )
        
        # Store the composite tool
        if spec_id not in composite_tools_store:
            composite_tools_store[spec_id] = []
        composite_tools_store[spec_id].append(composite_tool)
        
        return composite_tool
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Composite tool creation failed: {str(e)}")

@router.get("/composite-tools")
async def get_composite_tools(spec_id: str):
    """Get all composite tools for a spec"""
    
    if spec_id not in specs_store:
        raise HTTPException(status_code=404, detail="Spec not found")
    
    return {"composite_tools": composite_tools_store.get(spec_id, [])}

@router.post("/generate-tools", response_model=ToolModel)
async def generate_tools(spec_id: str, api_name: str, base_url: str):
    """Generate MCP tool definitions from enriched spec and save to JSON file"""

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
        
        # Add composite tools to the model
        if spec_id in composite_tools_store:
            tool_model.composite_tools = composite_tools_store[spec_id]
        
        # Save to JSON file
        output_dir = Path("generated_servers")
        output_dir.mkdir(exist_ok=True)
        tools_file = output_dir / f"{spec_id}_tools.json"
        
        import json
        with open(tools_file, 'w') as f:
            json.dump(tool_model.model_dump(), f, indent=2)
        
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
