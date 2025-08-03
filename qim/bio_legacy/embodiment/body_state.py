from dataclasses import dataclass, field, asdict
from typing import Dict


@dataclass
class ProprioceptiveState:
    """Simple proprioceptive state holder."""
    joint_positions: Dict[str, float] = field(default_factory=dict)
    acceleration: float = 0.0
    battery_level: float = 1.0

    def update_joint(self, joint: str, position: float) -> None:
        self.joint_positions[joint] = position

    def to_dict(self) -> Dict[str, float]:
        return asdict(self)
