"""
MATRIZ Adapter for Consciousness Module
Emits MATRIZ-compliant nodes for consciousness and awareness events
"""

import json
import time
import uuid
from pathlib import Path
from typing import Any, Optional


class ConsciousnessMatrizAdapter:
    """Adapter to emit MATRIZ nodes for consciousness system events"""

    SCHEMA_REF = "lukhas://schemas/matriz_node_v1.json"

    @staticmethod
    def create_node(
        node_type: str,
        state: dict[str, float],
        labels: Optional[list[str]] = None,
        provenance_extra: Optional[dict] = None,
    ) -> dict[str, Any]:
        """Create a MATRIZ-compliant node for consciousness events"""

        node = {
            "version": 1,
            "id": f"LT-CONS-{uuid.uuid4().hex[:8]}",
            "type": node_type,
            "state": {
                "confidence": state.get("confidence", 0.85),
                "salience": state.get("salience", 0.8),
                "urgency": state.get("urgency", 0.4),
                "novelty": state.get("novelty", 0.6),
                **state,
            },
            "timestamps": {"created_ts": int(time.time() * 1000)},
            "provenance": {
                "producer": "consciousness",
                "capabilities": [
                    "consciousness:aware",
                    "consciousness:decide",
                    "consciousness:dream",
                ],
                "tenant": "system",
                "trace_id": f"LT-CONS-{int(time.time())}",
                "consent_scopes": ["system:consciousness"],
                **(provenance_extra or {}),
            },
        }

        if labels:
            node["labels"] = labels

        return node

    @staticmethod
    def emit_awareness_state(
        awareness_level: float,
        focus_target: str,
        attention_distribution: dict[str, float],
    ) -> dict[str, Any]:
        """Emit a consciousness awareness state node"""

        return ConsciousnessMatrizAdapter.create_node(
            node_type="AWARENESS",
            state={
                "confidence": 0.9,
                "salience": awareness_level,
                "urgency": 0.3,
                "novelty": 0.5,
                "awareness": awareness_level,
                **attention_distribution,
            },
            labels=[
                f"awareness:{awareness_level:.2f}",
                f"focus:{focus_target}",
                "consciousness:awareness",
            ],
        )

    @staticmethod
    def emit_decision_point(
        decision_id: str, decision_type: str, confidence: float, alternatives: int
    ) -> dict[str, Any]:
        """Emit a consciousness decision node"""

        return ConsciousnessMatrizAdapter.create_node(
            node_type="DECISION",
            state={
                "confidence": confidence,
                "salience": 0.8,
                "urgency": 0.5,
                "novelty": 0.4,
                "alternatives": float(alternatives),
            },
            labels=[
                f"decision:{decision_id}",
                f"type:{decision_type}",
                f"alternatives:{alternatives}",
                "consciousness:decision",
            ],
        )

    @staticmethod
    def emit_dream_state(dream_id: str, lucidity: float, coherence: float, emotional_tone: float) -> dict[str, Any]:
        """Emit a dream consciousness state node"""

        return ConsciousnessMatrizAdapter.create_node(
            node_type="AWARENESS",
            state={
                "confidence": 0.7,
                "salience": lucidity,
                "urgency": 0.1,
                "novelty": 0.8,
                "lucidity": lucidity,
                "coherence": coherence,
                "emotional_tone": emotional_tone,
            },
            labels=[
                f"dream:{dream_id}",
                f"lucidity:{lucidity:.2f}",
                "consciousness:dream",
            ],
        )

    @staticmethod
    def emit_metacognition_event(
        metacognition_type: str, self_awareness: float, reflection_depth: int
    ) -> dict[str, Any]:
        """Emit a metacognitive awareness event"""

        return ConsciousnessMatrizAdapter.create_node(
            node_type="CAUSAL",
            state={
                "confidence": 0.85,
                "salience": self_awareness,
                "urgency": 0.3,
                "novelty": 0.7,
                "self_awareness": self_awareness,
                "reflection_depth": float(reflection_depth),
            },
            labels=[
                f"metacognition:{metacognition_type}",
                f"depth:{reflection_depth}",
                "consciousness:metacognition",
            ],
        )

    @staticmethod
    def emit_stream_of_consciousness(
        stream_id: str, flow_rate: float, coherence: float, thought_count: int
    ) -> dict[str, Any]:
        """Emit a stream of consciousness event"""

        return ConsciousnessMatrizAdapter.create_node(
            node_type="TEMPORAL",
            state={
                "confidence": 0.8,
                "salience": 0.6,
                "urgency": flow_rate,
                "novelty": 0.5,
                "flow_rate": flow_rate,
                "coherence": coherence,
                "thought_count": float(thought_count),
            },
            labels=[
                f"stream:{stream_id}",
                f"thoughts:{thought_count}",
                "consciousness:stream",
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
            output_dir = Path("memory/inbox/consciousness")

        output_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{node['id']}_{int(time.time())}.json"
        filepath = output_dir / filename

        with open(filepath, "w") as f:
            json.dump(node, f, indent=2)

        return filepath
