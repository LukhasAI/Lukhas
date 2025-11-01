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
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

ALLOWED_PRIORITIES = {"LOW", "MED", "MEDIUM", "HIGH"}
ALLOWED_SCOPES = {"PROD", "CANDIDATE", "DOCS"}


def normalize_priority(value: str) -> str:
    """Return a normalized priority label."""

    if not value:
        return "MED"
    normalized = value.strip().upper()
    if normalized == "MEDIUM":
        normalized = "MED"
    return normalized


def remove_control_characters(text: str, allow_newlines: bool = True) -> str:
    """Strip ASCII control characters from text while optionally allowing newlines."""

    if not text:
        return ""
    allowed_controls = {"\n", "\t"} if allow_newlines else set()
    return "".join(
        ch
        for ch in text
        if ch in allowed_controls or ord(ch) >= 32
    )


def collapse_whitespace(text: str) -> str:
    """Collapse consecutive whitespace characters into a single space."""

    return " ".join(text.split())


def validate_repo(repo: str) -> None:
    """Ensure the repository argument uses the expected owner/repo format."""

    if not repo:
        raise ValueError("Repository cannot be empty")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise ValueError(
            "Repository must be in the format 'owner/repo' using alphanumeric, '_', '-', or '.' characters"
        )


def validate_row(row: Dict[str, str]) -> Dict[str, str]:
    """Validate and sanitize a TODO inventory row."""

    file_path = (row.get("file") or "").strip()
    if not file_path:
        raise ValueError("missing file path")

    raw_line = (row.get("line") or "").strip()
    if not raw_line:
        raise ValueError("missing line number")
    if not raw_line.isdigit():
        raise ValueError("line number must be an integer")
    line_number = str(int(raw_line))

    scope = (row.get("scope") or "").strip().upper()
    if scope and scope not in ALLOWED_SCOPES:
        raise ValueError(f"invalid scope '{scope}'")

    priority = normalize_priority(row.get("priority", ""))
    if priority and priority not in ALLOWED_PRIORITIES:
        raise ValueError(f"invalid priority '{priority}'")

    message_raw = row.get("message", "")
    message_clean = remove_control_characters(message_raw, allow_newlines=True).strip()
    if not message_clean:
        raise ValueError("missing TODO message")

    title_fragment = collapse_whitespace(
        remove_control_characters(message_raw, allow_newlines=True)
    )
    if not title_fragment:
        # Fallback to cleaned message if collapsing removed everything
        title_fragment = collapse_whitespace(message_clean)

    return {
        "file": file_path,
        "line": line_number,
        "scope": scope,
        "priority": priority or "MED",
        "message": message_clean,
        "title_fragment": title_fragment,
    }


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

    try:
        validate_repo(args.repo)
    except ValueError as repo_error:
        print(f"Validation error: {repo_error}", file=sys.stderr)
        raise SystemExit(1) from repo_error

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Validation error: input file '{input_path}' does not exist", file=sys.stderr)
        raise SystemExit(1)

    validated_rows: List[Dict[str, str]] = []
    validation_errors: List[str] = []

    with input_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for idx, row in enumerate(reader, start=2):
            try:
                validated_rows.append(validate_row(row))
            except ValueError as exc:
                validation_errors.append(
                    f"Row {idx}: {exc}"
                )

    if validation_errors:
        for err in validation_errors:
            print(f"Validation error: {err}", file=sys.stderr)
        raise SystemExit(1)

    mapping: Dict[str, Dict[str, object]] = {}
    created = 0
    labels = "todo-migration"

    for entry in validated_rows:
        title = f"[TODO] {entry['title_fragment'][:80]}"
        body = (
            f"**Source:** `{entry['file']}`:{entry['line']}\n\n"
            f"**Priority:** {entry['priority']}\n\n"
            f"**Original line:**\n```\n{entry['message']}\n```\n\n"
            f"**Auto-migrated from inline TODO**\n\n"
            f"**Scope:** {entry['scope']}\n"
        )

        print(f"Would create issue: {title}" if args.dry_run else f"Creating issue: {title}")

        try:
            if args.dry_run:
                issue_number = 0
            else:
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
            mapping_key = f"{entry['file']}:{entry['line']}"
            mapping[mapping_key] = {
                "issue": issue_number,
                "title": title,
                "repo": args.repo,
            }
        except Exception as e:  # pragma: no cover - network failures are hard to simulate in unit tests
            print(
                "ERROR creating issue for",
                entry["file"],
                entry["line"],
                ":",
                e,
                file=sys.stderr,
            )

    Path("artifacts").mkdir(exist_ok=True)
    outpath = Path("artifacts") / args.out
    with open(outpath, "w", encoding="utf-8") as of:
        json.dump(mapping, of, indent=2)
    print(f"Wrote mapping to {outpath}. Created {created} issues (dry_run={args.dry_run}).")


if __name__ == "__main__":
    main()
