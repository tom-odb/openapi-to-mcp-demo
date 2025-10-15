# From OpenAPI Spec to Working MCP Server: A Complete Guide

This guide walks through the complete process of converting an existing OpenAPI specification into a functional Model Context Protocol (MCP) server using the tools in this repository.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Setup](#setup)
4. [The Conversion Process](#the-conversion-process)
5. [Using Your Generated Server](#using-your-generated-server)
6. [How It Works Under the Hood](#how-it-works-under-the-hood)
7. [Example Walkthrough](#example-walkthrough)
8. [Advanced Features](#advanced-features)

---

## Overview

The OpenAPI-to-MCP converter transforms existing REST APIs into MCP servers that can be used with Claude and other AI assistants. The process is:

1. **Upload** an OpenAPI specification
2. **Enrich** endpoints with AI-generated descriptions and business context
3. **Generate** MCP tool definitions from the enriched spec
4. **Create** a complete, working MCP server package
5. **Deploy** the server and connect it to Claude Desktop

The system uses a declarative approach: tools are defined in JSON, and a generic Python server runtime executes them by making HTTP requests to your API.

---

## Prerequisites

Before starting, ensure you have:

- **Python 3.11+** installed
- **Node.js 18+** installed
- **An Anthropic API key** (for AI enrichment)
- **An OpenAPI 3.0+ specification** for the API you want to convert
- **Access to the API** you're converting (for testing the generated server)

---

## Setup

### 1. Clone and Set Up the Converter Service

```bash
# Clone the repository (or navigate to it if already cloned)
cd openapi-to-mcp

# Set up the backend (converter API)
cd api

# Using uv (recommended - faster)
uv sync

# OR using pip
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure your Anthropic API key
cp .env.example .env
# Edit .env and add: ANTHROPIC_API_KEY=your-key-here
```

### 2. Start the Backend Service

```bash
# From the api/ directory
uv run uvicorn app.main:app --reload --port 8000

# OR if using pip
uvicorn app.main:app --reload --port 8000
```

The converter API will be available at `http://localhost:8000`.

### 3. Start the Web Interface

```bash
# In a new terminal, navigate to the ui/ directory
cd ui

# Install dependencies (first time only)
npm install

# Start the development server
npm run dev
```

The web interface will be available at `http://localhost:5173`.

### 4. (Optional) Start the Example CRM API

For testing purposes, this repository includes a sample CRM API:

```bash
# In a new terminal
cd crm

# Using uv
uv sync
uv run uvicorn main:app --reload --port 8001

# OR using pip
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

The CRM API will be available at `http://localhost:8001` with docs at `http://localhost:8001/docs`.

---

## The Conversion Process

### Step 1: Upload Your OpenAPI Specification

1. **Open the web interface** at `http://localhost:5173`

2. **Prepare your OpenAPI spec**:
   - Can be in YAML or JSON format
   - Must be OpenAPI 3.0 or later
   - Should include endpoint paths, methods, and parameter definitions
   - Example: Use `crm/docs/crm_openapi.yaml` to test

3. **Upload the specification**:
   - Click "Upload OpenAPI Spec" or drag-and-drop your file
   - The system will parse the spec and extract all endpoints

4. **Review extracted endpoints**:
   - All API endpoints are listed with their HTTP methods
   - Endpoints lacking descriptions are marked as "needs enrichment"
   - You'll see paths, methods, parameters, and existing descriptions

**What happens behind the scenes:**
- `OpenAPIParser` parses the YAML/JSON
- Extracts paths, methods, parameters, request bodies, and responses
- Resolves `$ref` references to components
- Identifies endpoints that need better descriptions

### Step 2: Enrich Endpoints with AI

Endpoints often have minimal or technical descriptions that don't help AI assistants understand *when* to use them. The enrichment process adds business context.

1. **Select an endpoint** that needs enrichment (marked with indicator)

2. **Add business context** (optional but recommended):
   - Describe what the endpoint is used for in your domain
   - Explain typical use cases or scenarios
   - Example: "This endpoint is used by sales teams to quickly find customer order history"

3. **Click "Enrich with AI"**:
   - The system sends the endpoint details to Claude
   - Claude generates:
     - **Technical description**: What the endpoint does
     - **Business context**: When and why to use it
   - The enriched content is stored and associated with the endpoint

4. **Review and edit** the generated descriptions if needed

5. **Repeat** for other endpoints you want to improve

**What happens behind the scenes:**
- `LLMEnricher` constructs a prompt with endpoint details
- Sends to Claude API (claude-sonnet-4-20250514)
- Parses structured response into description + business context
- Stores enrichment data in memory (associated with spec)

### Step 3: Generate MCP Tool Definitions

Once endpoints are enriched, convert them into MCP tool definitions.

1. **Configure API details**:
   - **API Name**: A short identifier (e.g., "crm", "products")
   - **Base URL**: The root URL of your API (e.g., "http://localhost:8001")

2. **Click "Generate Tool Definitions"**

3. **Review the generated tools**:
   - Each endpoint becomes an MCP tool
   - Tool names are derived from `operationId` or generated from the path
   - Input schemas are built from parameters and request bodies
   - Descriptions include enriched content

**What happens behind the scenes:**
- `ToolGenerator` processes each endpoint
- Converts parameters to JSON Schema format
- Merges query params, path params, and request body into input schema
- Creates tool definitions with `endpoint_mapping` (path + method)
- Produces a `ToolModel` with all tools and API metadata

### Step 4: Generate the MCP Server

Now create a complete, runnable MCP server package.

1. **Provide a server name** (e.g., "crm-mcp", "products-api")

2. **Click "Generate Server"**

3. **Download the generated ZIP file**

4. **Review what's included**:
   - `server.py`: Generic MCP server runtime
   - `tools.json`: Declarative tool definitions (your API's tools)
   - `pyproject.toml`: Python dependencies
   - `README.md`: Setup and usage instructions
   - `.env.example`: Environment variable template

**What happens behind the scenes:**
- `ServerGenerator` creates a new directory in `generated-servers/`
- Copies the generic server template (`server.template.py`)
- Writes `tools.json` with all tool definitions
- Generates `README.md`, `pyproject.toml`, and `.env.example` from templates
- Creates a ZIP archive for download

### Step 5 (Optional): Create Composite Tools

Composite tools combine multiple API endpoints into single, powerful tools that orchestrate complex workflows.

1. **Click "Create Composite Tool"**

2. **Describe the use case**:
   - Example: "Search for products and create an order with selected items"
   - Example: "Find a customer by email and retrieve their order history"

3. **Select the endpoints** to include in the composite tool

4. **Click "Generate"**:
   - Claude analyzes the endpoints and use case
   - Creates a composite tool with:
     - Combined input schema
     - Orchestration logic
     - Multiple endpoint mappings

5. **Review and add** to your tool set

**What happens behind the scenes:**
- `LLMEnricher.generate_composite_tool()` sends endpoint details to Claude
- Claude creates a tool that coordinates multiple API calls
- The composite tool uses LLM orchestration at runtime
- Stores in `composite_tools` array in the ToolModel

---

## Using Your Generated Server

### Installation

1. **Extract the downloaded ZIP file**:
   ```bash
   unzip your-server-name.zip
   cd your-server-name
   ```

2. **Install dependencies**:
   ```bash
   pip install -e .
   ```

   This installs:
   - `mcp`: MCP server SDK
   - `httpx`: HTTP client for API requests
   - `anthropic`: For composite tool orchestration
   - `python-dotenv`: Environment variable management

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add:
   # API_KEY=your-api-key (if your API requires authentication)
   # ANTHROPIC_API_KEY=your-key (if using composite tools)
   ```

### Running the Server

**Test locally:**
```bash
python server.py
```

You should see:
```
[MCP] Loading tools config from: tools.json
[MCP] Starting server for API: your-api-name
[MCP] Base URL: http://your-api-url
[MCP] Standard tools: 5 | Composite tools: 1
[MCP] Server is initializing...
```

### Connecting to Claude Desktop

1. **Locate your Claude Desktop config**:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. **Add your server**:
   ```json
   {
     "mcpServers": {
       "your-server-name": {
         "command": "python",
         "args": ["/absolute/path/to/your-server-name/server.py"],
         "env": {
           "API_KEY": "your-api-key-here"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop**

4. **Verify connection**:
   - Look for the MCP tools icon in Claude
   - Your tools should be listed and available

### Testing Your Server

Ask Claude to:
- "List available tools" - should show your converted endpoints
- "Get products from the API" - tests a GET endpoint
- "Create a new customer with email test@example.com" - tests a POST endpoint

---

## How It Works Under the Hood

### Architecture Overview

```
OpenAPI Spec → Parser → Enricher → Tool Generator → Server Generator
                                                            ↓
                                              Generic Server + tools.json
                                                            ↓
                                              MCP Server (runs with Claude)
```

### Key Components

#### 1. OpenAPI Parser (`openapi_parser.py`)

**Purpose**: Parse OpenAPI specifications and extract endpoint information.

**Key functions**:
- `parse_spec()`: Loads YAML/JSON and extracts structured data
- `_extract_endpoints()`: Iterates through paths and methods
- `_extract_parameters()`: Resolves parameters including `$ref` references
- `_resolve_ref()`: Follows JSON references to component definitions

**Output**: `OpenAPISpec` object with:
- API metadata (title, version, servers)
- List of `Endpoint` objects
- Raw spec for reference

#### 2. LLM Enricher (`llm_enricher.py`)

**Purpose**: Use Claude to enhance endpoint descriptions with business context.

**Key functions**:
- `enrich_endpoint()`: Generates descriptions for a single endpoint
- `suggest_tools()`: Recommends which endpoints make good MCP tools
- `generate_composite_tool()`: Creates multi-endpoint orchestration tools

**Prompt strategy**:
- Provides endpoint details (path, method, parameters)
- Includes user-supplied business context
- Requests structured output (DESCRIPTION + BUSINESS CONTEXT)
- Uses Claude Sonnet 4 for high-quality generation

**Output**: Enriched descriptions that help AI assistants understand:
- What the endpoint does technically
- When it should be used
- Why it's relevant in business workflows

#### 3. Tool Generator (`tool_generator.py`)

**Purpose**: Convert enriched endpoints into MCP tool definitions.

**Key functions**:
- `generate_tools()`: Processes all endpoints into tools
- `_endpoint_to_tool()`: Converts single endpoint to MCP tool
- `_build_input_schema()`: Creates JSON Schema from parameters and request body

**Tool structure**:
```json
{
  "name": "operationId or generated name",
  "description": "enriched description + business context",
  "input_schema": {
    "type": "object",
    "properties": { /* parameters as JSON Schema */ },
    "required": [ /* required parameter names */ ]
  },
  "endpoint_mapping": {
    "path": "/api/endpoint/{id}",
    "method": "get"
  }
}
```

**Schema generation**:
- Query parameters → top-level properties
- Path parameters → top-level properties
- Request body properties → flattened into top-level
- Types converted from OpenAPI to JSON Schema

#### 4. Server Generator (`server_generator.py`)

**Purpose**: Create a complete MCP server package from tool definitions.

**Key functions**:
- `generate_server()`: Orchestrates file generation
- `_generate_readme()`: Creates documentation from template
- `_generate_pyproject()`: Creates dependency manifest
- `_generate_env_example()`: Creates environment config template

**Generated files**:

1. **`server.py`** (copied from template):
   - Generic MCP server implementation
   - Reads `tools.json` at startup
   - Handles `list_tools()` and `call_tool()` MCP methods
   - Makes HTTP requests based on endpoint mappings
   - Supports both standard and composite tools

2. **`tools.json`**:
   - Declarative tool definitions
   - API metadata (name, base_url)
   - Array of standard tools
   - Array of composite tools (if any)

3. **`README.md`**:
   - Server-specific setup instructions
   - List of available tools
   - Configuration requirements
   - Claude Desktop integration steps

4. **`pyproject.toml`**:
   - Python package metadata
   - Dependencies (mcp, httpx, anthropic, etc.)
   - Entry points and build configuration

#### 5. Generic MCP Server Runtime (`server.template.py`)

**Purpose**: Universal server that can run any API's tool definitions.

**How it works**:

1. **Initialization**:
   - Loads `tools.json` from the same directory
   - Reads API name, base URL, and tool definitions
   - Checks for required environment variables
   - Initializes MCP Server instance

2. **Tool listing**:
   - Reads tools array from config
   - Converts to MCP Tool objects
   - Returns to Claude via MCP protocol

3. **Tool execution** (standard tools):
   - Looks up tool by name
   - Gets `endpoint_mapping` (path + method)
   - Substitutes path parameters (e.g., `{id}` → actual value)
   - Makes HTTP request with appropriate method:
     - GET/DELETE: Parameters in query string
     - POST/PUT/PATCH: Parameters in JSON body
   - Returns API response to Claude

4. **Tool execution** (composite tools):
   - Uses LLM orchestration (Claude)
   - Provides available standard tools as context
   - Executes multiple API calls in sequence
   - Aggregates results intelligently

**Key features**:
- No code generation required (pure configuration)
- Supports all HTTP methods
- Handles path parameters, query params, and request bodies
- Includes error handling and logging
- Works with any API that matches the tool definitions

### Data Flow Example

Let's trace a single endpoint through the system:

**Input OpenAPI endpoint**:
```yaml
/products/{id}:
  get:
    operationId: getProduct
    summary: Get product by ID
    parameters:
      - name: id
        in: path
        required: true
        schema:
          type: string
```

**After parsing**:
```python
Endpoint(
    path="/products/{id}",
    method=HTTPMethod.get,
    operation_id="getProduct",
    summary="Get product by ID",
    parameters=[
        Parameter(name="id", in_="path", required=True, schema_={"type": "string"})
    ]
)
```

**After enrichment**:
```python
Endpoint(
    # ... same as above, plus:
    enriched_description="Retrieves detailed information about a specific product including price, inventory, and description.",
    business_context="Use this when a customer asks about a specific product or when you need to verify product details before creating an order."
)
```

**After tool generation**:
```json
{
  "name": "getProduct",
  "description": "Retrieves detailed information about a specific product including price, inventory, and description.\n\nBusiness Context: Use this when a customer asks about a specific product or when you need to verify product details before creating an order.",
  "input_schema": {
    "type": "object",
    "properties": {
      "id": {
        "type": "string",
        "description": "Product ID"
      }
    },
    "required": ["id"]
  },
  "endpoint_mapping": {
    "path": "/products/{id}",
    "method": "get"
  }
}
```

**At runtime** (when Claude calls the tool):
```python
# Claude calls: getProduct(id="ABC123")
# Server:
1. Finds tool "getProduct" in tools.json
2. Gets endpoint_mapping: path="/products/{id}", method="get"
3. Substitutes: "/products/ABC123"
4. Makes HTTP GET to: http://base-url/products/ABC123
5. Returns JSON response to Claude
```

---

## Example Walkthrough

Let's convert the included CRM API to an MCP server.

### 1. Start Services

```bash
# Terminal 1: Converter API
cd api
uv run uvicorn app.main:app --reload --port 8000

# Terminal 2: Web UI
cd ui
npm run dev

# Terminal 3: Example CRM API
cd crm
uv run uvicorn main:app --reload --port 8001
```

### 2. Upload CRM Spec

1. Open `http://localhost:5173`
2. Upload `crm/docs/crm_openapi.yaml`
3. See 12+ endpoints extracted:
   - GET /products
   - POST /products
   - GET /products/{id}
   - GET /customers
   - POST /orders
   - etc.

### 3. Enrich Key Endpoints

**Example: GET /customers**

- Original: "Retrieve a paginated list of customers"
- Add context: "Sales reps use this to search for existing customers before creating orders"
- Click "Enrich with AI"
- Result:
  - Description: "Retrieves a paginated list of customers with optional filtering by email or name. Returns customer ID, name, email, and account creation date."
  - Business Context: "Use this endpoint when sales representatives need to search for existing customers before creating orders, or when generating customer reports for management."

**Example: POST /orders**

- Original: "Create a new order"
- Add context: "This is the primary order creation flow used by the sales team"
- Click "Enrich with AI"
- Result:
  - Description: "Creates a new order for an existing customer with specified products and quantities. Validates customer exists and products are in stock before order creation."
  - Business Context: "Use this endpoint when a customer is ready to purchase. Requires valid customer ID and product IDs. This is the core transaction endpoint for the sales process."

### 4. Generate Tools

- API Name: `crm`
- Base URL: `http://localhost:8001`
- Click "Generate Tool Definitions"

Review the generated tools:
- `listProducts` - search products
- `getProduct` - get product details
- `listCustomers` - search customers
- `createOrder` - create a new order
- etc.

### 5. Create Composite Tool (Optional)

- Use case: "Search for products by category and create an order for a customer"
- Select endpoints:
  - GET /products
  - GET /customers
  - POST /orders
- Click "Generate"
- Review composite tool: `search_and_order`

### 6. Generate Server

- Server name: `crm-mcp`
- Click "Generate Server"
- Download `crm-mcp.zip`

### 7. Install and Test

```bash
# Extract
unzip crm-mcp.zip
cd crm-mcp

# Install
pip install -e .

# Configure (CRM API doesn't need API key, but set it anyway)
cp .env.example .env

# Test
python server.py
```

### 8. Connect to Claude

Add to Claude Desktop config:
```json
{
  "mcpServers": {
    "crm": {
      "command": "python",
      "args": ["/absolute/path/to/crm-mcp/server.py"]
    }
  }
}
```

Restart Claude Desktop and test:
- "What products are available?"
- "Find customers with 'john' in their name"
- "Create an order for customer ID 1 with product ID 2"

---

## Advanced Features

### Composite Tools Deep Dive

Composite tools orchestrate multiple API calls to accomplish complex tasks. They're useful for:

- **Workflows**: "Find customer, check inventory, create order"
- **Aggregations**: "Get order and all related customer/product details"
- **Conditional logic**: "Search products, if found then add to cart"

**How they work**:

1. **Define use case**: Describe what the composite tool should accomplish
2. **Select endpoints**: Choose 2+ endpoints that work together
3. **LLM generates**: Claude creates:
   - Combined input schema
   - Orchestration instructions
   - Endpoint call sequence
4. **Runtime execution**:
   - Generic server receives composite tool call
   - Uses Anthropic API to orchestrate calls
   - Makes sequential HTTP requests
   - Aggregates and returns results

**Example composite tool**:
```json
{
  "name": "search_and_purchase",
  "description": "Search for products and create an order",
  "input_schema": {
    "type": "object",
    "properties": {
      "category": {"type": "string"},
      "customer_id": {"type": "integer"},
      "quantity": {"type": "integer"}
    }
  },
  "endpoint_mappings": [
    {"path": "/products", "method": "get", "step": 1},
    {"path": "/orders", "method": "post", "step": 2}
  ],
  "orchestration": "First search products by category, then create order with found products"
}
```

### Custom Server Modifications

The generated server is meant to be customized. Common modifications:

**1. Add authentication**:
```python
# In server.py, modify _handle_standard_tool
headers = {
    "Authorization": f"Bearer {self.api_key}",
    "Content-Type": "application/json"
}
```

**2. Add retry logic**:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
async def _make_request(self, ...):
    # HTTP request code
```

**3. Add caching**:
```python
from functools import lru_cache

@lru_cache(maxsize=100)
async def _get_cached(self, url: str):
    # GET request code
```

**4. Add request validation**:
```python
def _validate_arguments(self, arguments: dict, schema: dict):
    # Validate against input_schema
    required = schema.get("required", [])
    for field in required:
        if field not in arguments:
            raise ValueError(f"Missing required field: {field}")
```

### Updating Tools

To add or modify tools after generation:

1. **Edit `tools.json`** directly:
   - Add new tool objects
   - Modify descriptions
   - Update input schemas
   - Change endpoint mappings

2. **Restart the server**:
   - The server reads `tools.json` at startup
   - No code changes needed
   - Changes take effect immediately

3. **Restart Claude Desktop** to pick up new tools

### Error Handling

The generated server includes basic error handling. API errors are:

1. **Caught** by the server
2. **Logged** to console
3. **Returned** to Claude as text content
4. **Displayed** to the user

Claude can then:
- Interpret the error
- Suggest fixes
- Retry with different parameters
- Ask the user for clarification

### Security Considerations

**For production use**, enhance security:

1. **API keys**: Store in secure environment variables
2. **Rate limiting**: Add request throttling
3. **Input validation**: Validate all parameters
4. **Output sanitization**: Filter sensitive data
5. **HTTPS**: Use encrypted connections
6. **Authentication**: Implement proper auth flows
7. **Audit logging**: Log all API calls

---

## Troubleshooting

### Common Issues

**"Failed to parse spec"**
- Ensure spec is valid OpenAPI 3.0+
- Check YAML/JSON syntax
- Verify all `$ref` references resolve

**"Enrichment failed"**
- Check ANTHROPIC_API_KEY is set
- Verify API key has credits
- Check network connectivity

**"Tool not found"**
- Ensure tools.json is in the same directory as server.py
- Check tool name matches exactly
- Review server logs for loading errors

**"API request failed"**
- Verify base_url is correct
- Check API is running and accessible
- Ensure API_KEY is set if required
- Review endpoint paths match API exactly

**"Claude can't see tools"**
- Check Claude Desktop config syntax
- Use absolute paths in config
- Restart Claude Desktop after config changes
- Check server.py runs without errors

### Debug Mode

Enable verbose logging in your server:

```python
# At top of server.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

This shows:
- Tool loading details
- HTTP request/response details
- Parameter substitution
- Error stack traces

---

## Conclusion

You now understand the complete process:

1. **Upload** OpenAPI spec → Parsed endpoints
2. **Enrich** with AI → Better descriptions
3. **Generate** tools → MCP tool definitions
4. **Create** server → Complete package
5. **Deploy** → Connect to Claude

The key insight: **MCP servers don't have to be hard**. By using:
- Existing standards (OpenAPI)
- AI assistance (Claude for enrichment)
- Declarative configuration (tools.json)
- Generic runtime (server.py template)

You can rapidly convert any REST API into an AI-accessible tool. This approach works for:
- Internal company APIs
- Third-party services with OpenAPI specs
- Legacy systems with documentation
- New APIs you're building

The generated server is production-ready with additional hardening, and the entire conversion process can be completed in minutes rather than hours or days of custom development.

Happy building! 🚀
