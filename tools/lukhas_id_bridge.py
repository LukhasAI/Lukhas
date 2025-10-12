#!/usr/bin/env python3
"""
LUKHAS ΛiD Bridge - Matrix Contracts Integration

Synchronizes ΛiD tier definitions with Matrix contracts, ensuring consistency
between the canonical tier system and contract identity requirements.

Features:
- Validates Matrix contracts against canonical ΛiD tier definitions
- Syncs tier changes from tier_permissions.json to Matrix contracts
- Checks contract-tier alignment across all modules
- Generates reports on tier usage and distribution
"""

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

# Repository structure
ROOT = Path(__file__).resolve().parents[1]
TIER_PERMISSIONS = ROOT / "labs" / "lukhas.governance" / "identity" / "config" / "tier_permissions.json"
MATRIX_CONTRACTS = ROOT / "lukhas"

# ΛiD tier system (canonical)
CANONICAL_TIERS = ["guest", "visitor", "friend", "trusted", "inner_circle", "root_dev"]
TIER_TO_NUMERIC = {tier: i for i, tier in enumerate(CANONICAL_TIERS)}

@dataclass
class ContractAnalysis:
    """Analysis results for a Matrix contract."""
    path: Path
    module: str
    has_identity: bool
    tiers: List[str]
    tier_numeric: List[int]
    webauthn_required: bool
    scopes: List[str]
    accepted_subjects: List[str]
    issues: List[str]

class LukhasIdBridge:
    """Bridge between ΛiD tier system and Matrix contracts."""

    def __init__(self):
        self.tier_permissions = self._load_tier_permissions()
        self.contracts = self._discover_contracts()

    def _load_tier_permissions(self) -> Dict[str, Any]:
        """Load canonical tier permissions."""
        try:
            return json.loads(TIER_PERMISSIONS.read_text())
        except FileNotFoundError:
            print(f"⚠️ Tier permissions not found at {TIER_PERMISSIONS}")
            return {"tier_system": {"tiers": CANONICAL_TIERS}}
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in tier permissions: {e}")
            sys.exit(1)

    def _discover_contracts(self) -> List[Path]:
        """Discover all Matrix contracts."""
        return sorted(MATRIX_CONTRACTS.rglob("matrix_*.json"))

    def analyze_contract(self, contract_path: Path) -> ContractAnalysis:
        """Analyze a single Matrix contract for ΛiD compliance."""
        issues = []

        try:
            contract_data = json.loads(contract_path.read_text())
        except json.JSONDecodeError as e:
            return ContractAnalysis(
                path=contract_path,
                module=contract_path.stem.replace("matrix_", ""),
                has_identity=False,
                tiers=[], tier_numeric=[], webauthn_required=False,
                scopes=[], accepted_subjects=[],
                issues=[f"Invalid JSON: {e}"]
            )

        # Extract identity block
        identity = contract_data.get("identity", {})
        if not identity:
            issues.append("Missing identity block")

        # Extract tier information
        tiers = identity.get("required_tiers", [])
        tier_numeric = identity.get("required_tiers_numeric", [])

        # Validate tier consistency
        if tiers and tier_numeric:
            if len(tiers) != len(tier_numeric):
                issues.append("Tier arrays length mismatch")
            else:
                for tier, num in zip(tiers, tier_numeric):
                    if tier not in CANONICAL_TIERS:
                        issues.append(f"Invalid tier: {tier}")
                    elif TIER_TO_NUMERIC.get(tier) != num:
                        issues.append(f"Tier {tier} has wrong numeric value {num}, expected {TIER_TO_NUMERIC.get(tier)}")

        # Validate scopes format
        scopes = identity.get("scopes", [])
        module_name = contract_data.get("module", "").split(".")[-1]
        if scopes and module_name:
            expected_prefix = f"{module_name}."
            valid_scopes = [s for s in scopes if s.startswith(expected_prefix)]
            if len(valid_scopes) != len(scopes):
                issues.append(f"Some scopes don't follow {expected_prefix}* pattern")

        return ContractAnalysis(
            path=contract_path,
            module=contract_data.get("module", "unknown"),
            has_identity=bool(identity),
            tiers=tiers,
            tier_numeric=tier_numeric,
            webauthn_required=identity.get("webauthn_required", False),
            scopes=scopes,
            accepted_subjects=identity.get("accepted_subjects", []),
            issues=issues
        )

    def validate_all_contracts(self) -> List[ContractAnalysis]:
        """Validate all Matrix contracts for ΛiD compliance."""
        analyses = []

        for contract_path in self.contracts:
            analysis = self.analyze_contract(contract_path)
            analyses.append(analysis)

        return analyses

    def generate_report(self, analyses: List[ContractAnalysis]) -> Dict[str, Any]:
        """Generate comprehensive compliance report."""
        total_contracts = len(analyses)
        contracts_with_identity = sum(1 for a in analyses if a.has_identity)
        contracts_with_issues = sum(1 for a in analyses if a.issues)

        # Tier distribution
        tier_usage = {}
        for analysis in analyses:
            for tier in analysis.tiers:
                tier_usage[tier] = tier_usage.get(tier, 0) + 1

        # WebAuthn usage
        webauthn_required = sum(1 for a in analyses if a.webauthn_required)

        # Service account patterns
        service_account_usage = {}
        for analysis in analyses:
            for subject in analysis.accepted_subjects:
                if "lukhas:svc:" in subject:
                    service_account_usage[subject] = service_account_usage.get(subject, 0) + 1

        return {
            "summary": {
                "total_contracts": total_contracts,
                "contracts_with_identity": contracts_with_identity,
                "contracts_with_issues": contracts_with_issues,
                "compliance_rate": round(100 * (total_contracts - contracts_with_issues) / total_contracts, 1)
            },
            "tier_distribution": tier_usage,
            "webauthn_usage": {
                "required": webauthn_required,
                "not_required": total_contracts - webauthn_required,
                "percentage": round(100 * webauthn_required / total_contracts, 1)
            },
            "service_accounts": service_account_usage,
            "issues": [
                {
                    "contract": str(a.path.relative_to(ROOT)),
                    "module": a.module,
                    "issues": a.issues
                }
                for a in analyses if a.issues
            ]
        }

    def sync_tiers_to_contracts(self, dry_run: bool = True) -> List[Dict[str, Any]]:
        """Sync tier definitions from canonical source to Matrix contracts."""
        changes = []

        canonical_tiers = self.tier_permissions.get("tier_system", {}).get("tiers", CANONICAL_TIERS)
        canonical_mapping = {tier: i for i, tier in enumerate(canonical_tiers)}

        for contract_path in self.contracts:
            try:
                contract_data = json.loads(contract_path.read_text())
                identity = contract_data.get("identity", {})

                if not identity:
                    continue

                current_tiers = identity.get("required_tiers", [])
                current_numeric = identity.get("required_tiers_numeric", [])

                # Check if numeric mapping needs update
                needs_update = False
                new_numeric = []

                for tier in current_tiers:
                    if tier in canonical_mapping:
                        expected_num = canonical_mapping[tier]
                        new_numeric.append(expected_num)
                        if len(current_numeric) <= len(new_numeric) - 1 or current_numeric[len(new_numeric) - 1] != expected_num:
                            needs_update = True
                    else:
                        print(f"⚠️ Unknown tier '{tier}' in {contract_path}")

                if needs_update:
                    change = {
                        "contract": str(contract_path.relative_to(ROOT)),
                        "module": contract_data.get("module"),
                        "old_numeric": current_numeric,
                        "new_numeric": new_numeric
                    }
                    changes.append(change)

                    if not dry_run:
                        identity["required_tiers_numeric"] = new_numeric
                        contract_data["identity"] = identity
                        contract_path.write_text(json.dumps(contract_data, indent=2) + "\n")

            except Exception as e:
                print(f"❌ Error processing {contract_path}: {e}")

        return changes

    def check_tier_consistency(self) -> bool:
        """Check consistency between canonical tiers and contract usage."""
        analyses = self.validate_all_contracts()

        # Check for unknown tiers
        used_tiers = set()
        for analysis in analyses:
            used_tiers.update(analysis.tiers)

        canonical_set = set(CANONICAL_TIERS)
        unknown_tiers = used_tiers - canonical_set

        if unknown_tiers:
            print(f"❌ Unknown tiers found in contracts: {unknown_tiers}")
            return False

        print(f"✅ All {len(used_tiers)} used tiers are canonical")
        return True

def main():
    """CLI for ΛiD bridge operations."""
    parser = argparse.ArgumentParser(
        description="LUKHAS ΛiD Bridge - Matrix Contracts Integration",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("--validate", action="store_true",
                       help="Validate all Matrix contracts against ΛiD system")
    parser.add_argument("--report", action="store_true",
                       help="Generate compliance report")
    parser.add_argument("--sync", action="store_true",
                       help="Sync tier definitions to contracts")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show changes without applying them")
    parser.add_argument("--check-consistency", action="store_true",
                       help="Check tier consistency across all contracts")
    parser.add_argument("--output", type=str,
                       help="Output file for reports (JSON format)")

    args = parser.parse_args()

    if not any([args.validate, args.report, args.sync, args.check_consistency]):
        parser.print_help()
        return 1

    bridge = LukhasIdBridge()

    if args.check_consistency:
        print("🔍 Checking tier consistency...")
        if not bridge.check_tier_consistency():
            return 1

    if args.validate or args.report:
        print("🔍 Analyzing Matrix contracts...")
        analyses = bridge.validate_all_contracts()

        if args.report:
            report = bridge.generate_report(analyses)

            if args.output:
                Path(args.output).write_text(json.dumps(report, indent=2))
                print(f"📄 Report saved to {args.output}")
            else:
                print("\n📊 ΛiD Bridge Compliance Report")
                print("================================")
                print(f"Total contracts: {report['summary']['total_contracts']}")
                print(f"With identity blocks: {report['summary']['contracts_with_identity']}")
                print(f"Compliance rate: {report['summary']['compliance_rate']}%")
                print(f"WebAuthn usage: {report['webauthn_usage']['percentage']}%")

                if report['issues']:
                    print(f"\n⚠️ {len(report['issues'])} contracts with issues:")
                    for issue in report['issues'][:5]:  # Show first 5
                        print(f"  - {issue['contract']}: {', '.join(issue['issues'])}")

    if args.sync:
        print("🔄 Syncing tier definitions...")
        changes = bridge.sync_tiers_to_contracts(dry_run=args.dry_run)

        if changes:
            print(f"📝 Found {len(changes)} contracts needing updates")
            for change in changes[:5]:  # Show first 5
                print(f"  - {change['contract']}: {change['old_numeric']} → {change['new_numeric']}")

            if args.dry_run:
                print("🧪 Dry run mode - no changes applied")
            else:
                print("✅ Changes applied to contracts")
        else:
            print("✅ All contracts are up to date")

    return 0

if __name__ == "__main__":
    sys.exit(main())
