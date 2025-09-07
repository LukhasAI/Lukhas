"""
Decision Audit Engine for LUKHAS
====================================

This module provides decision auditing and embedding capabilities
for tracking and analyzing system decisions within the LUKHAS framework.
"""
import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Optional


@dataclass
class AuditDecision:
    """Represents an auditable decision made by the system"""

    decision_id: str
    timestamp: datetime
    decision_type: str
    input_data: dict[str, Any]
    output_data: dict[str, Any]
    confidence: float
    reasoning: str
    system_state: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


class DecisionAuditEngine:
    """
    Engine for auditing and embedding system decisions.

    This class provides functionality to:
    - Track system decisions with full context
    - Generate embeddings for decision analysis
    - Store and retrieve decision history
    - Analyze decision patterns
    """

    def __init__(self, audit_path: str = "audit_decisions.jsonl"):
        self.audit_path = audit_path
        self.decision_history: list[AuditDecision] = []
        self.embeddings_cache: dict[str, list[float]] = {}

    def audit_decision(
        self,
        decision_type: str,
        input_data: dict[str, Any],
        output_data: dict[str, Any],
        confidence: float,
        reasoning: str,
        system_state: Optional[dict[str, Any]] = None,
    ) -> AuditDecision:
        """
        Audit a system decision with full context.

        Args:
            decision_type: Type of decision made
            input_data: Input data that led to the decision
            output_data: Output/result of the decision
            confidence: Confidence score (0-1)
            reasoning: Explanation of the decision
            system_state: Optional system state at decision time

        Returns:
            AuditDecision object
        """
        # Generate unique decision ID
        decision_id = self._generate_decision_id(decision_type, input_data, datetime.now(timezone.utc))

        # Create audit decision
        decision = AuditDecision(
            decision_id=decision_id,
            timestamp=datetime.now(timezone.utc),
            decision_type=decision_type,
            input_data=input_data,
            output_data=output_data,
            confidence=confidence,
            reasoning=reasoning,
            system_state=system_state,
        )

        # Store decision
        self.decision_history.append(decision)
        self._persist_decision(decision)

        return decision

    def generate_embedding(self, decision: AuditDecision) -> list[float]:
        """
        Generate an embedding vector for a decision.

        This is a simplified embedding generator. In production,
        this would use a proper embedding model.

        Args:
            decision: The decision to embed

        Returns:
            Embedding vector
        """
        # Check cache
        if decision.decision_id in self.embeddings_cache:
            return self.embeddings_cache[decision.decision_id]

        # Generate simple embedding based on decision properties
        embedding = []

        # Add type-based features
        type_hash = hash(decision.decision_type) % 1000 / 1000.0
        embedding.append(type_hash)

        # Add confidence
        embedding.append(decision.confidence)

        # Add input complexity
        input_complexity = len(str(decision.input_data)) / 1000.0
        embedding.append(min(input_complexity, 1.0))

        # Add output complexity
        output_complexity = len(str(decision.output_data)) / 1000.0
        embedding.append(min(output_complexity, 1.0))

        # Add temporal feature
        hour_feature = decision.timestamp.hour / 24.0
        embedding.append(hour_feature)

        # Pad to standard size
        while len(embedding) < 10:
            embedding.append(0.0)

        # Cache embedding
        self.embeddings_cache[decision.decision_id] = embedding

        return embedding

    def analyze_decisions(self, decision_type: Optional[str] = None) -> dict[str, Any]:
        """
        Analyze decision patterns.

        Args:
            decision_type: Optional filter by decision type

        Returns:
            Analysis results
        """
        # Filter decisions
        decisions = self.decision_history
        if decision_type:
            decisions = [d for d in decisions if d.decision_type == decision_type]

        if not decisions:
            return {"error": "No decisions found"}

        # Calculate statistics
        total_decisions = len(decisions)
        avg_confidence = sum(d.confidence for d in decisions) / total_decisions

        # Group by type
        type_counts = {}
        for decision in decisions:
            type_counts[decision.decision_type] = type_counts.get(decision.decision_type, 0) + 1

        # Time distribution
        hour_distribution = [0] * 24
        for decision in decisions:
            hour_distribution[decision.timestamp.hour] += 1

        return {
            "total_decisions": total_decisions,
            "average_confidence": avg_confidence,
            "type_distribution": type_counts,
            "hourly_distribution": hour_distribution,
            "latest_decision": decisions[-1].to_dict() if decisions else None,
        }

    def _generate_decision_id(self, decision_type: str, input_data: dict[str, Any], timestamp: datetime) -> str:
        """Generate a unique decision ID"""
        content = f"{decision_type}:{json.dumps(input_data, sort_keys=True)}:{timestamp.isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _persist_decision(self, decision: AuditDecision):
        """Persist decision to audit log"""
        try:
            with open(self.audit_path, "a") as f:
                f.write(json.dumps(decision.to_dict()) + "\n")
        except Exception as e:
            # In production, this would use proper logging
            print(f"Failed to persist decision: {e}")

    def load_history(self):
        """Load decision history from audit log"""
        try:
            with open(self.audit_path) as f:
                for line in f:
                    data = json.loads(line.strip())
                    data["timestamp"] = datetime.fromisoformat(data["timestamp"])
                    decision = AuditDecision(**data)
                    self.decision_history.append(decision)
        except FileNotFoundError:
            # No existing audit log
            pass
        except Exception as e:
            print(f"Failed to load audit history: {e}")
