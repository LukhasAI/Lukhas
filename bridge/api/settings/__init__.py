"""Stable bridge for API settings surfaces used across main."""
from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from typing import Any, Callable, Dict, Optional

__all__ = [
    "ENV",
    "Settings",
    "get_settings",
    "load_env",
    "settings",
    "settings_router",
]

_CANDIDATES = (
    "lukhas_website.api.settings",
    "candidate.api.settings",
    "core.settings",
    "config.settings",
)


def _maybe(module: str, name: str) -> Any | None:
    try:
        mod = import_module(module)
    except Exception:
        return None
    return getattr(mod, name, None)


def _bind(name: str) -> bool:
    value = next((obj for obj in (_maybe(mod, name) for mod in _CANDIDATES) if obj), None)
    if value is not None:
        globals()[name] = value
        return True
    return False


for _name in list(__all__):
    _bind(_name)


if "Settings" not in globals():
    @dataclass
    class Settings:  # type: ignore[override]
        env: str = "dev"
        debug: bool = False

        def dict(self) -> dict[str, Any]:
            return {"env": self.env, "debug": self.debug}


if "get_settings" not in globals():
    def get_settings() -> Settings:  # type: ignore[override]
        return Settings()


if "settings" not in globals():
    settings: Settings = get_settings()


if "settings_router" not in globals():
    class _Router:
        def __init__(self) -> None:
            self.routes: list[Any] = []

    settings_router = _Router()


if "ENV" not in globals():
    ENV = getattr(settings, "env", "dev") if "settings" in globals() else "dev"  # type: ignore[name-defined]


if "load_env" not in globals():
    def load_env(*_args: Any, **_kwargs: Any) -> Settings | None:
        return settings
