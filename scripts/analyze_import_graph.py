#!/usr/bin/env python3
import ast
import sys
from collections import defaultdict
from pathlib import Path

ROOT="lukhas"
edges = defaultdict(set)

def mod_from_file(py: Path):
    rel = py.relative_to(Path(".").resolve())
    parts = list(rel.parts)
    if parts[0]!=ROOT: return None
    if parts[-1]=="__init__.py": parts=parts[:-1]
    else: parts[-1]=parts[-1].replace(".py","")
    return ".".join(parts)

def imports_in(py: Path):
    try:
        t = ast.parse(py.read_text(encoding="utf-8"))
    except Exception:
        return []
    out=[]
    for n in ast.walk(t):
        if isinstance(n, ast.ImportFrom) and n.module and not n.level:
            out.append(n.module)
        elif isinstance(n, ast.Import):
            for a in n.names: out.append(a.name.split(".")[0])
    return out

mods={}
for py in Path(ROOT).rglob("*.py"):
    m = mod_from_file(py)
    if not m: continue
    mods[m]=py
    for imp in imports_in(py):
        if imp.startswith(ROOT):
            edges[m].add(imp)

# find cycles (simple DFS)
seen=set(); stack=set(); order=[]
cycles=[]
def dfs(u):
    seen.add(u); stack.add(u)
    for v in edges[u]:
        if v not in seen: dfs(v)
        elif v in stack: cycles.append((u,v))
    stack.remove(u); order.append(u)

for m in mods:
    if m not in seen: dfs(m)

if cycles:
    print("[CYCLES]")
    for u,v in cycles:
        print(f" - {u} -> {v}")
    sys.exit(1)
print("[OK] no cycles")
