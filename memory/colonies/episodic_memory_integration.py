"""
Episodic Memory Colony Integration Module
Provides integration wrapper for connecting the episodic memory colony to the memory hub
"""
import logging

import uuid
from datetime import datetime
from typing import Any, Optional

from core.common import get_logger

try:
    from .episodic_memory_colony import (
        EpisodicMemoryColony,
        EpisodicMemoryRecord,
    )

    EPISODIC_COLONY_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Episodic memory colony not available: {e}")
    EPISODIC_COLONY_AVAILABLE = False

    # Create fallback mock classes
    class EpisodicMemoryColony:
        def __init__(self, *args, **kwargs):
            self.initialized = False

    class EpisodicMemoryRecord:
        def __init__(self, *args, **kwargs):
            pass


logger = get_logger(__name__)


class EpisodicMemoryIntegration:
    """
    Integration wrapper for the Episodic Memory Colony System.
    Provides a simplified interface for the memory hub.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize the episodic memory integration"""
        self.config = config or {
            "max_concurrent_operations": 50,
            "memory_capacity": 10000,
            "enable_background_processing": True,
            "replay_processing_interval": 2.0,
            "consolidation_assessment_interval": 30.0,
            "pattern_separation_threshold": 0.3,
            "pattern_completion_threshold": 0.7,
            "enable_autobiographical_significance": True,
            "enable_emotional_processing": True,
        }

        # Initialize the episodic memory colony
        if EPISODIC_COLONY_AVAILABLE:
            self.colony = EpisodicMemoryColony(
                colony_id="episodic_memory_colony",
                max_concurrent_operations=self.config.get(
                    "max_concurrent_operations", 50
                ),
                memory_capacity=self.config.get("memory_capacity", 10000),
            )
        else:
            logger.warning("Using mock implementation for episodic memory colony")
            self.colony = EpisodicMemoryColony()

        self.is_initialized = False
        self.episode_registry = {}
        self.replay_metrics = {
            "total_replays": 0,
            "successful_replays": 0,
            "consolidation_events": 0,
        }

        logger.info(
            "EpisodicMemoryIntegration initialized with config: %s", self.config
        )

    async def initialize(self):
        """Initialize the episodic memory integration system"""
        if self.is_initialized:
            return

        try:
            logger.info("Initializing episodic memory integration...")

            # Initialize the colony if available
            if EPISODIC_COLONY_AVAILABLE and hasattr(self.colony, "initialize"):
                await self.colony.initialize()
                logger.info("Episodic memory colony initialized")

            # Setup memory processing systems
            await self._initialize_processing_systems()

            # Setup performance monitoring
            await self._initialize_monitoring()

            self.is_initialized = True
            logger.info("Episodic memory integration initialization complete")

        except Exception as e:
            logger.error(f"Failed to initialize episodic memory integration: {e}")
            raise

    async def _initialize_processing_systems(self):
        """Initialize episodic memory processing system"""
        logger.info("Initializing episodic processing systems...")

        # Configure colony settings if available
        if EPISODIC_COLONY_AVAILABLE and hasattr(
            self.colony, "pattern_separation_threshold"
        ):
            self.colony.pattern_separation_threshold = self.config.get(
                "pattern_separation_threshold", 0.3
            )
            self.colony.pattern_completion_threshold = self.config.get(
                "pattern_completion_threshold", 0.7
            )

        logger.info("Episodic processing systems initialized")

    async def _initialize_monitoring(self):
        """Initialize performance monitoring"""
        logger.info("Initializing episodic memory monitoring...")

        # Setup monitoring metrics
        self.performance_metrics = {
            "episodes_created": 0,
            "episodes_retrieved": 0,
            "episodes_replayed": 0,
            "consolidation_ready": 0,
            "average_significance": 0.0,
            "last_activity": datetime.now().isoformat(),
        }

        logger.info("Episodic memory monitoring initialized")

    async def create_episodic_memory(
        self,
        content: dict[str, Any],
        event_type: str = "general",
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Create a new episodic memory

        Args:
            content: Memory content
            event_type: Type of event/episode
            context: Episodic context information

        Returns:
            Dict containing creation result with memory ID
        """
        if not self.is_initialized:
            await self.initialize()

        try:
            # Create memory operation if colony is available
            if EPISODIC_COLONY_AVAILABLE and hasattr(
                self.colony, "_create_episodic_memory"
            ):
                # Create mock operation object
                operation = self._create_mock_operation(
                    operation_type="create",
                    content=content,
                    event_type=event_type,
                    context=context,
                )

                response = await self.colony._create_episodic_memory(operation)

                if hasattr(response, "success") and response.success:
                    memory_id = getattr(response, "memory_id", str(uuid.uuid4()))

                    # Store in local registry
                    self.episode_registry[memory_id] = {
                        "content": content,
                        "event_type": event_type,
                        "context": context or {},
                        "created_at": datetime.now().isoformat(),
                        "access_count": 0,
                    }

                    # Update metrics
                    self.performance_metrics["episodes_created"] += 1
                    self.performance_metrics["last_activity"] = (
                        datetime.now().isoformat()
                    )

                    logger.info(f"Episodic memory created: {memory_id}")
                    return {
                        "success": True,
                        "memory_id": memory_id,
                        "event_type": event_type,
                        "created_at": datetime.now().isoformat(),
                    }

            # Fallback creation
            return await self._fallback_create_episode(content, event_type, context)

        except Exception as e:
            logger.error(f"Error creating episodic memory: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def retrieve_episodic_memory(
        self, memory_id: str, include_related: bool = False
    ) -> dict[str, Any]:
        """
        Retrieve episodic memory by ID

        Args:
            memory_id: Memory identifier
            include_related: Whether to include related episodes

        Returns:
            Dict containing memory content and metadata
        """
        if not self.is_initialized:
            await self.initialize()

        try:
            # Retrieve from colony if available
            if EPISODIC_COLONY_AVAILABLE and hasattr(
                self.colony, "_read_episodic_memory"
            ):
                operation = self._create_mock_operation(
                    operation_type="read",
                    memory_id=memory_id,
                    parameters={"include_related": include_related},
                )

                response = await self.colony._read_episodic_memory(operation)

                if hasattr(response, "success") and response.success:
                    content = getattr(response, "content", {})

                    # Update local registry access count
                    if memory_id in self.episode_registry:
                        self.episode_registry[memory_id]["access_count"] += 1

                    # Update metrics
                    self.performance_metrics["episodes_retrieved"] += 1
                    self.performance_metrics["last_activity"] = (
                        datetime.now().isoformat()
                    )

                    return {
                        "success": True,
                        "memory_id": memory_id,
                        "content": content,
                        "retrieved_at": datetime.now().isoformat(),
                    }

            # Fallback retrieval
            return await self._fallback_retrieve_episode(memory_id)

        except Exception as e:
            logger.error(f"Error retrieving episodic memory: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def search_episodic_memories(
        self, query: dict[str, Any], limit: int = 50
    ) -> list[dict[str, Any]]:
        """
        Search episodic memories

        Args:
            query: Search query parameters
            limit: Maximum number of results

        Returns:
            List of matching episodic memories
        """
        if not self.is_initialized:
            await self.initialize()

        try:
            if EPISODIC_COLONY_AVAILABLE and hasattr(
                self.colony, "_search_episodic_memories"
            ):
                operation = self._create_mock_operation(
                    operation_type="search", content=query, parameters={"limit": limit}
                )

                response = await self.colony._search_episodic_memories(operation)

                if hasattr(response, "success") and response.success:
                    results = getattr(response, "content", [])

                    # Update metrics
                    self.performance_metrics["last_activity"] = (
                        datetime.now().isoformat()
                    )

                    return results

            # Fallback search
            return await self._fallback_search_episodes(query, limit)

        except Exception as e:
            logger.error(f"Error searching episodic memories: {e}")
            return []

    async def trigger_episode_replay(
        self, memory_ids: Optional[list[str]] = None, replay_strength: float = 1.0
    ) -> dict[str, Any]:
        """
        Trigger replay of episodic memories for consolidation

        Args:
            memory_ids: Specific memory IDs to replay (optional)
            replay_strength: Strength of replay processing

        Returns:
            Dict containing replay results
        """
        if not self.is_initialized:
            await self.initialize()

        try:
            if EPISODIC_COLONY_AVAILABLE and hasattr(
                self.colony, "_trigger_episodic_replay"
            ):
                operation = self._create_mock_operation(
                    operation_type="replay",
                    parameters={
                        "memory_ids": memory_ids or [],
                        "replay_strength": replay_strength,
                    },
                )

                response = await self.colony._trigger_episodic_replay(operation)

                if hasattr(response, "success") and response.success:
                    replayed_memories = getattr(response, "content", [])

                    # Update metrics
                    self.replay_metrics["total_replays"] += len(replayed_memories)
                    self.replay_metrics["successful_replays"] += len(replayed_memories)
                    self.performance_metrics["episodes_replayed"] += len(
                        replayed_memories
                    )
                    self.performance_metrics["last_activity"] = (
                        datetime.now().isoformat()
                    )

                    logger.info(
                        f"Episode replay completed: {len(replayed_memories)} memories"
                    )
                    return {
                        "success": True,
                        "replayed_count": len(replayed_memories),
                        "replayed_memories": replayed_memories,
                        "timestamp": datetime.now().isoformat(),
                    }

            # Fallback replay
            return await self._fallback_trigger_replay(memory_ids, replay_strength)

        except Exception as e:
            logger.error(f"Error triggering episode replay: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def get_consolidation_candidates(self) -> list[dict[str, Any]]:
        """
        Get episodes ready for consolidation

        Returns:
            List of consolidation-ready episodes
        """
        if not self.is_initialized:
            await self.initialize()

        try:
            candidates = []

            if EPISODIC_COLONY_AVAILABLE and hasattr(
                self.colony, "consolidation_candidates"
            ):
                candidate_ids = getattr(self.colony, "consolidation_candidates", [])

                for memory_id in candidate_ids:
                    if hasattr(self.colony, "episodic_records"):
                        records = getattr(self.colony, "episodic_records", {})
                        if memory_id in records:
                            record = records[memory_id]
                            candidates.append(
                                {
                                    "memory_id": memory_id,
                                    "consolidation_readiness": getattr(
                                        record, "consolidation_readiness", 0.0
                                    ),
                                    "personal_significance": getattr(
                                        record, "personal_significance", 0.0
                                    ),
                                    "replay_count": getattr(record, "replay_count", 0),
                                    "last_accessed": getattr(
                                        record, "last_accessed", 0
                                    ),
                                }
                            )
            else:
                # Fallback - return mock candidates
                candidates = self._get_fallback_consolidation_candidates()

            # Update metrics
            self.performance_metrics["consolidation_ready"] = len(candidates)

            return candidates

        except Exception as e:
            logger.error(f"Error getting consolidation candidates: {e}")
            return []

    async def get_episodic_metrics(self) -> dict[str, Any]:
        """
        Get episodic memory processing metrics

        Returns:
            Dict containing processing metrics
        """
        if not self.is_initialized:
            await self.initialize()

        try:
            # Get colony-specific metrics if available
            colony_metrics = {}
            if EPISODIC_COLONY_AVAILABLE and hasattr(self.colony, "episodic_records"):
                records = getattr(self.colony, "episodic_records", {})
                if records:
                    significances = [
                        getattr(r, "personal_significance", 0.0)
                        for r in records.values()
                    ]
                    colony_metrics = {
                        "total_episodes": len(records),
                        "average_significance": (
                            sum(significances) / len(significances)
                            if significances
                            else 0.0
                        ),
                        "replay_queue_size": len(
                            getattr(self.colony, "replay_queue", [])
                        ),
                        "consolidation_candidates": len(
                            getattr(self.colony, "consolidation_candidates", [])
                        ),
                    }

            # Combine all metrics
            metrics = {
                **self.performance_metrics,
                **self.replay_metrics,
                **colony_metrics,
                "system_status": "active",
                "episodic_colony_available": EPISODIC_COLONY_AVAILABLE,
                "episode_registry_size": len(self.episode_registry),
                "last_updated": datetime.now().isoformat(),
            }

            return metrics

        except Exception as e:
            logger.error(f"Error getting episodic metrics: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    def _create_mock_operation(self, operation_type: str, **kwargs):
        """Create a mock operation object for colony interaction"""

        class MockOperation:
            def __init__(self, operation_type: str, **kwargs):
                self.operation_type = operation_type
                self.operation_id = str(uuid.uuid4())
                self.memory_id = kwargs.get("memory_id")
                self.content = kwargs.get("content")
                self.parameters = kwargs.get("parameters", {})
                self.metadata = kwargs.get("metadata", {})

                # Add event type to content if provided
                if "event_type" in kwargs:
                    if isinstance(self.content, dict):
                        self.content["event_type"] = kwargs["event_type"]

                # Add context to content if provided
                if "context" in kwargs:
                    if isinstance(self.content, dict):
                        self.content["context"] = kwargs["context"]

        return MockOperation(operation_type, **kwargs)

    async def _fallback_create_episode(
        self,
        content: dict[str, Any],
        event_type: str,
        context: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        """Fallback episode creation when colony is not available"""
        memory_id = str(uuid.uuid4())

        self.episode_registry[memory_id] = {
            "content": content,
            "event_type": event_type,
            "context": context or {},
            "created_at": datetime.now().isoformat(),
            "access_count": 0,
            "personal_significance": 0.5,
            "replay_count": 0,
        }

        logger.info(f"Fallback episodic memory created: {memory_id}")
        return {
            "success": True,
            "memory_id": memory_id,
            "event_type": event_type,
            "created_at": datetime.now().isoformat(),
            "fallback": True,
        }

    async def _fallback_retrieve_episode(self, memory_id: str) -> dict[str, Any]:
        """Fallback episode retrieval"""
        if memory_id in self.episode_registry:
            episode = self.episode_registry[memory_id]
            episode["access_count"] += 1

            return {
                "success": True,
                "memory_id": memory_id,
                "content": episode,
                "retrieved_at": datetime.now().isoformat(),
                "fallback": True,
            }
        else:
            return {
                "success": False,
                "error": "Episode not found",
                "timestamp": datetime.now().isoformat(),
            }

    async def _fallback_search_episodes(
        self, query: dict[str, Any], limit: int
    ) -> list[dict[str, Any]]:
        """Fallback episode search"""
        results = []

        for memory_id, episode in self.episode_registry.items():
            # Simple matching based on event type or content
            if "event_type" in query:
                if episode.get("event_type") == query["event_type"]:
                    results.append(
                        {
                            "memory_id": memory_id,
                            "content": episode,
                            "relevance_score": 0.8,
                        }
                    )
            elif "text" in query:
                query_text = query["text"].lower()
                episode_text = str(episode.get("content", "")).lower()
                if query_text in episode_text:
                    results.append(
                        {
                            "memory_id": memory_id,
                            "content": episode,
                            "relevance_score": 0.6,
                        }
                    )

        return results[:limit]

    async def _fallback_trigger_replay(
        self, memory_ids: Optional[list[str]], replay_strength: float
    ) -> dict[str, Any]:
        """Fallback replay triggering"""
        if not memory_ids:
            # Select top episodes for replay
            episodes_by_significance = sorted(
                self.episode_registry.items(),
                key=lambda x: x[1].get("personal_significance", 0.0),
                reverse=True,
            )
            memory_ids = [mid for mid, _ in episodes_by_significance[:5]]

        replayed_count = 0
        for memory_id in memory_ids:
            if memory_id in self.episode_registry:
                # SYNTAX_ERROR_FIXED:
                # self.episode_registry[memory_id]['replay_count'] = " +
                # "self.episode_registry[memory_id].get('replay_count', 0) + 1
                replayed_count += 1

        return {
            "success": True,
            "replayed_count": replayed_count,
            "timestamp": datetime.now().isoformat(),
            "fallback": True,
        }

    def _get_fallback_consolidation_candidates(self) -> list[dict[str, Any]]:
        """Get fallback consolidation candidate"""
        candidates = []

        for memory_id, episode in self.episode_registry.items():
            if (
                episode.get("replay_count", 0) >= 2
                and episode.get("personal_significance", 0.0) > 0.5
            ):
                candidates.append(
                    {
                        "memory_id": memory_id,
                        "consolidation_readiness": 0.7,
                        "personal_significance": episode.get(
                            "personal_significance", 0.5
                        ),
                        "replay_count": episode.get("replay_count", 0),
                        "last_accessed": episode.get(
                            "created_at", datetime.now().isoformat()
                        ),
                    }
                )

        return candidates[:10]


# Factory function for creating the integration
def create_episodic_memory_integration(
    config: Optional[dict[str, Any]] = None,
) -> EpisodicMemoryIntegration:
    """Create and return an episodic memory integration instance"""
    return EpisodicMemoryIntegration(config)