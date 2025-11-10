#!/usr/bin/env python3
"""
Generate Codex Web-ready prompt files from tasks/CODEX_PROMPTS.md and
optionally print GitHub CLI commands to create draft PRs for each task.

Outputs:
  - codex_artifacts/requests/<slug>.md: one per high-priority task (1–6)
  - codex_artifacts/requests/manifest.json: index with titles, slugs, branches

Usage:
  python3 scripts/push_codex_prompts.py [--dry-run] [--print-gh]

Notes:
  - Default is dry-run behavior for any gh actions; we only print commands.
  - This script does not modify code; it prepares request payloads you can
    paste into Codex Web or use with your VS Code extension.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
PROMPTS_MD = ROOT / "tasks" / "CODEX_PROMPTS.md"
OUT_DIR = ROOT / "codex_artifacts" / "requests"


@dataclass
class TaskPrompt:
    number: int
    title: str
    summary_bullets: list[str]
    code_prompt: str

    @property
    def slug(self) -> str:
        s = re.sub(r"[^a-z0-9]+", "-", self.title.lower()).strip("-")
        return f"{self.number:02d}-{s}"

    @property
    def branch(self) -> str:
        s = re.sub(r"[^a-z0-9]+", "-", self.title.lower()).strip("-")
        return f"codex/{s}"


HEADER_RE = re.compile(r"^###\s+(\d+)\.\s+\*\*(.+?)\*\*\s*$")


def _iter_lines(path: Path) -> Iterable[str]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            yield line.rstrip("\n")


def parse_high_priority_tasks(md_path: Path) -> list[TaskPrompt]:
    lines = list(_iter_lines(md_path))
    prompts: list[TaskPrompt] = []

    i = 0
    while i < len(lines):
        m = HEADER_RE.match(lines[i])
        if not m:
            i += 1
            continue
        number = int(m.group(1))
        title = m.group(2).strip()

        # Collect until next ### or end
        section: list[str] = []
        i += 1
        while i < len(lines) and not lines[i].startswith("### "):
            section.append(lines[i])
            i += 1

        # Within section, collect bullet lines under the header until first blank "Prompt example:" block
        bullets: list[str] = []
        for ln in section:
            if ln.strip().startswith("**Prompt example:"):
                break
            if ln.strip().startswith("-"):
                bullets.append(ln.strip().lstrip("- "))

        # Extract code block after **Prompt example:**
        code_prompt = ""
        in_code = False
        started = False
        for ln in section:
            if not started:
                if ln.strip().startswith("**Prompt example:"):
                    started = True
                continue
            if ln.strip().startswith("```"):
                if not in_code:
                    in_code = True
                    continue
                else:
                    in_code = False
                    break
            if in_code:
                code_prompt += (ln + "\n")

        prompts.append(TaskPrompt(number, title, bullets, code_prompt.strip()))

    # Keep only the first six high-priority items
    prompts = [p for p in prompts if 1 <= p.number <= 6]
    prompts.sort(key=lambda p: p.number)
    return prompts


def write_requests(tasks: list[TaskPrompt]) -> list[Path]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for t in tasks:
        out = OUT_DIR / f"{t.slug}.md"
        body = []
        body.append(f"# {t.title}\n")
        body.append("## Context\n")
        body.append("- Repo: Lukhas/Lukhas")
        body.append("- Label: codex:review")
        body.append("- PR: draft, assign Jules steward")
        body.append("- Branch: " + t.branch)
        if t.summary_bullets:
            body.append("\n## Requirements\n")
            for b in t.summary_bullets:
                body.append(f"- {b}")
        if t.code_prompt:
            body.append("\n## Prompt\n")
            body.append("```\n" + t.code_prompt + "\n```")
        body.append("\n## Checks\n")
        body.append("- Run ruff and mypy on changed files")
        body.append("- Add/adjust tests where behavior changes")
        body.append("- Keep patches focused and small")
        out.write_text("\n".join(body) + "\n", encoding="utf-8")
        written.append(out)
    # Manifest
    manifest = [
        {
            "number": t.number,
            "title": t.title,
            "slug": t.slug,
            "request_file": str((OUT_DIR / f"{t.slug}.md").relative_to(ROOT)),
            "branch": t.branch,
            "labels": ["codex:review"],
        }
        for t in tasks
    ]
    (OUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return written


def print_gh_commands(tasks: list[TaskPrompt]) -> None:
    for t in tasks:
        title = f"codex: {t.title}"
        body = (
            f"Automated Codex task: see `{(OUT_DIR / (t.slug + '.md')).relative_to(ROOT)}`.\n\n"
            f"Branch: `{t.branch}`. This PR should be created as DRAFT and labeled `codex:review`.\n"
        )
        cmd = [
            "gh", "pr", "create",
            "--draft",
            "--title", title,
            "--body", body,
            "--label", "codex:review",
        ]
        print("# Create draft PR (after pushing branch):")
        print(" ", " ".join(cmd))
        print()


def sh(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def current_branch() -> str:
    cp = sh(["git", "rev-parse", "--abbrev-ref", "HEAD"], check=False)
    return cp.stdout.strip() if cp.returncode == 0 else ""


def ensure_base_exists(base: str) -> str:
    # Best-effort: prefer provided base if it exists; else fall back to current.
    cp = sh(["git", "rev-parse", "--verify", base], check=False)
    if cp.returncode == 0:
        return base
    fallback = current_branch()
    if fallback:
        print(f"[INFO] Base '{base}' not found; using current branch '{fallback}'")
        return fallback
    raise SystemExit(f"Base branch '{base}' not found locally and no current branch detected.")


def create_branch_with_marker(task: TaskPrompt, base: str, dry_run: bool) -> None:
    marker_dir = ROOT / "codex_artifacts" / "branch_markers"
    marker_dir.mkdir(parents=True, exist_ok=True)
    marker_file = marker_dir / f"{task.slug}.txt"
    content = (
        f"Codex scaffold marker for '{task.title}'\n"
        f"Branch: {task.branch}\n"
        f"Request: codex_artifacts/requests/{task.slug}.md\n"
    )

    if dry_run:
        print(f"[DRY-RUN] create branch {task.branch} from {base} and add {marker_file.relative_to(ROOT)}")
        return

    # Create/update branch pointing at base
    sh(["git", "checkout", "-B", task.branch, base], check=False)
    marker_file.write_text(content, encoding="utf-8")
    sh(["git", "add", str(marker_file.relative_to(ROOT))])
    # Commit only if something staged
    cp = sh(["git", "diff", "--cached", "--quiet"], check=False)
    if cp.returncode != 0:
        sh(["git", "commit", "-m", f"codex: scaffold {task.slug}"])
    else:
        print(f"[INFO] No staged changes for {task.branch}; skipping commit")


def push_branch(task: TaskPrompt, dry_run: bool) -> None:
    if dry_run:
        print(f"[DRY-RUN] git push -u origin {task.branch}")
        return
    sh(["git", "push", "-u", "origin", task.branch], check=False)


def create_draft_pr(task: TaskPrompt, base: str, dry_run: bool) -> None:
    title = f"codex: {task.title}"
    body = (
        f"Automated Codex task: see `codex_artifacts/requests/{task.slug}.md`.\n\n"
        f"Branch: `{task.branch}`. This PR is a DRAFT labeled `codex:review`.\n"
    )
    args = [
        "gh", "pr", "create",
        "--draft",
        "--title", title,
        "--body", body,
        "--label", "codex:review",
        "--base", base,
        "--head", task.branch,
    ]
    if dry_run:
        print("[DRY-RUN] ", " ".join(args))
        return
    sh(args, check=False)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--print-gh", action="store_true", help="Print suggested gh commands for each task")
    ap.add_argument("--base", default="main", help="Base branch for scaffolding and PRs (default: main)")
    ap.add_argument("--scaffold-branches", action="store_true", help="Create per-task branches with marker commits")
    ap.add_argument("--push", action="store_true", help="Push created branches to origin")
    ap.add_argument("--create-prs", action="store_true", help="Create draft PRs via GitHub CLI for each task")
    ap.add_argument("--limit", type=int, default=0, help="Limit number of tasks processed (0 = all)")
    ap.add_argument("--dry-run", action="store_true", help="Preview actions without pushing or creating PRs")
    ap.add_argument("--emit-shell", action="store_true", help="Emit a shell script with git/gh commands for all tasks")
    args = ap.parse_args()

    if not PROMPTS_MD.exists():
        raise SystemExit(f"Missing {PROMPTS_MD}")

    tasks = parse_high_priority_tasks(PROMPTS_MD)
    if not tasks:
        raise SystemExit("No high-priority tasks found in CODEX_PROMPTS.md")
    if args.limit and args.limit > 0:
        tasks = tasks[: args.limit]
    written = write_requests(tasks)
    print(f"Wrote {len(written)} request files under {OUT_DIR.relative_to(ROOT)}")
    if args.print_gh:
        print()
        print_gh_commands(tasks)

    if args.scaffold_branches or args.push or args.create_prs:
        base = ensure_base_exists(args.base)
    else:
        base = args.base

    if args.scaffold_branches:
        for t in tasks:
            create_branch_with_marker(t, base, dry_run=args.dry_run)

    if args.push:
        for t in tasks:
            push_branch(t, dry_run=args.dry_run)

    if args.create_prs:
        for t in tasks:
            create_draft_pr(t, base, dry_run=args.dry_run)

    if args.emit_shell:
        script_path = OUT_DIR / "create_codex_prs.sh"
        lines = [
            "#!/usr/bin/env bash",
            "set -euo pipefail",
            f"BASE={base!s}",
            "echo 'Creating branches and draft PRs for Codex tasks...'",
            "# Ensure label exists (idempotent)",
            "gh label create 'codex:review' -d 'Codex task review' -c '#5319e7' >/dev/null 2>&1 || true",
        ]
        for t in tasks:
            mk = f"codex_artifacts/branch_markers/{t.slug}.txt"
            body = (
                f"Automated Codex task: see `codex_artifacts/requests/{t.slug}.md`.\\n\\n"
                f"Branch: `{t.branch}`. This PR is a DRAFT labeled `codex:review`."
            )
            lines += [
                f"echo '--- {t.branch} ---'",
                f"git checkout -B {t.branch} $BASE",
                "# Rebase on remote if exists to avoid push rejection; autostash local changes",
                f"git pull --rebase --autostash origin {t.branch} || true",
                f"mkdir -p codex_artifacts/branch_markers",
                f"printf '%s\n' 'Codex scaffold marker for {t.title}' 'Branch: {t.branch}' 'Request: codex_artifacts/requests/{t.slug}.md' > {mk}",
                f"git add {mk}",
                f"git commit -m 'codex: scaffold {t.slug}' || true",
                f"git push -u origin {t.branch}",
                "# Create draft PR",
                "gh pr create --draft "
                f"--title 'codex: {t.title}' "
                f"--body '{body}' "
                "--label codex:review "
                f"--base $BASE --head {t.branch} || "
                "gh pr create --draft "
                f"--title 'codex: {t.title}' "
                f"--body '{body}' "
                f"--base $BASE --head {t.branch}",
            ]
        script_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        # Best effort to make executable
        try:
            script_path.chmod(0o755)
        except Exception:
            pass
        print(f"Emitted shell: {script_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
