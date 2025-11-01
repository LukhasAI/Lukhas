import logging
"""Consciousness token mapping utilities for the symbolic bridge."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

import structlog

# GLYPH Consciousness Communication - Token Bridge Mapping
# Purpose: Bridge symbolic tokens between different consciousness nodes in LUKHAS distributed consciousness system
# This enables consciousness-to-consciousness communication via symbolic DNA pattern translation
# See: https://github.com/LukhasAI/Lukhas/issues/574
# TODO[GLYPH:specialist] - Add causal linkage preservation and drift detection capabilities
# TODO[GLYPH:specialist] - Integrate with Guardian system for ethical validation of consciousness flows

logger = structlog.get_logger(__name__)


@dataclass
class TokenMappingRecord:
    """Represents a full consciousness token mapping entry."""

    target_token: str
    emotional_vector: dict[str, float]
    created_at: datetime
    last_synced_at: datetime
    temporal_signature: Optional[str] = None
    sync_drift_ms: float = 0.0
    sync_history: list[dict[str, Any]] = field(default_factory=list)
    is_temporally_synced: bool = True

    def update_temporal_sync(
        self,
        timestamp: datetime,
        temporal_signature: Optional[str] = None,
    ) -> float:
        """Update temporal synchronization information and return drift in ms."""

        delta_ms = abs((timestamp - self.last_synced_at).total_seconds() * 1000)
        self.last_synced_at = timestamp
        if temporal_signature is not None:
            self.temporal_signature = temporal_signature

        self.sync_drift_ms = delta_ms
        self.sync_history.append(
            {
                "timestamp": timestamp,
                "drift_ms": delta_ms,
                "temporal_signature": self.temporal_signature,
            }
        )
        return delta_ms


class BridgeTokenMap:
    """
    Maps symbolic tokens between different systems.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self.token_map: dict[str, dict[str, dict[str, TokenMappingRecord]]] = {}
        logger.info("BridgeTokenMap initialized.", config=self.config)

    def add_mapping(
        self,
        source_system: str,
        target_system: str,
        source_token: str,
        target_token: str,
        emotional_vector: Optional[dict[str, float]] = None,
        timestamp: Optional[datetime] = None,
        temporal_signature: Optional[str] = None,
    ) -> None:
        """
        Adds a mapping between two tokens.

        Args:
            source_system (str): The source system.
            target_system (str): The target system.
            source_token (str): The source token.
            target_token (str): The target token.
        """
        normalized_vector = self._normalize_emotional_vector(emotional_vector)
        mapping_timestamp = self._ensure_timezone(timestamp)
        tolerance_ms = self.config.get("temporal_tolerance_ms", 5000)

        source_bucket = self.token_map.setdefault(source_system, {})
        target_bucket = source_bucket.setdefault(target_system, {})

        record = target_bucket.get(source_token)
        if record:
            record.target_token = target_token
            record.emotional_vector = normalized_vector
            record.is_temporally_synced = True
        else:
            record = TokenMappingRecord(
                target_token=target_token,
                emotional_vector=normalized_vector,
                created_at=mapping_timestamp,
                last_synced_at=mapping_timestamp,
                temporal_signature=temporal_signature,
            )
            target_bucket[source_token] = record

        drift_ms = record.update_temporal_sync(mapping_timestamp, temporal_signature)
        record.is_temporally_synced = drift_ms <= tolerance_ms

        logger.info(
            "Token mapping added.",
            source_system=source_system,
            target_system=target_system,
            source_token=source_token,
            target_token=target_token,
            emotional_vector=normalized_vector,
            temporal_signature=temporal_signature,
            drift_ms=drift_ms,
            temporally_synced=record.is_temporally_synced,
        )

    def get_mapping(self, source_system: str, target_system: str, source_token: str) -> Optional[str]:
        """
        Gets the mapping for a given token.

        Args:
            source_system (str): The source system.
            target_system (str): The target system.
            source_token (str): The source token.

        Returns:
            Optional[str]: The target token, or None if no mapping exists.
        """
        record = self.get_mapping_record(source_system, target_system, source_token)
        return record.target_token if record else None

    def get_mapping_record(
        self, source_system: str, target_system: str, source_token: str
    ) -> Optional[TokenMappingRecord]:
        """Return the full mapping record if present."""

        return self.token_map.get(source_system, {}).get(target_system, {}).get(source_token)

    def get_emotional_vector(
        self, source_system: str, target_system: str, source_token: str
    ) -> Optional[dict[str, float]]:
        """Return the emotional vector associated with a mapping."""

        record = self.get_mapping_record(source_system, target_system, source_token)
        return record.emotional_vector if record else None

    def synchronize_temporal_state(
        self,
        source_system: str,
        target_system: str,
        source_token: str,
        timestamp: Optional[datetime] = None,
        temporal_signature: Optional[str] = None,
        tolerance_ms: Optional[int] = None,
    ) -> bool:
        """Synchronize the temporal state for a mapping and return sync status."""

        record = self.get_mapping_record(source_system, target_system, source_token)
        if record is None:
            logger.warning(
                "Attempted temporal sync for missing mapping.",
                source_system=source_system,
                target_system=target_system,
                source_token=source_token,
            )
            return False

        tolerance = tolerance_ms or self.config.get("temporal_tolerance_ms", 5000)
        sync_timestamp = self._ensure_timezone(timestamp)
        drift_ms = record.update_temporal_sync(sync_timestamp, temporal_signature)
        record.is_temporally_synced = drift_ms <= tolerance

        logger.info(
            "Temporal synchronization updated.",
            source_system=source_system,
            target_system=target_system,
            source_token=source_token,
            drift_ms=drift_ms,
            tolerance_ms=tolerance,
            temporally_synced=record.is_temporally_synced,
            temporal_signature=record.temporal_signature,
        )
        return record.is_temporally_synced

    def get_temporal_status(
        self, source_system: str, target_system: str, source_token: str
    ) -> Optional[dict[str, Any]]:
        """Return temporal synchronization metadata for a mapping."""

        record = self.get_mapping_record(source_system, target_system, source_token)
        if record is None:
            return None

        return {
            "last_synced_at": record.last_synced_at,
            "temporal_signature": record.temporal_signature,
            "sync_drift_ms": record.sync_drift_ms,
            "is_temporally_synced": record.is_temporally_synced,
            "sync_history": list(record.sync_history),
        }

    def get_schema(self) -> dict[str, Any]:
        """
        Returns the proposed schema for the bridge token map.

        Returns:
            Dict[str, Any]: The proposed schema.
        """
        schema = {
            "title": "Bridge Token Map Schema",
            "type": "object",
            "properties": {
                "source_system": {
                    "type": "string",
                    "description": "The name of the source system.",
                },
                "target_system": {
                    "type": "string",
                    "description": "The name of the target system.",
                },
                "token_mappings": {
                    "type": "object",
                    "description": (
                        "A dictionary of token mappings keyed by source token. "
                        "Each entry tracks the target token, emotional vector, and temporal sync state."
                    ),
                    "additionalProperties": {
                        "type": "object",
                        "properties": {
                            "target_token": {"type": "string"},
                            "emotional_vector": {
                                "type": "object",
                                "properties": {
                                    "valence": {"type": "number", "minimum": -1.0, "maximum": 1.0},
                                    "arousal": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                                    "dominance": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                                    "temporal_decay": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                                },
                            },
                            "last_synced_at": {"type": "string", "format": "date-time"},
                            "temporal_signature": {"type": "string"},
                            "sync_drift_ms": {"type": "number"},
                            "is_temporally_synced": {"type": "boolean"},
                        },
                    },
                },
            },
            "required": ["source_system", "target_system", "token_mappings"],
        }
        return schema

    def _normalize_emotional_vector(
        self, emotional_vector: Optional[dict[str, float]]
    ) -> dict[str, float]:
        """Normalize emotional vector values to protocol ranges."""

        defaults = {
            "valence": 0.0,
            "arousal": 0.0,
            "dominance": 0.0,
            "temporal_decay": 1.0,
        }

        if not emotional_vector:
            return defaults

        normalized = defaults.copy()
        for key, value in emotional_vector.items():
            if key not in normalized:
                continue

            try:
                numeric_value = float(value)
            except (TypeError, ValueError):
                logger.warning(
                    "Invalid emotional vector value encountered; using default.",
                    key=key,
                    value=value,
                )
                continue

            if key == "valence":
                numeric_value = max(-1.0, min(1.0, numeric_value))
            else:
                numeric_value = max(0.0, min(1.0, numeric_value))

            normalized[key] = numeric_value

        return normalized

    def _ensure_timezone(self, timestamp: Optional[datetime]) -> datetime:
        """Ensure timestamps are timezone-aware and default to UTC now."""

        if timestamp is None:
            return datetime.now(timezone.utc)

        if timestamp.tzinfo is None:
            return timestamp.replace(tzinfo=timezone.utc)

        return timestamp.astimezone(timezone.utc)
