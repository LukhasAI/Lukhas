# Strategic Brainstorm T4 Skill

A reusable high-level strategic reasoning skill that runs multi-dimensional analysis, hypothesis generation, and a prioritized roadmap using the T4 lens (Altman, Amodei, Hassabis, Jobs). Designed for product/technical strategy sessions grounded in repository and module contexts.

## Reasoning

1. Ingest module-level `lukhas_context.md` files and MODULE_INDEX.md to understand current state and constraints.

2. Frame 3–5 key strategic questions (e.g., 'What is the minimal safe MATRIZ MVP?', 'How to get LUKHΛS to production-grade reproducibility?').

3. For each question, produce: (a) crisp hypothesis, (b) experiments to validate, (c) success metrics, (d) risks and mitigations, (e) resource & timeline estimate.

4. Prioritize efforts using a risk vs. reward matrix and output a 3-, 6-, and 12-month roadmap with checkpoints, inspired by T4 perspectives: safety-first, scientific rigor, product simplicity, and operational excellence.

5. Require that before any engineering action, Claude writes its step-by-step reasoning and assumptions (transparent decision record). This reasoning must be included in PRs or strategy docs.

## Actions

### What the skill produces:
- A templated `strategic_session.md` containing: questions, hypotheses, experiments, milestones, risks, and owner assignments.
- A prioritized roadmap JSON and an interactive briefing deck outline.

### Example output snippet (6-month roadmap for MATRIZ + website + docs):

```json
{
  "month_0-1": [
    "Phase A MATRIZ scaffold + unit tests (owner: @gonzalo)",
    "Run repo cleanup dry-run and create archive (owner: infra)",
    "Scaffold web starter and landing page (owner: frontend)"
  ],
  "month_2-3": [
    "Phase B: Orchestrator log-only integration + monitoring (owner: systems)",
    "Doc autogen + context completion across 80% modules (owner: docs)",
    "Public PR: minimal lukhas.ai landing + first-breath experience (owner: frontend)"
  ],
  "month_4-6": [
    "Phase C: Controlled MATRIZ experiments with human-in-loop (owner: research)",
    "Launch LUKHΛS Embedding experimental API (owner: infra)",
    "Apply for initial funding/grant (owner: bizdev)"
  ]
}
```

### Evaluation rubric (used to prioritize):
- Safety & ethics risk (lower is better), Scientific rigor, Product simplicity, Time-to-value, Cost.

### Sample Claude pre-action reasoning template (to be included in all strategic outputs):
1. "Assumptions: ..."
2. "Data sources: [list lukhas_context.md, MODULE_INDEX.md]"
3. "Steps I will take (detailed)"
4. "Expected deliverables"
5. "Failure modes & fallback plans"

## Context References

- `/MODULE_INDEX.md`
- `/context_files.txt`
- `/docs/AI_TOOLS_INTEGRATION.md`
- `/context_headers.md`
