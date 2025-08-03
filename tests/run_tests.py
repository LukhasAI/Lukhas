#!/usr/bin/env python3
"""
LUKHAS Comprehensive Test Runner
Runs all test suites with proper configuration and reporting
"""

import sys
import os
import argparse
import pytest
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any


class LUKHASTestRunner:
    """Comprehensive test runner for LUKHAS systems"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.test_dir = self.project_root / "tests"
        self.results_dir = self.test_dir / "results"
        self.results_dir.mkdir(exist_ok=True)
        
        # Test categories
        self.test_suites = {
            'unit': {
                'path': 'unit/',
                'description': 'Unit tests for individual components',
                'files': [
                    'test_consciousness.py',
                    'test_memory.py',
                    'test_guardian.py',
                    'test_symbolic.py'
                ]
            },
            'integration': {
                'path': 'integration/',
                'description': 'Integration tests for system interactions',
                'files': ['test_core_integration.py']
            },
            'e2e': {
                'path': 'e2e/',
                'description': 'End-to-end workflow tests',
                'files': ['test_e2e_workflows.py']
            },
            'security': {
                'path': 'security/',
                'description': 'Security and authentication tests',
                'files': ['test_enhanced_security.py']
            },
            'api': {
                'path': 'api/',
                'description': 'API functionality tests',
                'files': ['test_enhanced_api.py']
            },
            'governance': {
                'path': 'governance/',
                'description': 'Governance and compliance tests',
                'files': [
                    'test_governance.py',
                    'test_enhanced_governance.py',
                    'test_comprehensive_governance.py'
                ]
            }
        }
        
    def run_suite(self, suite_name: str, verbose: bool = False,
                  coverage: bool = False) -> Dict[str, Any]:
        """Run a specific test suite"""
        if suite_name not in self.test_suites:
            raise ValueError(f"Unknown test suite: {suite_name}")
            
        suite = self.test_suites[suite_name]
        suite_path = self.test_dir / suite['path']
        
        # Build pytest arguments
        pytest_args = []
        
        # Add test files
        for test_file in suite['files']:
            test_path = suite_path / test_file
            if test_path.exists():
                pytest_args.append(str(test_path))
                
        if not pytest_args:
            print(f"No test files found for suite: {suite_name}")
            return {'status': 'error', 'message': 'No test files found'}
            
        # Add options
        if verbose:
            pytest_args.extend(['-v', '-s'])
        else:
            pytest_args.append('-q')
            
        if coverage:
            pytest_args.extend([
                '--cov=core',
                '--cov=consciousness', 
                '--cov=memory',
                '--cov=governance',
                '--cov=emotion',
                '--cov=bridge',
                '--cov-report=term-missing',
                '--cov-report=html:tests/results/coverage'
            ])
            
        # Add result output
        result_file = self.results_dir / f"{suite_name}_results.json"
        pytest_args.extend(['--json-report', f'--json-report-file={result_file}'])
        
        # Run tests
        print(f"\n{'='*60}")
        print(f"Running {suite_name} tests: {suite['description']}")
        print(f"{'='*60}\n")
        
        exit_code = pytest.main(pytest_args)
        
        # Read results
        results = {
            'suite': suite_name,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'exit_code': exit_code,
            'status': 'passed' if exit_code == 0 else 'failed'
        }
        
        if result_file.exists():
            with open(result_file, 'r') as f:
                json_results = json.load(f)
                results.update(json_results)
                
        return results
        
    def run_all(self, exclude: List[str] = None, **kwargs) -> Dict[str, Any]:
        """Run all test suites"""
        exclude = exclude or []
        all_results = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'suites': {}
        }
        
        for suite_name in self.test_suites:
            if suite_name in exclude:
                print(f"Skipping {suite_name} tests (excluded)")
                continue
                
            suite_results = self.run_suite(suite_name, **kwargs)
            all_results['suites'][suite_name] = suite_results
            
        # Summary
        total_suites = len(all_results['suites'])
        passed_suites = sum(1 for r in all_results['suites'].values() 
                           if r.get('status') == 'passed')
        
        all_results['summary'] = {
            'total_suites': total_suites,
            'passed_suites': passed_suites,
            'failed_suites': total_suites - passed_suites,
            'success_rate': passed_suites / total_suites if total_suites > 0 else 0
        }
        
        return all_results
        
    def run_performance_tests(self, iterations: int = 3) -> Dict[str, Any]:
        """Run performance benchmarks"""
        print(f"\n{'='*60}")
        print("Running Performance Benchmarks")
        print(f"{'='*60}\n")
        
        pytest_args = [
            'tests/integration/test_core_integration.py::TestSystemPerformance',
            'tests/e2e/test_e2e_workflows.py::TestPerformanceScenarios',
            '-v',
            f'--benchmark-only',
            f'--benchmark-rounds={iterations}'
        ]
        
        exit_code = pytest.main(pytest_args)
        
        return {
            'status': 'completed' if exit_code == 0 else 'failed',
            'iterations': iterations,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    def run_smoke_tests(self) -> Dict[str, Any]:
        """Run quick smoke tests"""
        print(f"\n{'='*60}")
        print("Running Smoke Tests (Quick Validation)")
        print(f"{'='*60}\n")
        
        # Select key tests from each suite
        smoke_tests = [
            'tests/unit/test_consciousness.py::TestConsciousnessCore::test_initialization',
            'tests/unit/test_memory.py::TestMemoryCore::test_initialization',
            'tests/unit/test_guardian.py::TestGuardianCore::test_initialization',
            'tests/api/test_enhanced_api.py::TestEnhancedAPI::test_health_endpoint',
            'tests/security/test_enhanced_security.py::TestEnhancedCrypto::test_aes_encryption'
        ]
        
        pytest_args = smoke_tests + ['-v']
        exit_code = pytest.main(pytest_args)
        
        return {
            'status': 'passed' if exit_code == 0 else 'failed',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    def generate_report(self, results: Dict[str, Any]):
        """Generate test report"""
        report_path = self.results_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(report_path, 'w') as f:
            f.write("# LUKHAS Test Report\n\n")
            f.write(f"**Generated:** {results['timestamp']}\n\n")
            
            if 'summary' in results:
                summary = results['summary']
                f.write("## Summary\n\n")
                f.write(f"- Total Test Suites: {summary['total_suites']}\n")
                f.write(f"- Passed: {summary['passed_suites']}\n")
                f.write(f"- Failed: {summary['failed_suites']}\n")
                f.write(f"- Success Rate: {summary['success_rate']:.1%}\n\n")
                
            f.write("## Test Suites\n\n")
            
            for suite_name, suite_results in results.get('suites', {}).items():
                f.write(f"### {suite_name.upper()}\n\n")
                f.write(f"**Status:** {suite_results.get('status', 'unknown')}\n")
                
                if 'summary' in suite_results:
                    test_summary = suite_results['summary']
                    f.write(f"- Total Tests: {test_summary.get('total', 0)}\n")
                    f.write(f"- Passed: {test_summary.get('passed', 0)}\n")
                    f.write(f"- Failed: {test_summary.get('failed', 0)}\n")
                    f.write(f"- Skipped: {test_summary.get('skipped', 0)}\n")
                    
                f.write("\n")
                
        print(f"\nTest report generated: {report_path}")
        return report_path


def main():
    """Main test runner entry point"""
    parser = argparse.ArgumentParser(description='LUKHAS Comprehensive Test Runner')
    
    parser.add_argument(
        'command',
        choices=['all', 'suite', 'smoke', 'performance'],
        help='Test command to run'
    )
    
    parser.add_argument(
        '--suite',
        choices=['unit', 'integration', 'e2e', 'security', 'api', 'governance'],
        help='Specific test suite to run (with suite command)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    parser.add_argument(
        '--coverage', '-c',
        action='store_true',
        help='Generate coverage report'
    )
    
    parser.add_argument(
        '--exclude',
        nargs='+',
        help='Suites to exclude (with all command)'
    )
    
    parser.add_argument(
        '--report', '-r',
        action='store_true',
        help='Generate test report'
    )
    
    args = parser.parse_args()
    
    # Initialize runner
    runner = LUKHASTestRunner()
    
    # Run appropriate command
    if args.command == 'all':
        results = runner.run_all(
            exclude=args.exclude,
            verbose=args.verbose,
            coverage=args.coverage
        )
    elif args.command == 'suite':
        if not args.suite:
            print("Error: --suite required with suite command")
            sys.exit(1)
        results = runner.run_suite(
            args.suite,
            verbose=args.verbose,
            coverage=args.coverage
        )
    elif args.command == 'smoke':
        results = runner.run_smoke_tests()
    elif args.command == 'performance':
        results = runner.run_performance_tests()
        
    # Generate report if requested
    if args.report:
        runner.generate_report(results)
        
    # Exit with appropriate code
    if results.get('status') == 'passed' or results.get('summary', {}).get('failed_suites', 1) == 0:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()