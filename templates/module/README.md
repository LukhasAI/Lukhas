# {{module_title}}

> Status: {{status}} · Constellation: {{constellation}} · Lane: {{lane}}

## Purpose
{{one_sentence_purpose}}

## Capabilities
- {{capability1}}
- {{capability2}}
- {{capability3}}

## Key APIs
{{#each apis}}
- `{{name}}` — {{one_liner}}
{{/each}}

## Interactions
- Upstream: {{upstream_modules}}
- Downstream: {{downstream_modules}}

## Ops
- SLO p95 target: {{p95_target}} ms
- Observed p95: {{p95_observed}} ms ({{observed_at}})
- Coverage target: {{coverage_target}}%
