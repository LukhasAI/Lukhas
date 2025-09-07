#!/usr/bin/env python3
"""
Mass Fix Pattern 2: Malformed Function Definitions and Calls
Fix patterns like: def function(): and function_call()
"""

import os
import re
from pathlib import Path


def find_files_with_pattern():
    """Find all Python files with Pattern 2 errors"""
    import subprocess

    # Use ripgrep to find files with the pattern
    result = subprocess.run([
        "rg", r"def.*\(\s*,|\(\s*,.*\)", ".",
        "--type", "py", "-l"
    ], capture_output=True, text=True, cwd="/Users/agi_dev/LOCAL-REPOS/Lukhas")

    if result.returncode == 0:
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return []

def fix_pattern_2_errors(content):
    """Fix Pattern 2: malformed commas in function definitions and calls"""
    fixes = 0

    # Pattern 1: def function(): -> def function():
    pattern1 = r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\s*,\s*timezone\s*\):"
    matches = re.findall(pattern1, content)
    if matches:
        content = re.sub(pattern1, r"def \1():", content)
        fixes += len(matches)

    # Pattern 2: function_call() -> function_call()
    pattern2 = r"([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\s*,\s*timezone\s*\)"
    matches = re.findall(pattern2, content)
    if matches:
        content = re.sub(pattern2, r"\1()", content)
        fixes += len(matches)

    # Pattern 3: datetime.now() -> datetime.now(timezone.utc)
    pattern3 = r"datetime\.(now|utcnow)\s*\(\s*,\s*timezone\s*\)"
    matches = re.findall(pattern3, content)
    if matches:
        content = re.sub(pattern3, r"datetime.\1(timezone.utc)", content)
        fixes += len(matches)

    # Pattern 4: uuid.uuid4() -> uuid.uuid4()
    pattern4 = r"uuid\.uuid4\s*\(\s*,\s*timezone\s*\)"
    if re.search(pattern4, content):
        content = re.sub(pattern4, r"uuid.uuid4()", content)
        fixes += 1

    # Pattern 5: APIRouter() -> APIRouter()
    pattern5 = r"APIRouter\s*\(\s*,\s*timezone\s*\)"
    if re.search(pattern5, content):
        content = re.sub(pattern5, r"APIRouter()", content)
        fixes += 1

    # Pattern 6: load_dotenv() -> load_dotenv()
    pattern6 = r"load_dotenv\s*\(\s*,\s*timezone\s*\)"
    if re.search(pattern6, content):
        content = re.sub(pattern6, r"load_dotenv()", content)
        fixes += 1

    return content, fixes

def process_files():
    """Process all files with Pattern 2 errors"""
    files_to_fix = find_files_with_pattern()

    if not files_to_fix:
        print("🎉 No Pattern 2 errors found!")
        return 0, 0

    total_files_fixed = 0
    total_fixes = 0

    for file_path in files_to_fix:
        full_path = Path("/Users/agi_dev/LOCAL-REPOS/Lukhas") / file_path

        if not full_path.exists():
            continue

        try:
            with open(full_path, encoding="utf-8") as f:
                original_content = f.read()

            fixed_content, fixes_made = fix_pattern_2_errors(original_content)

            if fixes_made > 0:
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(fixed_content)

                total_files_fixed += 1
                total_fixes += fixes_made

                print(f"✅ {file_path}: {fixes_made} fixes")

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")

    return total_files_fixed, total_fixes

if __name__ == "__main__":
    print("🔧 MASS FIX PATTERN 2: Malformed function definitions and calls")
    print("=" * 70)

    files_fixed, total_fixes = process_files()

    print("=" * 70)
    print("📊 MASS FIX RESULTS:")
    print(f"  📁 Files fixed: {files_fixed}")
    print(f"  🔧 Total fixes: {total_fixes}")
    print("  📋 Pattern: Malformed comma placement in functions")
    print("=" * 70)
