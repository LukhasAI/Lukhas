import logging

logger = logging.getLogger(__name__)
"""

#TAG:consciousness
#TAG:awareness
#TAG:neuroplastic
#TAG:colony


LUKHAS Attention Monitor - Eye-tracking and Input Lag Processor

This module implements attention monitoring for cognitive load assessment
and user engagement tracking in LUKHAS authentication.

Author: LUKHAS Team
Date: June 2025
Purpose: Monitor user attention patterns for adaptive UI and security
"""

import statistics
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

from candidate.core.common import get_logger

logger = get_logger(__name__)


class AttentionState(Enum):
    """User attention state"""

    FOCUSED = "focused"  # High attention, engaged
    DISTRACTED = "distracted"  # Low attention, not focused
    SWITCHING = "switching"  # Attention switching between tasks
    OVERLOADED = "overloaded"  # Cognitive overload detected
    UNKNOWN = "unknown"  # Cannot determine state


class InputModality(Enum):
    """Input modality types for attention tracking"""

    MOUSE = "mouse"
    TOUCH = "touch"
    KEYBOARD = "keyboard"
    EYE_GAZE = "eye_gaze"
    HEAD_MOVEMENT = "head_movement"


@dataclass
class AttentionMetrics:
    """Attention measurement metric"""

    focus_score: float  # 0.0-1.0 focus intensity
    distraction_events: int  # Number of attention switches
    reaction_time_ms: float  # Average reaction time
    input_lag_ms: float  # Input processing lag
    cognitive_load: float  # Estimated cognitive load 0.0-1.0
    engagement_duration: float  # Total engagement time in seconds
    confidence: float  # Confidence in measurements 0.0-1.0


@dataclass
class EyeTrackingData:
    """Eye tracking data point"""

    timestamp: float
    x: float
    y: float
    pupil_diameter: float
    fixation_duration: float
    saccade_velocity: float
    blink_rate: float


@dataclass
class InputEvent:
    """Input event for lag analysi"""

    timestamp: float
    event_type: InputModality
    coordinates: tuple[float, float]
    processing_time: float
    response_time: float


class AttentionMonitor:
    """
    Attention monitoring system for LUKHAS authentication.

    Features:
    - Eye tracking analysis (when available)
    - Input lag detection and measurement
    - Cognitive load estimation
    - Attention pattern recognition
    - Distraction event detection
    - Adaptive threshold adjustment
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or self._get_default_config()

        # Attention tracking state
        self.current_state = AttentionState.UNKNOWN
        self.attention_history = []
        self.metrics_buffer = []
        self.baseline_metrics = None

        # Eye tracking data
        self.eye_tracking_enabled = False
        self.eye_data_buffer = []
        self.fixation_points = []

        # Input lag monitoring
        self.input_events = []
        self.lag_measurements = []
        self.baseline_lag = None

        # Pattern recognition
        self.attention_patterns = {}
        self.distraction_triggers = []

        # Adaptive thresholds
        self.thresholds = {
            "high_focus": 0.8,
            "low_focus": 0.3,
            "max_reaction_time": 2000,  # ms
            "high_cognitive_load": 0.7,
            "distraction_threshold": 3,  # events per minute
        }

    def _get_default_config(self) -> dict[str, Any]:
        """Get default configuration for attention monitoring."""
        return {
            "eye_tracking_enabled": False,
            "input_lag_tracking": True,
            "cognitive_load_estimation": True,
            "pattern_recognition": True,
            "adaptive_thresholds": True,
            "baseline_calibration": True,
            "data_retention_minutes": 30,
            "measurement_interval_ms": 100,
            "smoothing_window_size": 10,
        }

    async def start_attention_monitoring(self) -> bool:
        """
        Start attention monitoring with available input modalities.

        Returns:
            True if monitoring started successfully
        """
        try:
            logger.info("Starting attention monitoring system")

            # Initialize eye tracking if available
            if self.config.get("eye_tracking_enabled", False):
                self.eye_tracking_enabled = await self._initialize_eye_tracking()

            # Start baseline calibration
            if self.config.get("baseline_calibration", True):
                await self._calibrate_baseline()

            # Start monitoring loops
            # Note: In production, these would be actual monitoring tasks
            logger.info("Attention monitoring started successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to start attention monitoring: {e}")
            return False

    async def _initialize_eye_tracking(self) -> bool:
        """
        Initialize eye tracking system if available.

        Returns:
            True if eye tracking is available and initialized
        """
        # In production, this would initialize actual eye tracking hardware/software
        # For now, we simulate eye tracking availability
        try:
            # Check for eye tracking capability (webcam, specialized hardware, etc.)
            eye_tracking_available = False  # Would be actual detection

            if eye_tracking_available:
                logger.info("Eye tracking initialized")
                return True
            else:
                logger.info("Eye tracking not available, using fallback methods")
                return False

        except Exception as e:
            logger.error(f"Eye tracking initialization failed: {e}")
            return False

    async def _calibrate_baseline(self):
        """Calibrate baseline attention metrics for this user/session."""
        logger.info("Calibrating baseline attention metrics")

        # In production, this would collect baseline measurements
        # For now, we use reasonable defaults
        self.baseline_metrics = AttentionMetrics(
            focus_score=0.6,
            distraction_events=2,
            reaction_time_ms=800,
            input_lag_ms=50,
            cognitive_load=0.4,
            engagement_duration=0,
            confidence=0.8,
        )

        self.baseline_lag = 50.0  # ms
        logger.info("Baseline calibration completed")

    def process_eye_tracking_data(self, eye_data: EyeTrackingData) -> dict[str, Any]:
        """
        Process eye tracking data to extract attention metrics.

        Args:
            eye_data: Eye tracking data point

        Returns:
            Processed attention metrics from eye movement
        """
        if not self.eye_tracking_enabled:
            return {"error": "eye_tracking_not_enabled"}

        # Add to buffer
        self.eye_data_buffer.append(eye_data)

        # Limit buffer size
        if len(self.eye_data_buffer) > 1000:
            self.eye_data_buffer = self.eye_data_buffer[-500:]

        # Analyze recent eye movement patterns
        analysis = self._analyze_eye_movement_patterns()

        # Update attention state based on eye tracking
        attention_metrics = self._calculate_attention_from_eye_data(analysis)

        return {
            "eye_analysis": analysis,
            "attention_metrics": attention_metrics,
            "timestamp": eye_data.timestamp,
        }

    def _analyze_eye_movement_patterns(self) -> dict[str, Any]:
        """
        Analyze eye movement patterns to detect attention state.

        Returns:
            Eye movement analysis results
        """
        if len(self.eye_data_buffer) < 10:
            return {"status": "insufficient_data"}

        recent_data = self.eye_data_buffer[-20:]  # Last 20 data points

        # Calculate fixation stability
        fixation_variance = statistics.variance([d.x for d in recent_data]) + statistics.variance(
            [d.y for d in recent_data]
        )

        # Calculate average pupil diameter (attention indicator)
        avg_pupil_diameter = statistics.mean([d.pupil_diameter for d in recent_data])

        # Calculate blink rate (stress/fatigue indicator)
        avg_blink_rate = statistics.mean([d.blink_rate for d in recent_data])

        # Calculate saccade frequency (scanning vs focused attention)
        high_velocity_saccades = len([d for d in recent_data if d.saccade_velocity > 300])

        return {
            "fixation_stability": 1.0 / (1.0 + fixation_variance),  # Higher = more stable
            "pupil_diameter": avg_pupil_diameter,
            "blink_rate": avg_blink_rate,
            "saccade_frequency": high_velocity_saccades / len(recent_data),
            "attention_indicators": {
                "focused": fixation_variance < 100 and avg_pupil_diameter > 4.0,
                "distracted": high_velocity_saccades > len(recent_data) * 0.3,
                "fatigued": avg_blink_rate > 20,
            },
        }

    def _calculate_attention_from_eye_data(self, eye_analysis: dict[str, Any]) -> AttentionMetrics:
        """
        Calculate attention metrics from eye movement analysis.

        Args:
            eye_analysis: Eye movement analysis results

        Returns:
            Attention metrics derived from eye tracking
        """
        if "fixation_stability" not in eye_analysis:
            return self.baseline_metrics

        # Calculate focus score from eye data
        focus_score = (
            eye_analysis["fixation_stability"] * 0.4
            + min(eye_analysis["pupil_diameter"] / 6.0, 1.0) * 0.3
            + max(0, 1.0 - eye_analysis["saccade_frequency"]) * 0.3
        )

        # Detect distraction events
        distraction_events = 1 if eye_analysis["attention_indicators"]["distracted"] else 0

        # Estimate cognitive load
        cognitive_load = (
            (1.0 - focus_score) * 0.5
            + min(eye_analysis["blink_rate"] / 30.0, 1.0) * 0.3
            + eye_analysis["saccade_frequency"] * 0.2
        )

        return AttentionMetrics(
            focus_score=focus_score,
            distraction_events=distraction_events,
            reaction_time_ms=self.baseline_metrics.reaction_time_ms,
            input_lag_ms=self.baseline_metrics.input_lag_ms,
            cognitive_load=cognitive_load,
            engagement_duration=time.time(),
            confidence=0.9 if self.eye_tracking_enabled else 0.5,
        )

    def process_input_event(self, input_event: InputEvent) -> dict[str, Any]:
        """
        Process input event to measure lag and extract attention indicators.

        Args:
            input_event: Input event data

        Returns:
            Input processing analysis and attention indicators
        """
        # Add to input events buffer
        self.input_events.append(input_event)

        # Limit buffer size
        if len(self.input_events) > 500:
            self.input_events = self.input_events[-250:]

        # Calculate input lag
        lag_analysis = self._analyze_input_lag(input_event)

        # Extract attention indicators from input patterns
        attention_indicators = self._extract_attention_from_input_patterns()

        # Update lag measurements
        self.lag_measurements.append(input_event.processing_time)
        if len(self.lag_measurements) > 100:
            self.lag_measurements = self.lag_measurements[-50:]

        return {
            "lag_analysis": lag_analysis,
            "attention_indicators": attention_indicators,
            "timestamp": input_event.timestamp,
        }

    def _analyze_input_lag(self, input_event: InputEvent) -> dict[str, Any]:
        """
        Analyze input lag to detect performance issues and cognitive load.

        Args:
            input_event: Input event to analyze

        Returns:
            Input lag analysis results
        """
        processing_lag = input_event.processing_time
        response_lag = input_event.response_time

        # Compare to baseline
        baseline = self.baseline_lag or 50.0
        lag_ratio = processing_lag / baseline

        # Categorize lag level
        if lag_ratio < 1.2:
            lag_level = "normal"
        elif lag_ratio < 2.0:
            lag_level = "elevated"
        else:
            lag_level = "high"

        # Detect lag patterns
        recent_lags = self.lag_measurements[-10:] if self.lag_measurements else []
        trending_up = len(recent_lags) > 5 and all(
            recent_lags[i] <= recent_lags[i + 1] for i in range(len(recent_lags) - 1)
        )

        return {
            "processing_lag_ms": processing_lag,
            "response_lag_ms": response_lag,
            "lag_ratio": lag_ratio,
            "lag_level": lag_level,
            "trending_up": trending_up,
            "baseline_comparison": {
                "vs_baseline": lag_ratio,
                "performance_impact": lag_ratio > 1.5,
            },
        }

    def _extract_attention_from_input_patterns(self) -> dict[str, Any]:
        """
        Extract attention indicators from input timing and patterns.

        Returns:
            Attention indicators from input analysis
        """
        if len(self.input_events) < 5:
            return {"status": "insufficient_data"}

        recent_events = self.input_events[-20:]

        # Calculate input timing variability (attention indicator)
        intervals = []
        for i in range(1, len(recent_events)):
            interval = recent_events[i].timestamp - recent_events[i - 1].timestamp
            intervals.append(interval)

        if not intervals:
            return {"status": "no_intervals"}

        timing_variance = statistics.variance(intervals) if len(intervals) > 1 else 0
        avg_interval = statistics.mean(intervals)

        # Calculate input accuracy (spatial consistency)
        coordinates = [event.coordinates for event in recent_events]
        if len(coordinates) > 1:
            x_variance = statistics.variance([c[0] for c in coordinates])
            y_variance = statistics.variance([c[1] for c in coordinates])
            spatial_consistency = 1.0 / (1.0 + x_variance + y_variance)
        else:
            spatial_consistency = 1.0

        # Detect erratic input patterns
        erratic_pattern = timing_variance > avg_interval * 0.5

        return {
            "timing_variance": timing_variance,
            "spatial_consistency": spatial_consistency,
            "avg_input_interval": avg_interval,
            "erratic_pattern": erratic_pattern,
            "attention_indicators": {
                "consistent_timing": timing_variance < avg_interval * 0.2,
                "steady_input": spatial_consistency > 0.7,
                "rushed_input": avg_interval < 200,  # Very fast input
                "hesitant_input": avg_interval > 2000,  # Very slow input
            },
        }

    def get_current_attention_state(self) -> tuple[AttentionState, AttentionMetrics]:
        """
        Get current attention state and metrics.

        Returns:
            Tuple of (attention_state, attention_metrics)
        """
        # Combine all available indicators
        if self.metrics_buffer:
            latest_metrics = self.metrics_buffer[-1]
        else:
            latest_metrics = self.baseline_metrics or AttentionMetrics(
                focus_score=0.5,
                distraction_events=0,
                reaction_time_ms=800,
                input_lag_ms=50,
                cognitive_load=0.5,
                engagement_duration=0,
                confidence=0.5,
            )

        # Determine attention state from metrics
        if latest_metrics.focus_score > self.thresholds["high_focus"]:
            state = AttentionState.FOCUSED if latest_metrics.cognitive_load < 0.5 else AttentionState.OVERLOADED
        elif latest_metrics.focus_score < self.thresholds["low_focus"]:
            state = AttentionState.DISTRACTED
        elif latest_metrics.distraction_events > self.thresholds["distraction_threshold"]:
            state = AttentionState.SWITCHING
        else:
            state = AttentionState.UNKNOWN

        self.current_state = state
        return state, latest_metrics

    def update_attention_metrics(
        self,
        eye_data: Optional[EyeTrackingData] = None,
        input_event: Optional[InputEvent] = None,
    ) -> AttentionMetrics:
        """
        Update attention metrics with new data.

        Args:
            eye_data: Optional eye tracking data
            input_event: Optional input event data

        Returns:
            Updated attention metrics
        """
        time.time()

        # Process available data
        eye_metrics = None
        if eye_data and self.eye_tracking_enabled:
            eye_result = self.process_eye_tracking_data(eye_data)
            eye_metrics = eye_result.get("attention_metrics")

        input_metrics = None
        if input_event:
            input_result = self.process_input_event(input_event)
            # Extract attention metrics from input analysis
            input_result.get("attention_indicators", {})

        # Combine metrics from all sources
        combined_metrics = self._combine_attention_metrics(eye_metrics, input_metrics)

        # Add to metrics buffer
        self.metrics_buffer.append(combined_metrics)
        if len(self.metrics_buffer) > 100:
            self.metrics_buffer = self.metrics_buffer[-50:]

        return combined_metrics

    def _combine_attention_metrics(
        self, eye_metrics: Optional[AttentionMetrics], input_metrics: Optional[dict]
    ) -> AttentionMetrics:
        """
        Combine attention metrics from multiple sources.

        Args:
            eye_metrics: Metrics from eye tracking
            input_metrics: Metrics from input analysis

        Returns:
            Combined attention metrics
        """
        baseline = self.baseline_metrics or AttentionMetrics(
            focus_score=0.5,
            distraction_events=0,
            reaction_time_ms=800,
            input_lag_ms=50,
            cognitive_load=0.5,
            engagement_duration=0,
            confidence=0.5,
        )

        # Start with baseline
        combined = AttentionMetrics(
            focus_score=baseline.focus_score,
            distraction_events=0,
            reaction_time_ms=baseline.reaction_time_ms,
            input_lag_ms=baseline.input_lag_ms,
            cognitive_load=baseline.cognitive_load,
            engagement_duration=time.time(),
            confidence=0.5,
        )

        # Incorporate eye tracking metrics if available
        if eye_metrics:
            combined.focus_score = eye_metrics.focus_score
            combined.distraction_events = eye_metrics.distraction_events
            combined.cognitive_load = eye_metrics.cognitive_load
            combined.confidence = max(combined.confidence, 0.9)

        # Incorporate input metrics if available
        if input_metrics:
            # Adjust focus score based on input consistency
            input_indicators = input_metrics.get("attention_indicators", {})
            if input_indicators.get("consistent_timing") and input_indicators.get("steady_input"):
                combined.focus_score = min(1.0, combined.focus_score + 0.1)
            elif input_indicators.get("erratic_pattern"):
                combined.focus_score = max(0.0, combined.focus_score - 0.2)
                combined.distraction_events += 1

        return combined

    def get_attention_status(self) -> dict[str, Any]:
        """Get comprehensive attention monitoring status."""
        state, metrics = self.get_current_attention_state()

        return {
            "current_state": state.value,
            "metrics": {
                "focus_score": metrics.focus_score,
                "distraction_events": metrics.distraction_events,
                "reaction_time_ms": metrics.reaction_time_ms,
                "input_lag_ms": metrics.input_lag_ms,
                "cognitive_load": metrics.cognitive_load,
                "confidence": metrics.confidence,
            },
            "capabilities": {
                "eye_tracking_enabled": self.eye_tracking_enabled,
                "input_lag_tracking": self.config.get("input_lag_tracking", True),
                "pattern_recognition": self.config.get("pattern_recognition", True),
            },
            "data_points": {
                "eye_data_buffer_size": len(self.eye_data_buffer),
                "input_events_count": len(self.input_events),
                "metrics_history_size": len(self.metrics_buffer),
            },
            "thresholds": self.thresholds.copy(),
        }


# Export the main classes
__all__ = [
    "AttentionMetrics",
    "AttentionMonitor",
    "AttentionState",
    "EyeTrackingData",
    "InputEvent",
    "InputModality",
]