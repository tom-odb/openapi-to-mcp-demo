# Quick Start: Declarative MCP Servers

## What Changed?

Instead of generating Python code with embedded tool definitions, we now:
1. Generate a **tools.json** file with all tool configurations
2. Copy a **generic server.py** that reads the JSON and creates tools dynamically

## Benefits

- ✅ Edit tools by modifying JSON (no regeneration needed)
- ✅ Version control friendly
- ✅ Easier to debug and understand
- ✅ Single server implementation for all APIs
- ✅ Supports both standard and composite tools

## Usage

### 1. Generate Tools from OpenAPI Spec

Upload your OpenAPI spec and generate tools:

```bash
# Via API
POST /upload-spec (upload your OpenAPI YAML/JSON)
POST /generate-tools?spec_id=YOUR_SPEC&api_name=my-api&base_url=https://api.example.com
```

This creates: `generated_servers/{spec_id}_tools.json`

### 2. Generate Server Package

```bash
POST /generate-server
{
  "tool_model": { /* your tools.json content */ },
  "server_name": "my-api-server"
}
```

This creates:
```
generated_servers/my-api-server/
├── server.py          # Generic MCP server
├── tools.json         # Your tool definitions
├── pyproject.toml     # Python dependencies
├── .env.example       # Environment template
└── README.md          # Documentation
```

### 3. Install and Run

```bash
cd generated_servers/my-api-server

# Install dependencies
pip install -e .

# Configure environment
cp .env.example .env
# Edit .env with your API_KEY

# Run the server
export TOOLS_CONFIG_PATH=./tools.json
export API_KEY=your-api-key-here
python server.py
```

### 4. Use with Claude Desktop

Add to your Claude Desktop config:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "my-api-server": {
      "command": "python",
      "args": ["/full/path/to/generated_servers/my-api-server/server.py"],
      "env": {
        "API_KEY": "your-api-key-here",
        "TOOLS_CONFIG_PATH": "/full/path/to/generated_servers/my-api-server/tools.json"
      }
    }
  }
}
```

## Customizing Tools

### Edit tools.json directly

You can manually edit `tools.json` to:
- Update tool descriptions
- Modify input schemas
- Change endpoint mappings
- Add/remove tools
- Update composite tool orchestration

Example:
```json
{
  "api_name": "my-api",
  "base_url": "https://api.example.com",
  "tools": [
    {
      "name": "get_user",
      "description": "Get user by ID (updated description!)",
      "input_schema": {
        "type": "object",
        "properties": {
          "user_id": { "type": "string" }
        },
        "required": ["user_id"]
      },
      "endpoint_mapping": {
        "path": "/users/{user_id}",
        "method": "get"
      }
    }
  ]
}
```

**No need to regenerate the server!** Just restart it to pick up changes.

## Composite Tools

Composite tools combine multiple API endpoints into a single MCP tool using **LLM-powered orchestration**:

```json
{
  "composite_tools": [
    {
      "name": "get_user_with_orders",
      "description": "Get user info and their orders",
      "orchestration_logic": "Fetch user profile, then orders, combine results",
      "input_schema": {
        "type": "object",
        "properties": {
          "user_id": { "type": "string" }
        },
        "required": ["user_id"]
      },
      "endpoint_mappings": [
        {
          "path": "/users/{user_id}",
          "method": "get",
          "purpose": "Fetch user profile"
        },
        {
          "path": "/users/{user_id}/orders",
          "method": "get",
          "purpose": "Fetch order history"
        }
      ]
    }
  ]
}
```

**How it works:** An LLM agent (Claude) orchestrates the API calls intelligently:
- Executes endpoints in the correct order
- Extracts data from responses to use in subsequent calls
- Handles dynamic iteration (e.g., calling `/products/{id}` for each product)
- Aggregates and combines results

**Requirements:**
- Set `ANTHROPIC_API_KEY` environment variable
- Composite tools won't work without it

See [COMPOSITE_TOOL_ORCHESTRATION.md](COMPOSITE_TOOL_ORCHESTRATION.md) for detailed documentation.

## Testing

Validate your tools.json:

```bash
cd backend/templates
cp /path/to/your/tools.json test_tools.json
python test_loader.py
```

## File Structure

### Generated Server Files

| File | Purpose | Can Edit? |
|------|---------|-----------|
| `server.py` | Generic MCP server | No (copied from template) |
| `tools.json` | Tool definitions | ✅ Yes! Edit freely |
| `pyproject.toml` | Python deps | Rarely needed |
| `.env.example` | Env template | No (copy to .env) |
| `README.md` | Documentation | Optional |

### Only Edit tools.json

The beauty of this approach: **you only need to edit `tools.json`** to change your tools!

## Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `TOOLS_CONFIG_PATH` | No | `./tools.json` | Path to tools config |
| `API_KEY` | Maybe | None | API authentication |
| `ANTHROPIC_API_KEY` | For composite tools | None | LLM orchestration for composite tools |

## Troubleshooting

### Server won't start
- Check `tools.json` is valid JSON
- Verify `TOOLS_CONFIG_PATH` points to the right file
- Run `python test_loader.py` to validate structure

### Tools not appearing
- Check tool names are unique
- Verify input_schema is valid JSON Schema
- Ensure endpoint_mapping has `path` and `method`

### API calls failing
- Verify `base_url` in tools.json
- Check `API_KEY` environment variable
- Test API endpoint directly with curl first

### Composite tool issues
- Ensure all endpoints in `endpoint_mappings` are valid
- Check that required parameters are in `input_schema`
- Verify orchestration_logic describes the flow

## Examples

See `backend/templates/test_tools.json` for a complete example with:
- Standard tools
- Composite tools
- Different HTTP methods
- Path parameters
- Query parameters

## Next Steps

1. ✅ Upload your OpenAPI spec
2. ✅ Generate tools.json
3. ✅ Generate server package
4. ✅ Customize tools.json as needed
5. ✅ Run and test your MCP server
6. ✅ Add to Claude Desktop config

For detailed architecture info, see `DECLARATIVE_ARCHITECTURE.md`.
