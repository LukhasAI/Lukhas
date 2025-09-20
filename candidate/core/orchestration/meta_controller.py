# candidate/core/orchestration/meta_controller.py
"""
Simple oscillation detector to break loops in orchestrations.
"""

from __future__ import annotations
from collections import deque


class MetaController:
    def __init__(self, window: int = 4):
        self.window = deque(maxlen=window)

    def step(self, stage_name: str) -> bool:
        """
        Return True if a 2-cycle A->B->A->B detected in last 4 steps.
        """
        snapshot = list(self.window) + [stage_name]
        self.window.append(stage_name)
        if len(snapshot) < 4:
            return False
        return snapshot[-4] == snapshot[-2] and snapshot[-3] == snapshot[-1]