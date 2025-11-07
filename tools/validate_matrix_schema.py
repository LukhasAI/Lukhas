#!/usr/bin/env python3
"""
Matrix Contract Schema Validator

Validates all generated Matrix contracts against the authoritative schema template.
"""

import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

# Repository structure
ROOT = Path(__file__).resolve().parents[1]
CONTRACTS_DIR = ROOT / "contracts"
SCHEMA_FILE = ROOT / "matrix.schema.template.json"

def load_schema() -> dict[str, Any]:
    """Load the Matrix contract schema."""
    return json.loads(SCHEMA_FILE.read_text())

def validate_contract(contract_path: Path, schema: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate a contract against the schema."""
    errors = []

    try:
        contract = json.loads(contract_path.read_text())

        # Create validator
        validator = Draft202012Validator(schema)

        # Collect validation errors
        for error in validator.iter_errors(contract):
            error_path = " -> ".join(str(e) for e in error.path) if error.path else "root"
            errors.append(f"{error_path}: {error.message}")

        # Additional custom validations

        # Check tier consistency
        if "identity" in contract:
            identity = contract["identity"]
            if "required_tiers" in identity and "required_tiers_numeric" in identity:
                tiers = identity["required_tiers"]
                nums = identity["required_tiers_numeric"]

                if len(tiers) != len(nums):
                    errors.append("identity: tier arrays length mismatch")

                tier_map = {
                    "guest": 0, "visitor": 1, "friend": 2,
                    "trusted": 3, "inner_circle": 4, "root_dev": 5
                }

                for i, tier in enumerate(tiers):
                    if i < len(nums) and tier_map.get(tier) != nums[i]:
                        errors.append(f"identity: tier '{tier}' has wrong numeric value {nums[i]}")

        # Check tokenization
        if "tokenization" in contract:
            tok = contract["tokenization"]
            if tok.get("enabled", False) and not tok.get("mint_address"):
                errors.append("tokenization: enabled but no mint_address")

        return len(errors) == 0, errors

    except json.JSONDecodeError as e:
        return False, [f"JSON parsing error: {e}"]
    except Exception as e:
        return False, [f"Unexpected error: {e}"]

def main():
    """Validate all Matrix contracts."""
    print("🔍 Matrix Contract Schema Validator")
    print("=" * 60)

    # Load schema
    print("📋 Loading schema from matrix.schema.template.json...")
    try:
        schema = load_schema()
        print("✅ Schema loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load schema: {e}")
        return 1

    # Find all contracts
    print("\n🔍 Discovering contracts...")
    contracts = sorted(CONTRACTS_DIR.glob("matrix_*.json"))
    print(f"📦 Found {len(contracts)} contracts to validate")

    # Validate each contract
    valid_count = 0
    invalid_contracts = []

    print("\n⚡ Validating contracts...")
    for contract_path in contracts:
        contract_name = contract_path.stem
        is_valid, errors = validate_contract(contract_path, schema)

        if is_valid:
            valid_count += 1
            print(f"  ✅ {contract_name}")
        else:
            invalid_contracts.append((contract_name, errors))
            print(f"  ❌ {contract_name}: {len(errors)} errors")
            for error in errors[:3]:  # Show first 3 errors
                print(f"     - {error}")

    # Summary
    print("\n" + "=" * 60)
    print("📊 Validation Summary")
    print(f"  ✅ Valid: {valid_count}/{len(contracts)}")
    print(f"  ❌ Invalid: {len(invalid_contracts)}/{len(contracts)}")

    if valid_count == len(contracts):
        print("\n🎉 All contracts are schema-compliant!")
    else:
        print(f"\n⚠️ {len(invalid_contracts)} contracts have validation errors")

        # Create validation report
        report_path = ROOT / "tests" / "matrix_schema_validation_report.md"
        report = ["# Matrix Schema Validation Report\n\n"]
        report.append("## Summary\n")
        report.append(f"- **Total Contracts**: {len(contracts)}\n")
        report.append(f"- **Valid**: {valid_count}\n")
        report.append(f"- **Invalid**: {len(invalid_contracts)}\n\n")

        if invalid_contracts:
            report.append("## Validation Errors\n\n")
            for contract_name, errors in invalid_contracts:
                report.append(f"### {contract_name}\n")
                for error in errors:
                    report.append(f"- {error}\n")
                report.append("\n")

        report_path.write_text("".join(report))
        print(f"\n📄 Detailed report written to: {report_path.relative_to(ROOT)}")

    # Show schema compliance features
    print("\n✅ Schema Compliance Features:")
    print("  • Required fields: schema_version, module, owner, gates")
    print("  • Identity block with ΛiD tier mappings (0-5)")
    print("  • Tokenization placeholder (Solana, disabled)")
    print("  • Telemetry with OpenTelemetry semantic conventions")
    print("  • WebAuthn requirements for critical modules")
    print("  • Service account patterns (lukhas:user:*, lukhas:svc:*)")

    return 0 if valid_count == len(contracts) else 1

if __name__ == "__main__":
    sys.exit(main())
