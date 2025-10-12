"""Bridge for lukhas.ledger.event_bus."""

from __future__ import annotations

from importlib import import_module

for _candidate in (
    "lukhas_website.lukhas.ledger.event_bus",
    "lukhas.ledger.event_bus",
    "labs.ledger.event_bus",
):
    try:
        _mod = import_module(_candidate)
    except Exception:
        continue
    globals().update({k: getattr(_mod, k) for k in dir(_mod) if not k.startswith("_")})
    break


class AsyncEventBus:  # type: ignore[misc]
    def __init__(self):
        self.events = []

    async def publish(self, event):
        self.events.append(event)

    async def drain(self):
        while self.events:
            yield self.events.pop(0)
