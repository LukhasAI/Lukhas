"""
LUKHAS Event Contracts - Typed events for professional module communication
Replaces direct module calls with well-defined event contracts
"""
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
from typing import Any, Optional


class EventPriority(IntEnum):
    """Event priority levels"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


# Base Event Contract


@dataclass
class DomainEvent(ABC):
    """Base class for all domain events"""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source_module: str = ""
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None  # ID of the event that caused this one
    priority: EventPriority = EventPriority.NORMAL

    @property
    @abstractmethod
    def event_type(self) -> str:
        """Get the event type identifier"""


# Memory Domain Events


@dataclass
class MemoryFoldCreated(DomainEvent):
    """Event when a new memory fold is created"""

    fold_id: str = ""
    content_hash: str = ""
    emotional_context: dict[str, float] = field(default_factory=dict)
    compression_ratio: float = 0.0

    @property
    def event_type(self) -> str:
        return "memory.fold.created"


@dataclass
class MemoryFoldRetrieved(DomainEvent):
    """Event when a memory fold is retrieved"""

    fold_id: str = ""
    retrieval_context: dict[str, Any] = field(default_factory=dict)

    @property
    def event_type(self) -> str:
        return "memory.fold.retrieved"


@dataclass
class MemoryFoldCompressed(DomainEvent):
    """Event when a memory fold is compressed"""

    fold_id: str = ""
    original_size: int = 0
    compressed_size: int = 0
    compression_method: str = ""

    @property
    def event_type(self) -> str:
        return "memory.fold.compressed"


@dataclass
class MemoryConsolidationCompleted(DomainEvent):
    """Event when memory consolidation is completed"""

    consolidated_folds: list[str] = field(default_factory=list)
    new_connections: int = 0
    strengthened_connections: int = 0

    @property
    def event_type(self) -> str:
        return "memory.consolidation.completed"


# GLYPH and Symbol Domain Events


@dataclass
class GlyphCreated(DomainEvent):
    """Event when a new GLYPH is created"""

    glyph_id: str = ""
    symbol_id: str = ""
    concept: str = ""
    modalities: list[str] = field(default_factory=list)

    @property
    def event_type(self) -> str:
        return "glyph.created"


@dataclass
class SymbolTranslated(DomainEvent):
    """Event when a symbol is translated between modalities"""

    original_id: str = ""
    translated_id: str = ""
    target_module: str = ""
    target_modality: str = ""

    @property
    def event_type(self) -> str:
        return "symbol.translated"


@dataclass
class ConsensusReached(DomainEvent):
    """Event when colony consensus is reached"""

    proposal_id: str = ""
    decision: str = ""
    confidence: float = 0.0
    method: str = ""
    participants: int = 0

    @property
    def event_type(self) -> str:
        return "consensus.reached"


@dataclass
class QIStateCollapsed(DomainEvent):
    """Event when a quantum state collapses"""

    state_id: str = ""
    measurement_result: str = ""
    coherence_before: float = 0.0
    coherence_after: float = 0.0

    @property
    def event_type(self) -> str:
        return "qi.state.collapsed"


# Consciousness Domain Events


@dataclass
class ConsciousnessStateChanged(DomainEvent):
    """Event when consciousness state changes"""

    previous_state: str = ""
    current_state: str = ""
    new_state: str = ""  # Added alias for bootstrap compatibility
    trigger: str = ""
    awareness_level: float = 0.0

    def __post_init__(self):
        # Ensure new_state matches current_state
        if not self.new_state and self.current_state:
            self.new_state = self.current_state
        elif self.new_state and not self.current_state:
            self.current_state = self.new_state

    @property
    def event_type(self) -> str:
        return "consciousness.state.changed"


@dataclass
class DecisionMade(DomainEvent):
    """Event when a conscious decision is made"""

    decision_id: str = ""
    options_considered: list[dict[str, Any]] = field(default_factory=list)
    selected_option: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    ethical_score: float = 0.0

    @property
    def event_type(self) -> str:
        return "consciousness.decision.made"


@dataclass
class ReflectionCompleted(DomainEvent):
    """Event when reflection process completes"""

    reflection_id: str = ""
    insights: list[str] = field(default_factory=list)
    self_awareness_delta: float = 0.0

    @property
    def event_type(self) -> str:
        return "consciousness.reflection.completed"


@dataclass
class AwarenessProcessed(DomainEvent):
    """Event when awareness is processed"""

    awareness_id: str = ""
    input_data: dict[str, Any] = field(default_factory=dict)
    awareness_delta: float = 0.0

    @property
    def event_type(self) -> str:
        return "consciousness.awareness.processed"


# Dream Domain Events


@dataclass
class DreamGenerated(DomainEvent):
    """Event when a dream is generated"""

    dream_id: str = ""
    dream_type: str = ""
    dream_content: dict[str, Any] = field(default_factory=dict)  # Added for bootstrap
    seed_data: dict[str, Any] = field(default_factory=dict)
    vividness: float = 0.0
    coherence: float = 0.0

    @property
    def event_type(self) -> str:
        return "dream.generated"


@dataclass
class DreamAnalyzed(DomainEvent):
    """Event when dream analysis completes"""

    dream_id: str = ""
    symbols_identified: list[str] = field(default_factory=list)
    emotional_themes: dict[str, float] = field(default_factory=dict)
    insights: list[str] = field(default_factory=list)

    @property
    def event_type(self) -> str:
        return "dream.analyzed"


@dataclass
class DreamCycleStarted(DomainEvent):
    """Event when dream cycle starts"""

    cycle_id: str = ""
    cycle_type: str = ""

    @property
    def event_type(self) -> str:
        return "dream.cycle.started"


# Quantum (QIM) Domain Events


@dataclass
class QIStateCreated(DomainEvent):
    """Event when quantum state is created"""

    state_id: str = ""
    state_type: str = ""  # superposition, entanglement
    coherence: float = 0.0
    dimensions: int = 0

    @property
    def event_type(self) -> str:
        return "qi.state.created"


@dataclass
class QIStateCollapsed(DomainEvent):
    """Event when quantum state collapses"""

    state_id: str = ""
    measurement_result: Any = None
    collapse_reason: str = ""

    @property
    def event_type(self) -> str:
        return "qi.state.collapsed"


@dataclass
class QISuperpositionCreated(DomainEvent):
    """Event when quantum superposition is created"""

    superposition_id: str = ""
    states: list[Any] = field(default_factory=list)
    state_count: int = 0

    @property
    def event_type(self) -> str:
        return "qi.superposition.created"


@dataclass
class EntanglementCreated(DomainEvent):
    """Event when entanglement is created"""

    entanglement_id: str = ""
    entangled_states: list[str] = field(default_factory=list)
    correlation: float = 0.0

    @property
    def event_type(self) -> str:
        return "qi.entanglement.created"


# Emotion Domain Events


@dataclass
class EmotionalStateChanged(DomainEvent):
    """Event when emotional state changes"""

    previous_vad: dict[str, float] = field(default_factory=dict)
    current_vad: dict[str, float] = field(default_factory=dict)
    trigger: str = ""
    intensity: float = 0.0

    @property
    def event_type(self) -> str:
        return "emotion.state.changed"


@dataclass
class EmotionalRegulationApplied(DomainEvent):
    """Event when emotional regulation is applied"""

    regulation_type: str = ""
    target_state: dict[str, float] = field(default_factory=dict)
    success_rate: float = 0.0

    @property
    def event_type(self) -> str:
        return "emotion.regulation.applied"


@dataclass
class EmotionAnalyzed(DomainEvent):
    """Event when emotion is analyzed"""

    analysis_id: str = ""
    vad_values: dict[str, float] = field(default_factory=dict)

    @property
    def event_type(self) -> str:
        return "emotion.analyzed"


@dataclass
class EmotionalResponseGenerated(DomainEvent):
    """Event when emotional response is generated"""

    response_id: str = ""
    response_vad: dict[str, float] = field(default_factory=dict)
    expression: str = ""

    @property
    def event_type(self) -> str:
        return "emotion.response.generated"


@dataclass
class EmotionRegulated(DomainEvent):
    """Event when emotion is regulated"""

    regulation_id: str = ""
    final_state: dict[str, float] = field(default_factory=dict)

    @property
    def event_type(self) -> str:
        return "emotion.regulated"


# Governance Domain Events


@dataclass
class EthicalViolationDetected(DomainEvent):
    """Event when ethical violation is detected"""

    violation_id: str = ""
    violation_type: str = ""
    severity: str = ""  # low, medium, high, critical
    action_taken: str = ""

    @property
    def event_type(self) -> str:
        return "governance.violation.detected"


@dataclass
class PolicyApplied(DomainEvent):
    """Event when governance policy is applied"""

    policy_id: str = ""
    policy_name: str = ""
    target_action: str = ""
    result: str = ""  # allowed, denied, modified

    @property
    def event_type(self) -> str:
        return "governance.policy.applied"


@dataclass
class EthicsCheckPerformed(DomainEvent):
    """Event when ethics check is performed"""

    check_id: str = ""
    action: str = ""
    permitted: bool = True

    @property
    def event_type(self) -> str:
        return "governance.ethics.checked"


@dataclass
class RiskEvaluated(DomainEvent):
    """Event when risk is evaluated"""

    evaluation_id: str = ""
    risk_level: str = ""
    risk_score: float = 0.0

    @property
    def event_type(self) -> str:
        return "governance.risk.evaluated"


# Bridge Domain Events


@dataclass
class ExternalMessageReceived(DomainEvent):
    """Event when external message is received"""

    message_id: str = ""
    source_system: str = ""
    protocol: str = ""
    payload_size: int = 0

    @property
    def event_type(self) -> str:
        return "bridge.message.received"


@dataclass
class ExternalMessageSent(DomainEvent):
    """Event when external message is sent"""

    message_id: str = ""
    destination_system: str = ""
    protocol: str = ""
    success: bool = False

    @property
    def event_type(self) -> str:
        return "bridge.message.sent"


@dataclass
class ExternalDataSent(DomainEvent):
    """Event when external data is sent"""

    data_id: str = ""
    destination: str = ""
    size: int = 0

    @property
    def event_type(self) -> str:
        return "bridge.data.sent"


@dataclass
class ExternalDataReceived(DomainEvent):
    """Event when external data is received"""

    data_id: str = ""
    source: str = ""
    size: int = 0

    @property
    def event_type(self) -> str:
        return "bridge.data.received"


@dataclass
class ProtocolTranslated(DomainEvent):
    """Event when protocol is translated"""

    translation_id: str = ""
    from_protocol: str = ""
    to_protocol: str = ""

    @property
    def event_type(self) -> str:
        return "bridge.protocol.translated"


# System-wide Events


@dataclass
class SystemStressLevelChanged(DomainEvent):
    """Event when system stress level changes"""

    previous_level: float = 0.0
    current_level: float = 0.0
    stress_source: str = ""
    hormone_levels: dict[str, float] = field(default_factory=dict)

    @property
    def event_type(self) -> str:
        return "system.stress.changed"


@dataclass
class ModuleHealthChanged(DomainEvent):
    """Event when module health status changes"""

    module_name: str = ""
    previous_health: dict[str, Any] = field(default_factory=dict)
    current_health: dict[str, Any] = field(default_factory=dict)

    @property
    def event_type(self) -> str:
        return "system.health.changed"


# Event Registry
EVENT_REGISTRY = {
    # Memory events
    "memory.fold.created": MemoryFoldCreated,
    "memory.fold.retrieved": MemoryFoldRetrieved,
    "memory.fold.compressed": MemoryFoldCompressed,
    "memory.consolidation.completed": MemoryConsolidationCompleted,
    # Consciousness events
    "consciousness.state.changed": ConsciousnessStateChanged,
    "consciousness.decision.made": DecisionMade,
    "consciousness.reflection.completed": ReflectionCompleted,
    "consciousness.awareness.processed": AwarenessProcessed,
    # Dream events
    "dream.generated": DreamGenerated,
    "dream.analyzed": DreamAnalyzed,
    "dream.cycle.started": DreamCycleStarted,
    # Quantum events
    "qi.state.created": QIStateCreated,
    "qi.state.collapsed": QIStateCollapsed,
    "qi.superposition.created": QISuperpositionCreated,
    "qi.entanglement.created": EntanglementCreated,
    # Emotion events
    "emotion.state.changed": EmotionalStateChanged,
    "emotion.regulation.applied": EmotionalRegulationApplied,
    "emotion.analyzed": EmotionAnalyzed,
    "emotion.response.generated": EmotionalResponseGenerated,
    "emotion.regulated": EmotionRegulated,
    # Governance events
    "governance.violation.detected": EthicalViolationDetected,
    "governance.policy.applied": PolicyApplied,
    "governance.ethics.checked": EthicsCheckPerformed,
    "governance.risk.evaluated": RiskEvaluated,
    # Bridge events
    "bridge.message.received": ExternalMessageReceived,
    "bridge.message.sent": ExternalMessageSent,
    "bridge.data.sent": ExternalDataSent,
    "bridge.data.received": ExternalDataReceived,
    "bridge.protocol.translated": ProtocolTranslated,
    # System events
    "system.stress.changed": SystemStressLevelChanged,
    "system.health.changed": ModuleHealthChanged,
}


def serialize_event(event: DomainEvent) -> dict[str, Any]:
    """Serialize domain event to dictionary"""
    return {
        "event_type": event.event_type,
        "event_id": event.event_id,
        "timestamp": event.timestamp.isoformat(),
        "source_module": event.source_module,
        "correlation_id": event.correlation_id,
        "causation_id": event.causation_id,
        "data": {
            k: v
            for k, v in event.__dict__.items()
            if k
            not in [
                "event_id",
                "timestamp",
                "source_module",
                "correlation_id",
                "causation_id",
            ]
        },
    }


def deserialize_event(data: dict[str, Any]) -> Optional[DomainEvent]:
    """Deserialize dictionary to domain event"""
    event_type = data.get("event_type")
    event_class = EVENT_REGISTRY.get(event_type)

    if not event_class:
        return None

    # Reconstruct event
    event_data = data.get("data", {})
    event_data.update(
        {
            "event_id": data.get("event_id"),
            "timestamp": datetime.fromisoformat(data.get("timestamp")),
            "source_module": data.get("source_module"),
            "correlation_id": data.get("correlation_id"),
            "causation_id": data.get("causation_id"),
        }
    )

    return event_class(**event_data)


# Neuroplastic tags
# TAG:core
# TAG:events
# TAG:contracts
# TAG:professional_architecture
