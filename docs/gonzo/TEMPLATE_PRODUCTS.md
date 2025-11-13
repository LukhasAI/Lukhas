# Branding page templates for LUKHAS products

> **📋 IMPLEMENTATION STATUS**
>
> **Status**: MOVED TO CANONICAL LOCATION (2025-11-06)
>
> These templates have been moved to:
> - **[branding/templates/PRODUCT_TEMPLATES.md](../../branding/templates/PRODUCT_TEMPLATES.md)**
>
> **This document remains as source reference.** For template usage, refer to the canonical location above.

---

These are three **Markdown templates** for common LUKHAS product pages:
1. Reasoning
2. Product overview
3. Quickstart guide

Drop each into `branding/templates/` (or directly into `branding/websites/<domain>/`) and then authors copy and edit for each product/domain. I’ve included helpful microcopy, example code blocks for quickstarts, and instructions for how to use the templates.

---

## 1) Reasoning Lab page template

**File:** `branding/templates/reasoning_lab.md`

````markdown
---
title: "Reasoning Lab — Explore MΛTRIZ Reasoning"
domain: "lukhas.ai"
owner: "@gonzalo"
audience: "general|developers|enterprise"
tone:
  poetic: 0.20
  user_friendly: 0.50
  academic: 0.30
canonical: true
source: "branding/templates/reasoning_lab.md"
variants:
  assistive: "reasoning_lab.assistive.md"
evidence_links: []
claims_verified_by: []
claims_verified_date: null
claims_approval: false
seo:
  title: "Reasoning Lab — MΛTRIZ interactive demo"
  description: "Interactive Reasoning Lab: watch MΛTRIZ build a reasoning chain step-by-step. Public demo, developer playground, and enterprise audit modes available."
last_reviewed: "2025-11-06"
tags: ["reasoning-lab","matriz","demo","interactive"]
---

# Reasoning Lab — Short summary

The Reasoning Lab lets you watch how MΛTRIZ reasons.  
There are 3 modes:
- **Public Demo** — safe, read-only, redacted graphs.
- **Developer Playground** — runnable examples, save & export graphs.
- **Enterprise Audit** — full graphs, signed logs, compliance view (requires approval).

---

## How it works (plain)
1. Enter a short question.  
2. MΛTRIZ builds a reasoning graph. Nodes represent steps (Memory → Attention → Thought → Decision → Awareness).  
3. Click any node for a short explanation and the sources it used.  
4. Export a trace (JSON) or request an audit pack (enterprise).

---

## Modes & what you see

### Public Demo (default)
- Read-only view.  
- Nodes are redacted to protect data; each node has a short explanation.  
- Good for understanding the idea.

### Developer Playground
- Run queries with your API key (lukhas.dev).  
- Inspect full node metadata, performance timings, and small example inputs/outputs.  
- Save and share reproducible reasoning JSON.

### Enterprise Audit
- Full graph with signed logs and Guardian interventions visible.  
- Requires an enterprise role and claims approval to access.

---

## UI affordances (author notes)
- Provide a **"Why?"** button on each node (opens a side panel with explanation, data sources, confidence).  
- Provide keyboard navigation: arrow keys to move nodes, Enter to open details.  
- Provide `Download trace` (JSON), `Share` (link), and `Request audit` (enterprise).

---

## Evidence & limits
- All public demo content is redacted and anonymized.  
- Any production claims visible in Enterprise Audit mode must be backed by evidence in `release_artifacts/` and have `claims_approval: true`.

---

## Assistive variant (summary)
- Provide `reasoning_lab.assistive.md` for Assistive Mode. It must:
  - Offer a **linear step-by-step** view (Memory → Attention → Thought → Decision → Awareness) with 1–2 sentence explanations per step.
  - Include a “Show me the short version” button that reads out the steps.
  - Provide explicit instructions for keyboard users.

*(Authors: create `reasoning_lab.assistive.md` or add `variants.assistive` pointing to a canonical file.)*

---

## Developer examples (quick)
**Example export JSON (truncated)**:
```json
{
  "query":"How to reduce churn?",
  "trace":[
    {"node":"Memory","explain":"pulled customer cohort for 12 months","sources":["db:cohort_2024.json"]},
    {"node":"Attention","explain":"highlighted churn spike months"}
  ],
  "p95_latency_ms": 210
}
````

---

## Reviewer checklist (Reasoning Lab PR)

* [ ] Assistive variant exists and FK grade ≤ 8 for text.
* [ ] Keyboard access tested for graph navigation.
* [ ] Evidence for any numeric claims included and `claims_approval` state set.
* [ ] Public demo redaction policy documented and enforced.
* [ ] GDPR / privacy note added for data uploaded by users.

---

````

---

## 2) Product Page template  
**File:** `branding/templates/product_page.md`

```markdown
---
title: "{{PRODUCT_NAME}}"       # e.g. "MΛTRIZ — Cognitive DNA Engine"
domain: "lukhas.ai"            # or lukhas.dev / lukhas.cloud / lukhas.com
owner: "@product-lead"
audience: "general|developers|enterprise"
tone:
  poetic: 0.25
  user_friendly: 0.45
  academic: 0.30
canonical: true
source: "branding/templates/product_page.md"
variants:
  assistive: "product_page.assistive.md"
evidence_links:
  - "release_artifacts/products/matriz/perf_summary_2025Q3.json"
claims_verified_by:
  - "@web-architect"
claims_verified_date: "2025-11-06"
claims_approval: false
seo:
  title: "{{PRODUCT_NAME}} — LUKHAS"
  description: "{{ONE_LINE_DESC}}"
tags: ["product","matriz","guardian"]
---

# {{PRODUCT_NAME}} — One-line value proposition

**Short subhead**: A concise sentence that explains the primary benefit.

---

## What it is (3–4 short bullets)
- **Core** — one sentence describing the capability.
- **For** — who it is built for.
- **Benefits** — 2–3 direct business or developer benefits.

---

## Key features (card grid)
### Feature 1 — short headline
Short description (12–20 words).  
**Spec**: small bullet with starting input/output shape or behavior.

### Feature 2 — short headline
Short description.

(Repeat 3–6 times)

---

## How it works (brief technical overview)
- Architecture diagram (SVG) — alt text required.  
- Brief data flow: Client → LUKHAS Cloud → MΛTRIZ pipeline (Memory → Attention → Thought → Decision → Awareness) → Result.

---

## Performance & adoption
- **Latency (example):** p95 reasoning latency: `<value>` (link to evidence).  
- **Production scale:** outlets / customers / workloads (link to case studies).

**Note**: Any claim must appear in `evidence_links`.

---

## Integrations & SDKs
- Quick links: `lukhas.dev/quickstart`, `lukhas.io/api`, SDKs (Python, JS, Go).  
- Example code snippet (Python):
```python
from lukhas import MatrizClient
client = MatrizClient(api_key="XXX")
resp = client.pipeline.run(query="Summarize Q3 results", memory_scope="org:ops")
print(resp.answer)
````

---

## Security & Governance

* Short bullets describing Guardian, privacy-by-design, and compliance.
* Link to `lukhas.com/trust` and regional compliance pages (`lukhas.eu`).

---

## Pricing & plans

* Link to pricing; do not include raw confidential enterprise pricing. For public tiers show standard tiers.

---

## Evidence & Resources

* `evidence_links` items.
* Links to docs, SDKs, papers, and case studies.

---

## Assistive variant

* `product_page.assistive.md` should provide a short summary, 3 simple bullets for use cases, and a clear “How to try” section with 1–2 step instructions.

---

## Reviewer checklist (Product page)

* [ ] Evidence links present for every numeric claim.
* [ ] Security & compliance links are up-to-date.
* [ ] Assistive variant exists for critical product pages.
* [ ] Diagrams have alt text and short captions.

````

---

## 3) Quickstart template (5-minute)  
**File:** `branding/templates/quickstart.md`

```markdown
---
title: "{{PRODUCT}} Quickstart — 5 minutes"
domain: "lukhas.dev"
owner: "@developer-lead"
audience: "developers"
tone:
  poetic: 0.10
  user_friendly: 0.30
  academic: 0.60
canonical: true
source: "branding/templates/quickstart.md"
variants:
  assistive: "quickstart.assistive.md"
evidence_links: []
claims_verified_by: []
claims_verified_date: null
claims_approval: false
seo:
  title: "{{PRODUCT}} Quickstart — Lukhas.dev"
  description: "Get up and running with {{PRODUCT}} in 5 minutes with code examples and a runnable demo."
tags: ["quickstart","developers","matriz"]
---

# Quickstart — Get a reasoning chain in 5 minutes

**Goal:** Run a simple query and inspect the reasoning graph.

**Prerequisites**
- Python 3.10+ or Node 18+  
- API key (get from lukhas.dev console)  
- `pip` / `npm` access

---

## Python (5-min)
1. Create & activate virtualenv:
```bash
python3 -m venv venv && source venv/bin/activate
````

2. Install SDK:

```bash
pip install @lukhas/sdk   # example package name; replace with actual
```

3. Run quickstart:

```python
from lukhas import MatrizClient
client = MatrizClient(api_key="YOUR_API_KEY")
response = client.pipeline.run(
    query="Summarize last week's support tickets",
    memory_scope="project:helpdesk"
)
print("Answer:", response.answer)
print("Reasoning trace:", response.trace_summary)  # short summary
```

4. Inspect: Visit the Reasoning Lab and paste the `response.trace_id` into the playground to view step-by-step reasoning.

---

## JavaScript / Node (5-min)

1. Setup:

```bash
npm init -y
npm install @lukhas/sdk
```

2. Example:

```js
import { LukhasClient } from "@lukhas/sdk";
const client = new LukhasClient({ apiKey: process.env.LUKHAS_API_KEY });

const resp = await client.pipeline.run({
  query: "Generate a short summary of project status",
  memoryScope: "project:teamA"
});
console.log("Answer:", resp.answer);
console.log("Trace ID:", resp.traceId);
```

---

## What to expect (explain like small steps)

* You will receive `answer`, `confidence`, and a `traceId`.
* Use `traceId` in the Reasoning Lab to view nodes and sources.
* If you want to reproduce results, include the `memory_scope` and timestamp.

---

## Troubleshooting

* **No output?** Ensure your API key is valid and the `memory_scope` has accessible data.
* **High latency?** Check `p95` data in the response metadata and link to perf evidence.

---

## Assistive variant (quick)

`quickstart.assistive.md` should:

* Use numbered steps with no nested code blocks.
* Provide one-line descriptions under each step.
* Use plain language and explain what the developer should see.

---

## Reviewer checklist (Quickstart)

* [ ] Code examples are minimal, copy-pastable, and executable.
* [ ] SDK package names, commands and environment variables are accurate.
* [ ] Assistive variant exists or is declared.
* [ ] Links to Reasoning Lab and SDK docs included.

---

### How authors should use these templates

1. Copy the template into `branding/websites/<domain>/` (or templates folder).
2. Replace placeholders (e.g., `{{PRODUCT}}`, `{{PAGE_TITLE}}`).
3. Add `homepage.assistive.md` / `product_page.assistive.md` etc. or declare `variants.assistive`.
4. Run local checks:

   ```bash
   python3 tools/branding_vocab_lint.py
   python3 tools/assistive_validate.py
   ```
5. Create PR and request reviews per CODEOWNERS and the checklist.

---
