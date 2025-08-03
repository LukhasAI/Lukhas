# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: learning_system.py
# MODULE: learning.learning_system
# DESCRIPTION: Implements advanced learning mechanisms including meta-learning,
#              few-shot learning, and continual learning, with episodic memory
#              integration and consolidation processes.
# DEPENDENCIES: asyncio, numpy, typing, datetime, dataclasses, enum, json, math, pickle, abc, structlog
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════
# ΛORIGIN_AGENT: Jules-04
# ΛTASK_ID: 171-176
# ΛCOMMIT_WINDOW: pre-audit
# ΛAPPROVED_BY: Human Overseer (GRDM)
# ΛUDIT: Standardized header/footer, added comments, normalized logger, applied ΛTAGs.

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

import asyncio # Not actively used in async defs, but kept for potential future use
# import logging # Original logging
import structlog # ΛTRACE: Using structlog for structured logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Callable, Set # Added Set, Callable
from datetime import datetime, timedelta # Imported timedelta
from dataclasses import dataclass, field
from enum import Enum
import json # Not directly used, but often useful with Dicts
import math # Not directly used
import pickle # Not directly used
from abc import ABC, abstractmethod

# ΛTRACE: Initialize logger for learning phase
logger = structlog.get_logger().bind(tag="learning_phase")


# # Enum for types of learning supported
class LearningType(Enum):
    """Types of learning supported"""
    # ΛNOTE: Defines distinct learning paradigms.
    FEW_SHOT = "few_shot"
    META_LEARNING = "meta_learning"
    CONTINUAL = "continual"
    EPISODIC = "episodic"
    TRANSFER = "transfer"
    REINFORCEMENT = "reinforcement"


# # Enum for learning strategies
class LearningStrategy(Enum):
    """Learning strategies"""
    # ΛNOTE: Categorizes different algorithmic approaches to learning.
    GRADIENT_BASED = "gradient_based"
    MODEL_AGNOSTIC = "model_agnostic"
    MEMORY_AUGMENTED = "memory_augmented"
    NEURAL_PLASTICITY = "neural_plasticity"
    EPISODIC_REPLAY = "episodic_replay"


# # Dataclass for a learning episode
# ΛEXPOSE: Structure for representing a single learning episode, likely used across learning components.
@dataclass
class LearningEpisode:
    """Represents a learning episode"""
    # ΛNOTE: Encapsulates data and context for a discrete learning event.
    # ΛSEED: Each LearningEpisode can be considered a seed for meta-learning or few-shot tasks.
    episode_id: str
    task_type: str
    support_set: List[Dict[str, Any]] # Data to learn/adapt from
    query_set: List[Dict[str, Any]]   # Data to evaluate learning/adaptation
    learning_objective: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    performance_metrics: Dict[str, float] = field(default_factory=dict)


# # Dataclass for the result of a meta-learning process
# ΛEXPOSE: Defines the output structure of a meta-learning operation.
@dataclass
class MetaLearningResult:
    """Result of meta-learning process"""
    # ΛNOTE: Captures the outcome of learning how to learn.
    learned_strategy: Dict[str, Any] # Details of the learned meta-strategy
    adaptation_speed: float          # How quickly the learned strategy adapts
    generalization_score: float      # How well it generalizes to new tasks
    memory_efficiency: float         # Efficiency of memory usage
    confidence: float                # Confidence in the learned strategy
    applicable_domains: List[str] = field(default_factory=list)


# # Abstract base class for meta-learning algorithms
class BaseMetaLearner(ABC):
    """Abstract base class for meta-learning algorithms"""
    # ΛNOTE: Defines the contract for all meta-learning implementations.

    # # Abstract method to adapt to a new task
    @abstractmethod
    async def adapt(self,
                   support_examples: List[Dict[str, Any]],
                   task_context: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt to new task given support examples"""
        # ΛTRACE: BaseMetaLearner adapt called (should be overridden)
        logger.warn("base_meta_learner_adapt_called_abstract_method", task_context=task_context)
        pass

    # # Abstract method to meta-train on a collection of episodes
    @abstractmethod
    async def meta_train(self,
                        episodes: List[LearningEpisode]) -> MetaLearningResult:
        """Meta-train on collection of learning episodes"""
        # ΛTRACE: BaseMetaLearner meta_train called (should be overridden)
        logger.warn("base_meta_learner_meta_train_called_abstract_method", num_episodes=len(episodes))
        pass


# # Model-Agnostic Meta-Learning (MAML) implementation
# ΛEXPOSE: A specific meta-learning algorithm implementation.
class ModelAgnosticMetaLearner(BaseMetaLearner):
    """
    Model-Agnostic Meta-Learning (MAML) implementation

    Learns to learn quickly by finding good initialization points
    that can be rapidly adapted to new tasks.
    """

    # # Initialization
    def __init__(self,
                 learning_rate: float = 0.01,
                 meta_learning_rate: float = 0.001,
                 num_adaptation_steps: int = 5):
        # ΛNOTE: Configures the MAML algorithm's hyperparameters.
        # ΛSEED: Learning rates and adaptation steps are initial seeds for the MAML process.
        self.learning_rate = learning_rate
        self.meta_learning_rate = meta_learning_rate
        self.num_adaptation_steps = num_adaptation_steps
        self.meta_parameters: Dict[str, Any] = {} # Type hint for clarity
        self.adaptation_history: List[Dict[str,Any]] = [] # Type hint for clarity
        # ΛTRACE: ModelAgnosticMetaLearner initialized
        logger.debug("maml_initialized", lr=learning_rate, meta_lr=meta_learning_rate, steps=num_adaptation_steps)

    # # Adapt model to a new task using support examples
    # ΛEXPOSE: Adapts the meta-learned model to a specific task.
    async def adapt(self,
                   support_examples: List[Dict[str, Any]],
                   task_context: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt model to new task using support examples"""
        # ΛDREAM_LOOP: The adaptation process itself is a mini learning loop, refining parameters for a specific task.
        # ΛTRACE: MAML adapt start
        logger.info("maml_adapt_start", task_id=task_context.get('task_id', 'unknown'), num_support_examples=len(support_examples))
        try:
            adapted_params = self.meta_parameters.copy() # Start from meta-learned parameters

            for step in range(self.num_adaptation_steps):
                gradients = await self._compute_gradients(support_examples, adapted_params)
                for param_name, gradient in gradients.items():
                    if param_name in adapted_params and isinstance(adapted_params[param_name], (np.ndarray, list)): # Check if param exists and is list/array
                        # Ensure gradient is compatible (e.g. numpy array if param is numpy array)
                        param_val = np.array(adapted_params[param_name]) if isinstance(adapted_params[param_name], list) else adapted_params[param_name]
                        grad_val = np.array(gradient) if isinstance(gradient, list) else gradient
                        if param_val.shape == grad_val.shape:
                           adapted_params[param_name] = (param_val - self.learning_rate * grad_val).tolist() if isinstance(adapted_params[param_name], list) else (param_val - self.learning_rate * grad_val)
                        else:
                            logger.warn("maml_adapt_shape_mismatch", param_name=param_name, param_shape=param_val.shape, grad_shape=grad_val.shape)

                if step % 2 == 0: # Log progress periodically
                    loss = await self._compute_loss(support_examples, adapted_params)
                    # ΛTRACE: MAML adaptation step progress
                    logger.debug("maml_adaptation_step_progress", step=step, loss=loss)

            adaptation_quality = await self._evaluate_adaptation(support_examples, adapted_params)
            result = {
                "adapted_parameters": adapted_params, "adaptation_steps": self.num_adaptation_steps,
                "adaptation_quality": adaptation_quality, "task_context": task_context,
                "timestamp": datetime.now().isoformat()
            }
            self.adaptation_history.append(result)
            # ΛTRACE: MAML adaptation completed
            logger.info("maml_adapt_completed", task_id=task_context.get('task_id', 'unknown'), quality=adaptation_quality)
            return result
        except Exception as e:
            # ΛTRACE: MAML adaptation failed
            logger.error("maml_adapt_failed", task_id=task_context.get('task_id', 'unknown'), error=str(e), exc_info=True)
            return {"status": "failed", "error": str(e)}

    # # Meta-train on a collection of learning episodes
    # ΛEXPOSE: The core meta-training process for MAML.
    async def meta_train(self, episodes: List[LearningEpisode]) -> MetaLearningResult:
        """Meta-train on collection of learning episodes"""
        # ΛDREAM_LOOP: Meta-training is a higher-order learning loop, learning how to initialize models for quick adaptation.
        # ΛTRACE: MAML meta_train start
        logger.info("maml_meta_train_start", num_episodes=len(episodes))
        try:
            if not episodes:
                logger.error("maml_meta_train_no_episodes")
                raise ValueError("No episodes provided for meta-training")

            if not self.meta_parameters: # Initialize if empty
                # ΛSEED: Initial meta-parameters are seeded based on the first episode's structure.
                self.meta_parameters = await self._initialize_meta_parameters(episodes[0])
                # ΛTRACE: MAML meta-parameters initialized
                logger.info("maml_meta_parameters_initialized_first_time")

            total_meta_loss = 0.0
            successful_adaptations = 0

            for episode in episodes:
                # ΛTRACE: MAML meta-train processing episode
                logger.debug("maml_meta_train_processing_episode", episode_id=episode.episode_id)
                try:
                    support_set, query_set = episode.support_set, episode.query_set
                    adaptation_result = await self.adapt(support_set, {"task_type": episode.task_type, "episode_id": episode.episode_id})

                    if adaptation_result.get("status") != "failed":
                        query_loss = await self._compute_loss(query_set, adaptation_result["adapted_parameters"])
                        meta_gradients = await self._compute_meta_gradients(support_set, query_set, self.meta_parameters)

                        for param_name, meta_gradient in meta_gradients.items():
                            if param_name in self.meta_parameters and isinstance(self.meta_parameters[param_name], (np.ndarray, list)):
                                param_val = np.array(self.meta_parameters[param_name]) if isinstance(self.meta_parameters[param_name], list) else self.meta_parameters[param_name]
                                grad_val = np.array(meta_gradient) if isinstance(meta_gradient, list) else meta_gradient
                                if param_val.shape == grad_val.shape:
                                    self.meta_parameters[param_name] = (param_val - self.meta_learning_rate * grad_val).tolist() if isinstance(self.meta_parameters[param_name], list) else (param_val - self.meta_learning_rate * grad_val)
                                else:
                                     logger.warn("maml_meta_train_shape_mismatch", param_name=param_name, param_shape=param_val.shape, grad_shape=grad_val.shape)

                        total_meta_loss += query_loss
                        successful_adaptations += 1
                except Exception as e_episode: # Catch error per episode
                    logger.warn("maml_meta_train_episode_error", episode_id=episode.episode_id, error=str(e_episode), exc_info=True)
                    continue

            avg_meta_loss, adaptation_speed, generalization_score, memory_efficiency, confidence = float('inf'), 0.0, 0.0, 0.0, 0.0
            if successful_adaptations > 0:
                avg_meta_loss = total_meta_loss / successful_adaptations
                adaptation_speed = successful_adaptations / len(episodes)
                generalization_score = self._calculate_generalization_score(episodes)
                memory_efficiency = self._calculate_memory_efficiency()
                confidence = min(0.95, adaptation_speed * generalization_score)

            result = MetaLearningResult(
                learned_strategy={
                    "meta_parameters": self.meta_parameters, "learning_rate": self.learning_rate,
                    "adaptation_steps": self.num_adaptation_steps, "avg_meta_loss": avg_meta_loss
                },
                adaptation_speed=adaptation_speed, generalization_score=generalization_score,
                memory_efficiency=memory_efficiency, confidence=confidence,
                applicable_domains=self._extract_applicable_domains(episodes)
            )
            # ΛTRACE: MAML meta-training completed
            logger.info("maml_meta_train_completed", confidence=confidence, avg_meta_loss=avg_meta_loss)
            return result
        except Exception as e:
            # ΛTRACE: MAML meta-training failed
            logger.error("maml_meta_train_failed", error=str(e), exc_info=True)
            raise

    # # Placeholder: Initialize meta-parameters based on a sample episode
    async def _initialize_meta_parameters(self, sample_episode: LearningEpisode) -> Dict[str, Any]:
        """Initialize meta-parameters based on sample episode"""
        # ΛNOTE: Simplified initialization. Real MAML would infer shapes from a model architecture.
        # ΛCAUTION: Mock initialization. Parameter structure should match an actual underlying model.
        # ΛTRACE: Initializing MAML meta-parameters (mock)
        logger.debug("maml_initialize_meta_parameters_mock", sample_episode_id=sample_episode.episode_id)
        # Example: if examples have 'features' that are vectors of size 10
        feature_dim = 10
        if sample_episode.support_set and isinstance(sample_episode.support_set[0].get("features"), list):
            feature_dim = len(sample_episode.support_set[0]["features"])

        params = {
            "weights": np.random.normal(0, 0.1, (feature_dim, feature_dim)).tolist(), # Adjusted based on feature_dim
            "biases": np.zeros(feature_dim).tolist(),
            "adaptation_learning_rate_scale": 1.0 # Meta-learnable learning rate scaler
        }
        return params

    # # Placeholder: Compute gradients for parameter update
    async def _compute_gradients(self, examples: List[Dict[str, Any]], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Compute gradients for parameter update"""
        # ΛNOTE: Simplified mock gradient computation.
        # ΛCAUTION: Mock gradients. Real implementation requires backpropagation through a model.
        # ΛTRACE: Computing MAML gradients (mock)
        logger.debug("maml_compute_gradients_mock", num_examples=len(examples))
        gradients = {}
        for param_name, param_value in parameters.items():
            if isinstance(param_value, list): # Assuming list means numerical array-like
                param_array = np.array(param_value)
                gradients[param_name] = np.random.normal(0, 0.01, param_array.shape).tolist()
            elif isinstance(param_value, (int, float)): # Scalar parameter
                 gradients[param_name] = np.random.normal(0, 0.01)
        return gradients

    # # Placeholder: Compute loss on examples given parameters
    async def _compute_loss(self, examples: List[Dict[str, Any]], parameters: Dict[str, Any]) -> float:
        """Compute loss on examples given parameters"""
        # ΛNOTE: Simplified mock loss computation.
        # ΛCAUTION: Mock loss. Real implementation depends on the task and model.
        # ΛTRACE: Computing MAML loss (mock)
        logger.debug("maml_compute_loss_mock", num_examples=len(examples))
        base_loss = 1.0
        data_factor = min(0.8, len(examples) * 0.01) # Adjusted data_factor scaling
        noise = np.random.normal(0, 0.05) # Reduced noise
        loss = max(0.01, base_loss - data_factor + noise)
        return loss

    # # Placeholder: Evaluate quality of adaptation
    async def _evaluate_adaptation(self, examples: List[Dict[str, Any]], parameters: Dict[str, Any]) -> float:
        """Evaluate quality of adaptation"""
        # ΛNOTE: Mock adaptation quality evaluation.
        # ΛTRACE: Evaluating MAML adaptation (mock)
        logger.debug("maml_evaluate_adaptation_mock")
        loss = await self._compute_loss(examples, parameters)
        quality = max(0.0, 1.0 - loss) # Quality is inverse of loss
        return quality

    # # Placeholder: Compute meta-gradients for meta-parameter update
    async def _compute_meta_gradients(self, support_set: List[Dict[str, Any]], query_set: List[Dict[str, Any]], meta_params: Dict[str, Any]) -> Dict[str, Any]:
        """Compute meta-gradients for meta-parameter update"""
        # ΛNOTE: Simplified mock meta-gradient computation.
        # ΛCAUTION: Mock meta-gradients. Real implementation is complex (e.g., differentiating through optimization).
        # ΛTRACE: Computing MAML meta-gradients (mock)
        logger.debug("maml_compute_meta_gradients_mock")
        meta_gradients = {}
        for param_name, param_value in meta_params.items():
            if isinstance(param_value, list):
                param_array = np.array(param_value)
                meta_gradients[param_name] = np.random.normal(0, 0.001, param_array.shape).tolist()
            elif isinstance(param_value, (int, float)):
                 meta_gradients[param_name] = np.random.normal(0, 0.001)
        return meta_gradients

    # # Calculate generalization score across episodes
    def _calculate_generalization_score(self, episodes: List[LearningEpisode]) -> float:
        """Calculate generalization score across episodes"""
        # ΛNOTE: Heuristic for generalization based on task diversity.
        # ΛTRACE: Calculating MAML generalization score
        logger.debug("maml_calculate_generalization_score")
        if not episodes: return 0.0
        unique_tasks = len(set(ep.task_type for ep in episodes))
        task_diversity = min(1.0, unique_tasks / 5.0)
        # Assuming some baseline performance related to diversity
        return task_diversity * random.uniform(0.7, 0.9) # Add some randomness to the base score

    # # Calculate memory efficiency of meta-learning
    def _calculate_memory_efficiency(self) -> float:
        """Calculate memory efficiency of meta-learning"""
        # ΛNOTE: Heuristic for memory efficiency.
        # ΛTRACE: Calculating MAML memory efficiency
        logger.debug("maml_calculate_memory_efficiency")
        param_size = sum(np.array(v).nbytes for v in self.meta_parameters.values() if isinstance(v, (list, np.ndarray)))
        # Assuming higher is better, up to a point, then it might indicate bloat.
        # This is a placeholder, real efficiency is complex.
        efficiency = max(0.1, 1.0 - (param_size / (1024 * 1024))) # e.g. 1MB limit for high efficiency
        return efficiency

    # # Extract domains where meta-learning is applicable
    def _extract_applicable_domains(self, episodes: List[LearningEpisode]) -> List[str]:
        """Extract domains where meta-learning is applicable"""
        # ΛNOTE: Identifies domains from episode metadata.
        # ΛTRACE: Extracting MAML applicable domains
        logger.debug("maml_extract_applicable_domains")
        domains: Set[str] = set() # type hint for clarity
        for episode in episodes:
            if episode.task_type: domains.add(episode.task_type)
            if "domain" in episode.metadata: domains.add(episode.metadata["domain"])
        return list(domains)

# # Few-shot learning system
# ΛEXPOSE: System for learning from very few examples.
class FewShotLearner:
    """
    Few-shot learning system that can learn from limited examples

    Implements various few-shot learning strategies including:
    - Prototypical networks
    - Matching networks
    - Memory-augmented approaches
    """

    # # Initialization
    def __init__(self, strategy: LearningStrategy = LearningStrategy.MEMORY_AUGMENTED):
        # ΛNOTE: Initializes with a chosen few-shot learning strategy.
        # ΛSEED: The chosen `strategy` is a seed for how few-shot learning will operate.
        self.strategy = strategy
        self.prototypes: Dict[str, Any] = {}
        self.memory_bank: List[Dict[str,Any]] = []
        self.support_examples: Dict[str, Any] = {}
        # ΛTRACE: FewShotLearner initialized
        logger.debug("few_shot_learner_initialized", strategy=strategy.value)

    # # Learn from a few examples (k-shot learning)
    # ΛEXPOSE: Main method to perform k-shot learning.
    async def learn_from_examples(self,
                                task_id: str,
                                examples: List[Dict[str, Any]],
                                labels: List[str],
                                k_shot: int = 5) -> Dict[str, Any]:
        """Learn from few examples (k-shot learning)"""
        # ΛDREAM_LOOP: Each k-shot learning instance refines prototypes or memory, contributing to an adaptive knowledge base.
        # ΛTRACE: Few-shot learn_from_examples start
        logger.info("few_shot_learn_from_examples_start", task_id=task_id, k_shot=k_shot, num_examples=len(examples), strategy=self.strategy.value)
        try:
            if len(examples) < k_shot:
                logger.warn("few_shot_insufficient_examples", task_id=task_id, available=len(examples), required=k_shot)

            actual_k_shot = min(k_shot, len(examples)) # Use available examples if less than k_shot
            self.support_examples[task_id] = {
                "examples": examples[:actual_k_shot], "labels": labels[:actual_k_shot], "timestamp": datetime.now()
            }

            if self.strategy == LearningStrategy.MEMORY_AUGMENTED:
                result = await self._memory_augmented_learning(task_id, examples, labels, actual_k_shot)
            elif self.strategy == LearningStrategy.NEURAL_PLASTICITY: # Not a common FSL strategy, more for continual
                result = await self._neural_plasticity_learning(task_id, examples, labels, actual_k_shot)
            else: # Default to prototypical or make it explicit
                result = await self._prototypical_learning(task_id, examples, labels, actual_k_shot)

            learning_quality = await self._evaluate_few_shot_learning(task_id, examples, labels)
            result["learning_quality"] = learning_quality
            # ΛTRACE: Few-shot learning completed
            logger.info("few_shot_learn_from_examples_completed", task_id=task_id, quality=learning_quality)
            return result
        except Exception as e:
            # ΛTRACE: Few-shot learning failed
            logger.error("few_shot_learn_from_examples_failed", task_id=task_id, error=str(e), exc_info=True)
            return {"status": "failed", "error": str(e)}

    # # Placeholder: Memory-augmented few-shot learning
    async def _memory_augmented_learning(self, task_id: str, examples: List[Dict[str, Any]], labels: List[str], k_shot: int) -> Dict[str, Any]:
        """Memory-augmented few-shot learning"""
        # ΛNOTE: Simulates learning by creating prototypes and storing them in a memory bank.
        # ΛCAUTION: Mock implementation. Real memory-augmented networks are more complex.
        # ΛTRACE: Few-shot memory_augmented_learning (mock)
        logger.debug("few_shot_memory_augmented_learning_mock", task_id=task_id, k_shot=k_shot)
        class_prototypes: Dict[str, List[Any]] = defaultdict(list) # Use defaultdict
        for example, label in zip(examples[:k_shot], labels[:k_shot]):
            class_prototypes[label].append(example)

        for label, class_examples in class_prototypes.items():
            prototype = await self._compute_prototype(class_examples)
            self.prototypes[f"{task_id}_{label}"] = prototype # Store task-specific prototypes

        memory_entry = {"task_id": task_id, "prototypes_generated": list(class_prototypes.keys()), "timestamp": datetime.now(), "k_shot": k_shot}
        self.memory_bank.append(memory_entry)
        if len(self.memory_bank) > 100: self.memory_bank.pop(0) # FIFO queue for memory bank

        return {"strategy": "memory_augmented", "learned_prototypes": len(class_prototypes), "memory_bank_size": len(self.memory_bank), "task_id": task_id}

    # # Placeholder: Neural plasticity-based few-shot learning (conceptual)
    async def _neural_plasticity_learning(self, task_id: str, examples: List[Dict[str, Any]], labels: List[str], k_shot: int) -> Dict[str, Any]:
        """Neural plasticity-based few-shot learning"""
        # ΛNOTE: Conceptual simulation of rapid synaptic changes.
        # ΛCAUTION: Highly abstract mock. Real neural plasticity is a complex biological and computational field.
        # ΛTRACE: Few-shot neural_plasticity_learning (mock)
        logger.debug("few_shot_neural_plasticity_learning_mock", task_id=task_id, k_shot=k_shot)
        plasticity_params = {"adaptation_rate": 0.1, "consolidation_rate": 0.05, "interference_resistance": 0.8}
        synaptic_changes = [{"example_id": i, "label": label, "synaptic_strength": 0.8 + (i * 0.05), "consolidation_time": (datetime.now() + timedelta(minutes=30)).isoformat()} for i, (example, label) in enumerate(zip(examples[:k_shot], labels[:k_shot]))]
        return {"strategy": "neural_plasticity", "synaptic_changes_count": len(synaptic_changes), "plasticity_params": plasticity_params, "task_id": task_id} # Return count

    # # Placeholder: Prototypical networks approach
    async def _prototypical_learning(self, task_id: str, examples: List[Dict[str, Any]], labels: List[str], k_shot: int) -> Dict[str, Any]:
        """Prototypical networks approach"""
        # ΛNOTE: Simulates learning by forming class prototypes.
        # ΛCAUTION: Mock implementation. Real prototypical networks involve embedding spaces and distance metrics.
        # ΛTRACE: Few-shot prototypical_learning (mock)
        logger.debug("few_shot_prototypical_learning_mock", task_id=task_id, k_shot=k_shot)
        class_groups: Dict[str, List[Any]] = defaultdict(list) # Use defaultdict
        for example, label in zip(examples[:k_shot], labels[:k_shot]):
            class_groups[label].append(example)

        prototypes = {}
        for label, class_examples in class_groups.items():
            prototype = await self._compute_prototype(class_examples)
            prototypes[label] = prototype
            self.prototypes[f"{task_id}_{label}"] = prototype # Store task-specific prototypes
        return {"strategy": "prototypical", "learned_prototypes_count": len(prototypes), "prototype_keys": list(prototypes.keys()), "task_id": task_id} # Return count

    # # Placeholder: Compute prototype representation from examples
    async def _compute_prototype(self, examples: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compute prototype representation from examples"""
        # ΛNOTE: Simplified prototype computation (averaging).
        # ΛCAUTION: Mock prototype computation. Real methods depend on feature types and model.
        # ΛTRACE: Computing prototype (mock)
        logger.debug("few_shot_compute_prototype_mock", num_examples=len(examples))
        if not examples: return {}
        prototype: Dict[str, Any] = {}
        all_keys: Set[str] = set()
        for example in examples: all_keys.update(example.keys())

        for key in all_keys:
            values = [ex[key] for ex in examples if key in ex and isinstance(ex[key], (int, float))]
            if values: prototype[key] = sum(values) / len(values)

        prototype["_prototype_metadata"] = {"size": len(examples), "computed_at": datetime.now().isoformat()} # Renamed key
        return prototype

    # # Placeholder: Evaluate quality of few-shot learning
    async def _evaluate_few_shot_learning(self, task_id: str, examples: List[Dict[str, Any]], labels: List[str]) -> float:
        """Evaluate quality of few-shot learning"""
        # ΛNOTE: Mock evaluation of few-shot learning quality.
        # ΛTRACE: Evaluating few-shot learning (mock)
        logger.debug("few_shot_evaluate_learning_mock", task_id=task_id)
        if task_id not in self.support_examples or not self.support_examples[task_id]["labels"]: return 0.0
        support_data = self.support_examples[task_id]
        unique_labels = len(set(support_data["labels"]))
        # Quality based on how many unique labels were actually used to form prototypes vs expected
        # This is a proxy for how well the few shots covered the necessary classes.
        num_prototypes_for_task = sum(1 for k in self.prototypes if k.startswith(f"{task_id}_"))
        coverage_score = min(1.0, num_prototypes_for_task / max(1,unique_labels))
        consistency_score = random.uniform(0.6, 0.9) # Mock consistency
        return (coverage_score * 0.5 + consistency_score * 0.5)


# # Continual learning system
# ΛEXPOSE: System for learning sequentially without forgetting previous tasks.
class ContinualLearner:
    """
    Continual learning system that learns without catastrophic forgetting

    Implements elastic weight consolidation and other anti-forgetting techniques.
    """

    # # Initialization
    def __init__(self):
        # ΛNOTE: Initializes structures for tracking tasks and importance weights.
        self.learned_tasks: Dict[str, Any] = {}
        self.importance_weights: Dict[str, Any] = {} # Stores Fisher information or similar
        self.task_sequence: List[str] = []
        self.consolidation_threshold: float = 0.7 # Importance threshold for memory consolidation
        # ΛTRACE: ContinualLearner initialized
        logger.debug("continual_learner_initialized", consolidation_threshold=self.consolidation_threshold)

    # # Learn a new task continually
    # ΛEXPOSE: Main method for learning a new task in a continual learning setting.
    async def learn_task_continually(self, task_id: str, task_data: Dict[str, Any], prevent_forgetting: bool = True) -> Dict[str, Any]:
        """Learn new task while preserving previous knowledge"""
        # ΛDREAM_LOOP: Each new task learned builds upon previous ones, ideally without catastrophic forgetting, forming a lifelong learning loop.
        # ΛTRACE: Continual learn_task_continually start
        logger.info("continual_learn_task_start", task_id=task_id, prevent_forgetting=prevent_forgetting)
        try:
            self.learned_tasks[task_id] = {"task_data": task_data, "learned_at": datetime.now(), "importance": 1.0} # Initial importance
            self.task_sequence.append(task_id)

            result: Dict[str, Any] = {"task_id": task_id, "total_tasks": len(self.learned_tasks)}
            if prevent_forgetting and len(self.learned_tasks) > 1:
                # ΛNOTE: EWC and memory consolidation are key anti-forgetting strategies.
                consolidation_result = await self._apply_elastic_weight_consolidation(task_id)
                memory_result = await self._consolidate_memories(task_id)
                result.update({"continual_learning_active": True, "ewc_result": consolidation_result, "memory_consolidation_result": memory_result})
            else:
                result["continual_learning_active"] = False

            performance = await self._evaluate_continual_performance()
            result["performance_metrics"] = performance
            # ΛTRACE: Continual learning for task completed
            logger.info("continual_learn_task_completed", task_id=task_id, overall_performance=performance.get("overall"))
            return result
        except Exception as e:
            # ΛTRACE: Continual learning task failed
            logger.error("continual_learn_task_failed", task_id=task_id, error=str(e), exc_info=True)
            return {"status": "failed", "error": str(e)}

    # # Placeholder: Apply Elastic Weight Consolidation (EWC)
    async def _apply_elastic_weight_consolidation(self, new_task_id: str) -> Dict[str, Any]:
        """Apply elastic weight consolidation to prevent forgetting"""
        # ΛNOTE: Simulates EWC by calculating and storing importance weights.
        # ΛCAUTION: Mock EWC. Real EWC involves quadratic penalties on important parameters.
        # ΛTRACE: Applying EWC (mock)
        logger.debug("continual_apply_ewc_mock", new_task_id=new_task_id)
        try:
            previous_tasks = [tid for tid in self.task_sequence[:-1]] # Exclude current new_task_id
            consolidation_strength = 0.0; protected_parameters_count = 0

            for prev_task_id in previous_tasks:
                if prev_task_id in self.learned_tasks:
                    task_importance = self.learned_tasks[prev_task_id].get("importance", 0.5) # Use .get
                    # ΛSEED: Importance weights for previous tasks act as seeds guiding current learning.
                    importance_weights = await self._calculate_parameter_importance(prev_task_id)
                    self.importance_weights[prev_task_id] = importance_weights
                    consolidation_strength += task_importance
                    protected_parameters_count += sum(1 for v in importance_weights.values() if v > 0) # Count params with non-zero importance

            return {"ewc_applied": True, "consolidation_strength": consolidation_strength, "protected_parameters_count": protected_parameters_count, "previous_tasks_considered": len(previous_tasks)}
        except Exception as e:
            # ΛTRACE: EWC application failed
            logger.error("continual_apply_ewc_failed", error=str(e), exc_info=True)
            return {"ewc_applied": False, "error": str(e)}

    # # Placeholder: Calculate parameter importance (e.g., Fisher information)
    async def _calculate_parameter_importance(self, task_id: str) -> Dict[str, float]:
        """Calculate parameter importance for task (Fisher information)"""
        # ΛNOTE: Mock calculation of parameter importance.
        # ΛCAUTION: Mock Fisher info. Real calculation is data and model dependent.
        # ΛTRACE: Calculating parameter importance (mock)
        logger.debug("continual_calculate_parameter_importance_mock", task_id=task_id)
        # task_data = self.learned_tasks[task_id]["task_data"] # Not used in mock
        # Example: importance based on parameter name patterns or random
        importance_weights = {f"param_{i}": random.uniform(0.1, 1.0) for i in range(5)} # Mock 5 parameters
        return importance_weights

    # # Placeholder: Consolidate memories to strengthen important knowledge
    async def _consolidate_memories(self, new_task_id: str) -> Dict[str, Any]:
        """Consolidate memories to strengthen important knowledge"""
        # ΛNOTE: Simulates strengthening important memories/tasks.
        # ΛDREAM_LOOP: Memory consolidation is a process of refining and reinforcing learned knowledge over time.
        # ΛCAUTION: Mock memory consolidation. Real mechanisms are complex (e.g., replay, generative replay).
        # ΛTRACE: Consolidating memories (mock)
        logger.debug("continual_consolidate_memories_mock", new_task_id=new_task_id)
        try:
            high_importance_tasks = [tid for tid, info in self.learned_tasks.items() if info.get("importance",0) > self.consolidation_threshold and tid != new_task_id]
            consolidated_memories_count = 0
            for task_id_to_consolidate in high_importance_tasks: # Renamed task_id
                current_importance = self.learned_tasks[task_id_to_consolidate]["importance"]
                self.learned_tasks[task_id_to_consolidate]["importance"] = min(1.0, current_importance * 1.05) # Strengthen importance
                consolidated_memories_count +=1
            return {"consolidation_cycles_simulated": 1, "consolidated_memories_count": consolidated_memories_count, "high_importance_tasks_count": len(high_importance_tasks)}
        except Exception as e:
            # ΛTRACE: Memory consolidation failed
            logger.error("continual_consolidate_memories_failed", error=str(e), exc_info=True)
            return {"consolidation_failed": True, "error": str(e)}

    # # Evaluate continual learning performance
    async def _evaluate_continual_performance(self) -> Dict[str, float]:
        """Evaluate continual learning performance"""
        # ΛNOTE: Calculates stability (retaining old knowledge) and plasticity (learning new).
        # ΛTRACE: Evaluating continual performance
        logger.debug("continual_evaluate_performance")
        if not self.learned_tasks: return {"stability": 0.0, "plasticity": 0.0, "overall": 0.0, "task_count":0}

        total_importance = sum(task.get("importance", 0.0) for task in self.learned_tasks.values()) # Use .get
        avg_importance = total_importance / len(self.learned_tasks) if self.learned_tasks else 0.0
        stability = min(1.0, avg_importance) # Higher average importance means better stability

        # Plasticity: Consider how many recent tasks were "successfully" added (e.g. have non-zero importance)
        recent_task_count = min(3, len(self.task_sequence)) # Look at up to last 3 tasks
        successfully_learned_recent = sum(1 for tid in self.task_sequence[-recent_task_count:] if self.learned_tasks.get(tid, {}).get("importance",0) > 0.1) # Proxy for successful learning
        plasticity = successfully_learned_recent / recent_task_count if recent_task_count > 0 else 0.0

        overall = (stability * 0.6 + plasticity * 0.4) # Weighted average
        return {"stability": stability, "plasticity": plasticity, "overall": overall, "task_count": len(self.learned_tasks)}


# # Unified Advanced Learning System
# ΛEXPOSE: Top-level class integrating various advanced learning mechanisms.
class AdvancedLearningSystem:
    """
    Unified Advanced Learning System for lukhas AI

    Integrates meta-learning, few-shot learning, and continual learning
    capabilities into a single coherent system.
    """

    # # Initialization
    def __init__(self):
        # ΛNOTE: Composes the different learning systems.
        self.meta_learner = ModelAgnosticMetaLearner()
        self.few_shot_learner = FewShotLearner()
        self.continual_learner = ContinualLearner()

        self.learning_history: List[Dict[str,Any]] = []
        self.performance_metrics: Dict[str, Any] = {}
        self.active_learning_tasks: Dict[str, Any] = {}

        self._setup_logging() # Called here, but logger is module-level via structlog
        # ΛTRACE: AdvancedLearningSystem initialized
        logger.info("advanced_learning_system_initialized")

    # # Setup logging (structlog is already set up at module level)
    def _setup_logging(self):
        """Setup logging for advanced learning system"""
        # structlog is configured at module level, this can be a pass or for specific configurations.
        # ΛTRACE: Logging setup confirmed (using module-level structlog)
        logger.debug("advanced_learning_system_logging_setup_confirmed")

    # # Initialize the advanced learning system and its components
    # ΛEXPOSE: Method to explicitly initialize the system if needed post-construction.
    async def initialize(self) -> bool:
        """Initialize the advanced learning system"""
        # ΛTRACE: AdvancedLearningSystem initializing components
        logger.info("advanced_learning_system_initialize_start")
        try:
            await self._initialize_components() # Components are simple inits, but kept async for consistency
            self.performance_metrics = {
                "meta_learning_episodes": 0, "few_shot_tasks": 0, "continual_learning_tasks": 0,
                "overall_performance": 0.0, "last_update": datetime.now().isoformat()
            }
            # ΛTRACE: AdvancedLearningSystem initialized successfully
            logger.info("advanced_learning_system_initialize_success")
            return True
        except Exception as e:
            # ΛTRACE: AdvancedLearningSystem initialization failed
            logger.error("advanced_learning_system_initialize_failed", error=str(e), exc_info=True)
            return False

    # # Placeholder: Initialize learning components (if more complex setup needed)
    async def _initialize_components(self):
        """Initialize learning components"""
        # ΛNOTE: Currently components are initialized in __init__. This is for future extension.
        # ΛTRACE: Initializing learning components (currently no-op beyond __init__)
        logger.debug("advanced_learning_system_initialize_components_noop")
        pass # Components are already initialized in __init__

    # # Learn from a collection of learning episodes based on specified type
    # ΛEXPOSE: Central method to dispatch learning tasks to appropriate sub-systems.
    async def learn_from_episodes(self, episodes: List[LearningEpisode], learning_type: LearningType = LearningType.META_LEARNING) -> Dict[str, Any]:
        """Learn from a collection of learning episodes"""
        # ΛDREAM_LOOP: This function routes learning tasks, contributing to the overall adaptive behavior of the AGI.
        # ΛTRACE: learn_from_episodes called
        logger.info("advanced_system_learn_from_episodes_start", num_episodes=len(episodes), type=learning_type.value)
        try:
            result: Dict[str, Any] = {} # Ensure result is always defined
            if learning_type == LearningType.META_LEARNING:
                result = await self.meta_learner.meta_train(episodes) # result is MetaLearningResult, convert to dict if necessary
                if isinstance(result, MetaLearningResult): result = result.__dict__ # Basic conversion
                self.performance_metrics["meta_learning_episodes"] += len(episodes)
            elif learning_type == LearningType.FEW_SHOT:
                processed_results = []
                for episode in episodes:
                    if episode.support_set and len(episode.support_set) > 0 : # Ensure support_set is not empty
                        examples = episode.support_set
                        labels = [ex.get("label", f"unknown_label_{i}") for i, ex in enumerate(examples)] # Provide default labels
                        k = min(5, len(examples)) if len(examples) > 0 else 0 # Ensure k_shot > 0
                        if k > 0:
                           processed_results.append(await self.few_shot_learner.learn_from_examples(episode.episode_id, examples, labels, k_shot=k))
                result = {"learning_type": "few_shot", "processed_episodes": len(processed_results), "results": processed_results, "successful_learning": sum(1 for r in processed_results if r.get("status") != "failed")}
                self.performance_metrics["few_shot_tasks"] += len(processed_results)
            elif learning_type == LearningType.CONTINUAL:
                processed_results = [await self.continual_learner.learn_task_continually(ep.episode_id, {"support_set": ep.support_set, "query_set": ep.query_set, "task_type": ep.task_type, "metadata": ep.metadata}) for ep in episodes]
                result = {"learning_type": "continual", "processed_episodes": len(processed_results), "results": processed_results, "successful_learning": sum(1 for r in processed_results if r.get("status") != "failed")}
                self.performance_metrics["continual_learning_tasks"] += len(processed_results)
            else:
                logger.error("unsupported_learning_type_in_learn_from_episodes", type=learning_type.value)
                raise ValueError(f"Unsupported learning type: {learning_type}")

            self.learning_history.append({"timestamp": datetime.now(), "learning_type": learning_type.value, "episodes_count": len(episodes), "result_summary": {k:v for k,v in result.items() if k != 'results' and k != 'learned_strategy'} }) # Avoid too large results in history
            await self._update_overall_performance()
            # ΛTRACE: learn_from_episodes completed
            logger.info("advanced_system_learn_from_episodes_completed", type=learning_type.value, num_episodes=len(episodes))
            return result
        except Exception as e:
            # ΛTRACE: learn_from_episodes failed
            logger.error("advanced_system_learn_from_episodes_failed", type=learning_type.value, error=str(e), exc_info=True)
            return {"status": "failed", "error": str(e)}

    # # Adapt to a new task using available learning mechanisms
    # ΛEXPOSE: Allows the system to adapt to new tasks dynamically.
    async def adapt_to_new_task(self, task_definition: Dict[str, Any], support_examples: List[Dict[str, Any]], adaptation_strategy: Optional[LearningStrategy] = None) -> Dict[str, Any]: # adaptation_strategy not used yet
        """Adapt to a new task using available learning mechanisms"""
        # ΛDREAM_LOOP: Adapting to new tasks is a core AGI capability, representing a learning cycle.
        # ΛTRACE: adapt_to_new_task called
        task_id = task_definition.get("task_id", f"task_{datetime.now().timestamp()}")
        logger.info("advanced_system_adapt_to_new_task_start", task_id=task_id, num_support_examples=len(support_examples))
        try:
            adaptation_results: Dict[str, Any] = {}
            # ΛNOTE: Tries multiple adaptation approaches.
            if len(support_examples) >= 1: # MAML can work with k=1, but more is better.
                meta_result = await self.meta_learner.adapt(support_examples, task_definition)
                adaptation_results["meta_learning_adaptation"] = meta_result # Changed key for clarity

            if len(support_examples) > 0 and len(support_examples) <= 10: # Typical few-shot range
                labels = [ex.get("label", f"default_label_{i}") for i, ex in enumerate(support_examples)] # Provide default labels
                few_shot_result = await self.few_shot_learner.learn_from_examples(task_id, support_examples, labels, k_shot=min(5, len(support_examples)))
                adaptation_results["few_shot_learning"] = few_shot_result # Changed key

            continual_result = await self.continual_learner.learn_task_continually(task_id, {"task_definition": task_definition, "support_examples": support_examples})
            adaptation_results["continual_learning"] = continual_result # Changed key

            combined_result = {
                "task_id": task_id, "adaptation_methods_attempted": list(adaptation_results.keys()),
                "adaptation_details": adaptation_results, # Keep detailed results under a sub-key
                "overall_success_heuristic": all(res.get("status") != "failed" and res.get("error") is None for res in adaptation_results.values() if isinstance(res,dict)), # More robust check
                "timestamp": datetime.now().isoformat()
            }
            self.active_learning_tasks[task_id] = combined_result
            # ΛTRACE: adapt_to_new_task completed
            logger.info("advanced_system_adapt_to_new_task_completed", task_id=task_id, success_heuristic=combined_result["overall_success_heuristic"])
            return combined_result
        except Exception as e:
            # ΛTRACE: adapt_to_new_task failed
            logger.error("advanced_system_adapt_to_new_task_failed", task_id=task_id, error=str(e), exc_info=True)
            return {"status": "failed", "error": str(e)}

    # # Get comprehensive learning analytics
    # ΛEXPOSE: Provides insights into the system's learning performance and state.
    async def get_learning_analytics(self) -> Dict[str, Any]:
        """Get comprehensive learning analytics"""
        # ΛTRACE: get_learning_analytics called
        logger.info("advanced_system_get_learning_analytics_start")
        try:
            return {
                "overall_metrics": self.performance_metrics.copy(),
                "history_analysis": self._analyze_learning_history(),
                "meta_learning_analytics": await self._get_meta_learning_analytics(),
                "few_shot_analytics": await self._get_few_shot_analytics(),
                "continual_learning_analytics": await self._get_continual_analytics(),
                "active_tasks_count": len(self.active_learning_tasks), # Return count
                "analysis_timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            # ΛTRACE: get_learning_analytics failed
            logger.error("advanced_system_get_learning_analytics_failed", error=str(e), exc_info=True)
            return {"status": "error", "error": str(e)}

    # # Analyze learning history for insights
    def _analyze_learning_history(self) -> Dict[str, Any]:
        """Analyze learning history for insights"""
        # ΛNOTE: Provides meta-analysis of past learning activities.
        # ΛTRACE: Analyzing learning history
        logger.debug("advanced_system_analyze_learning_history")
        if not self.learning_history: return {"status": "no_history_to_analyze"}
        total_episodes = sum(entry.get("episodes_count",0) for entry in self.learning_history)
        learning_types = [entry.get("learning_type", "unknown") for entry in self.learning_history]
        type_counts = {lt: learning_types.count(lt) for lt in set(learning_types)}
        timestamps = [entry.get("timestamp", datetime.min) for entry in self.learning_history] # Ensure datetime objects
        learning_frequency = 0.0
        if len(timestamps) > 1 :
            time_span_seconds = (max(timestamps) - min(timestamps)).total_seconds()
            if time_span_seconds > 0 :
                 learning_frequency = len(timestamps) / (time_span_seconds / 3600.0) # sessions per hour

        return {
            "total_learning_sessions": len(self.learning_history), "total_episodes_processed": total_episodes,
            "learning_type_distribution": type_counts, "learning_frequency_per_hour": learning_frequency,
            "most_recent_session_time": max(timestamps).isoformat() if timestamps else None
        }

    # # Get meta-learning specific analytics
    async def _get_meta_learning_analytics(self) -> Dict[str, Any]:
        """Get meta-learning specific analytics"""
        # ΛTRACE: Getting meta-learning analytics
        logger.debug("advanced_system_get_meta_learning_analytics")
        return {
            "adaptation_history_size": len(self.meta_learner.adaptation_history),
            "meta_parameters_keys": list(self.meta_learner.meta_parameters.keys()), # Show keys instead of full params
            "current_learning_rate": self.meta_learner.learning_rate, # Corrected attribute name
            "current_meta_learning_rate": self.meta_learner.meta_learning_rate, # Corrected
            "current_adaptation_steps": self.meta_learner.num_adaptation_steps # Corrected
        }

    # # Get few-shot learning specific analytics
    async def _get_few_shot_analytics(self) -> Dict[str, Any]:
        """Get few-shot learning specific analytics"""
        # ΛTRACE: Getting few-shot analytics
        logger.debug("advanced_system_get_few_shot_analytics")
        return {
            "learned_prototypes_count": len(self.few_shot_learner.prototypes), # Corrected
            "memory_bank_size": len(self.few_shot_learner.memory_bank),
            "tracked_support_tasks_count": len(self.few_shot_learner.support_examples), # Corrected
            "current_strategy": self.few_shot_learner.strategy.value # Corrected
        }

    # # Get continual learning specific analytics
    async def _get_continual_analytics(self) -> Dict[str, Any]:
        """Get continual learning specific analytics"""
        # ΛTRACE: Getting continual learning analytics
        logger.debug("advanced_system_get_continual_analytics")
        performance = await self.continual_learner._evaluate_continual_performance()
        return {
            "learned_tasks_count": len(self.continual_learner.learned_tasks), # Corrected
            "task_sequence_length": len(self.continual_learner.task_sequence),
            "importance_weights_tracked_tasks_count": len(self.continual_learner.importance_weights), # Corrected
            "current_consolidation_threshold": self.continual_learner.consolidation_threshold, # Corrected
            "current_performance_metrics": performance
        }

    # # Update overall performance metrics (mock)
    async def _update_overall_performance(self):
        """Update overall performance metrics"""
        # ΛNOTE: Mock calculation for overall system performance.
        # ΛCAUTION: Mock performance update. Real evaluation is complex.
        # ΛTRACE: Updating overall performance (mock)
        logger.debug("advanced_system_update_overall_performance_mock")
        try:
            meta_perf = self.performance_metrics.get("meta_learning_episodes",0) > 0 # Simplified check
            few_shot_perf = self.performance_metrics.get("few_shot_tasks",0) > 0
            continual_perf_metrics = await self.continual_learner._evaluate_continual_performance()
            continual_overall = continual_perf_metrics.get("overall", 0.0)

            # Very rough heuristic
            perf_indicators = [1 if meta_perf else 0.5, 1 if few_shot_perf else 0.5, continual_overall]
            overall = np.mean(perf_indicators) * random.uniform(0.8,1.0) # Add some variability

            self.performance_metrics["overall_performance"] = min(1.0, overall) # Cap at 1.0
            self.performance_metrics["last_update"] = datetime.now().isoformat()
        except Exception as e:
            # ΛTRACE: Overall performance update failed
            logger.error("advanced_system_overall_performance_update_failed", error=str(e), exc_info=True)

    # # Cleanup learning system resources
    # ΛEXPOSE: Method for system cleanup, e.g., managing history size.
    async def cleanup(self):
        """Cleanup learning system resources"""
        # ΛTRACE: AdvancedLearningSystem cleanup initiated
        logger.info("advanced_system_cleanup_start")
        try:
            if len(self.learning_history) > 100: # Limit history size
                self.learning_history = self.learning_history[-100:]
                # ΛTRACE: Learning history truncated
                logger.debug("learning_history_truncated", new_size=len(self.learning_history))

            current_time = datetime.now()
            # Remove tasks older than 1 hour (3600 seconds)
            old_tasks = [task_id for task_id, task_data in self.active_learning_tasks.items() if isinstance(task_data.get("timestamp"), str) and (current_time - datetime.fromisoformat(task_data["timestamp"])).total_seconds() > 3600]

            for task_id in old_tasks: del self.active_learning_tasks[task_id]
            if old_tasks:
                # ΛTRACE: Old active tasks cleared
                logger.debug("old_active_tasks_cleared", num_cleared=len(old_tasks))

            # ΛTRACE: AdvancedLearningSystem cleanup completed
            logger.info("advanced_system_cleanup_completed")
        except Exception as e:
            # ΛTRACE: Cleanup failed
            logger.error("advanced_system_cleanup_failed", error=str(e), exc_info=True)


# # Export main classes and enums for module users
__all__ = [
    'AdvancedLearningSystem', 'ModelAgnosticMetaLearner', 'FewShotLearner',
    'ContinualLearner', 'LearningEpisode', 'MetaLearningResult',
    'LearningType', 'LearningStrategy'
]

# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: learning_system.py
# VERSION: 1.1 (Jules-04 update)
# TIER SYSTEM: Core AI / Advanced Learning (Assumed Highest Tier)
# ΛTRACE INTEGRATION: ENABLED (structlog)
# CAPABILITIES: Meta-learning (MAML-like), Few-shot learning (Prototypical, Memory-Augmented),
#               Continual learning (EWC-like), unified learning system interface.
# FUNCTIONS: AdvancedLearningSystem (class and methods), various learner classes and dataclasses.
# CLASSES: LearningType (Enum), LearningStrategy (Enum), LearningEpisode, MetaLearningResult,
#          BaseMetaLearner, ModelAgnosticMetaLearner, FewShotLearner, ContinualLearner, AdvancedLearningSystem
# DECORATORS: @dataclass, @abstractmethod
# DEPENDENCIES: asyncio, structlog, numpy, typing, datetime, dataclasses, enum, abc
# INTERFACES: `AdvancedLearningSystem.initialize()`, `learn_from_episodes()`, `adapt_to_new_task()`, `get_learning_analytics()`, `cleanup()`
# ERROR HANDLING: Try/except blocks in main methods, logging errors. Some placeholders return basic error dicts.
# LOGGING: ΛTRACE_ENABLED via structlog, bound with tag="learning_phase"
# AUTHENTICATION: N/A (Assumed handled by calling service or environment)
# HOW TO USE:
#   Instantiate `AdvancedLearningSystem()`. Call `initialize()`.
#   Use `learn_from_episodes()` for batch learning tasks of different types.
#   Use `adapt_to_new_task()` for dynamic adaptation.
#   Use `get_learning_analytics()` for insights. Call `cleanup()` periodically.
# INTEGRATION NOTES: Many internal methods (_compute_gradients, _compute_loss, etc.) are currently
#                    placeholders (mocks) and need full implementation with actual models and algorithms.
#                    Asyncio not heavily utilized yet but available for future IO-bound operations.
# MAINTENANCE: Implement all placeholder methods. Refine mock calculations for more realistic behavior.
#              Expand error handling and reporting. Integrate real underlying ML models.
# CONTACT: LUKHAS DEVELOPMENT TEAM
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════
