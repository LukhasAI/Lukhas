---
status: wip
type: documentation
---
# 🎭 LUKHAS AI - 6-Agent Coordination Dashboard

## Active Agents

| Agent | Specialist | Status | Focus Area |
|-------|------------|--------|------------|
| 1 | identity-auth-specialist | 🟢 ACTIVE | ΛID Core, OIDC, WebAuthn |
| 2 | consent-compliance-specialist | 🟢 ACTIVE | Consent Ledger, Policy Engine |
| 3 | adapter-integration-specialist | 🟢 ACTIVE | External APIs, Resilience |
| 4 | context-orchestrator-specialist | 🟢 ACTIVE | Context Bus, Pipelines |
| 5 | ux-feedback-specialist | 🟢 ACTIVE | UI, Transparency, Feedback |
| 6 | testing-devops-specialist | 🟢 ACTIVE | QA, CI/CD, Integration |

## Key Integration Points

### Critical Dependencies
1. **Identity ↔ Consent**: All auth events must generate Λ-trace audit records
2. **Adapters ↔ Consent**: External data access requires consent validation
3. **Orchestrator ↔ Policy**: Every workflow step invokes policy engine
4. **UI ↔ All**: Display status and collect feedback from all components

### Shared Contracts
- **Capability Tokens**: See global_schemas.capability_token_schema
- **Audit Events**: See global_schemas.audit_event_schema

## MVP Demo Scenario
User logs in with passkey → requests 'Summarize my travel documents from Dropbox and Gmail' →
system shows consent prompts → executes multi-step workflow → displays results → collects feedback

## Success Metrics
- ✅ Authentication latency p95 <100ms
- ✅ Context handoff latency <250ms
- ✅ Zero PII leaks
- ✅ Duress gesture compliance
- ✅ All actions logged with Λ-trace

## Coordination Commands

```bash
# View all agent tasks
ls CLAUDE_ARMY/tasks/*_tasks.md

# Check agent workspaces
ls CLAUDE_ARMY/workspaces/

# View deployment logs
cat CLAUDE_ARMY/logs/*/deployment.log

# Run integration tests
pytest tests/integration/test_agent_coordination.py
```

---
*Last Updated: $(date)*
| 7 | special-ops-secrets-kms-legacy | 🟢 ACTIVE | Secrets, KMS, Legacy |
