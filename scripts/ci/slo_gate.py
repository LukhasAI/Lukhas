#!/usr/bin/env python3
"""
T4/0.01% SLO Violation Gate
============================

Hard fail if any L2/L3 module violates SLA targets with fresh observed data.

Violation Conditions:
- observed.latency_p95_ms > sla_targets.latency_p95_ms
- observed_at ≤ 14 days old (configurable via schema/flags.json)
- Module is in lane:L2 or lane:L3

Guarantees:
- Hard fail on violations (non-zero exit)
- Actionable error messages with module names
- Configurable freshness threshold via flags

Usage:
  python scripts/ci/slo_gate.py
  python scripts/ci/slo_gate.py --verbose
  python scripts/ci/slo_gate.py --max-age-days 7
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "docs" / "_generated" / "MODULE_REGISTRY.json"
FLAGS = ROOT / "schemas" / "flags.json"


def load_flags() -> Dict:
    """Load feature flags"""
    if FLAGS.exists():
        try:
            return json.loads(FLAGS.read_text())
        except Exception:
            return {}
    return {}


def parse_lane(tags: List[str]) -> str:
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


def check_slo_violation(manifest: Dict, module_name: str, tags: List[str], max_age_days: int) -> tuple[bool, str]:
    """
    Check if module violates SLO targets.

    Returns:
        (violated: bool, reason: str)
    """
    lane = parse_lane(tags)

    # Only check L2/L3 modules
    if lane not in ["L2", "L3"]:
        return False, ""

    performance = manifest.get("performance", {}) or {}
    targets = performance.get("sla_targets", {}) or {}
    observed = performance.get("observed", {}) or {}

    target_p95 = targets.get("latency_p95_ms")
    observed_p95 = observed.get("latency_p95_ms")
    observed_at = observed.get("observed_at")

    # No targets or observations = no violation
    if target_p95 is None or observed_p95 is None:
        return False, ""

    # Check freshness
    days = days_since(observed_at)
    if days > max_age_days:
        # Stale data - don't block on it, but warn
        return False, ""

    # Check violation
    if observed_p95 > target_p95:
        return True, f"p95: {observed_p95:.1f}ms > {target_p95:.1f}ms target (observed {days}d ago)"

    return False, ""


def main():
    ap = argparse.ArgumentParser(description="Fail if L2/L3 modules violate SLA targets with fresh data")
    ap.add_argument(
        "--max-age-days", type=int, default=14, help="Maximum age of observed data to enforce (default: 14)"
    )
    ap.add_argument("--verbose", action="store_true", help="Show detailed checking")
    args = ap.parse_args()

    # Load flags
    flags = load_flags()
    max_age = flags.get("enforce_observed_freshness_days", args.max_age_days)

    # Load registry
    if not REGISTRY.exists():
        print(f"❌ Registry not found: {REGISTRY.relative_to(ROOT)}", file=sys.stderr)
        print("   Run: python scripts/generate_module_registry.py", file=sys.stderr)
        sys.exit(1)

    try:
        registry = json.loads(REGISTRY.read_text())
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in registry: {e}", file=sys.stderr)
        sys.exit(1)

    modules = registry.get("modules", [])
    print(f"🔍 Checking {len(modules)} modules for SLO violations (max age: {max_age}d)...")

    violations = []

    for module in modules:
        manifest_path = ROOT / module["manifest"]

        try:
            manifest = json.loads(manifest_path.read_text())
        except Exception:
            continue

        violated, reason = check_slo_violation(manifest, module["name"], module.get("tags", []), max_age)

        if violated:
            violations.append((module["name"], reason))

        if args.verbose and violated:
            print(f"❌ {module['name']}: {reason}")

    if violations:
        print(f"\n❌ SLO gate failed ({len(violations)} violations):\n", file=sys.stderr)
        for module_name, reason in violations:
            print(f"  {module_name}: {reason}", file=sys.stderr)
        print("\n💡 Fix performance issues or update sla_targets in manifests", file=sys.stderr)
        sys.exit(1)

    print("✅ No SLO violations (L2/L3 modules meet targets)")
    sys.exit(0)


if __name__ == "__main__":
    main()
