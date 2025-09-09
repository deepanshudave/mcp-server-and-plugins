"""Weather client configuration management."""

import os
from typing import Optional
from dotenv import load_dotenv

from .types import WeatherConfig


# OpenWeatherMap API Constants
DEFAULT_BASE_URL = "https://api.openweathermap.org/data/2.5"
DEFAULT_GEO_URL = "https://api.openweathermap.org/geo/1.0"


def get_env_var(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """Get an environment variable with optional default and required validation."""
    value = os.getenv(key, default)
    
    if required and value is None:
        raise ValueError(f"Required environment variable '{key}' is not set")
    
    return value


def get_weather_config() -> WeatherConfig:
    """Get weather client configuration from environment."""
    # Ensure environment is loaded
    load_dotenv()
    
    return WeatherConfig(
        api_key=get_env_var("OPENWEATHERMAP_API_KEY", required=True),
        base_url=DEFAULT_BASE_URL,
        geo_url=DEFAULT_GEO_URL
    )