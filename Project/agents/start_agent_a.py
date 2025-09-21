#!/usr/bin/env python3
"""
Startup script for Agent A service
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    """Start the Agent A service"""
    print("Starting Agent A (Buyer Logic) service...")
    print("=" * 50)
    
    # Set default environment variables if not set
    os.environ.setdefault("USE_MOCK_BEDROCK", "true")
    os.environ.setdefault("LOG_LEVEL", "INFO")
    os.environ.setdefault("PORT", "8001")
    os.environ.setdefault("HOST", "0.0.0.0")
    
    # Print configuration
    print(f"Configuration:")
    print(f"  Mock Bedrock: {os.getenv('USE_MOCK_BEDROCK')}")
    print(f"  Log Level: {os.getenv('LOG_LEVEL')}")
    print(f"  Host: {os.getenv('HOST')}")
    print(f"  Port: {os.getenv('PORT')}")
    print("=" * 50)
    
    # Start the service
    try:
        uvicorn.run(
            "agent_a.main:app",
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8001")),
            log_level=os.getenv("LOG_LEVEL", "info").lower(),
            reload=False
        )
    except KeyboardInterrupt:
        print("\nService stopped by user")
    except Exception as e:
        print(f"Failed to start service: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

