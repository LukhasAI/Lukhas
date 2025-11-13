"""Debug endpoints for development."""
from typing import Dict, Any, Optional


def get_last_directive(
    orchestrator: Any,
    user_id: str,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get last directive for debugging.

    Args:
        orchestrator: DAST orchestrator instance
        user_id: User identifier
        session_id: Optional session identifier

    Returns:
        Debug information about last directive
    """
    directive = orchestrator.get_last_directive(user_id, session_id)

    if directive is None:
        return {
            "user_id": user_id,
            "session_id": session_id,
            "directive": None,
            "message": "No directive found"
        }

    return {
        "user_id": user_id,
        "session_id": session_id,
        "directive": directive.to_dict()
    }


if __name__ == "__main__":
    print("=== Debug Last-Directive Endpoint Demo ===\n")

    import json
    from dast.orchestrator import Orchestrator

    orch = Orchestrator()
    orch.process_directive("Test command", "user_123", "session_abc")

    result = get_last_directive(orch, "user_123", "session_abc")
    print(json.dumps(result, indent=2))
