"""Base client abstract class for all MCP clients."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
import logging

from ..types.common import ToolDefinition, ToolResult, ClientConfig


class BaseClient(ABC):
    """Abstract base class for all MCP clients."""
    
    def __init__(self, config: ClientConfig):
        """Initialize the client with configuration."""
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{config.name}")
        self._tools: Dict[str, ToolDefinition] = {}
        self._initialize_tools()
    
    @abstractmethod
    def _initialize_tools(self) -> None:
        """Initialize the tools for this client."""
        pass
    
    @abstractmethod
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
        """Execute a tool with the given arguments."""
        pass
    
    def get_tools(self) -> List[ToolDefinition]:
        """Get all available tools for this client."""
        return list(self._tools.values())
    
    def register_tool(self, tool: ToolDefinition) -> None:
        """Register a tool with this client."""
        self._tools[tool.name] = tool
        self.logger.info(f"Registered tool: {tool.name}")
    
    def has_tool(self, tool_name: str) -> bool:
        """Check if the client has a specific tool."""
        return tool_name in self._tools
    
    @property
    def name(self) -> str:
        """Get the client name."""
        return self.config.name
    
    @property
    def description(self) -> str:
        """Get the client description."""
        return self.config.description
    
    @property
    def is_enabled(self) -> bool:
        """Check if the client is enabled."""
        return self.config.enabled