"""
Bio Utilities Module
Bio-inspired utility functions and classes for LUKHAS consciousness systems

⚛️🧠🛡️ Trinity Framework: Identity-Consciousness-Guardian
"""

import logging
from typing import Dict, Any, Optional, List
from enum import Enum

logger = logging.getLogger(__name__)

class FatigueLevel(Enum):
    """Fatigue levels for bio-inspired processing"""
    FRESH = 0
    SLIGHT = 1
    MODERATE = 2
    HIGH = 3
    EXHAUSTED = 4

class BioUtilities:
    """Bio-inspired utility functions for consciousness systems"""
    
    def __init__(self):
        self.fatigue_level = FatigueLevel.FRESH
        self.energy_level = 1.0
        self.adaptation_rate = 0.1
        
    def calculate_fatigue(self, workload: float, duration: float) -> FatigueLevel:
        """Calculate fatigue level based on workload and duration"""
        fatigue_score = workload * duration * 0.1
        
        if fatigue_score < 0.2:
            return FatigueLevel.FRESH
        elif fatigue_score < 0.4:
            return FatigueLevel.SLIGHT
        elif fatigue_score < 0.6:
            return FatigueLevel.MODERATE
        elif fatigue_score < 0.8:
            return FatigueLevel.HIGH
        else:
            return FatigueLevel.EXHAUSTED
            
    def adapt_to_environment(self, environment_data: Dict[str, Any]) -> float:
        """Bio-inspired adaptation to environment changes"""
        adaptation_score = 0.5  # Base adaptation
        
        # Simple adaptation logic
        if environment_data.get('complexity', 0) > 0.7:
            adaptation_score *= 0.8  # Reduce adaptation for high complexity
        if environment_data.get('stability', 1.0) < 0.3:
            adaptation_score *= 0.9  # Reduce adaptation for low stability
            
        return min(1.0, max(0.0, adaptation_score))
        
    def get_energy_status(self) -> Dict[str, Any]:
        """Get current energy and fatigue status"""
        return {
            'energy_level': self.energy_level,
            'fatigue_level': self.fatigue_level.name,
            'adaptation_rate': self.adaptation_rate,
            'status': 'operational' if self.energy_level > 0.2 else 'low_energy'
        }

# Module-level utility functions
def fatigue_level(workload: float = 0.0, duration: float = 0.0) -> FatigueLevel:
    """Calculate fatigue level for given workload and duration"""
    bio_utils = BioUtilities()
    return bio_utils.calculate_fatigue(workload, duration)

def bio_adapt(environment: Dict[str, Any]) -> float:
    """Bio-inspired adaptation function"""
    bio_utils = BioUtilities()
    return bio_utils.adapt_to_environment(environment)

# Export main components
__all__ = [
    'BioUtilities',
    'FatigueLevel', 
    'fatigue_level',
    'bio_adapt'
]
