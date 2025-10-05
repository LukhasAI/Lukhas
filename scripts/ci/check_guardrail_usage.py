#!/usr/bin/env python3
# scripts/ci/check_guardrail_usage.py
"""
T4 / 0.01% guard: ban direct LLM calls; require llm_guardrail.

Blocks common SDKs unless:
- path is tests/*
- path is core/bridge/llm_guardrail.py (the wrapper)
- path is docs/* (snippets are allowed)

Extendable: add vendors as needed.
"""

import re
import sys
from pathlib import Path

BANNED = [
    r"\bopenai\.",                  # OpenAI Python
    r"\banthropic\.",               # Anthropic Python
    r"\bgoogle\.generativeai\.",    # Google GenAI
    r"\bbotocore\.client\(['\"]bedrock['\"]\)",  # AWS Bedrock
]
ALLOWLIST_PREFIXES = ("tests/", "docs/", "core/bridge/llm_guardrail.py")

def search_file(p: Path) -> list[str]:
    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []
    hits = []
    for pat in BANNED:
        if re.search(pat, text):
            hits.append(pat)
    return hits

def main() -> int:
    # Pre-commit passes file list; fall back to repo scan if none given
    files = [Path(f) for f in sys.argv[1:] if f.endswith(".py")]
    if not files:
        # Conservative fallback: only scan tracked Python files
        try:
            import shlex
            import subprocess
            out = subprocess.check_output(shlex.split("git ls-files '*.py'")).decode().splitlines()
            files = [Path(x) for x in out]
        except Exception:
            return 0  # non-fatal in odd environments

    violations = []
    for p in files:
        sp = str(p).replace("\\", "/")
        if sp.startswith(ALLOWLIST_PREFIXES):
            continue
        hits = search_file(p)
        if hits:
            violations.append((sp, hits))

    if not violations:
        return 0

    print("❌ Direct LLM calls detected. Use core.bridge.llm_guardrail.call_llm(...)\n")
    for sp, hits in violations:
        pats = ", ".join(set(hits))
        print(f" - {sp}  ← matched: {pats}")
    print("\nFix: replace direct SDK calls with the guardrail wrapper.")
    return 2

if __name__ == "__main__":
    sys.exit(main())
