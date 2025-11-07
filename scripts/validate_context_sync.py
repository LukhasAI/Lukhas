#!/usr/bin/env python3

"""Context Sync Validator - ensures lane-aware documentation consistency"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

REQUIRED = [
    r"Schema v2\.0\.0",
    r"Lane:\s*(production|integration|development)",
    r"Canonical imports:\s*lukhas\.\*",
]

FILES = [
    ROOT/"claude.me",
    ROOT/"lukhas_context.md",
    ROOT/"candidate/claude.me",
    ROOT/"candidate/core/claude.me",
    ROOT/"lukhas/claude.me",
]

bad = []

for f in FILES:
    if not f.exists():
        bad.append((str(f), "missing"))
        continue

    t = f.read_text(errors="ignore")
    for pat in REQUIRED:
        if not re.search(pat, t):
            bad.append((str(f), f"missing: {pat}"))
            break

if bad:
    print("Context sync failures:")
    for p, why in bad:
        print(f" - {p}: {why}")
    sys.exit(2)

print("Context sync OK")
