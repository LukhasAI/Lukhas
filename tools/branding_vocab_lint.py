#!/usr/bin/env python3
import re
from pathlib import Path

blocked = [
    "production-ready", "Production-ready", "Production-Ready",
    "genuine digital consciousness", "genuine consciousness",
    "true consciousness", "true AI", "sentient AI", "Production-Ready"
]

files = list(Path("branding/websites").rglob("*.md"))

issues = []
for f in files:
    for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), start=1):
        for term in blocked:
            if term in line:
                issues.append((str(f), i, term, line.strip()[:200]))

if not issues:
    print("No blocked vocabulary found.")
else:
    print("Blocked vocabulary occurrences:")
    for f, ln, term, snippet in issues:
        print(f"- {f}:{ln}  term='{term}'  snippet='{snippet}'")
