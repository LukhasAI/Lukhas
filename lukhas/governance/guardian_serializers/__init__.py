"""Bridge for lukhas.governance.guardian_serializers."""

from __future__ import annotations

from importlib import import_module
from typing import List

__all__: List[str] = []

for _candidate in (
    "lukhas_website.lukhas.governance.guardian_serializers",
    "governance.guardian_serializers",
    "candidate.governance.guardian_serializers",
):
    try:
        _mod = import_module(_candidate)
    except Exception:
        continue
    for _attr in dir(_mod):
        if _attr.startswith("_"):
            continue
        globals()[_attr] = getattr(_mod, _attr)
        if _attr not in __all__:
            __all__.append(_attr)
    break


if "GuardianSerializer" not in globals():

    class GuardianSerializer:  # type: ignore[misc]
        def serialize(self, payload):
            return payload


if "GuardianEnvelopeSerializer" not in globals():

    class GuardianEnvelopeSerializer(GuardianSerializer):  # type: ignore[misc]
        pass
