#!/usr/bin/env python3
"""

#TAG:memory
#TAG:folds
#TAG:neuroplastic
#TAG:colony


Memory Services
Dependency injection services for the memory module.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from hub.service_registry import get_service, inject_services


class MemoryService:
    """
    Service layer for memory operations.
    Uses dependency injection to avoid circular imports.
    """

    def __init__(self):
        # Core memory components
        self._storage = {}  # Simple in-memory storage
        self._index = {}    # Index for fast retrieval

        # Services will be injected as needed
        self._identity = None
        self._initialized = False

    def _ensure_services(self):
        """Lazy load services to avoid circular imports"""
        if not self._initialized:
            try:
                self._identity = get_service('identity_service')
            except KeyError:
                self._identity = None

            self._initialized = True

    @inject_services(identity='identity_service')
    async def store(self,
                   agent_id: str,
                   memory_data: Dict[str, Any],
                   memory_type: str = "experience",
                   identity=None) -> Dict[str, Any]:
        """
        Store a memory with injected dependencies.
        """
        # Verify access through identity service
        if identity:
            if not await identity.verify_access(agent_id, "memory.write"):
                raise PermissionError(f"Agent {agent_id} lacks memory write access")

        # Create memory entry
        memory_id = f"{agent_id}_{datetime.now().timestamp()}"
        memory_entry = {
            "id": memory_id,
            "agent_id": agent_id,
            "type": memory_type,
            "data": memory_data,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "version": 1,
                "indexed": False
            }
        }

        # Store in memory
        if agent_id not in self._storage:
            self._storage[agent_id] = []

        self._storage[agent_id].append(memory_entry)

        # Update index
        self._update_index(agent_id, memory_entry)

        # Log if identity service available
        if identity:
            await identity.log_audit(agent_id, "memory.store", {"memory_id": memory_id})

        return {
            "memory_id": memory_id,
            "stored": True,
            "timestamp": memory_entry["timestamp"]
        }

    def _update_index(self, agent_id: str, memory_entry: Dict[str, Any]):
        """Update memory index for fast retrieval"""
        if agent_id not in self._index:
            self._index[agent_id] = {
                "by_type": {},
                "by_time": []
            }

        # Index by type
        mem_type = memory_entry["type"]
        if mem_type not in self._index[agent_id]["by_type"]:
            self._index[agent_id]["by_type"][mem_type] = []

        self._index[agent_id]["by_type"][mem_type].append(memory_entry["id"])

        # Index by time
        self._index[agent_id]["by_time"].append({
            "id": memory_entry["id"],
            "timestamp": memory_entry["timestamp"]
        })

    async def retrieve(self,
                      agent_id: str,
                      query: Optional[Dict[str, Any]] = None,
                      limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve memories based on query.
        """
        self._ensure_services()

        # Check access
        if self._identity:
            if not await self._identity.verify_access(agent_id, "memory.read"):
                raise PermissionError(f"Agent {agent_id} lacks memory read access")

        if agent_id not in self._storage:
            return []

        memories = self._storage[agent_id]

        # Apply query filters
        if query:
            if "type" in query:
                memories = [m for m in memories if m["type"] == query["type"]]

            if "after" in query:
                memories = [m for m in memories if m["timestamp"] > query["after"]]

            if "before" in query:
                memories = [m for m in memories if m["timestamp"] < query["before"]]

        # Sort by timestamp (most recent first)
        memories.sort(key=lambda m: m["timestamp"], reverse=True)

        # Apply limit
        return memories[:limit]

    async def consolidate(self,
                         agent_id: str,
                         consolidation_type: str = "fold") -> Dict[str, Any]:
        """
        Consolidate memories using specified strategy.
        """
        if agent_id not in self._storage:
            return {"consolidated": False, "reason": "No memories found"}

        memories = self._storage[agent_id]

        if consolidation_type == "fold":
            # Memory folding - compress similar memories
            consolidated = await self._fold_memories(memories)
        elif consolidation_type == "summarize":
            # Summarization - create summary memories
            consolidated = await self._summarize_memories(memories)
        else:
            consolidated = {"error": f"Unknown consolidation type: {consolidation_type}"}

        return {
            "consolidated": True,
            "type": consolidation_type,
            "original_count": len(memories),
            "result": consolidated
        }

    async def _fold_memories(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fold similar memories together"""
        # Group by type
        by_type = {}
        for mem in memories:
            mem_type = mem["type"]
            if mem_type not in by_type:
                by_type[mem_type] = []
            by_type[mem_type].append(mem)

        # Create folded representations
        folded = {}
        for mem_type, mems in by_type.items():
            folded[mem_type] = {
                "count": len(mems),
                "first": mems[0]["timestamp"] if mems else None,
                "last": mems[-1]["timestamp"] if mems else None,
                "summary": f"Folded {len(mems)} {mem_type} memories"
            }

        return folded

    async def _summarize_memories(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create summary of memories"""
        return {
            "total_memories": len(memories),
            "types": list(set(m["type"] for m in memories)),
            "time_span": {
                "start": min(m["timestamp"] for m in memories) if memories else None,
                "end": max(m["timestamp"] for m in memories) if memories else None
            },
            "summary": "Memory summary placeholder"
        }

    # Specific convenience methods used by other services

    async def store_experience(self, agent_id: str, experience: Dict[str, Any]) -> Dict[str, Any]:
        """Store an experience memory"""
        return await self.store(agent_id, experience, "experience")

    async def store_learning_outcome(self, agent_id: str, outcome: Dict[str, Any]) -> Dict[str, Any]:
        """Store a learning outcome"""
        return await self.store(agent_id, outcome, "learning_outcome")

    async def store_creation(self, agent_id: str, creation: Dict[str, Any]) -> Dict[str, Any]:
        """Store a creative output"""
        return await self.store(agent_id, creation, "creation")

    async def retrieve_context(self, agent_id: str, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve context memories for a query"""
        # Simplified - in real implementation would use semantic search
        return await self.retrieve(agent_id, {"type": "experience"}, limit)

    async def retrieve_learning_context(self, agent_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve learning-specific context"""
        return await self.retrieve(agent_id, {"type": "learning_outcome"}, limit)

    async def get_learning_history(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get full learning history"""
        return await self.retrieve(agent_id, {"type": "learning_outcome"}, limit=1000)

    async def consolidate_meta_learning(self, package: Dict[str, Any]) -> Dict[str, Any]:
        """Consolidate meta-learning cycle"""
        agent_id = package.get("metadata", {}).get("agent_id", "unknown")
        return await self.store(agent_id, package, "meta_learning_cycle")

    async def query_meta_learning_history(self, agent_id: str) -> List[Dict[str, Any]]:
        """Query meta-learning history"""
        return await self.retrieve(agent_id, {"type": "meta_learning_cycle"}, limit=100)


# Create service factory
def create_memory_service():
    """Factory function for memory service"""
    service = MemoryService()

    # Could initialize with actual memory backend here
    try:
        from memory.core import MemoryCore
        service.core = MemoryCore()
    except ImportError:
        service.core = None

    return service


# Register with hub on import
from hub.service_registry import register_factory

register_factory(
    'memory_service',
    create_memory_service,
    {
        "module": "memory",
        "provides": ["storage", "retrieval", "consolidation"]
    }
)