"""ΛiD login telemetry events."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any


@dataclass
class LoginResult:
    """Login result telemetry event."""

    user_id: str
    """User identifier"""

    method: str
    """Login method (faceid, seed_phrase, webauthn, etc.)"""

    success: bool
    """Whether login succeeded"""

    latency_ms: float
    """Login latency in milliseconds"""

    timestamp: datetime
    """When login occurred"""

    error_code: Optional[str] = None
    """Error code if login failed"""

    metadata: Optional[dict] = None
    """Additional metadata"""

    def to_dict(self) -> dict:
        """Convert to dictionary for event emission."""
        return {
            "user_id": self.user_id,
            "method": self.method,
            "success": self.success,
            "latency_ms": self.latency_ms,
            "timestamp": self.timestamp.isoformat(),
            "error_code": self.error_code,
            "metadata": self.metadata or {}
        }


class LoginTelemetry:
    """Manages login telemetry emission."""

    def __init__(self, event_bus: Optional[Any] = None):
        self.event_bus = event_bus
        self.events = []

    def emit_login_result(
        self,
        user_id: str,
        method: str,
        success: bool,
        latency_ms: float,
        error_code: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> LoginResult:
        """
        Emit login result event.

        Args:
            user_id: User identifier
            method: Login method
            success: Success status
            latency_ms: Latency in milliseconds
            error_code: Optional error code
            metadata: Additional metadata

        Returns:
            Created LoginResult event
        """
        event = LoginResult(
            user_id=user_id,
            method=method,
            success=success,
            latency_ms=latency_ms,
            timestamp=datetime.utcnow(),
            error_code=error_code,
            metadata=metadata
        )

        # Store locally
        self.events.append(event)

        # Emit to event bus if available
        if self.event_bus:
            self.event_bus.emit("LoginResult", event.to_dict())

        return event


if __name__ == "__main__":
    print("=== ΛiD Login Telemetry Demo ===\n")

    telemetry = LoginTelemetry()

    # Successful login
    result1 = telemetry.emit_login_result(
        user_id="user_123",
        method="faceid",
        success=True,
        latency_ms=245.3
    )
    print(f"Event 1: {result1.method} - {'✓' if result1.success else '❌'} ({result1.latency_ms}ms)")

    # Failed login
    result2 = telemetry.emit_login_result(
        user_id="user_456",
        method="seed_phrase",
        success=False,
        latency_ms=180.5,
        error_code="INVALID_SEED"
    )
    print(f"Event 2: {result2.method} - {'✓' if result2.success else '❌'} ({result2.latency_ms}ms) - {result2.error_code}")

    print(f"\nTotal events: {len(telemetry.events)}")
