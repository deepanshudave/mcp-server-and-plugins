# MCP Server and Plugins

This project is a Modular MCP (Model Context Protocol) server with FastAPI supporting multiple clients including Weather functionality. It provides both HTTP REST API and native MCP protocol support for integration with Claude Desktop and other MCP-compatible clients.

## Architecture Overview

### Option 1: HTTP Bridge Integration
```
Claude Desktop → MCP HTTP Bridge → HTTP API Server → Weather Client → OpenWeatherMap API
     ↓              ↓                    ↓                ↓              ↓
   User asks    Converts MCP        Validates API     Processes      Returns weather
  "weather?"   to HTTP requests      key & routes     request        data to user
```

### Option 2: Native MCP Integration  
```
Claude Desktop → Native MCP Server → Weather Client → OpenWeatherMap API
     ↓               ↓                    ↓              ↓
   User asks     Direct stdio        Processes       Returns weather
  "weather?"    protocol comm.      request         data to user
```

**Key Differences:**
- **HTTP Bridge**: Python 3.9+ compatible, goes through HTTP layer with API key validation
- **Native MCP**: Python 3.10+ required, direct protocol communication, optional API keys

### Detailed Flow Example

**User Request**: *"What's the weather in London?"*

#### HTTP Bridge Flow:
```
1. Claude Desktop → "get_current_weather(location: 'London')" → MCP HTTP Bridge
2. MCP HTTP Bridge → POST /tools/get_current_weather + API Key → HTTP Server
3. HTTP Server → Validates "api_http_bridge_***" → Weather Client  
4. Weather Client → GET weather?q=London → OpenWeatherMap API
5. OpenWeatherMap → Weather Data → Weather Client → HTTP Server
6. HTTP Server → Logs "Claude Desktop HTTP Bridge executed tool" → MCP Bridge
7. MCP Bridge → Weather Response → Claude Desktop → User
```

#### Native MCP Flow:
```
1. Claude Desktop → "get_current_weather(location: 'London')" → Native MCP Server
2. Native MCP Server → Logs "Claude Desktop MCP Native executed tool" → Weather Client
3. Weather Client → GET weather?q=London → OpenWeatherMap API  
4. OpenWeatherMap → Weather Data → Weather Client → Native MCP Server
5. Native MCP Server → Weather Response → Claude Desktop → User
```

## Features

- **Weather Tools**: Current weather conditions and 5-day forecasts using OpenWeatherMap API
- **Dual Protocol Support**: Both HTTP REST API and native MCP stdio protocol
- **API Key Authentication**: Client identification and usage tracking with secure API keys
- **Client Tracking**: Comprehensive logging of API access and tool usage by client
- **Claude Desktop Integration**: Ready-to-use configuration files for seamless integration
- **Modular Architecture**: Extensible client system for adding new tools
- **Hot Reload**: Development server with automatic code reloading
- **Centralized Caching**: Python bytecode cache organized in `.cache/pycache/`
- **Comprehensive Logging**: Detailed logging for debugging, monitoring, and client analytics

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
# Test HTTP API with authentication
./test/check_endpoints.sh

# Test Native MCP server authentication (optional)
./test/check_native_mcp.sh
```

### 5. Stop the Server
```bash
./scripts/stop.sh
```

## Claude Desktop Integration

This project supports two integration methods with Claude Desktop, both with **API key authentication** for client tracking:

### Option 1: HTTP Bridge (Recommended for Python 3.9+)

Use the HTTP bridge that converts MCP protocol to HTTP REST calls:

```json
{
  "mcpServers": {
    "weather-server": {
      "command": "<PATH_TO_PROJECT_CODEBASE>/mcp-server-env/bin/python",
      "args": ["<PATH_TO_PROJECT_CODEBASE>/mcp_http_bridge.py"],
      "env": {
        "SERVER_URL": "http://localhost:8008",
        "API_KEY": "api_http_bridge_3f8a2c9d1e6b4f7a8c5d2e9f1a3b6c8d"
      }
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
      "env": {
        "API_KEY": "api_mcp_native_3f8a2c9d1e6b4f7a8c5d2e9f1a3b6c8d"
      }
    }
  }
}
```

Copy `claude-desktop-config-native-mcp.json.example` and update the paths.

## Authentication & Client Tracking

### API Key Authentication

Both integration methods support API key authentication for client identification and usage tracking:

**Available API Keys:**
- `api_mcp_native_3f8a2c9d1e6b4f7a8c5d2e9f1a3b6c8d` → Claude Desktop MCP Native
- `api_http_bridge_3f8a2c9d1e6b4f7a8c5d2e9f1a3b6c8d` → Claude Desktop HTTP Bridge

### Usage Tracking

All API calls are logged with client identification:

```
2025-09-09 14:42:30,882 - src.middleware.auth - INFO - API access: Claude Desktop MCP Native - Key: api_mcp_***
2025-09-09 14:42:30,883 - __main__ - INFO - Client 'Claude Desktop MCP Native' executing tool: get_current_weather
```

**Log Location:** `logs/mcp-server.log`

### Authentication Behavior

**HTTP API (Port 8008):**
- ✅ Public endpoints: `/`, `/health`, `/docs`, `/openapi.json`
- 🔐 Protected endpoints: `/tools`, `/tools/{tool_name}` (require `X-API-Key` header)
- ❌ Invalid/missing API key: HTTP 401 error

**Native MCP Server:**
- ✅ Valid API key: Client identified, usage logged
- ⚠️ No API key: Warning logged, runs as "Anonymous MCP Client"
- ❌ Invalid API key: Server startup fails

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

**List All Tools** 🔐
```
GET http://localhost:8008/tools
X-API-Key: api_http_bridge_3f8a2c9d1e6b4f7a8c5d2e9f1a3b6c8d
```
Returns all available tools with their schemas

### Weather Tools

**Get Current Weather** 🔐
```
POST http://localhost:8008/tools/get_current_weather
Content-Type: application/json
X-API-Key: api_http_bridge_3f8a2c9d1e6b4f7a8c5d2e9f1a3b6c8d

{
  "location": "London"
}
```

**Get Weather Forecast** 🔐
```
POST http://localhost:8008/tools/get_weather_forecast
Content-Type: application/json
X-API-Key: api_http_bridge_3f8a2c9d1e6b4f7a8c5d2e9f1a3b6c8d

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
# Test current weather (with API key)
curl -X POST "http://localhost:8008/tools/get_current_weather" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: api_http_bridge_3f8a2c9d1e6b4f7a8c5d2e9f1a3b6c8d" \
  -d '{"location": "Paris"}'

# Test weather forecast (with API key)
curl -X POST "http://localhost:8008/tools/get_weather_forecast" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: api_http_bridge_3f8a2c9d1e6b4f7a8c5d2e9f1a3b6c8d" \
  -d '{"location": "Tokyo", "days": 5}'

# Test without API key (will return 401 error)
curl -X POST "http://localhost:8008/tools/get_current_weather" \
  -H "Content-Type: application/json" \
  -d '{"location": "London"}'
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
2. **"Missing API key" (HTTP 401)**: Ensure `API_KEY` is set in Claude Desktop config
3. **"Invalid API key"**: Verify using correct API key from authentication section
4. **"Server disconnected"**: Verify Python path in Claude Desktop config
5. **Import errors**: Ensure virtual environment is activated and dependencies installed
6. **Port conflicts**: Make sure port 8008 is available

### Logs

- **HTTP Server**: Check console output from `./scripts/start.sh`
- **Client Tracking**: See `logs/mcp-server.log` for API access logs
- **MCP Bridge**: See `logs/mcp-bridge.log`  
- **MCP Server**: See `logs/mcp-server.log`
- **Claude Desktop**: Check Claude Desktop's MCP logs

**Monitor client usage**:
```bash
# Real-time client tracking
tail -f logs/mcp-server.log | grep "API access"

# Search specific client
grep "Claude Desktop MCP Native" logs/mcp-server.log
```
