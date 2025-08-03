"""
LUKHAS Entropy Synchronizer - Gemini's Multi-Device Entropy Sync

This module implements multi-device entropy synchronization for the LUKHAS authentication system.
It coordinates entropy collection across devices using WebSocket communication and constitutional
enforcement to ensure secure and accessible authentication.

Author: LUKHAS Team
Date: June 2025
Constitutional AI Guidelines: Enforced
Integration: Gemini's multi-device architecture with Claude's constitutional oversight
"""

import asyncio
import websockets
import json
import hashlib
import time
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Import constitutional enforcement
from .constitutional_gatekeeper import get_constitutional_gatekeeper, ConstitutionalLevel

# Configure entropy logging
logging.basicConfig(level=logging.INFO)
entropy_logger = logging.getLogger('LUKHAS_ENTROPY_SYNC')

class DeviceType(Enum):
    """Supported device types for entropy synchronization"""
    MOBILE_PHONE = "mobile_phone"
    TABLET = "tablet"
    WEARABLE = "wearable"
    DESKTOP = "desktop"
    WEB_BROWSER = "web_browser"

@dataclass
class EntropySource:
    """Represents a source of entropy from a device"""
    device_id: str
    device_type: DeviceType
    entropy_data: Dict[str, Any]
    timestamp: datetime
    quality_score: float  # 0.0 to 1.0
    constitutional_validation: bool

class EntropySynchronizer:
    """
    Multi-device entropy synchronization coordinator.

    This class manages entropy collection across multiple devices while enforcing
    constitutional constraints and ensuring accessibility compliance.
    """

    def __init__(self, session_id: str, enforcement_level: ConstitutionalLevel = ConstitutionalLevel.STANDARD):
        self.session_id = session_id
        self.constitutional_gatekeeper = get_constitutional_gatekeeper(enforcement_level)
        self.connected_devices: Dict[str, DeviceType] = {}
        self.entropy_buffer: List[EntropySource] = []
        self.sync_callbacks: List = []
        self.websocket_server = None
        self.min_entropy_bits = 512  # Constitutional minimum
        self.max_sync_devices = 10   # Constitutional maximum

        entropy_logger.info(f"Entropy Synchronizer initialized for session {session_id}")

    async def start_sync_server(self, host: str = "localhost", port: int = 8080) -> bool:
        """
        Start the WebSocket server for device synchronization.

        Args:
            host: Server host address
            port: Server port number

        Returns:
            True if server started successfully
        """
        try:
            # Validate constitutional parameters
            if not self.constitutional_gatekeeper.validate_entropy_sync(
                device_count=1,  # Starting with 0 devices
                sync_interval=1.0
            ):
                entropy_logger.error("Constitutional validation failed for sync server")
                return False

            self.websocket_server = await websockets.serve(
                self._handle_device_connection,
                host,
                port
            )

            entropy_logger.info(f"Entropy sync server started on {host}:{port}")
            return True

        except Exception as e:
            entropy_logger.error(f"Failed to start sync server: {e}")
            return False

    async def _handle_device_connection(self, websocket, path):
        """Handle incoming device connections"""
        device_id = None
        try:
            async for message in websocket:
                data = json.loads(message)

                if data.get("type") == "device_auth":
                    device_id = data.get("device_id")
                    device_type = DeviceType(data.get("device_type", "web_browser"))

                    # Constitutional device limit check
                    if len(self.connected_devices) >= self.max_sync_devices:
                        await websocket.send(json.dumps({
                            "type": "connection_rejected",
                            "reason": "Maximum device limit reached (constitutional enforcement)"
                        }))
                        break

                    self.connected_devices[device_id] = device_type
                    await websocket.send(json.dumps({
                        "type": "device_authenticated",
                        "session_id": self.session_id
                    }))

                    entropy_logger.info(f"Device {device_id} connected as {device_type.value}")

                elif data.get("type") == "entropy_data":
                    await self._process_entropy_data(device_id, data, websocket)

        except websockets.exceptions.ConnectionClosed:
            if device_id and device_id in self.connected_devices:
                del self.connected_devices[device_id]
                entropy_logger.info(f"Device {device_id} disconnected")
        except Exception as e:
            entropy_logger.error(f"Error handling device connection: {e}")

    async def _process_entropy_data(self, device_id: str, data: Dict[str, Any], websocket):
        """Process incoming entropy data from a device"""
        try:
            entropy_data = data.get("entropy", {})
            device_type = self.connected_devices.get(device_id)

            if not device_type:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "Device not authenticated"
                }))
                return

            # Validate entropy quality
            quality_score = self._calculate_entropy_quality(entropy_data, device_type)

            # Constitutional validation
            constitutional_valid = quality_score >= 0.3  # Minimum quality threshold

            entropy_source = EntropySource(
                device_id=device_id,
                device_type=device_type,
                entropy_data=entropy_data,
                timestamp=datetime.now(),
                quality_score=quality_score,
                constitutional_validation=constitutional_valid
            )

            if constitutional_valid:
                self.entropy_buffer.append(entropy_source)

                # Limit buffer size (constitutional memory management)
                if len(self.entropy_buffer) > 100:
                    self.entropy_buffer = self.entropy_buffer[-80:]  # Keep last 80 entries

                # Broadcast to other devices if sufficient entropy
                if self._calculate_total_entropy_bits() >= self.min_entropy_bits:
                    await self._broadcast_sync_complete()

            # Send acknowledgment
            await websocket.send(json.dumps({
                "type": "entropy_ack",
                "quality_score": quality_score,
                "constitutional_valid": constitutional_valid,
                "total_entropy_bits": self._calculate_total_entropy_bits()
            }))

        except Exception as e:
            entropy_logger.error(f"Error processing entropy data: {e}")

    def _calculate_entropy_quality(self, entropy_data: Dict[str, Any], device_type: DeviceType) -> float:
        """
        Calculate the quality score of entropy data.

        Args:
            entropy_data: The entropy data to evaluate
            device_type: Type of device providing the entropy

        Returns:
            Quality score between 0.0 and 1.0
        """
        quality_factors = []

        # Check data variety
        data_types = len(entropy_data.keys())
        variety_score = min(data_types / 5.0, 1.0)  # Max score at 5+ data types
        quality_factors.append(variety_score)

        # Check temporal freshness
        if 'timestamp' in entropy_data:
            age_seconds = (datetime.now() - datetime.fromisoformat(entropy_data['timestamp'])).total_seconds()
            freshness_score = max(0.0, 1.0 - (age_seconds / 60.0))  # Decay over 1 minute
            quality_factors.append(freshness_score)

        # Device-specific quality factors
        if device_type == DeviceType.MOBILE_PHONE:
            # Mobile devices provide high-quality entropy from sensors
            if 'accelerometer' in entropy_data or 'gyroscope' in entropy_data:
                quality_factors.append(0.9)
            if 'touch_pressure' in entropy_data:
                quality_factors.append(0.8)

        elif device_type == DeviceType.WEARABLE:
            # Wearables provide biometric entropy
            if 'heart_rate' in entropy_data:
                quality_factors.append(0.95)
            if 'motion' in entropy_data:
                quality_factors.append(0.8)

        elif device_type == DeviceType.WEB_BROWSER:
            # Browser entropy is lower quality but still valuable
            if 'mouse_movement' in entropy_data:
                quality_factors.append(0.6)
            if 'keyboard_timing' in entropy_data:
                quality_factors.append(0.7)

        # Calculate weighted average
        if quality_factors:
            return sum(quality_factors) / len(quality_factors)
        else:
            return 0.1  # Minimum quality for any data

    def _calculate_total_entropy_bits(self) -> int:
        """Calculate total entropy bits from all collected sources"""
        if not self.entropy_buffer:
            return 0

        # Simple entropy calculation based on data variety and quality
        total_bits = 0
        for source in self.entropy_buffer:
            data_complexity = len(json.dumps(source.entropy_data))
            quality_multiplier = source.quality_score
            entropy_contribution = min(64, data_complexity * quality_multiplier)  # Cap per source
            total_bits += entropy_contribution

        return int(total_bits)

    async def _broadcast_sync_complete(self):
        """Broadcast sync completion to all connected devices"""
        completion_message = {
            "type": "sync_complete",
            "session_id": self.session_id,
            "total_entropy_bits": self._calculate_total_entropy_bits(),
            "device_count": len(self.connected_devices),
            "timestamp": datetime.now().isoformat()
        }

        # Trigger callbacks
        for callback in self.sync_callbacks:
            try:
                await callback(completion_message)
            except Exception as e:
                entropy_logger.error(f"Error in sync callback: {e}")

    def add_sync_callback(self, callback):
        """Add callback function for sync completion events"""
        self.sync_callbacks.append(callback)

    def get_entropy_summary(self) -> Dict[str, Any]:
        """
        Get summary of current entropy state.

        Returns:
            Dictionary containing entropy statistics
        """
        return {
            "session_id": self.session_id,
            "connected_devices": len(self.connected_devices),
            "device_types": [dt.value for dt in self.connected_devices.values()],
            "entropy_sources": len(self.entropy_buffer),
            "total_entropy_bits": self._calculate_total_entropy_bits(),
            "constitutional_compliance": self._calculate_total_entropy_bits() >= self.min_entropy_bits,
            "average_quality_score": sum(s.quality_score for s in self.entropy_buffer) / len(self.entropy_buffer) if self.entropy_buffer else 0.0
        }

    async def emergency_reset(self, reason: str = "Emergency reset requested"):
        """
        Emergency reset of all entropy synchronization.

        Args:
            reason: Reason for emergency reset
        """
        entropy_logger.warning(f"Emergency reset triggered: {reason}")

        # Clear all entropy data
        self.entropy_buffer.clear()

        # Disconnect all devices
        self.connected_devices.clear()

        # Trigger constitutional emergency if needed
        emergency_report = self.constitutional_gatekeeper.emergency_lockdown(
            f"Entropy synchronization emergency: {reason}"
        )

        return emergency_report

# Export the main class
__all__ = ['EntropySynchronizer', 'DeviceType', 'EntropySource']
