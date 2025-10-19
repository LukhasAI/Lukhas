#!/usr/bin/env python3
"""
Module: policy_guard.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

"""
Fail if T1_critical modules contain eval/exec/subprocess.* unless whitelisted via manifest.security.policies.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFESTS = list(ROOT.rglob("module.manifest.json"))
BAN = [r"\beval\(", r"\bexec\(", r"\bsubprocess\."]
ALLOW_TAG = "allow-dangerous-exec"

def code_files_for_module(path_rel: str):
    p = ROOT / path_rel
    if p.is_dir():
        yield from p.rglob("*.py")
    else:
        # best effort: derive from module path
        yield from (ROOT / path_rel).parent.rglob("*.py")

def main():
    fails = []
    for mf in MANIFESTS:
        m = json.loads(mf.read_text(encoding="utf-8"))
        tier = m.get("testing",{}).get("quality_tier")
        if tier != "T1_critical":
            continue
        policies = set(m.get("security",{}).get("policies",[]))
        if ALLOW_TAG in policies:
            continue
        mod_path = m.get("module",{}).get("path")
        if not mod_path:
            continue
        for f in code_files_for_module(mod_path):
            text = f.read_text(encoding="utf-8", errors="ignore")
            for pat in BAN:
                if re.search(pat, text):
                    fails.append(f"{f}:{pat}")
    if fails:
        print("Policy violations:\n" + "\n".join(fails[:50]))
        sys.exit(1)
    print("Guardian belt: OK")

if __name__ == "__main__":
    main()
