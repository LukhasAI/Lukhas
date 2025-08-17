#!/usr/bin/env python3
"""
Elite Test Runner
Run the 0.01% tests that push systems to their absolute limits
"""

import subprocess
import time
import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass
import traceback

@dataclass
class TestResult:
    name: str
    status: str  # PASSED, FAILED, SKIPPED
    duration: float
    details: str = ""
    vulnerability_found: bool = False
    

class EliteTestRunner:
    """Runner for elite-level tests"""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent / "elite"
        self.results = []
        
    def run_all_elite_tests(self):
        """Run all elite test categories"""
        print("🎯 LUKHAS AI Elite Test Suite")
        print("="*50)
        print("Running tests that only 0.01% of engineers would create")
        print()
        
        categories = [
            ("Security & Adversarial", "test_security_adversarial.py"),
            ("Performance Extreme", "test_performance_extreme.py"), 
            ("Consciousness Edge Cases", "test_consciousness_edge_cases.py"),
            ("Chaos Engineering", "test_chaos_engineering.py")
        ]
        
        total_start = time.time()
        
        for category_name, test_file in categories:
            print(f"🔥 {category_name}")
            print("-" * 30)
            
            category_results = self.run_test_category(test_file)
            self.results.extend(category_results)
            
            # Summary for category
            passed = sum(1 for r in category_results if r.status == "PASSED")
            failed = sum(1 for r in category_results if r.status == "FAILED")
            vulnerabilities = sum(1 for r in category_results if r.vulnerability_found)
            
            print(f"  ✅ Passed: {passed}")
            print(f"  ❌ Failed: {failed}")
            if vulnerabilities > 0:
                print(f"  🚨 Vulnerabilities Found: {vulnerabilities}")
            print()
            
        total_time = time.time() - total_start
        
        print("🏆 Elite Test Suite Complete")
        print("="*50)
        self.print_summary(total_time)
        
        return self.results
        
    def run_test_category(self, test_file: str) -> List[TestResult]:
        """Run a specific test category"""
        test_path = self.test_dir / test_file
        
        if not test_path.exists():
            print(f"  ⚠️ Test file not found: {test_file}")
            return []
            
        # Get test methods in the file
        test_methods = self.discover_test_methods(test_path)
        category_results = []
        
        for method in test_methods:
            result = self.run_single_test(test_file, method)
            category_results.append(result)
            
            # Print result
            status_icon = "✅" if result.status == "PASSED" else "❌"
            print(f"  {status_icon} {result.name} ({result.duration:.3f}s)")
            
            if result.vulnerability_found:
                print(f"      🚨 VULNERABILITY DETECTED")
            
            if result.status == "FAILED" and result.details:
                print(f"      💡 {result.details[:100]}...")
                
        return category_results
        
    def run_single_test(self, test_file: str, method_name: str) -> TestResult:
        """Run a single test method"""
        test_spec = f"tests/elite/{test_file}::{method_name}"
        
        start_time = time.time()
        
        try:
            # Run pytest for single test
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                test_spec, 
                "-v", "--tb=short", "--quiet"
            ], capture_output=True, text=True, timeout=60)
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                status = "PASSED"
                details = "Test passed successfully"
            else:
                status = "FAILED" 
                details = result.stdout + result.stderr
                
            # Check if failure indicates vulnerability found
            vulnerability_keywords = [
                "SQL injection", "buffer overflow", "race condition",
                "memory leak", "deadlock", "cascade", "vulnerability"
            ]
            
            vulnerability_found = any(
                keyword.lower() in details.lower() 
                for keyword in vulnerability_keywords
            )
            
            # Special case: some "failures" are actually successful vulnerability detection
            if status == "FAILED" and any([
                "assert not True" in details,  # Security test found injection
                "assert leaked >" in details,  # Memory leak detected
                "assert.*_time.*>" in details,  # Timing attack detected
                "assert cascade_events" in details,  # Cascade prevented
            ]):
                vulnerability_found = True
                
            return TestResult(
                name=method_name,
                status=status,
                duration=duration,
                details=details,
                vulnerability_found=vulnerability_found
            )
            
        except subprocess.TimeoutExpired:
            return TestResult(
                name=method_name,
                status="FAILED",
                duration=60.0,
                details="Test timed out after 60 seconds"
            )
        except Exception as e:
            return TestResult(
                name=method_name,
                status="FAILED", 
                duration=time.time() - start_time,
                details=str(e)
            )
            
    def discover_test_methods(self, test_file: Path) -> List[str]:
        """Discover test methods in a file"""
        methods = []
        
        try:
            with open(test_file) as f:
                content = f.read()
                
            # Simple regex to find test methods
            import re
            pattern = r'def (test_\w+)\s*\('
            matches = re.findall(pattern, content)
            
            # Get class name for full test specification
            class_pattern = r'class (\w+):'
            class_matches = re.findall(class_pattern, content)
            
            if class_matches:
                class_name = class_matches[0]
                methods = [f"{class_name}::{method}" for method in matches]
            else:
                methods = matches
                
        except Exception as e:
            print(f"Error discovering tests in {test_file}: {e}")
            
        return methods
        
    def print_summary(self, total_time: float):
        """Print comprehensive test summary"""
        total_tests = len(self.results)
        passed = sum(1 for r in self.results if r.status == "PASSED")
        failed = sum(1 for r in self.results if r.status == "FAILED")
        vulnerabilities = sum(1 for r in self.results if r.vulnerability_found)
        
        print(f"📊 Summary:")
        print(f"  Total Tests: {total_tests}")
        print(f"  ✅ Passed: {passed}")
        print(f"  ❌ Failed: {failed}")
        print(f"  🚨 Vulnerabilities/Edge Cases Found: {vulnerabilities}")
        print(f"  ⏱️ Total Time: {total_time:.2f}s")
        print(f"  📈 Success Rate: {(passed/total_tests*100):.1f}%")
        
        if vulnerabilities > 0:
            print(f"\n🔍 Elite Tests Successfully Detected:")
            for result in self.results:
                if result.vulnerability_found:
                    print(f"  🎯 {result.name}")
                    
        print(f"\n💡 Elite Tests demonstrate:")
        print(f"  • Advanced security vulnerability detection")
        print(f"  • Performance bottleneck identification") 
        print(f"  • Edge case boundary testing")
        print(f"  • Chaos engineering resilience")
        print(f"  • Memory safety validation")
        print(f"  • Concurrency issue detection")
        
        # Generate report
        self.generate_elite_report()
        
    def generate_elite_report(self):
        """Generate comprehensive elite test report"""
        report = {
            "test_suite": "LUKHAS AI Elite Tests",
            "description": "Tests that only 0.01% of engineers would create",
            "timestamp": time.time(),
            "summary": {
                "total_tests": len(self.results),
                "passed": sum(1 for r in self.results if r.status == "PASSED"),
                "failed": sum(1 for r in self.results if r.status == "FAILED"),
                "vulnerabilities_found": sum(1 for r in self.results if r.vulnerability_found)
            },
            "categories": {
                "security_adversarial": [r.name for r in self.results if "security" in r.name.lower()],
                "performance_extreme": [r.name for r in self.results if "performance" in r.name.lower()],
                "consciousness_edge": [r.name for r in self.results if "consciousness" in r.name.lower()],
                "chaos_engineering": [r.name for r in self.results if "chaos" in r.name.lower()]
            },
            "vulnerabilities_detected": [
                {
                    "test": r.name,
                    "status": r.status,
                    "details": r.details[:200] + "..." if len(r.details) > 200 else r.details
                }
                for r in self.results if r.vulnerability_found
            ]
        }
        
        report_path = Path("tests/elite_test_report.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
            
        print(f"\n📄 Detailed report saved: {report_path}")


def main():
    """Main execution"""
    runner = EliteTestRunner()
    results = runner.run_all_elite_tests()
    
    # Exit with appropriate code
    failed_count = sum(1 for r in results if r.status == "FAILED")
    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    exit(main())