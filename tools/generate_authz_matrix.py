#!/usr/bin/env python3
"""
Authorization Matrix Generator

Auto-generates authorization test matrices for Matrix contracts.
For every interface.public_api.fn, creates test cases with different
(subject, tier, scopes) combinations to validate expected decisions.

Ensures authorization policy intent is executable and testable.
"""

import json
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass
import argparse


@dataclass
class AuthzTestCase:
    """Single authorization test case."""
    name: str
    subject: str
    tier: str
    tier_num: int
    scopes: List[str]
    action: str
    expected: bool
    mfa: bool = False
    webauthn_verified: bool = True
    reason: str = ""


class AuthzMatrixGenerator:
    """Generates authorization test matrices from Matrix contracts."""

    def __init__(self):
        """Initialize generator with ΛiD tier mappings."""
        self.tier_map = {
            "guest": 0, "visitor": 1, "friend": 2,
            "trusted": 3, "inner_circle": 4, "root_dev": 5
        }
        self.tier_names = list(self.tier_map.keys())

    def load_contract(self, contract_path: Path) -> Dict[str, Any]:
        """Load and validate Matrix contract."""
        if not contract_path.exists():
            raise FileNotFoundError(f"Contract not found: {contract_path}")

        with open(contract_path) as f:
            contract = json.load(f)

        if "identity" not in contract:
            raise ValueError(f"Contract {contract_path} has no identity block")

        return contract

    def generate_matrix_for_module(self, module_name: str) -> List[AuthzTestCase]:
        """Generate authorization matrix for a specific module."""

        # Find the contract file
        contract_path = Path(f"{module_name}/matrix_{module_name}.json")
        if not contract_path.exists():
            # Try alternative locations
            alt_paths = [
                Path(f"matrix_{module_name}.json"),
                Path(f"{module_name}/matrix_{module_name}.json"),
                Path(f"memory/matrix_memoria.json") if module_name == "memoria" else None
            ]
            for path in alt_paths:
                if path and path.exists():
                    contract_path = path
                    break
            else:
                raise FileNotFoundError(f"No contract found for module: {module_name}")

        contract = self.load_contract(contract_path)
        return self._generate_test_cases(contract, module_name)

    def _generate_test_cases(self, contract: Dict[str, Any], module_name: str) -> List[AuthzTestCase]:
        """Generate comprehensive test cases for a contract."""
        test_cases = []

        identity = contract["identity"]
        required_tiers = identity.get("required_tiers", [])
        required_tiers_numeric = identity.get("required_tiers_numeric", [])
        required_scopes = identity.get("scopes", [])
        api_policies = {p["fn"]: p for p in identity.get("api_policies", [])}

        # Get public APIs
        public_apis = contract.get("interface", {}).get("public_api", [])

        # Generate baseline test cases for each tier
        for tier_name in self.tier_names:
            tier_num = self.tier_map[tier_name]

            # Determine if tier should be allowed
            tier_allowed = self._is_tier_allowed(
                tier_name, tier_num, required_tiers, required_tiers_numeric
            )

            # Test each public API
            for api in public_apis:
                fn_name = api["fn"]

                # Basic access test
                test_cases.append(AuthzTestCase(
                    name=f"{tier_name}_{fn_name}_basic",
                    subject=f"lukhas:user:test_{tier_name}",
                    tier=tier_name,
                    tier_num=tier_num,
                    scopes=required_scopes.copy(),
                    action=fn_name,
                    expected=tier_allowed,
                    reason=f"Tier {tier_name} {'allowed' if tier_allowed else 'denied'} for {fn_name}"
                ))

                # Step-up requirement test
                if fn_name in api_policies and api_policies[fn_name].get("requires_step_up", False):
                    # Without MFA (should fail)
                    test_cases.append(AuthzTestCase(
                        name=f"{tier_name}_{fn_name}_no_mfa",
                        subject=f"lukhas:user:test_{tier_name}",
                        tier=tier_name,
                        tier_num=tier_num,
                        scopes=required_scopes.copy(),
                        action=fn_name,
                        expected=False,
                        mfa=False,
                        reason=f"Step-up required for {fn_name} but MFA not provided"
                    ))

                    # With MFA (should pass if tier allowed)
                    test_cases.append(AuthzTestCase(
                        name=f"{tier_name}_{fn_name}_with_mfa",
                        subject=f"lukhas:user:test_{tier_name}",
                        tier=tier_name,
                        tier_num=tier_num,
                        scopes=required_scopes.copy(),
                        action=fn_name,
                        expected=tier_allowed,
                        mfa=True,
                        reason=f"Step-up satisfied for {fn_name} with MFA"
                    ))

                # Extra scopes test
                if fn_name in api_policies and api_policies[fn_name].get("extra_scopes"):
                    extra_scopes = api_policies[fn_name]["extra_scopes"]
                    full_scopes = required_scopes + extra_scopes

                    test_cases.append(AuthzTestCase(
                        name=f"{tier_name}_{fn_name}_extra_scopes",
                        subject=f"lukhas:user:test_{tier_name}",
                        tier=tier_name,
                        tier_num=tier_num,
                        scopes=full_scopes,
                        action=fn_name,
                        expected=tier_allowed,
                        reason=f"Extra scopes provided for {fn_name}"
                    ))

        # Add edge cases
        test_cases.extend(self._generate_edge_cases(contract, module_name))

        # Add service account test cases
        test_cases.extend(self._generate_service_cases(contract, module_name))

        return test_cases

    def _is_tier_allowed(
        self,
        tier_name: str,
        tier_num: int,
        required_tiers: List[str],
        required_tiers_numeric: List[int]
    ) -> bool:
        """Determine if a tier meets the requirements."""

        # If no requirements, any authenticated tier is allowed
        if not required_tiers and not required_tiers_numeric:
            return True

        # Check textual tier requirements
        if required_tiers and tier_name in required_tiers:
            return True

        # Check numeric tier requirements
        if required_tiers_numeric and tier_num in required_tiers_numeric:
            return True

        return False

    def _generate_edge_cases(self, contract: Dict[str, Any], module_name: str) -> List[AuthzTestCase]:
        """Generate edge case test scenarios."""
        edge_cases = []

        identity = contract["identity"]
        required_scopes = identity.get("scopes", [])

        # Missing scopes test
        if required_scopes:
            edge_cases.append(AuthzTestCase(
                name="trusted_missing_scopes",
                subject="lukhas:user:test_trusted",
                tier="trusted",
                tier_num=3,
                scopes=[],  # No scopes provided
                action="read",
                expected=False,
                reason="Missing required scopes"
            ))

            # Partial scopes test
            if len(required_scopes) > 1:
                edge_cases.append(AuthzTestCase(
                    name="trusted_partial_scopes",
                    subject="lukhas:user:test_trusted",
                    tier="trusted",
                    tier_num=3,
                    scopes=[required_scopes[0]],  # Only first scope
                    action="read",
                    expected=False,
                    reason="Partial scopes provided"
                ))

        # Expired token test
        edge_cases.append(AuthzTestCase(
            name="trusted_expired_token",
            subject="lukhas:user:test_trusted",
            tier="trusted",
            tier_num=3,
            scopes=required_scopes.copy(),
            action="read",
            expected=False,
            reason="Token expired"
        ))

        # Wrong audience test
        edge_cases.append(AuthzTestCase(
            name="trusted_wrong_audience",
            subject="lukhas:user:test_trusted",
            tier="trusted",
            tier_num=3,
            scopes=required_scopes.copy(),
            action="read",
            expected=False,
            reason="Wrong audience in token"
        ))

        return edge_cases

    def _generate_service_cases(self, contract: Dict[str, Any], module_name: str) -> List[AuthzTestCase]:
        """Generate service account authorization test cases."""
        service_cases = []

        identity = contract["identity"]
        accepted_subjects = identity.get("accepted_subjects", [])
        required_scopes = identity.get("scopes", [])

        # Service account allowed
        if any("lukhas:svc:" in subj for subj in accepted_subjects):
            service_cases.append(AuthzTestCase(
                name="service_orchestrator_allowed",
                subject="lukhas:svc:orchestrator",
                tier="root_dev",  # Services typically have high tier
                tier_num=5,
                scopes=required_scopes.copy(),
                action="process",
                expected=True,
                reason="Service account in accepted subjects"
            ))

        # Service account denied
        service_cases.append(AuthzTestCase(
            name="service_unknown_denied",
            subject="lukhas:svc:unknown",
            tier="root_dev",
            tier_num=5,
            scopes=required_scopes.copy(),
            action="process",
            expected=False if accepted_subjects else True,
            reason="Unknown service account"
        ))

        return service_cases

    def save_matrix_yaml(self, test_cases: List[AuthzTestCase], output_path: Path) -> None:
        """Save test matrix as YAML fixture."""

        # Convert test cases to YAML structure
        yaml_data = {
            "module": output_path.stem.replace("_authz", ""),
            "generated": "auto-generated by generate_authz_matrix.py",
            "test_cases": []
        }

        for case in test_cases:
            yaml_data["test_cases"].append({
                "name": case.name,
                "input": {
                    "subject": case.subject,
                    "tier": case.tier,
                    "tier_num": case.tier_num,
                    "scopes": case.scopes,
                    "action": case.action,
                    "env": {
                        "mfa": case.mfa,
                        "webauthn_verified": case.webauthn_verified
                    }
                },
                "expected": case.expected,
                "reason": case.reason
            })

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save as YAML
        with open(output_path, 'w') as f:
            yaml.dump(yaml_data, f, default_flow_style=False, sort_keys=False, indent=2)

    def save_matrix_json(self, test_cases: List[AuthzTestCase], output_path: Path) -> None:
        """Save test matrix as JSON fixture."""

        json_data = {
            "module": output_path.stem.replace("_authz", ""),
            "generated": "auto-generated by generate_authz_matrix.py",
            "test_cases": [
                {
                    "name": case.name,
                    "input": {
                        "subject": case.subject,
                        "tier": case.tier,
                        "tier_num": case.tier_num,
                        "scopes": case.scopes,
                        "action": case.action,
                        "env": {
                            "mfa": case.mfa,
                            "webauthn_verified": case.webauthn_verified
                        }
                    },
                    "expected": case.expected,
                    "reason": case.reason
                }
                for case in test_cases
            ]
        }

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save as JSON
        with open(output_path, 'w') as f:
            json.dump(json_data, f, indent=2)


def main():
    """CLI for generating authorization matrices."""
    parser = argparse.ArgumentParser(description="Generate authorization test matrices")
    parser.add_argument("--module", required=True, help="Module name (e.g., memoria)")
    parser.add_argument("--output-dir", default="tests/authz", help="Output directory")
    parser.add_argument("--format", choices=["yaml", "json"], default="yaml", help="Output format")

    args = parser.parse_args()

    generator = AuthzMatrixGenerator()

    try:
        # Generate test cases
        print(f"🔧 Generating authorization matrix for module: {args.module}")
        test_cases = generator.generate_matrix_for_module(args.module)

        # Save matrix
        output_dir = Path(args.output_dir)
        output_file = output_dir / f"{args.module}_authz.{args.format}"

        if args.format == "yaml":
            generator.save_matrix_yaml(test_cases, output_file)
        else:
            generator.save_matrix_json(test_cases, output_file)

        print(f"✅ Generated {len(test_cases)} test cases")
        print(f"   Output: {output_file}")

        # Summary by result
        allowed_count = sum(1 for case in test_cases if case.expected)
        denied_count = len(test_cases) - allowed_count

        print(f"   Expected: {allowed_count} allowed, {denied_count} denied")

        # Summary by tier
        tier_summary = {}
        for case in test_cases:
            tier = case.tier
            if tier not in tier_summary:
                tier_summary[tier] = {"allowed": 0, "denied": 0}

            if case.expected:
                tier_summary[tier]["allowed"] += 1
            else:
                tier_summary[tier]["denied"] += 1

        print("   Tier breakdown:")
        for tier, counts in tier_summary.items():
            print(f"     {tier}: {counts['allowed']} allowed, {counts['denied']} denied")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()