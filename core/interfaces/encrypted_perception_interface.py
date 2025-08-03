"""
🔌 Encrypted Perception Interface
==================================

Interface module to break circular dependencies between:
vivox.encrypted_perception.anomaly_detection <-> vivox.encrypted_perception.vivox_evrn_core
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
import numpy as np
from core.common import GLYPHToken


class EthicalSignificance(Enum):
    """Ethical significance levels"""
    NEUTRAL = "neutral"
    LOW = "low" 
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PerceptualVector:
    """Shared perceptual vector class"""
    def __init__(self, data: np.ndarray, metadata: Dict[str, Any] = None):
        self.data = data
        self.metadata = metadata or {}
        self.timestamp = metadata.get('timestamp') if metadata else None
        

class AnomalySignature:
    """Shared anomaly signature class"""
    def __init__(self, signature_id: str, vector: PerceptualVector, severity: float):
        self.signature_id = signature_id
        self.vector = vector
        self.severity = severity
        self.ethical_significance = EthicalSignificance.NEUTRAL


class Encrypted_PerceptionInterface(ABC):
    """Abstract interface for encrypted_perception modules"""
    
    @abstractmethod
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data through the module"""
        pass
        
    @abstractmethod
    async def handle_glyph(self, token: GLYPHToken) -> GLYPHToken:
        """Handle GLYPH token"""
        pass
        
    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """Get module status"""
        pass


class AnomalyDetectorInterface(ABC):
    """Interface for anomaly detection"""
    
    @abstractmethod
    async def detect_anomalies(self, vectors: List[PerceptualVector]) -> List[AnomalySignature]:
        """Detect anomalies in perceptual vectors"""
        pass
    
    @abstractmethod
    async def update_signatures(self, new_signatures: List[AnomalySignature]) -> None:
        """Update anomaly signatures"""
        pass


class EVRNCoreInterface(ABC):
    """Interface for EVRN core functionality"""
    
    @abstractmethod
    async def process_perceptual_input(self, input_data: Any) -> PerceptualVector:
        """Process raw input into perceptual vector"""
        pass
    
    @abstractmethod
    async def encrypt_perception(self, vector: PerceptualVector) -> bytes:
        """Encrypt perceptual vector"""
        pass


# Module registry for dependency injection
_module_registry: Dict[str, Encrypted_PerceptionInterface] = {}


def register_module(name: str, module: Encrypted_PerceptionInterface) -> None:
    """Register module implementation"""
    _module_registry[name] = module
    

def get_module(name: str) -> Optional[Encrypted_PerceptionInterface]:
    """Get registered module"""
    return _module_registry.get(name)
