"""
MATRIZ Adapter for Memory Module
Emits MATRIZ-compliant nodes for memory and fold events
"""

import json
import time
import uuid
from pathlib import Path
from typing import Any, Optional


class MemoryMatrizAdapter:
    """Adapter to emit MATRIZ nodes for memory system events"""

    SCHEMA_REF = "lukhas://schemas/matriz_node_v1.json"

    @staticmethod
    def create_node(
        node_type: str,
        state: dict[str, float],
        labels: Optional[list[str]] = None,
        provenance_extra: Optional[dict] = None,
    ) -> dict[str, Any]:
        """Create a MATRIZ-compliant node for memory events"""

        node = {
            "version": 1,
            "id": f"LT-MEM-{uuid.uuid4().hex[:8]}",
            "type": node_type,
            "state": {
                "confidence": state.get("confidence", 0.9),
                "salience": state.get("salience", 0.7),
                "urgency": state.get("urgency", 0.3),
                "novelty": state.get("novelty", 0.5),
                **state,
            },
            "timestamps": {"created_ts": int(time.time() * 1000)},
            "provenance": {
                "producer": "lukhas.memory",
                "capabilities": ["memory:fold", "memory:recall", "memory:cascade"],
                "tenant": "system",
                "trace_id": f"LT-MEM-{int(time.time())}",
                "consent_scopes": ["system:memory"],
                **(provenance_extra or {}),
            },
        }

        if labels:
            node["labels"] = labels

        return node

    @staticmethod
    def emit_fold_creation(
        fold_id: str, fold_type: str, depth: int, emotional_valence: float = 0.0
    ) -> dict[str, Any]:
        """Emit a memory fold creation event"""

        return MemoryMatrizAdapter.create_node(
            node_type="TEMPORAL",
            state={
                "confidence": 0.95,
                "salience": 0.7,
                "urgency": 0.2,
                "novelty": 0.6,
                "depth": float(depth),
                "emotional_valence": emotional_valence,
            },
            labels=[
                f"fold:{fold_id}",
                f"type:{fold_type}",
                f"depth:{depth}",
                "memory:fold",
            ],
        )

    @staticmethod
    def emit_recall_event(
        memory_id: str, recall_accuracy: float, latency_ms: int, fold_count: int
    ) -> dict[str, Any]:
        """Emit a memory recall event"""

        return MemoryMatrizAdapter.create_node(
            node_type="DECISION",
            state={
                "confidence": recall_accuracy,
                "salience": 0.8,
                "urgency": 0.3,
                "novelty": 0.2,
                "accuracy": recall_accuracy,
                "latency_ms": float(latency_ms),
                "fold_count": float(fold_count),
            },
            labels=[f"memory:{memory_id[:8]}", f"folds:{fold_count}", "memory:recall"],
        )

    @staticmethod
    def emit_cascade_prevention(
        cascade_id: str, prevention_success: bool, affected_folds: int
    ) -> dict[str, Any]:
        """Emit a cascade prevention event (99.7% success rate)"""

        urgency = 0.1 if prevention_success else 0.9

        return MemoryMatrizAdapter.create_node(
            node_type="CAUSAL",
            state={
                "confidence": 0.997,  # 99.7% cascade prevention rate
                "salience": 0.9,
                "urgency": urgency,
                "novelty": 0.3,
                "prevented": 1.0 if prevention_success else 0.0,
                "affected_folds": float(affected_folds),
            },
            labels=[
                f"cascade:{cascade_id}",
                "status:prevented" if prevention_success else "status:cascaded",
                f"folds_affected:{affected_folds}",
                "memory:cascade",
            ],
        )

    @staticmethod
    def emit_dream_state(
        dream_id: str, coherence: float, memory_integration: float, fold_depth: int
    ) -> dict[str, Any]:
        """Emit a dream state memory consolidation event"""

        return MemoryMatrizAdapter.create_node(
            node_type="AWARENESS",
            state={
                "confidence": 0.8,
                "salience": coherence,
                "urgency": 0.2,
                "novelty": 0.7,
                "coherence": coherence,
                "integration": memory_integration,
                "fold_depth": float(fold_depth),
            },
            labels=[f"dream:{dream_id}", f"coherence:{coherence:.2f}", "memory:dream"],
        )

    @staticmethod
    def emit_memory_consolidation(
        consolidation_id: str, memories_merged: int, compression_ratio: float
    ) -> dict[str, Any]:
        """Emit a memory consolidation event"""

        return MemoryMatrizAdapter.create_node(
            node_type="TEMPORAL",
            state={
                "confidence": 0.9,
                "salience": 0.6,
                "urgency": 0.2,
                "novelty": 0.4,
                "memories_merged": float(memories_merged),
                "compression_ratio": compression_ratio,
            },
            labels=[
                f"consolidation:{consolidation_id}",
                f"merged:{memories_merged}",
                "memory:consolidation",
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
            output_dir = Path("memory/inbox/memory")

        output_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{node['id']}_{int(time.time())}.json"
        filepath = output_dir / filename

        with open(filepath, "w") as f:
            json.dump(node, f, indent=2)

        return filepath
