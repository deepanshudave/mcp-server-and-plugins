#!/bin/bash

# MCP Server Startup Script
# Ensures clean restart on port 8008

set -e

echo "🔧 Starting MCP Server..."

# Kill any existing processes on port 8008
echo "🧹 Cleaning up any existing processes..."
lsof -ti:8008 | xargs kill -9 2>/dev/null || true
sleep 1

# Use virtual environment python directly
echo "🚀 Starting server on port 8008..."
./mcp-server-env/bin/python run.py