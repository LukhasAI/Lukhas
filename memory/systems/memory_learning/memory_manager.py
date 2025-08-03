#!/usr/bin/env python3
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🚀 LUKHAS AI - ```PLAINTEXT
║ Enhanced memory system with intelligent optimization
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: memory_manager.py
║ Path: memory/systems/memory_learning/memory_manager.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Development Team
╠══════════════════════════════════════════════════════════════════════════════════
║                             ◊ POETIC ESSENCE ◊
║
║ │                             A LUKHAS AI SYSTEM COMPONENT                              │
║ ├─────────────────────────────────────────────────────────────────────────────────────┤
║ │  **One-Line Description:**                                                             │
║ │  A pivotal architect of memory, orchestrating the harmony of learning and recall.     │
║ ├─────────────────────────────────────────────────────────────────────────────────────┤
║ │                           **Poetic Essence:**                                          │
║ │                                                                                       │
║ │  In the vast expanse of the digital cosmos, where the flickering circuits whisper      │
║ │  tales of ephemeral thoughts, the Memory Manager emerges as the steadfast keeper of    │
║ │  knowledge — a custodian of the ethereal library, where the echoes of learning        │
║ │  reverberate through the corridors of silicon and code. Like a grand tapestry woven    │
║ │  from the threads of experience, it gathers and preserves the fragments of insight,    │
║ │  ensuring that each moment of enlightenment is not lost to the void of forgetfulness.  │
║ │                                                                                       │
║ │  Imagine, if you will, a great river, its waters shimmering with the reflections of    │
║
╠══════════════════════════════════════════════════════════════════════════════════
║ TECHNICAL FEATURES:
║ • Advanced memory system implementation
║ • Optimized performance with intelligent caching
║ • Comprehensive error handling and validation
║ • Integration with LUKHAS AI architecture
║ • Extensible design for future enhancements
║
║ ΛTAG: ΛLUKHAS, ΛMEMORY, ΛPYTHON
╚══════════════════════════════════════════════════════════════════════════════════
"""

from core.common import get_logger
import json
import os
import time
import hashlib
import uuid
from typing import Dict, Any, List, Optional, Union, Tuple, Set
from datetime import datetime, timedelta
from enum import Enum
import re # Add re for regex operations in extract_insights

# Import memory components
# TODO: Resolve import paths if these files are moved or structure changes.
# Assuming memory_folds and trauma_lock are now in the same directory
from .memory_folds import AGIMemory, MemoryType, MemoryPriority, MemoryFold
from .trauma_lock import TraumaLockSystem as TraumaLock # Renamed class in trauma_lock.py
# from AID.core.lambda_id import ID, AccessTier  # TODO: Install or implement AID
# from AID.core.memory_identity import MemoryIdentityIntegration, MemoryAccessPolicy  # TODO: Install or implement AID
# Assuming dream_reflection_loop is in CORE/dream_engine
# from consciousness.core_consciousness.dream_engine.dream_reflection_loop import DreamReflectionLoop # Removed DREAM_CLUSTERING_AVAILABLE as it's not used directly here  # Removed to break circular dependency

logger = logging.getLogger("v1_AGI.memory")

from core.common import LukhasError, GuardianRejectionError, MemoryDriftError
class MemoryAccessError(LukhasError):
    """Exception raised for memory access permission errors."""
    pass

class MemoryManager:
    """
    Memory Manager for v1_AGI.
    Handles the storage, retrieval, and organization of system memories,
    including integration with the trauma lock system and Lukhas_ID identity.
    """

    def __init__(self, storage_path: str = "./memory_store", id_integration: Optional[MemoryIdentityIntegration] = None):
        """
        Initialize the memory manager.

        Args:
            storage_path: Path to store memory data
            id_integration: Optional memory-identity integration component
        """
        logger.info("Initializing Memory Manager...")

        self.storage_path = storage_path
        self.memory_folds = AGIMemory()
        self.trauma_lock = TraumaLock()

        # Identity integration
        self.id_integration = id_integration

        # Memory statistics
        self.stats = {
            "total_memories": 0,
            "locked_memories": 0,
            "user_memories": {},  # user_id -> count
            "last_access": None,
            "access_count": 0,
            "memory_types": {t.value: 0 for t in MemoryType},
            "identity_protected": 0  # Count of memories requiring identity verification
        }

        # Initialize access tier requirements for memory types
        self._init_access_requirements()

        # Create storage directory if it doesn't exist
        os.makedirs(storage_path, exist_ok=True)
        logger.info(f"Memory storage initialized at: {storage_path}")

        # Vector embeddings support flag (to be implemented)
        self.vector_search_enabled = False

        # Dream reflection loop integration
        self.dream_reflection = DreamReflectionLoop()
        self.last_dream_cycle = None
        self.dream_cycle_interval = timedelta(hours=6)  # Run dream cycle every 6 hours

        logger.info("Memory Manager initialized")

    def _init_access_requirements(self):
        """Initialize the access tier requirements for different memory types."""
        # Map memory types to minimum access tiers required
        self.tier_requirements = {
            MemoryType.EPISODIC: AccessTier.TIER_1,
            MemoryType.SEMANTIC: AccessTier.TIER_1,
            MemoryType.PROCEDURAL: AccessTier.TIER_1,
            MemoryType.EMOTIONAL: AccessTier.TIER_2,
            MemoryType.ASSOCIATIVE: AccessTier.TIER_1,
            MemoryType.SYSTEM: AccessTier.TIER_3,
            MemoryType.IDENTITY: AccessTier.TIER_2,
            MemoryType.CONTEXT: AccessTier.TIER_1
        }

        # Memory priority overrides - higher priority memories might need higher access
        self.priority_overrides = {
            MemoryPriority.CRITICAL: AccessTier.TIER_3,
            MemoryPriority.HIGH: AccessTier.TIER_2
        }

    def process_dream_cycle(self) -> Dict[str, Any]:
        """
        Process memories through dream reflection cycle to identify patterns
        and generate new insights. Integrated from OXN dream engine.

        Returns:
            Dict[str, Any]: Results of dream processing
        """
        now = datetime.now()

        # Only run if enough time has passed since last cycle
        if (self.last_dream_cycle and
            now - self.last_dream_cycle < self.dream_cycle_interval):
            return {"status": "skipped", "reason": "too_soon"}

        try:
            # Get recent memories for processing
            recent_memories = self._get_recent_memories()

            # Process through dream reflection
            patterns = self.dream_reflection.recognize_patterns()

            # Store recognized patterns as new memories
            for pattern in patterns.get("patterns", []):
                pattern_key = f"dream_pattern_{uuid.uuid4().hex[:8]}"
                self.store(
                    key=pattern_key,
                    data={
                        "pattern_type": pattern["type"],
                        "confidence": pattern.get("confidence", 0.0),
                        "timestamp": now.isoformat()
                    },
                    metadata={
                        "generated_by": "dream_reflection",
                        "pattern_source": "memory_analysis"
                    },
                    memory_type=MemoryType.ASSOCIATIVE,
                    priority=MemoryPriority.MEDIUM
                )

            self.last_dream_cycle = now

            return {
                "status": "success",
                "patterns_found": len(patterns.get("patterns", [])),
                "timestamp": now.isoformat()
            }

        except Exception as e:
            logger.error(f"Error in dream cycle: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    def _get_recent_memories(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get memories from the last N days for dream processing"""
        cutoff = datetime.now() - timedelta(days=days)
        recent_memories = []

        for key, fold in self.memory_folds.folds.items():
            if fold.created_at >= cutoff:
                memory = fold.retrieve()
                recent_memories.append({
                    "key": key,
                    "content": memory,
                    "type": fold.memory_type.value,
                    "timestamp": fold.created_at.isoformat()
                })

        return recent_memories

    def store(self, key: str, data: Any, metadata: Dict[str, Any] = None,
              memory_type: Union[MemoryType, str] = MemoryType.SEMANTIC,
              priority: Union[MemoryPriority, int] = MemoryPriority.MEDIUM,
              owner_id: Optional[str] = None,
              tags: List[str] = None,
              access_policy: Optional[MemoryAccessPolicy] = None) -> bool:
        """
        Store data in memory.

        Args:
            key: Unique identifier for the memory
            data: The data to store
            metadata: Additional metadata about the memory
            memory_type: Type of memory to store
            priority: Priority level for this memory
            owner_id: Lukhas_ID of the memory owner
            tags: List of tags for this memory
            access_policy: Optional access policy for this memory

        Returns:
            bool: Success status
        """
        try:
            # Ensure metadata exists
            if metadata is None:
                metadata = {}

            # Add timestamp if not in metadata
            if "timestamp" not in metadata:
                metadata["timestamp"] = datetime.now().isoformat()

            # Prepare memory object
            memory = {
                "data": data,
                "metadata": metadata,
                "memory_type": memory_type.value if isinstance(memory_type, MemoryType) else memory_type,
                "priority": priority.value if isinstance(priority, MemoryPriority) else priority,
                "owner_id": owner_id,
                "timestamp": datetime.now().isoformat()
            }

            # Encrypt memory if identity integration is available
            if owner_id and self.id_integration:
                memory = self.id_integration.encrypt_memory_content(key, memory)

            # Add to memory folds
            fold = self.memory_folds.add_fold(
                key=key,
                content=memory,
                memory_type=memory_type,
                priority=priority,
                owner_id=owner_id
            )

            # Add tags if provided
            if tags:
                for tag in tags:
                    fold.add_tag(tag)

            # Register with identity integration if available
            if self.id_integration and owner_id:
                # Determine minimum access tier
                min_tier = self.tier_requirements.get(
                    memory_type if isinstance(memory_type, MemoryType) else MemoryType(memory_type),
                    AccessTier.TIER_1
                )

                # Apply priority overrides
                priority_obj = priority if isinstance(priority, MemoryPriority) else MemoryPriority(priority)
                if priority_obj in self.priority_overrides:
                    priority_tier = self.priority_overrides[priority_obj]
                    if priority_tier.value > min_tier.value:
                        min_tier = priority_tier

                # Use the provided access policy or default to tier-based
                policy = access_policy or MemoryAccessPolicy.TIER_BASED

                # Register with identity system
                self.id_integration.register_memory(key, owner_id, memory_type, policy, min_tier)

                # Track identity-protected memories
                self.stats["identity_protected"] += 1

            # Update stats
            self.stats["total_memories"] += 1
            self.stats["last_access"] = datetime.now().isoformat()

            if owner_id:
                if owner_id not in self.stats["user_memories"]:
                    self.stats["user_memories"][owner_id] = 0
                self.stats["user_memories"][owner_id] += 1

            # Update memory type stats
            mem_type_str = memory_type.value if isinstance(memory_type, MemoryType) else memory_type
            self.stats["memory_types"][mem_type_str] = self.stats["memory_types"].get(mem_type_str, 0) + 1

            # Persist to disk
            self._persist_memory(key, memory)

            logger.debug(f"Memory stored: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to store memory: {str(e)}")
            return False

    def retrieve(self, key: str, user_identity: Optional[ID] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve data from memory with identity verification.

        Args:
            key: Unique identifier for the memory
            user_identity: User identity for access control

        Returns:
            Optional[Dict]: The retrieved memory, or None if not found/access denied

        Raises:
            MemoryAccessError: If access to the memory is denied
        """
        # Check if memory is trauma-locked
        if self.trauma_lock.is_locked(key):
            logger.warning(f"Attempted to access trauma-locked memory: {key}")
            return None

        # Retrieve from memory folds
        memory_fold = self.memory_folds.get_fold(key)
        if not memory_fold:
            # Try to load from storage
            memory = self._load_memory(key)
            if memory:
                # Create memory fold from loaded data
                memory_type = memory.get("memory_type", MemoryType.SEMANTIC)
                priority = memory.get("priority", MemoryPriority.MEDIUM)
                owner_id = memory.get("owner_id")

                # Add to active memory folds
                memory_fold = self.memory_folds.add_fold(
                    key=key,
                    content=memory,
                    memory_type=memory_type,
                    priority=priority,
                    owner_id=owner_id
                )
                logger.debug(f"Memory loaded from storage: {key}")
            else:
                logger.warning(f"Memory not found: {key}")
                return None

        # Check identity-based access control
        if not self._verify_access(memory_fold, user_identity):
            message = f"Access denied to memory: {key}"
            logger.warning(message)
            raise MemoryAccessError(message)

        # Update stats
        self.stats["last_access"] = datetime.now().isoformat()
        self.stats["access_count"] += 1

        # Retrieve memory content
        memory = memory_fold.retrieve()

        # Decrypt if necessary and if identity integration is available
        if self.id_integration and memory.get("_meta", {}).get("encrypted", False):
            # Only decrypt if user has appropriate access
            if user_identity and memory_fold.owner_id == user_identity.get_user_id():
                memory = self.id_integration.decrypt_memory_content(key, memory)
            elif user_identity and user_identity.has_access_to_tier(AccessTier.TIER_3):
                # Admin tier can decrypt any memory
                memory = self.id_integration.decrypt_memory_content(key, memory)

        return memory

    def forget(self, key: str, user_identity: Optional[ID] = None) -> bool:
        """
        Mark a memory as forgotten rather than removing it.
        Memories are maintained as immutable records for EU compliance and security.

        Args:
            key: Key of the memory to mark as forgotten
            user_identity: Optional identity of the requesting user

        Returns:
            bool: True if the memory was successfully marked as forgotten
        """
        # Check if memory exists
        memory_fold = self.memory_folds.get_fold(key)
        if not memory_fold:
            # Try to load from storage
            memory_path = os.path.join(self.storage_path, f"{key}.json")
            if os.path.exists(memory_path):
                with open(memory_path, "r") as f:
                    memory = json.load(f)
            else:
                logger.warning(f"Memory not found for forgetting: {key}")
                return False
        else:
            memory = memory_fold.retrieve()

        # Check identity-based access control for permission to forget
        if memory_fold and not self._verify_access(memory_fold, user_identity, require_owner=True):
            logger.warning(f"Access denied to forget memory: {key}")
            return False

        # Instead of deleting, mark as forgotten while keeping the data
        memory_path = os.path.join(self.storage_path, f"{key}.json")
        if os.path.exists(memory_path):
            with open(memory_path, "r") as f:
                stored_memory = json.load(f)

            # Mark as forgotten with timestamp
            if "metadata" not in stored_memory:
                stored_memory["metadata"] = {}

            stored_memory["metadata"]["forgotten"] = True
            stored_memory["metadata"]["forgotten_at"] = datetime.now().isoformat()
            stored_memory["metadata"]["forgotten_by"] = user_identity.get_user_id() if user_identity else "system"

            # Write back the updated memory with forgotten status
            with open(memory_path, "w") as f:
                json.dump(stored_memory, f)

        # If the memory is in active folds, mark it as forgotten there too
        if memory_fold:
            memory = memory_fold.retrieve()
            if "metadata" not in memory:
                memory["metadata"] = {}

            memory["metadata"]["forgotten"] = True
            memory["metadata"]["forgotten_at"] = datetime.now().isoformat()
            memory["metadata"]["forgotten_by"] = user_identity.get_user_id() if user_identity else "system"

            # Update the memory fold
            self.memory_folds.add_fold(
                key=key,
                content=memory,
                memory_type=memory.get("memory_type", "semantic"),
                priority=memory.get("priority", MemoryPriority.MEDIUM),
                owner_id=memory.get("owner_id")
            )

        # Notify identity integration if available
        if self.id_integration:
            self.id_integration.notify_memory_removal([key])

        logger.info(f"Memory marked as forgotten: {key}")
        return True

    def batch_forget(self, keys: List[str], user_identity: Optional[ID] = None) -> Dict[str, bool]:
        """
        Remove multiple memories at once.

        Args:
            keys: List of memory keys to forget
            user_identity: User identity for access control

        Returns:
            Dict[str, bool]: Keys mapped to their removal status
        """
        results = {}

        for key in keys:
            results[key] = self.forget(key, user_identity)

        return results

    def extract_user_insights(self, user_id: str, user_identity: Optional[ID] = None) -> Dict[str, Any]:
        """
        Extract insights and patterns from a specific user's memories.
        Adapted from prot1/memory_manager.py and enhanced for prot2.

        Args:
            user_id: The ID of the user whose memories to analyze.
            user_identity: ID of the requesting user, for access control.

        Returns:
            Dictionary of insights, including preferences, activity patterns, and summary.
        """
        logger.info(f"Extracting insights for user_id: {user_id}")

        user_memories_data = []
        # Iterate through all memory folds to find those belonging to the user
        # This is a simplified approach; a more optimized version might query by owner_id directly
        # or use an index if available.
        for key, fold in self.memory_folds.folds.items():
            if fold.owner_id == user_id:
                # Verify access before including memory in insight generation
                if not self._verify_access(fold, user_identity):
                    logger.warning(f"Access denied to memory {key} for user {user_id} during insight extraction. Skipping.")
                    continue

                # Retrieve and potentially decrypt
                memory_content = fold.retrieve()
                if self.id_integration and memory_content.get("_meta", {}).get("encrypted", False):
                    if user_identity and fold.owner_id == user_identity.get_user_id():
                         memory_content = self.id_integration.decrypt_memory_content(key, memory_content)
                    # Add other conditions for decryption if necessary (e.g. admin)

                # Ensure the memory is not marked as forgotten
                if memory_content.get("metadata", {}).get("forgotten", False):
                    continue

                user_memories_data.append(memory_content)

        if not user_memories_data:
            logger.info(f"No accessible memories found for user {user_id} to extract insights.")
            return {"preferences": {}, "activity_patterns": {}, "summary_insights": [], "raw_memory_count": 0}

        preferences = {}
        # Look for memories of type PREFERENCE or analyze text from other types
        # For prot1 compatibility, we'll analyze 'text' field if present in 'data'
        for memory in user_memories_data:
            text_to_analyze = None
            if memory.get("memory_type") == MemoryType.PREFERENCE.value: # Assuming PREFERENCE type exists
                if isinstance(memory.get("data"), dict) and "text" in memory["data"]:
                    text_to_analyze = memory["data"]["text"]
                elif isinstance(memory.get("data"), str):
                    text_to_analyze = memory["data"]
            elif isinstance(memory.get("data"), dict) and "text" in memory["data"]: # Fallback for other types
                 text_to_analyze = memory["data"]["text"]
            elif isinstance(memory.get("data"), str): # Fallback for string data
                 text_to_analyze = memory["data"]


            if text_to_analyze:
                text_lower = text_to_analyze.lower()
                # Simplified preference extraction patterns from prot1
                preference_patterns = [
                    (r"prefers? (.*)", "general_preference"),
                    (r"likes? (.*)", "likes"),
                    (r"dislikes? (.*)", "dislikes"),
                    (r"interested in (.*)", "interests"),
                    (r"wants? (.*)", "wants"),
                    (r"needs? (.*)", "needs"),
                    (r"enjoys? (.*)", "enjoys"),
                    (r"avoids? (.*)", "avoids"),
                    (r"favorite (?:is|color|food|movie|book|song|activity|place|etc\\.) (.*)", "favorites"),
                    (r"allergic to (.*)", "allergies")
                ]
                for pattern, category in preference_patterns:
                    matches = re.finditer(pattern, text_lower)
                    for match in matches:
                        extracted_value = match.group(1).strip().split('.')[0].split(',')[0] # Get first part
                        if extracted_value: # Ensure non-empty
                            preferences.setdefault(category, []).append(extracted_value)
                            # Avoid duplicate entries for the same preference
                            preferences[category] = list(set(preferences[category]))


        # Activity Patterns (e.g., peak interaction times)
        activity_patterns = {}
        timestamps = []
        for mem in user_memories_data:
            ts_str = mem.get("timestamp", mem.get("metadata", {}).get("timestamp"))
            if ts_str:
                try:
                    timestamps.append(datetime.fromisoformat(ts_str.replace("Z", "")))
                except ValueError:
                    logger.debug(f"Could not parse timestamp: {ts_str} for insight generation.")


        if timestamps:
            hour_counts = {}
            for ts_obj in timestamps:
                hour = ts_obj.hour
                hour_counts[hour] = hour_counts.get(hour, 0) + 1

            if hour_counts:
                peak_hour = max(hour_counts, key=hour_counts.get)
                if 5 <= peak_hour < 12: activity_patterns["peak_interaction_time"] = "morning"
                elif 12 <= peak_hour < 17: activity_patterns["peak_interaction_time"] = "afternoon"
                elif 17 <= peak_hour < 22: activity_patterns["peak_interaction_time"] = "evening"
                else: activity_patterns["peak_interaction_time"] = "night"
                activity_patterns["hourly_activity_distribution"] = hour_counts

        # Summary Insights
        summary_insights = []
        if len(user_memories_data) > 50:
            summary_insights.append(f"User has an extensive interaction history with {len(user_memories_data)} memories.")
        elif len(user_memories_data) > 10:
            summary_insights.append(f"User has a moderate interaction history with {len(user_memories_data)} memories.")
        else:
            summary_insights.append(f"User has a limited interaction history with {len(user_memories_data)} memories.")

        if preferences.get("likes") and len(preferences["likes"]) >= 3:
            summary_insights.append("User has expressed multiple likes/preferences.")
        if preferences.get("dislikes") and len(preferences["dislikes"]) >= 1:
            summary_insights.append("User has expressed some dislikes.")
        if activity_patterns.get("peak_interaction_time"):
            summary_insights.append(f"User is typically most active during the {activity_patterns['peak_interaction_time']}.")

        # Optionally, store these insights as a new memory for the user or system
        # For example:
        # insight_key = f"user_insight_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        # self.store(
        #     key=insight_key,
        #     data={"preferences": preferences, "activity": activity_patterns, "summary": summary_insights},
        #     memory_type=MemoryType.ASSOCIATIVE, # Or a new "INSIGHT" type
        #     priority=MemoryPriority.LOW,
        #     owner_id=user_id, # Or system if it's a system-generated insight about the user
        #     metadata={"generated_by": "insight_extraction_module"}
        # )
        # logger.info(f"Stored new insight memory: {insight_key}")

        return {
            "preferences": preferences,
            "activity_patterns": activity_patterns,
            "summary_insights": summary_insights,
            "analyzed_memory_count": len(user_memories_data)
        }

    def get_interaction_history(self, memory_type_filter: str = "CONTEXT", owner_id_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve a history of interactions or specific memory types, optionally filtered by owner.
        Args:
            memory_type_filter: The string value of MemoryType to filter by (e.g., "CONTEXT").
            owner_id_filter: Optional owner_id to filter memories.
        Returns:
            List of memory data payloads, sorted by timestamp if available.
        """
        history = []
        if not os.path.exists(self.storage_path):
            logger.warning(f"Memory storage path {self.storage_path} does not exist.")
            return history

        for filename in os.listdir(self.storage_path):
            if filename.endswith(".json"):
                key = filename[:-5]  # Remove .json extension
                # Note: _load_memory does not handle decryption by itself.
                # If interaction logs are encrypted and require specific identity to decrypt,
                # this method might need to use self.retrieve(key, system_identity) for each,
                # or ensure logs are stored in a way that system can access directly.
                # For now, assuming logs are accessible or decryption is not an issue here.
                memory_content = self._load_memory(key)
                if memory_content:
                    # Check if memory is marked as forgotten
                    if memory_content.get("metadata", {}).get("forgotten", False):
                        continue

                    type_match = memory_content.get("memory_type") == memory_type_filter
                    owner_match = True  # Assume match if no owner_id_filter
                    if owner_id_filter:
                        owner_match = memory_content.get("owner_id") == owner_id_filter

                    if type_match and owner_match:
                        data_payload = memory_content.get("data")
                        if data_payload: # Ensure data is not None
                            history.append(data_payload)

        # Sort by timestamp if available in the data payload (interaction_details)
        try:
            # Ensure that 'x' is a dictionary and has 'timestamp' before trying to sort
            history.sort(key=lambda x: x.get("timestamp", "") if isinstance(x, dict) else "", reverse=False)
        except TypeError:
            logger.warning("Could not sort interaction history by timestamp due to missing/inconsistent timestamp data.")

        return history

    def _persist_memory(self, key: str, memory: Dict[str, Any]):
        """
        Persist memory data to disk (storage implementation).

        Args:
            key: Unique identifier for the memory
            memory: The memory data to persist
        """
        try:
            # Determine file path
            file_path = os.path.join(self.storage_path, f"{key}.json")

            # Write memory data to file
            with open(file_path, "w") as f:
                json.dump(memory, f, default=str)  # default=str to handle non-serializable types like datetime

            logger.info(f"Memory persisted to disk: {key}")
        except Exception as e:
            logger.error(f"Failed to persist memory to disk: {str(e)}")

    def _load_memory(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Load memory data from disk (storage implementation).

        Args:
            key: Unique identifier for the memory

        Returns:
            Optional[Dict]: The loaded memory data, or None if not found
        """
        try:
            # Determine file path
            file_path = os.path.join(self.storage_path, f"{key}.json")

            if not os.path.exists(file_path):
                return None

            # Read memory data from file
            with open(file_path, "r") as f:
                memory = json.load(f)

            logger.info(f"Memory loaded from disk: {key}")
            return memory
        except Exception as e:
            logger.error(f"Failed to load memory from disk: {str(e)}")
            return None

    def _verify_access(self, memory_fold: MemoryFold, user_identity: Optional[ID], require_owner: bool = False) -> bool:
        """
        Verify access permissions for a memory fold based on user identity.

        Args:
            memory_fold: The memory fold to check access for
            user_identity: The user identity attempting to access the memory
            require_owner: If True, access is only granted if the user is the owner

        Returns:
            bool: True if access is granted, False otherwise
        """
        if not user_identity:
            return False  # No access without identity

        # Owner access
        if memory_fold.owner_id == user_identity.get_user_id():
            return True

        # Tier-based access (admin or specific access levels)
        if user_identity.has_access_to_tier(AccessTier.TIER_3):
            return True

        # For other cases, check specific policies or default deny
        return False

    def _register_memory_with_id_integration(self, key: str, owner_id: str, memory_type: Union[MemoryType, str], priority: Union[MemoryPriority, int], access_policy: Optional[MemoryAccessPolicy] = None):
        """
        Register a memory with the identity integration system.

        Args:
            key: Unique identifier for the memory
            owner_id: Lukhas_ID of the memory owner
            memory_type: Type of memory
            priority: Priority level for this memory
            access_policy: Optional access policy for this memory
        """
        if not self.id_integration:
            return  # No identity integration available

        # Determine minimum access tier
        min_tier = self.tier_requirements.get(
            memory_type if isinstance(memory_type, MemoryType) else MemoryType(memory_type),
            AccessTier.TIER_1
        )

        # Apply priority overrides
        priority_obj = priority if isinstance(priority, MemoryPriority) else MemoryPriority(priority)
        if priority_obj in self.priority_overrides:
            priority_tier = self.priority_overrides[priority_obj]
            if priority_tier.value > min_tier.value:
                min_tier = priority_tier

        # Use the provided access policy or default to tier-based
        policy = access_policy or MemoryAccessPolicy.TIER_BASED

        # Register with identity system
        self.id_integration.register_memory(key, owner_id, memory_type, policy, min_tier)





# Last Updated: 2025-06-05 09:37:28
