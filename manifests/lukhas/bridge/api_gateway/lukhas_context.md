---
module: lukhas.bridge.api_gateway
star: Supporting
tier: T3_standard
owner: unassigned
colony: actuation
manifest_path: manifests/lukhas/bridge/api_gateway/module.manifest.json
matriz: [action]
---
# lukhas.bridge.api_gateway

**Star**: Supporting
**MATRIZ Nodes**: action
**Colony**: actuation

## What it does
_TODO: short description (2–3 sentences). Add links to demos, notebooks, or dashboards._

## Contracts
- **Publishes**: _e.g., `topic.name@v1`_
- **Subscribes**: _e.g., `topic.other@v1`_
- **Exports**: _e.g., `ClassName`, `function_name()`_

## Observability
- **Spans**: _otlp-span-name_
- **Metrics**: _counter.foo, histogram.bar_
- **Logging**: `lukhas.bridge.api_gateway: INFO`

## Security
- **Auth**: _OIDC|Token|None_
- **Data classification**: _public|internal|restricted|sensitive_
- **Policies**: _Guardian/North policy refs_

## Tests
- _Add paths under_ `tests/…`
- Coverage target (tier-driven): T1≥70% • T2≥50% • T3≥30% • T4=n/a
