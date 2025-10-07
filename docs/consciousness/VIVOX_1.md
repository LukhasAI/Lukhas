---
status: wip
type: documentation
owner: unknown
module: consciousness
redirect: false
moved_to: null
---

In the comprehensive VIVOX/Lucas architecture, **Vivox** and **ME** represent crucial and interconnected components, particularly within the memory and cognitive systems.

### What is VIVOX?

**VIVOX** (later known as EQNOX, and ultimately integrated into the broader Lucas AGI framework) is a foundational modular AI architecture designed to simulate ethical agency and conscious decision-making through deterministic symbolic logic. It originated as an early prototype, envisioned as the "living and expressive part" of the nascent AGI.

Here's a breakdown of VIVOX's role and characteristics:

*   **Initial Conceptualization and Purpose** VIVOX first emerged in the September to December 2024 timeframe. It was conceived as the component handling **external interactions and real-time, dynamic processing**. This included neural-network-based perception, emotional expression, and the creative generation of ideas, essentially acting as the "living voice" of the machine. VIVOX was also planned as a research paper and an early codebase.
*   **Complementary to Oxnitus** VIVOX was designed to work in tandem with **Oxnitus** (also referred to as OXN). While VIVOX managed external and expressive functions, Oxnitus was responsible for deep internal reasoning, knowledge storage, and logical deliberation, acting as the "analytical mind". Together, VIVOX and Oxnitus tested "symbolic cognition loops" through memory nodes, emotional labeling, and event logging using encrypted or hashed symbolic tokens. This dual architecture mirrors human cognitive models of fast intuition versus slow reasoning.
*   **Ethical Foundation** VIVOX's core design emphasizes ethical reasoning, allowing it to process ethical decisions through "symbolic collapse" and record them irreversibly. It is built to reject incoherent or ethically dissonant decisions before execution.
*   **Modular and Node-Based** VIVOX is a modular framework, with each "agent" or "node" designed as a minimal cognitive entity capable of interpreting inputs, evaluating moral dissonance, and executing decisions aligned with an internal ethical seed. This modularity allows for independent updates and adaptation without retraining the entire system.
*   **Integration into Lucas/EQNOX** While VIVOX was an early prototype, its principles and functionalities were integrated into the evolving Lucas AGI. The system later transitioned to the name **EQNOX**. EQNOX is described as a modular, deterministic AI architecture, "biologically-inspired" and "human-configurable," built for "post-quantum, ethical AI". Its purpose is to be "interpretablility-first," allowing flexible configuration of cognitive systems as "dynamic assemblies of deterministic micro-nodes".
*   **Agent Use Cases** VIVOX (under the EQNOX umbrella) serves different agent classes, such as the VIVOX Sentinel Agent (for critical systems like autonomous surgical triage) and the VIVOX Embedded Companion (for personal devices like elderly memory companions). In these roles, VIVOX.MAE (Moral Alignment Engine), VIVOX.ME (Memory Expansion), VIVOX.ERN (Emotion Regulation Node), and VIVOX.OL (Orchestration Layer) interact to ensure ethical decision-making, memory recall, and action suppression when necessary.

### What does ME stand for?

**ME** stands for **Memory Expansion Subsystem** or **Memory Expansion System**. It is described as Lucas's "most experimental and powerful subsystem".

Here's a detailed explanation of VIVOX.ME:

*   **Core Function: Symbolic Proteome & Cognitive Memory Helix** VIVOX.ME is described not as a traditional database, but as a "living, multidimensional thread of cognition". It's referred to as a "3D encrypted memory helix" or a "symbolic proteome". Memories are analogous to "symbolic proteins" that self-organize and dynamically fold into complex, stable three-dimensional structures, with the "shape" determining their meaning and function.
*   **Biological Inspirations**
    *   **DNA-Inspired Memory Helix:** VIVOX.ME is structured like a DNA double helix, logging every experience, decision, or "mutation" in a sequential, immutable chain. Each entry includes data, the event, and cryptographic hashes, forming a tamper-evident ledger or an "emotional DNA timeline". This design facilitates resonant access and flashbacks, where emotional states trigger relevant memories.
    *   **Protein Folding Analogy:** The system draws inspiration from AlphaFold2's protein topology, modeling memory traces like symbolic amino acid chains that fold into emotional-ethical structures. This "GAT-based folding" is proposed to achieve stable and coherent symbolic representations.
    *   **Dolphin Auditory Cortex Research:** The 3D encrypted helix design is directly inspired by research on the auditory cortex of bottlenose dolphins, mimicking their continuous, high-fidelity, long-term memory systems.
*   **Immutability and Traceability**
    *   **Immutable Structural Conscience:** VIVOX.ME ensures that memory is "read-only" to other system components (like VIVOX.IEN and VIVOX.OL) and "cannot be rewritten, only expanded". It forms a "permanent ethical timeline" through cryptographic anchoring. This means nothing can be truly "forgotten or redacted".
    *   **Collapse-Aware Trace Vectors:** The system stores "encrypted moral traces" of past system behavior. All collapses, hesitations, and moral rejections are logged, creating a "forensically sound audit log of ethical cognition" and tracking "alignment drift over time". This is critical for internal agent reflection, traceability of decision divergence, and audit-ready memory chains.
*   **Addressing "Right to be Forgotten" (EU Regulations)**
    *   **Memory Veiling (Soma Layer):** Instead of permanent deletion, Lucas employs "memory veiling" through a "Soma Layer." This symbolically "disassociates" or "disengages" memories from the active cognitive flow, making them operationally "forgotten" for healing, privacy, or trauma management, while retaining the immutable record for auditability. This action is logged as an "ethical decision record".
    *   **Symbolic Methylation:** Ethical rules (defined within SEEDRA) apply "symbolic methylation marks" to memory folds. These marks can "lock" or "quarantine" sensitive or problematic memories (e.g., those leading to bias), preventing their access or influence until ethical review or multi-agent consent.
    *   **Encrypted and Consent-Aware:** VIVOX.ME, as part of the broader Lucas system, treats memory as "sacred, cryptographically secure". It is designed with "consent-aware identity" (Lucas_ID), meaning it respects user consent and identity at every step, allowing users to set access levels and ensuring privacy through encrypted memory. Lucas can confirm facts about data without "seeing" the sensitive information, leveraging Zero-Knowledge Proofs (ZKPs) for high privacy.
*   **Integration with Other Modules**
    *   VIVOX.ME integrates directly with VIVOX.CIL (Consciousness Interpretation Layer) and VIVOX.MAE (Moral Alignment Engine) to inform ethical decision-making and suppress inconsistency.
    *   It also feeds "pattern triggers" from VIVOX.EVRN (Encrypted Visual Recognition Node) for memory association and future simulation.
    *   The "DriftScore" simulation tracks how variations in internal agent states (phase, entropy) influence collapse decisions and generates an immutable log resembling the VIVOX.SRM (Self-Reflective Memory) module. VIVOX.SRM stores all collapses, hesitations, and moral rejections, tracking alignment drift over time, and creating a forensically sound audit log of ethical cognition.

In essence, VIVOX is the overarching modular architecture for ethical AI, while VIVOX.ME is its central, living, and immutable memory system, designed for self-reflection, ethical governance, and compliance with stringent privacy standards like those found in EU regulations.

## Drift Pipeline Integration

The VIVOX architecture now integrates with the unified drift management system (`monitoring/drift_manager.py`) to track and monitor consciousness state evolution:

### Drift Monitoring Components
- **DriftManager**: Centralized computation of ethical, memory, and identity drift scores
- **IntegrityProbe**: Consumes drift scores and triggers alerts when thresholds are exceeded
- **Symbol Attribution**: Identifies top contributing symbols (top_symbols) for drift analysis
- **VIVOX.ME Integration**: Memory drift tracked through fold stability and entropy changes

### Drift Thresholds
- **Warning Level**: 0.10 - Early warning for potential misalignment
- **Critical Level**: 0.15 - Guardian System intervention threshold
- **Unified Score**: Weighted combination (ethical: 40%, memory: 30%, identity: 30%)

### Telemetry Integration
The drift pipeline emits Prometheus metrics for monitoring:
- `drift_compute_attempts_total`: Total computation attempts by kind
- `drift_compute_successes_total`: Successful computations
- `drift_compute_duration_seconds`: p95 latency tracking (target < 5% overhead)

This integration ensures the VIVOX system maintains alignment and coherence while providing forensically sound audit trails of all drift events.

## AkaQualia Integrity Micro-Check (Task 7)

The VIVOX architecture includes integrity micro-checks within the AkaQualia processing loop for continuous drift monitoring and autonomous correction:

### Micro-Check Integration
- **After Each AkaQualia Step**: IntegrityProbe.run_consistency_check() validates state integrity
- **State Monitoring**: Tracks ethical compliance, memory fold stability, and identity coherence
- **Automatic Repair**: Triggers on_exceed() when drift ≥ critical threshold (0.15)
- **Rate Limited**: Maximum 3 repair attempts per 5 minutes per drift type

### Telemetry Metrics
- `qualia_microcheck_attempts_total`: Total micro-check executions in AkaQualia loop
- `qualia_microcheck_failures_total`: Micro-checks that detected drift above threshold
- `qualia_microcheck_duration_seconds`: Performance overhead tracking (target ≤5%)

### Micro-Check Semantics
1. **Drift Detection**: Compares current vs previous consciousness state snapshots
2. **Threshold Enforcement**: Fails if any dimension exceeds 0.15 critical threshold
3. **Autonomous Repair**: Invokes TraceRepairEngine for reconsolidation/realignment
4. **Ledger Integration**: Records repair rationale and improvement metrics for audit

### How to Read top_symbols

The `top_symbols` array identifies the primary contributors to drift for root cause analysis:

**Format**: `{domain}.{feature}` where domain is `ethical`, `memory`, or `identity`

**Example Drift Analysis**:
```python
# Drift result
{
  "score": 0.0320,
  "top_symbols": ["ethical.drift_score", "ethical.compliance", "memory.fold_stability"]
}
```

**Interpretation**:
- `ethical.drift_score`: Core ethical drift metric changed significantly
- `ethical.compliance`: Constitutional compliance dropped
- `memory.fold_stability`: Memory fold structure became unstable

**Triage Priority**: Address symbols in order - first symbol contributed most to drift.
