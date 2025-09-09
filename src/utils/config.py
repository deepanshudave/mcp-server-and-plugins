"""Configuration management utilities."""

import os
from typing import Any, Dict, Optional
from dotenv import load_dotenv
import logging


def load_environment() -> None:
    """Load environment variables from .env file."""
    # Use absolute path to .env file to work from any directory
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    env_path = os.path.join(project_root, ".env")
    load_dotenv(env_path)


def get_env_var(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """Get an environment variable with optional default and required validation."""
    value = os.getenv(key, default)
    
    if required and value is None:
        raise ValueError(f"Required environment variable '{key}' is not set")
    
    return value


def get_mcp_config() -> Dict[str, Any]:
    """Get MCP server configuration from environment."""
    return {
        "name": get_env_var("MCP_SERVER_NAME", "mcp-server"),
        "version": get_env_var("MCP_SERVER_VERSION", "1.0.0")
    }


def setup_logging() -> None:
    """Set up logging configuration."""
    log_level = get_env_var("LOG_LEVEL", "INFO")
    
    # Use absolute path to logs directory
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    logs_dir = os.path.join(project_root, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    log_file = os.path.join(logs_dir, "mcp-server.log")
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file)
        ]
    )