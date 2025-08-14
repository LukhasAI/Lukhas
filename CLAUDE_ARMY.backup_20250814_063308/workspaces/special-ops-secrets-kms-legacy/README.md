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
