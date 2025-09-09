"""API key authentication middleware."""

import logging
from typing import Optional
from fastapi import HTTPException, Request

logger = logging.getLogger(__name__)

# API Keys - can be made modular later
VALID_API_KEYS = {
    "api_mcp_native_3f8a2c9d1e6b4f7a8c5d2e9f1a3b6c8d": "Claude Desktop MCP Native",
    "api_http_bridge_3f8a2c9d1e6b4f7a8c5d2e9f1a3b6c8d": "Claude Desktop HTTP Bridge",
    "api_utest_mcp_Yr9aK7oG2lJp8RtZxQ3nMu0vBd4EsF1T": "Unit Test MCP Native",
    "api_utest_http_Xp4cVm9Lt2WdHq0GyEz6BoA1Ns3JkfUM": "Unit Test HTTP Bridge"
}

def validate_api_key(api_key: str) -> Optional[str]:
    """Validate API key and return client name."""
    if api_key in VALID_API_KEYS:
        client_name = VALID_API_KEYS[api_key]
        # Log client access for tracking
        logger.info(f"API access: {client_name} - Key: {api_key[:8]}***")
        return client_name
    return None

async def validate_client_request(request: Request):
    """Middleware to validate API key."""
    # Skip validation for health checks and docs
    if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
        return None
    
    # Get API key from header
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API key. Include X-API-Key header."
        )
    
    # Validate API key
    client_name = validate_api_key(api_key)
    if not client_name:
        logger.warning(f"Invalid API key attempt: {api_key[:8]}***")
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    # Add client info to request state
    request.state.client_name = client_name
    request.state.api_key = api_key
    
    return client_name