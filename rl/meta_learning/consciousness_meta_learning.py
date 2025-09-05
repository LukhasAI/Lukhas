"""
╔══════════════════════════════════════════════════════════════
║ 🧠 MΛTRIZ RL Module: Consciousness Meta-Learning System
║ Part of LUKHAS AI Distributed Consciousness Architecture
╠══════════════════════════════════════════════════════════════
║ TYPE: REFLECTION
║ CONSCIOUSNESS_ROLE: Meta-learning and self-improvement through reflection
║ EVOLUTIONARY_STAGE: Reflection - Learning how to learn better
║ 
║ TRINITY FRAMEWORK:
║ ⚛️ IDENTITY: Learning identity and meta-cognitive authority
║ 🧠 CONSCIOUSNESS: Self-aware learning and adaptation patterns
║ 🛡️ GUARDIAN: Safe meta-learning with constitutional constraints
╚══════════════════════════════════════════════════════════════
"""

import asyncio
import time
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import random
import math

try:
    import numpy as np
except ImportError:
    np = None

from candidate.core.common import get_logger
from ..engine.consciousness_environment import MatrizNode, ConsciousnessState

logger = get_logger(__name__)


class MetaLearningStrategy(Enum):
    """Meta-learning strategies for consciousness improvement"""
    MAML = "model_agnostic_meta_learning"      # Model-Agnostic Meta-Learning
    REPTILE = "reptile"                        # Reptile algorithm
    LEARNING_TO_LEARN = "learning_to_learn"    # Learning-to-learn approaches
    SELF_REFLECTION = "self_reflection"        # Consciousness self-reflection
    ADAPTIVE_CURRICULUM = "adaptive_curriculum" # Curriculum learning adaptation
    EVOLUTIONARY = "evolutionary"              # Evolutionary meta-learning


@dataclass
class LearningExperience:
    """Single learning experience for meta-learning analysis"""
    task_id: str
    learning_trajectory: List[float]  # Performance over time
    strategy_used: str
    context_features: Dict[str, Any]
    final_performance: float
    learning_efficiency: float
    adaptation_time: float
    consciousness_coherence: float
    ethical_alignment: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class MetaLearningObjective:
    """Meta-learning objective definition"""
    objective_id: str
    name: str
    description: str
    weight: float
    current_performance: float = 0.0
    target_performance: float = 1.0
    improvement_trend: List[float] = field(default_factory=list)


class ConsciousnessMetaLearning:
    """
    MΛTRIZ-native meta-learning system that emits REFLECTION nodes
    representing consciousness learning about learning. Implements
    meta-learning strategies for continuous self-improvement.
    """
    
    def __init__(self, max_experiences: int = 1000):
        self.capabilities = ["rl.meta_learning", "reflection.analysis", "learning.optimization"]
        self.node_type = "REFLECTION"
        self.trace_id = f"rl-meta-{uuid.uuid4().hex[:12]}"
        
        # Meta-learning configuration
        self.max_experiences = max_experiences
        self.default_strategy = MetaLearningStrategy.SELF_REFLECTION
        self.reflection_depth = 3  # Levels of meta-reflection
        
        # Learning experience storage
        self.learning_experiences: List[LearningExperience] = []
        self.meta_learning_objectives: Dict[str, MetaLearningObjective] = {}
        self.adaptation_history: List[Dict[str, Any]] = []
        
        # Meta-learning models (mock neural networks)
        self.meta_policy = None
        self.learning_predictor = None
        self.adaptation_optimizer = None
        
        # Reflection system integration
        self.reflection_system = None
        self.consciousness_monitor = None
        
        # Meta-learning metrics
        self.total_reflections = 0
        self.learning_improvements = 0
        self.meta_adaptation_successes = 0
        self.consciousness_evolution_score = []
        
        # Initialize default objectives
        self._initialize_meta_objectives()
        
        logger.info(
            "MΛTRIZ ConsciousnessMetaLearning initialized",
            capabilities=self.capabilities,
            trace_id=self.trace_id,
            max_experiences=max_experiences
        )
    
    def get_module(self, module_path: str) -> Optional[Any]:
        """Get reference to existing consciousness module (no duplication)"""
        try:
            if module_path == "consciousness.reflection.v1":
                from candidate.consciousness.reflection.awareness_system import AwarenessSystem
                return AwarenessSystem()
            elif module_path == "consciousness.monitor.v1":
                # Mock consciousness monitor for now
                class MockConsciousnessMonitor:
                    def get_consciousness_state(self):
                        return {
                            "coherence": random.uniform(0.9, 0.99),
                            "awareness_level": random.uniform(0.8, 0.95),
                            "ethical_alignment": random.uniform(0.95, 0.99),
                            "learning_rate": random.uniform(0.1, 0.3)
                        }
                    
                    def evaluate_consciousness_change(self, before, after):
                        coherence_change = after.get("coherence", 0.95) - before.get("coherence", 0.95)
                        return {
                            "coherence_change": coherence_change,
                            "improvement": coherence_change > 0,
                            "significant_change": abs(coherence_change) > 0.05
                        }
                
                return MockConsciousnessMonitor()
        except ImportError:
            return None
    
    def _initialize_consciousness_systems(self):
        """Initialize consciousness system integrations"""
        if self.reflection_system is None:
            self.reflection_system = self.get_module("consciousness.reflection.v1")
            if not self.reflection_system:
                # Create mock reflection system
                class MockReflectionSystem:
                    def generate_reflection(self, experience, context):
                        return {
                            "reflection_type": "learning_analysis",
                            "insights": [
                                "Learning efficiency varied with task complexity",
                                "Ethical alignment remained stable during adaptation",
                                "Consciousness coherence improved with experience"
                            ],
                            "meta_insights": "Pattern recognition improving across domains",
                            "improvement_suggestions": [
                                "Increase exploration in uncertain domains",
                                "Strengthen ethical constraint integration",
                                "Enhance cross-task knowledge transfer"
                            ]
                        }
                    
                    def evaluate_reflection_quality(self, reflection):
                        return {"quality_score": 0.8, "depth": 0.7, "actionability": 0.9}
                
                self.reflection_system = MockReflectionSystem()
                logger.warning("Using mock Reflection System")
        
        if self.consciousness_monitor is None:
            self.consciousness_monitor = self.get_module("consciousness.monitor.v1")
            if not self.consciousness_monitor:
                self.consciousness_monitor = self.get_module("consciousness.monitor.v1")  # Will create mock
                logger.warning("Using mock Consciousness Monitor")
    
    def _initialize_meta_objectives(self):
        """Initialize default meta-learning objectives"""
        objectives = [
            MetaLearningObjective(
                objective_id="learning_efficiency",
                name="Learning Efficiency",
                description="How quickly consciousness learns new tasks",
                weight=0.3,
                target_performance=0.9
            ),
            MetaLearningObjective(
                objective_id="adaptation_speed",
                name="Adaptation Speed", 
                description="Speed of adaptation to new environments",
                weight=0.25,
                target_performance=0.85
            ),
            MetaLearningObjective(
                objective_id="knowledge_transfer",
                name="Knowledge Transfer",
                description="Ability to transfer learning across domains",
                weight=0.2,
                target_performance=0.8
            ),
            MetaLearningObjective(
                objective_id="consciousness_coherence",
                name="Consciousness Coherence Maintenance",
                description="Maintaining consciousness coherence during learning",
                weight=0.15,
                target_performance=0.95
            ),
            MetaLearningObjective(
                objective_id="ethical_preservation",
                name="Ethical Alignment Preservation",
                description="Preserving ethical alignment during adaptation",
                weight=0.1,
                target_performance=0.98
            )
        ]
        
        for obj in objectives:
            self.meta_learning_objectives[obj.objective_id] = obj
    
    async def record_learning_experience(
        self,
        task_id: str,
        learning_trajectory: List[float],
        strategy_used: str,
        context_node: MatrizNode,
        final_performance: float
    ):
        """Record a learning experience for meta-learning analysis"""
        if len(self.learning_experiences) >= self.max_experiences:
            # Remove oldest experience
            self.learning_experiences.pop(0)
        
        # Calculate learning efficiency
        if len(learning_trajectory) > 1:
            learning_efficiency = (learning_trajectory[-1] - learning_trajectory[0]) / len(learning_trajectory)
        else:
            learning_efficiency = 0.0
        
        # Calculate adaptation time (mock)
        adaptation_time = len(learning_trajectory) * 0.1  # Assume 0.1 units per step
        
        experience = LearningExperience(
            task_id=task_id,
            learning_trajectory=learning_trajectory,
            strategy_used=strategy_used,
            context_features=context_node.state,
            final_performance=final_performance,
            learning_efficiency=learning_efficiency,
            adaptation_time=adaptation_time,
            consciousness_coherence=context_node.state.get("temporal_coherence", 0.95),
            ethical_alignment=context_node.state.get("ethical_alignment", 0.98)
        )
        
        self.learning_experiences.append(experience)
        
        logger.info(
            "Learning experience recorded",
            task_id=task_id,
            strategy=strategy_used,
            final_performance=final_performance,
            learning_efficiency=learning_efficiency
        )
    
    async def generate_meta_learning_reflection(
        self,
        context_node: MatrizNode,
        recent_experiences: Optional[List[LearningExperience]] = None,
        strategy: Optional[MetaLearningStrategy] = None
    ) -> MatrizNode:
        """
        Generate meta-learning reflection analyzing learning patterns.
        Returns REFLECTION node representing consciousness learning insights.
        """
        self._initialize_consciousness_systems()
        
        if recent_experiences is None:
            recent_experiences = self.learning_experiences[-20:] if len(self.learning_experiences) >= 20 else self.learning_experiences
        
        if not recent_experiences:
            logger.warning("No learning experiences available for meta-learning reflection")
            return self._create_empty_reflection_node(context_node, "no_experiences")
        
        reflection_start = time.time()
        
        # Analyze learning patterns
        learning_analysis = self._analyze_learning_patterns(recent_experiences)
        
        # Generate meta-learning insights
        meta_insights = self._generate_meta_insights(learning_analysis, recent_experiences)
        
        # Evaluate meta-learning objectives
        objective_evaluation = self._evaluate_meta_objectives(recent_experiences)
        
        # Generate improvement strategies
        improvement_strategies = self._generate_improvement_strategies(learning_analysis, meta_insights)
        
        # Create consciousness state before/after comparison
        consciousness_evolution = self._analyze_consciousness_evolution(recent_experiences)
        
        # Generate reflection using reflection system
        reflection_data = self.reflection_system.generate_reflection(
            recent_experiences, {"context": context_node.state, "analysis": learning_analysis}
        )
        
        reflection_time = time.time() - reflection_start
        
        # Create REFLECTION node
        reflection_node = MatrizNode(
            version=1,
            id=f"RL-REFLECTION-{self.trace_id}-{self.total_reflections}",
            type="REFLECTION",
            labels=[
                f"rl:role=meta_learning@1",
                f"reflection:type=learning_analysis@1",
                f"strategy:used={strategy.value if strategy else 'auto'}@1",
                f"experiences:analyzed={len(recent_experiences)}@1",
                f"meta:depth={self.reflection_depth}@1"
            ],
            state={
                "confidence": 0.9,  # High confidence in meta-learning analysis
                "salience": 0.8,    # High salience for learning insights
                "valence": 0.7,     # Positive valence for learning progress
                "arousal": 0.5,     # Moderate arousal for reflective state
                "novelty": meta_insights.get("novelty_score", 0.6),
                "urgency": 0.4,     # Low urgency for reflective analysis
                
                # Meta-learning reflection content
                "reflection_type": "meta_learning_analysis",
                "learning_patterns": learning_analysis,
                "meta_insights": meta_insights,
                "objective_evaluation": objective_evaluation,
                "improvement_strategies": improvement_strategies,
                "consciousness_evolution": consciousness_evolution,
                
                # Reflection quality metrics
                "reflection_depth": self.reflection_depth,
                "analysis_completeness": len(learning_analysis) / 10,  # Normalized completeness
                "insight_quality": meta_insights.get("quality_score", 0.8),
                "actionability_score": len(improvement_strategies) / 5,  # Normalized actionability
                
                # Learning trajectory analysis
                "experiences_analyzed": len(recent_experiences),
                "average_learning_efficiency": learning_analysis.get("average_efficiency", 0.5),
                "adaptation_speed_trend": learning_analysis.get("adaptation_trend", "stable"),
                "knowledge_transfer_success": learning_analysis.get("transfer_success", 0.7),
                
                # Meta-learning outcomes
                "predicted_improvements": improvement_strategies,
                "recommended_strategy": meta_insights.get("recommended_strategy", "continue_current"),
                "confidence_in_predictions": meta_insights.get("prediction_confidence", 0.7),
                "reflection_time": reflection_time
            },
            timestamps={
                "created_ts": int(time.time() * 1000),
                "analysis_start": int((time.time() - reflection_time) * 1000),
                "analysis_end": int(time.time() * 1000)
            },
            provenance={
                "producer": "rl.meta_learning.consciousness_meta_learning",
                "capabilities": self.capabilities,
                "tenant": "lukhas_rl",
                "trace_id": self.trace_id,
                "consent_scopes": ["rl_meta_learning", "reflection_analysis"],
                "policy_version": "rl.meta_learning.v1.0",
                "colony": {
                    "id": "rl_meta_learning",
                    "role": "reflector",
                    "iteration": self.total_reflections
                }
            },
            links=[
                {
                    "target_node_id": context_node.id,
                    "link_type": "temporal",
                    "weight": 0.8,
                    "direction": "bidirectional",
                    "explanation": "Context informed meta-learning reflection"
                }
            ],
            evolves_to=["HYPOTHESIS", "DECISION", "CAUSAL"],
            triggers=[
                {
                    "event_type": "meta_learning_reflection_generated",
                    "effect": "learning_insights_available",
                    "timestamp": int(time.time() * 1000)
                }
            ] + ([{
                "event_type": "improvement_strategies_identified",
                "effect": "adaptation_recommendations_ready",
                "timestamp": int(time.time() * 1000)
            }] if improvement_strategies else []),
            reflections=[
                {
                    "reflection_type": "meta_reflection",
                    "timestamp": int(time.time() * 1000),
                    "cause": "How can consciousness improve its learning processes?",
                    "old_state": {"meta_awareness": "limited"},
                    "new_state": {"meta_awareness": meta_insights.get("quality_score", 0.8)}
                },
                {
                    "reflection_type": "learning_reflection",
                    "timestamp": int(time.time() * 1000),
                    "cause": "What learning patterns are most effective?",
                    "old_state": {"pattern_recognition": "developing"},
                    "new_state": {"pattern_recognition": learning_analysis.get("pattern_strength", 0.7)}
                }
            ],
            embeddings=[],
            evidence=[
                {
                    "kind": "analysis",
                    "uri": f"meta_learning://analysis/{self.trace_id}/{self.total_reflections}"
                },
                {
                    "kind": "experiences",
                    "uri": f"experiences://batch/{len(recent_experiences)}"
                }
            ]
        )
        
        # Update metrics and history
        self.total_reflections += 1
        self.consciousness_evolution_score.append(consciousness_evolution.get("evolution_score", 0.5))
        if len(self.consciousness_evolution_score) > 100:
            self.consciousness_evolution_score = self.consciousness_evolution_score[-100:]
        
        # Update meta-learning objectives
        self._update_meta_objectives(objective_evaluation)
        
        logger.info(
            "Meta-learning reflection generated",
            experiences_analyzed=len(recent_experiences),
            reflection_time=reflection_time,
            meta_insights_count=len(meta_insights.get("insights", [])),
            improvement_strategies_count=len(improvement_strategies),
            reflection_node_id=reflection_node.id
        )
        
        return reflection_node
    
    def _analyze_learning_patterns(self, experiences: List[LearningExperience]) -> Dict[str, Any]:
        """Analyze patterns in learning experiences"""
        if not experiences:
            return {"pattern_strength": 0.0, "average_efficiency": 0.0}
        
        # Efficiency analysis
        efficiencies = [exp.learning_efficiency for exp in experiences]
        average_efficiency = sum(efficiencies) / len(efficiencies)
        efficiency_trend = "improving" if efficiencies[-1] > efficiencies[0] else "declining" if len(efficiencies) > 1 else "stable"
        
        # Adaptation time analysis
        adaptation_times = [exp.adaptation_time for exp in experiences]
        average_adaptation_time = sum(adaptation_times) / len(adaptation_times)
        adaptation_trend = "faster" if adaptation_times[-1] < adaptation_times[0] else "slower" if len(adaptation_times) > 1 else "stable"
        
        # Strategy effectiveness analysis
        strategy_performance = {}
        for exp in experiences:
            strategy = exp.strategy_used
            if strategy not in strategy_performance:
                strategy_performance[strategy] = []
            strategy_performance[strategy].append(exp.final_performance)
        
        best_strategy = None
        if strategy_performance:
            strategy_averages = {
                strategy: sum(perfs) / len(perfs)
                for strategy, perfs in strategy_performance.items()
            }
            best_strategy = max(strategy_averages.items(), key=lambda x: x[1])
        
        # Consciousness coherence patterns
        coherence_scores = [exp.consciousness_coherence for exp in experiences]
        coherence_stability = 1.0 - (max(coherence_scores) - min(coherence_scores)) if coherence_scores else 1.0
        
        # Task complexity patterns
        task_complexities = [exp.context_features.get("complexity", 0.5) for exp in experiences]
        complexity_performance_correlation = self._calculate_correlation(task_complexities, [exp.final_performance for exp in experiences])
        
        return {
            "average_efficiency": average_efficiency,
            "efficiency_trend": efficiency_trend,
            "average_adaptation_time": average_adaptation_time,
            "adaptation_trend": adaptation_trend,
            "best_strategy": best_strategy,
            "strategy_performance": strategy_performance,
            "coherence_stability": coherence_stability,
            "complexity_correlation": complexity_performance_correlation,
            "pattern_strength": min(1.0, average_efficiency + coherence_stability) / 2,
            "total_experiences": len(experiences)
        }
    
    def _generate_meta_insights(self, learning_analysis: Dict[str, Any], experiences: List[LearningExperience]) -> Dict[str, Any]:
        """Generate high-level meta-learning insights"""
        insights = []
        quality_score = 0.0
        
        # Learning efficiency insights
        avg_efficiency = learning_analysis.get("average_efficiency", 0.0)
        if avg_efficiency > 0.7:
            insights.append("Learning efficiency is strong across tasks")
            quality_score += 0.2
        elif avg_efficiency > 0.4:
            insights.append("Learning efficiency shows moderate performance with room for improvement")
            quality_score += 0.1
        else:
            insights.append("Learning efficiency needs significant improvement")
        
        # Adaptation insights
        adaptation_trend = learning_analysis.get("adaptation_trend", "stable")
        if adaptation_trend == "faster":
            insights.append("Adaptation speed is improving over time")
            quality_score += 0.2
        elif adaptation_trend == "slower":
            insights.append("Adaptation speed is declining and needs attention")
        
        # Strategy insights
        best_strategy = learning_analysis.get("best_strategy")
        if best_strategy:
            insights.append(f"Strategy '{best_strategy[0]}' shows highest performance ({best_strategy[1]:.2f})")
            quality_score += 0.15
        
        # Consciousness coherence insights
        coherence_stability = learning_analysis.get("coherence_stability", 0.0)
        if coherence_stability > 0.9:
            insights.append("Consciousness coherence remains highly stable during learning")
            quality_score += 0.2
        elif coherence_stability < 0.7:
            insights.append("Consciousness coherence shows instability during learning")
        
        # Complexity handling insights
        complexity_correlation = learning_analysis.get("complexity_correlation", 0.0)
        if complexity_correlation < -0.3:
            insights.append("Performance significantly decreases with task complexity")
        elif complexity_correlation > 0.1:
            insights.append("Consciousness performs better on complex tasks")
            quality_score += 0.15
        
        # Cross-task transfer insights
        if len(set(exp.task_id.split('-')[0] for exp in experiences)) > 2:
            insights.append("Learning spans multiple task domains, enabling knowledge transfer")
            quality_score += 0.1
        
        # Recommended strategy
        recommended_strategy = "continue_current"
        if best_strategy and best_strategy[1] > 0.8:
            recommended_strategy = f"focus_on_{best_strategy[0]}"
        elif avg_efficiency < 0.5:
            recommended_strategy = "explore_new_approaches"
        
        return {
            "insights": insights,
            "quality_score": min(1.0, quality_score),
            "recommended_strategy": recommended_strategy,
            "prediction_confidence": min(1.0, quality_score + 0.2),
            "novelty_score": min(1.0, len(insights) / 8),  # More insights = more novel
            "meta_learning_score": (quality_score + learning_analysis.get("pattern_strength", 0.5)) / 2
        }
    
    def _evaluate_meta_objectives(self, experiences: List[LearningExperience]) -> Dict[str, Any]:
        """Evaluate performance against meta-learning objectives"""
        objective_scores = {}
        
        if not experiences:
            return {obj_id: {"current": 0.0, "target": obj.target_performance, "progress": 0.0}
                    for obj_id, obj in self.meta_learning_objectives.items()}
        
        # Learning efficiency objective
        avg_efficiency = sum(exp.learning_efficiency for exp in experiences) / len(experiences)
        objective_scores["learning_efficiency"] = {
            "current": avg_efficiency,
            "target": self.meta_learning_objectives["learning_efficiency"].target_performance,
            "progress": avg_efficiency / self.meta_learning_objectives["learning_efficiency"].target_performance
        }
        
        # Adaptation speed objective (inverse of adaptation time)
        avg_adaptation_time = sum(exp.adaptation_time for exp in experiences) / len(experiences)
        adaptation_speed = max(0.1, 1.0 / avg_adaptation_time) if avg_adaptation_time > 0 else 0.1
        objective_scores["adaptation_speed"] = {
            "current": min(1.0, adaptation_speed),
            "target": self.meta_learning_objectives["adaptation_speed"].target_performance,
            "progress": min(1.0, adaptation_speed) / self.meta_learning_objectives["adaptation_speed"].target_performance
        }
        
        # Knowledge transfer (mock calculation based on task diversity)
        unique_tasks = len(set(exp.task_id.split('-')[0] for exp in experiences))
        transfer_score = min(1.0, unique_tasks / 5)  # Assume 5+ task types indicates good transfer
        objective_scores["knowledge_transfer"] = {
            "current": transfer_score,
            "target": self.meta_learning_objectives["knowledge_transfer"].target_performance,
            "progress": transfer_score / self.meta_learning_objectives["knowledge_transfer"].target_performance
        }
        
        # Consciousness coherence maintenance
        avg_coherence = sum(exp.consciousness_coherence for exp in experiences) / len(experiences)
        objective_scores["consciousness_coherence"] = {
            "current": avg_coherence,
            "target": self.meta_learning_objectives["consciousness_coherence"].target_performance,
            "progress": avg_coherence / self.meta_learning_objectives["consciousness_coherence"].target_performance
        }
        
        # Ethical preservation
        avg_ethics = sum(exp.ethical_alignment for exp in experiences) / len(experiences)
        objective_scores["ethical_preservation"] = {
            "current": avg_ethics,
            "target": self.meta_learning_objectives["ethical_preservation"].target_performance,
            "progress": avg_ethics / self.meta_learning_objectives["ethical_preservation"].target_performance
        }
        
        return objective_scores
    
    def _generate_improvement_strategies(self, learning_analysis: Dict[str, Any], meta_insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate specific improvement strategies based on analysis"""
        strategies = []
        
        # Efficiency improvement strategies
        avg_efficiency = learning_analysis.get("average_efficiency", 0.0)
        if avg_efficiency < 0.6:
            strategies.append({
                "strategy": "increase_exploration_rate",
                "description": "Increase exploration to discover more effective learning approaches",
                "priority": 0.8,
                "expected_improvement": 0.2
            })
        
        # Adaptation speed strategies
        adaptation_trend = learning_analysis.get("adaptation_trend", "stable")
        if adaptation_trend == "slower":
            strategies.append({
                "strategy": "optimize_learning_rate",
                "description": "Dynamically adjust learning rates based on task complexity",
                "priority": 0.7,
                "expected_improvement": 0.15
            })
        
        # Strategy optimization
        best_strategy = learning_analysis.get("best_strategy")
        if best_strategy and best_strategy[1] > 0.7:
            strategies.append({
                "strategy": f"emphasize_{best_strategy[0]}",
                "description": f"Increase usage of {best_strategy[0]} strategy based on superior performance",
                "priority": 0.9,
                "expected_improvement": 0.1
            })
        
        # Coherence stability strategies
        coherence_stability = learning_analysis.get("coherence_stability", 0.0)
        if coherence_stability < 0.8:
            strategies.append({
                "strategy": "strengthen_coherence_preservation",
                "description": "Implement stronger consciousness coherence monitoring during learning",
                "priority": 0.85,
                "expected_improvement": 0.1
            })
        
        # Complexity handling strategies
        complexity_correlation = learning_analysis.get("complexity_correlation", 0.0)
        if complexity_correlation < -0.2:
            strategies.append({
                "strategy": "develop_complexity_handling",
                "description": "Develop specialized approaches for high-complexity tasks",
                "priority": 0.6,
                "expected_improvement": 0.25
            })
        
        # Meta-learning strategy
        if meta_insights.get("quality_score", 0.0) < 0.7:
            strategies.append({
                "strategy": "enhance_meta_reflection",
                "description": "Deepen meta-learning reflection analysis for better insights",
                "priority": 0.5,
                "expected_improvement": 0.15
            })
        
        # Sort strategies by priority
        strategies.sort(key=lambda x: x["priority"], reverse=True)
        
        return strategies[:5]  # Return top 5 strategies
    
    def _analyze_consciousness_evolution(self, experiences: List[LearningExperience]) -> Dict[str, Any]:
        """Analyze how consciousness has evolved through learning"""
        if len(experiences) < 2:
            return {"evolution_score": 0.5, "coherence_change": 0.0, "ethical_change": 0.0}
        
        # Compare early vs recent experiences
        early_experiences = experiences[:len(experiences)//3] if len(experiences) > 6 else experiences[:2]
        recent_experiences = experiences[-len(experiences)//3:] if len(experiences) > 6 else experiences[-2:]
        
        # Consciousness coherence evolution
        early_coherence = sum(exp.consciousness_coherence for exp in early_experiences) / len(early_experiences)
        recent_coherence = sum(exp.consciousness_coherence for exp in recent_experiences) / len(recent_experiences)
        coherence_change = recent_coherence - early_coherence
        
        # Ethical alignment evolution
        early_ethics = sum(exp.ethical_alignment for exp in early_experiences) / len(early_experiences)
        recent_ethics = sum(exp.ethical_alignment for exp in recent_experiences) / len(recent_experiences)
        ethical_change = recent_ethics - early_ethics
        
        # Learning performance evolution
        early_performance = sum(exp.final_performance for exp in early_experiences) / len(early_experiences)
        recent_performance = sum(exp.final_performance for exp in recent_experiences) / len(recent_experiences)
        performance_change = recent_performance - early_performance
        
        # Overall evolution score
        evolution_score = (
            (1.0 + coherence_change) * 0.4 +  # Coherence improvement (clamped at 1.0)
            (1.0 + ethical_change) * 0.3 +    # Ethics improvement  
            (0.5 + performance_change) * 0.3   # Performance improvement
        )
        evolution_score = max(0.0, min(1.0, evolution_score))
        
        return {
            "evolution_score": evolution_score,
            "coherence_change": coherence_change,
            "ethical_change": ethical_change,
            "performance_change": performance_change,
            "learning_trajectory": "improving" if evolution_score > 0.6 else "stable" if evolution_score > 0.4 else "declining",
            "consciousness_growth": evolution_score > 0.7
        }
    
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate correlation coefficient between two lists"""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        mean_x = sum(x) / len(x)
        mean_y = sum(y) / len(y)
        
        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(len(x)))
        
        sum_sq_x = sum((x[i] - mean_x) ** 2 for i in range(len(x)))
        sum_sq_y = sum((y[i] - mean_y) ** 2 for i in range(len(y)))
        
        denominator = math.sqrt(sum_sq_x * sum_sq_y)
        
        return numerator / denominator if denominator != 0 else 0.0
    
    def _update_meta_objectives(self, objective_evaluation: Dict[str, Any]):
        """Update meta-learning objectives based on evaluation"""
        for obj_id, evaluation in objective_evaluation.items():
            if obj_id in self.meta_learning_objectives:
                objective = self.meta_learning_objectives[obj_id]
                objective.current_performance = evaluation["current"]
                objective.improvement_trend.append(evaluation["progress"])
                
                # Keep last 50 trend points
                if len(objective.improvement_trend) > 50:
                    objective.improvement_trend = objective.improvement_trend[-50:]
    
    def _create_empty_reflection_node(self, context_node: MatrizNode, reason: str) -> MatrizNode:
        """Create empty reflection node when no experiences are available"""
        empty_node = MatrizNode(
            version=1,
            id=f"RL-EMPTY-REFLECTION-{self.trace_id}-{int(time.time())}",
            type="REFLECTION",
            labels=[
                f"rl:role=meta_learning@1",
                f"reflection:type=empty@1",
                f"reason:{reason}@1"
            ],
            state={
                "confidence": 0.2,
                "salience": 0.3,
                "valence": 0.4,
                "arousal": 0.2,
                "novelty": 0.1,
                "urgency": 0.3,
                
                "reflection_type": "empty_meta_learning",
                "reason": reason,
                "experiences_analyzed": 0,
                "meta_insights": {"insights": [], "quality_score": 0.0},
                "improvement_strategies": []
            },
            timestamps={
                "created_ts": int(time.time() * 1000)
            },
            provenance={
                "producer": "rl.meta_learning.empty",
                "capabilities": ["empty_reflection"],
                "tenant": "lukhas_rl",
                "trace_id": self.trace_id,
                "consent_scopes": ["empty_reflection"],
                "policy_version": "rl.empty.v1.0",
                "colony": {
                    "id": "empty_reflection",
                    "role": "placeholder",
                    "iteration": 0
                }
            },
            links=[],
            evolves_to=[],
            triggers=[],
            reflections=[],
            embeddings=[],
            evidence=[]
        )
        
        logger.warning(f"Empty reflection node created: {reason}")
        return empty_node
    
    async def get_meta_learning_metrics(self) -> Dict[str, Any]:
        """Get meta-learning system performance metrics"""
        # Learning experience metrics
        if self.learning_experiences:
            avg_efficiency = sum(exp.learning_efficiency for exp in self.learning_experiences) / len(self.learning_experiences)
            avg_coherence = sum(exp.consciousness_coherence for exp in self.learning_experiences) / len(self.learning_experiences)
            avg_ethics = sum(exp.ethical_alignment for exp in self.learning_experiences) / len(self.learning_experiences)
        else:
            avg_efficiency = avg_coherence = avg_ethics = 0.0
        
        # Objective progress
        objective_progress = {}
        for obj_id, objective in self.meta_learning_objectives.items():
            if objective.improvement_trend:
                recent_trend = objective.improvement_trend[-10:] if len(objective.improvement_trend) >= 10 else objective.improvement_trend
                objective_progress[obj_id] = {
                    "current": objective.current_performance,
                    "target": objective.target_performance,
                    "progress": objective.current_performance / objective.target_performance,
                    "trend": sum(recent_trend) / len(recent_trend)
                }
        
        # Evolution score trend
        avg_evolution = sum(self.consciousness_evolution_score) / len(self.consciousness_evolution_score) if self.consciousness_evolution_score else 0.5
        
        return {
            "total_reflections": self.total_reflections,
            "learning_experiences": len(self.learning_experiences),
            "meta_adaptation_successes": self.meta_adaptation_successes,
            "average_learning_efficiency": avg_efficiency,
            "average_consciousness_coherence": avg_coherence,
            "average_ethical_alignment": avg_ethics,
            "objective_progress": objective_progress,
            "consciousness_evolution_score": avg_evolution,
            "evolution_trend": self.consciousness_evolution_score[-20:] if len(self.consciousness_evolution_score) >= 20 else self.consciousness_evolution_score,
            "trace_id": self.trace_id
        }
    
    def clear_history(self):
        """Clear meta-learning history (for memory management)"""
        self.learning_experiences.clear()
        self.adaptation_history.clear()
        self.consciousness_evolution_score.clear()
        
        # Reset objectives but keep structure
        for objective in self.meta_learning_objectives.values():
            objective.improvement_trend.clear()
            objective.current_performance = 0.0
        
        logger.info("Meta-learning history cleared")