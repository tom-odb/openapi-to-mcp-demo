# OpenAPI to MCP Converter

Convert OpenAPI specifications into working MCP (Model Context Protocol) servers with AI-powered enrichment.

## Overview

This tool demonstrates how quickly you can transform an existing API into a functional MCP server that works with Claude and other AI assistants. It combines:

- **OpenAPI Parsing**: Automatically extracts endpoints, parameters, and schemas
- **LLM Enrichment**: Uses Claude to generate better descriptions and business context
- **Tool Generation**: Creates declarative MCP tool definitions in JSON format
- **Server Generation**: Produces a complete, ready-to-run MCP server using a generic runtime
- **Composite Tools**: Combine multiple API endpoints into single, powerful tools

## Project Structure

```
openapi-to-mcp/
├── api/                    # FastAPI backend (converter service)
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── services/       # Core services (parser, enricher, generators)
│   │   ├── models/         # Pydantic schemas
│   │   └── templates/      # Template files for MCP server generation
│   ├── pyproject.toml      # Python dependencies (uv-compatible)
│   └── requirements.txt    # Alternative pip requirements
├── ui/                     # Vue 3 frontend
│   ├── src/
│   │   ├── components/     # Vue components
│   │   ├── stores/         # Pinia state management
│   │   └── views/          # Vue views
│   ├── package.json        # Node.js dependencies
│   └── vite.config.js      # Vite configuration
├── crm/                    # Example CRM API (for testing)
│   ├── main.py             # FastAPI CRM implementation
│   ├── docs/
│   │   └── crm_openapi.yaml  # OpenAPI spec for CRM
│   ├── pyproject.toml      # CRM API dependencies
│   └── seed_data.py        # Sample data generator
└── generated-servers/      # Output directory for generated MCP servers
```

## Prerequisites

- Python 3.11+
- Node.js 18+
- Anthropic API key

## Quick Start

### 1. Backend Setup (Converter API)

#### Using uv (recommended)

```bash
cd api

# Install uv if you haven't already
# curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies (creates .venv automatically)
uv sync

# Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Start backend server
uv run uvicorn app.main:app --reload --port 8000
```

#### Using pip (alternative)

```bash
cd api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Start backend server
uvicorn app.main:app --reload --port 8000
```

The backend will be available at `http://localhost:8000`

### 2. Frontend Setup

```bash
cd ui

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

### 3. Example CRM API (Optional)

To test the converter with a real API:

```bash
cd crm

# Using uv (recommended)
uv sync
uv run uvicorn main:app --reload --port 8001

# OR using pip
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

The CRM API will be available at `http://localhost:8001` with OpenAPI docs at `http://localhost:8001/docs`

## Usage Workflow

### Step 1: Upload OpenAPI Spec

1. Open the web interface at `http://localhost:5173`
2. Upload your OpenAPI specification (YAML or JSON)
3. The system will parse and extract all endpoints

### Step 2: Enrich Endpoints

1. Review the extracted endpoints
2. For endpoints lacking descriptions, add business context
3. Click "Enrich with AI" to generate improved descriptions using Claude
4. The LLM will provide:
   - Technical descriptions of what the endpoint does
   - Business context explaining when/why to use it

### Step 3: Generate Tools

1. Configure your API details (name and base URL)
2. Click "Generate Tool Definitions"
3. Review the generated MCP tools and their input schemas
4. Each tool maps to an API endpoint with proper parameter definitions

### Step 4: Generate Server

1. Provide a name for your MCP server
2. Click "Generate Server"
3. Download the complete server package as a ZIP file

### Step 5: Use Your MCP Server

1. Extract the downloaded ZIP file
2. Navigate to the server directory
3. Install dependencies:
   ```bash
   pip install -e .
   ```
4. Configure your API key in `.env`
5. Add to Claude Desktop config:
   ```json
   {
     "mcpServers": {
       "your-server-name": {
         "command": "python",
         "args": ["/path/to/server/server.py"],
         "env": {
           "API_KEY": "your-api-key-here"
         }
       }
     }
   }
   ```

## Example

An example CRM API is included in the `crm/` directory with its OpenAPI specification at `crm/docs/crm_openapi.yaml`. This provides:
- A working FastAPI implementation to test against
- A complete OpenAPI spec for conversion testing
- Sample endpoints for products, customers, and orders

You can use the CRM API's OpenAPI spec to test the entire conversion workflow.

## Key Features

### Intelligent Parsing
- Automatically identifies endpoints that need better descriptions
- Extracts parameters, request bodies, and response schemas
- Preserves original API metadata

### AI-Powered Enrichment
- Uses Claude to generate clear, technical descriptions
- Adds business context to help AI assistants understand when to use each tool
- Combines user domain knowledge with LLM reasoning

### Composite Tools
- Combine multiple API endpoints into single, powerful tools
- Create workflows like "search and purchase" or "create customer and order"
- AI-assisted suggestions for useful composite tool combinations

### Complete Server Generation
- Creates working Python MCP servers with declarative tool definitions
- Includes proper error handling and HTTP method support
- Generates README, pyproject.toml, and installation instructions
- Output saved to `generated-servers/` directory

## Architecture

### Backend Services

- **OpenAPIParser**: Parses YAML/JSON specs and extracts endpoint data
- **LLMEnricher**: Uses Claude API to enhance endpoint descriptions
- **ToolGenerator**: Converts endpoints to MCP tool definitions
- **ServerGenerator**: Creates complete MCP server packages

### Frontend Components (ui/)

- **SpecUploader**: File upload interface with drag-and-drop
- **EndpointList**: Interactive endpoint review and enrichment
- **ToolPreview**: Displays generated tool definitions
- **ServerGenerator**: Handles server creation and download
- **CompositeToolCreator**: Create composite tools from multiple endpoints

## API Endpoints

- `POST /api/upload-spec`: Upload and parse OpenAPI spec
- `POST /api/enrich-endpoint`: Enrich endpoint with LLM
- `POST /api/suggest-tools`: Get LLM suggestions for tools
- `POST /api/generate-tools`: Generate MCP tool definitions
- `POST /api/generate-server`: Create complete MCP server
- `GET /api/download-server/{name}`: Download server package

## Development

### Running Tests

```bash
# Backend tests
cd api
pytest

# Frontend tests
cd ui
npm run test
```

### Code Style

The project follows:
- Python: PEP 8 with Black formatting
- JavaScript: ESLint + Prettier

## Presentation Tips

For demo/presentation purposes:

1. **Prepare ahead**: Have your OpenAPI spec and enrichment context ready to copy-paste
2. **Use screenshots**: Capture key screens as backup if live demo fails
3. **Choose simple APIs**: E-commerce or CRM examples are easy for audiences to understand
4. **Pre-populate context**: Have business use cases ready to paste for quick enrichment
5. **Show the output**: Display the generated server code to demonstrate completeness

## Core Message

- This is **not hard or magic** - anyone can build this
- It's **not a silver bullet** - we combine human expertise with LLM capabilities
- Using **existing tools** (OpenAPI) + lightweight coding = quick results
- Great for **accelerating development** of both internal tools and client solutions

## Limitations

- In-memory storage (not production-ready)
- No authentication/authorization
- Limited error handling for malformed specs
- Generated servers use basic HTTP client (no retry logic, rate limiting, etc.)

## Future Enhancements

- Database persistence
- User authentication
- Support for more API specifications (GraphQL, gRPC)
- Advanced server features (caching, rate limiting)
- Batch endpoint enrichment
- Custom tool templates

## License

MIT License - feel free to use for demos, presentations, and learning.

## Contributing

This is a demonstration project for educational purposes. Feel free to fork and adapt for your needs.

## Support

For questions or issues, please refer to the project documentation or create an issue in the repository.
