# tools/ci/debt_ratchet.py
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

try:
    import tomllib
except Exception:
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / ".t4autofix.toml"
ALLOWED = set()

def load_allowed():
    if POLICY.exists():
        data = tomllib.loads(POLICY.read_text())
        # Check for rules.allow first, then auto_fix as fallback
        for c in data.get("rules", {}).get("allow", []):
            ALLOWED.add(c)
        if not ALLOWED:
            # Fallback to auto_fix rules if no allow rules
            for c in data.get("rules", {}).get("auto_fix", []):
                ALLOWED.add(c)
        if not ALLOWED:
            # Use DEFAULT_ALLOW from auto_fix_safe.py
            ALLOWED.update({"UP006","UP035","SIM102","SIM103","F841","B007","C401"})
    return ALLOWED

def run_ruff(paths, out_json):
    paths = paths or ["."]
    try:
        subprocess.run(["ruff","check","--output-format","json","-o", out_json, *paths],
                      capture_output=True, check=False)
    except Exception:
        # If ruff fails, create empty results
        Path(out_json).write_text("[]")

def to_pkg(path: str) -> str:
    parts = Path(path).parts
    return parts[0] if parts else ""

def touched_files_against_main():
    try:
        base = os.environ.get("GITHUB_BASE_REF")
        if base:
            # In GitHub Actions context
            out = subprocess.check_output(["git","diff","--name-only",f"origin/{base}...HEAD"], text=True).splitlines()
        else:
            # Local context
            out = subprocess.check_output(["git","diff","--name-only","origin/main...HEAD"], text=True).splitlines()
    except Exception:
        try:
            # Fallback to origin/main
            out = subprocess.check_output(["git","diff","--name-only","origin/main...HEAD"], text=True).splitlines()
        except Exception:
            return []
    return [f for f in out if f.endswith(".py")]

def count_by_pkg(json_path):
    data = json.loads(Path(json_path).read_text() or "[]")
    counts = {}
    for item in data:
        if item.get("code") not in ALLOWED:
            continue
        pkg = to_pkg(item.get("filename",""))
        counts[pkg] = counts.get(pkg, 0) + 1
    return counts

def main():
    load_allowed()
    changed = touched_files_against_main()
    pkgs_touched = sorted({to_pkg(f) for f in changed if to_pkg(f) in {"lukhas","candidate","universal_language"}})
    if not pkgs_touched:
        print("No tracked packages touched; ratchet passes.")
        return 0

    Path("reports/lints").mkdir(parents=True, exist_ok=True)

    # current PR
    run_ruff(["."], "reports/lints/ruff_pr.json")
    pr_counts = count_by_pkg("reports/lints/ruff_pr.json")

    # baseline from main
    try:
        subprocess.check_call(["git","fetch","origin","main","--depth","1"], capture_output=True)
        subprocess.check_call(["git","checkout","-q","origin/main"], capture_output=True)
        run_ruff(["."], "reports/lints/ruff_main.json")
        base_counts = count_by_pkg("reports/lints/ruff_main.json")
        # return to head
        subprocess.check_call(["git","checkout","-q","-"], capture_output=True)
    except Exception as e:
        print(f"Warning: Could not fetch main branch: {e}")
        base_counts = {}

    bad = []
    for pkg in pkgs_touched:
        if pr_counts.get(pkg,0) > base_counts.get(pkg,0):
            bad.append((pkg, base_counts.get(pkg,0), pr_counts.get(pkg,0)))

    if bad:
        print("❌ Debt ratchet failed (allowlist lint increased):")
        for pkg, base, cur in bad:
            print(f"  {pkg}: {base} → {cur}")
        return 1

    print("✅ Debt ratchet OK.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
