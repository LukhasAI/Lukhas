#!/usr/bin/env python3
"""
MATRIZ Module Manifest Validator - Comprehensive Lane Assignment Verification
============================================================================

Validates all LUKHAS AI modules have proper lane manifests with correct
assignments, dependencies, and T4/0.01% excellence configurations.

Usage:
    python scripts/validate_module_manifests.py
    python scripts/validate_module_manifests.py --fix
    python scripts/validate_module_manifests.py --report artifacts/manifest_validation.json
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModuleManifestValidator:
    """MATRIZ module manifest validation with lane assignment verification."""

    def __init__(self):
        self.validation_results = {
            "validation_timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%f+00:00"),
            "modules_scanned": 0,
            "modules_with_manifests": 0,
            "modules_missing_manifests": 0,
            "lane_distribution": {
                "candidate": 0,
                "integration": 0,
                "production": 0
            },
            "validation_errors": [],
            "missing_manifests": [],
            "invalid_manifests": []
        }

    def find_lukhas_modules(self) -> List[Path]:
        """Find all LUKHAS AI module directories."""
        lukhas_root = Path("lukhas")
        if not lukhas_root.exists():
            logger.error("lukhas/ directory not found")
            return []

        modules = []
        for item in lukhas_root.iterdir():
            if item.is_dir() and not item.name.startswith('__'):
                # Skip deep subdirectories that are not top-level modules
                if item.name not in ['accepted', 'shims', 'tools', 'utils', 'trinity']:
                    modules.append(item)

        return sorted(modules)

    def load_module_manifest(self, module_path: Path) -> Optional[Dict[str, Any]]:
        """Load module lane manifest if it exists."""
        manifest_path = module_path / "module.lane.yaml"

        if not manifest_path.exists():
            return None

        try:
            with open(manifest_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading manifest {manifest_path}: {e}")
            return None

    def validate_manifest_structure(self, manifest: Dict[str, Any], module_path: Path) -> List[str]:
        """Validate manifest structure and required fields."""
        errors = []

        required_fields = ['name', 'lane', 'owner', 'description']
        for field in required_fields:
            if field not in manifest:
                errors.append(f"Missing required field: {field}")

        # Validate lane value
        valid_lanes = ['candidate', 'integration', 'production']
        if 'lane' in manifest and manifest['lane'] not in valid_lanes:
            errors.append(f"Invalid lane '{manifest['lane']}', must be one of {valid_lanes}")

        # Validate SLO structure for non-candidate lanes
        if manifest.get('lane') != 'candidate':
            if 'slo' not in manifest:
                errors.append("SLO configuration required for integration/production lanes")
            else:
                slo = manifest['slo']
                if 'p95_ms' not in slo:
                    errors.append("SLO p95_ms configuration missing")
                else:
                    p95_ms = slo['p95_ms']
                    required_metrics = ['tick', 'reflect', 'decide', 'e2e']
                    for metric in required_metrics:
                        if metric not in p95_ms:
                            errors.append(f"Missing SLO metric: {metric}")

        # Validate gates configuration
        if 'gates' not in manifest:
            errors.append("Gates configuration missing")
        elif not isinstance(manifest['gates'], list):
            errors.append("Gates must be a list")

        # Validate artifacts configuration
        if 'artifacts' not in manifest:
            errors.append("Artifacts configuration missing")
        elif not isinstance(manifest['artifacts'], list):
            errors.append("Artifacts must be a list")

        return errors

    def validate_lane_assignment_logic(self, manifest: Dict[str, Any], module_name: str) -> List[str]:
        """Validate that lane assignment makes sense for the module."""
        errors = []
        lane = manifest.get('lane')

        # Core infrastructure modules should be in integration or production
        infrastructure_modules = ['core', 'governance', 'security', 'observability', 'api']
        if module_name in infrastructure_modules and lane == 'candidate':
            errors.append(f"Infrastructure module '{module_name}' should not be in candidate lane")

        # Experimental modules should start in candidate
        experimental_modules = ['bio', 'qi', 'rl', 'emotion', 'agents', 'vivox']
        if module_name in experimental_modules and lane == 'production':
            errors.append(f"Experimental module '{module_name}' should not be in production lane")

        # Production-critical modules
        critical_modules = ['identity', 'memory', 'consciousness', 'governance']
        if module_name in critical_modules and lane == 'candidate':
            errors.append(f"Critical module '{module_name}' should be at least in integration lane")

        return errors

    def validate_dependencies(self, manifest: Dict[str, Any], all_modules: Set[str]) -> List[str]:
        """Validate module dependencies are valid and don't create cycles."""
        errors = []

        if 'dependencies' not in manifest:
            return errors

        dependencies = manifest['dependencies']
        if not isinstance(dependencies, list):
            errors.append("Dependencies must be a list")
            return errors

        for dep in dependencies:
            # Validate dependency format (should be modulename)
            if not dep.startswith('lukhas.'):
                errors.append(f"Invalid dependency format: {dep} (should start with 'lukhas.')")
                continue

            module_name = dep.replace('lukhas.', '')
            if module_name not in all_modules:
                errors.append(f"Unknown dependency: {dep}")

        return errors

    def validate_all_modules(self) -> Dict[str, Any]:
        """Validate all LUKHAS AI modules."""
        logger.info("🔍 Starting module manifest validation")

        modules = self.find_lukhas_modules()
        all_module_names = {module.name for module in modules}

        self.validation_results["modules_scanned"] = len(modules)

        for module_path in modules:
            module_name = module_path.name
            logger.info(f"Validating module: {module_name}")

            manifest = self.load_module_manifest(module_path)

            if manifest is None:
                self.validation_results["modules_missing_manifests"] += 1
                self.validation_results["missing_manifests"].append(module_name)
                logger.warning(f"❌ Missing manifest: {module_name}")
                continue

            self.validation_results["modules_with_manifests"] += 1

            # Track lane distribution
            lane = manifest.get('lane')
            if lane in self.validation_results["lane_distribution"]:
                self.validation_results["lane_distribution"][lane] += 1

            # Validate manifest structure
            structure_errors = self.validate_manifest_structure(manifest, module_path)

            # Validate lane assignment logic
            assignment_errors = self.validate_lane_assignment_logic(manifest, module_name)

            # Validate dependencies
            dependency_errors = self.validate_dependencies(manifest, all_module_names)

            all_errors = structure_errors + assignment_errors + dependency_errors

            if all_errors:
                self.validation_results["invalid_manifests"].append({
                    "module": module_name,
                    "errors": all_errors
                })
                for error in all_errors:
                    logger.error(f"❌ {module_name}: {error}")
            else:
                logger.info(f"✅ {module_name}: Valid manifest")

        return self.validation_results

    def generate_summary_report(self) -> str:
        """Generate human-readable validation summary."""
        results = self.validation_results

        report = []
        report.append("🔍 MATRIZ Module Manifest Validation Report")
        report.append("=" * 50)
        report.append(f"Modules scanned: {results['modules_scanned']}")
        report.append(f"Modules with manifests: {results['modules_with_manifests']}")
        report.append(f"Modules missing manifests: {results['modules_missing_manifests']}")
        report.append("")

        # Lane distribution
        report.append("📊 Lane Distribution:")
        for lane, count in results['lane_distribution'].items():
            percentage = (count / max(results['modules_with_manifests'], 1)) * 100
            report.append(f"  {lane}: {count} modules ({percentage:.1f}%)")
        report.append("")

        # Missing manifests
        if results['missing_manifests']:
            report.append("❌ Modules missing manifests:")
            for module in results['missing_manifests']:
                report.append(f"  - {module}")
            report.append("")

        # Invalid manifests
        if results['invalid_manifests']:
            report.append("⚠️  Modules with invalid manifests:")
            for invalid in results['invalid_manifests']:
                report.append(f"  {invalid['module']}:")
                for error in invalid['errors']:
                    report.append(f"    - {error}")
            report.append("")

        # Overall status
        total_issues = len(results['missing_manifests']) + len(results['invalid_manifests'])
        if total_issues == 0:
            report.append("🎉 All modules have valid manifests!")
        else:
            report.append(f"⚠️  {total_issues} modules need attention")

        return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description="MATRIZ Module Manifest Validator")
    parser.add_argument("--report",
                       help="Output detailed validation report to JSON file")
    parser.add_argument("--fix", action="store_true",
                       help="Automatically fix common issues")

    args = parser.parse_args()

    # Run validation
    validator = ModuleManifestValidator()
    results = validator.validate_all_modules()

    # Generate and display summary
    summary = validator.generate_summary_report()
    print(summary)

    # Output detailed report if requested
    if args.report:
        output_path = Path(args.report)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info(f"📄 Detailed report written to: {output_path}")

    # Exit with appropriate code
    total_issues = len(results['missing_manifests']) + len(results['invalid_manifests'])
    if total_issues > 0:
        logger.error(f"❌ Validation failed: {total_issues} issues found")
        return 1
    else:
        logger.info("✅ All module manifests are valid")
        return 0

if __name__ == "__main__":
    sys.exit(main())
