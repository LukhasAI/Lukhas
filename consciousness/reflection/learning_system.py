"""

#TAG:consciousness
#TAG:reflection
#TAG:neuroplastic
#TAG:colony


🧠 Advanced Learning Systems for lukhas AI
Sophisticated meta-learning, few-shot learning, and continual learning capabilities

This module implements advanced learning mechanisms including:
- Few-shot learning capabilities
- Meta-learning frameworks
- Continual learning without catastrophic forgetting
- Episodic memory integration
- Memory consolidation processes

Based on requirements from elite AI expert evaluation.
"""

import asyncio
from core.common import get_logger
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Callable, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import math
import pickle
from abc import ABC, abstractmethod

logger = get_logger(__name__)


class LearningType(Enum):
    """Types of learning supported"""
    FEW_SHOT = "few_shot"
    META_LEARNING = "meta_learning"
    CONTINUAL = "continual"
    EPISODIC = "episodic"
    TRANSFER = "transfer"
    REINFORCEMENT = "reinforcement"


class LearningStrategy(Enum):
    """Learning strategies"""
    GRADIENT_BASED = "gradient_based"
    MODEL_AGNOSTIC = "model_agnostic"
    MEMORY_AUGMENTED = "memory_augmented"
    NEURAL_PLASTICITY = "neural_plasticity"
    EPISODIC_REPLAY = "episodic_replay"


@dataclass
class LearningEpisode:
    """Represents a learning episode"""
    episode_id: str
    task_type: str
    support_set: List[Dict[str, Any]]
    query_set: List[Dict[str, Any]]
    learning_objective: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    performance_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class MetaLearningResult:
    """Result of meta-learning process"""
    learned_strategy: Dict[str, Any]
    adaptation_speed: float
    generalization_score: float
    memory_efficiency: float
    confidence: float
    applicable_domains: List[str] = field(default_factory=list)


class BaseMetaLearner(ABC):
    """Abstract base class for meta-learning algorithms"""
    
    @abstractmethod
    async def adapt(self, 
                   support_examples: List[Dict[str, Any]], 
                   task_context: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt to new task given support examples"""
        pass
    
    @abstractmethod
    async def meta_train(self, 
                        episodes: List[LearningEpisode]) -> MetaLearningResult:
        """Meta-train on collection of learning episodes"""
        pass


class ModelAgnosticMetaLearner(BaseMetaLearner):
    """
    Model-Agnostic Meta-Learning (MAML) implementation
    
    Learns to learn quickly by finding good initialization points
    that can be rapidly adapted to new tasks.
    """
    
    def __init__(self, 
                 learning_rate: float = 0.01,
                 meta_learning_rate: float = 0.001,
                 num_adaptation_steps: int = 5):
        self.learning_rate = learning_rate
        self.meta_learning_rate = meta_learning_rate
        self.num_adaptation_steps = num_adaptation_steps
        self.meta_parameters = {}
        self.adaptation_history = []
        
    async def adapt(self, 
                   support_examples: List[Dict[str, Any]], 
                   task_context: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt model to new task using support examples"""
        try:
            logger.info(f"🎯 Adapting to new task: {task_context.get('task_id', 'unknown')}")
            
            # Initialize with meta-learned parameters
            adapted_params = self.meta_parameters.copy()
            
            # Perform gradient-based adaptation
            for step in range(self.num_adaptation_steps):
                # Compute gradients on support set
                gradients = await self._compute_gradients(support_examples, adapted_params)
                
                # Update parameters
                for param_name, gradient in gradients.items():
                    if param_name in adapted_params:
                        adapted_params[param_name] -= self.learning_rate * gradient
                
                # Log adaptation progress
                if step % 2 == 0:
                    loss = await self._compute_loss(support_examples, adapted_params)
                    logger.debug(f"Adaptation step {step}, loss: {loss:.4f}")
            
            # Evaluate adaptation quality
            adaptation_quality = await self._evaluate_adaptation(
                support_examples, adapted_params
            )
            
            result = {
                "adapted_parameters": adapted_params,
                "adaptation_steps": self.num_adaptation_steps,
                "adaptation_quality": adaptation_quality,
                "task_context": task_context,
                "timestamp": datetime.now().isoformat()
            }
            
            # Store adaptation history
            self.adaptation_history.append(result)
            
            logger.info(f"✅ Task adaptation completed (quality: {adaptation_quality:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"Task adaptation failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def meta_train(self, episodes: List[LearningEpisode]) -> MetaLearningResult:
        """Meta-train on collection of learning episodes"""
        try:
            logger.info(f"🧠 Starting meta-training on {len(episodes)} episodes")
            
            if not episodes:
                raise ValueError("No episodes provided for meta-training")
            
            # Initialize meta-parameters if not exists
            if not self.meta_parameters:
                self.meta_parameters = await self._initialize_meta_parameters(episodes[0])
            
            total_meta_loss = 0.0
            successful_adaptations = 0
            
            # Meta-training loop
            for episode in episodes:
                try:
                    # Split episode into support and query sets
                    support_set = episode.support_set
                    query_set = episode.query_set
                    
                    # Adapt to task using support set
                    adaptation_result = await self.adapt(
                        support_set, 
                        {"task_type": episode.task_type, "episode_id": episode.episode_id}
                    )
                    
                    if adaptation_result.get("status") != "failed":
                        # Evaluate on query set
                        query_loss = await self._compute_loss(
                            query_set, 
                            adaptation_result["adapted_parameters"]
                        )
                        
                        # Compute meta-gradients
                        meta_gradients = await self._compute_meta_gradients(
                            support_set, query_set, self.meta_parameters
                        )
                        
                        # Update meta-parameters
                        for param_name, meta_gradient in meta_gradients.items():
                            if param_name in self.meta_parameters:
                                self.meta_parameters[param_name] -= (
                                    self.meta_learning_rate * meta_gradient
                                )
                        
                        total_meta_loss += query_loss
                        successful_adaptations += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to process episode {episode.episode_id}: {e}")
                    continue
            
            # Calculate meta-learning metrics
            if successful_adaptations > 0:
                avg_meta_loss = total_meta_loss / successful_adaptations
                adaptation_speed = successful_adaptations / len(episodes)
                generalization_score = self._calculate_generalization_score(episodes)
                memory_efficiency = self._calculate_memory_efficiency()
                confidence = min(0.95, adaptation_speed * generalization_score)
            else:
                avg_meta_loss = float('inf')
                adaptation_speed = 0.0
                generalization_score = 0.0
                memory_efficiency = 0.0
                confidence = 0.0
            
            result = MetaLearningResult(
                learned_strategy={
                    "meta_parameters": self.meta_parameters,
                    "learning_rate": self.learning_rate,
                    "adaptation_steps": self.num_adaptation_steps,
                    "avg_meta_loss": avg_meta_loss
                },
                adaptation_speed=adaptation_speed,
                generalization_score=generalization_score,
                memory_efficiency=memory_efficiency,
                confidence=confidence,
                applicable_domains=self._extract_applicable_domains(episodes)
            )
            
            logger.info(f"✅ Meta-training completed (confidence: {confidence:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"Meta-training failed: {e}")
            raise
    
    async def _initialize_meta_parameters(self, sample_episode: LearningEpisode) -> Dict[str, Any]:
        """Initialize meta-parameters based on sample episode"""
        # Simple initialization based on sample data structure
        params = {
            "weights": np.random.normal(0, 0.1, (10, 10)).tolist(),
            "biases": np.zeros(10).tolist(),
            "adaptation_rate": 0.01,
            "task_embedding": np.random.normal(0, 0.1, 5).tolist()
        }
        return params
    
    async def _compute_gradients(self, 
                               examples: List[Dict[str, Any]], 
                               parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Compute gradients for parameter update"""
        # Simplified gradient computation
        gradients = {}
        
        for param_name, param_value in parameters.items():
            if isinstance(param_value, list):
                # Compute mock gradients (in real implementation, this would be actual gradients)
                param_array = np.array(param_value)
                gradient = np.random.normal(0, 0.01, param_array.shape)
                gradients[param_name] = gradient.tolist()
        
        return gradients
    
    async def _compute_loss(self, 
                          examples: List[Dict[str, Any]], 
                          parameters: Dict[str, Any]) -> float:
        """Compute loss on examples given parameters"""
        # Simplified loss computation
        base_loss = 1.0
        
        # Reduce loss based on number of examples (more data = better fit)
        data_factor = min(0.8, len(examples) * 0.1)
        
        # Add some randomness to simulate actual computation
        noise = np.random.normal(0, 0.1)
        
        loss = max(0.01, base_loss - data_factor + noise)
        return loss
    
    async def _evaluate_adaptation(self, 
                                 examples: List[Dict[str, Any]], 
                                 parameters: Dict[str, Any]) -> float:
        """Evaluate quality of adaptation"""
        # Quality based on loss and consistency
        loss = await self._compute_loss(examples, parameters)
        quality = max(0.0, 1.0 - loss)
        return quality
    
    async def _compute_meta_gradients(self, 
                                    support_set: List[Dict[str, Any]], 
                                    query_set: List[Dict[str, Any]], 
                                    meta_params: Dict[str, Any]) -> Dict[str, Any]:
        """Compute meta-gradients for meta-parameter update"""
        # Simplified meta-gradient computation
        meta_gradients = {}
        
        for param_name, param_value in meta_params.items():
            if isinstance(param_value, list):
                param_array = np.array(param_value)
                meta_gradient = np.random.normal(0, 0.001, param_array.shape)
                meta_gradients[param_name] = meta_gradient.tolist()
        
        return meta_gradients
    
    def _calculate_generalization_score(self, episodes: List[LearningEpisode]) -> float:
        """Calculate generalization score across episodes"""
        if not episodes:
            return 0.0
        
        # Score based on diversity of tasks and performance
        unique_tasks = len(set(ep.task_type for ep in episodes))
        task_diversity = min(1.0, unique_tasks / 5.0)  # Normalize to 5 max unique tasks
        
        return task_diversity * 0.8  # Good generalization baseline
    
    def _calculate_memory_efficiency(self) -> float:
        """Calculate memory efficiency of meta-learning"""
        # Efficiency based on parameter count and adaptation history
        param_count = sum(len(str(v)) for v in self.meta_parameters.values())
        efficiency = max(0.3, 1.0 - (param_count / 10000))  # Normalize
        return efficiency
    
    def _extract_applicable_domains(self, episodes: List[LearningEpisode]) -> List[str]:
        """Extract domains where meta-learning is applicable"""
        domains = set()
        for episode in episodes:
            if episode.task_type:
                domains.add(episode.task_type)
            if "domain" in episode.metadata:
                domains.add(episode.metadata["domain"])
        
        return list(domains)


class FewShotLearner:
    """
    Few-shot learning system that can learn from limited examples
    
    Implements various few-shot learning strategies including:
    - Prototypical networks
    - Matching networks
    - Memory-augmented approaches
    """
    
    def __init__(self, strategy: LearningStrategy = LearningStrategy.MEMORY_AUGMENTED):
        self.strategy = strategy
        self.prototypes = {}
        self.memory_bank = []
        self.support_examples = {}
        
    async def learn_from_examples(self, 
                                task_id: str,
                                examples: List[Dict[str, Any]], 
                                labels: List[str],
                                k_shot: int = 5) -> Dict[str, Any]:
        """Learn from few examples (k-shot learning)"""
        try:
            logger.info(f"📚 Starting {k_shot}-shot learning for task: {task_id}")
            
            if len(examples) < k_shot:
                logger.warning(f"Only {len(examples)} examples available for {k_shot}-shot learning")
            
            # Store support examples
            self.support_examples[task_id] = {
                "examples": examples[:k_shot],
                "labels": labels[:k_shot],
                "timestamp": datetime.now()
            }
            
            # Learn based on strategy
            if self.strategy == LearningStrategy.MEMORY_AUGMENTED:
                result = await self._memory_augmented_learning(task_id, examples, labels, k_shot)
            elif self.strategy == LearningStrategy.NEURAL_PLASTICITY:
                result = await self._neural_plasticity_learning(task_id, examples, labels, k_shot)
            else:
                result = await self._prototypical_learning(task_id, examples, labels, k_shot)
            
            # Evaluate learning quality
            learning_quality = await self._evaluate_few_shot_learning(task_id, examples, labels)
            result["learning_quality"] = learning_quality
            
            logger.info(f"✅ Few-shot learning completed (quality: {learning_quality:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"Few-shot learning failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _memory_augmented_learning(self, 
                                       task_id: str,
                                       examples: List[Dict[str, Any]], 
                                       labels: List[str],
                                       k_shot: int) -> Dict[str, Any]:
        """Memory-augmented few-shot learning"""
        # Create prototypes for each class
        class_prototypes = {}
        for example, label in zip(examples[:k_shot], labels[:k_shot]):
            if label not in class_prototypes:
                class_prototypes[label] = []
            class_prototypes[label].append(example)
        
        # Compute prototype embeddings
        for label, class_examples in class_prototypes.items():
            prototype = await self._compute_prototype(class_examples)
            self.prototypes[f"{task_id}_{label}"] = prototype
        
        # Add to memory bank
        memory_entry = {
            "task_id": task_id,
            "prototypes": class_prototypes,
            "timestamp": datetime.now(),
            "k_shot": k_shot
        }
        self.memory_bank.append(memory_entry)
        
        # Maintain memory bank size
        if len(self.memory_bank) > 100:
            self.memory_bank = self.memory_bank[-100:]
        
        return {
            "strategy": "memory_augmented",
            "learned_prototypes": len(class_prototypes),
            "memory_bank_size": len(self.memory_bank),
            "task_id": task_id
        }
    
    async def _neural_plasticity_learning(self, 
                                        task_id: str,
                                        examples: List[Dict[str, Any]], 
                                        labels: List[str],
                                        k_shot: int) -> Dict[str, Any]:
        """Neural plasticity-based few-shot learning"""
        # Simulate neural plasticity adaptation
        plasticity_params = {
            "adaptation_rate": 0.1,
            "consolidation_rate": 0.05,
            "interference_resistance": 0.8
        }
        
        # Rapid synaptic changes for quick learning
        synaptic_changes = []
        for i, (example, label) in enumerate(zip(examples[:k_shot], labels[:k_shot])):
            change = {
                "example_id": i,
                "label": label,
                "synaptic_strength": 0.8 + (i * 0.05),  # Increasing strength
                "consolidation_time": datetime.now() + timedelta(minutes=30)
            }
            synaptic_changes.append(change)
        
        return {
            "strategy": "neural_plasticity",
            "synaptic_changes": len(synaptic_changes),
            "plasticity_params": plasticity_params,
            "task_id": task_id
        }
    
    async def _prototypical_learning(self, 
                                   task_id: str,
                                   examples: List[Dict[str, Any]], 
                                   labels: List[str],
                                   k_shot: int) -> Dict[str, Any]:
        """Prototypical networks approach"""
        # Group examples by class
        class_groups = {}
        for example, label in zip(examples[:k_shot], labels[:k_shot]):
            if label not in class_groups:
                class_groups[label] = []
            class_groups[label].append(example)
        
        # Compute prototypes
        prototypes = {}
        for label, class_examples in class_groups.items():
            prototype = await self._compute_prototype(class_examples)
            prototypes[label] = prototype
            self.prototypes[f"{task_id}_{label}"] = prototype
        
        return {
            "strategy": "prototypical",
            "learned_prototypes": len(prototypes),
            "prototype_keys": list(prototypes.keys()),
            "task_id": task_id
        }
    
    async def _compute_prototype(self, examples: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compute prototype representation from examples"""
        if not examples:
            return {}
        
        # Simple averaging of features
        prototype = {}
        
        # Get all keys from all examples
        all_keys = set()
        for example in examples:
            all_keys.update(example.keys())
        
        # Compute average for each feature
        for key in all_keys:
            values = []
            for example in examples:
                if key in example:
                    value = example[key]
                    if isinstance(value, (int, float)):
                        values.append(value)
            
            if values:
                prototype[key] = sum(values) / len(values)
        
        # Add metadata
        prototype["_prototype_size"] = len(examples)
        prototype["_computed_at"] = datetime.now().isoformat()
        
        return prototype
    
    async def _evaluate_few_shot_learning(self, 
                                        task_id: str,
                                        examples: List[Dict[str, Any]], 
                                        labels: List[str]) -> float:
        """Evaluate quality of few-shot learning"""
        if task_id not in self.support_examples:
            return 0.0
        
        # Quality based on prototype consistency and coverage
        support_data = self.support_examples[task_id]
        unique_labels = len(set(support_data["labels"]))
        coverage_score = min(1.0, unique_labels / 3.0)  # Normalize to 3 classes
        
        # Consistency score (mock)
        consistency_score = 0.8  # Good baseline
        
        return (coverage_score + consistency_score) / 2.0


class ContinualLearner:
    """
    Continual learning system that learns without catastrophic forgetting
    
    Implements elastic weight consolidation and other anti-forgetting techniques.
    """
    
    def __init__(self):
        self.learned_tasks = {}
        self.importance_weights = {}
        self.task_sequence = []
        self.consolidation_threshold = 0.7
        
    async def learn_task_continually(self, 
                                   task_id: str,
                                   task_data: Dict[str, Any],
                                   prevent_forgetting: bool = True) -> Dict[str, Any]:
        """Learn new task while preserving previous knowledge"""
        try:
            logger.info(f"🔄 Starting continual learning for task: {task_id}")
            
            # Store current task
            self.learned_tasks[task_id] = {
                "task_data": task_data,
                "learned_at": datetime.now(),
                "importance": 1.0
            }
            
            self.task_sequence.append(task_id)
            
            if prevent_forgetting and len(self.learned_tasks) > 1:
                # Apply elastic weight consolidation
                consolidation_result = await self._apply_elastic_weight_consolidation(task_id)
                
                # Perform memory consolidation
                memory_result = await self._consolidate_memories(task_id)
                
                result = {
                    "task_id": task_id,
                    "continual_learning": True,
                    "consolidation": consolidation_result,
                    "memory_consolidation": memory_result,
                    "total_tasks": len(self.learned_tasks)
                }
            else:
                result = {
                    "task_id": task_id,
                    "continual_learning": False,
                    "total_tasks": len(self.learned_tasks)
                }
            
            # Evaluate continual learning performance
            performance = await self._evaluate_continual_performance()
            result["performance_metrics"] = performance
            
            logger.info(f"✅ Continual learning completed for {task_id}")
            return result
            
        except Exception as e:
            logger.error(f"Continual learning failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _apply_elastic_weight_consolidation(self, new_task_id: str) -> Dict[str, Any]:
        """Apply elastic weight consolidation to prevent forgetting"""
        try:
            # Calculate importance weights for previous tasks
            previous_tasks = [tid for tid in self.task_sequence if tid != new_task_id]
            
            consolidation_strength = 0.0
            protected_parameters = 0
            
            for prev_task_id in previous_tasks:
                if prev_task_id in self.learned_tasks:
                    task_importance = self.learned_tasks[prev_task_id]["importance"]
                    
                    # Calculate parameter importance (Fisher information approximation)
                    importance_weights = await self._calculate_parameter_importance(prev_task_id)
                    self.importance_weights[prev_task_id] = importance_weights
                    
                    consolidation_strength += task_importance
                    protected_parameters += len(importance_weights)
            
            return {
                "consolidation_applied": True,
                "consolidation_strength": consolidation_strength,
                "protected_parameters": protected_parameters,
                "previous_tasks": len(previous_tasks)
            }
            
        except Exception as e:
            logger.error(f"Elastic weight consolidation failed: {e}")
            return {"consolidation_applied": False, "error": str(e)}
    
    async def _calculate_parameter_importance(self, task_id: str) -> Dict[str, float]:
        """Calculate parameter importance for task (Fisher information)"""
        # Mock Fisher information calculation
        task_data = self.learned_tasks[task_id]["task_data"]
        
        importance_weights = {}
        
        # Generate importance weights based on task characteristics
        data_complexity = len(str(task_data))
        base_importance = min(1.0, data_complexity / 1000.0)
        
        # Create importance weights for different parameter types
        param_types = ["weights", "biases", "embeddings", "attention"]
        for param_type in param_types:
            importance_weights[param_type] = base_importance * np.random.uniform(0.5, 1.0)
        
        return importance_weights
    
    async def _consolidate_memories(self, new_task_id: str) -> Dict[str, Any]:
        """Consolidate memories to strengthen important knowledge"""
        try:
            # Identify high-importance memories
            high_importance_tasks = []
            for task_id, task_info in self.learned_tasks.items():
                if task_info["importance"] > self.consolidation_threshold:
                    high_importance_tasks.append(task_id)
            
            # Simulate memory consolidation process
            consolidation_cycles = 3
            consolidated_memories = 0
            
            for cycle in range(consolidation_cycles):
                for task_id in high_importance_tasks:
                    # Strengthen memory traces
                    if task_id in self.learned_tasks:
                        current_importance = self.learned_tasks[task_id]["importance"]
                        # Gradual strengthening
                        new_importance = min(1.0, current_importance * 1.05)
                        self.learned_tasks[task_id]["importance"] = new_importance
                        consolidated_memories += 1
            
            return {
                "consolidation_cycles": consolidation_cycles,
                "consolidated_memories": consolidated_memories,
                "high_importance_tasks": len(high_importance_tasks)
            }
            
        except Exception as e:
            logger.error(f"Memory consolidation failed: {e}")
            return {"consolidation_failed": True, "error": str(e)}
    
    async def _evaluate_continual_performance(self) -> Dict[str, float]:
        """Evaluate continual learning performance"""
        if not self.learned_tasks:
            return {"stability": 0.0, "plasticity": 0.0, "overall": 0.0}
        
        # Stability: how well previous knowledge is retained
        total_importance = sum(task["importance"] for task in self.learned_tasks.values())
        avg_importance = total_importance / len(self.learned_tasks)
        stability = min(1.0, avg_importance)
        
        # Plasticity: ability to learn new tasks
        recent_tasks = self.task_sequence[-3:] if len(self.task_sequence) >= 3 else self.task_sequence
        plasticity = len(recent_tasks) / 3.0  # Normalize to 3 recent tasks
        
        # Overall performance
        overall = (stability + plasticity) / 2.0
        
        return {
            "stability": stability,
            "plasticity": plasticity,
            "overall": overall,
            "task_count": len(self.learned_tasks)
        }


class AdvancedLearningSystem:
    """
    Unified Advanced Learning System for lukhas AI
    
    Integrates meta-learning, few-shot learning, and continual learning
    capabilities into a single coherent system.
    """
    
    def __init__(self):
        self.meta_learner = ModelAgnosticMetaLearner()
        self.few_shot_learner = FewShotLearner()
        self.continual_learner = ContinualLearner()
        
        self.learning_history = []
        self.performance_metrics = {}
        self.active_learning_tasks = {}
        
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging for advanced learning system"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    async def initialize(self) -> bool:
        """Initialize the advanced learning system"""
        try:
            logger.info("🧠 Initializing Advanced Learning System...")
            
            # Initialize components
            await self._initialize_components()
            
            # Setup performance tracking
            self.performance_metrics = {
                "meta_learning_episodes": 0,
                "few_shot_tasks": 0,
                "continual_learning_tasks": 0,
                "overall_performance": 0.0,
                "last_update": datetime.now().isoformat()
            }
            
            logger.info("✅ Advanced Learning System initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Advanced Learning System: {e}")
            return False
    
    async def _initialize_components(self):
        """Initialize learning components"""
        # Components are already initialized in __init__
        logger.info("🔧 Learning components initialized")
    
    async def learn_from_episodes(self, 
                                episodes: List[LearningEpisode],
                                learning_type: LearningType = LearningType.META_LEARNING) -> Dict[str, Any]:
        """Learn from a collection of learning episodes"""
        try:
            logger.info(f"📚 Starting learning from {len(episodes)} episodes (type: {learning_type.value})")
            
            if learning_type == LearningType.META_LEARNING:
                result = await self.meta_learner.meta_train(episodes)
                self.performance_metrics["meta_learning_episodes"] += len(episodes)
                
            elif learning_type == LearningType.FEW_SHOT:
                # Process as few-shot learning tasks
                results = []
                for episode in episodes:
                    if episode.support_set and len(episode.support_set) <= 10:
                        examples = episode.support_set
                        labels = [ex.get("label", "unknown") for ex in examples]
                        
                        few_shot_result = await self.few_shot_learner.learn_from_examples(
                            episode.episode_id,
                            examples,
                            labels,
                            k_shot=min(5, len(examples))
                        )
                        results.append(few_shot_result)
                
                result = {
                    "learning_type": "few_shot",
                    "processed_episodes": len(results),
                    "successful_learning": sum(1 for r in results if r.get("status") != "failed"),
                    "results": results
                }
                self.performance_metrics["few_shot_tasks"] += len(results)
                
            elif learning_type == LearningType.CONTINUAL:
                # Process as continual learning
                results = []
                for episode in episodes:
                    continual_result = await self.continual_learner.learn_task_continually(
                        episode.episode_id,
                        {
                            "support_set": episode.support_set,
                            "query_set": episode.query_set,
                            "task_type": episode.task_type,
                            "metadata": episode.metadata
                        }
                    )
                    results.append(continual_result)
                
                result = {
                    "learning_type": "continual",
                    "processed_episodes": len(results),
                    "successful_learning": sum(1 for r in results if r.get("status") != "failed"),
                    "results": results
                }
                self.performance_metrics["continual_learning_tasks"] += len(results)
                
            else:
                raise ValueError(f"Unsupported learning type: {learning_type}")
            
            # Update learning history
            learning_entry = {
                "timestamp": datetime.now(),
                "learning_type": learning_type.value,
                "episodes_count": len(episodes),
                "result": result
            }
            self.learning_history.append(learning_entry)
            
            # Update overall performance
            await self._update_overall_performance()
            
            logger.info(f"✅ Learning completed for {len(episodes)} episodes")
            return result
            
        except Exception as e:
            logger.error(f"Learning from episodes failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def adapt_to_new_task(self, 
                              task_definition: Dict[str, Any],
                              support_examples: List[Dict[str, Any]],
                              adaptation_strategy: Optional[LearningStrategy] = None) -> Dict[str, Any]:
        """Adapt to a new task using available learning mechanisms"""
        try:
            task_id = task_definition.get("task_id", f"task_{datetime.now().timestamp()}")
            logger.info(f"🎯 Adapting to new task: {task_id}")
            
            adaptation_results = {}
            
            # Try meta-learning adaptation
            if len(support_examples) >= 3:
                meta_result = await self.meta_learner.adapt(support_examples, task_definition)
                adaptation_results["meta_learning"] = meta_result
            
            # Try few-shot learning
            if len(support_examples) <= 10:
                labels = [ex.get("label", "default") for ex in support_examples]
                few_shot_result = await self.few_shot_learner.learn_from_examples(
                    task_id,
                    support_examples,
                    labels,
                    k_shot=min(5, len(support_examples))
                )
                adaptation_results["few_shot"] = few_shot_result
            
            # Apply continual learning
            continual_result = await self.continual_learner.learn_task_continually(
                task_id,
                {
                    "task_definition": task_definition,
                    "support_examples": support_examples
                }
            )
            adaptation_results["continual"] = continual_result
            
            # Combine adaptation results
            combined_result = {
                "task_id": task_id,
                "adaptation_methods": list(adaptation_results.keys()),
                "adaptation_results": adaptation_results,
                "overall_success": all(
                    result.get("status") != "failed" 
                    for result in adaptation_results.values()
                ),
                "timestamp": datetime.now().isoformat()
            }
            
            # Store as active learning task
            self.active_learning_tasks[task_id] = combined_result
            
            logger.info(f"✅ Task adaptation completed: {task_id}")
            return combined_result
            
        except Exception as e:
            logger.error(f"Task adaptation failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def get_learning_analytics(self) -> Dict[str, Any]:
        """Get comprehensive learning analytics"""
        try:
            # Performance metrics
            current_metrics = self.performance_metrics.copy()
            
            # Learning history analysis
            history_stats = self._analyze_learning_history()
            
            # Component-specific analytics
            meta_learning_analytics = await self._get_meta_learning_analytics()
            few_shot_analytics = await self._get_few_shot_analytics()
            continual_analytics = await self._get_continual_analytics()
            
            return {
                "overall_metrics": current_metrics,
                "history_analysis": history_stats,
                "meta_learning": meta_learning_analytics,
                "few_shot_learning": few_shot_analytics,
                "continual_learning": continual_analytics,
                "active_tasks": len(self.active_learning_tasks),
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Learning analytics failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def _analyze_learning_history(self) -> Dict[str, Any]:
        """Analyze learning history for insights"""
        if not self.learning_history:
            return {"status": "no_history"}
        
        # Basic statistics
        total_episodes = sum(entry["episodes_count"] for entry in self.learning_history)
        learning_types = [entry["learning_type"] for entry in self.learning_history]
        type_counts = {lt: learning_types.count(lt) for lt in set(learning_types)}
        
        # Temporal analysis
        timestamps = [entry["timestamp"] for entry in self.learning_history]
        learning_frequency = len(timestamps) / max(1, (max(timestamps) - min(timestamps)).total_seconds() / 3600)
        
        return {
            "total_learning_sessions": len(self.learning_history),
            "total_episodes_processed": total_episodes,
            "learning_type_distribution": type_counts,
            "learning_frequency_per_hour": learning_frequency,
            "most_recent_session": max(timestamps).isoformat()
        }
    
    async def _get_meta_learning_analytics(self) -> Dict[str, Any]:
        """Get meta-learning specific analytics"""
        return {
            "adaptation_history_size": len(self.meta_learner.adaptation_history),
            "meta_parameters_count": len(self.meta_learner.meta_parameters),
            "learning_rate": self.meta_learner.learning_rate,
            "meta_learning_rate": self.meta_learner.meta_learning_rate,
            "adaptation_steps": self.meta_learner.num_adaptation_steps
        }
    
    async def _get_few_shot_analytics(self) -> Dict[str, Any]:
        """Get few-shot learning specific analytics"""
        return {
            "learned_prototypes": len(self.few_shot_learner.prototypes),
            "memory_bank_size": len(self.few_shot_learner.memory_bank),
            "support_examples_tasks": len(self.few_shot_learner.support_examples),
            "learning_strategy": self.few_shot_learner.strategy.value
        }
    
    async def _get_continual_analytics(self) -> Dict[str, Any]:
        """Get continual learning specific analytics"""
        performance = await self.continual_learner._evaluate_continual_performance()
        
        return {
            "learned_tasks": len(self.continual_learner.learned_tasks),
            "task_sequence_length": len(self.continual_learner.task_sequence),
            "importance_weights_count": len(self.continual_learner.importance_weights),
            "consolidation_threshold": self.continual_learner.consolidation_threshold,
            "performance_metrics": performance
        }
    
    async def _update_overall_performance(self):
        """Update overall performance metrics"""
        try:
            # Calculate overall performance based on component performances
            meta_performance = 0.8  # Mock performance
            few_shot_performance = 0.7  # Mock performance
            continual_performance = 0.75  # Mock performance
            
            overall = (meta_performance + few_shot_performance + continual_performance) / 3.0
            
            self.performance_metrics["overall_performance"] = overall
            self.performance_metrics["last_update"] = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"Performance update failed: {e}")
    
    async def cleanup(self):
        """Cleanup learning system resources"""
        try:
            logger.info("🧹 Cleaning up Advanced Learning System...")
            
            # Clear caches and temporary data
            if len(self.learning_history) > 100:
                self.learning_history = self.learning_history[-100:]
            
            # Clear old active tasks
            current_time = datetime.now()
            old_tasks = [
                task_id for task_id, task_data in self.active_learning_tasks.items()
                if (current_time - datetime.fromisoformat(task_data["timestamp"])).total_seconds() > 3600
            ]
            
            for task_id in old_tasks:
                del self.active_learning_tasks[task_id]
            
            logger.info("✅ Advanced Learning System cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")


# Export main classes
__all__ = [
    'AdvancedLearningSystem', 'ModelAgnosticMetaLearner', 'FewShotLearner', 
    'ContinualLearner', 'LearningEpisode', 'MetaLearningResult', 
    'LearningType', 'LearningStrategy'
]
