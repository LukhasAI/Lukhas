---
module: candidate.core.compliance
star: Supporting
tier: T4_experimental
owner: unassigned
colony: -
manifest_path: manifests/labs/core/compliance/module.manifest.json
matriz: [risk]
---
# candidate.core.compliance

**Star**: Supporting
**MATRIZ Nodes**: risk
**Colony**: -

## What it does
_TODO: short description (2–3 sentences). Add links to demos, notebooks, or dashboards._

## Contracts
- **Publishes**: _e.g., `topic.name@v1`_
- **Subscribes**: _e.g., `topic.other@v1`_
- **Exports**: _e.g., `ClassName`, `function_name()`_

## Observability
- **Spans**: _otlp-span-name_
- **Metrics**: _counter.foo, histogram.bar_
- **Logging**: `candidate.core.compliance: INFO`

## Security
- **Auth**: _OIDC|Token|None_
- **Data classification**: _public|internal|restricted|sensitive_
- **Policies**: _Guardian/North policy refs_

## Tests
- _Add paths under_ `tests/…`
- Coverage target (tier-driven): T1≥70% • T2≥50% • T3≥30% • T4=n/a
