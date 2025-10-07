---
status: wip
type: documentation
owner: unknown
module: root
redirect: false
moved_to: null
---

![Status: WIP](https://img.shields.io/badge/status-wip-yellow)

# 🌌 LUKHΛS Dream System — Phase EXPAND++

## Vision

Phase EXPAND++ is the experimental layer of the Dream System.
It pushes beyond stability and benchmarks into symbolic resonance,
ethical guardrails, and intuitive explainability.

This phase is deliberately opt-in, sandboxed, and T4-compliant:
- **Deterministic defaults**
- **Explicit environment flags**
- **No regressions to FORTIFY/BENCHMARK guarantees**

---

## 🍒 Core Components

### 1. Drift Atlas (`atlas.py`)
- **Logs symbolic/emotional drift & entropy across runs.**
- **Exports JSON and optional HTML constellation maps.**
- **Use case**: Visualize dream evolution and detect drift spikes.
- **Safety**: Emotional fields anonymized before export.

### 2. Conflict Mediation (`mediation.py`)
- **Resolves high-tension conflicts (e.g. fear vs confidence).**
- **Produces compromise vectors instead of binary overrides.**
- **Traceable**: Every mediation decision stored in trace.
- **Safety**: Mediation never overwrites canonical alignment, only annotates.

### 3. Ethical Sentinel (`sentinel.py`)
- **Threshold monitors (e.g. fear > 0.8).**
- **Blocks unsafe dreams before selection.**
- **Governance Hook**: Connects to higher-level ethical modules.
- **Safety**: Always logs block decisions, never silent.

### 4. Archetypal Mesh (`archetypes.py`)
- **Tags dreams with archetypes (Hero, Shadow, Trickster, etc.).**
- **Enables multi-agent mesh simulations with archetype clashes/harmonies.**
- **Opt-in**: Controlled by `LUKHAS_DREAM_ARCHETYPES=1`.
- **Symbolic layer**: Adds mythic context to dream interactions.

### 5. Narrative Replay (`replay.py`)
- **Converts numeric alignment/drift traces into plain-language stories.**
- **Explainability 2.0**: "Dream Alpha chosen (align=0.87, drift=0.12) over Beta due to higher curiosity resonance."
- **Safety**: Privacy filters applied to remove identifiers.

---

## ⚙️ CI Integration
- **Smoke Job** → Runs on EXPAND code changes, fast guardrail tests.
- **Bench Job** → Nightly cron + manual dispatch; runs Drift Atlas, Mediation, Archetypes, Replay.
- **Artifacts**: JSON summaries, dashboards, optional HTML exports.
- **Badges**:
  - `dream-expand-smoke` for PR confidence
  - `dream-expand-bench` for nightly science pulse

---

## 🧪 Testing
- **Unit tests per module** (`tests/unit/dream/expand/…`).
- **Benchmarks integrated** with existing corpus + synthetic adversarial cases.
- **CI enforces determinism** (`LUKHAS_DETERMINISTIC=1`).
- **EXPAND failures never block production PRs.**

---

## 🚦 Safety & Ethics
- **All features default OFF.**
- **Explicit environment flags required** to enable EXPAND features.
- **Guardrails at multiple levels**:
  - Sentinel thresholds
  - Atlas anonymization
  - Replay privacy filters
- **Compliance**: aligns with T4 and 0.01% audit standards.

---

## 🔮 Future Directions
- **Noise Fields**: Gaussian/symbolic noise injection for robustness.
- **Conflict Taxonomy**: Richer classification of dream conflicts.
- **Governance Loop**: Integrate EXPAND metrics into Matriz governance dashboards.
- **Human-in-the-loop labeling**: Extend corpus with real-world symbolic drift cases.

---

✅ **With EXPAND++, the Dream System evolves from deterministic alignment into a living symbolic lab — always safe, always explainable, and always pushing the frontier of LUKHΛS.**