"""
The Collective Ad Mind.

This module serves as the main entry point for the Collective Intelligence Layer,
integrating clustering, swarm recommendations, and altruistic routing.
"""

from typing import Any, Dict, List, Optional

from .clusters.consciousness_clusters import ConsciousnessClusteringEngine
from .swarm.swarm_recommendations import SwarmRecommendationSystem
from .routing.altruistic_router import AltruisticAdRouter


class CollectiveAdMind:
    """
    Harnesses collective human intelligence for ad optimization.
    This class acts as a facade for the various components of the
    Collective Intelligence Layer.
    """

    # ΛTAG: collective, facade, mind

    def __init__(self):
        """
        Initializes the CollectiveAdMind and its sub-components.
        """
        self.clustering_engine = ConsciousnessClusteringEngine()
        self.swarm_recommender = SwarmRecommendationSystem()
        self.altruistic_router = AltruisticAdRouter()

    async def get_collective_recommendations(
        self, user_id: str
    ) -> List[Dict[str, Any]]:
        """
        Generates a set of recommendations for a user, enhanced with
        collective intelligence and altruistic routing.

        Args:
            user_id: The ID of the user.

        Returns:
            A list of dictionaries, each representing a full, routed recommendation.
        """
        # 1. Find the user's consciousness cluster
        cluster_id = await self.clustering_engine.find_cluster_for_user(user_id)

        # 2. Get swarm recommendations for that cluster
        swarm_recs = await self.swarm_recommender.get_swarm_recommendations(
            user_id, cluster_id
        )

        # 3. Find altruistic routing for each recommendation
        routed_recommendations = []
        for rec in swarm_recs:
            routing_path = await self.altruistic_router.find_routing_path(user_id, rec)

            full_recommendation = {
                "base_recommendation": rec,
                "routing": routing_path,
                "final_narrative": routing_path.get("narrative", rec.get("description")),
            }
            routed_recommendations.append(full_recommendation)

        return routed_recommendations
