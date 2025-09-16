import pytest

from candidate.bridge.api_gateway.route_handlers import RouteHandlers


@pytest.mark.asyncio
async def test_status_handler_reports_uptime():
    handlers = RouteHandlers()

    # Simulate uptime to avoid zero-second output
    handlers._boot_monotonic -= 5  # type: ignore[attr-defined]

    response = await handlers.handle_request("/status", {"path": "/status"})

    assert response["uptime"].endswith("s")
    assert "T" in response["started_at"]
    assert response["status_code"] == 200
