#!/usr/bin/env python3
"""
Author Reference Guard

Enforces the No-Name Inspiration Policy by detecting unauthorized author
references in public-facing content while allowing academic exceptions.
"""

import re
import sys
from pathlib import Path

import yaml

BLOCK_CTX_FLAG = "context: academic"


def load_blocklist(path=Path("tone/tools/author_blocklist.yaml")):
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def is_academic(text: str, file_path: str, cfg) -> bool:
    if BLOCK_CTX_FLAG in text:
        return True
    return any(
        str(file_path).replace("\\", "/").startswith(prefix.strip("/"))
        for prefix in cfg["exceptions"]["paths"]
    )


def scan_text(text: str, blocked: list[str]) -> list[str]:
    hits = []
    # whole-word-ish, case-insensitive
    for term in blocked:
        if re.search(rf"\b{re.escape(term)}\b", text, re.IGNORECASE):
            hits.append(term)
    return sorted(set(hits))


def validate_file(fp: Path, cfg) -> list[str]:
    try:
        text = fp.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []

    # Gate by extension and academic context
    if (
        fp.suffix.lower()
        not in {".md", ".mdx", ".txt", ".py", ".tsx", ".ts", ".js"}
        or is_academic(text, str(fp), cfg)
    ):
        return []

    # Process blocked terms, neutralizing allowed stance terms first
    blocked = cfg["blocked_terms"]
    processed_text = text
    for term in (cfg.get("allow_stance_terms") or []):
        processed_text = processed_text.replace(term, "")  # neutralize before scanning

    hits = scan_text(processed_text, blocked)
    return [f"{fp}: blocked reference -> {h}" for h in hits]


def validate_paths(paths):
    cfg = load_blocklist()
    violations = []
    for root in paths:
        root_path = Path(root)
        if root_path.is_file():
            # Handle single files directly
            violations.extend(validate_file(root_path, cfg))
        else:
            # Handle directories recursively
            for p in root_path.rglob("*"):
                if p.is_file():
                    violations.extend(validate_file(p, cfg))
    return violations


if __name__ == "__main__":
    roots = sys.argv[1:] or ["branding", "tone", "vocabularies", "content"]
    v = validate_paths(roots)
    if v:
        print("❌ Author-reference guard violations:")
        for line in v:
            print(" -", line)
        raise SystemExit(1)
    print("✅ Author-reference guard: clean")
