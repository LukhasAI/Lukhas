#!/usr/bin/env python3
"""
Check status of Autonomous Guide patches and key guide files.

Run this from the repository root. It will:
- verify presence of canonical Autonomous Guide files and AGENTS/README
- search for expected markers (Agent Responsibility Matrix, Last updated)
- print git status summary and last commits for the checked files

Usage:
  python3 scripts/check_autonomous_guides_patch_status.py

This script only reports. It does not change files.
"""

import subprocess
from pathlib import Path

REPO_ROOT = Path(".").resolve()
FILES = [
    "AUTONOMOUS_GUIDE_CANDIDATE_CLEANUP.md",
    "AUTONOMOUS_GUIDE_MATRIZ_COMPLETION.md",
    "AUTONOMOUS_GUIDE_TODO_CLEANUP.md",
    "AUTONOMOUS_GUIDE_IMPORT_ORGANIZATION.md",
    "README_AUTONOMOUS_GUIDES.md",
    "AGENTS.md",
]
WORKFLOWS = [
    ".github/workflows/migration-dryrun.yml",
    ".github/workflows/todo-dryrun.yml",
]
EXPECTED_MARKERS = [
    "Agent Responsibility Matrix",
    "Last updated: 2025-10-28",
]


def run(cmd, cwd=REPO_ROOT):
    try:
        out = subprocess.check_output(cmd, cwd=cwd, shell=True, stderr=subprocess.STDOUT, text=True)
        return out.strip()
    except subprocess.CalledProcessError as e:
        return f"(error) {e.returncode}: {e.output.strip()}"


def check_file(path: Path):
    result = {
        "path": str(path),
        "exists": False,
        "size": 0,
        "markers": {},
        "head": None,
        "git_log": None,
    }
    if path.exists():
        result["exists"] = True
        content = path.read_text(encoding="utf-8", errors="ignore")
        result["size"] = len(content)
        lines = content.splitlines()
        result["head"] = "\n".join(lines[:20]) if lines else ""
        for m in EXPECTED_MARKERS:
            result["markers"][m] = m in content
        git_cmd = f"git log -n 3 --pretty=format:'%h %ad %an - %s' -- {path}"
        result["git_log"] = run(git_cmd)
    return result


def main():
    print("\n=== AUTONOMOUS GUIDES PATCH STATUS CHECK ===\n")
    print(f"Repo root: {REPO_ROOT}")

    # git status
    print("\n-- Git status summary (porcelain) --")
    gs = run("git status --porcelain")
    print(gs if gs else "(clean working tree)")

    all_ok = True
    print("\n-- Files check --")
    for f in FILES:
        p = REPO_ROOT / f
        r = check_file(p)
        print(f"\nFile: {r['path']}")
        print(f"  Exists: {r['exists']}, Size: {r['size']}")
        for m, v in r["markers"].items():
            print(f"  Marker '{m}': {'FOUND' if v else 'MISSING'}")
            if not v:
                all_ok = False
        if r["git_log"]:
            print("  Last commits:")
            print("\n".join("    " + line for line in r["git_log"].splitlines()))

    print("\n-- Workflows check --")
    for w in WORKFLOWS:
        p = REPO_ROOT / w
        exists = p.exists()
        print(f"  {w}: {'EXISTS' if exists else 'MISSING'}")
        if not exists:
            all_ok = False

    print("\n-- Additional quick scans --")
    grep_cmd = "rg --hidden --no-ignore -n 'Agent Responsibility Matrix' || true"
    grep_out = run(grep_cmd)
    print("\nFound Agent Responsibility Matrix occurrences:")
    print(grep_out if grep_out else "(none)")

    print("\nSummary:")
    if all_ok:
        print("  All expected files and markers appear present.")
    else:
        print("  Some files or markers are missing — inspect output above.")

    print(
        "\nIf anything looks missing, open the file or run `git log -p <file>` to inspect changes."
    )


if __name__ == "__main__":
    main()
