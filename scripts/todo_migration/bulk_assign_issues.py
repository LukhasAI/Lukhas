#!/usr/bin/env python3
"""
Bulk-assign TODO-migrated issues and post kickoff comments.

Usage:
  python3 scripts/todo_migration/bulk_assign_issues.py \
    --map artifacts/todo_to_issue_map.json [--repo LukhasAI/Lukhas] [--dry-run]
    [--assignees-json path/to/assignees.json] [--sleep 0.2]

Notes:
  - If no assignee mapping is provided, the script will skip assignment and only
    post kickoff comments (unless --dry-run).
  - Writes results to artifacts/assignment_log.json
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List


def load_json(p: str) -> Any:
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def area_for_path(path: str) -> str:
    p = path.lower()
    if ".semgrep" in p or "/security" in p:
        return "security"
    if "/lukhas_website" in p or "/identity" in p or "webauthn" in p or "oidc" in p:
        return "identity"
    if "/labs/" in p:
        return "labs"
    if "/qi/" in p or "quantum" in p:
        return "qi"
    if "/docs/" in p:
        return "docs"
    return "misc"


def ensure_artifacts_dir() -> Path:
    outdir = Path("artifacts")
    outdir.mkdir(parents=True, exist_ok=True)
    return outdir


def run_cmd(cmd: List[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--map", required=True, help="Path to todo->issue mapping json")
    ap.add_argument("--repo", default="LukhasAI/Lukhas", help="GitHub repo (owner/name)")
    ap.add_argument("--dry-run", action="store_true", help="Do not make changes; print actions")
    ap.add_argument("--assignees-json", help="JSON file mapping area->list of GH usernames")
    ap.add_argument("--sleep", type=float, default=0.2, help="Sleep seconds between issues")
    args = ap.parse_args()

    mapping: Dict[str, Dict[str, Any]] = load_json(args.map)
    assignees_map: Dict[str, List[str]] = {}
    if args.assignees_json:
        assignees_map = load_json(args.assignees_json)

    agents_mention = os.environ.get("AGENTS_MENTION", "@Claude @Codex @Copilot")

    results = []
    keys = list(mapping.keys())
    # deterministic order for reproducibility
    keys.sort()

    for k in keys:
        entry = mapping[k]
        issue = int(entry["issue"]) if isinstance(entry.get("issue"), (int, str)) else None
        if issue is None:
            continue
        path_line = k
        area = area_for_path(path_line.split(":")[0])
        title = entry.get("title", "")
        assigned: List[str] = []
        comment_posted = False
        err: str = ""

        # Prepare comment body
        body = (
            f"Automated kickoff (TODO migration)\n\n"
            f"Location: `{path_line}`\n"
            f"Area: `{area}`\n\n"
            f"Original TODO: {title or '(not provided)'}\n\n"
            f"Agents: {agents_mention}\n\n"
            f"Acceptance Criteria (draft):\n"
            f"- Address the TODO described above.\n"
            f"- Add/adjust tests to cover the change.\n"
            f"- Link the PR to this issue and include Problem/Solution/Impact.\n"
        )

        try:
            if args.dry_run:
                print(f"[DRY-RUN] Would assign issue #{issue} (area={area}) and post kickoff comment")
            else:
                # Attempt assignment if mapping provided for area
                area_assignees = assignees_map.get(area, [])
                if area_assignees:
                    try:
                        run_cmd([
                            "gh",
                            "issue",
                            "edit",
                            str(issue),
                            "--repo",
                            args.repo,
                            "--add-assignee",
                            ",".join(area_assignees),
                        ])
                        assigned = list(area_assignees)
                    except subprocess.CalledProcessError as e:
                        err = f"assign_failed: {e.stderr.strip()}"

                # Post comment
                with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as tf:
                    tf.write(body)
                    tf.flush()
                    tmp_path = tf.name
                try:
                    run_cmd([
                        "gh",
                        "issue",
                        "comment",
                        str(issue),
                        "--repo",
                        args.repo,
                        "--body-file",
                        tmp_path,
                    ])
                    comment_posted = True
                except subprocess.CalledProcessError as e:
                    err = (err + "; " if err else "") + f"comment_failed: {e.stderr.strip()}"
                finally:
                    try:
                        os.unlink(tmp_path)
                    except Exception:
                        pass

                time.sleep(max(0.0, args.sleep))
        except Exception as e:
            err = (err + "; " if err else "") + f"unexpected_error: {e}"

        results.append({
            "issue": issue,
            "area": area,
            "location": path_line,
            "assigned": assigned,
            "comment_posted": comment_posted if not args.dry_run else False,
            "error": err,
        })

    outdir = ensure_artifacts_dir()
    out_path = outdir / "assignment_log.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Wrote assignment log to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

