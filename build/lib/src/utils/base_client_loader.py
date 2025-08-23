"""Base client loading functionality."""

from typing import Any
import importlib

from ..types.common import ClientConfig


def load_client_class(client_name: str, client_config: ClientConfig) -> Any:
    """
    Dynamically load and initialize a client class.
    
    Args:
        client_name: Name of the client (e.g., "weather", "stocks")
        client_config: Configuration for the client
        
    Returns:
        The initialized client instance
    """
    # Import client class
    client_module = importlib.import_module(f"src.clients.{client_name}.client")
    client_class_name = f"{client_name.capitalize()}Client"
    client_class = getattr(client_module, client_class_name)
    
    # Initialize client
    client_instance = client_class(client_config)
    
    return client_instance