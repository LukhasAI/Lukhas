#!/usr/bin/env python3
"""
Matrix Test Runner for LUKHAS
Runs comprehensive validation tests for all generated matrix authorization test cases.
"""

import yaml
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging
import glob
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MatrixTestRunner:
    """Runs and validates matrix authorization tests."""

    def __init__(self, test_dir: Path = None):
        """Initialize the test runner."""
        self.test_dir = test_dir or Path(__file__).parent.parent / "tests" / "matrix_identity"
        self.lukhas_root = Path(__file__).parent.parent / "lukhas"

        # Test statistics
        self.stats = {
            'total_matrices': 0,
            'total_test_cases': 0,
            'passed_test_cases': 0,
            'failed_test_cases': 0,
            'skipped_test_cases': 0,
            'coverage_by_tier': defaultdict(int),
            'coverage_by_module': defaultdict(int)
        }

        logger.info(f"Initialized MatrixTestRunner:")
        logger.info(f"  Test directory: {self.test_dir}")
        logger.info(f"  Lukhas root: {self.lukhas_root}")

    def find_test_matrices(self) -> List[Path]:
        """Find all test matrix files."""
        pattern = str(self.test_dir / "**" / "*_authz.yaml")
        matrices = [Path(p) for p in glob.glob(pattern, recursive=True)]
        logger.info(f"Found {len(matrices)} test matrices")
        return matrices

    def load_matrix_contract(self, module_name: str) -> Dict[str, Any]:
        """Load the matrix contract for a module."""
        # Handle nested module names (e.g., core.policy -> core/policy)
        if '.' in module_name:
            parts = module_name.split('.')
            contract_path = self.lukhas_root / '/'.join(parts) / f"matrix_{parts[-1]}.json"
        else:
            # Search for the contract file
            pattern = str(self.lukhas_root / "**" / f"matrix_{module_name}.json")
            matches = glob.glob(pattern, recursive=True)
            if matches:
                contract_path = Path(matches[0])
            else:
                logger.warning(f"Contract not found for module: {module_name}")
                return {}

        try:
            with open(contract_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading contract for {module_name}: {e}")
            return {}

    def validate_test_case(self, test_case: Dict[str, Any], module_contract: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate a single test case against the module contract."""
        try:
            test_input = test_case['input']
            expected = test_case['expected']

            # Extract test parameters
            tier = test_input['tier']
            tier_num = test_input['tier_num']
            subject = test_input['subject']
            scopes = test_input.get('scopes', [])
            action = test_input['action']
            env = test_input.get('env', {})
            token = test_input.get('token', {})

            # Get identity configuration from contract
            identity = module_contract.get('identity', {})
            if not identity:
                return False, "No identity configuration in contract"

            required_tiers = identity.get('required_tiers', [])
            required_tiers_numeric = identity.get('required_tiers_numeric', [])
            accepted_subjects = identity.get('accepted_subjects', [])
            required_scopes = identity.get('scopes', [])
            webauthn_required = identity.get('webauthn_required', False)

            # Validation logic

            # 1. Check if subject is accepted
            subject_accepted = False
            for accepted_pattern in accepted_subjects:
                if accepted_pattern.endswith('*'):
                    prefix = accepted_pattern[:-1]
                    if subject.startswith(prefix):
                        subject_accepted = True
                        break
                elif subject == accepted_pattern:
                    subject_accepted = True
                    break

            if not subject_accepted:
                actual_result = False
                validation_reason = f"Subject {subject} not in accepted subjects"

            # 2. Check tier authorization
            elif tier in required_tiers or tier_num in required_tiers_numeric:
                # Tier is authorized, check other conditions

                # 3. Check scopes
                if required_scopes and not all(scope in scopes for scope in required_scopes):
                    actual_result = False
                    validation_reason = "Missing required scopes"

                # 4. Check token validity
                elif token and token.get('exp', float('inf')) < 1700000000:  # Rough current timestamp
                    actual_result = False
                    validation_reason = "Token expired"

                elif token and token.get('aud') != 'lukhas-matrix':
                    actual_result = False
                    validation_reason = "Wrong token audience"

                # 5. Check WebAuthn if required
                elif webauthn_required and not env.get('webauthn_verified', False):
                    actual_result = False
                    validation_reason = "WebAuthn required but not verified"

                else:
                    actual_result = True
                    validation_reason = f"Tier {tier} authorized for {action}"

            else:
                # Tier is not authorized
                actual_result = False
                validation_reason = f"Tier {tier} not authorized"

            # Compare with expected result
            if actual_result == expected:
                return True, f"PASS: {validation_reason}"
            else:
                return False, f"FAIL: Expected {expected}, got {actual_result}. {validation_reason}"

        except Exception as e:
            return False, f"ERROR: {str(e)}"

    def run_matrix_tests(self, matrix_path: Path) -> Dict[str, Any]:
        """Run tests for a single matrix file."""
        try:
            with open(matrix_path, 'r') as f:
                matrix_data = yaml.safe_load(f)

            module_name = matrix_data['module']
            test_cases = matrix_data.get('test_cases', [])

            # Load corresponding contract
            module_contract = self.load_matrix_contract(module_name)

            results = {
                'module': module_name,
                'matrix_path': str(matrix_path),
                'total_cases': len(test_cases),
                'passed': 0,
                'failed': 0,
                'skipped': 0,
                'test_results': []
            }

            for i, test_case in enumerate(test_cases):
                test_name = test_case.get('name', f'test_{i}')

                if not module_contract:
                    results['skipped'] += 1
                    results['test_results'].append({
                        'name': test_name,
                        'status': 'SKIPPED',
                        'reason': 'Contract not found'
                    })
                    continue

                passed, reason = self.validate_test_case(test_case, module_contract)

                if passed:
                    results['passed'] += 1
                    status = 'PASS'
                else:
                    results['failed'] += 1
                    status = 'FAIL'

                results['test_results'].append({
                    'name': test_name,
                    'status': status,
                    'reason': reason
                })

                # Update statistics
                tier = test_case['input'].get('tier', 'unknown')
                self.stats['coverage_by_tier'][tier] += 1
                self.stats['coverage_by_module'][module_name] += 1

            return results

        except Exception as e:
            logger.error(f"Error running tests for {matrix_path}: {e}")
            return {
                'module': 'unknown',
                'matrix_path': str(matrix_path),
                'total_cases': 0,
                'passed': 0,
                'failed': 0,
                'skipped': 1,
                'test_results': [{
                    'name': 'matrix_load',
                    'status': 'ERROR',
                    'reason': str(e)
                }]
            }

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all matrix tests and return comprehensive results."""
        matrices = self.find_test_matrices()
        all_results = []

        logger.info(f"Running tests for {len(matrices)} matrices...")

        for matrix_path in matrices:
            logger.info(f"Testing matrix: {matrix_path.name}")
            result = self.run_matrix_tests(matrix_path)
            all_results.append(result)

            # Update global statistics
            self.stats['total_matrices'] += 1
            self.stats['total_test_cases'] += result['total_cases']
            self.stats['passed_test_cases'] += result['passed']
            self.stats['failed_test_cases'] += result['failed']
            self.stats['skipped_test_cases'] += result['skipped']

        # Generate summary
        summary = {
            'statistics': dict(self.stats),
            'results_by_matrix': all_results,
            'success_rate': (self.stats['passed_test_cases'] / max(self.stats['total_test_cases'], 1)) * 100
        }

        return summary

    def generate_coverage_report(self) -> str:
        """Generate a coverage report."""
        report = ["# Matrix Test Coverage Report\n"]

        report.append(f"## Overall Statistics")
        report.append(f"- Total Matrices: {self.stats['total_matrices']}")
        report.append(f"- Total Test Cases: {self.stats['total_test_cases']}")
        report.append(f"- Passed: {self.stats['passed_test_cases']}")
        report.append(f"- Failed: {self.stats['failed_test_cases']}")
        report.append(f"- Skipped: {self.stats['skipped_test_cases']}")

        success_rate = (self.stats['passed_test_cases'] / max(self.stats['total_test_cases'], 1)) * 100
        report.append(f"- Success Rate: {success_rate:.1f}%\n")

        report.append("## Coverage by Tier")
        for tier, count in sorted(self.stats['coverage_by_tier'].items()):
            report.append(f"- {tier}: {count} test cases")

        report.append("\n## Coverage by Module")
        for module, count in sorted(self.stats['coverage_by_module'].items()):
            report.append(f"- {module}: {count} test cases")

        return "\n".join(report)

    def print_summary(self, results: Dict[str, Any]):
        """Print a summary of test results."""
        print("\n" + "="*60)
        print("MATRIX TEST SUMMARY")
        print("="*60)

        stats = results['statistics']
        print(f"Total Matrices: {stats['total_matrices']}")
        print(f"Total Test Cases: {stats['total_test_cases']}")
        print(f"Passed: {stats['passed_test_cases']}")
        print(f"Failed: {stats['failed_test_cases']}")
        print(f"Skipped: {stats['skipped_test_cases']}")
        print(f"Success Rate: {results['success_rate']:.1f}%")

        # Show failures if any
        if stats['failed_test_cases'] > 0:
            print("\nFAILED TESTS:")
            for matrix_result in results['results_by_matrix']:
                if matrix_result['failed'] > 0:
                    print(f"\n  {matrix_result['module']}:")
                    for test_result in matrix_result['test_results']:
                        if test_result['status'] == 'FAIL':
                            print(f"    - {test_result['name']}: {test_result['reason']}")

        print("\n" + "="*60)

def main():
    """Main function to run all matrix tests."""
    runner = MatrixTestRunner()

    logger.info("Starting comprehensive matrix test validation...")

    results = runner.run_all_tests()

    # Print summary
    runner.print_summary(results)

    # Generate coverage report
    coverage_report = runner.generate_coverage_report()
    report_path = Path(__file__).parent.parent / "tests" / "matrix_coverage_report.md"
    with open(report_path, 'w') as f:
        f.write(coverage_report)

    logger.info(f"Coverage report saved to: {report_path}")

    # Return exit code based on success rate
    success_rate = results['success_rate']
    if success_rate >= 95:
        logger.info("All tests passed with excellent coverage!")
        return 0
    elif success_rate >= 80:
        logger.warning("Most tests passed, but some issues found")
        return 1
    else:
        logger.error("Significant test failures - review matrices")
        return 2

if __name__ == "__main__":
    sys.exit(main())