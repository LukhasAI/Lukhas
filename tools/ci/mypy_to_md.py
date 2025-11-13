#!/usr/bin/env python3
import os
import re
import sys
from collections import Counter, defaultdict

IN = sys.argv[1] if len(sys.argv) > 1 else "reports/audit/types/mypy.txt"
OUT = sys.argv[2] if len(sys.argv) > 2 else "reports/audit/types/mypy_summary.md"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

if not os.path.exists(IN):
    print(f"Missing input: {IN}", file=sys.stderr)
    sys.exit(1)

with open(IN, encoding="utf-8") as f:
    content = f.read()

# Parse mypy text output: path:line:col: [code] message
errors = []
by_file = defaultdict(list)
core_violations = 0


def is_core(p: str) -> bool:
    p = p.replace("\\", "/")
    return p.startswith("lukhas/") or p.startswith("MATRIZ/")


# Parse each line like: lukhas/api.py:25:10: error: Name 'foo' is not defined  [name-defined]
for _line_num, line in enumerate(content.splitlines(), 1):
    line = line.strip()
    if not line or line.startswith("Found ") or line.startswith("Success"):
        continue

    # Match: path:line:col: error_type: message [code]
    match = re.match(r"^([^:]+):(\d+):(\d+):\s*(\w+):\s*(.+?)(?:\s+\[([^\]]+)\])?$", line)
    if match:
        path, line_no, col, severity, message, code = match.groups()
        error = {
            "path": path,
            "line": int(line_no),
            "column": int(col),
            "code": code or "unknown",
            "message": message.strip(),
            "severity": severity,
        }
        errors.append(error)
        by_file[path].append(error)
        if is_core(path):
            core_violations += 1

counts = Counter(e["code"] for e in errors)

with open(OUT, "w", encoding="utf-8") as f:
    f.write("# Mypy Strict - Summary\n\n")
    f.write(f"- Total errors: {len(errors)}\n")
    f.write(f"- Core (lukhas/MATRIZ) errors: {core_violations}\n\n")
    if counts:
        f.write("## By error code\n")
        for k, v in counts.most_common():
            f.write(f"- `{k}`: {v}\n")
        f.write("\n")
    f.write("## Top files\n")
    for p, items in sorted(by_file.items(), key=lambda kv: len(kv[1]), reverse=True)[:10]:
        f.write(f"- {p}: {len(items)}\n")
    f.write("\n## Sample (first 12)\n")
    for e in errors[:12]:
        f.write(f"- {e['path']}:{e['line']}:{e['column']} [{e['code']}] {e['message']}\n")

print(f"Wrote {OUT}")
