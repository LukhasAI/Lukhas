import re
import sys
from pathlib import Path

PATS = [r"\bassert\s+True\b", r"^\s*pass\s*(#.*)?$", r"^\s*print\("]
bad = []
for f in Path("tests").rglob("*.py"):
    s = f.read_text(errors="ignore")
    if re.search("|".join(PATS), s, re.M):
        bad.append(str(f))
if bad:
    print("❌ Trivial patterns found in:", *[f"- {x}" for x in bad], sep="\n")
    sys.exit(1)