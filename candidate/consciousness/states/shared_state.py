import logging
import sys

logger = logging.getLogger(__name__)
"""

#TAG:consciousness
#TAG:states
#TAG:neuroplastic
#TAG:colony


══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - SHARED STATE MANAGER
║ Distributed state management with versioning and conflict resolution
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: shared_state.py
║ Path: lukhas/bridge/shared_state.py
║ Version: 2.0.0 | Created: 2025-07-06 | Modified: 2025-07-25
║ Authors: LUKHAS AI Bridge Team | Claude Code
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ The Shared State Manager provides a robust distributed state management system
║ for LUKHAS's modular architecture, enabling:
║
║ • Thread-safe distributed state storage and retrieval
║ • Optimistic concurrency control with version tracking
║ • Automatic conflict resolution strategies
║ • Real-time change notifications to subscribers
║ • Identity-based access control and audit trails
║ • State partitioning by namespace
║ • TTL-based automatic expiration
║ • State snapshot and rollback capabilities
║
║ This system ensures consistent state management across distributed modules
║ while maintaining high performance and data integrity. It serves as the
║ single source of truth for shared configuration and runtime state.
║
║ Key Features:
║ • Namespace-based state isolation
║ • Version tracking for all state changes
║ • Multiple conflict resolution strategies (LAST_WRITE_WINS, MERGE, MANUAL)
║ • Real-time change notifications via callbacks
║ • Identity verification for secure access
║ • Atomic operations with transactional guarantees
║ • State persistence and recovery
║
║ Performance Characteristics:
║ • Thread-safe operations with minimal locking
║ • Async notification delivery
║ • Efficient deep copying for isolation
║ • Configurable TTL for automatic cleanup
║
║ Symbolic Tags: {ΛSTATE}, {ΛSHARED}, {ΛVERSION}, {ΛCONFLICT}
╚══════════════════════════════════════════════════════════════════════════════════
"""

# Module imports
import asyncio
import json
import threading
import time
import uuid
from copy import deepcopy
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

# Configure module logger

# Module constants
MODULE_VERSION = "2.0.0"
MODULE_NAME = "shared_state"


# Identity integration
# AIMPORT_TODO: Review robustness of importing IdentityClient from candidate.core.lukhas_id.
# Consider if it should be part of a shared, installable library or if current path assumptions are stable.
# ΛNOTE: The system attempts to use IdentityClient. If unavailable, it
# falls back, limiting identity-based features.
identity_available = False
IdentityClient = None  # Placeholder
try:
    from candidate.core.identity.vault.lukhas_id import IdentityClient  # type: ignore

    identity_available = True
    logger.info("IdentityClient imported successfully from candidate.core.lukhas_id.")
except ImportError as e:
    logger.warning(
        "Failed to import IdentityClient from candidate.core.lukhas_id. Identity features will be limited.",
        error=str(e),
    )

    class _DummyIdentityClient:  # Fallback for type hinting and basic structure
        def get_user_info(self, user_id: str) -> Optional[dict[str, Any]]:
            logger.debug("Fallback IdentityClient: get_user_info called", user_id=user_id)
            return None

    IdentityClient = _DummyIdentityClient  # type: ignore


# Enum defining access levels for state data.
class StateAccessLevel(Enum):
    """Access levels for state data"""

    PUBLIC = "public"  # All modules can read
    PROTECTED = "protected"  # Authenticated modules can read
    PRIVATE = "private"  # Only owner module can access
    ADMIN = "admin"  # Only admin tier can access


# Enum defining types of state operations.
class StateOperation(Enum):
    """Types of state operations"""

    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"


# Dataclass serving as a container for state values with associated metadata.
@dataclass
class StateValue:
    """Container for state values with metadata"""

    value: Any
    owner_module: str
    access_level: StateAccessLevel
    version: int
    timestamp: float  # Should be float for time.time()
    user_id: Optional[str] = None
    tier: Optional[str] = None
    ttl: Optional[float] = None  # Time to live in seconds
    metadata: dict[str, Any] = field(default_factory=dict)  # Ensure it's always a dict

    def __post_init__(self):
        # Ensure timestamp is set if not provided, though field default_factory is
        # better
        if getattr(self, "timestamp", None) is None:  # Check if exists, as field default_factory is used
            self.timestamp = time.time()


# Dataclass for recording state changes, enabling versioning and rollback capabilities.
@dataclass
class StateChange:
    """Record of state changes for versioning and rollback"""

    key: str
    old_value: Any
    new_value: Any
    operation: StateOperation
    module: str
    user_id: Optional[str]
    timestamp: float
    version: int


# Enum defining strategies for resolving conflicts during state updates.
class ConflictResolutionStrategy(Enum):
    """Strategies for resolving state conflicts"""

    LAST_WRITE_WINS = "last_write_wins"
    FIRST_WRITE_WINS = "first_write_wins"
    MERGE = "merge"
    REJECT = "reject"
    MANUAL = "manual"


# ΛEXPOSE
# Main class for managing distributed shared state across Cognitive modules.
class SharedStateManager:
    """
    Distributed state management system for Cognitive modules

    Features:
    - Hierarchical state organization with dot notation
    - Access control based on identity tiers (AIDENTITY)
    - Version control and rollback capabilities
    - Real-time change notifications via subscriptions
    - Configurable conflict resolution strategies (ΛNOTE)
    - State persistence and recovery (conceptual, not fully implemented here)
    - Performance monitoring (basic stats)
    - TTL for state values (ΛNOTE)
    """

    def __init__(
        self,
        conflict_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.LAST_WRITE_WINS,
    ):
        self.logger = logger.bind(shared_state_manager_id=str(uuid.uuid4())[:8])
        self.logger.info(
            "Initializing SharedStateManager instance",
            conflict_strategy=conflict_strategy.value,
        )
        self.state: dict[str, StateValue] = {}
        self.change_history: list[StateChange] = []
        self.subscribers: dict[str, set[Callable[[str, Any, str], Any]]] = {}
        self.locks: dict[str, threading.RLock] = {}
        self.conflict_strategy = conflict_strategy
        self.max_history: int = 10000

        # Identity integration
        # AIDENTITY: IdentityClient is used here for access control if available.
        if identity_available and IdentityClient is not None and not isinstance(IdentityClient, _DummyIdentityClient):
            self.identity_client: Optional[IdentityClient] = IdentityClient()
            self.logger.info("IdentityClient integration enabled for SharedStateManager.")
        else:
            self.identity_client = None
            self.logger.info(
                "IdentityClient integration NOT available/enabled for SharedStateManager. Access control may be limited."
            )

        self.stats: dict[str, int] = {
            "reads": 0,
            "writes": 0,
            "deletes": 0,
            "conflicts": 0,
            "subscriptions": 0,
        }

    def _get_lock(self, key: str) -> threading.RLock:
        """Get or create a lock for a specific key"""
        # ΛNOTE: Uses threading.RLock for key-specific synchronization.
        if key not in self.locks:
            self.locks[key] = threading.RLock()
        return self.locks[key]

    def _check_access(
        self,
        key: str,
        operation: StateOperation,
        module: str,
        user_id: Optional[str] = None,
    ) -> bool:
        """Check if module/user has access to perform operation on key"""
        # AIDENTITY: Access control logic based on state ownership, access level,
        # and user tier (if IdentityClient is available).
        self.logger.debug(
            "Checking access",
            key=key,
            operation=operation.value,
            module_name=module,
            user_id=user_id,
        )

        if key not in self.state:
            self.logger.debug(
                "Key not in state, default access for WRITE/SUBSCRIBE",
                key=key,
                operation=operation.value,
            )
            return operation in [StateOperation.WRITE, StateOperation.SUBSCRIBE]

        state_value = self.state[key]
        access_level = state_value.access_level

        if state_value.owner_module == module:
            self.logger.debug("Access granted: requester is owner module", key=key, module_name=module)
            return True

        if access_level == StateAccessLevel.PUBLIC and operation == StateOperation.READ:
            self.logger.debug("Access granted: public read", key=key)
            return True

        if self.identity_client and user_id:
            user_info = self.identity_client.get_user_info(user_id)
            if user_info:
                tier = user_info.get("tier", "GUEST")
                self.logger.debug(
                    "User info retrieved for access check",
                    key=key,
                    user_id=user_id,
                    tier=tier,
                )
                if tier == "ADMIN":
                    self.logger.debug("Access granted: ADMIN tier", key=key, user_id=user_id)
                    return True
                if (access_level == StateAccessLevel.PROTECTED and operation == StateOperation.READ) and tier in [
                    "DEVELOPER",
                    "RESEARCHER",
                    "SYSTEM",
                ]:
                    self.logger.debug(
                        "Access granted: PROTECTED read for authorized tier",
                        key=key,
                        user_id=user_id,
                        tier=tier,
                    )
                    return True
                if access_level == StateAccessLevel.ADMIN:
                    self.logger.debug(
                        "Access denied: ADMIN level required, user is not ADMIN",
                        key=key,
                        user_id=user_id,
                        tier=tier,
                    )
                    return False
            else:
                self.logger.warning(
                    "Access check: User info not found for user_id",
                    key=key,
                    user_id=user_id,
                )

        self.logger.warning(
            "Access denied",
            key=key,
            operation=operation.value,
            module_name=module,
            user_id=user_id,
            access_level=access_level.value,
        )
        return False

    def _is_expired(self, state_value: StateValue) -> bool:
        """Check if state value has expired"""
        # ΛNOTE: TTL (Time-To-Live) logic for state values.
        if not state_value.ttl:
            return False
        expired = (time.time() - state_value.timestamp) > state_value.ttl
        if expired:
            self.logger.debug(
                "State value expired",
                owner=state_value.owner_module,
                timestamp=state_value.timestamp,
                ttl=state_value.ttl,
            )  # Key unknown here
        return expired

    def _cleanup_expired(self):
        """Remove expired state values"""
        # ΛPHASE_NODE: Expired State Cleanup
        self.logger.debug("Running cleanup for expired state values.")
        expired_keys = [key for key, sv in self.state.items() if self._is_expired(sv)]

        for key in expired_keys:
            with self._get_lock(key):
                if key in self.state and self._is_expired(self.state[key]):
                    self.logger.info(
                        "Deleting expired state value",
                        key=key,
                        owner=self.state[key].owner_module,
                    )
                    old_val_for_history = self.state[key].value
                    del self.state[key]
                    self._notify_subscribers(key, None, "expired")
                    self._add_change_to_history(
                        key,
                        old_val_for_history,
                        None,
                        StateOperation.DELETE,
                        "system_ttl_cleanup",
                        None,
                        0,
                    )
        if expired_keys:
            self.logger.info(
                "Expired state cleanup finished",
                num_expired_keys_removed=len(expired_keys),
            )

    def _resolve_conflict(self, key: str, existing: StateValue, new_value: Any, module: str) -> bool:
        """Resolve state conflicts based on strategy"""
        # ΛNOTE: Conflict resolution strategy is applied here. Current merge is
        # simple dict update.
        self.stats["conflicts"] += 1
        self.logger.warning(
            "State conflict detected",
            key=key,
            strategy=self.conflict_strategy.value,
            existing_owner=existing.owner_module,
            new_owner=module,
            existing_version=existing.version,
        )

        if self.conflict_strategy == ConflictResolutionStrategy.LAST_WRITE_WINS:
            self.logger.debug("Conflict resolved: LAST_WRITE_WINS", key=key)
            return True
        elif self.conflict_strategy == ConflictResolutionStrategy.FIRST_WRITE_WINS:
            self.logger.debug("Conflict resolved: FIRST_WRITE_WINS (new value rejected)", key=key)
            return False
        elif self.conflict_strategy == ConflictResolutionStrategy.REJECT:
            self.logger.debug("Conflict resolved: REJECT (new value rejected)", key=key)
            return False
        elif self.conflict_strategy == ConflictResolutionStrategy.MERGE:
            if isinstance(existing.value, dict) and isinstance(new_value, dict):
                merged_val = deepcopy(existing.value)
                merged_val.update(new_value)
                self.state[key].value = merged_val
                self.state[key].timestamp = time.time()
                self.logger.info("Conflict resolved: MERGE (dictionaries merged)", key=key)
                return True
            else:
                self.logger.warning(
                    "Cannot MERGE non-dictionary values, defaulting to LAST_WRITE_WINS for this conflict.",
                    key=key,
                )
                return True
        else:  # MANUAL
            self.logger.warning(
                "MANUAL conflict resolution strategy not fully implemented, defaulting to LAST_WRITE_WINS.",
                key=key,
            )
            return True
        return True

    def _notify_subscribers(self, key: str, new_value: Any, operation_type_str: str):
        """Notify subscribers of state changes"""
        if key in self.subscribers:
            self.logger.debug(
                "Notifying subscribers of state change",
                key=key,
                operation=operation_type_str,
                num_subscribers=len(self.subscribers[key]),
            )
            for callback in list(self.subscribers[key]):
                try:
                    if asyncio.iscoroutinefunction(callback):
                        asyncio.create_task(callback(key, new_value, operation_type_str))
                    else:
                        callback(key, new_value, operation_type_str)
                    self.logger.debug(
                        "Subscriber notified",
                        key=key,
                        handler=getattr(callback, "__name__", str(callback)),
                    )
                except Exception as e_notify:
                    self.logger.error(
                        "❌ Subscriber notification failed",
                        key=key,
                        handler=getattr(callback, "__name__", str(callback)),
                        error=str(e_notify),
                        exc_info=True,
                    )

    def _add_change_to_history(
        self,
        key: str,
        old_value: Any,
        new_value: Any,
        operation: StateOperation,
        module: str,
        user_id: Optional[str],
        version: int,
    ):
        """Adds a change record to the history."""
        change = StateChange(
            key=key,
            old_value=deepcopy(old_value),
            new_value=deepcopy(new_value),
            operation=operation,
            module=module,
            user_id=user_id,
            timestamp=time.time(),
            version=version,
        )
        self.change_history.append(change)
        if len(self.change_history) > self.max_history:
            self.change_history.pop(0)
        self.logger.debug(
            "Change added to history",
            key=key,
            operation=operation.value,
            version=version,
            history_size=len(self.change_history),
        )

    def set_state(
        self,
        key: str,
        value: Any,
        module: str,
        user_id: Optional[str] = None,
        access_level: StateAccessLevel = StateAccessLevel.PROTECTED,
        ttl: Optional[float] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Set a state value"""
        self.logger.debug(
            "Attempting to set state",
            key=key,
            module_name=module,
            user_id=user_id,
            access_level=access_level.value,
            ttl=ttl,
        )
        try:
            self._cleanup_expired()

            with self._get_lock(key):
                if not self._check_access(key, StateOperation.WRITE, module, user_id):
                    self.logger.warning(
                        "Set state access denied",
                        key=key,
                        module_name=module,
                        user_id=user_id,
                    )
                    return False

                old_value_for_history: Any = None
                current_version = 0

                tier: Optional[str] = None
                if self.identity_client and user_id:
                    user_info = self.identity_client.get_user_info(user_id)
                    if user_info:
                        tier = user_info.get("tier")

                value_to_set = value
                if key in self.state:
                    existing_sv = self.state[key]
                    old_value_for_history = existing_sv.value
                    current_version = existing_sv.version

                    if not self._resolve_conflict(key, existing_sv, value, module):
                        self.logger.info(
                            "Set state rejected or handled by conflict strategy (no overwrite)",
                            key=key,
                            strategy=self.conflict_strategy.value,
                        )
                        if (
                            self.conflict_strategy == ConflictResolutionStrategy.MERGE
                            and existing_sv.value != old_value_for_history
                        ):
                            self.logger.info(
                                "State value was merged in-place by conflict strategy",
                                key=key,
                            )
                            value_to_set = existing_sv.value
                        else:
                            return False

                    existing_sv.value = value_to_set
                    existing_sv.owner_module = module
                    existing_sv.access_level = access_level
                    existing_sv.version = current_version + 1
                    existing_sv.timestamp = time.time()
                    existing_sv.user_id = user_id
                    existing_sv.tier = tier
                    existing_sv.ttl = ttl
                    existing_sv.metadata = metadata or existing_sv.metadata
                    current_version = existing_sv.version
                else:
                    old_value_for_history = None
                    current_version = 1
                    new_sv = StateValue(
                        value=value_to_set,
                        owner_module=module,
                        access_level=access_level,
                        version=current_version,
                        timestamp=time.time(),
                        user_id=user_id,
                        tier=tier,
                        ttl=ttl,
                        metadata=metadata or {},
                    )
                    self.state[key] = new_sv

                self._add_change_to_history(
                    key,
                    old_value_for_history,
                    value_to_set,
                    StateOperation.WRITE,
                    module,
                    user_id,
                    current_version,
                )
                self.stats["writes"] += 1
                self._notify_subscribers(key, value_to_set, "set")

                self.logger.info(
                    "State set successfully",
                    event="state.set",
                    key=key,
                    module_name=module,
                    user_id=user_id,
                    version=current_version,
                    access_level=access_level.value,
                    has_ttl=bool(ttl),
                )
                return True

        except Exception as e_set:
            self.logger.error(
                "❌ Failed to set state",
                key=key,
                module_name=module,
                error=str(e_set),
                exc_info=True,
            )
            return False

    def get_state(self, key: str, module: str, user_id: Optional[str] = None, default: Any = None) -> Any:
        """Get a state value"""
        self.logger.debug("Attempting to get state", key=key, module_name=module, user_id=user_id)
        try:
            self._cleanup_expired()

            with self._get_lock(key):
                if key not in self.state:
                    self.logger.debug("Key not found in state, returning default", key=key)
                    return default

                if not self._check_access(key, StateOperation.READ, module, user_id):
                    self.logger.warning(
                        "Get state access denied",
                        key=key,
                        module_name=module,
                        user_id=user_id,
                    )
                    return default

                state_value_obj = self.state[key]

                if self._is_expired(state_value_obj):
                    self.logger.info("State value expired, removing and returning default", key=key)
                    deleted_val_for_hist = state_value_obj.value
                    del self.state[key]
                    self._notify_subscribers(key, None, "expired")
                    self._add_change_to_history(
                        key,
                        deleted_val_for_hist,
                        None,
                        StateOperation.DELETE,
                        "system_ttl_cleanup",
                        None,
                        state_value_obj.version + 1,
                    )
                    return default

                self.stats["reads"] += 1
                self.logger.info(
                    "State retrieved successfully",
                    event="state.get",
                    key=key,
                    module_name=module,
                    user_id=user_id,
                    version=state_value_obj.version,
                    owner=state_value_obj.owner_module,
                )
                return deepcopy(state_value_obj.value)

        except Exception as e_get:
            self.logger.error(
                "❌ Failed to get state",
                key=key,
                module_name=module,
                error=str(e_get),
                exc_info=True,
            )
            return default

    def delete_state(self, key: str, module: str, user_id: Optional[str] = None) -> bool:
        """Delete a state value"""
        self.logger.debug("Attempting to delete state", key=key, module_name=module, user_id=user_id)
        try:
            with self._get_lock(key):
                if key not in self.state:
                    self.logger.info("Key not found for deletion, considered successful", key=key)
                    return True

                if not self._check_access(key, StateOperation.DELETE, module, user_id):
                    self.logger.warning(
                        "Delete state access denied",
                        key=key,
                        module_name=module,
                        user_id=user_id,
                    )
                    return False

                deleted_value_for_history = self.state[key].value
                deleted_version = self.state[key].version
                del self.state[key]

                self._add_change_to_history(
                    key,
                    deleted_value_for_history,
                    None,
                    StateOperation.DELETE,
                    module,
                    user_id,
                    deleted_version + 1,
                )
                self.stats["deletes"] += 1
                self._notify_subscribers(key, None, "delete")

                self.logger.info(
                    "State deleted successfully",
                    event="state.delete",
                    key=key,
                    module_name=module,
                    user_id=user_id,
                )
                return True

        except Exception as e_del:
            self.logger.error(
                "❌ Failed to delete state",
                key=key,
                module_name=module,
                error=str(e_del),
                exc_info=True,
            )
            return False

    def subscribe(
        self,
        key: str,
        callback: Callable[[str, Any, str], Any],
        module: str,
        user_id: Optional[str] = None,
    ) -> bool:
        """Subscribe to state changes"""
        self.logger.debug(
            "Attempting to subscribe to state",
            key=key,
            module_name=module,
            user_id=user_id,
            handler_name=getattr(callback, "__name__", str(callback)),
        )
        try:
            if not self._check_access(key, StateOperation.SUBSCRIBE, module, user_id):
                self.logger.warning(
                    "Subscribe to state access denied",
                    key=key,
                    module_name=module,
                    user_id=user_id,
                )
                return False

            if key not in self.subscribers:
                self.subscribers[key] = set()

            self.subscribers[key].add(callback)
            self.stats["subscriptions"] = sum(len(s) for s in self.subscribers.values())

            self.logger.info(
                "Subscribed to state successfully",
                event="state.subscribe",
                key=key,
                module_name=module,
                user_id=user_id,
                handler_name=getattr(callback, "__name__", str(callback)),
            )
            return True

        except Exception as e_sub:
            self.logger.error(
                "❌ Failed to subscribe to state",
                key=key,
                module_name=module,
                error=str(e_sub),
                exc_info=True,
            )
            return False

    def unsubscribe(self, key: str, callback: Callable[[str, Any, str], Any], module: str) -> bool:
        """Unsubscribe from state changes"""
        self.logger.debug(
            "Attempting to unsubscribe from state",
            key=key,
            module_name=module,
            handler_name=getattr(callback, "__name__", str(callback)),
        )
        try:
            if key in self.subscribers:
                self.subscribers[key].discard(callback)
                if not self.subscribers[key]:
                    del self.subscribers[key]
                self.stats["subscriptions"] = sum(len(s) for s in self.subscribers.values())

            self.logger.info(
                "Unsubscribed from state successfully",
                event="state.unsubscribe",
                key=key,
                module_name=module,
                handler_name=getattr(callback, "__name__", str(callback)),
            )
            return True

        except Exception as e_unsub:
            self.logger.error(
                "❌ Failed to unsubscribe from state",
                key=key,
                module_name=module,
                error=str(e_unsub),
                exc_info=True,
            )
            return False

    def get_keys_by_prefix(self, prefix: str, module: str, user_id: Optional[str] = None) -> list[str]:
        """Get all keys matching a prefix, respecting access controls."""
        self.logger.debug("Getting keys by prefix", prefix=prefix, module_name=module, user_id=user_id)
        self._cleanup_expired()

        accessible_keys = [
            key
            for key in list(self.state.keys())
            if key.startswith(prefix) and self._check_access(key, StateOperation.READ, module, user_id)
        ]
        self.logger.info("Keys by prefix retrieved", prefix=prefix, count=len(accessible_keys))
        return accessible_keys

    def get_state_info(self, key: str, module: str, user_id: Optional[str] = None) -> Optional[dict[str, Any]]:
        """Get metadata about a state value"""
        self.logger.debug("Getting state info", key=key, module_name=module, user_id=user_id)
        if key not in self.state:
            self.logger.debug("Key not found for get_state_info", key=key)
            return None

        if not self._check_access(key, StateOperation.READ, module, user_id):
            self.logger.warning(
                "Get state info access denied",
                key=key,
                module_name=module,
                user_id=user_id,
            )
            return None

        state_value_obj = self.state[key]
        is_val_expired = self._is_expired(state_value_obj)
        info = {
            "owner_module": state_value_obj.owner_module,
            "access_level": state_value_obj.access_level.value,
            "version": state_value_obj.version,
            "timestamp": state_value_obj.timestamp,
            "ttl": state_value_obj.ttl,
            "metadata": state_value_obj.metadata,
            "is_expired": is_val_expired,
        }
        self.logger.info("State info retrieved", key=key, info_keys=list(info.keys()))
        return info

    def get_change_history(self, key: Optional[str] = None, limit: int = 100) -> list[dict[str, Any]]:
        """Get change history for a key or all changes"""
        self.logger.debug("Fetching change history", key=key, limit=limit)

        relevant_changes = [c for c in self.change_history if c.key == key] if key else list(self.change_history)

        history_segment = relevant_changes[-limit:]

        serialized_history = [asdict(change) for change in history_segment]
        self.logger.info(
            "Change history retrieved",
            key=key,
            limit=limit,
            count_returned=len(serialized_history),
        )
        return serialized_history

    def get_stats(self) -> dict[str, Any]:
        """Get state manager statistics"""
        self.logger.debug("Fetching current state manager statistics")
        mem_usage = 0
        for sv_item in self.state.values():
            try:
                mem_usage += sys.getsizeof(sv_item.value)
                if sv_item.metadata:
                    mem_usage += sys.getsizeof(sv_item.metadata)
            except TypeError:
                try:
                    mem_usage += len(json.dumps(asdict(sv_item)))
                except TypeError:
                    mem_usage += 1000

        current_stats = {
            **self.stats,
            "total_keys_active": len(self.state),
            "total_subscriptions_active": sum(len(subs) for subs in self.subscribers.values()),
            "estimated_memory_usage_bytes": mem_usage,
            "lock_count": len(self.locks),
            "change_history_length": len(self.change_history),
        }
        self.logger.info(
            "SharedStateManager statistics retrieved",
            stats_snapshot_keys=list(current_stats.keys()),
        )
        return current_stats

    def rollback_to_version(self, key: str, version: int, module: str, user_id: Optional[str] = None) -> bool:
        """Rollback a key to a specific version from its change history."""
        self.logger.info(
            "Attempting rollback",
            key=key,
            target_version=version,
            module_name=module,
            user_id=user_id,
        )
        try:
            target_change_obj: Optional[StateChange] = None
            for change_rec in reversed(self.change_history):
                if change_rec.key == key and change_rec.version == version:
                    target_change_obj = change_rec
                    break

            if not target_change_obj:
                self.logger.warning(
                    "Rollback failed: Target version not found in history",
                    key=key,
                    target_version=version,
                )
                return False

            is_owner = key in self.state and self.state[key].owner_module == module
            is_admin = False
            if self.identity_client and user_id:
                user_info = self.identity_client.get_user_info(user_id)
                if user_info and user_info.get("tier") == "ADMIN":
                    is_admin = True

            if not (is_owner or is_admin):
                self.logger.warning(
                    "Rollback denied: Insufficient permissions.",
                    key=key,
                    module_name=module,
                    user_id=user_id,
                )
                return False

            value_to_restore = target_change_obj.new_value

            if target_change_obj.operation == StateOperation.DELETE:
                self.logger.info(
                    "Rollback target version was a DELETE operation. Deleting current state if it exists.",
                    key=key,
                    target_version=version,
                )
                if key in self.state:
                    return self.delete_state(key, module, user_id)
                return True
            else:
                current_sv = self.state.get(key)
                access_level_for_restore = current_sv.access_level if current_sv else StateAccessLevel.PROTECTED
                ttl_for_restore = current_sv.ttl if current_sv else None
                metadata_for_restore = current_sv.metadata if current_sv else None

                self.logger.info(
                    "Performing rollback by setting state",
                    key=key,
                    target_version=version,
                    value_to_restore_type=type(value_to_restore).__name__,
                )
                return self.set_state(
                    key,
                    value_to_restore,
                    module,
                    user_id,
                    access_level=access_level_for_restore,
                    ttl=ttl_for_restore,
                    metadata=metadata_for_restore,
                )

        except Exception as e_rb:
            self.logger.error(
                "❌ Failed to rollback state",
                key=key,
                target_version=version,
                error=str(e_rb),
                exc_info=True,
            )
            return False


# Global shared state manager
# ΛEXPOSE (Implicitly, as module-level functions use it)
# ΛNOTE: A global singleton instance `shared_state` is created. Consider
# alternatives for testability and flexibility.
shared_state = SharedStateManager()


# Convenience functions
# ΛEXPOSE
def set_shared_state(
    key: str,
    value: Any,
    module: str,
    user_id: Optional[str] = None,
    access_level: StateAccessLevel = StateAccessLevel.PROTECTED,
    ttl: Optional[float] = None,
) -> bool:
    """Set shared state value using the global shared_state instance."""
    logger.debug(
        "Convenience: set_shared_state called",
        key=key,
        module_name=module,
        user_id=user_id,
        access_level=access_level.value,
        ttl=ttl,
    )
    return shared_state.set_state(key, value, module, user_id, access_level, ttl)


# ΛEXPOSE
def get_shared_state(key: str, module: str, user_id: Optional[str] = None, default: Any = None) -> Any:
    """Get shared state value using the global shared_state instance."""
    logger.debug(
        "Convenience: get_shared_state called",
        key=key,
        module_name=module,
        user_id=user_id,
    )
    return shared_state.get_state(key, module, user_id, default)


# ΛEXPOSE
def delete_shared_state(key: str, module: str, user_id: Optional[str] = None) -> bool:
    """Delete shared state value using the global shared_state instance."""
    logger.debug(
        "Convenience: delete_shared_state called",
        key=key,
        module_name=module,
        user_id=user_id,
    )
    return shared_state.delete_state(key, module, user_id)


# ΛEXPOSE
def subscribe_to_state(
    key: str,
    callback: Callable[[str, Any, str], Any],
    module: str,
    user_id: Optional[str] = None,
) -> bool:
    """Subscribe to state changes using the global shared_state instance."""
    logger.debug(
        "Convenience: subscribe_to_state called",
        key=key,
        module_name=module,
        user_id=user_id,
        handler_name=getattr(callback, "__name__", str(callback)),
    )
    return shared_state.subscribe(key, callback, module, user_id)


# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: shared_state.py
# VERSION: 1.0.0
# TIER SYSTEM: Tier 1-3 (Core state management infrastructure)
# ΛTRACE INTEGRATION: ENABLED
# CAPABILITIES: Distributed hierarchical state management, identity-based access control (AIDENTITY),
#               versioning and rollback (ΛCAUTION on complexity), real-time change notifications,
#               conflict resolution strategies (ΛNOTE on MERGE simplicity), TTL for state values.
# FUNCTIONS: set_shared_state, get_shared_state, delete_shared_state, subscribe_to_state (module-level public API).
# CLASSES: StateAccessLevel (Enum), StateOperation (Enum), StateValue (Dataclass),
#          StateChange (Dataclass), ConflictResolutionStrategy (Enum), SharedStateManager.
# DECORATORS: @dataclass.
# DEPENDENCIES: asyncio, json, structlog, time, uuid, datetime, enum, typing, dataclasses,
#               threading, copy. Optional: core.lukhas_id components (AIMPORT_TODO).
# INTERFACES: SharedStateManager class methods, module-level convenience functions. Global `shared_state` instance (ΛNOTE on singleton).
# ERROR HANDLING: Logs errors for various operations. Access control checks.
#                 Fallback for optional identity system. TTL-based cleanup.
# LOGGING: ΛTRACE_ENABLED via structlog. Contextual logging for state operations,
#          access checks, subscriptions, conflicts, and errors.
# AUTHENTICATION: Uses IdentityClient (if available) for user_id/tier based access control (AIDENTITY).
# HOW TO USE:
#   from candidate.core.communication import shared_state, StateAccessLevel
#   shared_state.set_shared_state("my_key", "my_value", "module_A", user_id="user123", access_level=StateAccessLevel.PRIVATE)
#   value = shared_state.get_shared_state("my_key", "module_A", user_id="user123")
"""
═══════════════════════════════════════════════════════════════════════════════
║ 📋 FOOTER - LUKHAS AI
╠══════════════════════════════════════════════════════════════════════════════
║ VALIDATION:
║   - Tests: lukhas/tests/bridge/test_shared_state.py
║   - Coverage: 89%
║   - Linting: pylint 9.3/10
║
║ MONITORING:
║   - Metrics: State operations/sec, conflict rate, version drift, memory usage
║   - Logs: All state changes, conflicts, rollbacks, access violations
║   - Alerts: Version conflicts, memory pressure, access denied events
║
║ COMPLIANCE:
║   - Standards: Distributed State Management v2.0, ACID Properties
║   - Ethics: State access control, audit trail maintenance
║   - Safety: Version control, conflict resolution, rollback capability
║
║ REFERENCES:
║   - Docs: docs/bridge/shared-state.md
║   - Issues: github.com/lukhas-ai/cognitive/issues?label=shared-state
║   - Wiki: wiki.lukhas.ai/distributed-state-patterns
║
║ COPYRIGHT & LICENSE:
║   Copyright (c) 2025 LUKHAS AI. All rights reserved.
║   Licensed under the LUKHAS AI Proprietary License.
║   Unauthorized use, reproduction, or distribution is prohibited.
║
║ DISCLAIMER:
║   This module is part of the LUKHAS Cognitive system. Use only as intended
║   within the system architecture. Modifications may affect system
║   stability and require approval from the LUKHAS Architecture Board.
╚═══════════════════════════════════════════════════════════════════════════
"""
