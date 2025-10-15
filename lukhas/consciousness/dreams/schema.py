from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class DreamTrace:
    id: str
    model: str
    seed: str
    constraints: Dict[str, Any]
    steps: List[Dict[str, Any]]  # thought/action/observation frames
    duration_ms: int
