"""Pure MCP Server implementation following MCP protocol."""

import asyncio
import json
import sys
import os
import logging
from typing import Any, Dict, List, Optional

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
import mcp.types as types

from .types.common import ClientConfig
from .utils.config import load_environment, setup_logging
from .utils.mcp_client_loader import load_all_mcp_clients

# Import API key validation from middleware
from .middleware.auth import validate_api_key


class PureMCPServer:
    """Pure MCP server implementation."""
    
    def __init__(self):
        """Initialize the MCP server."""
        load_environment()
        setup_logging()
        
        # Get logger after setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Initialize API key authentication
        self.api_key = os.getenv("API_KEY")
        self.client_name = None
        
        if self.api_key:
            self.client_name = validate_api_key(self.api_key)
            if self.client_name:
                self.logger.info(f"MCP Native Server initialized for client: {self.client_name}")
            else:
                self.logger.error(f"Invalid API key provided: {self.api_key[:8]}***")
                raise ValueError("Invalid API key provided")
        else:
            self.logger.warning("No API key provided - running without authentication")
            self.client_name = "Anonymous MCP Client"
        
        self.server = Server("mcp-server")
        self.clients: Dict[str, Any] = {}
        
        # Setup server handlers
        self._setup_handlers()
    
    def _setup_handlers(self) -> None:
        """Set up MCP server handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List all available tools."""
            tools = []
            
            for client in self.clients.values():
                if not client.is_enabled:
                    continue
                    
                for tool_def in client.get_tools():
                    tool = Tool(
                        name=tool_def.name,
                        description=tool_def.description,
                        inputSchema=tool_def.inputSchema
                    )
                    tools.append(tool)
            
            return tools
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool execution."""
            # Log tool execution with client identification
            self.logger.info(f"Client '{self.client_name}' executing tool: {name} with arguments: {arguments}")
            
            # Execute tool through clients
            for client in self.clients.values():
                if client.has_tool(name):
                    try:
                        result = await client.execute_tool(name, arguments)
                        
                        # Convert result to MCP format
                        content = []
                        for item in result.content:
                            if item["type"] == "text":
                                content.append(TextContent(type="text", text=item["text"]))
                        
                        return content
                    except Exception as e:
                        self.logger.error(f"Error executing tool {name} for client '{self.client_name}': {e}")
                        return [TextContent(type="text", text=f"Tool execution failed: {str(e)}")]
            
            # Tool not found
            self.logger.warning(f"Tool '{name}' not found for client '{self.client_name}'")
            return [TextContent(type="text", text=f"Tool '{name}' not found")]
        
        @self.server.list_resources()
        async def handle_list_resources() -> List[Resource]:
            """List available resources."""
            resources = []
            
            # Add help resources for each enabled client
            for client_name, client in self.clients.items():
                if client.is_enabled:
                    resources.append(
                        Resource(
                            uri=f"{client_name}://help",
                            name=f"{client_name.capitalize()} Help",
                            description=f"Help and usage information for {client_name} tools",
                            mimeType="text/plain"
                        )
                    )
            
            return resources
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read a resource."""
            # Parse client name from URI (format: clientname://help)
            if "://help" in uri:
                client_name = uri.split("://")[0]
                
                if client_name in self.clients:
                    client = self.clients[client_name]
                    if hasattr(client, 'get_help_text'):
                        return client.get_help_text()
                    else:
                        # Generic help text
                        tools = client.get_tools()
                        help_lines = [f"{client_name.capitalize()} Assistant Help", "", "Available Tools:"]
                        
                        for i, tool in enumerate(tools, 1):
                            help_lines.append(f"{i}. {tool.name}")
                            help_lines.append(f"   - {tool.description}")
                            help_lines.append("")
                        
                        return "\n".join(help_lines)
            
            raise ValueError(f"Unknown resource: {uri}")
    
    async def initialize_clients(self) -> None:
        """Initialize all MCP clients."""
        try:
            # Load all clients dynamically
            loaded_clients = load_all_mcp_clients()
            self.clients.update(loaded_clients)
            
        except Exception as e:
            print(f"Error initializing clients: {e}", file=sys.stderr)
            raise
    
    async def run(self) -> None:
        """Run the MCP server."""
        try:
            await self.initialize_clients()
            
            print("Starting MCP server...", file=sys.stderr)
            
            # Use stdio transport for MCP
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="mcp-server",
                        server_version="1.0.0",
                        capabilities=self.server.get_capabilities(
                            notification_options=NotificationOptions(),
                            experimental_capabilities={}
                        )
                    )
                )
                
        except Exception as e:
            print(f"Server error: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            raise


async def main():
    """Main entry point for MCP server."""
    try:
        server = PureMCPServer()
        await server.run()
    except Exception as e:
        print(f"Main error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        raise


if __name__ == "__main__":
    asyncio.run(main())