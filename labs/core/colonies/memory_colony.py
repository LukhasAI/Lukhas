"""
Enhanced Memory Colony - Full implementation with actual memory capabilities
Replaces the dummy implementation with real functionality
"""

import asyncio
import hashlib
import json
import logging
import time
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Any, Optional

from core.colonies.base_colony import BaseColony
from core.efficient_communication import MessagePriority
from core.swarm import SwarmAgent

logger = logging.getLogger(__name__)


class MemoryAgent(SwarmAgent):
    """Agent specialized in memory storage and retrieval."""

    def __init__(self, agent_id: str, memory_type: str = "general"):
        super().__init__(agent_id)
        self.memory_type = memory_type
        self.local_storage: dict[str, dict[str, Any]] = {}
        self.memory_index: dict[str, list[str]] = defaultdict(list)  # tag -> memory_ids
        self.access_log: deque = deque(maxlen=1000)

    async def store_memory(self, memory_id: str, content: dict[str, Any], tags: list[str]) -> bool:
        """Store a memory locally."""
        try:
            self.local_storage[memory_id] = {
                "content": content,
                "tags": tags,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "access_count": 0,
                "memory_type": self.memory_type,
            }

            # Update index
            for tag in tags:
                self.memory_index[tag].append(memory_id)

            return True
        except Exception as e:
            logger.error(f"Agent {self.agent_id} failed to store memory: {e}")
            return False

    async def retrieve_memory(self, memory_id: str) -> Optional[dict[str, Any]]:
        """Retrieve a memory by ID."""
        if memory_id in self.local_storage:
            memory = self.local_storage[memory_id]
            memory["access_count"] += 1
            self.access_log.append(
                {
                    "memory_id": memory_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "action": "retrieve",
                }
            )
            return memory
        return None

    async def search_by_tags(self, tags: list[str]) -> list[dict[str, Any]]:
        """Search memories by tags."""
        matching_ids = set()

        for tag in tags:
            if tag in self.memory_index:
                matching_ids.update(self.memory_index[tag])

        results = []
        for memory_id in matching_ids:
            memory = await self.retrieve_memory(memory_id)
            if memory:
                results.append(
                    {
                        "memory_id": memory_id,
                        "memory": memory,
                        "relevance": len(set(tags) & set(memory["tags"])) / len(tags),
                    }
                )

        # Sort by relevance
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results


class MemoryColony(BaseColony):
    """
    Enhanced Memory Colony with real storage, retrieval, and search capabilities.
    """

    def __init__(self, colony_id: str):
        super().__init__(
            colony_id,
            capabilities=[
                "memory",
                "storage",
                "retrieval",
                "search",
                "indexing",
            ],
        )

        # Memory agents by specialization
        self.memory_agents: dict[str, list[MemoryAgent]] = {
            "episodic": [],
            "semantic": [],
            "procedural": [],
            "working": [],
        }

        # Global memory index
        self.global_index: dict[str, list[tuple[str, str]]] = defaultdict(list)  # tag -> [(agent_id, memory_id)]

        # Memory statistics
        self.stats = {
            "total_memories": 0,
            "total_retrievals": 0,
            "total_searches": 0,
            "avg_retrieval_time": 0.0,
        }

        # Replication settings
        self.replication_factor = 3

    async def start(self):
        """Start the memory colony with specialized agents."""
        await super().start()

        # Create memory agents
        await self._initialize_memory_agents()

        # Subscribe to memory events
        self.comm_fabric.subscribe_to_events("memory_request", self._handle_memory_request)

        logger.info(f"MemoryColony {self.colony_id} started with {len(self.agents)} agents")

    async def _initialize_memory_agents(self):
        """Initialize specialized memory agents."""
        agent_configs = [
            ("episodic", 3),  # 3 agents for episodic memory
            ("semantic", 3),  # 3 for semantic
            ("procedural", 2),  # 2 for procedural
            ("working", 2),  # 2 for working memory
        ]

        for memory_type, count in agent_configs:
            for i in range(count):
                agent_id = f"{self.colony_id}-{memory_type}-{i}"
                agent = MemoryAgent(agent_id, memory_type)

                self.agents[agent_id] = agent
                self.memory_agents[memory_type].append(agent)

        logger.info(f"Initialized {len(self.agents)} memory agents")

    async def execute_task(self, task_id: str, task_data: dict[str, Any]) -> dict[str, Any]:
        """Execute memory-related tasks with real functionality."""

        task_type = task_data.get("type", "unknown")
        start_time = time.time()

        try:
            if task_type == "store":
                result = await self._store_memory(task_data)
            elif task_type == "retrieve":
                result = await self._retrieve_memory(task_data)
            elif task_type == "search":
                result = await self._search_memories(task_data)
            elif task_type == "forget":
                result = await self._forget_memory(task_data)
            elif task_type == "consolidate":
                result = await self._consolidate_memories(task_data)
            else:
                result = {
                    "status": "error",
                    "message": f"Unknown task type: {task_type}",
                }

            # Update statistics
            elapsed = time.time() - start_time
            self._update_stats(task_type, elapsed, result.get("status") == "completed")

            result["task_id"] = task_id
            result["execution_time"] = elapsed

            return result

        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            return {"status": "failed", "task_id": task_id, "error": str(e)}

    async def _store_memory(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """Store a memory with replication."""
        content = task_data.get("content", {})
        tags = task_data.get("tags", [])
        memory_type = task_data.get("memory_type", "semantic")
        importance = task_data.get("importance", 0.5)

        # Generate memory ID
        memory_id = self._generate_memory_id(content)

        # Determine replication based on importance
        replication = max(
            1,
            min(
                self.replication_factor,
                int(importance * self.replication_factor),
            ),
        )

        # Select agents for storage
        agents = self._select_storage_agents(memory_type, replication)

        # Store in parallel
        storage_tasks = []
        for agent in agents:
            task = agent.store_memory(memory_id, content, tags)
            storage_tasks.append(task)

        results = await asyncio.gather(*storage_tasks)

        # Update global index if any storage succeeded
        if any(results):
            for agent, success in zip(agents, results):
                if success:
                    for tag in tags:
                        self.global_index[tag].append((agent.agent_id, memory_id))

            self.stats["total_memories"] += 1

            return {
                "status": "completed",
                "memory_id": memory_id,
                "replicas": sum(results),
                "memory_type": memory_type,
            }
        else:
            return {
                "status": "failed",
                "error": "Failed to store in any agent",
            }

    async def _retrieve_memory(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """Retrieve a memory by ID."""
        memory_id = task_data.get("memory_id")

        if not memory_id:
            return {"status": "error", "message": "No memory_id provided"}

        # Try to retrieve from any agent that has it
        for agent_id, agent in self.agents.items():
            memory = await agent.retrieve_memory(memory_id)
            if memory:
                self.stats["total_retrievals"] += 1
                return {
                    "status": "completed",
                    "memory": memory,
                    "retrieved_from": agent_id,
                }

        return {"status": "not_found", "memory_id": memory_id}

    async def _search_memories(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """Search memories by tags or content."""
        tags = task_data.get("tags", [])
        task_data.get("query", "")
        limit = task_data.get("limit", 10)
        memory_type = task_data.get("memory_type")  # Optional filter

        # Collect results from all relevant agents
        all_results = []

        agents_to_search = []
        if memory_type and memory_type in self.memory_agents:
            agents_to_search = self.memory_agents[memory_type]
        else:
            agents_to_search = list(self.agents.values())

        # Search in parallel
        search_tasks = []
        for agent in agents_to_search:
            if isinstance(agent, MemoryAgent):
                task = agent.search_by_tags(tags)
                search_tasks.append((agent.agent_id, task))

        # Gather results
        for agent_id, task in search_tasks:
            try:
                results = await task
                for result in results:
                    result["agent_id"] = agent_id
                    all_results.append(result)
            except Exception as e:
                logger.error(f"Search failed for agent {agent_id}: {e}")

        # Deduplicate and sort by relevance
        seen_memories = set()
        unique_results = []

        for result in sorted(all_results, key=lambda x: x["relevance"], reverse=True):
            memory_id = result["memory_id"]
            if memory_id not in seen_memories:
                seen_memories.add(memory_id)
                unique_results.append(result)

                if len(unique_results) >= limit:
                    break

        self.stats["total_searches"] += 1

        return {
            "status": "completed",
            "results": unique_results,
            "total_found": len(unique_results),
        }

    async def _forget_memory(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """Remove a memory from all agents."""
        memory_id = task_data.get("memory_id")

        if not memory_id:
            return {"status": "error", "message": "No memory_id provided"}

        removed_count = 0

        for agent in self.agents.values():
            if isinstance(agent, MemoryAgent) and memory_id in agent.local_storage:
                # Remove from storage
                memory = agent.local_storage.pop(memory_id)

                # Remove from index
                for tag in memory.get("tags", []):
                    if tag in agent.memory_index and memory_id in agent.memory_index[tag]:
                        agent.memory_index[tag].remove(memory_id)

                removed_count += 1

        # Update global index
        for tag, entries in list(self.global_index.items()):
            self.global_index[tag] = [(aid, mid) for aid, mid in entries if mid != memory_id]
            if not self.global_index[tag]:
                del self.global_index[tag]

        if removed_count > 0:
            self.stats["total_memories"] -= 1

        return {
            "status": "completed",
            "memory_id": memory_id,
            "removed_from": removed_count,
        }

    async def _consolidate_memories(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """Consolidate similar memories to save space."""
        memory_type = task_data.get("memory_type", "semantic")
        task_data.get("similarity_threshold", 0.8)

        # This is a simplified consolidation - in reality would use embeddings
        consolidated_count = 0

        # Get all memories of the specified type
        memories_by_content = defaultdict(list)

        for agent in self.memory_agents.get(memory_type, []):
            for memory_id, memory in agent.local_storage.items():
                # Create a simple content hash for grouping
                content_str = json.dumps(memory["content"], sort_keys=True)
                content_hash = hashlib.sha256(content_str.encode()).hexdigest()[:8]
                memories_by_content[content_hash].append((agent, memory_id, memory))

        # Consolidate duplicates
        for content_hash, memory_list in memories_by_content.items():
            if len(memory_list) > 1:
                # Keep the most accessed memory
                memory_list.sort(key=lambda x: x[2]["access_count"], reverse=True)
                memory_list[0]

                # Remove duplicates
                for agent, memory_id, memory in memory_list[1:]:
                    if memory_id in agent.local_storage:
                        del agent.local_storage[memory_id]
                        consolidated_count += 1

        return {
            "status": "completed",
            "consolidated": consolidated_count,
            "memory_type": memory_type,
        }

    def _generate_memory_id(self, content: dict[str, Any]) -> str:
        """Generate a unique memory ID."""
        content_str = json.dumps(content, sort_keys=True)
        timestamp = str(time.time())
        hash_input = f"{content_str}:{timestamp}:{self.colony_id}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    def _select_storage_agents(self, memory_type: str, count: int) -> list[MemoryAgent]:
        """Select agents for storing a memory."""
        available_agents = self.memory_agents.get(memory_type, [])

        if not available_agents:
            # Fallback to any available agents
            available_agents = [a for a in self.agents.values() if isinstance(a, MemoryAgent)]

        # Round-robin selection
        selected = []
        for i in range(min(count, len(available_agents))):
            selected.append(available_agents[i % len(available_agents)])

        return selected

    def _update_stats(self, operation: str, elapsed_time: float, success: bool):
        """Update colony statistics."""
        if success:
            # Update average retrieval time
            if operation == "retrieve":
                current_avg = self.stats["avg_retrieval_time"]
                total_retrievals = self.stats["total_retrievals"]
                new_avg = (current_avg * total_retrievals + elapsed_time) / (total_retrievals + 1)
                self.stats["avg_retrieval_time"] = new_avg

    async def _handle_memory_request(self, message):
        """Handle incoming memory requests from other colonies."""
        request_type = message.payload.get("request_type")

        if request_type == "cross_colony_search":
            # Handle search requests from other colonies
            result = await self._search_memories(message.payload)

            await self.comm_fabric.send_message(
                message.sender_id,
                "memory_response",
                result,
                MessagePriority.NORMAL,
            )

    async def get_statistics(self) -> dict[str, Any]:
        """Get detailed colony statistics."""
        agent_stats = {}

        for agent_id, agent in self.agents.items():
            if isinstance(agent, MemoryAgent):
                agent_stats[agent_id] = {
                    "memory_count": len(agent.local_storage),
                    "memory_type": agent.memory_type,
                    "total_accesses": sum(m["access_count"] for m in agent.local_storage.values()),
                }

        return {
            **self.stats,
            "agent_stats": agent_stats,
            "total_tags": len(self.global_index),
            "memory_distribution": {
                mt: sum(len(a.local_storage) for a in agents) for mt, agents in self.memory_agents.items()
            },
        }


# Example usage showing the enhanced capabilities


async def demo_enhanced_memory_colony():
    """Demonstrate the enhanced memory colony."""

    colony = MemoryColony("enhanced-memory")
    await colony.start()

    try:
        # Store some memories
        memories = [
            {
                "type": "store",
                "content": {
                    "event": "System initialization",
                    "details": "Colony started",
                },
                "tags": ["system", "startup", "milestone"],
                "memory_type": "episodic",
                "importance": 0.9,
            },
            {
                "type": "store",
                "content": {
                    "concept": "Colony",
                    "definition": "Group of collaborative agents",
                },
                "tags": ["concept", "architecture", "core"],
                "memory_type": "semantic",
                "importance": 0.8,
            },
            {
                "type": "store",
                "content": {
                    "skill": "memory_storage",
                    "steps": ["receive", "index", "store"],
                },
                "tags": ["skill", "procedure", "memory"],
                "memory_type": "procedural",
                "importance": 0.7,
            },
        ]

        stored_ids = []
        for i, memory_task in enumerate(memories):
            result = await colony.execute_task(f"store-{i}", memory_task)
            print(f"Stored memory: {result}")
            if result["status"] == "completed":
                stored_ids.append(result["memory_id"])

        # Search memories
        search_result = await colony.execute_task(
            "search-1",
            {"type": "search", "tags": ["system", "core"], "limit": 5},
        )
        print(f"\nSearch results: {search_result}")

        # Retrieve specific memory
        if stored_ids:
            retrieve_result = await colony.execute_task("retrieve-1", {"type": "retrieve", "memory_id": stored_ids[0]})
            print(f"\nRetrieved memory: {retrieve_result}")

        # Get statistics
        stats = await colony.get_statistics()
        print(f"\nColony statistics: {stats}")

    finally:
        await colony.stop()


if __name__ == "__main__":
    asyncio.run(demo_enhanced_memory_colony())
