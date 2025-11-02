#!/usr/bin/env python3
"""
Matrix Test Generator for LUKHAS
Generates comprehensive test matrices for all 65 modules based on their identity configurations.
"""

import glob
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class MatrixTestGenerator:
    """Generates test matrices for all Matrix contracts based on their identity configurations."""

    # Tier mapping with numeric values
    TIER_MAPPING = {"guest": 0, "visitor": 1, "friend": 2, "trusted": 3, "inner_circle": 4, "root_dev": 5}

    # All possible tiers in order
    ALL_TIERS = ["guest", "visitor", "friend", "trusted", "inner_circle", "root_dev"]

    def __init__(self, lukhas_root: Path = None):
        """Initialize the generator with paths to lukhas contracts."""
        self.lukhas_root = lukhas_root or Path(__file__).parent.parent / "lukhas"
        self.output_dir = Path(__file__).parent.parent / "tests" / "matrix_identity"

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Initialized MatrixTestGenerator:")
        logger.info(f"  Lukhas root: {self.lukhas_root}")
        logger.info(f"  Output dir: {self.output_dir}")

    def find_matrix_contracts(self) -> List[Path]:
        """Find all matrix contract files."""
        pattern = str(self.lukhas_root / "**" / "matrix_*.json")
        contracts = [Path(p) for p in glob.glob(pattern, recursive=True)]
        logger.info(f"Found {len(contracts)} matrix contracts")
        return contracts

    def extract_identity_config(self, contract_path: Path) -> Optional[Dict[str, Any]]:
        """Extract identity configuration from a matrix contract."""
        try:
            with open(contract_path, "r") as f:
                contract = json.load(f)

            # Extract module name from contract or filename
            module_name = contract.get("module")
            if not module_name:
                # Fallback to extracting from filename
                module_name = contract_path.stem.replace("matrix_", "")

            identity = contract.get("identity", {})
            if not identity:
                logger.warning(f"No identity block found in {contract_path}")
                return None

            # Extract the public API functions for testing
            interface = contract.get("interface", {})
            public_api = interface.get("public_api", [])

            return {
                "module": module_name,
                "contract_path": str(contract_path),
                "identity": identity,
                "public_api": public_api,
            }

        except Exception as e:
            logger.error(f"Error parsing {contract_path}: {e}")
            return None

    def determine_module_scopes(self, module_name: str, identity_config: Dict[str, Any]) -> List[str]:
        """Determine the scopes for a module based on its identity configuration."""
        configured_scopes = identity_config.get("scopes", [])
        if configured_scopes:
            return configured_scopes

        # Fallback to default scopes based on module name
        # Handle nested module names (e.g., core.policy -> core and policy)
        base_module = module_name.split(".")[-1]
        return [f"{base_module}.read", f"{base_module}.write"]

    def extract_public_functions(self, public_api: List[Dict[str, Any]]) -> List[str]:
        """Extract function signatures from public API."""
        functions = []
        for api_item in public_api:
            fn_name = api_item.get("fn", "")
            if fn_name and not fn_name.isupper():  # Skip constants like MEMORY_AVAILABLE
                # Generate a realistic function signature based on the function name
                if "recall" in fn_name.lower() or "query" in fn_name.lower():
                    functions.append(f"{fn_name}(query: str, k: int) -> list[str]")
                elif "store" in fn_name.lower() or "save" in fn_name.lower():
                    functions.append(f"{fn_name}(content: str, metadata: dict) -> str")
                elif "fold" in fn_name.lower():
                    functions.append(f"{fn_name}(memories: list[str]) -> str")
                elif "process" in fn_name.lower():
                    functions.append(f"{fn_name}(data: dict) -> dict")
                elif "get" in fn_name.lower() or "read" in fn_name.lower():
                    functions.append(f"{fn_name}(id: str) -> dict")
                elif "create" in fn_name.lower() or "add" in fn_name.lower():
                    functions.append(f"{fn_name}(params: dict) -> str")
                elif "update" in fn_name.lower() or "modify" in fn_name.lower():
                    functions.append(f"{fn_name}(id: str, data: dict) -> bool")
                elif "delete" in fn_name.lower() or "remove" in fn_name.lower():
                    functions.append(f"{fn_name}(id: str) -> bool")
                else:
                    functions.append(f"{fn_name}() -> bool")

        # If no functions found, add default module operations
        if not functions:
            functions = ["read(id: str) -> dict", "write(data: dict) -> str", "process() -> bool"]

        return functions

    def generate_test_cases(self, module_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate test cases for a module based on its identity configuration."""
        module_name = module_config["module"]
        identity = module_config["identity"]
        public_api = module_config["public_api"]

        # Extract configuration
        required_tiers = identity.get("required_tiers", [])
        required_tiers_numeric = identity.get("required_tiers_numeric", [])
        accepted_subjects = identity.get("accepted_subjects", ["lukhas:user:*"])
        webauthn_required = identity.get("webauthn_required", False)
        scopes = self.determine_module_scopes(module_name, identity)
        functions = self.extract_public_functions(public_api)

        test_cases = []

        # Generate test cases for each tier
        for tier in self.ALL_TIERS:
            tier_num = self.TIER_MAPPING[tier]
            is_allowed = tier in required_tiers or tier_num in required_tiers_numeric

            # Generate test cases for each function
            for function in functions:
                # Basic test case
                test_case = {
                    "name": f"{tier}_{function.split('(')[0]}_basic",
                    "input": {
                        "subject": f"lukhas:user:test_{tier}",
                        "tier": tier,
                        "tier_num": tier_num,
                        "scopes": scopes,
                        "action": function,
                        "env": {"mfa": False, "webauthn_verified": webauthn_required},
                    },
                    "expected": is_allowed,
                    "reason": f"Tier {tier} {'allowed' if is_allowed else 'denied'} for {function}",
                }

                # For certain functions that require MFA, add MFA variant
                if "fold" in function and is_allowed:
                    test_case["input"]["env"]["mfa"] = True
                    test_case["reason"] += " with MFA"
                    # Also add special fold scope if available
                    if f"{module_name}.fold" not in scopes:
                        test_case["input"]["scopes"] = scopes + [f"{module_name}.fold"]

                test_cases.append(test_case)

        # Add edge case tests for higher tiers
        if "trusted" in required_tiers or 3 in required_tiers_numeric:
            # Missing scopes test
            test_cases.append(
                {
                    "name": "trusted_missing_scopes",
                    "input": {
                        "subject": "lukhas:user:test_trusted",
                        "tier": "trusted",
                        "tier_num": 3,
                        "scopes": [],
                        "action": "read",
                        "env": {"mfa": False, "webauthn_verified": webauthn_required},
                    },
                    "expected": False,
                    "reason": "Missing required scopes",
                }
            )

            # Partial scopes test
            test_cases.append(
                {
                    "name": "trusted_partial_scopes",
                    "input": {
                        "subject": "lukhas:user:test_trusted",
                        "tier": "trusted",
                        "tier_num": 3,
                        "scopes": scopes[:1],  # Only first scope
                        "action": "read",
                        "env": {"mfa": False, "webauthn_verified": webauthn_required},
                    },
                    "expected": False,
                    "reason": "Partial scopes provided",
                }
            )

            # Expired token test
            test_cases.append(
                {
                    "name": "trusted_expired_token",
                    "input": {
                        "subject": "lukhas:user:test_trusted",
                        "tier": "trusted",
                        "tier_num": 3,
                        "scopes": scopes,
                        "action": "read",
                        "token": {"exp": 1658892261, "aud": "lukhas-matrix"},  # Past expiry (2022)
                        "env": {"mfa": False, "webauthn_verified": webauthn_required},
                    },
                    "expected": False,
                    "reason": "Token expired",
                }
            )

            # Wrong audience test
            test_cases.append(
                {
                    "name": "trusted_wrong_audience",
                    "input": {
                        "subject": "lukhas:user:test_trusted",
                        "tier": "trusted",
                        "tier_num": 3,
                        "scopes": scopes,
                        "action": "read",
                        "token": {"exp": 1758894061, "aud": "wrong-audience"},  # Future expiry
                        "env": {"mfa": False, "webauthn_verified": webauthn_required},
                    },
                    "expected": False,
                    "reason": "Wrong audience in token",
                }
            )

        # Add service account tests
        for subject in accepted_subjects:
            if "lukhas:svc:" in subject:
                service_name = subject.split(":")[-1]
                if service_name != "*":  # Specific service
                    test_cases.append(
                        {
                            "name": f"service_{service_name}_allowed",
                            "input": {
                                "subject": subject,
                                "tier": "root_dev",
                                "tier_num": 5,
                                "scopes": scopes,
                                "action": "process",
                                "env": {"mfa": False, "webauthn_verified": webauthn_required},
                            },
                            "expected": True,
                            "reason": "Service account in accepted subjects",
                        }
                    )

        # Add unknown service denial test
        if any("lukhas:svc:" in s for s in accepted_subjects):
            test_cases.append(
                {
                    "name": "service_unknown_denied",
                    "input": {
                        "subject": "lukhas:svc:unknown",
                        "tier": "root_dev",
                        "tier_num": 5,
                        "scopes": scopes,
                        "action": "process",
                        "env": {"mfa": False, "webauthn_verified": webauthn_required},
                    },
                    "expected": False,
                    "reason": "Unknown service account",
                }
            )

        return test_cases

    def generate_matrix_yaml(self, module_config: Dict[str, Any]) -> str:
        """Generate YAML test matrix for a module."""
        module_name = module_config["module"]
        test_cases = self.generate_test_cases(module_config)

        matrix_data = {
            "module": module_name,
            "generated": "auto-generated by matrix_test_generator.py",
            "test_cases": test_cases,
        }

        return yaml.dump(matrix_data, default_flow_style=False, sort_keys=False)

    def generate_all_matrices(self) -> Tuple[int, int]:
        """Generate test matrices for all modules."""
        contracts = self.find_matrix_contracts()
        generated_count = 0
        skipped_count = 0

        for contract_path in contracts:
            module_config = self.extract_identity_config(contract_path)
            if not module_config:
                skipped_count += 1
                continue

            module_name = module_config["module"]
            try:
                # Generate YAML content
                yaml_content = self.generate_matrix_yaml(module_config)

                # Write to file
                output_file = self.output_dir / f"{module_name}_authz.yaml"
                with open(output_file, "w") as f:
                    f.write(yaml_content)

                logger.info(f"Generated test matrix for {module_name}: {output_file}")
                generated_count += 1

            except Exception as e:
                logger.error(f"Error generating matrix for {module_name}: {e}")
                skipped_count += 1

        return generated_count, skipped_count

    def validate_against_memoria(self) -> bool:
        """Validate generated matrices against the existing memoria pattern."""
        memoria_path = Path(__file__).parent.parent / "tests" / "authz" / "memoria_authz.yaml"
        if not memoria_path.exists():
            logger.warning("memoria_authz.yaml not found for validation")
            return False

        # Load memoria test matrix
        with open(memoria_path, "r") as f:
            memoria_data = yaml.safe_load(f)

        # Validate that our generated memoria matrix matches the expected structure
        generated_memoria_path = self.output_dir / "memoria_authz.yaml"
        if not generated_memoria_path.exists():
            logger.error("Generated memoria matrix not found")
            return False

        with open(generated_memoria_path, "r") as f:
            generated_data = yaml.safe_load(f)

        # Compare key structure elements
        if generated_data["module"] != memoria_data["module"]:
            logger.error("Module name mismatch in memoria validation")
            return False

        # Check that we have similar test case structure
        original_test_count = len(memoria_data["test_cases"])
        generated_test_count = len(generated_data["test_cases"])

        logger.info(f"Memoria validation: original={original_test_count}, generated={generated_test_count}")

        if generated_test_count < original_test_count * 0.8:  # Allow some variation
            logger.warning("Generated test count significantly lower than original")
            return False

        logger.info("Memoria validation passed")
        return True


def main():
    """Main function to generate all test matrices."""
    generator = MatrixTestGenerator()

    logger.info("Starting Matrix Test Generation for all 65 modules...")

    generated_count, skipped_count = generator.generate_all_matrices()

    logger.info("Generation complete:")
    logger.info(f"  Generated: {generated_count} matrices")
    logger.info(f"  Skipped: {skipped_count} matrices")

    # Validate against memoria pattern
    logger.info("Validating against memoria pattern...")
    validation_passed = generator.validate_against_memoria()

    if validation_passed:
        logger.info("All validations passed!")
    else:
        logger.warning("Some validations failed - review generated matrices")

    return 0 if validation_passed else 1


if __name__ == "__main__":
    sys.exit(main())
