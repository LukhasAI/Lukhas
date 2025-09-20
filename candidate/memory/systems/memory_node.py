"""
Memory Node

Responsible for storing and retrieving memories.
Supports encrypted, traceable, and evolving memory logs.

Design inspired by:
- Apple's privacy-focused approach to personal data
- OpenAI's sophisticated vector-based memory architectures
"""
from typing import List
from typing import Dict
import random
import streamlit as st

import hashlib
import logging
import time
import uuid
from collections import deque
from typing import Any, Optional

import numpy as np

from candidate.core.common import get_logger

logger = get_logger(__name__)


class MemoryNode:
    """
    Responsible for storing and retrieving memories.
    Implements a multi-tiered memory system with short-term, working, and long-term memory.
    """

    def __init__(self, agi_system):
        """
        Initialize the memory node

        Args:
            agi_system: Reference to the main Cognitive system
        """
        self.agi = agi_system
        self.logger = logging.getLogger("MemoryNode")

        # Memory systems
        self.short_term_memory = deque(maxlen=100)  # Recent memories
        self.working_memory = []  # Current context memories
        self.long_term_memory = []  # Important memories
        self.memory_embeddings = []  # For semantic search

        # Memory encryption (simulation)
        self.encryption_enabled = True
        self.encryption_key = self._generate_encryption_key()

        # Memory statistics
        self.stats = {
            "total_memories": 0,
            "short_term_accesses": 0,
            "long_term_accesses": 0,
            "successful_retrievals": 0,
            "failed_retrievals": 0,
        }

        logger.info("Memory Node initialized")

    def store(
        self,
        data: dict[str, Any],
        memory_type: str = "default",
        metadata: Optional[dict[str, Any]] = None,
        encrypt: bool = True,
    ) -> str:
        """
        Store a new memory entry

        Args:
            data: Memory data to store
            memory_type: Type of memory ("user_input", "system_output", "internal", etc.)
            metadata: Additional metadata
            encrypt: Whether to encrypt sensitive data

        Returns:
            Memory ID
        """
        # Generate a unique ID
        memory_id = f"mem_{int(time.time())}_{str(uuid.uuid4()}[:8]}"

        # Prepare metadata
        metadata = metadata or {}
        metadata.update(
            {
                "created_at": time.time(),
                "memory_type": memory_type,
                "encrypted": encrypt and self.encryption_enabled,
            }
        )

        # Calculate importance
        importance = self._calculate_importance(data, metadata)

        # Create the memory entry
        memory_entry = {
            "id": memory_id,
            "data": (self._encrypt_data(data) if encrypt and self.encryption_enabled else data),
            "metadata": metadata,
            "importance": importance,
            "access_count": 0,
            "last_accessed": None,
        }

        # Store in appropriate memory systems
        self.short_term_memory.append(memory_entry)

        # If memory is important, also store in long-term memory
        if importance > 0.7:
            self.long_term_memory.append(memory_entry)
            # In a real implementation, we would compute embeddings here
            embedding = self._generate_embedding(data)
            self.memory_embeddings.append({"memory_id": memory_id, "embedding": embedding})

        # Update stats
        self.stats["total_memories"] += 1

        logger.debug(f"Stored new memory: {memory_id} (type: {memory_type}, importance: {importance:.2f})")
        return memory_id

    def retrieve(self, memory_id: str) -> Optional[dict[str, Any]]:
        """
        Retrieve a specific memory by ID

        Args:
            memory_id: ID of the memory to retrieve

        Returns:
            Memory entry if found, None otherwise
        """
        # Check short-term memory
        for memory in self.short_term_memory:
            if memory["id"] == memory_id:
                self._update_memory_access(memory)
                self.stats["short_term_accesses"] += 1
                self.stats["successful_retrievals"] += 1
                return self._prepare_memory_for_return(memory)

        # Check working memory
        for memory in self.working_memory:
            if memory["id"] == memory_id:
                self._update_memory_access(memory)
                self.stats["successful_retrievals"] += 1
                return self._prepare_memory_for_return(memory)

        # Check long-term memory
        for memory in self.long_term_memory:
            if memory["id"] == memory_id:
                self._update_memory_access(memory)
                self.stats["long_term_accesses"] += 1
                self.stats["successful_retrievals"] += 1
                return self._prepare_memory_for_return(memory)

        self.stats["failed_retrievals"] += 1
        logger.warning(f"Memory not found: {memory_id}")
        return None

    def retrieve_recent(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        Retrieve the most recent memories

        Args:
            limit: Maximum number of memories to retrieve

        Returns:
            List of recent memory entries
        """
        recent = list(self.short_term_memory)[-limit:]

        # Update access statistics
        for memory in recent:
            self._update_memory_access(memory)

        self.stats["short_term_accesses"] += len(recent)
        self.stats["successful_retrievals"] += len(recent)

        return [self._prepare_memory_for_return(memory) for memory in recent]

    def retrieve_by_type(self, memory_type: str, limit: int = 10) -> list[dict[str, Any]]:
        """
        Retrieve memories of a specific type

        Args:
            memory_type: Type of memories to retrieve
            limit: Maximum number of memories to retrieve

        Returns:
            List of matching memory entries
        """
        # First check short-term memory (most recent)
        matches = []
        for memory in reversed(list(self.short_term_memory)):
            if memory["metadata"].get("memory_type") == memory_type:
                matches.append(memory)
                if len(matches) >= limit:
                    break

        # If we need more, check long-term memory
        if len(matches) < limit:
            for memory in reversed(self.long_term_memory):
                if (
                    memory["id"] not in [m["id"] for m in matches]
                    and memory["metadata"].get("memory_type") == memory_type
                ):
                    matches.append(memory)
                    if len(matches) >= limit:
                        break

        # Update access statistics
        for memory in matches:
            self._update_memory_access(memory)

        self.stats["successful_retrievals"] += len(matches)

        return [self._prepare_memory_for_return(memory) for memory in matches]

    def semantic_search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """
        Search for memories semantically related to the query

        Args:
            query: Search query
            limit: Maximum number of results to return

        Returns:
            List of semantically relevant memory entries
        """
        if not self.memory_embeddings:
            return []

        # Generate query embedding
        query_embedding = self._generate_embedding({"text": query})

        # Calculate similarity with all memory embeddings
        similarities = []
        for _idx, embedding_data in enumerate(self.memory_embeddings):
            similarity = self._calculate_similarity(query_embedding, embedding_data["embedding"])
            similarities.append((similarity, embedding_data["memory_id"]))

        # Sort by similarity (descending)
        similarities.sort(reverse=True)

        # Get top matches
        results = []
        for similarity, memory_id in similarities[:limit]:
            memory = self.retrieve(memory_id)
            if memory:
                memory["relevance"] = float(similarity)
                results.append(memory)

        return results

    def forget(self, memory_id: str) -> bool:
        """
        Remove a memory from all systems

        Args:
            memory_id: ID of the memory to remove

        Returns:
            True if memory was removed, False otherwise
        """
        removed = False

        # Check and remove from short-term memory
        self.short_term_memory = deque(
            [m for m in self.short_term_memory if m["id"] != memory_id],
            maxlen=self.short_term_memory.maxlen,
        )

        # Check and remove from working memory
        working_before = len(self.working_memory)
        self.working_memory = [m for m in self.working_memory if m["id"] != memory_id]
        if working_before > len(self.working_memory):
            removed = True

        # Check and remove from long-term memory
        long_term_before = len(self.long_term_memory)
        self.long_term_memory = [m for m in self.long_term_memory if m["id"] != memory_id]
        if long_term_before > len(self.long_term_memory):
            removed = True

            # Also remove from embeddings
            self.memory_embeddings = [e for e in self.memory_embeddings if e["memory_id"] != memory_id]

        if removed:
            logger.info(f"Removed memory: {memory_id}")
        else:
            logger.warning(f"Memory not found for removal: {memory_id}")

        return removed

    def add_to_working_memory(self, memory_id: str) -> bool:
        """
        Add a memory to working memory for current context

        Args:
            memory_id: ID of the memory to add

        Returns:
            True if memory was added, False otherwise
        """
        memory = self.retrieve(memory_id)
        if not memory:
            return False

        # Check if already in working memory
        for existing in self.working_memory:
            if existing["id"] == memory_id:
                return True

        # Add to working memory
        self.working_memory.append(memory)

        # Limit working memory size
        if len(self.working_memory) > 20:
            # Remove least important memory
            least_important = min(self.working_memory, key=lambda m: m["importance"])
            self.working_memory.remove(least_important)

        logger.debug(f"Added memory {memory_id} to working memory")
        return True

    def clear_working_memory(self) -> None:
        """Clear all items from working memory"""
        count = len(self.working_memory)
        self.working_memory = []
        logger.info(f"Cleared {count} items from working memory")

    def update_memory(
        self,
        memory_id: str,
        data: Optional[dict[str, Any]] = None,
        metadata: Optional[dict[str, Any]] = None,
        importance: Optional[float] = None,
    ) -> bool:
        """
        Update an existing memory

        Args:
            memory_id: ID of the memory to update
            data: New data (if None, keeps existing)
            metadata: New metadata to merge (if None, keeps existing)
            importance: New importance score (if None, keeps existing)

        Returns:
            True if memory was updated, False otherwise
        """
        memory = None

        # Find memory in all systems
        for mem_system in [
            self.short_term_memory,
            self.working_memory,
            self.long_term_memory,
        ]:
            for mem in mem_system:
                if mem["id"] == memory_id:
                    memory = mem
                    break
            if memory:
                break

        if not memory:
            logger.warning(f"Memory not found for update: {memory_id}")
            return False

        # Update fields
        if data is not None:
            memory["data"] = self._encrypt_data(data) if memory["metadata"].get("encrypted", False) else data

        if metadata is not None:
            memory["metadata"].update(metadata)

        if importance is not None:
            memory["importance"] = importance

            # Check if memory should be in long-term memory based on new importance
            in_long_term = any(m["id"] == memory_id for m in self.long_term_memory)

            if importance > 0.7 and not in_long_term:
                # Add to long-term memory
                self.long_term_memory.append(memory)
                # Generate and add embedding
                embedding = self._generate_embedding(
                    self._decrypt_data(memory["data"]) if memory["metadata"].get("encrypted", False) else memory["data"]
                )
                self.memory_embeddings.append({"memory_id": memory_id, "embedding": embedding})
            elif importance <= 0.7 and in_long_term:
                # Remove from long-term memory
                self.long_term_memory = [m for m in self.long_term_memory if m["id"] != memory_id]
                self.memory_embeddings = [e for e in self.memory_embeddings if e["memory_id"] != memory_id]

        # Add update timestamp
        memory["metadata"]["updated_at"] = time.time()

        logger.debug(f"Updated memory: {memory_id}")
        return True

    def get_memory_stats(self) -> dict[str, Any]:
        """
        Get memory system statistics

        Returns:
            Dictionary with memory statistics
        """
        return {
            "total_memories": self.stats["total_memories"],
            "short_term_count": len(self.short_term_memory),
            "working_memory_count": len(self.working_memory),
            "long_term_count": len(self.long_term_memory),
            "access_stats": {
                "short_term_accesses": self.stats["short_term_accesses"],
                "long_term_accesses": self.stats["long_term_accesses"],
                "successful_retrievals": self.stats["successful_retrievals"],
                "failed_retrievals": self.stats["failed_retrievals"],
            },
            "encryption_enabled": self.encryption_enabled,
        }

    def _calculate_importance(self, data: dict[str, Any], metadata: dict[str, Any]) -> float:
        """
        Calculate the importance of a memory for long-term storage

        Args:
            data: Memory data
            metadata: Memory metadata

        Returns:
            Importance score between 0 and 1
        """
        importance = 0.5  # Default importance

        # Memory type can affect importance
        memory_type = metadata.get("memory_type", "default")
        if memory_type == "user_input":
            importance += 0.1  # User inputs are slightly more important
        elif memory_type == "system_decision":
            importance += 0.2  # System decisions are more important
        elif memory_type == "error":
            importance += 0.3  # Errors are highly important

        # If it contains an error or warning, increase importance
        data_str = str(data).lower()
        if any(key in data_str for key in ["error", "warning", "fail"]):
            importance += 0.2

        # If it's a successful interaction, slightly increase importance
        if "result" in data and data.get("result", {}).get("status") == "success":
            importance += 0.1

        # If data is complex (lots of fields), it might be more important
        if isinstance(data, dict) and len(data) > 5:
            importance += 0.1

        return min(1.0, importance)

    def _generate_embedding(self, data: dict[str, Any]) -> np.ndarray:
        """
        Generate an embedding vector for memory data

        Args:
            data: Memory data

        Returns:
            Embedding vector
        """
        # In a real implementation, this would use a proper embedding model
        # For simulation, generate a random but deterministic embedding based on data

        # Convert data to a string representation
        data_str = str(data)

        # Use hash of data string as seed for random generator
        seed = int(hashlib.sha256(data_str.encode()).hexdigest(), 16) % (2**32)
        np.random.seed(seed)

        # Generate a 128-dimensional embedding
        embedding = np.random.rand(128)

        # Normalize to unit length
        embedding = embedding / np.linalg.norm(embedding)

        return embedding

    def _calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings

        Args:
            embedding1: First embedding
            embedding2: Second embedding

        Returns:
            Similarity score between -1 and 1
        """
        return np.dot(embedding1, embedding2)

    def _generate_encryption_key(self) -> bytes:
        """Generate an encryption key for memory encryption"""
        # In a real implementation, this would use proper key management
        # For simulation, generate a random key
        return hashlib.sha256(str(uuid.uuid4()).encode()).digest()

    def _encrypt_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Encrypt sensitive memory data

        Args:
            data: Data to encrypt

        Returns:
            Data with sensitive fields encrypted
        """
        # In a real implementation, this would use proper encryption
        # For simulation, we'll just mark the data as encrypted

        # Make a copy of the data
        encrypted_data = {}

        for key, value in data.items():
            # Determine if field should be encrypted
            if key in ["personal_info", "user_data", "credentials", "private"]:
                encrypted_data[key] = {
                    "__encrypted": True,
                    "data": f"ENCRYPTED:{value}",
                }
            else:
                encrypted_data[key] = value

        return encrypted_data

    def _decrypt_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Decrypt encrypted memory data

        Args:
            data: Data to decrypt

        Returns:
            Decrypted data
        """
        # In a real implementation, this would use proper decryption
        # For simulation, we'll just remove the encryption marking

        # Make a copy of the data
        decrypted_data = {}

        for key, value in data.items():
            if isinstance(value, dict) and value.get("__encrypted"):
                # Extract original value from the encrypted data
                encrypted_str = value.get("data", "")
                if encrypted_str.startswith("ENCRYPTED:"):
                    decrypted_data[key] = encrypted_str[10:]  # Remove "ENCRYPTED:" prefix
                else:
                    decrypted_data[key] = encrypted_str
            else:
                decrypted_data[key] = value

        return decrypted_data

    def _update_memory_access(self, memory: dict[str, Any]) -> None:
        """Update memory access statistics"""
        memory["access_count"] = memory.get("access_count", 0) + 1
        memory["last_accessed"] = time.time()

    def _prepare_memory_for_return(self, memory: dict[str, Any]) -> dict[str, Any]:
        """
        Prepare a memory for returning to the caller

        Args:
            memory: Memory entry to prepare

        Returns:
            Prepared memory entry
        """
        result = memory.copy()

        # Decrypt data if encrypted
        if memory["metadata"].get("encrypted", False):
            result["data"] = self._decrypt_data(memory["data"])

        return result

    def process_message(self, message_type: str, payload: Any, from_node: str) -> None:
        """
        Process a message from another node

        Args:
            message_type: Type of the message
            payload: Message payload
            from_node: ID of the node that sent the message
        """
        logger.debug(f"Received message of type {message_type} from {from_node}")

        # Handle different message types
        if message_type == "store_memory":
            # Store new memory
            try:
                data = payload.get("data", {})
                memory_type = payload.get("memory_type", "default")
                metadata = payload.get("metadata", {})
                encrypt = payload.get("encrypt", True)

                memory_id = self.store(data, memory_type, metadata, encrypt)
                logger.debug(f"Stored memory from message: {memory_id}")

                # Could respond with the memory ID if needed
            except Exception as e:
                logger.error(f"Error storing memory from message: {e}")

        elif message_type == "retrieve_memory":
            # Retrieve memory
            memory_id = payload.get("memory_id")
            if memory_id:
                self.retrieve(memory_id)
                # Would need to send response message with memory

        elif message_type == "semantic_search":
            # Perform semantic search
            query = payload.get("query")
            limit = payload.get("limit", 5)

            if query:
                self.semantic_search(query, limit)
                # Would need to send response message with results