"""
═══════════════════════════════════════════════════════════════════════════
LUKHAS Cognitive AI Awareness Protocol Interface
═══════════════════════════════════════════════════════════════════════════

Comprehensive interface for awareness assessment, tier management, and
bio-symbolic integration across the LUKHAS Cognitive AI ecosystem.

Features:
- Multi-modal awareness assessment
- Dynamic tier assignment
- Bio-symbolic integration
- Session management
- Security and compliance
"""
import hashlib
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class AwarenessType(Enum):
    """Types of awareness assessment"""

    ENVIRONMENTAL = "environmental"
    COGNITIVE = "cognitive"
    EMOTIONAL = "emotional"
    SOCIAL = "social"
    CREATIVE = "creative"
    ETHICAL = "ethical"
    QUANTUM = "quantum"
    SYMBOLIC = "symbolic"


class TierLevel(Enum):
    """Access tier levels"""

    TIER_1 = 1  # Basic access
    TIER_2 = 2  # Standard access
    TIER_3 = 3  # Premium access
    TIER_4 = 4  # Advanced access
    TIER_5 = 5  # Maximum access


class ProtocolStatus(Enum):
    """Protocol status states"""

    INITIALIZING = "initializing"
    ACTIVE = "active"
    ASSESSING = "assessing"
    COMPLETE = "complete"
    ERROR = "error"
    SUSPENDED = "suspended"


@dataclass
class AwarenessInput:
    """Input data for awareness assessment"""

    user_id: str
    session_id: str
    awareness_type: AwarenessType
    timestamp: datetime = field(default_factory=datetime.utcnow)
    context_data: dict[str, Any] = field(default_factory=dict)
    bio_metrics: dict[str, float] = field(default_factory=dict)
    symbolic_state: dict[str, Any] = field(default_factory=dict)
    environmental_data: dict[str, Any] = field(default_factory=dict)


@dataclass
class AwarenessOutput:
    """Output from awareness assessment"""

    request_id: str
    user_id: str
    tier_assignment: TierLevel
    confidence_score: float
    reasoning: list[str] = field(default_factory=list)
    bio_feedback: dict[str, Any] = field(default_factory=dict)
    symbolic_signature: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None


@dataclass
class SessionContext:
    """Session context for awareness protocol"""

    session_id: str
    user_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    tier_history: list[TierLevel] = field(default_factory=list)
    assessment_count: int = 0
    status: ProtocolStatus = ProtocolStatus.INITIALIZING
    metadata: dict[str, Any] = field(default_factory=dict)


class AwarenessAssessor(ABC):
    """Abstract base class for awareness assessors"""

    @abstractmethod
    async def assess(self, input_data: AwarenessInput) -> AwarenessOutput:
        """Assess awareness and return tier assignment"""

    @abstractmethod
    def get_supported_types(self) -> list[AwarenessType]:
        """Get list of supported awareness types"""

    @abstractmethod
    def get_assessor_info(self) -> dict[str, Any]:
        """Get information about this assessor"""


class AwarenessProtocolInterface(ABC):
    """Interface for awareness protocol implementations"""

    @abstractmethod
    async def initialize_session(self, user_id: str, session_data: dict[str, Any]) -> SessionContext:
        """Initialize a new awareness session"""

    @abstractmethod
    async def assess_awareness(self, input_data: AwarenessInput) -> AwarenessOutput:
        """Assess user awareness and assign tier"""

    @abstractmethod
    async def update_session(self, session_id: str, update_data: dict[str, Any]) -> SessionContext:
        """Update session context"""

    @abstractmethod
    async def terminate_session(self, session_id: str) -> bool:
        """Terminate an awareness session"""

    @abstractmethod
    def get_session_status(self, session_id: str) -> Optional[SessionContext]:
        """Get current session status"""

    @abstractmethod
    def register_assessor(self, assessor: AwarenessAssessor) -> bool:
        """Register an awareness assessor"""


class DefaultAwarenessProtocol(AwarenessProtocolInterface):
    """Default implementation of awareness protocol"""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self.sessions: dict[str, SessionContext] = {}
        self.assessors: dict[AwarenessType, AwarenessAssessor] = {}
        self.logger = logger.getChild("DefaultAwarenessProtocol")
        self.session_timeout = timedelta(minutes=self.config.get("session_timeout_minutes", 60))

        # Initialize built-in assessors
        self._initialize_builtin_assessors()

    def _initialize_builtin_assessors(self):
        """Initialize built-in awareness assessors"""
        # Register default assessors for each type
        for awareness_type in AwarenessType:
            assessor = DefaultAwarenessAssessor(awareness_type)
            self.assessors[awareness_type] = assessor

    async def initialize_session(self, user_id: str, session_data: dict[str, Any]) -> SessionContext:
        """Initialize a new awareness session"""
        session_id = self._generate_session_id(user_id)

        session = SessionContext(
            session_id=session_id,
            user_id=user_id,
            metadata=session_data.copy(),
        )

        self.sessions[session_id] = session
        self.logger.info(f"Initialized session {session_id} for user {user_id}")

        return session

    async def assess_awareness(self, input_data: AwarenessInput) -> AwarenessOutput:
        """Assess user awareness and assign tier"""
        # Get session context
        session = self.sessions.get(input_data.session_id)
        if not session:
            raise ValueError(f"Session {input_data.session_id} not found")

        # Update session activity
        session.last_activity = datetime.now(timezone.utc)
        session.assessment_count += 1
        session.status = ProtocolStatus.ASSESSING

        # Get appropriate assessor
        assessor = self.assessors.get(input_data.awareness_type)
        if not assessor:
            raise ValueError(f"No assessor for type {input_data.awareness_type}")

        try:
            # Perform assessment
            output = await assessor.assess(input_data)

            # Update session with new tier
            session.tier_history.append(output.tier_assignment)
            session.status = ProtocolStatus.COMPLETE

            # Set expiration
            output.expires_at = datetime.now(timezone.utc) + timedelta(hours=self.config.get("tier_validity_hours", 24))

            self.logger.info(
                f"Assessment complete: {input_data.user_id} -> "
                f"{output.tier_assignment} (confidence: {output.confidence_score})"
            )

            return output

        except Exception as e:
            session.status = ProtocolStatus.ERROR
            self.logger.error(f"Assessment failed: {e}")
            raise

    async def update_session(self, session_id: str, update_data: dict[str, Any]) -> SessionContext:
        """Update session context"""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Update metadata
        session.metadata.update(update_data)
        session.last_activity = datetime.now(timezone.utc)

        return session

    async def terminate_session(self, session_id: str) -> bool:
        """Terminate an awareness session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            self.logger.info(f"Terminated session {session_id}")
            return True
        return False

    def get_session_status(self, session_id: str) -> Optional[SessionContext]:
        """Get current session status"""
        session = self.sessions.get(session_id)
        if session:
            # Check for timeout
            if datetime.now(timezone.utc) - session.last_activity > self.session_timeout:
                session.status = ProtocolStatus.SUSPENDED
        return session

    def register_assessor(self, assessor: AwarenessAssessor) -> bool:
        """Register an awareness assessor"""
        try:
            supported_types = assessor.get_supported_types()
            for awareness_type in supported_types:
                self.assessors[awareness_type] = assessor
                self.logger.info(f"Registered assessor for {awareness_type}: {assessor.__class__.__name__}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to register assessor: {e}")
            return False

    def _generate_session_id(self, user_id: str) -> str:
        """Generate a unique session ID"""
        timestamp = str(int(time.time()))
        data = f"{user_id}:{timestamp}:{hash(user_id)}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def get_protocol_metrics(self) -> dict[str, Any]:
        """Get protocol performance metrics"""
        active_sessions = sum(
            1 for s in self.sessions.values() if s.status in [ProtocolStatus.ACTIVE, ProtocolStatus.ASSESSING]
        )

        total_assessments = sum(s.assessment_count for s in self.sessions.values())

        return {
            "total_sessions": len(self.sessions),
            "active_sessions": active_sessions,
            "total_assessments": total_assessments,
            "registered_assessors": len(self.assessors),
            "session_timeout_minutes": self.session_timeout.total_seconds() / 60,
        }


class DefaultAwarenessAssessor(AwarenessAssessor):
    """Default implementation of awareness assessor"""

    def __init__(self, awareness_type: AwarenessType):
        self.awareness_type = awareness_type
        self.logger = logger.getChild(f"DefaultAssessor.{awareness_type.value}")

    async def assess(self, input_data: AwarenessInput) -> AwarenessOutput:
        """Assess awareness and return tier assignment"""
        # Basic assessment logic (placeholder)
        confidence_score = self._calculate_confidence(input_data)
        tier = self._determine_tier(confidence_score)

        output = AwarenessOutput(
            request_id=self._generate_request_id(input_data),
            user_id=input_data.user_id,
            tier_assignment=tier,
            confidence_score=confidence_score,
            reasoning=[f"Assessment based on {self.awareness_type.value} factors"],
            symbolic_signature=self._generate_symbolic_signature(tier),
            metadata={
                "assessor": self.__class__.__name__,
                "awareness_type": self.awareness_type.value,
                "algorithm_version": "1.0.0",
            },
        )

        return output

    def get_supported_types(self) -> list[AwarenessType]:
        """Get list of supported awareness types"""
        return [self.awareness_type]

    def get_assessor_info(self) -> dict[str, Any]:
        """Get information about this assessor"""
        return {
            "name": self.__class__.__name__,
            "version": "1.0.0",
            "supported_types": [self.awareness_type.value],
            "description": f"Default assessor for {self.awareness_type.value}",
        }

    def _calculate_confidence(self, input_data: AwarenessInput) -> float:
        """Calculate confidence score based on input data"""
        # Placeholder logic - in real implementation, this would use
        # sophisticated algorithms based on the awareness type
        base_score = 0.7

        # Adjust based on available data
        if input_data.bio_metrics:
            base_score += 0.1
        if input_data.symbolic_state:
            base_score += 0.1
        if input_data.environmental_data:
            base_score += 0.05

        return min(base_score, 1.0)

    def _determine_tier(self, confidence_score: float) -> TierLevel:
        """Determine tier based on confidence score"""
        if confidence_score >= 0.9:
            return TierLevel.TIER_5
        elif confidence_score >= 0.8:
            return TierLevel.TIER_4
        elif confidence_score >= 0.7:
            return TierLevel.TIER_3
        elif confidence_score >= 0.6:
            return TierLevel.TIER_2
        else:
            return TierLevel.TIER_1

    def _generate_request_id(self, input_data: AwarenessInput) -> str:
        """Generate unique request ID"""
        data = f"{input_data.user_id}:{input_data.session_id}:{time.time()}"
        return hashlib.sha256(data.encode()).hexdigest()[:12]  # Changed from MD5 for security

    def _generate_symbolic_signature(self, tier: TierLevel) -> str:
        """Generate symbolic signature for tier"""
        symbols = {
            TierLevel.TIER_1: "Λ¹",
            TierLevel.TIER_2: "Λ²",
            TierLevel.TIER_3: "Λ³",
            TierLevel.TIER_4: "Λ⁴",
            TierLevel.TIER_5: "Λ⁵",
        }
        return symbols.get(tier, "LUKHAS?")


# Factory function for creating protocol instances


def create_awareness_protocol(
    protocol_type: str = "default", config: Optional[dict[str, Any]] = None
) -> AwarenessProtocolInterface:
    """Factory function to create awareness protocol instances"""
    if protocol_type == "default":
        return DefaultAwarenessProtocol(config)
    else:
        raise ValueError(f"Unknown protocol type: {protocol_type}")


# Global instance for easy access
_default_protocol: Optional[DefaultAwarenessProtocol] = None


def get_default_protocol(
    config: Optional[dict[str, Any]] = None,
) -> DefaultAwarenessProtocol:
    """Get the default awareness protocol instance"""
    global _default_protocol
    if _default_protocol is None:
        _default_protocol = DefaultAwarenessProtocol(config)
    return _default_protocol
