Here's the complete list of URLs to test the MCP server application:

  Server Information Endpoints

  1. Root Endpoint

  GET http://localhost:8008/
  Returns server info and loaded clients

  2. Health Check

  GET http://localhost:8008/health
  Returns server health status and client states

  3. List All Tools

  GET http://localhost:8008/tools
  Returns all available tools with their schemas

  Weather Tool Endpoints

  4. Get Current Weather

  POST http://localhost:8008/tools/get_current_weather
  Content-Type: application/json

  {
    "location": "London"
  }

  5. Get Weather Forecast

  POST http://localhost:8008/tools/get_weather_forecast
  Content-Type: application/json

  {
    "location": "New York",
    "days": 3
  }

  6. Get Weather Alerts

  POST http://localhost:8008/tools/get_weather_alerts
  Content-Type: application/json

  {
    "location": "Tokyo"
  }

  cURL Test Commands

Quick Test Script Usage

  1. Start the server:
  cd /Users/deepanshu/Documents/code/gen-ai/mcp-server-and-plugins
  ./scripts/start.sh

  2. Run all endpoint tests:
  ./test/check_endpoints.sh

  3. Stop the server:
  ./scripts/stop.sh

Manual Browser Testing

  - Visit http://localhost:8008/docs for interactive testing
  - Use the Swagger UI to test all endpoints with different parameters
  - Check real-time weather data for various cities

