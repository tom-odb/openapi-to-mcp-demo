# Declarative MCP Server Architecture

## Overview

The system now uses a **declarative configuration approach** instead of generating inline Python code. This provides a cleaner, more maintainable architecture for creating MCP servers from OpenAPI specifications.

## Architecture Changes

### Old Approach (Code Generation)
- Generated inline Python code with tool handlers embedded in strings
- Each server had unique generated code
- Hard to modify or update tools after generation
- Version control unfriendly (large generated files)

### New Approach (Declarative JSON)
- Tools defined in a **tools.json** file (data, not code)
- **Generic server.py** reads the JSON and dynamically creates tools
- Easy to modify tools by editing JSON
- Version control friendly
- Separation of concerns: configuration vs. runtime

## File Structure

A generated server now contains:

```
my-api-server/
├── server.py           # Generic MCP server (copied from template)
├── tools.json          # Tool definitions (generated from OpenAPI)
├── pyproject.toml      # Python dependencies
├── .env.example        # Environment variable template
└── README.md           # Documentation
```

## Key Components

### 1. Generic Server (`templates/generic_server.py`)

A reusable MCP server that:
- Reads `tools.json` on startup
- Dynamically creates MCP tools from the JSON
- Handles both standard and composite tools
- Makes HTTP requests to the target API

**Key Features:**
- No tool-specific code generation needed
- Supports path parameter substitution
- Handles different HTTP methods (GET, POST, PUT, DELETE, PATCH)
- Configurable via environment variables

### 2. Tools JSON Format

```json
{
  "api_name": "my-api",
  "base_url": "https://api.example.com",
  "tools": [
    {
      "name": "tool_name",
      "description": "Tool description",
      "input_schema": { /* JSON Schema */ },
      "endpoint_mapping": {
        "path": "/path/{param}",
        "method": "get"
      },
      "is_composite": false
    }
  ],
  "composite_tools": [
    {
      "name": "composite_tool_name",
      "description": "Combines multiple endpoints",
      "use_case_description": "...",
      "input_schema": { /* JSON Schema */ },
      "endpoint_mappings": [
        {
          "path": "/path1",
          "method": "get",
          "purpose": "First call"
        },
        {
          "path": "/path2",
          "method": "get",
          "purpose": "Second call"
        }
      ],
      "orchestration_logic": "Description of how calls are combined",
      "is_composite": true
    }
  ]
}
```

### 3. Template Files

Located in `backend/templates/`:

- **`generic_server.py`** - The generic MCP server implementation
- **`README.template.md`** - Template for generated README files
- **`pyproject.template.toml`** - Template for Python project config
- **`.env.template`** - Template for environment variables

### 4. Server Generator (`app/services/server_generator.py`)

Refactored to:
- Copy `generic_server.py` instead of generating code
- Write `tools.json` with tool definitions
- Generate documentation from templates
- Use string replacement for placeholders

## Workflow

### 1. Generate Tools JSON

```
POST /generate-tools?spec_id=XXX&api_name=YYY&base_url=ZZZ
```

Creates:
- `generated_servers/{spec_id}_tools.json`
- Returns ToolModel JSON

### 2. Generate Server Package

```
POST /generate-server
{
  "tool_model": { /* ToolModel JSON */ },
  "server_name": "my-api-server"
}
```

Creates:
```
generated_servers/my-api-server/
├── server.py
├── tools.json
├── pyproject.toml
├── .env.example
└── README.md
```

### 3. Use the Server

```bash
cd generated_servers/my-api-server
pip install -e .
export API_KEY=your-key-here
export TOOLS_CONFIG_PATH=./tools.json
python server.py
```

## Benefits

### ✅ Maintainability
- Modify tools by editing JSON, no code regeneration needed
- Single generic server to maintain and improve
- Clear separation between configuration and runtime logic

### ✅ Version Control
- JSON files are easy to diff and merge
- No large generated code files
- Track tool changes independently from server logic

### ✅ Flexibility
- Add new tools without touching server code
- Update tool descriptions, schemas, or endpoints easily
- Combine multiple OpenAPI specs into one server

### ✅ Debugging
- Easier to understand what the server does
- Tool definitions are human-readable JSON
- Can test tools individually by modifying JSON

### ✅ Reusability
- Same generic server for all APIs
- Templates can be improved once, benefit all servers
- Easy to create custom tool configurations manually

## Composite Tool Support

The generic server fully supports composite tools that combine multiple API endpoints:

1. **Sequential Execution**: Endpoints are called in order
2. **Result Aggregation**: Results from all calls are combined
3. **Error Handling**: Each endpoint call is tracked separately
4. **Rich Context**: Each call includes its purpose and endpoint details

Example composite tool execution:
```
Call 1: GET /users/{user_id}
Purpose: Fetch user profile information
Status: 200
Data: { "id": "123", "name": "John" }

Call 2: GET /users/{user_id}/orders
Purpose: Fetch user's order history
Status: 200
Data: [ { "order_id": "456" } ]
```

## Environment Variables

- **`API_KEY`**: API authentication key (optional)
- **`TOOLS_CONFIG_PATH`**: Path to tools.json (default: `./tools.json`)

## Future Enhancements

Potential improvements to this architecture:

1. **Tool Validation**: Validate tools.json against a schema on server startup
2. **Hot Reloading**: Watch tools.json for changes and reload without restart
3. **Tool Plugins**: Allow custom Python handlers for specific tools
4. **Caching**: Cache API responses for improved performance
5. **Rate Limiting**: Built-in rate limiting for API calls
6. **Authentication Schemes**: Support multiple auth types (OAuth, API key, etc.)
7. **Response Transformations**: Transform API responses before returning to MCP client

## Migration Guide

If you have existing generated servers with inline code:

1. Extract tool definitions to `tools.json` format
2. Replace `server.py` with the generic version
3. Update environment variables
4. Test that all tools work correctly

## Testing

Test the configuration without MCP dependencies:

```bash
cd backend/templates
python test_loader.py
```

This validates:
- JSON can be loaded
- Required fields are present
- Tool structures are correct
- Composite tools are properly defined
