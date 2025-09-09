"""Weather client FastAPI router."""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

# Create weather router
weather_router = APIRouter(prefix="/weather", tags=["weather"])


# This will be set by the main app when registering the client
weather_client = None


def set_weather_client(client):
    """Set the weather client instance for the router."""
    global weather_client
    weather_client = client


@weather_router.post("/current")
async def get_current_weather(location: str):
    """Get current weather for a location (always in Celsius)."""
    if not weather_client:
        raise HTTPException(status_code=500, detail="Weather client not initialized")
    
    try:
        result = await weather_client.execute_tool("get_current_weather", {
            "location": location, 
            "units": "metric"
        })
        
        if result.isError:
            raise HTTPException(status_code=400, detail=result.content[0]["text"])
        
        return {
            "tool": "get_current_weather",
            "result": result.content[0]["text"] if result.content else "No result"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@weather_router.post("/forecast")
async def get_weather_forecast(location: str, days: int = 3):
    """Get weather forecast for a location (always in Celsius)."""
    if not weather_client:
        raise HTTPException(status_code=500, detail="Weather client not initialized")
    
    try:
        result = await weather_client.execute_tool("get_weather_forecast", {
            "location": location, 
            "days": days, 
            "units": "metric"
        })
        
        if result.isError:
            raise HTTPException(status_code=400, detail=result.content[0]["text"])
        
        return {
            "tool": "get_weather_forecast", 
            "result": result.content[0]["text"] if result.content else "No result"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


