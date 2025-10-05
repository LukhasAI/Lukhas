#!/usr/bin/env python3
"""
Matrix Contract Presence Validator

Ensures every Python module in the lukhas/ directory has a corresponding
Matrix contract file, enforcing the "every module must have a contract" policy.

Features:
- Discovers all Python modules via __init__.py files
- Validates presence of matrix_<module>.json for each module
- Checks contract completeness and identity block presence
- Generates enforcement reports for CI/CD
"""

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Repository structure
ROOT = Path(__file__).resolve().parents[1]
LUKHAS_DIR = ROOT / "lukhas"

@dataclass
class ModuleContractCheck:
    """Results of module contract validation."""
    module_path: Path
    module_name: str
    has_init: bool
    expected_contract: Path
    contract_exists: bool
    contract_valid: bool
    has_identity_block: bool
    issues: List[str]

class ContractPresenceValidator:
    """Validates Matrix contract presence for all modules."""

    def __init__(self):
        self.modules = self._discover_modules()

    def _discover_modules(self) -> List[Tuple[Path, str]]:
        """Discover all Python modules under lukhas/."""
        modules = []

        for init_file in LUKHAS_DIR.rglob("__init__.py"):
            module_dir = init_file.parent
            # Convert path to module name
            relative_path = module_dir.relative_to(LUKHAS_DIR)

            if relative_path.parts:
                module_name = ".".join(relative_path.parts)
            else:
                module_name = "root"

            modules.append((module_dir, module_name))

        return sorted(modules, key=lambda x: x[1])

    def _get_expected_contract_path(self, module_dir: Path, module_name: str) -> Path:
        """Get expected contract path for a module."""
        simple_name = module_name.split(".")[-1] if "." in module_name else module_name
        return module_dir / f"matrix_{simple_name}.json"

    def _validate_contract_file(self, contract_path: Path) -> Tuple[bool, bool, List[str]]:
        """Validate contract file format and required sections."""
        issues = []

        if not contract_path.exists():
            return False, False, ["Contract file does not exist"]

        try:
            contract_data = json.loads(contract_path.read_text())
        except json.JSONDecodeError as e:
            return False, False, [f"Invalid JSON: {e}"]

        # Check required top-level fields
        required_fields = ["schema_version", "module", "owner", "identity"]
        for field in required_fields:
            if field not in contract_data:
                issues.append(f"Missing required field: {field}")

        # Check identity block structure
        has_identity = "identity" in contract_data
        if has_identity:
            identity = contract_data["identity"]
            identity_required = ["requires_auth", "accepted_subjects", "required_tiers", "scopes"]
            for field in identity_required:
                if field not in identity:
                    issues.append(f"Missing identity field: {field}")

        return True, has_identity, issues

    def check_module_contract(self, module_dir: Path, module_name: str) -> ModuleContractCheck:
        """Check contract presence and validity for a module."""
        init_file = module_dir / "__init__.py"
        has_init = init_file.exists()

        expected_contract = self._get_expected_contract_path(module_dir, module_name)
        contract_exists = expected_contract.exists()

        contract_valid = False
        has_identity_block = False
        issues = []

        if contract_exists:
            contract_valid, has_identity_block, validation_issues = self._validate_contract_file(expected_contract)
            issues.extend(validation_issues)
        else:
            issues.append("Matrix contract file missing")

        return ModuleContractCheck(
            module_path=module_dir,
            module_name=module_name,
            has_init=has_init,
            expected_contract=expected_contract,
            contract_exists=contract_exists,
            contract_valid=contract_valid,
            has_identity_block=has_identity_block,
            issues=issues
        )

    def validate_all_modules(self) -> List[ModuleContractCheck]:
        """Validate contract presence for all discovered modules."""
        results = []

        for module_dir, module_name in self.modules:
            check_result = self.check_module_contract(module_dir, module_name)
            results.append(check_result)

        return results

    def generate_enforcement_report(self, results: List[ModuleContractCheck]) -> Dict[str, Any]:
        """Generate enforcement report for CI/CD."""
        total_modules = len(results)
        modules_with_contracts = sum(1 for r in results if r.contract_exists)
        valid_contracts = sum(1 for r in results if r.contract_valid)
        modules_with_identity = sum(1 for r in results if r.has_identity_block)

        failing_modules = [r for r in results if r.issues]

        return {
            "summary": {
                "total_modules": total_modules,
                "modules_with_contracts": modules_with_contracts,
                "valid_contracts": valid_contracts,
                "modules_with_identity": modules_with_identity,
                "contract_coverage": round(100 * modules_with_contracts / total_modules, 1),
                "identity_coverage": round(100 * modules_with_identity / total_modules, 1),
                "failing_modules": len(failing_modules)
            },
            "enforcement_status": "PASS" if len(failing_modules) == 0 else "FAIL",
            "missing_contracts": [
                {
                    "module": r.module_name,
                    "path": str(r.module_path.relative_to(ROOT)),
                    "expected_contract": str(r.expected_contract.relative_to(ROOT))
                }
                for r in results if not r.contract_exists
            ],
            "invalid_contracts": [
                {
                    "module": r.module_name,
                    "contract": str(r.expected_contract.relative_to(ROOT)),
                    "issues": r.issues
                }
                for r in results if r.contract_exists and not r.contract_valid
            ],
            "modules_without_identity": [
                {
                    "module": r.module_name,
                    "contract": str(r.expected_contract.relative_to(ROOT))
                }
                for r in results if r.contract_exists and r.contract_valid and not r.has_identity_block
            ]
        }

    def create_missing_contracts(self, results: List[ModuleContractCheck], dry_run: bool = True) -> List[str]:
        """Create missing contract files with basic templates."""
        created_contracts = []

        for result in results:
            if not result.contract_exists:
                template = self._generate_contract_template(result.module_name)

                if dry_run:
                    created_contracts.append(str(result.expected_contract.relative_to(ROOT)))
                else:
                    try:
                        result.expected_contract.write_text(json.dumps(template, indent=2) + "\n")
                        created_contracts.append(str(result.expected_contract.relative_to(ROOT)))
                    except Exception as e:
                        print(f"❌ Error creating {result.expected_contract}: {e}")

        return created_contracts

    def _generate_contract_template(self, module_name: str) -> Dict[str, Any]:
        """Generate basic contract template for a module."""
        simple_name = module_name.split(".")[-1] if "." in module_name else module_name

        return {
            "schema_version": "1.0.0",
            "module": module_name,
            "owner": {
                "team": "Core",
                "codeowners": ["@gonzo.dominguez", "@lukhas-core"]
            },
            "interface": {
                "public_api": [],
                "contracts": []
            },
            "params": {},
            "gates": [
                {"metric": "security.osv_high", "op": "==", "value": 0},
                {"metric": "symbolic.DriftScore", "op": ">=", "value": 0.010}
            ],
            "telemetry": {
                "opentelemetry_semconv_version": "1.37.0",
                "spans": [{"name": f"{simple_name}.operation", "attrs": ["code.function"]}],
                "metrics": [{"name": f"lukhas.{simple_name}.latency", "unit": "s", "type": "histogram"}]
            },
            "symbolic_diagnostics": {
                "CollapseHash": "sha256:pending",
                "DriftScore": 0.010,
                "EthicalDriftIndex": 0.0,
                "ConvergencePct": 0.0
            },
            "lineage": {
                "openlineage_event_id": "",
                "datasets_in": [],
                "datasets_out": [],
                "job": f"lukhas.{simple_name}.job"
            },
            "provenance": {
                "@context": "",
                "commit": "",
                "branch": "",
                "built_by": {},
                "environment": {"os": "", "cpu": "", "python": ""},
                "config_fingerprint": "sha256:"
            },
            "identity": {
                "requires_auth": True,
                "accepted_subjects": ["lukhas:user:*"],
                "required_tiers": ["trusted"],
                "required_tiers_numeric": [3],
                "scopes": [f"{simple_name}.read", f"{simple_name}.write"],
                "webauthn_required": False,
                "api_policies": []
            },
            "docs": {
                "lens_markdown": f"../products/intelligence/lens/{simple_name}.qmd",
                "design_notes": f"../docs/{simple_name}/architecture.md"
            }
        }

def main():
    """CLI for contract presence validation."""
    parser = argparse.ArgumentParser(
        description="Matrix Contract Presence Validator",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("--check", action="store_true",
                       help="Check contract presence for all modules")
    parser.add_argument("--enforce", action="store_true",
                       help="Enforce contract presence (fail if missing)")
    parser.add_argument("--create-missing", action="store_true",
                       help="Create missing contract files")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be created without creating files")
    parser.add_argument("--output", type=str,
                       help="Output file for reports (JSON format)")
    parser.add_argument("--quiet", action="store_true",
                       help="Suppress verbose output")

    args = parser.parse_args()

    if not any([args.check, args.enforce, args.create_missing]):
        parser.print_help()
        return 1

    validator = ContractPresenceValidator()

    if not args.quiet:
        print("🔍 Discovering Python modules...")

    results = validator.validate_all_modules()

    if not args.quiet:
        print(f"📦 Found {len(results)} modules")

    if args.check or args.enforce:
        report = validator.generate_enforcement_report(results)

        if args.output:
            Path(args.output).write_text(json.dumps(report, indent=2))
            if not args.quiet:
                print(f"📄 Report saved to {args.output}")

        if not args.quiet:
            print("\n📊 Matrix Contract Presence Report")
            print("===================================")
            print(f"Total modules: {report['summary']['total_modules']}")
            print(f"Contract coverage: {report['summary']['contract_coverage']}%")
            print(f"Identity coverage: {report['summary']['identity_coverage']}%")
            print(f"Status: {report['enforcement_status']}")

            if report['missing_contracts']:
                print(f"\n❌ Missing contracts ({len(report['missing_contracts'])}):")
                for missing in report['missing_contracts'][:5]:
                    print(f"  - {missing['module']}")

            if report['invalid_contracts']:
                print(f"\n🔧 Invalid contracts ({len(report['invalid_contracts'])}):")
                for invalid in report['invalid_contracts'][:5]:
                    print(f"  - {invalid['module']}: {', '.join(invalid['issues'][:2])}")

        if args.enforce and report['enforcement_status'] == "FAIL":
            print("\n❌ ENFORCEMENT FAILURE: Some modules lack valid Matrix contracts")
            return 1

    if args.create_missing:
        if not args.quiet:
            print("🔧 Creating missing contract files...")

        created = validator.create_missing_contracts(results, dry_run=args.dry_run)

        if created:
            if not args.quiet:
                print(f"📝 {'Would create' if args.dry_run else 'Created'} {len(created)} contracts")
                for contract in created[:5]:
                    print(f"  - {contract}")

            if args.dry_run and not args.quiet:
                print("🧪 Dry run mode - no files created")
        else:
            if not args.quiet:
                print("✅ All modules already have contracts")

    return 0

if __name__ == "__main__":
    sys.exit(main())
