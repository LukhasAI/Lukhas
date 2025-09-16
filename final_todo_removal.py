#!/usr/bin/env python3
"""
Final TODO Removal - Conservative approach for safe cleanup
"""

import re
import subprocess
import json
from pathlib import Path
from datetime import datetime


def final_todo_removal():
    """Conservative TODO removal focusing on confirmed safe patterns"""

    print("🎯 FINAL TODO REMOVAL - CONSERVATIVE APPROACH")
    print("=" * 60)

    # Start with the most conservative, confirmed safe patterns
    safe_patterns = {
        "streamlit_stubs": {
            "pattern": r".*#\s*TODO:\s*Install or implement streamlit\s*\n",
            "description": "Streamlit installation stubs",
        },
        "consolidation_stubs": {
            "pattern": r".*#\s*TODO:\s*Implement actual consolidation logic\s*\n",
            "description": "Consolidation logic stubs",
        },
    }

    # Track results
    results = {
        "timestamp": datetime.now().isoformat(),
        "files_processed": [],
        "total_removals": 0,
        "removals_by_type": {},
    }

    # Process each pattern type
    for pattern_name, config in safe_patterns.items():
        print(f"\n🔍 Processing: {config['description']}")

        # Find files with this pattern
        try:
            cmd = ["git", "grep", "-l", config["pattern"].replace(".*", "").replace("\\s*", " ").replace("\\n", "")]
            search_term = (
                "TODO: Install or implement streamlit"
                if "streamlit" in config["pattern"]
                else "TODO: Implement actual consolidation logic"
            )

            result = subprocess.run(["git", "grep", "-l", search_term], capture_output=True, text=True)

            if result.returncode == 0:
                files = [f.strip() for f in result.stdout.split("\n") if f.strip() and f.endswith(".py")]
                print(f"  📁 Found {len(files)} files")

                removals = 0
                for file_path_str in files:
                    file_path = Path(file_path_str)

                    if not file_path.exists():
                        continue

                    # Process file
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()

                        # Find and remove matches
                        matches = list(re.finditer(config["pattern"], content, re.MULTILINE))

                        if matches:
                            # Create backup
                            backup_path = file_path.with_suffix(file_path.suffix + ".cleanup_backup")
                            with open(backup_path, "w", encoding="utf-8") as f:
                                f.write(content)

                            # Remove matches (reverse order)
                            new_content = content
                            file_removals = 0
                            for match in reversed(matches):
                                line = match.group(0)
                                if (
                                    pattern_name == "streamlit_stubs"
                                    and "install or implement streamlit" in line.lower()
                                ):
                                    new_content = new_content[: match.start()] + new_content[match.end() :]
                                    file_removals += 1
                                elif (
                                    pattern_name == "consolidation_stubs"
                                    and "implement actual consolidation logic" in line.lower()
                                ):
                                    new_content = new_content[: match.start()] + new_content[match.end() :]
                                    file_removals += 1

                            if file_removals > 0:
                                with open(file_path, "w", encoding="utf-8") as f:
                                    f.write(new_content)

                                print(f"    ✂️  {file_path}: {file_removals} removals")
                                removals += file_removals
                                results["files_processed"].append(str(file_path))

                    except Exception as e:
                        print(f"    ❌ Error processing {file_path}: {e}")

                results["removals_by_type"][pattern_name] = removals
                results["total_removals"] += removals
                print(f"  ✅ Total {pattern_name}: {removals} removals")

            else:
                print(f"  ℹ️  No files found for {pattern_name}")
                results["removals_by_type"][pattern_name] = 0

        except Exception as e:
            print(f"  ❌ Error with {pattern_name}: {e}")
            results["removals_by_type"][pattern_name] = 0

    # Save results
    results_file = Path("TODO_REMOVAL_RESULTS.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    # Print final summary
    print("\n" + "=" * 60)
    print("📊 FINAL REMOVAL SUMMARY")
    print("=" * 60)
    print(f"Total files processed: {len(set(results['files_processed']))}")
    print(f"Total removals: {results['total_removals']}")
    print(f"Results saved to: {results_file}")

    for pattern_name, count in results["removals_by_type"].items():
        description = safe_patterns[pattern_name]["description"]
        print(f"  {pattern_name}: {count} ({description})")

    print("\n🔍 Verify changes with:")
    print("  git status")
    print("  git diff")
    print("  python -m py_compile <modified_file>")

    return results


if __name__ == "__main__":
    final_todo_removal()
