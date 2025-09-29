#!/usr/bin/env python3
"""
Unified Cognitive Orchestrator
===============================
Central orchestration system that deeply integrates all enhanced LUKHAS capabilities.
This replaces fragmented orchestration with a unified cognitive architecture.

Core Integration Points:
- Universal Symbol Protocol for all inter-module communication
- Advanced Colony Consensus for distributed decision-making
- Optimized Memory Folds for efficient state management
- Enhanced Quantum Processing for complex computations
"""
from typing import List
import time
import streamlit as st

import asyncio
import contextlib
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

import numpy as np

from lukhas.core.colonies.advanced_consensus_algorithms import (
    AdvancedColonyConsensus,
    AdvancedConsensusMethod,
    VoteType,
)

# Import existing services
from lukhas.core.container.service_container import get_container
from lukhas.core.events.contracts import (
    ConsensusReached,
    GlyphCreated,
    MemoryFoldCreated,
    QIStateCollapsed,
)

# Import event system
from lukhas.core.events.typed_event_bus import get_typed_event_bus

# Import enhanced core components
from lukhas.core.glyph.glyph_engine_enhanced import get_enhanced_glyph_engine
from lukhas.core.glyph.universal_symbol_protocol import (
    SymbolDomain,
    SymbolModality,
    UniversalSymbol,
)
from lukhas.memory.folds.optimized_fold_engine import OptimizedFoldEngine
from qi.engines.consciousness.qi_processor_enhanced import QIProcessor, QIState

logger = logging.getLogger(__name__)


@dataclass
class CognitiveState:
    """Unified cognitive state across all modules"""

    awareness_level: float = 0.5
    emotional_valence: float = 0.0
    qi_coherence: float = 1.0
    memory_load: float = 0.0
    consensus_confidence: float = 0.0
    active_symbols: set[str] = field(default_factory=set)
    pending_decisions: list[str] = field(default_factory=list)

    def to_symbol(self) -> UniversalSymbol:
        """Convert cognitive state to universal symbol"""
        engine = get_enhanced_glyph_engine()
        return engine.encode_concept(
            "cognitive_state",
            emotion={
                "valence": self.emotional_valence,
                "arousal": self.awareness_level,
            },
            modalities={SymbolModality.CONSCIOUSNESS, SymbolModality.QUANTUM},
            domains={SymbolDomain.COGNITIVE},
            source_module="orchestrator",
        )


class UnifiedCognitiveOrchestrator:
    """
    Unified orchestrator that coordinates all LUKHAS modules using
    enhanced capabilities for seamless integration.
    """

    def __init__(self):
        # Core enhanced components
        self.glyph_engine = get_enhanced_glyph_engine()
        self.memory_engine = OptimizedFoldEngine(max_memory_mb=2048, cache_size=1000, enable_mmap=True)
        self.qi_processor = QIProcessor(num_qubits=8)
        self.consensus_system = AdvancedColonyConsensus("main_colony")

        # Event bus for system-wide communication
        self.event_bus = get_typed_event_bus()

        # Service container for existing modules
        self.container = get_container()

        # Cognitive state
        self.cognitive_state = CognitiveState()

        # Module registrations
        self.registered_modules = {}
        self.module_symbols = {}  # Module -> List[Symbol]

        # Performance tracking
        self.metrics = {
            "thoughts_processed": 0,
            "decisions_made": 0,
            "memories_created": 0,
            "qi_computations": 0,
            "consensus_rounds": 0,
        }

        self._running = False
        self._cognitive_loop_task = None

    async def initialize(self):
        """Initialize the unified orchestrator"""
        logger.info("🧠 Initializing Unified Cognitive Orchestrator...")

        # Initialize event subscriptions
        await self._setup_event_handlers()

        # Register core modules as colony agents
        await self._register_core_modules()

        # Load existing cognitive state from memory
        await self._restore_cognitive_state()

        # Start cognitive processing loop
        self._running = True
        self._cognitive_loop_task = asyncio.create_task(self._cognitive_loop())

        logger.info("✅ Unified Cognitive Orchestrator initialized")

    async def _setup_event_handlers(self):
        """Set up event handlers for cross-module integration"""

        # GLYPH/Symbol events trigger consciousness updates
        async def on_glyph_created(event: GlyphCreated):
            await self._process_new_symbol(event.symbol_id, event.source_module)

        # Memory events update cognitive state
        async def on_memory_created(event: MemoryFoldCreated):
            self.cognitive_state.memory_load = self.memory_engine.get_statistics()["total_size_mb"] / 2048
            await self._update_awareness_from_memory(event.fold_id)

        # Consensus events trigger decisions
        async def on_consensus_reached(event: ConsensusReached):
            await self._execute_consensus_decision(event)

        # Quantum events update coherence
        async def on_quantum_collapse(event: QIStateCollapsed):
            self.cognitive_state.qi_coherence = event.coherence_after

        # Register handlers
        self.event_bus.subscribe(GlyphCreated, on_glyph_created)
        self.event_bus.subscribe(MemoryFoldCreated, on_memory_created)
        self.event_bus.subscribe(ConsensusReached, on_consensus_reached)
        self.event_bus.subscribe(QIStateCollapsed, on_quantum_collapse)

    async def _register_core_modules(self):
        """Register core modules as agents in the colony consensus system"""
        modules = [
            ("consciousness", 1.5),  # Higher weight for consciousness
            ("memory", 1.2),
            ("dream", 1.0),
            ("quantum", 1.3),
            ("emotion", 1.1),
            ("governance", 1.4),  # High weight for ethics
        ]

        for module_name, weight in modules:
            self.consensus_system.register_agent(agent_id=module_name, weight=weight, capabilities=[module_name])
            self.registered_modules[module_name] = {
                "weight": weight,
                "active": True,
                "last_activity": datetime.now(timezone.utc),
            }

    async def _restore_cognitive_state(self):
        """Restore cognitive state from memory"""
        # Look for previous state in memory
        state_fold = self.memory_engine.get_fold("cognitive_state_checkpoint")

        if state_fold:
            stored_state = state_fold.content
            if isinstance(stored_state, dict):
                self.cognitive_state.awareness_level = stored_state.get("awareness_level", 0.5)
                self.cognitive_state.emotional_valence = stored_state.get("emotional_valence", 0.0)
                self.cognitive_state.qi_coherence = stored_state.get("qi_coherence", 1.0)
                logger.info("📂 Restored cognitive state from memory")

    async def _cognitive_loop(self):
        """Main cognitive processing loop"""
        while self._running:
            try:
                # Process pending thoughts
                await self._process_cognitive_cycle()

                # Check for decisions needed
                if self.cognitive_state.pending_decisions:
                    await self._make_decisions()

                # Memory consolidation
                if self.cognitive_state.memory_load > 0.8:
                    await self._consolidate_memories()

                # Quantum coherence maintenance
                if self.cognitive_state.qi_coherence < 0.5:
                    await self._restore_quantum_coherence()

                # Save cognitive state periodically
                await self._checkpoint_cognitive_state()

                # Brief pause
                await asyncio.sleep(0.1)

            except Exception as e:
                logger.error(f"Error in cognitive loop: {e}")
                await asyncio.sleep(1)

    async def _process_cognitive_cycle(self):
        """Process one cycle of cognitive activity"""
        # Create a thought symbol representing current state
        thought_symbol = self.cognitive_state.to_symbol()

        # Process through different modalities
        # 1. Consciousness processing
        self.glyph_engine.translate_for_module(thought_symbol, "consciousness")

        # 2. Emotional analysis
        self.glyph_engine.translate_for_module(thought_symbol, "emotion")

        # 3. Memory encoding
        await self._encode_to_memory(thought_symbol)

        # 4. Quantum processing for complex decisions
        if self.cognitive_state.pending_decisions:
            await self._quantum_process_decisions()

        self.metrics["thoughts_processed"] += 1

    async def _process_new_symbol(self, symbol_id: str, source_module: str):
        """Process a new symbol from any module"""
        # Track active symbols
        self.cognitive_state.active_symbols.add(symbol_id)

        # Limit active symbols
        if len(self.cognitive_state.active_symbols) > 100:
            # Remove oldest symbols
            oldest = list(self.cognitive_state.active_symbols)[:50]
            for old_id in oldest:
                self.cognitive_state.active_symbols.discard(old_id)

        # Update module activity
        if source_module in self.registered_modules:
            self.registered_modules[source_module]["last_activity"] = datetime.now(timezone.utc)

        # Find related symbols across modules
        if symbol_id in self.glyph_engine.universal_protocol.symbol_registry:
            symbol = self.glyph_engine.universal_protocol.symbol_registry[symbol_id]
            related = self.glyph_engine.find_related_symbols(symbol, max_depth=2)

            # Create cross-module links
            for symbols in related.values():
                for related_symbol in symbols[:3]:  # Limit connections
                    self.glyph_engine.create_cross_module_link(symbol, related_symbol, link_type="semantic")

    async def _make_decisions(self):
        """Make decisions using advanced consensus"""
        for decision_id in self.cognitive_state.pending_decisions[:5]:  # Process up to 5
            # Create consensus proposal
            proposal_id = await self.consensus_system.propose(
                content=decision_id,
                proposer="orchestrator",
                method=AdvancedConsensusMethod.QUANTUM_SUPERPOSITION,
            )

            # Get module votes using quantum superposition
            for module_name in self.registered_modules:
                # Create quantum vote based on module state
                amplitudes = self._calculate_vote_amplitudes(module_name, decision_id)

                await self.consensus_system.qi_superposition_vote(
                    proposal_id,
                    module_name,
                    amplitudes,
                    entangle_with=[
                        "consciousness",
                        "governance",
                    ],  # Entangle key modules
                )

            # Reach consensus
            outcome = await self.consensus_system.reach_consensus(proposal_id)

            # Update cognitive state
            self.cognitive_state.consensus_confidence = outcome.confidence

            # Execute decision
            await self._execute_consensus_decision(outcome)

            # Remove from pending
            self.cognitive_state.pending_decisions.remove(decision_id)

            self.metrics["decisions_made"] += 1
            self.metrics["consensus_rounds"] += 1

    def _calculate_vote_amplitudes(self, module: str, decision: str) -> dict[VoteType, complex]:
        """Calculate quantum vote amplitudes for a module"""
        # Module-specific voting patterns
        if module == "governance":
            # Ethics module is conservative
            return {
                VoteType.APPROVE: complex(0.3, 0.1),
                VoteType.REJECT: complex(0.7, 0.2),
                VoteType.ABSTAIN: complex(0.1, 0.0),
            }
        elif module == "dream":
            # Dream module is creative/explorative
            return {
                VoteType.APPROVE: complex(0.8, 0.3),
                VoteType.REJECT: complex(0.1, 0.1),
                VoteType.ABSTAIN: complex(0.2, 0.1),
            }
        else:
            # Default balanced vote
            return {
                VoteType.APPROVE: complex(0.5, 0.2),
                VoteType.REJECT: complex(0.4, 0.2),
                VoteType.ABSTAIN: complex(0.3, 0.1),
            }

    async def _execute_consensus_decision(self, outcome):
        """Execute a decision reached through consensus"""
        if outcome.is_approved:
            # Create action symbol
            action_symbol = self.glyph_engine.encode_concept(
                f"execute_{outcome.proposal_id}",
                modalities={SymbolModality.CAUSAL},
                domains={SymbolDomain.COGNITIVE},
                source_module="orchestrator",
            )

            # Store decision in memory
            await self._encode_to_memory(action_symbol)

            # Update awareness
            self.cognitive_state.awareness_level = min(1.0, self.cognitive_state.awareness_level + 0.1)

    async def _encode_to_memory(self, symbol: UniversalSymbol):
        """Encode a symbol to optimized memory"""
        fold = self.memory_engine.create_fold(
            key=symbol.symbol_id,
            content={
                "symbol": symbol,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "cognitive_state": {
                    "awareness": self.cognitive_state.awareness_level,
                    "valence": self.cognitive_state.emotional_valence,
                },
            },
            tags=["cognitive", "symbol"] + [d.value for d in symbol.domains],
        )

        self.metrics["memories_created"] += 1

        # Emit event
        self.event_bus.publish(
            MemoryFoldCreated(
                fold_id=fold.key,
                content_hash=fold.content_hash,
                emotional_context={"valence": self.cognitive_state.emotional_valence},
                compression_ratio=fold.compression_ratio,
                source_module="orchestrator",
            )
        )

        return fold

    async def _update_awareness_from_memory(self, fold_id: str):
        """Update awareness based on memory content"""
        fold = self.memory_engine.get_fold(fold_id)
        if fold and isinstance(fold.content, dict):
            # Extract emotional context
            if "cognitive_state" in fold.content:
                past_awareness = fold.content["cognitive_state"].get("awareness", 0.5)
                # Blend with current awareness
                self.cognitive_state.awareness_level = 0.7 * self.cognitive_state.awareness_level + 0.3 * past_awareness

    async def _consolidate_memories(self):
        """Consolidate memories using compression"""
        logger.info("🗜️ Consolidating memories...")

        # Get recent memory folds
        recent_folds = []
        for key in list(self.memory_engine.index.by_key.keys())[:100]:
            fold = self.memory_engine.get_fold(key)
            if fold:
                recent_folds.append(fold)

        # Extract symbols from folds
        symbols_to_compress = []
        for fold in recent_folds:
            if isinstance(fold.content, dict) and "symbol" in fold.content:
                symbols_to_compress.append(fold.content["symbol"])

        if len(symbols_to_compress) > 10:
            # Compress symbols
            compressed = self.glyph_engine.universal_protocol.compress_symbols(symbols_to_compress[:50])

            # Store compressed state
            self.memory_engine.create_fold(
                key=f"consolidated_{datetime.now(timezone.utc).timestamp()}",
                content=compressed,
                tags=["consolidation", "compressed"],
            )

            # Optimize memory storage
            self.memory_engine.deduplicate()
            self.memory_engine.optimize_storage()

            # Update memory load
            stats = self.memory_engine.get_statistics()
            self.cognitive_state.memory_load = stats["total_size_mb"] / 2048

    async def _quantum_process_decisions(self):
        """Use quantum processor for complex decisions"""
        # Create quantum state from pending decisions
        num_decisions = min(len(self.cognitive_state.pending_decisions), 4)

        if num_decisions > 0:
            # Use Grover's search to find optimal decision
            def oracle(index: int) -> bool:
                # Simple oracle: prefer even indices (simplified)
                return index % 2 == 0

            optimal_index = self.qi_processor.grover_search(oracle, num_iterations=2)

            # Create quantum state for decision
            self.qi_processor.create_bell_pair()

            self.metrics["qi_computations"] += 1
            self.cognitive_state.qi_coherence *= 0.95  # Decoherence

            return optimal_index

    async def _restore_quantum_coherence(self):
        """Restore quantum coherence through error correction"""
        logger.info("⚛️ Restoring quantum coherence...")

        # Create test quantum state
        test_state = QIState(
            num_qubits=2,
            amplitudes=np.array([0.5, 0.5, 0.5, 0.5]),
            coherence=self.cognitive_state.qi_coherence,
        )

        # Apply error correction
        corrected = self.qi_processor.apply_error_correction(test_state)

        # Update cognitive state
        self.cognitive_state.qi_coherence = corrected.coherence

    async def _checkpoint_cognitive_state(self):
        """Save cognitive state checkpoint to memory"""
        # Create checkpoint every 100 thoughts
        if self.metrics["thoughts_processed"] % 100 == 0:
            checkpoint = {
                "awareness_level": self.cognitive_state.awareness_level,
                "emotional_valence": self.cognitive_state.emotional_valence,
                "qi_coherence": self.cognitive_state.qi_coherence,
                "memory_load": self.cognitive_state.memory_load,
                "consensus_confidence": self.cognitive_state.consensus_confidence,
                "metrics": self.metrics.copy(),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            self.memory_engine.create_fold(
                key="cognitive_state_checkpoint",
                content=checkpoint,
                tags=["checkpoint", "cognitive_state"],
            )

    async def process_thought(self, thought: str, context: Optional[dict[str, Any]] = None):
        """
        Process a thought through the unified cognitive system.
        This is the main interface for external input.
        """
        # Create thought symbol
        thought_symbol = self.glyph_engine.encode_concept(
            thought,
            emotion=context.get("emotion") if context else None,
            modalities={SymbolModality.TEXT, SymbolModality.CONSCIOUSNESS},
            domains={SymbolDomain.COGNITIVE},
            source_module="input",
        )

        # Create cognitive chain
        self.glyph_engine.create_cognitive_chain(
            ["perceive", thought, "analyze", "decide", "act"],
            source_module="orchestrator",
        )

        # Process through all modules
        results = {}

        # Consciousness processing
        consciousness_result = self.glyph_engine.translate_for_module(thought_symbol, "consciousness")
        results["consciousness"] = consciousness_result

        # Memory encoding
        memory_fold = await self._encode_to_memory(thought_symbol)
        results["memory"] = memory_fold.key

        # Emotional analysis
        emotion_result = self.glyph_engine.translate_for_module(thought_symbol, "emotion")
        results["emotion"] = emotion_result

        # If decision needed, add to pending
        if "decide" in thought.lower() or "?" in thought:
            self.cognitive_state.pending_decisions.append(thought_symbol.symbol_id)

        return {
            "thought_id": thought_symbol.symbol_id,
            "processing_results": results,
            "cognitive_state": {
                "awareness": self.cognitive_state.awareness_level,
                "valence": self.cognitive_state.emotional_valence,
                "coherence": self.cognitive_state.qi_coherence,
            },
        }

    async def get_system_status(self) -> dict[str, Any]:
        """Get comprehensive system status"""
        memory_stats = self.memory_engine.get_statistics()
        qi_stats = self.qi_processor.get_statistics()
        glyph_stats = self.glyph_engine.get_system_statistics()
        consensus_history = self.consensus_system.get_consensus_history()

        return {
            "cognitive_state": {
                "awareness_level": self.cognitive_state.awareness_level,
                "emotional_valence": self.cognitive_state.emotional_valence,
                "qi_coherence": self.cognitive_state.qi_coherence,
                "memory_load": self.cognitive_state.memory_load,
                "consensus_confidence": self.cognitive_state.consensus_confidence,
                "active_symbols": len(self.cognitive_state.active_symbols),
                "pending_decisions": len(self.cognitive_state.pending_decisions),
            },
            "metrics": self.metrics,
            "memory": {
                "total_folds": memory_stats["total_folds"],
                "cache_hit_rate": memory_stats["cache_hit_rate"],
                "compression_ratio": memory_stats["avg_compression_ratio"],
                "size_mb": memory_stats["total_size_mb"],
            },
            "quantum": qi_stats,
            "symbols": {
                "total": glyph_stats["total_symbols"],
                "by_module": glyph_stats["module_breakdown"],
                "cross_links": glyph_stats["cross_module_links"],
            },
            "consensus": {
                "total_decisions": len(consensus_history),
                "recent": consensus_history[-5:] if consensus_history else [],
            },
        }

    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("🛑 Shutting down Unified Cognitive Orchestrator...")

        self._running = False

        if self._cognitive_loop_task:
            self._cognitive_loop_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._cognitive_loop_task

        # Final checkpoint
        await self._checkpoint_cognitive_state()

        # Cleanup
        self.memory_engine.shutdown()

        logger.info("✅ Unified Cognitive Orchestrator shutdown complete")


# Demonstration function
async def demo_unified_orchestration():
    """Demonstrate the unified cognitive orchestration"""

    print("🎭 Unified Cognitive Orchestrator Demo")
    print("=" * 60)

    orchestrator = UnifiedCognitiveOrchestrator()
    await orchestrator.initialize()

    print("\n1️⃣ Processing Complex Thought:")

    result = await orchestrator.process_thought(
        "Should we increase processing resources to handle the increased load?",
        context={"emotion": {"concern": 0.7, "anticipation": 0.5}
    )

    print(f"   Thought ID: {result['thought_id']}")
    print(f"   Awareness: {result['cognitive_state']['awareness']:.3f}")
    print(f"   Quantum Coherence: {result['cognitive_state']['coherence']:.3f}")

    # Let system process
    await asyncio.sleep(2)

    print("\n2️⃣ System Status:")

    status = await orchestrator.get_system_status()

    print(f"   Active Symbols: {status['cognitive_state']['active_symbols']}")
    print(f"   Pending Decisions: {status['cognitive_state']['pending_decisions']}")
    print(f"   Memory Load: {status['cognitive_state']['memory_load']:.3f}")
    print(f"   Thoughts Processed: {status['metrics']['thoughts_processed']}")

    print("\n3️⃣ Processing Multiple Thoughts:")

    thoughts = [
        "Remember the importance of ethical considerations",
        "Dream about creative solutions to complex problems",
        "Analyze quantum entanglement patterns",
        "Feel the emotional resonance of decisions",
    ]

    for thought in thoughts:
        await orchestrator.process_thought(thought)
        await asyncio.sleep(0.5)

    print("\n4️⃣ Final System Statistics:")

    final_status = await orchestrator.get_system_status()

    print(f"   Total Symbols: {final_status['symbols']['total']}")
    print(f"   Memory Folds: {final_status['memory']['total_folds']}")
    print(f"   Cache Hit Rate: {final_status['memory']['cache_hit_rate']:.3%}")
    print(f"   Decisions Made: {final_status['metrics']['decisions_made']}")
    print(f"   Quantum Computations: {final_status['metrics']['qi_computations']}")

    # Module breakdown
    print("\n   Module Activity:")
    for module, stats in final_status["symbols"]["by_module"].items():
        print(f"      {module}: {stats['count']} symbols, {stats['links']} links")

    await orchestrator.shutdown()

    print("\n✅ Unified orchestration demonstration complete!")


if __name__ == "__main__":
    asyncio.run(demo_unified_orchestration())