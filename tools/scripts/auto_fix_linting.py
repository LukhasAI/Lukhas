#!/usr/bin/env python3
"""
Automated Linting Fix Script
Runs all linters and formatters with auto-fix capabilities
"""

import json
import subprocess
import sys
import time
from pathlib import Path


class AutoLintFixer:

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.issues_fixed = []
        self.issues_remaining = []

    def run_command(self, cmd: list[str]) -> tuple[int, str, str]:
        """Run a command and return exit code, stdout, stderr"""
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=self.project_root
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return 1, "", str(e)

    def fix_with_black(self):
        """Format code with Black"""
        print("🔧 Running Black formatter...")
        dirs = ["lukhas_pwm", "bridge", "core", "serve", "tests"]
        for dir_name in dirs:
            if (self.project_root / dir_name).exists():
                code, out, err = self.run_command(
                    ["black", "--line-length", "79", dir_name]
                )
                if code == 0:
                    self.issues_fixed.append(f"Black formatted {dir_name}")
                else:
                    self.issues_remaining.append(f"Black failed on {dir_name}: {err}")

    def fix_with_ruff(self):
        """Fix issues with Ruff"""
        print("🔧 Running Ruff auto-fixes...")
        code, out, err = self.run_command(["ruff", "check", "--fix", "."])
        if "Fixed" in out:
            self.issues_fixed.append(f"Ruff fixed issues: {out}")
        if code != 0 and err:
            self.issues_remaining.append(f"Ruff couldn't fix: {err}")

    def fix_imports_with_isort(self):
        """Sort imports with isort"""
        print("🔧 Sorting imports with isort...")
        dirs = ["lukhas_pwm", "bridge", "core", "serve", "tests"]
        for dir_name in dirs:
            if (self.project_root / dir_name).exists():
                code, out, err = self.run_command(
                    [
                        "isort",
                        "--profile",
                        "black",
                        "--line-length",
                        "79",
                        dir_name,
                    ]
                )
                if code == 0:
                    self.issues_fixed.append(f"isort sorted imports in {dir_name}")

    def remove_unused_imports(self):
        """Remove unused imports with autoflake"""
        print("🔧 Removing unused imports...")
        dirs = ["lukhas_pwm", "bridge", "core", "serve"]
        for dir_name in dirs:
            if (self.project_root / dir_name).exists():
                code, out, err = self.run_command(
                    [
                        "autoflake",
                        "--in-place",
                        "--remove-unused-variables",
                        "--remove-all-unused-imports",
                        "--recursive",
                        dir_name,
                    ]
                )
                if code == 0:
                    self.issues_fixed.append(f"Removed unused imports from {dir_name}")

    def check_remaining_issues(self):
        """Check for any remaining issues"""
        print("🔍 Checking for remaining issues...")

        # Run flake8 to check
        code, out, err = self.run_command(
            [
                "flake8",
                "--count",
                "--statistics",
                "--max-line-length",
                "79",
                "--extend-ignore",
                "E203,W503",
                ".",
            ]
        )

        if out:
            self.issues_remaining.append(f"Flake8 issues remain: {out}")

        # Run mypy to check types
        code, out, err = self.run_command(["mypy", "--ignore-missing-imports", "."])

        if code != 0:
            self.issues_remaining.append(f"Type issues remain: {out}")

    def generate_report(self):
        """Generate a report of fixes"""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "fixes_applied": len(self.issues_fixed),
            "issues_remaining": len(self.issues_remaining),
            "fixed": self.issues_fixed,
            "remaining": self.issues_remaining,
        }

        report_path = self.project_root / "test_results" / "linting_report.json"
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        return report

    def run_full_fix(self):
        """Run all fixes in sequence"""
        print("🚀 Starting automated linting fixes...")
        print("-" * 50)

        # Install required tools if missing
        self.ensure_tools_installed()

        # Run fixes in order
        self.remove_unused_imports()
        self.fix_imports_with_isort()
        self.fix_with_black()
        self.fix_with_ruff()

        # Check what's left
        self.check_remaining_issues()

        # Generate report
        report = self.generate_report()

        print("\n" + "=" * 50)
        print("📊 LINTING FIX REPORT")
        print("=" * 50)
        print(f"✅ Issues Fixed: {report['fixes_applied']}")
        print(f"⚠️  Issues Remaining: {report['issues_remaining']}")

        if self.issues_fixed:
            print("\n✅ Fixed Issues:")
            for fix in self.issues_fixed[:5]:  # Show first 5
                print(f"  - {fix}")
            if len(self.issues_fixed) > 5:
                print(f"  ... and {len(self.issues_fixed) - 5} more")

        if self.issues_remaining:
            print("\n⚠️  Remaining Issues (manual fix needed):")
            for issue in self.issues_remaining[:5]:  # Show first 5
                print(f"  - {issue[:100]}...")  # Truncate long messages
            if len(self.issues_remaining) > 5:
                print(f"  ... and {len(self.issues_remaining) - 5} more")

        print("\n📄 Full report saved to: test_results/linting_report.json")

        return len(self.issues_remaining) == 0

    def ensure_tools_installed(self):
        """Ensure required tools are installed"""
        tools = {
            "black": "black",
            "ruff": "ruff",
            "isort": "isort",
            "autoflake": "autoflake",
            "flake8": "flake8",
            "mypy": "mypy",
        }

        missing = []
        for name, cmd in tools.items():
            code, _, _ = self.run_command([cmd, "--version"])
            if code != 0:
                missing.append(name)

        if missing:
            print(f"📦 Installing missing tools: {', '.join(missing)}")
            self.run_command(
                [sys.executable, "-m", "pip", "install", *missing, "--quiet"]
            )


if __name__ == "__main__":
    fixer = AutoLintFixer()
    success = fixer.run_full_fix()
    sys.exit(0 if success else 1)
