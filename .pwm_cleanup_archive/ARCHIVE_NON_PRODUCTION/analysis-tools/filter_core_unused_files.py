#!/usr/bin/env python3
"""
Filter unused files to show only core system/AGI/AI logic files
Excludes: tests, demos, benchmarks, examples, docs, etc.
"""

import json
import re
from pathlib import Path
from typing import Any, Dict

# Patterns to EXCLUDE (obvious non-core files)
EXCLUDE_PATTERNS = [
    # Test related
    r"test[s]?[_/]",
    r"_test\.py$",
    r"test_.*\.py$",
    r".*_test\.py$",
    r"spec[s]?[_/]",
    r"_spec\.py$",
    # Demo/Example related
    r"demo[s]?[_/]",
    r"_demo\.py$",
    r"example[s]?[_/]",
    r"_example\.py$",
    r"sample[s]?[_/]",
    r"tutorial[s]?[_/]",
    # Benchmark/Performance
    r"benchmark[s]?[_/]",
    r"_benchmark\.py$",
    r"perf[_/]",
    r"performance[_/]",
    # Documentation
    r"doc[s]?[_/]",
    r"\.md$",
    r"\.rst$",
    r"\.txt$",
    r"README",
    r"CHANGELOG",
    r"LICENSE",
    # Development tools
    r"tool[s]?[_/]",
    r"script[s]?[_/]",
    r"util[s]?[_/]",
    r"helper[s]?[_/]",
    r"debug[_/]",
    r"dev[_/]",
    r"\.sh$",
    # Config/Setup
    r"config[_/]",
    r"\.json$",
    r"\.yaml$",
    r"\.yml$",
    r"\.toml$",
    r"\.ini$",
    r"\.cfg$",
    r"setup\.py$",
    r"__pycache__",
    r"\.pyc$",
    # Frontend/UI
    r"\.html$",
    r"\.css$",
    r"\.js$",
    r"\.tsx?$",
    r"\.jsx?$",
    r"frontend[_/]",
    r"ui[_/]",
    r"static[_/]",
    r"template[s]?[_/]",
    # Notebooks/Analysis
    r"\.ipynb$",
    r"notebook[s]?[_/]",
    r"analysis[_/]",
    # Other non-core
    r"migration[s]?[_/]",
    r"backup[s]?[_/]",
    r"archive[s]?[_/]",
    r"old[_/]",
    r"deprecated[_/]",
    r"legacy[_/]",
    r"tmp[_/]",
    r"temp[_/]",
    r"\.git",
    r"node_modules",
    r"venv[_/]",
    r"env[_/]",
    r"\.env",
    r"Dockerfile",
    r"docker-compose",
    r"Makefile",
    r"requirements\.txt",
    r"package\.json",
]

# Patterns to INCLUDE (core system files we want to keep)
INCLUDE_PATTERNS = [
    r"core/",
    r"memory/",
    r"consciousness/",
    r"quantum/",
    r"learning/",
    r"bio/",
    r"ethics/",
    r"identity/",
    r"safety/",
    r"orchestration/",
    r"dast/",
    r"abas/",
    r"nias/",
    r"symbolic/",
    r"dream/",
    r"seedra/",
    r"bridge[s]?/",
    r"hub[s]?/",
    r"engine[s]?/",
    r"processor[s]?/",
    r"manager[s]?/",
    r"handler[s]?/",
    r"service[s]?/",
    r"agent[s]?/",
    r"model[s]?/",
    r"algorithm[s]?/",
    r"neural",
    r"ai[_/]",
    r"ml[_/]",
    r"intelligence",
]


def should_exclude(file_path: str) -> bool:
    """Check if file should be excluded based on patterns"""
    file_path_lower = file_path.lower()

    # Check exclude patterns
    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, file_path_lower):
            return True

    return False


def is_core_system_file(file_path: str) -> bool:
    """Check if file is likely a core system/AGI/AI file"""
    file_path_lower = file_path.lower()

    # Check if it matches any include pattern
    for pattern in INCLUDE_PATTERNS:
        if re.search(pattern, file_path_lower):
            return True

    # Check file name indicators
    core_indicators = [
        "hub",
        "bridge",
        "engine",
        "processor",
        "manager",
        "handler",
        "service",
        "agent",
        "model",
        "algorithm",
        "neural",
        "quantum",
        "consciousness",
        "memory",
        "learning",
        "ethics",
        "identity",
        "orchestrat",
    ]

    file_name = Path(file_path).name.lower()
    for indicator in core_indicators:
        if indicator in file_name:
            return True

    return False


def filter_core_unused_files(
    input_file: str = "unused_files_report.json",
) -> Dict[str, Any]:
    """Filter unused files to show only core system files"""

    with open(input_file) as f:
        data = json.load(f)

    all_unused = data.get("unused_files", [])
    core_unused = []
    excluded_count = 0

    # Category counters
    categories = {
        "dast": [],
        "abas": [],
        "nias": [],
        "core": [],
        "orchestration": [],
        "memory": [],
        "consciousness": [],
        "quantum": [],
        "learning": [],
        "bio": [],
        "ethics": [],
        "identity": [],
        "safety": [],
        "bridges": [],
        "other_system": [],
    }

    for file_info in all_unused:
        file_path = file_info["path"]

        # Skip if matches exclude pattern
        if should_exclude(file_path):
            excluded_count += 1
            continue

        # Check if it's a core system file
        if not is_core_system_file(file_path):
            excluded_count += 1
            continue

        # Categorize the file
        file_path_lower = file_path.lower()
        categorized = False

        for category in categories:
            if category in file_path_lower:
                categories[category].append(file_info)
                categorized = True
                break

        if not categorized:
            if "bridge" in file_path_lower:
                categories["bridges"].append(file_info)
            else:
                categories["other_system"].append(file_info)

        core_unused.append(file_info)

    # Calculate statistics
    total_size = sum(f["size_bytes"] for f in core_unused)
    size_by_category = {}
    for cat, files in categories.items():
        if files:
            size_by_category[cat] = {
                "count": len(files),
                "total_size": sum(f["size_bytes"] for f in files),
                "files": files,
            }

    return {
        "total_unused": len(all_unused),
        "core_unused": len(core_unused),
        "excluded": excluded_count,
        "core_files": core_unused,
        "total_size_bytes": total_size,
        "total_size_human": f"{total_size / 1024 / 1024:.1f} MB",
        "categories": size_by_category,
    }


def main():
    """Main function"""
    print("Filtering unused files to show only core system/AGI/AI logic files...")

    result = filter_core_unused_files()

    # Save filtered results
    with open("core_unused_files.json", "w") as f:
        json.dump(result, f, indent=2)

    # Print summary
    print("\n📊 Filtering Summary:")
    print(f"Total unused files: {result['total_unused']}")
    print(f"Excluded (tests/demos/docs/etc): {result['excluded']}")
    print(f"Core system files remaining: {result['core_unused']}")
    print(f"Total size of core unused: {result['total_size_human']}")

    print("\n📂 Core Unused Files by Category:")
    for category, info in sorted(
        result["categories"].items(), key=lambda x: x[1]["count"], reverse=True
    ):
        count = info["count"]
        size_mb = info["total_size"] / 1024 / 1024
        print(f"  {category:15} {count:4} files ({size_mb:6.1f} MB)")

    # Print top 20 largest core unused files
    print("\n📋 Top 20 Largest Core Unused Files:")
    sorted_files = sorted(
        result["core_files"], key=lambda x: x["size_bytes"], reverse=True
    )[:20]

    for i, file_info in enumerate(sorted_files, 1):
        print(f"{i:2}. {file_info['size_human']:>8} {file_info['path']}")

    # Save a simple text list
    with open("core_unused_files_list.txt", "w") as f:
        f.write(f"# Core Unused Files ({result['core_unused']} files)\n")
        f.write(f"# Filtered from {result['total_unused']} total unused files\n\n")

        for category, info in sorted(result["categories"].items()):
            if info["count"] > 0:
                f.write(f"\n## {category.upper()} ({info['count']} files)\n")
                for file_info in sorted(info["files"], key=lambda x: x["path"]):
                    f.write(f"{file_info['path']}\n")

    print("\n✅ Results saved to:")
    print("   - core_unused_files.json (detailed with sizes)")
    print("   - core_unused_files_list.txt (simple list by category)")


if __name__ == "__main__":
    main()
