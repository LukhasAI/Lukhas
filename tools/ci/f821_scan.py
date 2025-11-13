#!/usr/bin/env python3
"""
F821 scan & prioritizer

Input: /tmp/ruff_f821.json (ruff --select F821 --output-format json .)
Output:
 - /tmp/ruff_f821_summary.json (structured summary)
 - Prints:
    * Top files by F821 count (top 40)
    * Top undefined names (top 60)
    * Suggested heuristic shard (files to try first)
"""

import json
import pathlib
import re
import sys
from collections import Counter, defaultdict

# Try updated file first, then cleaned, then original
RuffJsonPath = pathlib.Path("/tmp/ruff_f821_updated.json")
if not RuffJsonPath.exists():
    RuffJsonPath = pathlib.Path("/tmp/ruff_f821_clean.json")
if not RuffJsonPath.exists():
    RuffJsonPath = pathlib.Path("/tmp/ruff_f821.json")

if not RuffJsonPath.exists():
    print("Missing /tmp/ruff_f821.json. Run:")
    print(
        "  python3 -m ruff check --select F821 --output-format json . > /tmp/ruff_f821.json"
    )
    sys.exit(1)

data = json.loads(RuffJsonPath.read_text())

# Counters
by_file = Counter()
by_name = Counter()
occurrences = defaultdict(list)

# Extract undefined name from typical ruff message
name_re = re.compile(r"Undefined name [`']([^'`]+)[`']")

for rec in data:
    fn = rec.get("filename")
    msg = rec.get("message", "")
    loc = rec.get("location", {})
    row = loc.get("row")
    by_file[fn] += 1
    m = name_re.search(msg)
    if m:
        nm = m.group(1)
    else:
        # fallback: guess last token in message
        parts = re.findall(r"[`']([^'`]+)[`']", msg)
        nm = parts[0] if parts else msg[:30]
    by_name[nm] += 1
    occurrences[fn].append({"name": nm, "msg": msg, "row": row})

# Print top files
print("\n=== Top files by F821 count ===")
for f, c in by_file.most_common(40):
    print(f"{c:4d}  {f}")

print("\n=== Top undefined names ===")
for name, c in by_name.most_common(60):
    print(f"{c:4d}  {name}")

# Heuristic map for common missing imports to try first
HEUR = {
    "np": "import numpy as np",
    "pd": "import pandas as pd",
    "torch": "import torch",
    "plt": "from matplotlib import pyplot as plt",
    "Path": "from pathlib import Path",
    "dataclass": "from dataclasses import dataclass",
    "dataclasses": "from dataclasses import dataclass",
    "Optional": "from typing import Optional",
    "List": "from typing import List",
    "Dict": "from typing import Dict",
    "Any": "from typing import Any",
    "Union": "from typing import Union",
    "Tuple": "from typing import Tuple",
    "datetime": "from datetime import datetime",
}

# Build a heuristic shard: files where the undefined name is in HEUR
heuristic_shard = []
for fname, items in occurrences.items():
    # skip test files optionally? we'll include both, but top-level strategy can filter
    for it in items:
        nm = it["name"]
        if nm in HEUR:
            heuristic_shard.append((fname, nm))
            break

# Deduplicate and keep a reasonable shard size
seen = set()
heuristic_files = []
for f, nm in heuristic_shard:
    if f in seen:
        continue
    seen.add(f)
    heuristic_files.append((f, nm))
    if len(heuristic_files) >= 40:
        break

print("\n=== Heuristic-first candidate files (name -> suggested import) ===")
for f, nm in heuristic_files[:40]:
    print(f"{f}  ->  {nm}   ({HEUR.get(nm)})")

# For convenience, create a compact suggested-shard (first 12 files)
shard = [f for f, nm in heuristic_files[:12]]
shard_path = pathlib.Path("/tmp/f821_first_shard.txt")
shard_path.write_text("\n".join(shard))
print(f"\nWrote suggested shard (first 12 heuristic files) to {shard_path}")

# Prepare summary JSON
summary = {
    "total_f821": len(data),
    "unique_files": len(by_file),
    "unique_names": len(by_name),
    "top_files": by_file.most_common(40),
    "top_names": by_name.most_common(60),
    "heuristic_shard": [
        {"file": f, "name": n, "suggested_import": HEUR.get(n)}
        for f, n in heuristic_files[:40]
    ],
    "first_shard": shard,
}

out_path = pathlib.Path("/tmp/ruff_f821_summary.json")
out_path.write_text(json.dumps(summary, indent=2))
print(f"\nWrote summary to {out_path}")
