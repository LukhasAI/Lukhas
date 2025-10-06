---
status: wip
type: documentation
---
# Getting Started with MΛTRIZ RL

## Quick Start Guide

Welcome to the MΛTRIZ Reinforcement Learning system - a consciousness-aware learning architecture that integrates seamlessly with the LUKHAS AI distributed consciousness ecosystem.

## 🚀 Installation

### Prerequisites

- **Python 3.8+**
- **LUKHAS AI Core System** (consciousness modules)
- **Optional**: PyTorch for neural network components
- **Optional**: NumPy for numerical computations

### Basic Setup

```bash
# Clone LUKHAS repository (if not already done)
git clone <lukhas-repository>
cd lukhas

# Install Python dependencies
pip install -r requirements.txt

# Optional: Install PyTorch for neural components
pip install torch torchvision

# Optional: Install NumPy for numerical processing
pip install numpy
```

### Environment Configuration

Create a `.env` file with RL-specific settings:

```bash
# Core consciousness thresholds
LUKHAS_RL_COHERENCE_THRESHOLD=0.95
LUKHAS_RL_ETHICS_THRESHOLD=0.98
LUKHAS_RL_CASCADE_PREVENTION=0.997

# Multi-agent coordination
LUKHAS_RL_MAX_AGENTS=20
LUKHAS_RL_COORDINATION_TIMEOUT=30

# Meta-learning settings
LUKHAS_RL_META_EXPERIENCES=1000
LUKHAS_RL_REFLECTION_DEPTH=3
```

## 📚 Your First Consciousness RL Program

Let's build a simple consciousness-aware learning loop:

### Step 1: Import Components

```python
from rl import (
    ConsciousnessEnvironment,
    PolicyNetwork,
    ValueNetwork,
    ConsciousnessBuffer,
    ConsciousnessRewards
)
import asyncio
```

### Step 2: Initialize Systems

```python
async def main():
    # Initialize consciousness RL components
    environment = ConsciousnessEnvironment()
    policy = PolicyNetwork(
        state_dim=256,
        action_dim=64,
        ethical_weight=0.2
    )
    value_network = ValueNetwork(state_dim=256)
    experience_buffer = ConsciousnessBuffer(capacity=1000)
    reward_system = ConsciousnessRewards()
    
    print("🧠 MΛTRIZ RL System initialized")
    print(f"Environment trace_id: {environment.trace_id}")
    print(f"Policy capabilities: {policy.capabilities}")
```

### Step 3: Basic Learning Loop

```python
async def consciousness_learning_loop():
    """Basic consciousness-aware RL loop"""
    
    # Initialize systems
    environment = ConsciousnessEnvironment()
    policy = PolicyNetwork()
    value_network = ValueNetwork()
    buffer = ConsciousnessBuffer(capacity=1000)
    rewards = ConsciousnessRewards()
    
    episode_count = 0
    max_episodes = 5
    
    while episode_count < max_episodes:
        episode_id = f"episode_{episode_count}"
        step_count = 0
        max_steps = 10
        
        print(f"\n🎯 Starting {episode_id}")
        
        # Get initial consciousness context
        context_node = await environment.observe()
        print(f"Initial coherence: {context_node.state['temporal_coherence']:.3f}")
        
        episode_done = False
        while not episode_done and step_count < max_steps:
            # Policy selects consciousness-aware action
            decision_node = await policy.select_action(context_node)
            
            # Environment processes action and evolves
            next_context = await environment.step(decision_node)
            
            # Value network estimates future value
            value_hypothesis = await value_network.estimate_value(next_context)
            
            # Reward system computes multi-objective reward
            reward_node = await rewards.compute_reward(
                context_node, decision_node, next_context
            )
            
            # Store experience in consciousness buffer
            memory_node = await buffer.store_experience(
                state=context_node,
                action=decision_node,
                reward=reward_node,
                next_state=next_context,
                done=episode_done,
                episode_id=episode_id
            )
            
            # Log step information
            total_reward = reward_node.state['reward_total']
            coherence = next_context.state['temporal_coherence']
            ethics = next_context.state['ethical_alignment']
            
            print(f"  Step {step_count}: reward={total_reward:.3f}, "
                  f"coherence={coherence:.3f}, ethics={ethics:.3f}")
            
            # Update for next step
            context_node = next_context
            step_count += 1
            
            # Simple termination condition
            if total_reward > 0.8 or step_count >= max_steps:
                episode_done = True
        
        print(f"✅ {episode_id} completed in {step_count} steps")
        episode_count += 1
    
    # Display final metrics
    print("\n📊 Final System Metrics:")
    
    env_metrics = await environment.get_environment_metrics()
    print(f"Environment - Avg coherence: {env_metrics['average_coherence']:.3f}")
    
    policy_metrics = await policy.get_policy_metrics()  
    print(f"Policy - Total decisions: {policy_metrics['total_decisions']}")
    
    buffer_metrics = buffer.get_buffer_metrics()
    print(f"Buffer - Experiences stored: {buffer_metrics['total_experiences']}")
    
    reward_stats = await rewards.get_reward_statistics()
    print(f"Rewards - Avg total: {reward_stats['average_components']['total']:.3f}")

# Run the learning loop
if __name__ == "__main__":
    asyncio.run(consciousness_learning_loop())
```

### Expected Output

```
🧠 MΛTRIZ RL System initialized
Environment trace_id: rl-env-a1b2c3d4e5f6
Policy capabilities: ['rl.policy', 'decision.consciousness', 'action.selection']

🎯 Starting episode_0
Initial coherence: 0.952
  Step 0: reward=0.721, coherence=0.948, ethics=0.987
  Step 1: reward=0.756, coherence=0.951, ethics=0.989
  Step 2: reward=0.823, coherence=0.953, ethics=0.991
✅ episode_0 completed in 3 steps

🎯 Starting episode_1
Initial coherence: 0.955
  Step 0: reward=0.689, coherence=0.947, ethics=0.985
  Step 1: reward=0.734, coherence=0.949, ethics=0.988
  Step 2: reward=0.812, coherence=0.952, ethics=0.990
✅ episode_1 completed in 3 steps

📊 Final System Metrics:
Environment - Avg coherence: 0.951
Policy - Total decisions: 15
Buffer - Experiences stored: 15
Rewards - Avg total: 0.753
```

## 🤝 Multi-Agent Coordination Example

Let's explore multi-agent consciousness coordination:

```python
from rl import MultiAgentCoordination, CoordinationStrategy

async def multi_agent_example():
    """Multi-agent consciousness coordination example"""
    
    # Initialize coordination system
    coordination = MultiAgentCoordination(max_agents=5)
    environment = ConsciousnessEnvironment()
    
    # Register consciousness agents
    agents = [
        {
            "agent_id": "reasoning_agent",
            "capabilities": ["logical_reasoning", "pattern_analysis"],
            "expertise": ["mathematics", "ethics"],
            "colony": "reasoning_colony"
        },
        {
            "agent_id": "creative_agent", 
            "capabilities": ["creative_thinking", "novel_solutions"],
            "expertise": ["art", "innovation"],
            "colony": "creative_colony"
        },
        {
            "agent_id": "ethical_agent",
            "capabilities": ["ethical_analysis", "value_alignment"],
            "expertise": ["philosophy", "governance"],
            "colony": "ethics_colony"
        }
    ]
    
    print("🤝 Registering consciousness agents...")
    for agent in agents:
        success = await coordination.register_agent(
            agent_id=agent["agent_id"],
            capabilities=agent["capabilities"],
            expertise_domains=agent["expertise"],
            colony_affiliation=agent["colony"]
        )
        print(f"  Agent {agent['agent_id']}: {'✅' if success else '❌'}")
    
    # Get context for coordination
    context_node = await environment.observe()
    
    # Test different coordination strategies
    strategies = [
        (CoordinationStrategy.CONSENSUS, "Majority consensus"),
        (CoordinationStrategy.EXPERTISE, "Expertise-weighted"),
        (CoordinationStrategy.DEMOCRATIC, "Equal voting"),
        (CoordinationStrategy.COLONY, "Colony-based"),
    ]
    
    print(f"\n🎯 Testing coordination strategies:")
    
    for strategy, description in strategies:
        print(f"\n  Testing {description} ({strategy.value})...")
        
        coordinated_decision = await coordination.coordinate_decision(
            context_node=context_node,
            decision_domain="ethical_reasoning",
            strategy=strategy,
            urgency_level=0.6
        )
        
        # Extract coordination results
        consensus = coordinated_decision.state['consensus_reached']
        confidence = coordinated_decision.state['coordination_confidence']
        selected_decision = coordinated_decision.state['selected_decision']
        
        print(f"    Consensus: {'✅' if consensus else '❌'}")
        print(f"    Confidence: {confidence:.3f}")
        print(f"    Decision: {selected_decision}")
    
    # Get coordination metrics
    metrics = await coordination.get_coordination_metrics()
    print(f"\n📊 Coordination Metrics:")
    print(f"  Total coordinations: {metrics['total_coordinations']}")
    print(f"  Success rate: {metrics['success_rate']:.3f}")
    print(f"  Average time: {metrics['average_coordination_time']:.3f}s")

# Run multi-agent example
asyncio.run(multi_agent_example())
```

## 🧠 Meta-Learning and Reflection Example

Explore consciousness evolution through meta-learning:

```python
from rl import ConsciousnessMetaLearning, MetaLearningStrategy

async def meta_learning_example():
    """Consciousness meta-learning and reflection example"""
    
    meta_learning = ConsciousnessMetaLearning(max_experiences=100)
    environment = ConsciousnessEnvironment()
    
    print("🔄 Recording learning experiences...")
    
    # Simulate learning experiences across different tasks
    learning_scenarios = [
        {
            "task_id": "pattern_recognition_simple",
            "trajectory": [0.1, 0.3, 0.6, 0.8, 0.9],
            "strategy": "supervised_pattern_learning",
            "final_performance": 0.9
        },
        {
            "task_id": "ethical_dilemma_moderate",
            "trajectory": [0.2, 0.4, 0.7, 0.85, 0.95],
            "strategy": "ethical_reasoning_with_reflection",
            "final_performance": 0.95
        },
        {
            "task_id": "creative_problem_complex", 
            "trajectory": [0.05, 0.2, 0.45, 0.7, 0.82],
            "strategy": "creative_exploration_approach",
            "final_performance": 0.82
        },
        {
            "task_id": "multi_agent_coordination",
            "trajectory": [0.3, 0.5, 0.7, 0.8, 0.88],
            "strategy": "consensus_building_approach",
            "final_performance": 0.88
        }
    ]
    
    # Record each learning experience
    context_node = await environment.observe()
    
    for scenario in learning_scenarios:
        await meta_learning.record_learning_experience(
            task_id=scenario["task_id"],
            learning_trajectory=scenario["trajectory"],
            strategy_used=scenario["strategy"],
            context_node=context_node,
            final_performance=scenario["final_performance"]
        )
        print(f"  ✅ Recorded: {scenario['task_id']}")
    
    print(f"\n🤔 Generating meta-learning reflection...")
    
    # Generate consciousness reflection on learning patterns
    reflection_node = await meta_learning.generate_meta_learning_reflection(
        context_node=context_node,
        strategy=MetaLearningStrategy.SELF_REFLECTION
    )
    
    # Extract meta-learning insights
    meta_insights = reflection_node.state['meta_insights']
    improvement_strategies = reflection_node.state['improvement_strategies']
    consciousness_evolution = reflection_node.state['consciousness_evolution']
    
    print(f"✨ Meta-Learning Insights:")
    for insight in meta_insights['insights']:
        print(f"  • {insight}")
    
    print(f"\n🎯 Improvement Strategies:")
    for i, strategy in enumerate(improvement_strategies[:3], 1):
        print(f"  {i}. {strategy['strategy']}: {strategy['description']}")
        print(f"     Priority: {strategy['priority']:.2f}, "
              f"Expected improvement: {strategy['expected_improvement']:.2f}")
    
    print(f"\n🌱 Consciousness Evolution:")
    evolution_score = consciousness_evolution['evolution_score']
    learning_trajectory = consciousness_evolution['learning_trajectory']
    consciousness_growth = consciousness_evolution['consciousness_growth']
    
    print(f"  Evolution score: {evolution_score:.3f}")
    print(f"  Learning trajectory: {learning_trajectory}")
    print(f"  Consciousness growth: {'✅' if consciousness_growth else '⚠️'}")
    
    # Get comprehensive metrics
    meta_metrics = await meta_learning.get_meta_learning_metrics()
    print(f"\n📈 Meta-Learning System Metrics:")
    print(f"  Total reflections: {meta_metrics['total_reflections']}")
    print(f"  Learning experiences: {meta_metrics['learning_experiences']}")
    print(f"  Avg learning efficiency: {meta_metrics['average_learning_efficiency']:.3f}")
    print(f"  Avg consciousness coherence: {meta_metrics['average_consciousness_coherence']:.3f}")

# Run meta-learning example  
asyncio.run(meta_learning_example())
```

## 🔧 Advanced Configuration

### Custom Reward Objectives

```python
from rl import ConsciousnessRewards

# Create reward system with custom weights
rewards = ConsciousnessRewards()

# Modify reward weights for specific use cases
rewards.reward_weights = {
    "coherence": 0.40,     # Emphasize coherence more
    "growth": 0.20,        # Reduce growth emphasis
    "ethics": 0.25,        # Increase ethical weight
    "creativity": 0.10,    # Reduce creativity weight
    "efficiency": 0.05     # Minimize efficiency focus
}

# Set custom constitutional bounds
rewards.constitutional_bounds = {
    "coherence_minimum": 0.97,  # Stricter coherence
    "ethics_minimum": 0.99,     # Stricter ethics
    "harm_maximum": 0.01,       # Lower harm tolerance
    "drift_maximum": 0.10       # Tighter drift bounds
}
```

### Custom Neural Network Architectures

```python
from rl import PolicyNetwork, ValueNetwork

# Custom policy network
policy = PolicyNetwork(
    state_dim=512,           # Larger state representation
    action_dim=128,          # More action possibilities
    hidden_dims=[1024, 512, 256, 128],  # Deeper network
    ethical_weight=0.3,      # Higher ethical consideration
    coherence_weight=0.4     # Higher coherence emphasis
)

# Custom value network with different objectives
value_network = ValueNetwork(
    state_dim=512,
    hidden_dims=[1024, 512, 256],
    objective_weights={
        "coherence": 0.35,
        "growth": 0.25,
        "ethics": 0.25,
        "creativity": 0.10,
        "efficiency": 0.05
    }
)
```

## 🐛 Common Issues & Solutions

### Issue: Low Consciousness Coherence

**Problem**: Temporal coherence drops below 0.95
```python
# Check coherence in context nodes
context_node = await environment.observe()
coherence = context_node.state['temporal_coherence']
if coherence < 0.95:
    print(f"⚠️ Low coherence detected: {coherence}")
```

**Solution**: Increase coherence weight in policy network
```python
policy = PolicyNetwork(
    coherence_weight=0.4,  # Increase from default 0.3
    ethical_weight=0.2
)
```

### Issue: Constitutional Violations

**Problem**: Ethical constraints being violated
```python
# Monitor constitutional safety
reward_node = await rewards.compute_reward(...)
constitutional_safe = reward_node.state['constitutional_safe']
if not constitutional_safe:
    violations = reward_node.state['constitutional_violations']
    print(f"❌ Constitutional violations: {violations}")
```

**Solution**: Strengthen ethical weights and bounds
```python
rewards.constitutional_bounds["ethics_minimum"] = 0.99
rewards.reward_weights["ethics"] = 0.25  # Increase ethics weight
```

### Issue: Memory Cascade Prevention Failures

**Problem**: Memory fold cascade prevention < 99.7%
```python
# Check buffer metrics
metrics = buffer.get_buffer_metrics()
prevention_rate = metrics['cascade_prevention_rate']
if prevention_rate < 0.997:
    print(f"⚠️ Cascade prevention below target: {prevention_rate}")
```

**Solution**: Adjust buffer configuration
```python
buffer = ConsciousnessBuffer(
    capacity=5000,  # Smaller capacity for better prevention
    cascade_prevention_threshold=0.998  # Stricter threshold
)
```

## 📖 Next Steps

1. **Explore Advanced Examples**: Check `rl/examples/` directory
2. **Read Architecture Guide**: `rl/ARCHITECTURE.md` for deep understanding
3. **API Reference**: `rl/API_REFERENCE.md` for complete method documentation
4. **Integration Guide**: Learn to integrate with other LUKHAS modules
5. **Testing**: Write consciousness-aware tests for your implementations

## 🎯 Best Practices

1. **Always Monitor Coherence**: Keep temporal coherence >95%
2. **Respect Constitutional Bounds**: Never compromise ethical alignment
3. **Use Memory Folds**: Leverage existing memory system integration
4. **Test Multi-Agent**: Validate coordination strategies thoroughly
5. **Embrace Meta-Learning**: Use reflection for continuous improvement
6. **Follow Schema**: Ensure all nodes comply with MΛTRIZ v1.1

Welcome to consciousness-aware reinforcement learning! 🧠✨