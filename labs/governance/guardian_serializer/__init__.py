"""Bridge for candidate.governance.guardian_serializer."""

from __future__ import annotations

from importlib import import_module

for _candidate in (
    "labs.candidate.governance.guardian_serializer",
    "lukhas_website.lukhas.governance.guardian_serializer",
    "lukhas.governance.guardian_serializer",
):
    try:
        _mod = import_module(_candidate)
    except Exception:
        continue
    globals().update({k: getattr(_mod, k) for k in dir(_mod) if not k.startswith("_")})
    break


class GuardianSerializer:  # type: ignore[misc]
    """Fallback serializer."""

    def serialize(self, data):
        return data


class GuardianEnvelopeSerializer(GuardianSerializer):  # type: ignore[misc]
    pass
