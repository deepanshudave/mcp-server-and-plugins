#!/bin/bash

# Native MCP Server Testing Script
echo "🧪 Testing Native MCP Server with Authentication"
echo "==============================================="

echo "1. ✅ Testing with valid API key:"
API_KEY="api_utest_mcp_Yr9aK7oG2lJp8RtZxQ3nMu0vBd4EsF1T"
env API_KEY="$API_KEY" ./mcp-server-env/bin/python -m src.mcp_server 2>&1 &
PID=$!
sleep 2
kill $PID 2>/dev/null || true
wait $PID 2>/dev/null || true
echo -e "\n"

echo "2. ❌ Testing with invalid API key (should fail):"
env API_KEY="invalid-key-123" ./mcp-server-env/bin/python -m src.mcp_server 2>&1 | head -5
echo -e "\n"

echo "3. ⚠️ Testing without API key (should work with warning):"
./mcp-server-env/bin/python -m src.mcp_server 2>&1 &
PID=$!
sleep 2
kill $PID 2>/dev/null || true
wait $PID 2>/dev/null || true
echo -e "\n"

echo "✅ Native MCP server tests completed!"
echo "📊 Check logs/mcp-server.log for client authentication logs"