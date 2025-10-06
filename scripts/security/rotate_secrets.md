---
status: wip
type: documentation
---
# 🔒 LUKHAS AI Secrets Rotation Guide

**Purpose**: Step-by-step procedures for rotating all secrets and API keys in LUKHAS AI systems.

**Security Level**: CRITICAL - Follow procedures exactly, validate each step.

## 🚨 Emergency Rotation (Immediate)

If secrets are compromised or suspected to be exposed:

```bash
# 1. Immediately revoke compromised keys at provider
# 2. Generate new secrets
openssl rand -base64 32  # For 32-byte secrets
openssl rand -base64 64  # For 64-byte secrets

# 3. Update environment variables
export OLD_SECRET="compromised-secret"
export NEW_SECRET="new-secure-secret"

# 4. Deploy immediately
make security-emergency-patch
```

## 📋 Regular Rotation Schedule

### API Keys (Every 90 Days)

#### OpenAI API Key
```bash
# 1. Generate new key at https://platform.openai.com/api-keys
# 2. Test new key
curl -H "Authorization: Bearer $NEW_OPENAI_KEY" \
     https://api.openai.com/v1/models

# 3. Update environment
export OPENAI_API_KEY="new-key-here"

# 4. Update production secrets vault
# AWS: aws secretsmanager update-secret --secret-id openai-api-key
# Azure: az keyvault secret set --vault-name lukhas-vault --name openai-key

# 5. Deploy and verify
make api-serve
curl http://localhost:8080/health

# 6. Revoke old key at OpenAI dashboard
```

#### Anthropic API Key
```bash
# 1. Generate new key at https://console.anthropic.com/
# 2. Test new key
curl -H "Authorization: Bearer $NEW_ANTHROPIC_KEY" \
     -H "anthropic-version: 2023-06-01" \
     https://api.anthropic.com/v1/messages \
     -d '{"model":"claude-3-haiku-20240307","max_tokens":10,"messages":[{"role":"user","content":"test"}]}'

# 3. Update environment and deploy
export ANTHROPIC_API_KEY="new-key-here"
make api-serve && make test

# 4. Update secrets vault
# 5. Revoke old key
```

#### Google API Key
```bash
# 1. Generate new key at https://console.cloud.google.com/apis/credentials
# 2. Test with Gemini API
curl -H "Content-Type: application/json" \
     -d '{"contents":[{"parts":[{"text":"test"}]}]}' \
     "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=$NEW_GOOGLE_KEY"

# 3. Update and deploy
export GOOGLE_API_KEY="new-key-here"
```

### System Secrets (Every 30 Days)

#### JWT Signing Secret
```bash
# 1. Generate new 32-byte secret
NEW_JWT_SECRET=$(openssl rand -base64 32)

# 2. Create migration script
cat > migrate_jwt.py << 'EOF'
import jwt
import os

old_secret = os.getenv("JWT_SECRET_OLD")
new_secret = os.getenv("JWT_SECRET_NEW")

# Decode with old, encode with new for active sessions
# Implementation depends on your JWT handling
EOF

# 3. Coordinate deployment with active sessions
export JWT_SECRET_OLD="$JWT_SECRET"
export JWT_SECRET="$NEW_JWT_SECRET"

# 4. Deploy with dual-key support during transition
make api-serve

# 5. Monitor for 24 hours, then remove old key support
```

#### LUKHAS ID Secret
```bash
# 1. Generate new secret (minimum 32 characters)
NEW_LUKHAS_SECRET=$(openssl rand -base64 48 | tr -d '\n')

# 2. Test secret strength
python3 -c "
secret='$NEW_LUKHAS_SECRET'
print(f'Length: {len(secret)} chars')
print(f'Entropy: {len(set(secret))} unique chars')
assert len(secret) >= 32, 'Too short'
print('✅ Secret meets requirements')
"

# 3. Update environment and deploy
export LUKHAS_ID_SECRET="$NEW_LUKHAS_SECRET"
```

#### Encryption Key
```bash
# ⚠️  CRITICAL: Encryption key rotation requires data migration

# 1. Generate new 32-byte encryption key
NEW_ENCRYPTION_KEY=$(openssl rand -base64 32)

# 2. Create data migration script
cat > migrate_encryption.py << 'EOF'
# Decrypt all sensitive data with old key
# Re-encrypt with new key
# Verify integrity
EOF

# 3. Backup all encrypted data first
make backup-local

# 4. Run migration in maintenance window
python migrate_encryption.py --old-key="$ENCRYPTION_KEY" --new-key="$NEW_ENCRYPTION_KEY"

# 5. Update environment
export ENCRYPTION_KEY="$NEW_ENCRYPTION_KEY"
```

### External Service Tokens (Every 180 Days)

#### GitHub Token
```bash
# 1. Generate new Personal Access Token at https://github.com/settings/tokens
#    Scopes: repo, workflow, read:org

# 2. Test token access
curl -H "Authorization: token $NEW_GITHUB_TOKEN" \
     https://api.github.com/user

# 3. Update environment
export GITHUB_TOKEN="$NEW_GITHUB_TOKEN"

# 4. Test automation
make ci-local

# 5. Revoke old token
```

#### Azure Credentials
```bash
# 1. Generate new service principal
az ad sp create-for-rbac --name "lukhas-ai-rotation-$(date +%Y%m%d)"

# 2. Update environment
export AZURE_CLIENT_ID="new-client-id"
export AZURE_CLIENT_SECRET="new-client-secret"
export AZURE_TENANT_ID="tenant-id"

# 3. Test Azure access
az login --service-principal -u $AZURE_CLIENT_ID -p $AZURE_CLIENT_SECRET --tenant $AZURE_TENANT_ID

# 4. Remove old service principal
az ad sp delete --id "old-client-id"
```

## ✅ Post-Rotation Validation

### Automated Testing
```bash
# 1. Run full test suite
make test

# 2. Run security tests
make security-scan

# 3. Test all API endpoints
make api-serve &
sleep 5
curl http://localhost:8080/health
curl http://localhost:8080/auth/validate
curl http://localhost:8080/consciousness/status

# 4. Test external integrations
python3 -c "
from config.env import get_lukhas_config
config = get_lukhas_config()
assert config.openai_api_key, 'OpenAI key missing'
assert config.anthropic_api_key, 'Anthropic key missing'
print('✅ All keys configured')
"
```

### Manual Verification
```bash
# 1. Check logs for authentication errors
tail -f logs/lukhas.log | grep -i "auth\|error"

# 2. Verify consciousness system functionality
python main.py --consciousness-active --test-mode

# 3. Test Guardian System
python3 -c "
from candidate.governance.guardian_system import GuardianSystem
guardian = GuardianSystem()
result = guardian.validate_operation({'type': 'test'})
print(f'Guardian validation: {result}')
"

# 4. Monitor for 48 hours
```

## 📊 Rotation Log Template

Create entry in `security/rotation_log.md`:

```markdown
## Rotation: YYYY-MM-DD

**Operator**: [Name]
**Reason**: Scheduled rotation / Security incident / Key exposure
**Systems Affected**: [List systems]

### Secrets Rotated
- [ ] OpenAI API Key
- [ ] Anthropic API Key
- [ ] Google API Key
- [ ] JWT Secret
- [ ] LUKHAS ID Secret
- [ ] Encryption Key
- [ ] GitHub Token
- [ ] Azure Credentials

### Validation Results
- [ ] All tests pass
- [ ] Security scan clean
- [ ] API endpoints functional
- [ ] External integrations working
- [ ] No authentication errors in logs
- [ ] 48-hour monitoring complete

**Notes**: [Any issues or special considerations]
```

## 🚨 Rollback Procedures

If issues are detected after rotation:

```bash
# 1. Immediately revert to old secrets
export OPENAI_API_KEY="$OLD_OPENAI_KEY"
export JWT_SECRET="$OLD_JWT_SECRET"
# ... other secrets

# 2. Deploy rollback
make api-serve

# 3. Verify system functionality
make test

# 4. Investigate root cause
tail -100 logs/lukhas.log

# 5. Fix issues and retry rotation
```

## 🛡️ Security Best Practices

### Secret Generation
- **Use cryptographically secure random generators**: `openssl rand`, `/dev/urandom`
- **Minimum entropy**: 256 bits for critical secrets
- **Avoid predictable patterns**: No timestamps, sequential numbers
- **Validate strength**: Check entropy and character distribution

### Storage & Access
- **Never commit secrets to version control**
- **Use secure vaults**: AWS Secrets Manager, Azure Key Vault, HashiCorp Vault
- **Principle of least privilege**: Limit access to secrets
- **Audit access**: Log all secret retrievals
- **Encrypt at rest**: Even in secure vaults

### Rotation Hygiene
- **Document everything**: Every rotation must be logged
- **Test before deploy**: Always validate new secrets work
- **Gradual rollout**: Deploy to staging first
- **Monitor closely**: Watch for errors post-rotation
- **Have rollback ready**: Keep old secrets accessible during transition

### Incident Response
- **Rotate immediately** if compromise suspected
- **Revoke old secrets** as soon as new ones are deployed
- **Audit access logs** to understand scope of exposure
- **Update incident response documentation**

---

**⚠️ CRITICAL**: Never perform secret rotation without proper backup and rollback procedures in place. Always test new secrets in staging environment first.
