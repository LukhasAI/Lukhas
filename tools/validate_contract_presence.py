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
- Manifest-aware coverage reporting (--manifest-coverage)
- Intelligent contract suggestions based on manifest capabilities (--suggest-contracts)
"""

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Repository structure
ROOT = Path(__file__).resolve().parents[1]
LUKHAS_DIR = ROOT / "lukhas"
MANIFESTS_DIR = ROOT / "manifests"

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
    manifest_path: Optional[Path] = None
    has_manifest: bool = False
    manifest_capabilities: List[str] = None
    constellation_star: Optional[str] = None

    def __post_init__(self):
        if self.manifest_capabilities is None:
            self.manifest_capabilities = []

class ContractPresenceValidator:
    """Validates Matrix contract presence for all modules."""

    def __init__(self, enable_manifest_integration: bool = False):
        self.modules = self._discover_modules()
        self.enable_manifest_integration = enable_manifest_integration
        self.manifests_cache = {} if enable_manifest_integration else None
        if enable_manifest_integration:
            self._load_manifests()

    def _load_manifests(self) -> None:
        """Load all module manifests for cross-referencing."""
        if not MANIFESTS_DIR.exists():
            return

        for manifest_file in MANIFESTS_DIR.rglob("module.manifest.json"):
            try:
                manifest_data = json.loads(manifest_file.read_text())
                module_name = manifest_data.get("identity", {}).get("module_name", "")
                if module_name:
                    self.manifests_cache[module_name] = {
                        "path": manifest_file,
                        "data": manifest_data
                    }
            except (json.JSONDecodeError, KeyError):
                pass  # Skip invalid manifests

    def _discover_modules(self) -> List[Tuple[Path, str]]:
        """Discover all Python modules under lukhas/."""
        modules = []

        for init_file in LUKHAS_DIR.rglob("__init__.py"):
            module_dir = init_file.parent
            # Convert path to module name
            relative_path = module_dir.relative_to(LUKHAS_DIR)

            module_name = ".".join(relative_path.parts) if relative_path.parts else "root"

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

        # Manifest integration (if enabled)
        manifest_path = None
        has_manifest = False
        manifest_capabilities = []
        constellation_star = None

        if self.enable_manifest_integration and self.manifests_cache:
            # Try to find manifest for this module
            manifest_info = self.manifests_cache.get(module_name)
            if manifest_info:
                manifest_path = manifest_info["path"]
                has_manifest = True
                manifest_data = manifest_info["data"]

                # Extract capabilities from manifest
                capabilities = manifest_data.get("capabilities", [])
                if isinstance(capabilities, list):
                    manifest_capabilities = [
                        cap.get("name", cap) if isinstance(cap, dict) else cap
                        for cap in capabilities
                    ]

                # Extract Constellation star
                constellation = manifest_data.get("constellation", {})
                if isinstance(constellation, dict):
                    constellation_star = constellation.get("primary_star")

        return ModuleContractCheck(
            module_path=module_dir,
            module_name=module_name,
            has_init=has_init,
            expected_contract=expected_contract,
            contract_exists=contract_exists,
            contract_valid=contract_valid,
            has_identity_block=has_identity_block,
            issues=issues,
            manifest_path=manifest_path,
            has_manifest=has_manifest,
            manifest_capabilities=manifest_capabilities,
            constellation_star=constellation_star
        )

    def validate_all_modules(self) -> List[ModuleContractCheck]:
        """Validate contract presence for all discovered modules."""
        results = []

        for module_dir, module_name in self.modules:
            check_result = self.check_module_contract(module_dir, module_name)
            results.append(check_result)

        return results

    def generate_enforcement_report(self, results: List[ModuleContractCheck], include_manifest_coverage: bool = False) -> Dict[str, Any]:
        """Generate enforcement report for CI/CD."""
        total_modules = len(results)
        modules_with_contracts = sum(1 for r in results if r.contract_exists)
        valid_contracts = sum(1 for r in results if r.contract_valid)
        modules_with_identity = sum(1 for r in results if r.has_identity_block)

        failing_modules = [r for r in results if r.issues]

        report = {
            "summary": {
                "total_modules": total_modules,
                "modules_with_contracts": modules_with_contracts,
                "valid_contracts": valid_contracts,
                "modules_with_identity": modules_with_identity,
                "contract_coverage": round(100 * modules_with_contracts / total_modules, 1) if total_modules > 0 else 0,
                "identity_coverage": round(100 * modules_with_identity / total_modules, 1) if total_modules > 0 else 0,
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

        # Add manifest coverage report if requested
        if include_manifest_coverage:
            modules_with_manifests = sum(1 for r in results if r.has_manifest)
            modules_with_both = sum(1 for r in results if r.contract_exists and r.has_manifest)

            report["manifest_integration"] = {
                "modules_with_manifests": modules_with_manifests,
                "modules_with_both_contract_and_manifest": modules_with_both,
                "manifest_coverage": round(100 * modules_with_manifests / total_modules, 1) if total_modules > 0 else 0,
                "full_coverage": round(100 * modules_with_both / total_modules, 1) if total_modules > 0 else 0,
                "modules_with_contract_no_manifest": [
                    {
                        "module": r.module_name,
                        "contract": str(r.expected_contract.relative_to(ROOT))
                    }
                    for r in results if r.contract_exists and not r.has_manifest
                ],
                "modules_with_manifest_no_contract": [
                    {
                        "module": r.module_name,
                        "manifest": str(r.manifest_path.relative_to(ROOT)) if r.manifest_path else "",
                        "capabilities": r.manifest_capabilities,
                        "constellation_star": r.constellation_star
                    }
                    for r in results if r.has_manifest and not r.contract_exists
                ],
                "contract_to_manifest_mapping": [
                    {
                        "module": r.module_name,
                        "contract": str(r.expected_contract.relative_to(ROOT)),
                        "manifest": str(r.manifest_path.relative_to(ROOT)) if r.manifest_path else None,
                        "capabilities": r.manifest_capabilities,
                        "constellation_star": r.constellation_star
                    }
                    for r in results if r.contract_exists and r.has_manifest
                ]
            }

        return report

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

    def suggest_contracts_from_manifests(self, results: List[ModuleContractCheck]) -> Dict[str, Any]:
        """Suggest contract content based on manifest capabilities."""
        if not self.enable_manifest_integration:
            return {
                "error": "Manifest integration not enabled. Use --manifest-coverage flag."
            }

        suggestions = []

        for result in results:
            if result.has_manifest and not result.contract_exists:
                # Generate intelligent suggestions based on manifest
                suggestion = self._generate_intelligent_contract_suggestion(
                    result.module_name,
                    result.manifest_capabilities,
                    result.constellation_star
                )
                suggestions.append({
                    "module": result.module_name,
                    "manifest_path": str(result.manifest_path.relative_to(ROOT)) if result.manifest_path else "",
                    "capabilities": result.manifest_capabilities,
                    "constellation_star": result.constellation_star,
                    "suggested_contract": suggestion
                })

        return {
            "total_suggestions": len(suggestions),
            "suggestions": suggestions
        }

    def _generate_intelligent_contract_suggestion(
        self,
        module_name: str,
        capabilities: List[str],
        constellation_star: Optional[str]
    ) -> Dict[str, Any]:
        """Generate intelligent contract template based on manifest capabilities."""
        simple_name = module_name.split(".")[-1] if "." in module_name else module_name

        # Base template
        contract = self._generate_contract_template(module_name)

        # Enhance based on capabilities
        if capabilities:
            # Add capability-specific API contracts
            contract["interface"]["contracts"] = [
                {
                    "endpoint": f"/api/v1/{simple_name}/{cap.lower().replace(' ', '_')}",
                    "method": "POST",
                    "capability": cap,
                    "requires_auth": True
                }
                for cap in capabilities[:5]  # Limit to top 5 capabilities
            ]

            # Add capability-specific scopes
            contract["identity"]["scopes"].extend([
                f"{simple_name}.{cap.lower().replace(' ', '_')}"
                for cap in capabilities[:3]  # Top 3 as scopes
            ])

            # Add capability-specific telemetry
            contract["telemetry"]["spans"].extend([
                {
                    "name": f"{simple_name}.{cap.lower().replace(' ', '_')}",
                    "attrs": ["code.function", "capability.name"]
                }
                for cap in capabilities[:3]
            ])

        # Enhance based on Constellation star
        if constellation_star:
            star_tiers = {
                "🌟 Origin": ["trusted", "core"],
                "🌸 Flow": ["trusted"],
                "💠 Skill": ["authenticated"],
                "🎯 Guard": ["trusted", "core"],
                "⚛️ Core": ["trusted", "core"],
                "🔧 Bridge": ["authenticated"]
            }

            star_tiers_numeric = {
                "🌟 Origin": [4, 5],
                "🌸 Flow": [3, 4, 5],
                "💠 Skill": [2, 3, 4, 5],
                "🎯 Guard": [4, 5],
                "⚛️ Core": [4, 5],
                "🔧 Bridge": [2, 3, 4, 5]
            }

            if constellation_star in star_tiers:
                contract["identity"]["required_tiers"] = star_tiers[constellation_star]
                contract["identity"]["required_tiers_numeric"] = star_tiers_numeric[constellation_star]

            # Add star-specific documentation hints
            contract["docs"]["constellation_star"] = constellation_star

        return contract

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
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic contract presence check
  python validate_contract_presence.py --check

  # Check with manifest coverage integration
  python validate_contract_presence.py --check --manifest-coverage

  # Suggest contracts based on manifest capabilities
  python validate_contract_presence.py --suggest-contracts --output suggestions.json

  # Create missing contracts
  python validate_contract_presence.py --create-missing --dry-run
        """
    )

    parser.add_argument("--check", action="store_true",
                       help="Check contract presence for all modules")
    parser.add_argument("--enforce", action="store_true",
                       help="Enforce contract presence (fail if missing)")
    parser.add_argument("--create-missing", action="store_true",
                       help="Create missing contract files")
    parser.add_argument("--manifest-coverage", action="store_true",
                       help="Include manifest coverage in report and enable manifest integration")
    parser.add_argument("--suggest-contracts", action="store_true",
                       help="Suggest contract content based on manifest capabilities")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be created without creating files")
    parser.add_argument("--output", type=str,
                       help="Output file for reports (JSON format)")
    parser.add_argument("--quiet", action="store_true",
                       help="Suppress verbose output")

    args = parser.parse_args()

    if not any([args.check, args.enforce, args.create_missing, args.suggest_contracts]):
        parser.print_help()
        return 1

    # Enable manifest integration if requested
    enable_manifest = args.manifest_coverage or args.suggest_contracts

    validator = ContractPresenceValidator(enable_manifest_integration=enable_manifest)

    if not args.quiet:
        print("🔍 Discovering Python modules...")
        if enable_manifest:
            print("📋 Loading module manifests for integration...")

    results = validator.validate_all_modules()

    if not args.quiet:
        print(f"📦 Found {len(results)} modules")
        if enable_manifest and validator.manifests_cache:
            print(f"📋 Loaded {len(validator.manifests_cache)} module manifests")

    # Handle contract suggestions
    if args.suggest_contracts:
        suggestions = validator.suggest_contracts_from_manifests(results)

        if args.output:
            Path(args.output).write_text(json.dumps(suggestions, indent=2))
            if not args.quiet:
                print(f"📄 Suggestions saved to {args.output}")

        if not args.quiet:
            print("\n💡 Contract Suggestions from Manifests")
            print("======================================")
            print(f"Total suggestions: {suggestions.get('total_suggestions', 0)}")

            if "error" in suggestions:
                print(f"❌ Error: {suggestions['error']}")
            else:
                for suggestion in suggestions.get("suggestions", [])[:5]:
                    print(f"\n  Module: {suggestion['module']}")
                    print(f"  Star: {suggestion.get('constellation_star', 'N/A')}")
                    print(f"  Capabilities: {', '.join(suggestion.get('capabilities', [])[:3])}")
                    if len(suggestion.get('capabilities', [])) > 3:
                        print(f"                 (+{len(suggestion['capabilities']) - 3} more)")

        return 0

    # Standard validation flow
    if args.check or args.enforce:
        report = validator.generate_enforcement_report(results, include_manifest_coverage=args.manifest_coverage)

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

            # Manifest integration reporting
            if args.manifest_coverage and "manifest_integration" in report:
                mi = report["manifest_integration"]
                print("\n📋 Manifest Integration")
                print(f"Manifest coverage: {mi['manifest_coverage']}%")
                print(f"Full coverage (contract + manifest): {mi['full_coverage']}%")
                print(f"Modules with both: {mi['modules_with_both_contract_and_manifest']}")

                if mi['modules_with_contract_no_manifest']:
                    print(f"\n⚠️  Contracts without manifests ({len(mi['modules_with_contract_no_manifest'])}):")
                    for item in mi['modules_with_contract_no_manifest'][:3]:
                        print(f"  - {item['module']}")

                if mi['modules_with_manifest_no_contract']:
                    print(f"\n⚠️  Manifests without contracts ({len(mi['modules_with_manifest_no_contract'])}):")
                    for item in mi['modules_with_manifest_no_contract'][:3]:
                        print(f"  - {item['module']} (Star: {item.get('constellation_star', 'N/A')})")

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
