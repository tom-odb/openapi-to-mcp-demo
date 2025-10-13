import yaml
import json
from typing import Dict, Any, List, Optional
from ..models.schemas import OpenAPISpec, Endpoint, Parameter, HTTPMethod

class OpenAPIParser:
    def __init__(self):
        self.raw_spec = None
    
    def parse_spec(self, spec_content: str, file_type: str = "yaml") -> OpenAPISpec:
        """Parse OpenAPI spec from YAML or JSON string"""
        if file_type == "yaml":
            self.raw_spec = yaml.safe_load(spec_content)
        else:
            self.raw_spec = json.loads(spec_content)

        endpoints = self._extract_endpoints(self.raw_spec)

        return OpenAPISpec(
            openapi_version=self.raw_spec.get("openapi", "3.0.0"),
            info=self.raw_spec.get("info", {}),
            servers=self.raw_spec.get("servers", []),
            endpoints=endpoints,
            raw_spec=self.raw_spec
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
        """Extract parameters from endpoint definition, resolving $ref if needed"""
        resolved_params = []
        
        for p in params:
            # Check if this is a reference
            if "$ref" in p:
                # Resolve the reference
                resolved_param = self._resolve_ref(p["$ref"])
                if resolved_param:
                    resolved_params.append(resolved_param)
            else:
                # Direct parameter definition
                resolved_params.append(p)
        
        return [
            Parameter(
                name=p.get("name"),
                in_=p.get("in"),
                description=p.get("description"),
                required=p.get("required", False),
                schema_=p.get("schema", {})
            )
            for p in resolved_params
        ]
    
    def _resolve_ref(self, ref: str) -> Optional[Dict[str, Any]]:
        """Resolve a $ref reference to its actual value"""
        if not ref.startswith("#/"):
            return None
        
        # Split the reference path (e.g., "#/components/parameters/Page")
        parts = ref.lstrip("#/").split("/")
        
        # Navigate through the spec to find the referenced object
        current = self.raw_spec
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        
        return current if isinstance(current, dict) else None
