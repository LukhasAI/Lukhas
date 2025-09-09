#!/usr/bin/env python3
"""
Fix remaining syntax errors in LUKHAS codebase
"""
import os
import re


def fix_file_syntax(file_path):
    """Fix syntax errors in a single file."""
    print(f"Processing: {file_path}")

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    original_content = content

    # Fix f-string parentheses mismatches
    content = re.sub(r'f"[^"]*time\.time\(\s*\}[^"]*"',
                     lambda m: m.group(0).replace("time.time(}", "time.time())"),
                     content)

    # Fix missing closing brackets in dictionaries
    # Pattern: {"key": {"nested": value without closing }}
    content = re.sub(r'(\{"[^"]*":\s*\{"[^"]*":\s*[^}]+)\n', r"\1}}\n", content)

    # Fix bracket-parenthesis mismatches in specific patterns
    content = re.sub(r"\{[^{}]*\)\s*$", lambda m: m.group(0).replace(")", "}"), content, flags=re.MULTILINE)

    if content != original_content:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  ✅ Fixed syntax errors in {file_path}")
        except Exception as e:
            print(f"  ❌ Error writing {file_path}: {e}")

# Files with known syntax errors
problematic_files = [
    "candidate/bridge/api/flows.py",
    "candidate/core/security/secure_logging.py",
    "tests/test_aka_qualia.py"
]

print("🔧 Fixing remaining syntax errors in LUKHAS codebase...")

for file_path in problematic_files:
    if os.path.exists(file_path):
        fix_file_syntax(file_path)
    else:
        print(f"⚠️  File not found: {file_path}")

print("✅ Syntax error fixing complete!")