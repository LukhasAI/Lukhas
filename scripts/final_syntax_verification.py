#!/usr/bin/env python3
"""
Module: final_syntax_verification.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

"""
Final Syntax Verification
Check for any remaining syntax errors after mass fixes
"""

import ast
import os
from pathlib import Path


def scan_syntax_errors():
    """Scan all Python files for syntax errors"""
    total_files = 0
    files_with_errors = 0
    error_details = []

    print("🔍 FINAL SYNTAX VERIFICATION SCAN")
    print("=" * 60)

    for root, dirs, files in os.walk("."):
        # Skip certain directories
        skip_dirs = {".venv", "__pycache__", ".git", "node_modules", ".pytest_cache"}
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for file in files:
            if not file.endswith(".py"):
                continue

            filepath = Path(root) / file
            total_files += 1

            try:
                with open(filepath, encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Try to parse with AST
                ast.parse(content, filename=str(filepath))

            except SyntaxError as e:
                files_with_errors += 1
                error_details.append({"file": str(filepath), "line": e.lineno, "error": str(e).split("(")[0].strip()})

            except Exception:
                # Skip files that can't be read
                continue

    print("📊 VERIFICATION RESULTS:")
    print(f"  📁 Total Python files: {total_files}")
    print(f"  ❌ Files with syntax errors: {files_with_errors}")
    print(f"  ✅ Clean files: {total_files - files_with_errors}")
    print(f"  🎯 Success rate: {((total_files - files_with_errors) / total_files * 100):.1f}%")

    if error_details:
        print("\n🚨 REMAINING ERRORS:")
        print("-" * 40)
        for error in error_details[:20]:  # Show first 20 errors
            print(f"  {error['file']}:{error['line']} - {error['error']}")

        if len(error_details) > 20:
            print(f"  ... and {len(error_details) - 20} more errors")
    else:
        print("\n🎉 ZERO SYNTAX ERRORS FOUND!")

    return files_with_errors == 0


if __name__ == "__main__":
    success = scan_syntax_errors()
    exit(0 if success else 1)
