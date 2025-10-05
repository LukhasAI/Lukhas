#!/usr/bin/env python3
import json, subprocess, sys, os, tempfile, pathlib
srv = ["python3","mcp-servers/lukhas-devtools-mcp/server.py"]
p = subprocess.Popen(srv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
def rpc(method, params=None, id=1):
    p.stdin.write(json.dumps({"jsonrpc":"2.0","id":id,"method":method,"params":params or {}})+"\n"); p.stdin.flush()
    line = p.stdout.readline().strip()
    print(line)
rpc("tools/list")
rpc("health/ping", {})
p.terminate()