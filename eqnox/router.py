"""EQNOX resonance router with log-only mode."""
from datetime import datetime
from typing import Any, Dict, Optional


class Router:
    """Resonance router with safety mode."""

    def __init__(self, log_only: bool = False):
        """
        Initialize router.

        Args:
            log_only: If True, log decisions without acting
        """
        self.log_only = log_only
        self.decision_log = []

    def route(self, input_data: Dict[str, Any]) -> Optional[str]:
        """
        Route input to appropriate handler.

        Args:
            input_data: Input to route

        Returns:
            Target route if not in log-only mode, None otherwise
        """
        # Compute routing decision
        decision = self._compute_route(input_data)

        # Log decision
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "input": input_data,
            "decision": decision,
            "acted": not self.log_only
        }
        self.decision_log.append(log_entry)

        # Act or just log
        if self.log_only:
            print(f"[LOG-ONLY] Would route to: {decision}")
            return None
        else:
            return decision

    def _compute_route(self, input_data: Dict[str, Any]) -> str:
        """Compute routing decision (placeholder logic)."""
        priority = input_data.get("priority", "normal")
        if priority == "high":
            return "fast_lane"
        return "standard_lane"


if __name__ == "__main__":
    print("=== Router Log-Only Mode Demo ===\n")

    # Normal mode
    router = Router(log_only=False)
    result = router.route({"priority": "high", "data": "test"})
    print(f"Normal mode result: {result}\n")

    # Log-only mode
    safe_router = Router(log_only=True)
    result = safe_router.route({"priority": "high", "data": "test"})
    print(f"Log-only mode result: {result}")
    print(f"Logged decisions: {len(safe_router.decision_log)}")
