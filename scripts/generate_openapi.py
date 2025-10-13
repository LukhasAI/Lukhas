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
from pathlib import Path


def main():
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
