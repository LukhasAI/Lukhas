"""
LUKHAS Adaptive UI Controller - Claude-Gemini Bridge

This module implements the adaptive UI controller that bridges Claude's constitutional
enforcement with Gemini's dynamic UI elements. It manages grid sizing, timeout adaptation,
and real-time cognitive load assessment while maintaining constitutional compliance.

Author: LUKHAS Team
Date: June 2025
Constitutional AI Guidelines: Enforced
Integration: Claude's constitutional oversight with Gemini's adaptive rendering
"""

import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any

# Import constitutional enforcement and other core modules
from .constitutional_gatekeeper import (
    ConstitutionalLevel,
    get_constitutional_gatekeeper,
)

# Configure adaptive UI logging
logging.basicConfig(level=logging.INFO)
ui_logger = logging.getLogger("LUKHAS_ADAPTIVE_UI")


class UIAdaptationMode(Enum):
    """UI adaptation modes based on user state"""

    OPTIMAL = "optimal"  # Standard responsive UI
    ACCESSIBLE = "accessible"  # Enhanced accessibility features
    SIMPLIFIED = "simplified"  # Reduced complexity for cognitive load
    EMERGENCY = "emergency"  # Crisis mode with minimal UI


@dataclass
class CognitiveLoadMetrics:
    """Metrics for assessing user cognitive load"""

    attention_score: float  # 0.0 to 1.0 (higher = more focused)
    processing_speed: float  # Response time in seconds
    error_rate: float  # Percentage of errors (0.0 to 1.0)
    stress_indicators: float  # Physiological stress level (0.0 to 1.0)
    fatigue_level: float  # Mental fatigue assessment (0.0 to 1.0)
    timestamp: datetime


@dataclass
class UIConfiguration:
    """Current UI configuration parameters"""

    grid_size: int  # Number of emoji elements
    timeout_seconds: int  # Authentication timeout
    animation_speed: float  # UI animation speed (0.0 to 1.0)
    contrast_level: float  # Visual contrast adjustment (0.0 to 1.0)
    font_size_multiplier: float  # Font size scaling factor
    simplified_layout: bool  # Whether to use simplified layout
    audio_feedback: bool  # Enable audio feedback
    haptic_feedback: bool  # Enable haptic feedback


class AdaptiveUIController:
    """
    Adaptive UI controller that bridges constitutional enforcement with dynamic rendering.

    This class monitors user cognitive state and adapts the UI accordingly while
    ensuring all changes comply with constitutional constraints.
    """

    def __init__(
        self,
        session_id: str,
        enforcement_level: ConstitutionalLevel = ConstitutionalLevel.STANDARD,
    ):
        self.session_id = session_id
        self.constitutional_gatekeeper = get_constitutional_gatekeeper(
            enforcement_level
        )
        self.current_config = self._get_default_config()
        self.cognitive_history: list[CognitiveLoadMetrics] = []
        self.adaptation_callbacks: list = []
        self.monitoring_active = False

        ui_logger.info(f"Adaptive UI Controller initialized for session {session_id}")

    def _get_default_config(self) -> UIConfiguration:
        """Get default UI configuration that complies with constitutional limits"""
        return UIConfiguration(
            grid_size=9,  # 3x3 grid (within working memory limits)
            timeout_seconds=15,  # Reasonable timeout
            animation_speed=0.5,  # Moderate animation speed
            contrast_level=0.7,  # Good contrast for accessibility
            font_size_multiplier=1.0,  # Standard font size
            simplified_layout=False,  # Standard layout initially
            audio_feedback=False,  # Disabled by default (accessibility)
            haptic_feedback=True,  # Enabled for mobile devices
        )

    def assess_cognitive_load(
        self, user_metrics: dict[str, Any]
    ) -> CognitiveLoadMetrics:
        """
        Assess user cognitive load from various input metrics.

        Args:
            user_metrics: Dictionary containing user interaction metrics

        Returns:
            CognitiveLoadMetrics object with assessed load
        """
        # Extract metrics with defaults
        response_time = user_metrics.get("response_time", 5.0)
        click_accuracy = user_metrics.get("click_accuracy", 1.0)
        mouse_hesitation = user_metrics.get("mouse_hesitation", 0.0)
        heart_rate_var = user_metrics.get("heart_rate_variability", 0.5)
        blink_rate = user_metrics.get("blink_rate", 15.0)  # blinks per minute

        # Calculate attention score (inverse of hesitation and response time)
        attention_score = max(
            0.0, min(1.0, 1.0 - (mouse_hesitation * 0.5) - (response_time / 30.0))
        )

        # Calculate processing speed (inverse of response time)
        processing_speed = max(0.1, min(10.0, 1.0 / response_time))

        # Calculate error rate (inverse of accuracy)
        error_rate = max(0.0, min(1.0, 1.0 - click_accuracy))

        # Calculate stress indicators from physiological data
        # Normal HRV is around 0.5, normal blink rate is 15-20/min
        stress_indicators = max(
            0.0,
            min(1.0, abs(heart_rate_var - 0.5) * 2.0 + abs(blink_rate - 17.5) / 17.5),
        )

        # Calculate fatigue based on declining performance over time
        fatigue_level = self._calculate_fatigue_level()

        metrics = CognitiveLoadMetrics(
            attention_score=attention_score,
            processing_speed=processing_speed,
            error_rate=error_rate,
            stress_indicators=stress_indicators,
            fatigue_level=fatigue_level,
            timestamp=datetime.now(),
        )

        # Add to history
        self.cognitive_history.append(metrics)

        # Limit history size
        if len(self.cognitive_history) > 50:
            self.cognitive_history = self.cognitive_history[-40:]

        ui_logger.info(
            f"Cognitive load assessed: attention={attention_score:.2f}, stress={stress_indicators:.2f}"
        )

        return metrics

    def _calculate_fatigue_level(self) -> float:
        """Calculate fatigue level based on performance degradation over time"""
        if len(self.cognitive_history) < 3:
            return 0.0

        # Look at attention and processing speed trends
        recent_attention = [m.attention_score for m in self.cognitive_history[-5:]]
        earlier_attention = (
            [m.attention_score for m in self.cognitive_history[-10:-5]]
            if len(self.cognitive_history) >= 10
            else recent_attention
        )

        # Calculate trend (negative means declining performance)
        recent_avg = sum(recent_attention) / len(recent_attention)
        earlier_avg = sum(earlier_attention) / len(earlier_attention)

        performance_decline = max(0.0, earlier_avg - recent_avg)

        # Session duration factor
        session_duration = (
            datetime.now() - self.cognitive_history[0].timestamp
        ).total_seconds() / 3600.0  # hours
        # Fatigue increases over 2 hours
        duration_fatigue = min(1.0, session_duration / 2.0)

        return min(1.0, performance_decline * 2.0 + duration_fatigue * 0.3)

    def adapt_ui_to_cognitive_state(
        self, cognitive_metrics: CognitiveLoadMetrics
    ) -> UIConfiguration:
        """
        Adapt UI configuration based on cognitive load assessment.

        Args:
            cognitive_metrics: Current cognitive load metrics

        Returns:
            New UI configuration adapted to user state
        """
        new_config = UIConfiguration(**asdict(self.current_config))
        adaptation_reasons = []

        # Calculate overall cognitive load
        cognitive_load = (
            (1.0 - cognitive_metrics.attention_score) * 0.3
            + cognitive_metrics.error_rate * 0.3
            + cognitive_metrics.stress_indicators * 0.2
            + cognitive_metrics.fatigue_level * 0.2
        )

        # Adapt grid size based on cognitive load
        if cognitive_load > 0.7:
            # High cognitive load - simplify
            new_config.grid_size = max(4, min(new_config.grid_size - 2, 6))
            new_config.simplified_layout = True
            adaptation_reasons.append("High cognitive load detected - simplified UI")
        elif cognitive_load < 0.3 and cognitive_metrics.attention_score > 0.8:
            # Low cognitive load, high attention - can handle complexity
            new_config.grid_size = min(16, new_config.grid_size + 1)
            new_config.simplified_layout = False
            adaptation_reasons.append("Low cognitive load - enhanced UI complexity")

        # Adapt timeout based on processing speed and fatigue
        processing_factor = min(2.0, 1.0 / cognitive_metrics.processing_speed)
        fatigue_factor = 1.0 + cognitive_metrics.fatigue_level * 0.5

        new_timeout = int(15 * processing_factor * fatigue_factor)
        new_config.timeout_seconds = max(10, min(45, new_timeout))

        if new_config.timeout_seconds != self.current_config.timeout_seconds:
            adaptation_reasons.append(
                f"Timeout adapted to {new_config.timeout_seconds}s for processing speed"
            )

        # Adapt visual elements based on stress and attention
        if cognitive_metrics.stress_indicators > 0.6:
            new_config.animation_speed = max(0.1, new_config.animation_speed - 0.2)
            new_config.contrast_level = min(1.0, new_config.contrast_level + 0.1)
            adaptation_reasons.append(
                "Stress detected - reduced animations, increased contrast"
            )

        if cognitive_metrics.attention_score < 0.4:
            new_config.font_size_multiplier = min(
                1.5, new_config.font_size_multiplier + 0.1
            )
            adaptation_reasons.append("Low attention - increased font size")

        # Constitutional validation of new configuration
        ui_dict = {
            "total_interactive_elements": new_config.grid_size,
            "required_processing_time_seconds": new_config.timeout_seconds,
            "has_moving_elements": new_config.animation_speed > 0.1,
            "popup_notifications": False,
            "time_pressure_indicators": new_config.timeout_seconds < 20,
            "color_scheme": {"high_contrast": new_config.contrast_level > 0.8},
            "audio": {"notification_sounds": new_config.audio_feedback},
        }

        is_accessible, accessibility_issues = (
            self.constitutional_gatekeeper.validate_neurodivergent_accessibility(
                ui_dict
            )
        )

        if not is_accessible:
            # Apply constitutional corrections
            for issue in accessibility_issues:
                if "Too many interactive elements" in issue:
                    new_config.grid_size = min(5, new_config.grid_size)
                elif "Moving elements" in issue:
                    new_config.animation_speed = 0.0
                elif "Time pressure" in issue:
                    new_config.timeout_seconds = max(20, new_config.timeout_seconds)

            adaptation_reasons.append(
                "Constitutional accessibility corrections applied"
            )

        # Validate final configuration
        is_valid, violations = self.constitutional_gatekeeper.validate_ui_parameters(
            new_config.grid_size, new_config.timeout_seconds, cognitive_load
        )

        if is_valid:
            self.current_config = new_config
            ui_logger.info(f"UI adapted: {', '.join(adaptation_reasons)}")

            # Notify callbacks
            for callback in self.adaptation_callbacks:
                try:
                    callback(new_config, adaptation_reasons)
                except Exception as e:
                    ui_logger.error(f"Error in adaptation callback: {e}")
        else:
            ui_logger.warning(
                f"UI adaptation blocked by constitutional violations: {violations}"
            )

        return self.current_config

    def get_adaptation_mode(
        self, cognitive_metrics: CognitiveLoadMetrics
    ) -> UIAdaptationMode:
        """
        Determine the appropriate UI adaptation mode.

        Args:
            cognitive_metrics: Current cognitive load metrics

        Returns:
            Recommended UI adaptation mode
        """
        cognitive_load = (
            (1.0 - cognitive_metrics.attention_score) * 0.3
            + cognitive_metrics.error_rate * 0.3
            + cognitive_metrics.stress_indicators * 0.2
            + cognitive_metrics.fatigue_level * 0.2
        )

        if cognitive_load > 0.8 or cognitive_metrics.stress_indicators > 0.7:
            return UIAdaptationMode.EMERGENCY
        elif cognitive_load > 0.6 or cognitive_metrics.fatigue_level > 0.6:
            return UIAdaptationMode.SIMPLIFIED
        elif (
            cognitive_metrics.error_rate > 0.3
            or cognitive_metrics.attention_score < 0.4
        ):
            return UIAdaptationMode.ACCESSIBLE
        else:
            return UIAdaptationMode.OPTIMAL

    def add_adaptation_callback(self, callback):
        """Add callback function for UI adaptation events"""
        self.adaptation_callbacks.append(callback)

    def get_ui_state_summary(self) -> dict[str, Any]:
        """
        Get comprehensive UI state summary.

        Returns:
            Dictionary containing current UI state and metrics
        """
        latest_metrics = self.cognitive_history[-1] if self.cognitive_history else None

        return {
            "session_id": self.session_id,
            "current_config": asdict(self.current_config),
            "adaptation_mode": (
                self.get_adaptation_mode(latest_metrics).value
                if latest_metrics
                else "unknown"
            ),
            "cognitive_metrics": asdict(latest_metrics) if latest_metrics else None,
            "cognitive_history_length": len(self.cognitive_history),
            "constitutional_compliance": True,  # Always true due to enforcement
            "monitoring_active": self.monitoring_active,
        }

    def emergency_ui_reset(self, reason: str = "Emergency UI reset"):
        """
        Emergency reset to safe UI configuration.

        Args:
            reason: Reason for emergency reset
        """
        ui_logger.warning(f"Emergency UI reset triggered: {reason}")

        # Reset to ultra-safe configuration
        self.current_config = UIConfiguration(
            grid_size=4,  # Minimal cognitive load
            timeout_seconds=30,  # Extended timeout
            animation_speed=0.0,  # No animations
            contrast_level=1.0,  # Maximum contrast
            font_size_multiplier=1.2,  # Larger font
            simplified_layout=True,  # Simplified layout
            audio_feedback=False,  # No audio distractions
            haptic_feedback=False,  # No haptic distractions
        )

        # Trigger constitutional emergency
        emergency_report = self.constitutional_gatekeeper.emergency_lockdown(
            f"UI adaptation emergency: {reason}"
        )

        return emergency_report


# Export the main classes and types
__all__ = [
    "AdaptiveUIController",
    "CognitiveLoadMetrics",
    "UIAdaptationMode",
    "UIConfiguration",
]
