"""DAST orchestrator with directive memory for continuity."""
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from collections import defaultdict


class Directive:
    """Represents a user directive or instruction."""

    def __init__(
        self,
        directive_id: str,
        content: str,
        user_id: str,
        session_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ):
        """
        Initialize a directive.

        Args:
            directive_id: Unique directive identifier
            content: Directive content/instruction
            user_id: User who issued the directive
            session_id: Session in which directive was issued
            metadata: Additional metadata
            timestamp: When directive was issued (defaults to now)
        """
        self.directive_id = directive_id
        self.content = content
        self.user_id = user_id
        self.session_id = session_id
        self.metadata = metadata or {}
        self.timestamp = timestamp or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert directive to dictionary."""
        return {
            "directive_id": self.directive_id,
            "content": self.content,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Directive":
        """Create directive from dictionary."""
        timestamp = datetime.fromisoformat(data["timestamp"])
        return cls(
            directive_id=data["directive_id"],
            content=data["content"],
            user_id=data["user_id"],
            session_id=data["session_id"],
            metadata=data.get("metadata", {}),
            timestamp=timestamp
        )


class DirectiveMemory:
    """Memory store for user directives per user/session."""

    def __init__(self):
        """Initialize directive memory."""
        # Store last directive per (user_id, session_id)
        self._user_session_directives: Dict[Tuple[str, str], Directive] = {}

        # Store last directive per user_id (across all sessions)
        self._user_directives: Dict[str, Directive] = {}

        # Complete directive history
        self._history: list[Directive] = []

    def store_directive(self, directive: Directive) -> None:
        """
        Store a directive in memory.

        Args:
            directive: Directive to store
        """
        key = (directive.user_id, directive.session_id)

        # Update per-user-session memory
        self._user_session_directives[key] = directive

        # Update per-user memory (latest across all sessions)
        if directive.user_id not in self._user_directives:
            self._user_directives[directive.user_id] = directive
        else:
            # Only update if newer
            existing = self._user_directives[directive.user_id]
            if directive.timestamp > existing.timestamp:
                self._user_directives[directive.user_id] = directive

        # Add to history
        self._history.append(directive)

    def get_last_directive(
        self,
        user_id: str,
        session_id: Optional[str] = None
    ) -> Optional[Directive]:
        """
        Get the last directive for a user/session.

        Args:
            user_id: User identifier
            session_id: Optional session identifier. If None, returns last across all sessions.

        Returns:
            Last Directive if found, None otherwise
        """
        if session_id:
            # Get last directive for specific session
            key = (user_id, session_id)
            return self._user_session_directives.get(key)
        else:
            # Get last directive across all sessions
            return self._user_directives.get(user_id)

    def get_session_directives(
        self,
        user_id: str,
        session_id: str
    ) -> list[Directive]:
        """
        Get all directives for a specific user/session.

        Args:
            user_id: User identifier
            session_id: Session identifier

        Returns:
            List of directives for the session
        """
        return [
            d for d in self._history
            if d.user_id == user_id and d.session_id == session_id
        ]

    def get_user_directives(self, user_id: str) -> list[Directive]:
        """
        Get all directives for a user across all sessions.

        Args:
            user_id: User identifier

        Returns:
            List of all directives for the user
        """
        return [d for d in self._history if d.user_id == user_id]

    def clear_session(self, user_id: str, session_id: str) -> None:
        """
        Clear directives for a specific session.

        Args:
            user_id: User identifier
            session_id: Session identifier
        """
        key = (user_id, session_id)
        if key in self._user_session_directives:
            del self._user_session_directives[key]

        # Remove from history
        self._history = [
            d for d in self._history
            if not (d.user_id == user_id and d.session_id == session_id)
        ]


class Orchestrator:
    """DAST orchestrator with directive memory for continuity."""

    def __init__(self):
        """Initialize the orchestrator."""
        self.directive_memory = DirectiveMemory()
        self.active_tasks: Dict[str, Any] = {}
        self._directive_counter = 0

    def process_directive(
        self,
        content: str,
        user_id: str,
        session_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Directive:
        """
        Process and store a user directive.

        Args:
            content: Directive content
            user_id: User identifier
            session_id: Session identifier
            metadata: Additional metadata

        Returns:
            Created Directive
        """
        # Generate directive ID
        self._directive_counter += 1
        directive_id = f"dir_{user_id[:8]}_{session_id[:8]}_{self._directive_counter:04d}"

        # Create directive
        directive = Directive(
            directive_id=directive_id,
            content=content,
            user_id=user_id,
            session_id=session_id,
            metadata=metadata
        )

        # Store in memory
        self.directive_memory.store_directive(directive)

        # Process the directive (placeholder for actual orchestration logic)
        self._orchestrate(directive)

        return directive

    def get_last_directive(
        self,
        user_id: str,
        session_id: Optional[str] = None
    ) -> Optional[Directive]:
        """
        Get the last directive for a user/session.

        Args:
            user_id: User identifier
            session_id: Optional session identifier

        Returns:
            Last Directive if found, None otherwise
        """
        return self.directive_memory.get_last_directive(user_id, session_id)

    def get_context_for_session(self, user_id: str, session_id: str) -> Dict[str, Any]:
        """
        Get orchestration context for a session, including last directive.

        Args:
            user_id: User identifier
            session_id: Session identifier

        Returns:
            Context dictionary with last directive and session info
        """
        last_directive = self.get_last_directive(user_id, session_id)

        context = {
            "user_id": user_id,
            "session_id": session_id,
            "last_directive": last_directive.to_dict() if last_directive else None,
            "session_directive_count": len(
                self.directive_memory.get_session_directives(user_id, session_id)
            )
        }

        return context

    def _orchestrate(self, directive: Directive) -> None:
        """
        Internal orchestration logic (placeholder).

        Args:
            directive: Directive to orchestrate
        """
        # In a real implementation, this would:
        # - Parse the directive
        # - Create tasks
        # - Coordinate execution
        # - Track state
        pass


if __name__ == "__main__":
    # Demonstration
    print("=== DAST Orchestrator with Directive Memory Demo ===\n")

    # Initialize orchestrator
    orchestrator = Orchestrator()

    # Process directives for user1, session_a
    dir1 = orchestrator.process_directive(
        content="Analyze the recent logs for errors",
        user_id="user1",
        session_id="session_a",
        metadata={"priority": "high"}
    )
    print(f"Processed directive: {dir1.directive_id}")
    print(f"Content: {dir1.content}\n")

    dir2 = orchestrator.process_directive(
        content="Generate a summary report",
        user_id="user1",
        session_id="session_a"
    )
    print(f"Processed directive: {dir2.directive_id}")
    print(f"Content: {dir2.content}\n")

    # Process directive for user1, session_b
    dir3 = orchestrator.process_directive(
        content="Deploy the latest build to staging",
        user_id="user1",
        session_id="session_b"
    )
    print(f"Processed directive: {dir3.directive_id}")
    print(f"Content: {dir3.content}\n")

    # Get last directive for session_a
    last_a = orchestrator.get_last_directive("user1", "session_a")
    print(f"Last directive for session_a: {last_a.content if last_a else 'None'}")

    # Get last directive for session_b
    last_b = orchestrator.get_last_directive("user1", "session_b")
    print(f"Last directive for session_b: {last_b.content if last_b else 'None'}")

    # Get last directive across all sessions
    last_overall = orchestrator.get_last_directive("user1")
    print(f"Last directive overall: {last_overall.content if last_overall else 'None'}\n")

    # Get context for session_a
    context = orchestrator.get_context_for_session("user1", "session_a")
    print("Context for session_a:")
    print(f"  User: {context['user_id']}")
    print(f"  Session: {context['session_id']}")
    print(f"  Last directive: {context['last_directive']['content'] if context['last_directive'] else 'None'}")
    print(f"  Total directives in session: {context['session_directive_count']}")
