"""
Consensus Engine for Multi-Model Decision Making

Coordinates multiple AI models to reach consensus on complex decisions,
combining their outputs with confidence weighting and disagreement analysis.
"""

import asyncio
import json
import logging
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .model_router import ModelResponse, ModelRouter, ModelType, RoutingRequest, TaskType

logger = logging.getLogger(__name__)


class ConsensusMethod(Enum):
    """Methods for reaching consensus"""
    MAJORITY_VOTE = "majority_vote"          # Simple majority voting
    WEIGHTED_CONFIDENCE = "weighted_confidence"  # Weight by confidence scores
    EXPERT_OVERRIDE = "expert_override"      # Best model for task overrides
    ITERATIVE_REFINEMENT = "iterative_refinement"  # Multiple rounds of consensus
    DEMOCRATIC = "democratic"                # Equal weight all models


class AgreementLevel(Enum):
    """Levels of agreement between models"""
    STRONG_CONSENSUS = "strong_consensus"    # >90% agreement
    CONSENSUS = "consensus"                  # >70% agreement
    MAJORITY = "majority"                    # >50% agreement
    SPLIT = "split"                          # No clear majority
    CONTRADICTION = "contradiction"          # Direct contradictions


@dataclass
class ModelVote:
    """A vote from a model in consensus process"""
    model_type: ModelType
    response: ModelResponse
    vote_weight: float = 1.0
    reasoning: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConsensusResult:
    """Result of consensus process"""
    consensus_content: str
    agreement_level: AgreementLevel
    confidence: float
    participating_models: list[ModelType]
    individual_votes: list[ModelVote]
    disagreement_points: list[str] = field(default_factory=list)
    consensus_method: ConsensusMethod = ConsensusMethod.WEIGHTED_CONFIDENCE
    processing_time_ms: float = 0.0
    total_cost: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ConsensusEngine:
    """
    Multi-model consensus engine for AGI decision making

    Coordinates multiple AI models to reach consensus on complex questions,
    providing more robust and reliable answers than single model responses.
    """

    def __init__(self, model_router: Optional[ModelRouter] = None):
        """Initialize consensus engine with model router"""
        self.model_router = model_router or ModelRouter()
        self.consensus_history = []
        self.disagreement_patterns = {}

        logger.info("🤝 Consensus engine initialized")

    async def reach_consensus(self,
                            question: str,
                            context: Optional[dict[str, Any]] = None,
                            models: Optional[list[ModelType]] = None,
                            method: ConsensusMethod = ConsensusMethod.WEIGHTED_CONFIDENCE,
                            min_models: int = 3,
                            task_type: TaskType = TaskType.REASONING) -> ConsensusResult:
        """
        Reach consensus among multiple models on a question

        Args:
            question: The question/task to get consensus on
            context: Optional context for the question
            models: Specific models to use (if None, selects optimal set)
            method: Consensus method to use
            min_models: Minimum number of models for consensus
            task_type: Type of task for optimal model selection

        Returns:
            Consensus result with aggregated response
        """
        logger.info(f"🤝 Seeking consensus on: {question[:100]}...")

        start_time = asyncio.get_event_loop().time()

        try:
            # Step 1: Select models if not specified
            if not models:
                models = await self._select_consensus_models(question, task_type, min_models)

            # Step 2: Gather individual model responses
            votes = await self._gather_model_votes(question, models, context, task_type)

            if len(votes) < 2:
                logger.warning("Insufficient model responses for consensus")
                return self._create_fallback_consensus(question, votes)

            # Step 3: Apply consensus method
            consensus_result = await self._apply_consensus_method(votes, method)

            # Step 4: Analyze agreement level
            consensus_result.agreement_level = self._analyze_agreement(votes)

            # Step 5: Identify disagreement points
            consensus_result.disagreement_points = self._identify_disagreements(votes)

            # Step 6: Calculate final metrics
            end_time = asyncio.get_event_loop().time()
            consensus_result.processing_time_ms = (end_time - start_time) * 1000
            consensus_result.total_cost = sum(vote.response.cost_estimate for vote in votes)
            consensus_result.participating_models = [vote.model_type for vote in votes]
            consensus_result.individual_votes = votes

            # Step 7: Update tracking
            self.consensus_history.append(consensus_result)
            self._update_disagreement_patterns(votes)

            logger.info(f"✅ Consensus reached: {consensus_result.agreement_level.value} "
                       f"({consensus_result.confidence:.3f} confidence, {len(votes)} models)")

            return consensus_result

        except Exception as e:
            logger.error(f"❌ Consensus process failed: {e}")
            return self._create_error_consensus(question, str(e))

    async def _select_consensus_models(self, question: str, task_type: TaskType,
                                     min_models: int) -> list[ModelType]:
        """Select optimal set of models for consensus"""

        # Get all available models with their capabilities
        capabilities = self.model_router.get_model_capabilities()

        # Score models for this specific task
        scored_models = []
        task_weights = self._get_task_selection_weights(task_type)

        for model_name, caps in capabilities.items():
            try:
                model_type = ModelType(model_name)

                # Calculate task-specific score
                score = (
                    caps["reasoning_score"] * task_weights["reasoning"] +
                    caps["creativity_score"] * task_weights["creativity"] +
                    caps["code_score"] * task_weights["code"] +
                    caps["analysis_score"] * task_weights["analysis"]
                )

                # Bonus for diversity (different model families)
                if "gpt" in model_name.lower():
                    family_bonus = 0.0
                elif "claude" in model_name.lower():
                    family_bonus = 0.1
                elif "gemini" in model_name.lower():
                    family_bonus = 0.2
                else:
                    family_bonus = 0.05

                total_score = score + family_bonus
                scored_models.append((model_type, total_score))

            except ValueError:
                # Skip invalid model types
                continue

        # Sort by score and select diverse set
        scored_models.sort(key=lambda x: x[1], reverse=True)

        # Select models ensuring diversity
        selected = []
        families_used = set()

        for model_type, score in scored_models:
            if len(selected) >= min_models + 2:  # Select a few extra for robustness
                break

            # Get model family
            family = model_type.value.split("-")[0].lower()

            # Always select top model, then ensure diversity
            if not selected or family not in families_used or len(selected) < min_models:
                selected.append(model_type)
                families_used.add(family)

        # Ensure minimum models
        if len(selected) < min_models:
            # Add more models if needed
            for model_type, _ in scored_models:
                if model_type not in selected and len(selected) < min_models:
                    selected.append(model_type)

        logger.debug(f"Selected {len(selected)} models for consensus: {[m.value for m in selected]}")
        return selected

    def _get_task_selection_weights(self, task_type: TaskType) -> dict[str, float]:
        """Get weights for model selection by task type"""

        weights = {
            TaskType.REASONING: {"reasoning": 0.6, "creativity": 0.1, "code": 0.1, "analysis": 0.2},
            TaskType.CODE_GENERATION: {"reasoning": 0.2, "creativity": 0.2, "code": 0.5, "analysis": 0.1},
            TaskType.CREATIVE_WRITING: {"reasoning": 0.1, "creativity": 0.7, "code": 0.0, "analysis": 0.2},
            TaskType.ANALYSIS: {"reasoning": 0.3, "creativity": 0.1, "code": 0.1, "analysis": 0.5},
            TaskType.MATH: {"reasoning": 0.6, "creativity": 0.0, "code": 0.2, "analysis": 0.2},
            TaskType.RESEARCH: {"reasoning": 0.4, "creativity": 0.1, "code": 0.1, "analysis": 0.4}
        }

        return weights.get(task_type, {"reasoning": 0.25, "creativity": 0.25, "code": 0.25, "analysis": 0.25})

    async def _gather_model_votes(self, question: str, models: list[ModelType],
                                context: Optional[dict[str, Any]],
                                task_type: TaskType) -> list[ModelVote]:
        """Gather responses from all specified models"""

        votes = []

        # Create routing requests for each model
        tasks = []
        for model_type in models:
            request = RoutingRequest(
                task_type=task_type,
                content=question,
                context=context,
                preferred_models=[model_type]  # Force specific model
            )
            tasks.append(self._get_single_model_vote(model_type, request))

        # Execute all requests concurrently
        vote_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for i, result in enumerate(vote_results):
            if isinstance(result, Exception):
                logger.warning(f"Model {models[i].value} failed: {result}")
                continue

            if result:
                votes.append(result)

        logger.debug(f"Gathered {len(votes)} votes from {len(models)} models")
        return votes

    async def _get_single_model_vote(self, model_type: ModelType,
                                   request: RoutingRequest) -> Optional[ModelVote]:
        """Get a single vote from a specific model"""

        try:
            decision, response = await self.model_router.route_request(request)

            # Create vote with confidence-based weighting
            vote_weight = response.confidence

            return ModelVote(
                model_type=model_type,
                response=response,
                vote_weight=vote_weight,
                reasoning=f"Model {model_type.value} response with {response.confidence:.3f} confidence",
                metadata={
                    "processing_time_ms": response.processing_time_ms,
                    "tokens_used": response.tokens_used,
                    "cost": response.cost_estimate
                }
            )

        except Exception as e:
            logger.warning(f"Failed to get vote from {model_type.value}: {e}")
            return None

    async def _apply_consensus_method(self, votes: list[ModelVote],
                                    method: ConsensusMethod) -> ConsensusResult:
        """Apply the specified consensus method to votes"""

        if method == ConsensusMethod.MAJORITY_VOTE:
            return await self._majority_vote_consensus(votes)
        elif method == ConsensusMethod.WEIGHTED_CONFIDENCE:
            return await self._weighted_confidence_consensus(votes)
        elif method == ConsensusMethod.EXPERT_OVERRIDE:
            return await self._expert_override_consensus(votes)
        elif method == ConsensusMethod.ITERATIVE_REFINEMENT:
            return await self._iterative_refinement_consensus(votes)
        elif method == ConsensusMethod.DEMOCRATIC:
            return await self._democratic_consensus(votes)
        else:
            # Default to weighted confidence
            return await self._weighted_confidence_consensus(votes)

    async def _weighted_confidence_consensus(self, votes: list[ModelVote]) -> ConsensusResult:
        """Create consensus based on confidence-weighted responses"""

        if not votes:
            raise ValueError("No votes provided for consensus")

        # Weight responses by confidence
        total_weight = sum(vote.vote_weight * vote.response.confidence for vote in votes)

        if total_weight == 0:
            # Fallback to equal weighting
            consensus_content = self._combine_responses([vote.response.content for vote in votes])
            confidence = 0.5
        else:
            # Weighted combination
            weighted_responses = []
            confidence_sum = 0

            for vote in votes:
                weight = vote.vote_weight * vote.response.confidence / total_weight
                weighted_responses.append(f"[Weight: {weight:.3f}] {vote.response.content}")
                confidence_sum += vote.response.confidence * weight

            consensus_content = self._synthesize_weighted_responses(votes, total_weight)
            confidence = min(1.0, confidence_sum)

        return ConsensusResult(
            consensus_content=consensus_content,
            agreement_level=AgreementLevel.CONSENSUS,  # Will be updated later
            confidence=confidence,
            participating_models=[],  # Will be filled later
            individual_votes=[],
            consensus_method=ConsensusMethod.WEIGHTED_CONFIDENCE
        )

    async def _majority_vote_consensus(self, votes: list[ModelVote]) -> ConsensusResult:
        """Simple majority vote consensus"""

        # For text responses, this is complex - we'll use similarity clustering
        # For now, use the most confident response as representative

        votes_by_confidence = sorted(votes, key=lambda v: v.response.confidence, reverse=True)

        # Use top response as base, note agreement in content
        top_vote = votes_by_confidence[0]

        consensus_content = f"Majority consensus (led by {top_vote.model_type.value}): {top_vote.response.content}"

        # Average confidence
        avg_confidence = sum(vote.response.confidence for vote in votes) / len(votes)

        return ConsensusResult(
            consensus_content=consensus_content,
            agreement_level=AgreementLevel.MAJORITY,
            confidence=avg_confidence,
            participating_models=[],
            individual_votes=[],
            consensus_method=ConsensusMethod.MAJORITY_VOTE
        )

    async def _expert_override_consensus(self, votes: list[ModelVote]) -> ConsensusResult:
        """Use the most capable model's response as consensus"""

        # Find the vote with highest capability score for this task
        best_vote = max(votes, key=lambda v: v.vote_weight * v.response.confidence)

        consensus_content = f"Expert consensus from {best_vote.model_type.value}: {best_vote.response.content}"

        # Use expert's confidence, but note other model input
        other_models = [v.model_type.value for v in votes if v != best_vote]
        if other_models:
            consensus_content += f"\n\n(Consulted with: {', '.join(other_models)})"

        return ConsensusResult(
            consensus_content=consensus_content,
            agreement_level=AgreementLevel.CONSENSUS,
            confidence=best_vote.response.confidence,
            participating_models=[],
            individual_votes=[],
            consensus_method=ConsensusMethod.EXPERT_OVERRIDE
        )

    async def _democratic_consensus(self, votes: list[ModelVote]) -> ConsensusResult:
        """Equal weight democratic consensus"""

        # Give equal weight to all responses
        all_responses = [vote.response.content for vote in votes]
        consensus_content = self._combine_responses(all_responses)

        # Average all confidences equally
        avg_confidence = sum(vote.response.confidence for vote in votes) / len(votes)

        return ConsensusResult(
            consensus_content=consensus_content,
            agreement_level=AgreementLevel.CONSENSUS,
            confidence=avg_confidence,
            participating_models=[],
            individual_votes=[],
            consensus_method=ConsensusMethod.DEMOCRATIC
        )

    async def _iterative_refinement_consensus(self, votes: list[ModelVote]) -> ConsensusResult:
        """Multiple rounds of consensus refinement"""

        # For now, implement as enhanced weighted consensus
        # In full implementation, would do multiple rounds with feedback

        initial_consensus = await self._weighted_confidence_consensus(votes)

        # Simulate refinement by boosting confidence if models agree
        agreement_bonus = self._calculate_agreement_bonus(votes)
        refined_confidence = min(1.0, initial_consensus.confidence + agreement_bonus)

        initial_consensus.confidence = refined_confidence
        initial_consensus.consensus_method = ConsensusMethod.ITERATIVE_REFINEMENT

        return initial_consensus

    def _synthesize_weighted_responses(self, votes: list[ModelVote], total_weight: float) -> str:
        """Synthesize responses based on their weights"""

        # Find the most confident response as the base
        top_vote = max(votes, key=lambda v: v.response.confidence)

        # Create synthesis
        synthesis = f"Consensus synthesis (based on {len(votes)} models):\n\n"
        synthesis += top_vote.response.content

        # Add perspectives from other models
        other_votes = [v for v in votes if v != top_vote and v.response.confidence > 0.5]

        if other_votes:
            synthesis += "\n\nAdditional perspectives:\n"
            for vote in other_votes[:2]:  # Limit to top 2 additional perspectives
                weight = vote.vote_weight * vote.response.confidence / total_weight
                synthesis += f"• {vote.model_type.value} (weight: {weight:.2f}): {vote.response.content[:200]}...\n"

        return synthesis

    def _combine_responses(self, responses: list[str]) -> str:
        """Combine multiple responses into a cohesive consensus"""

        if not responses:
            return "No responses to combine"

        if len(responses) == 1:
            return responses[0]

        # Simple combination - in production would use more sophisticated NLP
        combined = f"Combined consensus from {len(responses)} models:\n\n"
        combined += responses[0]  # Use first response as base

        if len(responses) > 1:
            combined += f"\n\n(Incorporating insights from {len(responses)-1} additional models)"

        return combined

    def _analyze_agreement(self, votes: list[ModelVote]) -> AgreementLevel:
        """Analyze the level of agreement between model responses"""

        if len(votes) <= 1:
            return AgreementLevel.CONSENSUS

        # Simple agreement analysis based on confidence distribution
        confidences = [vote.response.confidence for vote in votes]

        # Calculate agreement metrics
        avg_confidence = statistics.mean(confidences)
        confidence_std = statistics.stdev(confidences) if len(confidences) > 1 else 0

        # High average confidence + low std = strong consensus
        if avg_confidence > 0.8 and confidence_std < 0.1:
            return AgreementLevel.STRONG_CONSENSUS
        elif avg_confidence > 0.6 and confidence_std < 0.2:
            return AgreementLevel.CONSENSUS
        elif avg_confidence > 0.5:
            return AgreementLevel.MAJORITY
        elif confidence_std > 0.3:
            return AgreementLevel.SPLIT
        else:
            return AgreementLevel.CONTRADICTION

    def _identify_disagreements(self, votes: list[ModelVote]) -> list[str]:
        """Identify points of disagreement between models"""

        disagreements = []

        # Find low confidence responses
        low_confidence_votes = [v for v in votes if v.response.confidence < 0.6]

        for vote in low_confidence_votes:
            disagreements.append(f"{vote.model_type.value} expressed uncertainty (confidence: {vote.response.confidence:.3f})")

        # Find outlier responses (very different confidence from average)
        if len(votes) > 2:
            avg_confidence = sum(v.response.confidence for v in votes) / len(votes)

            for vote in votes:
                if abs(vote.response.confidence - avg_confidence) > 0.3:
                    disagreements.append(f"{vote.model_type.value} confidence ({vote.response.confidence:.3f}) differs significantly from average ({avg_confidence:.3f})")

        return disagreements

    def _calculate_agreement_bonus(self, votes: list[ModelVote]) -> float:
        """Calculate bonus for high agreement between models"""

        if len(votes) <= 1:
            return 0.0

        confidences = [vote.response.confidence for vote in votes]
        avg_confidence = statistics.mean(confidences)
        confidence_std = statistics.stdev(confidences) if len(confidences) > 1 else 0

        # Bonus inversely related to standard deviation
        agreement_bonus = max(0.0, 0.1 - confidence_std) if avg_confidence > 0.7 else 0.0

        return agreement_bonus

    def _update_disagreement_patterns(self, votes: list[ModelVote]):
        """Track disagreement patterns between models"""

        for i, vote_a in enumerate(votes):
            for _j, vote_b in enumerate(votes[i+1:], i+1):
                model_pair = tuple(sorted([vote_a.model_type.value, vote_b.model_type.value]))

                confidence_diff = abs(vote_a.response.confidence - vote_b.response.confidence)

                if model_pair not in self.disagreement_patterns:
                    self.disagreement_patterns[model_pair] = {
                        "total_comparisons": 0,
                        "disagreements": 0,
                        "avg_confidence_diff": 0.0
                    }

                pattern = self.disagreement_patterns[model_pair]
                pattern["total_comparisons"] += 1

                if confidence_diff > 0.3:  # Significant disagreement
                    pattern["disagreements"] += 1

                # Update running average of confidence differences
                n = pattern["total_comparisons"]
                pattern["avg_confidence_diff"] = ((n - 1) * pattern["avg_confidence_diff"] + confidence_diff) / n

    def _create_fallback_consensus(self, question: str, votes: list[ModelVote]) -> ConsensusResult:
        """Create fallback consensus when insufficient responses"""

        if votes:
            vote = votes[0]
            content = f"Single model response from {vote.model_type.value}: {vote.response.content}"
            confidence = vote.response.confidence * 0.7  # Reduce confidence for single response
            cost = vote.response.cost_estimate
        else:
            content = f"Unable to get model responses for: {question}"
            confidence = 0.0
            cost = 0.0

        return ConsensusResult(
            consensus_content=content,
            agreement_level=AgreementLevel.SPLIT,
            confidence=confidence,
            participating_models=[vote.model_type for vote in votes],
            individual_votes=votes,
            total_cost=cost,
            consensus_method=ConsensusMethod.WEIGHTED_CONFIDENCE
        )

    def _create_error_consensus(self, question: str, error: str) -> ConsensusResult:
        """Create error consensus result"""

        return ConsensusResult(
            consensus_content=f"Consensus process failed for question: '{question}'. Error: {error}",
            agreement_level=AgreementLevel.CONTRADICTION,
            confidence=0.0,
            participating_models=[],
            individual_votes=[],
            disagreement_points=[f"Process error: {error}"],
            total_cost=0.0
        )

    def get_consensus_metrics(self) -> dict[str, Any]:
        """Get consensus engine performance metrics"""

        if not self.consensus_history:
            return {"total_consensus_attempts": 0}

        # Calculate success metrics
        successful_consensus = [c for c in self.consensus_history if c.confidence > 0.6]
        strong_consensus = [c for c in self.consensus_history if c.agreement_level == AgreementLevel.STRONG_CONSENSUS]

        # Average metrics
        avg_confidence = sum(c.confidence for c in self.consensus_history) / len(self.consensus_history)
        avg_models = sum(len(c.participating_models) for c in self.consensus_history) / len(self.consensus_history)
        avg_cost = sum(c.total_cost for c in self.consensus_history) / len(self.consensus_history)
        avg_time = sum(c.processing_time_ms for c in self.consensus_history) / len(self.consensus_history)

        # Agreement distribution
        agreement_counts = {}
        for consensus in self.consensus_history:
            level = consensus.agreement_level.value
            agreement_counts[level] = agreement_counts.get(level, 0) + 1

        return {
            "total_consensus_attempts": len(self.consensus_history),
            "successful_consensus_rate": len(successful_consensus) / len(self.consensus_history),
            "strong_consensus_rate": len(strong_consensus) / len(self.consensus_history),
            "average_confidence": round(avg_confidence, 3),
            "average_models_per_consensus": round(avg_models, 1),
            "average_cost_per_consensus": round(avg_cost, 4),
            "average_processing_time_ms": round(avg_time, 1),
            "agreement_level_distribution": agreement_counts,
            "model_disagreement_patterns": {
                pair: {
                    "disagreement_rate": pattern["disagreements"] / pattern["total_comparisons"],
                    "avg_confidence_diff": round(pattern["avg_confidence_diff"], 3)
                }
                for pair, pattern in self.disagreement_patterns.items()
                if pattern["total_comparisons"] > 2  # Only show patterns with sufficient data
            }
        }
