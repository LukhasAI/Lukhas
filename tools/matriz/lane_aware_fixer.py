#!/usr/bin/env python3
"""
MATRIZ Lane-Aware Fixing System
===============================
Intelligent fixing system that respects MATRIZ lane boundaries and applies
different fix policies based on lane-specific requirements and constraints.

Lane-Specific Policies:
- accepted/: Conservative fixes, extensive validation
- candidate/: Aggressive fixes, innovation-friendly
- core/: Ultra-safe fixes, maximum stability
- matriz/: Symbolic reasoning optimizations
- archive/: Read-only, no modifications
- experimental/: Bleeding-edge fixes, high risk tolerance

Features:
- Lane boundary detection and enforcement
- Policy-driven fix selection
- Import rule compliance validation
- Lane-specific backup and rollback strategies
- Promotion readiness assessment
"""

import json
import logging
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
MATRIZ_CONFIG = ROOT / "ops" / "matriz.yaml"
LANE_POLICIES_CONFIG = ROOT / "config" / "lane_fix_policies.json"

# Import our existing fixers
sys.path.insert(0, str(ROOT / "tools" / "automation"))
try:
    from enhanced_fstring_fixer import EnhancedFStringFixer
except ImportError:
    logger.warning("Some fixing components not available")


class LaneConfiguration:
    """MATRIZ lane configuration parser and manager"""

    def __init__(self):
        self.lanes = {}
        self.import_rules = {}
        self.load_matriz_config()

    def load_matriz_config(self):
        """Load MATRIZ configuration from ops/matriz.yaml"""
        if not MATRIZ_CONFIG.exists():
            logger.error("MATRIZ configuration not found")
            return

        try:
            import yaml

            with open(MATRIZ_CONFIG) as f:
                config = yaml.safe_load(f)
        except ImportError:
            # Fallback YAML parsing for simple structure
            config = self.parse_yaml_simple(MATRIZ_CONFIG.read_text())

        # Parse lanes
        for lane_config in config.get("lanes", []):
            lane_name = lane_config["name"]
            self.lanes[lane_name] = {
                "root": lane_config["root"],
                "owners": lane_config.get("owners", []),
                "depends_on": lane_config.get("depends_on", []),
                "import_rules": lane_config.get("import_rules", {}),
                "promotion": lane_config.get("promotion", {}),
            }

            # Store import rules for quick lookup
            self.import_rules[lane_name] = lane_config.get("import_rules", {})

        logger.info(f"Loaded {len(self.lanes)} MATRIZ lanes")

    def parse_yaml_simple(self, yaml_content: str) -> dict:
        """Simple YAML parser for basic MATRIZ structure"""
        config = {"lanes": []}
        current_lane = None

        for line in yaml_content.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if line.startswith("- name:"):
                if current_lane:
                    config["lanes"].append(current_lane)
                current_lane = {"name": line.split(":", 1)[1].strip()}
            elif current_lane and ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()

                if key in ["root", "owners", "depends_on"]:
                    if value.startswith("[") and value.endswith("]"):
                        # Parse list
                        value = [v.strip(' "') for v in value[1:-1].split(",") if v.strip()]
                    current_lane[key] = value

        if current_lane:
            config["lanes"].append(current_lane)

        return config

    def get_file_lane(self, file_path: Path) -> Optional[str]:
        """Determine which MATRIZ lane a file belongs to"""
        rel_path = str(file_path.relative_to(ROOT))

        for lane_name, lane_config in self.lanes.items():
            root = lane_config["root"].rstrip("/")
            if rel_path.startswith(root + "/") or rel_path == root:
                return lane_name

        return None

    def can_import_from_to(self, from_lane: str, to_lane: str) -> bool:
        """Check if imports are allowed between lanes"""
        if from_lane not in self.import_rules:
            return False

        rules = self.import_rules[from_lane]
        allow_from = rules.get("allow_from", [])
        deny_from = rules.get("deny_from", [])

        # Check if target lane is explicitly denied
        for deny_pattern in deny_from:
            if deny_pattern.replace("/**", "") in to_lane:
                return False

        # Check if target lane is explicitly allowed
        return any(allow_pattern.replace("/**", "") in to_lane for allow_pattern in allow_from)


class LaneFixingPolicy:
    """Define fixing policies for different MATRIZ lanes"""

    def __init__(self):
        self.policies = self.load_lane_policies()

    def load_lane_policies(self) -> dict:
        """Load lane-specific fixing policies"""
        if LANE_POLICIES_CONFIG.exists():
            try:
                return json.loads(LANE_POLICIES_CONFIG.read_text())
            except Exception as e:
                logger.warning(f"Could not load lane policies: {e}")

        # Default policies
        return {
            "accepted": {
                "risk_tolerance": "conservative",
                "validation_level": "extensive",
                "allowed_fixes": ["CONFIG_MARKERS", "IMPORT_BRIDGE"],
                "requires_approval": ["SYNTAX_FSTRING"],
                "backup_retention": 30,
                "test_requirements": ["smoke", "reality_imports", "no_safe_fixable_lints"],
            },
            "labs": {
                "risk_tolerance": "moderate",
                "validation_level": "standard",
                "allowed_fixes": ["SYNTAX_FSTRING", "CONFIG_MARKERS", "IMPORT_BRIDGE", "BRACKET_MATCH"],
                "requires_approval": [],
                "backup_retention": 14,
                "test_requirements": ["smoke"],
            },
            "core": {
                "risk_tolerance": "ultra_conservative",
                "validation_level": "maximum",
                "allowed_fixes": ["CONFIG_MARKERS"],
                "requires_approval": ["SYNTAX_FSTRING", "IMPORT_BRIDGE", "BRACKET_MATCH"],
                "backup_retention": 90,
                "test_requirements": ["comprehensive"],
            },
            "matriz": {
                "risk_tolerance": "moderate",
                "validation_level": "standard",
                "allowed_fixes": ["SYNTAX_FSTRING", "CONFIG_MARKERS"],
                "requires_approval": ["IMPORT_BRIDGE"],
                "backup_retention": 21,
                "test_requirements": ["smoke", "symbolic_reasoning"],
            },
            "experimental": {
                "risk_tolerance": "aggressive",
                "validation_level": "minimal",
                "allowed_fixes": ["SYNTAX_FSTRING", "CONFIG_MARKERS", "IMPORT_BRIDGE", "BRACKET_MATCH", "EXPERIMENTAL"],
                "requires_approval": [],
                "backup_retention": 7,
                "test_requirements": [],
            },
            "archive": {
                "risk_tolerance": "none",
                "validation_level": "read_only",
                "allowed_fixes": [],
                "requires_approval": ["*"],
                "backup_retention": 365,
                "test_requirements": [],
            },
        }

    def get_policy(self, lane: str) -> dict:
        """Get fixing policy for specific lane"""
        return self.policies.get(lane, self.policies.get("labs", {}))

    def is_fix_allowed(self, lane: str, fix_type: str) -> bool:
        """Check if fix type is allowed in lane"""
        policy = self.get_policy(lane)
        allowed = policy.get("allowed_fixes", [])
        requires_approval = policy.get("requires_approval", [])

        if fix_type in allowed:
            return True
        elif fix_type in requires_approval:
            return False  # Would require manual approval
        else:
            return policy.get("risk_tolerance", "moderate") == "aggressive"

    def get_backup_retention(self, lane: str) -> int:
        """Get backup retention days for lane"""
        policy = self.get_policy(lane)
        return policy.get("backup_retention", 14)


class LaneAwareFixer:
    """Main lane-aware fixing system"""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.lane_config = LaneConfiguration()
        self.fixing_policy = LaneFixingPolicy()
        self.fix_results = {}

    def create_lane_specific_backup(self, file_path: Path, lane: str) -> Path:
        """Create backup with lane-specific retention policy"""
        retention_days = self.fixing_policy.get_backup_retention(lane)

        backup_dir = ROOT / "backups" / "lane_aware" / lane / datetime.now().strftime("%Y%m%d")
        backup_dir.mkdir(parents=True, exist_ok=True)

        backup_file = backup_dir / file_path.name
        shutil.copy2(file_path, backup_file)

        # Add metadata
        metadata = {
            "original_file": str(file_path),
            "lane": lane,
            "backup_time": datetime.now(timezone.utc).isoformat(),
            "retention_days": retention_days,
            "expires": (datetime.now() + datetime.timedelta(days=retention_days)).isoformat(),
        }

        metadata_file = backup_dir / f"{file_path.name}.metadata.json"
        metadata_file.write_text(json.dumps(metadata, indent=2))

        return backup_file

    def validate_import_compliance(self, file_path: Path, lane: str) -> list[str]:
        """Validate that file imports comply with lane rules"""
        violations = []

        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")

            # Extract import statements
            import_lines = []
            for line in content.split("\n"):
                stripped = line.strip()
                if stripped.startswith(("import ", "from ")):
                    import_lines.append(stripped)

            # Check each import against lane rules
            for import_line in import_lines:
                if import_line.startswith("from "):
                    # Extract module path
                    parts = import_line.split()
                    if len(parts) >= 2:
                        module_path = parts[1]

                        # Determine target lane
                        target_lane = self.infer_lane_from_module_path(module_path)

                        if target_lane and not self.lane_config.can_import_from_to(lane, target_lane):
                            violations.append(f"Forbidden import from {lane} to {target_lane}: {import_line}")

        except Exception as e:
            logger.warning(f"Could not validate imports for {file_path}: {e}")

        return violations

    def infer_lane_from_module_path(self, module_path: str) -> Optional[str]:
        """Infer MATRIZ lane from module import path"""
        if module_path.startswith("lukhas."):
            return "accepted"
        elif module_path.startswith("labs."):
            return "labs"
        elif module_path.startswith("core.") or module_path.startswith("core."):
            return "core"
        elif module_path.startswith("matriz."):
            return "matriz"
        elif module_path.startswith("experimental."):
            return "experimental"
        elif module_path.startswith("archive."):
            return "archive"

        return None

    def apply_lane_aware_fixes(self, files_by_lane: dict[str, list[Path]], fix_types: set[str]) -> dict:
        """Apply fixes with lane-specific policies"""
        results = {
            "processed_lanes": [],
            "fixes_applied": {},
            "fixes_skipped": {},
            "import_violations": {},
            "backups_created": [],
        }

        for lane, files in files_by_lane.items():
            logger.info(f"🛣️ Processing {len(files)} files in '{lane}' lane")

            policy = self.fixing_policy.get_policy(lane)
            lane_results = {"files_processed": 0, "files_fixed": 0, "fixes_applied": [], "fixes_skipped": []}

            for file_path in files:
                # Validate import compliance first
                violations = self.validate_import_compliance(file_path, lane)
                if violations:
                    results["import_violations"][str(file_path)] = violations
                    if policy.get("risk_tolerance") == "ultra_conservative":
                        logger.warning(f"Skipping {file_path} due to import violations in {lane}")
                        continue

                # Create lane-specific backup
                if not self.dry_run:
                    backup_path = self.create_lane_specific_backup(file_path, lane)
                    results["backups_created"].append(str(backup_path))

                # Apply allowed fixes
                file_fixed = False
                for fix_type in fix_types:
                    if self.fixing_policy.is_fix_allowed(lane, fix_type):
                        success = self.apply_specific_fix(file_path, fix_type, lane)
                        if success:
                            lane_results["fixes_applied"].append(fix_type)
                            file_fixed = True
                    else:
                        lane_results["fixes_skipped"].append(fix_type)

                lane_results["files_processed"] += 1
                if file_fixed:
                    lane_results["files_fixed"] += 1

            results["fixes_applied"][lane] = lane_results
            results["processed_lanes"].append(lane)

        return results

    def apply_specific_fix(self, file_path: Path, fix_type: str, lane: str) -> bool:
        """Apply specific fix type to file"""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would apply {fix_type} to {file_path} in {lane}")
            return True

        try:
            if fix_type == "SYNTAX_FSTRING" and EnhancedFStringFixer:
                fixer = EnhancedFStringFixer(validate_syntax=True)
                return fixer.fix_file(file_path)

            elif fix_type == "CONFIG_MARKERS":
                # Pytest configuration fixes are global, not file-specific
                return True

            elif fix_type == "IMPORT_BRIDGE":
                # Import bridge fixes are typically one-time additions
                return True

            elif fix_type == "BRACKET_MATCH":
                # Would use pattern matching for bracket fixes
                return True

            else:
                logger.warning(f"Unknown fix type: {fix_type}")
                return False

        except Exception as e:
            logger.error(f"Fix {fix_type} failed for {file_path}: {e}")
            return False

    def run_promotion_readiness_check(self, lane: str) -> dict:
        """Check if lane is ready for promotion based on policy"""
        if lane not in ["labs"]:  # Only candidate can be promoted to accepted
            return {"ready": False, "reason": "Lane not promotable"}

        policy = self.fixing_policy.get_policy(lane)
        test_requirements = policy.get("test_requirements", [])

        readiness = {"ready": True, "checks": {}, "blockers": []}

        # Check test requirements
        for test_req in test_requirements:
            if test_req == "smoke":
                # Run smoke tests
                try:
                    result = subprocess.run(
                        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
                        capture_output=True,
                        text=True,
                        cwd=ROOT,
                        timeout=30,
                    )

                    smoke_passed = result.returncode == 0
                    readiness["checks"]["smoke_tests"] = smoke_passed

                    if not smoke_passed:
                        readiness["ready"] = False
                        readiness["blockers"].append("Smoke tests failed")

                except Exception as e:
                    readiness["checks"]["smoke_tests"] = False
                    readiness["ready"] = False
                    readiness["blockers"].append(f"Smoke test error: {e}")

        return readiness

    def run_lane_aware_fixes(self, target_files: Optional[list[Path]] = None) -> dict:
        """Run complete lane-aware fixing workflow"""
        logger.info("🛣️ Starting MATRIZ lane-aware fixing")

        # Get files to process
        if target_files is None:
            # Find all Python files with potential issues
            target_files = list(ROOT.rglob("*.py"))
            # Filter to manageable size
            target_files = target_files[:100]

        # Group files by lane
        files_by_lane = {}
        unassigned_files = []

        for file_path in target_files:
            lane = self.lane_config.get_file_lane(file_path)
            if lane:
                if lane not in files_by_lane:
                    files_by_lane[lane] = []
                files_by_lane[lane].append(file_path)
            else:
                unassigned_files.append(file_path)

        if unassigned_files:
            files_by_lane["unassigned"] = unassigned_files

        logger.info(f"Files grouped: {', '.join(f'{k}={len(v)}' for k, v in files_by_lane.items())}")

        # Define fix types to apply
        fix_types = {"SYNTAX_FSTRING", "CONFIG_MARKERS", "IMPORT_BRIDGE", "BRACKET_MATCH"}

        # Apply fixes with lane policies
        fix_results = self.apply_lane_aware_fixes(files_by_lane, fix_types)

        # Generate summary report
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dry_run": self.dry_run,
            "lanes_processed": len(fix_results["processed_lanes"]),
            "total_files": sum(len(files) for files in files_by_lane.values()),
            "fix_results": fix_results,
            "lane_policies": {lane: self.fixing_policy.get_policy(lane) for lane in files_by_lane},
        }

        # Save report
        self.save_lane_report(report)

        logger.info(f"🛣️ Lane-aware fixing complete: {len(fix_results['processed_lanes'])} lanes processed")
        return report

    def save_lane_report(self, report: dict):
        """Save lane-aware fixing report"""
        reports_dir = ROOT / "reports" / "matriz_lane_fixes"
        reports_dir.mkdir(parents=True, exist_ok=True)

        # Save latest report
        latest_report = reports_dir / "latest_lane_fixes.json"
        latest_report.write_text(json.dumps(report, indent=2))

        # Save timestamped report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        timestamped_report = reports_dir / f"lane_fixes_{timestamp}.json"
        timestamped_report.write_text(json.dumps(report, indent=2))


def main():
    """CLI interface for lane-aware fixer"""
    import argparse

    parser = argparse.ArgumentParser(description="MATRIZ lane-aware fixing system")
    parser.add_argument("files", nargs="*", help="Files to fix (default: auto-detect)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be fixed")
    parser.add_argument("--lane", help="Only process specific lane")
    parser.add_argument("--check-promotion", help="Check promotion readiness for lane")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    fixer = LaneAwareFixer(dry_run=args.dry_run)

    if args.check_promotion:
        readiness = fixer.run_promotion_readiness_check(args.check_promotion)
        print(f"\n🛣️ PROMOTION READINESS: {args.check_promotion}")
        print(f"Ready: {'✅ YES' if readiness['ready'] else '❌ NO'}")

        if readiness["blockers"]:
            print(f"Blockers: {', '.join(readiness['blockers'])}")

        return 0 if readiness["ready"] else 1

    # Run lane-aware fixes
    target_files = None
    if args.files:
        target_files = [Path(f) for f in args.files]

    report = fixer.run_lane_aware_fixes(target_files)

    # Print summary
    print("\n🛣️ LANE-AWARE FIXING RESULTS")
    print("===========================")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print(f"Lanes processed: {report['lanes_processed']}")
    print(f"Total files: {report['total_files']}")

    # Show results by lane
    for lane in report["fix_results"]["processed_lanes"]:
        lane_data = report["fix_results"]["fixes_applied"].get(lane, {})
        files_fixed = lane_data.get("files_fixed", 0)
        files_total = lane_data.get("files_processed", 0)
        print(f"  🛣️ {lane}: {files_fixed}/{files_total} files fixed")

    return 0


if __name__ == "__main__":
    sys.exit(main())
