#!/bin/bash

# MCP Server Endpoint Testing Script
echo "🧪 Testing MCP Server Endpoints with Authentication"
echo "===================================================="

BASE_URL="http://localhost:8008"
API_KEY="api_utest_http_Xp4cVm9Lt2WdHq0GyEz6BoA1Ns3JkfUM"

echo "1. 📊 Server Info:"
curl -s "$BASE_URL/" | jq . 2>/dev/null || curl -s "$BASE_URL/"
echo -e "\n"

echo "2. ❤️ Health Check:"
curl -s "$BASE_URL/health" | jq . 2>/dev/null || curl -s "$BASE_URL/health"
echo -e "\n"

echo "3. 🔧 Available Tools (with API key):"
curl -s -H "X-API-Key: $API_KEY" "$BASE_URL/tools" | jq . 2>/dev/null || curl -s -H "X-API-Key: $API_KEY" "$BASE_URL/tools"
echo -e "\n"

echo "4. 🌤️ Current Weather (London) - with API key:"
curl -s -X POST "$BASE_URL/tools/get_current_weather" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"location": "London"}' | jq . 2>/dev/null || curl -s -X POST "$BASE_URL/tools/get_current_weather" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"location": "London"}'
echo -e "\n"

echo "5. 📅 Weather Forecast (New York, 3 days) - with API key:"
curl -s -X POST "$BASE_URL/tools/get_weather_forecast" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"location": "New York", "days": 3}' | jq . 2>/dev/null || curl -s -X POST "$BASE_URL/tools/get_weather_forecast" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"location": "New York", "days": 3}'
echo -e "\n"

echo "6. 🌍 Multiple Locations Test - with API key:"
echo "Paris Weather:"
curl -s -X POST "$BASE_URL/tools/get_current_weather" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"location": "Paris"}' | jq . 2>/dev/null || curl -s -X POST "$BASE_URL/tools/get_current_weather" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"location": "Paris"}'
echo -e "\n"

echo "Sydney 5-day Forecast:"
curl -s -X POST "$BASE_URL/tools/get_weather_forecast" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"location": "Sydney", "days": 5}' | jq . 2>/dev/null || curl -s -X POST "$BASE_URL/tools/get_weather_forecast" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"location": "Sydney", "days": 5}'
echo -e "\n"

echo "7. 🚨 Authentication Tests:"
echo "Testing without API key (should fail):"
curl -s -X POST "$BASE_URL/tools/get_current_weather" \
  -H "Content-Type: application/json" \
  -d '{"location": "London"}' | jq . 2>/dev/null || curl -s -X POST "$BASE_URL/tools/get_current_weather" \
  -H "Content-Type: application/json" \
  -d '{"location": "London"}'
echo -e "\n"

echo "Testing with invalid API key (should fail):"
curl -s -X POST "$BASE_URL/tools/get_current_weather" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: invalid-key-123" \
  -d '{"location": "London"}' | jq . 2>/dev/null || curl -s -X POST "$BASE_URL/tools/get_current_weather" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: invalid-key-123" \
  -d '{"location": "London"}'
echo -e "\n"

echo "✅ All endpoint tests completed!"
echo "📊 Check logs/mcp-server.log for client tracking information"