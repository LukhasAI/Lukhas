"""
Symbolic Loop Harmonizer
Harmonizes reasoning loops by detecting and correcting symbolic misalignments
"""

from core.common import get_logger
import asyncio
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime, timedelta
from collections import defaultdict
import json
import numpy as np
from enum import Enum
from pathlib import Path

logger = get_logger(__name__)


class HarmonizerMode(Enum):
    """Operating modes for the harmonizer"""
    PASSIVE = "passive"  # Monitor only
    ACTIVE = "active"    # Apply corrections
    ADAPTIVE = "adaptive" # Learn and adapt
    DREAM = "dream"      # Dream-state integration


class SymbolicPatch:
    """Represents a symbolic correction patch"""

    def __init__(self, patch_type: str, target_symbol: str,
                 correction: Any, confidence: float = 0.8):
        self.patch_type = patch_type
        self.target_symbol = target_symbol
        self.correction = correction
        self.confidence = confidence
        self.timestamp = datetime.now()
        self.applied = False
        self.impact = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "patch_type": self.patch_type,
            "target_symbol": self.target_symbol,
            "correction": self.correction,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "applied": self.applied,
            "impact": self.impact
        }


class SymbolicLoopHarmonizer:
    """
    Harmonizes symbolic reasoning loops to maintain coherence
    and prevent divergence in long-running reasoning chains
    """

    def __init__(self, mode: HarmonizerMode = HarmonizerMode.ACTIVE):
        self.mode = mode
        self.harmony_threshold = 0.7
        self.drift_tolerance = 0.3
        self.symbol_registry = {}
        self.harmony_history = []
        self.patch_history = []
        self.dream_state = None
        self.emotional_alignments = defaultdict(float)

        # Harmonization strategies
        self.strategies = {
            "polarity_inversion": self._polarity_inversion_strategy,
            "memory_anchoring": self._memory_anchoring_strategy,
            "symbol_realignment": self._symbol_realignment_strategy,
            "resonance_tuning": self._resonance_tuning_strategy,
            "dream_integration": self._dream_integration_strategy
        }

        self.log_dir = Path("lukhas/logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)

    async def harmonize_trace(self,
                            unstable_trace: Dict[str, Any],
                            context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Harmonize an unstable reasoning trace

        Args:
            unstable_trace: The trace showing instability
            context: Additional context for harmonization

        Returns:
            Harmonization result with suggested patches
        """
        logger.info(f"Harmonizing trace in {self.mode.value} mode")

        # Analyze the trace
        analysis = await self._analyze_symbolic_stability(unstable_trace)

        # Generate patches based on analysis
        patches = await self._generate_symbolic_patches(analysis, unstable_trace)

        # Apply patches if in active mode
        harmonized_trace = unstable_trace.copy()
        applied_patches = []

        if self.mode in [HarmonizerMode.ACTIVE, HarmonizerMode.ADAPTIVE]:
            for patch in patches:
                try:
                    harmonized_trace = await self._apply_symbolic_patch(
                        harmonized_trace, patch
                    )
                    patch.applied = True
                    applied_patches.append(patch)

                    # Record impact
                    patch.impact = await self._measure_patch_impact(
                        unstable_trace, harmonized_trace
                    )

                except Exception as e:
                    logger.error(f"Failed to apply patch: {e}")

        # Dream integration if enabled
        if self.mode == HarmonizerMode.DREAM and self.dream_state:
            dream_adjustments = await self._integrate_dream_state(
                harmonized_trace, applied_patches
            )
            harmonized_trace.update(dream_adjustments)

        # Calculate harmony score
        harmony_score = await self._calculate_harmony_score(harmonized_trace)

        # Store in history
        result = {
            "original_trace": unstable_trace,
            "harmonized_trace": harmonized_trace,
            "analysis": analysis,
            "patches_generated": len(patches),
            "patches_applied": len(applied_patches),
            "harmony_score": harmony_score,
            "mode": self.mode.value,
            "timestamp": datetime.now().isoformat()
        }

        self.harmony_history.append(result)
        self.patch_history.extend(applied_patches)

        # Log results
        await self._log_harmonization(result)

        return result

    async def _analyze_symbolic_stability(self, trace: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze symbolic stability of a reasoning trace
        """
        analysis = {
            "drift_score": trace.get("drift_score", 0.0),
            "symbol_coherence": 0.0,
            "loop_detection": False,
            "divergence_risk": 0.0,
            "unstable_symbols": [],
            "recommendation": "none"
        }

        # Analyze symbol usage patterns
        symbols = trace.get("symbols", [])
        if symbols:
            # Check for undefined symbols
            undefined = [s for s in symbols if s not in self.symbol_registry]
            if undefined:
                analysis["unstable_symbols"].extend(undefined)
                analysis["symbol_coherence"] = 1.0 - (len(undefined) / len(symbols))
            else:
                analysis["symbol_coherence"] = 1.0

        # Check for reasoning loops
        path = trace.get("reasoning_path", [])
        if self._detect_reasoning_loop(path):
            analysis["loop_detection"] = True
            analysis["divergence_risk"] += 0.3

        # Calculate overall stability
        drift = analysis["drift_score"]
        coherence = analysis["symbol_coherence"]

        if drift > 0.8 or coherence < 0.3:
            analysis["recommendation"] = "urgent_harmonization"
            analysis["divergence_risk"] = 0.9
        elif drift > 0.6 or coherence < 0.5:
            analysis["recommendation"] = "moderate_harmonization"
            analysis["divergence_risk"] = 0.6
        elif drift > 0.3:
            analysis["recommendation"] = "light_harmonization"
            analysis["divergence_risk"] = 0.3
        else:
            analysis["recommendation"] = "monitoring_only"

        return analysis

    def _detect_reasoning_loop(self, path: List[Dict[str, Any]]) -> bool:
        """
        Detect if reasoning is stuck in a loop
        """
        if len(path) < 4:
            return False

        # Check for repeated patterns
        strategies = [step.get("strategy", "") for step in path]

        # Simple loop detection - check for repeated subsequences
        for window_size in range(2, min(5, len(strategies) // 2)):
            for i in range(len(strategies) - window_size * 2):
                pattern = strategies[i:i+window_size]
                next_pattern = strategies[i+window_size:i+window_size*2]
                if pattern == next_pattern:
                    return True

        return False

    async def _generate_symbolic_patches(self,
                                       analysis: Dict[str, Any],
                                       trace: Dict[str, Any]) -> List[SymbolicPatch]:
        """
        Generate symbolic patches based on analysis
        """
        patches = []

        # Select strategies based on analysis
        if analysis["drift_score"] > 0.8:
            patch = await self.strategies["polarity_inversion"](trace, analysis)
            if patch:
                patches.append(patch)

        if analysis["drift_score"] > 0.6:
            patch = await self.strategies["memory_anchoring"](trace, analysis)
            if patch:
                patches.append(patch)

        if analysis["symbol_coherence"] < 0.5:
            patch = await self.strategies["symbol_realignment"](trace, analysis)
            if patch:
                patches.append(patch)

        if analysis["loop_detection"]:
            patch = await self.strategies["resonance_tuning"](trace, analysis)
            if patch:
                patches.append(patch)

        # Dream integration strategy if applicable
        if self.mode == HarmonizerMode.DREAM:
            patch = await self.strategies["dream_integration"](trace, analysis)
            if patch:
                patches.append(patch)

        return patches

    async def _polarity_inversion_strategy(self,
                                         trace: Dict[str, Any],
                                         analysis: Dict[str, Any]) -> Optional[SymbolicPatch]:
        """
        Invert reasoning polarity to correct severe drift
        """
        return SymbolicPatch(
            patch_type="polarity_inversion",
            target_symbol="reasoning_direction",
            correction={
                "action": "invert",
                "strength": min(analysis["drift_score"], 1.0),
                "apply_to": "future_steps"
            },
            confidence=0.8
        )

    async def _memory_anchoring_strategy(self,
                                       trace: Dict[str, Any],
                                       analysis: Dict[str, Any]) -> Optional[SymbolicPatch]:
        """
        Anchor reasoning to stable memory patterns
        """
        return SymbolicPatch(
            patch_type="memory_anchor",
            target_symbol="memory_reference",
            correction={
                "action": "reinforce_anchor",
                "anchor_points": ["initial_premise", "core_axioms"],
                "strength": 0.7
            },
            confidence=0.75
        )

    async def _symbol_realignment_strategy(self,
                                         trace: Dict[str, Any],
                                         analysis: Dict[str, Any]) -> Optional[SymbolicPatch]:
        """
        Realign unstable symbols with registry
        """
        unstable = analysis.get("unstable_symbols", [])
        if not unstable:
            return None

        return SymbolicPatch(
            patch_type="symbol_realignment",
            target_symbol="symbol_definitions",
            correction={
                "action": "realign",
                "symbols": unstable[:5],  # Limit to 5 symbols
                "method": "registry_lookup",
                "fallback": "auto_define"
            },
            confidence=0.85
        )

    async def _resonance_tuning_strategy(self,
                                       trace: Dict[str, Any],
                                       analysis: Dict[str, Any]) -> Optional[SymbolicPatch]:
        """
        Tune reasoning resonance to break loops
        """
        return SymbolicPatch(
            patch_type="resonance_tuning",
            target_symbol="reasoning_frequency",
            correction={
                "action": "detune",
                "shift": 0.1 + (0.2 * analysis.get("divergence_risk", 0.5)),
                "damping": 0.3
            },
            confidence=0.7
        )

    async def _dream_integration_strategy(self,
                                        trace: Dict[str, Any],
                                        analysis: Dict[str, Any]) -> Optional[SymbolicPatch]:
        """
        Integrate dream-state insights for creative solutions
        """
        if not self.dream_state:
            return None

        return SymbolicPatch(
            patch_type="dream_integration",
            target_symbol="creative_insight",
            correction={
                "action": "inject_dream_pattern",
                "pattern": self.dream_state.get("current_pattern", "default"),
                "blend_ratio": 0.3
            },
            confidence=0.6
        )

    async def _apply_symbolic_patch(self,
                                  trace: Dict[str, Any],
                                  patch: SymbolicPatch) -> Dict[str, Any]:
        """
        Apply a symbolic patch to a trace
        """
        patched_trace = trace.copy()

        # Apply based on patch type
        if patch.patch_type == "polarity_inversion":
            # Invert reasoning direction
            if "metadata" not in patched_trace:
                patched_trace["metadata"] = {}
            patched_trace["metadata"]["polarity_inverted"] = True
            patched_trace["metadata"]["inversion_strength"] = patch.correction["strength"]

        elif patch.patch_type == "memory_anchor":
            # Add memory anchors
            if "anchors" not in patched_trace:
                patched_trace["anchors"] = []
            patched_trace["anchors"].extend(patch.correction["anchor_points"])

        elif patch.patch_type == "symbol_realignment":
            # Realign symbols
            for symbol in patch.correction["symbols"]:
                if symbol not in self.symbol_registry:
                    # Auto-define if needed
                    self.symbol_registry[symbol] = {
                        "definition": f"auto_defined_{symbol}",
                        "timestamp": datetime.now().isoformat()
                    }

        elif patch.patch_type == "resonance_tuning":
            # Adjust resonance parameters
            if "resonance" not in patched_trace:
                patched_trace["resonance"] = {}
            patched_trace["resonance"]["frequency_shift"] = patch.correction["shift"]
            patched_trace["resonance"]["damping"] = patch.correction["damping"]

        elif patch.patch_type == "dream_integration":
            # Blend dream patterns
            if "dream_blend" not in patched_trace:
                patched_trace["dream_blend"] = {}
            patched_trace["dream_blend"]["pattern"] = patch.correction["pattern"]
            patched_trace["dream_blend"]["ratio"] = patch.correction["blend_ratio"]

        return patched_trace

    async def _measure_patch_impact(self,
                                  original: Dict[str, Any],
                                  patched: Dict[str, Any]) -> Dict[str, Any]:
        """
        Measure the impact of a patch
        """
        # Simple impact measurement
        original_drift = original.get("drift_score", 0.5)
        patched_drift = patched.get("drift_score", original_drift * 0.8)

        impact = {
            "drift_reduction": original_drift - patched_drift,
            "stability_improvement": 0.2,  # Placeholder
            "side_effects": []
        }

        return impact

    async def _integrate_dream_state(self,
                                   trace: Dict[str, Any],
                                   patches: List[SymbolicPatch]) -> Dict[str, Any]:
        """
        Integrate dream state adjustments
        """
        adjustments = {}

        if self.dream_state and self.dream_state.get("active"):
            # Adjust based on dream insights
            dream_influence = self.dream_state.get("influence", 0.3)

            adjustments["dream_influenced"] = True
            adjustments["dream_confidence_boost"] = dream_influence * 0.5

            # Record emotional alignment
            for patch in patches:
                if patch.applied:
                    self._record_emotional_alignment(patch, dream_influence)

        return adjustments

    async def _calculate_harmony_score(self, trace: Dict[str, Any]) -> float:
        """
        Calculate overall harmony score of a trace
        """
        factors = []

        # Drift factor (inverted)
        drift = trace.get("drift_score", 0.0)
        factors.append(1.0 - min(drift, 1.0))

        # Symbol coherence
        symbols = trace.get("symbols", [])
        if symbols:
            defined = sum(1 for s in symbols if s in self.symbol_registry)
            coherence = defined / len(symbols)
            factors.append(coherence)

        # Resonance stability
        if "resonance" in trace:
            # Lower frequency shift = more stable
            shift = trace["resonance"].get("frequency_shift", 0.0)
            stability = 1.0 - min(abs(shift), 1.0)
            factors.append(stability)

        # Dream integration bonus
        if "dream_blend" in trace:
            factors.append(0.8)  # Bonus for dream integration

        return sum(factors) / len(factors) if factors else 0.5

    async def _log_harmonization(self, result: Dict[str, Any]):
        """
        Log harmonization results
        """
        log_entry = {
            "timestamp": result["timestamp"],
            "mode": result["mode"],
            "patches_applied": result["patches_applied"],
            "harmony_score": result["harmony_score"],
            "analysis": result["analysis"]
        }

        log_file = self.log_dir / "symbolic_harmonization.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    def _record_emotional_alignment(self, patch: SymbolicPatch, influence: float):
        """
        Record emotional alignment impact of a patch
        """
        alignment_key = f"{patch.patch_type}_{patch.target_symbol}"
        self.emotional_alignments[alignment_key] += influence

        logger.info(f"Emotional alignment recorded: {alignment_key} += {influence}")

    def update_symbol_registry(self, symbols: Dict[str, Any]):
        """
        Update the symbol registry with new definitions
        """
        self.symbol_registry.update(symbols)
        logger.info(f"Symbol registry updated with {len(symbols)} symbols")

    def set_dream_state(self, dream_state: Dict[str, Any]):
        """
        Set the current dream state for integration
        """
        self.dream_state = dream_state
        if dream_state.get("active"):
            self.mode = HarmonizerMode.DREAM
            logger.info("Dream integration mode activated")

    def get_harmony_summary(self, last_n: int = 10) -> Dict[str, Any]:
        """
        Get summary of recent harmonizations
        """
        recent = self.harmony_history[-last_n:]

        if not recent:
            return {"status": "no_history"}

        avg_harmony = sum(h["harmony_score"] for h in recent) / len(recent)
        total_patches = sum(h["patches_applied"] for h in recent)

        summary = {
            "harmonizations_analyzed": len(recent),
            "average_harmony_score": avg_harmony,
            "total_patches_applied": total_patches,
            "mode_distribution": defaultdict(int),
            "emotional_alignments": dict(self.emotional_alignments)
        }

        for h in recent:
            summary["mode_distribution"][h["mode"]] += 1

        return summary


# Global harmonizer instance
_harmonizer = None


def get_harmonizer(mode: HarmonizerMode = HarmonizerMode.ACTIVE) -> SymbolicLoopHarmonizer:
    """Get or create the global harmonizer instance"""
    global _harmonizer
    if _harmonizer is None:
        _harmonizer = SymbolicLoopHarmonizer(mode)
    return _harmonizer


# Backward compatibility functions
def harmonize_symbolic_loop(unstable_trace: Dict[str, Any]) -> Dict[str, Any]:
    """
    Accepts unstable traces and suggests a symbolic patch.
    """
    if not unstable_trace:
        return {"suggestion": "No trace provided."}

    harmonizer = get_harmonizer()

    # Run async function in sync context
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        result = loop.run_until_complete(
            harmonizer.harmonize_trace(unstable_trace)
        )

        # Extract suggestion from patches
        if result["patches_applied"] > 0:
            patch = harmonizer.patch_history[-1]
            return {
                "suggestion": f"{patch.patch_type}: {patch.correction}",
                "harmony_score": result["harmony_score"]
            }
        else:
            drift_score = unstable_trace.get("drift_score", 0.0)
            if drift_score > 0.8:
                return {"suggestion": "Invert drift polarity."}
            elif drift_score > 0.6:
                return {"suggestion": "Adjust memory anchor."}
            else:
                return {"suggestion": "No patch needed."}

    finally:
        loop.close()


def adjust_dream_trajectory(patch: Dict[str, Any]) -> None:
    """
    Adjusts dream trajectories live based on harmonizer patches.
    """
    harmonizer = get_harmonizer()

    # Update dream state
    dream_state = {
        "active": True,
        "current_pattern": patch.get("pattern", "default"),
        "influence": patch.get("influence", 0.5)
    }

    harmonizer.set_dream_state(dream_state)
    logger.info(f"Adjusting dream trajectory with patch: {patch}")


def record_emotional_alignment_impact(patch: Dict[str, Any]) -> None:
    """
    Records emotional alignment impact of a patch.
    """
    harmonizer = get_harmonizer()

    # Create a symbolic patch from the dict
    symbolic_patch = SymbolicPatch(
        patch_type=patch.get("type", "unknown"),
        target_symbol=patch.get("target", "unknown"),
        correction=patch.get("correction", {}),
        confidence=patch.get("confidence", 0.5)
    )

    influence = patch.get("emotional_influence", 0.3)
    harmonizer._record_emotional_alignment(symbolic_patch, influence)

    logger.info(f"Recording emotional alignment impact of patch: {patch}")
