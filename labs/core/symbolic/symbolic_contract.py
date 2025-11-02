"""

#TAG:core
#TAG:symbolic
#TAG:neuroplastic
#TAG:colony

Formal Symbolic Interface (FSI) for the Symbiotic Swarm
Addresses Phase Δ, Step 1

This module defines the SymbolicContract class, which provides a formal
definition for how symbolic tags are interpreted, propagated, and managed
across the LUKHΛS ecosystem.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SymbolicContract:
    """
    Defines a formal contract for a symbolic tag.
    """

    tag_name: str
    description: str
    version: str = "1.0"

    # Propagation rules
    max_propagation_depth: int = -1  # -1 for infinite
    allowed_colonies: list[str] = field(default_factory=list)  # Empty list means all colonies

    # Meaning and interpretation
    schema: dict[str, Any] = field(default_factory=dict)

    # Lineage and provenance
    author: str = "LUKHΛS Core"

    def validate_propagation(self, current_depth, colony_id):
        """
        Checks if a tag can be propagated further.
        """
        if self.max_propagation_depth != -1 and current_depth >= self.max_propagation_depth:
            return False
        return not (self.allowed_colonies and colony_id not in self.allowed_colonies)

    def validate_payload(self, payload):
        """
        Validates a payload against the contract's schema.
        """
        # This is a simplified schema validation. A real implementation would
        # use a more robust library like JSONSchema.
        for key, expected_type in self.schema.items():
            if key not in payload or not isinstance(payload[key], expected_type):
                return False
        return True


class SymbolicContractRegistry:
    """
    A registry for all symbolic contracts in the system.
    """

    def __init__(self):
        self._contracts: dict[str, SymbolicContract] = {}

    def register(self, contract: SymbolicContract):
        self._contracts[contract.tag_name] = contract

    def get(self, tag_name: str) -> SymbolicContract:
        return self.get(tag_name)

    def to_json(self) -> str:
        import json
        from dataclasses import asdict

        return json.dumps(
            {name: asdict(contract) for name, contract in self._contracts.items()},
            indent=2,
        )


if __name__ == "__main__":
    # Example usage
    contract1 = SymbolicContract(
        tag_name="EthicalDriftScore",
        description="Represents the ethical drift score of an agent or colony.",
        schema={"score": float, "agent_id": str},
        max_propagation_depth=5,
        allowed_colonies=["ethics", "governance"],
    )

    contract2 = SymbolicContract(
        tag_name="DreamEntropy",
        description="Measures the entropy of a dream sequence.",
        schema={"entropy": float, "dream_id": str},
    )

    contract3 = SymbolicContract(
        tag_name="EmotionRegulation",
        description="Represents an emotion regulation action.",
        schema={"emotion": str, "intensity": float, "agent_id": str},
        max_propagation_depth=2,
        allowed_colonies=["ethics", "consciousness"],
    )

    contract4 = SymbolicContract(
        tag_name="PrivacyTag",
        description="A tag that indicates that the associated data is private.",
        schema={"data_id": str, "privacy_level": str},
        max_propagation_depth=0,  # Should not be propagated
    )

    contract5 = SymbolicContract(
        tag_name="DreamPropagation",
        description="A tag that indicates that a dream can be propagated to other agents.",
        schema={"dream_id": str, "source_agent_id": str},
        allowed_colonies=["creativity", "consciousness"],
    )

    registry = SymbolicContractRegistry()
    registry.register(contract1)
    registry.register(contract2)
    registry.register(contract3)
    registry.register(contract4)
    registry.register(contract5)

    print("--- Symbolic Contract Registry ---")
    print(registry.to_json())
