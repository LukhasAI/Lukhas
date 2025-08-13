"""
LUKHAS AI Memory - Colony System
Distributed memory across colony nodes
Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ColonyRole(Enum):
    """Roles for memory colony nodes"""
    COORDINATOR = "coordinator"
    STORAGE = "storage"
    PROCESSOR = "processor"
    CACHE = "cache"
    BACKUP = "backup"

@dataclass
class ColonyNode:
    """Represents a memory colony node"""
    id: str
    role: ColonyRole
    capacity: int
    load: float = 0.0
    active: bool = True
    memories: Dict[str, Any] = None

class MemoryColony:
    """Manages distributed memory across colony nodes"""
    
    def __init__(self):
        self.nodes: Dict[str, ColonyNode] = {}
        self.routing_table: Dict[str, str] = {}  # memory_id -> node_id
        self.replication_factor = 3
        self._init_default_nodes()
    
    def _init_default_nodes(self):
        """Initialize default colony nodes"""
        # Create coordinator node
        self.add_node(ColonyNode(
            id="coordinator-1",
            role=ColonyRole.COORDINATOR,
            capacity=1000,
            memories={}
        ))
        
        # Create storage nodes
        for i in range(3):
            self.add_node(ColonyNode(
                id=f"storage-{i+1}",
                role=ColonyRole.STORAGE,
                capacity=10000,
                memories={}
            ))
        
        # Create cache node
        self.add_node(ColonyNode(
            id="cache-1",
            role=ColonyRole.CACHE,
            capacity=100,
            memories={}
        ))
    
    def add_node(self, node: ColonyNode):
        """Add a node to the colony"""
        self.nodes[node.id] = node
    
    def store_memory(self, memory_id: str, content: Any) -> List[str]:
        """Store memory across colony nodes"""
        # Find suitable nodes based on load
        storage_nodes = [n for n in self.nodes.values() 
                        if n.role == ColonyRole.STORAGE and n.active]
        
        # Sort by load
        storage_nodes.sort(key=lambda n: n.load)
        
        # Store in multiple nodes for redundancy
        stored_nodes = []
        for i, node in enumerate(storage_nodes[:self.replication_factor]):
            if node.memories is None:
                node.memories = {}
            
            node.memories[memory_id] = content
            node.load = len(node.memories) / node.capacity
            stored_nodes.append(node.id)
            
            # Update routing table
            self.routing_table[memory_id] = node.id
        
        return stored_nodes
    
    def retrieve_memory(self, memory_id: str) -> Optional[Any]:
        """Retrieve memory from colony"""
        # Check cache first
        cache_nodes = [n for n in self.nodes.values() 
                      if n.role == ColonyRole.CACHE and n.active]
        
        for node in cache_nodes:
            if node.memories and memory_id in node.memories:
                return node.memories[memory_id]
        
        # Check routing table
        if memory_id in self.routing_table:
            node_id = self.routing_table[memory_id]
            if node := self.nodes.get(node_id):
                if node.memories and memory_id in node.memories:
                    # Add to cache
                    self._cache_memory(memory_id, node.memories[memory_id])
                    return node.memories[memory_id]
        
        # Search all storage nodes
        for node in self.nodes.values():
            if node.role == ColonyRole.STORAGE and node.memories:
                if memory_id in node.memories:
                    return node.memories[memory_id]
        
        return None
    
    def _cache_memory(self, memory_id: str, content: Any):
        """Add memory to cache"""
        cache_nodes = [n for n in self.nodes.values() 
                      if n.role == ColonyRole.CACHE]
        
        if cache_nodes:
            cache = cache_nodes[0]
            if cache.memories is None:
                cache.memories = {}
            
            # Simple LRU: remove oldest if at capacity
            if len(cache.memories) >= cache.capacity:
                oldest = next(iter(cache.memories))
                del cache.memories[oldest]
            
            cache.memories[memory_id] = content
    
    def get_colony_status(self) -> Dict[str, Any]:
        """Get colony health status"""
        return {
            "total_nodes": len(self.nodes),
            "active_nodes": sum(1 for n in self.nodes.values() if n.active),
            "total_memories": sum(len(n.memories or {}) for n in self.nodes.values()),
            "average_load": sum(n.load for n in self.nodes.values()) / len(self.nodes),
            "replication_factor": self.replication_factor
        }

# Singleton instance
_colony = None

def get_memory_colony() -> MemoryColony:
    """Get or create memory colony singleton"""
    global _colony
    if _colony is None:
        _colony = MemoryColony()
    return _colony
