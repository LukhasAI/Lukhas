#!/usr/bin/env python3

"""
VIVOX Integration for Aka Qualia - CollapseHash & DriftScore
===========================================================

Integrates Aka Qualia phenomenological processing with VIVOX consciousness
system, specifically the Z(t) collapse function and drift score monitoring.

Key Integrations:
- CollapseHash verification for phenomenological scenes
- DriftScore monitoring for consciousness stability
- Z(t) collapse integration for state transitions
- VIVOX ME (Memory Expansion) for scene storage
- VIVOX MAE (Moral Alignment Engine) integration
"""
import streamlit as st

import hashlib
import math
import time
from dataclasses import dataclass
from typing import Any, Optional

from candidate.aka_qualia.models import PhenomenalScene, ProtoQualia


@dataclass
class VivoxCollapseState:
    """VIVOX collapse state for phenomenological scenes"""

    scene_id: str
    proto_qualia: ProtoQualia
    probability_amplitude: float
    ethical_weight: float
    emotional_resonance: float
    phase: float
    creation_timestamp: float
    state_vector: list[float]
    collapse_hash: Optional[str] = None


@dataclass
class VivoxDriftResult:
    """VIVOX drift detection result"""

    drift_score: float
    drift_threshold: float
    drift_exceeded: bool
    collapse_hash: str
    timestamp: float
    previous_state_hash: Optional[str]
    stabilization_required: bool


class VivoxAkaQualiaIntegration:
    """
    Integration layer between Aka Qualia and VIVOX consciousness system.

    Provides:
    - CollapseHash generation and verification for phenomenological scenes
    - DriftScore monitoring for consciousness stability
    - Z(t) collapse integration for state transitions
    - VIVOX memory integration for scene persistence
    """

    def __init__(
        self,
        drift_threshold: float = 0.15,
        collapse_validation_enabled: bool = True,
        vivox_me_integration: bool = True,
    ):
        """
        Initialize VIVOX-Aka Qualia integration.

        Args:
            drift_threshold: Maximum allowed drift score (0.15 for strict monitoring)
            collapse_validation_enabled: Enable Z(t) collapse validation
            vivox_me_integration: Enable VIVOX Memory Expansion integration
        """
        self.drift_threshold = drift_threshold
        self.collapse_validation_enabled = collapse_validation_enabled
        self.vivox_me_integration = vivox_me_integration

        # State tracking for drift detection
        self.previous_collapse_hash: Optional[str] = None
        self.collapse_history: list[dict[str, Any]] = []
        self.drift_history: list[VivoxDriftResult] = []

        # Initialize VIVOX components (lazy loading)
        self._vivox_collapse_engine = None
        self._vivox_memory_expansion = None

    def generate_collapse_hash(self, scene: PhenomenalScene) -> str:
        """
        Generate VIVOX-compatible collapse hash for phenomenological scene.

        Uses VIVOX formula: SHA3(z(t) || TraceEcho || MoralFingerprint)
        Adapted for proto-qualia phenomenological data.

        Args:
            scene: PhenomenalScene to hash

        Returns:
            SHA3-256 collapse hash
        """
        # Extract proto-qualia vector components
        pq = scene.proto
        z_component = f"{pq.tone:.6f},{pq.arousal:.6f},{pq.clarity:.6f},{pq.embodiment:.6f}"

        # Create trace echo from temporal and symbolic components
        trace_echo = (
            f"t:{scene.timestamp or time.time()}:.6f}|"
            f"cf:{pq.colorfield}|"
            f"tf:{pq.temporal_feel.value}|"
            f"af:{pq.agency_feel.value}|"
            f"ng:{pq.narrative_gravity:.6f}"
        )

        # Generate moral fingerprint from risk profile
        moral_fingerprint = (
            f"risk:{scene.risk.score:.6f}|"
            f"severity:{scene.risk.severity.value}|"
            f"reasons:{','.join(scene.risk.reasons)} if scene.risk.reasons else 'none'}"
        )

        # Combine components following VIVOX format
        hash_input = f"{z_component}||{trace_echo}||{moral_fingerprint}"

        # Generate SHA3-256 hash (same as VIVOX)
        collapse_hash = hashlib.sha3_256(hash_input.encode("utf-8")).hexdigest()

        return collapse_hash

    def verify_collapse_hash(self, scene: PhenomenalScene, expected_hash: str) -> bool:
        """
        Verify collapse hash integrity for phenomenological scene.

        Args:
            scene: PhenomenalScene to verify
            expected_hash: Expected collapse hash

        Returns:
            True if hash is valid
        """
        computed_hash = self.generate_collapse_hash(scene)
        return computed_hash == expected_hash

    def compute_drift_score(
        self,
        current_scene: PhenomenalScene,
        previous_scene: Optional[PhenomenalScene] = None,
    ) -> VivoxDriftResult:
        """
        Compute VIVOX-style drift score for consciousness stability monitoring.

        Integrates phenomenological coherence with VIVOX drift detection.

        Args:
            current_scene: Current phenomenological scene
            previous_scene: Previous scene for drift comparison

        Returns:
            VivoxDriftResult with drift analysis
        """
        timestamp = time.time()
        current_hash = self.generate_collapse_hash(current_scene)

        if previous_scene is None and self.collapse_history:
            # Use most recent scene from history
            previous_data = self.collapse_history[-1]
            previous_hash = previous_data.get("collapse_hash")
        else:
            previous_hash = self.generate_collapse_hash(previous_scene) if previous_scene else None

        # Compute phenomenological drift
        drift_score = self._compute_phenomenological_drift(current_scene, previous_scene)

        # Apply VIVOX drift threshold
        drift_exceeded = drift_score > self.drift_threshold
        stabilization_required = drift_exceeded or drift_score > (self.drift_threshold * 0.8)

        result = VivoxDriftResult(
            drift_score=drift_score,
            drift_threshold=self.drift_threshold,
            drift_exceeded=drift_exceeded,
            collapse_hash=current_hash,
            timestamp=timestamp,
            previous_state_hash=previous_hash,
            stabilization_required=stabilization_required,
        )

        # Store in history
        self.drift_history.append(result)
        self.previous_collapse_hash = current_hash

        return result

    def _compute_phenomenological_drift(self, current: PhenomenalScene, previous: Optional[PhenomenalScene]) -> float:
        """
        Compute drift score based on phenomenological changes.

        Measures deviation in proto-qualia dimensions and symbolic representations.
        """
        if previous is None:
            return 0.0  # No drift with no comparison

        curr_pq = current.proto
        prev_pq = previous.proto

        # Compute dimensional drifts
        tone_drift = abs(curr_pq.tone - prev_pq.tone)
        arousal_drift = abs(curr_pq.arousal - prev_pq.arousal)
        clarity_drift = abs(curr_pq.clarity - prev_pq.clarity)
        embodiment_drift = abs(curr_pq.embodiment - prev_pq.embodiment)
        narrative_drift = abs(curr_pq.narrative_gravity - prev_pq.narrative_gravity)

        # Symbolic drift (categorical changes have higher impact)
        colorfield_drift = 0.5 if curr_pq.colorfield != prev_pq.colorfield else 0.0
        temporal_drift = 0.3 if curr_pq.temporal_feel != prev_pq.temporal_feel else 0.0
        agency_drift = 0.2 if curr_pq.agency_feel != prev_pq.agency_feel else 0.0

        # Risk profile drift
        risk_drift = abs(current.risk.score - previous.risk.score)
        severity_drift = 0.4 if current.risk.severity != previous.risk.severity else 0.0

        # Weighted combination (matches VIVOX consciousness monitoring)
        drift_components = [
            tone_drift * 0.20,  # Emotional valence changes
            arousal_drift * 0.25,  # Activation level changes
            clarity_drift * 0.15,  # Phenomenal clarity changes
            embodiment_drift * 0.10,  # Body awareness changes
            narrative_drift * 0.10,  # Story gravity changes
            colorfield_drift * 0.05,  # Symbolic palette changes
            temporal_drift * 0.05,  # Temporal feel changes
            agency_drift * 0.05,  # Agency feel changes
            risk_drift * 0.03,  # Risk score changes
            severity_drift * 0.02,  # Risk severity changes
        ]

        total_drift = sum(drift_components)

        # Clamp to [0, 1] range
        return min(1.0, max(0.0, total_drift))

    def create_vivox_collapse_state(self, scene: PhenomenalScene) -> VivoxCollapseState:
        """
        Convert phenomenological scene to VIVOX collapse state representation.

        Args:
            scene: PhenomenalScene to convert

        Returns:
            VivoxCollapseState for VIVOX processing
        """
        pq = scene.proto

        # Create state vector from proto-qualia
        state_vector = [
            pq.tone,
            pq.arousal,
            pq.clarity,
            pq.embodiment,
            pq.narrative_gravity,
        ]

        # Calculate probability amplitude from clarity and embodiment
        probability_amplitude = (pq.clarity + pq.embodiment) / 2.0

        # Ethical weight from risk profile (inverted - lower risk = higher ethical weight)
        ethical_weight = 1.0 - scene.risk.score

        # Emotional resonance from tone and arousal
        emotional_resonance = (abs(pq.tone) + pq.arousal) / 2.0

        # Phase from proto-qualia dimensional angles
        phase = math.atan2(pq.arousal, pq.tone + 1.0)  # Offset tone for positive domain

        # Generate collapse hash
        collapse_hash = self.generate_collapse_hash(scene)

        return VivoxCollapseState(
            scene_id=f"scene_{int(scene.timestamp or time.time()}",
            proto_qualia=pq,
            probability_amplitude=probability_amplitude,
            ethical_weight=ethical_weight,
            emotional_resonance=emotional_resonance,
            phase=phase,
            creation_timestamp=scene.timestamp or time.time(),
            state_vector=state_vector,
            collapse_hash=collapse_hash,
        )

    async def integrate_with_vivox_collapse(self, scene: PhenomenalScene) -> dict[str, Any]:
        """
        Integrate phenomenological scene with VIVOX Z(t) collapse function.

        Args:
            scene: PhenomenalScene to integrate

        Returns:
            VIVOX collapse integration result
        """
        if not self.collapse_validation_enabled:
            return {"status": "collapse_validation_disabled"}

        # Create VIVOX collapse state
        collapse_state = self.create_vivox_collapse_state(scene)

        # Initialize VIVOX collapse engine if needed
        if self._vivox_collapse_engine is None:
            try:
                from candidate.vivox.collapse.z_collapse_engine import ZCollapseEngine

                self._vivox_collapse_engine = ZCollapseEngine(
                    entropy_threshold=0.5,
                    alignment_threshold=0.7,
                    drift_epsilon=self.drift_threshold,
                )
            except ImportError:
                return {
                    "status": "vivox_unavailable",
                    "message": "VIVOX collapse engine not available",
                    "collapse_hash": collapse_state.collapse_hash,
                }

        try:
            # Execute VIVOX Z(t) collapse
            collapse_result = self._vivox_collapse_engine.compute_z_collapse(
                t=time.time(),
                amplitude=collapse_state.probability_amplitude,
                theta=collapse_state.phase,
                entropy_weight=collapse_state.ethical_weight,
                phase_drift=0.0,  # Will be computed by drift detection
                alignment_score=collapse_state.ethical_weight,
            )

            # Store collapse result
            collapse_data = {
                "scene_id": collapse_state.scene_id,
                "collapse_hash": collapse_state.collapse_hash,
                "vivox_z_result": {
                    "real": collapse_result.collapsed_state_vector.real,
                    "imag": collapse_result.collapsed_state_vector.imag,
                    "magnitude": abs(collapse_result.collapsed_state_vector),
                },
                "collapse_status": collapse_result.collapse_status.value,
                "entropy_score": collapse_result.entropy_score,
                "alignment_score": collapse_result.alignment_score,
                "timestamp": collapse_result.collapse_timestamp,
            }

            self.collapse_history.append(collapse_data)

            return {
                "status": "integrated",
                "collapse_result": collapse_data,
                "vivox_validation": collapse_result.collapse_status.value == "success",
            }

        except Exception as e:
            return {
                "status": "integration_error",
                "error": str(e),
                "collapse_hash": collapse_state.collapse_hash,
            }

    async def integrate_with_vivox_memory(self, scene: PhenomenalScene) -> dict[str, Any]:
        """
        Integrate phenomenological scene with VIVOX Memory Expansion (ME).

        Args:
            scene: PhenomenalScene to store

        Returns:
            Memory integration result
        """
        if not self.vivox_me_integration:
            return {"status": "vivox_me_disabled"}

        # Initialize VIVOX ME if needed
        if self._vivox_memory_expansion is None:
            try:
                from candidate.vivox.memory_expansion.vivox_me_core import (
                    VIVOXMemoryExpansion,
                )

                self._vivox_memory_expansion = VIVOXMemoryExpansion()
            except ImportError:
                return {
                    "status": "vivox_me_unavailable",
                    "message": "VIVOX Memory Expansion not available",
                }

        try:
            # Create memory record for phenomenological scene
            memory_data = {
                "experience_type": "phenomenological_scene",
                "proto_qualia": scene.proto.dict(),
                "risk_profile": scene.risk.dict(),
                "context": scene.context,
                "collapse_hash": self.generate_collapse_hash(scene),
                "emotional_dna": {
                    "valence": scene.proto.tone,
                    "arousal": scene.proto.arousal,
                    "embodiment": scene.proto.embodiment,
                    "clarity": scene.proto.clarity,
                },
                "temporal_metadata": {
                    "temporal_feel": scene.proto.temporal_feel.value,
                    "agency_feel": scene.proto.agency_feel.value,
                    "narrative_gravity": scene.proto.narrative_gravity,
                },
                "timestamp": scene.timestamp or time.time(),
            }

            # Store in VIVOX ME
            memory_result = await self._vivox_memory_expansion.store_phenomenological_experience(memory_data)

            return {
                "status": "stored",
                "memory_sequence_id": memory_result.get("sequence_id"),
                "emotional_resonance": memory_result.get("emotional_resonance"),
                "storage_success": memory_result.get("success", False),
            }

        except Exception as e:
            return {"status": "storage_error", "error": str(e)}

    def get_drift_status(self) -> dict[str, Any]:
        """Get current VIVOX drift monitoring status"""
        if not self.drift_history:
            return {"status": "no_drift_data", "drift_threshold": self.drift_threshold}

        latest_drift = self.drift_history[-1]

        # Calculate drift trend
        if len(self.drift_history) >= 3:
            recent_scores = [d.drift_score for d in self.drift_history[-3:]]
            drift_trend = "increasing" if recent_scores[-1] > recent_scores[0] else "decreasing"
        else:
            drift_trend = "insufficient_data"

        return {
            "status": "active",
            "latest_drift_score": latest_drift.drift_score,
            "drift_threshold": self.drift_threshold,
            "drift_exceeded": latest_drift.drift_exceeded,
            "stabilization_required": latest_drift.stabilization_required,
            "drift_trend": drift_trend,
            "collapse_hash": latest_drift.collapse_hash,
            "monitoring_history": len(self.drift_history),
            "vivox_integration": {
                "collapse_validation": self.collapse_validation_enabled,
                "memory_expansion": self.vivox_me_integration,
            },
        }

    def get_collapse_history(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent VIVOX collapse history"""
        return self.collapse_history[-limit:] if self.collapse_history else []
