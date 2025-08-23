"""Generic MCP client loader for pure MCP server."""

from typing import Dict, Any
import sys

from ..types.common import ClientConfig
from .base_client_loader import load_client_class
from .client_config import get_client_configs


def load_mcp_client(client_name: str, client_config: ClientConfig) -> Any:
    """
    Dynamically load an MCP client.
    
    Args:
        client_name: Name of the client (e.g., "weather", "stocks")
        client_config: Configuration for the client
        
    Returns:
        The initialized client instance
    """
    try:
        # Load client using shared base loader
        client_instance = load_client_class(client_name, client_config)
        
        print(f"{client_name.capitalize()} client initialized", file=sys.stderr)
        
        return client_instance
        
    except Exception as e:
        print(f"Failed to load {client_name} client: {e}", file=sys.stderr)
        raise


def load_all_mcp_clients() -> Dict[str, Any]:
    """
    Load all available MCP clients.
    
    Returns:
        Dictionary of loaded clients
    """
    clients = {}
    
    # Get client configurations from shared config
    client_configs = get_client_configs()
    
    for client_name, config in client_configs.items():
        if config.enabled:
            try:
                client = load_mcp_client(client_name, config)
                clients[client_name] = client
            except Exception as e:
                print(f"Failed to load {client_name}: {e}", file=sys.stderr)
    
    return clients