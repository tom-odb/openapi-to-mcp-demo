# Start resources

API:

```bash
cd ~/projects/demos/openapi-to-mcp/api && uv run uvicorn app.main:app --reload --port 8000
```

UI:

```bash
cd ~/projects/demos/openapi-to-mcp/ui && npm run dev
```

CRM:

```bash
cd ~/projects/demos/openapi-to-mcp/crm && uv run uvicorn main:app --reload --port 3000
```

# Upload 

[OpenAPI Spec](\\wsl.localhost\Ubuntu\home\tom\projects\demos\openapi-to-mcp\crm\docs)

# Download & install

1. extract zip
2. move to demos folder
3. uv install
4. update env

# Add config to Claude Desktop

```json
{
  "mcpServers": {
    "products": {
      "command": "/Users/opdebto/Projects/demos/products-mcp/.venv/Scripts/python",
      "args": [
        "/Users/opdebto/Projects/demos/products-mcp/server.py"
      ],
      "cwd": "/Users/opdebto/Projects/demos/products-mcp"
    }
  }
}
```