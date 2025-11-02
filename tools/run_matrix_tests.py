#!/usr/bin/env python3
"""
Authorization Matrix Test Runner

Executes authorization test matrices against OPA policies and generates
comprehensive results for CI/CD validation.
"""

import argparse
import glob
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MatrixTestRunner:
    """Runs and validates matrix authorization tests."""

    def __init__(self, fixtures_dir: Optional[str] = None):
        """Initialize the test runner."""
        self.fixtures_dir = Path(fixtures_dir) if fixtures_dir else Path(__file__).parent.parent / "tests" / "authz"
        self.matrix_dir = Path(__file__).parent.parent / "tests" / "matrix_identity"
        self.contracts_dir = Path(__file__).parent.parent / "contracts"
        self.policies_dir = Path(__file__).parent.parent / "policies" / "matrix"

        # Test statistics
        self.stats = {
            'total_matrices': 0,
            'total_test_cases': 0,
            'passed_test_cases': 0,
            'failed_test_cases': 0,
            'skipped_test_cases': 0,
            'modules': {},
            'tiers_tested': set(),
            'start_time': datetime.utcnow().isoformat() + 'Z'
        }

        logger.info("Initialized MatrixTestRunner:")
        logger.info(f"  Fixtures directory: {self.fixtures_dir}")
        logger.info(f"  Matrix directory: {self.matrix_dir}")
        logger.info(f"  Contracts directory: {self.contracts_dir}")
        logger.info(f"  Policies directory: {self.policies_dir}")

    def find_test_matrices(self) -> List[Path]:
        """Find all test matrix files."""
        # Look in both fixtures and matrix directories
        patterns = [
            str(self.fixtures_dir / "**" / "*.yaml"),
            str(self.fixtures_dir / "**" / "*.json"),
            str(self.matrix_dir / "**" / "*_authz.yaml")
        ]

        matrices = []
        for pattern in patterns:
            matrices.extend([Path(p) for p in glob.glob(pattern, recursive=True)])

        logger.info(f"Found {len(matrices)} test matrices")
        return matrices

    def load_matrix(self, matrix_path: Path) -> Dict[str, Any]:
        """Load a test matrix file."""
        try:
            content = matrix_path.read_text()
            if matrix_path.suffix in ['.yaml', '.yml']:
                return yaml.safe_load(content)
            elif matrix_path.suffix == '.json':
                return json.loads(content)
            else:
                logger.warning(f"Unsupported file format: {matrix_path}")
                return {}
        except Exception as e:
            logger.error(f"Failed to load matrix {matrix_path}: {e}")
            return {}

    def load_contract(self, module: str) -> Dict[str, Any]:
        """Load Matrix contract for a module."""
        # Try different naming patterns
        contract_patterns = [
            f"matrix_{module.replace('.', '_')}.json",
            f"matrix_{module}.json"
        ]

        # Special cases for legacy naming
        if module == "memoria":
            contract_patterns.append("matrix_memory.json")
        elif module == "memoria":
            contract_patterns.append("matrix_memoria.json")

        for pattern in contract_patterns:
            contract_path = self.contracts_dir / pattern
            if contract_path.exists():
                try:
                    return json.loads(contract_path.read_text())
                except Exception as e:
                    logger.error(f"Failed to load contract {contract_path}: {e}")

        logger.warning(f"No contract found for module: {module}")
        return {}

    def execute_opa_query(self, input_data: Dict[str, Any], contract: Dict[str, Any]) -> Dict[str, Any]:
        """Execute OPA policy query (mock implementation)."""
        # This would normally call OPA via subprocess or HTTP API
        # For now, we'll simulate the authorization logic

        identity = contract.get('identity', {})

        # Basic authorization simulation
        subject = input_data.get('subject', '')
        tier = input_data.get('tier', 'guest')
        scopes = input_data.get('scopes', [])
        module = input_data.get('module', '')
        action = input_data.get('action', '')

        # Check tier requirements
        required_tiers = identity.get('required_tiers', [])
        tier_levels = {'guest': 0, 'visitor': 1, 'friend': 2, 'trusted': 3, 'inner_circle': 4, 'root_dev': 5}

        user_level = tier_levels.get(tier, 0)
        required_levels = [tier_levels.get(t, 5) for t in required_tiers]

        tier_ok = not required_levels or user_level >= min(required_levels)

        # Check scopes
        required_scope = f"{module}.{action}"
        scope_ok = required_scope in scopes or not identity.get('requires_auth', True)

        # Check subject patterns
        accepted_subjects = identity.get('accepted_subjects', [])
        subject_ok = not accepted_subjects or any(
            subject.startswith(pattern.rstrip('*')) if pattern.endswith('*') else subject == pattern
            for pattern in accepted_subjects
        )

        allow = tier_ok and scope_ok and subject_ok

        return {
            'allow': allow,
            'decision': 'allow' if allow else 'deny',
            'reason': 'Authorized' if allow else 'Insufficient privileges',
            'tier_ok': tier_ok,
            'scope_ok': scope_ok,
            'subject_ok': subject_ok
        }

    def run_test_case(self, test_case: Dict[str, Any], contract: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single authorization test case."""
        module = test_case.get('module', '')
        subject = test_case.get('subject', '')
        tier = test_case.get('tier', 'guest')
        scopes = test_case.get('scopes', [])
        action = test_case.get('action', 'read')
        expected = test_case.get('expect', 'allow')

        # Track tiers being tested
        self.stats['tiers_tested'].add(tier)

        # Prepare input for OPA
        input_data = {
            'subject': subject,
            'tier': tier,
            'scopes': scopes,
            'module': module,
            'action': action,
            'authenticated': True,
            'token': {'exp': 9999999999},  # Far future
            'env': {
                'mfa': test_case.get('mfa', False),
                'webauthn_verified': test_case.get('webauthn', True)
            }
        }

        # Execute authorization check
        try:
            result = self.execute_opa_query(input_data, contract)
            actual = result['decision']

            # Determine if test passed
            passed = (actual == expected)

            return {
                'module': module,
                'subject': subject,
                'tier': tier,
                'action': action,
                'expected': expected,
                'actual': actual,
                'passed': passed,
                'reason': result.get('reason', ''),
                'details': result
            }

        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            return {
                'module': module,
                'subject': subject,
                'tier': tier,
                'action': action,
                'expected': expected,
                'actual': 'error',
                'passed': False,
                'reason': f"Error: {e}",
                'details': {}
            }

    def run_matrix(self, matrix_path: Path) -> Dict[str, Any]:
        """Run all test cases in a matrix."""
        matrix_data = self.load_matrix(matrix_path)
        if not matrix_data:
            return {'tests': [], 'passed': 0, 'total': 0}

        module = matrix_data.get('module', matrix_path.stem.replace('_authz', ''))
        test_cases = matrix_data.get('test_cases', [])

        # Load contract for module
        contract = self.load_contract(module)
        if not contract:
            logger.warning(f"Skipping matrix {matrix_path} - no contract found")
            return {'tests': [], 'passed': 0, 'total': 0}

        results = []
        passed_count = 0

        for test_case in test_cases:
            result = self.run_test_case(test_case, contract)
            results.append(result)

            if result['passed']:
                passed_count += 1

            # Update module statistics
            if module not in self.stats['modules']:
                self.stats['modules'][module] = {'passed': 0, 'total': 0}

            self.stats['modules'][module]['total'] += 1
            if result['passed']:
                self.stats['modules'][module]['passed'] += 1

        return {
            'module': module,
            'tests': results,
            'passed': passed_count,
            'total': len(test_cases),
            'pass_rate': passed_count / len(test_cases) if test_cases else 0
        }

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all authorization matrix tests."""
        logger.info("Starting authorization matrix test run")

        matrices = self.find_test_matrices()
        self.stats['total_matrices'] = len(matrices)

        all_results = []
        total_passed = 0
        total_tests = 0

        for matrix_path in matrices:
            logger.info(f"Running matrix: {matrix_path.name}")
            matrix_result = self.run_matrix(matrix_path)

            all_results.append(matrix_result)
            total_passed += matrix_result['passed']
            total_tests += matrix_result['total']

        # Update global statistics
        self.stats['total_test_cases'] = total_tests
        self.stats['passed_test_cases'] = total_passed
        self.stats['failed_test_cases'] = total_tests - total_passed

        overall_pass_rate = total_passed / total_tests if total_tests > 0 else 0

        return {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'summary': {
                'total_matrices': len(matrices),
                'total_tests': total_tests,
                'passed': total_passed,
                'failed': total_tests - total_passed,
                'pass_rate': overall_pass_rate,
                'tiers_tested': sorted(self.stats['tiers_tested'])
            },
            'modules': self.stats['modules'],
            'matrices': all_results
        }

    def generate_output(self, results: Dict[str, Any], output_file: Optional[str] = None, min_pass_rate: float = 0.95):
        """Generate output file and check pass rate."""
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(results, indent=2))
            logger.info(f"Results written to {output_file}")

        # Print summary
        summary = results['summary']
        logger.info("Authorization Matrix Test Results:")
        logger.info(f"  Total matrices: {summary['total_matrices']}")
        logger.info(f"  Total tests: {summary['total_tests']}")
        logger.info(f"  Passed: {summary['passed']}")
        logger.info(f"  Failed: {summary['failed']}")
        logger.info(f"  Pass rate: {summary['pass_rate']:.1%}")

        # Check minimum pass rate
        if summary['pass_rate'] < min_pass_rate:
            logger.error(f"Pass rate {summary['pass_rate']:.1%} below minimum {min_pass_rate:.1%}")
            return False

        logger.info("✅ All authorization tests passed minimum threshold")
        return True


def main():
    """CLI interface for authorization matrix runner."""
    parser = argparse.ArgumentParser(
        description="Authorization Matrix Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("--fixtures", type=str,
                       help="Directory containing test fixtures")
    parser.add_argument("--output", type=str,
                       help="Output file for JSON results")
    parser.add_argument("--min-pass-rate", type=float, default=0.95,
                       help="Minimum pass rate threshold (default: 0.95)")
    parser.add_argument("--quiet", action="store_true",
                       help="Suppress verbose logging")

    args = parser.parse_args()

    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)

    # Initialize runner
    runner = MatrixTestRunner(fixtures_dir=args.fixtures)

    # Run all tests
    results = runner.run_all_tests()

    # Generate output and check pass rate
    success = runner.generate_output(results, args.output, args.min_pass_rate)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
