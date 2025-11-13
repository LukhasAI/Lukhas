"""MATRIZ cognitive node implementations."""
# ΛTAG: matriz_nodes
import os

from .decision_node import DecisionNode
from .memory_node import MemoryNode
from .thought_node import ThoughtNode

_COMPAT_MODE = os.getenv("MATRIZ_COMPAT_IMPORTS", "1") == "1"

if _COMPAT_MODE:
    CognitiveMemoryNode = MemoryNode
    CognitiveThoughtNode = ThoughtNode
    CognitiveDecisionNode = DecisionNode
    __all__ = [
        "CognitiveDecisionNode",
        "CognitiveMemoryNode",
        "CognitiveThoughtNode",
        "DecisionNode",
        "MemoryNode",
        "ThoughtNode",
    ]
else:
    __all__ = ["DecisionNode", "MemoryNode", "ThoughtNode"]
