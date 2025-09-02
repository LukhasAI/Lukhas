#!/usr/bin/env python3
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🚀 LUKHAS AI - ┌──────────────────────────────────────────────────────────────────────────────┐
║ Enhanced memory system with intelligent optimization
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: memory_utils.py
║ Path: memory/systems/memory_utils.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Development Team
╠══════════════════════════════════════════════════════════════════════════════════
║                             ◊ POETIC ESSENCE ◊
║
║ │  memory intertwine like the delicate threads of a spider's web, there lies    │
║ │  a sanctuary of utility—an ethereal repository of shared memories. This      │
║ │  module, a beacon of simplicity amidst the tempest of complexity, serves      │
║ │  as a guiding star for the AGI system, illuminating pathways of memory        │
║ │  management with the soft glow of shared purpose. Herein lies the alchemy of  │
║ │  transformation—where ephemeral thoughts are etched into the annals of       │
║ │  permanence, encapsulated within the sacred architecture of algorithms.       │
║ │                                                                              │
║ │  Like a masterful painter wielding a brush dipped in the ink of creation,    │
║ │  the `MemoryUtils` class breathes life into the abstract. It encapsulates     │
║ │  the essence of memory—its fleeting nature, its capacity for renewal, and     │
║ │  its intricate dance with time. As we traverse through the functions it       │
║ │  offers, we find ourselves crafting unique identifiers for memories,          │
║ │  ensuring each fragment of thought is cherished in its individuality. In      │
║ │  this digital tapestry, each memory ID becomes a thread, woven with          │
║
╠══════════════════════════════════════════════════════════════════════════════════
║ TECHNICAL FEATURES:
║ • Advanced memory system implementation
║ • Optimized performance with intelligent caching
║ • Comprehensive error handling and validation
║ • Integration with LUKHAS AI architecture
║ • Extensible design for future enhancements
║
║ ΛTAG: ΛLUKHAS, ΛMEMORY, ΛPYTHON
╚══════════════════════════════════════════════════════════════════════════════════
"""

import hashlib
import json
from datetime import datetime
from typing import Any


class MemoryUtils:
    """Shared memory utility functions."""

    @staticmethod
    def generate_memory_id(content: str) -> str:
        """Generate a unique memory ID based on content."""
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    @staticmethod
    def encrypt_memory_data(data: dict[str, Any], key: str) -> str:
        """Encrypt memory data."""
        # Simple encryption for demonstration
        data_str = json.dumps(data)
        encrypted = "".join(chr(ord(c) ^ ord(k)) for c, k in zip(data_str, key * (len(data_str) // len(key) + 1)))
        return encrypted

    @staticmethod
    def decrypt_memory_data(encrypted_data: str, key: str) -> dict[str, Any]:
        """Decrypt memory data."""
        # Simple decryption for demonstration
        decrypted = "".join(
            chr(ord(c) ^ ord(k)) for c, k in zip(encrypted_data, key * (len(encrypted_data) // len(key) + 1))
        )
        return json.loads(decrypted)

    @staticmethod
    def validate_memory_access(user_id: str, memory_id: str, access_policy: dict[str, Any]) -> bool:
        """Validate memory access permissions."""
        if access_policy.get("public", False):
            return True
        return user_id in access_policy.get("allowed_users", [])

    @staticmethod
    def format_memory_timestamp(timestamp: datetime) -> str:
        """Format memory timestamp consistently."""
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def calculate_memory_size(memory_data: dict[str, Any]) -> int:
        """Calculate memory size in bytes."""
        return len(json.dumps(memory_data).encode())
