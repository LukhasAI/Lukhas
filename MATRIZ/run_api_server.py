#!/usr/bin/env python3
"""
MATADA-AGI API Server Launcher
Simple script to start the FastAPI server with development settings
"""

import argparse
import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from interfaces.api_server import run_server


def main():
    parser = argparse.ArgumentParser(description="Launch MATADA-AGI FastAPI Server")
    parser.add_argument(
        "--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to listen on (default: 8000)"
    )
    parser.add_argument(
        "--reload", action="store_true", help="Enable auto-reload for development"
    )
    parser.add_argument(
        "--log-level",
        default="info",
        choices=["debug", "info", "warning", "error"],
        help="Log level (default: info)",
    )

    args = parser.parse_args()

    print("🚀 Starting MATADA-AGI FastAPI Server...")
    print(f"📍 Server will be available at: http://{args.host}:{args.port}")
    print(f"📖 API Documentation: http://{args.host}:{args.port}/docs")
    print(f"🔌 WebSocket endpoint: ws://{args.host}:{args.port}/ws")
    print("=" * 60)

    try:
        run_server(
            host=args.host, port=args.port, reload=args.reload, log_level=args.log_level
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
