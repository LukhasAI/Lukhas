"""
GTΨ Edge Recognition
===================
On-device gesture recognition that preserves privacy.
Extracts hashed kinematic features without storing raw gesture data.

System-wide guardrails applied:
1. Edge-first processing - never transmit raw strokes
2. Store only hashed kinematic features + salt
3. Quality-based gesture validation
4. Multiple gesture type support (stroke, tap, swipe, signature)

ACK GUARDRAILS
"""

import hashlib
import json
import math
from typing import Any

import numpy as np

from .. import GestureRecognizer, GestureType


class StrokeGestureRecognizer(GestureRecognizer):
    """
    On-device stroke gesture recognizer.

    Extracts kinematic features from stroke data:
    - Path length and curvature
    - Velocity and acceleration profiles
    - Pressure variations (if available)
    - Timing characteristics
    """

    def extract_features(self, raw_gesture_data: Any) -> list[float]:
        """
        Extract kinematic features from stroke data.

        Args:
            raw_gesture_data: Dictionary with 'points' array containing:
                             [{x, y, timestamp, pressure?}, ...]

        Returns:
            List of numerical features for hashing
        """
        if not isinstance(raw_gesture_data, dict) or "points" not in raw_gesture_data:
            raise ValueError("Invalid stroke data format")

        points = raw_gesture_data["points"]
        if len(points) < 2:
            raise ValueError("Stroke must have at least 2 points")

        features = []

        # 1. Path geometry features
        path_features = self._extract_path_features(points)
        features.extend(path_features)

        # 2. Velocity/acceleration features
        motion_features = self._extract_motion_features(points)
        features.extend(motion_features)

        # 3. Pressure features (if available)
        if "pressure" in points[0]:
            pressure_features = self._extract_pressure_features(points)
            features.extend(pressure_features)

        # 4. Timing features
        timing_features = self._extract_timing_features(points)
        features.extend(timing_features)

        # 5. Normalize features to [0, 1] range
        normalized_features = self._normalize_features(features)

        return normalized_features

    def _extract_path_features(self, points: list[dict]) -> list[float]:
        """Extract path geometry features"""
        features = []

        # Total path length
        total_length = 0.0
        for i in range(1, len(points)):
            dx = points[i]["x"] - points[i - 1]["x"]
            dy = points[i]["y"] - points[i - 1]["y"]
            total_length += math.sqrt(dx * dx + dy * dy)

        features.append(total_length)

        # Bounding box features
        x_coords = [p["x"] for p in points]
        y_coords = [p["y"] for p in points]

        bbox_width = max(x_coords) - min(x_coords)
        bbox_height = max(y_coords) - min(y_coords)
        bbox_aspect_ratio = bbox_width / bbox_height if bbox_height > 0 else 1.0

        features.extend([bbox_width, bbox_height, bbox_aspect_ratio])

        # Curvature features (simplified)
        if len(points) >= 3:
            curvatures = []
            for i in range(1, len(points) - 1):
                # Calculate angle change at point i
                v1x = points[i]["x"] - points[i - 1]["x"]
                v1y = points[i]["y"] - points[i - 1]["y"]
                v2x = points[i + 1]["x"] - points[i]["x"]
                v2y = points[i + 1]["y"] - points[i]["y"]

                # Cross product for angle
                cross = v1x * v2y - v1y * v2x
                dot = v1x * v2x + v1y * v2y

                angle = math.atan2(abs(cross), dot) if dot != 0 else 0
                curvatures.append(angle)

            if curvatures:
                features.extend([np.mean(curvatures), np.std(curvatures), max(curvatures)])
            else:
                features.extend([0.0, 0.0, 0.0])
        else:
            features.extend([0.0, 0.0, 0.0])

        return features

    def _extract_motion_features(self, points: list[dict]) -> list[float]:
        """Extract velocity and acceleration features"""
        features = []

        if len(points) < 2:
            return [0.0] * 6  # Return zeros for insufficient data

        velocities = []

        # Calculate velocities
        for i in range(1, len(points)):
            dx = points[i]["x"] - points[i - 1]["x"]
            dy = points[i]["y"] - points[i - 1]["y"]
            dt = points[i]["timestamp"] - points[i - 1]["timestamp"]

            if dt > 0:
                velocity = math.sqrt(dx * dx + dy * dy) / dt
                velocities.append(velocity)

        if velocities:
            features.extend([np.mean(velocities), np.std(velocities), max(velocities)])
        else:
            features.extend([0.0, 0.0, 0.0])

        # Calculate accelerations
        if len(velocities) >= 2:
            accelerations = []
            for i in range(1, len(velocities)):
                dv = velocities[i] - velocities[i - 1]
                dt = points[i + 1]["timestamp"] - points[i]["timestamp"]

                if dt > 0:
                    acceleration = abs(dv) / dt
                    accelerations.append(acceleration)

            if accelerations:
                features.extend([np.mean(accelerations), np.std(accelerations), max(accelerations)])
            else:
                features.extend([0.0, 0.0, 0.0])
        else:
            features.extend([0.0, 0.0, 0.0])

        return features

    def _extract_pressure_features(self, points: list[dict]) -> list[float]:
        """Extract pressure variation features"""
        pressures = [p.get("pressure", 0.5) for p in points]

        return [np.mean(pressures), np.std(pressures), max(pressures), min(pressures)]

    def _extract_timing_features(self, points: list[dict]) -> list[float]:
        """Extract timing characteristics"""
        if len(points) < 2:
            return [0.0, 0.0]

        # Total gesture duration
        total_duration = points[-1]["timestamp"] - points[0]["timestamp"]

        # Average time between points
        time_intervals = []
        for i in range(1, len(points)):
            dt = points[i]["timestamp"] - points[i - 1]["timestamp"]
            time_intervals.append(dt)

        avg_interval = np.mean(time_intervals) if time_intervals else 0.0

        return [total_duration, avg_interval]

    def _normalize_features(self, features: list[float]) -> list[float]:
        """Normalize features to [0, 1] range"""
        if not features:
            return features

        # Simple min-max normalization
        min_val = min(features)
        max_val = max(features)

        if max_val - min_val == 0:
            return [0.5] * len(features)  # All features are the same

        normalized = [(f - min_val) / (max_val - min_val) for f in features]
        return normalized

    def hash_features(self, features: list[float], salt: str) -> str:
        """Hash features with salt for privacy"""
        # Round features to reduce sensitivity to minor variations
        rounded_features = [round(f, 4) for f in features]

        # Create deterministic string representation
        feature_str = json.dumps(rounded_features, sort_keys=True)

        # Hash with salt
        hasher = hashlib.sha256()
        hasher.update(salt.encode())
        hasher.update(feature_str.encode())

        return hasher.hexdigest()

    def calculate_quality_score(self, features: list[float]) -> float:
        """Calculate gesture quality score based on features"""
        if not features or len(features) < 5:
            return 0.0

        quality_factors = []

        # Path length factor (longer strokes generally better)
        if features[0] > 0:
            path_factor = min(1.0, features[0] / 100.0)  # Normalize to reasonable path length
            quality_factors.append(path_factor)

        # Complexity factor (some curvature is good)
        if len(features) > 7:  # Has curvature features
            curvature_std = features[7] if len(features) > 7 else 0
            complexity_factor = min(1.0, curvature_std * 2.0)  # More variation = higher quality
            quality_factors.append(complexity_factor)

        # Consistency factor (not too much variation in velocity)
        if len(features) > 10:  # Has velocity features
            velocity_consistency = 1.0 - min(1.0, features[10])  # Lower std = more consistent
            quality_factors.append(velocity_consistency)

        # Duration factor (not too fast, not too slow)
        if len(features) > -2:  # Has timing features (at the end)
            duration = features[-2]
            if 0.1 <= duration <= 2.0:  # Good duration range
                duration_factor = 1.0
            else:
                duration_factor = max(0.2, 1.0 / (1.0 + abs(duration - 1.0)))
            quality_factors.append(duration_factor)

        # Overall quality is average of factors
        if quality_factors:
            return np.mean(quality_factors)
        else:
            return 0.5  # Neutral quality if no factors available


class TapSequenceRecognizer(GestureRecognizer):
    """Recognizes tap rhythm patterns for GTΨ"""

    def extract_features(self, raw_gesture_data: Any) -> list[float]:
        """Extract timing features from tap sequence"""
        if not isinstance(raw_gesture_data, dict) or "taps" not in raw_gesture_data:
            raise ValueError("Invalid tap sequence data format")

        taps = raw_gesture_data["taps"]  # [{'timestamp': float, 'x': float, 'y': float}, ...]

        if len(taps) < 2:
            return [0.0] * 8

        features = []

        # Inter-tap intervals
        intervals = []
        for i in range(1, len(taps)):
            interval = taps[i]["timestamp"] - taps[i - 1]["timestamp"]
            intervals.append(interval)

        # Timing statistics
        features.extend(
            [
                len(taps),  # Number of taps
                np.mean(intervals),  # Average interval
                np.std(intervals),  # Interval variation
                max(intervals),  # Longest interval
                min(intervals),  # Shortest interval
            ]
        )

        # Spatial spread
        x_coords = [tap["x"] for tap in taps]
        y_coords = [tap["y"] for tap in taps]

        x_spread = max(x_coords) - min(x_coords) if len(x_coords) > 1 else 0
        y_spread = max(y_coords) - min(y_coords) if len(y_coords) > 1 else 0

        features.extend([x_spread, y_spread])

        # Total sequence duration
        total_duration = taps[-1]["timestamp"] - taps[0]["timestamp"]
        features.append(total_duration)

        return features

    def hash_features(self, features: list[float], salt: str) -> str:
        """Hash tap timing features"""
        rounded_features = [round(f, 3) for f in features]
        feature_str = json.dumps(rounded_features, sort_keys=True)

        hasher = hashlib.sha256()
        hasher.update(salt.encode())
        hasher.update(feature_str.encode())

        return hasher.hexdigest()

    def calculate_quality_score(self, features: list[float]) -> float:
        """Quality based on rhythm consistency and complexity"""
        if len(features) < 5:
            return 0.0

        tap_count = features[0]
        interval_std = features[2]

        # More taps and consistent timing = higher quality
        complexity_score = min(1.0, tap_count / 5.0)  # Up to 5 taps
        consistency_score = max(0.1, 1.0 - min(1.0, interval_std))

        return (complexity_score + consistency_score) / 2.0


class MockStrokeData:
    """Generate realistic mock stroke data for development"""

    @staticmethod
    def generate_signature_stroke() -> dict[str, Any]:
        """Generate mock signature stroke"""
        import random
        import time

        points = []
        start_time = time.time()

        # Simulate signature with curves and variations
        for i in range(20):
            t = i / 19.0

            # Curved path with some randomness
            x = 100 + 200 * t + 30 * math.sin(t * math.pi * 2)
            y = 200 + 50 * math.sin(t * math.pi * 4) + random.gauss(0, 5)

            # Varying pressure
            pressure = 0.3 + 0.4 * math.sin(t * math.pi) + random.gauss(0, 0.1)
            pressure = max(0.1, min(1.0, pressure))

            timestamp = start_time + t * 1.5  # 1.5 second gesture

            points.append({"x": x, "y": y, "timestamp": timestamp, "pressure": pressure})

        return {"points": points}

    @staticmethod
    def generate_tap_sequence() -> dict[str, Any]:
        """Generate mock tap sequence"""
        import random
        import time

        taps = []
        base_time = time.time()

        # Generate 4-tap rhythm: quick-quick-slow-quick
        intervals = [0.0, 0.2, 0.4, 1.0, 1.3]

        for _i, interval in enumerate(intervals):
            tap = {
                "timestamp": base_time + interval,
                "x": 200 + random.gauss(0, 10),  # Some spatial variation
                "y": 300 + random.gauss(0, 10),
            }
            taps.append(tap)

        return {"taps": taps}


# Factory function for creating recognizers
def create_gesture_recognizer(gesture_type: GestureType) -> GestureRecognizer:
    """Create appropriate gesture recognizer for type"""
    if gesture_type == GestureType.STROKE:
        return StrokeGestureRecognizer()
    elif gesture_type == GestureType.TAP_SEQUENCE:
        return TapSequenceRecognizer()
    elif gesture_type == GestureType.SIGNATURE:
        return StrokeGestureRecognizer()  # Signatures use stroke recognition
    else:
        raise ValueError(f"Unsupported gesture type: {gesture_type}")


# Import EdgeGestureProcessor from parent module
from .. import EdgeGestureProcessor

__all__ = [
    "EdgeGestureProcessor",  # Re-export from parent
    "MockStrokeData",
    "StrokeGestureRecognizer",
    "TapSequenceRecognizer",
    "create_gesture_recognizer",
]