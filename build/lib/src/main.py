"""Main entry point for the weather FastAPI server."""

import uvicorn
from .app import app

def main():
    """Main entry point."""
    uvicorn.run(
        "src.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()