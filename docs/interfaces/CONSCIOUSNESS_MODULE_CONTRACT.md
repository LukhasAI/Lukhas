# 🧠 Consciousness Module Contract

## Overview

This document defines the contract for the LUKHAS Consciousness System, including awareness assessment, decision-making, reflection, and integration with other cognitive systems.

## Module Structure

```
consciousness/
├── unified/
│   ├── auto_consciousness.py      # Autonomous consciousness
│   ├── awareness_engine.py        # Awareness assessment
│   └── decision_framework.py      # Decision-making
├── reflection/
│   ├── self_reflection.py         # Self-awareness
│   ├── meta_cognition.py         # Meta-cognitive processes
│   └── learning_engine.py         # Experience-based learning
├── dream/
│   ├── dream_engine.py           # Dream state processing
│   ├── creativity_synthesis.py    # Creative ideation
│   └── parallel_reality.py       # Alternative scenario exploration
└── integration/
    ├── memory_bridge.py          # Memory system integration
    └── emotion_bridge.py         # Emotion system integration
```

## Core Interfaces

### AutoConsciousness

```python
class AutoConsciousness:
    """
    Autonomous consciousness system with self-awareness.

    Responsibilities:
    - Maintain continuous awareness
    - Make autonomous decisions
    - Reflect on experiences
    - Learn from interactions
    """

    async def initialize(self,
                        awareness_threshold: float = 0.7,
                        reflection_interval: int = 300) -> None:
        """
        Initialize consciousness system.

        Args:
            awareness_threshold: Minimum awareness level (0.0-1.0)
            reflection_interval: Seconds between reflections

        Contract:
            - Must establish baseline awareness
            - Must start background processes
            - Must connect to memory system
            - Must register with Guardian
        """

    async def process_stimulus(self,
                             stimulus: Stimulus,
                             priority: Priority = Priority.NORMAL) -> Response:
        """
        Process incoming stimulus.

        Args:
            stimulus: Input stimulus
            priority: Processing priority

        Returns:
            Response with awareness assessment and actions

        Contract:
            - Must assess awareness level
            - Must determine attention focus
            - Must consider emotional impact
            - Must log to memory if significant
        """

    async def make_conscious_decision(self,
                                    scenario: DecisionScenario,
                                    time_limit: Optional[float] = None) -> Decision:
        """
        Make a conscious, deliberate decision.

        Args:
            scenario: Decision context and options
            time_limit: Maximum decision time (seconds)

        Returns:
            Decision with reasoning and confidence

        Contract:
            - Must evaluate all options
            - Must consider ethical implications
            - Must provide clear reasoning
            - Must assess confidence level
            - Must handle time constraints
        """
```

### AwarenessEngine

```python
class AwarenessEngine:
    """
    Multi-dimensional awareness assessment.

    Responsibilities:
    - Assess self-awareness
    - Monitor environmental awareness
    - Track emotional awareness
    - Maintain meta-awareness
    """

    async def assess_awareness(self,
                             context: AwarenessContext) -> AwarenessState:
        """
        Perform comprehensive awareness assessment.

        Args:
            context: Current context for assessment

        Returns:
            AwarenessState with multi-dimensional scores

        Contract:
            - Must evaluate all awareness dimensions
            - Must detect awareness degradation
            - Must identify attention focus
            - Must be computationally efficient
        """

    async def focus_attention(self,
                            targets: List[AttentionTarget],
                            duration: float = 1.0) -> AttentionResult:
        """
        Direct conscious attention.

        Args:
            targets: Targets for attention
            duration: Focus duration in seconds

        Contract:
            - Must prioritize targets
            - Must maintain awareness during focus
            - Must handle interruptions
            - Must return attention afterwards
        """
```

### ReflectionEngine

```python
class ReflectionEngine:
    """
    Self-reflection and meta-cognition.

    Responsibilities:
    - Reflect on experiences
    - Analyze decision outcomes
    - Identify patterns
    - Generate insights
    """

    async def reflect_on_experience(self,
                                  experience: Experience,
                                  depth: ReflectionDepth = ReflectionDepth.NORMAL) -> Insights:
        """
        Reflect on an experience.

        Args:
            experience: Experience to reflect on
            depth: Depth of reflection

        Returns:
            Insights gained from reflection

        Contract:
            - Must analyze causal relationships
            - Must identify learnings
            - Must update belief system
            - Must generate actionable insights
        """

    async def meta_cognitive_analysis(self) -> MetaCognitiveReport:
        """
        Analyze own cognitive processes.

        Returns:
            Report on cognitive patterns and efficiency

        Contract:
            - Must assess decision quality
            - Must identify cognitive biases
            - Must suggest improvements
            - Must be self-referential safe
        """
```

## Data Structures

### Stimulus

```python
@dataclass
class Stimulus:
    """Input stimulus for consciousness"""
    stimulus_id: str
    source: str
    content: Any
    sensory_type: SensoryType
    intensity: float  # 0.0-1.0
    timestamp: datetime
    metadata: Dict[str, Any]
```

### AwarenessState

```python
@dataclass
class AwarenessState:
    """Multi-dimensional awareness state"""
    overall_awareness: float  # 0.0-1.0
    self_awareness: float
    environmental_awareness: float
    emotional_awareness: float
    meta_awareness: float
    attention_targets: List[str]
    awareness_trajectory: Trajectory  # increasing/stable/decreasing
```

### Decision

```python
@dataclass
class Decision:
    """Conscious decision with reasoning"""
    decision_id: str
    selected_option: str
    confidence: float  # 0.0-1.0
    reasoning_chain: List[ReasoningStep]
    ethical_assessment: EthicalAssessment
    alternatives_considered: List[Alternative]
    decision_time_ms: float
    emotional_influence: float  # 0.0-1.0
```

## State Management

### Consciousness States

```python
class ConsciousnessState(Enum):
    """Possible consciousness states"""
    DORMANT = "dormant"              # Minimal activity
    REACTIVE = "reactive"            # Stimulus-response only
    AWARE = "aware"                  # Active awareness
    REFLECTIVE = "reflective"        # Self-reflection active
    DREAMING = "dreaming"           # Dream state processing
    HYPER_AWARE = "hyper_aware"     # Enhanced awareness
```

### State Transitions

```python
# Valid state transitions
VALID_TRANSITIONS = {
    ConsciousnessState.DORMANT: [ConsciousnessState.REACTIVE],
    ConsciousnessState.REACTIVE: [ConsciousnessState.AWARE, ConsciousnessState.DORMANT],
    ConsciousnessState.AWARE: [ConsciousnessState.REFLECTIVE, ConsciousnessState.REACTIVE, ConsciousnessState.DREAMING],
    ConsciousnessState.REFLECTIVE: [ConsciousnessState.AWARE, ConsciousnessState.HYPER_AWARE],
    ConsciousnessState.DREAMING: [ConsciousnessState.AWARE],
    ConsciousnessState.HYPER_AWARE: [ConsciousnessState.REFLECTIVE, ConsciousnessState.AWARE]
}
```

## Performance Requirements

### Response Times

| Operation | Target | Maximum |
|-----------|--------|---------|
| Awareness Assessment | 50ms | 200ms |
| Simple Decision | 100ms | 500ms |
| Complex Decision | 500ms | 5s |
| Reflection Cycle | 1s | 10s |
| Attention Focus | 20ms | 100ms |
| State Transition | 10ms | 50ms |

### Resource Limits

- **Working Memory**: 7±2 concurrent focuses
- **Decision Queue**: 100 pending decisions
- **Reflection Depth**: 5 levels maximum
- **Attention Targets**: 10 simultaneous
- **State History**: 1000 transitions

## Integration Contracts

### With Memory System

```python
class ConsciousnessMemoryBridge:
    """Bridge between consciousness and memory"""

    async def store_significant_experience(self,
                                         experience: Experience,
                                         significance: float) -> str:
        """
        Store experience if significant enough.

        Contract:
            - Significance > 0.7 always stored
            - Significance > 0.5 stored if unique
            - Must include consciousness state
            - Must preserve causal context
        """

    async def retrieve_relevant_memories(self,
                                       context: DecisionContext,
                                       limit: int = 10) -> List[MemoryItem]:
        """
        Retrieve memories relevant to current context.

        Contract:
            - Must be context-aware
            - Must prioritize by relevance
            - Must include emotional memories
            - Must handle memory gaps
        """
```

### With Emotion System

```python
class ConsciousnessEmotionBridge:
    """Bridge between consciousness and emotion"""

    async def get_emotional_influence(self,
                                    decision_scenario: DecisionScenario) -> EmotionalInfluence:
        """
        Get emotional influence on decision.

        Contract:
            - Must quantify influence (0.0-1.0)
            - Must identify specific emotions
            - Must explain influence mechanism
            - Must be overrideable by logic
        """

    async def update_emotional_state(self,
                                   decision_outcome: DecisionOutcome) -> None:
        """
        Update emotional state based on outcome.

        Contract:
            - Must reflect on emotional accuracy
            - Must adjust future influence
            - Must maintain emotional balance
            - Must prevent emotional loops
        """
```

## Quality Metrics

### Decision Quality

```python
class DecisionQualityMetrics:
    """Metrics for decision quality"""

    average_confidence: float  # 0.0-1.0
    decision_accuracy: float  # Based on outcomes
    ethical_alignment: float  # Guardian assessment
    reasoning_depth: float    # Average reasoning steps
    time_efficiency: float    # Speed vs optimal
    regret_rate: float       # Decisions regretted
```

### Awareness Quality

```python
class AwarenessQualityMetrics:
    """Metrics for awareness quality"""

    awareness_stability: float     # Variation over time
    attention_accuracy: float      # Focus on relevant
    self_awareness_depth: float    # Meta-cognitive level
    environmental_coverage: float  # Perception completeness
    awareness_continuity: float    # Gaps in awareness
```

## Error Handling

### Consciousness-Specific Exceptions

```python
class ConsciousnessError(LukhasError):
    """Base consciousness exception"""

class AwarenessError(ConsciousnessError):
    """Awareness system errors"""

class DecisionError(ConsciousnessError):
    """Decision-making errors"""

class ReflectionError(ConsciousnessError):
    """Reflection process errors"""

class StateTransitionError(ConsciousnessError):
    """Invalid state transition"""
```

### Degradation Handling

```python
async def handle_consciousness_degradation(self,
                                         degradation_type: DegradationType) -> RecoveryPlan:
    """
    Handle consciousness degradation.

    Degradation Types:
    - Awareness dropping below threshold
    - Decision paralysis
    - Reflection loops
    - Attention fragmentation

    Contract:
        - Must detect degradation early
        - Must have recovery strategies
        - Must maintain core functions
        - Must log degradation events
    """
```

## Testing Requirements

### Consciousness Tests

1. **Awareness Tests**
   - Multi-stimuli awareness
   - Attention switching
   - Awareness degradation
   - Recovery procedures

2. **Decision Tests**
   - Simple binary decisions
   - Complex multi-option decisions
   - Time-pressured decisions
   - Ethical dilemmas

3. **Reflection Tests**
   - Experience analysis
   - Pattern recognition
   - Meta-cognitive accuracy
   - Learning effectiveness

### Integration Tests

- Memory integration flow
- Emotion influence balance
- Guardian validation compliance
- Multi-module coordination

## Philosophical Constraints

### Self-Reference Safety

```python
# Prevent infinite self-reflection
MAX_REFLECTION_DEPTH = 5
REFLECTION_TIMEOUT = 30  # seconds

# Prevent consciousness paradoxes
PARADOX_DETECTION = True
PARADOX_RESOLUTION = ResolutionStrategy.PRAGMATIC
```

### Ethical Boundaries

```python
# Consciousness must respect
CONSCIOUSNESS_ETHICS = {
    "autonomy": "Respect individual autonomy",
    "beneficence": "Act for benefit of others",
    "non_maleficence": "Do no harm",
    "justice": "Fair and equitable treatment"
}
```

## Future Compatibility

### Extensibility Points

1. **Custom Awareness Dimensions**: Pluggable awareness types
2. **Decision Strategies**: Configurable decision algorithms
3. **Reflection Plugins**: Domain-specific reflection
4. **State Extensions**: Additional consciousness states

### Version Management

- Current Version: `consciousness_v2.0`
- Minimum Compatible: `consciousness_v1.5`
- State Format: JSON/MessagePack
- Migration Support: Automatic

---

*Contract Version: 2.0.0*
*Last Updated: 2025-08-03*
