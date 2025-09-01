#!/usr/bin/env python3

"""
Oneiric Hook for Narrative Feedback (Wave C - C3)
================================================

Implements RegulationPolicy → dream generation feedback integration.
Provides control hints for next narrative steps based on phenomenological regulation.

Connects AKA QUALIA regulation policies to the existing LUKHAS oneiric/dream systems,
enabling closed-loop phenomenological control with narrative feedback.
"""

import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests

from candidate.aka_qualia.models import PhenomenalScene, RegulationPolicy
from candidate.aka_qualia.palette import get_safe_palette_recommendation

logger = logging.getLogger(__name__)


class OneiricHook:
    """
    Oneiric hook for applying regulation policies to dream/narrative generation.

    Converts RegulationPolicy outputs into actionable control hints for LUKHAS
    oneiric systems, enabling phenomenological feedback loops.
    """

    def __init__(self, http_client: Optional["OneiricHTTPClient"] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize oneiric hook.

        Args:
            http_client: Optional HTTP client for external oneiric services
            config: Configuration overrides
        """
        self.http_client = http_client
        self.config = self._load_config(config)

        # Statistics
        self.policies_applied = 0
        self.http_requests_sent = 0
        self.http_failures = 0

    def _load_config(self, config_override: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Load oneiric hook configuration"""
        default_config = {
            "enable_palette_hints": True,
            "enable_tempo_modulation": True,
            "enable_action_suggestions": True,
            "grounding_urgency_threshold": 0.7,
            "tempo_smoothing_factor": 0.8,
            "palette_culture_profile": "default",
            "http_timeout_seconds": 5.0,
            "enable_symbolic_anchors": True,
        }

        if config_override:
            default_config.update(config_override)

        return default_config

    def apply_policy(self, *, scene: PhenomenalScene, policy: RegulationPolicy) -> Dict[str, Any]:
        """
        Apply regulation policy to generate control hints for narrative feedback.

        Core Wave C C3 implementation: RegulationPolicy → dream generation feedback.

        Args:
            scene: PhenomenalScene for context
            policy: RegulationPolicy to apply

        Returns:
            Dict containing control hints:
            - tempo: float [0.1, 2.0] - temporal pace adjustment
            - palette_hint: str - suggested colorfield for grounding
            - ops: List[str] - regulation operations to perform
            - anchors: Dict - symbolic anchors when grounding needed
        """
        self.policies_applied += 1

        hints = {
            "tempo": self._compute_tempo_hint(scene, policy),
            "palette_hint": self._compute_palette_hint(scene, policy),
            "ops": self._compute_operation_hints(scene, policy),
            "anchors": {},
        }

        # Add symbolic anchors when grounding is urgently needed
        if self.config["enable_symbolic_anchors"]:
            grounding_urgency = self._compute_grounding_urgency(scene)
            if grounding_urgency >= self.config["grounding_urgency_threshold"]:
                hints["anchors"] = self._generate_symbolic_anchors(scene, policy, grounding_urgency)

        # Optional HTTP integration for external oneiric services
        if self.http_client:
            try:
                self._send_http_feedback(scene, policy, hints)
            except Exception as e:
                logger.warning(f"HTTP feedback failed: {e}")
                self.http_failures += 1

        logger.debug(f"Applied policy to scene: {len(hints)} hints generated")
        return hints

    def _compute_tempo_hint(self, scene: PhenomenalScene, policy: RegulationPolicy) -> float:
        """Compute tempo adjustment hint from regulation policy"""
        if not self.config["enable_tempo_modulation"]:
            return 1.0

        base_tempo = policy.pace

        # Apply smoothing to prevent jarring tempo changes
        smoothing = self.config["tempo_smoothing_factor"]

        # Adjust based on scene urgency
        urgency_factor = 1.0
        if scene.proto.temporal_feel.value == "urgent":
            urgency_factor = 1.2
        elif scene.proto.temporal_feel.value == "suspended":
            urgency_factor = 0.7

        adjusted_tempo = base_tempo * urgency_factor

        # Apply smoothing (exponential moving average)
        # In practice, you'd store previous tempo and smooth
        smoothed_tempo = adjusted_tempo  # Simplified for demo

        return max(0.1, min(2.0, smoothed_tempo))

    def _compute_palette_hint(self, scene: PhenomenalScene, policy: RegulationPolicy) -> Optional[str]:
        """Compute palette hint for visual/colorfield guidance"""
        if not self.config["enable_palette_hints"]:
            return None

        # Use policy color_contrast if specified
        if policy.color_contrast:
            return policy.color_contrast

        # Generate safe palette recommendation if current colorfield is problematic
        current_colorfield = scene.proto.colorfield
        if current_colorfield:
            # Check if current colorfield has high threat bias
            from candidate.aka_qualia.palette import map_colorfield

            bias = map_colorfield(current_colorfield, self.config["palette_culture_profile"])

            # If threat bias is high, recommend safer alternative
            if bias.threat_bias > 0.6:
                safe_palette = get_safe_palette_recommendation(
                    current_colorfield, self.config["palette_culture_profile"]
                )
                logger.debug(f"Recommending safe palette {safe_palette} (current threat_bias: {bias.threat_bias})")
                return safe_palette

        # Default to calming blue for grounding
        return "aoi/blue"

    def _compute_operation_hints(self, scene: PhenomenalScene, policy: RegulationPolicy) -> List[str]:
        """Compute regulation operation hints"""
        if not self.config["enable_action_suggestions"]:
            return []

        ops = policy.actions.copy()

        # Add context-sensitive operations based on scene state
        if scene.proto.arousal > 0.7 and scene.proto.tone < -0.3:
            # High arousal + negative tone: suggest breathing
            if "breathing" not in ops:
                ops.append("breathing")

        if scene.proto.clarity < 0.4:
            # Low clarity: suggest focus-shift
            if "focus-shift" not in ops:
                ops.append("focus-shift")

        if scene.risk.severity.value in {"moderate", "high"}:
            # Risk present: suggest pause and reframe
            if "pause" not in ops:
                ops.append("pause")
            if "reframe" not in ops:
                ops.append("reframe")

        # Sublimation for creative transformation of difficult emotions
        if scene.proto.tone < -0.2 and scene.proto.arousal > 0.5 and scene.proto.narrative_gravity > 0.6:
            if "sublimate" not in ops:
                ops.append("sublimate")

        return ops

    def _compute_grounding_urgency(self, scene: PhenomenalScene) -> float:
        """Compute urgency of grounding intervention needed"""
        # Higher urgency for: low embodiment, low clarity, high risk
        embodiment_factor = 1.0 - scene.proto.embodiment
        clarity_factor = 1.0 - scene.proto.clarity
        risk_factor = scene.risk.score

        # Weighted combination
        urgency = embodiment_factor * 0.4 + clarity_factor * 0.3 + risk_factor * 0.3

        return min(1.0, max(0.0, urgency))

    def _generate_symbolic_anchors(
        self, scene: PhenomenalScene, policy: RegulationPolicy, urgency: float
    ) -> Dict[str, Any]:
        """Generate symbolic anchors for grounding when urgency is high"""
        anchors = {}

        # Embodiment anchor - physical grounding
        if scene.proto.embodiment < 0.4:
            anchors["embodiment"] = {
                "type": "physical_grounding",
                "intensity": urgency,
                "suggestion": "breathing",
                "colorfield": "midori/green",  # Green for grounding
            }

        # Clarity anchor - cognitive grounding
        if scene.proto.clarity < 0.4:
            anchors["clarity"] = {
                "type": "cognitive_grounding",
                "intensity": urgency,
                "suggestion": "focus-shift",
                "colorfield": "aoi/blue",  # Blue for clarity
            }

        # Safety anchor - emotional grounding
        if scene.risk.score > 0.6:
            anchors["safety"] = {
                "type": "emotional_grounding",
                "intensity": urgency,
                "suggestion": "pause",
                "colorfield": "shiro/white",  # White for safety
            }

        return anchors

    def _send_http_feedback(self, scene: PhenomenalScene, policy: RegulationPolicy, hints: Dict[str, Any]) -> None:
        """Send feedback to external oneiric service via HTTP"""
        if not self.http_client:
            return

        payload = {
            "scene_id": getattr(scene, "id", None) or f"scene_{scene.proto.narrative_gravity:.3f}",
            "policy": policy.model_dump(),
            "hints": hints,
            "timestamp": scene.timestamp,
        }

        self.http_client.send_feedback(payload)
        self.http_requests_sent += 1

    def get_statistics(self) -> Dict[str, Any]:
        """Get oneiric hook statistics"""
        return {
            "policies_applied": self.policies_applied,
            "http_requests_sent": self.http_requests_sent,
            "http_failures": self.http_failures,
            "http_success_rate": (1.0 - self.http_failures / max(1, self.http_requests_sent)),
        }


class OneiricHTTPClient:
    """
    HTTP client for external oneiric/dream services.

    Optional component for integrating with external LUKHAS oneiric systems
    or dream generation services via HTTP API.
    """

    def __init__(self, base_url: str, timeout: float = 5.0):
        """
        Initialize HTTP client.

        Args:
            base_url: Base URL for oneiric service (e.g., "http://localhost:8081")
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

        # Statistics
        self.requests_sent = 0
        self.requests_failed = 0

    def send_feedback(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send feedback payload to oneiric service.

        Args:
            payload: Feedback data to send

        Returns:
            Response data from service

        Raises:
            requests.RequestException: On HTTP errors
        """
        url = urljoin(self.base_url, "/api/v1/oneiric/feedback")

        try:
            response = self.session.post(
                url, json=payload, timeout=self.timeout, headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()

            self.requests_sent += 1
            return response.json()

        except requests.RequestException as e:
            self.requests_failed += 1
            logger.error(f"Oneiric HTTP request failed: {e}")
            raise

    def get_status(self) -> Dict[str, Any]:
        """Get oneiric service status"""
        url = urljoin(self.base_url, "/api/v1/oneiric/status")

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Oneiric status request failed: {e}")
            raise

    def get_statistics(self) -> Dict[str, Any]:
        """Get HTTP client statistics"""
        return {
            "requests_sent": self.requests_sent,
            "requests_failed": self.requests_failed,
            "success_rate": (1.0 - self.requests_failed / max(1, self.requests_sent)),
        }


def create_oneiric_hook(
    mode: str = "local", base_url: Optional[str] = None, config: Optional[Dict[str, Any]] = None
) -> OneiricHook:
    """
    Factory function to create OneiricHook with appropriate configuration.

    Args:
        mode: "local" for local processing, "http" for external service
        base_url: Base URL for HTTP mode (required if mode="http")
        config: Configuration overrides

    Returns:
        OneiricHook: Configured hook instance
    """
    if mode == "http":
        if not base_url:
            raise ValueError("base_url required for HTTP mode")
        http_client = OneiricHTTPClient(base_url)
        return OneiricHook(http_client=http_client, config=config)
    elif mode == "local":
        return OneiricHook(config=config)
    else:
        raise ValueError(f"Unknown mode: {mode}. Use 'local' or 'http'")
