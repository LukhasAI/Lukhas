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
from core.metrics_exporters import enable_runtime_exporters
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
