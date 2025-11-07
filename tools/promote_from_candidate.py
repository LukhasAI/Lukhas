#!/usr/bin/env python3
"""
Promotion Executor - Reads promotion plan and executes git mv operations
"""

import json
import pathlib
import subprocess
import sys
from typing import Dict


def run_git_mv(source: str, target: str) -> bool:
    """Execute git mv command"""
    # Create target directory if needed
    target_path = pathlib.Path(target)
    target_dir = target_path.parent
    target_dir.mkdir(parents=True, exist_ok=True)

    try:
        subprocess.run(
            ["git", "mv", source, target],
            capture_output=True,
            text=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to move {source} → {target}")
        print(f"   Error: {e.stderr}")
        return False

def load_plan(plan_file: str) -> list[Dict]:
    """Load promotion plan from JSONL file"""
    plan = []
    with open(plan_file) as f:
        for line in f:
            if line.strip():
                plan.append(json.loads(line))
    return plan

def execute_promotions(plan: list[Dict], dry_run: bool = False) -> Dict:
    """Execute all promotions in the plan"""
    results = {
        "successful": [],
        "failed": [],
        "skipped": []
    }

    for item in plan:
        source = item.get("source")
        target = item.get("target")

        if not source or not target:
            print(f"⚠️  Skipping invalid entry: {item}")
            results["skipped"].append(item)
            continue

        # Check if source exists
        if not pathlib.Path(source).exists():
            print(f"⏭️  Source not found, skipping: {source}")
            results["skipped"].append(item)
            continue

        # Check if target already exists
        if pathlib.Path(target).exists():
            print(f"⏭️  Target already exists, skipping: {target}")
            results["skipped"].append(item)
            continue

        if dry_run:
            print(f"[DRY RUN] Would move: {source} → {target}")
            results["successful"].append(item)
        else:
            print(f"📦 Moving: {source} → {target}")
            if run_git_mv(source, target):
                results["successful"].append(item)
            else:
                results["failed"].append(item)

    return results

def write_summary(results: Dict, output_file: str):
    """Write promotion summary to JSON file"""
    summary = {
        "total": len(results["successful"]) + len(results["failed"]) + len(results["skipped"]),
        "successful": len(results["successful"]),
        "failed": len(results["failed"]),
        "skipped": len(results["skipped"]),
        "details": results
    }

    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2)

    return summary

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Execute promotion plan")
    parser.add_argument("--plan", default="artifacts/promotion_batch.plan.jsonl",
                      help="Path to promotion plan JSONL file")
    parser.add_argument("--dry-run", action="store_true",
                      help="Show what would be done without executing")
    parser.add_argument("--output", default="artifacts/promotion_batch.summary.json",
                      help="Path to output summary JSON")
    args = parser.parse_args()

    # Load plan
    try:
        plan = load_plan(args.plan)
        print(f"📋 Loaded {len(plan)} items from promotion plan")
    except FileNotFoundError:
        print(f"❌ Plan file not found: {args.plan}")
        return 1
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in plan file: {e}")
        return 1

    # Execute promotions
    results = execute_promotions(plan, dry_run=args.dry_run)

    # Write summary
    summary = write_summary(results, args.output)

    # Print results
    print("\n" + "="*50)
    print("📊 Promotion Summary:")
    print(f"  ✅ Successful: {summary['successful']}")
    print(f"  ❌ Failed: {summary['failed']}")
    print(f"  ⏭️  Skipped: {summary['skipped']}")
    print(f"  📋 Total: {summary['total']}")

    if results["failed"]:
        print("\n⚠️  Some promotions failed. Check the summary file for details.")
        return 1

    print(f"\n✅ Summary written to: {args.output}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
