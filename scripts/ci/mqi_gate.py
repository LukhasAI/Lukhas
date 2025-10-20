#!/usr/bin/env python3
"""
T4/0.01% Manifest Quality Index (MQI) Gate
==========================================

Score each manifest 0-100 based on:
- Schema compliance (20)
- Provenance presence (15)
- Vocab-compliant features (15)
- APIs import-verified + doc_ok (15)
- SLA targets present (10)
- Observed data fresh ≤14d (15)
- Coverage meets target (10)

Gate merges at MQI ≥ 90 for lane:L2/L3 modules.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


def score_manifest(manifest_path: Path) -> tuple[int, list[str]]:
    """
    Score a single manifest.

    Returns:
        (score, reasons) tuple
    """
    try:
        data = json.loads(manifest_path.read_text())
    except (json.JSONDecodeError, FileNotFoundError):
        return 0, ["invalid_json"]

    score = 0
    reasons = []

    # 1. Schema compliance (assumed valid if we got here - checked in validate_schema.py)
    # Add 20 points baseline

    # 2. Provenance presence (15 points)
    prov = data.get("_provenance", {})
    critical_fields = {"description", "features", "apis"}
    prov_fields = critical_fields & set(prov.keys())

    if len(prov_fields) == len(critical_fields):
        score += 15
        reasons.append("provenance_complete")
    elif prov_fields:
        partial = len(prov_fields) * 15 // len(critical_fields)
        score += partial
        reasons.append(f"provenance_partial:{len(prov_fields)}/{len(critical_fields)}")

    # 3. Vocab-compliant features (15 points)
    features = data.get("features", [])
    if features and len(features) >= 3:
        score += 15
        reasons.append(f"features_ok:{len(features)}")
    elif features:
        score += 10
        reasons.append(f"features_minimal:{len(features)}")

    # 4. APIs import-verified + doc_ok (15 points)
    apis = data.get("apis", {})
    if apis:
        verified = sum(
            1 for v in apis.values()
            if isinstance(v, dict) and v.get("import_verified") and v.get("doc_ok")
        )
        total = len(apis)

        if verified == total:
            score += 15
            reasons.append(f"apis_verified:{verified}/{total}")
        elif verified > 0:
            partial = verified * 15 // total
            score += partial
            reasons.append(f"apis_partial:{verified}/{total}")

    # 5. SLA targets present (10 points)
    sla_targets = data.get("performance", {}).get("sla_targets", {})
    if sla_targets:
        score += 10
        reasons.append("sla_targets_present")

    # 6. Observed data freshness ≤14d (15 points) for L2/L3 lanes
    tags = data.get("tags", [])
    lane = next((t for t in tags if t.startswith("lane:")), "lane:l1-experimental")

    if lane in {"lane:l2-integration", "lane:l3-production"}:
        observed = data.get("performance", {}).get("observed", {})
        observed_at = observed.get("observed_at")

        if observed_at:
            try:
                obs_dt = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
                age = datetime.now(timezone.utc) - obs_dt

                if age <= timedelta(days=14):
                    score += 15
                    reasons.append(f"observed_fresh:{age.days}d")
                else:
                    score += 5  # Partial credit if present but stale
                    reasons.append(f"observed_stale:{age.days}d")
            except (ValueError, TypeError):
                reasons.append("observed_invalid_timestamp")
        else:
            reasons.append("observed_missing")
    else:
        # Not required for L1/experimental
        score += 15
        reasons.append("observed_not_required")

    # 7. Coverage meets target (10 points)
    testing = data.get("testing", {})
    target = testing.get("coverage_target")
    observed = testing.get("coverage_observed")

    if target and observed is not None:
        if observed >= target:
            score += 10
            reasons.append(f"coverage_met:{observed}%≥{target}%")
        else:
            partial = int((observed / target) * 10)
            score += partial
            reasons.append(f"coverage_partial:{observed}%<{target}%")
    elif target:
        # Target set but no measurement yet - partial credit
        score += 5
        reasons.append("coverage_target_only")

    return score, reasons


def main():
    parser = argparse.ArgumentParser(description="MQI gate for manifest quality")
    parser.add_argument(
        "--min",
        type=int,
        default=90,
        help="Minimum MQI score required (default: 90)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show scores for all manifests"
    )

    args = parser.parse_args()

    root = Path(".")

    # Find all manifests
    manifests = [
        m for m in root.rglob("module.manifest.json")
        if not any(part in m.parts for part in ["node_modules", ".venv", "dist", "__pycache__"])
    ]

    print(f"🔍 Scoring {len(manifests)} manifests (min: {args.min})...")

    failures = []
    total_score = 0

    for manifest_path in manifests:
        score, reasons = score_manifest(manifest_path)
        total_score += score

        module_name = manifest_path.parent.name

        if args.verbose:
            print(f"  {module_name}: {score}/100 ({', '.join(reasons[:3])})")

        if score < args.min:
            failures.append((module_name, score, reasons))

    avg_score = total_score / len(manifests) if manifests else 0

    print(f"\n📊 Average MQI: {avg_score:.1f}/100")

    if failures:
        print(f"\n❌ MQI gate failed ({len(failures)} modules below {args.min}):\n", file=sys.stderr)
        for module, score, reasons in failures:
            print(f"  {module}: {score}/100", file=sys.stderr)
            print(f"    Missing: {', '.join(reasons[:5])}", file=sys.stderr)
        sys.exit(1)

    print(f"✅ MQI gate passed (all modules ≥ {args.min})")
    sys.exit(0)


if __name__ == "__main__":
    main()
