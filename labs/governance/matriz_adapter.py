"""
MATRIZ Adapter for Governance Module
Emits MATRIZ-compliant nodes for governance, ethics, and guardian events
"""

import json
import time
import uuid
from pathlib import Path
from typing import Any, Optional


class GovernanceMatrizAdapter:
    """Adapter to emit MATRIZ nodes for governance system events"""

    SCHEMA_REF = "lukhas://schemas/matriz_node_v1.json"

    @staticmethod
    def create_node(
        node_type: str,
        state: dict[str, float],
        labels: Optional[list[str]] = None,
        provenance_extra: Optional[dict] = None,
    ) -> dict[str, Any]:
        """Create a MATRIZ-compliant node for governance events"""

        node = {
            "version": 1,
            "id": f"LT-GOV-{uuid.uuid4().hex[:8]}",
            "type": node_type,
            "state": {
                "confidence": state.get("confidence", 0.95),
                "salience": state.get("salience", 0.8),
                "urgency": state.get("urgency", 0.5),
                "novelty": state.get("novelty", 0.3),
                **state,
            },
            "timestamps": {"created_ts": int(time.time() * 1000)},
            "provenance": {
                "producer": "governance",
                "capabilities": [
                    "governance:ethics",
                    "governance:drift",
                    "governance:guardian",
                ],
                "tenant": "system",
                "trace_id": f"LT-GOV-{int(time.time())}",
                "consent_scopes": ["system:governance", "system:ethics"],
                **(provenance_extra or {}),
            },
        }

        if labels:
            node["labels"] = labels

        return node

    @staticmethod
    def emit_ethics_decision(decision_id: str, ethical_score: float, action: str, allowed: bool) -> dict[str, Any]:
        """Emit an ethical decision node"""

        urgency = 0.2 if allowed else 0.9

        return GovernanceMatrizAdapter.create_node(
            node_type="DECISION",
            state={
                "confidence": 0.95,
                "salience": 0.9,
                "urgency": urgency,
                "novelty": 0.2,
                "ethical_score": ethical_score,
                "allowed": 1.0 if allowed else 0.0,
            },
            labels=[
                f"decision:{decision_id}",
                f"action:{action}",
                "status:allowed" if allowed else "status:blocked",
                "governance:ethics",
            ],
        )

    @staticmethod
    def emit_drift_detection(
        drift_id: str,
        drift_score: float,
        threshold: float = 0.15,
        component: str = "unknown",
    ) -> dict[str, Any]:
        """Emit a drift detection event (threshold: 0.15)"""

        is_drifting = drift_score > threshold
        urgency = min(1.0, drift_score / threshold) if is_drifting else 0.1

        return GovernanceMatrizAdapter.create_node(
            node_type="CAUSAL",
            state={
                "confidence": 0.9,
                "salience": drift_score,
                "urgency": urgency,
                "novelty": 0.4,
                "drift_score": drift_score,
                "threshold": threshold,
                "drifting": 1.0 if is_drifting else 0.0,
            },
            labels=[
                f"drift:{drift_id}",
                f"component:{component}",
                f"score:{drift_score:.3f}",
                "status:drifting" if is_drifting else "status:stable",
                "governance:drift",
            ],
        )

    @staticmethod
    def emit_guardian_intervention(
        intervention_id: str, severity: str, action_taken: str, success: bool
    ) -> dict[str, Any]:
        """Emit a Guardian System intervention event"""

        severity_urgency = {"low": 0.3, "medium": 0.5, "high": 0.8, "critical": 1.0}

        return GovernanceMatrizAdapter.create_node(
            node_type="DECISION",
            state={
                "confidence": 1.0,
                "salience": 0.9,
                "urgency": severity_urgency.get(severity, 0.5),
                "novelty": 0.3,
                "success": 1.0 if success else 0.0,
            },
            labels=[
                f"intervention:{intervention_id}",
                f"severity:{severity}",
                f"action:{action_taken}",
                "status:success" if success else "status:failed",
                "governance:guardian",
            ],
        )

    @staticmethod
    def emit_policy_evaluation(
        policy_id: str,
        policy_type: str,
        compliance_score: float,
        violations: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """Emit a policy evaluation event"""

        is_compliant = compliance_score >= 0.8

        labels = [
            f"policy:{policy_id}",
            f"type:{policy_type}",
            f"compliance:{compliance_score:.2f}",
            "governance:policy",
        ]

        if violations:
            labels.extend([f"violation:{v}" for v in violations[:3]])

        return GovernanceMatrizAdapter.create_node(
            node_type="DECISION",
            state={
                "confidence": 0.9,
                "salience": 0.7,
                "urgency": 0.0 if is_compliant else 0.7,
                "novelty": 0.2,
                "compliance": compliance_score,
                "violation_count": len(violations) if violations else 0,
            },
            labels=labels,
        )

    @staticmethod
    def emit_constitutional_check(check_id: str, principle: str, aligned: bool, confidence: float) -> dict[str, Any]:
        """Emit a constitutional AI principle check"""

        return GovernanceMatrizAdapter.create_node(
            node_type="DECISION",
            state={
                "confidence": confidence,
                "salience": 0.85,
                "urgency": 0.0 if aligned else 0.8,
                "novelty": 0.1,
                "aligned": 1.0 if aligned else 0.0,
            },
            labels=[
                f"check:{check_id}",
                f"principle:{principle}",
                "status:aligned" if aligned else "status:misaligned",
                "governance:constitutional",
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
            output_dir = Path("memory/inbox/governance")

        output_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{node['id']}_{int(time.time())}.json"
        filepath = output_dir / filename

        with open(filepath, "w") as f:
            json.dump(node, f, indent=2)

        return filepath
