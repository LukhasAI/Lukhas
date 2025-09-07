#!/usr/bin/env python3
"""
Critical Syntax Fixer for LUKHAS Workspace
Fixes the most common and critical syntax errors preventing basic operation.
"""
import ast
import re
import sys
from pathlib import Path


class CriticalSyntaxFixer:
    def __init__(self):
        self.fixes_applied = 0
        self.files_processed = 0

    def fix_f_string_issues(self, content: str) -> str:
        """Fix common f-string syntax errors."""

        # Pattern 1: f"...{var}[:10]}" -> f"...{var[:10]}"
        content = re.sub(r'(f"[^"]*\{[^}]+)\}(\[:?\d+\])\}', r"\1\2}", content)
        content = re.sub(r"(f'[^']*\{[^}]+)\}(\[:?\d+\])\}", r"\1\2}", content)

        # Pattern 2: f"...{var}:.3f}" -> f"...{var:.3f}"
        content = re.sub(r'(f"[^"]*\{[^}]+)\}(\:[.\d]+f)\}', r"\1\2}", content)
        content = re.sub(r"(f'[^']*\{[^}]+)\}(\:[.\d]+f)\}", r"\1\2}", content)

        # Pattern 3: Fix missing closing parentheses in f-strings
        content = re.sub(r'f"([^"]*\{[^}]+)\}([^"}]*)"([^}]*)\}', r'f"\1}\2}"', content)

        # Pattern 4: Fix escaped quotes in f-strings
        content = re.sub(r"f\\?'([^']*)'", r"f'\1'", content)
        content = re.sub(r'f\\?"([^"]*)"', r'f"\1"', content)

        return content

    def fix_missing_parentheses(self, content: str) -> str:
        """Fix missing parentheses and brackets."""

        # Fix missing closing parentheses in function calls
        lines = content.split("\n")
        fixed_lines = []

        for line in lines:
            # Common pattern: f"...{func()}
            if re.search(r'f"[^"]*\{[^}]*\([^)]*$', line):
                line = line + ")"

            # Missing closing parentheses for time.time()
            line = re.sub(r"time\.time\(\}", "time.time()}", line)
            line = re.sub(r"int\(time\.time\(\}", "int(time.time())}", line)

            fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def fix_basic_syntax_errors(self, content: str) -> str:
        """Fix basic syntax errors."""

        # Fix single } in f-strings
        content = re.sub(r"(\{[^}]+)\}\}", r"\1}", content)

        # Fix malformed dictionary literals
        content = re.sub(r"\{\)\}", "{}", content)

        # Fix incomplete if/elif statements
        content = re.sub(r"if\s+[^:]+\n\s*elif", lambda m: m.group(0).replace("\nelif", ":\nelif"), content)

        return content

    def fix_file(self, file_path: Path) -> bool:
        """Fix syntax errors in a single file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                original_content = f.read()

            # Skip empty files
            if not original_content.strip():
                return True

            content = original_content

            # Apply fixes in order
            content = self.fix_f_string_issues(content)
            content = self.fix_missing_parentheses(content)
            content = self.fix_basic_syntax_errors(content)

            # Only write if changes were made
            if content != original_content:
                # Test if the fix creates valid Python
                try:
                    ast.parse(content)
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    self.fixes_applied += 1
                    print(f"✅ Fixed: {file_path}")
                    return True
                except SyntaxError as e:
                    print(f"⚠️  Could not fix: {file_path} - {e}")
                    return False
            else:
                # Test original content
                try:
                    ast.parse(original_content)
                    return True
                except SyntaxError:
                    print(f"❌ Syntax error remains: {file_path}")
                    return False

        except Exception as e:
            print(f"🚨 Error processing {file_path}: {e}")
            return False

    def process_directory(self, root_path: Path) -> dict:
        """Process all Python files in directory."""
        results = {
            "total_files": 0,
            "fixed_files": 0,
            "valid_files": 0,
            "error_files": 0
        }

        # Skip problematic directories - ONLY process actual LUKHAS project files
        skip_dirs = {".git", "__pycache__", ".venv", ".lintvenv", ".venv_runtime_test", "node_modules", "venv"}

        for py_file in root_path.rglob("*.py"):
            # Skip if in problematic directory
            if any(skip_dir in py_file.parts for skip_dir in skip_dirs):
                continue

            # Only process files that are clearly part of the LUKHAS project
            file_path_str = str(py_file)
            if ("site-packages" in file_path_str or
                "lib/python" in file_path_str or
                "transformers/" in file_path_str or
                "kubernetes/" in file_path_str or
                "scipy/" in file_path_str):
                continue

            results["total_files"] += 1
            self.files_processed += 1

            if self.fix_file(py_file):
                results["valid_files"] += 1
            else:
                results["error_files"] += 1

        return results


def main():
    print("🔧 CRITICAL SYNTAX FIXER FOR LUKHAS")
    print("=" * 50)

    root_path = Path.cwd()
    fixer = CriticalSyntaxFixer()

    results = fixer.process_directory(root_path)

    print("\n📊 RESULTS SUMMARY")
    print("=" * 30)
    print(f"📁 Total files processed: {results['total_files']}")
    print(f"✅ Files fixed: {fixer.fixes_applied}")
    print(f"✅ Valid files: {results['valid_files']}")
    print(f"❌ Files with errors: {results['error_files']}")

    success_rate = (results["valid_files"] / results["total_files"]) * 100 if results["total_files"] > 0 else 0
    print(f"📈 Syntax success rate: {success_rate:.1f}%")

    if success_rate >= 80:
        print("\n🎉 EXCELLENT: Workspace syntax is in good condition!")
    elif success_rate >= 60:
        print("\n⚠️  GOOD: Most files are syntactically valid.")
    else:
        print("\n🚨 CRITICAL: Many syntax errors remain. Manual review needed.")

    return 0 if success_rate >= 80 else 1


if __name__ == "__main__":
    sys.exit(main())
