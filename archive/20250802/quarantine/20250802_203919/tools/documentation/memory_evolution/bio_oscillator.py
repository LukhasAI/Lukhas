"""
Bio-Oscillator Integration for DocuTutor.
Connects the memory evolution system with the bio-inspired computing core.
"""

from typing import Dict, List, Optional
from datetime import datetime
import numpy as np

class BioOscillatorAdapter:
    def __init__(self):
        self.oscillation_patterns = {}
        self.current_state = None
        self.learning_rate = 0.1

    def process_knowledge(self, knowledge_id: str, content: Dict) -> float:
        """Process knowledge through bio-oscillator to get resonance score."""
        # Convert content to oscillation pattern
        pattern = self._content_to_pattern(content)
        self.oscillation_patterns[knowledge_id] = pattern

        # Calculate resonance with current state
        if self.current_state is not None:
            return self._calculate_resonance(pattern, self.current_state)
        return 1.0

    def update_state(self, interaction_data: Dict):
        """Update oscillator state based on user interactions."""
        # Extract relevant features
        timestamp = datetime.now().timestamp()
        success_rate = interaction_data.get('success_rate', 1.0)
        interaction_type = interaction_data.get('type', 'view')

        # Create new state vector
        new_state = np.array([
            np.sin(timestamp / 1000),  # Time component
            success_rate,              # Success component
            self._interaction_type_to_value(interaction_type)  # Type component
        ])

        if self.current_state is None:
            self.current_state = new_state
        else:
            # Update state with learning rate
            self.current_state = (1 - self.learning_rate) * self.current_state + " + "self.learning_rate * new_state

    def get_resonant_knowledge(self, threshold: float = 0.5) -> List[str]:
        """Get knowledge IDs that resonate with current state."""
        if self.current_state is None:
            return []

        resonant_ids = []
        for knowledge_id, pattern in self.oscillation_patterns.items():
            resonance = self._calculate_resonance(pattern, self.current_state)
            if resonance >= threshold:
                resonant_ids.append(knowledge_id)

        return sorted(resonant_ids,
                     key=lambda k: self._calculate_resonance(
                         self.oscillation_patterns[k],
                         self.current_state
                     ),
                     reverse=True)

    def _content_to_pattern(self, content: Dict) -> np.ndarray:
        """Convert content to oscillation pattern."""
        # Extract features from content
        complexity = len(str(content)) / 1000  # Normalized content length
        structure_score = content.get('structure_score', 0.5)
        update_frequency = content.get('update_frequency', 0.5)

        return np.array([complexity, structure_score, update_frequency])

    def _calculate_resonance(self, pattern: np.ndarray, state: np.ndarray) -> float:
        """Calculate resonance between pattern and state."""
        # Normalize vectors
        pattern_norm = pattern / np.linalg.norm(pattern)
        state_norm = state / np.linalg.norm(state)

        # Calculate cosine similarity
        resonance = np.dot(pattern_norm, state_norm)

        # Scale to [0,1] range
        return (resonance + 1) / 2

    def _interaction_type_to_value(self, interaction_type: str) -> float:
        """Convert interaction type to numeric value."""
        type_values = {
            'view': 0.3,
            'edit': 0.6,
            'search': 0.4,
            'link': 0.5
        }
        return type_values.get(interaction_type, 0.3)
