"""
lukhas/__main__.py

Main entry point for LUKHAS AI system.
Enables runtime exporters and provides basic CLI functionality.

Usage:
  python -m lukhas
  LUKHAS_PROM_PORT=9095 python -m lukhas
"""

import logging
import os
import sys

# Enable runtime exporters at startup
from core.metrics_exporters import enable_runtime_exporters

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


enable_runtime_exporters()


def main():
    """Main CLI entry point."""
    logger = logging.getLogger(__name__)

    print("🤖 LUKHAS AI System")
    print("Phase 3: Learning Loop & Observability")

    if os.getenv("LUKHAS_PROM_PORT"):
        print(f"📊 Prometheus metrics: http://localhost:{os.getenv('LUKHAS_PROM_PORT')}/metrics")

    if os.getenv("LUKHAS_OTEL_ENDPOINT"):
        print(f"📡 OTEL endpoint: {os.getenv('LUKHAS_OTEL_ENDPOINT')}")

    print("✅ Runtime exporters initialized")
    print("Press Ctrl+C to exit...")

    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down LUKHAS AI system")
        print("\n👋 LUKHAS AI system stopped")
        sys.exit(0)


if __name__ == "__main__":
    main()
