"""
LUKHAS AI Symbolic Tags
Tag scopes and permissions for symbolic processing
Trinity Framework: ⚛️🧠🛡️

Defines the symbolic tagging system used throughout LUKHAS AI for marking
and categorizing different types of symbolic content and operations.
"""

import logging
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class TagScope(Enum):
    """
    Defines the scope of a symbolic tag within the LUKHAS AI system.

    Different scopes determine how tags are processed and their lifecycle:
    - GLOBAL: System-wide tags visible across all colonies
    - LOCAL: Colony-specific tags with limited visibility
    - ETHICAL: Tags related to ethical evaluation and governance
    - TEMPORAL: Time-sensitive tags with automatic expiration
    - GENETIC: Heritable tags that can be passed between generations
    """

    GLOBAL = "global"
    LOCAL = "local"
    ETHICAL = "ethical"
    TEMPORAL = "temporal"
    GENETIC = "genetic"


class TagPermission(Enum):
    """
    Defines access permissions for symbolic tags.

    Permission levels control who can read, modify, or delete tags:
    - PUBLIC: Readable by all colonies and agents
    - PROTECTED: Readable by authorized colonies, modifiable by owners
    - PRIVATE: Only accessible by the creating colony/agent
    - RESTRICTED: Requires special privileges for any access
    """

    PUBLIC = "public"
    PROTECTED = "protected"
    PRIVATE = "private"
    RESTRICTED = "restricted"


class SymbolicTag:
    """
    Represents a symbolic tag with scope, permissions, and metadata.
    """

    def __init__(
        self,
        tag_id: str,
        content: Any,
        scope: TagScope,
        permission: TagPermission = TagPermission.PUBLIC,
        metadata: Optional[dict[str, Any]] = None,
        lifespan: Optional[float] = None,
    ):
        self.tag_id = tag_id
        self.content = content
        self.scope = scope
        self.permission = permission
        self.metadata = metadata or {}
        self.lifespan = lifespan  # In seconds, None means permanent
        self.created_at = None  # Will be set by tag manager
        self.access_count = 0

        logger.debug(f"Created symbolic tag {tag_id} with scope {scope.value}")

    def is_accessible(
        self, requester_id: str, requester_privileges: list[str] = None
    ) -> bool:
        """
        Check if the tag is accessible to the requester.

        Args:
            requester_id: ID of the requesting entity
            requester_privileges: List of privileges held by requester

        Returns:
            True if access is allowed
        """
        requester_privileges = requester_privileges or []

        if self.permission == TagPermission.PUBLIC:
            return True
        elif self.permission == TagPermission.PROTECTED:
            # Allow if requester is the owner or has protected access
            return (
                requester_id == self.metadata.get("owner")
                or "protected_access" in requester_privileges
            )
        elif self.permission == TagPermission.PRIVATE:
            # Only owner can access
            return requester_id == self.metadata.get("owner")
        elif self.permission == TagPermission.RESTRICTED:
            # Requires special privileges
            return "restricted_access" in requester_privileges

        return False

    def increment_access(self):
        """Increment the access counter."""
        self.access_count += 1

    def to_dict(self) -> dict[str, Any]:
        """Convert tag to dictionary representation."""
        return {
            "tag_id": self.tag_id,
            "content": self.content,
            "scope": self.scope.value,
            "permission": self.permission.value,
            "metadata": self.metadata,
            "lifespan": self.lifespan,
            "created_at": self.created_at,
            "access_count": self.access_count,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SymbolicTag":
        """Create tag from dictionary representation."""
        tag = cls(
            tag_id=data["tag_id"],
            content=data["content"],
            scope=TagScope(data["scope"]),
            permission=TagPermission(data["permission"]),
            metadata=data.get("metadata", {}),
            lifespan=data.get("lifespan"),
        )
        tag.created_at = data.get("created_at")
        tag.access_count = data.get("access_count", 0)
        return tag


class TagManager:
    """
    Manages symbolic tags with lifecycle and access control.
    """

    def __init__(self):
        self.tags: dict[str, SymbolicTag] = {}
        self.tag_index: dict[TagScope, list[str]] = {scope: [] for scope in TagScope}

        logger.info("TagManager initialized")

    def create_tag(
        self,
        tag_id: str,
        content: Any,
        scope: TagScope,
        permission: TagPermission = TagPermission.PUBLIC,
        owner_id: str = None,
        lifespan: Optional[float] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> SymbolicTag:
        """
        Create a new symbolic tag.

        Args:
            tag_id: Unique identifier for the tag
            content: Tag content/payload
            scope: Tag scope
            permission: Access permission level
            owner_id: ID of the tag owner
            lifespan: Tag lifetime in seconds
            metadata: Additional metadata

        Returns:
            Created SymbolicTag
        """
        if tag_id in self.tags:
            raise ValueError(f"Tag {tag_id} already exists")

        # Prepare metadata
        tag_metadata = metadata or {}
        if owner_id:
            tag_metadata["owner"] = owner_id

        # Create tag
        tag = SymbolicTag(tag_id, content, scope, permission, tag_metadata, lifespan)
        tag.created_at = None  # Would set to current timestamp in real implementation

        # Store tag
        self.tags[tag_id] = tag
        self.tag_index[scope].append(tag_id)

        logger.debug(f"Created tag {tag_id} with scope {scope.value}")
        return tag

    def get_tag(
        self,
        tag_id: str,
        requester_id: str = None,
        requester_privileges: list[str] = None,
    ) -> Optional[SymbolicTag]:
        """
        Retrieve a tag by ID with access control.

        Args:
            tag_id: Tag identifier
            requester_id: ID of requesting entity
            requester_privileges: Privileges held by requester

        Returns:
            SymbolicTag if found and accessible, None otherwise
        """
        tag = self.tags.get(tag_id)
        if not tag:
            return None

        # Check access permissions
        if requester_id and not tag.is_accessible(requester_id, requester_privileges):
            logger.warning(
                f"Access denied to tag {tag_id} for requester {requester_id}"
            )
            return None

        tag.increment_access()
        return tag

    def get_tags_by_scope(
        self,
        scope: TagScope,
        requester_id: str = None,
        requester_privileges: list[str] = None,
    ) -> list[SymbolicTag]:
        """
        Get all accessible tags within a scope.

        Args:
            scope: Tag scope to query
            requester_id: ID of requesting entity
            requester_privileges: Privileges held by requester

        Returns:
            List of accessible tags
        """
        tag_ids = self.tag_index.get(scope, [])
        accessible_tags = []

        for tag_id in tag_ids:
            tag = self.get_tag(tag_id, requester_id, requester_privileges)
            if tag:
                accessible_tags.append(tag)

        return accessible_tags

    def remove_tag(self, tag_id: str, requester_id: str = None) -> bool:
        """
        Remove a tag.

        Args:
            tag_id: Tag to remove
            requester_id: ID of requesting entity

        Returns:
            True if removed successfully
        """
        tag = self.tags.get(tag_id)
        if not tag:
            return False

        # Check if requester can modify the tag
        if requester_id and tag.metadata.get("owner") != requester_id:
            logger.warning(f"Unauthorized tag removal attempt by {requester_id}")
            return False

        # Remove from index
        if tag_id in self.tag_index[tag.scope]:
            self.tag_index[tag.scope].remove(tag_id)

        # Remove from storage
        del self.tags[tag_id]

        logger.debug(f"Removed tag {tag_id}")
        return True

    def get_tag_stats(self) -> dict[str, Any]:
        """Get statistics about managed tags."""
        stats = {"total_tags": len(self.tags), "by_scope": {}, "by_permission": {}}

        # Count by scope
        for scope in TagScope:
            stats["by_scope"][scope.value] = len(self.tag_index[scope])

        # Count by permission
        permission_counts = {}
        for tag in self.tags.values():
            perm = tag.permission.value
            permission_counts[perm] = permission_counts.get(perm, 0) + 1

        stats["by_permission"] = permission_counts

        return stats


# Global tag manager instance
_tag_manager = None


def get_tag_manager() -> TagManager:
    """Get or create the global tag manager."""
    global _tag_manager  # noqa: PLW0603
    if _tag_manager is None:
        _tag_manager = TagManager()
    return _tag_manager


# Export public interface
__all__ = ["TagScope", "TagPermission", "SymbolicTag", "TagManager", "get_tag_manager"]
