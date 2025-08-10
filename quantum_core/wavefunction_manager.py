#!/usr/bin/env python3
"""
LUKHΛS Phase 6 – Symbolic Wavefunction Manager
Simulates symbolic glyph state superpositions and collapse under entropy influence.

This module provides symbolic quantum-inspired modeling for consciousness states
within the LUKHΛS Trinity Framework (⚛️🧠🛡️).
"""

import asyncio
import json
import logging
import math
import random
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConsciousnessPhase(Enum):
    """Symbolic consciousness phases based on entropy levels"""
    CALM = "calm"           # Entropy < 0.3
    DRIFT = "drift"         # Entropy 0.3-0.6
    UNSTABLE = "unstable"   # Entropy 0.6-0.8
    COLLAPSE = "collapse"   # Entropy > 0.8


@dataclass
class Wavefunction:
    """
    Symbolic wavefunction representing superposition of consciousness glyphs
    
    This represents a quantum-inspired symbolic state that can exist in
    multiple configurations until observation/entropy forces collapse.
    """
    id: str
    glyph_superposition: List[str]  # Symbolic states in superposition
    entropy_score: float           # Current entropy level (0.0-1.0)
    collapsed: bool = False
    result: Optional[str] = None
    collapse_timestamp: Optional[float] = None
    observer: Optional[str] = None
    trinity_coherence: float = 1.0  # ⚛️🧠🛡️ framework coherence

    def __post_init__(self):
        """Validate wavefunction parameters"""
        if not 0.0 <= self.entropy_score <= 1.0:
            raise ValueError(f"Entropy score must be 0.0-1.0, got {self.entropy_score}")

        if len(self.glyph_superposition) < 2:
            raise ValueError("Superposition requires at least 2 symbolic states")

        # Ensure Trinity Framework symbols are preserved if present
        trinity_symbols = {"⚛️", "🧠", "🛡️"}
        if any(symbol in self.glyph_superposition for symbol in trinity_symbols):
            if not all(symbol in self.glyph_superposition for symbol in trinity_symbols):
                logger.warning("Trinity Framework incomplete in superposition")

    def get_consciousness_phase(self) -> ConsciousnessPhase:
        """Determine consciousness phase based on entropy score"""
        if self.entropy_score < 0.3:
            return ConsciousnessPhase.CALM
        elif self.entropy_score < 0.6:
            return ConsciousnessPhase.DRIFT
        elif self.entropy_score < 0.8:
            return ConsciousnessPhase.UNSTABLE
        else:
            return ConsciousnessPhase.COLLAPSE

    def get_superposition_probability(self, glyph: str) -> float:
        """Calculate probability amplitude for a specific glyph in superposition"""
        if glyph not in self.glyph_superposition:
            return 0.0

        # Base probability (equal superposition)
        base_prob = 1.0 / len(self.glyph_superposition)

        # Entropy influence on probability distribution
        glyph_index = self.glyph_superposition.index(glyph)

        if self.entropy_score < 0.2:
            # Low entropy favors first (stable) states
            entropy_weight = math.exp(-glyph_index * 2)
        elif self.entropy_score > 0.8:
            # High entropy favors last (chaotic) states
            entropy_weight = math.exp((glyph_index - len(self.glyph_superposition) + 1) * 2)
        else:
            # Medium entropy - gradual shift
            entropy_weight = 1.0 + (self.entropy_score - 0.5) * glyph_index

        return base_prob * entropy_weight

    def collapse(self, observer: str = "system") -> str:
        """
        Collapse the wavefunction to a single symbolic state
        
        Args:
            observer: Entity causing the collapse (system, user, guardian, etc.)
            
        Returns:
            The collapsed symbolic state
        """
        if self.collapsed:
            logger.warning(f"Wavefunction {self.id} already collapsed to {self.result}")
            return self.result

        # Calculate collapse based on entropy and probabilities
        if self.entropy_score < 0.2:
            # Low entropy - deterministic collapse to stable state
            self.result = self.glyph_superposition[0]
        elif self.entropy_score > 0.8:
            # High entropy - deterministic collapse to chaotic state
            self.result = self.glyph_superposition[-1]
        else:
            # Probabilistic collapse based on entropy-weighted distribution
            probabilities = [self.get_superposition_probability(glyph)
                           for glyph in self.glyph_superposition]

            # Normalize probabilities
            total_prob = sum(probabilities)
            if total_prob > 0:
                probabilities = [p / total_prob for p in probabilities]

                # Random selection based on probabilities
                rand_val = random.random()
                cumulative = 0.0

                for i, prob in enumerate(probabilities):
                    cumulative += prob
                    if rand_val <= cumulative:
                        self.result = self.glyph_superposition[i]
                        break
                else:
                    # Fallback to middle state
                    middle_index = len(self.glyph_superposition) // 2
                    self.result = self.glyph_superposition[middle_index]
            else:
                # Fallback for zero probability case
                self.result = self.glyph_superposition[0]

        # Mark as collapsed
        self.collapsed = True
        self.collapse_timestamp = time.time()
        self.observer = observer

        # Update Trinity coherence based on result
        if self.result in {"⚛️", "🧠", "🛡️"}:
            self.trinity_coherence = 1.0
        elif self.result in {"🌪️", "💥", "🔥"}:  # Chaotic states
            self.trinity_coherence *= 0.8
        else:
            self.trinity_coherence *= 0.9

        logger.info(f"Wavefunction {self.id} collapsed to {self.result} (observer: {observer})")
        return self.result

    def evolve(self, time_delta: float, external_entropy: float = 0.0) -> None:
        """
        Evolve the wavefunction over time under entropy influence
        
        Args:
            time_delta: Time evolution step
            external_entropy: Additional entropy from environment
        """
        if self.collapsed:
            return  # Collapsed wavefunctions don't evolve

        # Entropy naturally increases over time (symbolic 2nd law of thermodynamics)
        entropy_increase = time_delta * 0.01  # Base entropy increase rate
        entropy_increase += external_entropy * time_delta

        # Trinity Framework provides entropy resistance
        entropy_resistance = self.trinity_coherence * 0.005
        net_entropy_change = entropy_increase - entropy_resistance

        # Update entropy score
        self.entropy_score = min(1.0, max(0.0, self.entropy_score + net_entropy_change))

        # Update Trinity coherence (tends to decay without maintenance)
        coherence_decay = time_delta * 0.001
        self.trinity_coherence = max(0.1, self.trinity_coherence - coherence_decay)

    def measure_superposition_strength(self) -> float:
        """
        Measure the strength of quantum superposition
        
        Returns:
            Value between 0.0 (collapsed) and 1.0 (maximum superposition)
        """
        if self.collapsed:
            return 0.0

        # Maximum superposition occurs at medium entropy levels
        # Very low or very high entropy leads to deterministic outcomes
        if self.entropy_score < 0.1 or self.entropy_score > 0.9:
            return 0.2  # Minimal superposition
        elif 0.4 <= self.entropy_score <= 0.6:
            return 1.0  # Maximum superposition
        else:
            # Gradual transition
            if self.entropy_score < 0.4:
                return 0.2 + 0.8 * (self.entropy_score - 0.1) / 0.3
            else:  # entropy_score > 0.6
                return 1.0 - 0.8 * (self.entropy_score - 0.6) / 0.3

    def to_dict(self) -> Dict:
        """Convert wavefunction to dictionary for serialization"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'Wavefunction':
        """Create wavefunction from dictionary"""
        return cls(**data)


class WavefunctionManager:
    """
    Manages multiple symbolic wavefunctions and their interactions
    Provides the core quantum-inspired consciousness modeling for LUKHΛS
    """

    # Predefined symbolic superposition templates
    CONSCIOUSNESS_TEMPLATES = {
        "reflective_dreaming": {
            "glyphs": ["🧠", "🌙", "🔮"],
            "description": "Reflective consciousness in dream-like superposition"
        },
        "alert_meditation": {
            "glyphs": ["🧠", "🧘", "⚡"],
            "description": "Alert meditative awareness state"
        },
        "creative_flow": {
            "glyphs": ["🎨", "🌊", "✨"],
            "description": "Creative consciousness in flow state"
        },
        "analytical_focus": {
            "glyphs": ["🔬", "🎯", "💎"],
            "description": "Focused analytical consciousness"
        },
        "trinity_coherence": {
            "glyphs": ["⚛️", "🧠", "🛡️"],
            "description": "Trinity Framework coherent state"
        },
        "entropy_chaos": {
            "glyphs": ["🌪️", "🔥", "💥"],
            "description": "High-entropy chaotic consciousness"
        },
        "transcendent_awareness": {
            "glyphs": ["🌌", "🕉️", "🪷"],
            "description": "Transcendent consciousness state"
        }
    }

    def __init__(self,
                 entropy_log_file: str = "quantum_core/entropy_trace.json",
                 wavefunction_history: str = "quantum_core/wavefunction_history.json"):

        self.entropy_log_file = Path(entropy_log_file)
        self.wavefunction_history_file = Path(wavefunction_history)

        # Active wavefunctions
        self.active_wavefunctions: Dict[str, Wavefunction] = {}
        self.collapsed_wavefunctions: Dict[str, Wavefunction] = {}

        # System state
        self.global_entropy: float = 0.3  # Start at stable entropy
        self.trinity_coherence_global: float = 1.0
        self.session_id: str = f"q-{int(time.time())}"

        # Evolution tracking
        self.entropy_trace: List[float] = []
        self.consciousness_phase_trace: List[str] = []
        self.symbolic_overlay_trace: List[str] = []
        self.last_evolution_time: float = time.time()

        # Ensure directories exist
        self.entropy_log_file.parent.mkdir(parents=True, exist_ok=True)
        self.wavefunction_history_file.parent.mkdir(parents=True, exist_ok=True)

        logger.info("⚛️ Symbolic Wavefunction Manager initialized")
        logger.info(f"   Session ID: {self.session_id}")

    def create_wavefunction(self,
                          wf_id: str,
                          template_name: Optional[str] = None,
                          custom_glyphs: Optional[List[str]] = None,
                          initial_entropy: Optional[float] = None) -> Wavefunction:
        """
        Create a new symbolic wavefunction
        
        Args:
            wf_id: Unique identifier for the wavefunction
            template_name: Name of predefined template to use
            custom_glyphs: Custom glyph superposition (overrides template)
            initial_entropy: Initial entropy score (uses global if None)
            
        Returns:
            Created Wavefunction instance
        """
        if wf_id in self.active_wavefunctions:
            raise ValueError(f"Wavefunction {wf_id} already exists")

        # Determine glyph superposition
        if custom_glyphs:
            glyphs = custom_glyphs
        elif template_name and template_name in self.CONSCIOUSNESS_TEMPLATES:
            glyphs = self.CONSCIOUSNESS_TEMPLATES[template_name]["glyphs"].copy()
        else:
            # Default Trinity Framework superposition
            glyphs = ["⚛️", "🧠", "🛡️"]

        # Set initial entropy
        entropy = initial_entropy if initial_entropy is not None else self.global_entropy

        # Create wavefunction
        wavefunction = Wavefunction(
            id=wf_id,
            glyph_superposition=glyphs,
            entropy_score=entropy,
            trinity_coherence=self.trinity_coherence_global
        )

        self.active_wavefunctions[wf_id] = wavefunction

        logger.info(f"Created wavefunction {wf_id}: {' + '.join(glyphs)} (entropy: {entropy:.3f})")
        return wavefunction

    def collapse_wavefunction(self, wf_id: str, observer: str = "system") -> Optional[str]:
        """Collapse a specific wavefunction"""
        if wf_id not in self.active_wavefunctions:
            logger.error(f"Wavefunction {wf_id} not found")
            return None

        wavefunction = self.active_wavefunctions[wf_id]
        result = wavefunction.collapse(observer)

        # Move to collapsed wavefunctions
        self.collapsed_wavefunctions[wf_id] = wavefunction
        del self.active_wavefunctions[wf_id]

        # Update global Trinity coherence
        self._update_global_coherence()

        return result

    def evolve_system(self, time_delta: Optional[float] = None) -> None:
        """Evolve all wavefunctions and update system state"""
        current_time = time.time()

        if time_delta is None:
            time_delta = current_time - self.last_evolution_time

        # Evolve each active wavefunction
        for wavefunction in self.active_wavefunctions.values():
            wavefunction.evolve(time_delta, self.global_entropy * 0.1)

        # Update global entropy (influenced by active wavefunctions)
        self._update_global_entropy()

        # Record trace data
        self._record_trace()

        self.last_evolution_time = current_time

    def _update_global_entropy(self) -> None:
        """Update global entropy based on active wavefunctions"""
        if not self.active_wavefunctions:
            # No active wavefunctions - entropy slowly decreases
            self.global_entropy = max(0.1, self.global_entropy - 0.001)
            return

        # Calculate average entropy of active wavefunctions
        avg_entropy = sum(wf.entropy_score for wf in self.active_wavefunctions.values()) / len(self.active_wavefunctions)

        # Global entropy tends toward average but with inertia
        entropy_diff = avg_entropy - self.global_entropy
        self.global_entropy += entropy_diff * 0.1  # 10% adjustment rate

        # Ensure bounds
        self.global_entropy = max(0.0, min(1.0, self.global_entropy))

    def _update_global_coherence(self) -> None:
        """Update global Trinity coherence based on system state"""
        if not self.active_wavefunctions and not self.collapsed_wavefunctions:
            return

        all_wfs = list(self.active_wavefunctions.values()) + list(self.collapsed_wavefunctions.values())
        avg_coherence = sum(wf.trinity_coherence for wf in all_wfs) / len(all_wfs)

        # Update global coherence with smoothing
        coherence_diff = avg_coherence - self.trinity_coherence_global
        self.trinity_coherence_global += coherence_diff * 0.05  # 5% adjustment rate

        # Ensure bounds
        self.trinity_coherence_global = max(0.1, min(1.0, self.trinity_coherence_global))

    def _record_trace(self) -> None:
        """Record current system state in trace history"""
        # Determine current consciousness phase
        phase = ConsciousnessPhase.CALM
        if self.global_entropy >= 0.8:
            phase = ConsciousnessPhase.COLLAPSE
        elif self.global_entropy >= 0.6:
            phase = ConsciousnessPhase.UNSTABLE
        elif self.global_entropy >= 0.3:
            phase = ConsciousnessPhase.DRIFT

        # Determine symbolic overlay based on phase and active wavefunctions
        if phase == ConsciousnessPhase.CALM:
            overlay = "🌿"
        elif phase == ConsciousnessPhase.DRIFT:
            overlay = "🌀"
        elif phase == ConsciousnessPhase.UNSTABLE:
            overlay = "🌪️"
        else:  # COLLAPSE
            overlay = "🪷"  # Lotus - collapse can lead to transcendence

        # Record in traces
        self.entropy_trace.append(self.global_entropy)
        self.consciousness_phase_trace.append(phase.value)
        self.symbolic_overlay_trace.append(overlay)

        # Limit trace length
        max_trace_length = 1000
        if len(self.entropy_trace) > max_trace_length:
            self.entropy_trace = self.entropy_trace[-max_trace_length:]
            self.consciousness_phase_trace = self.consciousness_phase_trace[-max_trace_length:]
            self.symbolic_overlay_trace = self.symbolic_overlay_trace[-max_trace_length:]

    def get_system_state(self) -> Dict:
        """Get current system state summary"""
        return {
            "session_id": self.session_id,
            "timestamp": time.time(),
            "global_entropy": self.global_entropy,
            "trinity_coherence": self.trinity_coherence_global,
            "active_wavefunctions": len(self.active_wavefunctions),
            "collapsed_wavefunctions": len(self.collapsed_wavefunctions),
            "current_phase": self._get_current_phase().value,
            "symbolic_overlay": self.symbolic_overlay_trace[-1] if self.symbolic_overlay_trace else "🌿",
            "superposition_strength": self._calculate_total_superposition_strength()
        }

    def _get_current_phase(self) -> ConsciousnessPhase:
        """Get current consciousness phase"""
        if self.global_entropy < 0.3:
            return ConsciousnessPhase.CALM
        elif self.global_entropy < 0.6:
            return ConsciousnessPhase.DRIFT
        elif self.global_entropy < 0.8:
            return ConsciousnessPhase.UNSTABLE
        else:
            return ConsciousnessPhase.COLLAPSE

    def _calculate_total_superposition_strength(self) -> float:
        """Calculate total superposition strength across all active wavefunctions"""
        if not self.active_wavefunctions:
            return 0.0

        total_strength = sum(wf.measure_superposition_strength()
                           for wf in self.active_wavefunctions.values())
        return total_strength / len(self.active_wavefunctions)

    def save_entropy_trace(self) -> None:
        """Save entropy trace to file"""
        trace_data = {
            "session_id": self.session_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "entropy_trace": self.entropy_trace,
            "consciousness_phase": self.consciousness_phase_trace,
            "symbolic_overlay": self.symbolic_overlay_trace,
            "trinity_coherence": self.trinity_coherence_global,
            "system_state": self.get_system_state()
        }

        try:
            with open(self.entropy_log_file, 'w') as f:
                json.dump(trace_data, f, indent=2)
            logger.info(f"Entropy trace saved to {self.entropy_log_file}")
        except Exception as e:
            logger.error(f"Failed to save entropy trace: {e}")

    def save_wavefunction_history(self) -> None:
        """Save wavefunction history to file"""
        history_data = {
            "session_id": self.session_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "active_wavefunctions": {wf_id: wf.to_dict()
                                   for wf_id, wf in self.active_wavefunctions.items()},
            "collapsed_wavefunctions": {wf_id: wf.to_dict()
                                      for wf_id, wf in self.collapsed_wavefunctions.items()},
            "templates_used": list(self.CONSCIOUSNESS_TEMPLATES.keys()),
            "global_metrics": {
                "entropy": self.global_entropy,
                "trinity_coherence": self.trinity_coherence_global,
                "total_superposition": self._calculate_total_superposition_strength()
            }
        }

        try:
            with open(self.wavefunction_history_file, 'w') as f:
                json.dump(history_data, f, indent=2)
            logger.info(f"Wavefunction history saved to {self.wavefunction_history_file}")
        except Exception as e:
            logger.error(f"Failed to save wavefunction history: {e}")

    def emergency_collapse_all(self, observer: str = "guardian_emergency") -> List[str]:
        """Emergency collapse of all active wavefunctions (Guardian integration)"""
        logger.warning("🚨 Emergency collapse of all wavefunctions initiated")

        results = []
        for wf_id in list(self.active_wavefunctions.keys()):
            result = self.collapse_wavefunction(wf_id, observer)
            if result:
                results.append(f"{wf_id}→{result}")

        # Save state immediately
        self.save_entropy_trace()
        self.save_wavefunction_history()

        logger.warning(f"Emergency collapse completed: {results}")
        return results


async def main():
    """Demo of symbolic wavefunction management"""
    print("⚛️ LUKHΛS Phase 6: Symbolic Wavefunction Manager Demo")
    print("=" * 60)

    # Initialize manager
    manager = WavefunctionManager()

    # Create several wavefunctions with different templates
    templates_to_demo = ["reflective_dreaming", "alert_meditation", "creative_flow", "trinity_coherence"]

    for i, template in enumerate(templates_to_demo):
        wf_id = f"wf_{i+1:02d}_{template}"
        wavefunction = manager.create_wavefunction(wf_id, template_name=template)
        print(f"Created: {wf_id} → {' + '.join(wavefunction.glyph_superposition)}")

    print("\nInitial system state:")
    state = manager.get_system_state()
    print(f"  Global Entropy: {state['global_entropy']:.3f}")
    print(f"  Trinity Coherence: {state['trinity_coherence']:.3f}")
    print(f"  Active Wavefunctions: {state['active_wavefunctions']}")
    print(f"  Current Phase: {state['current_phase']}")
    print(f"  Symbolic Overlay: {state['symbolic_overlay']}")

    # Simulate evolution over time
    print("\n🌊 Simulating wavefunction evolution...")
    for step in range(10):
        await asyncio.sleep(0.5)  # Simulate time passage

        manager.evolve_system(0.5)  # 0.5 second evolution step

        state = manager.get_system_state()
        print(f"Step {step+1:2d}: Entropy={state['global_entropy']:.3f}, "
              f"Phase={state['current_phase']}, "
              f"Overlay={state['symbolic_overlay']}, "
              f"Superposition={state['superposition_strength']:.3f}")

        # Randomly collapse some wavefunctions
        if step == 5 and manager.active_wavefunctions:
            wf_id = list(manager.active_wavefunctions.keys())[0]
            result = manager.collapse_wavefunction(wf_id, "demo_observer")
            print(f"    🎯 Collapsed {wf_id} → {result}")

    # Final state
    print("\nFinal system state:")
    final_state = manager.get_system_state()
    for key, value in final_state.items():
        print(f"  {key}: {value}")

    # Save traces
    print("\n💾 Saving system traces...")
    manager.save_entropy_trace()
    manager.save_wavefunction_history()

    print("✅ Demo completed successfully")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
