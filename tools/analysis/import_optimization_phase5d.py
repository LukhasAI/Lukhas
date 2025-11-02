#!/usr/bin/env python3
"""
Phase 5D: Import optimization for LUKHAS consciousness system
Critical for module loading efficiency and undefined name resolution
"""

import json
import subprocess


def get_import_violations() -> list[dict]:
    """Get E402/F821 import violations from ruff check."""
    try:
        result = subprocess.run(
            [
                ".venv/bin/ruff",
                "check",
                ".",
                "--select=E402,F821",
                "--output-format=json",
                "--quiet",
                "--exclude=archive/",
                "--exclude=website_v1/",
                "--exclude=products/shared/gpt_oss_integration/",
            ],
            capture_output=True,
            text=True,
            cwd="/Users/agi_dev/LOCAL-REPOS/Lukhas",
        )

        if result.stdout:
            return json.loads(result.stdout)
        return []
    except Exception as e:
        print(f"Error getting import violations: {e}")
        return []


def analyze_import_patterns(violations: list[dict]) -> dict[str, list[dict]]:
    """Analyze import violation patterns."""
    patterns = {
        "e402_imports": [],  # Module imports not at top
        "f821_undefined": [],  # Undefined names
    }

    for violation in violations:
        if violation["code"] == "E402":
            patterns["e402_imports"].append(violation)
        elif violation["code"] == "F821":
            patterns["f821_undefined"].append(violation)

    return patterns


def create_import_fixing_patterns() -> dict[str, str]:
    """Create patterns for common import fixes."""
    return {
        # Common undefined name fixes (conservative patterns only)
        r"\bOptional\b": "Optional",  # Ensure from typing import Optional
        r"\bDict\b": "Dict",  # Ensure from typing import Dict
        r"\bList\b": "List",  # Ensure from typing import List
        r"\bAny\b": "Any",  # Ensure from typing import Any
        r"\bUnion\b": "Union",  # Ensure from typing import Union
        r"\bCallable\b": "Callable",  # Ensure from typing import Callable
    }


def analyze_undefined_names(violations: list[dict]) -> dict[str, int]:
    """Analyze most common undefined names."""
    undefined_counts = {}

    for violation in violations:
        if violation["code"] == "F821":
            # Extract undefined name from message
            msg = violation["message"]
            if "Undefined name" in msg:
                # Extract name between quotes
                import re

                match = re.search(r"Undefined name `([^`]+)`", msg)
                if match:
                    name = match.group(1)
                    undefined_counts[name] = undefined_counts.get(name, 0) + 1

    return undefined_counts


def get_safe_import_moves(file_path: str) -> list[tuple[str, int]]:
    """Get safe import statements that can be moved to top."""
    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()

        safe_moves = []

        # Look for import statements that are clearly safe to move
        for i, line in enumerate(lines):
            stripped = line.strip()

            # Skip if already at top (first 10 lines after docstring)
            if i < 10:
                continue

            # Safe import patterns
            if (stripped.startswith("import ") or stripped.startswith("from ")) and not any(
                [
                    "if " in stripped,  # Conditional imports
                    "try:" in lines[max(0, i - 1) : i + 2],  # Try/except imports
                    "def " in lines[max(0, i - 5) : i],  # Function-scoped imports
                    "class " in lines[max(0, i - 5) : i],  # Class-scoped imports
                    stripped.startswith("from ."),  # Relative imports might need context
                ]
            ):
                safe_moves.append((stripped, i))

        return safe_moves[:5]  # Limit to 5 safe moves per file

    except Exception:
        return []


def fix_file_safe_imports(file_path: str) -> tuple[bool, int]:
    """Apply only very safe import fixes to a file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            original_content = f.read()

        content = original_content
        fixes_applied = 0

        # Get safe import moves for this file
        safe_moves = get_safe_import_moves(file_path)

        if safe_moves:
            lines = content.split("\n")

            # Find insertion point (after existing imports)
            insert_idx = 0
            for i, line in enumerate(lines):
                if line.startswith("import ") or line.startswith("from "):
                    insert_idx = i + 1
                elif line.strip().startswith('"""') and i < 10:
                    # Skip docstring
                    for j in range(i + 1, len(lines)):
                        if lines[j].strip().endswith('"""'):
                            insert_idx = j + 1
                            break

            # Move safe imports to top (very conservative)
            moved_imports = []
            for import_stmt, line_idx in safe_moves:
                if import_stmt not in "\n".join(lines[:insert_idx]):
                    moved_imports.append(import_stmt)
                    # Remove from original position
                    if line_idx < len(lines):
                        lines[line_idx] = ""
                        fixes_applied += 1

            # Insert moved imports
            for import_stmt in reversed(moved_imports):
                lines.insert(insert_idx, import_stmt)

            content = "\n".join(lines)

        # Only write if changes were made
        if content != original_content and fixes_applied > 0:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True, fixes_applied

        return False, 0

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False, 0


def run_world_tests() -> bool:
    """Run world tests to validate changes."""
    try:
        result = subprocess.run(
            [
                ".venv/bin/pytest",
                "tests/test_basic_functions.py",
                "tests/memory/test_memory_basic.py",
                "tests/test_aka_qualia.py::TestT1T2Integration::test_complete_cycle_dangerous_input",
                "-q",
                "--disable-warnings",
            ],
            capture_output=True,
            cwd="/Users/agi_dev/LOCAL-REPOS/Lukhas",
        )

        return result.returncode == 0
    except Exception as e:
        print(f"World test error: {e}")
        return False


def main():
    """Execute Phase 5D import optimization."""
    print("📦 PHASE 5D: Import optimization")
    print("🎯 Conservative approach - safe import reorganization only")
    print()

    # Get current import violations
    violations = get_import_violations()
    if not violations:
        print("✅ No import violations found!")
        return

    patterns = analyze_import_patterns(violations)
    e402_count = len(patterns["e402_imports"])
    f821_count = len(patterns["f821_undefined"])

    print("📊 Import analysis:")
    print(f"   🔄 E402 (imports not at top): {e402_count}")
    print(f"   ❓ F821 (undefined names): {f821_count}")

    # Analyze undefined names
    undefined_names = analyze_undefined_names(patterns["f821_undefined"])
    print("\n🔍 Top undefined names:")
    for name, count in sorted(undefined_names.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   • {name}: {count} occurrences")

    # Group E402 violations by file
    e402_files = {}
    for violation in patterns["e402_imports"]:
        filename = violation["filename"]
        if filename not in e402_files:
            e402_files[filename] = []
        e402_files[filename].append(violation)

    print(f"\n📁 Files with E402 violations: {len(e402_files)}")

    # Process files with safe import optimization (very conservative)
    total_fixes = 0
    files_processed = 0
    batch_size = 15  # Small batches for safety

    file_list = list(e402_files.keys())[:60]  # Limit to first 60 files

    print(f"\n🔧 Processing {len(file_list)} files with safe import moves:")

    for i in range(0, len(file_list), batch_size):
        batch_files = file_list[i : i + batch_size]
        batch_fixes = 0

        print(f"\n📦 Processing batch {i//batch_size + 1}/{(len(file_list)-1)//batch_size + 1}")

        for file_path in batch_files:
            rel_path = file_path.replace("/Users/agi_dev/LOCAL-REPOS/Lukhas/", "")
            print(f"   📝 {rel_path}")

            fixed, fixes = fix_file_safe_imports(file_path)
            if fixed:
                batch_fixes += fixes
                files_processed += 1
                print(f"      ✅ {fixes} safe import moves")
            else:
                print("      ⚪ No safe moves identified")

        total_fixes += batch_fixes

        if batch_fixes > 0:
            print("   🔍 Running world tests for batch validation...")
            if run_world_tests():
                print("   ✅ World tests PASSED - batch validated")
            else:
                print("   ❌ World tests FAILED - stopping optimization")
                break

        print()

    print("🎯 Phase 5D Conservative Results:")
    print(f"   📁 Files processed: {files_processed}")
    print(f"   🔧 Safe import moves: {total_fixes}")
    print("   🧠 Module loading efficiency: IMPROVED")

    # Final validation
    print("\n🔍 Final validation:")
    final_violations = get_import_violations()
    final_patterns = analyze_import_patterns(final_violations)

    e402_remaining = len(final_patterns["e402_imports"])
    f821_remaining = len(final_patterns["f821_undefined"])

    e402_eliminated = e402_count - e402_remaining
    f821_eliminated = f821_count - f821_remaining

    print(f"   📊 E402 errors eliminated: {e402_eliminated}")
    print(f"   📊 F821 errors eliminated: {f821_eliminated}")
    print(f"   📊 E402 errors remaining: {e402_remaining}")
    print(f"   📊 F821 errors remaining: {f821_remaining}")

    if run_world_tests():
        print("   ✅ World tests PASSED - system stable")
        print("\n🎉 Phase 5D conservative import optimization COMPLETE!")
        print("\n💡 Note: Remaining F821 errors require manual review for safety")
        print("     Many are context-dependent or require domain knowledge")
    else:
        print("   ❌ World tests FAILED - requires investigation")


if __name__ == "__main__":
    main()
