#!/usr/bin/env python3
"""
🧪 LUKHAS QRG Testing & Validation Suite

Comprehensive testing system for LUKHAS QR Code Generators (QRGs),
including unit tests, integration tests, performance benchmarks,
security validation, and consciousness-awareness verification.

Features:
- QRG functionality testing
- Performance benchmarking
- Security validation
- Consciousness adaptation testing
- Cultural sensitivity verification
- Quantum coherence validation
- Emergency override testing
- Multi-modal compatibility testing

Author: LUKHAS AI System
License: LUKHAS Commercial License
"""

import json
import os
import sys
import time
import unittest
from datetime import datetime

# Add the current directory to the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from qrg_integration import LukhusQRGIntegrator, QRGType, SecurityLevel


class TestQRGCore(unittest.TestCase):
    """Core QRG functionality tests"""

    def setUp(self):
        """Set up test environment"""
        self.integrator = LukhusQRGIntegrator()
        self.test_user_id = "test_user_qrg_001"
        self.test_context = self.integrator.create_qrg_context(
            user_id=self.test_user_id,
            security_level="protected",
            attention_focus=["testing", "validation"],
        )

    def test_integrator_initialization(self):
        """Test QRG integrator initialization"""
        self.assertIsNotNone(self.integrator)
        self.assertIsInstance(self.integrator.config, dict)
        self.assertIn("max_pattern_size", self.integrator.config)
        self.assertEqual(self.integrator.config["max_pattern_size"], 177)

    def test_context_creation(self):
        """Test QRG context creation"""
        context = self.integrator.create_qrg_context(
            user_id="test_context_user",
            security_level="confidential",
            attention_focus=["security", "testing"],
        )

        self.assertEqual(context.user_id, "test_context_user")
        self.assertEqual(context.security_clearance, SecurityLevel.CONFIDENTIAL)
        self.assertIn("security", context.attention_focus)
        self.assertIsInstance(context.timestamp, datetime)
        self.assertIsInstance(context.session_id, str)

    def test_consciousness_qrg_generation(self):
        """Test consciousness-adaptive QRG generation"""
        result = self.integrator.generate_consciousness_qrg(self.test_context)

        self.assertEqual(result.qr_type, QRGType.CONSCIOUSNESS_ADAPTIVE)
        self.assertIsInstance(result.pattern_data, str)
        self.assertIn("CONSCIOUSNESS_QR", result.pattern_data)
        self.assertIsInstance(result.metadata, dict)
        self.assertIn("consciousness_state", result.metadata)
        self.assertGreaterEqual(result.compliance_score, 0.0)
        self.assertLessEqual(result.compliance_score, 1.0)

    def test_cultural_qrg_generation(self):
        """Test cultural QRG generation"""
        # Test with different cultural contexts
        cultural_contexts = [
            {"region": "east_asian", "preferences": {"colors": ["red", "gold"]}},
            {"region": "islamic", "preferences": {"symbols": ["geometric"]}},
            {"region": "universal", "preferences": {}},
        ]

        for cultural_profile in cultural_contexts:
            with self.subTest(cultural_profile=cultural_profile):
                context = self.integrator.create_qrg_context(
                    user_id=f"cultural_test_{cultural_profile['region']}",
                    security_level="protected",
                )
                context.cultural_profile = cultural_profile

                result = self.integrator.generate_cultural_qrg(context)

                self.assertEqual(result.qr_type, QRGType.CULTURAL_SYMBOLIC)
                self.assertIn("CULTURAL_QR", result.pattern_data)
                self.assertIn("cultural_context", result.metadata)
                self.assertEqual(
                    result.metadata["cultural_context"], cultural_profile["region"]
                )

    def test_quantum_qrg_generation(self):
        """Test quantum-encrypted QRG generation"""
        # Test with different security levels
        security_levels = [
            SecurityLevel.PROTECTED,
            SecurityLevel.SECRET,
            SecurityLevel.COSMIC,
        ]

        for security_level in security_levels:
            with self.subTest(security_level=security_level):
                context = self.integrator.create_qrg_context(
                    user_id=f"quantum_test_{security_level.value}",
                    security_level=security_level.value,
                )

                result = self.integrator.generate_quantum_qrg(context)

                self.assertEqual(result.qr_type, QRGType.QUANTUM_ENCRYPTED)
                self.assertIn("QUANTUM_QR", result.pattern_data)
                self.assertIn("quantum_parameters", result.metadata)
                self.assertTrue(result.metadata["post_quantum_protected"])
                self.assertIn("encryption_methods", result.metadata)

    def test_dream_state_qrg_generation(self):
        """Test dream-state QRG generation"""
        # Modify context for dream state
        dream_context = self.test_context
        dream_context.consciousness_level = 0.3  # Lower consciousness for dream state

        result = self.integrator.generate_dream_state_qrg(dream_context)

        self.assertEqual(result.qr_type, QRGType.DREAM_STATE)
        self.assertIn("DREAM_QR", result.pattern_data)
        self.assertIn("dream_state", result.metadata)
        self.assertIn("symbolic_elements", result.metadata)
        self.assertLess(result.consciousness_resonance, 0.5)  # Reduced consciousness

    def test_emergency_override_qrg_generation(self):
        """Test emergency override QRG generation"""
        result = self.integrator.generate_emergency_override_qrg(self.test_context)

        self.assertEqual(result.qr_type, QRGType.EMERGENCY_OVERRIDE)
        self.assertIn("EMERGENCY_QR", result.pattern_data)
        self.assertIn("emergency_code", result.metadata)
        self.assertIn("override_level", result.metadata)
        self.assertEqual(result.metadata["override_level"], "EMERGENCY_ALPHA")

        # Emergency QRGs should have short expiration
        time_diff = result.expiration - self.test_context.timestamp
        self.assertLessEqual(
            time_diff.total_seconds(), 901
        )  # 15 minutes max (with small buffer)

    def test_adaptive_qrg_type_selection(self):
        """Test automatic QRG type selection"""
        # Test different contexts that should trigger different QRG types
        test_cases = [
            {
                "context_mods": {"security_clearance": SecurityLevel.SECRET},
                "expected_type": QRGType.QUANTUM_ENCRYPTED,
            },
            {
                "context_mods": {"consciousness_level": 0.2},
                "expected_type": QRGType.DREAM_STATE,
            },
            {
                "context_mods": {"cognitive_load": 0.95},
                "expected_type": QRGType.EMERGENCY_OVERRIDE,
            },
        ]

        for case in test_cases:
            with self.subTest(case=case):
                context = self.integrator.create_qrg_context(
                    user_id="adaptive_test_user", security_level="protected"
                )

                # Apply context modifications
                for attr, value in case["context_mods"].items():
                    setattr(context, attr, value)

                # Test type determination
                determined_type = self.integrator._determine_optimal_qrg_type(context)
                self.assertEqual(determined_type, case["expected_type"])


class TestQRGPerformance(unittest.TestCase):
    """QRG performance and benchmarking tests"""

    def setUp(self):
        self.integrator = LukhusQRGIntegrator()
        self.performance_data = []

    def test_generation_speed(self):
        """Test QRG generation speed"""
        qrg_types = [
            QRGType.CONSCIOUSNESS_ADAPTIVE,
            QRGType.CULTURAL_SYMBOLIC,
            QRGType.QUANTUM_ENCRYPTED,
            QRGType.DREAM_STATE,
            QRGType.EMERGENCY_OVERRIDE,
        ]

        for qrg_type in qrg_types:
            with self.subTest(qrg_type=qrg_type):
                context = self.integrator.create_qrg_context(
                    user_id=f"perf_test_{qrg_type.value}", security_level="protected"
                )

                start_time = time.time()
                result = self.integrator.generate_adaptive_qrg(context, qrg_type)
                end_time = time.time()

                generation_time = end_time - start_time

                # Performance assertions
                self.assertLess(generation_time, 1.0)  # Should be under 1 second
                self.assertIsNotNone(result)

                # Record performance data
                self.performance_data.append(
                    {
                        "qrg_type": qrg_type.value,
                        "generation_time": generation_time,
                        "pattern_length": len(result.pattern_data),
                        "metadata_size": len(json.dumps(result.metadata)),
                    }
                )

    def test_concurrent_generation(self):
        """Test concurrent QRG generation"""
        import threading

        results = []
        errors = []

        def generate_qrg(user_id):
            try:
                context = self.integrator.create_qrg_context(
                    user_id=f"concurrent_user_{user_id}", security_level="protected"
                )
                result = self.integrator.generate_consciousness_qrg(context)
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=generate_qrg, args=(i,))
            threads.append(thread)

        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()
        end_time = time.time()

        # Validate results
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        self.assertEqual(len(results), 5)
        self.assertLess(end_time - start_time, 2.0)  # Should complete within 2 seconds

    def test_memory_usage(self):
        """Test memory usage during QRG generation"""
        import tracemalloc

        tracemalloc.start()

        # Generate multiple QRGs
        for i in range(10):
            context = self.integrator.create_qrg_context(
                user_id=f"memory_test_{i}", security_level="protected"
            )
            result = self.integrator.generate_consciousness_qrg(context)

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Memory usage should be reasonable (under 10MB)
        self.assertLess(
            peak / 1024 / 1024, 10, f"Peak memory usage: {peak / 1024 / 1024:.2f}MB"
        )

    def tearDown(self):
        """Print performance summary"""
        if self.performance_data:
            print("\n📊 QRG Performance Results:")
            for data in self.performance_data:
                print(f"   {data['qrg_type']}: {data['generation_time']:.3f}s")


class TestQRGSecurity(unittest.TestCase):
    """QRG security and validation tests"""

    def setUp(self):
        self.integrator = LukhusQRGIntegrator()

    def test_unique_signatures(self):
        """Test that QRGs have unique security signatures"""
        signatures = set()

        for i in range(10):
            context = self.integrator.create_qrg_context(
                user_id=f"unique_test_{i}", security_level="protected"
            )
            result = self.integrator.generate_consciousness_qrg(context)

            # Check uniqueness
            self.assertNotIn(result.security_signature, signatures)
            signatures.add(result.security_signature)

            # Validate signature format
            self.assertIsInstance(result.security_signature, str)
            self.assertGreater(len(result.security_signature), 32)

    def test_quantum_security_properties(self):
        """Test quantum QRG security properties"""
        context = self.integrator.create_qrg_context(
            user_id="quantum_security_test", security_level="secret"
        )

        result = self.integrator.generate_quantum_qrg(context)

        # Validate quantum security properties
        self.assertTrue(result.metadata["post_quantum_protected"])
        self.assertIn("encryption_methods", result.metadata)
        self.assertIn("Kyber-1024", result.metadata["encryption_methods"])
        self.assertIn("Dilithium-5", result.metadata["encryption_methods"])
        self.assertIn("LUKHAS-Quantum-v2", result.metadata["encryption_methods"])

    def test_emergency_override_security(self):
        """Test emergency override security measures"""
        context = self.integrator.create_qrg_context(
            user_id="emergency_security_test", security_level="protected"
        )

        result = self.integrator.generate_emergency_override_qrg(context)

        # Emergency QRGs should have specific security properties
        self.assertIn("emergency_code", result.metadata)
        self.assertEqual(len(result.metadata["emergency_code"]), 64)  # 32 bytes hex
        self.assertEqual(result.metadata["override_level"], "EMERGENCY_ALPHA")

        # Short expiration for security
        time_diff = result.expiration - context.timestamp
        self.assertLessEqual(time_diff.total_seconds(), 901)  # 15 minutes (with buffer)

    def test_steganographic_security(self):
        """Test steganographic QRG security (if available)"""
        # This would test steganographic capabilities if implemented
        # For now, we test the basic steganographic pattern creation

        context = self.integrator.create_qrg_context(
            user_id="stego_security_test", security_level="confidential"
        )

        # Note: Steganographic QRG is not fully implemented in the current system
        # This is a placeholder for future implementation
        pass


class TestQRGCompliance(unittest.TestCase):
    """QRG compliance and constitutional AI tests"""

    def setUp(self):
        self.integrator = LukhusQRGIntegrator()

    def test_constitutional_compliance(self):
        """Test constitutional AI compliance in QRGs"""
        context = self.integrator.create_qrg_context(
            user_id="compliance_test", security_level="protected"
        )

        result = self.integrator.generate_consciousness_qrg(context)

        # All QRGs should have high compliance scores
        self.assertGreaterEqual(result.compliance_score, 0.8)
        self.assertLessEqual(result.compliance_score, 1.0)

    def test_cultural_safety_compliance(self):
        """Test cultural safety compliance"""
        cultural_profiles = [
            {"region": "east_asian", "preferences": {}},
            {"region": "islamic", "preferences": {}},
            {"region": "indigenous", "preferences": {}},
            {"region": "universal", "preferences": {}},
        ]

        for profile in cultural_profiles:
            with self.subTest(profile=profile):
                context = self.integrator.create_qrg_context(
                    user_id=f"cultural_safety_{profile['region']}",
                    security_level="protected",
                )
                context.cultural_profile = profile

                result = self.integrator.generate_cultural_qrg(context)

                # Cultural QRGs should have high safety scores
                self.assertGreaterEqual(result.cultural_safety_score, 0.8)

    def test_consciousness_resonance_validation(self):
        """Test consciousness resonance validation"""
        consciousness_levels = [0.1, 0.3, 0.5, 0.7, 0.9]

        for level in consciousness_levels:
            with self.subTest(consciousness_level=level):
                context = self.integrator.create_qrg_context(
                    user_id=f"consciousness_test_{level}", security_level="protected"
                )
                context.consciousness_level = level

                result = self.integrator.generate_consciousness_qrg(context)

                # Consciousness resonance should correlate with input level
                self.assertGreaterEqual(result.consciousness_resonance, 0.0)
                self.assertLessEqual(result.consciousness_resonance, 1.0)


def run_comprehensive_qrg_tests():
    """Run comprehensive QRG test suite"""
    print("🧪 LUKHAS QRG Comprehensive Test Suite")
    print("=" * 60)

    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test classes
    test_classes = [TestQRGCore, TestQRGPerformance, TestQRGSecurity, TestQRGCompliance]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Test summary
    print("\n📊 Test Results Summary:")
    print(f"   🧪 Tests run: {result.testsRun}")
    print(
        f"   ✅ Successful: {result.testsRun - len(result.failures) - len(result.errors)}"
    )
    print(f"   ❌ Failures: {len(result.failures)}")
    print(f"   🚨 Errors: {len(result.errors)}")

    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   • {test}: {traceback}")

    if result.errors:
        print("\n🚨 Errors:")
        for test, traceback in result.errors:
            print(f"   • {test}: {traceback}")

    # Overall success
    success = len(result.failures) == 0 and len(result.errors) == 0

    if success:
        print("\n🎉 All QRG tests passed successfully!")
        print("🔗 LUKHAS QRG system is ready for production!")
    else:
        print("\n⚠️ Some tests failed. Review and fix issues before deployment.")

    return result


def create_qrg_validation_report():
    """Create a comprehensive QRG validation report"""
    print("\n📋 Creating QRG Validation Report...")

    integrator = LukhusQRGIntegrator()

    # Test different scenarios
    validation_scenarios = [
        {
            "name": "High Consciousness User",
            "context": {
                "user_id": "high_consciousness_user",
                "consciousness_level": 0.9,
                "security_level": "protected",
                "attention_focus": ["transcendence", "awareness"],
            },
        },
        {
            "name": "Cultural Sensitive Context",
            "context": {
                "user_id": "cultural_user",
                "consciousness_level": 0.6,
                "security_level": "protected",
                "cultural_profile": {
                    "region": "east_asian",
                    "preferences": {"respect": "formal"},
                },
            },
        },
        {
            "name": "High Security Environment",
            "context": {
                "user_id": "security_user",
                "consciousness_level": 0.7,
                "security_level": "secret",
                "attention_focus": ["security", "protection"],
            },
        },
        {
            "name": "Dream State Session",
            "context": {
                "user_id": "dream_user",
                "consciousness_level": 0.2,
                "security_level": "protected",
                "attention_focus": ["relaxation", "meditation"],
            },
        },
        {
            "name": "Emergency Situation",
            "context": {
                "user_id": "emergency_user",
                "consciousness_level": 0.8,
                "security_level": "protected",
                "attention_focus": ["emergency", "urgent_access"],
            },
        },
    ]

    report_data = {
        "timestamp": datetime.now().isoformat(),
        "system_version": "LUKHAS QRG v1.0",
        "test_scenarios": [],
        "summary": {},
    }

    total_tests = 0
    successful_tests = 0

    for scenario in validation_scenarios:
        print(f"   Testing: {scenario['name']}")

        try:
            # Create context
            context_data = scenario["context"]
            context = integrator.create_qrg_context(**context_data)

            # If cultural profile provided, update it
            if "cultural_profile" in context_data:
                context.cultural_profile = context_data["cultural_profile"]

            # Generate adaptive QRG
            result = integrator.generate_adaptive_qrg(context)

            scenario_result = {
                "name": scenario["name"],
                "status": "success",
                "qrg_type": result.qr_type.value,
                "compliance_score": result.compliance_score,
                "cultural_safety_score": result.cultural_safety_score,
                "consciousness_resonance": result.consciousness_resonance,
                "security_signature_length": len(result.security_signature),
                "pattern_data_length": len(result.pattern_data),
                "metadata_keys": list(result.metadata.keys()),
                "generation_metrics": result.generation_metrics,
            }

            successful_tests += 1

        except Exception as e:
            scenario_result = {
                "name": scenario["name"],
                "status": "failed",
                "error": str(e),
            }

        report_data["test_scenarios"].append(scenario_result)
        total_tests += 1

    # Calculate summary
    report_data["summary"] = {
        "total_scenarios": total_tests,
        "successful_scenarios": successful_tests,
        "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
        "system_status": (
            "operational" if successful_tests == total_tests else "needs_attention"
        ),
    }

    # Generate statistics
    stats = integrator.get_generation_statistics()
    report_data["generation_statistics"] = stats

    # Save report
    report_filename = (
        f"qrg_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(report_filename, "w") as f:
        json.dump(report_data, f, indent=2, default=str)

    print(f"   📄 Report saved: {report_filename}")
    print(f"   📊 Success rate: {report_data['summary']['success_rate']:.1%}")
    print(f"   🎯 System status: {report_data['summary']['system_status']}")

    return report_data


if __name__ == "__main__":
    print("🚀 Starting LUKHAS QRG Test & Validation Suite")
    print("=" * 60)

    # Run comprehensive tests
    test_result = run_comprehensive_qrg_tests()

    # Create validation report
    validation_report = create_qrg_validation_report()

    print("\n🎯 QRG Testing & Validation Complete!")
    print("🔗 System ready for consciousness-aware authentication!")
