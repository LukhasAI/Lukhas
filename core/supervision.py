"""Bridge module for core.supervision → labs.core.supervision"""
from __future__ import annotations

from labs.core.supervision import Supervisor, SupervisionManager, create_supervisor

__all__ = ["Supervisor", "SupervisionManager", "create_supervisor"]
