#!/usr/bin/env python3
"""
🎯 Phase 2: Comprehensive Automated Fix Application

Apply automated fixes while excluding the known problematic files.
"""

import os
import subprocess


class Phase2AutoFixer:
    def __init__(self):
        self.problematic_files = {
            "quarantine/critical/override_logic.py",
            "quarantine/encoding/lambda_products_gpt_adapter.py",
            "tools/scripts/enhance_all_modules.py",
            "tools/module_dependency_visualizer.py",
            "candidate/core/safety/predictive_harm_prevention.py",
            "candidate/bridge/adapters/api_documentation_generator.py",
            "products/communication/nias/vendor_portal_backup.py",
        }

        self.safe_fixes = [
            "W292",  # missing-newline-at-end-of-file
            "W293",  # blank-line-with-whitespace
            "F401",  # unused-import
            "SIM102",  # collapsible-if
        ]

        self.fixes_applied = 0
        self.errors_before = 0
        self.errors_after = 0

    def get_clean_python_files(self):
        """Get all Python files excluding problematic ones"""
        all_files = []
        for root, dirs, files in os.walk("."):
            # Skip hidden directories and common excludes
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ["__pycache__", "node_modules"]]

            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.relpath(os.path.join(root, file))
                    if filepath not in self.problematic_files:
                        all_files.append(filepath)

        return all_files

    def get_baseline_stats(self):
        """Get current error statistics"""
        try:
            result = subprocess.run(
                [".venv/bin/python", "-m", "ruff", "check", ".", "--statistics"], capture_output=True, text=True
            )

            lines = result.stdout.strip().split("\n")
            total_errors = 0
            for line in lines:
                if line.strip() and not line.startswith("warning:"):
                    parts = line.split()
                    if parts and parts[0].isdigit():
                        total_errors += int(parts[0])

            self.errors_before = total_errors
            print(f"📊 Baseline errors: {total_errors}")

        except Exception as e:
            print(f"⚠️  Error getting baseline: {e}")

    def apply_safe_fixes_to_files(self, files_batch):
        """Apply safe fixes to a batch of files"""
        if not files_batch:
            return 0

        fixes_applied = 0

        for fix_type in self.safe_fixes:
            try:
                # Apply fix to this batch of files
                cmd = [".venv/bin/python", "-m", "ruff", "check", f"--select={fix_type}", "--fix"] + files_batch

                result = subprocess.run(cmd, capture_output=True, text=True)

                # Count fixes from output
                if fix_type in result.stdout:
                    for line in result.stdout.split("\n"):
                        if fix_type in line and "fixed" in line.lower():
                            try:
                                count = int(line.split()[0])
                                fixes_applied += count
                            except:
                                pass

                print(f"  Applied {fix_type} fixes to batch")

            except Exception as e:
                print(f"⚠️  Error applying {fix_type}: {e}")

        return fixes_applied

    def apply_comprehensive_fixes(self):
        """Apply fixes in manageable batches"""
        print("🚀 Starting Phase 2: Comprehensive Automated Fixes")

        self.get_baseline_stats()

        clean_files = self.get_clean_python_files()
        print(f"📁 Found {len(clean_files)} clean Python files")

        # Process in batches to avoid command line length limits
        batch_size = 50
        total_fixes = 0

        for i in range(0, len(clean_files), batch_size):
            batch = clean_files[i : i + batch_size]
            print(f"\n🔧 Processing batch {i//batch_size + 1} ({len(batch)} files)")

            batch_fixes = self.apply_safe_fixes_to_files(batch)
            total_fixes += batch_fixes

            if batch_fixes > 0:
                print(f"  ✅ Applied {batch_fixes} fixes to this batch")

        self.fixes_applied = total_fixes
        print(f"\n🎯 Total fixes applied: {total_fixes}")

        # Get final stats
        self.get_final_stats()

    def get_final_stats(self):
        """Get final error statistics"""
        try:
            result = subprocess.run(
                [".venv/bin/python", "-m", "ruff", "check", ".", "--statistics"], capture_output=True, text=True
            )

            lines = result.stdout.strip().split("\n")
            total_errors = 0
            for line in lines:
                if line.strip() and not line.startswith("warning:"):
                    parts = line.split()
                    if parts and parts[0].isdigit():
                        total_errors += int(parts[0])

            self.errors_after = total_errors

            improvement = self.errors_before - self.errors_after
            print("\n📊 Final Results:")
            print(f"   Before: {self.errors_before} errors")
            print(f"   After:  {self.errors_after} errors")
            print(f"   Fixed:  {improvement} errors ({improvement/self.errors_before*100:.1f}% improvement)")

        except Exception as e:
            print(f"⚠️  Error getting final stats: {e}")

    def generate_report(self):
        """Generate improvement report"""
        report = f"""# 🎯 Phase 2: Comprehensive Automated Fixes Report

## 📊 Results Summary

- **Files Processed**: Clean Python files (excluding 7 problematic files)
- **Fixes Applied**: {self.fixes_applied} automated improvements
- **Errors Before**: {self.errors_before}
- **Errors After**: {self.errors_after}
- **Improvement**: {self.errors_before - self.errors_after} errors fixed ({(self.errors_before - self.errors_after)/self.errors_before*100:.1f}%)

## ✅ Fix Types Applied

- **W292**: Missing newline at end of file
- **W293**: Blank line with whitespace  
- **F401**: Unused imports
- **SIM102**: Collapsible if statements

## 🎯 Next Steps

1. Commit these automated improvements
2. Address remaining F821 undefined name errors
3. Consider reconstructing the 5 damaged files
4. Continue with targeted manual fixes for complex issues

---
*Phase 2 automated improvements completed successfully*
"""

        with open("PHASE2_COMPLETION_REPORT.md", "w") as f:
            f.write(report)

        print("\n📄 Report saved: PHASE2_COMPLETION_REPORT.md")


if __name__ == "__main__":
    fixer = Phase2AutoFixer()
    fixer.apply_comprehensive_fixes()
    fixer.generate_report()
