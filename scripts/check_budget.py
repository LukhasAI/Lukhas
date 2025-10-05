#!/usr/bin/env python3
import os
import sys

elapsed = float(os.environ.get("ELAPSED", "0") or 0)
budget = float(os.environ.get("BUDGET_SEC", "0") or 0)
suite = os.environ.get("SUITE", "suite")

if budget and elapsed > budget:
    print(f"❌ {suite}: elapsed {elapsed:.2f}s > budget {budget:.2f}s")
    sys.exit(1)

print(f"✅ {suite}: elapsed {elapsed:.2f}s within budget {budget:.2f}s")
