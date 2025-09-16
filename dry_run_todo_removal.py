#!/usr/bin/env python3
"""
LUKHAS TODO Removal Dry Run
Shows exactly what would be removed without making changes.
"""

import re
import subprocess
from pathlib import Path


def dry_run_removal():
    """Dry run to show what would be removed"""

    # Define patterns (same as main script)
    patterns = {
        "completion_references": {
            "patterns": [
                r".*[Aa]ddresses TODO \d+.*\n",
                r".*[Ii]mplements TODO \d+.*\n",
                r".*[Cc]ompletes TODO \d+.*\n",
                r".*[Ff]ixes TODO \d+.*\n",
                r".*[Rr]esolves TODO \d+.*\n",
                r".*TODO \d+:.*implemented.*\n",
                r".*TODO \d+:.*completed.*\n",
                r".*TODO \d+ is now.*\n",
            ],
            "safety_check": lambda line: "address" in line.lower()
            or "implement" in line.lower()
            or "complete" in line.lower(),
            "description": "References to completed TODOs",
        },
        "symbol_resolver_duplicates": {
            "patterns": [
                r"^[\s]*#?\s*TODO\(symbol-resolver\):\s*implement missing functionality\s*\n",
                r"^[\s]*\/\/?\s*TODO\(symbol-resolver\):\s*implement missing functionality\s*\n",
            ],
            "safety_check": lambda line: "symbol-resolver" in line and "implement missing functionality" in line,
            "description": "Symbol resolver implementation stubs",
        },
        "streamlit_stubs": {
            "patterns": [
                r"^[\s]*#\s*TODO:\s*Install or implement streamlit\s*\n",
                r"^[\s]*\/\/?\s*TODO:\s*Install or implement streamlit\s*\n",
            ],
            "safety_check": lambda line: "install or implement streamlit" in line.lower(),
            "description": "Streamlit installation stubs",
        },
        "consolidation_stubs": {
            "patterns": [
                r"^[\s]*#?\s*TODO:\s*Implement actual consolidation logic\s*\n",
                r"^[\s]*\/\/?\s*TODO:\s*Implement actual consolidation logic\s*\n",
            ],
            "safety_check": lambda line: "implement actual consolidation logic" in line.lower(),
            "description": "Consolidation logic stubs",
        },
        "placeholder_stubs": {
            "patterns": [r"^[\s]*pass\s*#\s*TODO.*\n", r"^[\s]*pass\s*#.*TODO.*\n"],
            "safety_check": lambda line: "pass" in line and "TODO" in line,
            "description": "Pass statement TODO stubs",
        },
        "dependency_stubs": {
            "patterns": [r"^[\s]*#\s*TODO:\s*Install or implement \w+\s*\n", r"^[\s]*#\s*TODO:\s*Install \w+\s*\n"],
            "safety_check": lambda line: "TODO:" in line and ("install" in line.lower() or "implement" in line.lower()),
            "description": "Dependency installation stubs",
        },
    }

    print("🔍 DRY RUN: TODO Removal Analysis")
    print("=" * 60)

    # Focus on Python files to start with
    try:
        result = subprocess.run(
            ["find", ".", "-name", "*.py", "-not", "-path", "./.git/*", "-not", "-path", "./.venv/*"],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print("❌ Error finding Python files")
            return

        python_files = [Path(line.strip()) for line in result.stdout.split("\n") if line.strip()]
        print(f"📂 Found {len(python_files)} Python files")

    except Exception as e:
        print(f"❌ Error: {e}")
        return

    total_removals = {}
    files_with_removals = {}

    # Process each file
    for file_path in python_files[:50]:  # Limit to first 50 for dry run
        if not file_path.exists():
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            file_removals = {}

            # Check each pattern
            for category, config in patterns.items():
                for pattern in config["patterns"]:
                    matches = list(re.finditer(pattern, content, re.MULTILINE))

                    # Safety check
                    safe_matches = []
                    for match in matches:
                        line = match.group(0)
                        if config["safety_check"](line):
                            safe_matches.append(match)

                    if safe_matches:
                        if category not in file_removals:
                            file_removals[category] = []
                        file_removals[category].extend([m.group(0).strip() for m in safe_matches])

            if file_removals:
                files_with_removals[str(file_path)] = file_removals

                for category, lines in file_removals.items():
                    if category not in total_removals:
                        total_removals[category] = 0
                    total_removals[category] += len(lines)

        except Exception as e:
            print(f"⚠️ Error processing {file_path}: {e}")

    # Print results
    print(f"\n📊 DRY RUN RESULTS (first 50 Python files)")
    print("=" * 60)

    if not total_removals:
        print("✅ No removals would be made in the sampled files")
        return

    print("📈 Total removals by category:")
    for category, count in total_removals.items():
        description = patterns[category]["description"]
        print(f"  {category}: {count} lines ({description})")

    print(f"\n📁 Files that would be modified: {len(files_with_removals)}")

    # Show examples
    print("\n🔍 Examples of what would be removed:")
    for file_path, file_removals in list(files_with_removals.items())[:5]:
        print(f"\n📄 {file_path}:")
        for category, lines in file_removals.items():
            print(f"  {category}:")
            for line in lines[:3]:  # Show first 3 examples
                print(f"    - {line}")
            if len(lines) > 3:
                print(f"    ... and {len(lines) - 3} more")

    print("\n" + "=" * 60)
    print("✅ Dry run completed - these are examples from first 50 Python files")
    print("🔄 To proceed with full removal, use the main script")


if __name__ == "__main__":
    dry_run_removal()
