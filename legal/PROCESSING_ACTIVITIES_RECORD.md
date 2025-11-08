# Record of Processing Activities (Article 30 GDPR)

**Organization**: LUKHAS AI
**Role**: Data Controller and Data Processor
**Last Updated**: 2025-11-08
**Responsible Person**: [DPO Name]

---

## PROCESSING ACTIVITIES (As Controller)

### PA-C-001: User Account Management

**Purpose**: User authentication and access control

**Legal Basis**: Contract (Article 6(1)(b))

**Data Categories**:
- Identity: Name, email address, username
- Credentials: Password hash, MFA tokens
- Account: User ID, account status, creation date

**Data Subjects**: Platform users, customers

**Recipients**:
- Internal: Engineering team (limited access)
- External: None (self-hosted)

**International Transfers**: None (EU-only processing)

**Retention Period**: Account lifetime + 30 days after deletion request

**Security Measures**:
- Password hashing (bcrypt)
- Multi-factor authentication
- Encrypted at rest (AES-256)
- Access logging and monitoring

---

### PA-C-002: Customer Billing and Invoicing

**Purpose**: Payment processing and financial records

**Legal Basis**: Contract (Article 6(1)(b)) + Legal Obligation (Article 6(1)(c))

**Data Categories**:
- Financial: Payment method, billing address, transaction history
- Identity: Name, company name, VAT number
- Contact: Email, phone (optional)

**Data Subjects**: Paying customers

**Recipients**:
- Internal: Finance team
- External: Payment processors (Stripe - separate DPA)

**International Transfers**: Yes (Stripe - US, with SCCs)

**Retention Period**: 7 years (legal requirement for financial records)

**Security Measures**:
- PCI DSS compliance (via Stripe)
- Encrypted storage
- Limited access (finance team only)
- Regular audit logs

---

### PA-C-003: Marketing Communications

**Purpose**: Product updates, newsletters, promotional content

**Legal Basis**: Consent (Article 6(1)(a))

**Data Categories**:
- Contact: Email address, name (optional)
- Preferences: Communication preferences, opt-in date

**Data Subjects**: Newsletter subscribers, opted-in users

**Recipients**:
- Internal: Marketing team
- External: Email service provider (SendGrid - DPA executed)

**International Transfers**: Yes (SendGrid - US, with SCCs)

**Retention Period**: Until consent withdrawn + 30 days

**Security Measures**:
- Double opt-in confirmation
- Easy unsubscribe mechanism
- Encrypted storage
- Quarterly list cleaning

---

## PROCESSING ACTIVITIES (As Processor)

### PA-P-001: Reasoning Trace Generation

**Purpose**: Consciousness-inspired AI reasoning for customer applications

**Processing Operations**: Collection, storage, retrieval, analysis, deletion

**Legal Basis**: Customer's legal basis (we process on their behalf)

**Data Categories**:
- Query content (potentially containing personal data)
- Reasoning steps and traces
- Responses generated
- Metadata: Timestamps, user IDs (customer-defined)

**Data Subjects**: End users of customer applications

**Recipients**:
- Internal: Engineering team (troubleshooting only, with customer permission)
- External: None

**International Transfers**: None (EU-only by default)

**Retention Period**: 90 days default, customer-configurable (30-365 days)

**Security Measures**:
- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.3)
- Access controls (customer data isolated)
- Audit logging
- Automatic PII detection and flagging

**Customer Instructions**: Process reasoning queries as per API calls, store traces per retention configuration, delete per schedule

---

### PA-P-002: Memory Fold Persistence

**Purpose**: Context preservation across sessions (Memory Folds)

**Processing Operations**: Collection, storage, retrieval, consolidation, deletion

**Legal Basis**: Customer's legal basis

**Data Categories**:
- Conversation history
- User preferences and context
- Memory fold metadata
- Temporal decay parameters

**Data Subjects**: End users of customer applications

**Recipients**:
- Internal: Engineering team (with customer permission)
- External: None

**International Transfers**: None (EU-only by default)

**Retention Period**: Customer-configurable with biological decay curve

**Security Measures**:
- Encryption at rest (user-controlled keys optional)
- Access controls and isolation
- Granular deletion controls
- Audit logging of all access

**Customer Instructions**: Store memory folds per user preferences, apply temporal decay, delete on user request or schedule

---

### PA-P-003: Analytics and Usage Metrics

**Purpose**: Service improvement and performance monitoring (for customers)

**Processing Operations**: Collection, aggregation, analysis, storage

**Legal Basis**: Customer's legal basis (typically legitimate interest + consent)

**Data Categories**:
- Usage metrics (pseudonymized)
- Performance data
- Feature usage statistics
- Error logs (no personal data)

**Data Subjects**: End users of customer applications

**Recipients**:
- Internal: Engineering and product teams
- External: None (self-hosted analytics only)

**International Transfers**: None

**Retention Period**: 12 months maximum

**Security Measures**:
- Privacy-preserving analytics (differential privacy)
- Pseudonymization and anonymization
- No cross-site tracking
- GDPR-compliant by design

**Customer Instructions**: Collect anonymized usage data per customer configuration, aggregate for analytics, retain per schedule

---

### PA-P-004: Feature Flag Evaluation

**Purpose**: Gradual feature rollouts and A/B testing

**Processing Operations**: Collection, evaluation, storage

**Legal Basis**: Customer's legal basis (typically legitimate interest)

**Data Categories**:
- User ID (pseudonymized)
- Feature flag states
- Evaluation timestamps

**Data Subjects**: End users of customer applications

**Recipients**:
- Internal: Product and engineering teams
- External: None

**International Transfers**: None

**Retention Period**: Feature lifetime + 90 days

**Security Measures**:
- Pseudonymization
- Minimal data collection
- Encrypted storage
- Access controls

**Customer Instructions**: Evaluate feature flags per configuration, log evaluations, delete after feature stabilization

---

## DATA PROTECTION OFFICER (DPO)

**Name**: [DPO_NAME]
**Contact**: dpo@lukhas.ai
**Phone**: [PHONE]
**Address**: [ADDRESS]

---

## SUPERVISORY AUTHORITY

**Authority**: [Relevant supervisory authority based on jurisdiction]
**Contact**: [Authority contact information]
**Website**: [Authority website]

---

## REVIEW AND UPDATE SCHEDULE

**Review Frequency**: Quarterly
**Next Review**: 2026-02-08
**Review Triggers**:
- New processing activities
- Material changes to existing activities
- Regulatory changes
- Data breaches or incidents
- Supervisory authority requests

---

## SUPPORTING DOCUMENTATION

- Data Processing Agreements (DPAs) with customers
- Sub-processor agreements
- Data Protection Impact Assessments (DPIAs)
- Security policies and procedures
- Breach notification procedures
- Data Subject rights procedures

---

**Approved By**:

**Data Protection Officer**:
Signature: _________________________
Date: [DATE]

**Management**:
Signature: _________________________
Name: [NAME], [TITLE]
Date: [DATE]

---

**Version**: 1.0
**Generated**: 2025-11-08
**Classification**: Internal / Confidential
