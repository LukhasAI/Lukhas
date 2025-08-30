"""
Location Tracker - Real-time location tracking for LUKHAS
Handles device location updates and privacy-aware tracking
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable, Optional

logger = logging.getLogger(__name__)


@dataclass
class LocationUpdate:
    """Represents a location update"""

    latitude: float
    longitude: float
    accuracy: float
    timestamp: datetime
    source: str = "unknown"
    altitude: Optional[float] = None
    speed: Optional[float] = None
    heading: Optional[float] = None


class LocationTracker:
    """Tracks device location with privacy controls"""

    def __init__(self, privacy_level: str = "medium"):
        self.privacy_level = privacy_level  # low, medium, high
        self.tracking_enabled = False
        self.current_location: Optional[LocationUpdate] = None
        self.location_history: list[LocationUpdate] = []
        self.max_history_size = 100
        self.update_callbacks: list[Callable] = []
        self.minimum_distance = 10  # meters
        self.minimum_time = 30  # seconds
        self.last_update_time: Optional[datetime] = None

    async def start_tracking(self) -> bool:
        """Start location tracking"""
        try:
            if self.privacy_level == "high":
                logger.warning("Location tracking disabled due to high privacy level")
                return False

            self.tracking_enabled = True
            logger.info("Location tracking started")
            return True
        except Exception as e:
            logger.error(f"Failed to start location tracking: {e}")
            return False

    async def stop_tracking(self) -> bool:
        """Stop location tracking"""
        try:
            self.tracking_enabled = False
            logger.info("Location tracking stopped")
            return True
        except Exception as e:
            logger.error(f"Failed to stop location tracking: {e}")
            return False

    async def update_location(self, location: LocationUpdate) -> bool:
        """Update current location with privacy filtering"""
        try:
            if not self.tracking_enabled:
                return False

            # Apply privacy filtering
            if not self._should_update_location(location):
                return False

            # Store previous location
            if self.current_location:
                self.location_history.append(self.current_location)

                # Limit history size
                if len(self.location_history) > self.max_history_size:
                    self.location_history.pop(0)

            self.current_location = location
            self.last_update_time = datetime.utcnow()

            # Notify callbacks
            await self._notify_callbacks(location)

            logger.debug(f"Location updated: {location.latitude}, {location.longitude}")
            return True

        except Exception as e:
            logger.error(f"Failed to update location: {e}")
            return False

    def _should_update_location(self, new_location: LocationUpdate) -> bool:
        """Determine if location should be updated based on privacy and accuracy"""
        # Check minimum time interval
        if (
            self.last_update_time
            and (datetime.utcnow() - self.last_update_time).total_seconds() < self.minimum_time
        ):
            return False

        # Check minimum distance if we have a previous location
        if self.current_location:
            distance = self._calculate_distance(
                self.current_location.latitude,
                self.current_location.longitude,
                new_location.latitude,
                new_location.longitude,
            )
            if distance < self.minimum_distance:
                return False

        # Privacy level checks
        if self.privacy_level == "high":
            return False
        elif self.privacy_level == "medium":
            # Only update if accuracy is good
            return new_location.accuracy < 100
        else:  # low privacy
            return True

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points"""
        import math

        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        return 6371000 * c  # Earth radius in meters

    async def _notify_callbacks(self, location: LocationUpdate):
        """Notify all registered callbacks of location update"""
        for callback in self.update_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(location)
                else:
                    callback(location)
            except Exception as e:
                logger.error(f"Error in location callback: {e}")

    def add_update_callback(self, callback: Callable):
        """Add a callback for location updates"""
        self.update_callbacks.append(callback)

    def remove_update_callback(self, callback: Callable):
        """Remove a callback for location updates"""
        if callback in self.update_callbacks:
            self.update_callbacks.remove(callback)

    async def get_current_location(self) -> Optional[LocationUpdate]:
        """Get current location"""
        return self.current_location

    async def get_location_history(self, max_age_hours: int = 24) -> list[LocationUpdate]:
        """Get recent location history"""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        return [loc for loc in self.location_history if loc.timestamp >= cutoff_time]

    async def clear_history(self) -> bool:
        """Clear location history"""
        try:
            self.location_history.clear()
            logger.info("Location history cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear location history: {e}")
            return False

    async def set_privacy_level(self, level: str) -> bool:
        """Set privacy level (low, medium, high)"""
        try:
            if level not in ["low", "medium", "high"]:
                raise ValueError("Invalid privacy level")

            old_level = self.privacy_level
            self.privacy_level = level

            # If switching to high privacy, stop tracking
            if level == "high" and self.tracking_enabled:
                await self.stop_tracking()
                await self.clear_history()

            logger.info(f"Privacy level changed from {old_level} to {level}")
            return True

        except Exception as e:
            logger.error(f"Failed to set privacy level: {e}")
            return False

    async def get_privacy_status(self) -> dict:
        """Get current privacy and tracking status"""
        return {
            "privacy_level": self.privacy_level,
            "tracking_enabled": self.tracking_enabled,
            "has_current_location": self.current_location is not None,
            "history_size": len(self.location_history),
            "last_update": (self.last_update_time.isoformat() if self.last_update_time else None),
        }
