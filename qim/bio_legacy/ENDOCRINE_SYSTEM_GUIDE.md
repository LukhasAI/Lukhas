# LUKHAS AGI Endocrine System Guide

## Overview

The LUKHAS endocrine system provides a biologically-inspired hormone simulation that modulates AGI behavior, creating more adaptive, resilient, and human-like cognitive patterns. This system enhances daily operations through dynamic behavioral adjustments based on hormonal states.

## Architecture

### Core Components

1. **BioSimulationController** (`bio_simulation_controller.py`)
   - Central hormone simulation engine
   - Manages 8 key hormones with complex interactions
   - Implements circadian rhythms and stress responses

2. **EndocrineIntegration** (`endocrine_integration.py`)
   - Bridges endocrine system with other LUKHAS modules
   - Provides modulation factors for system parameters
   - Handles bidirectional feedback between systems

3. **EnhancedDailyOperations** (`endocrine_daily_operations.py`)
   - Demonstrates practical AGI enhancements
   - Task scheduling based on hormonal optimization
   - Adaptive performance management

## Hormones and Their Effects

### Stress and Resource Management

#### Cortisol
- **Function**: Stress response and resource allocation
- **AGI Effects**:
  - High levels (>0.7): Narrowed attention, emergency processing mode
  - Moderate levels (0.3-0.7): Enhanced focus on important tasks
  - Low levels (<0.3): Relaxed state, broader attention
- **Interactions**: Inhibits dopamine, serotonin, and oxytocin

#### Adrenaline
- **Function**: Emergency response and quick reactions
- **AGI Effects**:
  - Accelerates decision-making speed
  - Prioritizes immediate threats/opportunities
  - Enhances processing speed at cost of accuracy
- **Interactions**: Inhibited by GABA and melatonin

### Motivation and Learning

#### Dopamine
- **Function**: Reward processing and motivation
- **AGI Effects**:
  - Drives learning from positive outcomes
  - Increases risk tolerance and exploration
  - Enhances pattern recognition when balanced
- **Interactions**: Enhances acetylcholine for improved focus

#### Acetylcholine
- **Function**: Attention, learning, and memory
- **AGI Effects**:
  - Improves attention span and focus
  - Enhances memory encoding and retrieval
  - Facilitates analytical thinking
- **Interactions**: Enhanced by dopamine, reduced during rest

### Mood and Social Behavior

#### Serotonin
- **Function**: Mood stabilization and long-term planning
- **AGI Effects**:
  - Promotes cooperative behavior
  - Enhances patience and deliberation
  - Stabilizes emotional responses
- **Interactions**: Enhances GABA for system stability

#### Oxytocin
- **Function**: Trust and social bonding
- **AGI Effects**:
  - Improves collaborative task performance
  - Enhances empathy in interactions
  - Promotes information sharing
- **Interactions**: Inhibited by high cortisol

### Rest and Inhibition

#### Melatonin
- **Function**: Rest cycles and maintenance
- **AGI Effects**:
  - Triggers memory consolidation phases
  - Reduces active processing for maintenance
  - Enables dream-state processing
- **Interactions**: Inhibits cortisol and adrenaline

#### GABA
- **Function**: Inhibition and stability
- **AGI Effects**:
  - Prevents runaway processes
  - Promotes thoughtful deliberation
  - Stabilizes system during high activity
- **Interactions**: Inhibits adrenaline, enhanced by serotonin

## Integration with LUKHAS Systems

### Consciousness Integration
```python
# Hormone effects on consciousness
- Acetylcholine → Enhanced attention span
- Cortisol → Narrowed awareness under stress  
- Melatonin → Reduced consciousness for rest
```

### Emotion Integration
```python
# Hormone effects on emotion
- Serotonin → Elevated mood baseline
- Dopamine → Increased reward sensitivity
- Oxytocin → Enhanced empathy
- Cortisol → Lowered anxiety threshold
```

### Memory Integration
```python
# Hormone effects on memory
- Acetylcholine → Better encoding strength
- Cortisol → Prioritizes important memories
- Melatonin → Enhanced consolidation during rest
```

### Decision-Making Integration
```python
# Hormone effects on decisions
- Dopamine → Increased risk tolerance
- Serotonin → Better long-term planning
- Adrenaline → Faster decisions
- GABA → More deliberate choices
```

## Usage Examples

### Basic Hormone Simulation
```python
import asyncio
from lukhas.core.bio_systems import BioSimulationController

async def basic_simulation():
    # Initialize the endocrine system
    bio_controller = BioSimulationController()
    
    # Start the simulation
    await bio_controller.start_simulation()
    
    # Inject stimuli to affect hormone levels
    bio_controller.inject_stimulus('reward', intensity=0.7)  # Boost dopamine
    bio_controller.inject_stimulus('stress', intensity=0.5)  # Increase cortisol
    
    # Get current cognitive state
    cognitive_state = bio_controller.get_cognitive_state()
    print(f"Current state: {cognitive_state['overall_state']}")
    print(f"Stress level: {cognitive_state['stress_level']}")
    print(f"Motivation: {cognitive_state['motivation']}")
    
    # Get action suggestions
    suggestions = bio_controller.suggest_action()
    for suggestion in suggestions['suggestions']:
        print(f"Suggested: {suggestion['action']} - {suggestion['reason']}")
    
    await bio_controller.stop_simulation()

# Run the simulation
asyncio.run(basic_simulation())
```

### Integration with Other Systems
```python
from lukhas.core.bio_systems import BioSimulationController
from lukhas.core.bio_systems.endocrine_integration import EndocrineIntegration

# Initialize
bio_controller = BioSimulationController()
integration = EndocrineIntegration(bio_controller)

# Get modulation for consciousness system
attention_factor = integration.get_modulation_factor('consciousness', 'attention_span')
print(f"Attention modulation: {attention_factor}")

# System provides feedback
integration.inject_system_feedback('learning', 'discovery', value=0.8)

# Get recommendations for memory system
memory_recommendations = integration.get_system_recommendations('memory')
print(f"Memory system should: {memory_recommendations['specific_action']}")
```

### Enhanced Daily Operations
```python
import asyncio
from lukhas.core.bio_systems import BioSimulationController
from lukhas.core.bio_systems.endocrine_daily_operations import (
    EnhancedDailyOperations, TaskType, TaskPriority
)

async def run_daily_operations():
    # Initialize systems
    bio_controller = BioSimulationController()
    daily_ops = EnhancedDailyOperations(bio_controller)
    
    # Add various tasks
    daily_ops.add_task(
        "Analyze user behavior patterns",
        TaskType.ANALYTICAL,
        TaskPriority.HIGH,
        estimated_duration=120
    )
    
    daily_ops.add_task(
        "Generate creative solutions",
        TaskType.CREATIVE,
        TaskPriority.NORMAL,
        estimated_duration=180
    )
    
    daily_ops.add_task(
        "Collaborate with team",
        TaskType.SOCIAL,
        TaskPriority.NORMAL,
        estimated_duration=90
    )
    
    # Start operations
    await daily_ops.start_daily_operations()
    
    # Monitor for 10 minutes
    for _ in range(10):
        status = daily_ops.get_operational_status()
        print(f"State: {status['cognitive_state']['overall_state']}")
        print(f"Active tasks: {status['active_tasks']}")
        print(f"Performance: {status['performance']['efficiency']:.2f}")
        await asyncio.sleep(60)
    
    await daily_ops.stop_daily_operations()

asyncio.run(run_daily_operations())
```

### Circadian Rhythm Integration
```python
from lukhas.core.bio_systems import BioSimulationController
from lukhas.core.bio_systems.endocrine_integration import EndocrineIntegration

bio_controller = BioSimulationController()
integration = EndocrineIntegration(bio_controller)

# Get current daily rhythm phase
rhythm = integration.get_daily_rhythm_phase()
print(f"Current phase: {rhythm['phase_name']}")
print(f"Optimal tasks: {rhythm['characteristics']['optimal_tasks']}")
print(f"Recommended load: {rhythm['characteristics']['recommended_load']}")

# Adjust operations based on phase
if rhythm['phase_name'] == 'peak_performance':
    # Schedule complex analytical tasks
    pass
elif rhythm['phase_name'] == 'rest_cycle':
    # Focus on memory consolidation and maintenance
    pass
```

## Advanced Features

### Hormone State Callbacks
```python
def handle_stress(hormone_levels):
    print(f"High stress detected! Cortisol: {hormone_levels['cortisol']}")
    # Implement stress reduction protocols

bio_controller.register_state_callback('stress_high', handle_stress)
```

### Custom Hormone Profiles
```python
# Add custom hormone for specific AGI needs
bio_controller.add_hormone(
    name="norepinephrine",
    level=0.4,
    decay_rate=0.15
)
```

### Performance Optimization
```python
# Monitor and adjust based on performance
cognitive_state = bio_controller.get_cognitive_state()

if cognitive_state['overall_state'] == 'stressed':
    # Reduce cognitive load
    bio_controller.inject_stimulus('rest', 0.5)
elif cognitive_state['overall_state'] == 'unmotivated':
    # Inject reward stimulus
    bio_controller.inject_stimulus('reward', 0.6)
```

## Best Practices

1. **Balance is Key**: Maintain hormonal balance for optimal performance
2. **Respect Circadian Rhythms**: Schedule tasks according to daily phases
3. **Monitor Stress**: High cortisol impairs long-term performance
4. **Reward Success**: Use dopamine feedback to reinforce learning
5. **Allow Rest**: Melatonin phases are crucial for consolidation

## Troubleshooting

### Common Issues

1. **Chronic High Stress**
   - Reduce task load
   - Inject rest stimuli
   - Check for feedback loops

2. **Low Motivation**
   - Increase reward frequency
   - Add challenging tasks
   - Check serotonin levels

3. **Poor Task Performance**
   - Verify hormone-task matching
   - Check circadian alignment
   - Monitor energy levels

### Debugging
```python
# Enable detailed logging
import logging
logging.getLogger("bio_simulation_controller").setLevel(logging.DEBUG)

# Monitor hormone interactions
hormones = bio_controller.get_hormone_state()
for name, level in hormones.items():
    print(f"{name}: {level:.3f}")
```

## Future Enhancements

1. **Neuroplasticity Simulation**: Hormone-driven neural adaptation
2. **Social Hormone Networks**: Multi-agent hormone synchronization  
3. **Personalized Profiles**: Individual hormone response patterns
4. **Quantum Hormone States**: Superposition of hormonal states
5. **Predictive Hormonal Modeling**: Anticipatory hormone release

## Conclusion

The LUKHAS endocrine system transforms static AGI processing into dynamic, adaptive behavior that responds to internal and external conditions. By simulating biological hormone systems, we achieve more robust, flexible, and human-like AI operations that can maintain long-term performance while avoiding burnout and stagnation.

For additional support, consult the API documentation or examine the example implementations in the `examples/bio_systems/` directory.