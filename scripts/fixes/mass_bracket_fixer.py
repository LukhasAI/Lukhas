#!/usr/bin/env python3
"""
Module: mass_bracket_fixer.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

"""
Mass Bracket Fixer - Target Specific Systematic Patterns
========================================================

Fix the specific patterns identified in manual analysis:
1. .hexdigest()}}[:8]} -> .hexdigest()[:8]}
2. .timestamp(}} -> .timestamp()}
3. {).get( -> {}).get(
"""

import re
import subprocess
from pathlib import Path


def fix_systematic_patterns(content: str) -> tuple[str, int]:
    """Fix systematic bracket patterns"""
    fixes = 0

    # Pattern 1: .hexdigest()}}[:8]} -> .hexdigest()[:8]}
    pattern1_matches = len(re.findall(r"\.hexdigest\(\)\}+\[", content))
    content = re.sub(r"\.hexdigest\(\)\}+\[", ".hexdigest()[", content)
    fixes += pattern1_matches

    # Pattern 2: .timestamp(}} -> .timestamp()}
    pattern2_matches = len(re.findall(r"\.timestamp\(\)\}+", content))
    content = re.sub(r"\.timestamp\(\)\}+", ".timestamp()", content)
    fixes += pattern2_matches

    # Pattern 3: {).get( -> {}).get(
    pattern3_matches = len(re.findall(r"\{\)\.get\(", content))
    content = re.sub(r"\{\)\.get\(", r"{}.get(", content)
    fixes += pattern3_matches

    # Pattern 4: Fix f-string expecting '}'
    pattern4_matches = len(re.findall(r"\{[^}]+\"[^}]*$", content, re.MULTILINE))
    content = re.sub(r"(\{[^}]+)\"([^}]*)$", r'\1"\2}', content, flags=re.MULTILINE)
    fixes += pattern4_matches

    return content, fixes


def fix_file_brackets(file_path: str) -> bool:
    """Fix bracket patterns in a file"""
    try:
        with open(file_path, encoding="utf-8") as f:
            original = f.read()

        fixed, fix_count = fix_systematic_patterns(original)

        if fix_count > 0:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(fixed)

            # Test compilation
            result = subprocess.run(
                [".venv/bin/python", "-m", "py_compile", file_path], capture_output=True, text=True, cwd=Path.cwd()
            )

            if result.returncode == 0:
                print(f"✅ {file_path}: {fix_count} bracket fixes applied")
                return True
            else:
                # Revert
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(original)
                print(f"❌ {file_path}: Reverted after {fix_count} fixes - {result.stderr.strip()}")
                return False

        return True

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False


if __name__ == "__main__":
    target_files = [
        "candidate/governance/security/security_audit_engine.py",
        "candidate/qi/ui/abstract_reasoning_demo.original.py",
    ]

    print("🔧 Mass Bracket Fixer")
    print("=" * 30)

    for file_path in target_files:
        if Path(file_path).exists():
            fix_file_brackets(file_path)
        else:
            print(f"⚠️ File not found: {file_path}")
