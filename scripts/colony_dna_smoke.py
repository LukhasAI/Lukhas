from lukhas.colony.adapters.consensus_to_dna import (
    persist_consensus_to_dna,
)
from lukhas.colony.contracts import ConsensusResult
from lukhas.dna.memory_inmem import InMemoryHelix


def main() -> None:
    InMemoryHelix()


c = ConsensusResult(
    key="policy:modulation",
    decided_value="strict-under-risk",
    votes_for=4,
    votes_total=5,
    confidence=0.8,
    metadata={"method": "majority"},
    version=3,
)
r = persist_consensus_to_dna(dna, c)
print("receipt:", r)
print("row:", dna.read("policy:modulation"))


if __name__ == "__main__":
    main()
