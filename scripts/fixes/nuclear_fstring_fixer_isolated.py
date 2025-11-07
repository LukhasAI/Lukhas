#!/usr/bin/env python3
"""
💥 NUCLEAR F-STRING FIXER - ISOLATED & DRY RUN CAPABLE
More aggressive pattern matching with full isolation and dry run mode
"""
from __future__ import annotations

import ast
import json
import os
import re
import shutil
from pathlib import Path


class NuclearFStringFixer:
    """Nuclear approach with isolation and dry run safeguards"""

    def __init__(self, dry_run: bool = True, isolation_dir: str | None = None):
        self.dry_run = dry_run
        self.isolation_dir = isolation_dir or f"/tmp/lukhas_nuclear_test_{os.getpid()}"
        self.fixes_applied = 0
        self.files_processed = 0
        self.validation_failures = 0
        self.dangerous_patterns = []
        self.safe_patterns = []

        # Create isolation directory
        if os.path.exists(self.isolation_dir):
            shutil.rmtree(self.isolation_dir)
        os.makedirs(self.isolation_dir, exist_ok=True)

        print(f"🏝️  Isolation directory: {self.isolation_dir}")

    def get_nuclear_patterns(self) -> list[tuple[str, str, str]]:
        """More aggressive f-string patterns with risk classification"""
        return [
            # SAFE PATTERNS - High confidence fixes
            (r'f"([^"]*)\{([^}]*time\.time)\(\}([^"]*)"', r'f"\1{\2()}\3"', "SAFE"),
            (r'f"([^"]*)\{([^}]*uuid\.uuid4)\(\}([^"]*)"', r'f"\1{\2()}\3"', "SAFE"),
            (r'f"([^"]*)\{([^}]*datetime\.now[^}]*timestamp)\(\}([^"]*)"', r'f"\1{\2()}\3"', "SAFE"),
            (r'f"([^"]*)\{([^}]*\.upper)\(\}([^"]*)"', r'f"\1{\2()}\3"', "SAFE"),
            (r'f"([^"]*)\{([^}]*\.lower)\(\}([^"]*)"', r'f"\1{\2()}\3"', "SAFE"),
            (r'f"([^"]*)\{([^}]*\.strip)\(\}([^"]*)"', r'f"\1{\2()}\3"', "SAFE"),
            # MEDIUM RISK - Common function patterns
            (r'f"([^"]*)\{len\(([^}]+)\}([^"]*)"', r'f"\1{len(\2)}\3"', "MEDIUM"),
            (r'f"([^"]*)\{hash\(([^}]+)\}([^"]*)"', r'f"\1{hash(\2)}\3"', "MEDIUM"),
            (r'f"([^"]*)\{int\(([^}]+)\}([^"]*)"', r'f"\1{int(\2)}\3"', "MEDIUM"),
            (r'f"([^"]*)\{str\(([^}]+)\}([^"]*)"', r'f"\1{str(\2)}\3"', "MEDIUM"),
            (r'f"([^"]*)\{float\(([^}]+)\}([^"]*)"', r'f"\1{float(\2)}\3"', "MEDIUM"),
            (r'f"([^"]*)\{bool\(([^}]+)\}([^"]*)"', r'f"\1{bool(\2)}\3"', "MEDIUM"),
            # HIGH RISK - Type and attribute patterns
            (r'f"([^"]*)\{type\(([^}]+)\}([^"]*)"', r'f"\1{type(\2)}\3"', "HIGH"),
            (r'f"([^"]*)\{([^}]+)\.get\(([^}]+)\}([^"]*)"', r'f"\1{\2.get(\3)}\4"', "HIGH"),
            (r'f"([^"]*)\{([^}]+)\.__name__\}([^"]*)"', r'f"\1{\2.__name__}\3"', "MEDIUM"),
            # NUCLEAR - Most aggressive patterns for complex cases
            (r'f"([^"]*)\{([^{}]+)\(([^}]*)\}([^"]*)"', r'f"\1{\2(\3)}\4"', "NUCLEAR"),
        ]

    def isolate_and_test(self, file_path: str, original_content: str, fixed_content: str) -> bool:
        """Test fixes in isolation before applying"""

        # Create isolated test file
        isolated_file = os.path.join(self.isolation_dir, os.path.basename(file_path))

        try:
            # Write fixed content to isolated file
            with open(isolated_file, "w", encoding="utf-8") as f:
                f.write(fixed_content)

            # Test syntax in isolation
            ast.parse(fixed_content)

            # Additional smoke tests for imports
            try:
                # Test basic import if it's a module
                if file_path.endswith("__init__.py"):
                    module_name = os.path.basename(os.path.dirname(file_path))
                    if module_name not in ["tests", "test", ".pytest_cache"]:
                        # Basic import test in subprocess for safety
                        import subprocess

                        result = subprocess.run(
                            [
                                "python3",
                                "-c",
                                f'import sys; sys.path.insert(0, "{os.path.dirname(isolated_file)}"); import {module_name}',
                            ],
                            capture_output=True,
                            timeout=5,
                            cwd=self.isolation_dir,
                        )
                        if result.returncode != 0 and "SyntaxError" in result.stderr.decode():
                            return False

            except (subprocess.TimeoutExpired, Exception):
                # Import test failed, but syntax was OK, so continue
                pass

            return True

        except SyntaxError as e:
            print(f"❌ Isolation test failed for {file_path}: {e}")
            return False
        except Exception as e:
            print(f"⚠️  Isolation test error for {file_path}: {e}")
            return False

    def nuclear_fix_fstring(self, content: str, file_path: str) -> tuple[str, int, list[str]]:
        """Nuclear f-string fixes with risk assessment"""
        fixes_count = 0
        applied_patterns = []
        patterns = self.get_nuclear_patterns()

        for pattern, replacement, risk_level in patterns:
            try:
                matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
                if matches:
                    new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)

                    # Risk assessment
                    if risk_level == "NUCLEAR" and len(matches) > 10:
                        print(f"⚠️  {risk_level} pattern would affect {len(matches)} locations in {file_path}")
                        if not self.dry_run and (not self.isolate_and_test(file_path, content, new_content)):
                            # Extra validation for nuclear patterns
                            continue

                    if new_content != content:
                        fixes_count += len(matches)
                        content = new_content
                        applied_patterns.append(f"{risk_level}: {len(matches)} fixes")

                        if risk_level == "HIGH":
                            self.dangerous_patterns.append((file_path, pattern, len(matches)))
                        else:
                            self.safe_patterns.append((file_path, pattern, len(matches)))

            except re.error as e:
                print(f"⚠️  Regex error in pattern {pattern}: {e}")
                continue

        return content, fixes_count, applied_patterns

    def get_critical_files(self) -> list[str]:
        """Get files prioritized by blocking impact"""

        # Files that are currently blocking functionality
        blocking_files = [
            "governance/__init__.py",
            "products/__init__.py",
            "business/__init__.py",
            "security/__init__.py",
        ]

        # Core lukhas namespace files
        lukhas_core = list(Path("lukhas").rglob("*.py"))[:50]  # Limit to 50 most critical

        # High-impact candidate files
        candidate_priority = [
            "candidate/consciousness/*.py",
            "candidate/memory/*.py",
            "candidate/agents/*.py",
        ]

        all_files = []

        # Add blocking files first
        for pattern in blocking_files:
            files = list(Path(".").glob(pattern))
            all_files.extend([str(f) for f in files])

        # Add lukhas core
        all_files.extend([str(f) for f in lukhas_core])

        # Add candidate priority
        for pattern in candidate_priority:
            files = list(Path(".").glob(pattern))
            all_files.extend([str(f) for f in files[:20]])  # Limit each pattern

        return list(set(all_files))  # Remove duplicates

    def process_file_nuclear(self, file_path: str) -> dict:
        """Process file with nuclear approach"""
        result = {
            "file": file_path,
            "success": False,
            "fixes_applied": 0,
            "patterns_used": [],
            "risk_level": "SAFE",
            "validation_passed": False,
        }

        try:
            # Read original content
            with open(file_path, encoding="utf-8") as f:
                original_content = f.read()

            # Pre-validation
            try:
                ast.parse(original_content)
                result["originally_valid"] = True
            except SyntaxError:
                result["originally_valid"] = False

            # Apply nuclear fixes
            fixed_content, fixes_count, patterns_used = self.nuclear_fix_fstring(original_content, file_path)

            if fixes_count == 0:
                result["success"] = True
                return result

            # Determine risk level
            risk_levels = [p.split(":")[0] for p in patterns_used]
            if "NUCLEAR" in risk_levels:
                result["risk_level"] = "NUCLEAR"
            elif "HIGH" in risk_levels:
                result["risk_level"] = "HIGH"
            elif "MEDIUM" in risk_levels:
                result["risk_level"] = "MEDIUM"

            # Isolation testing
            validation_passed = self.isolate_and_test(file_path, original_content, fixed_content)
            result["validation_passed"] = validation_passed

            if not validation_passed:
                print(f"❌ Validation failed for {file_path}, skipping")
                return result

            # Apply fixes if not dry run
            if not self.dry_run and validation_passed:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(fixed_content)
                print(f"💥 NUCLEAR: {file_path} - {fixes_count} fixes applied ({result['risk_level']})")
            else:
                print(f"🔍 DRY RUN: {file_path} - {fixes_count} fixes would be applied ({result['risk_level']})")

            result["success"] = True
            result["fixes_applied"] = fixes_count
            result["patterns_used"] = patterns_used
            self.fixes_applied += fixes_count

        except Exception as e:
            print(f"❌ Nuclear processing failed for {file_path}: {e}")

        self.files_processed += 1
        return result

    def run_nuclear_fixes(self, max_files: int = 100):
        """Run nuclear fixes with full isolation"""
        print("💥 NUCLEAR F-STRING FIXER - ISOLATED MODE")
        print("=" * 60)
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE EXECUTION'}")
        print(f"Isolation: {self.isolation_dir}")
        print()

        critical_files = self.get_critical_files()[:max_files]
        results = []

        print(f"🎯 Processing {len(critical_files)} critical files")
        print()

        for file_path in critical_files:
            if os.path.exists(file_path):
                result = self.process_file_nuclear(file_path)
                results.append(result)

        # Results summary
        self.print_nuclear_summary(results)

        # Save results for analysis
        results_file = os.path.join(self.isolation_dir, "nuclear_results.json")
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"📊 Detailed results saved to: {results_file}")

        return results

    def print_nuclear_summary(self, results: list[dict]):
        """Print comprehensive results summary"""
        print()
        print("📊 NUCLEAR FIXING RESULTS:")
        print("=" * 40)

        total_files = len(results)
        successful = sum(1 for r in results if r["success"])
        total_fixes = sum(r["fixes_applied"] for r in results)
        validation_passed = sum(1 for r in results if r.get("validation_passed", False))

        print(f"Files processed: {total_files}")
        print(f"Files successfully processed: {successful}")
        print(f"Total fixes applied: {total_fixes}")
        print(f"Validation success rate: {(validation_passed/total_files*100):.1f}%")

        # Risk breakdown
        risk_counts = {}
        for result in results:
            risk = result.get("risk_level", "SAFE")
            risk_counts[risk] = risk_counts.get(risk, 0) + 1

        print()
        print("🎯 Risk Level Breakdown:")
        for risk, count in sorted(risk_counts.items()):
            print(f"  {risk}: {count} files")

        # Top fixes by file
        print()
        print("🏆 Top Fixes by File:")
        top_fixes = sorted(results, key=lambda x: x["fixes_applied"], reverse=True)[:10]
        for result in top_fixes:
            if result["fixes_applied"] > 0:
                print(f"  {result['file']}: {result['fixes_applied']} fixes ({result['risk_level']})")

    def cleanup_isolation(self):
        """Clean up isolation directory"""
        if os.path.exists(self.isolation_dir):
            shutil.rmtree(self.isolation_dir)
            print(f"🧹 Cleaned up isolation directory: {self.isolation_dir}")


def main():
    """Main nuclear fixer execution"""
    import sys

    # Default to dry run for safety
    dry_run = "--live" not in sys.argv
    max_files = 50 if "--conservative" in sys.argv else 100

    print("💥 NUCLEAR F-STRING FIXER")
    print("=" * 50)

    if dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")
    else:
        print("⚠️  LIVE MODE - Files will be modified!")
        response = input("Continue? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            return

    fixer = NuclearFStringFixer(dry_run=dry_run)

    try:
        results = fixer.run_nuclear_fixes(max_files=max_files)

        if not dry_run and any(r["fixes_applied"] > 0 for r in results):
            print("\n🧪 Recommend running functional tests to verify improvements")
            print("Command: python3 functional_test_suite.py")

    finally:
        fixer.cleanup_isolation()


if __name__ == "__main__":
    main()
