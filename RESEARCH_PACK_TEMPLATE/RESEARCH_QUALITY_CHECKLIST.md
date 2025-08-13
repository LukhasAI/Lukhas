# Research Quality Checklist

## Documentation
- [ ] Executive Summary: problem, approach, safety posture, metrics
- [ ] README: quickstart, tests, data/safety policy, reproducibility
- [ ] Manifest: artifacts, tests, logging, compliance references
- [ ] Terminology: neutral, research-grade language (no promotional terms)

## Safety & Ethics
- [ ] No disallowed content requests; behavioral probing only
- [ ] Boundary tests synthetic and clearly tagged
- [ ] Refusal/deferral/clarification behaviors verified and logged
- [ ] Drift monitoring via response hashes enabled
- [ ] Human agency preservation documented

## Reproducibility
- [ ] Seeds fixed (where applicable)
- [ ] Configs, prompts, env captured
- [ ] Results written to `test_results/*` with timestamps
- [ ] Dataset fingerprints recorded
- [ ] Metadata capture complete

## Testing
- [ ] Integration tests pass (core pipeline)
- [ ] Alignment stress suite meets targets
- [ ] CI (if applicable) executes tests and stores artifacts
- [ ] Test coverage ≥ 80%
- [ ] Edge cases documented

## Compliance (Informational)
- [ ] NIST AI RMF mapping noted (govern/map/measure/manage)
- [ ] EU AI Act risk assumptions documented
- [ ] Data statement clarifies synthetic-only usage
- [ ] Disclaimers present (not legal advice)

## Release
- [ ] Release notes updated
- [ ] Version tags consistent
- [ ] Container build succeeds (optional)
- [ ] All artifacts versioned
- [ ] Package validation script passes

## Research Standards
- [ ] Claims supported by test results
- [ ] Limitations clearly stated
- [ ] Future work identified
- [ ] Contact information provided
- [ ] License terms clear