# tools/reports/weekly_hygiene.py
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def todo_count():
    p = Path("reports/todos/index.json")
    if not p.exists():
        return 0
    data = json.loads(p.read_text() or "{}")
    return sum(len(v) for v in data.get("files", {}).values())


def lint_debt():
    # allowlist-only, whole repo
    Path("reports/lints").mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            [
                "ruff",
                "check",
                "--output-format",
                "json",
                "-o",
                "reports/lints/ruff_dash.json",
                ".",
            ],
            check=False,
            capture_output=True,
        )
    except FileNotFoundError:
        # Ruff not installed, create empty results
        Path("reports/lints/ruff_dash.json").write_text("[]")
        return 0
    pol = Path(".t4autofix.toml")
    if not pol.exists():
        return 0

    import tomllib

    try:
        allowed = set(tomllib.loads(pol.read_text()).get("rules", {}).get("allow", []))
        if not allowed:
            # Fallback to auto_fix rules
            allowed = set(tomllib.loads(pol.read_text()).get("rules", {}).get("auto_fix", []))
        if not allowed:
            # Use DEFAULT_ALLOW
            allowed = {"UP006", "UP035", "SIM102", "SIM103", "F841", "B007", "C401"}
    except Exception:
        allowed = {"UP006", "UP035", "SIM102", "SIM103", "F841", "B007", "C401"}

    try:
        data = json.loads(Path("reports/lints/ruff_dash.json").read_text() or "[]")
    except Exception:
        return 0

    return sum(1 for d in data if d.get("code") in allowed)


def nightly_prs_last_7():
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
        )
        arr = json.loads(out)
        return len(arr)
    except Exception:
        return 0


def spark(n):
    # tiny unicode sparkline by magnitude
    blocks = "▁▂▃▄▅▆▇█"
    n = max(0, n)
    idx = min(int(n / 5), len(blocks) - 1)
    return blocks[idx] * min(n, 20)


def main():
    todos = todo_count()
    debt = lint_debt()
    prs = nightly_prs_last_7()

    Path("reports/autofix").mkdir(parents=True, exist_ok=True)
    Path("reports/autofix/weekly.md").write_text(
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
