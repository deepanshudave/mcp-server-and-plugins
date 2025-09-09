# MCP Server and Plugins

This project is a Modular MCP (Model Context Protocol) server with FastAPI supporting multiple clients including Weather functionality. It provides both HTTP REST API and native MCP protocol support for integration with Claude Desktop and other MCP-compatible clients.

## Features

- **Weather Tools**: Current weather conditions and 5-day forecasts using OpenWeatherMap API
- **Dual Protocol Support**: Both HTTP REST API and native MCP stdio protocol
- **Claude Desktop Integration**: Ready-to-use configuration files for seamless integration
- **Modular Architecture**: Extensible client system for adding new tools
- **Hot Reload**: Development server with automatic code reloading
- **Comprehensive Logging**: Detailed logging for debugging and monitoring

## Quick Start

### 1. Install Dependencies
```bash
pip install -e .
```

### 2. Configure Environment
Copy `.env.example` to `.env` and add your OpenWeatherMap API key:
```bash
OPENWEATHERMAP_API_KEY=your_api_key_here
LOG_LEVEL=INFO
PYTHONPYCACHEPREFIX=.cache/pycache
```

### 3. Start the Server
```bash
./scripts/start.sh
```

### 4. Test the API
```bash
./test/check_endpoints.sh
```

### 5. Stop the Server
```bash
./scripts/stop.sh
```

## Claude Desktop Integration

This project supports two integration methods with Claude Desktop:

### Option 1: HTTP Bridge (Recommended for Python 3.9+)

Use the HTTP bridge that converts MCP protocol to HTTP REST calls:

```json
{
  "mcpServers": {
    "weather-server": {
      "command": "<PATH_TO_PROJECT_CODEBASE>/mcp-server-env/bin/python",
      "args": ["<PATH_TO_PROJECT_CODEBASE>/mcp_http_bridge.py"],
      "cwd": "<PATH_TO_PROJECT_CODEBASE>"
    }
  }
}
```

Copy `claude-desktop-config-http-bridge.json.example` and update the paths.

### Option 2: Native MCP (Requires Python 3.10+)

Use the native MCP stdio protocol:

```json
{
  "mcpServers": {
    "weather-server": {
      "command": "<PATH_TO_PROJECT_CODEBASE>/mcp-server-env/bin/python",
      "args": ["-m", "src.mcp_server"],
      "cwd": "<PATH_TO_PROJECT_CODEBASE>"
    }
  }
}
```

Copy `claude-desktop-config-native-mcp.json.example` and update the paths.

## API Endpoints

### Server Information

**Root Endpoint**
```
GET http://localhost:8008/
```
Returns server info and loaded clients

**Health Check**
```
GET http://localhost:8008/health
```
Returns server health status and client states

**List All Tools**
```
GET http://localhost:8008/tools
```
Returns all available tools with their schemas

### Weather Tools

**Get Current Weather**
```
POST http://localhost:8008/tools/get_current_weather
Content-Type: application/json

{
  "location": "London"
}
```

**Get Weather Forecast**
```
POST http://localhost:8008/tools/get_weather_forecast
Content-Type: application/json

{
  "location": "New York",
  "days": 3
}
```

## Available Weather Tools

1. **get_current_weather(location, units=metric)**
   - Get current weather conditions for any location
   - Location can be city name, "city,country", or coordinates
   - Temperature always in Celsius

2. **get_weather_forecast(location, days=3, units=metric)**
   - Get weather forecast for 1-5 days
   - Same location options as current weather
   - Temperature always in Celsius

## Testing

### Interactive Testing
- Visit `http://localhost:8008/docs` for Swagger UI
- Test all endpoints with different parameters
- Check real-time weather data for various cities

### Command Line Testing
```bash
# Test current weather
curl -X POST "http://localhost:8008/tools/get_current_weather" \
  -H "Content-Type: application/json" \
  -d '{"location": "Paris"}'

# Test weather forecast
curl -X POST "http://localhost:8008/tools/get_weather_forecast" \
  -H "Content-Type: application/json" \
  -d '{"location": "Tokyo", "days": 5}'
```

### Claude Desktop Testing
Once configured, ask Claude Desktop:
- "What's the current weather in London?"
- "Give me a 5-day weather forecast for New York"
- "Compare weather between Sydney and Vancouver"

## Project Structure

```
├── src/
│   ├── app.py                 # FastAPI HTTP server
│   ├── mcp_server.py         # Native MCP stdio server
│   ├── clients/
│   │   └── weather/          # Weather client implementation
│   ├── core/                 # Base client classes
│   ├── types/                # Common type definitions
│   └── utils/                # Utilities and config
├── scripts/
│   ├── start.sh              # Server startup script
│   └── stop.sh               # Server stop script
├── test/
│   └── check_endpoints.sh    # API testing script
├── mcp_http_bridge.py        # MCP to HTTP bridge
├── run.py                    # Server entry point
└── claude-desktop-config-*.json.example  # Claude Desktop configs
```

## Development

### Adding New Clients

1. Create a new client directory in `src/clients/`
2. Implement the client class extending `BaseClient`
3. Define tools and their schemas
4. Register the client in the loader

### Environment Variables

- `OPENWEATHERMAP_API_KEY`: Required for weather functionality
- `LOG_LEVEL`: Logging level (INFO, DEBUG, WARNING, ERROR)
- `PYTHONPYCACHEPREFIX`: Centralized Python cache location

### Virtual Environment

The project uses a virtual environment at `mcp-server-env/` with Python 3.12+ for full MCP support.

## Requirements

- **Python 3.10+** 
- **OpenWeatherMap API key** (free tier supported)
- **FastAPI** and dependencies (installed via `pip install -e .`)

## Troubleshooting

### Common Issues

1. **"Tool execution failed"**: Check API key is set in `.env` file
2. **"Server disconnected"**: Verify Python path in Claude Desktop config
3. **Import errors**: Ensure virtual environment is activated and dependencies installed
4. **Port conflicts**: Make sure port 8008 is available

### Logs

- **HTTP Server**: Check console output from `./scripts/start.sh`
- **MCP Bridge**: See `logs/mcp-bridge.log`
- **MCP Server**: See `logs/mcp-server.log`
- **Claude Desktop**: Check Claude Desktop's MCP logs
