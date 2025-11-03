#!/usr/bin/env python3
"""Generate a simple system health report from existing test summaries.

The script parses pass/fail counts from a markdown summary (default:
``TEST_RESULTS_SUMMARY.md``) and emits a markdown report plus a JSON payload
under ``docs/audits``. A shields.io-style badge line is included so the report
can be embedded directly in dashboards/READMEs.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path

DEFAULT_SUMMARY = Path("TEST_RESULTS_SUMMARY.md")
OUTPUT_DIR = Path("docs/audits")
MARKDOWN_OUT = OUTPUT_DIR / "system_health.md"
JSON_OUT = OUTPUT_DIR / "system_health.json"

BADGE_TEMPLATE = "![Smoke Tests](https://img.shields.io/badge/Smoke%20Tests-{passed}%2F{total}%20passing-{color})"


class ParseError(RuntimeError):
    """Raised when we cannot parse pass/fail counts from a summary input."""


def _detect_counts(text: str) -> tuple[int, int]:
    """Extract ``(passed, total)`` counts from summary markdown text."""
    # Pattern 1: "Test Results: 20/26 smoke tests passing"
    match = re.search(r"(?P<passed>\d+)\s*/\s*(?P<total>\d+)\s+smoke\s+tests", text, re.IGNORECASE)
    if match:
        passed = int(match.group("passed"))
        total = int(match.group("total"))
        return passed, total

    # Pattern 2: "20 passed, 6 failed"
    match = re.search(
        r"(?P<passed>\d+)\s+passed[^\n]*?(?P<failed>\d+)\s+failed",
        text,
        re.IGNORECASE,
    )
    if match:
        passed = int(match.group("passed"))
        failed = int(match.group("failed"))
        total = passed + failed
        return passed, total

    raise ParseError("Could not find pass/fail counts in summary text")


def _badge_color(pass_rate: float) -> str:
    if pass_rate >= 0.95:
        return "brightgreen"
    if pass_rate >= 0.85:
        return "green"
    if pass_rate >= 0.70:
        return "yellow"
    if pass_rate > 0:
        return "orange"
    return "lightgrey"


def _render_badge(passed: int, total: int) -> str:
    if total <= 0:
        return BADGE_TEMPLATE.format(passed=passed, total=total, color="lightgrey")
    color = _badge_color(passed / total)
    return BADGE_TEMPLATE.format(passed=passed, total=total, color=color)


def _load_summary(path: Path) -> str:
    if not path.exists():
        raise ParseError(f"Summary file not found: {path}")
    return path.read_text(encoding="utf-8")


def _timestamp() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def generate_report(summary_path: Path = DEFAULT_SUMMARY) -> dict[str, object]:
    """Generate the system health data structure from the summary file."""
    text = _load_summary(summary_path)
    passed, total = _detect_counts(text)
    failed = max(total - passed, 0)
    pass_rate = (passed / total) if total else 0.0
    badge = _render_badge(passed, total)

    return {
        "generated_at": _timestamp(),
        "summary_source": str(summary_path),
        "tests": {
            "passed": passed,
            "failed": failed,
            "total": total,
            "pass_rate": round(pass_rate, 4),
        },
        "badge_markdown": badge,
    }


def write_outputs(payload: dict[str, object]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    MARKDOWN_OUT.write_text(
        "\n".join(
            [
                "# System Health Snapshot",
                "",
                f"Generated: {payload['generated_at']}",
                "",
                str(payload["badge_markdown"]),
                "",
                f"- Tests Passed: {payload['tests']['passed']}",
                f"- Tests Failed: {payload['tests']['failed']}",
                f"- Total Tests: {payload['tests']['total']}",
                f"- Pass Rate: {payload['tests']['pass_rate'] * 100:.2f}%",
                "",
            ]
        ),
        encoding="utf-8",
    )

    JSON_OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate system health report")
    parser.add_argument(
        "--summary",
        type=Path,
        default=DEFAULT_SUMMARY,
        help="Path to markdown summary with pass/fail counts (default: TEST_RESULTS_SUMMARY.md)",
    )
    args = parser.parse_args(argv)

    try:
        payload = generate_report(args.summary)
    except ParseError as exc:
        parser.error(str(exc))
        return 2

    write_outputs(payload)
    print(f"✅ Generated system health report: {MARKDOWN_OUT}")
    print(f"✅ Generated system health JSON: {JSON_OUT}")
    print(f"   Badge: {payload['badge_markdown']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
