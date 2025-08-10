#!/usr/bin/env python3
"""
Analyze overlap between core/ modules and root directories to identify consolidation opportunities.
"""

import json
import os
from collections import defaultdict
from pathlib import Path


def analyze_core_modules(repo_path):
    """Analyze core modules and categorize them by domain."""

    core_path = Path(repo_path) / "core"
    root_dirs = set()
    core_modules = defaultdict(list)

    # Get all root directories
    for item in Path(repo_path).iterdir():
        if item.is_dir() and not item.name.startswith(".") and item.name != "core":
            root_dirs.add(item.name)

    # Categorize core modules by keywords
    keyword_mapping = {
        "quantum": ["quantum", "q_", "qubit"],
        "brain": ["brain", "neural", "neuro", "oscillator"],
        "consciousness": ["conscious", "awareness", "cognitive", "meta_cognitive"],
        "bridge": ["bridge", "integration", "fusion", "adapter", "wrapper"],
        "memory": ["memory", "cache", "storage", "recall"],
        "dream": ["dream", "oneiric", "sleep"],
        "emotion": ["emotion", "affect", "mood", "feeling"],
        "learning": ["learning", "learn", "meta_learn", "adaptive"],
        "creativity": ["creative", "creation", "imagination"],
        "ethics": ["ethics", "governance", "safety", "trust"],
        "reasoning": ["reasoning", "logic", "inference"],
        "bio": ["bio", "biological", "organism"],
    }

    # Walk through core directory
    for root, dirs, files in os.walk(core_path):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                file_path = Path(root) / file
                relative_path = file_path.relative_to(core_path)

                # Check which category this file belongs to
                categorized = False
                for category, keywords in keyword_mapping.items():
                    for keyword in keywords:
                        if keyword in str(relative_path).lower():
                            core_modules[category].append(str(relative_path))
                            categorized = True
                            break
                    if categorized:
                        break

                if not categorized:
                    core_modules["uncategorized"].append(str(relative_path))

    return core_modules, root_dirs


def generate_report(core_modules, root_dirs):
    """Generate a consolidation report."""

    report = []
    report.append("# Core Module Analysis Report\n")
    report.append(f"## Root Directories Found: {len(root_dirs)}\n")
    report.append(", ".join(sorted(root_dirs)))
    report.append("\n")

    report.append("## Core Modules by Category\n")

    total_modules = sum(len(modules) for modules in core_modules.values())
    report.append(f"Total Python modules in core/: {total_modules}\n")

    for category, modules in sorted(core_modules.items()):
        if modules:
            report.append(f"\n### {category.title()} ({len(modules)} modules)")

            # Check if corresponding root directory exists
            if category in root_dirs:
                report.append(f"✓ Root directory `{category}/` exists")
            else:
                report.append(f"✗ No `{category}/` root directory")

            report.append("\nModules:")
            for module in sorted(modules)[:10]:  # Show first 10
                report.append(f"- `{module}`")

            if len(modules) > 10:
                report.append(f"... and {len(modules) - 10} more")

    # Consolidation recommendations
    report.append("\n## Consolidation Recommendations\n")

    for category, modules in sorted(core_modules.items()):
        if modules and category != "uncategorized":
            if category in root_dirs:
                report.append(
                    f"- **{category}**: Move {len(modules)} modules to existing `{category}/` directory"
                )
            else:
                if category == "bio":
                    report.append(
                        f"- **{category}**: Distribute {len(modules)} bio-related modules across brain/, consciousness/, etc."
                    )
                else:
                    report.append(
                        f"- **{category}**: Consider creating `{category}/` directory for {len(modules)} modules"
                    )

    return "\n".join(report)


def main():
    repo_path = "/Users/agi_dev/Downloads/Consolidation-Repo"

    print("Analyzing core modules...")
    core_modules, root_dirs = analyze_core_modules(repo_path)

    print("\nGenerating report...")
    report = generate_report(core_modules, root_dirs)

    # Save report
    report_path = Path(repo_path) / "core_analysis_report.md"
    with open(report_path, "w") as f:
        f.write(report)

    print(f"\nReport saved to: {report_path}")

    # Also save JSON data for further processing
    data = {
        "root_directories": sorted(list(root_dirs)),
        "core_modules": {k: v for k, v in core_modules.items()},
        "total_modules": sum(len(modules) for modules in core_modules.values()),
    }

    json_path = Path(repo_path) / "core_analysis_data.json"
    with open(json_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"JSON data saved to: {json_path}")


if __name__ == "__main__":
    main()

# CLAUDE_EDIT_v0.1
