"""Bridge for candidate.governance.guardian.guardian_impl."""

from __future__ import annotations

from importlib import import_module

_BACKENDS = (
    "labs.candidate.governance.guardian.guardian_impl",
    "lukhas_website.lukhas.governance.guardian.guardian_impl",
    "lukhas.governance.guardian.guardian_impl",
)

for _candidate in _BACKENDS:
    try:
        _mod = import_module(_candidate)
    except Exception:
        continue
    globals().update({k: getattr(_mod, k) for k in dir(_mod) if not k.startswith("_")})
    break


if "GuardianSystemImpl" not in globals():

    class GuardianSystemImpl:  # type: ignore[misc]
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def evaluate(self, *args, **kwargs):
            return {"allowed": True}
