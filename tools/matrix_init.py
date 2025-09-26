#!/usr/bin/env python3
"""
Matrix Contract Initializer for Matrix Contracts v2

Creates a new matrix contract file for a module using the existing memory contract
as a template. Customizes module-specific fields while preserving the v2 structure.

Usage:
    python3 tools/matrix_init.py --module your.module.name
    python3 tools/matrix_init.py --module identity --output identity/
"""

import json
import argparse
import pathlib
from typing import Dict, Any


def load_template_contract() -> Dict[str, Any]:
    """Load the memory contract as a template."""
    template_path = pathlib.Path("memory/matrix_memoria.json")
    if not template_path.exists():
        raise FileNotFoundError(f"Template contract not found: {template_path}")

    with open(template_path) as f:
        return json.load(f)


def customize_contract_for_module(template: Dict[str, Any], module: str) -> Dict[str, Any]:
    """Customize the template contract for a specific module."""
    contract = template.copy()

    # Update basic module info
    contract["module"] = module
    contract["owner"]["codeowners"] = [f"@{module}-team"]

    # Module-specific customizations
    module_configs = {
        "identity": {
            "public_api": [
                {"fn": "authenticate(credentials: dict) -> dict", "stability": "stable", "doc": "Authenticate user credentials"},
                {"fn": "authorize(user_id: str, resource: str) -> bool", "stability": "stable", "doc": "Authorize user access to resource"},
                {"fn": "create_session(user_id: str) -> str", "stability": "stable", "doc": "Create new user session"}
            ],
            "contracts": [
                {"name": "auth_token_validity", "type": "invariant", "desc": "Auth tokens remain valid for session duration"},
                {"name": "webauthn_compliance", "type": "postcondition", "desc": "WebAuthn flows comply with FIDO2 specification"}
            ],
            "gates": [
                {"metric": "latency.auth_s", "op": "<=", "value": 2},
                {"metric": "symbolic.DriftScore", "op": ">=", "value": 0.010},
                {"metric": "security.osv_high", "op": "==", "value": 0},
                {"metric": "attestation.rats_verified", "op": "==", "value": 1},
                {"metric": "identity.auth_success_rate", "op": ">=", "value": 0.999}
            ],
            "spans": [
                {"name": "identity.authenticate", "attrs": ["code.function", "lukhas.module", "auth.method"]},
                {"name": "identity.authorize", "attrs": ["code.function", "lukhas.module", "resource.type"]}
            ],
            "metrics": [
                {"name": "lukhas.identity.auth.latency", "unit": "s", "type": "histogram"},
                {"name": "lukhas.identity.sessions.active", "unit": "1", "type": "gauge"}
            ]
        },
        "consciousness": {
            "public_api": [
                {"fn": "process(input: str) -> dict", "stability": "experimental", "doc": "Process input through consciousness layers"},
                {"fn": "dream(symbols: list) -> dict", "stability": "experimental", "doc": "Generate dream sequences from symbols"},
                {"fn": "emerge(patterns: dict) -> bool", "stability": "experimental", "doc": "Facilitate consciousness emergence"}
            ],
            "contracts": [
                {"name": "awareness_continuity", "type": "invariant", "desc": "Awareness levels maintain continuity over time"},
                {"name": "emergence_coherence", "type": "postcondition", "desc": "Emergent patterns exhibit coherence properties"}
            ],
            "gates": [
                {"metric": "latency.process_s", "op": "<=", "value": 5},
                {"metric": "symbolic.DriftScore", "op": ">=", "value": 0.015},
                {"metric": "security.osv_high", "op": "==", "value": 0},
                {"metric": "attestation.rats_verified", "op": "==", "value": 1},
                {"metric": "consciousness.awareness_stability", "op": ">=", "value": 0.80}
            ],
            "spans": [
                {"name": "consciousness.process", "attrs": ["code.function", "lukhas.module", "awareness.level"]},
                {"name": "consciousness.dream", "attrs": ["code.function", "lukhas.module", "dream.state"]}
            ],
            "metrics": [
                {"name": "lukhas.consciousness.awareness.level", "unit": "1", "type": "gauge"},
                {"name": "lukhas.consciousness.dreams.generated", "unit": "1", "type": "counter"}
            ]
        }
    }

    # Apply module-specific config if available
    if module in module_configs:
        config = module_configs[module]
        contract["interface"]["public_api"] = config["public_api"]
        contract["interface"]["contracts"] = config["contracts"]
        contract["gates"] = config["gates"]
        contract["telemetry"]["spans"] = config["spans"]
        contract["telemetry"]["metrics"] = config["metrics"]
    else:
        # Generic module configuration
        contract["interface"]["public_api"] = [
            {"fn": f"process(input: Any) -> Any", "stability": "experimental", "doc": f"Process input through {module}"}
        ]
        contract["interface"]["contracts"] = [
            {"name": f"{module}_consistency", "type": "invariant", "desc": f"{module} maintains internal consistency"}
        ]
        contract["gates"] = [
            {"metric": "latency.runtime_s_10k", "op": "<=", "value": 30},
            {"metric": "symbolic.DriftScore", "op": ">=", "value": 0.010},
            {"metric": "security.osv_high", "op": "==", "value": 0},
            {"metric": "attestation.rats_verified", "op": "==", "value": 1}
        ]
        contract["telemetry"]["spans"] = [
            {"name": f"{module}.process", "attrs": ["code.function", "lukhas.module"]}
        ]
        contract["telemetry"]["metrics"] = [
            {"name": f"lukhas.{module}.operations", "unit": "1", "type": "counter"}
        ]

    # Update SBOM reference
    contract["supply_chain"]["sbom_ref"] = f"../sbom/{module}.cdx.json"

    # Update lineage job name
    contract["lineage"]["job"] = f"lukhas.{module}.build-index"

    # Update docs references
    contract["docs"]["design_notes"] = f"../docs/{module}/architecture.md"
    contract["docs"]["lens_markdown"] = f"../products/{module}/lens/baseline.qmd"

    return contract


def write_contract_file(contract: Dict[str, Any], output_path: pathlib.Path) -> None:
    """Write contract to JSON file with pretty formatting."""
    with open(output_path, 'w') as f:
        json.dump(contract, f, indent=2, sort_keys=False)


def create_directory_structure(module: str, output_dir: pathlib.Path) -> None:
    """Create basic directory structure for the module."""
    module_dir = output_dir / module
    module_dir.mkdir(parents=True, exist_ok=True)

    runs_dir = module_dir / "runs"
    runs_dir.mkdir(exist_ok=True)

    # Create placeholder run report
    run_report = {
        "run_id": f"run-{module}-001",
        "module": module,
        "timestamp": "2025-09-26T00:00:00Z",
        "environment": {
            "os": "Darwin 25.1.0",
            "cpu": "Apple M4",
            "python": "3.11.6"
        },
        "metrics": {
            "latency.runtime_s_10k": 25.0,
            "symbolic.DriftScore": 0.012,
            "security.osv_high": 0
        },
        "attestation": {
            "rats_verified": 1
        }
    }

    run_file = runs_dir / f"{module}_2025-09-26T00-00-00Z.json"
    with open(run_file, 'w') as f:
        json.dump(run_report, f, indent=2)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Initialize Matrix contract for a new module")
    parser.add_argument(
        "--module",
        required=True,
        help="Module name (e.g., identity, consciousness, api)"
    )
    parser.add_argument(
        "--output",
        default=".",
        help="Output directory (default: current directory)"
    )
    parser.add_argument(
        "--no-dirs",
        action="store_true",
        help="Don't create directory structure, just generate contract file"
    )

    args = parser.parse_args()

    output_dir = pathlib.Path(args.output)

    print(f"🚀 Initializing matrix contract for module: {args.module}")
    print(f"📁 Output directory: {output_dir}")

    try:
        # Load template and customize for module
        template = load_template_contract()
        contract = customize_contract_for_module(template, args.module)

        # Create directory structure if requested
        if not args.no_dirs:
            create_directory_structure(args.module, output_dir)
            print(f"✅ Created directory structure for {args.module}")

        # Write contract file
        contract_path = output_dir / args.module / f"matrix_{args.module}.json"
        if args.no_dirs:
            contract_path = output_dir / f"matrix_{args.module}.json"

        contract_path.parent.mkdir(parents=True, exist_ok=True)
        write_contract_file(contract, contract_path)
        print(f"✅ Generated contract file: {contract_path}")

        print(f"🎉 Matrix contract initialized for {args.module}")
        print("\nNext steps:")
        print(f"1. Review and customize: {contract_path}")
        print(f"2. Generate telemetry fixtures: make telemetry-fixtures MODULE={args.module}")
        print(f"3. Create SBOM: touch sbom/{args.module}.cdx.json")
        print(f"4. Validate contract: make validate-matrix MODULE={args.module}")

    except Exception as e:
        print(f"❌ Error initializing contract: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())