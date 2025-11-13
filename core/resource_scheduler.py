"""Bridge module for core.resource_scheduler → labs.core.resource_scheduler"""
from __future__ import annotations

from labs.core.resource_scheduler import ResourceScheduler, SchedulerManager, create_scheduler

__all__ = ["ResourceScheduler", "SchedulerManager", "create_scheduler"]
