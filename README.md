# OpenAPI to MCP Converter

Convert OpenAPI specifications into working MCP (Model Context Protocol) servers with AI-powered enrichment.

## 🆕 NEW: Declarative Architecture

This tool now uses a **declarative JSON-based architecture** instead of code generation:
- ✅ Tools defined in `tools.json` (not generated code)
- ✅ Generic server reads JSON and creates tools dynamically
- ✅ Easy to modify tools by editing JSON
- ✅ Version control friendly
- ✅ Supports both standard and composite tools

**See [DECLARATIVE_QUICKSTART.md](DECLARATIVE_QUICKSTART.md) for the quick start guide.**
**See [DECLARATIVE_ARCHITECTURE.md](DECLARATIVE_ARCHITECTURE.md) for architecture details.**

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
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── services/    # Core services (parser, enricher, generators)
│   │   └── models/      # Pydantic schemas
│   └── requirements.txt
├── frontend/            # Vue 3 frontend
│   ├── src/
│   │   ├── components/  # Vue components
│   │   └── stores/      # Pinia state management
│   └── package.json
├── examples/            # Example OpenAPI specs
└── generated_servers/   # Output directory for MCP servers
```

## Prerequisites

- Python 3.11+
- Node.js 18+
- Anthropic API key

## Quick Start

### 1. Backend Setup

```bash
cd backend

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
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

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

An example e-commerce API specification is included in `examples/ecommerce_openapi.yaml`. Use this for testing and demonstration purposes.

## Key Features

### Intelligent Parsing
- Automatically identifies endpoints that need better descriptions
- Extracts parameters, request bodies, and response schemas
- Preserves original API metadata

### AI-Powered Enrichment
- Uses Claude to generate clear, technical descriptions
- Adds business context to help AI assistants understand when to use each tool
- Combines user domain knowledge with LLM reasoning

### Complete Server Generation
- Creates working Python MCP servers using the FastMCP library
- Includes proper error handling and HTTP method support
- Generates README, configuration files, and installation instructions

## Architecture

### Backend Services

- **OpenAPIParser**: Parses YAML/JSON specs and extracts endpoint data
- **LLMEnricher**: Uses Claude API to enhance endpoint descriptions
- **ToolGenerator**: Converts endpoints to MCP tool definitions
- **ServerGenerator**: Creates complete MCP server packages

### Frontend Components

- **SpecUploader**: File upload interface with drag-and-drop
- **EndpointList**: Interactive endpoint review and enrichment
- **ToolPreview**: Displays generated tool definitions
- **ServerGenerator**: Handles server creation and download

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
cd backend
pytest

# Frontend tests
cd frontend
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
