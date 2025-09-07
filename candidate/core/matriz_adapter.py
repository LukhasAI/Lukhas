"""
MATRIZ Adapter for Core Module
Emits MATRIZ-compliant nodes for core system events
"""
import streamlit as st

import json
import time
import uuid
from pathlib import Path
from typing import Any, Optional


class CoreMatrizAdapter:
    """Adapter to emit MATRIZ nodes for core system events"""

    SCHEMA_REF = "lukhas://schemas/matriz_node_v1.json"

    @staticmethod
    def create_node(
        node_type: str,
        state: dict[str, float],
        labels: Optional[list[str]] = None,
        provenance_extra: Optional[dict] = None,
    ) -> dict[str, Any]:
        """Create a MATRIZ-compliant node for core events"""

        node = {
            "version": 1,
            "id": f"LT-CORE-{uuid.uuid4()}.hex[:8]}",
            "type": node_type,
            "state": {
                "confidence": state.get("confidence", 0.9),
                "salience": state.get("salience", 0.6),
                "urgency": state.get("urgency", 0.3),
                "novelty": state.get("novelty", 0.4),
                **state,
            },
            "timestamps": {"created_ts": int(time.time() * 1000)},
            "provenance": {
                "producer": "lukhas.core",
                "capabilities": ["core:orchestrate", "core:glyph", "core:symbolic"],
                "tenant": "system",
                "trace_id": f"LT-CORE-{int(time.time()}",
                "consent_scopes": ["system:core"],
                **(provenance_extra or {}),
            },
        }

        if labels:
            node["labels"] = labels

        return node

    @staticmethod
    def emit_glyph_event(glyph: str, operation: str, context: Optional[dict] = None) -> dict[str, Any]:
        """Emit a GLYPH processing event node"""

        return CoreMatrizAdapter.create_node(
            node_type="DECISION",
            state={
                "confidence": 0.95,
                "salience": 0.7,
                "urgency": 0.2,
                "novelty": 0.3,
                **(context or {}),
            },
            labels=[f"glyph:{glyph}", f"operation:{operation}", "core:glyph"],
        )

    @staticmethod
    def emit_orchestration_event(
        component: str, action: str, status: str, latency_ms: Optional[int] = None
    ) -> dict[str, Any]:
        """Emit an orchestration event node"""

        urgency = 0.1 if status == "success" else 0.8

        state = {"confidence": 0.9, "salience": 0.6, "urgency": urgency, "novelty": 0.2}

        if latency_ms:
            state["latency_ms"] = latency_ms

        return CoreMatrizAdapter.create_node(
            node_type="TEMPORAL",
            state=state,
            labels=[
                f"component:{component}",
                f"action:{action}",
                f"status:{status}",
                "core:orchestration",
            ],
        )

    @staticmethod
    def emit_symbolic_reasoning(
        symbol: str,
        inference_type: str,
        confidence: float,
        conclusion: Optional[str] = None,
    ) -> dict[str, Any]:
        """Emit a symbolic reasoning event node"""

        labels = [f"symbol:{symbol}", f"inference:{inference_type}", "core:symbolic"]

        if conclusion:
            labels.append(f"conclusion:{conclusion[:20]}")

        return CoreMatrizAdapter.create_node(
            node_type="CAUSAL",
            state={
                "confidence": confidence,
                "salience": 0.8,
                "urgency": 0.3,
                "novelty": 0.5,
            },
            labels=labels,
        )

    @staticmethod
    def emit_actor_event(actor_id: str, event_type: str, message_type: Optional[str] = None) -> dict[str, Any]:
        """Emit an actor system event node"""

        return CoreMatrizAdapter.create_node(
            node_type="TEMPORAL",
            state={"confidence": 1.0, "salience": 0.5, "urgency": 0.2, "novelty": 0.1},
            labels=[
                f"actor:{actor_id}",
                f"event:{event_type}",
                f"message:{message_type}" if message_type else "message:none",
                "core:actor",
            ],
        )

    @staticmethod
    def emit_integration_event(source_module: str, target_module: str, operation: str, success: bool) -> dict[str, Any]:
        """Emit an integration event between modules"""

        return CoreMatrizAdapter.create_node(
            node_type="TEMPORAL",
            state={
                "confidence": 0.95,
                "salience": 0.6,
                "urgency": 0.1 if success else 0.9,
                "novelty": 0.2,
                "success": 1.0 if success else 0.0,
            },
            labels=[
                f"source:{source_module}",
                f"target:{target_module}",
                f"operation:{operation}",
                "status:success" if success else "status:failed",
                "core:integration",
            ],
        )

    @staticmethod
    def validate_node(node: dict[str, Any]) -> bool:
        """Validate that a node meets MATRIZ requirements"""
        required_fields = ["version", "id", "type", "state", "timestamps", "provenance"]

        for field in required_fields:
            if field not in node:
                return False

        # Check required provenance fields
        required_prov = [
            "producer",
            "capabilities",
            "tenant",
            "trace_id",
            "consent_scopes",
        ]
        return all(field in node.get("provenance", {}) for field in required_prov)

    @staticmethod
    def save_node(node: dict[str, Any], output_dir: Optional[Path] = None) -> Path:
        """Save a MATRIZ node to disk for audit"""
        if output_dir is None:
            output_dir = Path("memory/inbox/core")

        output_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{node['id']}_{int(time.time()}.json"
        filepath = output_dir / filename

        with open(filepath, "w") as f:
            json.dump(node, f, indent=2)

        return filepath
