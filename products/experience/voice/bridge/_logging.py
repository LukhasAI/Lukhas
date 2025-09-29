"""Shared logging helpers for voice bridge components."""

from __future__ import annotations

import logging
from typing import Optional

from lukhas.core.common.logger import get_logger

# ΛTAG: voice_logging_helper
_BASE_ADAPTER = get_logger("products.experience.voice.bridge", module_name="products.voice.bridge")
_LOGGER_BASE = _BASE_ADAPTER.logger if hasattr(_BASE_ADAPTER, "logger") else _BASE_ADAPTER
_BASE_EXTRA = getattr(_BASE_ADAPTER, "extra", {}).copy() if hasattr(_BASE_ADAPTER, "extra") else {}


def get_voice_bridge_logger(component: Optional[str] = None) -> logging.Logger:
    """Return a logger configured for voice bridge components."""

    if isinstance(_LOGGER_BASE, logging.Logger):
        extra = dict(_BASE_EXTRA)
        if component:
            extra["component"] = component
        return logging.LoggerAdapter(_LOGGER_BASE, extra)
    return _LOGGER_BASE


BRIDGE_LOGGER = get_voice_bridge_logger("module")

__all__ = ["get_voice_bridge_logger", "BRIDGE_LOGGER"]
