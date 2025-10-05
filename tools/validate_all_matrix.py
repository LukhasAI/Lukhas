#!/usr/bin/env python3
"""
Unified Matrix Contract Validator

Validates all Matrix contracts against schema and identity requirements.
Produces comprehensive validation results for CI/CD pipeline.
"""

import argparse
import json
import sys
from datetime import datetime
from glob import glob
from pathlib import Path
from typing import Any, Dict, List, Tuple

from jsonschema import Draft202012Validator

# Repository structure
ROOT = Path(__file__).resolve().parents[1]

# Valid tier names
VALID_TIERS = {"guest", "visitor", "friend", "trusted", "inner_circle", "root_dev"}
TIER_LEVELS = {
    "guest": 0,
    "visitor": 1,
    "friend": 2,
    "trusted": 3,
    "inner_circle": 4,
    "root_dev": 5
}

class MatrixValidator:
    """Comprehensive Matrix contract validator."""

    def __init__(self, schema_path: str):
        """Initialize validator with schema."""
        self.schema_path = Path(schema_path)
        self.schema = self._load_schema()
        self.results = {}

    def _load_schema(self) -> Dict[str, Any]:
        """Load Matrix contract schema."""
        try:
            return json.loads(self.schema_path.read_text())
        except Exception as e:
            print(f"❌ Failed to load schema: {e}")
            sys.exit(1)

    def find_contracts(self, pattern: str) -> List[Path]:
        """Find all Matrix contracts matching pattern."""
        contracts = []
        for path in glob(pattern, recursive=True):
            contracts.append(Path(path))
        return sorted(contracts)

    def validate_schema(self, contract_path: Path) -> Tuple[bool, List[str]]:
        """Validate contract against JSON schema."""
        errors = []

        try:
            contract = json.loads(contract_path.read_text())
            validator = Draft202012Validator(self.schema)

            for error in validator.iter_errors(contract):
                error_path = " -> ".join(str(e) for e in error.path) if error.path else "root"
                errors.append(f"Schema: {error_path}: {error.message}")

            return len(errors) == 0, errors

        except json.JSONDecodeError as e:
            return False, [f"JSON parse error: {e}"]
        except Exception as e:
            return False, [f"Unexpected error: {e}"]

    def validate_identity(self, contract_path: Path) -> Tuple[bool, List[str], Dict[str, Any]]:
        """Validate identity block requirements."""
        errors = []
        identity_info = {}

        try:
            contract = json.loads(contract_path.read_text())

            # Check for identity block
            if "identity" not in contract:
                errors.append("Identity: Missing identity block")
                return False, errors, identity_info

            identity = contract["identity"]
            identity_info = {
                "requires_auth": identity.get("requires_auth", True),
                "webauthn_required": identity.get("webauthn_required", False),
                "tiers": identity.get("required_tiers", []),
                "tiers_numeric": identity.get("required_tiers_numeric", []),
                "scopes": identity.get("scopes", []),
                "accepted_subjects": identity.get("accepted_subjects", []),
                "api_policies": identity.get("api_policies", [])
            }

            # Validate tiers
            if identity_info["tiers"]:
                for tier in identity_info["tiers"]:
                    if tier not in VALID_TIERS:
                        errors.append(f"Identity: Invalid tier '{tier}'")

                # Check tier-numeric consistency
                if identity_info["tiers_numeric"]:
                    if len(identity_info["tiers"]) != len(identity_info["tiers_numeric"]):
                        errors.append("Identity: Tier arrays length mismatch")
                    else:
                        for i, (tier, num) in enumerate(zip(identity_info["tiers"], identity_info["tiers_numeric"])):
                            expected = TIER_LEVELS.get(tier)
                            if expected is not None and expected != num:
                                errors.append(f"Identity: Tier '{tier}' has wrong numeric value {num}, expected {expected}")
            else:
                errors.append("Identity: No required_tiers specified")

            # Validate scopes for auth-required modules
            if identity_info["requires_auth"] and not identity_info["scopes"]:
                errors.append("Identity: No scopes defined for auth-required module")

            # Validate accepted subjects
            if not identity_info["accepted_subjects"]:
                errors.append("Identity: No accepted_subjects defined")
            else:
                for subject in identity_info["accepted_subjects"]:
                    if not (subject.startswith("lukhas:user:") or subject.startswith("lukhas:svc:")):
                        errors.append(f"Identity: Invalid subject pattern '{subject}'")

            # Check WebAuthn for critical modules
            module_name = contract.get("module", "")
            critical_patterns = ["identity", "auth", "security", "governance", "wallet", "passkey"]
            is_critical = any(pattern in module_name.lower() for pattern in critical_patterns)

            if is_critical and not identity_info["webauthn_required"]:
                errors.append(f"Identity: Critical module '{module_name}' should require WebAuthn")

            # Check high-tier WebAuthn requirement
            if "inner_circle" in identity_info["tiers"] or "root_dev" in identity_info["tiers"]:
                if not identity_info["webauthn_required"]:
                    errors.append("Identity: High-tier module should require WebAuthn")

            return len(errors) == 0, errors, identity_info

        except Exception as e:
            return False, [f"Identity validation error: {e}"], {}

    def validate_tokenization(self, contract_path: Path) -> Tuple[bool, List[str]]:
        """Validate tokenization block."""
        errors = []

        try:
            contract = json.loads(contract_path.read_text())

            if "tokenization" in contract:
                tokenization = contract["tokenization"]

                # Check enabled field
                if "enabled" in tokenization:
                    if not isinstance(tokenization["enabled"], bool):
                        errors.append("Tokenization: 'enabled' must be boolean")

                # Check network if enabled
                if tokenization.get("enabled", False):
                    if "network" not in tokenization:
                        errors.append("Tokenization: Missing 'network' for enabled tokenization")
                    elif tokenization["network"] not in ["solana", "ethereum", "polygon", "base", "arbitrum", "optimism", "near", "avalanche", "cosmos", "celestia", "tezos"]:
                        errors.append(f"Tokenization: Invalid network '{tokenization.get('network')}'")

            return len(errors) == 0, errors

        except Exception as e:
            return False, [f"Tokenization validation error: {e}"]

    def validate_contract(self, contract_path: Path) -> Dict[str, Any]:
        """Perform comprehensive validation of a single contract."""
        module_name = contract_path.stem.replace("matrix_", "")

        # Schema validation
        schema_ok, schema_errors = self.validate_schema(contract_path)

        # Identity validation
        identity_ok, identity_errors, identity_info = self.validate_identity(contract_path)

        # Tokenization validation
        tokenization_ok, tokenization_errors = self.validate_tokenization(contract_path)

        # Combine all errors
        all_errors = schema_errors + identity_errors + tokenization_errors

        return {
            "path": str(contract_path),
            "module": module_name,
            "schema_ok": schema_ok,
            "identity_ok": identity_ok,
            "tokenization_ok": tokenization_ok,
            "valid": schema_ok and identity_ok and tokenization_ok,
            "errors": all_errors,
            "identity_info": identity_info,
            "error_count": len(all_errors)
        }

    def validate_all(self, pattern: str, identity_lint: bool = True) -> Dict[str, Any]:
        """Validate all contracts matching pattern."""
        print(f"🔍 Finding contracts matching: {pattern}")
        contracts = self.find_contracts(pattern)
        print(f"📦 Found {len(contracts)} contracts to validate")

        results = {}
        summary = {
            "total": 0,
            "valid": 0,
            "schema_ok": 0,
            "identity_ok": 0,
            "tokenization_ok": 0,
            "critical_modules": 0,
            "webauthn_required": 0,
            "errors_by_type": {
                "schema": 0,
                "identity": 0,
                "tokenization": 0
            }
        }

        print("\n⚡ Validating contracts...")
        for contract_path in contracts:
            result = self.validate_contract(contract_path)
            module_name = result["module"]
            results[module_name] = result

            # Update summary
            summary["total"] += 1
            if result["valid"]:
                summary["valid"] += 1
                print(f"  ✅ {module_name}")
            else:
                print(f"  ❌ {module_name}: {result['error_count']} errors")
                for error in result["errors"][:3]:  # Show first 3 errors
                    print(f"     - {error}")

            if result["schema_ok"]:
                summary["schema_ok"] += 1
            if result["identity_ok"]:
                summary["identity_ok"] += 1
            if result["tokenization_ok"]:
                summary["tokenization_ok"] += 1

            # Count error types
            for error in result["errors"]:
                if error.startswith("Schema:"):
                    summary["errors_by_type"]["schema"] += 1
                elif error.startswith("Identity:"):
                    summary["errors_by_type"]["identity"] += 1
                elif error.startswith("Tokenization:"):
                    summary["errors_by_type"]["tokenization"] += 1

            # Check if WebAuthn required
            if result.get("identity_info", {}).get("webauthn_required"):
                summary["webauthn_required"] += 1

            # Check if critical module
            module_name_full = f"lukhas.{module_name}"
            critical_patterns = ["identity", "auth", "security", "governance"]
            if any(pattern in module_name_full.lower() for pattern in critical_patterns):
                summary["critical_modules"] += 1

        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "summary": summary,
            "modules": results
        }

def main():
    """CLI for unified Matrix validation."""
    parser = argparse.ArgumentParser(
        description="Unified Matrix Contract Validator",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("--schema", required=True,
                       help="Path to matrix.schema.template.json")
    parser.add_argument("--pattern", default="**/matrix_*.json",
                       help="Glob pattern for finding contracts")
    parser.add_argument("--identity", action="store_true",
                       help="Enable identity lint checks")
    parser.add_argument("--output-json", type=str,
                       help="Output file for JSON results")
    parser.add_argument("--quiet", action="store_true",
                       help="Suppress verbose output")

    args = parser.parse_args()

    # Initialize validator
    validator = MatrixValidator(args.schema)

    # Run validation
    results = validator.validate_all(args.pattern, identity_lint=args.identity)

    # Output results
    if args.output_json:
        output_path = Path(args.output_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(results, indent=2))
        if not args.quiet:
            print(f"\n📄 Results written to: {args.output_json}")

    # Print summary
    if not args.quiet:
        summary = results["summary"]
        print("\n" + "=" * 60)
        print("📊 Validation Summary")
        print(f"  Total contracts: {summary['total']}")
        print(f"  Valid: {summary['valid']}/{summary['total']} ({100*summary['valid']/summary['total']:.1f}%)")
        print(f"  Schema OK: {summary['schema_ok']}/{summary['total']}")
        print(f"  Identity OK: {summary['identity_ok']}/{summary['total']}")
        print(f"  Tokenization OK: {summary['tokenization_ok']}/{summary['total']}")
        print(f"  WebAuthn required: {summary['webauthn_required']}")
        print(f"  Critical modules: {summary['critical_modules']}")

        if summary["errors_by_type"]["schema"] > 0:
            print(f"\n  Schema errors: {summary['errors_by_type']['schema']}")
        if summary["errors_by_type"]["identity"] > 0:
            print(f"  Identity errors: {summary['errors_by_type']['identity']}")
        if summary["errors_by_type"]["tokenization"] > 0:
            print(f"  Tokenization errors: {summary['errors_by_type']['tokenization']}")

    # Exit with appropriate code
    if results["summary"]["valid"] < results["summary"]["total"]:
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
