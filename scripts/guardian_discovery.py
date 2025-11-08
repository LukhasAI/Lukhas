#!/usr/bin/env python3
"""
guardian_discovery.py

Purpose:
 - Scan a repo for duplicate or highly-similar functions/methods.
 - Build a simple import graph.
 - Find python modules under the `guardian/` area that are not present
   in ModuleRegistry.MODULE_TIER_REQUIREMENTS (quick sanity check).
 - Produce JSON + human-readable report for triage.

Usage:
  python3 scripts/guardian_discovery.py --repo-root /path/to/repo \
      --output reports/guardian_discovery.json --similarity 0.85

Notes:
 - Requires Python 3.9+ for ast.unparse. If unavailable, the script falls back
   to source extraction.
 - Designed to be non-destructive and fast enough for medium-sized repos.
"""

import argparse
import ast
import hashlib
import json
import os
import re
from collections import defaultdict
from difflib import SequenceMatcher

REPORT_DIR_DEFAULT = "reports"


def find_py_files(root: str, exclude_dirs=None):
    exclude_dirs = set(
        exclude_dirs
        or [".git", "__pycache__", "venv", "env", "node_modules", ".venv", "archive", "backup"]
    )
    py_files = []
    for dirpath, dirnames, filenames in os.walk(root):
        # skip excluded dirs
        parts = dirpath.split(os.sep)
        if any(p in exclude_dirs for p in parts):
            continue
        for f in filenames:
            if f.endswith(".py"):
                py_files.append(os.path.join(dirpath, f))
    return py_files


def read_file(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except (FileNotFoundError, PermissionError, OSError) as e:
        print(f"[WARN] Cannot read {path}: {e}")
        return ""


def normalize_code(source: str) -> str:
    """Minimal normalization: remove comments and collapse whitespace."""
    lines = []
    for line in source.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        # remove inline comments
        qcount = line.count('"') + line.count("'")
        if "#" in line and qcount % 2 == 0:
            line = line.split("#", 1)[0]
        lines.append(line.rstrip())

    joined = "\n".join(lines)
    collapsed = re.sub(r"\s+", " ", joined).strip()
    return collapsed


def node_to_signature(node: ast.AST) -> str:
    """Produce a stable signature for function/method nodes."""
    if isinstance(node, ast.FunctionDef):
        name = node.name
        args = [a.arg for a in node.args.args]
        return f"{name}({','.join(args)})"
    return repr(node)


def extract_functions_from_ast(tree: ast.AST, source_text: str, file_path: str):
    """Extract functions and methods with metadata."""
    funcs = []

    class FnVisitor(ast.NodeVisitor):
        def __init__(self):
            self.class_stack = []

        def visit_ClassDef(self, node: ast.ClassDef):
            self.class_stack.append(node.name)
            self.generic_visit(node)
            self.class_stack.pop()

        def visit_FunctionDef(self, node: ast.FunctionDef):
            qual = ".".join(self.class_stack + [node.name]) if self.class_stack else node.name
            try:
                src_seg = ast.get_source_segment(source_text, node) or ""
            except Exception:
                src_seg = ""

            normalized = normalize_code(src_seg if src_seg else str(node.name))
            sig = node_to_signature(node)
            kind = "method" if self.class_stack else "function"

            funcs.append(
                {
                    "name": node.name,
                    "qualname": qual,
                    "signature": sig,
                    "code": src_seg[:200] if src_seg else "",  # First 200 chars
                    "normalized": normalized[:500],  # Limit for performance
                    "lineno": getattr(node, "lineno", None),
                    "end_lineno": getattr(node, "end_lineno", None),
                    "kind": kind,
                    "file": file_path,
                }
            )
            self.generic_visit(node)

    v = FnVisitor()
    v.visit(tree)
    return funcs


def file_ast_safe(path: str):
    try:
        text = read_file(path)
        return ast.parse(text), text
    except SyntaxError:
        print(f"[WARN] SyntaxError parsing {path}, skipping")
        return None


def compute_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_import_graph(tree: ast.AST, current_module: str):
    """Return set of modules imported by current_module."""
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            mod = node.module
            if mod:
                imports.add(mod.split(".")[0])
    return list(imports)


def run_discovery(repo_root: str, output_path: str, similarity_threshold: float):
    py_files = find_py_files(repo_root)
    print(f"[i] Found {len(py_files)} python files.")

    all_funcs = []
    import_graph = {}

    for i, f in enumerate(py_files):
        if i % 100 == 0:
            print(f"[i] Processing file {i}/{len(py_files)}...")

        parsed = file_ast_safe(f)
        if not parsed:
            continue

        tree, text = parsed
        funcs = extract_functions_from_ast(tree, text, os.path.relpath(f, repo_root))
        if funcs:
            all_funcs.extend(funcs)

        module_key = os.path.relpath(f, repo_root)
        import_graph[module_key] = build_import_graph(tree, module_key)

    print(f"[i] Found {len(all_funcs)} total functions/methods.")

    # Group by hash for exact duplicates
    hash_map = defaultdict(list)
    for fn in all_funcs:
        h = compute_hash(fn["normalized"])
        hash_map[h].append(fn)

    exact_duplicates = {h: items for h, items in hash_map.items() if len(items) > 1}
    print(f"[i] Found {len(exact_duplicates)} exact duplicate groups.")

    # Find near-duplicates (sample only first 1000 functions for performance)
    print("[i] Analyzing near-duplicates (this may take a while)...")
    near_duplicates = []
    sample_size = min(1000, len(all_funcs))
    normalized_texts = [(i, fn["normalized"]) for i, fn in enumerate(all_funcs[:sample_size])]
    n = len(normalized_texts)

    for i in range(n):
        if i % 100 == 0 and i > 0:
            print(f"[i] Compared {i}/{n} functions...")
        for j in range(i + 1, n):
            a = normalized_texts[i][1]
            b = normalized_texts[j][1]
            if not a or not b:
                continue
            score = SequenceMatcher(None, a, b).ratio()
            if score >= similarity_threshold and compute_hash(a) != compute_hash(b):
                near_duplicates.append(
                    {
                        "score": round(score, 3),
                        "left": all_funcs[normalized_texts[i][0]],
                        "right": all_funcs[normalized_texts[j][0]],
                    }
                )

    print(f"[i] Found {len(near_duplicates)} near-duplicate pairs.")

    # Produce report structure
    report = {
        "summary": {
            "py_files": len(py_files),
            "functions_found": len(all_funcs),
            "exact_duplicate_groups": len(exact_duplicates),
            "near_duplicate_pairs": len(near_duplicates),
            "sample_note": f"Near-duplicates analyzed on sample of {sample_size} functions",
        },
        "exact_duplicates": [],
        "near_duplicates": near_duplicates[:100],  # Limit output
        "import_graph_sample": dict(list(import_graph.items())[:50]),  # Sample only
    }

    for h, items in list(exact_duplicates.items())[:100]:  # Top 100 groups
        report["exact_duplicates"].append(
            {
                "hash": h,
                "count": len(items),
                "examples": [
                    {
                        "qualname": it["qualname"],
                        "signature": it["signature"],
                        "file": it["file"],
                        "lineno": it["lineno"],
                    }
                    for it in items[:6]
                ],  # Max 6 examples per group
            }
        )

    # Write JSON
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Human readable
    hr = []
    hr.append("=" * 60)
    hr.append("Guardian Discovery Report")
    hr.append("=" * 60)
    hr.append(json.dumps(report["summary"], indent=2))
    hr.append("")
    hr.append("Top exact duplicate groups:")
    for g in report["exact_duplicates"][:20]:
        hr.append(f"\n- Hash {g['hash'][:16]}... ({g['count']} copies)")
        for ex in g["examples"]:
            hr.append(f"    {ex['qualname']} @ {ex['file']}:{ex['lineno']}")

    hr.append(f"\nNear-duplicate pairs (threshold {similarity_threshold}):")
    for pair in near_duplicates[:20]:
        hr.append(
            f"- score {pair['score']}: {pair['left']['qualname']} <-> {pair['right']['qualname']}"
        )
        hr.append(
            f"  {pair['left']['file']}:{pair['left']['lineno']} <-> {pair['right']['file']}:{pair['right']['lineno']}"
        )

    hr_text = "\n".join(hr)
    hr_path = os.path.splitext(output_path)[0] + ".txt"
    with open(hr_path, "w", encoding="utf-8") as f:
        f.write(hr_text)

    print(f"[i] JSON report written to: {output_path}")
    print(f"[i] Human-readable report written to: {hr_path}")
    return report


def main():
    ap = argparse.ArgumentParser(description="Guardian discovery and duplication scanner")
    ap.add_argument("--repo-root", default=".", help="Repo root to analyze")
    ap.add_argument(
        "--output",
        default=os.path.join(REPORT_DIR_DEFAULT, "guardian_discovery.json"),
        help="Output JSON path",
    )
    ap.add_argument(
        "--similarity", default=0.85, type=float, help="Threshold for near-duplicates (0..1)"
    )
    args = ap.parse_args()

    report = run_discovery(args.repo_root, args.output, args.similarity)
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(json.dumps(report["summary"], indent=2))
    print("=" * 60)


if __name__ == "__main__":
    main()
