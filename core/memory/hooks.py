"""Memory hooks for external system coupling."""
from typing import Dict, Any, Optional
from datetime import datetime


class MemoryFoldCreated:
    """Event emitted when a memory fold is created."""

    def __init__(self, fold_id: str, data: Dict[str, Any]):
        self.fold_id = fold_id
        self.data = data
        self.timestamp = datetime.utcnow()


class EndocrineMemoryHook:
    """Couples endocrine state to memory fold creation."""

    def __init__(self, endocrine_system: Optional[Any] = None):
        self.endocrine_system = endocrine_system

    def on_fold_created(self, event: MemoryFoldCreated) -> None:
        """
        Handle memory fold creation by snapshotting endocrine state.

        Args:
            event: The fold creation event
        """
        if not self.endocrine_system:
            return

        # Snapshot current endocrine state
        try:
            hormone_state = self.endocrine_system.get_state()

            # Add affect metadata to fold
            if "metadata" not in event.data:
                event.data["metadata"] = {}

            event.data["metadata"]["affect"] = {
                "hormones": hormone_state,
                "captured_at": event.timestamp.isoformat(),
                "source": "endocrine_system"
            }

            print(f"[Hook] Captured endocrine state for fold {event.fold_id}")

        except Exception as e:
            print(f"[Hook] Failed to capture endocrine state: {e}")


if __name__ == "__main__":
    print("=== Endocrine↔Memory Coupling Demo ===\n")

    # Mock endocrine system
    class MockEndocrine:
        def get_state(self):
            return {"cortisol": 0.6, "dopamine": 0.8}

    endocrine = MockEndocrine()
    hook = EndocrineMemoryHook(endocrine)

    # Create a fold event
    event = MemoryFoldCreated(
        fold_id="fold_123",
        data={"content": "test memory"}
    )

    print(f"Before hook: {event.data}")
    hook.on_fold_created(event)
    print(f"After hook: {event.data}")
