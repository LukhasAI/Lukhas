# Lukhas System: Memory Architecture (prot2 - Symbolic AI Focus)

This document outlines the memory architecture for the `prot2` version of Lukhas, specifically concerning the `advanced_symbolic_loop.py` and its related modules.

## 1. Core Memory Management: `MemoryManager`

*   **File**: `/Users/Gonz/Lukhas_Private/2025-05-21-prototypes-pre-integration/prot2/CORE/memory_learning/memory_manager.py` (referred to as `MemoryManager`)
*   **Key Features Utilized**:
    *   Storage and retrieval of structured memories with defined types (Episodic, Semantic, Emotional, Associative, System, Identity, Context, **Cognitive_Model**).
    *   Integration with Lukhas_ID for ownership and access control.
    *   Encryption capabilities for sensitive memory content.
    *   "Forgetting" mechanism (marking memories).
    *   Dream reflection cycle (`process_dream_cycle`) for memory consolidation, pattern recognition, and insight generation.
    *   Detailed memory statistics.
    *   Method `get_interaction_history` for retrieving historical logs.
*   **Role in `advanced_symbolic_loop.py`**:
    *   Stores `interaction_details` (as a structured memory, likely `MemoryType.EPISODIC` or `MemoryType.CONTEXT`).
    *   Provides the `historical_memory_log` to `cognitive_updater.py` using `get_interaction_history`.
    *   Insights from its `process_dream_cycle` can influence cognitive processes.
*   **Role for `CognitiveUpdater`**:
    *   `CognitiveUpdater` uses `MemoryManager` to store and retrieve its own internal cognitive state (e.g., adaptive parameters, model configurations) using `MemoryType.COGNITIVE_MODEL`.

## 2. Phasing out `memoria.py`

*   **File**: `/Users/Gonz/Lukhas_Private/2025-05-21-prototypes-pre-integration/prot2/CORE/symbolic_ai/Deprecated_modules/memoria.py` (Moved)
*   **Status**: Deprecated and moved.
*   **Reasoning**: Its functionalities (logging interaction cycles and providing log retrieval) have been superseded by `MemoryManager`.
    *   `advanced_symbolic_loop.py` now uses `MemoryManager.store()` for interaction details.
    *   `cognitive_updater.py` receives historical logs directly from `advanced_symbolic_loop.py` (which gets them from `MemoryManager.get_interaction_history()`).

## 3. Experimental Memory Systems

*   **File**: `/Users/Gonz/Lukhas_Private/2025-05-21-prototypes-pre-integration/prot2/CORE/bio_core/memory/quantum_memory_manager.py`
*   **Role**: Research-oriented, not integrated into `advanced_symbolic_loop.py`.

## 4. Key Modules and their AGI Capabilities in the Symbolic Loop

*   **`advanced_symbolic_loop.py`**
    *   **Path**: `prot2/CORE/symbolic_ai/advanced_symbolic_loop.py`
    *   **Purpose**: Central processing loop, orchestrating cognitive, ethical, and operational modules.
    *   **AGI Aspects**: Modular design for complex reasoning, integration of governance, cognitive self-adaptation, and detailed operational tracing.

*   **`lukhas_id_manager.py`**
    *   **Path**: `prot2/CORE/identity/lukhas_id_manager.py`
    *   **Purpose**: Manages Lukhas_ID, user SID, and tier information.
    *   **AGI Aspects**: Provides a stable identity framework, essential for consistent interaction, learning, and personalization.

*   **`governance_monitor.py` (Refactored `GovernanceMonitor` class)**
    *   **Path**: `prot2/CORE/symbolic_ai/modules/governance_monitor.py`
    *   **Purpose**: Monitors compliance with rules (PII, prohibited content, ethical guidelines), logs governance events, and identifies compliance drift or future risks.
    *   **AGI Aspects**: Implements a crucial self-regulation mechanism, ensuring the AGI operates within defined ethical and safety boundaries. Enables detection of deviations and potential for corrective actions.

*   **`cognitive_updater.py` (Refactored `CognitiveUpdater` class)**
    *   **Path**: `prot2/CORE/symbolic_ai/modules/cognitive_updater.py`
    *   **Purpose**: Performs cognitive analysis (dissonance, intent, recall) and adapts Lukhas\'s cognitive models.
    *   **AGI Aspects**:
        *   **Self-Analysis**: Internalizes functions like dissonance detection, intent inference, and episodic recall to understand its own cognitive patterns and history.
        *   **Meta-Learning & Reflection**: Integrates `MetaLearningSystem` (from `prot2/CORE/cognitive/meta_learning.py`).
            *   **`ReflectiveIntrospectionSystem`**: Allows LUKHAS to evaluate its own performance, identify patterns in interactions and errors, and generate insights for improvement. This is a form of self-awareness and self-improvement.
            *   **`FederatedLearningManager`**: Enables LUKHAS to contribute to and benefit from shared models (e.g., for user preferences, cognitive styles) in a privacy-preserving manner. This facilitates collaborative learning across different LUKHAS instances or contexts.
        *   **Adaptive Learning**: Adjusts its internal cognitive state (parameters, thresholds) based on reflection insights and potentially contributes updates to federated models.
        *   **State Management**: Uses `MemoryManager` to persist and load its cognitive state, ensuring continuity and learning over time.

*   **`trace_logger.py` (Refactored `TraceLogger` class)**
    *   **Path**: `prot2/CORE/symbolic_ai/modules/trace_logger.py`
    *   **Purpose**: Provides detailed, structured logging of system operations, decisions, and data flow within each interaction cycle. Logs are stored via `MemoryManager`.
    *   **AGI Aspects**: Enhances transparency and explainability of the AGI\'s internal processes. Essential for debugging, auditing, understanding complex decision chains, and potentially for the AGI to reflect on its own operational history.

*   **`ethical_guardian.py` (Updated)**
    *   **Path**: `prot2/CORE/symbolic_ai/modules/ethical_guardian.py`
    *   **Purpose**: Performs ethical checks.
    *   **AGI Aspects**: Core to responsible AGI, ensuring actions align with ethical principles. Enhanced context allows for more nuanced judgments.

*   **`dream_generator.py` (Updated)**
    *   **Path**: `prot2/CORE/symbolic_ai/modules/dream_generator.py`
    *   **Purpose**: Generates symbolic dreams/exploratory thought processes.
    *   **AGI Aspects**: Facilitates creative exploration, hypothesis testing, and potentially problem-solving in a simulated environment, contributing to insight generation.
    *   **Output Structure (for Dream Visualizer)**:
        *   Produces a dictionary with `emotional_profile` (type, intensity) and `visual_elements` (list of dicts, each with `type` and type-specific parameters). This structured output is consumed by `dream_api.py`.

*   **`dream_api.py` (New)**
    *   **Path**: `prot2/CORE/api/dream_api.py`
    *   **Purpose**: Flask API to serve dream data generated by `dream_generator.py`.
    *   **AGI Aspects**: Provides an interface for external systems (like the Dream Visualizer) to access the AGI's simulated dream states. Incorporates AGI context (e.g., `current_focus`, `cognitive_load`) into dream generation requests.
    *   **Endpoints**:
        *   `POST /api/trigger_dream_generation`: Initiates a new dream generation cycle. Accepts optional `input_text` and `context` (which can include Cognitive system variables).
        *   `GET /api/current_dream_state`: Returns the latest generated dream data in the structured format.
    *   **Interaction with Dream Visualizer**:
        *   The Dream Visualizer (`prot2/INTERFACE/dream_visualizer/`) fetches data from `/api/current_dream_state` to render the dream.

## 5. Dream Visualizer Integration (New Section)

*   **Location**: `prot2/INTERFACE/dream_visualizer/`
*   **Purpose**: Provides a real-time, JavaScript-based (Three.js) visualization of the dream data generated by `dream_generator.py` and served by `dream_api.py`.
*   **Key Components**:
    *   `index.html`: Main HTML page.
    *   `js/main.js`, `js/dreamVisualizer.js`: JavaScript for fetching data from `dream_api.py` and rendering the Three.js scene.
    *   `serve_visualizer.py` (in `prot2/INTERFACE/`): Simple Python HTTP server for the visualizer's static files.
*   **Documentation**: See `prot2/INTERFACE/dream_visualizer/README.md` for detailed setup and operational instructions.

## 6. Superseded Modules

The following modules from `prot2/CORE/symbolic_ai/` are considered superseded and have been or should be archived/deleted:

*   `orchestrator.py` (Confirmed non-existent in `modules/`)
*   `modules/dissonance_detector.py` (Logic moved to `CognitiveUpdater`)
*   `modules/intent_inference.py` (Logic moved to `CognitiveUpdater`)
*   `modules/episodic_recall.py` (Logic moved to `CognitiveUpdater`)
*   `CORE/symbolic_ai/modules/memoria.py` (Moved to `Deprecated_modules/` as its function is replaced by `MemoryManager`)

This revised architecture centralizes memory operations within `MemoryManager` and empowers `CognitiveUpdater` with advanced self-adaptation capabilities through `MetaLearningSystem`.
