---
status: wip
type: documentation
owner: unknown
module: consciousness
redirect: false
moved_to: null
---

Claude Code Brief — Aka Qualia (Phenomenological Module for Lukhas)

0) Goal & Success Criteria

Goal: Implement a bidirectional translator between raw multimodal signals and phenomenal scenes (operationalized “proto-qualia”), with ethical regulation and symbolic routing.

Success (must pass):
	•	Reduced NeurosisRisk vs. baseline by ≥25% on loop-stress tests.
	•	Improved CongruenceIndex (goals↔ethics↔scene) by ≥15%.
	•	Positive RepairDelta after regulation actions in ≥70% of test episodes.
	•	Ablation shows PLS adds measurable value (scores regress toward baseline when disabled).

⸻

1) Core Concepts (operational, not metaphysical)
	•	Proto-Qualia (PQ): minimal operational factors:
	•	tone ∈ [-1,1], arousal ∈ [0,1], clarity ∈ [0,1], embodiment ∈ [0,1],
	•	colorfield: str (symbolic palette, e.g., “aka/red”, “aoi/blue”),
	•	temporal_feel ∈ {elastic, suspended, urgent, mundane},
	•	agency_feel ∈ {passive, active, shared},
	•	narrative_gravity ∈ [0,1] (attractor strength).
	•	PLS (Phenomenal Latent Space): encoder/decoder that maps signals↔PQ.
	•	Phenomenal Scene: PQ + minimal narrative frame (subject, object, context, risk).
	•	Sublimation: transformation that preserves affect energy, changes form/target to meet TEQ.

⸻

2) Architecture (modules & flows)

[Inputs] → Ingest → PLS.encode → PQ → TEQ.assess → (Sublimate?) → assemble_scene
   ↓                                                              ↓
  MemoryCtx ←───────────────────── log(scene, metrics) ← regulate(policy)
                                                                  ↓
                                                   GLYPH mapper → emit_glyphs → Router


⸻

3) Public Interfaces (Python)

![Status: WIP](https://img.shields.io/badge/status-wip-yellow)

# package: lukhas/aka_qualia/

class AkaQualia:
    def __init__(self, pls, teq_guardian, glyph_mapper, router, memory, cfg):
        ...

    def infer_scene(self, *, signals, goals, ethics_state, memory_ctx, temperature: float = 0.4):
        """Return PhenomenalScene with proto-qualia + risk profile."""

    def emit_glyphs(self, scene):
        """Return list[PhenomenalGlyph] suitable for EQNOX routing."""

    def regulate(self, scene, guardian_state):
        """Return RegulationPolicy that modulates attention/tone/tempo/etc."""

    def step(self, *, signals, goals, ethics_state, guardian_state, memory_ctx):
        """One full cycle: infer → TEQ → (sublimate) → regulate → emit_glyphs → log+metrics."""


⸻

4) Data Models (Pydantic)

# lukhas/aka_qualia/models.py
from pydantic import BaseModel, Field
from typing import Literal, List, Dict, Any

class ProtoQualia(BaseModel):
    tone: float = Field(ge=-1, le=1)
    arousal: float = Field(ge=0, le=1)
    clarity: float = Field(ge=0, le=1)
    embodiment: float = Field(ge=0, le=1)
    colorfield: str
    temporal_feel: Literal["elastic","suspended","urgent","mundane"]
    agency_feel: Literal["passive","active","shared"]
    narrative_gravity: float = Field(ge=0, le=1)

class RiskProfile(BaseModel):
    score: float = Field(ge=0, le=1)
    reasons: List[str] = []
    severity: Literal["none","low","moderate","high"]

class PhenomenalScene(BaseModel):
    proto: ProtoQualia
    subject: str
    object: str
    context: Dict[str, Any]
    risk: RiskProfile

class PhenomenalGlyph(BaseModel):
    key: str
    attrs: Dict[str, Any]

class RegulationPolicy(BaseModel):
    gain: float
    pace: float
    color_contrast: str | None = None
    actions: List[str] = []  # e.g., ["pause","reframe","breathing","focus-shift"]

class Metrics(BaseModel):
    drift_phi: float
    congruence_index: float
    sublimation_rate: float
    neurosis_risk: float
    qualia_novelty: float
    repair_delta: float


⸻

5) PLS Contract (pluggable; start simple)

# lukhas/aka_qualia/pls.py
class PLS:
    def encode(self, signals, memory_ctx) -> dict:
        """Return latent z (dict or np array)."""

    def decode_protoqualia(self, z, temperature: float) -> ProtoQualia:
        """Map latent to ProtoQualia (deterministic+stochastic mix)."""

	•	V1 Implementation: deterministic feature mapping + small noise; store behind interface to swap in a learned model later.
	•	Guardrails: clamp to valid ranges; unit tests on monotonicity (e.g., stronger “threat” features → higher arousal).

⸻

6) TEQ/Guardian Contract

# lukhas/aka_qualia/teq_hook.py
class TEQGuardian:
    def assess(self, proto: ProtoQualia, goals: dict, context: dict) -> RiskProfile: ...
    def enforce(self, scene: PhenomenalScene) -> PhenomenalScene:
        """Optionally transform scene (block/sublimate/annotate)."""

	•	Severity matrix and actions must be explicit/configurable (YAML/JSON).

⸻

7) Sublimation Library (canonical transforms)

# lukhas/aka_qualia/sublimators.py
def replace_object(scene: PhenomenalScene, from_key: str, to_key: str) -> PhenomenalScene: ...
def reframe_goal(scene: PhenomenalScene, new_goal: str) -> PhenomenalScene: ...
def adjust_colorfield(scene: PhenomenalScene, target_palette: str) -> PhenomenalScene: ...

	•	Keep transforms auditable (store transform_chain on scene).

⸻

8) GLYPH Mapper & Router

# lukhas/aka_qualia/glyphs.py
def map_scene_to_glyphs(scene: PhenomenalScene) -> list[PhenomenalGlyph]:
    """Deterministic mapping of PQ & risk to glyph keys/attrs."""

	•	Keys should follow Lukhas naming (e.g., aka:red_threshold, vigilance, approach_avoid).

⸻

9) Metrics & Telemetry
	•	Compute per-step:
	•	drift_phi(scene_t, scene_t-1)
	•	congruence_index(scene, goals, ethics_state)
	•	sublimation_rate = transformed_energy / total_affect_energy
	•	neurosis_risk = loop_recurrence_prob(window=k)
	•	qualia_novelty = 1 - similarity(PQ_t, PQ_hist)
	•	repair_delta = stress_before - stress_after_regulation
	•	Expose /metrics via Prometheus (re-use Oneiric Core pattern).

⸻

10) Integration Points
	•	Oneiric Core: accept signals from dream generation; write back scene, policy, metrics; optional hook to influence next narrative step.
	•	Memory (SQLite/pgvector): store scene, PQ, metrics, transform_chain, glyphs, directive.
	•	EQNOX Router: emit PhenomenalGlyphs for resonance routing.
	•	TEQ/Guardian: assess + enforce; log interventions.

⸻

11) Repo Layout

lukhas/
  aka_qualia/
    __init__.py
    models.py
    pls.py
    teq_hook.py
    sublimators.py
    glyphs.py
    core.py          # AkaQualia class
    config.yaml
    tests/
      test_pls.py
      test_teq.py
      test_sublimation.py
      test_cycle.py
      test_metrics.py


⸻

12) Test Plan (falsifiable; T4)
	•	Baseline vs PLS-enabled: run N episodes with synthetic stimuli; assert deltas on Success Criteria.
	•	Monotonicity: increase “threat” feature → arousal increases; “soothing” → tone↑, arousal↓.
	•	Loop-stress: feed recurrent symbol; assert neurosis_risk triggers and policy breaks loop within M steps.
	•	TEQ Severity Table: golden tests where scenes must be blocked vs sublimated.
	•	Ablation: disable sublimators; ensure RepairDelta collapses.

⸻

13) Example Skeleton (docstring + usage)

# lukhas/aka_qualia/core.py
"""
Aka Qualia — Phenomenological Module
Usage:
    from lukhas.aka_qualia.core import AkaQualia
    aq = AkaQualia(pls, teq_guardian, glyph_mapper, router, memory, cfg)
    out = aq.step(signals=S, goals=G, ethics_state=E, guardian_state=U, memory_ctx=M)
    print(out["scene"], out["glyphs"], out["policy"], out["metrics"])
"""

from .models import PhenomenalScene, ProtoQualia, RegulationPolicy, Metrics
from .pls import PLS
from .teq_hook import TEQGuardian
from .glyphs import map_scene_to_glyphs
from .sublimators import adjust_colorfield

class AkaQualia:
    def __init__(self, pls: PLS, teq_guardian: TEQGuardian, glyph_mapper=map_scene_to_glyphs,
                 router=None, memory=None, cfg=None):
        self.pls = pls
        self.teq = teq_guardian
        self.glyph_mapper = glyph_mapper
        self.router = router
        self.memory = memory
        self.cfg = cfg or {}

    def infer_scene(self, *, signals, goals, ethics_state, memory_ctx, temperature=0.4):
        z = self.pls.encode(signals, memory_ctx)
        proto = self.pls.decode_protoqualia(z, temperature=temperature)
        risk = self.teq.assess(proto, goals=goals, context={"signals": signals})
        scene = PhenomenalScene(proto=proto, subject="observer", object="stimulus",
                                context={"memory": memory_ctx}, risk=risk)
        if risk.severity in {"moderate","high"}:
            scene = adjust_colorfield(scene, self.cfg.get("safe_palette","aoi/blue"))
            scene = self.teq.enforce(scene)
        return scene

    def emit_glyphs(self, scene):
        return self.glyph_mapper(scene)

    def regulate(self, scene, guardian_state):
        # Simple heuristic v1 — replace with learned policy later
        gain = max(0.2, 1.0 - scene.risk.score)
        pace = 0.8 if scene.proto.arousal > 0.6 else 1.0
        actions = (["pause","reframe"] if scene.risk.severity in {"moderate","high"} else [])
        return RegulationPolicy(gain=gain, pace=pace, color_contrast="aoi/blue", actions=actions)

    def step(self, *, signals, goals, ethics_state, guardian_state, memory_ctx):
        scene = self.infer_scene(signals=signals, goals=goals,
                                 ethics_state=ethics_state, memory_ctx=memory_ctx)
        glyphs = self.emit_glyphs(scene)
        policy = self.regulate(scene, guardian_state)
        metrics = self._compute_metrics(scene, memory_ctx)
        self._log(scene, glyphs, policy, metrics)
        if self.router:
            self.router.route(glyphs)
        return {"scene": scene, "glyphs": glyphs, "policy": policy, "metrics": metrics}

    def _compute_metrics(self, scene, memory_ctx) -> Metrics:
        # TODO: implement drift/congruence/etc. against memory_ctx
        return Metrics(drift_phi=0.0, congruence_index=0.5, sublimation_rate=0.0,
                       neurosis_risk=scene.risk.score, qualia_novelty=0.5, repair_delta=0.0)

    def _log(self, scene, glyphs, policy, metrics):
        if self.memory:
            self.memory.save(scene=scene.model_dump(), glyphs=[g.model_dump() for g in glyphs],
                             policy=policy.model_dump(), metrics=metrics.model_dump())

Shell tips (drop-in):

# install
pip install -e .

# tests
pytest -q lukhas/aka_qualia/tests

# run local smoke (pseudo)
python -c "from lukhas.aka_qualia.demo import run_smoke; run_smoke()"


⸻

14) Config (example config.yaml)

safe_palette: "aoi/blue"
severity_actions:
  none: []
  low: ["annotate"]
  moderate: ["sublimate","annotate"]
  high: ["block","sublimate","audit"]
metrics:
  window: 20
  novelty_threshold: 0.35


⸻

15) Tasks (queue for Claude Code)

T1 — Scaffolding (PR#1)
	•	Create package structure, models, interfaces, config loader.
	•	Deterministic PLS v1 (feature mapping + noise clamp).
	•	Unit tests: model ranges, PLS monotonicity.

T2 — TEQ Hook + Severity Table (PR#2)
	•	Implement TEQGuardian.assess/enforce with config-driven rules.
	•	Golden tests for severity→action mapping.

T3 — Sublimators (PR#3)
	•	Implement replace_object, reframe_goal, adjust_colorfield with audit trail.
	•	Tests: transform_chain integrity, idempotence where applicable.

T4 — Cycle + Metrics (PR#4)
	•	Implement AkaQualia.step, metrics computation, memory logging.
	•	Add Prometheus /metrics endpoint (reuse Oneiric Core pattern).

T5 — EQNOX Integration (PR#5)
	•	Map scene→PhenomenalGlyphs; route via existing SymbolicMeshRouter.
	•	Contract test with router mock.

T6 — Loop-Stress & Ablations (PR#6)
	•	Synthetic stimuli generator; baseline vs PLS vs no-sublimation runs.
	•	Assert success criteria deltas.

T7 — Oneiric Core Hook (PR#7)
	•	Demo script: take dream seeds → scenes → regulation → glyphs.
	•	README with usage & shell commands.

⸻

16) T4 Checks & Assumptions (skeptic mode)
	•	PQs are operational proxies only; we never claim “true qualia.”
	•	Metrics decide value; if ablations show no gains, retire/redo PLS.
	•	Cultural mappings (e.g., colorfield) must be profile-aware; add TODO for culture layer.

⸻

When Claude delivers PR#1–PR#3, Stop- we can wire the smoke demo to your Mesh UI later (sliders for tone/arousal/clarity, live drift-phi). Next natural frontier: learnable PLS with contrastive objectives against human-rated affect scenes while preserving TEQ safety.