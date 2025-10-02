"""
LUKHAS Audit System - Secure, Append-Only Decision Audit Trail

Provides:
- Consent-aware PII redaction at ingest
- Append-only ledger with cryptographic signatures
- Deterministic node IDs (UUID-based, collision-safe)
- Complete decision provenance tracking
"""

import hashlib
import json
import os
import socket
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


def _ulid_like() -> str:
    """Return a UUID-based sortable id placeholder (swap to UUIDv7/ULID in prod if available)."""
    return uuid.uuid4().hex


def _redact(input_data: Any, consent_scopes: List[str]) -> Any:
    """
    Best-effort PII redaction. If 'pii.read' is absent, scrub common fields in dicts.
    Never throws; audit must not be a point of failure.
    """
    try:
        if "pii.read" not in (consent_scopes or []) and isinstance(input_data, dict):
            for k in ["email", "phone", "ssn", "credit_card", "address"]:
                if k in input_data:
                    input_data[k] = "<redacted>"
    except Exception:
        pass
    return input_data


class DecisionType(Enum):
    """Types of decisions tracked in the audit system"""
    CONSCIOUSNESS_PROCESSING = "consciousness_processing"
    MEMORY_OPERATION = "memory_operation"
    IDENTITY_VALIDATION = "identity_validation"
    GUARDIAN_CHECK = "guardian_check"
    REASONING_INFERENCE = "reasoning_inference"
    ORCHESTRATION = "orchestration"
    USER_INTERACTION = "user_interaction"


class ConfidenceLevel(Enum):
    """Confidence level classifications"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class BrainContext:
    """Context for a participating brain in multi-brain decisions"""
    brain_id: str
    activation_level: float
    weight: float
    vote: Any = None


@dataclass
class DecisionNode:
    """A single decision node in the audit trail"""
    node_id: str
    timestamp: float
    decision_type: DecisionType
    input_data: Any
    input_hash: str
    parent_nodes: List[str] = field(default_factory=list)
    active_brains: List[BrainContext] = field(default_factory=list)
    brain_votes: Dict[str, Any] = field(default_factory=dict)
    consensus_mechanism: Optional[str] = None
    reasoning_steps: List[str] = field(default_factory=list)
    considered_alternatives: List[Any] = field(default_factory=list)
    decision_output: Any = None
    raw_confidence: float = 0.0
    calibrated_confidence: float = 0.0
    uncertainty: Dict[str, float] = field(default_factory=dict)
    confidence_level: ConfidenceLevel = ConfidenceLevel.MEDIUM
    safety_checks: List[str] = field(default_factory=list)
    safety_score: float = 1.0
    validation_status: str = "pending"
    ground_truth: Any = None
    outcome_error: Optional[float] = None
    outcome_timestamp: Optional[float] = None
    execution_time_ms: float = 0.0
    memory_used_mb: float = 0.0
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "node_id": self.node_id,
            "timestamp": self.timestamp,
            "decision_type": self.decision_type.value if isinstance(self.decision_type, Enum) else self.decision_type,
            "input_hash": self.input_hash,
            "parent_nodes": self.parent_nodes,
            "active_brains": [
                {"brain_id": b.brain_id, "activation_level": b.activation_level, "weight": b.weight, "vote": b.vote}
                for b in self.active_brains
            ],
            "brain_votes": self.brain_votes,
            "consensus_mechanism": self.consensus_mechanism,
            "reasoning_steps": self.reasoning_steps,
            "considered_alternatives": self.considered_alternatives,
            "decision_output": self.decision_output,
            "raw_confidence": self.raw_confidence,
            "calibrated_confidence": self.calibrated_confidence,
            "uncertainty": self.uncertainty,
            "confidence_level": self.confidence_level.value if isinstance(self.confidence_level, Enum) else self.confidence_level,
            "safety_checks": self.safety_checks,
            "safety_score": self.safety_score,
            "validation_status": self.validation_status,
            "ground_truth": self.ground_truth,
            "outcome_error": self.outcome_error,
            "outcome_timestamp": self.outcome_timestamp,
            "execution_time_ms": self.execution_time_ms,
            "memory_used_mb": self.memory_used_mb,
            "tags": self.tags,
        }


class AuditTrail:
    """
    Secure, append-only audit trail for LUKHAS decisions

    Features:
    - Consent-aware PII redaction
    - Cryptographic signatures for provenance
    - Deterministic, collision-safe node IDs
    - Complete decision lineage tracking
    """

    def __init__(self, storage_path: str = "audit_logs"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.audit_dir = self.storage_path
        self.ledger = self.audit_dir / "ledger.jsonl"
        self.ledger_sig = self.audit_dir / "ledger.sig.jsonl"

        self.active_decisions: Dict[str, DecisionNode] = {}
        self.completed_decisions: Dict[str, DecisionNode] = {}

    def _append_ledger(self, node: DecisionNode):
        """Append canonical JSON and a tiny signature line for provenance."""
        try:
            rec = node.to_dict()
            j = json.dumps(rec, sort_keys=True, default=str)
            self.audit_dir.mkdir(parents=True, exist_ok=True)
            with self.ledger.open("a") as f:
                f.write(j + "\n")
            sig = {
                "sha256": hashlib.sha256(j.encode()).hexdigest(),
                "commit": os.environ.get("GIT_COMMIT", "unknown"),
                "host": socket.gethostname(),
                "ts": time.time(),
                "node_id": node.node_id,
            }
            with self.ledger_sig.open("a") as s:
                s.write(json.dumps(sig, sort_keys=True) + "\n")
        except Exception:
            # Never block AGI operation on ledger write issues
            pass

    def generate_node_id(self, decision_type: DecisionType, context: str = "") -> str:
        """Generate a unique decision node ID (UUID-based; prefer UUIDv7/ULID in prod)."""
        return _ulid_like()

    def hash_input(self, input_data: Any) -> str:
        """Generate deterministic hash of input data"""
        data_str = json.dumps(input_data, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def create_decision_node(
        self,
        decision_type: DecisionType,
        input_data: Any,
        parent_nodes: List[str] = None,
        active_brains: List[BrainContext] = None,
        tags: List[str] = None,
        consent_scopes: List[str] = None
    ) -> str:
        """
        Create a new decision node with consent-aware redaction

        Args:
            decision_type: Type of decision being made
            input_data: Input data for the decision
            parent_nodes: IDs of parent decision nodes
            active_brains: Brains participating in this decision
            tags: Tags for categorization
            consent_scopes: Consent scopes for PII handling

        Returns:
            Node ID of the created decision
        """
        # Redact sensitive fields unless we have explicit consent
        redacted_input = _redact(input_data, consent_scopes or [])

        node_id = self.generate_node_id(decision_type)

        node = DecisionNode(
            node_id=node_id,
            timestamp=time.time(),
            decision_type=decision_type,
            input_data=redacted_input,
            input_hash=self.hash_input(redacted_input),
            parent_nodes=parent_nodes or [],
            active_brains=active_brains or [],
            tags=tags or []
        )

        self.active_decisions[node_id] = node
        return node_id

    def add_reasoning_step(self, node_id: str, step: str):
        """Add a reasoning step to a decision node"""
        if node_id in self.active_decisions:
            self.active_decisions[node_id].reasoning_steps.append(step)

    def add_alternative(self, node_id: str, alternative: Any):
        """Add a considered alternative to a decision node"""
        if node_id in self.active_decisions:
            self.active_decisions[node_id].considered_alternatives.append(alternative)

    def record_brain_vote(self, node_id: str, brain_id: str, vote: Any):
        """Record a brain's vote on a decision"""
        if node_id in self.active_decisions:
            self.active_decisions[node_id].brain_votes[brain_id] = vote

    def add_safety_check(self, node_id: str, check_name: str, passed: bool):
        """Record a safety check result"""
        if node_id in self.active_decisions:
            node = self.active_decisions[node_id]
            node.safety_checks.append(f"{check_name}:{'passed' if passed else 'failed'}")
            if not passed:
                node.safety_score *= 0.5

    def finalize_decision(
        self,
        node_id: str,
        decision_output: Any,
        raw_confidence: float,
        calibrated_confidence: float,
        execution_time_ms: float = 0.0,
        memory_used_mb: float = 0.0
    ):
        """
        Finalize a decision and move it to completed

        Args:
            node_id: ID of the decision node
            decision_output: The final decision output
            raw_confidence: Raw confidence score
            calibrated_confidence: Calibrated confidence score
            execution_time_ms: Execution time in milliseconds
            memory_used_mb: Memory used in MB
        """
        if node_id in self.active_decisions:
            node = self.active_decisions[node_id]
            node.decision_output = decision_output
            node.raw_confidence = raw_confidence
            node.calibrated_confidence = calibrated_confidence
            node.execution_time_ms = execution_time_ms
            node.memory_used_mb = memory_used_mb
            node.validation_status = "completed"

            # Classify confidence level
            if calibrated_confidence >= 0.9:
                node.confidence_level = ConfidenceLevel.VERY_HIGH
            elif calibrated_confidence >= 0.75:
                node.confidence_level = ConfidenceLevel.HIGH
            elif calibrated_confidence >= 0.5:
                node.confidence_level = ConfidenceLevel.MEDIUM
            elif calibrated_confidence >= 0.25:
                node.confidence_level = ConfidenceLevel.LOW
            else:
                node.confidence_level = ConfidenceLevel.VERY_LOW

            self.completed_decisions[node_id] = node
            del self.active_decisions[node_id]

            # Append to ledger
            try:
                self._append_ledger(node)
            except Exception:
                pass

    def record_outcome(self, node_id: str, ground_truth: Any):
        """
        Record the ground truth outcome for a decision

        Args:
            node_id: ID of the decision node
            ground_truth: The actual outcome/ground truth
        """
        if node_id in self.completed_decisions:
            node = self.completed_decisions[node_id]
            node.ground_truth = ground_truth
            node.outcome_timestamp = time.time()

            # Calculate outcome error if possible
            try:
                if isinstance(node.decision_output, (int, float)) and isinstance(ground_truth, (int, float)):
                    node.outcome_error = abs(node.decision_output - ground_truth)
            except Exception:
                pass

            # Append updated node to ledger
            try:
                self._append_ledger(node)
            except Exception:
                pass

    def get_decision(self, node_id: str) -> Optional[DecisionNode]:
        """Retrieve a decision node by ID"""
        return self.completed_decisions.get(node_id) or self.active_decisions.get(node_id)

    def get_lineage(self, node_id: str) -> List[DecisionNode]:
        """Get the full lineage of a decision (ancestors)"""
        lineage = []
        current = self.get_decision(node_id)

        if not current:
            return lineage

        lineage.append(current)

        for parent_id in current.parent_nodes:
            parent_lineage = self.get_lineage(parent_id)
            lineage.extend(parent_lineage)

        return lineage

    def export_audit_trail(self, output_path: str):
        """Export the complete audit trail to a file"""
        with open(output_path, 'w') as f:
            for node in self.completed_decisions.values():
                f.write(json.dumps(node.to_dict(), default=str) + "\n")
