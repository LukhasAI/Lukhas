"""Bridge module for core.task_manager → labs.core.task_manager"""
from __future__ import annotations

from labs.core.task_manager import ManagerInterface, TaskManager, create_task_manager

__all__ = ["ManagerInterface", "TaskManager", "create_task_manager"]
