#!/usr/bin/env python3
"""
MATRIZ Lane Assessor

Performs dry-run lane assessment to compute provisional L0-L5 lane assignments
for modules based on their characteristics, dependencies, and maturity.
"""

import argparse
import json
import pathlib
import sys
from typing import Any, Dict, List


class LaneAssessor:
    """Assesses modules for lane placement based on various criteria."""

    def __init__(self, root_path: pathlib.Path):
        self.root_path = root_path
        self.lane_criteria = {
            'L0': {
                'name': 'Archive',
                'description': 'Deprecated or archived modules',
                'criteria': ['deprecated', 'unused', 'legacy']
            },
            'L1': {
                'name': 'Experimental',
                'description': 'Early development, high risk',
                'criteria': ['experimental', 'prototype', 'unstable']
            },
            'L2': {
                'name': 'Development',
                'description': 'Active development, moderate stability',
                'criteria': ['development', 'active', 'testing']
            },
            'L3': {
                'name': 'Candidate',
                'description': 'Stable development, ready for promotion',
                'criteria': ['labs', 'stable', 'validated']
            },
            'L4': {
                'name': 'Accepted',
                'description': 'Production-ready, well-tested',
                'criteria': ['accepted', 'production', 'core']
            },
            'L5': {
                'name': 'Core',
                'description': 'Critical infrastructure, maximum stability',
                'criteria': ['core', 'critical', 'infrastructure']
            }
        }

    def assess_module_characteristics(self, module_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess various characteristics of a module."""
        module_name = module_data['module']
        paths = module_data.get('paths', [])
        contracts = module_data.get('contracts', [])

        characteristics = {
            'has_contract': len(contracts) > 0,
            'path_indicators': self._analyze_path_indicators(paths),
            'name_indicators': self._analyze_name_indicators(module_name),
            'contract_indicators': self._analyze_contract_indicators(contracts),
            'file_count': self._count_files_in_paths(paths),
            'test_coverage': self._assess_test_coverage(paths),
            'dependency_score': self._assess_dependency_score(module_name, paths)
        }

        return characteristics

    def _analyze_path_indicators(self, paths: List[str]) -> Dict[str, bool]:
        """Analyze path patterns for lane indicators."""
        indicators = {
            'in_core': any('core' in path for path in paths),
            'in_accepted': any('accepted' in path for path in paths),
            'in_candidate': any('labs' in path for path in paths),
            'in_experimental': any('experimental' in path for path in paths),
            'in_archive': any('archive' in path for path in paths),
            'in_lukhas_root': any(path.startswith('lukhas/') and '/' not in path[7:] for path in paths),
            'nested_deep': any(path.count('/') > 3 for path in paths)
        }
        return indicators

    def _analyze_name_indicators(self, module_name: str) -> Dict[str, bool]:
        """Analyze module name for lane indicators."""
        name_lower = module_name.lower()
        indicators = {
            'has_core': 'core' in name_lower,
            'has_experimental': 'experimental' in name_lower or 'exp' in name_lower,
            'has_test': 'test' in name_lower,
            'has_deprecated': 'deprecated' in name_lower or 'legacy' in name_lower,
            'has_governance': 'lukhas.governance' in name_lower,
            'has_identity': 'identity' in name_lower,
            'has_api': 'api' in name_lower,
            'has_bridge': 'bridge' in name_lower
        }
        return indicators

    def _analyze_contract_indicators(self, contracts: List[str]) -> Dict[str, Any]:
        """Analyze contract files for maturity indicators."""
        if not contracts:
            return {'maturity_score': 0, 'has_identity_config': False, 'has_policy_config': False}

        maturity_score = 0
        has_identity_config = False
        has_policy_config = False

        for contract_path in contracts:
            try:
                contract_file = self.root_path / contract_path
                if contract_file.exists():
                    with open(contract_file, 'r') as f:
                        contract_data = json.load(f)

                    # Check for maturity indicators
                    if 'identity' in contract_data:
                        has_identity_config = True
                        maturity_score += 2

                    if 'policy' in contract_data:
                        has_policy_config = True
                        maturity_score += 2

                    if 'version' in contract_data:
                        maturity_score += 1

                    if contract_data.get('lane') in ['L4', 'L5']:
                        maturity_score += 3

            except (json.JSONDecodeError, FileNotFoundError):
                continue

        return {
            'maturity_score': maturity_score,
            'has_identity_config': has_identity_config,
            'has_policy_config': has_policy_config
        }

    def _count_files_in_paths(self, paths: List[str]) -> int:
        """Count Python files in module paths."""
        total_files = 0
        for path in paths:
            path_obj = self.root_path / path
            if path_obj.exists() and path_obj.is_dir():
                total_files += len(list(path_obj.rglob("*.py")))
        return total_files

    def _assess_test_coverage(self, paths: List[str]) -> Dict[str, Any]:
        """Assess test coverage indicators."""
        has_tests = False
        test_file_count = 0

        for path in paths:
            path_obj = self.root_path / path
            if path_obj.exists() and path_obj.is_dir():
                test_files = list(path_obj.rglob("test_*.py")) + list(path_obj.rglob("*_test.py"))
                if test_files:
                    has_tests = True
                    test_file_count += len(test_files)

        return {
            'has_tests': has_tests,
            'test_file_count': test_file_count
        }

    def _assess_dependency_score(self, module_name: str, paths: List[str]) -> int:
        """Assess how critical this module might be based on location and name."""
        score = 0

        # Core infrastructure modules
        if any(keyword in module_name.lower() for keyword in ['core', 'identity', 'lukhas.governance']):
            score += 3

        # Critical system components
        if any(keyword in module_name.lower() for keyword in ['matriz', 'consciousness', 'lukhas.memory']):
            score += 2

        # Bridge and API modules (high connectivity)
        if any(keyword in module_name.lower() for keyword in ['bridge', 'api', 'orchestration']):
            score += 2

        return score

    def compute_provisional_lane(self, characteristics: Dict[str, Any]) -> str:
        """Compute provisional lane assignment based on characteristics."""
        path_indicators = characteristics['path_indicators']
        name_indicators = characteristics['name_indicators']
        contract_indicators = characteristics['contract_indicators']

        # Archive lane (L0)
        if (name_indicators['has_deprecated'] or
                path_indicators['in_archive'] or
                characteristics['file_count'] == 0):
            return 'L0'

        # Core lane (L5)
        if (path_indicators['in_core'] and
                name_indicators['has_core'] and
                contract_indicators['maturity_score'] >= 5 and
                characteristics['dependency_score'] >= 3):
            return 'L5'

        # Accepted lane (L4)
        if (path_indicators['in_accepted'] or
                (contract_indicators['maturity_score'] >= 4 and
                 characteristics['test_coverage']['has_tests'] and
                 characteristics['has_contract'])):
            return 'L4'

        # Candidate lane (L3)
        if (path_indicators['in_candidate'] or
                (contract_indicators['maturity_score'] >= 2 and
                 characteristics['has_contract'] and
                 characteristics['file_count'] >= 5)):
            return 'L3'

        # Experimental lane (L1)
        if (path_indicators['in_experimental'] or
                name_indicators['has_experimental'] or
                not characteristics['has_contract']):
            return 'L1'

        # Default to Development lane (L2)
        return 'L2'

    def assess_all_modules(self, inventory_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess lane assignments for all modules."""
        modules = inventory_data.get('modules', [])
        assessments = []

        for module_data in modules:
            characteristics = self.assess_module_characteristics(module_data)
            provisional_lane = self.compute_provisional_lane(characteristics)

            assessment = {
                'module': module_data['module'],
                'current_paths': module_data.get('paths', []),
                'contracts': module_data.get('contracts', []),
                'provisional_lane': provisional_lane,
                'lane_name': self.lane_criteria[provisional_lane]['name'],
                'characteristics': characteristics,
                'confidence': self._compute_confidence(characteristics, provisional_lane)
            }

            assessments.append(assessment)

        # Compute summary statistics
        lane_distribution = {}
        for assessment in assessments:
            lane = assessment['provisional_lane']
            if lane not in lane_distribution:
                lane_distribution[lane] = 0
            lane_distribution[lane] += 1

        return {
            'timestamp': '2025-09-27T13:12:00Z',
            'total_modules': len(assessments),
            'lane_distribution': lane_distribution,
            'lane_criteria': self.lane_criteria,
            'assessments': assessments
        }

    def _compute_confidence(self, characteristics: Dict[str, Any], provisional_lane: str) -> float:
        """Compute confidence score for lane assignment."""
        confidence = 0.5  # Base confidence

        # Increase confidence for clear indicators
        if characteristics['has_contract']:
            confidence += 0.2

        if characteristics['test_coverage']['has_tests']:
            confidence += 0.1

        if characteristics['contract_indicators']['maturity_score'] > 0:
            confidence += 0.1

        # Path-based confidence
        path_indicators = characteristics['path_indicators']
        if any(path_indicators.values()):
            confidence += 0.1

        return min(1.0, confidence)


def main():
    parser = argparse.ArgumentParser(description='Assess provisional lane assignments for MATRIZ modules')
    parser.add_argument('--root', default='.', help='Root directory to scan (default: current directory)')
    parser.add_argument('--inventory', default='artifacts/matriz_inventory.json', help='Input inventory file')
    parser.add_argument('--output', default='artifacts/matriz_lanes.json', help='Output file path')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    root_path = pathlib.Path(args.root).resolve()
    inventory_path = pathlib.Path(args.inventory)
    output_path = pathlib.Path(args.output)

    if args.verbose:
        print(f"Assessing lanes for modules from: {inventory_path}")

    # Load inventory
    try:
        with open(inventory_path, 'r') as f:
            inventory_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Inventory file not found: {inventory_path}")
        return 1

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Perform lane assessment
    assessor = LaneAssessor(root_path)
    results = assessor.assess_all_modules(inventory_data)

    # Write output
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    if args.verbose:
        print("Lane assessment complete:")
        print(f"  Total modules assessed: {results['total_modules']}")
        print("  Lane distribution:")
        for lane, count in sorted(results['lane_distribution'].items()):
            lane_name = results['lane_criteria'][lane]['name']
            print(f"    {lane} ({lane_name}): {count}")
        print(f"  Output written to: {output_path}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
