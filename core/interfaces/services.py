"""
LUKHAS Core Service Interfaces
Professional service contracts for all modules
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, AsyncIterator
from datetime import datetime

# Base service interface
class IService(ABC):
    """Base interface for all services"""
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the service"""
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Gracefully shutdown the service"""
        pass
    
    @abstractmethod
    def get_health(self) -> Dict[str, Any]:
        """Get service health status"""
        pass

# Memory Service Interface
class IMemoryService(IService):
    """Interface for memory operations"""
    
    @abstractmethod
    async def create_fold(self, content: Any, metadata: Optional[Dict] = None) -> str:
        """Create a new memory fold"""
        pass
    
    @abstractmethod
    async def retrieve_fold(self, fold_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a memory fold by ID"""
        pass
    
    @abstractmethod
    async def query_folds(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query memory folds"""
        pass
    
    @abstractmethod
    async def compress_fold(self, fold_id: str) -> bool:
        """Compress a memory fold"""
        pass

# Consciousness Service Interface
class IConsciousnessService(IService):
    """Interface for consciousness operations"""
    
    @abstractmethod
    async def get_current_state(self) -> Dict[str, Any]:
        """Get current consciousness state"""
        pass
    
    @abstractmethod
    async def process_awareness(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process awareness input"""
        pass
    
    @abstractmethod
    async def reflect(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform reflection on context"""
        pass
    
    @abstractmethod
    async def make_decision(self, options: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Make a conscious decision"""
        pass

# Dream Service Interface
class IDreamService(IService):
    """Interface for dream operations"""
    
    @abstractmethod
    async def generate_dream(self, seed: Any) -> Dict[str, Any]:
        """Generate a dream from seed"""
        pass
    
    @abstractmethod
    async def process_dream_cycle(self) -> AsyncIterator[Dict[str, Any]]:
        """Process a full dream cycle"""
        pass
    
    @abstractmethod
    async def analyze_dream(self, dream: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze dream content"""
        pass

# Quantum (QIM) Service Interface
class IQuantumService(IService):
    """Interface for quantum-inspired operations"""
    
    @abstractmethod
    async def create_superposition(self, states: List[Any]) -> Any:
        """Create quantum superposition"""
        pass
    
    @abstractmethod
    async def entangle(self, state1: Any, state2: Any) -> Any:
        """Create entanglement between states"""
        pass
    
    @abstractmethod
    async def collapse_state(self, superposition: Any) -> Any:
        """Collapse quantum state"""
        pass
    
    @abstractmethod
    async def measure_coherence(self, state: Any) -> float:
        """Measure quantum coherence"""
        pass

# Emotion Service Interface
class IEmotionService(IService):
    """Interface for emotion processing"""
    
    @abstractmethod
    async def analyze_emotion(self, input_data: Any) -> Dict[str, float]:
        """Analyze emotional content (returns VAD values)"""
        pass
    
    @abstractmethod
    async def generate_emotional_response(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate emotional response"""
        pass
    
    @abstractmethod
    async def regulate_emotion(self, current_state: Dict[str, float], target_state: Dict[str, float]) -> Dict[str, float]:
        """Regulate emotional state"""
        pass

# Governance Service Interface  
class IGovernanceService(IService):
    """Interface for governance and ethics"""
    
    @abstractmethod
    async def check_ethics(self, action: str, context: Dict[str, Any]) -> bool:
        """Check if action is ethically permitted"""
        pass
    
    @abstractmethod
    async def evaluate_risk(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate risk of scenario"""
        pass
    
    @abstractmethod
    async def apply_policy(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Apply governance policy"""
        pass
    
    @abstractmethod
    async def audit_action(self, action: Dict[str, Any]) -> None:
        """Audit an action for compliance"""
        pass

# Bridge Service Interface
class IBridgeService(IService):
    """Interface for external connections"""
    
    @abstractmethod
    async def send_external(self, destination: str, data: Any) -> Dict[str, Any]:
        """Send data to external system"""
        pass
    
    @abstractmethod
    async def receive_external(self, source: str) -> Optional[Any]:
        """Receive data from external system"""
        pass
    
    @abstractmethod
    async def translate_protocol(self, data: Any, from_protocol: str, to_protocol: str) -> Any:
        """Translate between protocols"""
        pass

# Event Service Interface
class IEventService(IService):
    """Interface for event handling"""
    
    @abstractmethod
    async def publish(self, event_type: str, data: Any) -> None:
        """Publish an event"""
        pass
    
    @abstractmethod
    async def subscribe(self, event_type: str, handler: Any) -> str:
        """Subscribe to events"""
        pass
    
    @abstractmethod
    async def unsubscribe(self, subscription_id: str) -> None:
        """Unsubscribe from events"""
        pass

# GLYPH Service Interface
class IGlyphService(IService):
    """Interface for GLYPH operations"""
    
    @abstractmethod
    async def encode(self, data: Any) -> str:
        """Encode data as GLYPH"""
        pass
    
    @abstractmethod
    async def decode(self, glyph: str) -> Any:
        """Decode GLYPH to data"""
        pass
    
    @abstractmethod
    async def validate_glyph(self, glyph: str) -> bool:
        """Validate GLYPH format"""
        pass

# Configuration Service Interface
class IConfigurationService(IService):
    """Interface for configuration management"""
    
    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        pass
    
    @abstractmethod
    def reload(self) -> None:
        """Reload configuration"""
        pass

# Neuroplastic tags
#TAG:core
#TAG:interfaces
#TAG:services
#TAG:professional_architecture