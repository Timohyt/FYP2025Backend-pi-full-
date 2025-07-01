#!/usr/bin/env python3
"""
Startup script for Traffic Management API Server
Run this on Raspberry Pi to start the backend API
"""

import uvicorn
import os
import sys
from pathlib import Path

def main():
    # Ensure we're in the correct directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Configuration
    host = os.getenv("API_HOST", "0.0.0.0")  # Listen on all interfaces
    port = int(os.getenv("API_PORT", "8000"))
    workers = int(os.getenv("API_WORKERS", "1"))  # Single worker for Pi
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    print(f"🚀 Starting Traffic Management API Server")
    print(f"📡 Host: {host}:{port}")
    print(f"🐛 Debug: {debug}")
    print(f"👥 Workers: {workers}")
    print(f"📁 Working directory: {script_dir}")
    
    try:
        uvicorn.run(
            "app:app",
            host=host,
            port=port,
            workers=workers,
            reload=debug,
            log_level="debug" if debug else "info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n⛔ Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 