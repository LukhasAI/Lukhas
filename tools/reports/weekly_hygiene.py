"""Generate the weekly hygiene report for automated maintenance."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Repository context for relative paths
REPO_ROOT = Path(__file__).resolve().parents[2]


def todo_count(base_path: Optional[Path] = None) -> int:
    """Return the number of tracked TODO entries from the generated index."""

    base = Path(base_path or REPO_ROOT)
    p = base / "reports" / "todos" / "index.json"
    if not p.exists():
        return 0
    try:
        data = json.loads(p.read_text(encoding="utf-8") or "{}")
    except json.JSONDecodeError:
        return 0
    return sum(len(v) for v in data.get("files", {}).values())


def lint_debt(base_path: Optional[Path] = None) -> int:
    # allowlist-only, whole repo
    base = Path(base_path or REPO_ROOT)
    lint_dir = base / "reports" / "lints"
    lint_dir.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            [
                "ruff",
                "check",
                "--output-format",
                "json",
                "-o",
                str(lint_dir / "ruff_dash.json"),
                ".",
            ],
            check=False,
            capture_output=True,
            cwd=base,
        )
    except FileNotFoundError:
        # Ruff not installed, create empty results
        (lint_dir / "ruff_dash.json").write_text("[]", encoding="utf-8")
        return 0
    pol = base / ".t4autofix.toml"
    if not pol.exists():
        return 0

    import tomllib

    try:
        allowed = set(tomllib.loads(pol.read_text(encoding="utf-8")).get("rules", {}).get("allow", []))
        if not allowed:
            # Fallback to auto_fix rules
            allowed = set(tomllib.loads(pol.read_text(encoding="utf-8")).get("rules", {}).get("auto_fix", []))
        if not allowed:
            # Use DEFAULT_ALLOW
            allowed = {"UP006", "UP035", "SIM102", "SIM103", "F841", "B007", "C401"}
    except Exception:
        allowed = {"UP006", "UP035", "SIM102", "SIM103", "F841", "B007", "C401"}

    try:
        data = json.loads((lint_dir / "ruff_dash.json").read_text(encoding="utf-8") or "[]")
    except Exception:
        return 0

    return sum(1 for d in data if d.get("code") in allowed)


def nightly_prs_last_7(base_path: Optional[Path] = None) -> int:
    try:
        out = subprocess.check_output(
            [
                "gh",
                "pr",
                "list",
                "--label",
                "autofix-nightly",
                "--search",
                "updated:>=-7days",
                "--json",
                "number",
            ],
            text=True,
            cwd=base_path or REPO_ROOT,
        )
        arr = json.loads(out)
        return len(arr)
    except Exception:
        return 0


def spark(n):
    # tiny unicode sparkline by magnitude
    # ΛTAG: hygiene_metrics_sparkline
    blocks = "▁▂▃▄▅▆▇█"
    n = max(0, n)
    idx = min(int(n / 5), len(blocks) - 1)
    return blocks[idx] * min(n, 20)


def main(base_path: Optional[Path] = None) -> int:
    """Run the hygiene report generation workflow."""

    # ΛTAG: hygiene_reporting
    base = Path(base_path or REPO_ROOT)
    todos = todo_count(base)
    debt = lint_debt(base)
    prs = nightly_prs_last_7(base)

    report_dir = base / "reports" / "autofix"
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "weekly.md").write_text(
        "# Weekly Hygiene\n\n"
        f"* TODO count: {todos} {spark(todos)}\n"
        f"* Allowlist lint debt: {debt} {spark(debt)}\n"
        f"* Nightly PRs (7d): {prs} {spark(prs)}\n",
        encoding="utf-8",
    )
    print("Wrote reports/autofix/weekly.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
