#!/usr/bin/env python3
"""
T4/0.01% Performance Validation - Production Run
================================================

Runs E2E performance tests with minimal logging for accurate results.
"""

import logging
import os
import sys

# Suppress verbose logging
logging.getLogger().setLevel(logging.CRITICAL)
logging.getLogger('lukhas').setLevel(logging.CRITICAL)
logging.getLogger('governance').setLevel(logging.CRITICAL)
logging.getLogger('memory').setLevel(logging.CRITICAL)

# Import after configuring logging
from bench_e2e import main

if __name__ == "__main__":
    # Set environment for reproducibility
    os.environ['PYTHONHASHSEED'] = '0'
    os.environ['LUKHAS_MODE'] = 'release'
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

    sys.exit(main())
