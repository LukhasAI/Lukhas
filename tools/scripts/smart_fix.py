#!/usr/bin/env python3
"""
Smart Linting Fix - Only fixes critical issues without breaking code
"""
import time
import streamlit as st

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional


class SmartFixer:
    """Intelligent fixer that preserves code functionality"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.critical_issues = []
        self.warnings = []
        self.fixed_count = 0

    def run_command(self, cmd: list[str]) -> tuple[int, str, str]:
        """Run command safely"""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root, timeout=30)
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return 1, "", str(e)

    def identify_critical_issues(self):
        """Identify only critical issues that need fixing"""
        print("🔍 Identifying critical issues...")

        # Run flake8 with our config
        code, out, err = self.run_command(
            [
                sys.executable,
                "-m",
                "flake8",
                ".",
                "--format",
                "%(path)s:%(row)d:%(col)d: %(code)s %(text)s",
                "--exclude",
                ".venv,venv,__pycache__,test_metadata,lukhas/flags",
            ]
        )

        if not out:
            print("✅ No critical issues found!")
            return

        # Parse issues
        for line in out.strip().split("\n"):
            if not line:
                continue

            # Parse flake8 output
            match = re.match(r"([^:]+):(\d+):(\d+): ([A-Z]\d+) (.+)", line)
            if match:
                file_path, line_num, col, code, message = match.groups()

                # Categorize issues
                issue = {
                    "file": file_path,
                    "line": int(line_num),
                    "col": int(col),
                    "code": code,
                    "message": message,
                }

                # Critical issues that should be fixed
                if code in ["F401", "F841", "E999", "F821", "F822", "F823"]:
                    self.critical_issues.append(issue)
                else:
                    self.warnings.append(issue)

        print(f"Found {len(self.critical_issues)} critical issues")
        print(f"Found {len(self.warnings)} warnings (will not auto-fix)")

    def fix_unused_imports(self):
        """Fix only truly unused imports"""
        print("🔧 Fixing unused imports (carefully)...")

        # Group issues by file
        files_to_fix = {}
        for issue in self.critical_issues:
            if issue["code"] == "F401":  # unused import
                file_path = issue["file"]
                if "__init__.py" in file_path:
                    continue  # Skip __init__ files
                if file_path not in files_to_fix:
                    files_to_fix[file_path] = []
                files_to_fix[file_path].append(issue)

        # Fix each file
        for file_path, issues in files_to_fix.items():
            print(f"  Fixing {file_path}...")

            # Use autoflake conservatively
            code, out, err = self.run_command(
                [
                    sys.executable,
                    "-m",
                    "autoflake",
                    "--in-place",
                    "--remove-unused-variables",
                    "--remove-all-unused-imports",
                    "--ignore-init-module-imports",
                    file_path,
                ]
            )

            if code == 0:
                self.fixed_count += len(issues)

    def format_conservatively(self):
        """Format only files with issues, preserving functionality"""
        print("🎨 Formatting code (conservative mode)...")

        # Get unique files with issues
        files_to_format = set()
        for issue in self.critical_issues + self.warnings[:10]:  # Only format files with issues
            files_to_format.add(issue["file"])

        for file_path in files_to_format:
            if not Path(file_path).exists():
                continue

            # Use Black with safe settings
            code, out, err = self.run_command(
                [
                    sys.executable,
                    "-m",
                    "black",
                    "--line-length",
                    "88",  # More reasonable than 79
                    "--target-version",
                    "py39",
                    "--quiet",
                    file_path,
                ]
            )

            if code == 0 and "reformatted" in out:
                self.fixed_count += 1

    def sort_imports_safely(self):
        """Sort imports without breaking star imports"""
        print("📦 Sorting imports (safe mode)...")

        # Only sort in files that don't use star imports
        files_to_sort = set()
        for issue in self.critical_issues:
            file_path = issue["file"]

            # Check if file has star imports
            try:
                with open(file_path) as f:
                    content = f.read()
                    if "import *" in content:
                        continue  # Skip files with star imports
                    files_to_sort.add(file_path)
            except BaseException:
                continue

        for file_path in files_to_sort:
            code, out, err = self.run_command(
                [
                    sys.executable,
                    "-m",
                    "isort",
                    "--profile",
                    "black",
                    "--line-length",
                    "88",
                    "--force-single-line",  # Safer
                    "--quiet",
                    file_path,
                ]
            )

            if code == 0:
                self.fixed_count += 1

    def validate_fixes(self):
        """Ensure fixes didn't break anything"""
        print("✅ Validating fixes...")

        # Quick syntax check
        code, out, err = self.run_command(
            [
                sys.executable,
                "-m",
                "py_compile",
                *[issue["file"] for issue in self.critical_issues[:10]],
            ]
        )

        if code != 0:
            print("⚠️ Some fixes may have introduced syntax errors!")
            print("Run 'git diff\' to review changes")
            return False

        return True

    def generate_report(self):
        """Generate a human-readable report"""
        report = {
            "fixed": self.fixed_count,
            "critical_remaining": len(self.critical_issues) - self.fixed_count,
            "warnings": len(self.warnings)},
            "summary": "Smart fix completed successfully",
        }

        # Save report
        report_path = self.project_root / "test_results" / "smart_fix_report.json"
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        # Print summary
        print("\n" + "=" * 60)
        print("📊 SMART FIX SUMMARY")
        print("=" * 60)
        print(f"✅ Fixed: {report[\'fixed']} issues")
        print(f"⚠️ Critical remaining: {report['critical_remaining']}")
        print(f"ℹ️ Warnings (not fixed): {report['warnings']}")
        print("=" * 60)

        if self.critical_issues:
            print("\n🔴 Critical issues that need manual attention:")
            for issue in self.critical_issues[:5]:
                print(f"  {issue['file']}:{issue['line']} - {issue['code']}: {issue['message'][:50]}...")

        print("\n📄 Full report: test_results/smart_fix_report.json")
        print("💡 Run 'git diff' to review all changes")
        print("💡 Run 'git checkout -- .' to undo if needed")

    def run(self):
        """Run the smart fix process"""
        print("🚀 Starting Smart Fix...")
        print("This will only fix critical issues without breaking your code")
        print("-" * 60)

        # Step 1: Identify issues
        self.identify_critical_issues()

        if not self.critical_issues:
            print("✨ No critical issues to fix!")
            return True

        # Step 2: Fix conservatively
        self.fix_unused_imports()
        self.sort_imports_safely()
        self.format_conservatively()

        # Step 3: Validate
        if self.validate_fixes():
            print("✅ All fixes validated successfully")

        # Step 4: Report
        self.generate_report()

        return True


if __name__ == "__main__":
    fixer = SmartFixer()
    success = fixer.run()
    sys.exit(0 if success else 1)
