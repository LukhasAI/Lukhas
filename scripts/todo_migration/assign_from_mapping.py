#!/usr/bin/env python3
"""
Assign owners to TODO issues based on area mapping.

Usage:
  python3 scripts/todo_migration/assign_from_mapping.py \
    --map artifacts/todo_to_issue_map.json \
    --assignees artifacts/assignees_by_area.json \
    --repo LukhasAI/Lukhas \
    [--dry-run]
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


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


def run(cmd: str) -> subprocess.CompletedProcess:
    print("+", cmd)
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def gh_add_assignee(repo: str, issue: int, assignee: str, dry: bool = False) -> bool:
    if dry:
        print(f"[DRY] would add assignee '{assignee}' to {repo}#{issue}")
        return True
    cmd = f"gh issue edit {issue} --repo {repo} --add-assignee {assignee}"
    r = run(cmd)
    if r.returncode != 0:
        print("ERR:", r.stderr.strip())
    return r.returncode == 0


def gh_comment(repo: str, issue: int, msg: str, dry: bool = False) -> bool:
    if dry:
        print(f"[DRY] would post comment to {repo}#{issue}")
        return True
    tf = tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8")
    tf.write(msg)
    tf.close()
    cmd = f"gh issue comment {issue} --repo {repo} --body-file {tf.name}"
    r = run(cmd)
    if r.returncode != 0:
        print("ERR:", r.stderr.strip())
    return r.returncode == 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--map", required=True)
    p.add_argument("--assignees", required=True)
    p.add_argument("--repo", default="LukhasAI/Lukhas")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    mapping = json.loads(Path(args.map).read_text(encoding="utf-8"))
    ass_map = json.loads(Path(args.assignees).read_text(encoding="utf-8"))

    log = []
    # deterministic order
    for key in sorted(mapping.keys()):
        val = mapping[key]
        issue = int(val.get("issue"))
        path = key.split(":")[0]
        area = area_for_path(path)
        owners = ass_map.get(area, [])
        entry = {"issue": issue, "area": area, "assigned": [], "skipped": [], "errors": []}
        for owner in owners:
            ok = gh_add_assignee(args.repo, issue, owner, dry=args.dry_run)
            if ok:
                entry["assigned"].append(owner)
            else:
                entry["skipped"].append(owner)
        log.append(entry)

    out = Path("artifacts/assignment_log_final.json")
    out.write_text(json.dumps(log, indent=2), encoding="utf-8")
    print("Wrote", out)
    print("Assigned counts by area:")
    from collections import Counter

    c = Counter()
    for e in log:
        for _ in e["assigned"]:
            c[e["area"]] += 1
    print(dict(c))


if __name__ == "__main__":
    sys.exit(main())
