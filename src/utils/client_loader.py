"""Generic client loader for FastAPI MCP server."""

from typing import Dict, Any
import importlib
import logging

from ..types.common import ClientConfig
from .base_client_loader import load_client_class
from .client_config import get_client_configs

logger = logging.getLogger(__name__)


def load_client(client_name: str, client_config: ClientConfig, app: Any) -> Any:
    """
    Dynamically load and register a client with its router.
    
    Args:
        client_name: Name of the client (e.g., "weather", "stocks")
        client_config: Configuration for the client
        app: FastAPI application instance
        
    Returns:
        The initialized client instance
    """
    try:
        # Load client using shared base loader
        client_instance = load_client_class(client_name, client_config)
        
        # Import and register router if it exists
        try:
            router_module = importlib.import_module(f"src.clients.{client_name}.router")
            router = getattr(router_module, f"{client_name}_router")
            set_client_func = getattr(router_module, f"set_{client_name}_client")
            
            # Connect client to router and register with app
            set_client_func(client_instance)
            app.include_router(router)
            
            logger.info(f"{client_name.capitalize()} client and router registered")
            
        except (ImportError, AttributeError) as e:
            logger.info(f"{client_name.capitalize()} client registered (no router found)")
        
        return client_instance
        
    except Exception as e:
        logger.error(f"Failed to load {client_name} client: {e}")
        raise


def load_all_clients(app: Any) -> Dict[str, Any]:
    """
    Load all available clients.
    
    Args:
        app: FastAPI application instance
        
    Returns:
        Dictionary of loaded clients
    """
    clients = {}
    
    # Get client configurations from shared config
    client_configs = get_client_configs()
    
    for client_name, config in client_configs.items():
        if config.enabled:
            try:
                client = load_client(client_name, config, app)
                clients[client_name] = client
            except Exception as e:
                logger.error(f"Failed to load {client_name}: {e}")
    
    return clients