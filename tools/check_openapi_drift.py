#!/usr/bin/env python3
"""
Deep OpenAPI specification drift detector with comprehensive diff analysis.

Usage:
    python tools/check_openapi_drift.py                    # Check for drift
    python tools/check_openapi_drift.py --autofix          # Update baseline
    python tools/check_openapi_drift.py --output drift.json  # Save to file
    python tools/check_openapi_drift.py --baseline custom.json  # Use custom baseline

Features:
    - Deep JSON Schema diff for OpenAPI specs
    - Detect path/method/response schema changes
    - Machine-readable JSON output
    - Optional auto-fix to update saved spec
    - CI/CD integration friendly
"""
import json
import sys
import argparse
from pathlib import Path
from typing import Any, Dict, Optional
from fastapi.testclient import TestClient

try:
    from deepdiff import DeepDiff
    DEEPDIFF_AVAILABLE = True
except ImportError:
    DEEPDIFF_AVAILABLE = False
    print("⚠️  Warning: deepdiff not installed. Install with: pip install deepdiff")
    print("   Falling back to basic comparison...")


def load_spec_from_app() -> Dict[str, Any]:
    """Load OpenAPI spec from the running FastAPI app."""
    try:
        from serve.main import app
        client = TestClient(app)
        response = client.get("/openapi.json")
        return response.json()
    except Exception as e:
        print(f"❌ Error: Could not import app: {e}", file=sys.stderr)
        sys.exit(1)


def load_spec_from_file(path: Path) -> Optional[Dict[str, Any]]:
    """Load OpenAPI spec from a JSON file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(1)


def save_spec_to_file(spec: Dict[str, Any], path: Path) -> None:
    """Save OpenAPI spec to a JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2, sort_keys=True)
    print(f"✅ Saved OpenAPI spec to {path}")


def basic_compare(baseline: Dict, current: Dict) -> Dict[str, Any]:
    """
    Basic comparison when DeepDiff is not available.
    Checks top-level keys and paths only.
    """
    # Check top-level keys
    live_keys = set(baseline.keys())
    saved_keys = set(current.keys())

    # Check paths
    lpaths = set(baseline.get("paths", {}).keys())
    spaths = set(current.get("paths", {}).keys())
    missing_paths = spaths - lpaths
    added_paths = lpaths - spaths

    return {
        "drift_detected": bool(live_keys != saved_keys or missing_paths or added_paths),
        "summary": {
            "top_level_keys_match": live_keys == saved_keys,
            "paths_added": len(added_paths),
            "paths_removed": len(missing_paths),
            "schemas_changed": 0,  # Can't detect without DeepDiff
        },
        "details": {
            "top_level_keys_diff": {
                "added": list(live_keys - saved_keys),
                "removed": list(saved_keys - live_keys),
            },
            "paths_diff": {
                "added": sorted(list(added_paths)),
                "removed": sorted(list(missing_paths)),
            }
        }
    }


def deep_compare(baseline: Dict, current: Dict) -> Dict[str, Any]:
    """
    Deep comparison using DeepDiff library.
    Provides comprehensive schema change detection.
    """
    if not DEEPDIFF_AVAILABLE:
        return basic_compare(baseline, current)

    diff = DeepDiff(
        baseline,
        current,
        ignore_order=True,
        report_repetition=True,
        view='tree'
    )

    # Extract meaningful changes
    paths_added = []
    paths_removed = []
    schemas_changed = []

    # Check for path changes
    if 'dictionary_item_added' in diff:
        for item in diff['dictionary_item_added']:
            path = str(item.path())
            if 'paths' in path:
                paths_added.append(path)

    if 'dictionary_item_removed' in diff:
        for item in diff['dictionary_item_removed']:
            path = str(item.path())
            if 'paths' in path:
                paths_removed.append(path)

    if 'values_changed' in diff:
        for item in diff['values_changed']:
            path = str(item.path())
            if 'schema' in path.lower() or 'properties' in path.lower():
                schemas_changed.append({
                    "path": path,
                    "old_value": str(item.t1),
                    "new_value": str(item.t2),
                })

    drift_detected = bool(diff)

    return {
        "drift_detected": drift_detected,
        "summary": {
            "paths_added": len(paths_added),
            "paths_removed": len(paths_removed),
            "schemas_changed": len(schemas_changed),
            "total_changes": len(diff) if hasattr(diff, '__len__') else 0,
        },
        "details": {
            "paths_added": paths_added,
            "paths_removed": paths_removed,
            "schemas_changed": schemas_changed[:10],  # Limit to first 10
            "raw_diff": diff.to_dict() if drift_detected else {},
        }
    }


def print_drift_report(result: Dict[str, Any], verbose: bool = False) -> None:
    """Print human-readable drift report."""
    summary = result.get("summary", {})
    details = result.get("details", {})

    if not result.get("drift_detected"):
        print("✅ No API drift detected - OpenAPI spec is stable")
        return

    print("🚨 API DRIFT DETECTED\n")
    print("=" * 60)

    print("\n📊 SUMMARY:")
    print(f"   Paths added:      {summary.get('paths_added', 0)}")
    print(f"   Paths removed:    {summary.get('paths_removed', 0)}")
    print(f"   Schemas changed:  {summary.get('schemas_changed', 0)}")

    if verbose:
        print("\n📋 DETAILS:\n")

        if details.get("paths_added"):
            print("  ➕ Added paths:")
            for path in details["paths_added"][:10]:
                print(f"     - {path}")

        if details.get("paths_removed"):
            print("\n  ➖ Removed paths:")
            for path in details["paths_removed"][:10]:
                print(f"     - {path}")

        if details.get("schemas_changed"):
            print("\n  🔄 Changed schemas:")
            for change in details["schemas_changed"][:5]:
                print(f"     - {change['path']}")

    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Detect OpenAPI specification drift"
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        default=Path("openapi.json"),
        help="Path to baseline OpenAPI spec (default: openapi.json)"
    )
    parser.add_argument(
        "--autofix",
        action="store_true",
        help="Automatically update the baseline spec with current version"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Save drift report to JSON file"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed drift information"
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI mode: exit with code 1 if drift detected"
    )

    args = parser.parse_args()

    # Load current spec from app
    print("Loading current OpenAPI spec from app...")
    current_spec = load_spec_from_app()

    # Load baseline spec
    print(f"Loading baseline spec from {args.baseline}...")
    baseline_spec = load_spec_from_file(args.baseline)

    if baseline_spec is None:
        print(f"⚠️  No baseline spec found at {args.baseline}")
        if args.autofix:
            print("Creating new baseline...")
            save_spec_to_file(current_spec, args.baseline)
            print("✅ Baseline created successfully")
            return 0
        else:
            print("Run with --autofix to create baseline")
            return 1

    # Compare specs
    print("Comparing specifications...\n")
    result = deep_compare(baseline_spec, current_spec)

    # Print report
    print_drift_report(result, verbose=args.verbose)

    # Save to file if requested
    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\n💾 Drift report saved to {args.output}")

    # Auto-fix if requested
    if args.autofix and result.get("drift_detected"):
        print(f"\n🔧 Updating baseline spec at {args.baseline}...")
        save_spec_to_file(current_spec, args.baseline)

    # Exit code for CI
    if args.ci and result.get("drift_detected"):
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
