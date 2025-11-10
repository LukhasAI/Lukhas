"""
Fail PRs that exceed patch-size caps, touch protected files, or add risky exception patterns.
Intended for CI use. Exits nonzero on violation.

Env/Args:
  --base <sha>   Base commit (default: origin/main)
  --head <sha>   Head commit (default: HEAD)
  --protected .lukhas/protected-files.yml
  --max-files 2
  --max-lines 40
"""
from __future__ import annotations
import argparse, os, subprocess, sys, yaml, re, json
from pathlib import Path

RISKY_EXCEPT_RE = re.compile(r'^\+\s*except(\s+Exception)?\s*:', re.IGNORECASE)

def sh(cmd: str) -> str:
    out = subprocess.check_output(cmd, shell=True, text=True)
    return out.strip()

def list_changed_files(base: str, head: str) -> list[str]:
    return sh(f"git diff --name-only --diff-filter=ACMRT {base}...{head}").splitlines()

def diff_stats(base: str, head: str, paths: list[str]) -> int:
    if not paths: return 0
    out = sh(f"git diff --unified=0 {base}...{head} -- " + " ".join(paths))
    added = sum(1 for line in out.splitlines() if line.startswith("+") and not line.startswith("+++"))
    removed = sum(1 for line in out.splitlines() if line.startswith("-") and not line.startswith("---"))
    return added + removed

def risky_exception_added(base: str, head: str) -> bool:
    out = sh(f"git diff {base}...{head}")
    return any(RISKY_EXCEPT_RE.search(line) for line in out.splitlines())

def any_protected_touched(changed: list[str], protected_globs: list[str]) -> list[str]:
    from fnmatch import fnmatch
    hit = []
    for f in changed:
        for g in protected_globs:
            if fnmatch(f, g):
                hit.append(f)
    return sorted(set(hit))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=os.environ.get("BASE_SHA", "origin/main"))
    ap.add_argument("--head", default=os.environ.get("HEAD_SHA", "HEAD"))
    ap.add_argument("--protected", default=".lukhas/protected-files.yml")
    ap.add_argument("--max-files", type=int, default=2)
    ap.add_argument("--max-lines", type=int, default=40)
    args = ap.parse_args()

    changed = list_changed_files(args.base, args.head)
    nfiles = len(changed)
    lines = diff_stats(args.base, args.head, changed)

    protected = []
    pf = Path(args.protected)
    if pf.exists():
        protected = yaml.safe_load(pf.read_text()) or []

    touched = any_protected_touched(changed, protected)
    risky = risky_exception_added(args.base, args.head)

    result = {
        "base": args.base, "head": args.head,
        "changed_files": nfiles, "changed_lines": lines,
        "max_files": args.max_files, "max_lines": args.max_lines,
        "protected_hits": touched, "risky_exception_added": risky,
        "status": "ok"
    }

    violations = []
    if nfiles > args.max_files:
        violations.append(f"Changed files {nfiles} > max {args.max_files}")
    if lines > args.max_lines:
        violations.append(f"Changed lines {lines} > max {args.max_lines}")
    if touched:
        violations.append(f"Touched protected paths: {', '.join(touched)}")
    if risky:
        violations.append("Introduced broad 'except' clause (policy forbids).")

    if violations:
        result["status"] = "fail"
        print(json.dumps(result, indent=2))
        print("\nPolicy violations:\n- " + "\n- ".join(violations))
        sys.exit(1)

    print(json.dumps(result, indent=2))
    sys.exit(0)

if __name__ == "__main__":
    main()
