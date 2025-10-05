#!/usr/bin/env python3
import json, os, subprocess, sys, pathlib, time
from typing import Dict, Any, List, Optional, Union
CATALOG = json.loads(pathlib.Path(__file__).parent.joinpath("tooling/catalog.json").read_text())

def timed_run_tool(tool: Dict[str, Any], stdin: Optional[str] = None) -> Dict[str, Any]:
    # RBAC: Block conveyor.execute if disabled
    if tool["name"] == "conveyor.execute" and os.environ.get("MCP_CONVEYOR_DISABLED") == "1":
        return {"code": 2, "stdout": "", "stderr": "blocked by CI policy"}
    
    cmd = tool["entry"].split() + tool.get("args", [])
    t0 = time.time()
    proc = subprocess.run(cmd, input=stdin, text=True, capture_output=True)
    dt = (time.time() - t0) * 1000
    
    # Emit latency metrics to stderr
    print(json.dumps({"event":"mcp.tool","name":tool["name"],"ms":dt}), file=sys.stderr)
    
    return {"code": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}

def list_tools() -> List[Dict[str, Any]]:
    ns = CATALOG["namespace"]
    out = []
    for t in CATALOG["tools"]:
        out.append({"name": f"{ns}.{t['name']}", "args": t.get("args", [])})
    return out

# Minimal MCP-like stdio handling (simplified): supports list/run
def main():
    for line in sys.stdin:
        req = json.loads(line)
        if req.get("method") == "tools/list":
            sys.stdout.write(json.dumps({"id": req["id"], "result": list_tools()}) + "\n"); sys.stdout.flush()
        elif req.get("method") == "tools/run":
            name = req["params"]["name"]
            ns, short = name.split(".", 1)
            tool = next((t for t in CATALOG["tools"] if t["name"] == short), None)
            if not tool:
                sys.stdout.write(json.dumps({"id": req["id"], "error":{"message":"unknown tool"}}) + "\n"); sys.stdout.flush(); continue
            stdin = req["params"].get("stdin")
            res = timed_run_tool(tool, stdin=stdin)
            sys.stdout.write(json.dumps({"id": req["id"], "result": res}) + "\n"); sys.stdout.flush()
        elif req.get("method") == "health/ping":
            sys.stdout.write(json.dumps({"id": req["id"], "result": {"ok": True}}) + "\n"); sys.stdout.flush()

if __name__ == "__main__":
    main()