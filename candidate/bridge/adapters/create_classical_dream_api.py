#!/usr/bin/env python3
"""
LUKHAS Classical Dream API - Non-Quantum Alternative
Provides dream-based exploration without quantum interference
"""

import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="LUKHAS Classical Dream API",
    description="Safe, deterministic dream exploration without quantum effects",
    version="1.0.0",
)


class ClassicalDreamScenario(BaseModel):
    """Input for classical dream exploration"""

    scenario: str = Field(..., description="The scenario to explore")
    branch_count: int = Field(
        5, ge=1, le=10, description="Number of branches to explore"
    )
    emotional_context: dict[str, float] = Field(
        default_factory=dict, description="Emotional state values 0-1"
    )
    deterministic_seed: Optional[int] = Field(
        None, description="Seed for reproducible results"
    )
    safety_level: float = Field(
        0.8, ge=0, le=1, description="Safety threshold for exploration"
    )


class ClassicalOutcome(BaseModel):
    """A single deterministic outcome branch"""

    branch_id: str
    outcome: str
    likelihood: float = Field(..., ge=0, le=1, description="Classical probability")
    path: list[str]
    emotional_evolution: dict[str, list[float]]
    decision_points: list[dict[str, Any]]
    safety_score: float = Field(..., ge=0, le=1)


class ClassicalDreamResponse(BaseModel):
    """Classical dream exploration response"""

    session_id: str
    timestamp: str
    original_scenario: str
    branches: list[ClassicalOutcome]
    convergence_metric: float = Field(..., ge=0, le=1)
    exploration_depth: int
    insights: list[str]
    safety_validated: bool


@dataclass
class DecisionNode:
    """Represents a decision point in the exploration tree"""

    id: str
    description: str
    options: list[str]
    probabilities: list[float]
    safety_scores: list[float]


class ClassicalDreamEngine:
    """Non-quantum dream engine using classical algorithms"""

    def __init__(self):
        self.decision_trees = {}
        self.safety_threshold = 0.7

    async def explore_scenario(
        self, scenario: ClassicalDreamScenario
    ) -> ClassicalDreamResponse:
        """Explore scenario using classical branching algorithms"""

        # Initialize deterministic random if seed provided
        if scenario.deterministic_seed:
            np.random.seed(scenario.deterministic_seed)

        session_id = self._generate_session_id(scenario.scenario)

        # Build decision tree
        root_node = self._create_decision_tree(scenario)

        # Explore branches
        branches = []
        for i in range(scenario.branch_count):
            branch = await self._explore_branch(
                root_node,
                scenario.emotional_context,
                scenario.safety_level,
                branch_index=i,
            )
            branches.append(branch)

        # Calculate metrics
        convergence = self._calculate_convergence(branches)
        insights = self._extract_insights(branches, scenario)

        # Validate safety
        safety_validated = all(
            b.safety_score >= scenario.safety_level for b in branches
        )

        return ClassicalDreamResponse(
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            original_scenario=scenario.scenario,
            branches=branches,
            convergence_metric=convergence,
            exploration_depth=(max(len(b.path) for b in branches) if branches else 0),
            insights=insights,
            safety_validated=safety_validated,
        )

    def _generate_session_id(self, scenario: str) -> str:
        """Generate deterministic session ID"""
        hash_input = f"{scenario}_{datetime.now().strftime('%Y%m%d_%H%M')}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:12]

    def _create_decision_tree(self, scenario: ClassicalDreamScenario) -> DecisionNode:
        """Create a decision tree based on scenario analysis"""

        # Analyze scenario to identify key decision points
        # In production, this would use NLP to extract decision factors

        # For demo, create a simple decision tree
        if "customer" in scenario.scenario.lower():
            return self._create_customer_service_tree()
        elif "technical" in scenario.scenario.lower():
            return self._create_technical_problem_tree()
        else:
            return self._create_generic_decision_tree()

    def _create_customer_service_tree(self) -> DecisionNode:
        """Create decision tree for customer service scenarios"""
        return DecisionNode(
            id="root",
            description="Customer interaction approach",
            options=[
                "Empathetic listening",
                "Quick solution focus",
                "Escalation to specialist",
                "Compensation offer",
            ],
            probabilities=[0.4, 0.3, 0.2, 0.1],
            safety_scores=[0.95, 0.85, 0.9, 0.8],
        )

    def _create_technical_problem_tree(self) -> DecisionNode:
        """Create decision tree for technical scenarios"""
        return DecisionNode(
            id="root",
            description="Technical problem approach",
            options=[
                "Systematic debugging",
                "Quick workaround",
                "Complete redesign",
                "External consultation",
            ],
            probabilities=[0.5, 0.2, 0.2, 0.1],
            safety_scores=[0.9, 0.7, 0.85, 0.95],
        )

    def _create_generic_decision_tree(self) -> DecisionNode:
        """Create generic decision tree"""
        return DecisionNode(
            id="root",
            description="General approach",
            options=[
                "Careful analysis",
                "Quick action",
                "Collaborative approach",
                "Wait and observe",
            ],
            probabilities=[0.4, 0.2, 0.3, 0.1],
            safety_scores=[0.9, 0.7, 0.85, 0.95],
        )

    async def _explore_branch(
        self,
        root: DecisionNode,
        emotions: dict[str, float],
        safety_level: float,
        branch_index: int,
    ) -> ClassicalOutcome:
        """Explore a single branch of possibilities"""

        # Select path based on probabilities and branch index
        path = []
        current_node = root
        emotional_evolution = {emotion: [value] for emotion, value in emotions.items()}
        decision_points = []
        total_safety = 1.0

        # Traverse decision tree
        for depth in range(3):  # Max depth of 3
            # Select option based on weighted probability
            option_index = self._select_option(
                current_node.probabilities, branch_index, depth
            )

            selected_option = current_node.options[option_index]
            path.append(selected_option)

            # Record decision point
            decision_points.append(
                {
                    "depth": depth,
                    "chosen": selected_option,
                    "alternatives": [
                        opt
                        for i, opt in enumerate(current_node.options)
                        if i != option_index
                    ],
                    "confidence": current_node.probabilities[option_index],
                }
            )

            # Update safety score
            total_safety *= current_node.safety_scores[option_index]

            # Evolve emotions based on decision
            emotional_evolution = self._evolve_emotions(
                emotional_evolution,
                selected_option,
                current_node.safety_scores[option_index],
            )

            # Generate next node (in real system, would continue tree)
            if depth < 2:
                current_node = self._generate_next_node(selected_option)

        # Calculate final likelihood
        likelihood = self._calculate_path_likelihood(path, emotional_evolution)

        return ClassicalOutcome(
            branch_id=f"branch_{branch_index}",
            outcome=f"Path leads to: {' → '.join(path)}",
            likelihood=likelihood,
            path=path,
            emotional_evolution=emotional_evolution,
            decision_points=decision_points,
            safety_score=total_safety,
        )

    def _select_option(
        self, probabilities: list[float], branch_index: int, depth: int
    ) -> int:
        """Deterministically select option based on probabilities"""
        # Use branch index and depth to create variation
        # This ensures different branches explore different paths
        offset = (branch_index + depth) % len(probabilities)

        # Rotate probabilities for this branch
        rotated_probs = probabilities[offset:] + probabilities[:offset]

        # Select highest probability from rotated list
        max_index = rotated_probs.index(max(rotated_probs))

        # Map back to original index
        return (max_index + offset) % len(probabilities)

    def _evolve_emotions(
        self,
        current_emotions: dict[str, list[float]],
        decision: str,
        safety_score: float,
    ) -> dict[str, list[float]]:
        """Evolve emotions based on decisions"""

        # Simple emotion evolution rules
        evolution_rules = {
            "empathetic": {"joy": 0.1, "trust": 0.15, "fear": -0.05},
            "quick": {"stress": 0.1, "anticipation": 0.1, "joy": -0.05},
            "collaborative": {"trust": 0.2, "joy": 0.1, "stress": -0.1},
            "careful": {"fear": -0.1, "trust": 0.1, "stress": 0.05},
            "escalation": {"stress": 0.15, "fear": 0.1, "trust": -0.05},
        }

        # Find matching rule
        rule_key = None
        for key in evolution_rules:
            if key in decision.lower():
                rule_key = key
                break

        if not rule_key:
            rule_key = "careful"  # Default

        # Apply evolution
        for emotion, change in evolution_rules[rule_key].items():
            if emotion in current_emotions:
                last_value = current_emotions[emotion][-1]
                new_value = max(0, min(1, last_value + change * safety_score))
                current_emotions[emotion].append(new_value)
            else:
                # Add default evolution for untracked emotions
                for e in current_emotions:
                    current_emotions[e].append(current_emotions[e][-1])

        return current_emotions

    def _generate_next_node(self, previous_decision: str) -> DecisionNode:
        """Generate next decision node based on previous choice"""

        # Simplified next node generation
        if "empathetic" in previous_decision.lower():
            return DecisionNode(
                id=f"node_{previous_decision}",
                description="Follow-up after empathy",
                options=[
                    "Offer specific help",
                    "Continue listening",
                    "Suggest resources",
                ],
                probabilities=[0.5, 0.3, 0.2],
                safety_scores=[0.9, 0.95, 0.85],
            )
        else:
            return DecisionNode(
                id=f"node_{previous_decision}",
                description="Next steps",
                options=[
                    "Monitor results",
                    "Adjust approach",
                    "Seek feedback",
                ],
                probabilities=[0.4, 0.4, 0.2],
                safety_scores=[0.95, 0.85, 0.9],
            )

    def _calculate_path_likelihood(
        self, path: list[str], emotions: dict[str, list[float]]
    ) -> float:
        """Calculate likelihood of path success"""

        # Base likelihood on path coherence
        base_likelihood = 0.5

        # Adjust based on emotional trajectory
        for emotion, values in emotions.items():
            if len(values) > 1:
                # Positive emotions increasing = good
                if emotion in ["joy", "trust", "anticipation"]:
                    if values[-1] > values[0]:
                        base_likelihood += 0.1
                # Negative emotions decreasing = good
                elif emotion in ["fear", "stress", "anger"]:
                    if values[-1] < values[0]:
                        base_likelihood += 0.1

        # Path length factor (shorter paths slightly preferred)
        length_factor = 1.0 - (len(path) - 3) * 0.05

        return min(0.95, max(0.05, base_likelihood * length_factor))

    def _calculate_convergence(self, branches: list[ClassicalOutcome]) -> float:
        """Calculate how much branches converge to similar outcomes"""

        if len(branches) < 2:
            return 0.0

        # Compare path similarities
        total_similarity = 0.0
        comparisons = 0

        for i in range(len(branches)):
            for j in range(i + 1, len(branches)):
                # Compare paths
                path1 = set(branches[i].path)
                path2 = set(branches[j].path)

                intersection = len(path1.intersection(path2))
                union = len(path1.union(path2))

                if union > 0:
                    similarity = intersection / union
                    total_similarity += similarity
                    comparisons += 1

        return total_similarity / comparisons if comparisons > 0 else 0.0

    def _extract_insights(
        self,
        branches: list[ClassicalOutcome],
        scenario: ClassicalDreamScenario,
    ) -> list[str]:
        """Extract insights from exploration"""

        insights = []

        # Find most likely branch
        if branches:
            best_branch = max(branches, key=lambda b: b.likelihood)
            insights.append(
                f"Most promising approach: {best_branch.path[0]} "
                f"(likelihood: {best_branch.likelihood:.2f})"
            )

        # Check safety
        safe_branches = [b for b in branches if b.safety_score >= scenario.safety_level]
        insights.append(
            f"{len(safe_branches)}/{len(branches)} branches meet safety threshold"
        )

        # Emotional patterns
        emotion_trends = {}
        for branch in branches:
            for emotion, values in branch.emotional_evolution.items():
                if len(values) > 1:
                    trend = values[-1] - values[0]
                    if emotion not in emotion_trends:
                        emotion_trends[emotion] = []
                    emotion_trends[emotion].append(trend)

        for emotion, trends in emotion_trends.items():
            avg_trend = np.mean(trends)
            if abs(avg_trend) > 0.1:
                direction = "increases" if avg_trend > 0 else "decreases"
                insights.append(f"{emotion.capitalize()} typically {direction}")

        return insights


# Initialize engine
dream_engine = ClassicalDreamEngine()


@app.post("/api/v1/classical-dream", response_model=ClassicalDreamResponse)
async def explore_classical_dream(scenario: ClassicalDreamScenario):
    """
    Explore scenarios using classical, deterministic algorithms.

    This provides a safe alternative to quantum dream exploration:
    - No quantum interference with classical systems
    - Deterministic results with optional seeding
    - Safety validation at every step
    - Clear decision trees instead of quantum superposition
    """
    try:
        response = await dream_engine.explore_scenario(scenario)
        return response

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Classical exploration failed: {str(e)}"
        )


@app.get("/")
async def root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to LUKHAS Classical Dream API",
        "description": "Safe, deterministic scenario exploration without quantum effects",
        "features": [
            "Classical probability models",
            "Deterministic branching",
            "Safety validation",
            "Reproducible results",
            "No quantum interference",
        ],
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "engine": "classical",
        "qi_free": True,
        "deterministic": True,
    }


@app.post("/api/v1/compare-quantum")
async def compare_with_quantum():
    """Compare classical vs quantum approaches"""
    return {
        "classical_advantages": [
            "No interference with classical systems",
            "Deterministic and reproducible",
            "Lower computational requirements",
            "Compatible with all hardware",
            "Easier to debug and verify",
        ],
        "qi_advantages": [
            "True superposition exploration",
            "Quantum entanglement insights",
            "Potentially deeper emergence",
            "Novel solution discovery",
        ],
        "recommendation": "Use classical for production, quantum for research",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8004)
