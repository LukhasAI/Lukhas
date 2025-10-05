#!/usr/bin/env python3
import json
import sys

try:
    payload = json.loads(sys.stdin.read())
    assert "code" in payload and "stdout" in payload and "stderr" in payload
    print("ok")
except Exception as e:
    print("non-json or invalid tool envelope:", e); sys.exit(1)
