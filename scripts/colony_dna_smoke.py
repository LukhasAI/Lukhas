"""
Module: colony_dna_smoke.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

from colony.adapters.consensus_to_dna import (
    persist_consensus_to_dna,
)
from colony.contracts import ConsensusResult
from dna.memory_inmem import InMemoryHelix


def main() -> None:
    dna = InMemoryHelix()  # ΛTAG: colony_smoke_setup

    consensus = ConsensusResult(
        key="policy:modulation",
        decided_value="strict-under-risk",
        votes_for=4,
        votes_total=5,
        confidence=0.8,
        metadata={"method": "majority"},
        version=3,
    )
    receipt = persist_consensus_to_dna(dna, consensus)
    print("receipt:", receipt)
    print("row:", dna.read("policy:modulation"))


if __name__ == "__main__":
    main()
