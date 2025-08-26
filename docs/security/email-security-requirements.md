# Email Security Requirements for ΛiD Authentication System

## 📧 Overview

This document outlines the email security requirements for the LUKHAS AI ΛiD authentication system, including SPF, DKIM, DMARC configuration, and anti-abuse measures.

## 🛡️ DNS Security Records

### SPF (Sender Policy Framework)
Configure SPF record to authorize sending servers:

```dns
lukhas.ai. IN TXT "v=spf1 include:_spf.google.com include:sendgrid.net ip4:203.0.113.1 -all"
```

#### SPF Configuration Details
- **include:_spf.google.com**: Allow Google Workspace if used
- **include:sendgrid.net**: Allow SendGrid for transactional emails
- **ip4:203.0.113.1**: Allow specific server IP addresses
- **-all**: Hard fail for unauthorized senders (recommended for production)

### DKIM (DomainKeys Identified Mail)
Generate and configure DKIM signing keys:

```bash
# Generate DKIM key pair
openssl genrsa -out dkim-private.pem 2048
openssl rsa -in dkim-private.pem -pubout -out dkim-public.pem

# Extract public key for DNS record
openssl rsa -in dkim-private.pem -pubout -outform DER | base64 -w 0
```

DNS Record:
```dns
auth._domainkey.lukhas.ai. IN TXT "v=DKIM1; k=rsa; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA..."
```

### DMARC (Domain-based Message Authentication, Reporting & Conformance)
Configure DMARC policy for email protection:

```dns
_dmarc.lukhas.ai. IN TXT "v=DMARC1; p=quarantine; rua=mailto:dmarc-reports@lukhas.ai; ruf=mailto:dmarc-failures@lukhas.ai; rf=afrf; pct=100; ri=86400"
```

#### DMARC Policy Details
- **p=quarantine**: Quarantine suspicious emails (use p=reject in production)
- **rua**: Aggregate reports email
- **ruf**: Forensic reports email
- **rf=afrf**: Report format
- **pct=100**: Apply policy to 100% of emails
- **ri=86400**: Report interval (24 hours)

## 🚨 Rate Limiting Configuration

### Email-Based Rate Limits
```typescript
const EMAIL_RATE_LIMITS = {
  // Per email address
  perEmail: {
    windowMs: 60 * 60 * 1000, // 1 hour
    maxAttempts: 3,
    blockDurationMs: 60 * 60 * 1000 // 1 hour block
  },

  // Per IP address
  perIP: {
    windowMs: 60 * 60 * 1000, // 1 hour
    maxAttempts: 5,
    blockDurationMs: 60 * 60 * 1000 // 1 hour block
  },

  // Global rate limit
  global: {
    windowMs: 60 * 1000, // 1 minute
    maxAttempts: 100,
    blockDurationMs: 5 * 60 * 1000 // 5 minute block
  }
};
```

### Anti-Enumeration Protection
```typescript
// Always return the same response regardless of email existence
const SAFE_RESPONSE = {
  message: "If that email address exists in our system, we've sent you a magic link.",
  success: true,
  estimatedDelivery: "2-5 minutes"
};
```

## 📨 SMTP Configuration

### Production SMTP Settings
```bash
# Environment variables for production email
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=SG.your-sendgrid-api-key
SMTP_FROM_NAME=LUKHAS AI
SMTP_FROM_EMAIL=noreply@lukhas.ai

# TLS configuration
SMTP_SECURE=false
SMTP_TLS_CIPHERS=ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS
SMTP_TLS_MIN_VERSION=TLSv1.2
```

### Development SMTP Settings
```bash
# Local development with MailHog
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM_NAME=LUKHAS AI (Dev)
SMTP_FROM_EMAIL=dev@localhost

# Disable TLS for local development
SMTP_SECURE=false
```

## 🔒 Magic Link Security

### Link Generation
```typescript
interface MagicLinkConfig {
  ttlSeconds: number;          // 600 (10 minutes)
  tokenLength: number;         // 32 bytes
  includeTimestamp: boolean;   // true
  includeFingerprint: boolean; // true (IP + User-Agent hash)
}

// Secure token generation
const generateMagicToken = (): string => {
  const timestamp = Date.now().toString();
  const random = crypto.randomBytes(32).toString('hex');
  const fingerprint = hashFingerprint(ip, userAgent);

  return jwt.sign(
    {
      type: 'magic_link',
      timestamp,
      fingerprint,
      random
    },
    JWT_SECRET,
    {
      expiresIn: '10m',
      issuer: 'lukhas.ai',
      audience: 'lukhas.ai'
    }
  );
};
```

### Link Format
```
https://lukhas.ai/auth/verify?token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Security Validations
1. **Token validity**: JWT signature and expiration
2. **Single use**: Token invalidated after use
3. **Fingerprint match**: IP and User-Agent consistency
4. **Time window**: Maximum 10-minute validity
5. **Rate limiting**: Per-email and per-IP limits

## 📊 Email Monitoring

### Delivery Metrics
```typescript
interface EmailMetrics {
  sent: number;
  delivered: number;
  bounced: number;
  rejected: number;
  opened: number;
  clicked: number;
  complained: number;
  unsubscribed: number;
}
```

### Bounce Handling
```typescript
const BOUNCE_TYPES = {
  HARD_BOUNCE: ['invalid', 'mailbox_full', 'unknown_user'],
  SOFT_BOUNCE: ['temporary_failure', 'rate_limited'],
  COMPLAINT: ['spam_complaint', 'abuse_report']
};

// Automatic bounce processing
const handleBounce = async (bounceEvent: BounceEvent) => {
  if (BOUNCE_TYPES.HARD_BOUNCE.includes(bounceEvent.type)) {
    await markEmailAsInvalid(bounceEvent.email);
  }

  if (bounceEvent.type === 'spam_complaint') {
    await addToSuppressionList(bounceEvent.email);
  }
};
```

## 🚫 Suppression List Management

### Automatic Suppression
- Hard bounces
- Spam complaints
- Multiple soft bounces (3+ in 24 hours)
- User unsubscribe requests

### Manual Suppression
```bash
# Add email to suppression list
curl -X POST https://api.lukhas.ai/internal/email/suppress \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "reason": "manual_request"}'
```

## 🔍 Security Monitoring

### Email Security Alerts
```typescript
interface EmailSecurityAlert {
  type: 'rate_limit_exceeded' | 'suspicious_pattern' | 'bounce_spike' | 'dmarc_failure';
  severity: 'low' | 'medium' | 'high' | 'critical';
  email?: string;
  ip?: string;
  count: number;
  timeWindow: string;
  metadata: Record<string, any>;
}
```

### Automated Responses
1. **Rate limit exceeded**: Temporary IP blocking
2. **Suspicious patterns**: Enhanced monitoring
3. **DMARC failures**: Alert security team
4. **Bounce spikes**: Pause email sending

## 📋 Compliance Requirements

### Data Protection
- **GDPR**: Email addresses encrypted at rest
- **CCPA**: Opt-out mechanisms implemented
- **CAN-SPAM**: Unsubscribe links in all emails
- **CASL**: Express consent for Canadian recipients

### Retention Policies
- **Email logs**: 90 days
- **Bounce data**: 365 days
- **Suppression list**: Indefinite (until user requests removal)
- **DMARC reports**: 365 days

## 🧪 Testing Procedures

### Email Deliverability Tests
```bash
# Test SPF record
dig TXT lukhas.ai | grep spf

# Test DKIM record
dig TXT auth._domainkey.lukhas.ai

# Test DMARC record
dig TXT _dmarc.lukhas.ai

# Test email delivery
curl -X POST https://api.lukhas.ai/auth/magic-link \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

### Security Testing
1. **Rate limit testing**: Verify limits are enforced
2. **Enumeration testing**: Confirm responses don't leak information
3. **Token validation**: Test expired/invalid tokens
4. **Bounce handling**: Verify automatic processing

## 📚 Tools and Services

### Recommended Email Services
- **SendGrid**: Transactional email delivery
- **Amazon SES**: Cost-effective option
- **Mailgun**: Developer-friendly API
- **Postmark**: High deliverability focus

### Monitoring Tools
- **MXToolbox**: DNS and deliverability monitoring
- **DMARC Analyzer**: DMARC report analysis
- **Mail-Tester**: Email spam score testing
- **GlockApps**: Inbox placement testing

---

**🔐 SECURITY NOTE**: Email security is critical for authentication systems. Regularly monitor and test all configurations to ensure optimal security and deliverability.
