"""Bridge module for core.settings → labs.core.settings"""
from __future__ import annotations

from labs.core.settings import Settings, SettingsManager, create_settings

__all__ = ["Settings", "SettingsManager", "create_settings"]
