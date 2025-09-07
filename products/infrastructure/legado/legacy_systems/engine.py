"""
Ethics Engine
=============

This module provides the core ethics engine for the LUKHAS system.
"""
from consciousness.qi import qi
import streamlit as st

from .guardian import DefaultGuardian


class EthicsEngine:
    def __init__(self, guardian=None, qi_mode=False):
        self.guardian = guardian or DefaultGuardian()
        self.mode = "quantum" if qi_mode else "deterministic"

    def evaluate(self, scenario: dict) -> dict:
        # Main entrypoint
        ethical_score = self.guardian.assess_risk(scenario)
        return {
            "score": ethical_score,
            "mode": self.mode,
            "verdict": self.interpret_score(ethical_score),
        }

    def interpret_score(self, score: float) -> str:
        if score > 0.9:
            return "Prohibited"
        elif score > 0.5:
            return "Conditional"
        return "Approved"
