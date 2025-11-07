#!/usr/bin/env python3
"""
Authorization Test Runner

Runs authorization test matrices against OPA policies or fallback simulation.
Validates that authorization policy intent matches expected behavior across
different tier/scope/action combinations.
"""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Tuple

import yaml


class AuthzTestRunner:
    """Runs authorization test matrices."""

    def __init__(self, verbose: bool = False):
        """Initialize test runner."""
        self.verbose = verbose
        self.passed = 0
        self.failed = 0
        self.errors = []

    def log(self, message: str):
        """Log message if verbose mode enabled."""
        if self.verbose:
            print(f"🔍 {message}")

    def load_test_matrix(self, matrix_path: Path) -> dict[str, Any]:
        """Load authorization test matrix from YAML or JSON file."""
        try:
            with open(matrix_path) as f:
                if matrix_path.suffix.lower() == '.yaml' or matrix_path.suffix.lower() == '.yml':
                    return yaml.safe_load(f)
                else:
                    return json.load(f)
        except Exception as e:
            raise ValueError(f"Could not load test matrix {matrix_path}: {e}")

    def load_contract(self, module: str) -> dict[str, Any]:
        """Load Matrix contract for module."""
        # Try multiple contract locations
        contract_paths = [
            Path(f"{module}/matrix_{module}.json"),
            Path(f"matrix_{module}.json"),
            Path("memory/matrix_memoria.json") if module == "memoria" else None
        ]

        for path in contract_paths:
            if path and path.exists():
                with open(path) as f:
                    return json.load(f)

        raise FileNotFoundError(f"No contract found for module: {module}")

    async def run_opa_test(self, test_input: dict[str, Any]) -> tuple[bool, str]:
        """Run single test case against OPA policy."""
        try:
            # Create temporary input file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump({"input": test_input}, f)
                input_file = f.name

            try:
                # Call OPA eval
                result = subprocess.run([
                    "opa", "eval",
                    "-d", "policies/matrix",
                    "-i", input_file,
                    "data.matrix.authz.allow"
                ], capture_output=True, text=True, timeout=5.0)

                if result.returncode == 0:
                    opa_output = json.loads(result.stdout)
                    allow_result = opa_output.get("result", [{}])[0].get("expressions", [{}])[0].get("value", False)
                    return allow_result, "OPA evaluation"
                else:
                    return False, f"OPA error: {result.stderr}"

            except subprocess.TimeoutExpired:
                return False, "OPA timeout"
            except json.JSONDecodeError as e:
                return False, f"OPA output parse error: {e}"
            except FileNotFoundError:
                # Fallback to simulation
                return self._simulate_policy_decision(test_input)

            finally:
                # Clean up temp file
                try:
                    Path(input_file).unlink()
                except Exception as e:
                    logger.debug(f"Expected optional failure: {e}")
                    pass

        except Exception as e:
            return False, f"Test error: {e}"

    def _simulate_policy_decision(self, opa_input: dict[str, Any]) -> tuple[bool, str]:
        """Simulate policy decision when OPA unavailable."""
        try:
            from matrix_authz_middleware import MatrixAuthzMiddleware
            middleware = MatrixAuthzMiddleware()
            result = middleware._fallback_policy_simulation(opa_input)
            return result.get("allow", False), result.get("reason", "Simulation")
        except Exception as e:
            return False, f"Simulation error: {e}"

    def build_opa_input(
        self,
        test_case: dict[str, Any],
        contract: dict[str, Any]
    ) -> dict[str, Any]:
        """Build OPA input from test case and contract."""
        test_input = test_case["input"]

        # Build standard OPA input structure
        opa_input = {
            "subject": test_input["subject"],
            "tier": test_input["tier"],
            "tier_num": test_input["tier_num"],
            "scopes": test_input["scopes"],
            "module": contract["module"],
            "action": test_input["action"],
            "contract": contract,
            "token": {
                "exp": test_input.get("token", {}).get("exp", 1758894061),  # Future expiry by default
                "iat": test_input.get("token", {}).get("iat", 1758892261),  # Recent issue by default
                "aud": test_input.get("token", {}).get("aud", "lukhas-matrix")   # Default audience
            },
            "env": {
                "mfa": test_input.get("env", {}).get("mfa", False),
                "webauthn_verified": test_input.get("env", {}).get("webauthn_verified", True),
                "device_id": None,
                "region": "us-west-2",
                "ip": "192.168.1.100",
                "time": 1758892261
            }
        }

        return opa_input

    async def run_test_case(
        self,
        test_case: dict[str, Any],
        contract: dict[str, Any]
    ) -> tuple[bool, str]:
        """Run single test case."""
        test_name = test_case["name"]
        expected = test_case["expected"]
        reason = test_case.get("reason", "")

        self.log(f"Running test: {test_name}")

        # Build OPA input
        opa_input = self.build_opa_input(test_case, contract)

        # Run authorization test
        actual, decision_reason = await self.run_opa_test(opa_input)

        # Check result
        if actual == expected:
            self.passed += 1
            if self.verbose:
                print(f"  ✅ {test_name}")
                if reason:
                    print(f"     Expected: {reason}")
                print(f"     Decision: {decision_reason}")
            return True, decision_reason
        else:
            self.failed += 1
            error_msg = f"{test_name}: expected {expected}, got {actual} ({decision_reason})"
            self.errors.append(error_msg)
            print(f"  ❌ {test_name}")
            print(f"     Expected: {expected} ({reason})")
            print(f"     Actual: {actual} ({decision_reason})")
            return False, decision_reason

    async def run_matrix(self, matrix_path: Path) -> tuple[int, int]:
        """Run complete authorization test matrix."""
        print(f"🧪 Running authorization test matrix: {matrix_path}")

        # Load test matrix
        matrix = self.load_test_matrix(matrix_path)
        module = matrix["module"]
        test_cases = matrix["test_cases"]

        print(f"   Module: {module}")
        print(f"   Test cases: {len(test_cases)}")

        # Load contract
        contract = self.load_contract(module)
        print(f"   Contract: {module}/matrix_{module}.json")
        print()

        # Run all test cases
        for test_case in test_cases:
            await self.run_test_case(test_case, contract)

        return self.passed, self.failed

    def print_summary(self):
        """Print test run summary."""
        total = self.passed + self.failed

        print()
        print("=" * 60)
        print("AUTHORIZATION TEST SUMMARY")
        print("=" * 60)
        print(f"Total tests: {total}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")

        if self.failed > 0:
            print()
            print("FAILURES:")
            for error in self.errors:
                print(f"  - {error}")

        print()
        if self.failed == 0:
            print("✅ ALL AUTHORIZATION TESTS PASSED")
        else:
            print("❌ SOME AUTHORIZATION TESTS FAILED")

    async def run_all_matrices(self, test_dir: Path) -> bool:
        """Run all authorization test matrices in directory."""
        matrix_files = list(test_dir.glob("*_authz.yaml")) + list(test_dir.glob("*_authz.json"))

        if not matrix_files:
            print(f"No authorization test matrices found in {test_dir}")
            return True

        print(f"🔧 Found {len(matrix_files)} authorization test matrix/matrices")
        print()

        all_passed = True
        for matrix_file in sorted(matrix_files):
            try:
                _passed, failed = await self.run_matrix(matrix_file)
                if failed > 0:
                    all_passed = False
                print()
            except Exception as e:
                print(f"❌ Error running matrix {matrix_file}: {e}")
                all_passed = False

        return all_passed


async def main():
    """CLI for running authorization tests."""
    parser = argparse.ArgumentParser(description="Authorization Test Runner")
    parser.add_argument("--matrix", help="Specific test matrix file to run")
    parser.add_argument("--test-dir", default="tests/authz", help="Directory containing test matrices")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    runner = AuthzTestRunner(verbose=args.verbose)

    try:
        if args.matrix:
            # Run specific matrix
            matrix_path = Path(args.matrix)
            if not matrix_path.exists():
                print(f"Error: Test matrix not found: {matrix_path}")
                sys.exit(1)

            await runner.run_matrix(matrix_path)
            runner.print_summary()

            if runner.failed > 0:
                sys.exit(1)

        else:
            # Run all matrices in directory
            test_dir = Path(args.test_dir)
            if not test_dir.exists():
                print(f"Error: Test directory not found: {test_dir}")
                sys.exit(1)

            success = await runner.run_all_matrices(test_dir)
            runner.print_summary()

            if not success:
                sys.exit(1)

    except KeyboardInterrupt:
        print("\n❌ Test run interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test runner error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
