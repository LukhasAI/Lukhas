from dataclasses import asdict, dataclass, field


@dataclass
class ProprioceptiveState:
    """Simple proprioceptive state holder."""

    joint_positions: dict[str, float] = field(default_factory=dict)
    acceleration: float = 0.0
    battery_level: float = 1.0

    def update_joint(self, joint: str, position: float) -> None:
        self.joint_positions[joint] = position

    def to_dict(self) -> dict[str, float]:
        return asdict(self)