"""Bridge module for consciousness.dream.expand.mesh → labs.consciousness.dream.expand.mesh"""
from __future__ import annotations

from labs.consciousness.dream.expand.mesh import DreamMesh, MeshNode, create_dream_mesh

__all__ = ["DreamMesh", "MeshNode", "create_dream_mesh"]

__all__ = ["Mesh"] if hasattr(__import__("labs.consciousness.dream.expand.mesh"), "Mesh") else []
