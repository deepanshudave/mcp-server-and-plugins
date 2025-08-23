#!/bin/bash

# MCP Server Endpoint Testing Script
echo "🧪 Testing MCP Server Endpoints"
echo "================================"

BASE_URL="http://localhost:8008"

echo "1. 📊 Server Info:"
curl -s "$BASE_URL/" | jq .
echo -e "\n"

echo "2. ❤️ Health Check:"
curl -s "$BASE_URL/health" | jq .
echo -e "\n"

echo "3. 🔧 Available Tools:"
curl -s "$BASE_URL/tools" | jq .
echo -e "\n"

echo "4. 🌤️ Current Weather (London):"
curl -s -X POST "$BASE_URL/tools/get_current_weather" \
  -H "Content-Type: application/json" \
  -d '{"location": "London"}' | jq .
echo -e "\n"

echo "5. 📅 Weather Forecast (New York, 3 days):"
curl -s -X POST "$BASE_URL/tools/get_weather_forecast" \
  -H "Content-Type: application/json" \
  -d '{"location": "New York", "days": 3}' | jq .
echo -e "\n"

echo "6. ⚠️ Weather Alerts (Tokyo):"
curl -s -X POST "$BASE_URL/tools/get_weather_alerts" \
  -H "Content-Type: application/json" \
  -d '{"location": "Tokyo"}' | jq .
echo -e "\n"

echo "7. 🌍 Multiple Locations Test:"
echo "Paris Weather:"
curl -s -X POST "$BASE_URL/tools/get_current_weather" \
  -H "Content-Type: application/json" \
  -d '{"location": "Paris"}' | jq .
echo -e "\n"

echo "Sydney 5-day Forecast:"
curl -s -X POST "$BASE_URL/tools/get_weather_forecast" \
  -H "Content-Type: application/json" \
  -d '{"location": "Sydney", "days": 5}' | jq .
echo -e "\n"

echo "✅ All endpoint tests completed!"