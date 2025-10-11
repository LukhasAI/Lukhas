
# LUKHAS — Constellation & Artifacts Kickoff (T4 / 0.01% Brief)

## Decisions (lock these first)

* **Consciousness is a first-class star** → **Flow (Consciousness) 🌊** becomes canonical (not a sub-aspect).
* **No lanes going forward**: treat `lane` as **deprecated** metadata. We keep it only for back-compat mapping.
* **Goal (now)**: **Map & tag** every module with compliant artifacts (manifest + docs) **before** big file moves. We will fix imports/paths after tagging to avoid thrash.

---

## Scope (what we’re doing this week)

1. **Schema bump to v1.1.0** (non-breaking) to match Constellation + deprecate lanes.
2. **Generate manifests for all ~780 modules**, prioritized by stars (user-facing capabilities first).
3. **Auto-scaffold documentation** (`lukhas_context.md` and `README.md`) for star-critical modules.
4. **CI gates** (warning-only initially): block new code without manifests; surface T1/T2 violations.
5. **Minimal P0 safety sweep**: undefined names/syntax only—full path fixes later.

---

## Canonical Constellation (single source of truth)

```
STAR_CANON = [
  "⚛️ Anchor (Identity)",
  "✦ Trail (Memory)",
  "🔬 Horizon (Vision)",
  "🌱 Living (Bio)",
  "🌙 Drift (Dream)",
  "⚖️ North (Ethics)",
  "🛡️ Watch (Guardian)",
  "🔮 Oracle (Quantum)",
  "🌊 Flow (Consciousness)",   # NEW: promoted to star
  "Supporting"                 # non-star, placeholder
]
```

**Aliases (accepted in manifests; normalized in tooling):**

* `"Flow (Consciousness)"`/`"Consciousness"` → `🌊 Flow (Consciousness)`
* `"Quantum"` → `🔮 Oracle (Quantum)`
* Any legacy names map to the canonical list above.

---

## v1.1.0 Schema Patch (apply to `schemas/matriz_module_compliance.schema.json`)

**Essentials only (copy/paste edits):**

* Make `module.lane` **optional** and **DEPRECATED**; add `module.colony` (free string or enum you prefer).
* Extend logging levels.
* Add `events` (publishes/subscribes contracts) and `security` block.
* Add **`🌊 Flow (Consciousness)`** to `constellation_alignment.primary_star` enum; keep “Supporting”.

```json
// PATCH: illustrative snippet
{
  "properties": {
    "module": {
      "type": "object",
      "additionalProperties": false,
      "required": ["name", "path", "type"],
      "properties": {
        "name": {"type":"string"},
        "path": {"type":"string"},
        "type": {"type":"string","enum":["package","module","namespace"]},
        "colony": {
          "type": "string",
          "description": "Flat capability domain (replaces legacy 'lane')"
        },
        "lane": {
          "type": "string",
          "description": "DEPRECATED: legacy import isolation (will be removed in v2.0)"
        }
      }
    },
    "constellation_alignment": {
      "type": "object",
      "additionalProperties": false,
      "required": ["primary_star"],
      "properties": {
        "primary_star": {
          "type": "string",
          "enum": [
            "⚛️ Anchor (Identity)","✦ Trail (Memory)","🔬 Horizon (Vision)","🌱 Living (Bio)",
            "🌙 Drift (Dream)","⚖️ North (Ethics)","🛡️ Watch (Guardian)","🔮 Oracle (Quantum)",
            "🌊 Flow (Consciousness)","Supporting"
          ]
        },
        "star_aliases": {"type":"array","items":{"type":"string"}},
        "trinity_aspects": {"type":"array","items":{"type":"string"},"uniqueItems": true}
      }
    },
    "observability": {
      "type":"object",
      "additionalProperties": false,
      "properties": {
        "spans": {"type":"array","items":{"type":"string"}},
        "metrics": {"type":"array","items":{
          "type":"object","required":["name","type"],
          "properties":{"name":{"type":"string"},"type":{"type":"string","enum":["counter","gauge","histogram"]},"description":{"type":"string"}}
        }},
        "logging": {
          "type":"object",
          "additionalProperties": false,
          "properties":{
            "logger_name":{"type":"string"},
            "default_level":{"type":"string","enum":["TRACE","DEBUG","INFO","WARNING","ERROR","CRITICAL"]}
          }
        },
        "events": {
          "type":"object",
          "properties":{
            "publishes":{"type":"array","items":{"type":"string","pattern":"^[a-z0-9_.:-]+@v\\d+$"}},
            "subscribes":{"type":"array","items":{"type":"string","pattern":"^[a-z0-9_.:-]+@v\\d+$"}}
          }
        }
      }
    },
    "security": {
      "type":"object",
      "properties":{
        "requires_auth":{"type":"boolean"},
        "data_classification":{"type":"string","enum":["public","internal","restricted","sensitive"]},
        "secrets_used":{"type":"array","items":{"type":"string"}},
        "network_calls":{"type":"boolean"},
        "sandboxed":{"type":"boolean"},
        "policies":{"type":"array","items":{"type":"string"}}
      }
    }
  }
}
```

> Also add `additionalProperties:false` to all nested objects (`module`, `matriz_integration`, `dependencies`, `exports`, `testing`, `observability`, `metadata`) to prevent silent drift.

---

## Heuristics for fast **module → star** tagging (first pass)

* **Flow (Consciousness) 🌊**: paths containing `/consciousness/`, `/awareness/`, `/dream/`, `/oneiric/`, `/creativity/`.
* **Trail (Memory) ✦**: `/memory/`, `/rag/`, `/kg/`, `/embeddings/`.
* **Anchor (Identity) ⚛️**: `/api/oidc`, `/auth/`, `/identity/`, `/tenancy/`.
* **Watch (Guardian) 🛡️** / **North (Ethics) ⚖️**: `/guardian_`, `/ethics/`, `*_policy*`, `*_consent*`.
* **Drift (Dream) 🌙**: simulation, planning, rehearsal engines (distinct from hot path).
* **Horizon (Vision) 🔬**: UI/rendering/visualization surfaces.
* **Living (Bio) 🌱**: `/bio/`, bio-inspired systems.
* **Oracle (Quantum) 🔮**: `quantum_*`, `qi_*`, `quantum_attention`.

> This is **initial labeling** for automation. Humans can refine later, but this gets us to 100% coverage quickly.

---

## Artifact Templates (drop these into the repo templates)

### 1) Manifest stub (`module.manifest.json`)

```json
{
  "schema_version": "1.1.0",
  "module": {
    "name": "<fqn>",
    "path": "<rel/path>",
    "type": "package",
    "colony": "<reflex|simulation|memory|ethics|perception|actuation|orchestration|interface|infrastructure>",
    "lane": "<legacy-lane-or-empty>"
  },
  "matriz_integration": {
    "status": "partial",
    "pipeline_nodes": ["supporting"],
    "cognitive_function": ""
  },
  "constellation_alignment": {
    "primary_star": "Supporting",
    "star_aliases": [],
    "trinity_aspects": []
  },
  "capabilities": [],
  "dependencies": {"internal": [], "external": [], "circular_dependencies": []},
  "exports": {"classes": [], "functions": [], "constants": []},
  "testing": {"has_tests": false, "test_paths": [], "quality_tier": "T4_experimental"},
  "observability": {
    "spans": [],
    "metrics": [],
    "logging": {"logger_name": "<package>", "default_level": "INFO"},
    "events": {"publishes": [], "subscribes": []}
  },
  "security": {"requires_auth": false, "data_classification": "internal", "secrets_used": [], "network_calls": false, "sandboxed": true, "policies": []},
  "metadata": {"created": "<ISO8601>", "last_updated": "<ISO8601>", "manifest_generated": true, "owner": "unassigned", "documentation_url": "", "tags": []}
}
```

### 2) `lukhas_context.md` (auto-generated scaffold)

```markdown
# <Module FQN>

**Star**: <🌊 Flow / ✦ Trail / …>  
**MATRIZ Nodes**: <memory|attention|thought|risk|intent|action|supporting>  
**Colony**: <reflex|simulation|…>  

## What it does
<1–2 paragraphs; link to demos/tests if any>

## Contracts
- **Publishes**: `<topic>@v1`
- **Subscribes**: `<topic>@v1`
- **Exports**: `<class|fn>` (public API)

## Observability
- **Spans**: `<otlp-span-names>`
- **Metrics**: `<counter/gauge/histogram>`
- **Logging**: `<logger_name: level>`

## Security
- **Auth**: `<OIDC|Token|None>`
- **Data classification**: `<public|internal|restricted|sensitive>`
- **Policies**: `<Guardian/North policy refs>`

## Tests
- `tests/<path>...`
- Coverage target: `<>=X%>` (T1≥70, T2≥50, T3≥30, T4=n/a)
```

---

## Commands (safe, repeatable)

> Run in a feature branch: `git checkout -b artifacts/constellation-v1`

**Find modules lacking manifests**

```bash
rg -l --glob '!venv' 'module.manifest.json' | wc -l
```

**Generate 100% manifests from inventory (skeleton script name)**

```bash
python scripts/generate_module_manifests.py \
  --inventory docs/audits/COMPLETE_MODULE_INVENTORY.json \
  --out manifests \
  --schema schemas/matriz_module_compliance.schema.json \
  --star-canon scripts/star_canon.json \
  --write-context
```

**Validate (Python jsonschema)**

```bash
python - <<'PY'
import json, glob
from jsonschema import Draft7Validator
schema = json.load(open("schemas/matriz_module_compliance.schema.json"))
v = Draft7Validator(schema)
fails = 0
for f in glob.glob("**/module.manifest.json", recursive=True):
    data = json.load(open(f))
    errs = sorted(v.iter_errors(data), key=lambda e: e.path)
    if errs:
        fails += 1
        print("[FAIL]", f); [print(" -", e.message) for e in errs[:5]]
print("DONE; failures:", fails)
PY
```

**CI (warning-only initially)**

* Add a job that runs validator; **do not** fail pipeline yet except on schema parse error.
* Gate PRs that add new modules without a manifest.

---

## Workstream Ownership & Tasking (paste to agents)

### CLAUDE (Gatekeeper / Reviewer, high-risk)

1. **Review v1.1.0 schema patch** (Constellation enum incl. Flow; deprecate lane; add events/security; tighten `additionalProperties:false`).

   * *Acceptance*: schema validates itself; passes AJV/jsonschema sanity.
2. **Define policy for T-tiers** (T1/T2 required fields: tests, owner, at least one span+metric, security classification).

   * *Acceptance*: `if/then` rules encode these; 3 gold sample manifests validate.
3. **Codify Constellation alias map** (JSON) and normalization rules.

   * *Acceptance*: generator converts aliases to canonical star with no manual edits.
4. **Review generator output on 50 critical modules** (Anchor/Trail/Flow/Watch/North).

   * *Acceptance*: ≤5% manual fixes required.

### CODE / CODEX (Mechanical / Scripts / Bulk)

1. **Apply schema patch** and commit `schemas/matriz_module_compliance.schema.json` v1.1.0.
2. **Implement `scripts/generate_module_manifests.py`**:

   * Input: inventory JSON; Output: `manifests/<path>/module.manifest.json` (+ `lukhas_context.md` scaffolds).
   * Heuristics above for star + pipeline nodes; populate security defaults; logging defaults.
3. **Validator script** (`scripts/validate_manifests.py`) + **Makefile** targets:

   * `make manifests`, `make validate-manifests`.
4. **CI pipeline** (GitHub Actions): add job `manifest-validate` (warning-only).
5. **Compute coverage badges**: manifest coverage %, context coverage % → write `docs/audits/*.svg`.

*Acceptance*: 100% manifests generated; validator runs green (except intentional warnings); badges render.

### COPILOT (Inline refactors / Docs)

1. Create/complete **`lukhas_context.md`** from manifest for **stars-critical modules first**.
2. Normalize headings, add links to tests, record exported APIs.
3. Fix simple ruff issues that block import/collection (F401/F821/F401 etc.) only in touched modules.

*Acceptance*: All star-critical modules have context pages; `pytest -q -k smoke` collects; ruff undefined-name errors eliminated in those modules.

---

## Prioritization (first passes)

**Wave 1 (today–tomorrow):**

* Anchor (Identity) ⚛️ — API/OIDC/adapters (critical surface)
* Flow (Consciousness) 🌊 — awareness, dream, engines (biggest cluster)
* Watch (Guardian) 🛡️ & North (Ethics) ⚖️ — guardian_integration, ethics_sync
* Trail (Memory) ✦ — memory core paths

**Wave 2:**

* Drift (Dream) 🌙 (simulation pathways distinct from Flow)
* Horizon (Vision) 🔬 (UI/visualization)
* Living (Bio) 🌱
* Oracle (Quantum) 🔮

---

## Done criteria for this phase

* **Schema v1.1.0 merged**; Constellation enum includes **Flow (Consciousness) 🌊**; lanes deprecated.
* **Manifests at 100%** (auto-generated) + **Context pages** for all star-critical modules.
* CI shows **artifact coverage badges** and runs **manifest validation** (warn stage).
* P0 safety: no undefined names/syntax errors in star-critical modules; smoke tests collect.

---

## Risks & Mitigations

* **Naming churn**: Freeze Constellation canon in a single JSON consumed by schema + generator.
* **Over-strict schema early**: Start with warnings; switch to hard-fail for T1/T2 only next week.
* **Time sink on long tail**: Auto-scaffold docs from manifests; human edits only for stars.

---

## Quick copy blocks for the agents

**Commit titles**

* `schema: bump MATRIZ compliance to v1.1.0 (Flow star, events/security, lane deprecated)`
* `scripts: add manifest generator + validator + star canon`
* `ci: add manifest validation (warn-only) + coverage badges`
* `docs: auto-scaffold lukhas_context.md for star-critical modules`

**Labels**

* `type:schema` `type:automation` `area:constellation` `priority:P0` (stars) / `P1` (rest)

---

