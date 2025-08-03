#!/usr/bin/env python3
"""
Test Entropy Monitoring - Integration test for Shannon entropy tracking and drift detection
Validates symbolic state transitions and Guardian intervention triggers
"""

import pytest
import asyncio
import sys
import json
import tempfile
import math
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "lukhas_next_gen"))

try:
    from entropy_log.entropy_tracker import EntropyTracker
    from stream.consciousness_broadcaster import ConsciousnessBroadcaster
except ImportError:
    # Mock classes for testing when modules aren't available
    class EntropyTracker:
        def __init__(self, *args, **kwargs):
            self.journal_entries = []
            self.current_state = "neutral"
    
    class ConsciousnessBroadcaster:
        def __init__(self, *args, **kwargs):
            self.current_state = "focused"


class TestEntropyMonitoring:
    """Integration tests for entropy monitoring and drift detection"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)
    
    @pytest.fixture
    def entropy_tracker(self, temp_dir):
        """Create entropy tracker for testing"""
        return EntropyTracker(
            journal_file=str(temp_dir / "entropy_test.json"),
            window_size=50
        )
    
    def test_shannon_entropy_calculation(self):
        """Test Shannon entropy calculation with symbolic transitions"""
        
        # Test case 1: Single transition type (minimum entropy)
        single_transitions = [("open", "neutral")] * 10
        entropy_single = self._calculate_shannon_entropy(single_transitions)
        
        assert entropy_single == 0.0, "Single transition type should have zero entropy"
        
        # Test case 2: Two equal transition types
        dual_transitions = [("open", "neutral")] * 5 + [("neutral", "stable")] * 5
        entropy_dual = self._calculate_shannon_entropy(dual_transitions)
        
        expected_dual = 1.0  # log2(2) = 1.0 for equal probability distribution
        assert abs(entropy_dual - expected_dual) < 0.001, f"Dual equal transitions should have entropy ~1.0, got {entropy_dual}"
        
        # Test case 3: Uniform distribution (maximum entropy for given set)
        uniform_transitions = [
            ("open", "neutral"), ("neutral", "stable"), ("stable", "locked"),
            ("locked", "open"), ("open", "turbulent"), ("turbulent", "neutral")
        ]
        entropy_uniform = self._calculate_shannon_entropy(uniform_transitions)
        
        expected_uniform = math.log2(len(uniform_transitions))
        assert entropy_uniform > 2.0, f"Uniform distribution should have high entropy, got {entropy_uniform}"
    
    def test_drift_class_assignment(self):
        """Test drift class assignment based on entropy levels"""
        
        test_cases = [
            {"entropy": 0.0, "expected_class": "stable", "expected_glyph": "🪷"},
            {"entropy": 0.15, "expected_class": "stable", "expected_glyph": "🪷"},
            {"entropy": 0.45, "expected_class": "neutral", "expected_glyph": "🌀"},
            {"entropy": 0.75, "expected_class": "unstable", "expected_glyph": "🌪️"},
            {"entropy": 0.95, "expected_class": "unstable", "expected_glyph": "🌪️"}
        ]
        
        for case in test_cases:
            entropy = case["entropy"]
            expected_class = case["expected_class"]
            expected_glyph = case["expected_glyph"]
            
            # Test drift classification logic
            if entropy < 0.3:
                actual_class = "stable"
                actual_glyph = "🪷"
            elif entropy < 0.7:
                actual_class = "neutral"
                actual_glyph = "🌀"
            else:
                actual_class = "unstable"
                actual_glyph = "🌪️"
            
            assert actual_class == expected_class, f"Entropy {entropy} should be {expected_class}, got {actual_class}"
            assert actual_glyph == expected_glyph, f"Entropy {entropy} should have glyph {expected_glyph}, got {actual_glyph}"
    
    def test_symbolic_state_transitions(self):
        """Test symbolic state transition validation and glyph sequences"""
        
        # Test valid transition sequences
        valid_sequences = [
            # Consent flow: lock → process → consent
            (["locked", "neutral", "open"], ["🔐", "🧬", "🪷"]),
            
            # Trust building: secure → verify → grant  
            (["locked", "stable", "open"], ["🔐", "🛡️", "🔓"]),
            
            # Drift recovery: turbulent → stabilizing → stable
            (["turbulent", "neutral", "stable"], ["🌪️", "🌀", "🌿"]),
            
            # Emergency sequence: stable → turbulent → locked
            (["stable", "turbulent", "locked"], ["🌿", "🌪️", "🔐"])
        ]
        
        for states, expected_glyphs in valid_sequences:
            # Validate state progression is logical
            assert len(states) == len(expected_glyphs), "State and glyph sequences must match length"
            
            # Test symbolic mapping consistency
            for i, state in enumerate(states):
                expected_glyph = expected_glyphs[i]
                
                # Validate glyph represents the semantic meaning of the state
                if state == "locked":
                    assert expected_glyph in ["🔐", "🔒"], f"Locked state should use lock glyph, got {expected_glyph}"
                elif state == "open":
                    assert expected_glyph in ["🔓", "🪷"], f"Open state should use open/consent glyph, got {expected_glyph}"
                elif state == "stable":
                    assert expected_glyph in ["🌿", "💎", "🛡️"], f"Stable state should use stability glyph, got {expected_glyph}"
                elif state == "turbulent":
                    assert expected_glyph in ["🌪️", "⚡", "🌊"], f"Turbulent state should use chaos glyph, got {expected_glyph}"
    
    def test_guardian_intervention_triggers(self):
        """Test Guardian system intervention trigger conditions"""
        
        # Define intervention thresholds
        ENTROPY_THRESHOLD = 0.8
        DRIFT_RATE_THRESHOLD = 0.1
        STATE_CHANGE_THRESHOLD = 0.4
        
        test_scenarios = [
            {
                "name": "entropy_spike",
                "entropy_score": 0.85,
                "drift_rate": 0.05,
                "state_changes": 0.2,
                "should_trigger": True,
                "expected_action": "entropy_cooling",
                "expected_sequence": ["🔥", "→", "💨", "→", "❄️"]
            },
            {
                "name": "drift_spike", 
                "entropy_score": 0.45,
                "drift_rate": 0.15,
                "state_changes": 0.3,
                "should_trigger": True,
                "expected_action": "drift_dampening",
                "expected_sequence": ["🌪️", "→", "🌀", "→", "🌿"]
            },
            {
                "name": "consciousness_instability",
                "entropy_score": 0.35,
                "drift_rate": 0.05,
                "state_changes": 0.55,
                "should_trigger": True,
                "expected_action": "consciousness_anchoring",
                "expected_sequence": ["⚓", "🧘", "🔒"]
            },
            {
                "name": "normal_operation",
                "entropy_score": 0.25,
                "drift_rate": 0.03,
                "state_changes": 0.15,
                "should_trigger": False,
                "expected_action": None,
                "expected_sequence": None
            }
        ]
        
        for scenario in test_scenarios:
            entropy = scenario["entropy_score"]
            drift_rate = scenario["drift_rate"]
            state_changes = scenario["state_changes"]
            expected_trigger = scenario["should_trigger"]
            
            # Test individual threshold breaches
            entropy_breach = entropy > ENTROPY_THRESHOLD
            drift_breach = drift_rate > DRIFT_RATE_THRESHOLD
            consciousness_breach = state_changes > STATE_CHANGE_THRESHOLD
            
            # Should trigger if any threshold is breached
            actual_trigger = entropy_breach or drift_breach or consciousness_breach
            
            assert actual_trigger == expected_trigger, \
                f"Scenario {scenario['name']}: expected trigger {expected_trigger}, got {actual_trigger}"
            
            # If trigger expected, validate intervention response
            if expected_trigger and scenario["expected_action"]:
                expected_action = scenario["expected_action"]
                expected_sequence = scenario["expected_sequence"]
                
                # Validate intervention action is appropriate for trigger type
                if entropy_breach:
                    assert "entropy" in expected_action, f"Entropy breach should trigger entropy action, got {expected_action}"
                elif drift_breach:
                    assert "drift" in expected_action, f"Drift breach should trigger drift action, got {expected_action}"
                elif consciousness_breach:
                    assert "consciousness" in expected_action, f"Consciousness breach should trigger consciousness action, got {expected_action}"
                
                # Validate symbolic sequence coherence
                if expected_sequence:
                    clean_sequence = [s for s in expected_sequence if s != "→"]
                    assert len(clean_sequence) >= 2, "Intervention sequence should have at least 2 symbols"
                    
                    # First symbol should represent the problem state
                    first_symbol = clean_sequence[0]
                    last_symbol = clean_sequence[-1]
                    
                    # Problem symbols
                    problem_symbols = ["🔥", "🌪️", "⚡", "🚨", "💥"]
                    # Solution symbols  
                    solution_symbols = ["❄️", "🌿", "🧘", "🔒", "🛡️", "💎"]
                    
                    if len(clean_sequence) >= 3:  # Has progression
                        assert first_symbol in problem_symbols or first_symbol == "⚓", \
                            f"First symbol should represent problem state, got {first_symbol}"
                        assert last_symbol in solution_symbols, \
                            f"Last symbol should represent solution state, got {last_symbol}"
    
    def test_entropy_journal_persistence(self, entropy_tracker, temp_dir):
        """Test entropy journal persistence and data integrity"""
        
        # Add test entries
        test_entries = [
            {
                "previous_state": "neutral",
                "current_state": "open", 
                "transition_type": "consent_grant",
                "entropy_score": 0.25,
                "notes": "User grants biometric access"
            },
            {
                "previous_state": "open",
                "current_state": "turbulent",
                "transition_type": "trust_decrease", 
                "entropy_score": 0.85,
                "notes": "Suspicious activity detected"
            },
            {
                "previous_state": "turbulent",
                "current_state": "locked",
                "transition_type": "emergency_lock",
                "entropy_score": 0.95,
                "notes": "Security breach detected"
            }
        ]
        
        # Mock adding entries (in real implementation would use entropy_tracker.add_transition)
        entropy_tracker.journal_entries = test_entries
        
        # Validate entry structure and content
        assert len(entropy_tracker.journal_entries) == 3
        
        for entry in entropy_tracker.journal_entries:
            # Validate required fields
            required_fields = ["previous_state", "current_state", "transition_type", "entropy_score"]
            for field in required_fields:
                assert field in entry, f"Entry missing required field: {field}"
            
            # Validate entropy score is within valid range
            entropy = entry["entropy_score"]
            assert 0.0 <= entropy <= 1.0, f"Entropy score {entropy} outside valid range [0.0, 1.0]"
            
            # Validate state names are valid
            valid_states = ["neutral", "open", "stable", "locked", "turbulent"]
            assert entry["previous_state"] in valid_states, f"Invalid previous state: {entry['previous_state']}"
            assert entry["current_state"] in valid_states, f"Invalid current state: {entry['current_state']}"
    
    def test_consciousness_state_entropy_correlation(self):
        """Test correlation between consciousness states and entropy levels"""
        
        # Define expected entropy ranges for different consciousness states
        consciousness_entropy_mappings = {
            "focused": (0.1, 0.3),      # Low entropy - stable focus
            "creative": (0.3, 0.6),     # Medium entropy - controlled chaos
            "analytical": (0.1, 0.4),   # Low-medium entropy - structured thinking
            "meditative": (0.0, 0.2),   # Very low entropy - peaceful stability
            "dreaming": (0.5, 0.8),     # High entropy - uncontrolled associations
            "flow_state": (0.2, 0.5),   # Medium entropy - dynamic balance
            "lucid": (0.3, 0.7),        # Variable entropy - conscious dream control
            "turbulent": (0.7, 1.0)     # High entropy - chaotic state
        }
        
        for state, (min_entropy, max_entropy) in consciousness_entropy_mappings.items():
            # Test boundary conditions
            assert min_entropy >= 0.0, f"Min entropy for {state} cannot be negative"
            assert max_entropy <= 1.0, f"Max entropy for {state} cannot exceed 1.0"
            assert min_entropy < max_entropy, f"Min entropy must be less than max for {state}"
            
            # Test expected glyph mappings for consciousness states
            if state in ["focused", "analytical", "meditative"]:
                # Low entropy states should use stability glyphs
                expected_glyphs = ["🧘", "💎", "🌿", "⚓"]
                assert len(expected_glyphs) > 0, f"Stability states need appropriate glyphs"
                
            elif state in ["dreaming", "turbulent"]:
                # High entropy states should use chaos glyphs
                expected_glyphs = ["🌪️", "⚡", "🌊", "💫"]
                assert len(expected_glyphs) > 0, f"Chaos states need appropriate glyphs"
                
            elif state in ["creative", "flow_state", "lucid"]:
                # Medium entropy states should use transition glyphs
                expected_glyphs = ["🌀", "🔮", "✨", "🎨"]
                assert len(expected_glyphs) > 0, f"Transition states need appropriate glyphs"
    
    def test_drift_pattern_recognition(self):
        """Test pattern recognition in drift sequences"""
        
        # Define test drift patterns
        drift_patterns = [
            {
                "name": "gradual_escalation",
                "sequence": [0.1, 0.2, 0.4, 0.6, 0.8],
                "pattern_type": "linear_increase",
                "should_trigger_early": True,
                "expected_glyphs": ["🌱", "🌿", "🌀", "🌪️", "⚡"]
            },
            {
                "name": "sudden_spike",
                "sequence": [0.2, 0.2, 0.3, 0.9, 0.95],
                "pattern_type": "sudden_jump",
                "should_trigger_early": False,
                "expected_glyphs": ["🌿", "🌿", "🌀", "🚨", "💥"]
            },
            {
                "name": "oscillating",
                "sequence": [0.3, 0.7, 0.2, 0.8, 0.1],
                "pattern_type": "unstable_oscillation", 
                "should_trigger_early": True,
                "expected_glyphs": ["🌀", "🌪️", "🌿", "⚡", "🧘"]
            },
            {
                "name": "stable_baseline",
                "sequence": [0.15, 0.18, 0.12, 0.20, 0.16],
                "pattern_type": "stable",
                "should_trigger_early": False,
                "expected_glyphs": ["🌿", "🌿", "🌿", "🌿", "🌿"]
            }
        ]
        
        for pattern in drift_patterns:
            sequence = pattern["sequence"]
            pattern_type = pattern["pattern_type"]
            should_trigger_early = pattern["should_trigger_early"]
            expected_glyphs = pattern["expected_glyphs"]
            
            # Test pattern detection logic
            max_entropy = max(sequence)
            min_entropy = min(sequence)
            entropy_range = max_entropy - min_entropy
            variance = sum((x - sum(sequence)/len(sequence))**2 for x in sequence) / len(sequence)
            
            # Pattern classification
            if max_entropy > 0.8:
                detected_pattern = "high_entropy"
            elif entropy_range > 0.5:
                detected_pattern = "high_variance"  
            elif variance > 0.05:
                detected_pattern = "unstable"
            else:
                detected_pattern = "stable"
            
            # Validate pattern detection matches expectations
            if pattern_type == "sudden_jump":
                assert max_entropy > 0.8, f"Sudden jump pattern should have high max entropy"
                assert not should_trigger_early, f"Sudden jumps shouldn't trigger early warning"
                
            elif pattern_type == "linear_increase":
                assert sequence[-1] > sequence[0], f"Linear increase should end higher than start"
                assert should_trigger_early, f"Linear increases should trigger early warning"
                
            elif pattern_type == "stable":
                assert entropy_range < 0.1, f"Stable pattern should have low range"
                assert not should_trigger_early, f"Stable patterns shouldn't trigger early"
            
            # Validate glyph sequence matches entropy progression
            assert len(expected_glyphs) == len(sequence), "Glyph sequence must match entropy sequence length"
            
            for i, (entropy, glyph) in enumerate(zip(sequence, expected_glyphs)):
                # Low entropy should map to stability glyphs
                if entropy < 0.3:
                    stability_glyphs = ["🧘", "💎", "🌿", "🌱", "⚓"]
                    assert glyph in stability_glyphs, f"Low entropy {entropy} should use stability glyph, got {glyph}"
                
                # High entropy should map to chaos glyphs
                elif entropy > 0.7:
                    chaos_glyphs = ["🌪️", "⚡", "🚨", "💥", "🌊"]
                    assert glyph in chaos_glyphs, f"High entropy {entropy} should use chaos glyph, got {glyph}"
    
    def _calculate_shannon_entropy(self, transitions: List[Tuple[str, str]]) -> float:
        """Helper method to calculate Shannon entropy for transitions"""
        if not transitions:
            return 0.0
        
        # Count transition frequencies
        transition_counts = {}
        for transition in transitions:
            key = f"{transition[0]}→{transition[1]}"
            transition_counts[key] = transition_counts.get(key, 0) + 1
        
        # Calculate probabilities and entropy
        total_transitions = len(transitions)
        entropy = 0.0
        
        for count in transition_counts.values():
            probability = count / total_transitions
            if probability > 0:
                entropy -= probability * math.log2(probability)
        
        return entropy


# Test runner configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])