# Composite Tools Feature

## Overview
Added the ability to create composite tools that combine multiple API endpoints into a single MCP tool. This allows you to define use cases that require orchestrating multiple API calls in sequence.

## Example Use Case
Instead of having separate tools for:
- `GET /customers/{id}` - Get customer details
- `GET /orders?customerId={id}` - Get customer orders

You can now create a composite tool like:
- `get_customer_with_orders` - Retrieves customer information along with all their orders in a single tool call

## How It Works

### 1. Workflow Update
The workflow now includes 5 steps instead of 4:
1. Upload Spec
2. Enrich Endpoints (existing)
3. **Composite Tools (NEW)** - Create multi-endpoint tools
4. Generate Tools
5. Download Server

### 2. User Experience

#### Creating a Composite Tool:
1. Navigate to the "Composite Tools" step (step 3)
2. Write a use case description (e.g., "Retrieve orders with full customer information")
3. Select 2+ endpoints to combine (checkboxes)
4. Click "Create Composite Tool"
5. The LLM analyzes your use case and selected endpoints to generate:
   - Tool name
   - Description
   - Input schema (combined parameters)
   - Orchestration logic (how to call APIs in sequence)

#### Viewing Created Tools:
- Created composite tools are displayed at the top of the screen
- Each shows:
  - Name and description
  - Use case it solves
  - Endpoints used (with their purpose in the orchestration)
  - Orchestration logic (step-by-step execution plan)

### 3. Backend Changes

#### New Models (`schemas.py`):
- `EndpointReference` - Reference to an endpoint by path and method
- `CompositeTool` - Complete composite tool definition with orchestration logic
- `CompositeToolRequest` - Request payload for creating a composite tool
- Updated `ToolModel` to include `composite_tools` array

#### New API Endpoints (`routes.py`):
- `POST /create-composite-tool` - Create a new composite tool
- `GET /composite-tools` - Get all composite tools for a spec

#### LLM Service (`llm_enricher.py`):
- `generate_composite_tool()` - Uses Claude to analyze use case and generate composite tool definition
- Builds comprehensive prompts with endpoint details
- Parses LLM response to extract tool definition

#### Server Generation (`server_generator.py`):
- Composite tools are included in the tool list
- Generates composite handlers that:
  - Execute multiple API calls in sequence
  - Collect results from each call
  - Combine results into a unified response
  - Include orchestration logic as comments

### 4. Frontend Changes

#### New Component (`CompositeToolCreator.vue`):
- Checkbox grid for selecting endpoints
- Textarea for use case description
- Display of created composite tools
- Navigation back/forward between steps

#### Updated Components:
- `App.vue` - Added step 3 for composite tools
- `ToolPreview.vue` - Shows composite tools separately from standard tools
- `converter.js` store - State and actions for composite tools

## Generated Code Example

For a composite tool that gets customer with orders, the generated server code will include:

```python
async def get_customer_with_orders_composite_handler(arguments: dict) -> list[TextContent]:
    """Composite handler for get_customer_with_orders"""
    # Orchestration: 1) Call GET /customers/{id} to get customer details,
    # 2) Use customer_id to call GET /orders?customerId={id} to get orders

    results = []
    async with httpx.AsyncClient() as client:
        # Call 1: GET /customers/{id}
        response_1 = await client.get(f"{API_BASE_URL}/customers/{arguments['id']}")
        results.append({...})

        # Call 2: GET /orders
        response_2 = await client.get(f"{API_BASE_URL}/orders?customerId={arguments['id']}")
        results.append({...})

    # Combine and return results
    return [TextContent(type="text", text=combined_output)]
```

## Benefits

1. **Reduced Complexity** - Complex workflows become single tool calls
2. **Better Context** - AI assistants get all needed data in one call
3. **Domain Knowledge** - Your expertise guides how endpoints should be combined
4. **Flexibility** - Mix and match any endpoints to solve specific use cases
5. **No Code Required** - LLM generates the orchestration logic

## Technical Notes

- Composite tools require at least 2 endpoints
- Use case description should be clear and specific
- The LLM determines parameter requirements and data flow
- Generated handlers execute calls sequentially (not in parallel)
- Error handling is built into each generated handler
- Composite tools appear alongside standard tools in the final MCP server
