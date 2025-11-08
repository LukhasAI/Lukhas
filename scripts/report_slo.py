#!/usr/bin/env python3
"""
T4/0.01% SLO Dashboard Generator
=================================

Auto-build SLO dashboard from manifests' performance.observed + sla_targets.
Provable, not vibes - all metrics from manifest data with timestamps.

Inputs:
  - docs/_generated/MODULE_REGISTRY.json
  - All module.manifest.json files

Output:
  - docs/_generated/SLO_DASHBOARD.md

Guarantees:
  - Emoji indicators based on thresholds only (no prose)
  - Sortable by violation status
  - Freshness tracking (observed_at timestamps)
  - Lane-specific filtering (L2/L3 have stricter requirements)

Usage:
  python scripts/report_slo.py
  python scripts/report_slo.py --verbose
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs" / "_generated" / "MODULE_REGISTRY.json"
OUTPUT = ROOT / "docs" / "_generated" / "SLO_DASHBOARD.md"


def parse_lane(tags: list[str]) -> str:
    """Extract lane from tags"""
    for tag in tags:
        if tag.startswith("lane:"):
            return tag.split(":")[1]
    return "unknown"


def days_since(timestamp: str) -> int:
    """Calculate days since timestamp"""
    if not timestamp:
        return 9999

    try:
        ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        delta = now - ts
        return delta.days
    except Exception:
        return 9999


def load_manifest(path: Path) -> Dict:
    """Load and parse manifest"""
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def extract_slo_data(manifest: Dict, module_name: str, tags: list[str]) -> tuple[str, Dict]:
    """Extract SLO data from manifest"""
    performance = manifest.get("performance", {}) or {}
    targets = performance.get("sla_targets", {}) or {}
    observed = performance.get("observed", {}) or {}

    lane = parse_lane(tags)

    slo = {
        "module": module_name,
        "lane": lane,
        "target_p95": targets.get("latency_p95_ms"),
        "observed_p95": observed.get("latency_p95_ms"),
        "observed_at": observed.get("observed_at"),
        "coverage_target": (manifest.get("testing", {}) or {}).get("coverage_target"),
        "coverage_observed": (manifest.get("testing", {}) or {}).get("coverage_observed")
    }

    # Calculate violations
    violations = []

    # P95 latency check
    if (slo['target_p95'] is not None and slo['observed_p95'] is not None) and slo['observed_p95'] > slo['target_p95']:
        violations.append("p95_latency")

    # Coverage check
    if (slo['coverage_target'] is not None and slo['coverage_observed'] is not None) and slo['coverage_observed'] < slo['coverage_target']:
        violations.append("coverage")

    # Freshness check (L2/L3 only, 14 days)
    if lane in ["L2", "L3"]:
        days = days_since(slo["observed_at"])
        if days > 14:
            violations.append("stale_data")

    slo["violations"] = violations
    slo["status"] = "✅" if not violations else "❌"

    return module_name, slo


def generate_dashboard(registry_path: Path, verbose: bool = False) -> str:
    """Generate SLO dashboard Markdown"""
    if not registry_path.exists():
        raise FileNotFoundError(f"Registry not found: {registry_path}")

    registry = json.loads(registry_path.read_text())

    # Collect SLO data
    slo_data = []

    for module in registry["modules"]:
        manifest_path = ROOT / module["manifest"]
        manifest = load_manifest(manifest_path)

        if not manifest:
            continue

        _, slo = extract_slo_data(manifest, module["name"], module.get("tags", []))

        # Only include modules with targets or observed data
        if slo["target_p95"] or slo["coverage_target"]:
            slo_data.append(slo)

            if verbose:
                status = "❌" if slo["violations"] else "✅"
                print(f"{status} {slo['module']}: {slo.get('violations', [])}")

    # Sort by status (violations first), then module name
    slo_data.sort(key=lambda s: (len(s["violations"]) == 0, s["module"]))

    # Generate Markdown
    md_lines = [
        "# SLO Dashboard",
        "",
        f"_Generated {datetime.now(timezone.utc).isoformat()}_",
        "",
        f"**Total modules tracked**: {len(slo_data)}",
        f"**Violations**: {sum(1 for s in slo_data if s['violations'])}",
        "",
        "## Summary",
        "",
        "| Module | Lane | Target p95 (ms) | Observed p95 (ms) | Coverage Target | Coverage Observed | Freshness (days) | Status |",
        "|--------|------|----------------:|------------------:|----------------:|------------------:|-----------------:|:------:|"
    ]

    for slo in slo_data:
        target_p95 = f"{slo['target_p95']:.1f}" if slo["target_p95"] is not None else "-"
        observed_p95 = f"{slo['observed_p95']:.1f}" if slo["observed_p95"] is not None else "-"
        coverage_target = f"{slo['coverage_target']:.1f}%" if slo["coverage_target"] is not None else "-"
        coverage_observed = f"{slo['coverage_observed']:.1f}%" if slo["coverage_observed"] is not None else "-"
        freshness = days_since(slo["observed_at"])
        freshness_str = str(freshness) if freshness < 9999 else "-"

        md_lines.append(
            f"| `{slo['module']}` | {slo['lane']} | {target_p95} | {observed_p95} | "
            f"{coverage_target} | {coverage_observed} | {freshness_str} | {slo['status']} |"
        )

    # Violations section
    violated = [s for s in slo_data if s["violations"]]
    if violated:
        md_lines.extend([
            "",
            "## Violations",
            ""
        ])

        for slo in violated:
            md_lines.append(f"### `{slo['module']}`")
            md_lines.append("")
            for violation in slo["violations"]:
                if violation == "p95_latency":
                    md_lines.append(
                        f"- **P95 Latency**: {slo['observed_p95']:.1f}ms > {slo['target_p95']:.1f}ms target"
                    )
                elif violation == "coverage":
                    md_lines.append(
                        f"- **Coverage**: {slo['coverage_observed']:.1f}% < {slo['coverage_target']:.1f}% target"
                    )
                elif violation == "stale_data":
                    days = days_since(slo["observed_at"])
                    md_lines.append(f"- **Stale Data**: {days} days old (> 14 day limit for {slo['lane']})")
            md_lines.append("")

    return "\n".join(md_lines) + "\n"


def main():
    ap = argparse.ArgumentParser(
        description="Generate SLO dashboard from manifest performance data"
    )
    ap.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed progress"
    )
    args = ap.parse_args()

    try:
        dashboard = generate_dashboard(REGISTRY, args.verbose)

        # Write output
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(dashboard)

        print("✅ SLO_DASHBOARD.md")
        print(f"   Location: {OUTPUT.relative_to(ROOT)}")

        sys.exit(0)

    except Exception as e:
        print(f"❌ Failed to generate SLO dashboard: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
