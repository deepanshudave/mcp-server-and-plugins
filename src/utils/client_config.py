"""Auto-discovery of client configurations."""

import os
import importlib
from typing import Dict
from ..types.common import ClientConfig


def discover_clients() -> Dict[str, ClientConfig]:
    """
    Automatically discover all available clients by scanning the clients directory.
    
    Returns:
        Dictionary of client configurations
    """
    clients = {}
    clients_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "clients")
    
    if not os.path.exists(clients_dir):
        return clients
    
    # Scan for client directories
    for item in os.listdir(clients_dir):
        client_path = os.path.join(clients_dir, item)
        
        # Skip non-directories and __pycache__
        if not os.path.isdir(client_path) or item.startswith("__"):
            continue
            
        # Check if client.py exists
        client_file = os.path.join(client_path, "client.py")
        if not os.path.exists(client_file):
            continue
            
        try:
            # Try to import the client to get its description
            client_module = importlib.import_module(f"src.clients.{item}.client")
            client_class_name = f"{item.capitalize()}Client"
            
            if hasattr(client_module, client_class_name):
                client_class = getattr(client_module, client_class_name)
                
                # Get description from client class if available
                if hasattr(client_class, 'get_description'):
                    description = client_class.get_description()
                else:
                    description = f"{item.capitalize()} service client"
                
                # Create config for this client
                clients[item] = ClientConfig(
                    name=item,
                    description=description,
                    enabled=True
                )
        except Exception:
            # If import fails, skip this client
            continue
    
    return clients


def get_client_configs() -> Dict[str, ClientConfig]:
    """
    Get configuration for all available clients.
    
    Returns:
        Dictionary of client configurations discovered automatically
    """
    return discover_clients()