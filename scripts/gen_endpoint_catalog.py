#!/usr/bin/env python3
"""
Generate endpoint catalog JSON from OpenAPI specs.

SPDX-License-Identifier: MIT
Author: LUKHAS AI Team
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    import yaml  # type: ignore
except Exception as e:  # pragma: no cover
    raise SystemExit("PyYAML is required: pip install pyyaml") from e


def extract_endpoints(spec_path: Path) -> list[dict]:
    """Extract endpoints from an OpenAPI spec file."""
    with spec_path.open(encoding="utf-8") as f:
        spec = yaml.safe_load(f)

    endpoints: list[dict] = []
    base_url = ""
    servers = spec.get("servers", []) or []
    if servers and isinstance(servers, list) and isinstance(servers[0], dict):
        base_url = servers[0].get("url", "")

    paths = spec.get("paths", {}) or {}
    for path, methods in paths.items():
        if not isinstance(methods, dict):
            continue
        for method, details in methods.items():
            if method.lower() not in {"get", "post", "put", "delete", "patch"}:
                continue
            if not isinstance(details, dict):
                continue
            endpoints.append(
                {
                    "api": spec.get("info", {}).get("title", ""),
                    "path": path,
                    "method": method.upper(),
                    "operation_id": details.get("operationId", ""),
                    "summary": details.get("summary", ""),
                    "tags": details.get("tags", []) or [],
                    "base_url": base_url,
                }
            )

    return endpoints


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate endpoint catalog")
    parser.add_argument("--specs", nargs="+", required=True, help="OpenAPI spec paths (globs ok)")
    parser.add_argument("--out", required=True, help="Output JSON path")
    args = parser.parse_args()

    # Expand globs manually
    paths: list[Path] = []
    for pat in args.specs:
        for p in Path().glob(pat):
            if p.is_file():
                paths.append(p)

    all_endpoints: list[dict] = []
    for spec_path in paths:
        all_endpoints.extend(extract_endpoints(spec_path))

    catalog = {
        "total_endpoints": len(all_endpoints),
        "apis": sorted({e["api"] for e in all_endpoints if e.get("api")}),
        "endpoints": all_endpoints,
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(catalog, indent=2), encoding="utf-8")
    print(f"✅ Generated catalog with {len(all_endpoints)} endpoints → {out_path}")


if __name__ == "__main__":
    main()

