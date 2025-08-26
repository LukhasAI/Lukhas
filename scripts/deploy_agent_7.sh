#!/bin/bash

# 🔐 Deploy Agent 7: Special Ops - Secrets, KMS & Legacy Recon
# Adds the security hardening specialist to the existing 6-agent army

set -e

echo "=================================================="
echo "🔐 Deploying Agent 7: Special Ops Specialist"
echo "=================================================="
echo ""

CLAUDE_CONFIG="scripts/Claude_7.yml"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
TASK_DIR="CLAUDE_ARMY/tasks"
WORKSPACE_DIR="CLAUDE_ARMY/workspaces/special-ops-secrets-kms-legacy"

# Create workspace for Agent 7
echo "📁 Creating Agent 7 workspace..."
mkdir -p "${WORKSPACE_DIR}/src"
mkdir -p "${WORKSPACE_DIR}/tests"
mkdir -p "${WORKSPACE_DIR}/docs"
mkdir -p "${WORKSPACE_DIR}/tools"

# Extract Agent 7 tasks
echo "📋 Extracting Agent 7 tasks..."
python3 -c "
import yaml
from datetime import datetime

with open('${CLAUDE_CONFIG}', 'r') as f:
    config = yaml.safe_load(f)

agent = config.get('agent_7', {})
task_file = '${TASK_DIR}/special-ops-secrets-kms-legacy_tasks.md'

with open(task_file, 'w') as f:
    # Header
    f.write('# 📋 Tasks for special-ops-secrets-kms-legacy\\n')
    f.write(f\"**Role**: {agent.get('role', 'Not specified')}\\n\")
    f.write(f\"**Description**: {agent.get('description', 'Not specified')}\\n\")
    f.write(f\"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n\\n\")

    # Core Mission
    f.write('## 🎯 Core Mission\\n')
    f.write(agent.get('core_mission', 'No mission defined').strip() + '\\n\\n')

    # Personality
    if 'personality' in agent:
        f.write('## 🎭 Personality & Approach\\n')
        for trait in agent['personality']:
            f.write(f'- {trait}\\n')
        f.write('\\n')

    # Technical Expertise
    if 'technical_expertise' in agent:
        f.write('## 💻 Technical Expertise\\n')
        for skill in agent['technical_expertise']:
            f.write(f'- {skill}\\n')
        f.write('\\n')

    # Focus Areas
    if 'current_focus_areas' in agent:
        f.write('## 📌 Current Focus Areas\\n')
        for area, items in agent['current_focus_areas'].items():
            f.write(f'\\n### {area.replace(\"_\", \" \").title()}\\n')
            for item in items:
                f.write(f'- [ ] {item}\\n')
        f.write('\\n')

    # Collaboration
    if 'collaboration_patterns' in agent:
        f.write('## 🤝 Collaboration Patterns\\n')
        for partner, items in agent['collaboration_patterns'].items():
            f.write(f'\\n### {partner.replace(\"_\", \" \").title()}\\n')
            for item in items:
                f.write(f'- {item}\\n')
        f.write('\\n')

    # Deliverables
    if 'deliverables' in agent:
        f.write('## ✅ Deliverables\\n')
        for deliverable in agent['deliverables']:
            f.write(f'- [ ] {deliverable}\\n')
        f.write('\\n')

    # Progress Tracking
    f.write('## 📈 Progress Tracking\\n\\n')
    f.write('### Status Legend\\n')
    f.write('- [ ] Not Started\\n')
    f.write('- [🔄] In Progress\\n')
    f.write('- [✅] Completed\\n')
    f.write('- [⚠️] Blocked\\n\\n')
    f.write('### Notes\\n')
    f.write('_Add implementation notes, blockers, and decisions here_\\n\\n')
    f.write('---\\n')
    f.write(f\"*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\\n\")

print('✅ Created task file: ' + task_file)
"

# Create Agent 7 README
cat > "${WORKSPACE_DIR}/README.md" << 'EOF'
# 🔐 Special Ops: Secrets, KMS & Legacy Recon Specialist

## Agent: special-ops-secrets-kms-legacy

This workspace is for the Special Ops specialist to implement security hardening and legacy modernization.

### 🎯 Core Responsibilities
- End-to-end secrets hygiene and key management
- KMS/Vault integration for OAuth tokens and signing keys
- Legacy module reconnaissance and modernization (QIM, etc.)
- Supply chain security and CI guardrails

### 🔑 Key Focus Areas
1. **Secrets & Keys**: Centralize in KMS/Vault, rotation policies, signed tokens
2. **OAuth Vaulting**: Enclave-sealed tokens, short TTL, consent-based revocation
3. **Legacy Recon**: Audit QIM and obsolete modules, modernize or retire
4. **Supply Chain**: gitleaks/semgrep/bandit in CI, SBOM generation

### 📁 Workspace Structure
```
special-ops-secrets-kms-legacy/
├── src/
│   ├── kms/           # KMS integration modules
│   ├── vault/         # Token vault implementation
│   ├── legacy/        # Legacy module wrappers
│   └── scanners/      # Security scanning tools
├── tests/
│   ├── rotation/      # Key rotation tests
│   ├── revocation/    # Token revocation tests
│   └── security/      # Security scan tests
├── docs/
│   ├── kms_setup.md   # KMS configuration guide
│   ├── legacy_map.md  # Legacy module mapping
│   └── runbooks/      # Operational runbooks
└── tools/
    ├── gitleaks.yml   # Secret scanning config
    ├── semgrep.yml    # Code analysis rules
    └── sbom.py        # SBOM generator
```

### 🤝 Collaboration Points
- **With Adapters**: Provide token vault SDK and rotation hooks
- **With Compliance**: Ledger key events, prove residency & policies
- **With Testing**: Secret scanning in CI, rotation/revoke tests

### 🛡️ Security Principles
- **Zero Trust**: Never trust, always verify
- **Least Privilege**: Minimal permissions by default
- **Defense in Depth**: Multiple layers of security
- **Fail Secure**: Default deny on errors

### 📊 Success Metrics
- Zero secrets in codebase (gitleaks clean)
- 100% OAuth tokens vaulted
- All keys rotated < 90 days
- Legacy modules wrapped or retired
- SBOM generated with no critical CVEs

### Status
- Created: $(date)
- Status: ACTIVE
- Priority: HIGH (Security Critical)
EOF

echo "✅ Agent 7 workspace created"
echo ""

# Create security tools templates
echo "🛠️ Creating security tool templates..."

# Gitleaks config
cat > "${WORKSPACE_DIR}/tools/gitleaks.yml" << 'EOF'
# Gitleaks configuration for LUKHAS
title: "LUKHAS Secret Detection"
allowlist:
  paths:
    - 'test_data/'
    - '*.test.py'
  regexes:
    - 'example_'
    - 'mock_'
    - 'test_'

rules:
  - id: openai_api_key
    description: OpenAI API Key
    regex: 'sk-[a-zA-Z0-9]{48}'
    tags: ["key", "openai"]

  - id: anthropic_api_key
    description: Anthropic API Key
    regex: 'sk-ant-[a-zA-Z0-9]{40,}'
    tags: ["key", "anthropic"]

  - id: oauth_token
    description: OAuth Bearer Token
    regex: 'Bearer\s+[a-zA-Z0-9\-\._~\+\/]+=*'
    tags: ["token", "oauth"]
EOF

# Semgrep rules
cat > "${WORKSPACE_DIR}/tools/semgrep.yml" << 'EOF'
rules:
  - id: hardcoded-secret
    pattern: |
      $KEY = "..."
    pattern-either:
      - pattern: API_KEY = "..."
      - pattern: SECRET = "..."
      - pattern: TOKEN = "..."
    message: "Hardcoded secret detected"
    severity: ERROR

  - id: unsafe-deserialization
    pattern: pickle.loads(...)
    message: "Unsafe deserialization detected"
    severity: ERROR

  - id: sql-injection
    pattern: |
      "SELECT * FROM ... WHERE " + $INPUT
    message: "Potential SQL injection"
    severity: ERROR
EOF

# SBOM generator
cat > "${WORKSPACE_DIR}/tools/sbom.py" << 'EOF'
#!/usr/bin/env python3
"""
Generate Software Bill of Materials (SBOM) for LUKHAS
"""
import json
import subprocess
from datetime import datetime

def generate_sbom():
    """Generate SBOM in SPDX format"""
    sbom = {
        "spdxVersion": "SPDX-2.3",
        "creationInfo": {
            "created": datetime.now().isoformat(),
            "creators": ["Tool: lukhas-sbom-generator"]
        },
        "name": "LUKHAS AI System",
        "packages": []
    }

    # Get Python dependencies
    result = subprocess.run(
        ["pip", "freeze"],
        capture_output=True,
        text=True
    )

    for line in result.stdout.split('\n'):
        if '==' in line:
            name, version = line.split('==')
            sbom["packages"].append({
                "name": name,
                "version": version,
                "supplier": "PyPI"
            })

    return sbom

if __name__ == "__main__":
    sbom = generate_sbom()
    with open("sbom.json", "w") as f:
        json.dump(sbom, f, indent=2)
    print("✅ SBOM generated: sbom.json")
EOF

chmod +x "${WORKSPACE_DIR}/tools/sbom.py"
echo "✅ Security tools created"
echo ""

# Update coordination dashboard
echo "📊 Updating coordination dashboard..."
sed -i '' 's/6 agents/7 agents/g' CLAUDE_ARMY/tasks/coordination_dashboard.md 2>/dev/null || true

# Add Agent 7 to dashboard
cat >> CLAUDE_ARMY/tasks/coordination_dashboard.md << 'EOF'
| 7 | special-ops-secrets-kms-legacy | 🟢 ACTIVE | Secrets, KMS, Legacy |
EOF

echo "✅ Coordination dashboard updated"
echo ""

# Create integration points document
cat > "${WORKSPACE_DIR}/docs/integration_points.md" << 'EOF'
# 🔐 Agent 7 Integration Points

## Critical Dependencies

### 1. Adapter Integration (Agent 3)
- **Provide**: Token vault SDK
- **Receive**: OAuth token requirements
- **Deliverable**: `sdk/token_vault.py`

### 2. Compliance Integration (Agent 2)
- **Provide**: Key event logs
- **Receive**: Policy requirements
- **Deliverable**: Key rotation audit trail

### 3. Testing Integration (Agent 6)
- **Provide**: Security scan configs
- **Receive**: CI pipeline hooks
- **Deliverable**: CI security gates

## Implementation Priority

### Week 1: Foundation
1. Set up HashiCorp Vault or AWS KMS
2. Create token vault SDK
3. Implement gitleaks in CI

### Week 2: Integration
1. Integrate vault SDK with adapters
2. Implement key rotation policies
3. Audit QIM and legacy modules

### Week 3: Hardening
1. Complete SBOM generation
2. Red team security tests
3. Document all security procedures

## Security Checklist
- [ ] No secrets in .env files
- [ ] All OAuth tokens vaulted
- [ ] Key rotation < 90 days
- [ ] gitleaks/semgrep passing
- [ ] SBOM generated
- [ ] Legacy modules assessed
- [ ] Red team tests passing
EOF

echo ""
echo "=================================================="
echo "✨ AGENT 7 DEPLOYMENT COMPLETE!"
echo "=================================================="
echo ""
echo "🔐 Special Ops Specialist Added:"
echo "--------------------------------"
echo "• Workspace: ${WORKSPACE_DIR}"
echo "• Tasks: ${TASK_DIR}/special-ops-secrets-kms-legacy_tasks.md"
echo "• Security Tools: ${WORKSPACE_DIR}/tools/"
echo ""
echo "🎯 Agent 7 Focus Areas:"
echo "----------------------"
echo "1. Secrets & KMS Integration"
echo "2. OAuth Token Vaulting"
echo "3. Legacy Module Recon (QIM)"
echo "4. Supply Chain Security"
echo ""
echo "📋 Micro-Additions Applied to:"
echo "-----------------------------"
echo "• Agent 2: +Refusal templates, jailbreak hygiene"
echo "• Agent 3: +Central capability scope registry"
echo "• Agent 4: +Rate limiter, circuit breaker metrics"
echo "• Agent 6: +Red team security tests"
echo ""
echo "🚀 Your 7-Agent Army is now complete!"
echo "=================================================="
