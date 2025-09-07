import re
import sys
from pathlib import Path

import streamlit as st

rx = r"@pytest\.mark\.(skip|skipif|xfail).*?(?:reason\s*=\s*['\"]).*?(temporary|flaky|todo|agent|llm)['\"]"
bad = []
for f in Path("tests").rglob("*.py"):
    s = f.read_text(errors="ignore").lower()
    if "pytest" in s and re.search(rx, s, re.S):
        bad.append(str(f))
if bad:
    print("❌ Suspicious skip/xfail markers:", *[f"- {x}" for x in bad], sep="\n")
    sys.exit(1)
