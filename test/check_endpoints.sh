#!/bin/bash

# MCP Server Endpoint Testing Script
echo "🧪 Testing MCP Server Endpoints"
echo "================================"

BASE_URL="http://localhost:8008"

echo "1. 📊 Server Info:"
curl -s "$BASE_URL/" | jq . 2>/dev/null || curl -s "$BASE_URL/"
echo -e "\n"

echo "2. ❤️ Health Check:"
curl -s "$BASE_URL/health" | jq . 2>/dev/null || curl -s "$BASE_URL/health"
echo -e "\n"

echo "3. 🔧 Available Tools:"
curl -s "$BASE_URL/tools" | jq . 2>/dev/null || curl -s "$BASE_URL/tools"
echo -e "\n"

echo "4. 🌤️ Current Weather (London):"
curl -s -X POST "$BASE_URL/tools/get_current_weather" \
  -H "Content-Type: application/json" \
  -d '{"location": "London"}' | jq . 2>/dev/null || curl -s -X POST "$BASE_URL/tools/get_current_weather" \
  -H "Content-Type: application/json" \
  -d '{"location": "London"}'
echo -e "\n"

echo "5. 📅 Weather Forecast (New York, 3 days):"
curl -s -X POST "$BASE_URL/tools/get_weather_forecast" \
  -H "Content-Type: application/json" \
  -d '{"location": "New York", "days": 3}' | jq . 2>/dev/null || curl -s -X POST "$BASE_URL/tools/get_weather_forecast" \
  -H "Content-Type: application/json" \
  -d '{"location": "New York", "days": 3}'
echo -e "\n"

echo "6. 🌍 Multiple Locations Test:"
echo "Paris Weather:"
curl -s -X POST "$BASE_URL/tools/get_current_weather" \
  -H "Content-Type: application/json" \
  -d '{"location": "Paris"}' | jq . 2>/dev/null || curl -s -X POST "$BASE_URL/tools/get_current_weather" \
  -H "Content-Type: application/json" \
  -d '{"location": "Paris"}'
echo -e "\n"

echo "Sydney 5-day Forecast:"
curl -s -X POST "$BASE_URL/tools/get_weather_forecast" \
  -H "Content-Type: application/json" \
  -d '{"location": "Sydney", "days": 5}' | jq . 2>/dev/null || curl -s -X POST "$BASE_URL/tools/get_weather_forecast" \
  -H "Content-Type: application/json" \
  -d '{"location": "Sydney", "days": 5}'
echo -e "\n"

echo "✅ All endpoint tests completed!"