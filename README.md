# MCP Server and Plugins

This project is a Modular MCP server with FastAPI supporting multiple clients including Weather functionality.

## Quick Start

### 1. Start the server:
```bash
./scripts/start.sh
```

### 2. Run endpoint tests:
```bash
./test/check_endpoints.sh
```

### 3. Stop the server:
```bash
./scripts/stop.sh
```

## API Endpoints

### Server Information Endpoints

**1. Root Endpoint**
```
GET http://localhost:8008/
```
Returns server info and loaded clients

**2. Health Check**
```
GET http://localhost:8008/health
```
Returns server health status and client states

**3. List All Tools**
```
GET http://localhost:8008/tools
```
Returns all available tools with their schemas

### Weather Tool Endpoints

**4. Get Current Weather**
```
POST http://localhost:8008/tools/get_current_weather
Content-Type: application/json

{
  "location": "London"
}
```

**5. Get Weather Forecast**
```
POST http://localhost:8008/tools/get_weather_forecast
Content-Type: application/json

{
  "location": "New York",
  "days": 3
}
```

**6. Get Weather Alerts**
```
POST http://localhost:8008/tools/get_weather_alerts
Content-Type: application/json

{
  "location": "Tokyo"
}
```

## Manual Browser Testing

- Visit `http://localhost:8008/docs` for interactive testing
- Use the Swagger UI to test all endpoints with different parameters
- Check real-time weather data for various cities
