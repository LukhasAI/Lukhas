"""
🔗 LUKHAS Integration for Endocrine Signal System

Connects endocrine modulation system with LUKHAS consciousness modules,
emitting signals from various systems and orchestrating LLM interactions.

Trinity Framework: ⚛️🧠🛡️
- ⚛️ Identity: Authentic signal emission from consciousness modules
- 🧠 Consciousness: Memory and learning from signal patterns
- 🛡️ Guardian: Safety-first signal validation and response
"""

import asyncio
import time
from typing import Any

from .openai_integration import ModulatedOpenAIClient, build_function_definitions
from .signals import ModulationParams, Signal, SignalModulator


class EndocrineSignalEmitter:
    """Emits endocrine signals from various LUKHAS modules"""

    def __init__(self, signal_bus=None):
        """Initialize with optional signal bus for system integration"""
        self.signal_bus = signal_bus

    async def emit_guardian_signals(self, action_context: dict) -> list[Signal]:
        """Emit signals from Guardian/Ethics systems"""
        signals = []

        # Check alignment risk based on action context
        risk_score = await self._assess_alignment_risk(action_context)
        if risk_score > 0.1:
            signals.append(
                Signal(
                    name="alignment_risk",
                    level=risk_score,
                    source="guardian",
                    audit_id=action_context.get("audit_id", ""),
                    ttl_ms=2000,  # Longer TTL for safety signals
                )
            )

        return signals

    async def emit_memory_signals(self, memory_context: dict) -> list[Signal]:
        """Emit signals from Memory system"""
        signals = []

        # Memory stress (too much to process)
        queue_length = memory_context.get("queue_length", 0)
        if queue_length > 100:
            stress_level = min(1.0, queue_length / 1000)
            signals.append(
                Signal(
                    name="stress",
                    level=stress_level,
                    source="memory",
                    audit_id=memory_context.get("audit_id", ""),
                )
            )

        # Trust signal based on memory confidence
        confidence = memory_context.get("confidence", 0.5)
        if confidence > 0.7:
            signals.append(
                Signal(
                    name="trust",
                    level=confidence,
                    source="memory",
                    audit_id=memory_context.get("audit_id", ""),
                )
            )

        return signals

    async def emit_consciousness_signals(self, consciousness_state: dict) -> list[Signal]:
        """Emit signals from Consciousness system"""
        signals = []

        # Novelty (new experiences, creative opportunities)
        novelty_score = consciousness_state.get("novelty_metric", 0.0)
        if novelty_score > 0.2:
            signals.append(
                Signal(
                    name="novelty",
                    level=novelty_score,
                    source="consciousness",
                    audit_id=consciousness_state.get("audit_id", ""),
                )
            )

        # Ambiguity (unclear inputs requiring deeper analysis)
        ambiguity_score = consciousness_state.get("ambiguity_metric", 0.0)
        if ambiguity_score > 0.3:
            signals.append(
                Signal(
                    name="ambiguity",
                    level=ambiguity_score,
                    source="consciousness",
                    audit_id=consciousness_state.get("audit_id", ""),
                )
            )

        return signals

    async def emit_orchestration_signals(self, orchestration_context: dict) -> list[Signal]:
        """Emit signals from Orchestration system"""
        signals = []

        # Urgency based on task priority and deadlines
        urgency_score = orchestration_context.get("urgency_metric", 0.0)
        if urgency_score > 0.4:
            signals.append(
                Signal(
                    name="urgency",
                    level=urgency_score,
                    source="orchestration",
                    audit_id=orchestration_context.get("audit_id", ""),
                )
            )

        return signals

    async def emit_universal_language_signals(self, language_context: dict) -> list[Signal]:
        """Emit signals from Universal Language system"""
        signals = []

        # Communication novelty (new symbolic patterns)
        symbol_novelty = language_context.get("symbol_novelty", 0.0)
        if symbol_novelty > 0.3:
            signals.append(
                Signal(
                    name="novelty",
                    level=symbol_novelty,
                    source="universal_language",
                    audit_id=language_context.get("audit_id", ""),
                )
            )

        # Communication ambiguity (unclear symbolic meaning)
        symbol_ambiguity = language_context.get("symbol_ambiguity", 0.0)
        if symbol_ambiguity > 0.4:
            signals.append(
                Signal(
                    name="ambiguity",
                    level=symbol_ambiguity,
                    source="universal_language",
                    audit_id=language_context.get("audit_id", ""),
                )
            )

        return signals

    async def _assess_alignment_risk(self, context: dict) -> float:
        """Assess alignment risk based on action context"""
        # This would integrate with actual Guardian system
        # For now, return a mock assessment

        risk_factors = []

        # Check for potentially harmful content
        if context.get("contains_harmful_content", False):
            risk_factors.append(0.8)

        # Check for privacy violations
        if context.get("privacy_risk", False):
            risk_factors.append(0.6)

        # Check for bias concerns
        if context.get("bias_detected", False):
            risk_factors.append(0.4)

        # Return maximum risk factor
        return max(risk_factors) if risk_factors else 0.0


class EndocrineLLMOrchestrator:
    """Main orchestrator coordinating signals and LLM interactions"""

    def __init__(self, modulator: SignalModulator, openai_client: ModulatedOpenAIClient):
        """Initialize with modulator and OpenAI client"""
        self.modulator = modulator
        self.openai_client = openai_client
        self.signal_emitter = EndocrineSignalEmitter()

        # Interaction history for learning
        self.interaction_history: list[dict] = []

    async def process_consciousness_query(self, user_query: str, context: dict) -> dict[str, Any]:
        """Process query through endocrine-modulated consciousness pipeline"""

        # Gather signals from all LUKHAS systems
        all_signals = await self._gather_system_signals(context)

        # Get modulation parameters
        params = self.modulator.combine_signals(all_signals)

        # Retrieve relevant context based on modulated retrieval_k
        context_snippets = await self._retrieve_context(user_query, params.retrieval_k)

        # Get available functions based on tool allowlist
        functions = build_function_definitions(params.tool_allowlist)

        # Make modulated LLM call
        result = self.openai_client.create_completion(
            user_message=user_query,
            signals=all_signals,
            context_snippets=context_snippets,
            functions=functions,
        )

        # Store interaction if memory write strength is sufficient
        if params.memory_write > 0.5:
            await self._store_consciousness_memory(user_query, result, params)

        # Learn from interaction
        await self._learn_from_interaction(user_query, result, params)

        return result

    async def _gather_system_signals(self, context: dict) -> list[Signal]:
        """Gather signals from all LUKHAS systems"""
        all_signals = []

        # Guardian signals
        guardian_context = context.get("guardian", {})
        guardian_signals = await self.signal_emitter.emit_guardian_signals(guardian_context)
        all_signals.extend(guardian_signals)

        # Memory signals
        memory_context = context.get("memory", {})
        memory_signals = await self.signal_emitter.emit_memory_signals(memory_context)
        all_signals.extend(memory_signals)

        # Consciousness signals
        consciousness_context = context.get("consciousness", {})
        consciousness_signals = await self.signal_emitter.emit_consciousness_signals(consciousness_context)
        all_signals.extend(consciousness_signals)

        # Orchestration signals
        orchestration_context = context.get("orchestration", {})
        orchestration_signals = await self.signal_emitter.emit_orchestration_signals(orchestration_context)
        all_signals.extend(orchestration_signals)

        # Universal Language signals
        language_context = context.get("universal_language", {})
        language_signals = await self.signal_emitter.emit_universal_language_signals(language_context)
        all_signals.extend(language_signals)

        return all_signals

    async def _retrieve_context(self, query: str, k: int) -> list[str]:
        """Retrieve relevant context from consciousness systems"""
        # This would integrate with actual memory/retrieval systems
        # For now, return mock context snippets

        context_snippets = [
            f"Memory context {i + 1}: Related to '{query}' with relevance score {0.9 - i * 0.1:.1f}"
            for i in range(min(k, 5))
        ]

        return context_snippets

    async def _store_consciousness_memory(self, query: str, result: dict, params: ModulationParams):
        """Store interaction in consciousness memory systems"""
        # This would integrate with actual memory systems
        memory_entry = {
            "timestamp": time.time(),
            "query": query,
            "response_success": result.get("success", False),
            "signal_context": params.signal_context,
            "prompt_style": params.prompt_style,
            "memory_strength": params.memory_write,
            "audit_id": params.audit_id,
        }

        # Store with strength-based persistence
        if params.memory_write > 0.8:
            # High-importance memory
            print(f"💾 Storing high-importance memory: {memory_entry['audit_id']}")
        elif params.memory_write > 0.5:
            # Medium-importance memory
            print(f"💾 Storing medium-importance memory: {memory_entry['audit_id']}")

    async def _learn_from_interaction(self, query: str, result: dict, params: ModulationParams):
        """Learn from interaction patterns to improve future modulation"""
        # Store interaction in history
        interaction = {
            "timestamp": time.time(),
            "query": query,
            "success": result.get("success", False),
            "error": result.get("error"),
            "signal_context": params.signal_context,
            "modulation_params": {
                "temperature": params.temperature,
                "max_tokens": params.max_tokens,
                "prompt_style": params.prompt_style,
            },
        }

        self.interaction_history.append(interaction)

        # Keep only recent interactions for learning
        if len(self.interaction_history) > 100:
            self.interaction_history = self.interaction_history[-100:]

        # Basic pattern analysis (could be expanded)
        await self._analyze_interaction_patterns()

    async def _analyze_interaction_patterns(self):
        """Analyze interaction patterns for learning insights"""
        if len(self.interaction_history) < 10:
            return

        # Analyze recent success rates by prompt style
        recent_interactions = self.interaction_history[-20:]
        style_success = {}

        for interaction in recent_interactions:
            style = interaction["modulation_params"]["prompt_style"]
            if style not in style_success:
                style_success[style] = {"success": 0, "total": 0}

            style_success[style]["total"] += 1
            if interaction["success"]:
                style_success[style]["success"] += 1

        # Print insights
        for style, stats in style_success.items():
            success_rate = stats["success"] / stats["total"] if stats["total"] > 0 else 0
            if stats["total"] >= 3:  # Only report on styles with enough data
                print(f"📊 Style '{style}' success rate: {success_rate:.1%} ({stats['success']}/{stats['total']})")


# Example usage and integration test
async def example_usage():
    """Example of the complete endocrine modulation system"""

    # Create modulator and OpenAI client
    modulator = SignalModulator()
    try:
        openai_client = ModulatedOpenAIClient(modulator)
    except ImportError:
        print("⚠️ OpenAI not available, using mock client")
        return

    # Create orchestrator
    orchestrator = EndocrineLLMOrchestrator(modulator, openai_client)

    # Simulate consciousness query with system context
    context = {
        "guardian": {
            "contains_harmful_content": False,
            "privacy_risk": False,
            "audit_id": "test-001",
        },
        "memory": {
            "queue_length": 150,  # Will generate stress signal
            "confidence": 0.8,  # Will generate trust signal
            "audit_id": "test-001",
        },
        "consciousness": {
            "novelty_metric": 0.7,  # Will generate novelty signal
            "ambiguity_metric": 0.2,
            "audit_id": "test-001",
        },
    }

    # Process query
    try:
        result = await orchestrator.process_consciousness_query(
            user_query="How should LUKHAS integrate bio-inspired consciousness patterns?",
            context=context,
        )

        print("🧠 Consciousness Query Result:")
        print(f"   Success: {result.get('success', False)}")
        print(f"   Audit ID: {result.get('audit_id', 'unknown')}")
        if result.get("modulation_params"):
            params = result["modulation_params"]
            print(f"   Temperature: {params.temperature:.2f}")
            print(f"   Style: {params.prompt_style}")
            print(f"   Active signals: {list(params.signal_context.keys())}")

    except Exception as e:
        print(f"❌ Error in consciousness processing: {e}")


if __name__ == "__main__":
    asyncio.run(example_usage())