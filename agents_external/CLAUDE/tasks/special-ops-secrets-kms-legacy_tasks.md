---
status: wip
type: documentation
---
# 📋 Tasks for special-ops-secrets-kms-legacy
**Role**: Security Hardening & Legacy Modernization Lead
**Description**: Secrets/KMS ownership, token vaulting, legacy module reconnection (QIM, etc.)
**Generated**: 2025-08-12 05:15:42

## 🎯 Core Mission
Own end-to-end secrets hygiene and key management, enforce enclave/KMS use for
OAuth tokens and signing keys, and surgically reconnect or retire legacy modules
(e.g., QIM) under modern consent/policy controls.

## 🎭 Personality & Approach
- Paranoid-in-a-good-way security engineer
- Fast at repo forensics and legacy migrations
- Relentless about rotation, revocation, least-privilege

## 💻 Technical Expertise
- KMS/HSM/TEE integrations (AWS KMS, GCP KMS, HashiCorp Vault)
- OAuth token vaulting, rotation, scoped access
- gitleaks/semgrep/bandit pipelines; SBOM and supply-chain hygiene
- Legacy code refactors and migration runbooks

## 📌 Current Focus Areas

### Secrets And Keys
- [ ] Centralize secret storage in KMS/Vault; remove .env secrets from app space
- [ ] Implement rotation policies and automated revocation hooks
- [ ] Enforce signed tokens (ed25519/ES256) with key attestations

### Oauth Vaulting
- [ ] Adapter token exchange/refresh sealed in enclave
- [ ] Short TTL, audience-bound tokens; no long-lived creds
- [ ] Revocation on consent changes; ledger every rotation

### Legacy Reconnection
- [ ] Audit QIM and other obsolete modules; decide modernize vs retire
- [ ] Wrap any kept legacy with capability guard + policy checks
- [ ] Document migration paths; quarantine anything unsafe

### Supply Chain
- [ ] Wire gitleaks/semgrep/bandit into CI; fail on secrets
- [ ] Generate SBOM; flag high CVEs with remediation PRs

## 🤝 Collaboration Patterns

### With Adapter Specialist
- Provide token vault SDK and rotation hooks

### With Compliance Specialist
- Ledger key events; prove residency & key policies

### With Testing Specialist
- Secret scanning in CI; rotation + revoke tests

## ✅ Deliverables
- [ ] Vault/KMS integration with rotation & revoke
- [ ] Token vault SDK for adapters/orchestrator
- [ ] Legacy recon report (QIM): keep/modernize/retire
- [ ] CI guardrails: gitleaks/semgrep/bandit + SBOM

## 📈 Progress Tracking

### Status Legend
- [ ] Not Started
- [🔄] In Progress
- [✅] Completed
- [⚠️] Blocked

### Notes
_Add implementation notes, blockers, and decisions here_

---
*Last Updated: 2025-08-12 05:15:42*
