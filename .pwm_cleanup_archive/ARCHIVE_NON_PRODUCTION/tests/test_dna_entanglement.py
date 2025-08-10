from bio.symbolic.dna_simulator import DNASimulator
from core.colonies.reasoning_colony import ReasoningColony
from core.symbolism.tags import TagPermission, TagScope


def test_dna_entanglement():
    colony = ReasoningColony("dna-test")
    simulator = DNASimulator()
    tags = simulator.parse_sequence("AC")
    colony.entangle_tags(tags)
    assert "dna_0" in colony.symbolic_carryover
    value, scope, perm, _, _ = colony.symbolic_carryover["dna_0"]
    assert value == "alpha"
    assert scope == TagScope.GLOBAL
    assert perm == TagPermission.PUBLIC
