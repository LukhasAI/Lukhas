#!/usr/bin/env python3
"""
Export OpenAI tool specs from manifests.
Writes build/openai_tools.json with:
  {"tools":[{"type":"function","function":{"name": "...","description":"...","parameters":{...}}}, ...]}
"""
import json, sys
from pathlib import Path

def main():
    out = Path("build"); out.mkdir(parents=True, exist_ok=True)
    tools = []
    for mf in Path("manifests").rglob("module.manifest.json"):
        try:
            m = json.loads(mf.read_text(encoding="utf-8"))
        except Exception:
            continue
        for cap in m.get("capabilities", []):
            name = cap.get("name") or cap.get("id") or mf.stem
            tools.append({"type":"function","function":{"name": name[:64], "description": cap.get("description",""), "parameters": cap.get("schema", {})}})
    (out/"openai_tools.json").write_text(json.dumps({"tools": tools}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[tools] wrote {out/'openai_tools.json'} with {len(tools)} tools")

if __name__ == "__main__":
    sys.exit(main())
