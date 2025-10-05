#!/usr/bin/env python3
import json, hashlib, os, pathlib, time

# Get absolute path to catalog relative to this script
script_dir = pathlib.Path(__file__).parent
CAT = script_dir / "tooling/catalog.json"
sha = hashlib.sha256(CAT.read_bytes()).hexdigest()[:12]
print(json.dumps({
  "service": "lukhas-devtools-mcp",
  "version": os.getenv("MCP_VERSION","0.1.0"),
  "catalog_sha": sha,
  "tool_count": len(json.loads(CAT.read_text())["tools"]),
  "p95_ms_last_run": float(os.getenv("MCP_P95_MS_LAST","0")),
  "time": time.time()
}, sort_keys=True))