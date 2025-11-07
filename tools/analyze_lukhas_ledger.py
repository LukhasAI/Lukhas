#!/usr/bin/env python3
"""
Analyze lukhas_import_ledger.ndjson to generate migration scorecard.
Ranks top legacy imports and recommends canonical targets.
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

LEDGER = Path("artifacts/lukhas_import_ledger.ndjson")
REPORT = Path("artifacts/IMPORT_MIGRATION_REPORT.md")

def read_ledger():
    if not LEDGER.exists():
        print(f"no ledger at {LEDGER}", file=sys.stderr)
        sys.exit(1)
    for line in LEDGER.read_text().splitlines():
        if not line.strip():
            continue
        try:
            yield json.loads(line)
        except Exception:
            continue

def main():
    alias_counts = Counter()
    target_counts = Counter()
    misses = Counter()
    pairs = defaultdict(Counter)  # mod -> {real.mod: count}

    for ev in read_ledger():
        if ev.get("event") == "alias":
            lukhas_mod = ev.get("lukhas")
            real_mod = ev.get("real")
            if lukhas_mod and real_mod:
                alias_counts[lukhas_mod] += 1
                target_counts[real_mod] += 1
                pairs[lukhas_mod][real_mod] += 1
        elif ev.get("event") == "miss":
            lukhas_mod = ev.get("lukhas")
            if lukhas_mod:
                misses[lukhas_mod] += 1

    top_legacy = alias_counts.most_common(30)
    total_alias = sum(alias_counts.values())
    total_miss = sum(misses.values())

    # Pick a canonical target per lukhas.* (plurality vote)
    recommended = {}
    for lukhas_mod, _ in top_legacy:
        if pairs[lukhas_mod]:
            best = pairs[lukhas_mod].most_common(1)[0][0]
            recommended[lukhas_mod] = best

    # Emit report
    lines = []
    lines.append("# IMPORT MIGRATION REPORT\n")
    lines.append(f"- Total alias hits: **{total_alias}**")
    lines.append(f"- Total misses: **{total_miss}**\n")
    if top_legacy:
        lines.append("## Top legacy imports\n")
        lines.append("| rank | lukhas.* | hits | recommended canonical |")
        lines.append("|---:|---|---:|---|")
        for i, (lukhas_mod, hit_count) in enumerate(top_legacy, 1):
            lines.append(f"| {i} | `{lukhas_mod}` | {hit_count} | `{recommended.get(lukhas_mod, '-')}` |")
        lines.append("")
    if misses:
        lines.append("## Misses (need real modules or xfail)\n")
        for lukhas_mod, miss_count in misses.most_common(20):
            lines.append(f"- `{lukhas_mod}` - {miss_count} misses")
        lines.append("")
    REPORT.write_text("\n".join(lines))
    print(f"✅ Wrote {REPORT}")

if __name__ == "__main__":
    main()
