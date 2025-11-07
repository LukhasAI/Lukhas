"""
LUKHAS Ledger Events v2.0.0
===========================

Immutable event dataclasses for consent ledger event sourcing.
Implements schema v2.0.0 with SHA256 integrity verification and
GDPR/CCPA compliance tracking.
"""

import hashlib
import json
import uuid
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

# Re-import enums from original implementation for compatibility
from ..governance.consent_ledger_impl import ConsentType, DataSubjectRights, PolicyVerdict


class EventType(Enum):
    """Event types for the consent ledger"""
    CONSENT_GRANTED = "consent_granted"
    CONSENT_REVOKED = "consent_revoked"
    CONSENT_CHECKED = "consent_checked"
    TRACE_CREATED = "trace_created"
    DURESS_DETECTED = "duress_detected"
    DATA_SUBJECT_REQUEST = "data_subject_request"
    POLICY_VIOLATION = "policy_violation"


@dataclass(frozen=True)
class ConsentEvent(ABC):
    """
    Base class for all consent ledger events.

    Implements immutable event sourcing with SHA256 integrity verification
    and compliance with schema v2.0.0.
    """
    event_id: str = field(default_factory=lambda: f"EVT-{uuid.uuid4().hex}")
    event_type: EventType = field(init=False)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    schema_version: str = field(default="2.0.0", init=False)
    lid: str = ""  # LUKHAS ID (Lambda ID)
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        # Set event_type based on class name
        event_type_map = {
            "ConsentGrantedEvent": EventType.CONSENT_GRANTED,
            "ConsentRevokedEvent": EventType.CONSENT_REVOKED,
            "ConsentCheckedEvent": EventType.CONSENT_CHECKED,
            "TraceCreatedEvent": EventType.TRACE_CREATED,
            "DuressDetectedEvent": EventType.DURESS_DETECTED,
            "DataSubjectRequestEvent": EventType.DATA_SUBJECT_REQUEST,
            "PolicyViolationEvent": EventType.POLICY_VIOLATION,
        }
        object.__setattr__(self, 'event_type', event_type_map.get(self.__class__.__name__, EventType.TRACE_CREATED))

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary for serialization"""
        data = asdict(self)
        # Convert enums to string values
        for key, value in data.items():
            if hasattr(value, 'value'):
                data[key] = value.value
            elif isinstance(value, list):
                data[key] = [v.value if hasattr(v, 'value') else v for v in value]
        return data

    def to_json(self) -> str:
        """Serialize event to JSON string"""
        return json.dumps(self.to_dict(), sort_keys=True, default=str)

    def compute_hash(self) -> str:
        """Compute SHA256 hash for tamper evidence"""
        content = self.to_json()
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def verify_integrity(self, expected_hash: str) -> bool:
        """Verify event integrity against expected hash"""
        return self.compute_hash() == expected_hash

    @abstractmethod
    def get_aggregate_id(self) -> str:
        """Get the aggregate identifier for this event"""
        pass


@dataclass(frozen=True)
class ConsentGrantedEvent(ConsentEvent):
    """Event fired when consent is granted for data processing"""

    consent_id: str = ""
    resource_type: str = ""
    scopes: list[str] = field(default_factory=list)
    purpose: str = ""
    lawful_basis: str = "consent"
    consent_type: ConsentType = ConsentType.EXPLICIT
    granted_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    expires_at: Optional[str] = None
    data_categories: list[str] = field(default_factory=list)
    third_parties: list[str] = field(default_factory=list)
    processing_locations: list[str] = field(default_factory=list)
    withdrawal_method: str = "api_revoke_consent"
    data_subject_rights: list[DataSubjectRights] = field(default_factory=list)
    retention_period: Optional[int] = None
    automated_decision_making: bool = False
    profiling: bool = False
    children_data: bool = False
    sensitive_data: bool = False
    trace_id: str = ""

    def get_aggregate_id(self) -> str:
        return f"consent:{self.consent_id}"


@dataclass(frozen=True)
class ConsentRevokedEvent(ConsentEvent):
    """Event fired when consent is revoked"""

    consent_id: str = ""
    revoked_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    reason: Optional[str] = None
    revocation_method: str = "api_request"
    cascade_deletions: list[str] = field(default_factory=list)
    trace_id: str = ""

    def get_aggregate_id(self) -> str:
        return f"consent:{self.consent_id}"


@dataclass(frozen=True)
class ConsentCheckedEvent(ConsentEvent):
    """Event fired when consent is checked for an operation"""

    resource_type: str = ""
    action: str = ""
    consent_id: Optional[str] = None
    allowed: bool = False
    reason: Optional[str] = None
    require_step_up: bool = False
    context: dict[str, Any] = field(default_factory=dict)
    trace_id: str = ""

    def get_aggregate_id(self) -> str:
        return f"consent_check:{self.lid}:{self.resource_type}"


@dataclass(frozen=True)
class TraceCreatedEvent(ConsentEvent):
    """Event fired when a Lambda trace is created"""

    trace_id: str = ""
    parent_trace_id: Optional[str] = None
    action: str = ""
    resource: str = ""
    purpose: str = ""
    policy_verdict: PolicyVerdict = PolicyVerdict.DENY
    capability_token_id: Optional[str] = None
    context: dict[str, Any] = field(default_factory=dict)
    explanation_unl: Optional[str] = None
    glyph_signature: Optional[str] = None
    triad_validation: dict[str, bool] = field(default_factory=lambda: {
        "identity_verified": False,
        "consciousness_aligned": False,
        "guardian_approved": False,
    })
    compliance_flags: dict[str, Any] = field(default_factory=dict)
    chain_integrity: Optional[str] = None

    def get_aggregate_id(self) -> str:
        return f"trace:{self.trace_id}"


@dataclass(frozen=True)
class DuressDetectedEvent(ConsentEvent):
    """Event fired when duress/coercion is detected"""

    signal_id: str = field(default_factory=lambda: f"DURESS-{uuid.uuid4().hex}")
    signal_type: str = ""
    detected_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    response_action: str = ""
    severity_level: int = 1
    context_data: dict[str, Any] = field(default_factory=dict)
    trace_id: str = ""

    def get_aggregate_id(self) -> str:
        return f"duress:{self.signal_id}"


@dataclass(frozen=True)
class DataSubjectRequestEvent(ConsentEvent):
    """Event fired when a data subject request is made (GDPR Article 15-22)"""

    request_id: str = field(default_factory=lambda: f"DSR-{uuid.uuid4().hex}")
    request_type: DataSubjectRights = DataSubjectRights.ACCESS
    submitted_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "pending"
    processing_deadline: Optional[str] = None
    response_data: Optional[dict[str, Any]] = None
    trace_id: str = ""

    def get_aggregate_id(self) -> str:
        return f"dsr:{self.request_id}"


@dataclass(frozen=True)
class PolicyViolationEvent(ConsentEvent):
    """Event fired when a policy violation is detected"""

    violation_id: str = field(default_factory=lambda: f"VIOL-{uuid.uuid4().hex}")
    violation_type: str = ""
    detected_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    severity: str = "medium"  # low, medium, high, critical
    violated_policy: str = ""
    context: dict[str, Any] = field(default_factory=dict)
    remediation_action: Optional[str] = None
    trace_id: str = ""

    def get_aggregate_id(self) -> str:
        return f"violation:{self.violation_id}"


# Event factory for creating events from dict/JSON
def create_event_from_dict(event_data: dict[str, Any]) -> ConsentEvent:
    """Create an event instance from dictionary data"""
    event_type_str = event_data.get('event_type', '')

    event_class_map = {
        EventType.CONSENT_GRANTED.value: ConsentGrantedEvent,
        EventType.CONSENT_REVOKED.value: ConsentRevokedEvent,
        EventType.CONSENT_CHECKED.value: ConsentCheckedEvent,
        EventType.TRACE_CREATED.value: TraceCreatedEvent,
        EventType.DURESS_DETECTED.value: DuressDetectedEvent,
        EventType.DATA_SUBJECT_REQUEST.value: DataSubjectRequestEvent,
        EventType.POLICY_VIOLATION.value: PolicyViolationEvent,
    }

    event_class = event_class_map.get(event_type_str)
    if not event_class:
        raise ValueError(f"Unknown event type: {event_type_str}")

    # Convert string values back to enums where needed
    processed_data = {}
    for key, value in event_data.items():
        if key == 'consent_type' and isinstance(value, str):
            try:
                processed_data[key] = ConsentType(value)
            except ValueError:
                processed_data[key] = ConsentType.EXPLICIT
        elif key == 'policy_verdict' and isinstance(value, str):
            try:
                processed_data[key] = PolicyVerdict(value)
            except ValueError:
                processed_data[key] = PolicyVerdict.DENY
        elif key == 'data_subject_rights' and isinstance(value, list):
            processed_data[key] = [DataSubjectRights(right) if isinstance(right, str) else right for right in value]
        elif key == 'request_type' and isinstance(value, str):
            try:
                processed_data[key] = DataSubjectRights(value)
            except ValueError:
                processed_data[key] = DataSubjectRights.ACCESS
        else:
            processed_data[key] = value

    # Remove fields that don't belong to the specific event class
    event_fields = {f.name for f in event_class.__dataclass_fields__.values()}
    filtered_data = {k: v for k, v in processed_data.items() if k in event_fields}

    return event_class(**filtered_data)


def create_event_from_json(json_data: str) -> ConsentEvent:
    """Create an event instance from JSON string"""
    event_data = json.loads(json_data)
    return create_event_from_dict(event_data)


# Event validation functions
def validate_event_schema(event: ConsentEvent) -> bool:
    """Validate event against schema v2.0.0 requirements"""
    try:
        # Basic validations
        if not event.event_id or not event.timestamp or not event.lid:
            return False

        if event.schema_version != "2.0.0":
            return False

        # Type-specific validations
        if isinstance(event, ConsentGrantedEvent):
            return bool(event.consent_id and event.resource_type and event.scopes)
        elif isinstance(event, ConsentRevokedEvent):
            return bool(event.consent_id)
        elif isinstance(event, ConsentCheckedEvent):
            return bool(event.resource_type and event.action)
        elif isinstance(event, TraceCreatedEvent):
            return bool(event.trace_id and event.action and event.resource)
        elif isinstance(event, DuressDetectedEvent):
            return bool(event.signal_type and event.response_action)
        elif isinstance(event, DataSubjectRequestEvent):
            return bool(event.request_id and event.request_type)
        elif isinstance(event, PolicyViolationEvent):
            return bool(event.violation_id and event.violation_type)

        return True

    except Exception:
        return False


def compute_event_chain_hash(events: list[ConsentEvent]) -> str:
    """Compute chain hash for a sequence of events"""
    if not events:
        return ""

    chain_data = ""
    for event in events:
        chain_data += event.compute_hash()

    return hashlib.sha256(chain_data.encode('utf-8')).hexdigest()
