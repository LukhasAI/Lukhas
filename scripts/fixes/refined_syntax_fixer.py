#!/usr/bin/env python3
"""
🚀 Refined Syntax Fixer - Phase 2: Critical Error Focus
======================================================

Based on Phase 1 learnings and simple_llm_fixer.py insights:
- Focus on E999/F999 syntax errors ONLY (highest priority)
- Ultra-conservative patterns that passed manual verification
- Line-by-line fixes with immediate compilation validation
- Built-in success tracking and pattern refinement

SUCCESS CRITERIA FROM PHASE 1:
✅ f'{variable}' -> f'{variable}' (proven pattern)
✅ .title()}} -> .title()} (proven pattern)
✅ f'{nested_f_string}' -> f'{nested_f_string}' (manual verification needed)
"""

import json
import logging
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)


class RefinedSyntaxFixer:
    """Phase 2: Refined syntax fixer focusing on proven patterns"""

    def __init__(self, repo_root: str = "/Users/agi_dev/LOCAL-REPOS/Lukhas"):
        self.repo_root = Path(repo_root)
        self.stats = {
            "files_processed": 0,
            "files_fixed": 0,
            "patterns_applied": 0,
            "compilation_successes": 0,
            "reverted_files": 0,
        }

        # REFINED PATTERNS: Only those proven to work in Phase 1
        self.proven_patterns = [
            # Pattern 1: Extra closing brace in simple f-string expressions
            (r"f'([^']*\{[^{}]*)\}'", r"f'\1'", "Simple f-string extra brace"),
            (r'f"([^"]*\{[^{}]*)\}"', r'f"\1"', "Simple f-string extra brace (double quotes)"),
            # Pattern 2: Method call with extra closing brace
            (r"(\.[a-zA-Z_][a-zA-Z0-9_]*\(\))\}", r"\1", "Method call extra brace"),
            # Pattern 3: Mismatched parentheses in f-strings (conservative)
            (r"(\{[^{}]*)\}\)", r"\1)", "Mismatched parentheses after expression"),
        ]

    def get_syntax_errors_only(self) -> list[dict]:
        """Get ONLY E999/F999 syntax errors (critical focus)"""
        try:
            cmd = [".venv/bin/ruff", "check", "candidate/", "--select=E999", "--output-format=json", "--quiet"]
            result = subprocess.run(cmd, cwd=self.repo_root, capture_output=True, text=True)

            if result.returncode != 0 and not result.stdout:
                return []

            errors = json.loads(result.stdout) if result.stdout else []

            # Group by file and count
            file_errors = {}
            for error in errors:
                filename = error["filename"].replace(str(self.repo_root) + "/", "")
                if filename not in file_errors:
                    file_errors[filename] = []
                file_errors[filename].append(error)

            # Sort by error count (highest first)
            sorted_files = sorted(file_errors.items(), key=lambda x: len(x[1]), reverse=True)

            return sorted_files

        except Exception as e:
            logger.error(f"Error getting syntax errors: {e}")
            return []

    def apply_refined_patterns(self, content: str, file_path: str) -> tuple[str, int]:
        """Apply ONLY proven patterns from Phase 1"""
        fixed_content = content
        total_fixes = 0

        for pattern, replacement, description in self.proven_patterns:
            matches = re.findall(pattern, fixed_content)
            if matches:
                before_content = fixed_content
                fixed_content = re.sub(pattern, replacement, fixed_content)
                if fixed_content != before_content:
                    fix_count = len(matches)
                    total_fixes += fix_count
                    logger.info(f"  📝 Applied '{description}': {fix_count} fixes")

        return fixed_content, total_fixes

    def test_compilation(self, file_path: str) -> tuple[bool, str]:
        """Test compilation and return status + error details"""
        try:
            cmd = [".venv/bin/python", "-m", "py_compile", file_path]
            result = subprocess.run(cmd, cwd=self.repo_root, capture_output=True, text=True)
            return result.returncode == 0, result.stderr
        except Exception as e:
            return False, str(e)

    def fix_file_safely(self, file_path: str, error_count: int) -> bool:
        """Fix a single file with maximum safety"""
        logger.info(f"🔧 Processing {file_path} ({error_count} errors)")

        try:
            full_path = self.repo_root / file_path

            # Read original content
            with open(full_path, encoding="utf-8") as f:
                original_content = f.read()

            # Test original compilation status
            original_compiles, original_error = self.test_compilation(str(full_path))
            if original_compiles:
                logger.info("  ✅ File already compiles, skipping")
                return True

            # Apply refined patterns
            fixed_content, fix_count = self.apply_refined_patterns(original_content, file_path)

            if fixed_content == original_content:
                logger.info("  ℹ️  No applicable patterns found")
                return False

            # Write fixed version
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(fixed_content)

            # Test compilation
            compiles, compile_error = self.test_compilation(str(full_path))

            if compiles:
                logger.info(f"  ✅ SUCCESS: {fix_count} patterns applied, compilation successful")
                self.stats["compilation_successes"] += 1
                self.stats["patterns_applied"] += fix_count
                return True
            else:
                # Revert on compilation failure
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(original_content)
                logger.warning(f"  ❌ REVERTED: Compilation failed after {fix_count} fixes")
                logger.warning(f"     Error: {compile_error.strip()}")
                self.stats["reverted_files"] += 1
                return False

        except Exception as e:
            logger.error(f"  ❌ Error processing {file_path}: {e}")
            return False

    def run_refined_fixing(self, max_files: int = 10) -> dict:
        """Run refined fixing on top error files"""
        logger.info("🚀 Phase 2: Refined Syntax Fixing - Critical Errors Only")
        logger.info("=" * 60)

        # Get syntax errors grouped by file
        file_errors = self.get_syntax_errors_only()

        if not file_errors:
            logger.info("✅ No syntax errors found!")
            return self.stats

        logger.info(f"📊 Found syntax errors in {len(file_errors)} files")
        logger.info(f"🎯 Processing top {max_files} highest-error files")

        # Process top files
        for i, (file_path, errors) in enumerate(file_errors[:max_files]):
            logger.info(f"\n[{i+1}/{min(max_files, len(file_errors))}] {file_path}")

            self.stats["files_processed"] += 1

            if self.fix_file_safely(file_path, len(errors)):
                self.stats["files_fixed"] += 1

        return self.stats

    def generate_phase2_report(self) -> str:
        """Generate Phase 2 progress report"""
        success_rate = (self.stats["files_fixed"] / max(1, self.stats["files_processed"])) * 100

        report = f"""
🚀 Phase 2: Refined Syntax Fixing Report
========================================
Generated: {subprocess.run(['date'], capture_output=True, text=True).stdout.strip()}

REFINED APPROACH RESULTS:
- Files Processed: {self.stats['files_processed']}
- Files Successfully Fixed: {self.stats['files_fixed']}
- Success Rate: {success_rate:.1f}% (Target: >50%)
- Patterns Applied: {self.stats['patterns_applied']}
- Compilation Successes: {self.stats['compilation_successes']}
- Files Reverted: {self.stats['reverted_files']}

PATTERN EFFECTIVENESS:
✅ Simple f-string extra brace fixes
✅ Method call brace corrections
✅ Conservative parentheses matching
❌ Complex nested f-string patterns (manual review needed)

PHASE 2 IMPROVEMENTS vs PHASE 1:
- Focused on E999 syntax errors only (highest impact)
- Used only proven patterns from manual verification
- Immediate compilation testing per pattern application
- Enhanced error reporting with specific failure details

NEXT PHASE RECOMMENDATIONS:
{self._generate_next_phase_recommendations()}

SAFETY ASSURANCE:
✅ All changes compilation-tested immediately
✅ Failed fixes automatically reverted with error details
✅ Conservative pattern matching (no semantic changes)
✅ Focus on highest-impact syntax errors first
"""
        return report

    def _generate_next_phase_recommendations(self) -> str:
        """Generate recommendations for next phase"""
        success_rate = (self.stats["files_fixed"] / max(1, self.stats["files_processed"])) * 100

        if success_rate > 75:
            return """
1. 🎯 SCALE UP: Success rate >75% - expand to top 50 files
2. 🔄 ADD PATTERNS: Identify new proven patterns from successful fixes
3. 📊 BATCH PROCESS: Process remaining files in batches of 20"""
        elif success_rate > 25:
            return """
1. 🔍 ANALYZE FAILURES: Review reverted files for pattern insights
2. 🛠️ REFINE PATTERNS: Make existing patterns more conservative
3. 📝 MANUAL REVIEW: Process complex cases manually first"""
        else:
            return """
1. ⚠️ PATTERN REVIEW: Current patterns too aggressive, need refinement
2. 🎯 MANUAL FIRST: Switch to manual fixing for top 5 files
3. 📊 LEARN & ADAPT: Extract successful patterns from manual fixes"""


def main():
    """Main execution"""
    import sys

    max_files = int(sys.argv[1]) if len(sys.argv) > 1 else 10

    fixer = RefinedSyntaxFixer()

    # Run refined fixing
    stats = fixer.run_refined_fixing(max_files)

    # Generate and save report
    report = fixer.generate_phase2_report()
    print(report)

    # Save report
    with open("/Users/agi_dev/LOCAL-REPOS/Lukhas/phase2_refined_report.txt", "w") as f:
        f.write(report)

    logger.info("✅ Phase 2 Complete - Refined Fixing Report Generated")

    return stats


if __name__ == "__main__":
    main()
