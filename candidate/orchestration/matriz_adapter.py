"""
MATRIZ Adapter for Orchestration Module
Emits MATRIZ-compliant nodes for brain and orchestration events
"""
import json
import time
import uuid
from pathlib import Path
from typing import Any, Optional

import streamlit as st


class OrchestrationMatrizAdapter:
    """Adapter to emit MATRIZ nodes for orchestration/brain events"""

    SCHEMA_REF = "lukhas://schemas/matriz_node_v1.json"

    @staticmethod
    def create_node(
        node_type: str,
        state: dict[str, float],
        labels: Optional[list[str]] = None,
        provenance_extra: Optional[dict] = None,
    ) -> dict[str, Any]:
        """Create a MATRIZ-compliant node for orchestration events"""

        node = {
            "version": 1,
            "id": f"LT-ORCH-{uuid.uuid4().hex[:8]}",
            "type": node_type,
            "state": {
                "confidence": state.get("confidence", 0.9),
                "salience": state.get("salience", 0.7),
                "urgency": state.get("urgency", 0.4),
                "novelty": state.get("novelty", 0.5),
                **state,
            },
            "timestamps": {"created_ts": int(time.time() * 1000)},
            "provenance": {
                "producer": "lukhas.orchestration",
                "capabilities": [
                    "orchestration:brain",
                    "orchestration:coordinate",
                    "orchestration:route",
                ],
                "tenant": "system",
                "trace_id": f"LT-ORCH-{int(time.time())}",
                "consent_scopes": ["system:orchestration"],
                **(provenance_extra or {}),
            },
        }

        if labels:
            node["labels"] = labels

        return node

    @staticmethod
    def emit_brain_decision(
        decision_id: str,
        decision_type: str,
        components_involved: list[str],
        confidence: float,
    ) -> dict[str, Any]:
        """Emit a brain-level decision event"""

        return OrchestrationMatrizAdapter.create_node(
            node_type="DECISION",
            state={
                "confidence": confidence,
                "salience": 0.9,
                "urgency": 0.5,
                "novelty": 0.4,
                "component_count": float(len(components_involved)),
            },
            labels=[
                f"brain:{decision_id}",
                f"type:{decision_type}",
                f"components:{len(components_involved)}",
                "orchestration:brain",
            ]
            + [f"component:{c}" for c in components_involved[:3]],
        )

    @staticmethod
    def emit_coordination_event(
        coordination_id: str,
        source_module: str,
        target_module: str,
        message_type: str,
        latency_ms: int,
    ) -> dict[str, Any]:
        """Emit a module coordination event"""

        return OrchestrationMatrizAdapter.create_node(
            node_type="TEMPORAL",
            state={
                "confidence": 0.95,
                "salience": 0.6,
                "urgency": 0.3,
                "novelty": 0.3,
                "latency_ms": float(latency_ms),
            },
            labels=[
                f"coordination:{coordination_id}",
                f"source:{source_module}",
                f"target:{target_module}",
                f"message:{message_type}",
                "orchestration:coordinate",
            ],
        )

    @staticmethod
    def emit_routing_event(route_id: str, event_type: str, route_path: list[str], success: bool) -> dict[str, Any]:
        """Emit an event routing decision"""

        return OrchestrationMatrizAdapter.create_node(
            node_type="CAUSAL",
            state={
                "confidence": 0.9,
                "salience": 0.7,
                "urgency": 0.2 if success else 0.8,
                "novelty": 0.4,
                "path_length": float(len(route_path)),
                "success": 1.0 if success else 0.0,
            },
            labels=[
                f"route:{route_id}",
                f"event:{event_type}",
                f"hops:{len(route_path)}",
                "status:success" if success else "status:failed",
                "orchestration:route",
            ],
        )

    @staticmethod
    def emit_kernel_bus_event(
        bus_id: str, event_type: str, subscribers: int, broadcast_latency_ms: int
    ) -> dict[str, Any]:
        """Emit a kernel bus broadcast event"""

        return OrchestrationMatrizAdapter.create_node(
            node_type="TEMPORAL",
            state={
                "confidence": 1.0,
                "salience": 0.5,
                "urgency": 0.3,
                "novelty": 0.2,
                "subscribers": float(subscribers),
                "latency_ms": float(broadcast_latency_ms),
            },
            labels=[
                f"bus:{bus_id}",
                f"event:{event_type}",
                f"subscribers:{subscribers}",
                "orchestration:kernel_bus",
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
            output_dir = Path("memory/inbox/orchestration")

        output_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{node['id']}_{int(time.time())}.json"
        filepath = output_dir / filename

        with open(filepath, "w") as f:
            json.dump(node, f, indent=2)

        return filepath
