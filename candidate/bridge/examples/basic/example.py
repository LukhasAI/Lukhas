#!/usr/bin/env python3
"""Basic bridge example demonstrating the API gateway route handlers."""

from __future__ import annotations

import asyncio
import json
from typing import Any, Dict

from candidate.bridge.api_gateway.route_handlers import RouteHandlers


async def _run_demo() -> None:
    """Run a small asynchronous demonstration."""

    # ΛTAG: bridge_example
    handlers = RouteHandlers()

    async def custom_handler(request: Dict[str, Any]) -> Dict[str, Any]:
        """Simple custom handler used by the demonstration."""

        payload = request.get("payload", {})
        return {
            "status_code": 200,
            "message": "custom handler engaged",
            "payload_echo": payload,
        }

    handlers.register_handler("/demo", custom_handler)

    status = await handlers.handle_request("/status", {"path": "/status"})
    demo_response = await handlers.handle_request("/demo", {"payload": {"value": 42}})

    print("[STATUS]", json.dumps(status, indent=2))
    print("[DEMO]", json.dumps(demo_response, indent=2))


def main() -> None:
    """Entry point for the example script."""

    asyncio.run(_run_demo())


if __name__ == "__main__":
    main()
