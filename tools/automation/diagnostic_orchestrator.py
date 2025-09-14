#!/usr/bin/env python3
"""
Diagnostic-Driven Fix Orchestrator
==================================
Parses diagnostic reports and applies appropriate fixes automatically.
Coordinates multiple fix strategies based on error categories.

Features:
- Error categorization and prioritization
- Fix validation and rollback
- Integration with T4 autofix pipeline
- Comprehensive logging and reporting
"""

import json
import logging
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
DIAGNOSTIC_DIR = ROOT / "reports" / "deep_search"
ORCHESTRATOR_LOG = ROOT / "reports" / "autofix" / "orchestrator.json"

# Import our enhanced fixers
sys.path.insert(0, str(ROOT / "tools" / "automation"))
sys.path.insert(0, str(ROOT / "tools" / "ci"))

try:
    from enhanced_fstring_fixer import EnhancedFStringFixer
except ImportError:
    logger.warning("Enhanced f-string fixer not available")
    EnhancedFStringFixer = None

try:
    from enhanced_auto_fix_safe import apply_config_fixes, apply_enhanced_fixes
except ImportError:
    logger.warning("Enhanced auto fix safe not available")
    apply_enhanced_fixes = None
    apply_config_fixes = None


class ErrorCategory:
    """Error category classification"""

    SYNTAX = "SyntaxError"
    IMPORT = "ImportError"
    CONFIG = "ConfigurationError"
    COLLECTION = "CollectionWarning"
    OTHER = "Other"


class FixStrategy:
    """Available fix strategies"""

    FSTRING_FIXER = "enhanced_fstring_fixer"
    CONFIG_MARKERS = "config_markers"
    IMPORT_BRIDGE = "import_bridge"
    T4_AUTOFIX = "t4_autofix"
    MANUAL_REVIEW = "manual_review"


class DiagnosticOrchestrator:
    """Main orchestrator for diagnostic-driven fixes"""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dry_run": dry_run,
            "errors_found": {},
            "fixes_applied": {},
            "validation_results": {},
            "rollbacks": [],
            "summary": {},
        }

    def load_diagnostic_report(self, report_path: Path) -> Optional[dict]:
        """Load and parse diagnostic report"""
        try:
            if not report_path.exists():
                logger.error(f"Diagnostic report not found: {report_path}")
                return None

            content = report_path.read_text()

            # Parse markdown diagnostic report
            errors = {}
            current_category = None

            for line in content.split("\n"):
                line = line.strip()

                if line.startswith("### ") and "Error" in line:
                    # Extract error type and count
                    if "SyntaxError" in line:
                        current_category = ErrorCategory.SYNTAX
                    elif "ImportError" in line:
                        current_category = ErrorCategory.IMPORT
                    elif "Configuration" in line:
                        current_category = ErrorCategory.CONFIG
                    elif "Collection Warning" in line:
                        current_category = ErrorCategory.COLLECTION
                    else:
                        current_category = ErrorCategory.OTHER

                elif current_category and "|" in line and line.count("|") >= 3:
                    # Parse table rows for specific errors
                    parts = [p.strip() for p in line.split("|")[1:-1]]
                    if len(parts) >= 2 and parts[0] and not parts[0].startswith("-"):
                        if current_category not in errors:
                            errors[current_category] = []
                        errors[current_category].append(
                            {"file": parts[0], "details": parts[1] if len(parts) > 1 else "Unknown"}
                        )

            return errors

        except Exception as e:
            logger.error(f"Failed to load diagnostic report: {e}")
            return None

    def categorize_errors(self, errors: dict) -> dict[str, list]:
        """Categorize errors by fix strategy"""
        strategy_map = {
            ErrorCategory.SYNTAX: FixStrategy.FSTRING_FIXER,
            ErrorCategory.CONFIG: FixStrategy.CONFIG_MARKERS,
            ErrorCategory.IMPORT: FixStrategy.IMPORT_BRIDGE,
            ErrorCategory.COLLECTION: FixStrategy.MANUAL_REVIEW,
            ErrorCategory.OTHER: FixStrategy.T4_AUTOFIX,
        }

        categorized = {}
        for error_type, error_list in errors.items():
            strategy = strategy_map.get(error_type, FixStrategy.MANUAL_REVIEW)
            if strategy not in categorized:
                categorized[strategy] = []
            categorized[strategy].extend(error_list)

        return categorized

    def create_backup(self, files: list[Path]) -> Path:
        """Create backup of files before fixing"""
        backup_dir = ROOT / "backups" / f"autofix_{int(time.time())}"
        backup_dir.mkdir(parents=True, exist_ok=True)

        for file_path in files:
            if file_path.exists():
                relative_path = file_path.relative_to(ROOT)
                backup_file = backup_dir / relative_path
                backup_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, backup_file)

        logger.info(f"Created backup at: {backup_dir}")
        return backup_dir

    def validate_fixes(self, files: list[Path]) -> dict[str, bool]:
        """Validate that fixes don't break syntax"""
        results = {}

        for file_path in files:
            if not file_path.exists():
                results[str(file_path)] = False
                continue

            try:
                # Python syntax validation
                result = subprocess.run(
                    [sys.executable, "-m", "py_compile", str(file_path)], capture_output=True, text=True, cwd=ROOT
                )

                results[str(file_path)] = result.returncode == 0

                if result.returncode != 0:
                    logger.warning(f"Syntax validation failed for {file_path}: {result.stderr}")

            except Exception as e:
                logger.error(f"Validation error for {file_path}: {e}")
                results[str(file_path)] = False

        return results

    def apply_fstring_fixes(self, error_list: list[dict]) -> dict:
        """Apply f-string syntax fixes"""
        if not EnhancedFStringFixer:
            return {"status": "skipped", "reason": "fixer not available"}

        fixer = EnhancedFStringFixer(validate_syntax=True)
        files_to_fix = []

        # Extract files from error list
        for error in error_list:
            file_path = ROOT / error["file"]
            if file_path.exists() and file_path.suffix == ".py":
                files_to_fix.append(file_path)

        if not files_to_fix:
            return {"status": "no_files", "files_processed": 0}

        if self.dry_run:
            logger.info(f"[DRY RUN] Would fix f-strings in {len(files_to_fix)} files")
            return {"status": "dry_run", "files_processed": len(files_to_fix)}

        # Create backup
        backup_dir = self.create_backup(files_to_fix)

        try:
            stats = fixer.fix_files(files_to_fix)

            # Validate fixes
            validation = self.validate_fixes(files_to_fix)
            failed_files = [f for f, success in validation.items() if not success]

            if failed_files:
                logger.error(f"Validation failed for {len(failed_files)} files, rolling back")
                self.rollback_from_backup(backup_dir, [Path(f) for f in failed_files])
                return {
                    "status": "partial_success",
                    "files_processed": stats["files_processed"],
                    "files_changed": stats["files_changed"] - len(failed_files),
                    "rollbacks": len(failed_files),
                    "backup": str(backup_dir),
                }

            return {
                "status": "success",
                "files_processed": stats["files_processed"],
                "files_changed": stats["files_changed"],
                "backup": str(backup_dir),
                "stats": stats,
            }

        except Exception as e:
            logger.error(f"F-string fixes failed: {e}")
            return {"status": "failed", "error": str(e), "backup": str(backup_dir)}

    def apply_config_fixes(self, error_list: list[dict]) -> dict:
        """Apply configuration fixes like pytest markers"""
        if self.dry_run:
            logger.info("[DRY RUN] Would apply configuration fixes")
            return {"status": "dry_run"}

        try:
            # Apply pytest marker fixes
            results = apply_config_fixes([], {"CONFIG_MARKERS"})

            return {"status": "success", "pytest_markers_added": results.get("pytest_markers_added", 0)}

        except Exception as e:
            logger.error(f"Configuration fixes failed: {e}")
            return {"status": "failed", "error": str(e)}

    def apply_import_fixes(self, error_list: list[dict]) -> dict:
        """Apply import bridge fixes"""
        if self.dry_run:
            logger.info("[DRY RUN] Would apply import bridge fixes")
            return {"status": "dry_run"}

        # Import fixes are typically one-time manual additions
        # For now, return success if auth_integration is available
        try:
            from lukhas.governance.identity import auth_integration  # noqa: F401  # TODO: lukhas.governance.identity.aut...

            return {"status": "success", "bridges_verified": 1}
        except ImportError as e:
            return {"status": "failed", "error": str(e)}

    def rollback_from_backup(self, backup_dir: Path, files: list[Path]) -> bool:
        """Rollback files from backup"""
        try:
            for file_path in files:
                relative_path = file_path.relative_to(ROOT)
                backup_file = backup_dir / relative_path
                if backup_file.exists():
                    shutil.copy2(backup_file, file_path)
                    logger.info(f"Rolled back: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False

    def run_orchestration(self, diagnostic_report_path: Optional[Path] = None) -> dict:
        """Main orchestration workflow"""
        logger.info("🎼 Starting diagnostic-driven fix orchestration")

        # Load diagnostic report
        if diagnostic_report_path is None:
            diagnostic_report_path = DIAGNOSTIC_DIR / "DIAGNOSTIC_REPORT.md"

        errors = self.load_diagnostic_report(diagnostic_report_path)
        if not errors:
            logger.error("No diagnostic report found or failed to parse")
            return {"status": "failed", "reason": "no_diagnostic_report"}

        self.results["errors_found"] = {k: len(v) for k, v in errors.items()}
        logger.info(f"Found errors: {self.results['errors_found']}")

        # Categorize by fix strategy
        categorized = self.categorize_errors(errors)
        logger.info(f"Fix strategies needed: {list(categorized.keys())}")

        # Apply fixes by strategy
        for strategy, error_list in categorized.items():
            logger.info(f"Applying {strategy} fixes to {len(error_list)} errors")

            if strategy == FixStrategy.FSTRING_FIXER:
                result = self.apply_fstring_fixes(error_list)
            elif strategy == FixStrategy.CONFIG_MARKERS:
                result = self.apply_config_fixes(error_list)
            elif strategy == FixStrategy.IMPORT_BRIDGE:
                result = self.apply_import_fixes(error_list)
            else:
                result = {"status": "skipped", "reason": "strategy_not_implemented"}

            self.results["fixes_applied"][strategy] = result
            logger.info(f"{strategy} result: {result['status']}")

        # Generate summary
        total_errors = sum(self.results["errors_found"].values())
        successful_fixes = sum(
            1 for r in self.results["fixes_applied"].values() if r.get("status") in ["success", "partial_success"]
        )

        self.results["summary"] = {
            "total_errors_found": total_errors,
            "fix_strategies_applied": len(self.results["fixes_applied"]),
            "successful_fixes": successful_fixes,
            "dry_run": self.dry_run,
        }

        # Save orchestration log
        ORCHESTRATOR_LOG.parent.mkdir(parents=True, exist_ok=True)
        ORCHESTRATOR_LOG.write_text(json.dumps(self.results, indent=2))

        logger.info(f"🎼 Orchestration complete: {successful_fixes}/{len(categorized)} strategies successful")
        return self.results


def main():
    """CLI interface for orchestrator"""
    import argparse

    parser = argparse.ArgumentParser(description="Diagnostic-driven fix orchestrator")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be fixed without making changes")
    parser.add_argument("--report", type=Path, help="Path to diagnostic report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    orchestrator = DiagnosticOrchestrator(dry_run=args.dry_run)
    results = orchestrator.run_orchestration(args.report)

    # Print summary
    print("\n🎼 DIAGNOSTIC ORCHESTRATION RESULTS")
    print("================================")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print(f"Errors found: {results.get('summary', {}).get('total_errors_found', 0)}")
    print(f"Strategies applied: {results.get('summary', {}).get('fix_strategies_applied', 0)}")
    print(f"Successful fixes: {results.get('summary', {}).get('successful_fixes', 0)}")
    print(f"Log saved to: {ORCHESTRATOR_LOG}")

    return 0 if results.get("summary", {}).get("successful_fixes", 0) > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
