#!/usr/bin/env python3
"""
GitHub Actions SHA Pinning Tool

Automatically converts action tag references to SHA references for security.

Usage:
    python tools/security/pin_github_actions.py --check
    python tools/security/pin_github_actions.py --update
"""

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Known action SHA mappings (as of Sep 2024)
ACTION_SHA_MAP = {
    "actions/checkout@v4": "actions/checkout@692973e3d937129bcbf40652eb9f2f61becf3332",  # v4.1.7
    "actions/checkout@v3": "actions/checkout@f43a0e5ff2bd294095638e18286ca9a3d1956744",  # v3.6.0
    "actions/setup-python@v5": "actions/setup-python@82c7e631bb3cdc910f68e0081d67478d79c6982d",  # v5.1.0
    "actions/setup-python@v6": "actions/setup-python@39cd14951b08e74b54015e9e001cdefcf80e669f",  # v6.1.7
    "actions/setup-node@v4": "actions/setup-node@1e60f620b9541d16bece96c5465dc8ee9832be0b",  # v4.0.3
    "actions/upload-artifact@v4": "actions/upload-artifact@834a144ee995460fba8ed112a2fc961b36a5ec5a",  # v4.3.6
    "actions/download-artifact@v4": "actions/download-artifact@fa0a91b85d4f404e444e00e005971372dc801d16",  # v4.1.8
    "actions/cache@v4": "actions/cache@0c45773b623bea8c8e75f6c82b208c3cf94ea4f9",  # v4.0.2
    "github/codeql-action/init@v3": "github/codeql-action/init@4fa2a7953630fd2f3fb380f21be14ede0169dd4f",  # v3.25.12
    "github/codeql-action/analyze@v3": "github/codeql-action/analyze@4fa2a7953630fd2f3fb380f21be14ede0169dd4f",  # v3.25.12
}


def find_workflow_files() -> List[Path]:
    """Find all GitHub workflow files"""
    workflows_dir = Path(".github/workflows")
    if not workflows_dir.exists():
        return []

    return list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))


def analyze_workflow_file(filepath: Path) -> List[Tuple[str, str, int]]:
    """Analyze a workflow file for action references that need pinning"""
    issues = []

    try:
        with open(filepath) as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, 1):
            # Look for 'uses:' lines with tag references
            match = re.search(r'uses:\s*([^@\s]+@[^@\s]+)', line.strip())
            if match:
                action_ref = match.group(1)
                # Check if it's using a tag (not a SHA)
                if not re.match(r'.*@[a-f0-9]{40}', action_ref):
                    issues.append((action_ref, line.strip(), line_num))

    except Exception as e:
        print(f"Error reading {filepath}: {e}")

    return issues


def update_workflow_file(filepath: Path, dry_run: bool = True) -> bool:
    """Update a workflow file to use SHA references"""
    try:
        with open(filepath) as f:
            content = f.read()

        updates_made = 0

        # Replace known action references
        for tag_ref, sha_ref in ACTION_SHA_MAP.items():
            if tag_ref in content:
                content = content.replace(f"uses: {tag_ref}", f"uses: {sha_ref}")
                updates_made += 1
                print(f"   🔄 {tag_ref} → {sha_ref}")

        if updates_made > 0 and not dry_run:
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"   ✅ Updated {filepath} ({updates_made} actions)")
            return True
        elif updates_made > 0:
            print(f"   📝 Would update {filepath} ({updates_made} actions)")

    except Exception as e:
        print(f"❌ Error updating {filepath}: {e}")

    return False


def check_workflows() -> Dict[str, List]:
    """Check all workflows for unpinned actions"""
    print("🔍 Scanning GitHub workflows for unpinned actions...")

    workflow_files = find_workflow_files()
    print(f"Found {len(workflow_files)} workflow files")

    all_issues = {}
    total_issues = 0

    for filepath in workflow_files:
        issues = analyze_workflow_file(filepath)
        if issues:
            all_issues[str(filepath)] = issues
            total_issues += len(issues)

    print(f"\n📊 Found {total_issues} unpinned action references across {len(all_issues)} files")

    if all_issues:
        print("\n🔍 Unpinned Actions Found:")
        for filepath, issues in all_issues.items():
            print(f"\n{filepath}:")
            for action_ref, line, line_num in issues:
                status = "🔄 CAN PIN" if action_ref in ACTION_SHA_MAP else "⚠️ UNKNOWN"
                print(f"   Line {line_num}: {action_ref} {status}")

    return all_issues


def update_workflows(dry_run: bool = True) -> None:
    """Update all workflows to use SHA references"""
    action = "Would update" if dry_run else "Updating"
    print(f"🔧 {action} GitHub workflows to use SHA references...")

    workflow_files = find_workflow_files()
    updated_count = 0

    for filepath in workflow_files:
        print(f"\n📄 Processing {filepath}...")
        if update_workflow_file(filepath, dry_run):
            updated_count += 1

    print(f"\n📊 {action.lower()} {updated_count} workflow files")

    if not dry_run:
        print("\n✅ SHA pinning complete!")
        print("💡 Consider setting up Dependabot to keep actions updated:")
        print("   https://docs.github.com/en/code-security/dependabot/working-with-dependabot/keeping-your-actions-up-to-date-with-dependabot")


def main():
    parser = argparse.ArgumentParser(description="Pin GitHub Actions to SHA references")
    parser.add_argument("--check", action="store_true", help="Check for unpinned actions")
    parser.add_argument("--update", action="store_true", help="Update actions to use SHA references")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Show what would be updated (default)")
    parser.add_argument("--execute", action="store_true", help="Actually perform updates")

    args = parser.parse_args()

    if args.check:
        issues = check_workflows()
        if issues:
            print("\n💡 Run with --update to pin known actions to SHA references")
            exit(1)
        else:
            print("✅ All actions are properly pinned!")

    elif args.update:
        dry_run = not args.execute
        update_workflows(dry_run)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
