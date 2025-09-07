#!/usr/bin/env python3
import ast
import sys
from pathlib import Path

import streamlit as st


def main() -> int:
    hits = []
    for p in Path("lukhas").rglob("*.py"):
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
            t = ast.parse(text)
        except Exception:
            continue
        for n in ast.walk(t):
            if isinstance(n, ast.Import):
                if any((a.name or "").split(".")[0] == "candidate" for a in n.names):
                    hits.append(f"{p}:{getattr(n, 'lineno', 1)}: import candidate")
            elif isinstance(n, ast.ImportFrom) and ((n.module or "").split(".")[0]) == "candidate":
                hits.append(f"{p}:{getattr(n, 'lineno', 1)}: from candidate import")
    if hits:
        print("\n".join(hits))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
