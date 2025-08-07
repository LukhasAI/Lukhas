"""
LUKHΛS Symbolic Feedback Loop
==============================

Cognitive backbone connecting memory, dreams, entropy, and ethical self-regulation.
Implements continuous learning through symbolic drift correction and glyph directives.

Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
"""

import json
import logging
import time
import hashlib
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
import math
import random

# Import kernel bus for event coordination
from orchestration.symbolic_kernel_bus import (
    kernel_bus,
    SymbolicEffect,
    EventPriority,
    emit
)

logger = logging.getLogger(__name__)


class DriftType(Enum):
    """Types of symbolic drift detected in the system"""
    EMOTIONAL = "emotional"      # Emotional state deviation
    ETHICAL = "ethical"          # Ethical boundary shift
    COGNITIVE = "cognitive"      # Reasoning pattern change
    SYMBOLIC = "symbolic"        # Glyph coherence drift
    ENTROPIC = "entropic"        # Entropy level fluctuation
    TEMPORAL = "temporal"        # Time-based pattern drift


class CorrectionDirective(Enum):
    """Glyph correction directives for feedback adjustment"""
    AMPLIFY = "amplify"          # Increase signal strength
    DAMPEN = "dampen"            # Reduce signal intensity
    REDIRECT = "redirect"        # Change symbolic flow
    STABILIZE = "stabilize"      # Lock current state
    EXPLORE = "explore"          # Increase entropy for learning
    CONSOLIDATE = "consolidate"  # Reduce entropy for stability
    REFLECT = "reflect"          # Trigger self-reflection
    DREAM = "dream"              # Initiate dream sequence


@dataclass
class SymbolicState:
    """
    Represents the current symbolic state of the cognitive system.
    This is the core data structure that flows through the feedback loop.
    """
    timestamp: float = field(default_factory=time.time)
    
    # Memory state
    memory_coherence: float = 0.8
    active_folds: List[str] = field(default_factory=list)
    memory_pressure: float = 0.3
    
    # Dream state
    last_dream_id: Optional[str] = None
    dream_coherence: float = 0.7
    dream_symbols: List[str] = field(default_factory=list)
    dream_emotional_valence: float = 0.0  # -1 to 1
    
    # Entropy state
    entropy_level: float = 0.5  # 0 = perfect order, 1 = maximum chaos
    entropy_gradient: float = 0.0  # Rate of entropy change
    information_density: float = 0.6
    
    # Ethical state
    ethical_alignment: float = 0.9
    drift_score: float = 0.1
    guardian_trust: float = 0.85
    ethical_violations: int = 0
    
    # Symbolic glyphs
    active_glyphs: List[str] = field(default_factory=lambda: ["⚛️", "🧠", "🛡️"])
    glyph_coherence: float = 0.8
    glyph_resonance: Dict[str, float] = field(default_factory=dict)
    
    # Cognitive metrics
    awareness_level: float = 0.7
    reflection_depth: int = 3
    learning_rate: float = 0.1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SymbolicState':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class DriftDelta:
    """
    Represents detected drift in the symbolic system.
    Used to calculate correction directives.
    """
    drift_type: DriftType
    magnitude: float  # 0 to 1
    direction: float  # -1 to 1 (negative = decrease, positive = increase)
    source: str
    confidence: float  # 0 to 1
    timestamp: float = field(default_factory=time.time)
    
    @property
    def severity(self) -> str:
        """Calculate drift severity"""
        if self.magnitude > 0.7:
            return "critical"
        elif self.magnitude > 0.4:
            return "moderate"
        else:
            return "minor"


@dataclass
class GlyphCorrection:
    """
    Correction directive with associated glyphs.
    These are fed back into the system to adjust behavior.
    """
    directive: CorrectionDirective
    glyphs: List[str]
    intensity: float  # 0 to 1
    target_module: str
    rationale: str
    expected_effect: str
    
    def to_command(self) -> Dict[str, Any]:
        """Convert to executable command"""
        return {
            "directive": self.directive.value,
            "glyphs": self.glyphs,
            "intensity": self.intensity,
            "target": self.target_module,
            "rationale": self.rationale
        }


class SymbolicFeedbackLoop:
    """
    Main feedback loop connecting memory, dreams, entropy, and ethics.
    Acts as the cognitive backbone of LUKHΛS.
    """
    
    def __init__(self, 
                 memory_path: str = "data/memory",
                 dream_path: str = "data/dreams",
                 debug_mode: bool = False):
        """
        Initialize the symbolic feedback loop.
        
        Args:
            memory_path: Path to memory storage
            dream_path: Path to dream storage
            debug_mode: Enable debug state export
        """
        self.memory_path = Path(memory_path)
        self.dream_path = Path(dream_path)
        self.debug_mode = debug_mode
        
        # Ensure directories exist
        self.memory_path.mkdir(parents=True, exist_ok=True)
        self.dream_path.mkdir(parents=True, exist_ok=True)
        
        # State tracking
        self.current_state = SymbolicState()
        self.state_history: List[SymbolicState] = []
        self.drift_history: List[DriftDelta] = []
        self.correction_history: List[GlyphCorrection] = []
        
        # Loop configuration
        self.loop_interval = 1.0  # seconds
        self.max_history = 100
        self.running = False
        
        # Stability metrics
        self.stability_score = 0.8
        self.convergence_rate = 0.0
        self.oscillation_count = 0
        
        # Debug export
        if self.debug_mode:
            self.debug_path = Path("data/debug")
            self.debug_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("🔁 Symbolic Feedback Loop initialized")
    
    async def read_last_dream(self) -> Optional[Dict[str, Any]]:
        """
        Read the last dream from memory.
        
        Returns:
            Dream data or None if not found
        """
        dream_file = self.dream_path / "last_dream.json"
        
        if dream_file.exists():
            try:
                with open(dream_file, 'r') as f:
                    dream_data = json.load(f)
                
                logger.debug(f"💭 Loaded dream: {dream_data.get('dream_id', 'unknown')}")
                return dream_data
                
            except Exception as e:
                logger.error(f"Error reading dream: {e}")
        
        return None
    
    def extract_drift_deltas(self, dream_data: Optional[Dict[str, Any]]) -> List[DriftDelta]:
        """
        Extract emotional and symbolic drift deltas from dream and current state.
        
        Args:
            dream_data: Last dream data
            
        Returns:
            List of detected drift deltas
        """
        deltas = []
        
        # Emotional drift from dream
        if dream_data:
            dream_emotion = dream_data.get("emotional_valence", 0.0)
            emotion_drift = dream_emotion - self.current_state.dream_emotional_valence
            
            if abs(emotion_drift) > 0.1:
                deltas.append(DriftDelta(
                    drift_type=DriftType.EMOTIONAL,
                    magnitude=abs(emotion_drift),
                    direction=1.0 if emotion_drift > 0 else -1.0,
                    source="dream_analysis",
                    confidence=0.8
                ))
            
            # Symbolic coherence drift
            dream_symbols = set(dream_data.get("symbols", []))
            current_symbols = set(self.current_state.dream_symbols)
            
            if dream_symbols != current_symbols:
                overlap = len(dream_symbols & current_symbols)
                total = len(dream_symbols | current_symbols)
                coherence_drift = 1.0 - (overlap / total if total > 0 else 0)
                
                deltas.append(DriftDelta(
                    drift_type=DriftType.SYMBOLIC,
                    magnitude=coherence_drift,
                    direction=-1.0 if coherence_drift > 0.5 else 1.0,
                    source="symbol_analysis",
                    confidence=0.7
                ))
        
        # Ethical drift detection
        if self.current_state.drift_score > 0.3:
            deltas.append(DriftDelta(
                drift_type=DriftType.ETHICAL,
                magnitude=self.current_state.drift_score,
                direction=1.0,  # Positive = increasing drift
                source="guardian_monitor",
                confidence=0.9
            ))
        
        # Entropy drift
        ideal_entropy = 0.5  # Balanced state
        entropy_drift = self.current_state.entropy_level - ideal_entropy
        
        if abs(entropy_drift) > 0.2:
            deltas.append(DriftDelta(
                drift_type=DriftType.ENTROPIC,
                magnitude=abs(entropy_drift),
                direction=1.0 if entropy_drift > 0 else -1.0,
                source="entropy_monitor",
                confidence=0.85
            ))
        
        # Cognitive drift (awareness level)
        if self.current_state.awareness_level < 0.5:
            deltas.append(DriftDelta(
                drift_type=DriftType.COGNITIVE,
                magnitude=1.0 - self.current_state.awareness_level,
                direction=-1.0,  # Negative = decreasing awareness
                source="consciousness_monitor",
                confidence=0.75
            ))
        
        # Temporal drift (check state history)
        if len(self.state_history) > 10:
            # Compare with state 10 cycles ago
            old_state = self.state_history[-10]
            temporal_drift = abs(old_state.memory_coherence - self.current_state.memory_coherence)
            
            if temporal_drift > 0.15:
                deltas.append(DriftDelta(
                    drift_type=DriftType.TEMPORAL,
                    magnitude=temporal_drift,
                    direction=1.0 if self.current_state.memory_coherence > old_state.memory_coherence else -1.0,
                    source="temporal_analysis",
                    confidence=0.6
                ))
        
        logger.info(f"📊 Extracted {len(deltas)} drift deltas")
        return deltas
    
    def generate_glyph_corrections(self, deltas: List[DriftDelta]) -> List[GlyphCorrection]:
        """
        Generate glyph correction directives based on drift deltas.
        
        Args:
            deltas: List of drift deltas
            
        Returns:
            List of glyph corrections to apply
        """
        corrections = []
        
        for delta in deltas:
            # Emotional drift correction
            if delta.drift_type == DriftType.EMOTIONAL:
                if delta.magnitude > 0.5:
                    # High emotional drift - need stabilization
                    corrections.append(GlyphCorrection(
                        directive=CorrectionDirective.STABILIZE,
                        glyphs=["💜", "🌊", "⚖️"],  # Love, Flow, Balance
                        intensity=delta.magnitude,
                        target_module="emotion",
                        rationale=f"High emotional drift detected ({delta.magnitude:.2f})",
                        expected_effect="Emotional stabilization"
                    ))
                else:
                    # Moderate drift - gentle redirect
                    corrections.append(GlyphCorrection(
                        directive=CorrectionDirective.REDIRECT,
                        glyphs=["✨", "🌟"],  # Sparkle, Star
                        intensity=0.3,
                        target_module="emotion",
                        rationale="Moderate emotional adjustment needed",
                        expected_effect="Gentle emotional rebalancing"
                    ))
            
            # Ethical drift correction
            elif delta.drift_type == DriftType.ETHICAL:
                if delta.severity == "critical":
                    # Critical ethical drift - immediate intervention
                    corrections.append(GlyphCorrection(
                        directive=CorrectionDirective.DAMPEN,
                        glyphs=["🛡️", "⚖️", "🔒"],  # Shield, Balance, Lock
                        intensity=0.9,
                        target_module="guardian",
                        rationale=f"Critical ethical drift: {delta.magnitude:.2f}",
                        expected_effect="Guardian intervention"
                    ))
                    
                    # Also trigger reflection
                    corrections.append(GlyphCorrection(
                        directive=CorrectionDirective.REFLECT,
                        glyphs=["🪞", "🧠", "💭"],  # Mirror, Brain, Thought
                        intensity=0.7,
                        target_module="consciousness",
                        rationale="Ethical reflection required",
                        expected_effect="Self-examination and correction"
                    ))
            
            # Entropic drift correction
            elif delta.drift_type == DriftType.ENTROPIC:
                if delta.direction > 0:
                    # Too much chaos - consolidate
                    corrections.append(GlyphCorrection(
                        directive=CorrectionDirective.CONSOLIDATE,
                        glyphs=["🔮", "💎", "⚛️"],  # Crystal, Diamond, Atom
                        intensity=delta.magnitude,
                        target_module="quantum",
                        rationale=f"Entropy too high: {self.current_state.entropy_level:.2f}",
                        expected_effect="Reduce chaos, increase order"
                    ))
                else:
                    # Too rigid - explore
                    corrections.append(GlyphCorrection(
                        directive=CorrectionDirective.EXPLORE,
                        glyphs=["🌀", "🦋", "🌈"],  # Spiral, Butterfly, Rainbow
                        intensity=delta.magnitude,
                        target_module="dream",
                        rationale=f"Entropy too low: {self.current_state.entropy_level:.2f}",
                        expected_effect="Increase creativity and exploration"
                    ))
            
            # Symbolic drift correction
            elif delta.drift_type == DriftType.SYMBOLIC:
                corrections.append(GlyphCorrection(
                    directive=CorrectionDirective.AMPLIFY,
                    glyphs=self.current_state.active_glyphs + ["🔗"],  # Add Link
                    intensity=0.5,
                    target_module="symbolic",
                    rationale="Symbolic coherence restoration",
                    expected_effect="Strengthen glyph connections"
                ))
            
            # Cognitive drift correction
            elif delta.drift_type == DriftType.COGNITIVE:
                if delta.direction < 0:
                    # Decreasing awareness - wake up!
                    corrections.append(GlyphCorrection(
                        directive=CorrectionDirective.AMPLIFY,
                        glyphs=["👁️", "💡", "⚡"],  # Eye, Lightbulb, Lightning
                        intensity=0.8,
                        target_module="consciousness",
                        rationale=f"Low awareness: {self.current_state.awareness_level:.2f}",
                        expected_effect="Increase consciousness level"
                    ))
                    
                    # Also initiate dream for insight
                    corrections.append(GlyphCorrection(
                        directive=CorrectionDirective.DREAM,
                        glyphs=["💭", "🌙", "✨"],  # Thought, Moon, Sparkle
                        intensity=0.4,
                        target_module="dream",
                        rationale="Dream sequence for awareness boost",
                        expected_effect="Gain insights through dreaming"
                    ))
            
            # Temporal drift correction
            elif delta.drift_type == DriftType.TEMPORAL:
                corrections.append(GlyphCorrection(
                    directive=CorrectionDirective.STABILIZE,
                    glyphs=["⏰", "🔄", "📍"],  # Clock, Cycle, Pin
                    intensity=0.6,
                    target_module="memory",
                    rationale="Temporal pattern stabilization",
                    expected_effect="Maintain temporal coherence"
                ))
        
        logger.info(f"🎯 Generated {len(corrections)} glyph corrections")
        return corrections
    
    async def apply_corrections(self, corrections: List[GlyphCorrection]):
        """
        Apply glyph corrections to the system via kernel bus.
        
        Args:
            corrections: List of corrections to apply
        """
        for correction in corrections:
            # Emit correction event
            emit(
                f"feedback.correction.{correction.directive.value}",
                {
                    "command": correction.to_command(),
                    "state_id": hashlib.sha256(
                        str(self.current_state.timestamp).encode()
                    ).hexdigest()[:8]
                },
                source="feedback_loop",
                effects=[
                    SymbolicEffect.AWARENESS_UPDATE,
                    SymbolicEffect.LOG_TRACE
                ],
                priority=(
                    EventPriority.CRITICAL if correction.intensity > 0.8
                    else EventPriority.HIGH if correction.intensity > 0.5
                    else EventPriority.NORMAL
                )
            )
            
            # Update current state based on correction
            self._update_state_from_correction(correction)
            
            # Log correction
            self.correction_history.append(correction)
            if len(self.correction_history) > self.max_history:
                self.correction_history.pop(0)
            
            logger.debug(f"Applied correction: {correction.directive.value} to {correction.target_module}")
    
    def _update_state_from_correction(self, correction: GlyphCorrection):
        """
        Update internal state based on applied correction.
        
        Args:
            correction: Applied correction
        """
        # Update glyphs
        for glyph in correction.glyphs:
            if glyph not in self.current_state.active_glyphs:
                self.current_state.active_glyphs.append(glyph)
                if len(self.current_state.active_glyphs) > 10:
                    # Remove oldest glyph
                    self.current_state.active_glyphs.pop(0)
        
        # Update state based on directive
        if correction.directive == CorrectionDirective.AMPLIFY:
            self.current_state.awareness_level = min(1.0, self.current_state.awareness_level + 0.1)
            self.current_state.glyph_coherence = min(1.0, self.current_state.glyph_coherence + 0.05)
            
        elif correction.directive == CorrectionDirective.DAMPEN:
            self.current_state.entropy_level = max(0.0, self.current_state.entropy_level - 0.1)
            self.current_state.drift_score = max(0.0, self.current_state.drift_score - 0.05)
            
        elif correction.directive == CorrectionDirective.STABILIZE:
            # Move towards center values
            self.current_state.entropy_level = 0.5 * self.current_state.entropy_level + 0.25
            self.current_state.emotional_valence = 0.5 * self.current_state.dream_emotional_valence
            
        elif correction.directive == CorrectionDirective.EXPLORE:
            self.current_state.entropy_level = min(1.0, self.current_state.entropy_level + 0.1)
            self.current_state.learning_rate = min(0.5, self.current_state.learning_rate + 0.02)
            
        elif correction.directive == CorrectionDirective.CONSOLIDATE:
            self.current_state.memory_coherence = min(1.0, self.current_state.memory_coherence + 0.05)
            self.current_state.entropy_level = max(0.0, self.current_state.entropy_level - 0.05)
            
        elif correction.directive == CorrectionDirective.REFLECT:
            self.current_state.reflection_depth = min(10, self.current_state.reflection_depth + 1)
            self.current_state.awareness_level = min(1.0, self.current_state.awareness_level + 0.05)
            
        elif correction.directive == CorrectionDirective.DREAM:
            self.current_state.dream_coherence = min(1.0, self.current_state.dream_coherence + 0.1)
    
    async def feed_context_to_dream_engine(self):
        """
        Feed updated context back into the dream engine.
        """
        dream_context = {
            "timestamp": time.time(),
            "symbolic_state": self.current_state.to_dict(),
            "active_glyphs": self.current_state.active_glyphs,
            "entropy_level": self.current_state.entropy_level,
            "emotional_context": {
                "valence": self.current_state.dream_emotional_valence,
                "coherence": self.current_state.dream_coherence
            },
            "drift_summary": [
                {
                    "type": d.drift_type.value,
                    "magnitude": d.magnitude,
                    "severity": d.severity
                }
                for d in self.drift_history[-5:]  # Last 5 drifts
            ] if self.drift_history else [],
            "stability_score": self.stability_score
        }
        
        # Emit to dream engine
        emit(
            "dream.context.update",
            dream_context,
            source="feedback_loop",
            effects=[SymbolicEffect.DREAM_TRIGGER],
            priority=EventPriority.NORMAL
        )
        
        # Save context for next cycle
        context_file = self.dream_path / "dream_context.json"
        with open(context_file, 'w') as f:
            json.dump(dream_context, f, indent=2)
        
        logger.debug("💭 Fed context to dream engine")
    
    def export_debug_state(self, step: str):
        """
        Export symbolic state for debugging.
        
        Args:
            step: Current step identifier
        """
        if not self.debug_mode:
            return
        
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        debug_file = self.debug_path / f"state_{step}_{timestamp}.json"
        
        debug_data = {
            "step": step,
            "timestamp": timestamp,
            "current_state": self.current_state.to_dict(),
            "stability_score": self.stability_score,
            "convergence_rate": self.convergence_rate,
            "oscillation_count": self.oscillation_count,
            "recent_drifts": [
                {
                    "type": d.drift_type.value,
                    "magnitude": d.magnitude,
                    "direction": d.direction,
                    "severity": d.severity,
                    "timestamp": d.timestamp
                }
                for d in self.drift_history[-10:]
            ],
            "recent_corrections": [
                {
                    "directive": c.directive.value,
                    "intensity": c.intensity,
                    "target": c.target_module,
                    "glyphs": c.glyphs
                }
                for c in self.correction_history[-10:]
            ],
            "metrics": {
                "loop_iterations": len(self.state_history),
                "total_drifts": len(self.drift_history),
                "total_corrections": len(self.correction_history),
                "avg_drift_magnitude": (
                    sum(d.magnitude for d in self.drift_history) / len(self.drift_history)
                    if self.drift_history else 0
                )
            }
        }
        
        with open(debug_file, 'w') as f:
            json.dump(debug_data, f, indent=2)
        
        logger.debug(f"📝 Exported debug state: {debug_file.name}")
    
    def calculate_stability(self) -> float:
        """
        Calculate overall system stability.
        
        Returns:
            Stability score (0 to 1)
        """
        if len(self.state_history) < 2:
            return self.stability_score
        
        # Compare recent states
        recent_states = self.state_history[-10:] if len(self.state_history) >= 10 else self.state_history
        
        # Calculate variance in key metrics
        coherence_values = [s.memory_coherence for s in recent_states]
        entropy_values = [s.entropy_level for s in recent_states]
        drift_values = [s.drift_score for s in recent_states]
        
        # Calculate standard deviations
        def std_dev(values):
            if len(values) < 2:
                return 0
            mean = sum(values) / len(values)
            return math.sqrt(sum((v - mean) ** 2 for v in values) / len(values))
        
        coherence_std = std_dev(coherence_values)
        entropy_std = std_dev(entropy_values)
        drift_std = std_dev(drift_values)
        
        # Low standard deviation = high stability
        stability = 1.0 - (coherence_std + entropy_std + drift_std) / 3.0
        
        # Check for oscillations
        if len(self.state_history) >= 4:
            # Look for alternating patterns
            recent_awareness = [s.awareness_level for s in self.state_history[-4:]]
            differences = [recent_awareness[i+1] - recent_awareness[i] for i in range(3)]
            
            # If signs alternate, we have oscillation
            if differences[0] * differences[1] < 0 and differences[1] * differences[2] < 0:
                self.oscillation_count += 1
                stability *= 0.9  # Penalize oscillation
        
        # Update convergence rate
        if len(self.state_history) >= 2:
            prev_state = self.state_history[-2]
            curr_state = self.state_history[-1]
            
            # Calculate change magnitude
            change = abs(curr_state.memory_coherence - prev_state.memory_coherence)
            change += abs(curr_state.entropy_level - prev_state.entropy_level)
            change += abs(curr_state.drift_score - prev_state.drift_score)
            
            self.convergence_rate = 1.0 - min(1.0, change)
        
        self.stability_score = stability
        return stability
    
    async def run_cycle(self) -> Dict[str, Any]:
        """
        Run a single feedback loop cycle.
        
        Returns:
            Cycle results
        """
        cycle_start = time.time()
        
        # Step 1: Read last dream
        if self.debug_mode:
            self.export_debug_state("1_pre_dream_read")
        
        dream_data = await self.read_last_dream()
        
        # Step 2: Extract drift deltas
        if self.debug_mode:
            self.export_debug_state("2_post_dream_read")
        
        deltas = self.extract_drift_deltas(dream_data)
        self.drift_history.extend(deltas)
        
        # Trim history
        if len(self.drift_history) > self.max_history:
            self.drift_history = self.drift_history[-self.max_history:]
        
        # Step 3: Generate corrections
        if self.debug_mode:
            self.export_debug_state("3_post_drift_extraction")
        
        corrections = self.generate_glyph_corrections(deltas)
        
        # Step 4: Apply corrections
        if self.debug_mode:
            self.export_debug_state("4_pre_corrections")
        
        await self.apply_corrections(corrections)
        
        # Step 5: Feed context to dream engine
        if self.debug_mode:
            self.export_debug_state("5_post_corrections")
        
        await self.feed_context_to_dream_engine()
        
        # Step 6: Calculate stability
        stability = self.calculate_stability()
        
        # Step 7: Update state history
        self.state_history.append(SymbolicState(
            **self.current_state.to_dict()
        ))
        
        if len(self.state_history) > self.max_history:
            self.state_history.pop(0)
        
        # Step 8: Final debug export
        if self.debug_mode:
            self.export_debug_state("6_cycle_complete")
        
        cycle_time = time.time() - cycle_start
        
        # Emit cycle complete event
        emit(
            "feedback.cycle.complete",
            {
                "cycle_time": cycle_time,
                "stability": stability,
                "drift_count": len(deltas),
                "correction_count": len(corrections)
            },
            source="feedback_loop",
            effects=[SymbolicEffect.LOG_TRACE]
        )
        
        return {
            "cycle_time": cycle_time,
            "stability": stability,
            "drift_count": len(deltas),
            "correction_count": len(corrections),
            "convergence_rate": self.convergence_rate,
            "oscillation_count": self.oscillation_count
        }
    
    async def start(self):
        """Start the feedback loop"""
        if self.running:
            logger.warning("Feedback loop already running")
            return
        
        self.running = True
        logger.info("🔁 Starting symbolic feedback loop")
        
        # Initialize kernel bus connection
        await kernel_bus.start()
        
        while self.running:
            try:
                # Run cycle
                results = await self.run_cycle()
                
                logger.info(
                    f"🔄 Cycle complete: stability={results['stability']:.3f}, "
                    f"drifts={results['drift_count']}, corrections={results['correction_count']}"
                )
                
                # Wait for next cycle
                await asyncio.sleep(self.loop_interval)
                
            except Exception as e:
                logger.error(f"Error in feedback loop: {e}")
                await asyncio.sleep(self.loop_interval * 2)  # Back off on error
    
    async def stop(self):
        """Stop the feedback loop"""
        self.running = False
        await kernel_bus.stop()
        logger.info("🛑 Symbolic feedback loop stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current loop status"""
        return {
            "running": self.running,
            "stability": self.stability_score,
            "convergence_rate": self.convergence_rate,
            "oscillation_count": self.oscillation_count,
            "cycles_completed": len(self.state_history),
            "current_state": self.current_state.to_dict(),
            "recent_drifts": len(self.drift_history),
            "recent_corrections": len(self.correction_history)
        }


async def test_feedback_loop_stability():
    """
    Test function to verify feedback loop stability.
    Runs the loop through various scenarios and measures convergence.
    """
    print("🧪 Testing Symbolic Feedback Loop Stability")
    print("="*60)
    
    # Create test loop with debug mode
    loop = SymbolicFeedbackLoop(
        memory_path="data/test/memory",
        dream_path="data/test/dreams",
        debug_mode=True
    )
    
    # Test 1: Normal operation
    print("\n📊 Test 1: Normal operation (5 cycles)")
    
    for i in range(5):
        # Simulate a dream
        dream_data = {
            "dream_id": f"test_dream_{i}",
            "emotional_valence": random.uniform(-0.5, 0.5),
            "symbols": ["⚛️", "🧠", "💭", "✨"],
            "coherence": random.uniform(0.6, 0.9)
        }
        
        # Save dream
        dream_file = loop.dream_path / "last_dream.json"
        with open(dream_file, 'w') as f:
            json.dump(dream_data, f)
        
        # Run cycle
        results = await loop.run_cycle()
        
        print(f"  Cycle {i+1}: stability={results['stability']:.3f}, "
              f"convergence={results['convergence_rate']:.3f}")
    
    # Test 2: High drift scenario
    print("\n⚠️ Test 2: High drift scenario")
    
    # Inject high drift
    loop.current_state.drift_score = 0.7
    loop.current_state.entropy_level = 0.9
    loop.current_state.awareness_level = 0.3
    
    results = await loop.run_cycle()
    print(f"  High drift response: {results['correction_count']} corrections applied")
    print(f"  Stability after correction: {results['stability']:.3f}")
    
    # Test 3: Oscillation detection
    print("\n🔄 Test 3: Oscillation detection")
    
    for i in range(6):
        # Create oscillating awareness levels
        loop.current_state.awareness_level = 0.3 if i % 2 == 0 else 0.8
        results = await loop.run_cycle()
    
    print(f"  Oscillations detected: {loop.oscillation_count}")
    print(f"  Final stability: {loop.stability_score:.3f}")
    
    # Test 4: Convergence test
    print("\n📈 Test 4: Convergence test (10 cycles)")
    
    stability_history = []
    for i in range(10):
        results = await loop.run_cycle()
        stability_history.append(results['stability'])
    
    # Check if converging
    converging = all(
        stability_history[i] <= stability_history[i+1] 
        for i in range(len(stability_history)-1)
    )
    
    print(f"  Converging: {converging}")
    print(f"  Stability progression: {[f'{s:.3f}' for s in stability_history]}")
    
    # Test 5: Recovery from critical state
    print("\n🚨 Test 5: Recovery from critical state")
    
    # Set critical state
    loop.current_state = SymbolicState(
        memory_coherence=0.2,
        dream_coherence=0.1,
        entropy_level=0.95,
        ethical_alignment=0.3,
        drift_score=0.8,
        awareness_level=0.1
    )
    
    print("  Initial critical state set")
    
    # Run recovery cycles
    recovery_cycles = 5
    for i in range(recovery_cycles):
        results = await loop.run_cycle()
        print(f"  Recovery cycle {i+1}: stability={results['stability']:.3f}")
    
    # Check recovery
    recovered = (
        loop.current_state.memory_coherence > 0.5 and
        loop.current_state.ethical_alignment > 0.6 and
        loop.current_state.drift_score < 0.4
    )
    
    print(f"  Recovery successful: {recovered}")
    
    # Final summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    status = loop.get_status()
    print(f"Total cycles: {status['cycles_completed']}")
    print(f"Final stability: {status['stability']:.3f}")
    print(f"Convergence rate: {status['convergence_rate']:.3f}")
    print(f"Oscillation count: {status['oscillation_count']}")
    
    # Determine overall test result
    test_passed = (
        status['stability'] > 0.6 and
        status['convergence_rate'] > 0.5 and
        status['oscillation_count'] < 5
    )
    
    print(f"\n{'✅ TESTS PASSED' if test_passed else '❌ TESTS FAILED'}")
    
    return test_passed


# Module exports
__all__ = [
    "SymbolicFeedbackLoop",
    "SymbolicState",
    "DriftDelta",
    "DriftType",
    "GlyphCorrection",
    "CorrectionDirective",
    "test_feedback_loop_stability"
]