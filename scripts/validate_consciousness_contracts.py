#!/usr/bin/env python3
"""
Module: validate_consciousness_contracts.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

"""
LUKHAS Consciousness Contract Validator
Validates consciousness component contracts against schema
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import jsonschema


class ConsciousnessContractValidator:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.schema_path = self.root_path / "schemas" / "consciousness_component.schema.json"
        self.contracts_dir = self.root_path / "contracts" / "consciousness"

    def load_schema(self) -> Dict:
        """Load the consciousness component schema"""
        try:
            with open(self.schema_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            return {"error": f"Failed to load schema: {e}"}

    def validate_contract(self, contract_path: Path, schema: Dict) -> Tuple[bool, List[str]]:
        """Validate a single contract against the schema"""
        try:
            with open(contract_path, 'r') as f:
                contract = json.load(f)

            jsonschema.validate(contract, schema)
            return True, []

        except jsonschema.ValidationError as e:
            return False, [f"Validation error: {e.message}"]
        except jsonschema.SchemaError as e:
            return False, [f"Schema error: {e.message}"]
        except json.JSONDecodeError as e:
            return False, [f"JSON decode error: {e}"]
        except Exception as e:
            return False, [f"Unexpected error: {e}"]

    def validate_all_contracts(self) -> Dict:
        """Validate all consciousness contracts"""
        results = {
            "validation_timestamp": datetime.now().isoformat(),
            "schema_valid": False,
            "total_contracts": 0,
            "valid_contracts": 0,
            "invalid_contracts": 0,
            "validation_errors": {},
            "summary": {},
            "recommendations": []
        }

        # Load schema
        schema = self.load_schema()
        if "error" in schema:
            results["schema_error"] = schema["error"]
            return results

        results["schema_valid"] = True

        if not self.contracts_dir.exists():
            results["error"] = "Contracts directory not found"
            return results

        # Find all contract files
        contract_files = list(self.contracts_dir.glob("*.json"))
        results["total_contracts"] = len(contract_files)

        # Track statistics
        component_types = {}
        lanes = {}
        constellation_integration = {"identity": 0, "guardian": 0}
        governance_stats = {"ethics_required": 0, "consent_required": 0}

        # Validate each contract
        for contract_file in contract_files:
            is_valid, errors = self.validate_contract(contract_file, schema)

            if is_valid:
                results["valid_contracts"] += 1

                # Collect statistics
                try:
                    with open(contract_file, 'r') as f:
                        contract = json.load(f)

                    comp_type = contract.get("component_type", "UNKNOWN")
                    component_types[comp_type] = component_types.get(comp_type, 0) + 1

                    lane = contract.get("lane", "unknown")
                    lanes[lane] = lanes.get(lane, 0) + 1

                    if contract.get("constellation_integration", {}).get("identity_coupling"):
                        constellation_integration["identity"] += 1
                    if contract.get("constellation_integration", {}).get("guardian_validation"):
                        constellation_integration["guardian"] += 1

                    if contract.get("governance", {}).get("ethics_validation") == "required":
                        governance_stats["ethics_required"] += 1
                    if contract.get("governance", {}).get("consent_required"):
                        governance_stats["consent_required"] += 1

                except Exception as e:
                    results["validation_errors"][contract_file.name] = [f"Post-validation error: {e}"]
                    results["valid_contracts"] -= 1
                    results["invalid_contracts"] += 1

            else:
                results["invalid_contracts"] += 1
                results["validation_errors"][contract_file.name] = errors

        # Generate summary
        results["summary"] = {
            "validation_rate": results["valid_contracts"] / results["total_contracts"] if results["total_contracts"] > 0 else 0,
            "component_types": component_types,
            "lanes": lanes,
            "constellation_integration": constellation_integration,
            "governance_stats": governance_stats
        }

        # Generate recommendations
        if results["invalid_contracts"] > 0:
            results["recommendations"].append(f"Fix {results['invalid_contracts']} invalid contracts")

        if lanes.get("development", 0) == results["valid_contracts"]:
            results["recommendations"].append("Consider promoting stable components to integration lane")

        if constellation_integration["identity"] == 0:
            results["recommendations"].append("Review identity coupling - no components are identity-coupled")

        return results


def main():
    validator = ConsciousnessContractValidator(".")
    results = validator.validate_all_contracts()

    print("Consciousness Contract Validation Results:")
    print(f"Schema valid: {'✅' if results.get('schema_valid') else '❌'}")
    print(f"Total contracts: {results['total_contracts']}")
    print(f"Valid contracts: {results['valid_contracts']}")
    print(f"Invalid contracts: {results['invalid_contracts']}")
    print(f"Validation rate: {results['summary']['validation_rate']:.1%}")

    if results["invalid_contracts"] > 0:
        print(f"\nValidation Errors ({results['invalid_contracts']}):")
        for filename, errors in list(results["validation_errors"].items())[:5]:
            print(f"  {filename}:")
            for error in errors:
                print(f"    - {error}")

    print("\nComponent Type Distribution:")
    for comp_type, count in results["summary"]["component_types"].items():
        print(f"  {comp_type}: {count}")

    print("\nTrinity Integration:")
    print(f"  Identity-coupled: {results['summary']['constellation_integration']['identity']}")
    print(f"  Guardian-validated: {results['summary']['constellation_integration']['guardian']}")

    print("\nGovernance Statistics:")
    print(f"  Ethics validation required: {results['summary']['governance_stats']['ethics_required']}")
    print(f"  Consent required: {results['summary']['governance_stats']['consent_required']}")

    if results["recommendations"]:
        print("\nRecommendations:")
        for rec in results["recommendations"]:
            print(f"  - {rec}")

    # Save full results
    with open("temp_consciousness_validation_report.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\nFull validation report saved to: temp_consciousness_validation_report.json")


if __name__ == "__main__":
    main()
