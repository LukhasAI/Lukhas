#!/usr/bin/env python3
"""
OpenAPI rate-limit headers guard.

Validates that the generated OpenAPI spec includes X-RateLimit-* headers
on all 2xx/4xx/5xx responses as required by OpenAI compatibility standards.

Exit codes:
  0 - All required headers present
  1 - Missing headers or validation failed
"""
import json
import sys
from pathlib import Path


def main():
    spec_path = Path("docs/openapi/lukhas-openai.json")
    if not spec_path.exists():
        print(f"❌ OpenAPI spec not found: {spec_path}")
        return 1

    with open(spec_path) as f:
        spec = json.load(f)

    required_headers = {"X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"}
    missing_headers = []

    # Check all paths for 2xx/4xx/5xx responses
    for path, methods in spec.get("paths", {}).items():
        for method, operation in methods.items():
            if not isinstance(operation, dict) or "responses" not in operation:
                continue

            for status_code, response_obj in operation["responses"].items():
                if not isinstance(response_obj, dict):
                    continue

                # Only check 2xx/4xx/5xx responses
                if not str(status_code).startswith(("2", "4", "5")):
                    continue

                response_headers = set(response_obj.get("headers", {}).keys())
                missing = required_headers - response_headers

                if missing:
                    missing_headers.append({
                        "path": path,
                        "method": method.upper(),
                        "status": status_code,
                        "missing": list(missing),
                    })

    if missing_headers:
        print("❌ Missing X-RateLimit-* headers in OpenAPI spec:")
        for issue in missing_headers:
            print(f"  {issue['method']} {issue['path']} [{issue['status']}]: missing {', '.join(issue['missing'])}")
        return 1

    print("✅ OpenAPI spec includes all required X-RateLimit-* headers")
    print(f"   Validated: {spec_path}")
    print(f"   Paths checked: {len(spec.get('paths', {}))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
