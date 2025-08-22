"""
LUKHAS AI Core System Wrapper
Production interface for the foundational GLYPH engine and symbolic processing
Trinity Framework: ⚛️🧠🛡️
"""

import os
import logging
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)

# Feature flags
CORE_ACTIVE = os.getenv("CORE_ACTIVE", "false").lower() == "true"
GLYPH_ENGINE_ENABLED = os.getenv("GLYPH_ENGINE_ENABLED", "true").lower() == "true"
SYMBOLIC_PROCESSING_ENABLED = os.getenv("SYMBOLIC_PROCESSING_ENABLED", "true").lower() == "true"
ACTOR_SYSTEM_ENABLED = os.getenv("ACTOR_SYSTEM_ENABLED", "true").lower() == "true"


class CoreStatus(Enum):
    """Core system status enumeration"""
    INACTIVE = "inactive"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    ERROR = "error"


@dataclass
class GlyphResult:
    """Result from GLYPH processing operations"""
    glyph_id: str
    symbol: str
    concept: str
    success: bool
    metadata: Dict[str, Any]


@dataclass
class SymbolicResult:
    """Result from symbolic processing operations"""
    symbols: List[str]
    relationships: List[Dict[str, Any]]
    patterns: List[Dict[str, Any]]
    reasoning: Dict[str, Any]
    success: bool


class CoreWrapper:
    """
    Production wrapper for LUKHAS AI Core system.
    
    Provides access to:
    - GLYPH engine for symbolic communication
    - Actor system for distributed processing
    - Symbolic reasoning and pattern recognition
    - Trinity Framework integration (⚛️🧠🛡️)
    - Graph-based processing capabilities
    """
    
    def __init__(self):
        """Initialize the Core wrapper with Trinity Framework support"""
        self._status = CoreStatus.INACTIVE
        self._glyph_engine = None
        self._actor_system = None
        self._symbolic_world = None
        self._trinity_context = {
            "identity": "⚛️",
            "consciousness": "🧠", 
            "guardian": "🛡️",
            "framework": "⚛️🧠🛡️"
        }
        
        if CORE_ACTIVE:
            self._initialize_core_system()
    
    def _initialize_core_system(self):
        """Initialize the core systems with lazy loading"""
        try:
            self._status = CoreStatus.INITIALIZING
            logger.info("Initializing LUKHAS AI Core system...")
            
            if GLYPH_ENGINE_ENABLED:
                self._initialize_glyph_engine()
                
            if ACTOR_SYSTEM_ENABLED:
                self._initialize_actor_system()
                
            if SYMBOLIC_PROCESSING_ENABLED:
                self._initialize_symbolic_processing()
            
            self._status = CoreStatus.ACTIVE
            logger.info("Core system initialization complete")
            
        except Exception as e:
            self._status = CoreStatus.ERROR
            logger.error(f"Core system initialization failed: {e}")
    
    def _initialize_glyph_engine(self):
        """Initialize the GLYPH engine for symbolic communication"""
        try:
            # Import only when needed to avoid circular dependencies
            from candidate.core.glyph.glyph_engine import GlyphEngine
            self._glyph_engine = GlyphEngine()
            logger.info("GLYPH engine initialized")
        except ImportError as e:
            logger.warning(f"GLYPH engine not available: {e}")
            self._glyph_engine = None
    
    def _initialize_actor_system(self):
        """Initialize the actor system for distributed processing"""
        try:
            from candidate.core.actor_system import ActorSystem, get_global_actor_system
            self._actor_system = get_global_actor_system()
            logger.info("Actor system initialized")
        except ImportError as e:
            logger.warning(f"Actor system not available: {e}")
            self._actor_system = None
    
    def _initialize_symbolic_processing(self):
        """Initialize symbolic processing capabilities"""
        try:
            from candidate.core.symbolic.symbolic_core import SymbolicWorld, SymbolicReasoner
            self._symbolic_world = SymbolicWorld()
            self._symbolic_reasoner = SymbolicReasoner(self._symbolic_world)
            logger.info("Symbolic processing initialized")
        except ImportError as e:
            logger.warning(f"Symbolic processing not available: {e}")
            self._symbolic_world = None
    
    # GLYPH Engine Interface
    def encode_concept(self, concept: str, emotion: Optional[Dict[str, float]] = None) -> GlyphResult:
        """
        Encode a concept into GLYPH representation for symbolic communication.
        
        Args:
            concept: The concept to encode
            emotion: Optional emotional context (VAD model)
            
        Returns:
            GlyphResult with encoded symbol and metadata
        """
        if not CORE_ACTIVE or not self._glyph_engine:
            return GlyphResult(
                glyph_id="",
                symbol="",
                concept=concept,
                success=False,
                metadata={"error": "GLYPH engine not available"}
            )
        
        try:
            glyph_repr = self._glyph_engine.encode_concept(concept, emotion)
            glyph_obj = self._glyph_engine.decode_glyph(glyph_repr)
            
            return GlyphResult(
                glyph_id=glyph_obj.id if glyph_obj else "",
                symbol=glyph_obj.symbol if glyph_obj else "⚡",
                concept=concept,
                success=True,
                metadata={
                    "glyph_repr": glyph_repr,
                    "emotion": emotion,
                    "trinity_context": self._trinity_context
                }
            )
        except Exception as e:
            logger.error(f"Concept encoding failed: {e}")
            return GlyphResult(
                glyph_id="",
                symbol="⚠️",
                concept=concept,
                success=False,
                metadata={"error": str(e)}
            )
    
    def create_trinity_glyph(self, emphasis: str = "balanced") -> GlyphResult:
        """
        Create a Trinity Framework glyph for LUKHAS AI operations.
        
        Args:
            emphasis: Trinity aspect to emphasize (identity, consciousness, guardian, balanced)
            
        Returns:
            GlyphResult with Trinity Framework symbol
        """
        if not CORE_ACTIVE or not self._glyph_engine:
            # Fallback Trinity creation
            symbol = self._trinity_context.get("framework", "⚛️🧠🛡️")
            return GlyphResult(
                glyph_id=f"trinity_{emphasis}",
                symbol=symbol,
                concept=f"Trinity Framework ({emphasis})",
                success=True,
                metadata={"fallback": True, "emphasis": emphasis}
            )
        
        try:
            glyph_obj = self._glyph_engine.create_trinity_glyph(emphasis)
            return GlyphResult(
                glyph_id=glyph_obj.id,
                symbol=glyph_obj.symbol,
                concept=f"Trinity Framework ({emphasis})",
                success=True,
                metadata={"emphasis": emphasis, "trinity_context": self._trinity_context}
            )
        except Exception as e:
            logger.error(f"Trinity glyph creation failed: {e}")
            return GlyphResult(
                glyph_id="",
                symbol="⚠️",
                concept="Trinity Framework",
                success=False,
                metadata={"error": str(e)}
            )
    
    # Symbolic Processing Interface
    def create_symbol(self, name: str, properties: Dict[str, Any]) -> bool:
        """
        Create a symbolic representation in the symbolic world.
        
        Args:
            name: Symbol name
            properties: Symbol properties and metadata
            
        Returns:
            Success status
        """
        if not CORE_ACTIVE or not self._symbolic_world:
            logger.warning("Symbolic processing not available")
            return False
        
        try:
            self._symbolic_world.create_symbol(name, properties)
            return True
        except Exception as e:
            logger.error(f"Symbol creation failed: {e}")
            return False
    
    def link_symbols(self, symbol1_name: str, symbol2_name: str, 
                    relationship_type: str, properties: Optional[Dict[str, Any]] = None) -> bool:
        """
        Create a relationship between symbols in the symbolic world.
        
        Args:
            symbol1_name: First symbol name
            symbol2_name: Second symbol name
            relationship_type: Type of relationship
            properties: Optional relationship properties
            
        Returns:
            Success status
        """
        if not CORE_ACTIVE or not self._symbolic_world:
            logger.warning("Symbolic processing not available")
            return False
        
        try:
            # Get symbol objects
            symbol1 = self._symbolic_world.symbols.get(symbol1_name)
            symbol2 = self._symbolic_world.symbols.get(symbol2_name)
            
            if not symbol1 or not symbol2:
                logger.error("One or both symbols not found")
                return False
            
            self._symbolic_world.link_symbols(symbol1, symbol2, relationship_type, properties or {})
            return True
        except Exception as e:
            logger.error(f"Symbol linking failed: {e}")
            return False
    
    def perform_symbolic_reasoning(self, symbol_name: str) -> SymbolicResult:
        """
        Perform symbolic reasoning on a symbol to derive conclusions.
        
        Args:
            symbol_name: Name of symbol to reason about
            
        Returns:
            SymbolicResult with reasoning conclusions and patterns
        """
        if not CORE_ACTIVE or not self._symbolic_world:
            return SymbolicResult(
                symbols=[],
                relationships=[],
                patterns=[],
                reasoning={},
                success=False
            )
        
        try:
            symbol = self._symbolic_world.symbols.get(symbol_name)
            if not symbol:
                return SymbolicResult(
                    symbols=[],
                    relationships=[],
                    patterns=[],
                    reasoning={"error": "Symbol not found"},
                    success=False
                )
            
            # Perform reasoning
            reasoning_result = self._symbolic_reasoner.reason(symbol)
            
            # Get related symbols
            related_symbols = self._symbolic_world.get_related_symbols(symbol)
            
            # Find patterns
            all_symbols = list(self._symbolic_world.symbols.values())
            patterns = self._symbolic_reasoner.find_patterns(all_symbols)
            
            return SymbolicResult(
                symbols=[s.name for s in related_symbols],
                relationships=[],  # TODO: Extract relationship data
                patterns=patterns,
                reasoning=reasoning_result,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Symbolic reasoning failed: {e}")
            return SymbolicResult(
                symbols=[],
                relationships=[],
                patterns=[],
                reasoning={"error": str(e)},
                success=False
            )
    
    # Actor System Interface
    def send_actor_message(self, actor_id: str, message: Any) -> bool:
        """
        Send a message to an actor in the actor system.
        
        Args:
            actor_id: Target actor identifier
            message: Message to send
            
        Returns:
            Success status
        """
        if not CORE_ACTIVE or not self._actor_system:
            logger.warning("Actor system not available")
            return False
        
        try:
            self._actor_system.send(actor_id, message)
            return True
        except Exception as e:
            logger.error(f"Actor message sending failed: {e}")
            return False
    
    def register_actor(self, actor_id: str, actor: Any) -> bool:
        """
        Register an actor in the actor system.
        
        Args:
            actor_id: Actor identifier
            actor: Actor instance
            
        Returns:
            Success status
        """
        if not CORE_ACTIVE or not self._actor_system:
            logger.warning("Actor system not available")
            return False
        
        try:
            self._actor_system.register(actor_id, actor)
            return True
        except Exception as e:
            logger.error(f"Actor registration failed: {e}")
            return False
    
    # System Status and Control
    def get_status(self) -> Dict[str, Any]:
        """Get current core system status and capabilities"""
        return {
            "status": self._status.value,
            "core_active": CORE_ACTIVE,
            "capabilities": {
                "glyph_engine": self._glyph_engine is not None,
                "actor_system": self._actor_system is not None,
                "symbolic_processing": self._symbolic_world is not None
            },
            "trinity_framework": self._trinity_context,
            "feature_flags": {
                "CORE_ACTIVE": CORE_ACTIVE,
                "GLYPH_ENGINE_ENABLED": GLYPH_ENGINE_ENABLED,
                "SYMBOLIC_PROCESSING_ENABLED": SYMBOLIC_PROCESSING_ENABLED,
                "ACTOR_SYSTEM_ENABLED": ACTOR_SYSTEM_ENABLED
            }
        }
    
    def restart_core(self) -> bool:
        """Restart the core system"""
        try:
            self._status = CoreStatus.INACTIVE
            self._glyph_engine = None
            self._actor_system = None
            self._symbolic_world = None
            
            if CORE_ACTIVE:
                self._initialize_core_system()
            
            return self._status == CoreStatus.ACTIVE
        except Exception as e:
            logger.error(f"Core restart failed: {e}")
            self._status = CoreStatus.ERROR
            return False


# Global core instance
_core_instance = None


def get_core() -> CoreWrapper:
    """Get the global Core wrapper instance"""
    global _core_instance
    if _core_instance is None:
        _core_instance = CoreWrapper()
    return _core_instance


# Convenience functions for common operations
def encode_concept(concept: str, emotion: Optional[Dict[str, float]] = None) -> GlyphResult:
    """Encode a concept using the global core instance"""
    return get_core().encode_concept(concept, emotion)


def create_trinity_glyph(emphasis: str = "balanced") -> GlyphResult:
    """Create a Trinity Framework glyph using the global core instance"""
    return get_core().create_trinity_glyph(emphasis)


def get_core_status() -> Dict[str, Any]:
    """Get core system status using the global core instance"""
    return get_core().get_status()


# Export public interface
__all__ = [
    "CoreWrapper",
    "GlyphResult", 
    "SymbolicResult",
    "CoreStatus",
    "get_core",
    "encode_concept",
    "create_trinity_glyph", 
    "get_core_status"
]