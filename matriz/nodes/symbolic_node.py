# """
# ═══════════════════════════════════════════════════════════════════════════════════
# 🌌 Symbolic Node - Formal Proof Generation
# ═══════════════════════════════════════════════════════════════════════════════════
#
# Module: matriz.nodes.symbolic_node
# Purpose: Generate formal proofs for symbolic expressions.
# ═══════════════════════════════════════════════════════════════════════════════════
# """

import re

from matriz.core.node_interface import CognitiveNode
from matriz.schemas.proof import FormalProof


class SymbolicNode(CognitiveNode):
    """
    A cognitive node that specializes in symbolic reasoning and formal proof generation.
    """

    def __init__(self):
        super().__init__(node_name="symbolic_node", capabilities=["symbolic_reasoning", "formal_proof"])

    def process(self, node_input: dict) -> dict:
        """
        Processes a symbolic expression and returns a formal proof.

        Args:
            node_input: A dictionary containing the conclusion to prove and a list of premises.
                Expected format: {"conclusion": "q", "premises": ["p", "p -> q"]}

        Returns:
            A dictionary containing the generated formal proof or an error.
        """
        expression = node_input.get("expression", "")
        parts = expression.split("prove")[1].strip().split("from")
        conclusion = parts[0].strip()
        premises = [p.strip() for p in parts[1].split(",")] if len(parts) > 1 else []

        if not conclusion:
            return {"error": "No conclusion provided."}

        # 1. Check if the conclusion is already a premise
        if conclusion in premises:
            proof = FormalProof(
                premises=premises,
                conclusions=[conclusion],
                rules=[f"The conclusion '{conclusion}' is given as a premise."],
            )
            return {"proof": proof.to_dict(), "confidence": 1.0}

        # 2. Try to apply Modus Ponens
        # Look for a premise of the form "antecedent -> conclusion"
        for premise_rule in premises:
            match = re.match(r"^\s*(\w+)\s*->\s*(\w+)\s*$", premise_rule)
            if match:
                antecedent, consequent = match.groups()
                if consequent == conclusion:
                    # Found a rule that can derive the conclusion.
                    # Check if the antecedent is also a premise.
                    if antecedent in premises:
                        proof = FormalProof(
                            premises=premises,
                            conclusions=[conclusion],
                            rules=[
                                f"Given premise: '{antecedent}'",
                                f"Given premise: '{premise_rule}'",
                                f"From '{antecedent}' and '{premise_rule}', infer '{conclusion}' by Modus Ponens.",
                            ],
                        )
                        return {"proof": proof.to_dict(), "confidence": 1.0}

        return {
            "error": f"Could not prove '{conclusion}' from the given premises.",
            "confidence": 0.0,
        }

    def can_handle(self, intent: str) -> bool:
        """
        Determines if the node can handle a given intent.
        """
        return intent == "symbolic"

    def validate_output(self, output: dict) -> bool:
        """
        Validates the output of the process method.
        """
        return "proof" in output or "error" in output
