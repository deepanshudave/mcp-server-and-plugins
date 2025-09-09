"""FastAPI application for MCP server."""

from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging

from .utils.config import load_environment, setup_logging
from .utils.client_loader import load_all_clients
from .middleware.auth import validate_client_request

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="MCP Server",
    description="Modular MCP server with FastAPI supporting multiple clients",
    version="1.0.0"
)

# Global clients storage
clients: Dict[str, Any] = {}


@app.on_event("startup")
async def startup_event():
    """Initialize clients on startup."""
    logger.info("Starting MCP Server...")
    
    # Load environment
    load_environment()
    
    # Load all clients dynamically
    loaded_clients = load_all_clients(app)
    clients.update(loaded_clients)
    
    logger.info("Server startup complete")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "MCP Server",
        "version": "1.0.0",
        "clients": list(clients.keys())
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "clients": {name: client.is_enabled for name, client in clients.items()}
    }


@app.get("/tools")
async def list_tools():
    """List all available tools."""
    all_tools = []
    
    for client_name, client in clients.items():
        if client.is_enabled:
            for tool in client.get_tools():
                all_tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "client": client_name,
                    "input_schema": tool.inputSchema
                })
    
    return {"tools": all_tools}


@app.post("/tools/{tool_name}")
async def execute_tool(tool_name: str, arguments: Dict[str, Any], client_name: str = Depends(validate_client_request)):
    """Execute a specific tool."""
    logger.info(f"Client '{client_name}' executing tool: {tool_name} with arguments: {arguments}")
    
    # Find the client that has this tool
    for client in clients.values():
        if client.has_tool(tool_name):
            try:
                result = await client.execute_tool(tool_name, arguments)
                
                if result.isError:
                    raise HTTPException(status_code=400, detail=result.content[0]["text"])
                
                return {
                    "tool": tool_name,
                    "result": result.content[0]["text"] if result.content else "No result"
                }
                
            except Exception as e:
                logger.error(f"Error executing tool {tool_name}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)