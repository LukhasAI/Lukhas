#!/usr/bin/env python3
import json
import re
import subprocess
from collections import Counter

result = subprocess.run(
    [
        "python3",
        "-m",
        "ruff",
        "check",
        "--select",
        "F821",
        "--output-format",
        "json",
        "qi/distributed_qi_architecture.py",
    ],
    capture_output=True,
    text=True,
)
issues = json.loads(result.stdout) if result.stdout else []

print(f"File: qi/distributed_qi_architecture.py ({len(issues)} issues)\n")

names = []
for issue in issues:
    msg = issue.get("message", "")
    match = re.search(r"Undefined name `([^`]+)`", msg)
    if match:
        names.append(match.group(1))

name_counts = Counter(names)
print("Undefined names:")
for name, count in name_counts.most_common(10):
    print(f"  {count:2d}x {name}")
