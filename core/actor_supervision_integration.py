"""Bridge module for core.actor_supervision_integration → labs.core.actor_supervision_integration"""
from __future__ import annotations

from labs.core.actor_supervision_integration import (
    SupervisedActorSystem,
    patch_actor_for_supervision,
    patch_actor_system_for_supervision,
)

__all__ = ["SupervisedActorSystem", "patch_actor_for_supervision", "patch_actor_system_for_supervision"]
