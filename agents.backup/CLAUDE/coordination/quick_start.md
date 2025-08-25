# 🚀 LUKHAS 6-Agent Quick Start Guide

## Agent Assignments

### 🔑 Identity & Auth (Agent 1)
```bash
# Start with ΛID implementation
cd CLAUDE_ARMY/workspaces/identity-auth-specialist
# Review: CLAUDE_ARMY/tasks/identity-auth-specialist_tasks.md
# Focus: ΛID schema, OIDC provider, WebAuthn
```

### 🛡️ Consent & Compliance (Agent 2)
```bash
# Begin Consent Ledger design
cd CLAUDE_ARMY/workspaces/consent-compliance-specialist
# Review: CLAUDE_ARMY/tasks/consent-compliance-specialist_tasks.md
# Focus: Λ-trace, policy engine, GDPR
```

### 🔗 Service Adapters (Agent 3)
```bash
# Implement Gmail adapter first
cd CLAUDE_ARMY/workspaces/adapter-integration-specialist
# Review: CLAUDE_ARMY/tasks/adapter-integration-specialist_tasks.md
# Focus: OAuth, resilience, telemetry
```

### 🧠 Context Orchestrator (Agent 4)
```bash
# Build context bus foundation
cd CLAUDE_ARMY/workspaces/context-orchestrator-specialist
# Review: CLAUDE_ARMY/tasks/context-orchestrator-specialist_tasks.md
# Focus: Message bus, pipeline manager, policy integration
```

### 🎨 User Experience (Agent 5)
```bash
# Create demo interface
cd CLAUDE_ARMY/workspaces/ux-feedback-specialist
# Review: CLAUDE_ARMY/tasks/ux-feedback-specialist_tasks.md
# Focus: Passkey login, workflow display, feedback
```

### 🧪 Testing & DevOps (Agent 6)
```bash
# Set up test framework
cd CLAUDE_ARMY/workspaces/testing-devops-specialist
# Review: CLAUDE_ARMY/tasks/testing-devops-specialist_tasks.md
# Focus: Integration tests, CI/CD, coordination
```

## Daily Standup Format

### Morning Sync (10 minutes)
1. Each agent updates their task status
2. Identify blockers and dependencies
3. Plan pair programming sessions
4. Update coordination dashboard

### Evening Checkpoint (5 minutes)
1. Commit work to respective workspaces
2. Run integration tests
3. Update progress in task files
4. Note tomorrow's priorities

## Integration Milestones

### Week 1: Foundation
- [ ] ΛID schema defined
- [ ] Consent Ledger schema defined
- [ ] Gmail adapter OAuth working
- [ ] Context bus message passing
- [ ] Basic UI with passkey
- [ ] Test framework initialized

### Week 2: Integration
- [ ] Identity ↔ Consent connected
- [ ] Adapters ↔ Consent validation
- [ ] Orchestrator managing workflows
- [ ] UI displaying workflows
- [ ] Integration tests passing
- [ ] CI/CD pipeline active

### Week 3: Polish
- [ ] Performance optimization
- [ ] Error handling complete
- [ ] Documentation updated
- [ ] Demo scenario tested
- [ ] Feedback system active
- [ ] MVP demo ready

## Command Reference

```bash
# Check all agent tasks
ls CLAUDE_ARMY/tasks/*_tasks.md

# View coordination dashboard
cat CLAUDE_ARMY/tasks/coordination_dashboard.md

# Run integration tests
pytest tests/integration/test_agent_coordination.py

# Check interface contracts
ls CLAUDE_ARMY/coordination/contracts/*.yaml

# View MVP demo plan
cat CLAUDE_ARMY/coordination/mvp_demo_plan.md
```

## Success Metrics
- ✅ All 6 agents have working components
- ✅ Integration tests passing
- ✅ MVP demo runs without errors
- ✅ Performance targets met
- ✅ Compliance validated

---
*Let's build something amazing together!*
