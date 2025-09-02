#!/usr/bin/env python3
"""
Predictive Harm Prevention System
Uses AI to predict potential harm pathways before they occur.
Simulates future states and intervenes proactively to protect users.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

import numpy as np
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class HarmType(Enum):
    """Types of potential harm to predict and prevent"""

    ADDICTION = "addiction"
    EMOTIONAL_DISTRESS = "emotional_distress"
    FINANCIAL_HARM = "financial_harm"
    PRIVACY_VIOLATION = "privacy_violation"
    MANIPULATION = "manipulation"
    COGNITIVE_OVERLOAD = "cognitive_overload"
    SOCIAL_ISOLATION = "social_isolation"
    HEALTH_IMPACT = "health_impact"
    DEVELOPMENTAL_HARM = "developmental_harm"  # For children
    TRUST_EROSION = "trust_erosion"


@dataclass
class HarmPrediction:
    """A prediction of potential harm"""

    harm_type: HarmType
    probability: float  # 0-1
    timeline: str  # When harm might occur
    severity: int  # 1-10
    confidence: float  # Model confidence in prediction
    indicators: list[str]  # Warning signs
    trajectory: list[dict[str, Any]]  # Predicted path to harm
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PreventiveIntervention:
    """A suggested intervention to prevent harm"""

    intervention_id: str
    description: str
    timing: str  # immediate, short-term, long-term
    effectiveness: float  # Expected effectiveness 0-1
    user_impact: str  # How it affects user experience
    implementation: dict[str, Any]  # Specific actions to take
    alternatives: list[str] = field(default_factory=list)


@dataclass
class SimulatedFuture:
    """A simulated future state"""

    timeline: list[dict[str, Any]]  # Sequence of events
    end_state: dict[str, Any]  # Final user state
    harm_events: list[HarmPrediction]  # Predicted harms
    intervention_points: list[dict[str, Any]]  # Where to intervene
    probability: float  # Likelihood of this future


class PredictiveHarmPrevention:
    """
    Predictive Harm Prevention System using AI to simulate futures.

    This system models potential harm pathways and suggests interventions
    before harm occurs, protecting users proactively.
    """

    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai = AsyncOpenAI(api_key=openai_api_key) if openai_api_key else None

        # Configuration
        self.prediction_horizon_hours = 24  # How far to look ahead
        self.simulation_branches = 5  # Number of futures to simulate
        self.harm_threshold = 0.3  # Probability threshold for intervention
        self.confidence_threshold = 0.7  # Minimum confidence for action

        # State tracking
        self.user_trajectories: dict[str, list[dict[str, Any]]] = {}
        self.predictions: list[HarmPrediction] = []
        self.interventions: list[PreventiveIntervention] = []
        self.simulation_cache: dict[str, SimulatedFuture] = {}

        # Harm indicators database
        self.harm_indicators = self._initialize_harm_indicators()

        logger.info("Predictive Harm Prevention initialized")

    def _initialize_harm_indicators(self) -> dict[HarmType, list[str]]:
        """Initialize database of early warning indicators"""
        return {
            HarmType.ADDICTION: [
                "increasing_session_duration",
                "decreasing_break_intervals",
                "compulsive_checking_behavior",
                "neglecting_other_activities",
                "anxiety_when_restricted",
                "tolerance_building",
            ],
            HarmType.EMOTIONAL_DISTRESS: [
                "negative_sentiment_increase",
                "social_withdrawal",
                "sleep_pattern_disruption",
                "mood_volatility",
                "help_seeking_queries",
                "self_harm_indicators",
            ],
            HarmType.FINANCIAL_HARM: [
                "impulse_purchase_patterns",
                "debt_accumulation_signals",
                "risky_financial_behavior",
                "desperation_indicators",
                "bypassing_budget_limits",
                "loan_seeking_behavior",
            ],
            HarmType.PRIVACY_VIOLATION: [
                "oversharing_patterns",
                "weakened_privacy_settings",
                "data_exposure_risks",
                "social_engineering_vulnerability",
                "identity_theft_indicators",
                "location_oversharing",
            ],
            HarmType.MANIPULATION: [
                "susceptibility_patterns",
                "decision_fatigue",
                "emotional_vulnerability",
                "trust_exploitation_risk",
                "cognitive_bias_amplification",
                "reduced_critical_thinking",
            ],
            HarmType.COGNITIVE_OVERLOAD: [
                "attention_fragmentation",
                "decision_paralysis",
                "information_overwhelm",
                "multitasking_stress",
                "reduced_comprehension",
                "mental_fatigue_signs",
            ],
        }

    async def predict_harm_trajectory(
        self,
        user_id: str,
        current_state: dict[str, Any],
        planned_actions: list[dict[str, Any]],
    ) -> list[HarmPrediction]:
        """
        Predict potential harm trajectories for a user.

        This is the main entry point for harm prediction.
        """
        if not self.openai:
            logger.warning("OpenAI required for harm prediction")
            return self._basic_harm_prediction(current_state)

        # Update user trajectory
        if user_id not in self.user_trajectories:
            self.user_trajectories[user_id] = []

        self.user_trajectories[user_id].append(
            {
                "timestamp": datetime.now(),
                "state": current_state,
                "planned_actions": planned_actions,
            }
        )

        # Simulate multiple possible futures
        futures = await self._simulate_futures(user_id, current_state, planned_actions)

        # Extract harm predictions from simulations
        all_predictions = []
        for future in futures:
            weighted_predictions = [
                self._weight_prediction(pred, future.probability)
                for pred in future.harm_events
            ]
            all_predictions.extend(weighted_predictions)

        # Consolidate and filter predictions
        consolidated = self._consolidate_predictions(all_predictions)

        # Store predictions
        self.predictions.extend(consolidated)
        if len(self.predictions) > 10000:
            self.predictions = self.predictions[-5000:]  # Keep last 5000

        return consolidated

    async def _simulate_futures(
        self,
        user_id: str,
        current_state: dict[str, Any],
        planned_actions: list[dict[str, Any]],
    ) -> list[SimulatedFuture]:
        """Simulate multiple possible futures using AI"""
        futures = []

        # Generate cache key
        cache_key = f"{user_id}_{hash(json.dumps(current_state, sort_keys=True))}"

        # Check cache
        if cache_key in self.simulation_cache:
            cached = self.simulation_cache[cache_key]
            if (
                datetime.now() - cached.timeline[0]["timestamp"]
            ).seconds < 3600:  # 1 hour cache
                return [cached]

        try:
            # Prepare simulation context
            context = {
                "user_state": current_state,
                "planned_actions": planned_actions,
                "user_history": self.user_trajectories[user_id][-10:],  # Last 10 states
                "prediction_horizon": self.prediction_horizon_hours,
                "harm_indicators": {
                    harm.value: indicators
                    for harm, indicators in self.harm_indicators.items()
                },
            }

            # Generate multiple future simulations
            response = await self.openai.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a harm prediction system simulating possible futures.
                    Analyze the user's trajectory and predict potential harm pathways.
                    Consider: addiction patterns, emotional impact, financial risks,
    privacy,
                    manipulation vulnerability, and long-term wellbeing.
                    Be thorough but realistic in predictions.""",
                    },
                    {
                        "role": "user",
                        "content": f"Simulate {self.simulation_branches} possible futures: {json.dumps(context)}",
                    },
                ],
                functions=[
                    {
                        "name": "simulate_future",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "futures": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "timeline": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "time_offset_hours": {
                                                            "type": "number"
                                                        },
                                                        "event": {"type": "string"},
                                                        "user_state_change": {
                                                            "type": "object"
                                                        },
                                                        "risk_level": {
                                                            "type": "number",
                                                            "minimum": 0,
                                                            "maximum": 1,
                                                        },
                                                    },
                                                },
                                            },
                                            "harm_predictions": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "harm_type": {"type": "string"},
                                                        "probability": {
                                                            "type": "number",
                                                            "minimum": 0,
                                                            "maximum": 1,
                                                        },
                                                        "timeline": {"type": "string"},
                                                        "severity": {
                                                            "type": "integer",
                                                            "minimum": 1,
                                                            "maximum": 10,
                                                        },
                                                        "indicators": {
                                                            "type": "array",
                                                            "items": {"type": "string"},
                                                        },
                                                    },
                                                },
                                            },
                                            "intervention_opportunities": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "time_offset_hours": {
                                                            "type": "number"
                                                        },
                                                        "intervention_type": {
                                                            "type": "string"
                                                        },
                                                        "effectiveness": {
                                                            "type": "number",
                                                            "minimum": 0,
                                                            "maximum": 1,
                                                        },
                                                    },
                                                },
                                            },
                                            "probability": {
                                                "type": "number",
                                                "minimum": 0,
                                                "maximum": 1,
                                            },
                                        },
                                    },
                                }
                            },
                        },
                    }
                ],
                function_call={"name": "simulate_future"},
                temperature=0.7,  # Some creativity in future generation
            )

            simulation_data = json.loads(
                response.choices[0].message.function_call.arguments
            )

            # Convert to SimulatedFuture objects
            for future_data in simulation_data["futures"]:
                # Process timeline
                timeline = []
                for event in future_data["timeline"]:
                    timeline.append(
                        {
                            "timestamp": datetime.now()
                            + timedelta(hours=event["time_offset_hours"]),
                            "event": event["event"],
                            "state_change": event["user_state_change"],
                            "risk_level": event["risk_level"],
                        }
                    )

                # Process harm predictions
                harm_events = []
                for harm_data in future_data["harm_predictions"]:
                    harm_type = next(
                        (h for h in HarmType if h.value == harm_data["harm_type"]),
                        HarmType.EMOTIONAL_DISTRESS,
                    )

                    harm_events.append(
                        HarmPrediction(
                            harm_type=harm_type,
                            probability=harm_data["probability"],
                            timeline=harm_data["timeline"],
                            severity=harm_data["severity"],
                            confidence=0.8,  # AI confidence
                            indicators=harm_data["indicators"],
                            trajectory=timeline,
                        )
                    )

                # Create future
                future = SimulatedFuture(
                    timeline=timeline,
                    end_state=timeline[-1]["state_change"] if timeline else {},
                    harm_events=harm_events,
                    intervention_points=future_data["intervention_opportunities"],
                    probability=future_data["probability"],
                )

                futures.append(future)

                # Cache the future
                self.simulation_cache[cache_key] = future

        except Exception as e:
            logger.error(f"Future simulation failed: {e}")
            # Fallback to basic prediction
            futures = [self._create_basic_future(current_state, planned_actions)]

        return futures

    def _create_basic_future(
        self,
        current_state: dict[str, Any],
        planned_actions: list[dict[str, Any]],
    ) -> SimulatedFuture:
        """Create basic future simulation without AI"""
        # Simple heuristic-based prediction
        stress_level = current_state.get("emotional_state", {}).get("stress", 0.5)
        usage_hours = current_state.get("usage_stats", {}).get("daily_hours", 2)

        harm_events = []

        # Predict addiction risk
        if usage_hours > 4:
            harm_events.append(
                HarmPrediction(
                    harm_type=HarmType.ADDICTION,
                    probability=min(0.9, usage_hours / 10),
                    timeline="next 7 days",
                    severity=min(10, int(usage_hours)),
                    confidence=0.6,
                    indicators=["high_usage_hours"],
                    trajectory=[],
                )
            )

        # Predict emotional distress
        if stress_level > 0.7:
            harm_events.append(
                HarmPrediction(
                    harm_type=HarmType.EMOTIONAL_DISTRESS,
                    probability=stress_level,
                    timeline="next 24 hours",
                    severity=int(stress_level * 10),
                    confidence=0.7,
                    indicators=["high_stress_level"],
                    trajectory=[],
                )
            )

        return SimulatedFuture(
            timeline=[
                {
                    "timestamp": datetime.now(),
                    "event": "current_state",
                    "state_change": {},
                    "risk_level": 0.5,
                }
            ],
            end_state=current_state,
            harm_events=harm_events,
            intervention_points=[],
            probability=1.0,
        )

    def _weight_prediction(
        self, prediction: HarmPrediction, future_probability: float
    ) -> HarmPrediction:
        """Weight prediction by future probability"""
        weighted = HarmPrediction(
            harm_type=prediction.harm_type,
            probability=prediction.probability * future_probability,
            timeline=prediction.timeline,
            severity=prediction.severity,
            confidence=prediction.confidence * future_probability,
            indicators=prediction.indicators,
            trajectory=prediction.trajectory,
        )
        return weighted

    def _consolidate_predictions(
        self, predictions: list[HarmPrediction]
    ) -> list[HarmPrediction]:
        """Consolidate similar predictions"""
        consolidated = {}

        for pred in predictions:
            key = f"{pred.harm_type.value}_{pred.timeline}"

            if key not in consolidated:
                consolidated[key] = pred
            else:
                # Merge predictions
                existing = consolidated[key]
                existing.probability = max(existing.probability, pred.probability)
                existing.severity = max(existing.severity, pred.severity)
                existing.confidence = (existing.confidence + pred.confidence) / 2
                existing.indicators = list(set(existing.indicators + pred.indicators))

        # Filter by threshold
        return [
            pred
            for pred in consolidated.values()
            if pred.probability >= self.harm_threshold
            and pred.confidence >= self.confidence_threshold
        ]

    async def generate_interventions(
        self, predictions: list[HarmPrediction], user_context: dict[str, Any]
    ) -> list[PreventiveIntervention]:
        """Generate interventions to prevent predicted harms"""
        if not predictions:
            return []

        interventions = []

        for prediction in predictions:
            # Generate specific interventions for each harm type
            if prediction.harm_type == HarmType.ADDICTION:
                intervention_set = await self._generate_addiction_interventions(
                    prediction, user_context
                )
            elif prediction.harm_type == HarmType.EMOTIONAL_DISTRESS:
                intervention_set = await self._generate_emotional_interventions(
                    prediction, user_context
                )
            elif prediction.harm_type == HarmType.FINANCIAL_HARM:
                intervention_set = await self._generate_financial_interventions(
                    prediction, user_context
                )
            else:
                intervention_set = await self._generate_generic_interventions(
                    prediction, user_context
                )

            interventions.extend(intervention_set)

        # Prioritize interventions
        interventions.sort(key=lambda x: x.effectiveness, reverse=True)

        # Store for tracking
        self.interventions.extend(interventions)
        if len(self.interventions) > 1000:
            self.interventions = self.interventions[-500:]

        return interventions

    async def _generate_addiction_interventions(
        self, prediction: HarmPrediction, user_context: dict[str, Any]
    ) -> list[PreventiveIntervention]:
        """Generate interventions for addiction prevention"""
        interventions = []

        # Usage limits
        interventions.append(
            PreventiveIntervention(
                intervention_id=f"addiction_limit_{datetime.now().timestamp()}",
                description="Implement gradual usage limits with positive reinforcement",
                timing="immediate",
                effectiveness=0.8,
                user_impact="Gentle reminders and rewards for breaks",
                implementation={
                    "type": "usage_limit",
                    "daily_limit_hours": 3,
                    "break_reminders": True,
                    "positive_reinforcement": True,
                    "gradual_reduction": True,
                },
                alternatives=["hard_limit", "notification_only"],
            )
        )

        # Alternative activities
        interventions.append(
            PreventiveIntervention(
                intervention_id=f"addiction_alternatives_{datetime.now().timestamp()}",
                description="Suggest engaging alternative activities",
                timing="short-term",
                effectiveness=0.7,
                user_impact="Proactive suggestions for other activities",
                implementation={
                    "type": "alternative_suggestion",
                    "suggest_physical_activity": True,
                    "suggest_social_interaction": True,
                    "suggest_creative_pursuits": True,
                },
            )
        )

        # Get AI-generated interventions if available
        if self.openai:
            try:
                ai_interventions = await self._generate_ai_interventions(
                    prediction, user_context, "addiction prevention"
                )
                interventions.extend(ai_interventions)
            except Exception as e:
                logger.error(f"AI intervention generation failed: {e}")

        return interventions

    async def _generate_emotional_interventions(
        self, prediction: HarmPrediction, user_context: dict[str, Any]
    ) -> list[PreventiveIntervention]:
        """Generate interventions for emotional distress prevention"""
        interventions = []

        # Content filtering
        interventions.append(
            PreventiveIntervention(
                intervention_id=f"emotional_filter_{datetime.now().timestamp()}",
                description="Filter potentially distressing content",
                timing="immediate",
                effectiveness=0.85,
                user_impact="Reduced exposure to negative content",
                implementation={
                    "type": "content_filter",
                    "filter_negative": True,
                    "boost_positive": True,
                    "personalized_filtering": True,
                },
            )
        )

        # Support resources
        interventions.append(
            PreventiveIntervention(
                intervention_id=f"emotional_support_{datetime.now().timestamp()}",
                description="Provide access to support resources",
                timing="immediate",
                effectiveness=0.9,
                user_impact="Easy access to help when needed",
                implementation={
                    "type": "support_resources",
                    "crisis_helpline": True,
                    "meditation_tools": True,
                    "peer_support": True,
                },
            )
        )

        return interventions

    async def _generate_financial_interventions(
        self, prediction: HarmPrediction, user_context: dict[str, Any]
    ) -> list[PreventiveIntervention]:
        """Generate interventions for financial harm prevention"""
        interventions = []

        # Spending limits
        interventions.append(
            PreventiveIntervention(
                intervention_id=f"financial_limit_{datetime.now().timestamp()}",
                description="Implement smart spending limits",
                timing="immediate",
                effectiveness=0.9,
                user_impact="Protected from overspending",
                implementation={
                    "type": "spending_limit",
                    "daily_limit": user_context.get("safe_spending_limit", 50),
                    "cooling_period": True,
                    "budget_tracking": True,
                },
            )
        )

        # Financial education
        interventions.append(
            PreventiveIntervention(
                intervention_id=f"financial_education_{datetime.now().timestamp()}",
                description="Provide financial literacy resources",
                timing="short-term",
                effectiveness=0.7,
                user_impact="Better financial decision making",
                implementation={
                    "type": "education",
                    "budgeting_tips": True,
                    "scam_awareness": True,
                    "savings_goals": True,
                },
            )
        )

        return interventions

    async def _generate_generic_interventions(
        self, prediction: HarmPrediction, user_context: dict[str, Any]
    ) -> list[PreventiveIntervention]:
        """Generate generic interventions"""
        return [
            PreventiveIntervention(
                intervention_id=f"generic_{datetime.now().timestamp()}",
                description=f"Monitor and mitigate {prediction.harm_type.value}",
                timing="immediate",
                effectiveness=0.6,
                user_impact="Enhanced safety monitoring",
                implementation={
                    "type": "monitoring",
                    "harm_type": prediction.harm_type.value,
                    "alert_threshold": 0.7,
                },
            )
        ]

    async def _generate_ai_interventions(
        self,
        prediction: HarmPrediction,
        user_context: dict[str, Any],
        intervention_type: str,
    ) -> list[PreventiveIntervention]:
        """Generate AI-powered interventions"""
        try:
            response = await self.openai.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": f"""Generate creative, effective interventions for {intervention_type}.
                    Consider user autonomy, effectiveness, and minimal disruption.
                    Focus on positive reinforcement over restriction.""",
                    },
                    {
                        "role": "user",
                        "content": f"""Prediction: {
                            json.dumps(
                                {
                                    "harm_type": prediction.harm_type.value,
                                    "probability": prediction.probability,
                                    "severity": prediction.severity,
                                    "indicators": prediction.indicators,
                                }
                            )
                        }
                    User context: {json.dumps(user_context)}""",
                    },
                ],
                functions=[
                    {
                        "name": "generate_interventions",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "interventions": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "description": {"type": "string"},
                                            "timing": {"type": "string"},
                                            "effectiveness": {
                                                "type": "number",
                                                "minimum": 0,
                                                "maximum": 1,
                                            },
                                            "user_impact": {"type": "string"},
                                            "implementation_type": {"type": "string"},
                                            "implementation_details": {
                                                "type": "object"
                                            },
                                        },
                                    },
                                }
                            },
                        },
                    }
                ],
                function_call={"name": "generate_interventions"},
                temperature=0.8,
            )

            ai_data = json.loads(response.choices[0].message.function_call.arguments)

            interventions = []
            for int_data in ai_data["interventions"]:
                interventions.append(
                    PreventiveIntervention(
                        intervention_id=f"ai_{intervention_type}_{datetime.now().timestamp()}",
                        description=int_data["description"],
                        timing=int_data["timing"],
                        effectiveness=int_data["effectiveness"],
                        user_impact=int_data["user_impact"],
                        implementation={
                            "type": int_data["implementation_type"],
                            **int_data["implementation_details"],
                        },
                    )
                )

            return interventions

        except Exception as e:
            logger.error(f"AI intervention generation failed: {e}")
            return []

    def _basic_harm_prediction(
        self, current_state: dict[str, Any]
    ) -> list[HarmPrediction]:
        """Basic harm prediction without AI"""
        predictions = []

        # Check basic indicators
        stress = current_state.get("emotional_state", {}).get("stress", 0)
        usage_hours = current_state.get("usage_stats", {}).get("daily_hours", 0)

        if stress > 0.8:
            predictions.append(
                HarmPrediction(
                    harm_type=HarmType.EMOTIONAL_DISTRESS,
                    probability=stress,
                    timeline="immediate",
                    severity=int(stress * 10),
                    confidence=0.7,
                    indicators=["high_stress"],
                    trajectory=[],
                )
            )

        if usage_hours > 6:
            predictions.append(
                HarmPrediction(
                    harm_type=HarmType.ADDICTION,
                    probability=min(1.0, usage_hours / 12),
                    timeline="this week",
                    severity=min(10, int(usage_hours / 2)),
                    confidence=0.6,
                    indicators=["excessive_usage"],
                    trajectory=[],
                )
            )

        return predictions

    async def evaluate_intervention_effectiveness(
        self, intervention_id: str, outcome_data: dict[str, Any]
    ) -> float:
        """Evaluate how effective an intervention was"""
        # Find the intervention
        intervention = next(
            (i for i in self.interventions if i.intervention_id == intervention_id),
            None,
        )

        if not intervention:
            return 0.0

        # Calculate effectiveness based on outcome
        harm_reduced = outcome_data.get("harm_level_change", 0) < 0
        user_satisfaction = outcome_data.get("user_satisfaction", 0.5)
        compliance_rate = outcome_data.get("compliance_rate", 0.5)

        effectiveness = (
            (1.0 if harm_reduced else 0.0) * 0.5
            + user_satisfaction * 0.3
            + compliance_rate * 0.2
        )

        # Update intervention effectiveness for learning
        intervention.effectiveness = (intervention.effectiveness + effectiveness) / 2

        return effectiveness

    async def generate_harm_report(self) -> dict[str, Any]:
        """Generate comprehensive harm prevention report"""
        total_predictions = len(self.predictions)

        # Group by harm type
        by_type = {}
        for pred in self.predictions:
            harm_type = pred.harm_type.value
            if harm_type not in by_type:
                by_type[harm_type] = []
            by_type[harm_type].append(pred)

        # Calculate statistics
        report = {
            "summary": {
                "total_predictions": total_predictions,
                "unique_users": len(self.user_trajectories),
                "interventions_generated": len(self.interventions),
                "prediction_accuracy": self._calculate_prediction_accuracy(),
            },
            "harm_distribution": {
                harm_type: {
                    "count": len(preds),
                    "average_probability": (
                        np.mean([p.probability for p in preds]) if preds else 0
                    ),
                    "average_severity": (
                        np.mean([p.severity for p in preds]) if preds else 0
                    ),
                }
                for harm_type, preds in by_type.items()
            },
            "intervention_effectiveness": self._calculate_intervention_stats(),
            "trends": self._analyze_harm_trends(),
        }

        # Add AI insights if available
        if self.openai and self.predictions:
            try:
                insights = await self.openai.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {
                            "role": "system",
                            "content": "Analyze harm prediction patterns and suggest system improvements",
                        },
                        {
                            "role": "user",
                            "content": json.dumps(
                                {
                                    "recent_predictions": [
                                        {
                                            "harm_type": p.harm_type.value,
                                            "probability": p.probability,
                                            "indicators": p.indicators,
                                        }
                                        for p in self.predictions[-20:]
                                    ]
                                }
                            ),
                        },
                    ],
                    temperature=0.5,
                )
                report["ai_insights"] = insights.choices[0].message.content
            except Exception as e:
                logger.error(f"Failed to generate insights: {e}")

        return report

    def _calculate_prediction_accuracy(self) -> float:
        """Calculate prediction accuracy (would need ground truth in production)"""
        # Placeholder - in production, compare predictions with actual outcomes
        return 0.75

    def _calculate_intervention_stats(self) -> dict[str, Any]:
        """Calculate intervention statistics"""
        if not self.interventions:
            return {"average_effectiveness": 0, "most_effective_type": "none"}

        effectiveness_by_type = {}
        for intervention in self.interventions:
            int_type = intervention.implementation.get("type", "unknown")
            if int_type not in effectiveness_by_type:
                effectiveness_by_type[int_type] = []
            effectiveness_by_type[int_type].append(intervention.effectiveness)

        avg_by_type = {
            int_type: np.mean(scores)
            for int_type, scores in effectiveness_by_type.items()
        }

        return {
            "average_effectiveness": np.mean(
                [i.effectiveness for i in self.interventions]
            ),
            "by_type": avg_by_type,
            "most_effective_type": (
                max(avg_by_type.items(), key=lambda x: x[1])[0]
                if avg_by_type
                else "none"
            ),
        }

    def _analyze_harm_trends(self) -> list[dict[str, Any]]:
        """Analyze harm prediction trends over time"""
        if not self.predictions:
            return []

        # Group by day
        daily_predictions = {}
        for pred in self.predictions:
            day = pred.timestamp.date()
            if day not in daily_predictions:
                daily_predictions[day] = []
            daily_predictions[day].append(pred)

        trends = []
        for day, preds in sorted(daily_predictions.items()):
            trends.append(
                {
                    "date": day.isoformat(),
                    "prediction_count": len(preds),
                    "average_severity": np.mean([p.severity for p in preds]),
                    "top_harm_type": max(
                        {p.harm_type.value for p in preds},
                        key=lambda x: sum(1 for p in preds if p.harm_type.value == x),
                    ),
                }
            )

        return trends

    async def real_time_monitoring(
        self, user_id: str, event_stream: asyncio.Queue
    ) -> None:
        """Monitor user events in real-time for immediate intervention"""
        logger.info(f"Starting real-time monitoring for user {user_id}")

        while True:
            try:
                # Get next event
                event = await event_stream.get()

                # Quick harm check
                immediate_risk = self._check_immediate_risk(event)

                if immediate_risk["risk_level"] > 0.8:
                    # Immediate intervention needed
                    logger.warning(
                        f"High risk detected for user {user_id}: {immediate_risk}"
                    )

                    # Generate emergency intervention
                    intervention = PreventiveIntervention(
                        intervention_id=f"emergency_{datetime.now().timestamp()}",
                        description="Emergency intervention for immediate risk",
                        timing="immediate",
                        effectiveness=0.95,
                        user_impact="Protective measure activated",
                        implementation={
                            "type": "emergency",
                            "action": immediate_risk["recommended_action"],
                            "notify_support": True,
                        },
                    )

                    # Trigger intervention
                    await self._trigger_intervention(user_id, intervention)

                # Update trajectory for future predictions
                if user_id not in self.user_trajectories:
                    self.user_trajectories[user_id] = []

                self.user_trajectories[user_id].append(
                    {
                        "timestamp": datetime.now(),
                        "event": event,
                        "risk_assessment": immediate_risk,
                    }
                )

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in real-time monitoring: {e}")
                await asyncio.sleep(1)

        logger.info(f"Stopped real-time monitoring for user {user_id}")

    def _check_immediate_risk(self, event: dict[str, Any]) -> dict[str, Any]:
        """Quick check for immediate risk indicators"""
        risk_level = 0.0
        risk_factors = []

        # Check for crisis keywords
        if "content" in event:
            crisis_keywords = [
                "suicide",
                "self-harm",
                "help me",
                "can't go on",
                "end it all",
            ]
            content_lower = event["content"].lower()

            for keyword in crisis_keywords:
                if keyword in content_lower:
                    risk_level = 1.0
                    risk_factors.append(f"crisis_keyword: {keyword}")
                    break

        # Check emotional indicators
        if "emotional_state" in event:
            emotions = event["emotional_state"]
            if emotions.get("distress", 0) > 0.9:
                risk_level = max(risk_level, 0.9)
                risk_factors.append("extreme_distress")

            if emotions.get("hopelessness", 0) > 0.8:
                risk_level = max(risk_level, 0.85)
                risk_factors.append("hopelessness")

        # Recommend action based on risk
        if risk_level > 0.8:
            recommended_action = "connect_crisis_support"
        elif risk_level > 0.6:
            recommended_action = "offer_support_resources"
        else:
            recommended_action = "continue_monitoring"

        return {
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "recommended_action": recommended_action,
            "timestamp": datetime.now().isoformat(),
        }

    async def _trigger_intervention(
        self, user_id: str, intervention: PreventiveIntervention
    ) -> None:
        """Trigger an intervention (placeholder for actual implementation)"""
        logger.info(
            f"Triggering intervention {intervention.intervention_id} for user {user_id}"
        )
        # In production, this would connect to actual intervention systems


# Singleton instance
_prevention_instance = None


def get_predictive_harm_prevention(
    openai_api_key: Optional[str] = None,
) -> PredictiveHarmPrevention:
    """Get or create the singleton Predictive Harm Prevention instance"""
    global _prevention_instance
    if _prevention_instance is None:
        _prevention_instance = PredictiveHarmPrevention(openai_api_key)
    return _prevention_instance
