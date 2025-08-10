# Backup Security Hardening

This directory contains AWS security policies and configurations for production-grade backup protection.

## Overview

The security hardening implements:
- **S3 SSE-KMS enforcement**: All backups must use server-side encryption with AWS KMS
- **Least-privilege IAM**: Scoped permissions for OIDC roles
- **TLS-only transport**: Denies non-encrypted connections
- **KPI monitoring**: Visual badge showing backup health status
- **Chaos testing**: Controlled failure testing for alert validation

## S3 Bucket Policy

**File**: `policies/s3_enforce_sse_kms.json`

Apply this policy to enforce:
1. TLS-only connections (denies HTTP)
2. SSE-KMS encryption for all uploads
3. Specific KMS key requirement

### Configuration Required:
- Replace `lukhas-backups-prod` with your bucket name
- Replace `pwm` with your backup prefix
- Replace `REGION:ACCOUNT:key/YOUR-KMS-KEY-ID` with your KMS key ARN

### Apply Policy:
```bash
aws s3api put-bucket-policy --bucket lukhas-backups-prod \
  --policy file://backup/policies/s3_enforce_sse_kms.json
```

## IAM Role Policy

**File**: `policies/iam_role_policy.json`

Provides least-privilege access:
- List objects only under `pwm/` prefix
- Read/write objects only with correct KMS encryption
- KMS operations limited to specific key

### Configuration Required:
- Replace bucket name and prefix
- Replace KMS key ARN
- Attach to your GitHub Actions OIDC role

## KPI Badge System

**Script**: `scripts/kpi_badge.py`

Generates SVG badges showing backup health:
- Green: All backup checks passing (weekly, monthly, quarterly)
- Red: One or more backup checks failing

The badge is automatically updated by DR workflows and committed to the repository.

### Badge Location:
- File: `badges/backup_status.svg`
- URL: `https://raw.githubusercontent.com/<org>/<repo>/main/badges/backup_status.svg`

### Usage in README:
```markdown
![Backup KPI](./badges/backup_status.svg)
```

## Chaos Testing

The weekly DR workflow includes a chaos toggle for testing alert systems:

### Enable Chaos Mode:
Set either:
- Repository variable: `DR_CHAOS=true`
- Repository secret: `DR_CHAOS=true`

When enabled:
- Workflow will use invalid S3 paths
- Triggers controlled failure
- Tests Slack notifications
- Tests GitHub issue creation

### Disable After Testing:
Remove or set to `false` after validating alert systems.

## Security Best Practices

1. **KMS Key Rotation**: Enable automatic key rotation in AWS KMS console
2. **Bucket Versioning**: Enable to protect against accidental deletions
3. **MFA Delete**: Consider enabling for production environments
4. **Access Logging**: Enable S3 access logging for audit trails
5. **Regular Testing**: Run chaos tests quarterly to validate alerts

## Rollout Checklist

- [ ] Update S3 bucket policy with correct values
- [ ] Apply bucket policy to S3
- [ ] Update IAM role policy with correct values  
- [ ] Attach IAM policy to OIDC role
- [ ] Test DR workflow manually
- [ ] Verify badge generation
- [ ] Test chaos mode once
- [ ] Document KMS key ID in secure location

## Monitoring

Monitor these metrics:
- Badge status at `badges/backup_status.svg`
- Workflow runs in GitHub Actions
- S3 bucket metrics in AWS CloudWatch
- KMS key usage in AWS KMS console

## Support

For issues or questions:
- Check GitHub Actions logs
- Review S3 bucket policies in AWS console
- Verify OIDC role permissions
- Check KMS key permissions