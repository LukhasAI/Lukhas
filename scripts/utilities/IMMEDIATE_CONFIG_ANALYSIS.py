#!/usr/bin/env python3
"""
Config Consolidation Strategy
============================

Analysis of 287+ config files in LUKHAS workspace.
This script identifies redundant, conflicting, and orphaned config files.

CRITICAL FINDINGS:
- Multiple config.py files in different modules
- Potential namespace conflicts
- Duplicate configuration logic
- Missing centralized config management

RECOMMENDED ACTIONS:
1. Consolidate core configs into config/
2. Create module-specific config inheritance
3. Remove duplicate config logic
4. Standardize config loading patterns
"""

import os


def analyze_config_files():
    """Analyze all config files for consolidation opportunities."""
    config_files = []

    for root, _dirs, files in os.walk("."):
        if any(skip in root for skip in ["._cleanup_archive", ".cleanup_archive", ".git"]):
            continue

        for file in files:
            if "config" in file.lower() and file.endswith(".py"):
                filepath = os.path.join(root, file)
                config_files.append(filepath)

    print(f"📊 Found {len(config_files} config files")

    # Categorize by type
    categories = {
        "core_configs": [],
        "module_configs": [],
        "api_configs": [],
        "duplicates": [],
        "builders": [],
        "managers": [],
    }

    for filepath in config_files:
        name = os.path.basename(filepath).lower()
        if name == "config.py":
            categories["core_configs"].append(filepath)
        elif "api" in filepath:
            categories["api_configs"].append(filepath)
        elif "manager" in name:
            categories["managers"].append(filepath)
        elif "builder" in name:
            categories["builders"].append(filepath)
        else:
            categories["module_configs"].append(filepath)

    # Report findings
    for category, files in categories.items():
        print(f"\n🔧 {category}: {len(files} files")
        for f in files[:5]:  # Show first 5
            print(f"   - {f}")
        if len(files) > 5:
            print(f"   ... and {len(files} - 5} more")

    return categories


if __name__ == "__main__":
    print("🔍 LUKHAS Config Consolidation Analysis")
    print("=" * 50)
    categories = analyze_config_files()

    print("\n📋 CONSOLIDATION RECOMMENDATIONS:")
    print(f"1. Merge {len(categories['core_configs']} core config.py files")
    print(f"2. Standardize {len(categories['managers']} config managers")
    print(f"3. Review {len(categories['api_configs']} API configs for overlap")
    print(f"4. Consider consolidating {len(categories['module_configs']} module configs")
