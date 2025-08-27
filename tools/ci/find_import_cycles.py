from __future__ import annotations
import ast
import os
import sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(os.getcwd())
def py_files():
    for p in ROOT.rglob("*.py"):
        if ".git/" in str(p): continue
        yield p

def mod_name(p: Path) -> str:
    rel = p.relative_to(ROOT).with_suffix("")
    return ".".join(rel.parts)

def imports_of(path: Path):
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return []
    mod_name(path)
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names: out.add(a.name)
        elif isinstance(n, ast.ImportFrom) and n.module:
            out.add(n.module)
    # normalize relative-ish to top-level
    return {m.split(".")[0] for m in out if isinstance(m,str)}

def build_graph():
    g = defaultdict(set)
    rev = {}
    for f in py_files():
        m = mod_name(f)
        rev[m] = f
        for imp in imports_of(f):
            g[m].add(imp)
    return g, rev

def find_cycles(g):
    visited, stack = set(), set()
    path = []
    cycles = []

    def dfs(u):
        visited.add(u); stack.add(u); path.append(u)
        for v in g.get(u, ()):
            if v not in visited:
                dfs(v)
            elif v in stack:
                # record cycle
                try:
                    i = path.index(v)
                    cyc = path[i:] + [v]
                    if len(cyc) > 2: cycles.append(cyc)
                except ValueError:
                    pass
        stack.remove(u); path.pop()

    for n in list(g.keys()):
        if n not in visited:
            dfs(n)
    return cycles

if __name__ == "__main__":
    g, rev = build_graph()
    cycles = find_cycles(g)
    out = Path("reports/deep_search/IMPORT_CYCLES.txt")
    out.parent.mkdir(parents=True, exist_ok=True)
    if not cycles:
        out.write_text("No import cycles detected.\n")
        sys.exit(0)
    lines = []
    for c in cycles:
        lines.append(" -> ".join(c))
    out.write_text("\n".join(lines) + "\n")
    print(f"wrote {out}")
