"""
MATRIZ Adapter for Compliance Module
Emits MATRIZ-compliant nodes for compliance and regulatory events
"""

import json
import time
import uuid
from pathlib import Path
from typing import Any, Optional


class ComplianceMatrizAdapter:
    """Adapter to emit MATRIZ nodes for compliance events"""

    SCHEMA_REF = "lukhas://schemas/matriz_node_v1.json"

    @staticmethod
    def create_node(
        node_type: str,
        state: dict[str, float],
        labels: Optional[list[str]] = None,
        provenance_extra: Optional[dict] = None,
    ) -> dict[str, Any]:
        """Create a MATRIZ-compliant node for compliance events"""

        node = {
            "version": 1,
            "id": f"LT-COMP-{uuid.uuid4().hex[:8]}",
            "type": node_type,
            "state": {
                "confidence": state.get("confidence", 0.95),
                "salience": state.get("salience", 0.7),
                "urgency": state.get("urgency", 0.5),
                "novelty": state.get("novelty", 0.2),
                **state,
            },
            "timestamps": {"created_ts": int(time.time() * 1000)},
            "provenance": {
                "producer": "compliance",
                "capabilities": [
                    "compliance:validate",
                    "compliance:audit",
                    "compliance:consent",
                ],
                "tenant": "system",
                "trace_id": f"LT-COMP-{int(time.time())}",
                "consent_scopes": ["system:compliance", "system:audit"],
                **(provenance_extra or {}),
            },
        }

        if labels:
            node["labels"] = labels

        return node

    @staticmethod
    def emit_compliance_check(regulation: str, status: str, violations: Optional[list[str]] = None) -> dict[str, Any]:
        """Emit a compliance validation node"""

        is_compliant = status == "compliant"
        urgency = 0.0 if is_compliant else 0.9

        labels = [f"compliance:{regulation}", f"status:{status}"]

        if violations:
            labels.extend([f"violation:{v}" for v in violations[:3]])

        return ComplianceMatrizAdapter.create_node(
            node_type="DECISION",
            state={
                "confidence": 0.95,
                "salience": 0.8,
                "urgency": urgency,
                "novelty": 0.1,
                "compliant": 1.0 if is_compliant else 0.0,
                "violation_count": len(violations) if violations else 0,
            },
            labels=labels,
        )

    @staticmethod
    def emit_consent_verification(user_id: str, action: str, consent_given: bool, scope: str) -> dict[str, Any]:
        """Emit a consent verification node"""

        return ComplianceMatrizAdapter.create_node(
            node_type="DECISION",
            state={
                "confidence": 1.0,
                "salience": 0.9,
                "urgency": 0.0 if consent_given else 1.0,
                "novelty": 0.1,
                "consent": 1.0 if consent_given else 0.0,
            },
            labels=[
                f"consent:{scope}",
                f"action:{action}",
                "consent:granted" if consent_given else "consent:denied",
            ],
            provenance_extra={"user_id": user_id},
        )

    @staticmethod
    def emit_audit_event(event_type: str, entity: str, action: str, risk_level: str = "low") -> dict[str, Any]:
        """Emit an audit trail node"""

        risk_urgency = {"low": 0.1, "medium": 0.5, "high": 0.8, "critical": 1.0}

        return ComplianceMatrizAdapter.create_node(
            node_type="TEMPORAL",
            state={
                "confidence": 1.0,
                "salience": 0.6,
                "urgency": risk_urgency.get(risk_level, 0.5),
                "novelty": 0.2,
            },
            labels=[
                f"audit:{event_type}",
                f"entity:{entity}",
                f"action:{action}",
                f"risk:{risk_level}",
            ],
        )

    @staticmethod
    def emit_gdpr_compliance(data_type: str, purpose: str, lawful_basis: str, retention_days: int) -> dict[str, Any]:
        """Emit a GDPR compliance node"""

        return ComplianceMatrizAdapter.create_node(
            node_type="DECISION",
            state={
                "confidence": 0.9,
                "salience": 0.7,
                "urgency": 0.3,
                "novelty": 0.1,
                "retention_days": retention_days,
            },
            labels=[
                "compliance:gdpr",
                f"data:{data_type}",
                f"purpose:{purpose}",
                f"basis:{lawful_basis}",
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
            output_dir = Path("memory/inbox/compliance")

        output_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{node['id']}_{int(time.time())}.json"
        filepath = output_dir / filename

        with open(filepath, "w") as f:
            json.dump(node, f, indent=2)

        return filepath
