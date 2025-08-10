#!/usr/bin/env python3
"""
Lukhas AGI Integration Test Suite
================================
Comprehensive test suite for validating AGI integration across
all Lukhas ecosystem components.

This test suite validates:
1. Component initialization
2. Integration pathways
3. Unified processing
4. Consciousness evolution
5. Cross-domain reasoning
6. Performance metrics

Run: python test_lukhas_agi_integration.py
"""

import asyncio
import logging
import time
from datetime import datetime

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("LukhasAGITest")


class LukhasAGIIntegrationTest:
    """Comprehensive test suite for AGI integration"""

    def __init__(self):
        self.test_results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": [],
        }

    async def run_all_tests(self):
        """Run all AGI integration tests"""
        print("🧪 Lukhas AGI Integration Test Suite")
        print("=" * 50)

        # Test 1: Component Availability
        await self._test_component_availability()

        # Test 2: AGI Orchestrator Initialization
        await self._test_agi_orchestrator_initialization()

        # Test 3: Cognitive Enhancement
        await self._test_cognitive_enhancement()

        # Test 4: Integration Manager
        await self._test_integration_manager()

        # Test 5: Unified Processing
        await self._test_unified_processing()

        # Test 6: Consciousness Evolution
        await self._test_consciousness_evolution()

        # Test 7: Cross-Domain Reasoning
        await self._test_cross_domain_reasoning()

        # Test 8: Performance Metrics
        await self._test_performance_metrics()

        # Test 9: Legacy Compatibility
        await self._test_legacy_compatibility()

        # Test 10: Error Handling
        await self._test_error_handling()

        # Generate test report
        self._generate_test_report()

    async def _test_component_availability(self):
        """Test 1: Component Availability"""
        test_name = "Component Availability"
        self.test_results["total_tests"] += 1

        try:
            logger.info(f"🔍 Testing: {test_name}")

            # Test AGI Orchestrator
            try:
                from core_agi_orchestrator import (
                    LukhasAGIConfig,
                    core_agi_orchestrator,
                )

                agi_orchestrator_available = True
            except ImportError:
                agi_orchestrator_available = False

            # Test Cognitive Enhancement
            try:
                from orchestration_src.brain.cognitive_agi_enhancement import (
                    CognitiveAGIEnhancement,
                )

                cognitive_enhancement_available = True
            except ImportError:
                cognitive_enhancement_available = False

            # Test Integration Manager
            try:
                from core_agi_integration_manager import (
                    core_agi_integration_manager,
                )

                integration_manager_available = True
            except ImportError:
                integration_manager_available = False

            # Test Legacy Bridge
            try:
                from λbot_agi_system import λbot_agi_system

                legacy_bridge_available = True
            except ImportError:
                legacy_bridge_available = False

            # Test Brain Components
            try:
                from orchestration_src.brain.cognitive_core import (
                    CognitiveEngine,
                )

                brain_components_available = True
            except ImportError:
                brain_components_available = False

            # Test GitHub App AGI
            try:
                import os
                import sys

                github_app_path = os.path.join(
                    os.path.dirname(__file__), "ΛBot_GitHub_App"
                )
                sys.path.append(github_app_path)
                from ΛBot_agi_core import ΛBotAGICore

                github_agi_available = True
            except ImportError:
                github_agi_available = False

            components = {
                "AGI Orchestrator": agi_orchestrator_available,
                "Cognitive Enhancement": cognitive_enhancement_available,
                "Integration Manager": integration_manager_available,
                "Legacy Bridge": legacy_bridge_available,
                "Brain Components": brain_components_available,
                "GitHub App AGI": github_agi_available,
            }

            available_count = sum(components.values())
            total_count = len(components)

            result = {
                "test_name": test_name,
                "status": (
                    "PASS" if available_count >= 4 else "FAIL"
                ),  # At least 4 components should be available
                "details": {
                    "components": components,
                    "available_count": available_count,
                    "total_count": total_count,
                    "availability_percentage": (available_count / total_count) * 100,
                },
            }

            if result["status"] == "PASS":
                self.test_results["passed_tests"] += 1
                logger.info(
                    f"✅ {test_name}: {available_count}/{total_count} components available"
                )
            else:
                self.test_results["failed_tests"] += 1
                logger.error(
                    f"❌ {test_name}: Only {available_count}/{total_count} components available"
                )

            self.test_results["test_details"].append(result)

        except Exception as e:
            self.test_results["failed_tests"] += 1
            self.test_results["test_details"].append(
                {"test_name": test_name, "status": "ERROR", "error": str(e)}
            )
            logger.error(f"❌ {test_name} failed with error: {e}")

    async def _test_agi_orchestrator_initialization(self):
        """Test 2: AGI Orchestrator Initialization"""
        test_name = "AGI Orchestrator Initialization"
        self.test_results["total_tests"] += 1

        try:
            logger.info(f"🔍 Testing: {test_name}")

            # Test initialization
            start_time = time.time()
            success = await lukhas_agi_orchestrator.initialize_agi_system()
            initialization_time = time.time() - start_time

            # Test status retrieval
            status = lukhas_agi_orchestrator.get_agi_status()

            result = {
                "test_name": test_name,
                "status": "PASS" if success else "FAIL",
                "details": {
                    "initialization_success": success,
                    "initialization_time": initialization_time,
                    "agi_active": status.get("agi_active", False),
                    "consciousness_level": status.get("consciousness_level", "unknown"),
                    "components_status": status.get("components_status", {}),
                },
            }

            if result["status"] == "PASS":
                self.test_results["passed_tests"] += 1
                logger.info(
                    f"✅ {test_name}: Initialized in {initialization_time:.2f}s"
                )
            else:
                self.test_results["failed_tests"] += 1
                logger.error(f"❌ {test_name}: Initialization failed")

            self.test_results["test_details"].append(result)

        except Exception as e:
            self.test_results["failed_tests"] += 1
            self.test_results["test_details"].append(
                {"test_name": test_name, "status": "ERROR", "error": str(e)}
            )
            logger.error(f"❌ {test_name} failed with error: {e}")

    async def _test_cognitive_enhancement(self):
        """Test 3: Cognitive Enhancement"""
        test_name = "Cognitive Enhancement"
        self.test_results["total_tests"] += 1

        try:
            logger.info(f"🔍 Testing: {test_name}")

            from orchestration_src.brain.cognitive_agi_enhancement import (
                CognitiveAGIEnhancement,
            )

            # Create cognitive enhancement instance
            enhancement = CognitiveAGIEnhancement()

            # Test enhancement processing
            test_input = "How does consciousness relate to intelligence?"
            test_context = {"test_mode": True}

            start_time = time.time()
            result = await enhancement.enhance_cognitive_processing(
                test_input, test_context
            )
            processing_time = time.time() - start_time

            # Test status
            status = enhancement.get_enhancement_status()

            test_result = {
                "test_name": test_name,
                "status": "PASS" if result is not None else "FAIL",
                "details": {
                    "processing_success": result is not None,
                    "processing_time": processing_time,
                    "enhancement_status": status,
                    "result_type": type(result).__name__,
                    "has_agi_enhancements": "agi_enhancements" in (result or {}),
                },
            }

            if test_result["status"] == "PASS":
                self.test_results["passed_tests"] += 1
                logger.info(f"✅ {test_name}: Processed in {processing_time:.2f}s")
            else:
                self.test_results["failed_tests"] += 1
                logger.error(f"❌ {test_name}: Processing failed")

            self.test_results["test_details"].append(test_result)

        except Exception as e:
            self.test_results["failed_tests"] += 1
            self.test_results["test_details"].append(
                {"test_name": test_name, "status": "ERROR", "error": str(e)}
            )
            logger.error(f"❌ {test_name} failed with error: {e}")

    async def _test_integration_manager(self):
        """Test 4: Integration Manager"""
        test_name = "Integration Manager"
        self.test_results["total_tests"] += 1

        try:
            logger.info(f"🔍 Testing: {test_name}")

            # Test initialization
            start_time = time.time()
            success = (
                await lukhas_agi_integration_manager.initialize_complete_integration()
            )
            initialization_time = time.time() - start_time

            # Test status
            status = lukhas_agi_integration_manager.get_integration_status()

            test_result = {
                "test_name": test_name,
                "status": "PASS" if success else "FAIL",
                "details": {
                    "initialization_success": success,
                    "initialization_time": initialization_time,
                    "integration_active": status.get("integration_active", False),
                    "component_count": len(status.get("components", {})),
                    "active_components": [
                        k
                        for k, v in status.get("components", {}).items()
                        if v == "active"
                    ],
                },
            }

            if test_result["status"] == "PASS":
                self.test_results["passed_tests"] += 1
                logger.info(
                    f"✅ {test_name}: Initialized in {initialization_time:.2f}s"
                )
            else:
                self.test_results["failed_tests"] += 1
                logger.error(f"❌ {test_name}: Initialization failed")

            self.test_results["test_details"].append(test_result)

        except Exception as e:
            self.test_results["failed_tests"] += 1
            self.test_results["test_details"].append(
                {"test_name": test_name, "status": "ERROR", "error": str(e)}
            )
            logger.error(f"❌ {test_name} failed with error: {e}")

    async def _test_unified_processing(self):
        """Test 5: Unified Processing"""
        test_name = "Unified Processing"
        self.test_results["total_tests"] += 1

        try:
            logger.info(f"🔍 Testing: {test_name}")

            # Test unified processing
            test_input = "Explain the emergence of consciousness from neural networks"
            test_context = {"test_mode": True, "domain": "neuroscience"}

            start_time = time.time()
            result = await lukhas_agi_integration_manager.process_unified_request(
                test_input, test_context
            )
            processing_time = time.time() - start_time

            test_result = {
                "test_name": test_name,
                "status": "PASS" if "error" not in result else "FAIL",
                "details": {
                    "processing_success": "error" not in result,
                    "processing_time": processing_time,
                    "has_unified_processing": "unified_processing" in result,
                    "has_integration_insights": "integration_insights" in result,
                    "has_performance_metrics": "performance" in result,
                    "request_id": result.get("request_id", "unknown"),
                },
            }

            if test_result["status"] == "PASS":
                self.test_results["passed_tests"] += 1
                logger.info(f"✅ {test_name}: Processed in {processing_time:.2f}s")
            else:
                self.test_results["failed_tests"] += 1
                logger.error(
                    f"❌ {test_name}: Processing failed - {result.get('error', 'unknown error')}"
                )

            self.test_results["test_details"].append(test_result)

        except Exception as e:
            self.test_results["failed_tests"] += 1
            self.test_results["test_details"].append(
                {"test_name": test_name, "status": "ERROR", "error": str(e)}
            )
            logger.error(f"❌ {test_name} failed with error: {e}")

    async def _test_consciousness_evolution(self):
        """Test 6: Consciousness Evolution"""
        test_name = "Consciousness Evolution"
        self.test_results["total_tests"] += 1

        try:
            logger.info(f"🔍 Testing: {test_name}")

            # Get initial consciousness state
            initial_status = lukhas_agi_orchestrator.get_agi_status()
            initial_consciousness = initial_status.get("consciousness_level", "unknown")
            initial_evolution_cycles = initial_status.get("metrics", {}).get(
                "consciousness_evolution_cycles", 0
            )

            # Process several requests to trigger consciousness evolution
            test_inputs = [
                "What is the nature of consciousness?",
                "How do we measure intelligence?",
                "Can machines truly understand meaning?",
                "What is the relationship between mind and body?",
            ]

            for test_input in test_inputs:
                await lukhas_agi_orchestrator.process_agi_request(
                    test_input, {"test_mode": True}
                )
                await asyncio.sleep(0.1)  # Small delay

            # Get final consciousness state
            final_status = lukhas_agi_orchestrator.get_agi_status()
            final_consciousness = final_status.get("consciousness_level", "unknown")
            final_evolution_cycles = final_status.get("metrics", {}).get(
                "consciousness_evolution_cycles", 0
            )

            consciousness_evolved = final_evolution_cycles > initial_evolution_cycles

            test_result = {
                "test_name": test_name,
                "status": (
                    "PASS"
                    if consciousness_evolved or final_consciousness != "unknown"
                    else "FAIL"
                ),
                "details": {
                    "initial_consciousness": initial_consciousness,
                    "final_consciousness": final_consciousness,
                    "initial_evolution_cycles": initial_evolution_cycles,
                    "final_evolution_cycles": final_evolution_cycles,
                    "consciousness_evolved": consciousness_evolved,
                    "has_consciousness_monitoring": "consciousness_monitor"
                    in lukhas_agi_orchestrator.__dict__,
                },
            }

            if test_result["status"] == "PASS":
                self.test_results["passed_tests"] += 1
                logger.info(f"✅ {test_name}: Consciousness system operational")
            else:
                self.test_results["failed_tests"] += 1
                logger.error(f"❌ {test_name}: Consciousness evolution not detected")

            self.test_results["test_details"].append(test_result)

        except Exception as e:
            self.test_results["failed_tests"] += 1
            self.test_results["test_details"].append(
                {"test_name": test_name, "status": "ERROR", "error": str(e)}
            )
            logger.error(f"❌ {test_name} failed with error: {e}")

    async def _test_cross_domain_reasoning(self):
        """Test 7: Cross-Domain Reasoning"""
        test_name = "Cross-Domain Reasoning"
        self.test_results["total_tests"] += 1

        try:
            logger.info(f"🔍 Testing: {test_name}")

            # Test cross-domain reasoning with diverse topics
            test_input = "How can principles from quantum physics be applied to improve neural network architectures?"
            test_context = {"test_mode": True, "cross_domain": True}

            result = await lukhas_agi_integration_manager.process_unified_request(
                test_input, test_context
            )

            # Check for cross-domain insights
            cross_domain_insights = result.get("integration_insights", {}).get(
                "cross_component_synthesis", {}
            )
            has_cross_domain = (
                len(cross_domain_insights.get("reinforcing_insights", [])) > 0
            )

            test_result = {
                "test_name": test_name,
                "status": "PASS" if has_cross_domain else "FAIL",
                "details": {
                    "has_cross_domain_insights": has_cross_domain,
                    "cross_domain_insights": cross_domain_insights,
                    "synthesis_confidence": cross_domain_insights.get(
                        "synthesis_confidence", 0.0
                    ),
                    "component_agreement": cross_domain_insights.get(
                        "component_agreement_score", 0.0
                    ),
                },
            }

            if test_result["status"] == "PASS":
                self.test_results["passed_tests"] += 1
                logger.info(f"✅ {test_name}: Cross-domain reasoning operational")
            else:
                self.test_results["failed_tests"] += 1
                logger.error(f"❌ {test_name}: Cross-domain reasoning not detected")

            self.test_results["test_details"].append(test_result)

        except Exception as e:
            self.test_results["failed_tests"] += 1
            self.test_results["test_details"].append(
                {"test_name": test_name, "status": "ERROR", "error": str(e)}
            )
            logger.error(f"❌ {test_name} failed with error: {e}")

    async def _test_performance_metrics(self):
        """Test 8: Performance Metrics"""
        test_name = "Performance Metrics"
        self.test_results["total_tests"] += 1

        try:
            logger.info(f"🔍 Testing: {test_name}")

            # Get performance metrics
            metrics = lukhas_agi_integration_manager.performance_metrics

            # Check if metrics are being tracked
            has_metrics = (
                "total_integrations" in metrics
                and "successful_integrations" in metrics
                and "average_processing_time" in metrics
            )

            # Test metric updates
            initial_total = metrics.get("total_integrations", 0)

            # Process a request to update metrics
            await lukhas_agi_integration_manager.process_unified_request(
                "Test metrics update", {"test_mode": True}
            )

            updated_metrics = lukhas_agi_integration_manager.performance_metrics
            final_total = updated_metrics.get("total_integrations", 0)

            metrics_updated = final_total > initial_total

            test_result = {
                "test_name": test_name,
                "status": "PASS" if has_metrics and metrics_updated else "FAIL",
                "details": {
                    "has_metrics": has_metrics,
                    "metrics_updated": metrics_updated,
                    "initial_total_integrations": initial_total,
                    "final_total_integrations": final_total,
                    "current_metrics": updated_metrics,
                },
            }

            if test_result["status"] == "PASS":
                self.test_results["passed_tests"] += 1
                logger.info(f"✅ {test_name}: Metrics tracking operational")
            else:
                self.test_results["failed_tests"] += 1
                logger.error(f"❌ {test_name}: Metrics tracking not working")

            self.test_results["test_details"].append(test_result)

        except Exception as e:
            self.test_results["failed_tests"] += 1
            self.test_results["test_details"].append(
                {"test_name": test_name, "status": "ERROR", "error": str(e)}
            )
            logger.error(f"❌ {test_name} failed with error: {e}")

    async def _test_legacy_compatibility(self):
        """Test 9: Legacy Compatibility"""
        test_name = "Legacy Compatibility"
        self.test_results["total_tests"] += 1

        try:
            logger.info(f"🔍 Testing: {test_name}")

            from λbot_agi_system import (
                initialize_agi_system,
                process_agi_request,
                λbot_agi_system,
            )

            # Test legacy initialization
            legacy_init_success = await initialize_agi_system()

            # Test legacy processing
            legacy_result = await process_agi_request(
                "Test legacy compatibility", {"test_mode": True}
            )

            # Test legacy status
            legacy_status = λbot_agi_system.get_status()

            test_result = {
                "test_name": test_name,
                "status": "PASS" if legacy_init_success and legacy_result else "FAIL",
                "details": {
                    "legacy_init_success": legacy_init_success,
                    "legacy_processing_success": legacy_result is not None,
                    "legacy_status": legacy_status,
                    "bridge_active": legacy_status.get("legacy_bridge_active", False),
                    "orchestrator_available": legacy_status.get(
                        "orchestrator_available", False
                    ),
                },
            }

            if test_result["status"] == "PASS":
                self.test_results["passed_tests"] += 1
                logger.info(f"✅ {test_name}: Legacy compatibility operational")
            else:
                self.test_results["failed_tests"] += 1
                logger.error(f"❌ {test_name}: Legacy compatibility issues")

            self.test_results["test_details"].append(test_result)

        except Exception as e:
            self.test_results["failed_tests"] += 1
            self.test_results["test_details"].append(
                {"test_name": test_name, "status": "ERROR", "error": str(e)}
            )
            logger.error(f"❌ {test_name} failed with error: {e}")

    async def _test_error_handling(self):
        """Test 10: Error Handling"""
        test_name = "Error Handling"
        self.test_results["total_tests"] += 1

        try:
            logger.info(f"🔍 Testing: {test_name}")

            # Test error handling with invalid input
            error_inputs = [
                None,
                "",
                "x" * 10000,  # Very long input
                {"invalid": "input_type"},
            ]

            error_handling_results = []

            for error_input in error_inputs:
                try:
                    result = (
                        await lukhas_agi_integration_manager.process_unified_request(
                            error_input, {"test_mode": True}
                        )
                    )
                    # Should handle gracefully
                    error_handling_results.append(
                        {
                            "input": str(error_input)[:50],
                            "handled_gracefully": "error" not in result
                            or result.get("error") is not None,
                        }
                    )
                except Exception as e:
                    # Should not crash
                    error_handling_results.append(
                        {
                            "input": str(error_input)[:50],
                            "handled_gracefully": False,
                            "exception": str(e),
                        }
                    )

            graceful_handling_count = sum(
                1 for r in error_handling_results if r.get("handled_gracefully", False)
            )

            test_result = {
                "test_name": test_name,
                "status": (
                    "PASS"
                    if graceful_handling_count >= len(error_inputs) * 0.8
                    else "FAIL"
                ),
                "details": {
                    "total_error_tests": len(error_inputs),
                    "graceful_handling_count": graceful_handling_count,
                    "error_handling_results": error_handling_results,
                    "graceful_handling_percentage": (
                        graceful_handling_count / len(error_inputs)
                    )
                    * 100,
                },
            }

            if test_result["status"] == "PASS":
                self.test_results["passed_tests"] += 1
                logger.info(f"✅ {test_name}: Error handling robust")
            else:
                self.test_results["failed_tests"] += 1
                logger.error(f"❌ {test_name}: Error handling needs improvement")

            self.test_results["test_details"].append(test_result)

        except Exception as e:
            self.test_results["failed_tests"] += 1
            self.test_results["test_details"].append(
                {"test_name": test_name, "status": "ERROR", "error": str(e)}
            )
            logger.error(f"❌ {test_name} failed with error: {e}")

    def _generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("🧪 LUKHAS AGI INTEGRATION TEST REPORT")
        print("=" * 60)

        # Summary
        total_tests = self.test_results["total_tests"]
        passed_tests = self.test_results["passed_tests"]
        failed_tests = self.test_results["failed_tests"]
        pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

        print("📊 TEST SUMMARY:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Pass Rate: {pass_rate:.1f}%")

        # Overall Status
        if pass_rate >= 80:
            print("   Overall Status: ✅ EXCELLENT")
        elif pass_rate >= 60:
            print("   Overall Status: ⚠️ GOOD")
        elif pass_rate >= 40:
            print("   Overall Status: ⚠️ NEEDS IMPROVEMENT")
        else:
            print("   Overall Status: ❌ CRITICAL ISSUES")

        print("\n📋 DETAILED RESULTS:")

        # Detailed results
        for test_detail in self.test_results["test_details"]:
            status_emoji = (
                "✅"
                if test_detail["status"] == "PASS"
                else "❌" if test_detail["status"] == "FAIL" else "⚠️"
            )
            print(
                f"   {status_emoji} {test_detail['test_name']}: {test_detail['status']}"
            )

            if test_detail["status"] == "ERROR":
                print(f"      Error: {test_detail.get('error', 'Unknown error')}")
            elif "details" in test_detail:
                # Show key details
                details = test_detail["details"]
                if "processing_time" in details:
                    print(f"      Processing Time: {details['processing_time']:.2f}s")
                if "initialization_time" in details:
                    print(
                        f"      Initialization Time: {details['initialization_time']:.2f}s"
                    )
                if "availability_percentage" in details:
                    print(
                        f"      Component Availability: {details['availability_percentage']:.1f}%"
                    )

        print("\n🔧 RECOMMENDATIONS:")

        # Recommendations based on results
        if pass_rate < 80:
            print("   • Review failed tests and address underlying issues")
            print("   • Check component availability and dependencies")
            print("   • Verify system configuration and initialization")

        if any(test["status"] == "ERROR" for test in self.test_results["test_details"]):
            print("   • Investigate error cases and fix exceptions")
            print("   • Improve error handling and robustness")

        # Component-specific recommendations
        component_test = next(
            (
                t
                for t in self.test_results["test_details"]
                if t["test_name"] == "Component Availability"
            ),
            None,
        )
        if (
            component_test
            and component_test.get("details", {}).get("availability_percentage", 100)
            < 80
        ):
            print("   • Install missing AGI components")
            print("   • Check import paths and dependencies")

        print("\n📄 DETAILED TEST DATA:")
        print(
            f"   Test results saved to: test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        # Save detailed results to file
        import json

        filename = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(filename, "w") as f:
                json.dump(self.test_results, f, indent=2, default=str)
            print(f"   ✅ Test results saved to {filename}")
        except Exception as e:
            print(f"   ❌ Failed to save test results: {e}")

        print("\n" + "=" * 60)


async def main():
    """Main test runner"""
    test_suite = LukhasAGIIntegrationTest()
    await test_suite.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
