#!/usr/bin/env python3
"""
Create GitHub issues for TODOs from a CSV or inventory file.
Requires `gh` CLI auth or GITHUB_TOKEN env.

Usage:
  ./create_issues.py --input todo_inventory.csv --repo org/repo --dry-run
"""

import argparse
import csv
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional


def run_gh_issue_create(title: str, body: str, labels: str = "") -> int:
    """Create issue using gh CLI and return issue number. Raises on failure."""
    cmd = ["gh", "issue", "create", "--title", title, "--body", body]
    if labels:
        cmd += ["--label", labels]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"gh issue create failed: {res.stderr}")
    # gh prints the URL — parse issue number
    out = res.stdout.strip()
    # Try to parse last /number
    try:
        issue_number = int(out.rstrip("/").split("/")[-1])
    except Exception:
        # Fallback: print output and return -1
        print("Warning: couldn't parse issue number from gh output:", out)
        issue_number = -1
    return issue_number


def create_issue_rest(
    repo: str, token: str, title: str, body: str, labels: Optional[str] = None
) -> int:
    import requests  # type: ignore

    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    payload = {"title": title, "body": body}
    if labels:
        payload["labels"] = labels.split(",")
    r = requests.post(url, json=payload, headers=headers, timeout=30)
    r.raise_for_status()
    data = r.json()
    return data.get("number", -1)


def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--input",
        required=True,
        help="todo_inventory.csv (file,line,kind,priority,owner,scope,message)",
    )
    p.add_argument("--repo", required=True, help="owner/repo")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--out", default="todo_to_issue_map.json")
    args = p.parse_args()

    mapping = {}
    created = 0
    with open(args.input, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            # required fields: file,line,message,priority
            title = f"[TODO] {row.get('message', '').strip()[:80]}"
            body = (
                f"**Source:** `{row.get('file', '')}`:{row.get('line', '')}\n\n"
                f"**Priority:** {row.get('priority', '')}\n\n"
                f"**Original line:**\n```\n{row.get('message', '')}\n```\n\n"
                f"**Auto-migrated from inline TODO**\n\n"
                f"**Scope:** {row.get('scope', '')}\n"
            )
            labels = "todo-migration"
            print(f"Would create issue: {title}") if args.dry_run else print(
                f"Creating issue: {title}"
            )
            try:
                if args.dry_run:
                    issue_number = 0
                else:
                    # Try gh CLI first
                    try:
                        issue_number = run_gh_issue_create(title, body, labels)
                    except Exception:
                        token = os.environ.get("GITHUB_TOKEN")
                        if not token:
                            raise RuntimeError(
                                "No gh CLI and no GITHUB_TOKEN; cannot create issue."
                            )
                        issue_number = create_issue_rest(args.repo, token, title, body, labels)
                created += 1
                mapping_key = f"{row.get('file')}:{row.get('line')}"
                mapping[mapping_key] = {
                    "issue": issue_number,
                    "title": title,
                    "repo": args.repo,
                }
            except Exception as e:
                print(
                    "ERROR creating issue for",
                    row.get("file"),
                    row.get("line"),
                    ":",
                    e,
                    file=sys.stderr,
                )

    # write mapping
    Path("artifacts").mkdir(exist_ok=True)
    outpath = Path("artifacts") / args.out
    with open(outpath, "w", encoding="utf-8") as of:
        json.dump(mapping, of, indent=2)
    print(f"Wrote mapping to {outpath}. Created {created} issues (dry_run={args.dry_run}).")


if __name__ == "__main__":
    main()
