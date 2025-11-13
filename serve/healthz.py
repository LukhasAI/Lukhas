"""Health check endpoint with guardian state."""
from datetime import datetime
from typing import Any, Dict


def get_healthz(guardian_engine: Any = None) -> Dict[str, Any]:
    """
    Get health check with guardian state.

    Args:
        guardian_engine: Optional guardian engine instance

    Returns:
        Health check dictionary
    """
    health = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "guardian": {
            "enabled": False,
            "last_veto_ts": None,
            "last_reason_code": None
        }
    }

    # Add guardian state if available
    if guardian_engine:
        try:
            veto_history = guardian_engine.get_veto_history()
            health["guardian"]["enabled"] = True

            if veto_history:
                last_veto = veto_history[-1]
                health["guardian"]["last_veto_ts"] = last_veto.get("timestamp")
                health["guardian"]["last_reason_code"] = last_veto.get("reason_code")
        except Exception:
            health["guardian"]["error"] = "Failed to get guardian state"

    return health


if __name__ == "__main__":
    print("=== Healthz with Guardian State Demo ===\n")

    import json

    # Without guardian
    health1 = get_healthz()
    print("Without guardian:")
    print(json.dumps(health1, indent=2))

    # Mock guardian with history
    class MockGuardian:
        def get_veto_history(self):
            return [
                {"timestamp": "2025-11-12T10:00:00Z", "reason_code": "UNSAFE_CONTENT"}
            ]

    print("\nWith guardian:")
    health2 = get_healthz(MockGuardian())
    print(json.dumps(health2, indent=2))
