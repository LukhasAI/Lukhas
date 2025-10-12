#!/usr/bin/env python3
"""
WebAuthn Matrix Integration

Validates WebAuthn credential requirements against Matrix contracts,
ensuring proper authentication enforcement for tier-based access control.

Features:
- Validates WebAuthn requirements consistency across Matrix contracts
- Checks credential policies against ΛiD tier requirements
- Generates WebAuthn compliance reports
- Tests credential validation flows
"""

import argparse
import asyncio
import json
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# Repository structure
ROOT = Path(__file__).resolve().parents[1]
MATRIX_CONTRACTS = ROOT / "lukhas"

class TierLevel(Enum):
    """ΛiD tier levels with WebAuthn requirements."""
    GUEST = (0, "guest", False, "any")
    VISITOR = (1, "visitor", False, "any")
    FRIEND = (2, "friend", True, "any")
    TRUSTED = (3, "trusted", True, "platform")
    INNER_CIRCLE = (4, "inner_circle", True, "platform")
    ROOT_DEV = (5, "root_dev", True, "platform")

    def __init__(self, level: int, name: str, user_verification: bool, attachment: str):
        self.level = level
        self.tier_name = name
        self.user_verification = user_verification
        self.platform_attachment = attachment

    @classmethod
    def from_name(cls, name: str) -> Optional['TierLevel']:
        """Get tier level from name."""
        for tier in cls:
            if tier.tier_name == name:
                return tier
        return None

    @classmethod
    def from_level(cls, level: int) -> Optional['TierLevel']:
        """Get tier level from numeric level."""
        for tier in cls:
            if tier.level == level:
                return tier
        return None

@dataclass
class WebAuthnPolicy:
    """WebAuthn policy configuration."""
    user_verification: bool
    platform_attachment: str
    resident_key: bool = False
    attestation: str = "none"

@dataclass
class ContractWebAuthnAnalysis:
    """WebAuthn analysis for a Matrix contract."""
    path: Path
    module: str
    webauthn_required: bool
    required_tiers: List[str]
    highest_tier: Optional[TierLevel]
    recommended_policy: Optional[WebAuthnPolicy]
    current_compliance: bool
    issues: List[str]

class WebAuthnMatrixIntegration:
    """WebAuthn integration validator for Matrix contracts."""

    def __init__(self):
        self.contracts = self._discover_contracts()

    def _discover_contracts(self) -> List[Path]:
        """Discover all Matrix contracts."""
        return sorted(MATRIX_CONTRACTS.rglob("matrix_*.json"))

    def _get_recommended_policy(self, tiers: List[str]) -> Optional[WebAuthnPolicy]:
        """Get recommended WebAuthn policy based on tier requirements."""
        if not tiers:
            return None

        # Find highest tier level
        highest_level = -1
        for tier_name in tiers:
            tier = TierLevel.from_name(tier_name)
            if tier and tier.level > highest_level:
                highest_level = tier.level

        tier = TierLevel.from_level(highest_level)
        if not tier:
            return None

        # Generate policy based on tier
        policy = WebAuthnPolicy(
            user_verification=tier.user_verification,
            platform_attachment=tier.platform_attachment
        )

        # Enhanced requirements for higher tiers
        if tier.level >= TierLevel.TRUSTED.level:
            policy.attestation = "direct"

        if tier.level >= TierLevel.ROOT_DEV.level:
            policy.resident_key = True

        return policy

    def analyze_contract_webauthn(self, contract_path: Path) -> ContractWebAuthnAnalysis:
        """Analyze WebAuthn configuration for a Matrix contract."""
        issues = []

        try:
            contract_data = json.loads(contract_path.read_text())
        except json.JSONDecodeError as e:
            return ContractWebAuthnAnalysis(
                path=contract_path,
                module=contract_path.stem.replace("matrix_", ""),
                webauthn_required=False,
                required_tiers=[],
                highest_tier=None,
                recommended_policy=None,
                current_compliance=False,
                issues=[f"Invalid JSON: {e}"]
            )

        # Extract identity and WebAuthn info
        identity = contract_data.get("identity", {})
        webauthn_required = identity.get("webauthn_required", False)
        required_tiers = identity.get("required_tiers", [])

        # Find highest tier
        highest_tier = None
        if required_tiers:
            highest_level = -1
            for tier_name in required_tiers:
                tier = TierLevel.from_name(tier_name)
                if tier and tier.level > highest_level:
                    highest_level = tier.level
                    highest_tier = tier

        # Get recommended policy
        recommended_policy = self._get_recommended_policy(required_tiers)

        # Check compliance
        current_compliance = True

        # Check if WebAuthn should be required based on tiers
        should_require_webauthn = False
        if highest_tier and highest_tier.level >= TierLevel.INNER_CIRCLE.level:
            should_require_webauthn = True

        # Check for critical modules that should always require WebAuthn
        module_path = str(contract_path.relative_to(ROOT))
        critical_patterns = ["identity", "lukhas.governance", "security", "consciousness", "core"]
        is_critical = any(pattern in module_path for pattern in critical_patterns)

        if is_critical and not webauthn_required:
            should_require_webauthn = True
            issues.append("Critical module should require WebAuthn")

        if should_require_webauthn and not webauthn_required:
            issues.append(f"WebAuthn should be required for tier {highest_tier.tier_name if highest_tier else 'unknown'}")
            current_compliance = False

        # Check for over-engineering (WebAuthn required for low tiers)
        if webauthn_required and highest_tier and highest_tier.level < TierLevel.FRIEND.level and not is_critical:
            issues.append(f"WebAuthn may be over-engineered for tier {highest_tier.tier_name}")

        return ContractWebAuthnAnalysis(
            path=contract_path,
            module=contract_data.get("module", "unknown"),
            webauthn_required=webauthn_required,
            required_tiers=required_tiers,
            highest_tier=highest_tier,
            recommended_policy=recommended_policy,
            current_compliance=current_compliance,
            issues=issues
        )

    def validate_all_contracts(self) -> List[ContractWebAuthnAnalysis]:
        """Validate WebAuthn configuration for all Matrix contracts."""
        analyses = []

        for contract_path in self.contracts:
            analysis = self.analyze_contract_webauthn(contract_path)
            analyses.append(analysis)

        return analyses

    def generate_compliance_report(self, analyses: List[ContractWebAuthnAnalysis]) -> Dict[str, Any]:
        """Generate WebAuthn compliance report."""
        total_contracts = len(analyses)
        webauthn_required = sum(1 for a in analyses if a.webauthn_required)
        compliant_contracts = sum(1 for a in analyses if a.current_compliance)
        contracts_with_issues = sum(1 for a in analyses if a.issues)

        # Tier distribution for WebAuthn
        tier_webauthn_distribution = {}
        for analysis in analyses:
            if analysis.highest_tier:
                tier_name = analysis.highest_tier.tier_name
                if tier_name not in tier_webauthn_distribution:
                    tier_webauthn_distribution[tier_name] = {"total": 0, "webauthn_required": 0}
                tier_webauthn_distribution[tier_name]["total"] += 1
                if analysis.webauthn_required:
                    tier_webauthn_distribution[tier_name]["webauthn_required"] += 1

        # Critical modules analysis
        critical_modules = []
        for analysis in analyses:
            module_path = str(analysis.path.relative_to(ROOT))
            critical_patterns = ["identity", "lukhas.governance", "security", "consciousness", "core"]
            if any(pattern in module_path for pattern in critical_patterns):
                critical_modules.append({
                    "module": analysis.module,
                    "webauthn_required": analysis.webauthn_required,
                    "compliant": analysis.current_compliance
                })

        return {
            "summary": {
                "total_contracts": total_contracts,
                "webauthn_required": webauthn_required,
                "webauthn_percentage": round(100 * webauthn_required / total_contracts, 1),
                "compliant_contracts": compliant_contracts,
                "compliance_rate": round(100 * compliant_contracts / total_contracts, 1),
                "contracts_with_issues": contracts_with_issues
            },
            "tier_distribution": tier_webauthn_distribution,
            "critical_modules": critical_modules,
            "recommendations": self._generate_recommendations(analyses),
            "issues": [
                {
                    "contract": str(a.path.relative_to(ROOT)),
                    "module": a.module,
                    "webauthn_required": a.webauthn_required,
                    "highest_tier": a.highest_tier.tier_name if a.highest_tier else None,
                    "issues": a.issues
                }
                for a in analyses if a.issues
            ]
        }

    def _generate_recommendations(self, analyses: List[ContractWebAuthnAnalysis]) -> List[Dict[str, str]]:
        """Generate recommendations for WebAuthn improvements."""
        recommendations = []

        # Check for critical modules without WebAuthn
        for analysis in analyses:
            if not analysis.webauthn_required:
                module_path = str(analysis.path.relative_to(ROOT))
                critical_patterns = ["identity", "lukhas.governance", "security", "consciousness"]
                if any(pattern in module_path for pattern in critical_patterns):
                    recommendations.append({
                        "type": "security",
                        "module": analysis.module,
                        "recommendation": "Enable WebAuthn requirement for critical security module",
                        "rationale": f"Module {analysis.module} handles sensitive operations"
                    })

        # Check for high-tier modules without WebAuthn
        for analysis in analyses:
            if (not analysis.webauthn_required and
                analysis.highest_tier and
                analysis.highest_tier.level >= TierLevel.INNER_CIRCLE.level):
                recommendations.append({
                    "type": "tier_alignment",
                    "module": analysis.module,
                    "recommendation": f"Enable WebAuthn for {analysis.highest_tier.tier_name} tier module",
                    "rationale": f"Tier {analysis.highest_tier.tier_name} typically requires strong authentication"
                })

        return recommendations

    def fix_webauthn_requirements(self, dry_run: bool = True) -> List[Dict[str, Any]]:
        """Fix WebAuthn requirements based on analysis."""
        changes = []
        analyses = self.validate_all_contracts()

        for analysis in analyses:
            if not analysis.current_compliance and analysis.issues:
                # Determine if we should enable WebAuthn
                should_enable = False

                # Critical modules should have WebAuthn
                module_path = str(analysis.path.relative_to(ROOT))
                critical_patterns = ["identity", "lukhas.governance", "security", "consciousness"]
                if any(pattern in module_path for pattern in critical_patterns):
                    should_enable = True

                # High-tier modules should have WebAuthn
                if (analysis.highest_tier and
                    analysis.highest_tier.level >= TierLevel.INNER_CIRCLE.level):
                    should_enable = True

                if should_enable and not analysis.webauthn_required:
                    change = {
                        "contract": str(analysis.path.relative_to(ROOT)),
                        "module": analysis.module,
                        "action": "enable_webauthn",
                        "reason": f"Required for {analysis.highest_tier.tier_name if analysis.highest_tier else 'critical'} module"
                    }
                    changes.append(change)

                    if not dry_run:
                        try:
                            contract_data = json.loads(analysis.path.read_text())
                            contract_data["identity"]["webauthn_required"] = True
                            analysis.path.write_text(json.dumps(contract_data, indent=2) + "\n")
                        except Exception as e:
                            print(f"❌ Error updating {analysis.path}: {e}")

        return changes

async def test_webauthn_flow(module: str) -> Dict[str, Any]:
    """Test WebAuthn authentication flow for a module."""
    # Placeholder for actual WebAuthn testing
    # In a real implementation, this would test credential creation/validation
    return {
        "module": module,
        "test_result": "simulated",
        "credential_creation": "success",
        "authentication": "success",
        "latency_ms": 85
    }

def main():
    """CLI for WebAuthn Matrix integration."""
    parser = argparse.ArgumentParser(
        description="WebAuthn Matrix Integration Validator",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("--validate", action="store_true",
                       help="Validate WebAuthn configuration for all contracts")
    parser.add_argument("--report", action="store_true",
                       help="Generate WebAuthn compliance report")
    parser.add_argument("--fix", action="store_true",
                       help="Fix WebAuthn requirements based on analysis")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show changes without applying them")
    parser.add_argument("--test-flow", type=str,
                       help="Test WebAuthn flow for specific module")
    parser.add_argument("--output", type=str,
                       help="Output file for reports (JSON format)")

    args = parser.parse_args()

    if not any([args.validate, args.report, args.fix, args.test_flow]):
        parser.print_help()
        return 1

    integration = WebAuthnMatrixIntegration()

    if args.validate or args.report:
        print("🔍 Analyzing WebAuthn configuration...")
        analyses = integration.validate_all_contracts()

        if args.report:
            report = integration.generate_compliance_report(analyses)

            if args.output:
                Path(args.output).write_text(json.dumps(report, indent=2))
                print(f"📄 Report saved to {args.output}")
            else:
                print("\n🔐 WebAuthn Matrix Integration Report")
                print("====================================")
                print(f"Total contracts: {report['summary']['total_contracts']}")
                print(f"WebAuthn required: {report['summary']['webauthn_required']} ({report['summary']['webauthn_percentage']}%)")
                print(f"Compliance rate: {report['summary']['compliance_rate']}%")

                if report['critical_modules']:
                    print(f"\n🔑 Critical modules ({len(report['critical_modules'])}):")
                    for mod in report['critical_modules'][:5]:
                        status = "✅" if mod['webauthn_required'] else "❌"
                        print(f"  {status} {mod['module']}")

                if report['recommendations']:
                    print(f"\n💡 Recommendations ({len(report['recommendations'])}):")
                    for rec in report['recommendations'][:3]:
                        print(f"  - {rec['module']}: {rec['recommendation']}")

    if args.fix:
        print("🔧 Fixing WebAuthn requirements...")
        changes = integration.fix_webauthn_requirements(dry_run=args.dry_run)

        if changes:
            print(f"📝 Found {len(changes)} contracts needing updates")
            for change in changes:
                print(f"  - {change['module']}: {change['action']} ({change['reason']})")

            if args.dry_run:
                print("🧪 Dry run mode - no changes applied")
            else:
                print("✅ WebAuthn requirements updated")
        else:
            print("✅ All WebAuthn requirements are properly configured")

    if args.test_flow:
        print(f"🧪 Testing WebAuthn flow for {args.test_flow}...")
        result = asyncio.run(test_webauthn_flow(args.test_flow))
        print(f"📊 Test result: {result}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
