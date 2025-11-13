import time
from unittest.mock import patch

import pytest
from labs.core.orchestration.consensus_arbitrator import Proposal, choose, score


class TestConsensusArbitrator:
    def test_score_calculation(self):
        proposal = Proposal("p1", 0.8, time.time(), 0.1, 0.5)
        s = score(proposal)
        assert 0.0 < s < 1.0

    def test_ethics_gating(self):
        proposal = Proposal("p1", 0.9, time.time(), 0.9, 0.5)
        s = score(proposal)
        assert s == -float("inf")

    def test_choose_winner(self):
        proposals = [
            Proposal("p1", 0.7, time.time(), 0.1, 0.5),
            Proposal("p2", 0.9, time.time(), 0.1, 0.5),
            Proposal("p3", 0.8, time.time(), 0.1, 0.5),
        ]
        winner, _ = choose(proposals)
        assert winner.id == "p2"

    def test_choose_no_winner_with_high_risk(self):
        proposals = [
            Proposal("p1", 0.9, time.time(), 0.9, 0.5),
            Proposal("p2", 0.8, time.time(), 0.85, 0.5),
        ]
        winner, _ = choose(proposals)
        assert winner is None
