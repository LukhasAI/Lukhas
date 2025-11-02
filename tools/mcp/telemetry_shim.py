import json
import re
import sys
import time

REDACT = [("api_key", r"(?i)(api[_-]?key|token)\s*[:=]\s*\S+"), ("secret", r"(?i)(secret|password)\s*[:=]\s*\S+")]


def redact(s: str) -> str:
    out = s
    for _, pat in REDACT:
        out = re.sub(pat, "[REDACTED]", out)
    return out


def emit(event: dict):
    event["ts"] = time.time()
    print(json.dumps(event, sort_keys=True), file=sys.stderr, flush=True)


def wrap_result(tool_name: str, code: int, stdout: str, stderr: str):
    emit({"event": "mcp.tool", "name": tool_name, "code": code, "bytes": len(stdout)})
    return {"code": code, "stdout": redact(stdout), "stderr": redact(stderr)}
