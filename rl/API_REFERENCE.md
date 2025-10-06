---
status: wip
type: documentation
---
# MΛTRIZ RL System API Reference

## Overview

Complete API reference for the MΛTRIZ Reinforcement Learning system. All components follow consciousness-first design principles and emit MΛTRIZ schema v1.1 compliant nodes.

## Core Classes

### ConsciousnessEnvironment

**Purpose**: CONTEXT node emission for consciousness-aware environment observation

```python
class ConsciousnessEnvironment:
    def __init__(
        self,
        module_registry_size: int = 50,
        coherence_threshold: float = 0.95,
        context_depth: int = 3
    )
```

#### Methods

##### `async observe() -> MatrizNode`
Generate consciousness-aware environment observation.

**Returns**: CONTEXT node with environment state

**Example**:
```python
env = ConsciousnessEnvironment()
context_node = await env.observe()
print(f"Coherence: {context_node.state['temporal_coherence']}")
```

##### `async step(action_node: MatrizNode) -> MatrizNode`
Execute action and return new environment state.

**Parameters**:
- `action_node`: DECISION node representing action to take

**Returns**: CONTEXT node with updated environment state

**Example**:
```python
next_context = await env.step(decision_node)
reward_signal = next_context.state.get('reward_signal', 0.0)
```

##### `async get_environment_metrics() -> Dict[str, Any]`
Get comprehensive environment performance metrics.

**Returns**: Dictionary containing:
- `total_observations`: Number of observations generated
- `average_coherence`: Average temporal coherence
- `consciousness_modules_active`: Number of active consciousness modules
- `context_depth_average`: Average context integration depth

---

### PolicyNetwork

**Purpose**: DECISION node emission for consciousness-aware action selection

```python
class PolicyNetwork:
    def __init__(
        self,
        state_dim: int = 256,
        action_dim: int = 64,
        hidden_dims: List[int] = [512, 256, 128],
        ethical_weight: float = 0.2,
        coherence_weight: float = 0.3
    )
```

#### Methods

##### `async select_action(context_node: MatrizNode, **kwargs) -> MatrizNode`
Select consciousness-aware action based on context.

**Parameters**:
- `context_node`: CONTEXT node with environment state
- `exploration_rate`: Optional exploration parameter
- `urgency_modifier`: Optional urgency adjustment

**Returns**: DECISION node representing selected action

**Example**:
```python
policy = PolicyNetwork()
decision = await policy.select_action(
    context_node,
    exploration_rate=0.1,
    urgency_modifier=1.2
)
```

##### `async evaluate_action_batch(context_nodes: List[MatrizNode]) -> List[MatrizNode]`
Batch action selection for efficiency.

**Parameters**:
- `context_nodes`: List of CONTEXT nodes

**Returns**: List of DECISION nodes

##### `async get_policy_metrics() -> Dict[str, Any]`
Get policy performance metrics.

**Returns**: Dictionary containing:
- `total_decisions`: Number of decisions made
- `average_confidence`: Average decision confidence
- `ethical_violations`: Count of ethical constraint violations
- `exploration_rate`: Current exploration rate

---

### ValueNetwork

**Purpose**: HYPOTHESIS node emission for multi-objective value estimation

```python
class ValueNetwork:
    def __init__(
        self,
        state_dim: int = 256,
        hidden_dims: List[int] = [512, 256, 128],
        objective_weights: Dict[str, float] = None
    )
```

#### Methods

##### `async estimate_value(context_node: MatrizNode, **kwargs) -> MatrizNode`
Estimate multi-objective value for given context.

**Parameters**:
- `context_node`: CONTEXT node to evaluate
- `prediction_horizon`: Time horizon for prediction (default: 10)

**Returns**: HYPOTHESIS node with value predictions

**Example**:
```python
value_net = ValueNetwork()
value_hypothesis = await value_net.estimate_value(
    context_node,
    prediction_horizon=20
)

# Access multi-objective values
objectives = value_hypothesis.state['objective_predictions']
coherence_value = objectives['coherence']
ethics_value = objectives['ethics']
```

##### `async estimate_value_batch(context_nodes: List[MatrizNode]) -> List[MatrizNode]`
Batch value estimation for multiple contexts.

##### `async update_objectives(new_weights: Dict[str, float])`
Update multi-objective weights dynamically.

**Parameters**:
- `new_weights`: New objective weight distribution

---

### ConsciousnessBuffer

**Purpose**: MEMORY node emission with memory fold integration

```python
class ConsciousnessBuffer:
    def __init__(
        self,
        capacity: int = 10000,
        cascade_prevention_threshold: float = 0.997
    )
```

#### Methods

##### `async store_experience(...) -> MatrizNode`
Store RL experience using memory fold system.

**Parameters**:
```python
async def store_experience(
    self,
    state: MatrizNode,
    action: MatrizNode,
    reward: MatrizNode,
    next_state: MatrizNode,
    done: bool = False,
    episode_id: Optional[str] = None
) -> MatrizNode
```

**Returns**: MEMORY node with stored experience

**Example**:
```python
buffer = ConsciousnessBuffer(capacity=5000)
memory_node = await buffer.store_experience(
    state=context_node,
    action=decision_node,
    reward=reward_node,
    next_state=next_context,
    done=False,
    episode_id="episode_001"
)
```

##### `async sample_batch(batch_size: int = 32) -> List[RLExperience]`
Sample batch of experiences for training.

**Parameters**:
- `batch_size`: Number of experiences to sample

**Returns**: List of RLExperience objects

##### `async get_episode_experiences(episode_id: str) -> List[RLExperience]`
Get all experiences from specific episode.

##### `async get_high_salience_experiences(threshold: float = 0.8, limit: int = 50) -> List[RLExperience]`
Get experiences with high salience for priority learning.

##### `get_buffer_metrics() -> Dict[str, Any]`
Get buffer performance metrics.

**Returns**:
```python
{
    "total_experiences": 1500,
    "buffer_utilization": 0.75,
    "cascade_prevention_rate": 0.998,
    "average_salience": 0.72,
    "total_episodes": 45,
    "memory_efficiency_trend": [0.7, 0.71, 0.73, ...],
    "fold_registry_size": 1500,
    "trace_id": "rl-buffer-abc123"
}
```

---

### ConsciousnessRewards

**Purpose**: CAUSAL node emission for multi-objective reward computation

```python
class ConsciousnessRewards:
    def __init__(self):
        # Reward weights from design specification
        self.reward_weights = {
            "coherence": 0.30,    # Temporal consciousness coherence
            "growth": 0.25,       # Learning & development
            "ethics": 0.20,       # Ethical alignment
            "creativity": 0.15,   # Creative solutions  
            "efficiency": 0.10    # Resource efficiency
        }
```

#### Methods

##### `async compute_reward(...) -> MatrizNode`
Compute multi-objective reward with constitutional constraints.

**Parameters**:
```python
async def compute_reward(
    self,
    state_node: MatrizNode,
    action_node: MatrizNode,
    next_state_node: MatrizNode,
    episode_context: Optional[Dict[str, Any]] = None
) -> MatrizNode
```

**Returns**: CAUSAL node with reward analysis

**Example**:
```python
reward_system = ConsciousnessRewards()
causal_node = await reward_system.compute_reward(
    state_node=context_node,
    action_node=decision_node,
    next_state_node=next_context,
    episode_context={"episode_length": 150}
)

# Access reward components
components = causal_node.state['reward_components']
total_reward = causal_node.state['reward_total']
constitutional_safe = causal_node.state['constitutional_safe']
```

##### `async get_reward_statistics() -> Dict[str, Any]`
Get reward system performance statistics.

**Returns**:
```python
{
    "total_rewards_computed": 2500,
    "constitutional_violations": 3,
    "average_components": {
        "coherence": 0.94,
        "growth": 0.67,
        "ethics": 0.99,
        "creativity": 0.45,
        "efficiency": 0.78,
        "total": 0.71
    },
    "recent_trend": [0.7, 0.72, 0.69, ...],
    "trace_id": "rl-rewards-def456"
}
```

---

### MultiAgentCoordination

**Purpose**: DECISION node emission for multi-agent coordination

```python
class MultiAgentCoordination:
    def __init__(self, max_agents: int = 50)
```

#### Enums

##### CoordinationStrategy
```python
class CoordinationStrategy(Enum):
    CONSENSUS = "consensus"          # Majority consensus
    HIERARCHICAL = "hierarchical"   # Leader-follower
    DEMOCRATIC = "democratic"       # Equal-weight voting
    EXPERTISE = "expertise"         # Expertise-weighted
    COLONY = "colony"               # Colony-based swarm
    HYBRID = "hybrid"               # Adaptive strategy
```

#### Methods

##### `async register_agent(...) -> bool`
Register consciousness agent for coordination.

**Parameters**:
```python
async def register_agent(
    self,
    agent_id: str,
    capabilities: List[str],
    expertise_domains: List[str],
    colony_affiliation: Optional[str] = None
) -> bool
```

**Example**:
```python
coordination = MultiAgentCoordination(max_agents=20)
success = await coordination.register_agent(
    agent_id="reasoning_agent_1",
    capabilities=["logical_reasoning", "pattern_recognition"],
    expertise_domains=["mathematics", "ethics"],
    colony_affiliation="reasoning_colony"
)
```

##### `async coordinate_decision(...) -> MatrizNode`
Coordinate multi-agent decision-making process.

**Parameters**:
```python
async def coordinate_decision(
    self,
    context_node: MatrizNode,
    decision_domain: str,
    participating_agents: Optional[List[str]] = None,
    strategy: Optional[CoordinationStrategy] = None,
    urgency_level: float = 0.5,
    timeout_seconds: float = 30.0
) -> MatrizNode
```

**Returns**: DECISION node representing coordinated decision

**Example**:
```python
coordinated_decision = await coordination.coordinate_decision(
    context_node=current_context,
    decision_domain="ethical_reasoning",
    strategy=CoordinationStrategy.EXPERTISE,
    urgency_level=0.8,
    timeout_seconds=45.0
)
```

##### `async get_coordination_metrics() -> Dict[str, Any]`
Get coordination system performance metrics.

---

### ConsciousnessMetaLearning

**Purpose**: REFLECTION node emission for meta-learning and self-improvement

```python
class ConsciousnessMetaLearning:
    def __init__(self, max_experiences: int = 1000)
```

#### Data Classes

##### LearningExperience
```python
@dataclass
class LearningExperience:
    task_id: str
    learning_trajectory: List[float]
    strategy_used: str
    context_features: Dict[str, Any]
    final_performance: float
    learning_efficiency: float
    adaptation_time: float
    consciousness_coherence: float
    ethical_alignment: float
    timestamp: datetime
```

##### MetaLearningObjective
```python
@dataclass
class MetaLearningObjective:
    objective_id: str
    name: str
    description: str
    weight: float
    current_performance: float = 0.0
    target_performance: float = 1.0
    improvement_trend: List[float] = field(default_factory=list)
```

#### Methods

##### `async record_learning_experience(...)`
Record learning experience for meta-analysis.

**Parameters**:
```python
async def record_learning_experience(
    self,
    task_id: str,
    learning_trajectory: List[float],
    strategy_used: str,
    context_node: MatrizNode,
    final_performance: float
)
```

**Example**:
```python
meta_learning = ConsciousnessMetaLearning()
await meta_learning.record_learning_experience(
    task_id="navigation_complex_maze",
    learning_trajectory=[0.1, 0.3, 0.6, 0.8, 0.95],
    strategy_used="exploration_with_memory",
    context_node=task_context,
    final_performance=0.95
)
```

##### `async generate_meta_learning_reflection(...) -> MatrizNode`
Generate meta-learning reflection with insights.

**Parameters**:
```python
async def generate_meta_learning_reflection(
    self,
    context_node: MatrizNode,
    recent_experiences: Optional[List[LearningExperience]] = None,
    strategy: Optional[MetaLearningStrategy] = None
) -> MatrizNode
```

**Returns**: REFLECTION node with meta-learning insights

**Example**:
```python
reflection_node = await meta_learning.generate_meta_learning_reflection(
    context_node=current_context,
    strategy=MetaLearningStrategy.SELF_REFLECTION
)

# Access insights
insights = reflection_node.state['meta_insights']['insights']
strategies = reflection_node.state['improvement_strategies']
evolution = reflection_node.state['consciousness_evolution']
```

## Data Structures

### MatrizNode

**MΛTRIZ Schema v1.1 Node Structure**:

```python
@dataclass
class MatrizNode:
    version: int = 1
    id: str
    type: str  # CONTEXT, DECISION, HYPOTHESIS, MEMORY, CAUSAL, REFLECTION
    labels: List[str]
    state: Dict[str, Any]
    timestamps: Dict[str, int]
    provenance: Dict[str, Any]
    links: List[Dict[str, Any]]
    evolves_to: List[str]
    triggers: List[Dict[str, Any]]
    reflections: List[Dict[str, Any]]
    embeddings: List[Any]
    evidence: List[Dict[str, Any]]
```

### ConsciousnessState

**Consciousness State Information**:

```python
@dataclass
class ConsciousnessState:
    temporal_coherence: float = 0.95
    ethical_alignment: float = 0.98
    awareness_level: float = 0.85
    complexity: float = 0.5
    urgency: float = 0.5
    confidence: float = 0.8
    salience: float = 0.7
    valence: float = 0.5  # Emotional valence
    arousal: float = 0.5  # Activation level
    novelty: float = 0.5  # Novelty detection
```

## Error Handling

### Exception Types

```python
class ConsciousnessError(Exception):
    """Base exception for consciousness-related errors"""
    pass

class CoherenceViolationError(ConsciousnessError):
    """Raised when temporal coherence falls below threshold"""
    pass

class ConstitutionalViolationError(ConsciousnessError):
    """Raised when constitutional constraints are violated"""
    pass

class MemoryCascadeError(ConsciousnessError):
    """Raised when memory cascade prevention fails"""
    pass

class CoordinationTimeoutError(ConsciousnessError):
    """Raised when multi-agent coordination times out"""
    pass
```

### Error Handling Patterns

```python
try:
    decision_node = await policy.select_action(context_node)
except CoherenceViolationError as e:
    logger.error(f"Coherence violation: {e}")
    # Fallback to safe default action
    decision_node = await policy.safe_default_action(context_node)
except ConstitutionalViolationError as e:
    logger.critical(f"Constitutional violation: {e}")
    # Trigger Guardian System intervention
    await guardian_system.intervene(context_node, e)
```

## Logging & Monitoring

### Structured Logging

All components use structured logging with consciousness context:

```python
logger.info(
    "Action selected with consciousness awareness",
    decision_confidence=0.87,
    ethical_alignment=0.99,
    temporal_coherence=0.95,
    node_id=decision_node.id,
    trace_id=self.trace_id
)
```

### Performance Monitoring

Built-in metrics collection:

```python
# Environment metrics
env_metrics = await environment.get_environment_metrics()

# Policy metrics  
policy_metrics = await policy.get_policy_metrics()

# Buffer metrics
buffer_metrics = buffer.get_buffer_metrics()

# Reward metrics
reward_stats = await rewards.get_reward_statistics()

# Coordination metrics
coord_metrics = await coordination.get_coordination_metrics()

# Meta-learning metrics
meta_metrics = await meta_learning.get_meta_learning_metrics()
```

## Configuration

### Environment Variables

```bash
# Core RL settings
LUKHAS_RL_COHERENCE_THRESHOLD=0.95
LUKHAS_RL_ETHICS_THRESHOLD=0.98
LUKHAS_RL_CASCADE_PREVENTION=0.997

# Multi-agent settings
LUKHAS_RL_MAX_AGENTS=50
LUKHAS_RL_COORDINATION_TIMEOUT=30

# Meta-learning settings
LUKHAS_RL_META_EXPERIENCES=1000
LUKHAS_RL_REFLECTION_DEPTH=3
```

### Configuration Files

```yaml
# rl_config.yaml
consciousness:
  coherence_threshold: 0.95
  ethics_threshold: 0.98
  cascade_prevention: 0.997

reward_weights:
  coherence: 0.30
  growth: 0.25  
  ethics: 0.20
  creativity: 0.15
  efficiency: 0.10

coordination:
  max_agents: 50
  default_strategy: "consensus"
  timeout_seconds: 30.0

meta_learning:
  max_experiences: 1000
  reflection_depth: 3
  objectives:
    learning_efficiency: 0.90
    adaptation_speed: 0.85
    knowledge_transfer: 0.80
```

---

**Version**: 1.0.0  
**Schema Compatibility**: MΛTRIZ v1.1  
**Python Version**: 3.8+  
**Dependencies**: PyTorch (optional), NumPy (optional)