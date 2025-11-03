#!/usr/bin/env python3
"""
Generate a draft flatten_map.csv using discovery outputs.

Input:
  release_artifacts/matriz_readiness_v1/discovery/top_python_files.txt
  release_artifacts/matriz_readiness_v1/discovery/from_imports.txt
  release_artifacts/matriz_readiness_v1/discovery/simple_imports.txt

Output:
  release_artifacts/matriz_readiness_v1/flatten_map.csv

Heuristics:
  - score = depth * 2 + import_count
  - If import_count > 8 => strategy = shim (high centrality)
  - If import_count 4..8 => strategy = shim (medium)
  - Else => move
  - risk: high if import_count > 12 or depth > 5, medium if import_count >6 or depth 4-5
"""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
import argparse

ART_DIR = Path("release_artifacts/matriz_readiness_v1")
DISC = ART_DIR / "discovery"

def load_top_files(path):
    if not path.exists():
        raise SystemExit(f"Discovery top file missing: {path}")
    files = []
    for ln in path.read_text().splitlines():
        ln = ln.strip()
        if not ln: continue
        # file may be prefixed by numbers or depth; strip integers
        if ln.split()[0].isdigit():
            parts = ln.split()
            # if format "N path"
            if len(parts) >= 2:
                files.append(parts[1])
            else:
                files.append(parts[0])
        else:
            files.append(ln)
    return files

def count_imports(imports_file):
    c = Counter()
    if not imports_file.exists():
        return c
    for ln in imports_file.read_text().splitlines():
        ln = ln.strip()
        if not ln: continue
        # lines like "path: from package.module import X"
        # attempt to extract module token
        # fallback: split by whitespace and look for tokens separated by '.' with lowercase
        parts = ln.split()
        for token in parts:
            if "." in token and token[0].isalpha():
                mod = token.strip(",()")
                c[mod] += 1
    return c

def module_candidates(top_files, from_counts, simple_counts, limit=50):
    # compute import_count per file by checking occurrences of their dotted module roots
    candidates = []
    for f in top_files:
        depth = f.count("/")
        # infer module root e.g., candidate/core/matrix/nodes/memory_node.py -> candidate.core.matrix.nodes.memory_node
        mod = f.replace("/", ".").rstrip(".py")
        # aggregate import counts by seeing if module appears as prefix in import counts
        ic = 0
        for im, cnt in list(from_counts.items()) + list(simple_counts.items()):
            if im.startswith(mod) or mod.startswith(im) or im.startswith(mod.split(".")[0]):
                ic += cnt
        score = depth * 2 + ic
        candidates.append((score, depth, ic, f))
    # sort by score desc, return top limit
    candidates.sort(reverse=True, key=lambda x: (x[0], x[2], x[1]))
    return candidates[:limit]

def decide_strategy(depth, import_count):
    if import_count >= 9 or depth >= 5:
        return "shim"
    if import_count >= 4:
        return "shim"
    return "move"

def risk_level(depth, import_count):
    if import_count >= 13 or depth >= 7:
        return "high"
    if import_count >= 7 or depth >= 5:
        return "medium"
    return "low"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--top", default=DISC/"top_python_files.txt")
    parser.add_argument("--from_imports", default=DISC/"from_imports.txt")
    parser.add_argument("--simple_imports", default=DISC/"simple_imports.txt")
    parser.add_argument("--out", default=ART_DIR/"flatten_map.csv")
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args()

    top_files = load_top_files(Path(args.top))
    from_counts = count_imports(Path(args.from_imports))
    simple_counts = count_imports(Path(args.simple_imports))

    cands = module_candidates(top_files, from_counts, simple_counts, limit=args.limit)
    out_rows = []
    for score, depth, ic, f in cands:
        # host new_path: replace "/" with "_" and drop leading "./" or starting slash
        new_name = f.lstrip("./").replace("/", "_")
        if new_name.endswith(".py"):
            new_name = new_name[:-3] + ".py"
        else:
            new_name = new_name + ".py"
        # place MATRIZ-prefixed modules for matrix nodes
        if "candidate/core/matrix/nodes" in f or "MATRIZ" in f:
            new_path = "MATRIZ/" + new_name
        else:
            new_path = new_name
        strat = decide_strategy(depth, ic)
        risk = risk_level(depth, ic)
        reason = f"depth={depth}; import_count={ic}; score={score}"
        out_rows.append({
            "old_path": f,
            "new_path": new_path,
            "move_strategy": strat,
            "reason": reason,
            "estimated_risk": risk,
            "restoration_commit": ""
        })

    # write CSV
    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    with outp.open("w", newline="", encoding="utf-8") as cf:
        writer = csv.DictWriter(cf, fieldnames=["old_path","new_path","move_strategy","reason","estimated_risk","restoration_commit"])
        writer.writeheader()
        for r in out_rows:
            writer.writerow(r)
    print(f"Wrote {outp} with {len(out_rows)} rows")

if __name__ == "__main__":
    main()
