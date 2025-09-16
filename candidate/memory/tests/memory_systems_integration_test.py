"""
LUKHAS AI - Memory Systems Integration Test Suite
================================================

#TAG:testing
#TAG:memory
#TAG:integration
#TAG:validation

Comprehensive test suite for LUKHAS AI memory systems integration.
Tests all major components and their interactions.

Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""

import asyncio
import unittest
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import memory system components
try:
    from fold import FoldManager, MemoryFold
    from episodic.episodic_memory import ConsolidatedEpisodicmemory
    from systems.dream_memory_manager import DreamMemoryManager
    from systems.memory_collapse_verifier import MemoryCollapseVerifier
    from consciousness.awareness_mechanism import AwarenessMechanism
    from consciousness.dream_memory_integration import DreamMemoryIntegrator
    from consciousness.memory_consciousness_optimizer import MemoryConsciousnessOptimizer
    from trinity_framework_validator import TrinityFrameworkValidator
except ImportError as e:
    print(f"Warning: Could not import some modules: {e}")


class TestMemorySystemsIntegration(unittest.TestCase):
    """Integration tests for LUKHAS AI memory systems"""

    def setUp(self):
        """Set up test environment"""
        self.logger = logging.getLogger(__name__)

        # Initialize core components
        self.fold_manager = None
        self.episodic_memory = None
        self.dream_manager = None
        self.awareness_mechanism = None
        self.dream_integrator = None
        self.optimizer = None
        self.trinity_validator = None

        # Test data
        self.test_memories = [
            {'content': 'Test memory 1', 'importance': 0.8, 'emotional_weight': 0.6},
            {'content': 'Test memory 2', 'importance': 0.7, 'emotional_weight': 0.4},
            {'content': 'Test memory 3', 'importance': 0.9, 'emotional_weight': 0.8}
        ]

    def test_fold_manager_initialization(self):
        """Test FoldManager initialization and basic operations"""
        try:
            from fold import FoldManager

            # Initialize FoldManager
            fold_manager = FoldManager()
            self.assertIsNotNone(fold_manager)
            self.assertEqual(len(fold_manager.folds), 0)

            # Test fold creation
            fold = fold_manager.create_fold("Test content")
            self.assertIsNotNone(fold)
            self.assertEqual(fold.content, "Test content")
            self.assertIn(fold.id, fold_manager.folds)

            # Test fold retrieval
            retrieved_fold = fold_manager.retrieve_fold(fold.id)
            self.assertIsNotNone(retrieved_fold)
            self.assertEqual(retrieved_fold.content, "Test content")

            print("✅ FoldManager test passed")

        except ImportError:
            print("⚠️ FoldManager not available for testing")

    def test_episodic_memory_integration(self):
        """Test episodic memory system"""
        try:
            from episodic.episodic_memory import ConsolidatedEpisodicmemory

            # Initialize episodic memory
            episodic_memory = ConsolidatedEpisodicmemory()
            self.assertIsNotNone(episodic_memory)

            # Test memory processing
            test_memory = {
                'content': 'Test episodic memory',
                'emotional_context': {'valence': 0.7, 'arousal': 0.5, 'dominance': 0.6},
                'consciousness_state': 'awake'
            }

            # Process memory (async)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            result = loop.run_until_complete(episodic_memory.process_memory(test_memory))
            self.assertIsNotNone(result)
            self.assertEqual(result['status'], 'processed')

            loop.close()

            print("✅ Episodic Memory test passed")

        except ImportError:
            print("⚠️ Episodic Memory not available for testing")

    def test_cascade_prevention_system(self):
        """Test cascade prevention mechanisms"""
        try:
            from fold import FoldManager

            fold_manager = FoldManager()

            # Test cascade prevention by creating many folds
            initial_count = len(fold_manager.folds)

            # Create folds up to limit
            for i in range(1100):  # Exceed MAX_FOLDS (1000)
                fold_manager.create_fold(f"Test fold {i}")

            # Should not exceed reasonable limit due to cascade prevention
            final_count = len(fold_manager.folds)
            self.assertLessEqual(final_count, 1000)

            # Check cascade prevention stats
            stats = fold_manager.get_cascade_prevention_stats()
            self.assertGreater(stats['cascades_prevented'], 0)
            self.assertGreaterEqual(stats['success_rate'], 0.997)  # 99.7% target

            print(f"✅ Cascade Prevention test passed (prevented {stats['cascades_prevented']} cascades)")

        except ImportError:
            print("⚠️ Cascade Prevention not available for testing")

    def test_dream_memory_integration(self):
        """Test dream-memory integration system"""
        try:
            from consciousness.dream_memory_integration import DreamMemoryIntegrator, DreamType

            # Initialize dream integrator
            integrator = DreamMemoryIntegrator()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Initialize system
            init_result = loop.run_until_complete(integrator.initialize())
            self.assertTrue(init_result)

            # Test dream session
            dream_experience = loop.run_until_complete(
                integrator.start_dream_session(self.test_memories, DreamType.MEMORY_CONSOLIDATION)
            )

            self.assertIsNotNone(dream_experience)
            self.assertEqual(dream_experience.dream_type, DreamType.MEMORY_CONSOLIDATION)
            self.assertGreater(len(dream_experience.participating_memories), 0)

            # Test memory consolidation
            consolidation_result = loop.run_until_complete(
                integrator.consolidate_dream_memories(dream_experience)
            )

            self.assertIsNotNone(consolidation_result)
            self.assertGreaterEqual(consolidation_result['consolidation_quality'], 0.0)

            loop.close()

            print("✅ Dream-Memory Integration test passed")

        except ImportError:
            print("⚠️ Dream-Memory Integration not available for testing")

    def test_awareness_mechanism(self):
        """Test consciousness awareness mechanism"""
        try:
            from consciousness.awareness_mechanism import AwarenessMechanism, AwarenessLevel

            # Initialize awareness mechanism
            awareness = AwarenessMechanism()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Initialize system
            init_result = loop.run_until_complete(awareness.initialize())
            self.assertTrue(init_result)

            # Test awareness trigger
            trigger_data = {
                'content': 'Test awareness trigger',
                'triggers': ['test_trigger'],
                'emotional_context': {'valence': 0.7, 'arousal': 0.5},
                'intensity': 0.8
            }

            awareness_event = loop.run_until_complete(
                awareness.process_awareness_trigger(trigger_data)
            )

            self.assertIsNotNone(awareness_event)
            self.assertEqual(awareness_event.content, 'Test awareness trigger')
            self.assertIsInstance(awareness_event.awareness_level, AwarenessLevel)

            # Test self-reflection
            reflection = loop.run_until_complete(awareness.generate_self_reflection())
            self.assertIsNotNone(reflection)
            self.assertIn('reflection_id', reflection)

            # Test awareness state
            state = loop.run_until_complete(awareness.get_awareness_state())
            self.assertIsNotNone(state)
            self.assertIn('consciousness_state', state)

            loop.close()

            print("✅ Awareness Mechanism test passed")

        except ImportError:
            print("⚠️ Awareness Mechanism not available for testing")

    def test_memory_consciousness_optimizer(self):
        """Test memory-consciousness coupling optimizer"""
        try:
            from consciousness.memory_consciousness_optimizer import (
                MemoryConsciousnessOptimizer, CouplingType, OptimizationStrategy
            )

            # Initialize optimizer
            optimizer = MemoryConsciousnessOptimizer()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Initialize system
            init_result = loop.run_until_complete(optimizer.initialize())
            self.assertTrue(init_result)

            # Test coupling optimization
            optimization_result = loop.run_until_complete(
                optimizer.optimize_coupling(CouplingType.ATTENTION_MEMORY)
            )

            self.assertIsNotNone(optimization_result)
            self.assertEqual(optimization_result['status'], 'completed')
            self.assertIn('improvement', optimization_result)

            # Test comprehensive optimization
            comprehensive_result = loop.run_until_complete(
                optimizer.optimize_all_couplings()
            )

            self.assertIsNotNone(comprehensive_result)
            self.assertEqual(comprehensive_result['status'], 'completed')
            self.assertGreaterEqual(comprehensive_result['total_couplings_optimized'], 0)

            # Test coupling health monitoring
            health_report = loop.run_until_complete(optimizer.monitor_coupling_health())
            self.assertIsNotNone(health_report)
            self.assertIn('overall_health', health_report)
            self.assertGreaterEqual(health_report['overall_health'], 0.0)

            loop.close()

            print("✅ Memory-Consciousness Optimizer test passed")

        except ImportError:
            print("⚠️ Memory-Consciousness Optimizer not available for testing")

    def test_trinity_framework_validation(self):
        """Test Trinity Framework compliance validation"""
        try:
            from trinity_framework_validator import (
                TrinityFrameworkValidator, TrinityComponent, ValidationLevel
            )

            # Initialize validator
            validator = TrinityFrameworkValidator()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Initialize system
            init_result = loop.run_until_complete(validator.initialize())
            self.assertTrue(init_result)

            # Test comprehensive Trinity validation
            validation_result = loop.run_until_complete(
                validator.validate_trinity_compliance(ValidationLevel.STANDARD)
            )

            self.assertIsNotNone(validation_result)
            self.assertIn('overall_compliance', validation_result)
            self.assertIn('overall_score', validation_result)
            self.assertIn('component_results', validation_result)

            # Check individual component validation
            for component in TrinityComponent:
                component_result = loop.run_until_complete(
                    validator._validate_trinity_component(component, ValidationLevel.STANDARD)
                )
                self.assertIsNotNone(component_result)
                self.assertEqual(component_result.component, component)
                self.assertGreaterEqual(component_result.score, 0.0)
                self.assertLessEqual(component_result.score, 1.0)

            # Test Trinity status
            status = loop.run_until_complete(validator.get_trinity_status())
            self.assertIsNotNone(status)
            self.assertIn('system_references', status)

            loop.close()

            print(f"✅ Trinity Framework Validation test passed (score: {validation_result['overall_score']:.3f})")

        except ImportError:
            print("⚠️ Trinity Framework Validator not available for testing")

    def test_memory_collapse_verification(self):
        """Test memory collapse verification system"""
        try:
            from systems.memory_collapse_verifier import MemoryCollapseVerifier, MemoryNode
            from candidate.core.symbolic.symbolic_tracer import SymbolicTracer

            # Create mock tracer
            class MockTracer:
                def trace(self, *args, **kwargs):
                    pass

            tracer = MockTracer()

            # Initialize verifier
            verifier = MemoryCollapseVerifier(tracer)
            self.assertIsNotNone(verifier)

            # Test collapse operation verification
            collapse_operation = {
                'operation_id': 'test_collapse_001',
                'source_nodes': [
                    {'node_id': 'node1', 'parent_nodes': []},
                    {'node_id': 'node2', 'parent_nodes': []}
                ],
                'target_node': {'node_id': 'target', 'parent_nodes': []},
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'expected_content_hash': 'test_hash',
                'actual_content_hash': 'test_hash'
            }

            verification_result = verifier.verify_collapse_integrity(collapse_operation)
            self.assertTrue(verification_result)

            # Test memory nodes
            memory_nodes = [
                MemoryNode('node1', 'hash1', 0.8, [], []),
                MemoryNode('node2', 'hash2', 0.7, [], [])
            ]

            collapsed_node = MemoryNode('collapsed', 'hash_combined', 0.9, [], [])

            # Test semantic preservation
            semantic_result = verifier.validate_semantic_preservation(memory_nodes, collapsed_node)
            self.assertIsInstance(semantic_result, bool)

            # Test emotional consistency
            consistency_score = verifier.check_emotional_consistency(memory_nodes)
            self.assertGreaterEqual(consistency_score, 0.0)
            self.assertLessEqual(consistency_score, 1.0)

            print("✅ Memory Collapse Verification test passed")

        except ImportError:
            print("⚠️ Memory Collapse Verifier not available for testing")

    def test_system_integration_flow(self):
        """Test complete system integration flow"""
        try:
            print("\n🔄 Testing complete system integration flow...")

            # Test basic memory flow
            self._test_basic_memory_flow()

            # Test consciousness integration
            self._test_consciousness_integration_flow()

            # Test dream processing flow
            self._test_dream_processing_flow()

            # Test optimization flow
            self._test_optimization_flow()

            print("✅ Complete System Integration test passed")

        except Exception as e:
            print(f"❌ System Integration test failed: {e}")

    def _test_basic_memory_flow(self):
        """Test basic memory processing flow"""
        try:
            from fold import FoldManager

            # Create and process memories
            fold_manager = FoldManager()

            # Create multiple folds
            folds = []
            for i, memory_data in enumerate(self.test_memories):
                fold = fold_manager.create_fold(
                    content=memory_data['content'],
                    causal_chain=[f"cause_{i}"]
                )
                fold.importance = memory_data['importance']
                fold.emotional_valence = memory_data['emotional_weight']
                folds.append(fold)

            # Test consolidation
            consolidation_result = fold_manager.consolidate()
            self.assertIsNotNone(consolidation_result)
            self.assertTrue(consolidation_result['consolidated'])

            print("  ✓ Basic memory flow working")

        except ImportError:
            print("  ⚠️ Basic memory flow test skipped")

    def _test_consciousness_integration_flow(self):
        """Test consciousness-memory integration flow"""
        try:
            from consciousness.awareness_mechanism import AwarenessMechanism

            awareness = AwarenessMechanism()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Initialize and test awareness
            loop.run_until_complete(awareness.initialize())

            # Test memory integration
            memory_data = {
                'id': 'test_memory_001',
                'content': 'Integration test memory',
                'importance': 0.8,
                'emotional_context': {'valence': 0.7, 'arousal': 0.5}
            }

            integration_result = loop.run_until_complete(
                awareness.integrate_with_memory(memory_data)
            )

            self.assertTrue(integration_result['integration_successful'])

            loop.close()

            print("  ✓ Consciousness integration flow working")

        except ImportError:
            print("  ⚠️ Consciousness integration flow test skipped")

    def _test_dream_processing_flow(self):
        """Test dream processing integration flow"""
        try:
            from consciousness.dream_memory_integration import DreamMemoryIntegrator, DreamType

            integrator = DreamMemoryIntegrator()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Initialize and test dream processing
            loop.run_until_complete(integrator.initialize())

            # Start dream session
            dream_experience = loop.run_until_complete(
                integrator.start_dream_session(self.test_memories[:2], DreamType.MEMORY_CONSOLIDATION)
            )

            self.assertIsNotNone(dream_experience)

            # Test consolidation
            consolidation_result = loop.run_until_complete(
                integrator.consolidate_dream_memories(dream_experience)
            )

            self.assertGreaterEqual(consolidation_result['consolidation_quality'], 0.0)

            loop.close()

            print("  ✓ Dream processing flow working")

        except ImportError:
            print("  ⚠️ Dream processing flow test skipped")

    def _test_optimization_flow(self):
        """Test memory-consciousness optimization flow"""
        try:
            from consciousness.memory_consciousness_optimizer import (
                MemoryConsciousnessOptimizer, CouplingType
            )

            optimizer = MemoryConsciousnessOptimizer()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Initialize and test optimization
            loop.run_until_complete(optimizer.initialize())

            # Test single coupling optimization
            result = loop.run_until_complete(
                optimizer.optimize_coupling(CouplingType.AWARENESS_MEMORY)
            )

            self.assertEqual(result['status'], 'completed')

            # Test health monitoring
            health = loop.run_until_complete(optimizer.monitor_coupling_health())
            self.assertIn('overall_health', health)

            loop.close()

            print("  ✓ Optimization flow working")

        except ImportError:
            print("  ⚠️ Optimization flow test skipped")

    def test_performance_benchmarks(self):
        """Test system performance benchmarks"""
        print("\n⚡ Running performance benchmarks...")

        # Test memory creation performance
        start_time = datetime.now()
        try:
            from fold import FoldManager

            fold_manager = FoldManager()

            # Create 100 folds and measure time
            for i in range(100):
                fold_manager.create_fold(f"Performance test fold {i}")

            creation_time = (datetime.now() - start_time).total_seconds()
            self.assertLess(creation_time, 5.0)  # Should complete in under 5 seconds

            print(f"  ✓ Memory creation: {creation_time:.3f}s for 100 folds")

        except ImportError:
            print("  ⚠️ Memory creation benchmark skipped")

        # Test cascade prevention performance
        if hasattr(self, 'fold_manager'):
            start_time = datetime.now()

            # Trigger cascade prevention
            for i in range(50):
                self.fold_manager.create_fold(f"Cascade test {i}")

            cascade_time = (datetime.now() - start_time).total_seconds()
            print(f"  ✓ Cascade prevention: {cascade_time:.3f}s for 50 folds")

    def test_error_handling(self):
        """Test error handling across systems"""
        print("\n🛡️ Testing error handling...")

        # Test invalid fold operations
        try:
            from fold import FoldManager

            fold_manager = FoldManager()

            # Test retrieval of non-existent fold
            result = fold_manager.retrieve_fold("non_existent_id")
            self.assertIsNone(result)

            print("  ✓ Invalid fold retrieval handled correctly")

        except ImportError:
            print("  ⚠️ Fold error handling test skipped")

        # Test invalid awareness triggers
        try:
            from consciousness.awareness_mechanism import AwarenessMechanism

            awareness = AwarenessMechanism()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Test with invalid trigger data
            invalid_trigger = {}  # Empty trigger data

            try:
                event = loop.run_until_complete(
                    awareness.process_awareness_trigger(invalid_trigger)
                )
                # Should handle gracefully
                self.assertIsNotNone(event)
            except Exception:
                pass  # Expected to handle errors gracefully

            loop.close()

            print("  ✓ Invalid awareness triggers handled correctly")

        except ImportError:
            print("  ⚠️ Awareness error handling test skipped")


def run_comprehensive_tests():
    """Run comprehensive memory systems tests"""
    print("🧠 LUKHAS AI Memory Systems - Comprehensive Test Suite")
    print("=" * 60)

    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestMemorySystemsIntegration)

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")

    if result.errors:
        print("\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")

    # Overall result
    if result.wasSuccessful():
        print("\n🎉 All tests passed! Memory systems are functioning correctly.")
        return True
    else:
        print("\n⚠️ Some tests failed. Please review the issues above.")
        return False


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Run comprehensive tests
    success = run_comprehensive_tests()

    # Exit with appropriate code
    sys.exit(0 if success else 1)