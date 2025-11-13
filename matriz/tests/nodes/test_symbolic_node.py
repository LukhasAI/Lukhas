# """
# ═══════════════════════════════════════════════════════════════════════════════════
# 🌌 Test Symbolic Node
# ═══════════════════════════════════════════════════════════════════════════════════
#
# Module: matriz.tests.nodes.test_symbolic_node
# Purpose: Test the SymbolicNode's proof generation and export capabilities.
# ═══════════════════════════════════════════════════════════════════════════════════
# """

import pytest
from matriz.nodes.symbolic_node import SymbolicNode
from matriz.schemas.proof import FormalProof


@pytest.fixture
def symbolic_node():
    """
    Provides a SymbolicNode instance for testing.
    """
    return SymbolicNode()


def test_prove_conclusion_from_premise(symbolic_node):
    """
    Tests that the SymbolicNode can prove a conclusion that is also a premise.
    """
    node_input = {"expression": "prove p from p"}
    result = symbolic_node.process(node_input)
    assert "proof" in result
    assert result["confidence"] == 1.0
    proof = FormalProof(**result["proof"])
    assert proof.conclusions == ["p"]


def test_modus_ponens(symbolic_node):
    """
    Tests that the SymbolicNode can prove a conclusion using Modus Ponens.
    """
    node_input = {"expression": "prove q from p, p -> q"}
    result = symbolic_node.process(node_input)
    assert "proof" in result
    assert result["confidence"] == 1.0
    proof = FormalProof(**result["proof"])
    assert proof.conclusions == ["q"]
    assert "Modus Ponens" in " ".join(proof.rules)


def test_proof_export_to_json(symbolic_node):
    """
    Tests that the FormalProof can be exported to JSON.
    """
    node_input = {"expression": "prove q from p, p -> q"}
    result = symbolic_node.process(node_input)
    proof = FormalProof(**result["proof"])
    json_proof = proof.to_json()
    assert '"conclusions": [\n    "q"\n  ]' in json_proof


def test_proof_export_to_coq(symbolic_node):
    """
    Tests that the FormalProof can be exported to Coq.
    """
    node_input = {"expression": "prove q from p, p -> q"}
    result = symbolic_node.process(node_input)
    proof = FormalProof(**result["proof"])
    coq_proof = proof.to_coq()
    assert "Theorem proof: q." in coq_proof


def test_proof_export_to_lean(symbolic_node):
    """
    Tests that the FormalProof can be exported to Lean.
    """
    node_input = {"expression": "prove q from p, p -> q"}
    result = symbolic_node.process(node_input)
    proof = FormalProof(**result["proof"])
    lean_proof = proof.to_lean()
    assert "theorem proof : q := by" in lean_proof


def test_unprovable_conclusion(symbolic_node):
    """
    Tests that the SymbolicNode returns an error for an unprovable conclusion.
    """
    node_input = {"expression": "prove r from p, p -> q"}
    result = symbolic_node.process(node_input)
    assert "error" in result
    assert result["confidence"] == 0.0
