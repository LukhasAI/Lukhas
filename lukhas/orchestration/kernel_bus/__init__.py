"""Bridge for lukhas.orchestration.kernel_bus."""

from __future__ import annotations

from importlib import import_module

for _candidate in (
    "lukhas_website.lukhas.orchestration.kernel_bus",
    "orchestration.kernel_bus",
    "labs.orchestration.kernel_bus",
):
    try:
        _mod = import_module(_candidate)
    except Exception:
        continue
    globals().update({k: getattr(_mod, k) for k in dir(_mod) if not k.startswith("_")})
    break


class KernelBus:  # type: ignore[misc]
    def publish(self, event):
        return True
