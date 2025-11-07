#!/usr/bin/env python3
import json
import os
import pathlib
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional

# Import telemetry shim
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "tools", "mcp"))
from telemetry_shim import wrap_result

CATALOG = json.loads(pathlib.Path(__file__).parent.joinpath("tooling/catalog.json").read_text())

def timed_run_tool(tool: dict[str, Any], stdin: Optional[str] = None) -> dict[str, Any]:
    # Safe by default: Block unsafe tools unless explicitly enabled
    if tool.get("safe") is False and os.environ.get("ALLOW_UNSAFE_TOOLS") != "1":
        return wrap_result(tool["name"], 2, "", "blocked: unsafe tool (set ALLOW_UNSAFE_TOOLS=1)")

    # RBAC: Block conveyor.execute if disabled
    if tool["name"] == "conveyor.execute" and os.environ.get("MCP_CONVEYOR_DISABLED") == "1":
        return wrap_result(tool["name"], 2, "", "blocked by CI policy")

    cmd = tool["command"]["exec"].split() + tool["command"].get("args", [])
    t0 = time.time()
    proc = subprocess.run(cmd, input=stdin, text=True, capture_output=True)
    dt = (time.time() - t0) * 1000

    # Emit latency metrics to stderr
    print(json.dumps({"event":"mcp.tool","name":tool["name"],"ms":dt}), file=sys.stderr)

    return wrap_result(tool["name"], proc.returncode, proc.stdout, proc.stderr)

def list_tools() -> list[dict[str, Any]]:
    ns = CATALOG["namespace"]
    out = []
    for t in CATALOG["tools"]:
        out.append({"name": f"{ns}.{t['name']}", "args": t.get("command", {}).get("args", [])})
    return out

# Minimal MCP-like stdio handling (simplified): supports list/run
def main():
    for line in sys.stdin:
        req = json.loads(line)
        if req.get("method") == "tools/list":
            sys.stdout.write(json.dumps({"id": req["id"], "result": list_tools()}) + "\n"); sys.stdout.flush()  # TODO[T4-ISSUE]: {"code":"E702","ticket":"GH-1031","owner":"consciousness-team","status":"planned","reason":"Multiple statements on one line - split for readability","estimate":"5m","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_mcp_servers_lukhas_devtools_mcp_server_py_L47"}
        elif req.get("method") == "tools/run":
            name = req["params"]["name"]
            _ns, short = name.split(".", 1)
            tool = next((t for t in CATALOG["tools"] if t["name"] == short), None)
            if not tool:
                sys.stdout.write(json.dumps({"id": req["id"], "error":{"message":"unknown tool"}}) + "\n"); sys.stdout.flush(); continue  # TODO[T4-ISSUE]: {"code":"E702","ticket":"GH-1031","owner":"consciousness-team","status":"planned","reason":"Multiple statements on one line - split for readability","estimate":"5m","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_mcp_servers_lukhas_devtools_mcp_server_py_L53"}
            stdin = req["params"].get("stdin")
            res = timed_run_tool(tool, stdin=stdin)
            sys.stdout.write(json.dumps({"id": req["id"], "result": res}) + "\n"); sys.stdout.flush()  # TODO[T4-ISSUE]: {"code":"E702","ticket":"GH-1031","owner":"consciousness-team","status":"planned","reason":"Multiple statements on one line - split for readability","estimate":"5m","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_mcp_servers_lukhas_devtools_mcp_server_py_L56"}
        elif req.get("method") == "health/ping":
            sys.stdout.write(json.dumps({"id": req["id"], "result": {"ok": True}}) + "\n"); sys.stdout.flush()  # TODO[T4-ISSUE]: {"code":"E702","ticket":"GH-1031","owner":"consciousness-team","status":"planned","reason":"Multiple statements on one line - split for readability","estimate":"5m","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_mcp_servers_lukhas_devtools_mcp_server_py_L58"}
        elif req.get("method") == "health/info":
            import subprocess
            try:
                # Use relative path from server directory
                out = subprocess.check_output(["python3", "health.py"], cwd=os.path.dirname(__file__))
                health_data = json.loads(out.decode())
                sys.stdout.write(json.dumps({"id": req["id"], "result": health_data}) + "\n"); sys.stdout.flush()  # TODO[T4-ISSUE]: {"code":"E702","ticket":"GH-1031","owner":"consciousness-team","status":"planned","reason":"Multiple statements on one line - split for readability","estimate":"5m","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_mcp_servers_lukhas_devtools_mcp_server_py_L65"}
            except Exception as e:
                sys.stdout.write(json.dumps({"id": req["id"], "error": {"message": f"health check failed: {e}"}}) + "\n"); sys.stdout.flush()  # TODO[T4-ISSUE]: {"code":"E702","ticket":"GH-1031","owner":"consciousness-team","status":"planned","reason":"Multiple statements on one line - split for readability","estimate":"5m","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_mcp_servers_lukhas_devtools_mcp_server_py_L67"}

if __name__ == "__main__":
    main()
