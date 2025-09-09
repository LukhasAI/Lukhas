#!/usr/bin/env python3
"""
Memory Interface Definitions for LUKHAS Consciousness System
"""

from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional


class ValidationResult(Enum):
    """Memory validation result states"""
    VALID = "valid"
    INVALID = "invalid" 
    CORRUPTED = "corrupted"
    PENDING = "pending"


@dataclass
class MemoryOperation:
    """Basic memory operation structure"""
    operation_type: str
    content: Optional[Any] = None
    metadata: Optional[dict] = None