"""Weather client type definitions."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class WeatherConfig(BaseModel):
    """Weather client configuration."""
    api_key: str
    base_url: str
    geo_url: str
    onecall_url: str


class WeatherData(BaseModel):
    """Weather data structure."""
    location: str
    temperature: float
    description: str
    humidity: Optional[int] = None
    wind_speed: Optional[float] = None
    pressure: Optional[float] = None
    visibility: Optional[float] = None


class WeatherForecast(BaseModel):
    """Weather forecast data structure."""
    location: str
    forecasts: List[Dict[str, Any]]


class WeatherAlert(BaseModel):
    """Weather alert data structure."""
    location: str
    alerts: List[Dict[str, Any]]