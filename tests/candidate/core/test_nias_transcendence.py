"""
Tests for the NIAS Transcendence system integration.
"""

import pytest

from candidate.core.collective.collective_ad_mind import CollectiveAdMind
from candidate.core.consciousness.oracle.oracle import ConsciousnessOracle


@pytest.mark.nias_transcendence
@pytest.mark.asyncio
async def test_consciousness_oracle_integration():
    """
    Tests the integration of the ConsciousnessOracle facade.
    """
    oracle = ConsciousnessOracle()
    profile = await oracle.get_full_consciousness_profile("test_user_123")

    assert "vulnerability_protected" in profile["short_term_forecast"]
    assert profile["short_term_forecast"]["vulnerability_protected"]
    assert "recommended_nias_tier" in profile["long_term_journey"]

@pytest.mark.nias_transcendence
@pytest.mark.asyncio
async def test_collective_intelligence_ethics():
    """
    Tests the ethical considerations of the CollectiveAdMind facade.
    """
    collective = CollectiveAdMind()
    recs = await collective.get_collective_recommendations("test_user_123")

    if recs:
        for rec in recs:
            assert "base_recommendation" in rec
            assert "consent_based" in rec["base_recommendation"]
            assert rec["base_recommendation"]["consent_based"]

            assert "routing" in rec
            assert "mutual_benefit_tracked" in rec["routing"]
            assert rec["routing"]["mutual_benefit_tracked"] in [True, False]
