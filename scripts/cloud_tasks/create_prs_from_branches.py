#!/usr/bin/env python3
"""
Create PRs for Codex cloud branches automatically.

Discovers remote branches matching a pattern (default: codex/*) and creates
pull requests targeting the base branch (default: main) for any branch that
does not already have an open/closed PR.

Usage:
  python3 scripts/cloud_tasks/create_prs_from_branches.py \
    --pattern codex/ \
    --base main \
    --label codex-cloud --label ready-for-review \
    [--limit 72] [--dry-run]

Requires GitHub CLI (gh) and git.
"""
import argparse
import subprocess
import sys
from typing import List, Tuple


def sh(cmd: List[str], check=True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def list_remote_branches() -> List[str]:
    cp = sh(["git", "ls-remote", "--heads", "origin"])
    branches = []
    for line in cp.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) == 2 and parts[1].startswith("refs/heads/"):
            branches.append(parts[1].replace("refs/heads/", "", 1))
    return branches


def pr_exists(branch: str) -> Tuple[bool, str]:
    cp = sh(["gh", "pr", "list", "--state", "all", "--head", branch, "--json", "number,title,state,url"], check=False)
    if cp.returncode != 0:
        # treat as no PR found on API error
        return False, ""
    out = cp.stdout.strip()
    # A minimal check: gh prints [] for none
    if out and out != "[]":
        return True, out
    return False, ""


def create_pr(branch: str, base: str, labels: List[str], dry_run: bool) -> bool:
    title = f"codex: {branch}"
    body = (
        f"Automated PR for Codex Cloud Task branch `{branch}`.\n\n"
        f"- Base: `{base}`\n"
        f"- Source: `{branch}`\n\n"
        f"This PR was created by scripts/cloud_tasks/create_prs_from_branches.py.\n"
        f"Please review and merge according to T4 standards."
    )
    args = [
        "gh", "pr", "create",
        "--base", base,
        "--head", branch,
        "--title", title,
        "--body", body,
    ]
    if labels:
        args += ["--label", ",".join(labels)]
    if dry_run:
        print("[DRY-RUN] gh pr create", " ".join(args[2:]))
        return True
    cp = sh(args, check=False)
    if cp.returncode != 0:
        sys.stderr.write(f"Failed to create PR for {branch}: {cp.stderr}\n")
        return False
    print(cp.stdout.strip())
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pattern", action="append", default=["codex/"], help="Branch name prefix to include (repeatable)")
    ap.add_argument("--base", default="main", help="Base branch for PRs")
    ap.add_argument("--label", action="append", default=["codex-cloud", "ready-for-review"], help="Label(s) to apply")
    ap.add_argument("--limit", type=int, default=0, help="Max number of PRs to create (0 = no limit)")
    ap.add_argument("--dry-run", action="store_true", help="Preview actions without creating PRs")
    args = ap.parse_args()

    branches = list_remote_branches()
    candidates = [b for b in branches if any(b.startswith(p) for p in args.pattern)]
    print(f"Found {len(candidates)} candidate branches matching patterns {args.pattern}")

    created = 0
    skipped = 0
    already = 0
    for b in candidates:
        exists, _ = pr_exists(b)
        if exists:
            already += 1
            print(f"[SKIP] PR already exists for {b}")
            continue
        ok = create_pr(b, args.base, args.label, args.dry_run)
        if ok:
            created += 1
        else:
            skipped += 1
        if args.limit and created >= args.limit:
            break

    print(f"Created: {created}, Already had PR: {already}, Failed: {skipped}")
    return 0 if skipped == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

