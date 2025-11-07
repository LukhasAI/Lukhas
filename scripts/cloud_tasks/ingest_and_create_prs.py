#!/usr/bin/env python3
"""
Ingest Codex Cloud Task patches (via manifest or directory) and open PRs.

Two modes:
  1) --manifest <json>: JSON with task entries including patch_url/patch_path
  2) --dir <path>: directory containing *.patch files (task id inferred from filename)

For each task/patch:
  - Create a feature branch from --base (default: main)
  - Apply the patch (git apply --index) with -p0/-p1/-p2 fallback, or git am --3way
  - Commit if needed (when using git apply)
  - Push and create a PR via GitHub CLI with labels
  - Log results to artifacts/cloud_tasks_pr_log.json

Usage examples:
  # Manifest mode (recommended)
  python3 scripts/cloud_tasks/ingest_and_create_prs.py \
    --manifest artifacts/cloud_tasks_manifest.json \
    --base main --label codex-cloud --label ready-for-review

  # Directory mode
  python3 scripts/cloud_tasks/ingest_and_create_prs.py \
    --dir artifacts/cloud_tasks/patches \
    --branch-prefix codex/cloudtask/ --base main
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from urllib.request import Request, urlopen


def sh(cmd: list[str], check=True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def fetch_url(url: str, headers: dict[str, str] | None = None) -> str:
    req = Request(url, headers=headers or {})
    with urlopen(req) as resp:
        return resp.read().decode("utf-8")


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def list_remote_branches() -> list[str]:
    cp = sh(["git", "ls-remote", "--heads", "origin"])
    branches = []
    for line in cp.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) == 2 and parts[1].startswith("refs/heads/"):
            branches.append(parts[1].replace("refs/heads/", "", 1))
    return branches


def pr_exists(branch: str) -> bool:
    cp = sh(["gh", "pr", "list", "--state", "all", "--head", branch, "--json", "number"], check=False)
    out = (cp.stdout or "").strip()
    return out not in ("", "[]")


def branch_exists_local(name: str) -> bool:
    cp = sh(["git", "branch", "--list", name], check=False)
    return name in (cp.stdout or "")


def branch_exists_remote(name: str) -> bool:
    return name in list_remote_branches()


def git_checkout_new(base: str, name: str) -> bool:
    # Ensure base is up to date
    sh(["git", "fetch", "origin", base])
    sh(["git", "checkout", base])
    sh(["git", "reset", "--hard", f"origin/{base}"])
    cp = sh(["git", "checkout", "-b", name], check=False)
    return cp.returncode == 0


def try_git_apply(patch_path: Path) -> tuple[bool, str]:
    # Try -p0/-p1/-p2 with --check first
    for p in ("0", "1", "2"):
        cp = sh(["git", "apply", "--check", f"-p{p}", str(patch_path)], check=False)
        if cp.returncode == 0:
            # Apply to index and working tree
            ap = sh(["git", "apply", "--index", f"-p{p}", str(patch_path)], check=False)
            if ap.returncode == 0:
                return True, f"git apply -p{p}"
    # Fall back to git am (mailbox)
    am = sh(["git", "am", "--3way", str(patch_path)], check=False)
    if am.returncode == 0:
        return True, "git am --3way"
    return False, (am.stderr or "apply failed")


def create_commit(default_message: str) -> None:
    # Only commit if there are staged changes
    diff = sh(["git", "diff", "--cached", "--name-only"], check=False).stdout.strip()
    if diff:
        sh(["git", "commit", "-m", default_message])


def push_and_create_pr(branch: str, base: str, title: str, body: str, labels: list[str]) -> tuple[bool, str]:
    sh(["git", "push", "-u", "origin", branch], check=False)
    args = [
        "gh", "pr", "create",
        "--base", base,
        "--head", branch,
        "--title", title,
        "--body", body,
    ]
    if labels:
        args += ["--label", ",".join(labels)]
    cp = sh(args, check=False)
    if cp.returncode != 0:
        return False, cp.stderr
    return True, cp.stdout.strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", help="JSON manifest describing cloud tasks")
    ap.add_argument("--dir", help="Directory containing *.patch files")
    ap.add_argument("--base", default="main")
    ap.add_argument("--branch-prefix", default="codex/cloudtask/")
    ap.add_argument("--label", action="append", default=["codex-cloud", "ready-for-review"])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument(
        "--header",
        action="append",
        help="HTTP header to include when fetching patch_url (e.g., 'Authorization: Bearer <token>')",
    )
    args = ap.parse_args()

    if not args.manifest and not args.dir:
        print("ERROR: Provide --manifest or --dir")
        return 2

    artifacts_dir = Path("artifacts") / "cloud_tasks"
    ensure_dir(artifacts_dir)
    patches_dir = artifacts_dir / "patches"
    ensure_dir(patches_dir)

    tasks: list[Dict] = []
    if args.manifest:
        data = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
        # Support either {"tasks":[...]} or a raw list
        tasks = data.get("tasks", data if isinstance(data, list) else [])
    else:
        for p in Path(args.dir).glob("*.patch"):
            tasks.append({
                "id": p.stem,
                "title": p.stem,
                "branch": f"{args.branch_prefix}{p.stem}",
                "patch_path": str(p),
            })

    log_entries: list[Dict] = []
    for t in tasks:
        tid = t.get("id") or t.get("task_id") or t.get("title")
        branch = t.get("branch") or f"{args.branch_prefix}{tid}"
        base = t.get("base") or args.base
        labels = t.get("labels") or args.label
        patch_path = t.get("patch_path")
        patch_url = t.get("patch_url")
        commit_message = t.get("commit_message") or f"chore(cloud): apply Codex Cloud Task {tid}"
        pr_title = t.get("pr_title") or f"codex: {tid} - cloud task"
        pr_body = t.get("pr_body") or (
            f"Automated PR for Codex Cloud Task `{tid}`.\n\n"
            f"- Base: `{base}`\n- Branch: `{branch}`\n"
            + (f"- Patch: {patch_url}\n" if patch_url else "")
        )

        entry = {
            "id": tid,
            "branch": branch,
            "base": base,
            "patch": patch_url or patch_path,
            "status": "pending",
        }

        try:
            if pr_exists(branch):
                entry["status"] = "pr_exists"
                log_entries.append(entry)
                print(f"[SKIP] PR already exists for {branch}")
                continue
            if branch_exists_remote(branch) or branch_exists_local(branch):
                # If branch exists but no PR, we will try to create PR directly
                print(f"[INFO] Branch {branch} exists. Will attempt PR creation without patch apply.")
            else:
                if args.dry_run:
                    print(f"[DRY-RUN] Would create branch {branch} from {base}")
                else:
                    ok = git_checkout_new(base, branch)
                    if not ok:
                        entry["status"] = "branch_create_failed"
                        log_entries.append(entry)
                        print(f"[FAIL] Could not create branch {branch}")
                        continue

                # Obtain patch content to a file
                if not patch_path and patch_url:
                    # Build headers map if provided
                    headers: dict[str, str] = {}
                    if args.header:
                        for h in args.header:
                            if ":" in h:
                                k, v = h.split(":", 1)
                                headers[k.strip()] = v.strip()
                    content = fetch_url(patch_url, headers=headers)
                    patch_path = str(patches_dir / f"{tid}.patch")
                    Path(patch_path).write_text(content, encoding="utf-8")

                if patch_path and not args.dry_run:
                    ok, how = try_git_apply(Path(patch_path))
                    if not ok:
                        entry["status"] = "apply_failed"
                        log_entries.append(entry)
                        print(f"[FAIL] Could not apply patch for {tid}")
                        sh(["git", "am", "--abort"], check=False)
                        sh(["git", "reset", "--hard"], check=False)
                        continue
                    create_commit(commit_message)
                    entry["applied_via"] = how

            if args.dry_run:
                print(f"[DRY-RUN] Would push {branch} and create PR → {base}")
                entry["status"] = "dry_run_ok"
            else:
                ok, pr_out = push_and_create_pr(branch, base, pr_title, pr_body, labels)
                if not ok:
                    entry["status"] = "pr_create_failed"
                    entry["error"] = pr_out
                    print(f"[FAIL] PR create failed for {branch}: {pr_out}")
                else:
                    entry["status"] = "pr_created"
                    entry["pr"] = pr_out
                    print(f"[OK] {pr_out}")

        except Exception as e:
            entry["status"] = "exception"
            entry["error"] = str(e)
            print(f"[EXC] {tid}: {e}")
        finally:
            log_entries.append(entry)

    # Write log
    out = Path("artifacts") / "cloud_tasks_pr_log.json"
    out.write_text(json.dumps(log_entries, indent=2), encoding="utf-8")
    print(f"Wrote log to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
