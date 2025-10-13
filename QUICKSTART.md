# Quick Start Guide

Get the OpenAPI to MCP Converter running in 5 minutes!

## Prerequisites Check

```bash
# Check Python version (need 3.11+)
python --version

# Check Node.js version (need 18+)
node --version

# Get Anthropic API key from: https://console.anthropic.com/
```

## Setup (Terminal 1 - Backend)

```bash
# Navigate to backend
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Start backend server
uvicorn app.main:app --reload --port 8000
```

Backend will be running at: http://localhost:8000

## Setup (Terminal 2 - Frontend)

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be running at: http://localhost:5173

## Test the Application

1. Open browser to http://localhost:5173
2. Upload the example spec: `examples/ecommerce_openapi.yaml`
3. Review endpoints and add context
4. Click "Enrich with AI" on a few endpoints
5. Generate tools and server
6. Download your MCP server package!

## Demo Preparation Checklist

For your presentation:

- [ ] Test the full workflow once
- [ ] Prepare screenshots as backup
- [ ] Have example enrichment text ready to paste:
  ```
  This endpoint is used by store managers to view product inventory
  and make decisions about restocking. It's commonly used in
  dashboard views and reports.
  ```
- [ ] Know which endpoints to enrich during the demo (2-3 is enough)
- [ ] Have the base URL ready: `https://api.example-shop.com/v1`
- [ ] Test the download and extraction of the generated server

## Troubleshooting

**Backend won't start:**
- Check Python version: `python --version`
- Make sure venv is activated
- Verify ANTHROPIC_API_KEY in .env

**Frontend won't start:**
- Check Node version: `node --version`
- Delete `node_modules` and run `npm install` again
- Check for port conflicts (kill process on 5173)

**CORS errors:**
- Make sure backend is running on port 8000
- Check CORS settings in `backend/app/main.py`

**API calls failing:**
- Verify ANTHROPIC_API_KEY is set correctly
- Check backend logs for errors
- Ensure both servers are running

## Demo Flow (40 minutes)

1. **Introduction (5 min)**: Explain MCP and the goal
2. **Upload Spec (2 min)**: Show the parsing process
3. **Enrich Endpoints (10 min)**: Demonstrate AI enrichment with user context
4. **Generate Tools (5 min)**: Show the tool definitions
5. **Generate Server (5 min)**: Create and download the server
6. **Show Generated Code (8 min)**: Walk through the generated files
7. **Q&A (5 min)**: Answer questions

## Key Messages

1. **Accessible**: Not magic, anyone can build this
2. **Practical**: Combines human expertise with AI capabilities
3. **Fast**: From API spec to working MCP server in minutes
4. **Extensible**: Can be adapted for specific needs

## Post-Demo

Share the GitHub repository link and encourage people to:
- Try it with their own APIs
- Extend it for their use cases
- Use it as a learning resource for MCP development

## Resources

- MCP Documentation: https://modelcontextprotocol.io
- Claude API: https://docs.anthropic.com/
- OpenAPI Specification: https://swagger.io/specification/

Good luck with your presentation!
