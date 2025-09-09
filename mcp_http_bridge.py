#!/usr/bin/env python3
"""
MCP HTTP Bridge - Converts MCP stdio protocol to HTTP API calls
Compatible with Python 3.9+ - No external MCP library required
"""

import asyncio
import json
import sys
import os
import logging
import subprocess
import time
from typing import Any, Dict, Optional
import httpx

# Set up logging to file to avoid interfering with stdio
import os

# Ensure logs directory exists and use absolute path
script_dir = os.path.dirname(os.path.abspath(__file__))
logs_dir = os.path.join(script_dir, "logs")
os.makedirs(logs_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(os.path.join(logs_dir, "mcp-bridge.log"))]
)
logger = logging.getLogger(__name__)


class MCPHttpBridge:
    """Bridge between MCP stdio protocol and HTTP API."""
    
    def __init__(self):
        """Initialize the bridge."""
        self.server_url = os.getenv("SERVER_URL", "http://localhost:8008")
        self.api_key = os.getenv("API_KEY")
        self.server_process = None
        logger.info(f"MCP HTTP Bridge initialized, server URL: {self.server_url}")
        if not self.api_key:
            logger.warning("No API_KEY environment variable found")
    
    async def start_http_server(self):
        """Start the HTTP server if not already running."""
        try:
            # Check if server is already running
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.server_url}/health", timeout=2.0)
                if response.status_code == 200:
                    logger.info("HTTP server already running")
                    return True
        except:
            logger.info("HTTP server not running, starting it...")
        
        try:
            # Start the HTTP server using absolute paths
            project_dir = os.path.dirname(os.path.abspath(__file__))
            python_path = os.path.join(project_dir, "mcp-server-env", "bin", "python")
            
            self.server_process = subprocess.Popen([
                python_path, "-m", "src.app"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=project_dir)
            
            # Wait for server to start
            for _ in range(10):  # Wait up to 10 seconds
                await asyncio.sleep(1)
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.get(f"{self.server_url}/health", timeout=2.0)
                        if response.status_code == 200:
                            logger.info("HTTP server started successfully")
                            return True
                except:
                    continue
            
            logger.error("Failed to start HTTP server")
            return False
            
        except Exception as e:
            logger.error(f"Error starting HTTP server: {e}")
            return False
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP request and forward to HTTP server."""
        method = request.get("method")
        request_id = request.get("id")
        
        logger.info(f"Handling request: {method}")
        
        try:
            if method == "initialize":
                return await self._handle_initialize(request_id, request.get("params", {}))
            
            elif method == "tools/list":
                return await self._handle_list_tools(request_id)
            
            elif method == "tools/call":
                return await self._handle_call_tool(request_id, request.get("params", {}))
            
            elif method == "prompts/list":
                return await self._handle_list_prompts(request_id)
            
            elif method == "resources/list":
                return await self._handle_list_resources(request_id)
            
            elif method == "notifications/initialized":
                return await self._handle_notification_initialized(request_id)
            
            else:
                return self._error_response(request_id, -32601, f"Method not found: {method}")
        
        except Exception as e:
            logger.error(f"Error handling request {method}: {e}")
            return self._error_response(request_id, -32603, f"Internal error: {str(e)}")
    
    async def _handle_initialize(self, request_id: Optional[str], params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialization request."""
        # Start HTTP server if needed
        if not await self.start_http_server():
            return self._error_response(request_id, -32603, "Failed to start HTTP server")
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "weather-http-bridge",
                    "version": "1.0.0"
                }
            }
        }
    
    async def _handle_list_tools(self, request_id: Optional[str]) -> Dict[str, Any]:
        """Handle tools list request."""
        try:
            headers = {}
            if self.api_key:
                headers["X-API-Key"] = self.api_key
            
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.server_url}/tools", headers=headers)
                response.raise_for_status()
                tools_data = response.json()
            
            # Convert HTTP response to MCP format
            mcp_tools = []
            for tool in tools_data["tools"]:
                mcp_tools.append({
                    "name": tool["name"],
                    "description": tool["description"],
                    "inputSchema": tool["input_schema"]
                })
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": mcp_tools
                }
            }
            
        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            return self._error_response(request_id, -32603, f"Failed to list tools: {str(e)}")
    
    async def _handle_call_tool(self, request_id: Optional[str], params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool call request."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if not tool_name:
            return self._error_response(request_id, -32602, "Missing tool name")
        
        try:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["X-API-Key"] = self.api_key
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.server_url}/tools/{tool_name}",
                    json=arguments,
                    headers=headers
                )
                response.raise_for_status()
                result_data = response.json()
            
            # Convert HTTP response to MCP format
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result_data["result"]
                        }
                    ]
                }
            }
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling tool {tool_name}: {e}")
            error_detail = e.response.text if hasattr(e.response, 'text') else str(e)
            return self._error_response(request_id, -32603, f"Tool execution failed: {error_detail}")
        
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return self._error_response(request_id, -32603, f"Tool execution failed: {str(e)}")
    
    async def _handle_list_prompts(self, request_id: Optional[str]) -> Dict[str, Any]:
        """Handle prompts list request."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "prompts": []  # No prompts available
            }
        }
    
    async def _handle_list_resources(self, request_id: Optional[str]) -> Dict[str, Any]:
        """Handle resources list request."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "resources": []  # No resources available
            }
        }
    
    async def _handle_notification_initialized(self, request_id: Optional[str]) -> Optional[Dict[str, Any]]:
        """Handle initialized notification - no response needed."""
        logger.info("Received initialized notification")
        return None  # Notifications don't need responses
    
    def _error_response(self, request_id: Optional[str], code: int, message: str) -> Dict[str, Any]:
        """Create an error response."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }
    
    def cleanup(self):
        """Clean up resources."""
        # Don't kill the HTTP server - let it persist for future bridge calls
        logger.info("Bridge cleanup - keeping HTTP server running")


async def main():
    """Main bridge loop."""
    bridge = MCPHttpBridge()
    logger.info("Starting MCP HTTP Bridge")
    
    try:
        while True:
            # Read line from stdin
            line = sys.stdin.readline()
            if not line:
                break
            
            line = line.strip()
            if not line:
                continue
            
            try:
                # Parse JSON-RPC request
                request = json.loads(line)
                
                # Handle request
                response = await bridge.handle_request(request)
                
                # Send response to stdout (only if response is not None)
                if response is not None:
                    print(json.dumps(response))
                    sys.stdout.flush()
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
                
    except KeyboardInterrupt:
        logger.info("Bridge stopped by user")
    except Exception as e:
        logger.error(f"Bridge error: {e}")
    finally:
        bridge.cleanup()
        logger.info("MCP HTTP Bridge shutdown")


if __name__ == "__main__":
    asyncio.run(main())