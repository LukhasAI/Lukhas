"""
Tagging System Module
Symbolic tagging and resolution system for LUKHAS consciousness

⚛️🧠🛡️ Trinity Framework: Identity-Consciousness-Guardian
"""

import logging
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class TagScope(Enum):
    """Scope levels for symbolic tags"""
    LOCAL = "local"
    COLONY = "colony"
    GLOBAL = "global"
    CONSCIOUSNESS = "consciousness"
    TRINITY = "trinity"

class TagPriority(Enum):
    """Priority levels for tag resolution"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    TRINITY = 5

@dataclass
class SymbolicTag:
    """Represents a symbolic tag with metadata"""
    key: str
    value: Any
    scope: TagScope
    priority: TagPriority
    metadata: Dict[str, Any]
    created_timestamp: float
    
class SimpleTagResolver:
    """Simple tag resolution system for consciousness coordination"""
    
    def __init__(self):
        self.tags: Dict[str, SymbolicTag] = {}
        self.tag_hierarchy: Dict[str, Set[str]] = {}
        self.resolution_cache: Dict[str, Any] = {}
        
    def register_tag(self, tag: SymbolicTag) -> bool:
        """Register a symbolic tag in the system"""
        try:
            self.tags[tag.key] = tag
            logger.debug(f"🏷️ Registered tag: {tag.key} = {tag.value}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to register tag {tag.key}: {e}")
            return False
            
    def resolve_tag(self, key: str, default: Any = None) -> Any:
        """Resolve a tag value by key"""
        if key in self.resolution_cache:
            return self.resolution_cache[key]
            
        if key in self.tags:
            tag = self.tags[key]
            self.resolution_cache[key] = tag.value
            return tag.value
            
        logger.debug(f"🏷️ Tag not found: {key}, using default: {default}")
        return default
        
    def resolve_tags_by_scope(self, scope: TagScope) -> Dict[str, Any]:
        """Resolve all tags within a specific scope"""
        result = {}
        for key, tag in self.tags.items():
            if tag.scope == scope:
                result[key] = tag.value
        return result
        
    def resolve_tags_by_priority(self, min_priority: TagPriority) -> Dict[str, Any]:
        """Resolve tags with priority >= min_priority"""
        result = {}
        for key, tag in self.tags.items():
            if tag.priority.value >= min_priority.value:
                result[key] = tag.value
        return result
        
    def clear_cache(self) -> None:
        """Clear the resolution cache"""
        self.resolution_cache.clear()
        logger.debug("🏷️ Tag resolution cache cleared")
        
    def get_tag_count(self) -> int:
        """Get total number of registered tags"""
        return len(self.tags)
        
    def get_tag_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific tag"""
        if key in self.tags:
            return self.tags[key].metadata
        return None

class AdvancedTagResolver(SimpleTagResolver):
    """Advanced tag resolver with consciousness integration"""
    
    def __init__(self):
        super().__init__()
        self.consciousness_tags: Set[str] = set()
        self.trinity_tags: Set[str] = set()
        
    def register_consciousness_tag(self, tag: SymbolicTag) -> bool:
        """Register a consciousness-aware tag"""
        if self.register_tag(tag):
            if tag.scope == TagScope.CONSCIOUSNESS:
                self.consciousness_tags.add(tag.key)
            elif tag.scope == TagScope.TRINITY:
                self.trinity_tags.add(tag.key)
            return True
        return False
        
    def resolve_consciousness_context(self) -> Dict[str, Any]:
        """Resolve all consciousness-related tags"""
        context = {}
        for tag_key in self.consciousness_tags:
            if tag_key in self.tags:
                context[tag_key] = self.tags[tag_key].value
        return context
        
    def resolve_trinity_context(self) -> Dict[str, Any]:
        """Resolve Trinity Framework tags"""
        context = {}
        for tag_key in self.trinity_tags:
            if tag_key in self.tags:
                context[tag_key] = self.tags[tag_key].value
        return context

# Module-level convenience functions
def create_tag(key: str, value: Any, scope: TagScope = TagScope.LOCAL, 
               priority: TagPriority = TagPriority.MEDIUM) -> SymbolicTag:
    """Create a symbolic tag with default metadata"""
    import time
    return SymbolicTag(
        key=key,
        value=value,
        scope=scope,
        priority=priority,
        metadata={},
        created_timestamp=time.time()
    )

def quick_resolve(resolver: SimpleTagResolver, key: str, default: Any = None) -> Any:
    """Quick tag resolution helper"""
    return resolver.resolve_tag(key, default)

# Export main components
__all__ = [
    'SymbolicTag',
    'TagScope',
    'TagPriority', 
    'SimpleTagResolver',
    'AdvancedTagResolver',
    'create_tag',
    'quick_resolve'
]
