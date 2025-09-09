#!/usr/bin/env python3
"""
🧠 LUKHAS AI Consciousness Test Runner
=====================================

Trinity Framework Test Execution: ⚛️🧠🛡️

This script provides easy execution of the consciousness test suite
for the LUKHAS AI Agent Army. Use this for:

- Continuous integration validation
- Agent coordination testing
- Syntax error regression prevention
- Trinity Framework compliance checking

Usage:
    python tests/consciousness/run_consciousness_tests.py [options]

Options:
    --quick     : Run quick syntax validation only
    --full      : Run comprehensive test suite (default)
    --trinity   : Run Trinity Framework compliance tests only
    --regression: Run regression prevention tests only
    --verbose   : Enable verbose output
    --html      : Generate HTML test report

Author: LUKHAS AI Agent Army - GitHub Copilot Deputy Assistant
Date: September 9, 2025
"""

import argparse
import sys
import time
from pathlib import Path
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class ConsciousnessTestRunner:
    """🧠 Consciousness test execution coordinator"""
    
    def __init__(self):
        self.project_root = project_root
        self.test_dir = self.project_root / "tests" / "consciousness"
        self.results = {}
    
    def run_quick_validation(self):
        """⚡ Quick syntax validation for rapid feedback"""
        logger.info("🔍 Running quick consciousness syntax validation...")
        
        start_time = time.time()
        
        # Quick syntax check
        cmd = [
            "python3", "-m", "py_compile",
            str(self.project_root / "candidate" / "consciousness" / "reasoning" / "id_reasoning_engine.py"),
            str(self.project_root / "candidate" / "consciousness" / "reflection" / "brain_integration.py"),
            str(self.project_root / "candidate" / "consciousness" / "reflection" / "core_integrator.py")
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            duration = time.time() - start_time
            
            logger.info(f"✅ Quick validation passed in {duration:.2f}s")
            self.results['quick_validation'] = {'status': 'PASSED', 'duration': duration}
            return True
            
        except subprocess.CalledProcessError as e:
            duration = time.time() - start_time
            logger.error(f"❌ Quick validation failed in {duration:.2f}s: {e}")
            self.results['quick_validation'] = {'status': 'FAILED', 'duration': duration, 'error': str(e)}
            return False
    
    def run_comprehensive_suite(self, verbose=False):
        """🧠 Run comprehensive consciousness test suite"""
        logger.info("🧠 Running comprehensive consciousness test suite...")
        
        start_time = time.time()
        
        pytest_args = [
            "python3", "-m", "pytest",
            str(self.test_dir / "test_consciousness_suite_comprehensive.py"),
            "-v" if verbose else "-q",
            "--tb=short",
            "--color=yes"
        ]
        
        try:
            result = subprocess.run(pytest_args, capture_output=True, text=True, check=True)
            duration = time.time() - start_time
            
            logger.info(f"✅ Comprehensive suite passed in {duration:.2f}s")
            self.results['comprehensive_suite'] = {'status': 'PASSED', 'duration': duration}
            
            if verbose:
                print(result.stdout)
            
            return True
            
        except subprocess.CalledProcessError as e:
            duration = time.time() - start_time
            logger.error(f"❌ Comprehensive suite failed in {duration:.2f}s")
            self.results['comprehensive_suite'] = {'status': 'FAILED', 'duration': duration, 'error': str(e)}
            
            if verbose:
                print(result.stdout)
                print(result.stderr)
            
            return False
    
    def run_trinity_framework_tests(self):
        """⚛️🧠🛡️ Run Trinity Framework compliance tests"""
        logger.info("⚛️🧠🛡️ Running Trinity Framework compliance tests...")
        
        start_time = time.time()
        
        pytest_args = [
            "python3", "-m", "pytest",
            str(self.test_dir / "test_consciousness_suite_comprehensive.py"),
            "-k", "trinity",
            "-v",
            "--tb=short"
        ]
        
        try:
            result = subprocess.run(pytest_args, capture_output=True, text=True, check=True)
            duration = time.time() - start_time
            
            logger.info(f"✅ Trinity Framework tests passed in {duration:.2f}s")
            self.results['trinity_framework'] = {'status': 'PASSED', 'duration': duration}
            return True
            
        except subprocess.CalledProcessError as e:
            duration = time.time() - start_time
            logger.error(f"❌ Trinity Framework tests failed in {duration:.2f}s")
            self.results['trinity_framework'] = {'status': 'FAILED', 'duration': duration, 'error': str(e)}
            return False
    
    def run_regression_tests(self):
        """🛡️ Run syntax error regression prevention tests"""
        logger.info("🛡️ Running syntax error regression prevention tests...")
        
        start_time = time.time()
        
        pytest_args = [
            "python3", "-m", "pytest",
            str(self.test_dir / "test_consciousness_suite_comprehensive.py"),
            "-k", "regression",
            "-v",
            "--tb=short"
        ]
        
        try:
            result = subprocess.run(pytest_args, capture_output=True, text=True, check=True)
            duration = time.time() - start_time
            
            logger.info(f"✅ Regression tests passed in {duration:.2f}s")
            self.results['regression_tests'] = {'status': 'PASSED', 'duration': duration}
            return True
            
        except subprocess.CalledProcessError as e:
            duration = time.time() - start_time
            logger.error(f"❌ Regression tests failed in {duration:.2f}s")
            self.results['regression_tests'] = {'status': 'FAILED', 'duration': duration, 'error': str(e)}
            return False
    
    def generate_html_report(self):
        """📊 Generate HTML test report"""
        logger.info("📊 Generating HTML test report...")
        
        pytest_args = [
            "python3", "-m", "pytest",
            str(self.test_dir / "test_consciousness_suite_comprehensive.py"),
            "--html=tests/consciousness/report.html",
            "--self-contained-html",
            "-v"
        ]
        
        try:
            subprocess.run(pytest_args, check=True)
            logger.info("✅ HTML report generated: tests/consciousness/report.html")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ HTML report generation failed: {e}")
            return False
    
    def print_summary(self):
        """📋 Print test execution summary"""
        print("\n" + "="*60)
        print("🧠 LUKHAS Consciousness Test Suite Summary")
        print("="*60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results.values() if r['status'] == 'PASSED')
        
        print(f"Total Test Categories: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        
        if self.results:
            total_duration = sum(r['duration'] for r in self.results.values())
            print(f"Total Duration: {total_duration:.2f}s")
        
        print("\nDetailed Results:")
        for test_name, result in self.results.items():
            status_icon = "✅" if result['status'] == 'PASSED' else "❌"
            print(f"  {status_icon} {test_name}: {result['status']} ({result['duration']:.2f}s)")
        
        print("\n⚛️🧠🛡️ Trinity Framework Status: " + 
              ("OPERATIONAL" if passed_tests == total_tests else "REQUIRES ATTENTION"))
        print("="*60)


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="🧠 LUKHAS AI Consciousness Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_consciousness_tests.py --quick
  python run_consciousness_tests.py --full --verbose
  python run_consciousness_tests.py --trinity
  python run_consciousness_tests.py --regression
  python run_consciousness_tests.py --html
        """
    )
    
    parser.add_argument('--quick', action='store_true', 
                       help='Run quick syntax validation only')
    parser.add_argument('--full', action='store_true', 
                       help='Run comprehensive test suite (default)')
    parser.add_argument('--trinity', action='store_true', 
                       help='Run Trinity Framework compliance tests only')
    parser.add_argument('--regression', action='store_true', 
                       help='Run regression prevention tests only')
    parser.add_argument('--verbose', action='store_true', 
                       help='Enable verbose output')
    parser.add_argument('--html', action='store_true', 
                       help='Generate HTML test report')
    
    args = parser.parse_args()
    
    # Default to full suite if no specific option given
    if not any([args.quick, args.trinity, args.regression, args.html]):
        args.full = True
    
    runner = ConsciousnessTestRunner()
    all_passed = True
    
    print("🧠 LUKHAS AI Consciousness Test Runner")
    print("⚛️🧠🛡️ Trinity Framework Validation System")
    print("="*60)
    
    if args.quick:
        all_passed &= runner.run_quick_validation()
    
    if args.full:
        all_passed &= runner.run_comprehensive_suite(verbose=args.verbose)
    
    if args.trinity:
        all_passed &= runner.run_trinity_framework_tests()
    
    if args.regression:
        all_passed &= runner.run_regression_tests()
    
    if args.html:
        runner.generate_html_report()
    
    runner.print_summary()
    
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
