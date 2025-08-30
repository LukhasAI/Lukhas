"""
VIVOX State Variety Enhancement
Improves consciousness state determination for more varied states
"""

import numpy as np

from .vivox_cil_core import ConsciousnessState


class EnhancedStateDetermination:
    """Enhanced state determination with better variety"""

    def __init__(self):
        # State transition probabilities based on current state
        self.transition_matrix = {
            ConsciousnessState.DIFFUSE: {
                ConsciousnessState.DIFFUSE: 0.3,
                ConsciousnessState.INTROSPECTIVE: 0.3,
                ConsciousnessState.CREATIVE: 0.2,
                ConsciousnessState.FOCUSED: 0.1,
                ConsciousnessState.ALERT: 0.1,
            },
            ConsciousnessState.INTROSPECTIVE: {
                ConsciousnessState.DIFFUSE: 0.2,
                ConsciousnessState.INTROSPECTIVE: 0.3,
                ConsciousnessState.CREATIVE: 0.3,
                ConsciousnessState.FOCUSED: 0.15,
                ConsciousnessState.ALERT: 0.05,
            },
            ConsciousnessState.CREATIVE: {
                ConsciousnessState.DIFFUSE: 0.15,
                ConsciousnessState.INTROSPECTIVE: 0.2,
                ConsciousnessState.CREATIVE: 0.3,
                ConsciousnessState.FOCUSED: 0.25,
                ConsciousnessState.ALERT: 0.1,
            },
            ConsciousnessState.FOCUSED: {
                ConsciousnessState.DIFFUSE: 0.1,
                ConsciousnessState.INTROSPECTIVE: 0.1,
                ConsciousnessState.CREATIVE: 0.2,
                ConsciousnessState.FOCUSED: 0.4,
                ConsciousnessState.ALERT: 0.2,
            },
            ConsciousnessState.ALERT: {
                ConsciousnessState.DIFFUSE: 0.05,
                ConsciousnessState.INTROSPECTIVE: 0.05,
                ConsciousnessState.CREATIVE: 0.1,
                ConsciousnessState.FOCUSED: 0.5,
                ConsciousnessState.ALERT: 0.3,
            },
        }

        self.previous_state = ConsciousnessState.DIFFUSE

    def determine_state_enhanced(
        self,
        dimensions: np.ndarray,
        emotional: dict[str, float],
        context: dict[str, any] = None,
    ) -> ConsciousnessState:
        """
        Enhanced state determination with more variety

        Considers:
        - Previous state transitions
        - Context-specific factors
        - Emotional nuance
        - Temporal dynamics
        """
        magnitude = np.linalg.norm(dimensions)
        valence = emotional.get("valence", 0)
        arousal = emotional.get("arousal", 0.5)
        dominance = emotional.get("dominance", 0.5)

        # Calculate base probabilities for each state
        state_probs = self._calculate_base_probabilities(magnitude, valence, arousal, dominance)

        # Apply transition matrix from previous state
        if self.previous_state in self.transition_matrix:
            transition_probs = self.transition_matrix[self.previous_state]
            for state, trans_prob in transition_probs.items():
                if state in state_probs:
                    # Blend base probability with transition probability
                    state_probs[state] = state_probs[state] * 0.6 + trans_prob * 0.4

        # Apply context modifiers
        if context:
            state_probs = self._apply_context_modifiers(state_probs, context)

        # Normalize probabilities
        total_prob = sum(state_probs.values())
        if total_prob > 0:
            state_probs = {k: v / total_prob for k, v in state_probs.items()}

        # Select state based on probabilities
        states = list(state_probs.keys())
        probs = list(state_probs.values())

        # Add small random noise to prevent deterministic behavior
        probs = [p + np.random.uniform(-0.05, 0.05) for p in probs]
        probs = [max(0, p) for p in probs]

        # Renormalize
        total = sum(probs)
        if total > 0:
            probs = [p / total for p in probs]
        else:
            probs = [1 / len(states)] * len(states)

        # Choose state
        selected_state = np.random.choice(states, p=probs)
        self.previous_state = selected_state

        return selected_state

    def _calculate_base_probabilities(
        self, magnitude: float, valence: float, arousal: float, dominance: float
    ) -> dict[ConsciousnessState, float]:
        """Calculate base probabilities for each state"""
        probs = {}

        # DIFFUSE: Low magnitude, neutral emotional state
        diffuse_score = 0.0
        if magnitude < 8:
            diffuse_score += 0.4
        if abs(valence) < 0.3 and arousal < 0.4:
            diffuse_score += 0.3
        if dominance < 0.3:
            diffuse_score += 0.3
        probs[ConsciousnessState.DIFFUSE] = diffuse_score

        # INTROSPECTIVE: Low arousal, negative or neutral valence
        intro_score = 0.0
        if arousal < 0.4:
            intro_score += 0.3
        if valence < 0:
            intro_score += 0.4
        if magnitude > 5 and magnitude < 12:
            intro_score += 0.3
        probs[ConsciousnessState.INTROSPECTIVE] = intro_score

        # CREATIVE: Positive valence, moderate arousal
        creative_score = 0.0
        if valence > 0.2:
            creative_score += 0.3
        if 0.3 < arousal < 0.7:
            creative_score += 0.4
        if magnitude > 8 and magnitude < 15:
            creative_score += 0.3
        probs[ConsciousnessState.CREATIVE] = creative_score

        # FOCUSED: High dominance, moderate to high magnitude
        focused_score = 0.0
        if magnitude > 10:
            focused_score += 0.3
        if dominance > 0.6:
            focused_score += 0.4
        if 0.4 < arousal < 0.8:
            focused_score += 0.3
        probs[ConsciousnessState.FOCUSED] = focused_score

        # ALERT: High arousal, high magnitude
        alert_score = 0.0
        if arousal > 0.7:
            alert_score += 0.5
        if magnitude > 12:
            alert_score += 0.3
        if abs(valence) > 0.6:
            alert_score += 0.2
        probs[ConsciousnessState.ALERT] = alert_score

        return probs

    def _apply_context_modifiers(
        self, state_probs: dict[ConsciousnessState, float], context: dict[str, any]
    ) -> dict[ConsciousnessState, float]:
        """Apply context-specific modifiers to state probabilities"""

        # Time pressure increases alert/focused states
        if context.get("time_pressure", 0) > 0.5:
            state_probs[ConsciousnessState.ALERT] *= 1.5
            state_probs[ConsciousnessState.FOCUSED] *= 1.3
            state_probs[ConsciousnessState.DIFFUSE] *= 0.5

        # Complexity increases introspective/creative states
        if context.get("complexity_score", 0) > 0.6:
            state_probs[ConsciousnessState.INTROSPECTIVE] *= 1.4
            state_probs[ConsciousnessState.CREATIVE] *= 1.3

        # Novelty increases creative/alert states
        if context.get("novelty", 0) > 0.5:
            state_probs[ConsciousnessState.CREATIVE] *= 1.5
            state_probs[ConsciousnessState.ALERT] *= 1.2

        # Fatigue increases diffuse state
        if context.get("fatigue_level", 0) > 0.7:
            state_probs[ConsciousnessState.DIFFUSE] *= 2.0
            state_probs[ConsciousnessState.ALERT] *= 0.5

        return state_probs


def create_enhanced_state_determination():
    """Factory function to create enhanced state determination"""
    return EnhancedStateDetermination()
