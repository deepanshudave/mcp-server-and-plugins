#!/bin/bash

# MCP Server Stop Script  
# Clean shutdown of server processes

echo "🛑 Stopping MCP Server..."

# Kill processes on port 8008
echo "🧹 Terminating server processes..."
lsof -ti:8008 | xargs kill -9 2>/dev/null || true

# Also clean up any python processes running our server
pkill -f "python.*run.py" 2>/dev/null || true
pkill -f "uvicorn.*src.app:app" 2>/dev/null || true

echo "✅ Server stopped"