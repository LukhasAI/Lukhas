# 🔗 LUKHAS Integration Plan - Connecting Agent Code to Main System

## Current Status
✅ **Agents Delivered:** All 7 agents created working modules
✅ **MVP Demo:** Standalone demo proves concept works
⚠️ **Main Integration:** Agent code not yet connected to LUKHAS core

## Integration Tasks Remaining

### Phase 1: Core Module Integration
```python
# 1. Replace core/id.py with Agent 1's lambda_id.py
mv core/id.py core/id_legacy.py
cp CLAUDE_ARMY/workspaces/identity-auth-specialist/src/lambda_id.py core/id.py

# 2. Integrate consent ledger into governance/
cp CLAUDE_ARMY/workspaces/consent-compliance-specialist/src/consent_ledger.py governance/

# 3. Update imports in existing modules
# Update all files importing from core.id to use new ΛID system
```

### Phase 2: Adapter Integration
```python
# Move Agent 3's adapters to bridge/adapters/
mkdir -p bridge/adapters/services
cp CLAUDE_ARMY/workspaces/adapter-integration-specialist/src/* bridge/adapters/services/

# Update bridge/api/api.py to use new adapters
```

### Phase 3: Context Bus Integration
```python
# Replace orchestration/symbolic_kernel_bus.py with Agent 4's context bus
cp CLAUDE_ARMY/workspaces/context-orchestrator-specialist/src/context_bus.py orchestration/

# Update orchestration/brain/primary_hub.py to use new bus
```

### Phase 4: Connect to Existing Systems
```python
# Update these existing modules to use agent code:
- consciousness/unified/auto_consciousness.py → Use new ΛID
- memory/systems/memoria/dreams.py → Use consent ledger
- bridge/api/controllers.py → Use new adapters
- governance/guardian.py → Use policy engine
```

### Phase 5: Legacy Module Migration
```python
# QIM Assessment (Agent 7 responsibility)
- Analyze quantum/ directory
- Determine keep/modernize/retire
- Wrap with capability guards if keeping
```

## Quick Integration Script

```bash
#!/bin/bash
# integrate_agents.sh - Connect agent code to main LUKHAS

echo "🔗 Integrating Agent Code into LUKHAS Core..."

# Backup existing modules
mkdir -p .backups/pre-agent-integration
cp -r core/id* .backups/pre-agent-integration/
cp -r governance/* .backups/pre-agent-integration/

# Phase 1: Core Identity
echo "Installing Agent 1 Identity System..."
cp CLAUDE_ARMY/workspaces/identity-auth-specialist/src/lambda_id.py core/lambda_id.py
echo "from .lambda_id import IdentityService, LukhasID" >> core/__init__.py

# Phase 2: Consent Ledger
echo "Installing Agent 2 Consent System..."
cp CLAUDE_ARMY/workspaces/consent-compliance-specialist/src/consent_ledger.py governance/consent_ledger.py

# Phase 3: Update imports
echo "Updating imports..."
find . -name "*.py" -exec sed -i '' 's/from core.id import/from core.lambda_id import/g' {} \;

echo "✅ Agent code integrated into main LUKHAS"
```

## Validation Checklist

- [ ] Old core/id.py backed up
- [ ] New ΛID system accessible from core
- [ ] Consent ledger integrated in governance
- [ ] Adapters available in bridge
- [ ] Context bus replacing kernel bus
- [ ] All imports updated
- [ ] Tests passing with new modules
- [ ] Demo works with integrated code

## Risk Mitigation

1. **Keep backups** of all replaced modules
2. **Feature flag** new code initially
3. **Run parallel** (old + new) briefly
4. **Gradual migration** not big bang
5. **Test each integration** step

## Next Command

To start integration:
```bash
bash CLAUDE_ARMY/integrate_agents.sh
```

---
*Integration plan ready - agents built the modules, now they need connecting to main LUKHAS*
