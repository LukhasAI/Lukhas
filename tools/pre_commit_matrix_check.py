#!/usr/bin/env python3
"""
Pre-commit hook: Matrix Contract Validation

Validates matrix contracts against JSON Schema 2020-12 before commit.
Provides fast feedback on contract compliance without running full CI.
"""

import json
import pathlib
import sys
from typing import List

try:
    from jsonschema import (  # noqa: F401  # TODO: jsonschema.ValidationError; co...
        Draft202012Validator,
        ValidationError,
    )
except ImportError:
    print("❌ jsonschema not installed. Run: pip install jsonschema", file=sys.stderr)
    sys.exit(1)


def validate_matrix_contract(contract_path: str) -> List[str]:
    """Validate a single matrix contract against schema."""
    errors = []

    try:
        # Load contract
        with open(contract_path) as f:
            contract_data = json.load(f)

        # Find schema
        schema_path = pathlib.Path("schemas/matrix.schema.json")
        if not schema_path.exists():
            # Fallback to template if schema doesn't exist
            schema_path = pathlib.Path("matrix.schema.template.json")

        if not schema_path.exists():
            errors.append("Matrix schema not found")
            return errors

        # Load schema
        with open(schema_path) as f:
            schema = json.load(f)

        # Validate
        validator = Draft202012Validator(schema)
        validation_errors = list(validator.iter_errors(contract_data))

        for error in validation_errors:
            path = " -> ".join(str(p) for p in error.path) if error.path else "root"
            errors.append(f"Schema validation error at {path}: {error.message}")

    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON: {e}")
    except FileNotFoundError as e:
        errors.append(f"File not found: {e}")
    except Exception as e:
        errors.append(f"Validation error: {e}")

    return errors


def main():
    """Main pre-commit hook entry point."""
    if len(sys.argv) < 2:
        print("Usage: pre_commit_matrix_check.py <contract_file> [<contract_file>...]", file=sys.stderr)
        sys.exit(1)

    contract_files = sys.argv[1:]
    total_errors = 0

    print(f"🔍 Validating {len(contract_files)} matrix contract(s)...")

    for contract_path in contract_files:
        errors = validate_matrix_contract(contract_path)

        if errors:
            print(f"❌ {contract_path}:")
            for error in errors:
                print(f"   {error}")
            total_errors += len(errors)
        else:
            print(f"✅ {contract_path}")

    if total_errors > 0:
        print(f"\n❌ Found {total_errors} validation error(s) in matrix contracts")
        print("Fix these errors before committing to ensure contract compliance")
        sys.exit(1)
    else:
        print("\n✅ All matrix contracts valid")


if __name__ == "__main__":
    main()
