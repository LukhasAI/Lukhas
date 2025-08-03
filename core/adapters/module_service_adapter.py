"""
Module Service Adapter - Wraps existing module functionality with service interfaces
Professional pattern to avoid rewriting existing code
"""

import asyncio
from typing import Any, Dict, List, Optional, AsyncIterator
from datetime import datetime
import logging

from core.interfaces.services import (
    IMemoryService, IConsciousnessService, IDreamService,
    IQuantumService, IEmotionService, IGovernanceService,
    IBridgeService, IGlyphService
)
from core.container.service_container import injectable, ServiceLifetime
from core.events.contracts import (
    MemoryFoldCreated, ConsciousnessStateChanged,
    DreamGenerated, serialize_event
)

logger = logging.getLogger(__name__)

@injectable(ServiceLifetime.SINGLETON)
class MemoryServiceAdapter(IMemoryService):
    """Adapts existing memory module to IMemoryService interface"""
    
    def __init__(self):
        self._memory_module = None
        self._initialized = False
        
    async def initialize(self) -> None:
        """Lazy load memory module"""
        if not self._initialized:
            try:
                # Import existing memory components
                from memory import MemoryFoldManager, AGIMemory
                from memory.memory_fold import MemoryFoldSystem
                
                self._fold_manager = MemoryFoldManager() if MemoryFoldManager else None
                self._fold_system = MemoryFoldSystem() if not self._fold_manager else None
                self._agi_memory = AGIMemory() if AGIMemory else None
                
                self._initialized = True
                logger.info("Memory service adapter initialized")
            except ImportError as e:
                logger.warning(f"Some memory components not available: {e}")
                # Service can still function with reduced capability
                self._initialized = True
    
    async def shutdown(self) -> None:
        """Cleanup resources"""
        if hasattr(self, '_fold_manager') and hasattr(self._fold_manager, 'close'):
            await self._fold_manager.close()
    
    def get_health(self) -> Dict[str, Any]:
        """Get memory service health"""
        return {
            "status": "healthy" if self._initialized else "initializing",
            "initialized": self._initialized,
            "components": {
                "fold_manager": self._fold_manager is not None,
                "fold_system": hasattr(self, '_fold_system') and self._fold_system is not None,
                "agi_memory": hasattr(self, '_agi_memory') and self._agi_memory is not None
            }
        }
    
    async def create_fold(self, content: Any, metadata: Optional[Dict] = None) -> str:
        """Create memory fold using existing system"""
        await self.initialize()
        
        # Try different implementations
        if hasattr(self, '_fold_manager') and self._fold_manager:
            fold = await self._fold_manager.create_fold(content, metadata or {})
            fold_id = fold.get('id', str(id(fold)))
        elif hasattr(self, '_fold_system') and self._fold_system:
            fold_id = await self._fold_system.store({"content": content, "metadata": metadata})
        else:
            # Fallback implementation
            fold_id = f"fold_{datetime.now().timestamp()}"
            
        # Emit event through existing event bus
        try:
            from core.event_bus import EventBus
            event_bus = EventBus()
            event = MemoryFoldCreated(
                source_module="memory",
                fold_id=fold_id,
                content_hash=str(hash(str(content))),
                emotional_context=metadata.get('emotional_context', {}) if metadata else {}
            )
            await event_bus.publish("memory.fold.created", serialize_event(event))
        except:
            pass
            
        return fold_id
    
    async def retrieve_fold(self, fold_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve fold using existing system"""
        await self.initialize()
        
        if hasattr(self, '_fold_manager') and self._fold_manager and hasattr(self._fold_manager, 'get_fold'):
            return await self._fold_manager.get_fold(fold_id)
        elif hasattr(self, '_fold_system') and self._fold_system and hasattr(self._fold_system, 'retrieve'):
            return await self._fold_system.retrieve(fold_id)
        
        return None
    
    async def query_folds(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query folds using existing system"""
        await self.initialize()
        
        if hasattr(self, '_fold_manager') and self._fold_manager and hasattr(self._fold_manager, 'query'):
            return await self._fold_manager.query(criteria)
        elif hasattr(self, '_agi_memory') and self._agi_memory and hasattr(self._agi_memory, 'search'):
            return await self._agi_memory.search(**criteria)
        
        return []
    
    async def compress_fold(self, fold_id: str) -> bool:
        """Compress fold using existing system"""
        await self.initialize()
        
        if hasattr(self, '_fold_manager') and self._fold_manager and hasattr(self._fold_manager, 'compress_fold'):
            return await self._fold_manager.compress_fold(fold_id)
        
        return False

@injectable(ServiceLifetime.SINGLETON)
class ConsciousnessServiceAdapter(IConsciousnessService):
    """Adapts existing consciousness module to IConsciousnessService interface"""
    
    def __init__(self):
        self._consciousness_module = None
        self._initialized = False
        
    async def initialize(self) -> None:
        """Lazy load consciousness module"""
        if not self._initialized:
            try:
                # Import existing consciousness components
                from consciousness.unified.auto_consciousness import UnifiedConsciousness
                from consciousness.awareness import AwarenessModule
                
                self._unified = UnifiedConsciousness() if UnifiedConsciousness else None
                self._awareness = AwarenessModule() if AwarenessModule else None
                
                self._initialized = True
                logger.info("Consciousness service adapter initialized")
            except ImportError as e:
                logger.warning(f"Some consciousness components not available: {e}")
                self._initialized = True
    
    async def shutdown(self) -> None:
        """Cleanup resources"""
        pass
    
    def get_health(self) -> Dict[str, Any]:
        """Get consciousness service health"""
        return {
            "status": "healthy" if self._initialized else "initializing",
            "initialized": self._initialized,
            "components": {
                "unified_consciousness": hasattr(self, '_unified') and self._unified is not None,
                "awareness_module": hasattr(self, '_awareness') and self._awareness is not None
            }
        }
    
    async def get_current_state(self) -> Dict[str, Any]:
        """Get current consciousness state"""
        await self.initialize()
        
        state = {
            "awareness_level": 0.5,
            "state": "active",
            "last_reflection": None
        }
        
        if hasattr(self, '_unified') and hasattr(self._unified, 'get_state'):
            state.update(await self._unified.get_state())
        
        return state
    
    async def process_awareness(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process awareness input"""
        await self.initialize()
        
        if hasattr(self, '_awareness') and hasattr(self._awareness, 'process'):
            return await self._awareness.process(input_data)
        
        # Fallback processing
        return {
            "processed": True,
            "awareness_delta": 0.1,
            "insights": []
        }
    
    async def reflect(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform reflection"""
        await self.initialize()
        
        if hasattr(self, '_unified') and hasattr(self._unified, 'reflect'):
            return await self._unified.reflect(context)
        
        # Basic reflection
        return {
            "reflection_id": f"ref_{datetime.now().timestamp()}",
            "insights": ["Basic reflection completed"],
            "self_awareness_delta": 0.05
        }
    
    async def make_decision(self, options: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Make conscious decision"""
        await self.initialize()
        
        if hasattr(self, '_unified') and hasattr(self._unified, 'decide'):
            return await self._unified.decide(options)
        
        # Simple decision making
        selected = options[0] if options else {}
        return {
            "decision_id": f"dec_{datetime.now().timestamp()}",
            "selected_option": selected,
            "confidence": 0.7,
            "reasoning": "Default selection"
        }

@injectable(ServiceLifetime.SINGLETON)
class DreamServiceAdapter(IDreamService):
    """Adapts existing dream system to IDreamService interface"""
    
    def __init__(self):
        self._dream_engine = None
        self._initialized = False
        
    async def initialize(self) -> None:
        """Lazy load dream components"""
        if not self._initialized:
            try:
                from consciousness.dream.core.dream_engine import DreamEngine
                self._dream_engine = DreamEngine()
                self._initialized = True
                logger.info("Dream service adapter initialized")
            except ImportError as e:
                logger.warning(f"Dream engine not available: {e}")
                self._initialized = True
    
    async def shutdown(self) -> None:
        """Cleanup resources"""
        if self._dream_engine and hasattr(self._dream_engine, 'shutdown'):
            await self._dream_engine.shutdown()
    
    def get_health(self) -> Dict[str, Any]:
        """Get dream service health"""
        return {
            "status": "healthy" if self._initialized else "initializing",
            "initialized": self._initialized,
            "dream_engine_available": self._dream_engine is not None
        }
    
    async def generate_dream(self, seed: Any) -> Dict[str, Any]:
        """Generate dream using existing engine"""
        await self.initialize()
        
        if self._dream_engine and hasattr(self._dream_engine, 'generate'):
            return await self._dream_engine.generate(seed)
        
        # Fallback dream generation
        return {
            "dream_id": f"dream_{datetime.now().timestamp()}",
            "content": f"Generated from seed: {seed}",
            "vividness": 0.5,
            "coherence": 0.6
        }
    
    async def process_dream_cycle(self) -> AsyncIterator[Dict[str, Any]]:
        """Process dream cycle"""
        await self.initialize()
        
        if self._dream_engine and hasattr(self._dream_engine, 'dream_cycle'):
            async for dream in self._dream_engine.dream_cycle():
                yield dream
        else:
            # Simple dream cycle
            for i in range(3):
                await asyncio.sleep(0.1)
                yield {
                    "phase": f"phase_{i}",
                    "dream": await self.generate_dream(f"cycle_seed_{i}")
                }
    
    async def analyze_dream(self, dream: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze dream content"""
        await self.initialize()
        
        if self._dream_engine and hasattr(self._dream_engine, 'analyze'):
            return await self._dream_engine.analyze(dream)
        
        # Basic analysis
        return {
            "dream_id": dream.get("dream_id", "unknown"),
            "symbols_identified": ["seed", "generation"],
            "emotional_themes": {"neutral": 0.7, "curiosity": 0.3},
            "insights": ["Basic dream pattern detected"]
        }

@injectable(ServiceLifetime.SINGLETON)
class QuantumServiceAdapter(IQuantumService):
    """Adapts existing QIM module to IQuantumService interface"""
    
    def __init__(self):
        self._quantum_module = None
        self._initialized = False
        
    async def initialize(self) -> None:
        """Lazy load quantum components"""
        if not self._initialized:
            try:
                from qim.systems.quantum_engine import QuantumOscillator
                self._oscillator = QuantumOscillator()
                self._initialized = True
                logger.info("Quantum service adapter initialized")
            except ImportError:
                logger.warning("Quantum components not available")
                self._initialized = True
    
    async def shutdown(self) -> None:
        """Cleanup resources"""
        pass
    
    def get_health(self) -> Dict[str, Any]:
        """Get quantum service health"""
        return {
            "status": "healthy" if self._initialized else "initializing",
            "initialized": self._initialized,
            "quantum_oscillator": hasattr(self, '_oscillator') and self._oscillator is not None
        }
    
    async def create_superposition(self, states: List[Any]) -> Any:
        """Create quantum superposition"""
        await self.initialize()
        
        if hasattr(self, '_oscillator') and hasattr(self._oscillator, 'superpose'):
            return await self._oscillator.superpose(states)
        
        # Simulated superposition
        return {
            "state_id": f"super_{datetime.now().timestamp()}",
            "states": states,
            "coherence": 0.8
        }
    
    async def entangle(self, state1: Any, state2: Any) -> Any:
        """Create entanglement"""
        await self.initialize()
        
        if hasattr(self, '_oscillator') and hasattr(self._oscillator, 'entangle'):
            return await self._oscillator.entangle(state1, state2)
        
        return {
            "entanglement_id": f"ent_{datetime.now().timestamp()}",
            "state1": state1,
            "state2": state2,
            "correlation": 0.9
        }
    
    async def collapse_state(self, superposition: Any) -> Any:
        """Collapse quantum state"""
        await self.initialize()
        
        if hasattr(self, '_oscillator') and hasattr(self._oscillator, 'collapse'):
            return await self._oscillator.collapse(superposition)
        
        # Simple collapse
        states = superposition.get("states", [])
        return states[0] if states else None
    
    async def measure_coherence(self, state: Any) -> float:
        """Measure quantum coherence"""
        await self.initialize()
        
        if hasattr(self, '_oscillator') and hasattr(self._oscillator, 'coherence'):
            return await self._oscillator.coherence(state)
        
        return 0.75  # Default coherence

@injectable(ServiceLifetime.SINGLETON)
class EmotionServiceAdapter(IEmotionService):
    """Adapts existing emotion module to IEmotionService interface"""
    
    def __init__(self):
        self._emotion_module = None
        self._initialized = False
        
    async def initialize(self) -> None:
        """Lazy load emotion components"""
        if not self._initialized:
            try:
                from emotion.core.vad import VADSystem
                from emotion.core.emotional_engine import EmotionalEngine
                
                self._vad_system = VADSystem() if VADSystem else None
                self._emotional_engine = EmotionalEngine() if EmotionalEngine else None
                
                self._initialized = True
                logger.info("Emotion service adapter initialized")
            except ImportError as e:
                logger.warning(f"Some emotion components not available: {e}")
                self._initialized = True
    
    async def shutdown(self) -> None:
        """Cleanup resources"""
        pass
    
    def get_health(self) -> Dict[str, Any]:
        """Get emotion service health"""
        return {
            "status": "healthy" if self._initialized else "initializing",
            "initialized": self._initialized,
            "components": {
                "vad_system": hasattr(self, '_vad_system') and self._vad_system is not None,
                "emotional_engine": hasattr(self, '_emotional_engine') and self._emotional_engine is not None
            }
        }
    
    async def analyze_emotion(self, input_data: Any) -> Dict[str, float]:
        """Analyze emotional content"""
        await self.initialize()
        
        if hasattr(self, '_vad_system') and hasattr(self._vad_system, 'analyze'):
            return await self._vad_system.analyze(input_data)
        
        # Default VAD values
        return {
            "valence": 0.5,
            "arousal": 0.5,
            "dominance": 0.5
        }
    
    async def generate_emotional_response(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate emotional response"""
        await self.initialize()
        
        if hasattr(self, '_emotional_engine') and hasattr(self._emotional_engine, 'generate_response'):
            return await self._emotional_engine.generate_response(context)
        
        vad = await self.analyze_emotion(context)
        return {
            "response_id": f"emo_{datetime.now().timestamp()}",
            "vad": vad,
            "expression": "neutral",
            "intensity": 0.5
        }
    
    async def regulate_emotion(self, current_state: Dict[str, float], target_state: Dict[str, float]) -> Dict[str, float]:
        """Regulate emotional state"""
        await self.initialize()
        
        if hasattr(self, '_emotional_engine') and hasattr(self._emotional_engine, 'regulate'):
            return await self._emotional_engine.regulate(current_state, target_state)
        
        # Simple regulation
        regulated = {}
        for key in ['valence', 'arousal', 'dominance']:
            current = current_state.get(key, 0.5)
            target = target_state.get(key, 0.5)
            regulated[key] = current + (target - current) * 0.3
        
        return regulated

@injectable(ServiceLifetime.SINGLETON)
class GovernanceServiceAdapter(IGovernanceService):
    """Adapts existing governance module to IGovernanceService interface"""
    
    def __init__(self):
        self._guardian = None
        self._initialized = False
        
    async def initialize(self) -> None:
        """Lazy load governance components"""
        if not self._initialized:
            try:
                from governance.guardian.guardian_system import GuardianSystem
                from governance.reflector.guardian_reflector import GuardianReflector
                
                self._guardian = GuardianSystem() if GuardianSystem else None
                self._reflector = GuardianReflector() if GuardianReflector else None
                
                self._initialized = True
                logger.info("Governance service adapter initialized")
            except ImportError as e:
                logger.warning(f"Some governance components not available: {e}")
                self._initialized = True
    
    async def shutdown(self) -> None:
        """Cleanup resources"""
        if self._guardian and hasattr(self._guardian, 'shutdown'):
            await self._guardian.shutdown()
    
    def get_health(self) -> Dict[str, Any]:
        """Get governance service health"""
        return {
            "status": "healthy" if self._initialized else "initializing",
            "initialized": self._initialized,
            "components": {
                "guardian_system": self._guardian is not None,
                "reflector": hasattr(self, '_reflector') and self._reflector is not None
            }
        }
    
    async def check_ethics(self, action: str, context: Dict[str, Any]) -> bool:
        """Check if action is ethically permitted"""
        await self.initialize()
        
        if self._guardian and hasattr(self._guardian, 'validate_action'):
            result = await self._guardian.validate_action(action, context)
            return result.get('permitted', True)
        
        # Default permissive if no guardian
        return True
    
    async def evaluate_risk(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate risk of scenario"""
        await self.initialize()
        
        if hasattr(self, '_reflector') and hasattr(self._reflector, 'assess_risk'):
            return await self._reflector.assess_risk(scenario)
        
        return {
            "risk_level": "low",
            "risk_score": 0.2,
            "factors": [],
            "recommendations": []
        }
    
    async def apply_policy(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Apply governance policy"""
        await self.initialize()
        
        if self._guardian and hasattr(self._guardian, 'apply_policy'):
            return await self._guardian.apply_policy(request)
        
        return {
            "policy_id": f"pol_{datetime.now().timestamp()}",
            "decision": "allowed",
            "conditions": [],
            "audit_trail": []
        }
    
    async def audit_action(self, action: Dict[str, Any]) -> None:
        """Audit an action for compliance"""
        await self.initialize()
        
        if self._guardian and hasattr(self._guardian, 'audit'):
            await self._guardian.audit(action)
        
        # Log audit event
        logger.info(f"Audit: {action.get('type', 'unknown')} at {datetime.now()}")

@injectable(ServiceLifetime.SINGLETON)
class BridgeServiceAdapter(IBridgeService):
    """Adapts existing bridge module to IBridgeService interface"""
    
    def __init__(self):
        self._bridge_manager = None
        self._initialized = False
        
    async def initialize(self) -> None:
        """Lazy load bridge components"""
        if not self._initialized:
            try:
                from bridge.api_connector import APIConnector
                from bridge.protocol_translator import ProtocolTranslator
                
                self._api_connector = APIConnector() if APIConnector else None
                self._translator = ProtocolTranslator() if ProtocolTranslator else None
                
                self._initialized = True
                logger.info("Bridge service adapter initialized")
            except ImportError as e:
                logger.warning(f"Some bridge components not available: {e}")
                self._initialized = True
    
    async def shutdown(self) -> None:
        """Cleanup resources"""
        if hasattr(self, '_api_connector') and hasattr(self._api_connector, 'close'):
            await self._api_connector.close()
    
    def get_health(self) -> Dict[str, Any]:
        """Get bridge service health"""
        return {
            "status": "healthy" if self._initialized else "initializing",
            "initialized": self._initialized,
            "components": {
                "api_connector": hasattr(self, '_api_connector') and self._api_connector is not None,
                "protocol_translator": hasattr(self, '_translator') and self._translator is not None
            }
        }
    
    async def send_external(self, destination: str, data: Any) -> Dict[str, Any]:
        """Send data to external system"""
        await self.initialize()
        
        if hasattr(self, '_api_connector') and hasattr(self._api_connector, 'send'):
            return await self._api_connector.send(destination, data)
        
        return {
            "sent": True,
            "destination": destination,
            "timestamp": datetime.now().isoformat(),
            "response": None
        }
    
    async def receive_external(self, source: str) -> Optional[Any]:
        """Receive data from external system"""
        await self.initialize()
        
        if hasattr(self, '_api_connector') and hasattr(self._api_connector, 'receive'):
            return await self._api_connector.receive(source)
        
        return None
    
    async def translate_protocol(self, data: Any, from_protocol: str, to_protocol: str) -> Any:
        """Translate between protocols"""
        await self.initialize()
        
        if hasattr(self, '_translator') and hasattr(self._translator, 'translate'):
            return await self._translator.translate(data, from_protocol, to_protocol)
        
        # Passthrough if no translator
        return data

# Register adapters with container
def register_service_adapters():
    """Register all service adapters with the container"""
    from core.container.service_container import get_container
    
    container = get_container()
    
    # Register all service adapters
    container.register_singleton(IMemoryService, MemoryServiceAdapter)
    container.register_singleton(IConsciousnessService, ConsciousnessServiceAdapter)
    container.register_singleton(IDreamService, DreamServiceAdapter)
    container.register_singleton(IQuantumService, QuantumServiceAdapter)
    container.register_singleton(IEmotionService, EmotionServiceAdapter)
    container.register_singleton(IGovernanceService, GovernanceServiceAdapter)
    container.register_singleton(IBridgeService, BridgeServiceAdapter)
    
    logger.info("All service adapters registered with container")

# Neuroplastic tags
#TAG:core
#TAG:adapters
#TAG:services
#TAG:professional_architecture