# MATADA Quick Reference for Agents

## 🎖️ Leadership Framework Summary

MATADA implements AGI leadership-grade consciousness architecture with mandatory:
- **Safety-first**: Complete provenance + consent scopes
- **Modularity**: Skill Capsules with `node_out` compliance  
- **Governance**: Audit-ready with tenant/policy tracking
- **Innovation**: Modalityless architecture for all data types

## 📋 Mandatory Node Structure

```json
{
  "version": 1,
  "id": "LT-<trace>#N<index>",
  "type": "HYPOTHESIS|REPLAY|EMOTION|...",
  "state": {
    "confidence": 0.85,
    "salience": 0.7
  },
  "timestamps": {
    "created_ts": 1730000000000
  },
  "provenance": {
    "producer": "module.path",
    "capabilities": ["capability.name"],
    "tenant": "tenant_id", 
    "trace_id": "LT-...",
    "consent_scopes": ["scope.name"]
  }
}
```

## 🛡️ Policy Hard Lines

### Simulation Lane Restrictions
- **ALLOWED**: HYPOTHESIS, REPLAY nodes only
- **FORBIDDEN**: DECISION, AWARENESS nodes
- **ENFORCEMENT**: Schema validation + policy gates

### Step-Up Requirements (GTΨ)
- Privileged actions require step-up authentication
- Duress/shadow flags → immediate denial + Λ-trace
- Policy violations include trace correlation

### Consent & Privacy
- All nodes require consent_scopes in provenance
- Export filtering by consent permissions
- Subject pseudonymization by default

## 🔧 Implementation Checklist

### Skill Capsule Compliance
```python
# Required return format
return {
  "outputs": {...},
  "trace_id": trace_id,
  "node_out": matada_node  # MUST validate against schema
}
```

### Validation Steps
1. Import validation utility: `from MATADA.utils.matada_validate import validate_nodes`
2. Validate before persistence: `validate_nodes([node])`
3. Handle validation errors gracefully
4. Log failures but don't block core operations

### Registry Requirements
- Smoke tests MUST validate `node_out` against schema
- CI fails on missing consent_scopes or confidence/salience
- Performance tracking for node generation latency

## 📊 Node Types Reference

| Category | Types | Use Case |
|----------|-------|----------|
| **Sensory** | SENSORY_IMG, SENSORY_AUD, SENSORY_VID, SENSORY_TOUCH | Input processing |
| **Cognitive** | EMOTION, INTENT, DECISION, CONTEXT, MEMORY, REFLECTION | Core processing |
| **Meta** | CAUSAL, TEMPORAL, AWARENESS | Relationship mapping |
| **Simulation** | HYPOTHESIS, REPLAY | Dream/simulation lane only |
| **Special** | DRM | Digital rights management |

## 🎯 Agent-Specific Guidelines

### Claude Code Agents
- Focus on `node_out` compliance in all Skill Capsules
- Implement schema validation in adapter layers
- Ensure provenance.capabilities match declared capabilities

### ChatGPT Integration  
- Bridge existing outputs to MATADA format
- Maintain consent scope inheritance
- Validate against canonical schema before API return

### Specialized Agents
- Domain-specific node types (follow enum restrictions)
- Proper trace_id propagation across agent calls
- Policy compliance for node type restrictions

## 🚨 Common Pitfalls

1. **Missing Required Fields**: Always include confidence, salience, provenance
2. **Wrong Node Types**: Simulation lane cannot emit DECISION/AWARENESS
3. **Invalid Consent**: Check consent_scopes before node creation
4. **Schema Drift**: Always validate against canonical `matada_node_v1.json`
5. **Trace Correlation**: Maintain trace_id consistency across operations

## 📚 Additional Resources

- **Full Docs**: `../` (files 1.md-7.md with MATADA updates)
- **Schema**: `../../matada_node_v1.json` 
- **Validation**: `../utils/matada_validate.py`
- **Examples**: See implementation guides in main docs

---

*Quick reference for AGI leadership-grade MATADA compliance. Last updated: 2025-08-13.*
