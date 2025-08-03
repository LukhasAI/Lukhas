"""
Memory System Integration Connector

This module provides integration between the LUKHAS identity system and the
AGI memory systems, enabling identity-anchored memory storage and retrieval.

Features:
- Identity-linked memory storage
- Biographical memory integration
- Authentication memory patterns
- Memory-based identity verification
- Consciousness-memory synchronization

Author: LUKHAS Identity Team
Version: 1.0.0
"""

import hashlib
import json
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from core.common import get_logger
from datetime import datetime, timedelta

logger = logging.getLogger('LUKHAS_MEMORY_CONNECTOR')


class MemoryType(Enum):
    """Types of memories in the identity system"""
    BIOGRAPHICAL = "biographical"           # Life events and experiences
    AUTHENTICATION = "authentication"      # Authentication patterns and history
    EMOTIONAL = "emotional"                # Emotional anchors and patterns
    SYMBOLIC = "symbolic"                  # Personal symbols and meanings
    BIOMETRIC = "biometric"                # Biometric templates and patterns
    CONSCIOUSNESS = "consciousness"        # Consciousness states and patterns
    DREAM = "dream"                       # Dream patterns and content
    CULTURAL = "cultural"                 # Cultural context and preferences


class MemoryAccessLevel(Enum):
    """Access levels for memory data"""
    PUBLIC = "public"                      # Publicly accessible
    PROTECTED = "protected"                # Requires authentication
    PRIVATE = "private"                    # Requires high-level auth
    SACRED = "sacred"                      # Highest protection level


@dataclass
class MemoryRecord:
    """A record stored in the memory system"""
    memory_id: str
    lambda_id: str
    memory_type: MemoryType
    access_level: MemoryAccessLevel
    content: Dict[str, Any]
    emotional_weight: float               # 0.0 to 1.0
    consciousness_markers: Dict[str, float]
    creation_timestamp: datetime
    last_accessed: datetime
    access_count: int
    integrity_hash: str
    encryption_level: str
    expiry_date: Optional[datetime] = None


@dataclass
class MemoryQuery:
    """Query for memory retrieval"""
    lambda_id: str
    memory_types: List[MemoryType]
    access_level: MemoryAccessLevel
    temporal_range: Optional[Tuple[datetime, datetime]] = None
    emotional_range: Optional[Tuple[float, float]] = None
    consciousness_filters: Optional[Dict[str, Any]] = None
    content_keywords: Optional[List[str]] = None
    max_results: int = 100


@dataclass
class MemoryIntegrationResult:
    """Result of memory integration operation"""
    success: bool
    operation_type: str
    memory_id: Optional[str] = None
    records_affected: int = 0
    memory_records: List[MemoryRecord] = None
    integration_metadata: Dict[str, Any] = None
    error_message: Optional[str] = None


class MemoryConnector:
    """
    Memory System Integration Connector

    Provides integration between identity system and AGI memory systems
    for identity-anchored memory operations.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

        # Memory storage (in production, this would connect to actual memory system)
        self.memory_store: Dict[str, List[MemoryRecord]] = {}  # lambda_id -> memories

        # Memory access patterns for identity verification
        self.access_patterns: Dict[str, List[Dict[str, Any]]] = {}

        # Integration with memory systems
        self.memory_systems = {
            "biographical": self._get_biographical_connector(),
            "authentication": self._get_authentication_connector(),
            "consciousness": self._get_consciousness_connector()
        }

        # Encryption keys for memory protection
        self.memory_encryption_keys: Dict[str, bytes] = {}

        logger.info("Memory Connector initialized")

    def store_identity_memory(self, lambda_id: str, memory_data: Dict[str, Any]) -> MemoryIntegrationResult:
        """
        Store identity-related memory

        Args:
            lambda_id: User's Lambda ID
            memory_data: Memory data to store

        Returns:
            MemoryIntegrationResult with operation result
        """
        try:
            # Validate memory data
            if not self._validate_memory_data(memory_data):
                return MemoryIntegrationResult(
                    success=False,
                    operation_type="store_memory",
                    error_message="Invalid memory data"
                )

            # Create memory record
            memory_record = self._create_memory_record(lambda_id, memory_data)

            # Encrypt sensitive content
            encrypted_record = self._encrypt_memory_record(memory_record)

            # Store in memory system
            if lambda_id not in self.memory_store:
                self.memory_store[lambda_id] = []
            self.memory_store[lambda_id].append(encrypted_record)

            # Update access patterns
            self._update_access_patterns(lambda_id, "store", memory_record.memory_type)

            # Integrate with external memory systems
            integration_results = self._integrate_with_external_memory(encrypted_record)

            logger.info(f"Stored memory {memory_record.memory_id} for {lambda_id}")

            return MemoryIntegrationResult(
                success=True,
                operation_type="store_memory",
                memory_id=memory_record.memory_id,
                records_affected=1,
                integration_metadata={
                    "memory_type": memory_record.memory_type.value,
                    "access_level": memory_record.access_level.value,
                    "emotional_weight": memory_record.emotional_weight,
                    "external_integrations": integration_results
                }
            )

        except Exception as e:
            logger.error(f"Memory storage error: {e}")
            return MemoryIntegrationResult(
                success=False,
                operation_type="store_memory",
                error_message=str(e)
            )

    def retrieve_identity_memories(self, query: MemoryQuery) -> MemoryIntegrationResult:
        """
        Retrieve identity memories based on query

        Args:
            query: Memory query parameters

        Returns:
            MemoryIntegrationResult with retrieved memories
        """
        try:
            # Get user's memories
            user_memories = self.memory_store.get(query.lambda_id, [])

            if not user_memories:
                return MemoryIntegrationResult(
                    success=True,
                    operation_type="retrieve_memories",
                    records_affected=0,
                    memory_records=[],
                    integration_metadata={"query_filters": self._serialize_query(query)}
                )

            # Apply filters
            filtered_memories = self._apply_memory_filters(user_memories, query)

            # Decrypt accessible memories
            decrypted_memories = []
            for memory in filtered_memories:
                if self._check_memory_access(memory, query.access_level):
                    decrypted_memory = self._decrypt_memory_record(memory)
                    if decrypted_memory:
                        decrypted_memories.append(decrypted_memory)

            # Update access patterns
            self._update_access_patterns(query.lambda_id, "retrieve", query.memory_types)

            # Sort by relevance
            sorted_memories = self._sort_memories_by_relevance(decrypted_memories, query)

            # Limit results
            final_memories = sorted_memories[:query.max_results]

            logger.info(f"Retrieved {len(final_memories)} memories for {query.lambda_id}")

            return MemoryIntegrationResult(
                success=True,
                operation_type="retrieve_memories",
                records_affected=len(final_memories),
                memory_records=final_memories,
                integration_metadata={
                    "total_found": len(filtered_memories),
                    "accessible": len(decrypted_memories),
                    "returned": len(final_memories),
                    "query_filters": self._serialize_query(query)
                }
            )

        except Exception as e:
            logger.error(f"Memory retrieval error: {e}")
            return MemoryIntegrationResult(
                success=False,
                operation_type="retrieve_memories",
                error_message=str(e)
            )

    def create_biographical_anchor(self, lambda_id: str, life_event: Dict[str, Any]) -> MemoryIntegrationResult:
        """
        Create biographical memory anchor for identity verification

        Args:
            lambda_id: User's Lambda ID
            life_event: Biographical event data

        Returns:
            MemoryIntegrationResult with anchor creation result
        """
        try:
            # Process biographical event
            biographical_data = {
                "type": "biographical_event",
                "event_type": life_event.get("event_type", "general"),
                "description": life_event.get("description", ""),
                "date": life_event.get("date"),
                "location": life_event.get("location"),
                "people_involved": life_event.get("people_involved", []),
                "emotional_impact": life_event.get("emotional_impact", 0.5),
                "significance_level": life_event.get("significance_level", 0.5),
                "verification_questions": life_event.get("verification_questions", []),
                "cultural_context": life_event.get("cultural_context")
            }

            # Create memory record
            memory_data = {
                "memory_type": MemoryType.BIOGRAPHICAL.value,
                "access_level": MemoryAccessLevel.PRIVATE.value,
                "content": biographical_data,
                "emotional_weight": biographical_data["emotional_impact"],
                "consciousness_markers": {
                    "significance": biographical_data["significance_level"],
                    "clarity": life_event.get("memory_clarity", 0.8),
                    "confidence": life_event.get("confidence", 0.8)
                }
            }

            # Store as memory
            result = self.store_identity_memory(lambda_id, memory_data)

            if result.success:
                # Create verification anchor
                self._create_verification_anchor(lambda_id, result.memory_id, biographical_data)

                logger.info(f"Created biographical anchor for {lambda_id}")

            return result

        except Exception as e:
            logger.error(f"Biographical anchor creation error: {e}")
            return MemoryIntegrationResult(
                success=False,
                operation_type="create_biographical_anchor",
                error_message=str(e)
            )

    def verify_biographical_memory(self, lambda_id: str, verification_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify identity using biographical memory

        Args:
            lambda_id: User's Lambda ID
            verification_data: Data for verification

        Returns:
            Verification result
        """
        try:
            # Retrieve biographical memories
            query = MemoryQuery(
                lambda_id=lambda_id,
                memory_types=[MemoryType.BIOGRAPHICAL],
                access_level=MemoryAccessLevel.PRIVATE
            )

            memories_result = self.retrieve_identity_memories(query)

            if not memories_result.success or not memories_result.memory_records:
                return {
                    "verified": False,
                    "confidence": 0.0,
                    "error": "No biographical memories found"
                }

            # Match verification data against memories
            verification_scores = []

            for memory in memories_result.memory_records:
                if memory.memory_type == MemoryType.BIOGRAPHICAL:
                    score = self._calculate_biographical_match(
                        memory.content, verification_data
                    )
                    verification_scores.append(score)

            if not verification_scores:
                return {
                    "verified": False,
                    "confidence": 0.0,
                    "error": "No matching biographical data"
                }

            # Calculate overall verification confidence
            avg_score = sum(verification_scores) / len(verification_scores)
            max_score = max(verification_scores)

            # Weighted combination of average and max scores
            confidence = (avg_score * 0.6) + (max_score * 0.4)

            # Verification threshold
            verified = confidence >= 0.7

            # Update access patterns
            self._update_access_patterns(lambda_id, "verify", [MemoryType.BIOGRAPHICAL])

            return {
                "verified": verified,
                "confidence": confidence,
                "memories_checked": len(memories_result.memory_records),
                "match_scores": verification_scores,
                "verification_method": "biographical_memory"
            }

        except Exception as e:
            logger.error(f"Biographical verification error: {e}")
            return {
                "verified": False,
                "confidence": 0.0,
                "error": str(e)
            }

    def get_authentication_patterns(self, lambda_id: str) -> Dict[str, Any]:
        """
        Get authentication patterns for identity analysis

        Args:
            lambda_id: User's Lambda ID

        Returns:
            Authentication patterns data
        """
        patterns = self.access_patterns.get(lambda_id, [])

        if not patterns:
            return {
                "patterns_available": False,
                "total_accesses": 0
            }

        # Analyze patterns
        memory_type_counts = {}
        operation_counts = {}
        temporal_patterns = []

        for pattern in patterns:
            # Count by memory type
            memory_types = pattern.get("memory_types", [])
            for mem_type in memory_types:
                memory_type_counts[mem_type] = memory_type_counts.get(mem_type, 0) + 1

            # Count by operation
            operation = pattern.get("operation", "unknown")
            operation_counts[operation] = operation_counts.get(operation, 0) + 1

            # Temporal patterns
            temporal_patterns.append({
                "timestamp": pattern.get("timestamp"),
                "operation": operation,
                "memory_types": memory_types
            })

        # Calculate usage statistics
        recent_patterns = [p for p in patterns if p.get("timestamp", 0) > time.time() - 86400]  # Last 24h

        return {
            "patterns_available": True,
            "total_accesses": len(patterns),
            "recent_accesses": len(recent_patterns),
            "memory_type_distribution": memory_type_counts,
            "operation_distribution": operation_counts,
            "temporal_patterns": temporal_patterns[-10:],  # Last 10 patterns
            "most_accessed_type": max(memory_type_counts.items(), key=lambda x: x[1])[0] if memory_type_counts else None,
            "average_daily_accesses": len(patterns) / max(1, (time.time() - patterns[0].get("timestamp", time.time())) / 86400) if patterns else 0
        }

    def _validate_memory_data(self, memory_data: Dict[str, Any]) -> bool:
        """Validate memory data structure"""
        required_fields = ["memory_type", "content"]
        return all(field in memory_data for field in required_fields)

    def _create_memory_record(self, lambda_id: str, memory_data: Dict[str, Any]) -> MemoryRecord:
        """Create memory record from data"""
        memory_id = hashlib.sha256(f"{lambda_id}_{time.time()}".encode()).hexdigest()[:16]

        # Create integrity hash
        content_hash = hashlib.sha256(
            json.dumps(memory_data["content"], sort_keys=True).encode()
        ).hexdigest()

        return MemoryRecord(
            memory_id=memory_id,
            lambda_id=lambda_id,
            memory_type=MemoryType(memory_data["memory_type"]),
            access_level=MemoryAccessLevel(memory_data.get("access_level", "protected")),
            content=memory_data["content"],
            emotional_weight=memory_data.get("emotional_weight", 0.5),
            consciousness_markers=memory_data.get("consciousness_markers", {}),
            creation_timestamp=datetime.now(),
            last_accessed=datetime.now(),
            access_count=0,
            integrity_hash=content_hash,
            encryption_level=memory_data.get("encryption_level", "standard")
        )

    def _encrypt_memory_record(self, record: MemoryRecord) -> MemoryRecord:
        """Encrypt sensitive memory record content"""
        # In full implementation, would use proper encryption
        # For now, just mark as encrypted
        encrypted_record = record
        encrypted_record.encryption_level = "encrypted"
        return encrypted_record

    def _decrypt_memory_record(self, record: MemoryRecord) -> Optional[MemoryRecord]:
        """Decrypt memory record for access"""
        # In full implementation, would decrypt content
        # For now, just return the record
        record.last_accessed = datetime.now()
        record.access_count += 1
        return record

    def _apply_memory_filters(self, memories: List[MemoryRecord], query: MemoryQuery) -> List[MemoryRecord]:
        """Apply query filters to memories"""
        filtered = memories

        # Filter by memory type
        if query.memory_types:
            filtered = [m for m in filtered if m.memory_type in query.memory_types]

        # Filter by temporal range
        if query.temporal_range:
            start_time, end_time = query.temporal_range
            filtered = [m for m in filtered if start_time <= m.creation_timestamp <= end_time]

        # Filter by emotional range
        if query.emotional_range:
            min_emotion, max_emotion = query.emotional_range
            filtered = [m for m in filtered if min_emotion <= m.emotional_weight <= max_emotion]

        # Filter by content keywords
        if query.content_keywords:
            keyword_filtered = []
            for memory in filtered:
                content_str = json.dumps(memory.content).lower()
                if any(keyword.lower() in content_str for keyword in query.content_keywords):
                    keyword_filtered.append(memory)
            filtered = keyword_filtered

        return filtered

    def _check_memory_access(self, memory: MemoryRecord, required_level: MemoryAccessLevel) -> bool:
        """Check if memory is accessible at required level"""
        access_hierarchy = {
            MemoryAccessLevel.PUBLIC: 0,
            MemoryAccessLevel.PROTECTED: 1,
            MemoryAccessLevel.PRIVATE: 2,
            MemoryAccessLevel.SACRED: 3
        }

        return access_hierarchy[required_level] >= access_hierarchy[memory.access_level]

    def _sort_memories_by_relevance(self, memories: List[MemoryRecord], query: MemoryQuery) -> List[MemoryRecord]:
        """Sort memories by relevance to query"""
        def relevance_score(memory):
            score = 0.0

            # Recent memories score higher
            days_old = (datetime.now() - memory.creation_timestamp).days
            recency_score = max(0, 1.0 - (days_old / 365))  # Decay over year
            score += recency_score * 0.3

            # Emotional weight
            score += memory.emotional_weight * 0.4

            # Access frequency
            access_score = min(1.0, memory.access_count / 10.0)
            score += access_score * 0.3

            return score

        return sorted(memories, key=relevance_score, reverse=True)

    def _update_access_patterns(self, lambda_id: str, operation: str, memory_types: Any):
        """Update access patterns for identity analysis"""
        if lambda_id not in self.access_patterns:
            self.access_patterns[lambda_id] = []

        # Convert memory_types to list of strings
        if isinstance(memory_types, list):
            type_list = [mt.value if hasattr(mt, 'value') else str(mt) for mt in memory_types]
        else:
            type_list = [memory_types.value if hasattr(memory_types, 'value') else str(memory_types)]

        pattern = {
            "timestamp": time.time(),
            "operation": operation,
            "memory_types": type_list
        }

        self.access_patterns[lambda_id].append(pattern)

        # Keep only recent patterns (last 1000)
        if len(self.access_patterns[lambda_id]) > 1000:
            self.access_patterns[lambda_id] = self.access_patterns[lambda_id][-1000:]

    def _integrate_with_external_memory(self, memory_record: MemoryRecord) -> Dict[str, Any]:
        """Integrate with external memory systems"""
        # Placeholder for external system integration
        return {
            "biographical_system": False,
            "consciousness_system": False,
            "inference_system": False
        }

    def _create_verification_anchor(self, lambda_id: str, memory_id: str, biographical_data: Dict[str, Any]):
        """Create verification anchor from biographical data"""
        # This would create verification questions and anchors
        # For identity verification based on biographical memories
        pass

    def _calculate_biographical_match(self, stored_data: Dict[str, Any], verification_data: Dict[str, Any]) -> float:
        """Calculate match score between stored and verification biographical data"""
        matches = 0
        total_checks = 0

        # Check event type
        if "event_type" in both_dicts(stored_data, verification_data):
            total_checks += 1
            if stored_data["event_type"] == verification_data["event_type"]:
                matches += 1

        # Check location
        if "location" in both_dicts(stored_data, verification_data):
            total_checks += 1
            if stored_data["location"].lower() == verification_data["location"].lower():
                matches += 1

        # Check date (allow some flexibility)
        if "date" in both_dicts(stored_data, verification_data):
            total_checks += 1
            # Simple date matching logic
            stored_date = str(stored_data["date"])
            verification_date = str(verification_data["date"])
            if stored_date == verification_date:
                matches += 1
            elif any(part in verification_date for part in stored_date.split("-")):
                matches += 0.5  # Partial match

        # Check people involved
        if "people_involved" in both_dicts(stored_data, verification_data):
            total_checks += 1
            stored_people = set(p.lower() for p in stored_data["people_involved"])
            verification_people = set(p.lower() for p in verification_data["people_involved"])

            if stored_people.intersection(verification_people):
                overlap = len(stored_people.intersection(verification_people))
                total = len(stored_people.union(verification_people))
                matches += overlap / total

        return matches / total_checks if total_checks > 0 else 0.0

    def _serialize_query(self, query: MemoryQuery) -> Dict[str, Any]:
        """Serialize query for metadata"""
        return {
            "memory_types": [mt.value for mt in query.memory_types],
            "access_level": query.access_level.value,
            "max_results": query.max_results,
            "has_temporal_filter": query.temporal_range is not None,
            "has_emotional_filter": query.emotional_range is not None,
            "has_keyword_filter": query.content_keywords is not None
        }

    def _get_biographical_connector(self):
        """Get biographical memory system connector"""
        # Placeholder for external biographical system
        return None

    def _get_authentication_connector(self):
        """Get authentication memory system connector"""
        # Placeholder for external authentication system
        return None

    def _get_consciousness_connector(self):
        """Get consciousness system connector"""
        # Placeholder for external consciousness system
        return None


def both_dicts(dict1, dict2):
    """Helper function to get keys present in both dictionaries"""
    return set(dict1.keys()).intersection(set(dict2.keys()))