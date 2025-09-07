import re
import sys
from pathlib import Path

import streamlit as st

bad = []
for f in Path("tests").rglob("*.py"):
    s = f.read_text(errors="ignore")
    if re.search(r"\bfrom\s+unittest\.mock\s+import\s+\*", s):
        bad.append(str(f))
    # Disallow patch/monkeypatch in no-mock tests
    if "@pytest.mark.no_mock" in s and re.search(r"\b(monkeypatch|patch)\(", s):
        bad.append(str(f))
if bad:
    print(
        "❌ Unbounded mocking or mocking in @no_mock tests:",
        *[f"- {x}" for x in bad],
        sep="\n",
    )
    sys.exit(1)
