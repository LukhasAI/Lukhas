"""
LUKHAS Core Service Interfaces
Professional service contracts for all modules
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any, Optional

# Base service interface


class IService(ABC):
    """Base interface for all services"""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the service"""

    @abstractmethod
    async def shutdown(self) -> None:
        """Gracefully shutdown the service"""

    @abstractmethod
    def get_health(self) -> dict[str, Any]:
        """Get service health status"""


# Memory Service Interface


class IMemoryService(IService):
    """Interface for memory operations"""

    @abstractmethod
    async def create_fold(self, content: Any, metadata: Optional[dict] = None) -> str:
        """Create a new memory fold"""

    @abstractmethod
    async def retrieve_fold(self, fold_id: str) -> Optional[dict[str, Any]]:
        """Retrieve a memory fold by ID"""

    @abstractmethod
    async def query_folds(self, criteria: dict[str, Any]) -> list[dict[str, Any]]:
        """Query memory folds"""

    @abstractmethod
    async def compress_fold(self, fold_id: str) -> bool:
        """Compress a memory fold"""


# Consciousness Service Interface


class IConsciousnessService(IService):
    """Interface for consciousness operations"""

    @abstractmethod
    async def get_current_state(self) -> dict[str, Any]:
        """Get current consciousness state"""

    @abstractmethod
    async def process_awareness(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Process awareness input"""

    @abstractmethod
    async def reflect(self, context: dict[str, Any]) -> dict[str, Any]:
        """Perform reflection on context"""

    @abstractmethod
    async def make_decision(self, options: list[dict[str, Any]]) -> dict[str, Any]:
        """Make a conscious decision"""


# Dream Service Interface


class IDreamService(IService):
    """Interface for dream operations"""

    @abstractmethod
    async def generate_dream(self, seed: Any) -> dict[str, Any]:
        """Generate a dream from seed"""

    @abstractmethod
    async def process_dream_cycle(self) -> AsyncIterator[dict[str, Any]]:
        """Process a full dream cycle"""

    @abstractmethod
    async def analyze_dream(self, dream: dict[str, Any]) -> dict[str, Any]:
        """Analyze dream content"""


# Quantum (QIM) Service Interface


class IQuantumService(IService):
    """Interface for quantum-inspired operations"""

    @abstractmethod
    async def create_superposition(self, states: list[Any]) -> Any:
        """Create quantum superposition"""

    @abstractmethod
    async def entangle(self, state1: Any, state2: Any) -> Any:
        """Create entanglement between states"""

    @abstractmethod
    async def collapse_state(self, superposition: Any) -> Any:
        """Collapse quantum state"""

    @abstractmethod
    async def measure_coherence(self, state: Any) -> float:
        """Measure quantum coherence"""


# Emotion Service Interface


class IEmotionService(IService):
    """Interface for emotion processing"""

    @abstractmethod
    async def analyze_emotion(self, input_data: Any) -> dict[str, float]:
        """Analyze emotional content (returns VAD values)"""

    @abstractmethod
    async def generate_emotional_response(self, context: dict[str, Any]) -> dict[str, Any]:
        """Generate emotional response"""

    @abstractmethod
    async def regulate_emotion(
        self, current_state: dict[str, float], target_state: dict[str, float]
    ) -> dict[str, float]:
        """Regulate emotional state"""


# Identity Service Interface


class IIdentityService(IService):
    """Interface for identity and authentication operations"""

    @abstractmethod
    async def authenticate(self, credentials: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Authenticate user with credentials"""

    @abstractmethod
    async def verify_identity(self, token: str) -> bool:
        """Verify identity token"""

    @abstractmethod
    async def create_identity(self, user_data: dict[str, Any]) -> str:
        """Create new identity"""

    @abstractmethod
    async def get_identity(self, user_id: str) -> Optional[dict[str, Any]]:
        """Get identity information"""


# Governance Service Interface


class IGovernanceService(IService):
    """Interface for governance and ethics"""

    @abstractmethod
    async def check_ethics(self, action: str, context: dict[str, Any]) -> bool:
        """Check if action is ethically permitted"""

    @abstractmethod
    async def evaluate_risk(self, scenario: dict[str, Any]) -> dict[str, Any]:
        """Evaluate risk of scenario"""

    @abstractmethod
    async def apply_policy(self, request: dict[str, Any]) -> dict[str, Any]:
        """Apply governance policy"""

    @abstractmethod
    async def audit_action(self, action: dict[str, Any]) -> None:
        """Audit an action for compliance"""


# Bridge Service Interface


class IBridgeService(IService):
    """Interface for external connections"""

    @abstractmethod
    async def send_external(self, destination: str, data: Any) -> dict[str, Any]:
        """Send data to external system"""

    @abstractmethod
    async def receive_external(self, source: str) -> Optional[Any]:
        """Receive data from external system"""

    @abstractmethod
    async def translate_protocol(self, data: Any, from_protocol: str, to_protocol: str) -> Any:
        """Translate between protocols"""


# Event Service Interface


class IEventService(IService):
    """Interface for event handling"""

    @abstractmethod
    async def publish(self, event_type: str, data: Any) -> None:
        """Publish an event"""

    @abstractmethod
    async def subscribe(self, event_type: str, handler: Any) -> str:
        """Subscribe to events"""

    @abstractmethod
    async def unsubscribe(self, subscription_id: str) -> None:
        """Unsubscribe from events"""


# GLYPH Service Interface


class IGlyphService(IService):
    """Interface for GLYPH operations"""

    @abstractmethod
    async def encode(self, data: Any) -> str:
        """Encode data as GLYPH"""

    @abstractmethod
    async def decode(self, glyph: str) -> Any:
        """Decode GLYPH to data"""

    @abstractmethod
    async def validate_glyph(self, glyph: str) -> bool:
        """Validate GLYPH format"""


# Configuration Service Interface


class IConfigurationService(IService):
    """Interface for configuration management"""

    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""

    @abstractmethod
    def reload(self) -> None:
        """Reload configuration"""


# Neuroplastic tags
# TAG:core
# TAG:interfaces
# TAG:services
# TAG:professional_architecture
