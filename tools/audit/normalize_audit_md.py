#!/usr/bin/env python3
"""
Normalize audit markdowns so merge_audits.py can parse them.

- <br> -> newline
- "File: path:start-endcode" -> opens ```code fence
- Auto-close ``` before next section/table
- Remove smart quotes/zero-width chars
- Fix tabbed table header to pipe table
"""

from __future__ import annotations

import argparse
import re
import sys

RE_BR = re.compile(r"<br\s*/?>", re.IGNORECASE)
SECTION_STARTS = (
    "Findings Table",
    "Top 5 Low-Effort",
    "Top 5 Low-Effort",
    "Contradictions Appendix",
    "Appendix",
    "Executive Summary",
    "Clinical Summary",
    "Evidence Ledger",
    "Scoreboard",
    "First 48 Hours",
)


def clean_unicode(s: str) -> str:
    s = s.replace("\u200b", "").replace("\ufeff", "").replace("\ufffc", "")
    s = s.replace('"', '"').replace('"', '"').replace("'", "'").replace("–", "-").replace("—", "-")
    return s


def normalize(md: str) -> str:
    md = md.replace("\r\n", "\n").replace("\r", "\n")
    md = clean_unicode(md)
    md = RE_BR.sub("\n", md)

    lines = md.splitlines()
    out, in_code = [], False
    for line in lines:
        m = re.match(r"^(File:\s*[^:\n]+:\d+-\d+)\s*code\s*$", line.strip(), re.IGNORECASE)
        if m:
            out.append(m.group(1))
            out.append("```code")
            in_code = True
            continue

        if re.match(r"^\s*L\d+:\s", line) and in_code:
            out.append(line)
            continue

        starts_section = (
            line.startswith("|")
            or any(line.strip().startswith(s) for s in SECTION_STARTS)
            or line.strip().startswith("#")
        )
        if in_code and starts_section:
            out.append("```")
            in_code = False

        out.append(line)

    if in_code:
        out.append("```")

    fixed = []
    for line in out:
        if line.strip().startswith("Category\tFile\tEvidence"):
            fixed.append("| Category | File | Evidence (line range) | Risk | Fix |")
            fixed.append("|---|---|---|---|---|")
        else:
            fixed.append(line)
    return "\n".join(fixed).strip() + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="outp", required=True)
    args = ap.parse_args()
    try:
        with open(args.inp, encoding="utf-8", errors="ignore") as f:
            md = f.read()
    except FileNotFoundError:
        print(f"ERROR: cannot read {args.inp}", file=sys.stderr)
        sys.exit(2)
    with open(args.outp, "w", encoding="utf-8") as f:
        f.write(normalize(md))
    print(f"Normalized: {args.inp} -> {args.outp}")


if __name__ == "__main__":
    main()
