#!/usr/bin/env python3
"""
GitHub Actions Security - Pinned Actions Verification
===================================================

Verifies that all GitHub Actions in workflows use SHA-pinned references
instead of tag references for security best practices.

Security Requirements:
- All actions must use SHA-pinned refs (e.g., @a1b2c3d instead of @v4)
- Maintains allowlist of approved actions
- Fails CI if unpinned or unauthorized actions detected

T4/0.01% Excellence: 100% action pinning for supply chain security

Usage:
    python scripts/verify_pinned_actions.py
    python scripts/verify_pinned_actions.py --fix  # Auto-pin to latest SHA
"""

import argparse
import logging
import re
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Set, Tuple
import requests
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Approved GitHub Actions allowlist
APPROVED_ACTIONS = {
    "actions/checkout": {
        "v4": "692973e3d937129bcbf40652eb9f2f61becf3332",  # v4.1.7
        "v3": "f43a0e5ff2bd294095638e18286ca9a3d1956744"   # v3.6.0
    },
    "actions/setup-python": {
        "v5": "82c7e631bb3cdc910f68e0081d67478d79c6982d",  # v5.1.0
        "v4": "65d7f2d534ac1bc67fcd62888c5f4f3d2cb2b236"   # v4.7.1
    },
    "actions/cache": {
        "v4": "0c45773b623bea8c8e75f6c82b208c3cf94ea4f9",  # v4.0.2
        "v3": "88522ab9f39a2ea568f7027eddc7d8d8bc9d59c8"   # v3.3.1
    },
    "actions/upload-artifact": {
        "v4": "65462800fd760344b1a7b4382951275a0abb4808",  # v4.3.3
        "v3": "a8a3f3ad30e3422c9c7b888a15615d19a852ae32"   # v3.1.3
    },
    "actions/download-artifact": {
        "v4": "c14a0b9e72d31fbb7b7f3466e2a4f96c6498a1b0",  # v4.1.7
        "v3": "9bc31d5ccc31df68ecc42ccf4149144866c47d8a"   # v3.0.2
    }
}

# Pattern to match GitHub Actions usage
ACTION_PATTERN = re.compile(r'uses:\s*([^@\s]+)@([^\s]+)')

def find_workflow_files(workflows_dir: Path) -> List[Path]:
    """Find all GitHub Actions workflow files."""
    workflow_files = []

    if workflows_dir.exists():
        for pattern in ["*.yml", "*.yaml"]:
            workflow_files.extend(workflows_dir.glob(pattern))

    return workflow_files

def parse_workflow_actions(workflow_file: Path) -> List[Tuple[str, str, int]]:
    """Parse GitHub Actions from workflow file."""
    actions = []

    try:
        with open(workflow_file, 'r') as f:
            content = f.read()

        for line_num, line in enumerate(content.split('\n'), 1):
            match = ACTION_PATTERN.search(line)
            if match:
                action_name = match.group(1)
                action_ref = match.group(2)
                actions.append((action_name, action_ref, line_num))

    except Exception as e:
        logger.error(f"Error parsing {workflow_file}: {e}")

    return actions

def is_sha_pinned(ref: str) -> bool:
    """Check if reference is SHA-pinned (40-character hex)."""
    return bool(re.match(r'^[a-f0-9]{40}$', ref))

def is_action_approved(action_name: str) -> bool:
    """Check if action is in approved allowlist."""
    return action_name in APPROVED_ACTIONS

def get_latest_sha_for_tag(action_name: str, tag: str) -> str:
    """Get latest SHA for a given tag from GitHub API."""
    try:
        # GitHub API to get tag info
        api_url = f"https://api.github.com/repos/{action_name}/git/refs/tags/{tag}"
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            return data['object']['sha']
        else:
            # Try getting from releases API
            api_url = f"https://api.github.com/repos/{action_name}/releases/tags/{tag}"
            response = requests.get(api_url)

            if response.status_code == 200:
                data = response.json()
                return data['target_commitish']

    except Exception as e:
        logger.warning(f"Could not fetch SHA for {action_name}@{tag}: {e}")

    return None

def verify_workflow_security(workflow_file: Path, fix_issues: bool = False) -> Dict[str, any]:
    """Verify security of actions in workflow file."""
    actions = parse_workflow_actions(workflow_file)

    results = {
        "file": str(workflow_file),
        "total_actions": len(actions),
        "pinned_actions": 0,
        "unpinned_actions": 0,
        "unauthorized_actions": 0,
        "issues": [],
        "fixed": []
    }

    content_modifications = []

    with open(workflow_file, 'r') as f:
        original_content = f.read()

    modified_content = original_content

    for action_name, action_ref, line_num in actions:
        issue = {
            "action": f"{action_name}@{action_ref}",
            "line": line_num,
            "type": None,
            "severity": "high"
        }

        # Check if action is approved
        if not is_action_approved(action_name):
            issue["type"] = "unauthorized_action"
            issue["message"] = f"Unauthorized action '{action_name}' not in approved allowlist"
            results["unauthorized_actions"] += 1
            results["issues"].append(issue)
            continue

        # Check if already SHA-pinned
        if is_sha_pinned(action_ref):
            results["pinned_actions"] += 1
            continue

        # Action is approved but not SHA-pinned
        issue["type"] = "unpinned_action"
        issue["message"] = f"Action '{action_name}' uses tag '{action_ref}' instead of SHA pin"
        results["unpinned_actions"] += 1
        results["issues"].append(issue)

        # Fix if requested
        if fix_issues:
            # Try to get SHA from allowlist first
            approved_sha = None
            if action_ref in APPROVED_ACTIONS[action_name]:
                approved_sha = APPROVED_ACTIONS[action_name][action_ref]
            else:
                # Try to fetch from GitHub API
                approved_sha = get_latest_sha_for_tag(action_name, action_ref)

            if approved_sha:
                old_uses = f"uses: {action_name}@{action_ref}"
                new_uses = f"uses: {action_name}@{approved_sha}  # {action_ref}"
                modified_content = modified_content.replace(old_uses, new_uses)

                results["fixed"].append({
                    "action": action_name,
                    "old_ref": action_ref,
                    "new_ref": approved_sha,
                    "line": line_num
                })

    # Write fixed content if modifications were made
    if fix_issues and modified_content != original_content:
        with open(workflow_file, 'w') as f:
            f.write(modified_content)
        logger.info(f"Fixed {len(results['fixed'])} actions in {workflow_file}")

    return results

def main():
    parser = argparse.ArgumentParser(description="Verify GitHub Actions security")
    parser.add_argument("--workflows-dir",
                       default=".github/workflows",
                       help="Directory containing workflow files")
    parser.add_argument("--fix",
                       action="store_true",
                       help="Automatically fix unpinned actions")
    parser.add_argument("--fail-on-issues",
                       action="store_true",
                       default=True,
                       help="Exit with error code if issues found")

    args = parser.parse_args()

    workflows_dir = Path(args.workflows_dir)

    if not workflows_dir.exists():
        logger.warning(f"Workflows directory {workflows_dir} does not exist")
        return 0

    workflow_files = find_workflow_files(workflows_dir)

    if not workflow_files:
        logger.warning(f"No workflow files found in {workflows_dir}")
        return 0

    logger.info(f"🔍 Verifying GitHub Actions security in {len(workflow_files)} workflow files")

    overall_results = {
        "total_files": len(workflow_files),
        "total_actions": 0,
        "total_pinned": 0,
        "total_unpinned": 0,
        "total_unauthorized": 0,
        "files_with_issues": 0,
        "all_issues": []
    }

    for workflow_file in workflow_files:
        logger.info(f"Checking {workflow_file.name}...")

        file_results = verify_workflow_security(workflow_file, args.fix)

        overall_results["total_actions"] += file_results["total_actions"]
        overall_results["total_pinned"] += file_results["pinned_actions"]
        overall_results["total_unpinned"] += file_results["unpinned_actions"]
        overall_results["total_unauthorized"] += file_results["unauthorized_actions"]
        overall_results["all_issues"].extend(file_results["issues"])

        if file_results["issues"]:
            overall_results["files_with_issues"] += 1

            logger.warning(f"  Issues in {workflow_file.name}:")
            for issue in file_results["issues"]:
                logger.warning(f"    Line {issue['line']}: {issue['message']}")

        if file_results["fixed"]:
            logger.info(f"  Fixed {len(file_results['fixed'])} actions in {workflow_file.name}")

    # Summary report
    print("\n" + "="*70)
    print("🛡️  GitHub Actions Security Report")
    print("="*70)
    print(f"Workflow files scanned: {overall_results['total_files']}")
    print(f"Actions found: {overall_results['total_actions']}")
    print(f"SHA-pinned actions: {overall_results['total_pinned']} ✅")
    print(f"Unpinned actions: {overall_results['total_unpinned']} {'⚠️' if overall_results['total_unpinned'] > 0 else '✅'}")
    print(f"Unauthorized actions: {overall_results['total_unauthorized']} {'❌' if overall_results['total_unauthorized'] > 0 else '✅'}")

    if overall_results["total_actions"] > 0:
        pinning_rate = (overall_results["total_pinned"] / overall_results["total_actions"]) * 100
        print(f"Action pinning rate: {pinning_rate:.1f}%")

    print("\n📋 Approved Actions Allowlist:")
    for action_name in APPROVED_ACTIONS:
        print(f"  ✓ {action_name}")

    if overall_results["all_issues"]:
        print(f"\n⚠️  Issues found in {overall_results['files_with_issues']} files:")
        for issue in overall_results["all_issues"]:
            print(f"  • {issue['action']} - {issue['message']}")

        if not args.fix:
            print("\n💡 Run with --fix to automatically pin actions to approved SHAs")
    else:
        print("\n🎯 All GitHub Actions are properly pinned and authorized!")

    # T4/0.01% excellence check
    if overall_results["total_unpinned"] == 0 and overall_results["total_unauthorized"] == 0:
        print("\n✅ T4/0.01% Excellence: GitHub Actions security requirements met")
        return 0
    else:
        if args.fail_on_issues:
            print("\n❌ GitHub Actions security issues detected - failing build")
            return 1
        else:
            return 0

if __name__ == "__main__":
    sys.exit(main())