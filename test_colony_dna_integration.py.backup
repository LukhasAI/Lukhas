from lukhas_pwm.colony.adapters.consensus_to_dna import persist_consensus_to_dna
from lukhas_pwm.colony.contracts import ConsensusResult
from lukhas_pwm.dna.memory_inmem import InMemoryHelix


def _consensus(
    key="policy:modulation",
    value="strict-under-risk",
    v_for=3,
    v_total=4,
    conf=0.7,
    version=1,
):
    return ConsensusResult(
        key=key,
        decided_value=value,
        votes_for=v_for,
        votes_total=v_total,
        confidence=conf,
        metadata={"method": "majority"},
        version=version,
    )


essage = """
Tests for colony→DNA persistence: correct value, strength clamped, versioning.
"""


def test_consensus_persists_to_dna_with_strength_and_version():
    dna = InMemoryHelix()
    c = _consensus()
    receipt = persist_consensus_to_dna(dna, c)
    row = dna.read(c.key)
    assert receipt.upserted is True
    assert row["value"] == c.decided_value
    assert 0.1 <= row["strength"] <= 1.0
    assert row["version"] == c.version


def test_higher_version_wins():
    dna = InMemoryHelix()
    c1 = _consensus(version=1, value="strict-under-risk")
    c2 = _consensus(version=2, value="balanced-under-low-risk")
    persist_consensus_to_dna(dna, c1)
    persist_consensus_to_dna(dna, c2)
    row = dna.read(c1.key)
    assert row["version"] == 2
    assert row["value"] == "balanced-under-low-risk"


def test_lower_version_does_not_overwrite():
    dna = InMemoryHelix()
    c2 = _consensus(version=2, value="v2")
    c1 = _consensus(version=1, value="v1")
    persist_consensus_to_dna(dna, c2)
    persist_consensus_to_dna(dna, c1)
    row = dna.read(c1.key)
    assert row["version"] == 2 and row["value"] == "v2"
