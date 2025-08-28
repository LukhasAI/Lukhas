"""
Tests for the Collective Intelligence Layer.
"""

import pytest
from typing import Dict, Any, List

from candidate.core.collective.clusters.consciousness_clusters import ConsciousnessClusteringEngine
from candidate.core.collective.swarm.swarm_recommendations import SwarmRecommendationSystem
from candidate.core.collective.routing.altruistic_router import AltruisticAdRouter
from candidate.core.collective.collective_ad_mind import CollectiveAdMind

@pytest.mark.asyncio
async def test_consciousness_clustering_engine():
    """
    Tests the ConsciousnessClusteringEngine.
    """
    engine = ConsciousnessClusteringEngine()
    clusters = await engine.get_consciousness_clusters()
    assert isinstance(clusters, dict)
    assert len(clusters) > 0

    cluster_id = await engine.find_cluster_for_user("user_123")
    assert isinstance(cluster_id, str)
    assert "cluster_" in cluster_id

@pytest.mark.asyncio
async def test_swarm_recommendation_system():
    """
    Tests the SwarmRecommendationSystem.
    """
    system = SwarmRecommendationSystem()
    recommendations = await system.get_swarm_recommendations("user_123", "cluster_alpha_pioneers")
    assert isinstance(recommendations, list)
    if recommendations:
        rec = recommendations[0]
        assert isinstance(rec, dict)
        assert "recommendation_id" in rec
        assert "title" in rec
        assert "description" in rec
        assert "consent_based" in rec
        assert rec["consent_based"] is True

@pytest.mark.asyncio
async def test_altruistic_ad_router():
    """
    Tests the AltruisticAdRouter.
    """
    router = AltruisticAdRouter()
    recommendation = {"description": "A test recommendation."}
    path = await router.find_routing_path("user_123", recommendation)
    assert isinstance(path, dict)
    assert "is_routed" in path
    assert "narrative" in path

@pytest.mark.asyncio
async def test_collective_ad_mind_facade():
    """
    Tests the CollectiveAdMind facade.
    """
    mind = CollectiveAdMind()
    recommendations = await mind.get_collective_recommendations("user_123")
    assert isinstance(recommendations, list)
    if recommendations:
        rec = recommendations[0]
        assert isinstance(rec, dict)
        assert "base_recommendation" in rec
        assert "routing" in rec
        assert "final_narrative" in rec
        assert isinstance(rec["base_recommendation"], dict)
        assert isinstance(rec["routing"], dict)
        assert isinstance(rec["final_narrative"], str)
