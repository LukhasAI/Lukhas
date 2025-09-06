#!/usr/bin/env python3
"""
API Services Layer
Provides clean service interfaces for all API endpoints.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from hub.service_registry import get_service

from candidate.core.common import get_logger

logger = get_logger(__name__, timezone)


class APIServiceBase:
    """Base class for API services"""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self._service = None
        self._initialized = False

    def _ensure_service(self):
        """Ensure service is loaded"""
        if not self._initialized:
            try:
                self._service = get_service(self.service_name)
                self._initialized = True
            except KeyError:
                logger.error(f"Service {self.service_name} not found")
                self._service = None
                self._initialized = True


class MemoryAPIService(APIServiceBase):
    """Service layer for memory API operations"""

    def __init__(self):
        super().__init__('memory_service')

    async def store_memory(self,
                           agent_id: str,
                           content: str,
                           context: Optional[Dict[str, Any]] = None,
                           metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Store a memory"""
        self._ensure_service()

        if not self._service:
            raise HTTPException(status_code=503, detail="Memory service unavailable")

        memory_data = {
            "content": content,
            "context": context or {},
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        result = await self._service.store(agent_id, memory_data, "api_memory")

        return {
            "status": "success",
            "memory_id": result.get("memory_id"),
            "timestamp": result.get("timestamp")
        }

    async def retrieve_memories(self,
                                agent_id: str,
                                query: Optional[str] = None,
                                limit: int = 10,
                                memory_type: Optional[str] = None) -> List[Dict[str,
                                                                                Any]]:
        """Retrieve memories"""
        self._ensure_service()

        if not self._service:
            raise HTTPException(status_code=503, detail="Memory service unavailable")

        query_params = {}
        if query:
            query_params["query"] = query
        if memory_type:
            query_params["type"] = memory_type

        memories = await self._service.retrieve(agent_id, query_params, limit)

        return memories

    async def fold_memories(self, agent_id: str) -> Dict[str, Any]:
        """Perform memory folding operation"""
        self._ensure_service()

        if not self._service:
            raise HTTPException(status_code=503, detail="Memory service unavailable")

        result = await self._service.consolidate(agent_id, "fold")

        return {
            "status": "success",
            "folding_complete": result.get("consolidated", False),
            "result": result.get("result", {})
        }


class DreamAPIService(APIServiceBase):
    """Service layer for dream API operations"""

    def __init__(self):
        super().__init__('dream_service')

    async def generate_dream(self,
                             agent_id: str,
                             theme: Optional[str] = None,
                             intensity: float = 0.7,
                             lucidity: float = 0.5) -> Dict[str, Any]:
        """Generate a dream synthesis"""
        self._ensure_service()

        if not self._service:
            # Fallback to creativity service if dream service not available
            try:
                creativity_service = get_service('creativity_service')
                return await creativity_service.dream_inspired_creation(
                    agent_id,
                    {"theme": theme, "intensity": intensity}
                )
            except BaseException:
                raise HTTPException(status_code=503, detail="Dream service unavailable")

        dream_params = {
            "theme": theme or "spontaneous",
            "intensity": intensity,
            "lucidity": lucidity,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        result = await self._service.synthesize(agent_id, dream_params)

        return {
            "status": "success",
            "dream": result,
            "agent_id": agent_id
        }


class ConsciousnessAPIService(APIServiceBase):
    """Service layer for consciousness API operations"""

    def __init__(self):
        super().__init__('consciousness_service')

    async def get_awareness_state(self, agent_id: str) -> Dict[str, Any]:
        """Get current awareness state"""
        self._ensure_service()

        if not self._service:
            raise HTTPException(status_code=503,
                                detail="Consciousness service unavailable")

        state = await self._service.get_state(agent_id)

        return {
            "agent_id": agent_id,
            "awareness_level": state.get("level", 0.0),
            "state": state,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def process_stimulus(self,
                               agent_id: str,
                               stimulus_type: str,
                               stimulus_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a stimulus through consciousness"""
        self._ensure_service()

        if not self._service:
            raise HTTPException(status_code=503,
                                detail="Consciousness service unavailable")

        stimulus = {
            "type": stimulus_type,
            "data": stimulus_data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        result = await self._service.process_awareness(agent_id, stimulus)

        return {
            "status": "success",
            "processing_result": result,
            "agent_id": agent_id
        }


class EmotionAPIService(APIServiceBase):
    """Service layer for emotion API operations"""

    def __init__(self):
        super().__init__('emotion_service')

    async def get_emotional_state(self, agent_id: str) -> Dict[str, Any]:
        """Get current emotional state"""
        # Since emotion service might not be registered, use a fallback
        try:
            self._ensure_service()
            if self._service:
                return await self._service.get_state(agent_id)
        except BaseException:
            pass

        # Fallback implementation
        return {
            "agent_id": agent_id,
            "emotional_state": {
                "valence": 0.0,
                "arousal": 0.0,
                "dominance": 0.0
            },
            "primary_emotion": "neutral",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def update_emotion(self,
                             agent_id: str,
                             event: str,
                             intensity: float = 0.5) -> Dict[str, Any]:
        """Update emotional state based on event"""
        # Fallback implementation
        return {
            "status": "success",
            "agent_id": agent_id,
            "event": event,
            "intensity": intensity,
            "new_state": {
                "valence": intensity * 0.5,
                "arousal": intensity,
                "primary_emotion": "engaged"
            }
        }


class LearningAPIService(APIServiceBase):
    """Service layer for learning API operations"""

    def __init__(self):
        super().__init__('learning_service')

    async def train_model(self,
                          agent_id: str,
                          training_data: List[Dict[str, Any]],
                          model_type: str = "default") -> Dict[str, Any]:
        """Train a model"""
        self._ensure_service()

        if not self._service:
            raise HTTPException(status_code=503, detail="Learning service unavailable")

        config = {
            "model_type": model_type,
            "batch_size": 32,
            "epochs": 10
        }

        result = await self._service.train(
            agent_id,
            {"data": training_data},
            config
        )

        return {
            "status": "success",
            "training_result": result,
            "agent_id": agent_id
        }

    async def get_learning_status(self, agent_id: str) -> Dict[str, Any]:
        """Get learning status"""
        self._ensure_service()

        if not self._service:
            raise HTTPException(status_code=503, detail="Learning service unavailable")

        status = await self._service.get_learning_status(agent_id)

        return {
            "agent_id": agent_id,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


class IdentityAPIService(APIServiceBase):
    """Service layer for identity API operations"""

    def __init__(self):
        super().__init__('identity_service')

    async def verify_identity(self,
                              agent_id: str,
                              credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Verify agent identity"""
        self._ensure_service()

        if not self._service:
            # Fallback - allow all for development
            return {
                "verified": True,
                "agent_id": agent_id,
                "tier": 1,
                "permissions": ["basic"]
            }

        verified = await self._service.verify_access(agent_id, "api.access")
        tier = await self._service.get_agent_tier(agent_id) if verified else 0

        return {
            "verified": verified,
            "agent_id": agent_id,
            "tier": tier,
            "permissions": self._identity_core.resolve_access_tier(tier)
        }

    def _identity_core.resolve_access_tier(self, tier: int) -> List[str]:
        """Get permissions for a tier"""
        tier_permissions = {
            0: [],
            1: ["basic", "memory.read", "dream.view"],
            2: ["basic", "memory", "dream", "learning.view"],
            3: ["basic", "memory", "dream", "learning", "consciousness"],
            4: ["basic", "memory", "dream", "learning", "consciousness", "admin.view"],
            5: ["all"]
        }
        return tier_permissions.get(tier, [])


# Create singleton instances
_memory_service = None
_dream_service = None
_consciousness_service = None
_emotion_service = None
_learning_service = None
_identity_service = None


def get_memory_api_service() -> MemoryAPIService:
    """Get memory API service singleton"""
    global _memory_service
    if _memory_service is None:
        _memory_service = MemoryAPIService()
    return _memory_service


def get_dream_api_service() -> DreamAPIService:
    """Get dream API service singleton"""
    global _dream_service
    if _dream_service is None:
        _dream_service = DreamAPIService()
    return _dream_service


def get_consciousness_api_service() -> ConsciousnessAPIService:
    """Get consciousness API service singleton"""
    global _consciousness_service
    if _consciousness_service is None:
        _consciousness_service = ConsciousnessAPIService()
    return _consciousness_service


def get_emotion_api_service() -> EmotionAPIService:
    """Get emotion API service singleton"""
    global _emotion_service
    if _emotion_service is None:
        _emotion_service = EmotionAPIService()
    return _emotion_service


def get_learning_api_service() -> LearningAPIService:
    """Get learning API service singleton"""
    global _learning_service
    if _learning_service is None:
        _learning_service = LearningAPIService()
    return _learning_service


def get_identity_api_service() -> IdentityAPIService:
    """Get identity API service singleton"""
    global _identity_service
    if _identity_service is None:
        _identity_service = IdentityAPIService()
    return _identity_service


__all__ = [
    'MemoryAPIService',
    'DreamAPIService',
    'ConsciousnessAPIService',
    'EmotionAPIService',
    'LearningAPIService',
    'IdentityAPIService',
    'get_memory_api_service',
    'get_dream_api_service',
    'get_consciousness_api_service',
    'get_emotion_api_service',
    'get_learning_api_service',
    'get_identity_api_service'
]
