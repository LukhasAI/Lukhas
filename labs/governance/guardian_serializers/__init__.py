"""Bridge for candidate.governance.guardian_serializers."""

from __future__ import annotations

from importlib import import_module

for _candidate in (
    "labs.candidate.governance.guardian_serializers",
    "lukhas_website.governance.guardian_serializers",
    "governance.guardian_serializers",
):
    try:
        _mod = import_module(_candidate)
    except Exception:
        continue
    globals().update({k: getattr(_mod, k) for k in dir(_mod) if not k.startswith("_")})
    break


class GuardianSerializerRegistry(dict):  # type: ignore[misc]
    pass


class GuardianSerializer:  # type: ignore[misc]
    def serialize(self, payload):
        return payload


class GuardianEnvelopeSerializer(GuardianSerializer):  # type: ignore[misc]
    pass
