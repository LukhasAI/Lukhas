"""
Minimal feature flags core (internal)
Provides Flags class used by analytics and other modules.
"""

from __future__ import annotations

import json
import os
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Dict

# Default flags (safe, conservative defaults)
_DEFAULT_FLAGS: Dict[str, bool] = {
    "TOOL_ANALYTICS": True,
    "ADMIN_DASHBOARD": False,
    "adaptive_ai": True,
    "adaptive_signals": True,
}

# Override stack (LIFO) to support nested contexts
_override_stack: list[Dict[str, bool]] = []


def _env_overrides() -> Dict[str, bool]:
    """Read environment-based overrides.
    Supports:
    - LUKHAS_FLAGS='{"FLAG": true, ...}'
    - LUKHAS_FLAG_<NAME>=0/1/true/false
    """
    merged: Dict[str, bool] = {}
    blob = os.getenv("LUKHAS_FLAGS")
    if blob:
        try:
            data = json.loads(blob)
            if isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, bool):
                        merged[str(k)] = v
        except Exception:
            pass
    # Per-flag envs
    for k, v in os.environ.items():
        if not k.startswith("LUKHAS_FLAG_"):
            continue
        name = k[len("LUKHAS_FLAG_") :]
        val = str(v).strip().lower()
        if val in ("1", "true", "yes", "on"):
            merged[name] = True
        elif val in ("0", "false", "no", "off"):
            merged[name] = False
    return merged


class Flags:
    """Central accessor for feature flags."""

    @staticmethod
    def get(name: str, default: bool = False) -> bool:
        # Top of override stack wins
        if _override_stack:
            top = _override_stack[-1]
            if name in top:
                return bool(top[name])
        # Env overrides next
        env = _env_overrides()
        if name in env:
            return bool(env[name])
        # Defaults
        return bool(_DEFAULT_FLAGS.get(name, default))

    @staticmethod
    def is_enabled(name: str) -> bool:
        return bool(Flags.get(name, False))

    @staticmethod
    def all() -> Dict[str, bool]:
        combined = {**_DEFAULT_FLAGS, **_env_overrides()}
        if _override_stack:
            combined.update(_override_stack[-1])
        return dict(combined)

    @staticmethod
    @contextmanager
    def context(overrides: Dict[str, bool]) -> Iterator[None]:
        _override_stack.append({str(k): bool(v) for k, v in (overrides or {}).items()})
        try:
            yield None
        finally:
            _override_stack.pop()
