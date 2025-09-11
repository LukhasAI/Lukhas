#!/usr/bin/env python3
"""
GLYPH Types for ΛLens
Symbol types and data structures
"""

import time
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class SymbolType(Enum):
    """Types of symbols in the dashboard"""

    DOCUMENT = "📄"
    CODE = "💻"
    DATA = "📊"
    CONCEPT = "💡"
    ENTITY = "👤"
    RELATIONSHIP = "🔗"
    WARNING = "⚠️"
    SUCCESS = "✅"
    PROCESS = "🔄"
    GLYPH = "🔮"


@dataclass
class GlyphSymbol:
    """Represents a symbolic element in the dashboard"""

    id: str
    type: SymbolType
    content: str
    metadata: dict[str, Any]
    position: Optional[tuple[float, float, float]]  # 3D position for AR/VR
    connections: list[str]  # IDs of connected symbols
    timestamp: float
    confidence: float

    @classmethod
    def create(
        cls, symbol_type: SymbolType, content: str, metadata: Optional[dict] = None, confidence: float = 1.0
    ) -> "GlyphSymbol":
        """Create a new glyph symbol"""
        return cls(
            id=str(uuid.uuid4()),
            type=symbol_type,
            content=content,
            metadata=metadata or {},
            position=None,
            connections=[],
            timestamp=time.time(),
            confidence=confidence,
        )

    def add_connection(self, symbol_id: str):
        """Add a connection to another symbol"""
        if symbol_id not in self.connections:
            self.connections.append(symbol_id)

    def set_position(self, x: float, y: float, z: float = 0.0):
        """Set 3D position for AR/VR rendering"""
        self.position = (x, y, z)

    def to_dict(self) -> dict[str, Any]:
        """Convert symbol to dictionary representation"""
        return {
            "id": self.id,
            "type": self.type.value,
            "content": self.content,
            "metadata": self.metadata,
            "position": list(self.position) if self.position else None,
            "connections": self.connections,
            "timestamp": self.timestamp,
            "confidence": self.confidence,
        }
