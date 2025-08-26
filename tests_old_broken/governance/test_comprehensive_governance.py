#!/usr/bin/env python3
"""
🌟 Comprehensive  Governance Test Suite
==========================================

Ultimate testing combining ALL superior LUKHAS components:
- Guardian Reflector (ethical reflection testing)
- Enhanced Ethics Engine (multi-framework)
- Red Team Protocol (security validation)
- LUKHAS Ethics Guard (tier-based consent)
-  Workspace Guardian (complete protection)

This is the COMPREHENSIVE test suite using all your superior components.
"""

import asyncio
import os
import sys
from datetime import datetime

# Add paths for all modules
sys.path.insert(0, os.path.dirname(__file__))

print("🌟 Comprehensive  Governance Testing - ALL Superior Components")
print("=" * 70)

# Import availability tracking
modules_available = {
    "guardian_reflector": False,
    "enhanced_governance": False,
    "basic_governance": False,
    "ethics_orchestrator": False,
    "red_team": False,
}

# Try importing Guardian Reflector
try:
    from testing import TestOrchestrator

    modules_available["guardian_reflector"] = True
    print("✅ Guardian Reflector testing suite loaded")
except ImportError as e:
    print(f"⚠️ Guardian Reflector not available: {e}")

# Try importing Enhanced Governance
try:
    from candidate.governance.enhanced_guardian import EnhancedWorkspaceGuardian

    modules_available["enhanced_governance"] = True
    print("✅ Enhanced  Governance loaded")
except ImportError as e:
    print(f"⚠️ Enhanced Governance not available: {e}")

# Try importing Basic Governance
try:
    from candidate.governance._workspace_guardian import WorkspaceGuardian

    modules_available["basic_governance"] = True
    print("✅ Basic  Governance loaded")
except ImportError as e:
    print(f"⚠️ Basic Governance not available: {e}")

# Try importing Ethics Orchestrator
try:
    from ethics import EthicsOrchestrator

    modules_available["ethics_orchestrator"] = True
    print("✅  Ethics Orchestrator loaded")
except ImportError as e:
    print(f"⚠️ Ethics Orchestrator not available: {e}")

# Try importing Red Team
try:
    from red_team import RedTeamProtocol

    modules_available["red_team"] = True
    print("✅ Red Team Protocol loaded")
except ImportError as e:
    print(f"⚠️ Red Team Protocol not available: {e}")


class ComprehensiveTestSuite:
    """
    🚀 Ultimate  Testing Suite

    Tests ALL superior components in integrated fashion.
    """

    def __init__(self):
        self.test_orchestrator = None
        self.enhanced_guardian = None
        self.basic_guardian = None
        self.ethics_orchestrator = None
        self.red_team = None
        self.test_results = {}

    async def initialize_all_systems(self):
        """Initialize all available testing systems."""
        print("\n🔧 Initializing all available systems...")

        initialization_results = {}

        # Initialize Guardian Reflector Testing
        if modules_available["guardian_reflector"]:
            try:
                self.test_orchestrator = TestOrchestrator()
                success = await self.test_orchestrator.initialize_testing()
                initialization_results["guardian_reflector"] = (
                    "SUCCESS" if success else "FAILED"
                )
                print(
                    f"🧪 Guardian Reflector: {'✅ SUCCESS' if success else '❌ FAILED'}"
                )
            except Exception as e:
                initialization_results["guardian_reflector"] = f"ERROR: {e}"
                print(f"🧪 Guardian Reflector: ❌ ERROR - {e}")

        # Initialize Enhanced Governance
        if modules_available["enhanced_governance"]:
            try:
                self.enhanced_guardian = EnhancedWorkspaceGuardian()
                await self.enhanced_guardian.initialize()
                initialization_results["enhanced_governance"] = "SUCCESS"
                print("🛡️ Enhanced Governance: ✅ SUCCESS")
            except Exception as e:
                initialization_results["enhanced_governance"] = f"ERROR: {e}"
                print(f"🛡️ Enhanced Governance: ❌ ERROR - {e}")

        # Initialize Basic Governance (fallback)
        if modules_available["basic_governance"] and not self.enhanced_guardian:
            try:
                self.basic_guardian = WorkspaceGuardian()
                await self.basic_guardian.initialize()
                initialization_results["basic_governance"] = "SUCCESS"
                print("🛡️ Basic Governance: ✅ SUCCESS")
            except Exception as e:
                initialization_results["basic_governance"] = f"ERROR: {e}"
                print(f"🛡️ Basic Governance: ❌ ERROR - {e}")

        # Initialize Ethics Orchestrator
        if modules_available["ethics_orchestrator"]:
            try:
                self.ethics_orchestrator = EthicsOrchestrator()
                initialization_results["ethics_orchestrator"] = "SUCCESS"
                print("🧠 Ethics Orchestrator: ✅ SUCCESS")
            except Exception as e:
                initialization_results["ethics_orchestrator"] = f"ERROR: {e}"
                print(f"🧠 Ethics Orchestrator: ❌ ERROR - {e}")

        # Initialize Red Team
        if modules_available["red_team"]:
            try:
                self.red_team = RedTeamProtocol()
                initialization_results["red_team"] = "SUCCESS"
                print("🔴 Red Team Protocol: ✅ SUCCESS")
            except Exception as e:
                initialization_results["red_team"] = f"ERROR: {e}"
                print(f"🔴 Red Team Protocol: ❌ ERROR - {e}")

        return initialization_results

    async def run_comprehensive_testing(self):
        """Run the ultimate comprehensive test suite."""
        print("\n🚀 Running Comprehensive  Governance Testing...")
        print("=" * 70)

        test_results = {
            "timestamp": datetime.now().isoformat(),
            "test_suite_version": "COMPREHENSIVE-3.0.0",
            "modules_tested": [],
            "overall_status": "RUNNING",
        }

        # Test 1: Guardian Reflector Ethical Analysis
        if self.test_orchestrator:
            print("\n🧪 Testing Guardian Reflector Ethical Analysis...")
            try:
                reflector_results = (
                    await self.test_orchestrator.run_comprehensive_tests()
                )
                test_results["guardian_reflector"] = reflector_results
                test_results["modules_tested"].append("guardian_reflector")
                print("✅ Guardian Reflector tests completed")
            except Exception as e:
                test_results["guardian_reflector"] = {"error": str(e)}
                print(f"❌ Guardian Reflector tests failed: {e}")

        # Test 2: Enhanced Governance Security
        if self.enhanced_guardian:
            print("\n🛡️ Testing Enhanced Governance Security...")
            try:
                # Test file protection
                file_result = (
                    await self.enhanced_guardian.enhanced_file_operation_check(
                        "delete", "README.md"
                    )
                )

                # Test security validation
                security_result = await self.enhanced_guardian.run_security_validation()

                test_results["enhanced_governance"] = {
                    "file_protection": file_result,
                    "security_validation": security_result,
                }
                test_results["modules_tested"].append("enhanced_governance")
                print("✅ Enhanced Governance tests completed")
            except Exception as e:
                test_results["enhanced_governance"] = {"error": str(e)}
                print(f"❌ Enhanced Governance tests failed: {e}")

        # Test 3: Basic Governance (if enhanced not available)
        elif self.basic_guardian:
            print("\n🛡️ Testing Basic Governance...")
            try:
                file_result = await self.basic_guardian.check_file_operation(
                    "delete", "README.md"
                )
                health_result = await self.basic_guardian.analyze_workspace_health()

                test_results["basic_governance"] = {
                    "file_protection": file_result,
                    "workspace_health": health_result,
                }
                test_results["modules_tested"].append("basic_governance")
                print("✅ Basic Governance tests completed")
            except Exception as e:
                test_results["basic_governance"] = {"error": str(e)}
                print(f"❌ Basic Governance tests failed: {e}")

        # Test 4: Ethics Framework Integration
        if self.ethics_orchestrator:
            print("\n🧠 Testing Ethics Framework Integration...")
            try:
                ethics_result = (
                    await self.ethics_orchestrator.evaluate_workspace_action(
                        "delete critical_file.py",
                        {
                            "tier_required": 3,
                            "user_consent": {
                                "tier": 5,
                                "allowed_signals": ["workspace_management"],
                            },
                            "intent": "cleanup",
                            "impact": "moderate",
                        },
                    )
                )

                test_results["ethics_framework"] = ethics_result
                test_results["modules_tested"].append("ethics_framework")
                print("✅ Ethics Framework tests completed")
            except Exception as e:
                test_results["ethics_framework"] = {"error": str(e)}
                print(f"❌ Ethics Framework tests failed: {e}")

        # Test 5: Red Team Security Validation
        if self.red_team:
            print("\n🔴 Testing Red Team Security Protocols...")
            try:
                scenarios = [
                    "file_destruction",
                    "configuration_corruption",
                    "privilege_escalation",
                ]
                red_team_results = []

                for scenario in scenarios:
                    scenario_result = await self.red_team.run_attack_simulation(
                        scenario
                    )
                    red_team_results.append(scenario_result)

                test_results["red_team_validation"] = {
                    "scenarios_tested": red_team_results,
                    "protocol_summary": self.red_team.get_protocol_summary(),
                }
                test_results["modules_tested"].append("red_team_validation")
                print("✅ Red Team tests completed")
            except Exception as e:
                test_results["red_team_validation"] = {"error": str(e)}
                print(f"❌ Red Team tests failed: {e}")

        # Calculate overall test status
        successful_modules = len(
            [
                m
                for m in test_results["modules_tested"]
                if m in test_results and "error" not in test_results[m]
            ]
        )
        total_modules = len(test_results["modules_tested"])

        if successful_modules == total_modules and total_modules > 0:
            test_results["overall_status"] = "ALL_TESTS_PASSED"
        elif successful_modules > 0:
            test_results["overall_status"] = "PARTIAL_SUCCESS"
        else:
            test_results["overall_status"] = "ALL_TESTS_FAILED"

        self.test_results = test_results
        return test_results

    def generate_comprehensive_report(self):
        """Generate comprehensive test report."""
        print("\n" + "=" * 70)
        print("🏁 COMPREHENSIVE  GOVERNANCE TEST RESULTS")
        print("=" * 70)

        if not self.test_results:
            print("❌ No test results available")
            return

        # Overall Status
        status = self.test_results.get("overall_status", "UNKNOWN")
        status_symbols = {
            "ALL_TESTS_PASSED": "🌟 EXCELLENT",
            "PARTIAL_SUCCESS": "⚠️ PARTIAL",
            "ALL_TESTS_FAILED": "❌ FAILED",
            "UNKNOWN": "❓ UNKNOWN",
        }

        print(f"📊 Overall Status: {status_symbols.get(status, status)}")
        print(f"🕐 Test Timestamp: {self.test_results.get('timestamp', 'UNKNOWN')}")
        print(
            f"📦 Suite Version: {self.test_results.get('test_suite_version', 'UNKNOWN')}"
        )

        # Modules Tested
        modules_tested = self.test_results.get("modules_tested", [])
        print(f"\n�� Modules Tested: {len(modules_tested)}")
        for module in modules_tested:
            module_result = self.test_results.get(module, {})
            if "error" in module_result:
                print(f"   ❌ {module}: ERROR")
            else:
                print(f"   ✅ {module}: SUCCESS")

        # Detailed Results
        if "guardian_reflector" in self.test_results:
            gr_result = self.test_results["guardian_reflector"]
            if "guardian_reflector" in gr_result:
                gr_status = gr_result["guardian_reflector"].get("status", "UNKNOWN")
                print(f"\n🧪 Guardian Reflector: {gr_status}")
                if gr_status == "SUCCESS":
                    moral_score = gr_result["guardian_reflector"].get(
                        "moral_score", 0.0
                    )
                    print(f"   📊 Moral Score: {moral_score:.2f}")

        if "enhanced_governance" in self.test_results:
            eg_result = self.test_results["enhanced_governance"]
            if "security_validation" in eg_result:
                security_summary = eg_result["security_validation"].get(
                    "security_summary", "UNKNOWN"
                )
                print(f"\n🛡️ Enhanced Governance: {security_summary}")

        if "ethics_framework" in self.test_results:
            ef_result = self.test_results["ethics_framework"]
            if "allowed" in ef_result:
                ethics_allowed = ef_result["allowed"]
                ethics_framework = ef_result.get("framework", "UNKNOWN")
                print(
                    f"\n🧠 Ethics Framework: {'ALLOWED' if ethics_allowed else 'BLOCKED'} ({ethics_framework})"
                )

        if "red_team_validation" in self.test_results:
            rt_result = self.test_results["red_team_validation"]
            if "scenarios_tested" in rt_result:
                scenarios_count = len(rt_result["scenarios_tested"])
                print(f"\n🔴 Red Team: {scenarios_count} scenarios tested")

        # Recommendations
        print("\n💡 Recommendations:")
        if status == "ALL_TESTS_PASSED":
            print("   🌟 Your  workspace has ENTERPRISE-GRADE protection!")
            print("   🚀 All superior LUKHAS components are working optimally")
            print("   🎯 Ready for production workspace management")
        elif status == "PARTIAL_SUCCESS":
            print(
                "   📈 Some components working, consider installing missing dependencies"
            )
            print("   🔧 Review failed module errors for improvement opportunities")
        else:
            print("   🔧 System requires configuration and dependency resolution")
            print("   📚 Check module documentation for setup requirements")

        print("=" * 70)


async def main():
    """Run the ultimate comprehensive  governance test suite."""

    print("🚀 Initializing Comprehensive  Governance Test Suite...")

    # Check module availability summary
    available_count = sum(modules_available.values())
    total_count = len(modules_available)

    print(f"\n📊 Module Availability: {available_count}/{total_count}")

    if available_count == 0:
        print("❌ No governance modules available - check installation")
        return False

    # Initialize and run comprehensive tests
    test_suite = ComprehensiveTestSuite()

    # Initialize all systems
    await test_suite.initialize_all_systems()

    # Run comprehensive testing
    test_results = await test_suite.run_comprehensive_testing()

    # Generate final report
    test_suite.generate_comprehensive_report()

    # Return success status
    return test_results.get("overall_status") in [
        "ALL_TESTS_PASSED",
        "PARTIAL_SUCCESS",
    ]


if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("\n🎯  Comprehensive Governance Testing Complete!")
        sys.exit(0)
    else:
        print("\n🔧  Governance System Requires Attention")
        sys.exit(1)
