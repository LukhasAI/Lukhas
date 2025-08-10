#!/usr/bin/env python3
"""
Show unused files organized by category
"""

import json
from collections import defaultdict
from pathlib import Path


def main():
    # Load the unused files report
    report_path = Path(__file__).parent / "unused_files_report.json"
    with open(report_path) as f:
        data = json.load(f)

    # Organize by category
    categories = defaultdict(list)
    for file_info in data["unused_files"]:
        path = file_info["path"]
        parts = path.split("/")

        # Determine category
        if len(parts) > 0:
            top_dir = parts[0]
            if top_dir in [
                "bio",
                "consciousness",
                "memory",
                "quantum",
                "safety",
                "ethics",
                "orchestration",
            ]:
                category = f"System: {top_dir}"
            elif top_dir == "core":
                if len(parts) > 1:
                    category = f"Core: {parts[1]}"
                else:
                    category = "Core: root"
            elif top_dir == "tools":
                category = "Tools"
            elif top_dir == "features":
                category = "Features"
            elif top_dir == "api":
                category = "API"
            elif top_dir == "tests" or "test" in path:
                category = "Tests"
            elif top_dir == "docs":
                category = "Documentation"
            elif top_dir == "examples" or "example" in path:
                category = "Examples"
            elif top_dir == "scripts":
                category = "Scripts"
            else:
                category = "Other"
        else:
            category = "Root"

        categories[category].append(file_info)

    # Sort categories by number of unused files
    sorted_categories = sorted(
        categories.items(), key=lambda x: len(x[1]), reverse=True
    )

    print("=" * 80)
    print("UNUSED FILES BY CATEGORY")
    print("=" * 80)
    print(f"Total unused files: {len(data['unused_files'])}")
    print()

    # Show summary
    print("SUMMARY BY CATEGORY:")
    print("-" * 40)
    for category, files in sorted_categories:
        print(f"{category}: {len(files)} files")
    print()

    # Show details for each category
    for category, files in sorted_categories[:10]:  # Top 10 categories
        print(f"\n{'='*60}")
        print(f"{category} ({len(files)} unused files)")
        print("=" * 60)

        # Sort by size
        sorted_files = sorted(files, key=lambda x: x["size_bytes"], reverse=True)

        # Show top 10 largest unused files in this category
        for i, file_info in enumerate(sorted_files[:10]):
            print(f"{i+1}. {file_info['path']}")
            print(f"   Size: {file_info['size_human']}")

    # Show some specific interesting unused files
    print("\n" + "=" * 80)
    print("NOTABLE UNUSED FILES:")
    print("=" * 80)

    notable_patterns = {
        "Hubs": lambda p: "hub" in p.lower() and "github" not in p.lower(),
        "Bridges": lambda p: "bridge" in p.lower(),
        "Orchestrators": lambda p: "orchestrator" in p.lower(),
        "Engines": lambda p: "engine" in p.lower(),
        "Managers": lambda p: "manager" in p.lower(),
        "Core Systems": lambda p: p.startswith("core/")
        and any(x in p for x in ["system", "core", "main"]),
        "API Endpoints": lambda p: p.startswith("api/"),
        "LUKHAS Identity": lambda p: "lukhas" in p.lower() or "identity" in p.lower(),
        "Golden Trio": lambda p: any(x in p.lower() for x in ["dast", "abas", "nias"]),
    }

    for pattern_name, pattern_func in notable_patterns.items():
        matching_files = [f for f in data["unused_files"] if pattern_func(f["path"])]
        if matching_files:
            print(f"\n{pattern_name} ({len(matching_files)} files):")
            for f in matching_files[:5]:
                print(f"  - {f['path']} ({f['size_human']})")


if __name__ == "__main__":
    main()
