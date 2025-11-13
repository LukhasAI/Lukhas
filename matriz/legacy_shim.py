#!/usr/bin/env python3
"""
Legacy MATRIZ Interface Shim
T4-Approved: Adapts existing complex CognitiveNode to frozen v1.0.0 contract

This shim allows existing LUKHAS implementations to work with the
simplified MatrizNode contract without breaking changes.

Usage:
    from matriz.legacy_shim import LegacyShim
    from matriz.core.node_interface import SomeExistingNode

    legacy_node = SomeExistingNode()
    v1_node = LegacyShim(legacy_node)
    result = v1_node.handle(v1_message)
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from matriz.node_contract import (
    CONTRACT_VERSION,
    MatrizMessage,
    MatrizNode,
    MatrizResult,
    message_digest,
    mk_guardian_token,
    validate_message,
    validate_result,
)

# Import the existing complex interface
try:
    from matriz.core.node_interface import CognitiveNode

    LEGACY_AVAILABLE = True
except ImportError:
    # Graceful fallback if legacy interface not available
    LEGACY_AVAILABLE = False
    CognitiveNode = None

logger = logging.getLogger(__name__)


class LegacyShim(MatrizNode):
    """
    Shim to adapt legacy CognitiveNode to MatrizNode v1.0.0 contract

    This adapter wraps the complex legacy interface behind the
    simplified frozen contract, enabling gradual migration.
    """

    def __init__(self, legacy_node: Any):
        """
        Initialize shim with legacy node

        Args:
            legacy_node: Existing CognitiveNode implementation
        """
        if not LEGACY_AVAILABLE:
            raise ImportError("Legacy MATRIZ interface not available. " "Cannot create shim.")

        self.legacy = legacy_node
        self.name = f"shim_{legacy_node.__class__.__name__}"
        self.version = CONTRACT_VERSION

        logger.info(f"Created legacy shim for {self.legacy.__class__.__name__}")

    def handle(self, msg: MatrizMessage) -> MatrizResult:
        """
        Adapt v1.0.0 message to legacy format and back

        Args:
            msg: v1.0.0 MatrizMessage

        Returns:
            MatrizResult with legacy processing results
        """
        # Enforce incoming message contract early
        if not validate_message(msg):
            return MatrizResult(
                ok=False,
                reasons=["contract_violation:invalid_message"],
                payload={},
                trace={"error": "invalid_message", "shim_version": self.version},
                guardian_log=[mk_guardian_token(self.name, msg.lane, msg.msg_id)],
            )

        if not LEGACY_AVAILABLE:
            return MatrizResult(
                ok=False,
                reasons=["Legacy interface not available"],
                payload={},
                trace={"error": "legacy_unavailable"},
                guardian_log=["shim_error"],
            )

        try:
            # Transform v1 message to legacy format
            legacy_input = self._to_legacy_format(msg)

            # Process with legacy node
            if hasattr(self.legacy, "process"):
                legacy_output = self.legacy.process(legacy_input)
            elif hasattr(self.legacy, "handle"):
                legacy_output = self.legacy.handle(legacy_input)
            else:
                # Try to call the node directly
                legacy_output = self.legacy(legacy_input)

            # Transform legacy output to v1 format
            return self._from_legacy_format(legacy_output, msg)

        except Exception as e:
            logger.error(f"Legacy shim error: {e}")
            token = mk_guardian_token(self.name, msg.lane, msg.msg_id)
            return MatrizResult(
                ok=False,
                reasons=[f"Legacy processing error: {e!s}"],
                payload={},
                trace={
                    "error": str(e),
                    "legacy_node": self.legacy.__class__.__name__,
                    "shim_version": self.version,
                },
                guardian_log=[token],
            )

    def _to_legacy_format(self, msg: MatrizMessage) -> dict[str, Any]:
        """
        Convert v1.0.0 MatrizMessage to legacy format

        Args:
            msg: v1.0.0 message

        Returns:
            Dictionary in legacy format
        """
        # Create legacy-compatible structure
        legacy_input = {
            "node_id": str(msg.glyph.id),
            "timestamp": int(msg.ts.timestamp() * 1000),  # epoch millis
            "content": msg.payload,
            "metadata": {
                "topic": msg.topic,
                "lane": msg.lane,
                "glyph_kind": msg.glyph.kind,
                "glyph_version": msg.glyph.version,
                "glyph_tags": msg.glyph.tags,
                "guardian_token": msg.guardian_token,
            },
            # Legacy fields that may be expected
            "state": {"confidence": 0.8, "salience": 0.7, "novelty": 0.5},  # Default values
            "links": [],  # Empty for now
            "provenance": {
                "producer": "legacy_shim",
                "tenant": "default",
                "trace_id": str(msg.msg_id),
                "digest": message_digest(msg),
                "idempotency_key": msg.idempotency_key or str(msg.msg_id),
            },
        }

        return legacy_input

    def _from_legacy_format(self, legacy_output: Any, original_msg: MatrizMessage) -> MatrizResult:
        """
        Convert legacy output to v1.0.0 MatrizResult

        Args:
            legacy_output: Output from legacy node
            original_msg: Original v1 message for context

        Returns:
            MatrizResult in v1.0.0 format
        """
        # Handle different legacy output formats
        if isinstance(legacy_output, dict):
            # Dictionary output
            payload = legacy_output.get("content", legacy_output)
            success = legacy_output.get("success", True)
            trace = {
                "legacy_format": "dict",
                "original_keys": list(legacy_output.keys()),
                "processed_at": datetime.now(timezone.utc).isoformat(),
            }

        elif hasattr(legacy_output, "__dict__"):
            # Object output (NodeState, etc.)
            payload = {
                "confidence": getattr(legacy_output, "confidence", 0.8),
                "salience": getattr(legacy_output, "salience", 0.7),
                "content": getattr(legacy_output, "content", {}),
            }
            success = True
            trace = {
                "legacy_format": "object",
                "object_type": legacy_output.__class__.__name__,
                "processed_at": datetime.now(timezone.utc).isoformat(),
            }

        else:
            # Raw output
            payload = {"result": legacy_output}
            success = True
            trace = {
                "legacy_format": "raw",
                "output_type": type(legacy_output).__name__,
                "processed_at": datetime.now(timezone.utc).isoformat(),
            }

        # Add shim metadata to trace
        trace.update(
            {
                "shim_version": self.version,
                "legacy_node": self.legacy.__class__.__name__,
                "original_topic": original_msg.topic,
                "adaptation_successful": success,
            }
        )

        token = mk_guardian_token(self.name, original_msg.lane, original_msg.msg_id)
        result = MatrizResult(
            ok=success,
            reasons=[] if success else ["Legacy processing failed"],
            payload=payload,
            trace=trace,
            guardian_log=[token],
        )
        # Ensure the result conforms to contract (e.g., guardian_log non-empty, JSON payload)
        if not validate_result(result):
            # If legacy output produced an invalid result shape, coerce minimally
            result.ok = False  # type: ignore[attr-defined]
            result.reasons.append("contract_violation:invalid_result")  # type: ignore[attr-defined]
        return result


def create_shim(legacy_node: Any) -> MatrizNode:
    """
    Factory function to create legacy shim

    Args:
        legacy_node: Existing CognitiveNode or compatible object

    Returns:
        MatrizNode that wraps the legacy implementation
    """
    return LegacyShim(legacy_node)


def is_legacy_available() -> bool:
    """Check if legacy MATRIZ interface is available"""
    return LEGACY_AVAILABLE


# Compatibility utilities
def migrate_legacy_nodes() -> dict[str, MatrizNode]:
    """
    Auto-discover and wrap legacy nodes

    Returns:
        Dictionary mapping node names to shimmed v1.0.0 nodes
    """
    if not LEGACY_AVAILABLE:
        logger.warning("Legacy interface not available for migration")
        return {}

    # This would scan for existing legacy nodes and wrap them
    # Implementation depends on specific legacy node discovery mechanism
    legacy_nodes = {}

    try:
        # Example: scan for common legacy node types
        # In practice, this would discover actual legacy implementations
        logger.info("Scanning for legacy nodes to migrate...")

        # Placeholder for actual migration logic
        # legacy_nodes["memory"] = create_shim(some_legacy_memory_node)
        # legacy_nodes["consciousness"] = create_shim(some_legacy_consciousness_node)

    except Exception as e:
        logger.error(f"Error during legacy node migration: {e}")

    logger.info(f"Migrated {len(legacy_nodes)} legacy nodes to v1.0.0")
    return legacy_nodes


__all__ = ["LegacyShim", "create_shim", "is_legacy_available", "logger", "migrate_legacy_nodes"]
