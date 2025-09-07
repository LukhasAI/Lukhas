"""
LUKHAS AI Core Settings
Central configuration for feature flags and system parameters
"""
import time
import streamlit as st

import os
from datetime import datetime

# Feature Flags (DEFAULT: OFF in production)
UL_ENABLED = os.getenv("UL_ENABLED", "false").lower() == "true"
VIVOX_LITE = os.getenv("VIVOX_LITE", "false").lower() == "true"
QIM_SANDBOX = os.getenv("QIM_SANDBOX", "false").lower() == "true"

# Core Surface API Version
BUS_SCHEMA_VERSION = os.getenv("BUS_SCHEMA_VERSION", "v1")

# Deprecation & Migration
SHIM_CULL_DATE = datetime.fromisoformat(os.getenv("SHIM_CULL_DATE", "2025-11-01"))

# Performance Targets
AUTH_P95_TARGET_MS = int(os.getenv("AUTH_P95_TARGET_MS", "100"))
CONTEXT_P95_TARGET_MS = int(os.getenv("CONTEXT_P95_TARGET_MS", "250"))

# Environment
LUKHAS_ENV = os.getenv("LUKHAS_ENV", "development")
IS_PRODUCTION = LUKHAS_ENV == "production"

# Security
LUKHAS_ID_SECRET = os.getenv("LUKHAS_ID_SECRET", "")
ETHICS_ENFORCEMENT_LEVEL = os.getenv("ETHICS_ENFORCEMENT_LEVEL", "strict")

# Trinity Framework
DREAM_SIMULATION_ENABLED = os.getenv("DREAM_SIMULATION_ENABLED", "false").lower() == "true"
QUANTUM_PROCESSING_ENABLED = os.getenv("QUANTUM_PROCESSING_ENABLED", "false").lower() == "true"

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///lukhas.db")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# API Configuration
API_RATE_LIMIT = int(os.getenv("API_RATE_LIMIT", "100"))
MEMORY_FOLD_LIMIT = int(os.getenv("MEMORY_FOLD_LIMIT", "1000"))
DRIFT_THRESHOLD = float(os.getenv("DRIFT_THRESHOLD", "0.15"))


def validate_settings():
    """Validate critical settings on startup"""
    errors = []

    # Check required settings
    if IS_PRODUCTION:
        if not LUKHAS_ID_SECRET or len(LUKHAS_ID_SECRET) < 32:
            errors.append("LUKHAS_ID_SECRET must be at least 32 characters in production")

        # Ensure feature flags are OFF in production
        if UL_ENABLED or VIVOX_LITE or QIM_SANDBOX:
            errors.append("Feature flags must be OFF in production")

    # Check performance targets
    if AUTH_P95_TARGET_MS <= 0:
        errors.append("AUTH_P95_TARGET_MS must be positive")

    if CONTEXT_P95_TARGET_MS <= 0:
        errors.append("CONTEXT_P95_TARGET_MS must be positive")

    # Check drift threshold
    if not 0.0 <= DRIFT_THRESHOLD <= 1.0:
        errors.append("DRIFT_THRESHOLD must be between 0.0 and 1.0")

    return errors


# Run validation on import
validation_errors = validate_settings()
if validation_errors:
    import sys

    print("❌ Settings validation failed:", file=sys.stderr)
    for error in validation_errors:
        print(f"  - {error}", file=sys.stderr)
    if IS_PRODUCTION:
        sys.exit(1)
