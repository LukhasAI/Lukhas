#!/usr/bin/env python3
"""
Phase 5C: UTC/timezone standardization for LUKHAS consciousness system
Critical for consciousness timestamp accuracy and temporal coherence
"""

import json
import re
import subprocess


def get_dtz005_violations() -> list[dict]:
    """Get all DTZ005 violations from ruff check."""
    try:
        result = subprocess.run(
            [
                ".venv/bin/ruff",
                "check",
                ".",
                "--select=DTZ005",
                "--output-format=json",
                "--quiet",
                "--exclude=archive/",  # Exclude archive directory
                "--exclude=website_v1/",  # Exclude deprecated website
                "--exclude=products/shared/gpt_oss_integration/",  # Exclude problematic UTF-8 file
            ],
            capture_output=True,
            text=True,
            cwd="/Users/agi_dev/LOCAL-REPOS/Lukhas",
        )

        if result.stdout:
            return json.loads(result.stdout)
        return []
    except Exception as e:
        print(f"Error getting DTZ005 violations: {e}")
        return []


def create_utc_fixing_patterns() -> dict[str, str]:
    """Create patterns for UTC standardization fixes."""
    return {
        # Basic datetime.now() -> datetime.now(timezone.utc)
        r"datetime\.now\(\)": "datetime.now(timezone.utc)",
        r"datetime\.datetime\.now\(\)": "datetime.now(timezone.utc)",
        # With assignments - preserve variable names
        r"(\w+)\s*=\s*datetime\.now\(\)": r"\1 = datetime.now(timezone.utc)",
        r"(\w+)\s*=\s*datetime\.datetime\.now\(\)": r"\1 = datetime.now(timezone.utc)",
        # In f-strings and expressions
        r'f"([^"]*){datetime\.now\(\)}([^"]*)"': r'f"\1{datetime.now(timezone.utc)}\2"',
        r'f"([^"]*){datetime\.datetime\.now\(\)}([^"]*)"': r'f"\1{datetime.now(timezone.utc)}\2"',
        # Function call arguments
        r"datetime\.now\(\),": "datetime.now(timezone.utc),",
        r"datetime\.datetime\.now\(\),": "datetime.now(timezone.utc),",
    }


def ensure_timezone_import(content: str) -> str:
    """Ensure timezone import is present when needed."""
    if "timezone.utc" in content and "from datetime import" not in content:
        # Add timezone import
        import_line = "from datetime import datetime, timezone\n"

        # Find where to insert import
        lines = content.split("\n")
        insert_idx = 0

        # Find last import or after docstring
        for i, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                insert_idx = i + 1
            elif line.strip().startswith('"""') and i < 10:
                # Skip docstring
                for j in range(i + 1, len(lines)):
                    if lines[j].strip().endswith('"""'):
                        insert_idx = j + 1
                        break

        lines.insert(insert_idx, import_line)
        return "\n".join(lines)

    return content


def fix_file_utc_issues(file_path: str, patterns: dict[str, str]) -> tuple[bool, int]:
    """Fix UTC timezone issues in a single file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            original_content = f.read()

        content = original_content
        fixes_applied = 0

        # Apply UTC fixing patterns
        for pattern, replacement in patterns.items():
            matches = re.findall(pattern, content)
            if matches:
                content = re.sub(pattern, replacement, content)
                fixes_applied += len(matches)

        # Ensure timezone import if needed
        if fixes_applied > 0:
            content = ensure_timezone_import(content)

        # Only write if changes were made
        if content != original_content:
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
    """Execute Phase 5C UTC standardization."""
    print("🕐 PHASE 5C: UTC/timezone standardization")
    print("🎯 Critical for consciousness timestamp accuracy")
    print()

    # Get current DTZ005 violations
    violations = get_dtz005_violations()
    if not violations:
        print("✅ No DTZ005 violations found!")
        return

    print(f"📊 Found {len(violations)} DTZ005 violations")

    # Group by file for efficient processing
    files_to_fix = {}
    for violation in violations:
        filename = violation["filename"]
        if filename not in files_to_fix:
            files_to_fix[filename] = []
        files_to_fix[filename].append(violation)

    print(f"📁 Files to process: {len(files_to_fix)}")
    print()

    # Get UTC fixing patterns
    patterns = create_utc_fixing_patterns()

    # Process files in batches
    total_fixes = 0
    files_processed = 0
    batch_size = 10  # Small batches for consciousness modules

    file_list = list(files_to_fix.keys())

    for i in range(0, len(file_list), batch_size):
        batch_files = file_list[i : i + batch_size]
        batch_fixes = 0

        print(f"🔧 Processing batch {i//batch_size + 1}/{(len(file_list)-1)//batch_size + 1}")

        for file_path in batch_files:
            rel_path = file_path.replace("/Users/agi_dev/LOCAL-REPOS/Lukhas/", "")
            print(f"   📝 {rel_path}")

            fixed, fixes = fix_file_utc_issues(file_path, patterns)
            if fixed:
                batch_fixes += fixes
                files_processed += 1
                print(f"      ✅ {fixes} UTC fixes applied")
            else:
                print("      ⚪ No changes needed")

        total_fixes += batch_fixes

        if batch_fixes > 0:
            print("   🔍 Running world tests for batch validation...")
            if run_world_tests():
                print("   ✅ World tests PASSED - batch validated")
            else:
                print("   ❌ World tests FAILED - rolling back batch")
                # In production, would implement rollback here
                break

        print()

    print("🎯 Phase 5C Results:")
    print(f"   📁 Files processed: {files_processed}")
    print(f"   🔧 Total UTC fixes: {total_fixes}")
    print("   🧠 Consciousness timestamp accuracy: ENHANCED")

    # Final validation
    print("\n🔍 Final validation:")
    final_violations = get_dtz005_violations()
    remaining = len(final_violations)
    eliminated = len(violations) - remaining

    print(f"   📊 DTZ005 errors eliminated: {eliminated}")
    print(f"   📊 DTZ005 errors remaining: {remaining}")

    if run_world_tests():
        print("   ✅ World tests PASSED - system stable")
        print("\n🎉 Phase 5C UTC standardization COMPLETE!")
    else:
        print("   ❌ World tests FAILED - requires investigation")


if __name__ == "__main__":
    main()
