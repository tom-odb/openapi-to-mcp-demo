import anthropic
import os
import json
from typing import Dict, Any, List
from ..models.schemas import Endpoint, EndpointReference, CompositeTool

class LLMEnricher:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        self.client = anthropic.Anthropic(api_key=api_key)

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

    async def generate_composite_tool(
        self, 
        use_case_description: str,
        selected_endpoints: List[EndpointReference],
        all_endpoints: List[Endpoint]
    ) -> CompositeTool:
        """Use Claude to generate a composite tool that combines multiple endpoints"""
        
        # Get full endpoint details
        endpoint_details = []
        for ref in selected_endpoints:
            endpoint = next(
                (ep for ep in all_endpoints 
                 if ep.path == ref.path and ep.method == ref.method),
                None
            )
            if endpoint:
                endpoint_details.append(endpoint)
        
        prompt = self._build_composite_tool_prompt(use_case_description, endpoint_details)
        
        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text
        
        # Parse the JSON response
        try:
            # Extract JSON from response (handling markdown code blocks)
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            else:
                json_str = response_text.strip()
            
            tool_data = json.loads(json_str)
            
            # Build endpoint mappings
            endpoint_mappings = [
                {
                    "path": ep.path,
                    "method": ep.method.value,
                    "operation_id": ep.operation_id,
                    "purpose": tool_data.get("endpoint_purposes", {}).get(f"{ep.method.value}:{ep.path}", "")
                }
                for ep in endpoint_details
            ]
            
            return CompositeTool(
                name=tool_data["name"],
                description=tool_data["description"],
                use_case_description=use_case_description,
                input_schema=tool_data["input_schema"],
                endpoint_mappings=endpoint_mappings,
                orchestration_logic=tool_data["orchestration_logic"],
                is_composite=True
            )
        except Exception as e:
            raise ValueError(f"Failed to parse composite tool response: {str(e)}\nResponse: {response_text}")
    
    def _build_composite_tool_prompt(self, use_case: str, endpoints: List[Endpoint]) -> str:
        """Build prompt for generating composite tool"""
        
        endpoints_info = []
        for ep in endpoints:
            params_str = ", ".join([
                f"{p.name} ({p.in_})"
                for p in ep.parameters
            ]) or "None"
            
            endpoints_info.append(f"""
Endpoint: {ep.method.value.upper()} {ep.path}
Operation ID: {ep.operation_id or 'N/A'}
Summary: {ep.summary or 'None'}
Description: {ep.enriched_description or ep.description or 'None'}
Business Context: {ep.business_context or 'None'}
Parameters: {params_str}
""")
        
        endpoints_str = "\n---\n".join(endpoints_info)
        
        return f"""You are designing a composite MCP tool that combines multiple API endpoints to solve a specific use case.

USE CASE:
{use_case}

AVAILABLE ENDPOINTS:
{endpoints_str}

Your task is to design a composite tool that orchestrates these endpoints to fulfill the use case. The tool should:
1. Have a clear, descriptive name (snake_case)
2. Take the minimal necessary input parameters
3. Call the endpoints in the right sequence
4. Pass data between calls as needed
5. Return the combined result

Respond with a JSON object with this exact structure:
{{
  "name": "tool_name_in_snake_case",
  "description": "Clear description of what this composite tool does",
  "input_schema": {{
    "type": "object",
    "properties": {{
      "param_name": {{
        "type": "string|number|boolean",
        "description": "Parameter description"
      }}
    }},
    "required": ["required_param_names"]
  }},
  "endpoint_purposes": {{
    "get:/endpoint/path": "Why this endpoint is called and what data it provides",
    "post:/another/path": "Purpose of this call"
  }},
  "orchestration_logic": "Step-by-step description of how to orchestrate the API calls: 1) Call endpoint A with parameter X to get Y, 2) Use Y from step 1 to call endpoint B with parameter Z, 3) Combine results from both calls and return..."
}}

Ensure the orchestration_logic is detailed and explains the data flow between API calls.
"""

