#!/usr/bin/env python3
"""
Module: validate_openapi.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

"""Validate OpenAPI spec against OpenAPI 3.1 schema."""
import json
from pathlib import Path

try:
    from openapi_spec_validator import openapi_v3_spec_validator
except ImportError:
    print("❌ openapi-spec-validator not installed. Run: pip install openapi-spec-validator")
    exit(1)

spec_path = Path("docs/openapi/lukhas-openai.json")
if not spec_path.exists():
    print(f"❌ OpenAPI spec not found: {spec_path}")
    exit(1)

spec = json.load(open(spec_path))
errors = list(openapi_v3_spec_validator.iter_errors(spec))

if errors:
    print(f"❌ OpenAPI schema errors: {errors[:5]}")
    exit(1)

print("✅ OpenAPI validation passed")
