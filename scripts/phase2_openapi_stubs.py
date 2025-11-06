#!/usr/bin/env python3
"""
Phase 2: Generate OpenAPI Stubs for Flagship APIs

Creates OpenAPI 3.0 stubs for flagship constellation modules:
- Dream (consciousness expansion)
- MATRIZ (cognitive DNA processing)
- Guardian (ethical oversight)
- Identity (λID authentication)
- Memory (trail navigation)

Usage:
  python scripts/phase2_openapi_stubs.py --output docs/openapi/stubs
"""
from __future__ import annotations

import argparse
import json
import pathlib
from datetime import datetime, timezone
from typing import Any, Dict

ROOT = pathlib.Path(__file__).resolve().parents[1]

# Flagship API Definitions (Phase 2 - EXECUTION_PLAN.md)
FLAGSHIP_APIS = {
    "dream": {
        "title": "LUKHAS Dream API",
        "description": "Consciousness expansion and dream state processing",
        "star": "🌙 Drift (Dream)",
        "base_path": "/v1/dream",
        "endpoints": [
            {"path": "/expand", "method": "post", "summary": "Initiate dream expansion"},
            {"path": "/collapse", "method": "post", "summary": "Collapse dream state"},
            {"path": "/resonance", "method": "get", "summary": "Query resonance field"},
        ],
    },
    "matriz": {
        "title": "LUKHAS MATRIZ API",
        "description": "Cognitive DNA processing and node orchestration",
        "star": "⚛️ Quantum (Processing)",
        "base_path": "/v1/matriz",
        "endpoints": [
            {"path": "/nodes", "method": "post", "summary": "Create cognitive node"},
            {"path": "/nodes/{node_id}", "method": "get", "summary": "Retrieve node"},
            {"path": "/query", "method": "post", "summary": "Execute cognitive query"},
            {"path": "/trace", "method": "get", "summary": "Get reasoning trace"},
        ],
    },
    "guardian": {
        "title": "LUKHAS Guardian API",
        "description": "Constitutional AI and ethical oversight",
        "star": "🛡️ Watch (Guardian)",
        "base_path": "/v1/guardian",
        "endpoints": [
            {"path": "/audit", "method": "post", "summary": "Submit for ethical audit"},
            {"path": "/policies", "method": "get", "summary": "List active policies"},
            {"path": "/drift", "method": "get", "summary": "Detect consciousness drift"},
        ],
    },
    "identity": {
        "title": "LUKHAS Identity API",
        "description": "Lambda ID (λID) authentication and tiering",
        "star": "⚛️ Anchor (Identity)",
        "base_path": "/v1/identity",
        "endpoints": [
            {"path": "/authenticate", "method": "post", "summary": "Authenticate user"},
            {"path": "/tier", "method": "get", "summary": "Get tier eligibility"},
            {"path": "/session", "method": "post", "summary": "Create session"},
        ],
    },
    "memory": {
        "title": "LUKHAS Memory API",
        "description": "Fold-based memory retrieval and trail navigation",
        "star": "✦ Trail (Memory)",
        "base_path": "/v1/memory",
        "endpoints": [
            {"path": "/fold", "method": "post", "summary": "Create memory fold"},
            {"path": "/recall", "method": "post", "summary": "Recall memories"},
            {"path": "/trail", "method": "get", "summary": "Navigate memory trail"},
        ],
    },
}


def generate_openapi_stub(api_name: str, api_def: Dict[str, Any]) -> Dict[str, Any]:
    """Generate OpenAPI 3.0 stub for a flagship API."""

    paths: Dict[str, Any] = {}
    for endpoint in api_def["endpoints"]:
        path = api_def["base_path"] + endpoint["path"]
        method = endpoint["method"]

        paths[path] = {
            method: {
                "summary": endpoint["summary"],
                "operationId": f"{api_name}_{path.replace('/', '_')}_{method}",
                "tags": [api_name.capitalize()],
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string", "example": "success"},
                                        "data": {"type": "object"},
                                    },
                                },
                            },
                        },
                    },
                    "400": {"description": "Bad request"},
                    "401": {"description": "Unauthorized"},
                    "500": {"description": "Internal server error"},
                },
                "security": [{"BearerAuth": []}],
            },
        }

    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": api_def["title"],
            "description": f"{api_def['description']}\n\n**Constellation Star**: {api_def['star']}",
            "version": "1.0.0",
            "contact": {
                "name": "LUKHAS AI Platform",
                "url": "https://ai",
            },
        },
        "servers": [
            {"url": "https://api.ai", "description": "Production"},
            {"url": "http://localhost:8000", "description": "Development"},
        ],
        "paths": paths,
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": "Lambda ID (λID) JWT token",
                },
            },
        },
        "tags": [
            {"name": api_name.capitalize(), "description": api_def["description"]},
        ],
    }

    return spec


def main():
    parser = argparse.ArgumentParser(description="Phase 2: Generate OpenAPI Stubs")
    parser.add_argument("--output", default="docs/openapi/stubs", help="Output directory")
    args = parser.parse_args()

    output_dir = pathlib.Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating OpenAPI stubs for {len(FLAGSHIP_APIS)} flagship APIs\n")

    created = []
    for api_name, api_def in FLAGSHIP_APIS.items():
        spec = generate_openapi_stub(api_name, api_def)

        stub_path = output_dir / f"lukhas-{api_name}-api.json"
        stub_path.write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")

        print(f"[OK] {stub_path.name}")
        print(f"     {api_def['title']}")
        print(f"     Star: {api_def['star']}")
        print(f"     Endpoints: {len(api_def['endpoints'])}")
        print()

        created.append(stub_path.name)

    # Create index README
    readme = output_dir / "README.md"
    readme_content = f"""# LUKHAS OpenAPI Stubs

**Generated**: {datetime.now(timezone.utc).isoformat()}
**Purpose**: Flagship API stubs for ecosystem integration

## Flagship APIs ({len(created)})

"""

    for api_name, api_def in FLAGSHIP_APIS.items():
        readme_content += f"- **{api_def['title']}** (`lukhas-{api_name}-api.json`)\n"
        readme_content += f"  - {api_def['description']}\n"
        readme_content += f"  - Constellation: {api_def['star']}\n"
        readme_content += f"  - Endpoints: {len(api_def['endpoints'])}\n\n"

    readme_content += """## Usage

```bash
# Validate OpenAPI spec
openapi-spec-validator docs/openapi/stubs/lukhas-dream-api.json

# Generate client SDK
openapi-generator generate -i docs/openapi/stubs/lukhas-matriz-api.json -g python -o sdk/python
```

## Integration

These stubs are designed for:
1. **External ecosystem integration** (Claude Desktop, Cursor, etc.)
2. **SDK generation** (Python, TypeScript, Go clients)
3. **API contract testing** (Dredd, Postman)
4. **Documentation generation** (Redoc, Swagger UI)
"""

    readme.write_text(readme_content, encoding="utf-8")
    print(f"[OK] {readme.name}\n")

    print(f"{'=' * 60}")
    print(f"Summary: {len(created)} OpenAPI stubs created")
    print(f"Output: {output_dir}")


if __name__ == "__main__":
    main()
