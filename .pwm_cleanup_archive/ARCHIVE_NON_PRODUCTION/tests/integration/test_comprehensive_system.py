#!/usr/bin/env python3
"""
🔬 LUKHAS AGI Comprehensive System Test Suite
Tests all implemented features and generates detailed test report
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class SystemTestSuite:
    """Comprehensive test suite for LUKHAS AGI system"""

    def __init__(self):
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_categories": {},
            "detailed_results": [],
        }

    def run_test(self, category, test_name, test_func):
        """Run a single test and record results"""
        self.test_results["total_tests"] += 1

        if category not in self.test_results["test_categories"]:
            self.test_results["test_categories"][category] = {"passed": 0, "failed": 0}

        try:
            start_time = time.time()
            result = test_func()
            end_time = time.time()

            if result is True or (
                isinstance(result, dict) and result.get("success", False)
            ):
                self.test_results["passed_tests"] += 1
                self.test_results["test_categories"][category]["passed"] += 1
                status = "✅ PASS"
                error = None
            else:
                self.test_results["failed_tests"] += 1
                self.test_results["test_categories"][category]["failed"] += 1
                status = "❌ FAIL"
                error = str(result) if result is not True else "Test returned False"

        except Exception as e:
            self.test_results["failed_tests"] += 1
            self.test_results["test_categories"][category]["failed"] += 1
            status = "❌ ERROR"
            error = str(e)
            end_time = time.time()

        test_result = {
            "category": category,
            "test_name": test_name,
            "status": status,
            "duration": f"{(end_time - start_time):.3f}s",
            "error": error,
        }

        self.test_results["detailed_results"].append(test_result)
        print(f"{status} {category}: {test_name} ({test_result['duration']})")

        if error:
            print(f"   Error: {error}")

    def test_dast_component_instantiation(self):
        """Test all DAST components can be instantiated"""
        components = [
            (
                "aggregator",
                "core.interfaces.as_agent.sys.dast.aggregator",
                "DASTAggregator",
            ),
            (
                "dast_logger",
                "core.interfaces.as_agent.sys.dast.dast_logger",
                "DASTLogger",
            ),
            (
                "partner_sdk",
                "core.interfaces.as_agent.sys.dast.partner_sdk",
                "PartnerSDK",
            ),
            ("store", "core.interfaces.as_agent.sys.dast.store", "DASTStore"),
        ]

        success_count = 0
        for component_name, module_path, class_name in components:
            try:
                module = __import__(module_path, fromlist=[class_name])
                component_class = getattr(module, class_name)
                instance = component_class()
                success_count += 1
            except Exception as e:
                return {"success": False, "error": f"{component_name}: {e}"}

        return success_count == len(components)

    def test_dast_singleton_patterns(self):
        """Test singleton patterns work correctly"""
        try:
            # Test DASTAggregator singleton
            from core.interfaces.as_agent.sys.dast.aggregator import (
                DASTAggregator,
            )

            instance1 = DASTAggregator()
            instance2 = DASTAggregator()

            if instance1 is not instance2:
                return {"success": False, "error": "DASTAggregator singleton failed"}

            # Test DASTLogger singleton
            from core.interfaces.as_agent.sys.dast.dast_logger import (
                DASTLogger,
            )

            logger1 = DASTLogger()
            logger2 = DASTLogger()

            if logger1 is not logger2:
                return {"success": False, "error": "DASTLogger singleton failed"}

            return True

        except Exception as e:
            return {"success": False, "error": str(e)}

    def test_legacy_function_compatibility(self):
        """Test all legacy functions are accessible"""
        legacy_tests = [
            ("core.interfaces.as_agent.sys.dast.aggregator", "aggregate_dast_tags"),
            ("core.interfaces.as_agent.sys.dast.dast_logger", "log_tag_event"),
            ("core.interfaces.as_agent.sys.dast.partner_sdk", "receive_partner_input"),
            ("core.interfaces.as_agent.sys.dast.store", "save_tags_to_file"),
            ("core.interfaces.as_agent.sys.dast.store", "load_tags_from_file"),
        ]

        for module_path, function_name in legacy_tests:
            try:
                module = __import__(module_path, fromlist=[function_name])
                func = getattr(module, function_name)
                if not callable(func):
                    return {
                        "success": False,
                        "error": f"{function_name} is not callable",
                    }
            except Exception as e:
                return {"success": False, "error": f"{function_name}: {e}"}

        return True

    def test_dast_functionality(self):
        """Test DAST components basic functionality"""
        try:
            # Test aggregator functionality
            from core.interfaces.as_agent.sys.dast.aggregator import (
                DASTAggregator,
            )

            aggregator = DASTAggregator()
            test_input = {"gesture_tags": ["test"], "widget_tags": ["demo"]}
            result = aggregator.aggregate_symbolic_tags(test_input)

            if not isinstance(result, dict):
                return {"success": False, "error": "Aggregator did not return dict"}

            # Test logger functionality
            from core.interfaces.as_agent.sys.dast.dast_logger import (
                DASTLogger,
            )

            logger = DASTLogger()
            logger.log_tag_event("test_tag", {"test": True}, "INFO")

            if len(logger.event_logs) == 0:
                return {"success": False, "error": "Logger did not record event"}

            # Test partner SDK functionality
            from core.interfaces.as_agent.sys.dast.partner_sdk import (
                PartnerSDK,
            )

            sdk = PartnerSDK()
            partner_result = sdk.receive_partner_input(
                "test_source", ["tag1"], {"meta": "data"}
            )

            if not isinstance(partner_result, dict):
                return {"success": False, "error": "PartnerSDK did not return dict"}

            return True

        except Exception as e:
            return {"success": False, "error": str(e)}

    def test_file_structure(self):
        """Test that all required files exist"""
        required_files = [
            "core/interfaces/as_agent/sys/dast/aggregator.py",
            "core/interfaces/as_agent/sys/dast/dast_logger.py",
            "core/interfaces/as_agent/sys/dast/partner_sdk.py",
            "core/interfaces/as_agent/sys/dast/store.py",
            "dast/integration/dast_integration_hub.py",
            "TASK_2A_COMPLETION_STATUS.md",
            "test_task_2a_simple.py",
        ]

        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)

        if missing_files:
            return {"success": False, "error": f"Missing files: {missing_files}"}

        return True

    def test_hub_integration_readiness(self):
        """Test hub integration framework readiness"""
        try:
            # Check if hub file exists and has basic structure
            hub_file = Path("dast/integration/dast_integration_hub.py")
            if not hub_file.exists():
                return {"success": False, "error": "Hub file does not exist"}

            # Read hub file and check for key components
            hub_content = hub_file.read_text()
            required_elements = [
                "class DASTIntegrationHub",
                "def register_component",
                "def get_dast_integration_hub",
                "_dast_integration_hub",
            ]

            for element in required_elements:
                if element not in hub_content:
                    return {
                        "success": False,
                        "error": f"Missing hub element: {element}",
                    }

            return True

        except Exception as e:
            return {"success": False, "error": str(e)}

    def test_documentation_completeness(self):
        """Test documentation files exist and have content"""
        doc_files = [
            "TASK_2A_COMPLETION_STATUS.md",
            "SYSTEM_DOCUMENTATION_AND_TEST_RESULTS.md",
        ]

        for doc_file in doc_files:
            path = Path(doc_file)
            if not path.exists():
                return {"success": False, "error": f"Missing documentation: {doc_file}"}

            content = path.read_text()
            if len(content) < 100:  # Minimum content check
                return {
                    "success": False,
                    "error": f"Documentation too short: {doc_file}",
                }

        return True

    def run_all_tests(self):
        """Run complete test suite"""
        print("🔬 Starting LUKHAS AGI Comprehensive System Test Suite")
        print("=" * 60)

        # Component Tests
        self.run_test(
            "Component",
            "DAST Component Instantiation",
            self.test_dast_component_instantiation,
        )
        self.run_test(
            "Component",
            "Singleton Pattern Implementation",
            self.test_dast_singleton_patterns,
        )
        self.run_test(
            "Component", "DAST Basic Functionality", self.test_dast_functionality
        )

        # Compatibility Tests
        self.run_test(
            "Compatibility",
            "Legacy Function Availability",
            self.test_legacy_function_compatibility,
        )

        # Infrastructure Tests
        self.run_test(
            "Infrastructure", "File Structure Validation", self.test_file_structure
        )
        self.run_test(
            "Infrastructure",
            "Hub Integration Readiness",
            self.test_hub_integration_readiness,
        )
        self.run_test(
            "Infrastructure",
            "Documentation Completeness",
            self.test_documentation_completeness,
        )

        # Generate test report
        self.generate_test_report()

    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)

        # Overall statistics
        total = self.test_results["total_tests"]
        passed = self.test_results["passed_tests"]
        failed = self.test_results["failed_tests"]
        success_rate = (passed / total * 100) if total > 0 else 0

        print(f"Total Tests Run: {total}")
        print(f"Tests Passed: {passed}")
        print(f"Tests Failed: {failed}")
        print(f"Success Rate: {success_rate:.1f}%")

        # Category breakdown
        print("\n📋 CATEGORY BREAKDOWN:")
        for category, stats in self.test_results["test_categories"].items():
            cat_total = stats["passed"] + stats["failed"]
            cat_rate = (stats["passed"] / cat_total * 100) if cat_total > 0 else 0
            print(f"  {category}: {stats['passed']}/{cat_total} ({cat_rate:.1f}%)")

        # Detailed results
        print("\n🔍 DETAILED RESULTS:")
        for result in self.test_results["detailed_results"]:
            print(f"  {result['status']} {result['category']}: {result['test_name']}")
            if result["error"]:
                print(f"    ⚠️  {result['error']}")

        # Save results to file
        with open("test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)

        print("\n💾 Detailed results saved to: test_results.json")

        # Final status
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! System is fully operational.")
        else:
            print(f"\n⚠️  {failed} test(s) failed. See details above.")

        return self.test_results


def main():
    """Main test execution"""
    test_suite = SystemTestSuite()
    results = test_suite.run_all_tests()

    # Return appropriate exit code
    return 0 if results and results["failed_tests"] == 0 else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
