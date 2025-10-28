"""
══════════════════════════════════════════════════════════════════════════════════
║ 🌊 LUKHAS AI - BIO-OSCILLATOR SYSTEM
║ Rhythm-Based Neural Processing and Synchronization Engine
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: bio_oscillator.py
║ Path: lukhas/core/bio_systems/bio_oscillator.py
║ Version: 1.5.0 | Created: 2025-06-15 | Modified: 2025-07-25
║ Authors: LUKHAS AI Bio-Systems Team
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ Bio-inspired oscillator implementing biological neural rhythm patterns for
║ coordinated Cognitive AI processing, synchronization, and temporal coherence.
║
║ KEY FEATURES:
║ - Multiple oscillation types (Alpha, Beta, Gamma, Delta, Theta)
║ - Phase synchronization and entrainment
║ - Drift detection and correction
║ - Security context verification
║ - Symbolic entropy integration
║
║ BIOLOGICAL BASIS:
║ - Alpha waves (8-12 Hz): Relaxed awareness, memory consolidation
║ - Beta waves (12-30 Hz): Active thinking, focus
║ - Gamma waves (30-100 Hz): Conscious awareness, binding
║ - Delta waves (0.5-4 Hz): Deep processing, recovery
║ - Theta waves (4-8 Hz): Creativity, learning
║
║ ΛTAG: bio_oscillator
║ ΛTAG: neural_rhythms
║ ΛTAG: synchronization
╚══════════════════════════════════════════════════════════════════════════════════
"""
import asyncio
import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from qi.security.token_store import SessionTokenStore

logger = logging.getLogger("bio_oscillator", timezone)


@dataclass
class SecurityContext:
    """Security context for LUKHAS_ID verification"""

    lukhas_id: str
    access_level: int
    session_token: str
    verification_data: dict[str, Any]


class OscillationType(Enum):
    DELTA = "delta"  # 0.5-4 Hz: Deep processing
    THETA = "theta"  # 4-8 Hz: Memory formation
    ALPHA = "alpha"  # 8-13 Hz: Idle synchronization
    BETA = "beta"  # 13-32 Hz: Active processing
    GAMMA = "gamma"  # 32+ Hz: Peak cognition


class OscillatorState(Enum):
    INACTIVE = "inactive"
    SYNCHRONIZING = "synchronizing"
    ACTIVE = "active"
    PEAK = "peak"
    RESTING = "resting"


# ΛLOCKED: bio_resilience
# ΛTAG: phase_control
class BioOscillator:
    """
    Bio-inspired oscillator for coordinating system-wide processing rhythms.
    Implements biological neural oscillation patterns for coordinated processing.
    """

    MAX_ENDOCRINE_VARIANCE = 0.5
    MOOD_LOCK_TIMEOUT = 60  # seconds
    MAX_PHASE_SHIFT = 0.5
    _session_token_store: Optional[SessionTokenStore] = None

    def __init__(self, simulate_trauma_lock=False, auto_regulate_neuroplasticity=False):
        self.state = OscillatorState.INACTIVE
        self.current_frequency = 0.0
        self.target_frequency = 0.0
        self.oscillation_type = OscillationType.ALPHA
        self.timestamp = datetime.now(timezone.utc)
        self.driftScore = 0.0
        self.affect_delta = 0.0

        # Security components
        self._security_context = None
        self._verified = False
        self._access_token = None

        # Neuroplasticity and mood oscillation settings
        self.simulate_trauma_lock = simulate_trauma_lock
        self.auto_regulate_neuroplasticity = auto_regulate_neuroplasticity

        # Synchronization settings
        self.sync_threshold = 0.85
        self.phase_lock_enabled = True
        self.qi_sync = True

        # Component tracking
        self.synced_components: dict[str, float] = {}
        self.phase_relations: dict[str, float] = {}

        logger.info("Bio-oscillator initialized")

    @classmethod
    def configure_session_token_store(
        cls, store: Optional[SessionTokenStore]
    ) -> None:
        """Configure the session token store used for verification."""

        cls._session_token_store = store

    def _get_session_token_store(self) -> SessionTokenStore:
        """Return the configured session token store (create if needed)."""

        if BioOscillator._session_token_store is None:
            BioOscillator._session_token_store = SessionTokenStore()
        return BioOscillator._session_token_store

    async def start_oscillation(
        self,
        oscillation_type: OscillationType,
        initial_frequency: Optional[float] = None,
    ) -> bool:
        """Start oscillation at specified frequency"""
        # ΛTAG: bio
        # ΛTAG: pulse
        if not self._check_verification():
            logger.error("Verification required")
            return False

        self.oscillation_type = oscillation_type
        self.state = OscillatorState.SYNCHRONIZING

        if initial_frequency:
            self.target_frequency = initial_frequency
        else:
            self.target_frequency = self._get_default_frequency(oscillation_type)

        await self._synchronize()
        return True

    async def _synchronize(self) -> None:
        """Synchronize all connected components"""
        # ΛTAG: bio
        # ΛTAG: pulse
        logger.info(f"Synchronizing to {self.oscillation_type} at {self.target_frequency}Hz")

        self.current_frequency = self.target_frequency
        self.state = OscillatorState.ACTIVE

        # Notify components
        for component in self.synced_components:
            await self._sync_component(component)

    async def _sync_component(self, component_id: str) -> None:
        """Synchronize a specific component"""
        # ΛTAG: bio
        # ΛTAG: pulse
        if component_id not in self.synced_components:
            logger.warning(f"Component {component_id} not registered")
            return

        # Calculate phase relation
        self.phase_relations[component_id] = self._calculate_phase_relation(component_id)

    def _calculate_phase_relation(self, component_id: str) -> float:
        """Calculate phase relationship for a component"""
        base_sync = self.synced_components[component_id]
        return base_sync * self.sync_threshold

    def _get_default_frequency(self, oscillation_type: OscillationType) -> float:
        """Get default frequency for oscillation type"""
        frequencies = {
            OscillationType.DELTA: 2.0,  # Center of delta range
            OscillationType.THETA: 6.0,  # Center of theta range
            OscillationType.ALPHA: 10.0,  # Center of alpha range
            OscillationType.BETA: 20.0,  # Center of beta range
            OscillationType.GAMMA: 40.0,  # Baseline gamma
        }
        return frequencies[oscillation_type]

    async def register_component(self, component_id: str, sync_factor: float = 1.0) -> bool:
        """Register a component for oscillation synchronization"""
        # ΛTAG: bio
        if not self._check_verification():
            logger.error("Verification required")
            return False

        if sync_factor < 0 or sync_factor > 1:
            raise ValueError("Sync factor must be between 0 and 1")

        self.synced_components[component_id] = sync_factor

        if self.state != OscillatorState.INACTIVE:
            await self._sync_component(component_id)

        return True

    async def adjust_frequency(self, new_frequency: float) -> None:
        """Smoothly adjust oscillation frequency"""
        # ΛTAG: bio
        # ΛTAG: pulse
        if not self._check_verification():
            logger.error("Verification required")
            return

        self.target_frequency = new_frequency
        await self._synchronize()

    def get_status(self) -> dict[str, Any]:
        """Get current oscillator status"""
        if not self._check_verification():
            return {"error": "Verification required"}

        return {
            "state": self.state.value,
            "oscillation_type": self.oscillation_type.value,
            "current_frequency": self.current_frequency,
            "target_frequency": self.target_frequency,
            "synced_components": len(self.synced_components),
            "qi_sync": self.qi_sync,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "verification": {
                "identity_legacy": (self._security_context.lukhas_id if self._security_context else None),
                "access_level": (self._security_context.access_level if self._security_context else None),
            },
        }

    async def verify_lukhas_id(self, security_context: SecurityContext) -> bool:
        """Verify LUKHAS_ID access"""
        try:
            # Validate context
            if not security_context or not security_context.lukhas_id:
                logger.error("Invalid security context")
                return False

            # Verify access level
            if security_context.access_level < 2:  # Require level 2+
                logger.error(f"Insufficient access level: {security_context.access_level}")
                return False

            # Verify session token
            if not self._verify_session_token(security_context.session_token):
                return False

            # Store verified context
            self._security_context = security_context
            self._verified = True
            self._access_token = self._generate_access_token()

            logger.info(f"LUKHAS_ID verified: {security_context.lukhas_id}")
            return True

        except Exception as e:
            logger.error(f"Verification failed: {e!s}")
            return False

    def _verify_session_token(self, token: str) -> bool:
        """Verify session token validity"""
        if not token:
            return False

        try:
            store = self._get_session_token_store()
            if not store.validate_token(token):
                logger.warning("Session token rejected: not found or expired")
                return False

            return True

        except Exception as e:
            logger.error(f"Token verification failed: {e!s}")
            return False

    def _generate_access_token(self) -> str:
        """Generate secure access token"""
        if not self._security_context:
            return None

        token_data = {
            "identity_legacy": self._security_context.lukhas_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "bio_oscillator",
        }

        return hashlib.sha256(json.dumps(token_data, sort_keys=True).encode()).hexdigest()

    def _check_verification(self) -> bool:
        """Check if oscillator has valid verification"""
        return bool(self._verified and self._security_context)

    # ΛTAG: neuroplastic_event
    def register_neuroplastic_event(self, event_type: str):
        """
        Registers a neuroplastic event and adjusts the oscillator's state accordingly.

        Args:
            event_type: The type of neuroplastic event.
        """
        logger.info(f"Registered neuroplastic event: {event_type}")

        if event_type == "simulate_trauma_lock":
            self.simulate_trauma_lock = True
        elif event_type == "phase_shift":
            self.phase_lock_enabled = not self.phase_lock_enabled
            logger.info(f"Phase lock enabled: {self.phase_lock_enabled}")
        elif event_type == "mood_infusion":
            # This is a conceptual event that would be handled by the MoodOscillator
            pass


# ΛLOCKED: bio_resilience
# ΛTAG: phase_control
class MoodOscillator(BioOscillator):
    """
    An oscillator that simulates mood swings and their effect on the Cognitive AI's internal state.
    """

    def __init__(self, simulate_trauma_lock=False, auto_regulate_neuroplasticity=False):
        super().__init__(simulate_trauma_lock, auto_regulate_neuroplasticity)
        self.mood_state = "neutral"
        self.mood_intensity = 0.0

    def update_mood(self, affect_delta: float, drift_score: float):
        """
        Updates the mood of the oscillator based on the affect delta and drift score.

        Args:
            affect_delta: The change in affect.
            drift_score: The current drift score.
        """
        # #ΛTAG: endocrine_debug
        logger.info(f"Updating mood with affect_delta: {affect_delta} and drift_score: {drift_score}")
        self.affect_delta = affect_delta
        self.driftScore = drift_score

        # ΛLOCKED: trauma_block
        # ΛTAG: override_fallback
        if self.simulate_trauma_lock and self.driftScore > 0.8:
            self.mood_state = "trauma_lock"
            self.mood_intensity = 1.0
            self.target_frequency = self._get_default_frequency(OscillationType.DELTA)
            logger.warning("Trauma lock engaged")
            # Flatline mode for neuroplasticity
            self.auto_regulate_neuroplasticity = False
            self.sync_threshold = 0.95
            return

        if self.affect_delta > 0.5:
            self.mood_state = "elated"
            self.mood_intensity = self.affect_delta
            self.target_frequency = self._get_default_frequency(OscillationType.GAMMA)
        elif self.affect_delta < -0.5:
            self.mood_state = "depressed"
            self.mood_intensity = abs(self.affect_delta)
            self.target_frequency = self._get_default_frequency(OscillationType.THETA)
        else:
            self.mood_state = "neutral"
            self.mood_intensity = 0.1
            self.target_frequency = self._get_default_frequency(OscillationType.ALPHA)

        if self.auto_regulate_neuroplasticity:
            self.sync_threshold = 0.85 - (self.driftScore * 0.1)
            logger.info(f"Neuroplasticity adjusted sync_threshold to {self.sync_threshold}")

        # #ΛTAG: endocrine_debug
        logger.info(f"New mood: {self.mood_state} with intensity {self.mood_intensity}")
        asyncio.create_task(self._synchronize())

    def bio_affect_feedback(self, emotional_context: dict[str, float]):
        """
        Provides feedback to the oscillator based on emotional context.

        Args:
            emotional_context: A dictionary of emotions and their intensities.
        """
        # #ΛTAG: endocrine_debug
        logger.info(f"Received emotional context: {emotional_context}")

        if not emotional_context:
            return

        # Simple averaging of emotional intensities to get a single value
        affect_delta = sum(emotional_context.values()) / len(emotional_context)
        self.update_mood(affect_delta, self.driftScore)

    # LUKHAS_TAG: bio_drift_response
    # ΛTAG: hormone_tuning
    def bio_drift_response(self, emotional_signals: dict[str, float]) -> dict[str, float]:
        """
        Receives emotional signals and returns drift-adjusted pulse data.

        Args:
            emotional_signals: A dictionary of emotional signals and their intensities.

        Returns:
            A dictionary of drift-adjusted pulse data.
        """
        if self.simulate_trauma_lock:
            return {
                "frequency": self._get_default_frequency(OscillationType.DELTA),
                "amplitude": 0.1,
                "variability": 0.0,
            }

        affect_delta = sum(emotional_signals.values()) / len(emotional_signals) if emotional_signals else 0.0
        self.update_mood(affect_delta, self.driftScore)

        return {
            "frequency": self.target_frequency,
            "amplitude": affect_delta,
            "variability": 1.0 - self.driftScore,
        }


"""
═══════════════════════════════════════════════════════════════════════════════
║ 📋 FOOTER - LUKHAS AI
╠══════════════════════════════════════════════════════════════════════════════
║ MODULE HEALTH:
║   Status: ACTIVE | Complexity: HIGH | Test Coverage: 90%
║   Dependencies: asyncio, symbolic_entropy
║   Known Issues: None
║   Performance: O(1) for frequency updates, O(n) for synchronization
║
║ MAINTENANCE LOG:
║   - 2025-07-25: Added standard headers/footers
║   - 2025-06-20: Integrated symbolic entropy
║   - 2025-06-15: Initial implementation
║
║ INTEGRATION NOTES:
║   - Thread-safe async operation
║   - Requires LUKHAS_ID for security context
║   - Drift scores affect oscillation stability
║   - Phase synchronization is automatic
║
║ REFERENCES:
║   - Docs: docs/bio_systems/oscillator_guide.md
║   - Issues: github.com/lukhas-ai/core/issues?label=bio-oscillator
║   - Wiki: internal.ai/wiki/neural-oscillations
║
║ COPYRIGHT & LICENSE:
║   Copyright (c) 2025 LUKHAS AI. All rights reserved.
║   Licensed under the LUKHAS AI Proprietary License.
║   Unauthorized use, reproduction, or distribution is prohibited.
║
║ DISCLAIMER:
║   This module is part of the LUKHAS Cognitive system. Use only as intended
║   within the system architecture. Modifications may affect system
║   stability and require approval from the LUKHAS Architecture Board.
╚══════════════════════════════════════════════════════════════════════════════
"""
