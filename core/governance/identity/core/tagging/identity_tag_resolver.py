"""
Identity Tag Resolver with Trust Networks

Manages identity-based tagging, trust relationships, and tier-aware
permission resolution using distributed tag consensus.
"""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional

import networkx as nx

# Import tagging infrastructure
from core.tagging_system import Tag, TagManager, TagType

# Import identity components
from governance.identity.core.events import (
                try:
                    score = float(tag.metadata.get("score", 0))
                    weight = float(tag.metadata.get("weight", 1.0))
                    scores.append(score * weight)
                except BaseException:

        try:
            # Calculate various centrality measures
            degree_centrality = nx.degree_centrality(self.trust_network).get(identity_id, 0)

            # Only calculate betweenness for smaller networks to avoid performance
            # issues
            if len(self.trust_network) < 100:
                betweenness = nx.betweenness_centrality(self.trust_network).get(identity_id, 0)
            else:
                betweenness = degree_centrality  # Approximate

            # Combine metrics
            influence = (degree_centrality + betweenness) / 2

            return min(1.0, influence)

        except BaseException:

            try:
                current_time = datetime.now(timezone.utc)
                completed_requests = []

                for request_id, request in self.active_consensus_requests.items():
                    # Check if deadline passed or consensus reached
                    if current_time > request.deadline or request.is_consensus_reached():
                        completed_requests.append(request_id)

                        # Process result
                        if request.is_consensus_reached():
                            # Apply tag
                            self.identity_tags[request.target_id].append(request.tag)

                            # Record in history
                            self.tag_history.append(
                                {
                                    "timestamp": current_time,
                                    "lambda_id": request.target_id,
                                    "tag": request.tag,
                                    "action": "consensus_approved",
                                    "votes": len(request.votes),
                                    "approval_rate": sum(1 for v in request.votes.values() if v) / len(request.votes),
                                }
                            )

                            # Publish success event
                            await self.event_publisher.publish_identity_event(
                                IdentityEventType.TAG_CONSENSUS_ACHIEVED,
                                lambda_id=request.target_id,
                                tier_level=request.tag.tier_required or 0,
                                data={
                                    "tag": request.tag.name,
                                    "votes": len(request.votes),
                                    "consensus_threshold": request.tag.consensus_threshold,
                                },
                            )
                        else:
                            # Consensus failed
                            await self.event_publisher.publish_identity_event(
                                IdentityEventType.TAG_CONSENSUS_FAILED,
                                lambda_id=request.target_id,
                                tier_level=request.tag.tier_required or 0,
                                data={
                                    "tag": request.tag.name,
                                    "votes": len(request.votes),
                                    "required_votes": request.required_votes,
                                },
                            )

                # Move completed requests to history
                for request_id in completed_requests:
                    request = self.active_consensus_requests.pop(request_id)
                    self.consensus_history.append(request)

                await asyncio.sleep(1)

            except Exception as e:
                await asyncio.sleep(5)

            try:
                if len(self.trust_network) > 0:
                    # Calculate network density
                    self.network_metrics["network_density"] = nx.density(self.trust_network)

                    # Calculate average trust score
                    all_scores = []
                    for _, _, data in self.trust_network.edges(data=True):
                        all_scores.append(data.get("trust_score", 0))

                    if all_scores:
                        self.network_metrics["avg_trust_score"] = sum(all_scores) / len(all_scores)

                    # Calculate clustering coefficient for smaller networks
                    if len(self.trust_network) < 100:
                        self.network_metrics["clustering_coefficient"] = nx.average_clustering(
                            self.trust_network.to_undirected()
                        )

                await asyncio.sleep(60)  # Analyze every minute

            except Exception as e:
                await asyncio.sleep(60)


    IdentityEventPublisher,
    IdentityEventType,
    get_identity_event_publisher,
)

logger = logging.getLogger("LUKHAS_IDENTITY_TAG_RESOLVER")


class TrustLevel(Enum):
    """Trust levels between identities."""

    NONE = 0.0
    MINIMAL = 0.2
    LOW = 0.4
    MEDIUM = 0.6
    HIGH = 0.8
    FULL = 1.0


class IdentityTagType(Enum):
    """Identity-specific tag types."""

    TIER = "tier"  # Tier level tags
    CAPABILITY = "capability"  # Identity capabilities
    PERMISSION = "permission"  # Access permissions
    TRUST = "trust"  # Trust relationships
    REPUTATION = "reputation"  # Reputation scores
    VERIFICATION = "verification"  # Verification status
    ROLE = "role"  # Identity roles
    CERTIFICATION = "certification"  # Certifications/achievements
    RESTRICTION = "restriction"  # Access restrictions
    PREFERENCE = "preference"  # User preferences


@dataclass
class TrustRelationship:
    """Represents trust between two identities."""

    from_identity: str
    to_identity: str
    trust_level: TrustLevel
    trust_score: float  # 0.0 to 1.0
    established_at: datetime
    last_interaction: datetime
    interaction_count: int = 0
    positive_interactions: int = 0
    negative_interactions: int = 0
    trust_factors: dict[str, float] = field(default_factory=dict)

    def update_interaction(self, positive: bool):
        """Update trust based on interaction."""
        self.interaction_count += 1
        self.last_interaction = datetime.now(timezone.utc)

        if positive:
            self.positive_interactions += 1
        else:
            self.negative_interactions += 1

        # Recalculate trust score
        if self.interaction_count > 0:
            base_score = self.positive_interactions / self.interaction_count

            # Apply decay for old relationships
            age_days = (datetime.now(timezone.utc) - self.established_at).days
            decay_factor = 1.0 / (1.0 + age_days / 365)  # Yearly decay

            self.trust_score = base_score * (0.7 + 0.3 * decay_factor)

            # Update trust level
            if self.trust_score >= 0.8:
                self.trust_level = TrustLevel.FULL
            elif self.trust_score >= 0.6:
                self.trust_level = TrustLevel.HIGH
            elif self.trust_score >= 0.4:
                self.trust_level = TrustLevel.MEDIUM
            elif self.trust_score >= 0.2:
                self.trust_level = TrustLevel.LOW
            else:
                self.trust_level = TrustLevel.MINIMAL


@dataclass
class IdentityTag(Tag):
    """Extended tag for identity system."""

    tier_required: Optional[int] = None
    trust_required: Optional[TrustLevel] = None
    consensus_required: bool = False
    consensus_threshold: float = 0.67
    expiry_time: Optional[datetime] = None
    issuer_id: Optional[str] = None
    verification_proof: Optional[dict[str, Any]] = None


@dataclass
class TagConsensusRequest:
    """Request for tag consensus among trusted identities."""

    request_id: str
    requester_id: str
    target_id: str
    tag: IdentityTag
    trust_network: list[str]  # IDs of trusted identities to consult
    required_votes: int
    deadline: datetime
    votes: dict[str, bool] = field(default_factory=dict)
    vote_weights: dict[str, float] = field(default_factory=dict)

    def add_vote(self, voter_id: str, approve: bool, weight: float = 1.0):
        """Add a weighted vote."""
        self.votes[voter_id] = approve
        self.vote_weights[voter_id] = weight

    def is_consensus_reached(self) -> bool:
        """Check if consensus has been reached."""
        if len(self.votes) < self.required_votes:
            return False

        total_weight = sum(self.vote_weights.values())
        approve_weight = sum(weight for voter, weight in self.vote_weights.items() if self.votes.get(voter, False))

        return approve_weight / total_weight >= self.tag.consensus_threshold


class IdentityTagResolver:
    """
    Manages identity tags with trust network consensus and tier-aware resolution.
    """

    def __init__(self, resolver_id: str = "identity_tag_resolver"):
        self.resolver_id = resolver_id
        self.tag_manager = TagManager()

        # Trust network graph
        self.trust_network = nx.DiGraph()
        self.trust_relationships: dict[tuple[str, str], TrustRelationship] = {}

        # Identity tag storage
        self.identity_tags: dict[str, list[IdentityTag]] = defaultdict(list)
        self.tag_history: list[dict[str, Any]] = []

        # Consensus tracking
        self.active_consensus_requests: dict[str, TagConsensusRequest] = {}
        self.consensus_history: list[TagConsensusRequest] = []

        # Trust network metrics
        self.network_metrics = {
            "total_relationships": 0,
            "avg_trust_score": 0.0,
            "network_density": 0.0,
            "clustering_coefficient": 0.0,
        }

        # Event publisher
        self.event_publisher: Optional[IdentityEventPublisher] = None

        logger.info(f"Identity Tag Resolver {resolver_id} initialized")

    async def initialize(self):
        """Initialize the resolver and connect to systems."""
        # Get event publisher
        self.event_publisher = await get_identity_event_publisher()

        # Initialize tag manager
        await self.tag_manager.initialize()

        # Start consensus processor
        asyncio.create_task(self._process_consensus_requests())

        # Start trust network analyzer
        asyncio.create_task(self._analyze_trust_network())

        logger.info("Identity Tag Resolver initialized")

    async def assign_identity_tag(
        self,
        lambda_id: str,
        tag_type: IdentityTagType,
        tag_value: str,
        tier_level: int,
        metadata: Optional[dict[str, Any]] = None,
        require_consensus: bool = False,
        issuer_id: Optional[str] = None,
        expiry_hours: Optional[int] = None,
    ) -> str:
        """
        Assign a tag to an identity with optional consensus.
        """
        # Create identity tag
        tag = IdentityTag(
            name=f"{tag_type.value}:{tag_value}",
            tag_type=TagType.ENTITY,
            value=tag_value,
            metadata=metadata or {},
            tier_required=tier_level,
            consensus_required=require_consensus,
            issuer_id=issuer_id or "system",
            expiry_time=(datetime.now(timezone.utc) + timedelta(hours=expiry_hours) if expiry_hours else None),
        )

        # Check if consensus is required
        if require_consensus and issuer_id != "system":
            # Get trust network for consensus
            trust_network = self._get_trust_network(issuer_id, min_trust=TrustLevel.MEDIUM)

            if len(trust_network) < 3:
                logger.warning(f"Insufficient trust network for consensus on {lambda_id}")
                return ""

            # Create consensus request
            request_id = f"consensus_{lambda_id}_{tag.name}_{int(datetime.now(timezone.utc).timestamp())}"
            consensus_request = TagConsensusRequest(
                request_id=request_id,
                requester_id=issuer_id,
                target_id=lambda_id,
                tag=tag,
                trust_network=trust_network[:10],  # Limit to 10 trusted identities
                required_votes=min(5, len(trust_network)),
                deadline=datetime.now(timezone.utc) + timedelta(minutes=5),
            )

            self.active_consensus_requests[request_id] = consensus_request

            # Publish consensus request event
            await self.event_publisher.publish_colony_event(
                IdentityEventType.TAG_CONSENSUS_REQUESTED,
                lambda_id=lambda_id,
                tier_level=tier_level,
                colony_id=self.resolver_id,
                consensus_data={
                    "tag_type": tag_type.value,
                    "tag_value": tag_value,
                    "trust_network_size": len(trust_network),
                    "required_votes": consensus_request.required_votes,
                },
            )

            return request_id

        else:
            # Direct assignment (system or no consensus required)
            self.identity_tags[lambda_id].append(tag)

            # Record in history
            self.tag_history.append(
                {
                    "timestamp": datetime.now(timezone.utc),
                    "lambda_id": lambda_id,
                    "tag": tag,
                    "action": "assigned",
                    "issuer": issuer_id or "system",
                }
            )

            # Publish tag assignment event
            await self.event_publisher.publish_identity_event(
                IdentityEventType.TAG_ASSIGNED,
                lambda_id=lambda_id,
                tier_level=tier_level,
                data={
                    "tag_type": tag_type.value,
                    "tag_value": tag_value,
                    "metadata": metadata,
                },
            )

            return tag.name

    async def establish_trust_relationship(
        self,
        from_identity: str,
        to_identity: str,
        initial_trust: TrustLevel = TrustLevel.LOW,
        trust_factors: Optional[dict[str, float]] = None,
    ) -> bool:
        """
        Establish or update trust relationship between identities.
        """
        relationship_key = (from_identity, to_identity)

        if relationship_key in self.trust_relationships:
            # Update existing relationship
            relationship = self.trust_relationships[relationship_key]
            relationship.last_interaction = datetime.now(timezone.utc)
            if trust_factors:
                relationship.trust_factors.update(trust_factors)
        else:
            # Create new relationship
            relationship = TrustRelationship(
                from_identity=from_identity,
                to_identity=to_identity,
                trust_level=initial_trust,
                trust_score=initial_trust.value,
                established_at=datetime.now(timezone.utc),
                last_interaction=datetime.now(timezone.utc),
                trust_factors=trust_factors or {},
            )
            self.trust_relationships[relationship_key] = relationship

            # Add to trust network graph
            self.trust_network.add_edge(
                from_identity,
                to_identity,
                trust_score=initial_trust.value,
                relationship=relationship,
            )

        # Update network metrics
        self.network_metrics["total_relationships"] = len(self.trust_relationships)

        # Publish trust establishment event
        await self.event_publisher.publish_identity_event(
            IdentityEventType.TRUST_ESTABLISHED,
            lambda_id=from_identity,
            tier_level=0,  # Trust is tier-independent
            data={
                "to_identity": to_identity,
                "trust_level": initial_trust.name,
                "trust_score": relationship.trust_score,
            },
        )

        return True

    async def update_trust_interaction(
        self,
        from_identity: str,
        to_identity: str,
        positive: bool,
        interaction_type: str,
        details: Optional[dict[str, Any]] = None,
    ):
        """
        Update trust based on interaction outcome.
        """
        relationship_key = (from_identity, to_identity)

        if relationship_key not in self.trust_relationships:
            # Auto-establish minimal trust on first interaction
            await self.establish_trust_relationship(
                from_identity,
                to_identity,
                TrustLevel.MINIMAL if positive else TrustLevel.NONE,
            )

        relationship = self.trust_relationships[relationship_key]
        old_trust = relationship.trust_level

        # Update based on interaction
        relationship.update_interaction(positive)

        # Update graph edge weight
        self.trust_network[from_identity][to_identity]["trust_score"] = relationship.trust_score

        # Publish trust update event if level changed
        if old_trust != relationship.trust_level:
            await self.event_publisher.publish_identity_event(
                IdentityEventType.TRUST_UPDATED,
                lambda_id=from_identity,
                tier_level=0,
                data={
                    "to_identity": to_identity,
                    "old_trust": old_trust.name,
                    "new_trust": relationship.trust_level.name,
                    "trust_score": relationship.trust_score,
                    "interaction_type": interaction_type,
                },
            )

    def resolve_identity_permissions(self, lambda_id: str, resource: str, tier_level: int) -> dict[str, Any]:
        """
        Resolve permissions for identity based on tags and trust network.
        """
        permissions = {
            "allowed": False,
            "reason": "",
            "trust_boost": 0.0,
            "applicable_tags": [],
        }

        # Get identity tags
        identity_tags = self.identity_tags.get(lambda_id, [])

        # Filter valid tags (not expired, tier appropriate)
        valid_tags = []
        for tag in identity_tags:
            if tag.expiry_time and tag.expiry_time < datetime.now(timezone.utc):
                continue
            if tag.tier_required and tier_level < tag.tier_required:
                continue
            valid_tags.append(tag)

        # Check permission tags
        permission_tags = [tag for tag in valid_tags if tag.name.startswith("permission:") and resource in tag.value]

        if permission_tags:
            permissions["allowed"] = True
            permissions["applicable_tags"] = [tag.name for tag in permission_tags]

        # Check restriction tags
        restriction_tags = [tag for tag in valid_tags if tag.name.startswith("restriction:") and resource in tag.value]

        if restriction_tags:
            permissions["allowed"] = False
            permissions["reason"] = "Resource restricted"
            permissions["applicable_tags"] = [tag.name for tag in restriction_tags]
            return permissions

        # Calculate trust boost from network
        trust_boost = self._calculate_trust_network_boost(lambda_id)
        permissions["trust_boost"] = trust_boost

        # Apply trust boost to tier-based permissions
        if trust_boost > 0.5 and tier_level >= 2:
            permissions["allowed"] = True
            permissions["reason"] = "Trust network endorsement"

        return permissions

    def get_identity_reputation(self, lambda_id: str) -> dict[str, Any]:
        """
        Calculate identity reputation from tags and trust network.
        """
        # Get reputation tags
        identity_tags = self.identity_tags.get(lambda_id, [])
        reputation_tags = [tag for tag in identity_tags if tag.name.startswith("reputation:")]

        # Calculate base reputation from tags
        tag_reputation = 0.0
        if reputation_tags:
            scores = []
            for tag in reputation_tags:
            if scores:
                tag_reputation = sum(scores) / len(scores)

        # Calculate trust network reputation
        trust_reputation = self._calculate_trust_reputation(lambda_id)

        # Calculate network influence
        influence_score = self._calculate_network_influence(lambda_id)

        # Combine scores
        overall_reputation = tag_reputation * 0.4 + trust_reputation * 0.4 + influence_score * 0.2

        return {
            "overall_reputation": overall_reputation,
            "tag_reputation": tag_reputation,
            "trust_reputation": trust_reputation,
            "network_influence": influence_score,
            "reputation_tags": len(reputation_tags),
            "trust_relationships": self._count_trust_relationships(lambda_id),
        }

    def _get_trust_network(self, identity_id: str, min_trust: TrustLevel = TrustLevel.LOW) -> list[str]:
        """Get trusted identities above threshold."""
        trusted = []

        if identity_id in self.trust_network:
            for neighbor in self.trust_network[identity_id]:
                edge_data = self.trust_network[identity_id][neighbor]
                if edge_data["trust_score"] >= min_trust.value:
                    trusted.append(neighbor)

        # Sort by trust score
        trusted.sort(
            key=lambda x: self.trust_network[identity_id][x]["trust_score"],
            reverse=True,
        )

        return trusted

    def _calculate_trust_network_boost(self, identity_id: str) -> float:
        """Calculate trust boost from network connections."""
        if identity_id not in self.trust_network:
            return 0.0

        # Get incoming trust (who trusts this identity)
        incoming_trust = []
        for node in self.trust_network:
            if identity_id in self.trust_network[node]:
                trust_score = self.trust_network[node][identity_id]["trust_score"]
                incoming_trust.append(trust_score)

        if not incoming_trust:
            return 0.0

        # Calculate boost based on number and strength of trust relationships
        avg_trust = sum(incoming_trust) / len(incoming_trust)
        # Max boost at 10+ relationships
        trust_count_factor = min(1.0, len(incoming_trust) / 10)

        return avg_trust * trust_count_factor

    def _calculate_trust_reputation(self, identity_id: str) -> float:
        """Calculate reputation based on trust relationships."""
        outgoing_scores = []
        incoming_scores = []

        # Outgoing trust (how well they trust others)
        for relationship in self.trust_relationships.values():
            if relationship.from_identity == identity_id:
                outgoing_scores.append(relationship.trust_score)
            elif relationship.to_identity == identity_id:
                incoming_scores.append(relationship.trust_score)

        outgoing_avg = sum(outgoing_scores) / len(outgoing_scores) if outgoing_scores else 0.5
        incoming_avg = sum(incoming_scores) / len(incoming_scores) if incoming_scores else 0.5

        # Higher weight on incoming trust (being trusted by others)
        return incoming_avg * 0.7 + outgoing_avg * 0.3

    def _calculate_network_influence(self, identity_id: str) -> float:
        """Calculate network influence using graph metrics."""
        if identity_id not in self.trust_network:
            return 0.0

    def _count_trust_relationships(self, identity_id: str) -> dict[str, int]:
        """Count trust relationships by type."""
        counts = {"outgoing": 0, "incoming": 0, "mutual": 0}

        for from_id, to_id in self.trust_relationships:
            if from_id == identity_id:
                counts["outgoing"] += 1
                if (to_id, from_id) in self.trust_relationships:
                    counts["mutual"] += 1
            elif to_id == identity_id:
                counts["incoming"] += 1

        return counts

    async def _process_consensus_requests(self):
        """Background processor for consensus requests."""
        while True:
    async def _analyze_trust_network(self):
        """Periodically analyze trust network metrics."""
        while True:
    def get_resolver_statistics(self) -> dict[str, Any]:
        """Get comprehensive resolver statistics."""
        return {
            "total_identities_tagged": len(self.identity_tags),
            "total_tags": sum(len(tags) for tags in self.identity_tags.values()),
            "trust_relationships": len(self.trust_relationships),
            "network_metrics": self.network_metrics,
            "active_consensus_requests": len(self.active_consensus_requests),
            "consensus_history_size": len(self.consensus_history),
            "tag_history_size": len(self.tag_history),
        }
