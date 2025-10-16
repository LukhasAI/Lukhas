#!/usr/bin/env python3
"""
Generate OpenAPI spec with production metadata polish.

Adds:
- openapi version 3.1.0
- servers (prod + local)
- x-service-version (git SHA short)

Usage:
  python3 scripts/generate_openapi.py

Outputs to: docs/openapi/lukhas-openai.json
"""
import os
import json
import sys
from pathlib import Path


def main():
    # Ensure repo root is in path for lukhas imports
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    # Import FastAPI app factory
    from lukhas.adapters.openai.api import get_app

    app = get_app()
    spec = app.openapi()

    # Polish metadata
    spec["openapi"] = "3.1.0"
    spec.setdefault("info", {})
    spec["info"].setdefault("title", "LUKHAS OpenAI-Compatible API")
    spec["info"]["version"] = spec.get("info", {}).get("version", "0.9.0")

    # Add git SHA if available (CI provides GITHUB_SHA)
    git_sha = os.environ.get("GITHUB_SHA", "dev")[:7]
    spec["info"]["x-service-version"] = git_sha

    # Add server URLs
    spec["servers"] = [
        {"url": "https://api.lukhas.ai", "description": "Production"},
        {"url": "http://localhost:8000", "description": "Local Development"},
    ]

    # Phase 3: Add reusable header components
    spec.setdefault("components", {})
    spec["components"].setdefault("headers", {})

    spec["components"]["headers"]["X-Trace-Id"] = {
        "description": "W3C trace context ID (32-char hex) for request correlation",
        "schema": {"type": "string", "pattern": "^[0-9a-f]{32}$"},
        "example": "4bf92f3577b34da6a3ce929d0e0e4736"
    }

    spec["components"]["headers"]["X-Service-Version"] = {
        "description": "Deployment version (git SHA or version string)",
        "schema": {"type": "string"},
        "example": "a3f2d1c"
    }

    # OpenAI-compatible rate limit headers (Phase 3.1 Guardian)
    spec["components"]["headers"]["X-RateLimit-Limit"] = {
        "description": "Max requests allowed in the current window",
        "schema": {"type": "integer", "minimum": 0}
    }

    spec["components"]["headers"]["X-RateLimit-Remaining"] = {
        "description": "Requests remaining in the current window",
        "schema": {"type": "integer", "minimum": 0}
    }

    spec["components"]["headers"]["X-RateLimit-Reset"] = {
        "description": "Epoch seconds until the current window resets",
        "schema": {"type": "integer", "format": "int64", "minimum": 0}
    }

    # Legacy headers (backward compat)
    spec["components"]["headers"]["X-RateLimit-Limit-Requests"] = {
        "description": "Maximum requests allowed in the current window (legacy)",
        "schema": {"type": "integer", "minimum": 1}
    }

    spec["components"]["headers"]["X-RateLimit-Remaining-Requests"] = {
        "description": "Remaining requests in the current window (legacy)",
        "schema": {"type": "integer", "minimum": 0}
    }

    spec["components"]["headers"]["X-RateLimit-Reset-Requests"] = {
        "description": "Seconds until the rate limit window resets (legacy)",
        "schema": {"type": "string"},
        "example": "42.150"
    }

    spec["components"]["headers"]["Retry-After"] = {
        "description": "Seconds to wait before retrying (429 responses only)",
        "schema": {"type": "integer", "minimum": 1}
    }

    # Attach headers to all response definitions
    for path_item in spec.get("paths", {}).values():
        for operation in path_item.values():
            if not isinstance(operation, dict) or "responses" not in operation:
                continue

            for status_code, response_obj in operation["responses"].items():
                if not isinstance(response_obj, dict):
                    continue

                response_obj.setdefault("headers", {})

                # All responses get trace and version headers
                response_obj["headers"]["X-Trace-Id"] = {"$ref": "#/components/headers/X-Trace-Id"}
                response_obj["headers"]["X-Service-Version"] = {"$ref": "#/components/headers/X-Service-Version"}

                # Success responses (2xx) and error responses (4xx/5xx) get rate-limit headers
                if str(status_code).startswith(("2", "4", "5")):
                    # New OpenAI-compatible headers
                    response_obj["headers"]["X-RateLimit-Limit"] = {
                        "$ref": "#/components/headers/X-RateLimit-Limit"
                    }
                    response_obj["headers"]["X-RateLimit-Remaining"] = {
                        "$ref": "#/components/headers/X-RateLimit-Remaining"
                    }
                    response_obj["headers"]["X-RateLimit-Reset"] = {
                        "$ref": "#/components/headers/X-RateLimit-Reset"
                    }
                    # Legacy headers for backward compat
                    response_obj["headers"]["X-RateLimit-Limit-Requests"] = {
                        "$ref": "#/components/headers/X-RateLimit-Limit-Requests"
                    }
                    response_obj["headers"]["X-RateLimit-Remaining-Requests"] = {
                        "$ref": "#/components/headers/X-RateLimit-Remaining-Requests"
                    }
                    response_obj["headers"]["X-RateLimit-Reset-Requests"] = {
                        "$ref": "#/components/headers/X-RateLimit-Reset-Requests"
                    }

                # 429 responses get Retry-After header
                if str(status_code) == "429":
                    response_obj["headers"]["Retry-After"] = {"$ref": "#/components/headers/Retry-After"}

    # Ensure output directory exists
    out_dir = Path("docs/openapi")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Write spec
    out_file = out_dir / "lukhas-openai.json"
    with open(out_file, "w") as f:
        json.dump(spec, f, indent=2)

    print(f"✅ Generated OpenAPI spec: {out_file}")
    print(f"   Version: {spec['info']['version']}")
    print(f"   Service: {git_sha}")
    print(f"   Servers: {len(spec['servers'])}")
    print(f"   Paths: {len(spec.get('paths', {}))}")


if __name__ == "__main__":
    main()
