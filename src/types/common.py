"""Common type definitions for the MCP server."""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel


class ToolDefinition(BaseModel):
    """Definition of an MCP tool."""
    name: str
    description: str
    inputSchema: Dict[str, Any]


class ToolResult(BaseModel):
    """Result of a tool execution."""
    content: List[Dict[str, Any]]
    isError: bool = False


class ClientConfig(BaseModel):
    """Base configuration for all clients."""
    name: str
    description: str
    enabled: bool = True
