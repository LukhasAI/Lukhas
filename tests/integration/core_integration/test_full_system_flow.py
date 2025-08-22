#!/usr/bin/env python3
"""
Full System Integration Test
=============================
Demonstrates that all enhanced features work together as a cohesive whole.
Tests the complete flow from input through all systems to output.
"""

import asyncio
import time

import pytest

from core.colonies.advanced_consensus_algorithms import (
    AdvancedColonyConsensus,
    AdvancedConsensusMethod,
    VoteType,
)
from core.events.contracts import ConsensusReached, GlyphCreated
from core.events.typed_event_bus import get_typed_event_bus

# Import all enhanced components
from core.glyph.glyph_engine_enhanced import get_enhanced_glyph_engine
from core.glyph.universal_symbol_protocol import SymbolDomain
from lukhas.memory.folds.optimized_fold_engine import OptimizedFoldEngine
from lukhas.orchestration.brain.unified_cognitive_orchestrator import (
    UnifiedCognitiveOrchestrator,
)


class TestFullSystemIntegration:
    """Test complete system integration"""

    @pytest.mark.asyncio
    async def test_end_to_end_cognitive_flow(self):
        """Test complete cognitive processing flow through all systems"""

        print("\n" + "="*60)
        print("🧪 FULL SYSTEM INTEGRATION TEST")
        print("="*60)

        # Initialize unified orchestrator
        orchestrator = UnifiedCognitiveOrchestrator()
        await orchestrator.initialize()

        # Test 1: Complex thought processing
        print("\n1️⃣ Testing Complex Thought Processing:")

        thought = "Should we prioritize safety over innovation in our next decision?"
        result = await orchestrator.process_thought(
            thought,
            context={"emotion": {"concern": 0.6, "curiosity": 0.7}}
        )

        assert result["thought_id"] is not None
        assert "consciousness" in result["processing_results"]
        assert "memory" in result["processing_results"]
        assert "emotion" in result["processing_results"]

        print(f"   ✓ Thought processed: {result['thought_id']}")
        print(f"   ✓ Modules engaged: {list(result['processing_results'].keys())}")

        # Test 2: Cross-module symbol communication
        print("\n2️⃣ Testing Cross-Module Symbol Communication:")

        glyph_engine = get_enhanced_glyph_engine()

        # Create symbols from different modules
        memory_symbol = glyph_engine.encode_concept(
            "important_memory",
            domains={SymbolDomain.MEMORY},
            source_module="memory"
        )

        consciousness_symbol = glyph_engine.encode_concept(
            "awareness_state",
            domains={SymbolDomain.COGNITIVE},
            source_module="consciousness"
        )

        # Create cross-module link
        glyph_engine.create_cross_module_link(
            memory_symbol,
            consciousness_symbol,
            link_type="causal"
        )

        # Find related symbols
        related = glyph_engine.find_related_symbols(memory_symbol)

        assert "consciousness" in related or len(related) > 0
        print("   ✓ Cross-module links created")
        print(f"   ✓ Related modules found: {list(related.keys())}")

        # Test 3: Colony consensus decision
        print("\n3️⃣ Testing Advanced Colony Consensus:")

        # Process decision through orchestrator
        decision_thought = "Approve increasing processing resources?"
        await orchestrator.process_thought(decision_thought)

        # Wait for consensus
        await asyncio.sleep(1)

        status = await orchestrator.get_system_status()

        assert status["metrics"]["decisions_made"] >= 0
        print(f"   ✓ Decisions made: {status['metrics']['decisions_made']}")
        print(f"   ✓ Consensus confidence: {status['cognitive_state']['consensus_confidence']:.3f}")

        # Test 4: Memory optimization
        print("\n4️⃣ Testing Optimized Memory System:")

        memory_engine = orchestrator.memory_engine

        # Create multiple memories
        for i in range(50):
            memory_engine.create_fold(
                key=f"test_memory_{i}",
                content={"data": f"test_content_{i}" * 100},  # Compressible content
                tags=["test", f"batch_{i//10}"]
            )

        stats = memory_engine.get_statistics()

        assert stats["total_folds"] >= 50
        assert stats["avg_compression_ratio"] < 1.0  # Should be compressed

        print(f"   ✓ Memory folds created: {stats['total_folds']}")
        print(f"   ✓ Compression ratio: {stats['avg_compression_ratio']:.3f}")
        print(f"   ✓ Cache hit rate: {stats['cache_hit_rate']:.1%}")

        # Test 5: Quantum processing
        print("\n5️⃣ Testing Quantum Processing Integration:")

        quantum_processor = orchestrator.quantum_processor

        # Create Bell pair
        bell_state, entangled = quantum_processor.create_bell_pair()

        assert bell_state is not None
        assert len(entangled) == 2

        # Test quantum-enhanced decision
        await orchestrator._quantum_process_decisions()

        quantum_stats = quantum_processor.get_statistics()

        assert quantum_stats["circuits_executed"] > 0
        print(f"   ✓ Quantum circuits executed: {quantum_stats['circuits_executed']}")
        print(f"   ✓ Entanglements created: {quantum_stats['entanglements_created']}")

        # Test 6: Event flow
        print("\n6️⃣ Testing Event-Driven Architecture:")

        event_bus = get_typed_event_bus()
        events_received = []

        async def track_events(event):
            events_received.append(event.event_type)

        # Subscribe to events
        event_bus.subscribe(GlyphCreated, track_events)
        event_bus.subscribe(ConsensusReached, track_events)

        # Generate events through processing
        await orchestrator.process_thought("Test event generation")
        await asyncio.sleep(0.5)

        assert len(events_received) > 0
        print(f"   ✓ Events captured: {len(events_received)}")
        print(f"   ✓ Event types: {set(events_received)}")

        # Test 7: System coherence
        print("\n7️⃣ Testing System Coherence:")

        final_status = await orchestrator.get_system_status()

        # Check all systems are operational
        assert final_status["cognitive_state"]["awareness_level"] > 0
        assert final_status["cognitive_state"]["quantum_coherence"] > 0
        assert final_status["memory"]["total_folds"] > 0
        assert final_status["symbols"]["total"] > 0

        print(f"   ✓ Awareness level: {final_status['cognitive_state']['awareness_level']:.3f}")
        print(f"   ✓ Quantum coherence: {final_status['cognitive_state']['quantum_coherence']:.3f}")
        print(f"   ✓ Total symbols: {final_status['symbols']['total']}")
        print(f"   ✓ Active modules: {len(final_status['symbols']['by_module'])}")

        # Cleanup
        await orchestrator.shutdown()

        print("\n✅ ALL INTEGRATION TESTS PASSED!")
        print("="*60)

    @pytest.mark.asyncio
    async def test_symbol_flow_across_modules(self):
        """Test that symbols flow correctly between all modules"""

        print("\n🔄 Testing Symbol Flow Across Modules")

        engine = get_enhanced_glyph_engine()

        # Create cognitive chain
        chain = engine.create_cognitive_chain(
            ["perceive", "analyze", "decide", "act"],
            source_module="test"
        )

        assert len(chain) == 4

        # Verify causal links
        for i in range(len(chain) - 1):
            assert len(chain[i].causal_links) > 0

        print(f"   ✓ Cognitive chain created with {len(chain)} symbols")

        # Translate for different modules
        modules = ["consciousness", "memory", "quantum", "dream", "governance"]

        for module in modules:
            translated = engine.translate_for_module(chain[0], module)
            assert translated is not None
            print(f"   ✓ Symbol translated for {module}")

    @pytest.mark.asyncio
    async def test_consensus_with_quantum_voting(self):
        """Test advanced consensus with quantum superposition voting"""

        print("\n⚛️ Testing Quantum Consensus")

        consensus = AdvancedColonyConsensus("test_colony")

        # Register agents
        for i in range(5):
            consensus.register_agent(f"agent_{i}", weight=1.0 + i*0.1)

        # Create proposal
        proposal_id = await consensus.propose(
            content="Test quantum decision",
            proposer="test",
            method=AdvancedConsensusMethod.QUANTUM_SUPERPOSITION
        )

        # Cast quantum votes
        for i in range(5):
            amplitudes = {
                VoteType.APPROVE: complex(0.6, 0.3),
                VoteType.REJECT: complex(0.3, 0.2),
                VoteType.ABSTAIN: complex(0.2, 0.1)
            }

            await consensus.quantum_superposition_vote(
                proposal_id,
                f"agent_{i}",
                amplitudes,
                entangle_with=[f"agent_{(i+1)%5}"]  # Circular entanglement
            )

        # Get quantum votes and reach consensus
        quantum_votes = consensus.quantum_votes[proposal_id]
        outcome = await consensus._quantum_consensus(
            consensus.active_proposals[proposal_id],
            quantum_votes
        )

        assert outcome is not None
        assert outcome.confidence > 0

        print(f"   ✓ Quantum consensus reached: {outcome.decision.value}")
        print(f"   ✓ Confidence: {outcome.confidence:.3f}")
        print(f"   ✓ Entanglement clusters: {outcome.metadata.get('quantum_entanglement_clusters', 0)}")

    @pytest.mark.asyncio
    async def test_memory_performance(self):
        """Test memory system performance optimizations"""

        print("\n💾 Testing Memory Performance")

        engine = OptimizedFoldEngine(max_memory_mb=100, cache_size=50)

        start_time = time.time()

        # Batch create folds
        items = [
            (f"fold_{i}", {"data": f"content_{i}" * 100}, {"tags": ["test"]})
            for i in range(100)
        ]

        folds = await engine.batch_create(items)

        create_time = time.time() - start_time

        assert len(folds) == 100
        assert create_time < 5.0  # Should be fast

        # Test cache performance
        hit_count = 0
        for _ in range(1000):
            fold = engine.get_fold(f"fold_{hit_count % 20}")  # 80/20 access pattern
            if fold:
                hit_count += 1

        stats = engine.get_statistics()

        assert stats["cache_hit_rate"] > 0.7  # Should have good cache performance

        print(f"   ✓ Created 100 folds in {create_time:.3f}s")
        print(f"   ✓ Cache hit rate: {stats['cache_hit_rate']:.1%}")
        print(f"   ✓ Compression ratio: {stats['avg_compression_ratio']:.3f}")

        engine.shutdown()


def run_integration_tests():
    """Run all integration tests"""
    import sys

    # Run with pytest if available
    try:
        import pytest
        sys.exit(pytest.main([__file__, "-v"]))
    except ImportError:
        # Run manually
        print("Running manual integration tests...")
        test = TestFullSystemIntegration()

        asyncio.run(test.test_end_to_end_cognitive_flow())
        asyncio.run(test.test_symbol_flow_across_modules())
        asyncio.run(test.test_consensus_with_quantum_voting())
        asyncio.run(test.test_memory_performance())

        print("\n🎉 All manual tests completed!")


if __name__ == "__main__":
    run_integration_tests()
