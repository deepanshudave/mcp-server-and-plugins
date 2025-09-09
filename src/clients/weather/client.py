"""Weather client implementation using OpenWeatherMap API."""

import httpx
from typing import Any, Dict, List, Optional
import logging

from ...core.base_client import BaseClient
from ...types.common import ToolDefinition, ToolResult, ClientConfig
from .types import WeatherConfig, WeatherData, WeatherForecast


class WeatherClient(BaseClient):
    """Weather client for OpenWeatherMap API integration."""
    
    @classmethod
    def get_description(cls) -> str:
        """Get client description for auto-discovery."""
        return "Weather information and forecasting"
    
    def __init__(self, client_config: ClientConfig):
        """Initialize the weather client."""
        super().__init__(client_config)
        
        # Load weather configuration
        from .config import get_weather_config
        weather_config = get_weather_config()
        
        self.api_key = weather_config.api_key
        self.base_url = weather_config.base_url
        self.geo_url = weather_config.geo_url
    
    def _initialize_tools(self) -> None:
        """Initialize weather-specific tools."""
        self.register_tool(ToolDefinition(
            name="get_current_weather",
            description="Get current weather conditions for a specific location (temperature in Celsius)",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The location to get weather for (city name, city,country, or coordinates)"
                    },
                    "units": {
                        "type": "string",
                        "enum": ["metric"],
                        "default": "metric",
                        "description": "Temperature units (fixed to Celsius)"
                    }
                },
                "required": ["location"]
            }
        ))
        
        self.register_tool(ToolDefinition(
            name="get_weather_forecast",
            description="Get weather forecast for a specific location (temperature in Celsius)",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The location to get forecast for"
                    },
                    "days": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 5,
                        "default": 3,
                        "description": "Number of days for forecast (1-5)"
                    },
                    "units": {
                        "type": "string",
                        "enum": ["metric"],
                        "default": "metric",
                        "description": "Temperature units (fixed to Celsius)"
                    }
                },
                "required": ["location"]
            }
        ))
        
    
    def get_help_text(self) -> str:
        """Get help text for weather tools."""
        return """Weather Assistant Help

Available Tools:
1. get_current_weather(location, units=metric)
   - Get current weather conditions for any location
   - Location can be city name, "city,country", or coordinates
   - Units: metric (°C) - temperature always in Celsius

2. get_weather_forecast(location, days=3, units=metric) 
   - Get weather forecast for 1-5 days
   - Same location options as current weather
   - Temperature always in Celsius

Examples:
- get_current_weather("New York")
- get_weather_forecast("London,UK", 5)

All weather data is provided by OpenWeatherMap."""
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
        """Execute a weather tool."""
        try:
            if tool_name == "get_current_weather":
                return await self._get_current_weather(arguments)
            elif tool_name == "get_weather_forecast":
                return await self._get_weather_forecast(arguments)
            else:
                return ToolResult(
                    content=[{"type": "text", "text": f"Unknown tool: {tool_name}"}],
                    isError=True
                )
        except Exception as e:
            self.logger.error(f"Error executing tool {tool_name}: {e}")
            return ToolResult(
                content=[{"type": "text", "text": f"Error: {str(e)}"}],
                isError=True
            )
    
    async def _get_current_weather(self, arguments: Dict[str, Any]) -> ToolResult:
        """Get current weather for a location."""
        location = arguments["location"]
        units = "metric"  # Always use Celsius
        
        url = f"{self.base_url}/weather"
        params = {
            "q": location,
            "appid": self.api_key,
            "units": units
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            self.logger.info(f"Current weather API response for {location}: {data}")
        
        weather_data = WeatherData(
            location=f"{data['name']}, {data['sys']['country']}",
            temperature=data["main"]["temp"],
            description=data["weather"][0]["description"].title(),
            humidity=data["main"].get("humidity"),
            wind_speed=data.get("wind", {}).get("speed"),
            pressure=data["main"].get("pressure"),
            visibility=data.get("visibility")
        )
        
        unit_symbol = "°C"  # Always Celsius
        
        result_text = f"Current weather in {weather_data.location}:\n"
        result_text += f"Temperature: {weather_data.temperature}{unit_symbol}\n"
        result_text += f"Condition: {weather_data.description}\n"
        if weather_data.humidity:
            result_text += f"Humidity: {weather_data.humidity}%\n"
        if weather_data.wind_speed:
            result_text += f"Wind Speed: {weather_data.wind_speed} m/s\n"
        if weather_data.pressure:
            result_text += f"Pressure: {weather_data.pressure} hPa\n"
        
        return ToolResult(content=[{"type": "text", "text": result_text}])
    
    async def _get_weather_forecast(self, arguments: Dict[str, Any]) -> ToolResult:
        """Get weather forecast for a location."""
        location = arguments["location"]
        days = int(arguments.get("days", 3))  # Ensure days is an integer
        units = "metric"  # Always use Celsius
        
        url = f"{self.base_url}/forecast"
        params = {
            "q": location,
            "appid": self.api_key,
            "units": units,
            "cnt": days * 8  # 8 forecasts per day (every 3 hours)
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            self.logger.info(f"Weather forecast API response for {location}: {data}")
        
        unit_symbol = "°C"  # Always Celsius
        
        result_text = f"Weather forecast for {data['city']['name']}, {data['city']['country']}:\n\n"
        
        current_date = None
        for item in data["list"][:days * 8]:
            date_time = item["dt_txt"]
            date = date_time.split(" ")[0]
            time = date_time.split(" ")[1]
            
            if date != current_date:
                if current_date is not None:
                    result_text += "\n"
                result_text += f"Date: {date}\n"
                current_date = date
            
            temp = item["main"]["temp"]
            desc = item["weather"][0]["description"].title()
            result_text += f"  {time}: {temp}{unit_symbol}, {desc}\n"
        
        return ToolResult(content=[{"type": "text", "text": result_text}])
    
