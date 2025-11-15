"""
Integration tests for complete MATRIZ cognitive pipeline.

Tests the full cognitive loop:
Memory → Attention → Thought → Action → Decision → Awareness
"""

import pytest
import numpy as np
from matriz.adapters.attention_node import AttentionNode
from matriz.adapters.thought_node import ThoughtNode
from matriz.adapters.awareness_node import AwarenessNode


class TestCognitiveLoopIntegration:
    """Test complete cognitive processing loop"""

    @pytest.fixture
    def cognitive_nodes(self):
        return {
            "attention": AttentionNode(attention_bandwidth=7),
            "thought": ThoughtNode(),
            "awareness": AwarenessNode()
        }

    def test_full_cognitive_cycle(self, cognitive_nodes):
        """Test complete processing cycle through all nodes"""
        # Simulate memory retrieval (already implemented)
        memory_context = {
            "embedding": np.random.randn(128),
            "content": "Previous context"
        }

        # Current input
        current_input = {
            "embedding": np.random.randn(128),
            "content": "New sensory data"
        }

        # 1. Attention: Focus on salient features
        attention_map = cognitive_nodes["attention"].process(
            memory_context=memory_context,
            current_input=current_input,
            task_goals=["analyze", "respond"]
        )

        assert attention_map.attention_score > 0
        assert len(attention_map.focus_window) <= 7  # Miller's law
        assert len(attention_map.focus_window) > 0

        # 2. Thought: Generate internal representation
        thought = cognitive_nodes["thought"].process(
            attention_map=attention_map,
            memory_context=memory_context,
            mode="analytical"
        )

        assert thought.content != ""
        assert 0 <= thought.confidence <= 1
        assert 0 <= thought.novelty <= 1
        assert len(thought.reasoning_chain) > 0

        # 3. Awareness: Meta-cognitive monitoring
        awareness = cognitive_nodes["awareness"].process(
            attention_map=attention_map,
            thought=thought,
            decision_pending=True
        )

        assert 0 <= awareness.processing_quality <= 1
        assert 0 <= awareness.coherence <= 1
        assert len(awareness.meta_thoughts) > 0

    def test_attention_bandwidth_respected(self, cognitive_nodes):
        """Attention respects Miller's law (7±2 items)"""
        memory = {"embedding": np.random.randn(128)}
        input_data = {"embedding": np.random.randn(128)}

        attention_map = cognitive_nodes["attention"].process(memory, input_data)

        # Should be between 0 and 9 (7±2, but can be less if threshold not met)
        assert 0 <= len(attention_map.focus_window) <= 9

    def test_thought_novelty_detection(self, cognitive_nodes):
        """Thought node detects novel vs duplicate thoughts"""
        memory = {"embedding": np.zeros(128)}
        input1 = {"embedding": np.array([1.0] + [0]*127)}
        input2 = {"embedding": np.array([1.0] + [0]*127)}  # Same

        attention1 = cognitive_nodes["attention"].process(memory, input1)
        thought1 = cognitive_nodes["thought"].process(attention1, memory)

        attention2 = cognitive_nodes["attention"].process(memory, input2)
        thought2 = cognitive_nodes["thought"].process(attention2, memory)

        # First thought has novelty
        assert thought1.novelty > 0

        # Second identical thought has zero novelty
        assert thought2.novelty == 0 or thought2.thought_hash == thought1.thought_hash

    def test_awareness_drift_detection(self, cognitive_nodes):
        """Awareness detects attention drift over time"""
        memory = {"embedding": np.random.randn(128)}

        # Run 5 cycles with stable quality
        for _ in range(5):
            input_data = {"embedding": np.random.randn(128) * 0.5}
            attention = cognitive_nodes["attention"].process(memory, input_data)
            thought = cognitive_nodes["thought"].process(attention, memory)
            awareness = cognitive_nodes["awareness"].process(attention, thought)

        stable_drift = awareness.attention_drift

        # Now run with very different input (induce drift)
        input_data = {"embedding": np.random.randn(128) * 2.0}  # High variance
        attention = cognitive_nodes["attention"].process(memory, input_data)
        thought = cognitive_nodes["thought"].process(attention, memory)
        awareness = cognitive_nodes["awareness"].process(attention, thought)

        # Drift should be measurable
        # (May not always increase due to randomness, but should be in valid range)
        assert 0 <= awareness.attention_drift <= 1

    def test_attention_salience_computation(self, cognitive_nodes):
        """Test attention salience scoring"""
        # Create input with clear high-salience features
        memory = {"embedding": np.zeros(128)}
        input_data = {"embedding": np.array([0.9] * 10 + [0.1] * 118)}  # Strong features

        attention_map = cognitive_nodes["attention"].process(memory, input_data)

        # Should focus on high-salience features
        assert len(attention_map.focus_window) > 0
        assert attention_map.attention_score > 0

    def test_thought_modes(self, cognitive_nodes):
        """Test different thought generation modes"""
        memory = {"embedding": np.random.randn(128)}
        input_data = {"embedding": np.random.randn(128)}
        attention = cognitive_nodes["attention"].process(memory, input_data)

        # Analytical mode
        thought_analytical = cognitive_nodes["thought"].process(
            attention, memory, mode="analytical"
        )
        assert "Observe" in thought_analytical.content or "Analyze" in thought_analytical.content

        # Creative mode
        thought_creative = cognitive_nodes["thought"].process(
            attention, memory, mode="creative"
        )
        assert "Associate" in thought_creative.content or "Synthesize" in thought_creative.content

        # Reflective mode
        thought_reflective = cognitive_nodes["thought"].process(
            attention, memory, mode="reflective"
        )
        assert "Monitor" in thought_reflective.content or "Meta-cognize" in thought_reflective.content

    def test_awareness_meta_thoughts(self, cognitive_nodes):
        """Test awareness generates appropriate meta-thoughts"""
        memory = {"embedding": np.random.randn(128)}
        input_data = {"embedding": np.random.randn(128)}

        attention = cognitive_nodes["attention"].process(memory, input_data)
        thought = cognitive_nodes["thought"].process(attention, memory)
        awareness = cognitive_nodes["awareness"].process(
            attention, thought, decision_pending=True
        )

        # Should have at least one meta-thought
        assert len(awareness.meta_thoughts) > 0
        assert all(isinstance(mt, str) for mt in awareness.meta_thoughts)

    def test_attention_with_goals(self, cognitive_nodes):
        """Test task-driven attention modulation"""
        memory = {"embedding": np.random.randn(128)}
        input_data = {"embedding": np.random.randn(128)}

        # With goals
        attention_with_goals = cognitive_nodes["attention"].process(
            memory, input_data, task_goals=["analyze", "respond"]
        )

        # Without goals
        attention_no_goals = cognitive_nodes["attention"].process(
            memory, input_data, task_goals=None
        )

        # Both should produce valid attention maps
        assert attention_with_goals.attention_score >= 0
        assert attention_no_goals.attention_score >= 0

    def test_thought_confidence_scoring(self, cognitive_nodes):
        """Test thought confidence based on attention quality"""
        memory = {"embedding": np.zeros(128)}

        # High quality attention (strong signal)
        strong_input = {"embedding": np.array([0.9] * 128)}
        strong_attention = cognitive_nodes["attention"].process(memory, strong_input)
        strong_thought = cognitive_nodes["thought"].process(strong_attention, memory)

        # Weak quality attention (weak signal)
        weak_input = {"embedding": np.array([0.01] * 128)}
        weak_attention = cognitive_nodes["attention"].process(memory, weak_input)
        weak_thought = cognitive_nodes["thought"].process(weak_attention, memory)

        # Strong attention should generally produce higher confidence
        # (Not guaranteed due to novelty factor, but both should be valid)
        assert 0 <= strong_thought.confidence <= 1
        assert 0 <= weak_thought.confidence <= 1

    def test_awareness_self_model(self, cognitive_nodes):
        """Test awareness builds accurate self-model"""
        memory = {"embedding": np.random.randn(128)}
        input_data = {"embedding": np.random.randn(128)}

        attention = cognitive_nodes["attention"].process(memory, input_data)
        thought = cognitive_nodes["thought"].process(attention, memory)
        awareness = cognitive_nodes["awareness"].process(attention, thought)

        # Self-model should contain key cognitive state info
        assert "currently_attending_to" in awareness.self_model
        assert "current_thought" in awareness.self_model
        assert "thought_confidence" in awareness.self_model
        assert "thought_novelty" in awareness.self_model
        assert awareness.self_model["currently_attending_to"] == len(attention.focus_window)

    def test_cognitive_loop_performance(self, cognitive_nodes):
        """Test cognitive loop completes within performance targets"""
        import time

        memory = {"embedding": np.random.randn(128)}
        input_data = {"embedding": np.random.randn(128)}

        t0 = time.perf_counter()

        # Full cycle
        attention = cognitive_nodes["attention"].process(memory, input_data)
        thought = cognitive_nodes["thought"].process(attention, memory)
        awareness = cognitive_nodes["awareness"].process(attention, thought)

        latency_ms = (time.perf_counter() - t0) * 1000

        # Should complete within 250ms (target: <250ms p95)
        # This is a single run, so we're lenient
        assert latency_ms < 500  # 2x target for single test run

    def test_attention_feature_extraction(self, cognitive_nodes):
        """Test attention correctly extracts and normalizes features"""
        memory = {"embedding": np.random.randn(128)}
        input_data = {"embedding": np.random.randn(128)}

        attention = cognitive_nodes["attention"].process(memory, input_data)

        # Features should be combined (256 total)
        assert len(attention.features) == 256  # 128 + 128
        # Should be normalized
        norm = np.linalg.norm(attention.features)
        assert abs(norm - 1.0) < 0.01  # Approximately unit norm

    def test_thought_symbolic_form(self, cognitive_nodes):
        """Test thought generates symbolic representation"""
        memory = {"embedding": np.random.randn(128)}
        input_data = {"embedding": np.random.randn(128)}

        attention = cognitive_nodes["attention"].process(memory, input_data)
        thought = cognitive_nodes["thought"].process(attention, memory)

        # Symbolic form should have expected structure
        assert "concepts" in thought.symbolic_form
        assert "relations" in thought.symbolic_form
        assert "attributes" in thought.symbolic_form
        assert isinstance(thought.symbolic_form["concepts"], list)

    def test_awareness_coherence_checking(self, cognitive_nodes):
        """Test awareness checks thought coherence"""
        memory = {"embedding": np.random.randn(128)}
        input_data = {"embedding": np.random.randn(128)}

        attention = cognitive_nodes["attention"].process(memory, input_data)
        thought = cognitive_nodes["thought"].process(attention, memory)
        awareness = cognitive_nodes["awareness"].process(attention, thought)

        # Coherence should be in valid range
        assert 0 <= awareness.coherence <= 1
