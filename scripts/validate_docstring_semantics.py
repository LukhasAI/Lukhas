#!/usr/bin/env python3
"""
Validate docstring semantic completeness (advisory).

Performs heuristic checks for missing module docstrings and function docstrings
lacking Args/Returns sections. Generates an advisory report for manual review.

Usage:
    python scripts/validate_docstring_semantics.py \
      --roots scripts api \
      --report docs/audits/docstring_semantics_report.md \
      --no-llm

Options:
    --no-llm: Skip LLM-based semantic validation (use heuristics only)
    --llm: LLM model to use for semantic validation (future)

Author: LUKHAS Development Team
Last Updated: 2025-10-19
"""
import argparse
import pathlib
import re


def main():
    """Heuristically validate docstring semantic completeness.

    Args:
        --roots: One or more root directories to scan for Python files.
        --report: Output Markdown report path.
        --no-llm: Skip any LLM-based checks (heuristics only).
        --llm: Optional model name for future semantic checks.

    Returns:
        None: Writes a report summarizing missing module/function docstrings.
    """
    p = argparse.ArgumentParser(description="Validate docstring semantics")
    p.add_argument("--roots", nargs="+", required=True, help="Root directories to analyze")
    p.add_argument("--report", required=True, help="Output Markdown report path")
    p.add_argument("--no-llm", action="store_true", help="Skip LLM validation")
    p.add_argument("--llm", default="", help="LLM model for semantic checks (future)")
    args = p.parse_args()

    candidates = []

    for root in args.roots:
        root_path = pathlib.Path(root)
        if not root_path.exists():
            print(f"⚠️  Skipping non-existent root: {root}")
            continue

        for py in root_path.rglob("*.py"):
            try:
                src = py.read_text(encoding="utf-8")

                # Heuristic 1: Module must have a top-level docstring
                if '"""' not in "\n".join(src.splitlines()[:20]):
                    candidates.append((py.as_posix(), "missing module docstring"))
                    continue

                # Heuristic 2: Functions without Args/Returns in docstrings
                for m in re.finditer(r"def\s+(\w+)\(.*?\):", src):
                    fn = m.group(1)
                    if fn.startswith("_"):  # Skip private functions
                        continue

                    # Crude slice around function
                    idx = m.start()
                    window = src[max(0, idx - 400): idx + 400]

                    if ("Args:" not in window) or ("Returns:" not in window):
                        candidates.append((f"{py.as_posix()}::{fn}", "missing Args/Returns"))

            except Exception:
                continue

    # Write report
    outp = pathlib.Path(args.report)
    outp.parent.mkdir(parents=True, exist_ok=True)

    report = "# Docstring Semantics Report\n\n"
    report += f"**Files Analyzed**: {sum(1 for r in args.roots for _ in pathlib.Path(r).rglob('*.py') if pathlib.Path(r).exists())}\n"
    report += f"**Issues Found**: {len(candidates)}\n\n"
    report += "---\n\n"

    if candidates:
        report += "## Issues\n\n"
        for path, why in candidates:
            report += f"- `{path}` — {why}\n"
    else:
        report += "## ✅ No Issues Found\n\nAll analyzed files meet semantic docstring requirements.\n"

    outp.write_text(report)

    print(f"✅ Wrote {args.report} with {len(candidates)} candidates")


if __name__ == "__main__":
    main()
