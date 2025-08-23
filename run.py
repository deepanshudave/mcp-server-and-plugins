"""Simple script to run the FastAPI server."""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.app:app",
        host="0.0.0.0",
        port=8008,
        reload=True,
        log_level="info"
    )