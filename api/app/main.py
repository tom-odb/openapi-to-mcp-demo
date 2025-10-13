from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="OpenAPI to MCP Converter",
    description="Convert OpenAPI specifications to MCP servers",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api", tags=["converter"])

@app.get("/")
async def root():
    return {"message": "OpenAPI to MCP Converter API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
