"""
MATRIZ Adapter for Bio Module
Emits MATRIZ-compliant nodes for bio-inspired processing events
"""
import streamlit as st

import json
import time
import uuid
from pathlib import Path
from typing import Any, Optional


class BioMatrizAdapter:
    """Adapter to emit MATRIZ nodes for bio-inspired events"""

    SCHEMA_REF = "lukhas://schemas/matriz_node_v1.json"

    @staticmethod
    def create_node(
        node_type: str,
        state: dict[str, float],
        labels: Optional[list[str]] = None,
        provenance_extra: Optional[dict] = None,
    ) -> dict[str, Any]:
        """Create a MATRIZ-compliant node for bio events"""

        node = {
            "version": 1,
            "id": f"LT-BIO-{uuid.uuid4().hex[:8]}",
            "type": node_type,
            "state": {
                "confidence": state.get("confidence", 0.75),
                "salience": state.get("salience", 0.5),
                "urgency": state.get("urgency", 0.3),
                "novelty": state.get("novelty", 0.6),
                **state,
            },
            "timestamps": {"created_ts": int(time.time() * 1000)},
            "provenance": {
                "producer": "lukhas.bio",
                "capabilities": ["bio:oscillate", "bio:quantum", "bio:adapt"],
                "tenant": "system",
                "trace_id": f"LT-BIO-{int(time.time())}",
                "consent_scopes": ["system:bio"],
                **(provenance_extra or {}),
            },
        }

        if labels:
            node["labels"] = labels

        return node

    @staticmethod
    def emit_oscillator_state(
        frequency: float,
        amplitude: float,
        phase: float,
        oscillator_type: str = "neural",
    ) -> dict[str, Any]:
        """Emit an oscillator state node"""

        return BioMatrizAdapter.create_node(
            node_type="TEMPORAL",
            state={
                "confidence": 0.9,
                "salience": amplitude,
                "urgency": 0.2,
                "novelty": 0.4,
                "frequency": frequency,
                "amplitude": amplitude,
                "phase": phase,
            },
            labels=[
                f"bio:oscillator:{oscillator_type}",
                f"frequency:{frequency:.2f}Hz",
            ],
        )

    @staticmethod
    def emit_quantum_coherence(
        coherence_score: float, entanglement_level: float, system: str = "default"
    ) -> dict[str, Any]:
        """Emit a quantum-inspired coherence node"""

        return BioMatrizAdapter.create_node(
            node_type="AWARENESS",
            state={
                "confidence": 0.7,
                "salience": coherence_score,
                "urgency": max(0, 1.0 - coherence_score),
                "novelty": 0.7,
                "coherence": coherence_score,
                "entanglement": entanglement_level,
            },
            labels=[
                "bio:quantum",
                f"coherence:{coherence_score:.2f}",
                f"system:{system}",
            ],
        )

    @staticmethod
    def emit_adaptation_event(
        adaptation_type: str,
        fitness_before: float,
        fitness_after: float,
        mutation_rate: float = 0.01,
    ) -> dict[str, Any]:
        """Emit a bio-inspired adaptation event node"""

        improvement = fitness_after - fitness_before

        return BioMatrizAdapter.create_node(
            node_type="DECISION",
            state={
                "confidence": 0.8,
                "salience": abs(improvement),
                "urgency": 0.4,
                "novelty": mutation_rate * 10,
                "fitness_before": fitness_before,
                "fitness_after": fitness_after,
                "improvement": improvement,
                "mutation_rate": mutation_rate,
            },
            labels=[
                f"bio:adaptation:{adaptation_type}",
                "improvement:positive" if improvement > 0 else "improvement:negative",
            ],
        )

    @staticmethod
    def emit_awareness_pulse(awareness_level: float, sensory_inputs: dict[str, float]) -> dict[str, Any]:
        """Emit a bio-awareness pulse node"""

        avg_sensory = sum(sensory_inputs.values()) / len(sensory_inputs) if sensory_inputs else 0

        return BioMatrizAdapter.create_node(
            node_type="AWARENESS",
            state={
                "confidence": 0.85,
                "salience": awareness_level,
                "urgency": 0.3,
                "novelty": 0.5,
                "awareness": awareness_level,
                "sensory_avg": avg_sensory,
                **sensory_inputs,
            },
            labels=["bio:awareness", f"level:{awareness_level:.2f}"],
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
            output_dir = Path("memory/inbox/bio")

        output_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{node['id']}_{int(time.time())}.json"
        filepath = output_dir / filename

        with open(filepath, "w") as f:
            json.dump(node, f, indent=2)

        return filepath
