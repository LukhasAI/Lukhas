# ΛiD Authentication System: Break-Glass Emergency Access Procedure

## 🚨 Overview

This document outlines the emergency access procedures for the LUKHAS AI ΛiD authentication system. Break-glass access is a security measure that allows authorized personnel to bypass normal authentication in critical situations while maintaining full audit trails.

## 🔐 Break-Glass Access Requirements

### Multi-Factor Authentication Requirements
- **Hardware Security Key**: YubiKey or compatible FIDO2 device
- **TOTP**: Time-based One-Time Password (30-second rotation)
- **Emergency Owner Account**: Pre-configured account with break-glass privileges

### Authorization Levels
- **Level 1**: System recovery (service outages)
- **Level 2**: Security incident response
- **Level 3**: Data recovery operations

## 🎯 When to Use Break-Glass Access

### Authorized Use Cases
1. **Authentication Service Outage**: JWT signing keys compromised or lost
2. **Security Incident**: Suspected breach requiring immediate system access
3. **Key Rotation Failure**: JWKS rotation process fails
4. **Emergency Maintenance**: Critical security patches requiring immediate deployment
5. **Data Recovery**: User account recovery when normal processes fail

### Prohibited Use Cases
- Routine administrative tasks
- Normal user support operations
- Development or testing purposes
- Convenience access when normal auth is functional

## 📋 Emergency Access Procedure

### Step 1: Situation Assessment
1. Document the emergency situation
2. Confirm normal authentication is unavailable
3. Verify the emergency meets break-glass criteria
4. Notify security team (if different person)

### Step 2: Access Activation
```bash
# 1. Access the break-glass interface
https://lukhas.ai/auth/break-glass

# 2. Enter emergency owner email
BREAK_GLASS_OWNER_EMAIL=security@lukhas.ai

# 3. Insert hardware security key when prompted
# 4. Enter current TOTP code from authenticator app
```

### Step 3: Identity Verification
1. **Hardware Key Verification**: Touch YubiKey when browser prompts
2. **TOTP Verification**: Enter 6-digit code from authenticator app
3. **IP Verification**: Access must be from pre-authorized IP ranges
4. **Time Verification**: Access limited to business hours (unless Level 3)

### Step 4: Emergency Session
- **Session Duration**: Maximum 4 hours
- **Activity Logging**: All actions logged with video recording (if possible)
- **Witness Requirement**: Second authorized person must be present for Level 2/3 access
- **Justification**: Required documentation of all actions taken

## 🔧 Technical Implementation

### Environment Variables
```bash
# Emergency access configuration
BREAK_GLASS_OWNER_EMAIL=security@lukhas.ai
BREAK_GLASS_HARDWARE_KEY_ID=your-yubikey-credential-id
BREAK_GLASS_TOTP_SECRET=base64-encoded-totp-secret

# Access restrictions
BREAK_GLASS_AUTHORIZED_IPS=203.0.113.1,203.0.113.2
BREAK_GLASS_BUSINESS_HOURS_ONLY=false
BREAK_GLASS_MAX_SESSION_HOURS=4
```

### Key Management
```bash
# Generate new TOTP secret (rotate quarterly)
openssl rand -base64 32 > break-glass-totp.secret

# Register hardware key (WebAuthn)
# Use break-glass registration endpoint with existing emergency access
```

## 🔍 Monitoring and Alerting

### Real-Time Alerts
- **Slack**: `#security-alerts` channel
- **PagerDuty**: Critical incident escalation
- **Email**: Security team distribution list
- **SMS**: Emergency contact numbers

### Alert Content
```json
{
  "alert_type": "break_glass_access",
  "timestamp": "2025-08-19T10:30:00Z",
  "user": "security@lukhas.ai",
  "ip_address": "203.0.113.1",
  "justification": "Authentication service outage - JWT keys compromised",
  "access_level": 2,
  "session_id": "bg-session-abc123"
}
```

## 📊 Audit Requirements

### Required Documentation
1. **Incident Report**: Detailed description of the emergency
2. **Access Log**: Complete record of all actions taken
3. **Justification**: Business reason for break-glass access
4. **Resolution**: Steps taken to resolve the underlying issue
5. **Post-Incident Review**: Analysis and lessons learned

### Audit Trail Elements
- **Access timestamp** (start/end)
- **User identity** (email, hardware key ID)
- **IP address** and geolocation
- **Actions performed** (API calls, database queries)
- **Data accessed** (PII, authentication data)
- **Witnesses present**
- **Incident resolution status**

## 🛡️ Security Controls

### Access Restrictions
- **Geographic**: Limited to authorized countries
- **Network**: Restricted to company IP ranges
- **Time-based**: Business hours only (configurable)
- **Concurrent**: Maximum 1 active break-glass session

### Automated Protections
- **Rate limiting**: Maximum 3 attempts per hour
- **Account lockout**: 24-hour lockout after 3 failed attempts
- **Session recording**: All activities logged for compliance
- **Automatic expiry**: Sessions expire after maximum duration

## 🔄 Key Rotation Schedule

### Emergency Credentials Rotation
- **TOTP Secret**: Every 90 days
- **Hardware Key**: Annually or after security incident
- **Emergency Account**: Password-less (WebAuthn only)
- **Authorized IPs**: Quarterly review

### Rotation Procedure
```bash
# 1. Generate new TOTP secret
NEW_TOTP_SECRET=$(openssl rand -base64 32)

# 2. Update environment configuration
echo "BREAK_GLASS_TOTP_SECRET=$NEW_TOTP_SECRET" >> .env.production

# 3. Configure authenticator app with new secret
# 4. Test break-glass access with new credentials
# 5. Update documentation with new QR code
```

## 📞 Emergency Contact Information

### Primary Contacts
- **Security Team Lead**: security-lead@lukhas.ai
- **CTO**: cto@lukhas.ai
- **Emergency Hotline**: +1-XXX-XXX-XXXX

### Escalation Matrix
1. **Security Team Member** (0-15 minutes)
2. **Security Team Lead** (15-30 minutes)
3. **CTO** (30-60 minutes)
4. **External Security Consultant** (1+ hours)

## 🔍 Testing and Validation

### Monthly Tests
- **Access verification**: Confirm credentials work
- **Alert testing**: Verify monitoring alerts fire
- **Documentation review**: Update contact information
- **Procedure walkthrough**: Practice with team

### Annual Tests
- **Full drill**: Simulate real emergency scenario
- **Credential rotation**: Test full rotation procedure
- **Recovery testing**: Validate system recovery procedures
- **Third-party audit**: External security assessment

## 📚 Related Documentation

- [ΛiD Authentication Architecture](./authentication-architecture.md)
- [Security Incident Response Plan](./incident-response.md)
- [Key Management Procedures](./key-management.md)
- [Audit and Compliance Requirements](./audit-compliance.md)

## ⚖️ Legal and Compliance

### Regulatory Requirements
- **SOC 2 Type II**: Access controls and monitoring
- **ISO 27001**: Information security management
- **GDPR**: Data protection and breach notification
- **CCPA**: Consumer privacy rights

### Audit Evidence
- Break-glass access logs (5-year retention)
- Incident documentation (7-year retention)
- Training records (3-year retention)
- Procedure updates (permanent retention)

---

**⚠️ WARNING**: Break-glass access bypasses normal security controls. Use only in genuine emergencies and follow all documented procedures. Unauthorized or inappropriate use may result in disciplinary action and potential legal consequences.

**🔐 CONFIDENTIAL**: This document contains sensitive security information. Distribute only to authorized personnel with a legitimate business need to know.