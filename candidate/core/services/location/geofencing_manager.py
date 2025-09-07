"""
Geofencing Manager - Location-based services for LUKHAS
Provides geofencing capabilities for context-aware AI responses
"""
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class GeofenceRegion:
    """Represents a geofenced region"""

    id: str
    name: str
    latitude: float
    longitude: float
    radius: float  # in meters
    active: bool = True
    triggers: list[str] = None
    metadata: dict = None

    def __post_init__(self):
        if self.triggers is None:
            self.triggers = []
        if self.metadata is None:
            self.metadata = {}


class GeofencingManager:
    """Manages geofencing operations for LUKHAS"""

    def __init__(self):
        self.regions: dict[str, GeofenceRegion] = {}
        self.current_location: Optional[tuple[float, float]] = None
        self.active_triggers: list[str] = []

    async def add_region(self, region: GeofenceRegion) -> bool:
        """Add a new geofenced region"""
        try:
            self.regions[region.id] = region
            logger.info(f"Added geofence region: {region.name} ({region.id})")
            return True
        except Exception as e:
            logger.error(f"Failed to add geofence region: {e}")
            return False

    async def remove_region(self, region_id: str) -> bool:
        """Remove a geofenced region"""
        try:
            if region_id in self.regions:
                region = self.regions.pop(region_id)
                logger.info(f"Removed geofence region: {region.name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove geofence region: {e}")
            return False

    async def update_location(self, latitude: float, longitude: float) -> list[str]:
        """Update current location and check for geofence triggers"""
        try:
            self.current_location = (latitude, longitude)
            triggered_regions = []

            for region in self.regions.values():
                if not region.active:
                    continue

                distance = self._calculate_distance(latitude, longitude, region.latitude, region.longitude)

                if distance <= region.radius:
                    if region.id not in self.active_triggers:
                        self.active_triggers.append(region.id)
                        triggered_regions.append(region.id)
                        logger.info(f"Entered geofence: {region.name}")
                elif region.id in self.active_triggers:
                    self.active_triggers.remove(region.id)
                    logger.info(f"Exited geofence: {region.name}")

            return triggered_regions

        except Exception as e:
            logger.error(f"Failed to update location: {e}")
            return []

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula"""
        import math

        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))

        # Radius of earth in meters
        r = 6371000
        return c * r

    async def get_nearby_regions(self, max_distance: float = 1000) -> list[GeofenceRegion]:
        """Get regions within specified distance from current location"""
        if not self.current_location:
            return []

        nearby = []
        lat, lon = self.current_location

        for region in self.regions.values():
            distance = self._calculate_distance(lat, lon, region.latitude, region.longitude)
            if distance <= max_distance:
                nearby.append(region)

        return nearby

    async def get_context_for_location(self) -> dict:
        """Get contextual information for current location"""
        if not self.current_location:
            return {"status": "location_unknown"}

        context = {
            "current_location": self.current_location,
            "active_triggers": self.active_triggers,
            "nearby_regions": [region.name for region in await self.get_nearby_regions()],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        return context

    async def export_regions(self) -> str:
        """Export all regions to JSON"""
        data = {}
        for region_id, region in self.regions.items():
            data[region_id] = {
                "name": region.name,
                "latitude": region.latitude,
                "longitude": region.longitude,
                "radius": region.radius,
                "active": region.active,
                "triggers": region.triggers,
                "metadata": region.metadata,
            }
        return json.dumps(data, indent=2)

    async def import_regions(self, json_data: str) -> bool:
        """Import regions from JSON"""
        try:
            data = json.loads(json_data)
            for region_id, region_data in data.items():
                region = GeofenceRegion(
                    id=region_id,
                    name=region_data["name"],
                    latitude=region_data["latitude"],
                    longitude=region_data["longitude"],
                    radius=region_data["radius"],
                    active=region_data.get("active", True),
                    triggers=region_data.get("triggers", []),
                    metadata=region_data.get("metadata", {}),
                )
                await self.add_region(region)
            return True
        except Exception as e:
            logger.error(f"Failed to import regions: {e}")
            return False
