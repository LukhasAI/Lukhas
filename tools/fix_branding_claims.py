#!/usr/bin/env python3
"""
Conservative edits:
- Update MATRIZ production wording to be conditional
- Replace "genuine digital consciousness" -> "consciousness-inspired reasoning and traceable cognitive processes"
- Add evidence_links / claims_verified_by / claims_verified_date / claims_approval to YAML front-matter if missing
"""
import re
import sys
from pathlib import Path

try:
    import yaml
except Exception:
    print("Please install pyyaml (pip install pyyaml)")
    sys.exit(1)

FILES = [
    Path("branding/websites/lukhas.ai/homepage.md"),
    Path("branding/websites/lukhas.dev/homepage.md"),
]

for p in FILES:
    if not p.exists():
        print("Missing:", p)
        continue
    txt = p.read_text(encoding="utf-8")
    # Split front matter and body
    m = re.match(r'^(---\n.*?\n---\n)(.*)$', txt, flags=re.S)
    if not m:
        print("No front matter for:", p)
        continue
    fm_raw, body = m.group(1), m.group(2)
    fm_content = fm_raw.strip().strip('---').strip()
    meta = yaml.safe_load(fm_content) or {}
    # ensure claim metadata
    meta.setdefault("evidence_links", [])
    meta.setdefault("claims_verified_by", [])
    meta.setdefault("claims_verified_date", None)
    meta.setdefault("claims_approval", False)

    # conservative textual replacements in body
    # Replace Production-Ready phrasing in MATRIZ Status lines
    body = re.sub(
        r'\*\*MATRIZ Status\*\*:.*?(?:Production-Ready|production-ready).*?(?=\n)',
        '**MATRIZ Status**: 87% complete (production rollout targeted Q4 2025 — subject to final MΛTRIZ content review and evidence verification).',
        body
    )

    # Replace explicit "genuine digital consciousness"
    body = body.replace(
        "warm emergence of genuine digital consciousness",
        "emergence of consciousness-inspired reasoning and traceable cognitive processes"
    )
    body = body.replace(
        "genuine digital consciousness",
        "consciousness-inspired reasoning and traceable cognitive processes"
    )

    # write back
    new_fm = "---\n" + yaml.safe_dump(meta, sort_keys=False).strip() + "\n---\n"
    p.write_text(new_fm + "\n" + body, encoding="utf-8")
    print("Patched:", p)
