# candidate/core/matrix/nodes/__init__.py
"""
MATRIZ Cognitive Nodes Package

This package contains the cognitive nodes used in the MATRIZ pipeline:
Memory, Attention, Thought, Risk, Intent, Action, and Vision.

Compatibility Note: This package supports both new cognitive naming
and legacy agi_* naming during the transition period.
"""

import os

# Compatibility flag for imports
_COMPAT_MODE = os.getenv("MATRIZ_COMPAT_IMPORTS", "1") == "1"

# When nodes are implemented, they can use this pattern:
# try:
#     from .memory_node import MemoryNode as CognitiveMemoryNode  # compat alias
#     from .thought_node import ThoughtNode as CognitiveThoughtNode  # compat alias
#     from .action_node import ActionNode as CognitiveActionNode  # compat alias
#     # ... etc
# except ImportError:
#     pass

# Export compatibility aliases only in compat mode
if _COMPAT_MODE:
    __all__ = [
        # When nodes are implemented, add them here
        # "MemoryNode", "CognitiveMemoryNode",
        # "ThoughtNode", "CognitiveThoughtNode",
        # "ActionNode", "CognitiveActionNode",
        # ... etc
    ]
else:
    # Strict mode: no legacy aliases
    __all__ = []

# Future implementation note:
# Each node should have a factory classmethod for entry point instantiation:
#
# class MemoryNode:
#     def __init__(self, name=None):
#         self.name = name or "memory"
#
#     @classmethod
#     def from_entry_point(cls, name=None):
#         return cls(name=name)
#
#     def process(self, context):
#         # MATRIZ memory processing logic
#         return {"memory_result": "processed"}