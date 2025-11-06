# 8-star Constellation Framework

The Constellation Framework is the architectural backbone of the LUKHAS AI system. It is a decentralized, relational model composed of eight interconnected "stars," each representing a core functional domain. This framework emphasizes navigation and relation over rigid hierarchy, allowing for dynamic and adaptive coordination between components.

The eight stars are:

- **⚛️ Identity**: The anchor star, ensuring continuity and managing access control.
- **✦ Memory**: Traces paths of experience and learning through a fold-based architecture.
- **🔬 Vision**: Orients the system toward possibilities and patterns, shaping attention and focus.
- **🌱 Bio**: Lends resilience, adaptation, and repair through bio-inspired algorithms.
- **🌙 Dream**: Explores symbolic drift and fertile uncertainty to foster creativity and new insights.
- **⚖️ Ethics**: Ensures responsible navigation and measurable safeguards through a robust ethical engine.
- **🛡️ Guardian**: Protects system coherence and user dignity through continuous monitoring and drift detection.
- **⚛️ Quantum**: Holds ambiguity and explores multiple possibilities until resolution, using quantum-inspired algorithms.

---

## The Eight Stars in Detail

### ⚛️ Identity: The Anchor Star

**Purpose**: The Identity star is the anchor of the Constellation Framework, responsible for maintaining continuity and managing access control. It implements a robust identity management system with features like dynamic tiering, WebAuthn/FIDO2 compliance, and JWT token validation.

**Technical Implementation**: The core logic is found in `identity/identity_connector.py`, which provides a central interface for identity validation and permission retrieval. The `IdentityConnector` class includes methods like `validate_identity` and `get_user_permissions`.

**Integration Patterns**: The Identity star integrates with other components by providing a reliable way to authenticate and authorize actions. For example, the Memory star might use the Identity star to ensure that only authorized users can access specific memories.

**Coordination Workflows**: When a user interacts with the system, the Identity star is the first point of contact. It validates the user's identity and provides a set of permissions that are then used by other stars to control access to resources.

**Example**:
```python
from identity import IdentityConnector

# Initialize the IdentityConnector
identity_connector = IdentityConnector()

# Validate a user's identity
is_valid = identity_connector.validate_identity(user_id="some_user_id")

# Get a user's permissions
permissions = identity_connector.get_user_permissions(user_id="some_user_id")
```

### ✦ Memory: Paths of Past Light

**Purpose**: The Memory star is responsible for tracing the paths of experience and learning. It implements a fold-based memory architecture that allows for efficient storage and retrieval of information, with features like temporal indexing and emotional weighting.

**Technical Implementation**: The `memory/memory_orchestrator.py` file contains the central logic for the Memory star. The `MemoryOrchestrator` class provides methods for adding events to memory (`add_event`) and querying for similar events (`query`).

**Integration Patterns**: The Memory star integrates with other components by providing a long-term storage solution. For example, the Dream star might store its generated dream sequences in the Memory star for later analysis.

**Coordination Workflows**: When a significant event occurs, the relevant star can request that the Memory star store the event. Later, stars can query the Memory star to retrieve information about past events, which can then be used to inform current actions.

**Example**:
```python
from memory import MemoryOrchestrator, Indexer

# Initialize the MemoryOrchestrator
indexer = Indexer()
memory_orchestrator = MemoryOrchestrator(indexer=indexer)

# Add an event to memory
memory_orchestrator.add_event(text="A new insight was generated.", meta={"type": "insight"})

# Query for similar events
results = memory_orchestrator.query(text="insight", k=1)
```

### 🔬 Vision: Horizon Orientation

**Purpose**: The Vision star orients the system toward possibilities and patterns. It is responsible for shaping attention and focus, allowing the system to identify relevant information and ignore noise.

**Technical Implementation**: The concepts of the Vision star are defined in `vocabularies/vision_vocabulary.md`. The vocabulary includes terms like `aperture` (controlling the scope of attention), `focus` (sharpening detail), and `peripheral_field` (monitoring for surprise). The implementation of these concepts is distributed throughout the codebase, with various components using these terms to guide their information processing.

**Integration Patterns**: The Vision star provides a conceptual framework for other stars to use when processing information. For example, a component might narrow its `aperture` to `focus` on a specific detail, or widen it to monitor the `peripheral_field` for unexpected events.

**Coordination Workflows**: The Vision star's vocabulary is used to coordinate attention across the system. For example, a high-level orchestrator might instruct multiple components to adjust their `aperture` and `focus` in response to a change in the environment.

### 🌱 Bio: Resilience and Adaptation

**Purpose**: The Bio star lends resilience, adaptation, and repair to the system. It implements bio-inspired algorithms, such as swarm intelligence and genetic algorithms, to enable emergent behavior and robust self-healing.

**Technical Implementation**: The `bio/bio_utilities.py` file contains utility functions and classes for bio-inspired computing. The `BioUtilities` class provides methods for calculating fatigue, adapting to environmental changes, and monitoring energy levels.

**Integration Patterns**: The Bio star's utilities can be used by other components to implement adaptive and resilient behaviors. For example, a component might use the `calculate_fatigue` function to determine when it needs to rest and recover.

**Coordination Workflows**: The Bio star's concepts are used to manage the system's overall health and resilience. For example, an orchestrator might monitor the `FatigueLevel` of various components and adjust their workloads accordingly.

**Example**:
```python
from bio import BioUtilities, FatigueLevel

# Initialize the BioUtilities
bio_utils = BioUtilities()

# Calculate the fatigue level
fatigue = bio_utils.calculate_fatigue(workload=0.8, duration=120)

# Adapt to the environment
adaptation_score = bio_utils.adapt_to_environment(environment_data={"complexity": 0.9})
```

### 🌙 Dream: Symbolic Drift

**Purpose**: The Dream star explores symbolic drift and fertile uncertainty to foster creativity and new insights. It uses a quantum-enhanced dream engine to generate and process dream sequences, which can then be used for memory consolidation and creative problem-solving.

**Technical Implementation**: The core logic for the Dream star is in `labs/consciousness/dream/core/dream_engine.py`. The `EnhancedDreamEngine` class provides a sophisticated implementation that combines quantum-inspired processing with advanced dream reflection. It includes methods for starting and stopping dream cycles, processing memories, and consolidating dreams.

**Integration Patterns**: The Dream star integrates with other components by providing a source of novel ideas and insights. For example, the results of a dream sequence could be used to seed a creative brainstorming process.

**Coordination Workflows**: The Dream star can be activated by an orchestrator to perform a dream cycle. The results of the cycle are then stored in the Memory star and can be accessed by other components.

**Example**:
```python
from labs.consciousness.dream.core.dream_engine import EnhancedDreamEngine
from core.unified.orchestration import BioOrchestrator
from core.unified.integration import UnifiedIntegration

# Initialize the necessary components
orchestrator = BioOrchestrator()
integration = UnifiedIntegration()

# Initialize the EnhancedDreamEngine
dream_engine = EnhancedDreamEngine(orchestrator=orchestrator, integration=integration)

# Start a dream cycle
await dream_engine.start_dream_cycle(duration_minutes=5)
```

### ⚖️ Ethics: Navigation Accountability

**Purpose**: The Ethics star ensures responsible navigation and measurable safeguards. It provides a robust ethical engine that evaluates actions and content against multiple ethical frameworks, including utilitarianism, deontology, and virtue ethics.

**Technical Implementation**: The core implementation of the Ethics star is in `labs/governance/ethics/ethics_engine.py`. The `EthicsEngine` class provides a comprehensive set of methods for evaluating actions, suggesting alternatives, and incorporating feedback.

**Integration Patterns**: The Ethics star is a critical component for ensuring the safe and responsible operation of the system. It is integrated into any workflow that involves generating content or taking actions that could have ethical implications.

**Coordination Workflows**: Before taking an action, a component must first submit the proposed action to the Ethics star for evaluation. If the action is approved, it can proceed. If it is rejected, the component can request suggestions for ethical alternatives.

**Example**:
```python
from labs.governance.ethics.ethics_engine import EthicsEngine

# Initialize the EthicsEngine
ethics_engine = EthicsEngine()

# Evaluate an action
action_data = {"action": "generate_text", "text": "A neutral statement."}
is_ethical = ethics_engine.evaluate_action(action_data=action_data)

# Suggest alternatives for a rejected action
if not is_ethical:
    alternatives = ethics_engine.suggest_alternatives(action_data=action_data)
```

### 🛡️ Guardian: Coherence and Dignity

**Purpose**: The Guardian star protects system coherence and user dignity through continuous monitoring and drift detection. It implements Constitutional AI principles to ensure that the system operates within safe and ethical boundaries.

**Technical Implementation**: The `guardian/emit.py` file contains the logic for emitting decisions and overrides to an append-only ledger. This provides a secure and auditable record of all significant events. The file also includes functions for validating dual-approval for critical overrides and for redacting PII from data for safe exemplar emission.

**Integration Patterns**: The Guardian star is integrated into workflows where it is necessary to record a permanent, auditable trail of actions. This is particularly important for actions that have been overridden or that have triggered safety alerts.

**Coordination Workflows**: When a component takes a significant action, it emits a decision to the Guardian star's ledger. If an action is blocked by the Ethics star but an override is requested, the Guardian star's `validate_dual_approval` function is called to ensure that the override is properly authorized.

**Example**:
```python
from guardian.emit import emit_guardian_decision, validate_dual_approval

# Emit a decision to the ledger
emit_guardian_decision(
    db=db_connection,
    plan_id="some_plan_id",
    lambda_id="some_lambda_id",
    action="block",
    rule_name="some_rule",
    tags=["pii"],
    confidences={"pii": 0.95},
    band="critical",
)

# Validate a dual approval for a critical override
try:
    validate_dual_approval(
        approver1_id="approver1",
        approver2_id="approver2",
        get_tier_fn=get_user_tier,
    )
    # If validation succeeds, proceed with the override
except (ValueError, PermissionError) as e:
    # If validation fails, handle the error
    pass
```

### ⚛️ Quantum: Ambiguity and Resolution

**Purpose**: The Quantum star holds ambiguity and explores multiple possibilities until resolution. It uses quantum-inspired algorithms to simulate superposition, entanglement, and other quantum phenomena, enabling the system to perform complex calculations and explore a wide range of potential outcomes.

**Technical Implementation**: The `labs/consciousness/reflection/qi_dream_adapter.py` file provides an adapter for integrating the dream engine with the quantum bio-oscillator system. The `QIDreamAdapter` class enables quantum-enhanced dream processing and memory consolidation.

**Integration Patterns**: The Quantum star is used in situations where it is necessary to explore a large and complex solution space. For example, it could be used to generate a wide range of creative ideas, or to simulate the potential outcomes of a complex decision.

**Coordination Workflows**: A component can request that the Quantum star perform a simulation by providing a seed and a set of parameters. The Quantum star then runs the simulation and returns a set of convergent insights, which can be used to inform the component's decision-making process.

**Example**:
```python
from labs.consciousness.reflection.qi_dream_adapter import QIDreamAdapter
from ..oscillator.orchestrator import BioOrchestrator

# Initialize the necessary components
orchestrator = BioOrchestrator()

# Initialize the QIDreamAdapter
qi_dream_adapter = QIDreamAdapter(orchestrator=orchestrator)

# Simulate multiverse dreams
results = await qi_dream_adapter.simulate_multiverse_dreams(
    dream_seed={"initial_concept": "a new form of art"},
    parallel_paths=10,
)
```
