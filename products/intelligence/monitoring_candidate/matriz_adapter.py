"""
MATRIZ Adapter for Monitoring Module
Emits MATRIZ-compliant nodes for monitoring events
"""

import json
import time
import uuid
from pathlib import Path
from typing import Any, Optional


class MonitoringMatrizAdapter:
    """Adapter to emit MATRIZ nodes for monitoring events"""

    SCHEMA_REF = "lukhas://schemas/matriz_node_v1.json"

    @staticmethod
    def create_node(
        node_type: str,
        state: dict[str, float],
        labels: Optional[list[str]] = None,
        provenance_extra: Optional[dict] = None,
    ) -> dict[str, Any]:
        """Create a MATRIZ-compliant node for monitoring events"""

        node = {
            "version": 1,
            "id": f"LT-MON-{uuid.uuid4().hex[:8]}",
            "type": node_type,
            "state": {
                "confidence": state.get("confidence", 0.8),
                "salience": state.get("salience", 0.5),
                "urgency": state.get("urgency", 0.2),
                "novelty": state.get("novelty", 0.3),
                **state,
            },
            "timestamps": {"created_ts": int(time.time() * 1000)},
            "provenance": {
                "producer": "lukhas.monitoring",
                "capabilities": [
                    "monitoring:metrics",
                    "monitoring:drift",
                    "monitoring:alert",
                ],
                "tenant": "system",
                "trace_id": f"LT-MON-{int(time.time())}",
                "consent_scopes": ["system:monitoring"],
                **(provenance_extra or {}),
            },
        }

        if labels:
            node["labels"] = labels

        return node

    @staticmethod
    def emit_drift_detection(drift_score: float, component: str, threshold: float = 0.15) -> dict[str, Any]:
        """Emit a drift detection node"""

        urgency = min(1.0, drift_score / threshold) if drift_score > threshold else 0.0

        return MonitoringMatrizAdapter.create_node(
            node_type="AWARENESS",
            state={
                "confidence": 0.95,
                "salience": min(1.0, drift_score * 2),
                "urgency": urgency,
                "novelty": 0.1,
                "drift_score": drift_score,
                "threshold": threshold,
            },
            labels=[
                f"monitoring:drift={drift_score:.3f}",
                f"component:{component}",
                "alert:drift" if drift_score > threshold else "status:normal",
            ],
        )

    @staticmethod
    def emit_performance_metric(
        metric_name: str, value: float, unit: str = "ms", target: Optional[float] = None
    ) -> dict[str, Any]:
        """Emit a performance metric node"""

        labels = [f"metric:{metric_name}", f"unit:{unit}"]

        if target:
            labels.append(f"target:{target}{unit}")
            performance_ratio = value / target if target > 0 else 1.0
            urgency = max(0, min(1.0, performance_ratio - 1.0))
        else:
            urgency = 0.0

        return MonitoringMatrizAdapter.create_node(
            node_type="TEMPORAL",
            state={
                "confidence": 1.0,
                "salience": 0.3,
                "urgency": urgency,
                "novelty": 0.0,
                "value": value,
            },
            labels=labels,
        )

    @staticmethod
    def emit_health_check(component: str, status: str, details: Optional[dict] = None) -> dict[str, Any]:
        """Emit a health check node"""

        status_urgency = {
            "healthy": 0.0,
            "degraded": 0.5,
            "unhealthy": 0.9,
            "critical": 1.0,
        }

        return MonitoringMatrizAdapter.create_node(
            node_type="AWARENESS",
            state={
                "confidence": 1.0,
                "salience": 0.4,
                "urgency": status_urgency.get(status, 0.5),
                "novelty": 0.0,
                **(details or {}),
            },
            labels=[f"health:{status}", f"component:{component}", "monitoring:health"],
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
            output_dir = Path("memory/inbox/monitoring")

        output_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{node['id']}_{int(time.time())}.json"
        filepath = output_dir / filename

        with open(filepath, "w") as f:
            json.dump(node, f, indent=2)

        return filepath


# Example usage functions for existing monitoring code
def wrap_drift_detection(original_func):
    """Decorator to add MATRIZ emission to drift detection"""

    def wrapper(*args, **kwargs):
        result = original_func(*args, **kwargs)

        # Extract drift score from result (adapt based on actual function)
        if isinstance(result, dict) and "drift_score" in result:
            node = MonitoringMatrizAdapter.emit_drift_detection(
                drift_score=result["drift_score"],
                component=result.get("component", "unknown"),
            )
            MonitoringMatrizAdapter.save_node(node)

        return result

    return wrapper


def wrap_metric_collection(original_func):
    """Decorator to add MATRIZ emission to metric collection"""

    def wrapper(*args, **kwargs):
        result = original_func(*args, **kwargs)

        # Extract metrics from result (adapt based on actual function)
        if isinstance(result, dict):
            for metric_name, value in result.items():
                if isinstance(value, (int, float)):
                    node = MonitoringMatrizAdapter.emit_performance_metric(metric_name=metric_name, value=value)
                    MonitoringMatrizAdapter.save_node(node)

        return result

    return wrapper
