# Guardian Code Consolidation Toolkit

This package provides a set of tools to help safely consolidate and refactor guardian-related code in your repository, following T4's best practices for safety, auditability, and maintainability.
It includes:

* a **robust discovery script** (`scripts/guardian_discovery.py`) which:

  * finds *exact* and *near* duplicate functions/methods across the repo,
  * builds an import/dependency graph,
  * checks `guardian/` artifacts against `core/module_registry.py`,
  * emits a JSON + human-readable report for triage,
* a **simple PYTHONPATH quick-fix helper** (`scripts/fix_pythonpath.sh`) that helps create a reproducible PYTHONPATH for local dev,
* a **PR template** (`.github/PULL_REQUEST_TEMPLATE.md`) with the T4 guardrails (snapshot, tests, registry, docs),
* a **short brief for Copilot** so it knows the rules when doing the heavy lifting.

Everything is ready to copy into your repo. Run the discovery first, review the report, then use the PR template for safe merges. I also add run instructions and recommended thresholds.

---

# 1) `scripts/guardian_discovery.py`

Save this file as `scripts/guardian_discovery.py`.

```python
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
import textwrap
from collections import defaultdict
from difflib import SequenceMatcher
from typing import Dict, List, Tuple, Optional

REPORT_DIR_DEFAULT = "reports"


def find_py_files(root: str, exclude_dirs=None):
    exclude_dirs = set(exclude_dirs or [".git", "__pycache__", "venv", "env", "node_modules"])
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
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def normalize_code(source: str) -> str:
    """
    Minimal normalization:
     - remove leading/trailing whitespace
     - collapse consecutive whitespace into single spaces
     - remove comment-only lines
     - remove leading docstring if present (heuristic)
    """
    # Remove leading docstring (first triple-quoted string)
    src = source
    # heuristic removal of initial module/function/class docstring
    docstring_pattern = r'^\s*(?:[rubfRUBF]{0,2})?("""|\'\'\')(.+?)\1'
    src = re.sub(docstring_pattern, "", src, flags=re.DOTALL)

    # Remove comments and collapse whitespace
    lines = []
    for line in src.splitlines():
        # remove comment-only lines and trailing inline comments
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        # remove inline comments after code (risky but acceptable for normalization)
        # only remove when '#' is not inside quotes
        qcount = line.count('"') + line.count("'")
        if "#" in line and qcount % 2 == 0:
            line = line.split("#", 1)[0]
        lines.append(line.rstrip())

    joined = "\n".join(lines)
    # collapse whitespace
    collapsed = re.sub(r"\s+", " ", joined).strip()
    return collapsed


def node_to_signature(node: ast.AST) -> str:
    """
    Attempt to produce a stable signature for function/method nodes.
    """
    if isinstance(node, ast.FunctionDef):
        name = node.name
        args = []
        for a in node.args.args:
            args.append(a.arg)
        # ignore defaults/annotations for signature stability
        return f"{name}({','.join(args)})"
    return repr(node)


def extract_functions_from_ast(tree: ast.AST, source_text: str, file_path: str):
    """
    Walk AST, extract functions and methods with relevant metadata.
    Returns list of dicts with keys: name, qualname, signature, code, normalized, lineno, end_lineno, kind
    """
    funcs = []

    class FnVisitor(ast.NodeVisitor):
        def __init__(self):
            self.class_stack = []

        def visit_ClassDef(self, node: ast.ClassDef):
            self.class_stack.append(node.name)
            self.generic_visit(node)
            self.class_stack.pop()

        def visit_FunctionDef(self, node: ast.FunctionDef):
            # get qualified name
            qual = ".".join(self.class_stack + [node.name]) if self.class_stack else node.name
            try:
                src_seg = ast.get_source_segment(source_text, node) or ""
            except Exception:
                # fallback
                src_seg = ""
            normalized = normalize_code(src_seg or ast.unparse(node) if hasattr(ast, "unparse") else src_seg)
            sig = node_to_signature(node)
            kind = "method" if self.class_stack else "function"
            funcs.append(
                {
                    "name": node.name,
                    "qualname": qual,
                    "signature": sig,
                    "code": src_seg,
                    "normalized": normalized,
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


def file_ast_safe(path: str) -> Optional[ast.AST]:
    try:
        text = read_file(path)
        return ast.parse(text), text
    except SyntaxError:
        print(f"[WARN] SyntaxError parsing {path}, skipping")
        return None


def compute_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_import_graph(tree: ast.AST, current_module: str):
    """
    Return set of modules imported by current_module.
    """
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


def parse_module_registry(registry_path: str) -> Dict[str, int]:
    """
    Try to parse core/module_registry.py and extract MODULE_TIER_REQUIREMENTS dict keys.
    Returns mapping or empty dict on failure.
    """
    try:
        text = read_file(registry_path)
        tree = ast.parse(text)
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if getattr(target, "id", "") == "MODULE_TIER_REQUIREMENTS":
                        value = node.value
                        try:
                            # literal_eval should work for a dict literal
                            mapping = ast.literal_eval(value)
                            if isinstance(mapping, dict):
                                return mapping
                        except Exception:
                            # fallback: attempt regex extract of keys
                            raw = ast.get_source_segment(text, value)
                            keys = re.findall(r"['\"]([a-zA-Z0-9_]+)['\"]\s*:", raw or "")
                            return {k: None for k in keys}
    except Exception as e:
        print(f"[WARN] Failed to parse registry: {e}")
    return {}


def find_guardian_modules(py_files: List[str], repo_root: str):
    guardian_files = [p for p in py_files if os.path.normpath(p).split(os.sep)[0] == "guardian" or "/guardian/" in p or "\\guardian\\" in p]
    # also pick up labs/governance/guardian
    guardian_files += [p for p in py_files if "labs/governance/guardian" in p or "labs\\governance\\guardian" in p]
    # dedupe
    guardian_files = sorted(set(guardian_files))
    return guardian_files


def run_discovery(repo_root: str, output_path: str, similarity_threshold: float):
    py_files = find_py_files(repo_root)
    print(f"[i] Found {len(py_files)} python files.")
    all_funcs = []
    import_graph = {}
    for f in py_files:
        parsed = file_ast_safe(f)
        if not parsed:
            continue
        tree, text = parsed
        funcs = extract_functions_from_ast(tree, text, os.path.relpath(f, repo_root))
        if funcs:
            all_funcs.extend(funcs)
        # import graph keyed by module path relative to repo_root
        module_key = os.path.relpath(f, repo_root)
        import_graph[module_key] = build_import_graph(tree, module_key)

    # group by hash for exact duplicates
    hash_map = defaultdict(list)
    for fn in all_funcs:
        h = compute_hash(fn["normalized"])
        hash_map[h].append(fn)

    exact_duplicates = {h: items for h, items in hash_map.items() if len(items) > 1}

    # find near-duplicates (pairwise within top-level)
    near_duplicates = []
    normalized_texts = [(i, fn["normalized"]) for i, fn in enumerate(all_funcs)]
    n = len(normalized_texts)
    for i in range(n):
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

    # module registry check
    registry_path = os.path.join(repo_root, "lukhas", "core", "module_registry.py")
    registry = parse_module_registry(registry_path) if os.path.exists(registry_path) else {}
    registry_keys = set(registry.keys())
    guardian_files = find_guardian_modules(py_files, repo_root)
    guardian_modules = set()
    for f in guardian_files:
        # convert path to candidate module key (folder name)
        # e.g., guardian/core.py -> guardian
        parts = os.path.relpath(f, repo_root).split(os.sep)
        if parts:
            guardian_modules.add(parts[0])

    not_registered = []
    for gm in sorted(guardian_modules):
        if gm not in registry_keys:
            not_registered.append(gm)

    # produce report structure
    report = {
        "summary": {
            "py_files": len(py_files),
            "functions_found": len(all_funcs),
            "exact_duplicate_groups": len(exact_duplicates),
            "near_duplicate_pairs": len(near_duplicates),
            "guardian_files": len(guardian_files),
            "guardian_modules_detected": list(sorted(guardian_modules)),
            "guardian_not_registered_in_module_registry": not_registered,
        },
        "exact_duplicates": [],
        "near_duplicates": near_duplicates,
        "import_graph": import_graph,
        "registry_keys": list(sorted(registry_keys)),
    }

    for h, items in exact_duplicates.items():
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
                ],
            }
        )

    # write JSON
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # human readable
    hr = []
    hr.append("Guardian Discovery Report")
    hr.append("=" * 60)
    hr.append(json.dumps(report["summary"], indent=2))
    hr.append("")
    hr.append("Top exact duplicate groups (hash, count, examples):")
    for g in report["exact_duplicates"][:10]:
        lines = f"- {g['hash']} ({g['count']})"
        hr.append(lines)
        for ex in g["examples"]:
            hr.append(f"    - {ex['qualname']} @ {ex['file']}:{ex['lineno']}")
    hr.append("")
    hr.append(f"Near-duplicate pairs (threshold {similarity_threshold}): {len(near_duplicates)}")
    for pair in near_duplicates[:10]:
        hr.append(f"- score {pair['score']}: {pair['left']['qualname']} @ {pair['left']['file']}:{pair['left']['lineno']}  <-> {pair['right']['qualname']} @ {pair['right']['file']}:{pair['right']['lineno']}")
    hr.append("")
    hr.append("Guardian modules detected: " + ", ".join(report["summary"]["guardian_modules_detected"]))
    hr.append("Guardian modules not in module_registry.py: " + ", ".join(not_registered))
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
    ap.add_argument("--output", default=os.path.join(REPORT_DIR_DEFAULT, "guardian_discovery.json"), help="Output JSON path")
    ap.add_argument("--similarity", default=0.85, type=float, help="Threshold for near-duplicates (0..1)")
    args = ap.parse_args()

    report = run_discovery(args.repo_root, args.output, args.similarity)
    # print brief summary
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
```

**How to run**

```bash
# from repo root
python3 scripts/guardian_discovery.py --repo-root . --output reports/guardian_discovery.json --similarity 0.85
less reports/guardian_discovery.txt
```

**What it produces**

* `reports/guardian_discovery.json` — machine readable report
* `reports/guardian_discovery.txt` — human readable triage summary

Tweak `--similarity` between `0.7` and `0.9` to expand/contract matches.

---

# 2) `scripts/fix_pythonpath.sh`

A gentle, transparent helper that finds top-level package directories (those with `__init__.py`) and prints an export line you can paste into your dev shell or `.env`.

Save as `scripts/fix_pythonpath.sh` and `chmod +x` it.

```bash
#!/usr/bin/env bash
# fix_pythonpath.sh
# Suggests PYTHONPATH additions for local development.

REPO_ROOT="${1:-.}"
echo "Scanning for Python packages under ${REPO_ROOT} ..."
PKGS=()
while IFS= read -r -d '' dir; do
  # ensure it's under REPO_ROOT
  rel=$(realpath --relative-to="$REPO_ROOT" "$dir") 2>/dev/null || rel="$dir"
  PKGS+=("$rel")
done < <(find "$REPO_ROOT" -type f -name "__init__.py" -print0 | xargs -0 -n1 dirname | sort -u -z)

if [ ${#PKGS[@]} -eq 0 ]; then
  echo "No packages with __init__.py found under ${REPO_ROOT}."
  echo "You might want to add the repo root itself to PYTHONPATH:"
  echo "export PYTHONPATH=\"\$(pwd):\$PYTHONPATH\""
  exit 0
fi

# Collect unique top-level package directories (take first path component)
TOPS=()
for p in "${PKGS[@]}"; do
  top=$(echo "$p" | awk -F/ '{print $1}')
  TOPS+=("$top")
done
TOPS_UNIQ=($(printf "%s\n" "${TOPS[@]}" | sort -u))

echo ""
echo "Suggested PYTHONPATH entries (paste into shell or .env):"
for t in "${TOPS_UNIQ[@]}"; do
  echo "export PYTHONPATH=\"\$(pwd)/$t:\$PYTHONPATH\""
done

echo ""
echo "If you prefer to add the repository root:"
echo "export PYTHONPATH=\"\$(pwd):\$PYTHONPATH\""
```

**Note:** This script is conservative — it suggests adding package roots instead of mutating project files.

---

# 3) `.github/PULL_REQUEST_TEMPLATE.md`

Drop this under `.github/` so PRs follow the guardrails.

```markdown
## What/Why
Describe the change in one sentence. Why is this change necessary?

## Checklist (T4 guardrails)
- [ ] **Snapshot**: I ran `./guardian/flag_snapshot.sh` and recorded the snapshot for the PR (attach file or ledger id).
- [ ] **Tests**: Unit/integration tests added/updated. All tests pass locally: `pytest -q`.
- [ ] **Module Registry**: Any new/modified module is registered in `lukhas/core/module_registry.py` or a migration plan is included.
- [ ] **Observability**: Metrics remain intact (esp. `lukhas_guardian_decision_total`); Grafana dashboard impacts documented.
- [ ] **Doc**: Relevant docs updated (README, docs/guardian-enhancements.md).
- [ ] **Zero-regression**: No behaviour regressions introduced (explain test coverage).
- [ ] **Canary**: If the change is risky, provide a canary plan and rollback steps.
- [ ] **Audit**: If the change touches governance/flags, ensure dual approval was captured.

## Implementation notes
Add short implementation notes and reasoning. Link to discovery report if relevant.

## Testing instructions
How to run test locally and any manual checks.

## Snapshot metadata
Attach or paste the `flag_snapshot.sh` output or ledger transaction id here:
```

---

# 4) Short briefing for Copilot

Copy/paste this prompt at the head of any Copilot/agent task that will merge or rewrite guardian code:

```
T4 BRIEF (for Copilot):
- We are consolidating guardian code with strict safety and audit guardrails.
- First step: run `scripts/guardian_discovery.py` to produce a report of exact and near-duplicate functions and unmatched guardian modules.
- Do NOT rewrite or merge code until someone reviews the discovery report.
- Quick-win allowed: small PRs that only fix PYTHONPATH/imports and pass `pytest guardian/tests -q`.
- Any functional consolidation must:
  - register modules in `lukhas/core/module_registry.py`
  - include unit tests that cover behavior preserved by the consolidation
  - produce an audit snapshot via `./guardian/flag_snapshot.sh` and attach ledger id
  - update `guardian/docs/` and `docs/guardian-enhancements.md` as needed
- Use forwarding shims for old public APIs; deprecate, don't break.
- Provide a canary/rollback plan for each nontrivial change.
```

---

# 5) Suggested immediate workflow (concrete)

1. Commit scripts above into `scripts/` and `.github/PULL_REQUEST_TEMPLATE.md`.
2. Run:

   ```bash
   python3 scripts/guardian_discovery.py --repo-root . --output reports/guardian_discovery.json --similarity 0.85
   less reports/guardian_discovery.txt
   ```
3. Triage report: mark functions to merge vs. keep. Prioritize exact duplicates and high similarity pairs near critical paths (`guardian/pdp`, `guardian/metrics`, `lukhas/core/reliability`).
4. Create **small** PR that:

   * runs snapshot (`./guardian/flag_snapshot.sh`) and records ledger,
   * fixes PYTHONPATH / imports only,
   * passes `pytest guardian/tests -q`.
5. After that PR merges, prepare grouped refactors with clear PRs per module: `merge`, `extract` (shared utilities), or `forwarding`.

---

# Final notes / why this is T4-aligned

* The discovery script gives *evidence*, not opinions. You get exact duplicates and a ranked list of near-duplicates so decisions are data-driven.
* The PR template enforces tests, registry updates, and audit snapshots (zero-regression guardrails).
* The PYTHONPATH helper is intentionally non-destructive and helps the “quick win” without dangerous code changes.

---
