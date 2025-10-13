# Before & After: Architecture Comparison

## Old Approach: Code Generation

### What happened when you generated a server:

```
1. Parse OpenAPI spec
2. Generate tool definitions
3. Generate Python code with embedded tools
   └─ server.py (1000+ lines of generated code)
      ├─ Hardcoded tool definitions
      ├─ Hardcoded handlers for each tool
      └─ Template strings everywhere
```

### Generated Server Structure:
```
my-api-server/
├── server.py          # 1000+ lines of generated Python code
├── pyproject.toml
├── .env.example
└── README.md
```

### Example Generated Code:
```python
# Generated server.py (simplified)
async def get_user_handler(arguments: dict) -> list[TextContent]:
    """Handler for get_user"""
    method = "GET"
    path = "/users/{user_id}"
    # ... hardcoded logic ...
    
async def list_products_handler(arguments: dict) -> list[TextContent]:
    """Handler for list_products"""
    method = "GET"
    path = "/products"
    # ... hardcoded logic ...

# ... hundreds more lines ...
```

### Problems:
- ❌ Hard to modify tools (requires regeneration)
- ❌ Large generated files (bad for version control)
- ❌ Each server has unique generated code
- ❌ Can't easily update descriptions or schemas
- ❌ Template maintenance nightmare

---

## New Approach: Declarative JSON

### What happens when you generate a server:

```
1. Parse OpenAPI spec
2. Generate tool definitions
3. Save tools as JSON
4. Copy generic server.py (reads JSON)
```

### Generated Server Structure:
```
my-api-server/
├── server.py          # Generic runtime (copied, not generated)
├── tools.json         # Tool definitions (YOUR DATA)
├── pyproject.toml
├── .env.example
└── README.md
```

### Example tools.json:
```json
{
  "api_name": "my-api",
  "base_url": "https://api.example.com",
  "tools": [
    {
      "name": "get_user",
      "description": "Get user by ID",
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
    },
    {
      "name": "list_products",
      "description": "List all products",
      "input_schema": { "type": "object", "properties": {} },
      "endpoint_mapping": {
        "path": "/products",
        "method": "get"
      }
    }
  ],
  "composite_tools": [
    {
      "name": "get_user_with_orders",
      "description": "Get user and their orders",
      "endpoint_mappings": [
        { "path": "/users/{user_id}", "method": "get" },
        { "path": "/users/{user_id}/orders", "method": "get" }
      ],
      "orchestration_logic": "Fetch user, then orders"
    }
  ]
}
```

### Generic server.py (same for all APIs):
```python
# Generic server that reads tools.json
class GenericMCPServer:
    def __init__(self, tools_config_path: str):
        self.config = self._load_config(tools_config_path)
        # Dynamically create tools from JSON
        
    async def _handle_standard_tool(self, tool, arguments):
        # Generic handler for any tool
        # Reads endpoint mapping from JSON
        # Makes HTTP request
        
    async def _handle_composite_tool(self, tool, arguments):
        # Generic handler for composite tools
        # Executes multiple endpoints in sequence
```

### Benefits:
- ✅ Edit `tools.json` to modify tools (no regeneration!)
- ✅ Small, readable JSON files (great for version control)
- ✅ Single generic server for all APIs
- ✅ Easy to update descriptions, schemas, endpoints
- ✅ Template maintenance is simple
- ✅ Can manually create custom tools

---

## Side-by-Side Comparison

| Aspect | Old (Code Gen) | New (Declarative) |
|--------|----------------|-------------------|
| **Tool Storage** | Embedded in Python code | JSON file |
| **Server Code** | Generated (unique per API) | Generic (same for all APIs) |
| **File Size** | 1000+ lines | ~200 lines + JSON |
| **Modify Tools** | Regenerate entire server | Edit JSON file |
| **Version Control** | Difficult (large generated files) | Easy (small JSON files) |
| **Debugging** | Hard (generated code) | Easy (readable JSON) |
| **Add New Tool** | Regenerate all code | Add JSON object |
| **Update Description** | Regenerate all code | Edit JSON string |
| **Composite Tools** | Generated code for each | Generic handler |
| **Maintenance** | Update template, regenerate all | Update generic server once |

---

## Migration Example

### Before (Generated Code):
```python
# server.py (generated, 50 lines per tool)
@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "get_user":
        return await get_user_handler(arguments)
    if name == "list_products":
        return await list_products_handler(arguments)
    # ... 10 more ifs ...

async def get_user_handler(arguments: dict):
    method = "GET"
    path = "/users/{user_id}"
    for key, value in arguments.items():
        path = path.replace(f"{{{key}}}", str(value))
    url = f"{API_BASE_URL}{path}"
    # ... more code ...

async def list_products_handler(arguments: dict):
    # ... duplicate code ...
```

### After (Declarative):
```json
// tools.json (clean, readable data)
{
  "tools": [
    {
      "name": "get_user",
      "endpoint_mapping": { "path": "/users/{user_id}", "method": "get" }
    },
    {
      "name": "list_products",
      "endpoint_mapping": { "path": "/products", "method": "get" }
    }
  ]
}
```

```python
# server.py (generic, handles ANY tool)
async def _handle_standard_tool(self, tool, arguments):
    method = tool["endpoint_mapping"]["method"]
    path = tool["endpoint_mapping"]["path"]
    # Generic logic works for all tools!
```

---

## Real-World Example

### Scenario: Need to update a tool description

**Old Way:**
1. Update OpenAPI spec or enrichment
2. Re-run tool generation
3. Re-run server generation
4. Generate 1000+ lines of new code
5. Replace entire server.py file
6. Git diff shows 1000+ line change
7. Redeploy server

**New Way:**
1. Edit one line in tools.json
2. Git diff shows 1 line change
3. Restart server (reads new JSON)
4. Done!

---

## The Power of Declarative

### You can now:

✅ **Version control your tools** like configuration
✅ **A/B test different descriptions** by swapping JSON files
✅ **Manually craft custom tools** without touching code
✅ **Share tool configs** between teams
✅ **Generate tools from multiple sources** (OpenAPI, GraphQL, manual)
✅ **Hot-reload tools** (future enhancement)
✅ **Validate tools** against a schema
✅ **Transform tools programmatically** (it's just JSON!)

---

## Summary

| Old Approach | New Approach |
|--------------|--------------|
| Tools = Code | Tools = Data |
| Generate Code | Read JSON |
| Hard to Change | Easy to Change |
| Each API Unique | Generic for All |
| Version Control ❌ | Version Control ✅ |
| Debugging Hard | Debugging Easy |

**The future is declarative! 🚀**
