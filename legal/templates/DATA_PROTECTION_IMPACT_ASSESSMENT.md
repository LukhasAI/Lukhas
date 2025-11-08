# Data Protection Impact Assessment (DPIA)

**GDPR Article 35 Compliant Template**

⚠️ **LEGAL DISCLAIMER**: This template is for initial structure only and MUST be reviewed by qualified legal counsel and privacy professionals before use.

---

## EXECUTIVE SUMMARY

**Processing Activity**: [NAME_OF_PROCESSING]
**Assessment Date**: [DATE]
**Assessor**: [NAME, TITLE]
**Status**: [Draft | Under Review | Approved]

**Summary of Findings**:
[Brief overview of key risks and mitigations]

---

## 1. PROCESSING DESCRIPTION

### 1.1 Nature, Scope, Context, and Purpose

**What**: [Describe the processing activity]

**Why**: [Business purpose and legal basis]

**How**: [Technical and organizational details]

**Where**: [Geographic locations of processing]

**When**: [Duration and frequency]

### 1.2 Data Flow Diagram

```
[Data Subject] → [Collection] → [Processing] → [Storage] → [Deletion]
                      ↓              ↓             ↓
                 [Consent]    [Security]    [Retention]
```

---

## 2. DATA INVENTORY

### 2.1 Categories of Personal Data

| Category | Data Types | Special Category (Art 9)? |
|----------|-----------|---------------------------|
| Identity Data | Name, email, user ID | No |
| Content Data | Queries, responses | Potentially |
| Usage Data | Timestamps, interactions | No |
| Technical Data | IP address, device info | No |

### 2.2 Data Subjects

- **Primary**: [e.g., Platform users, customers]
- **Secondary**: [e.g., Employees, contractors]
- **Volume**: [Estimated number]

### 2.3 Data Recipients

- Internal: [Teams/departments with access]
- External: [Sub-processors, partners]
- International: [Third countries]

---

## 3. NECESSITY AND PROPORTIONALITY

### 3.1 Necessity Assessment

**Question**: Is the processing necessary for the stated purpose?

**Answer**: [Explanation with justification]

**Alternatives Considered**: [Other approaches evaluated]

**Conclusion**: ☐ Necessary  ☐ Not Necessary

### 3.2 Proportionality Assessment

**Question**: Is the data collected proportionate to the purpose?

**Data Minimization**: [How minimal data is achieved]

**Purpose Limitation**: [How purpose creep is prevented]

**Storage Limitation**: [Retention periods and deletion]

**Conclusion**: ☐ Proportionate  ☐ Not Proportionate

---

## 4. RISK IDENTIFICATION

### 4.1 Risk Matrix

| Risk ID | Risk Description | Likelihood | Impact | Risk Score |
|---------|------------------|------------|--------|------------|
| R001 | Unauthorized access | Medium | High | 6 |
| R002 | Data breach | Low | High | 4 |
| R003 | Function creep | Medium | Medium | 4 |
| R004 | Inadequate deletion | Low | Medium | 3 |
| R005 | Third-party processing | Medium | Medium | 4 |

**Risk Scoring**:
- Likelihood: Low (1), Medium (2), High (3)
- Impact: Low (1), Medium (2), High (3)
- Risk Score: Likelihood × Impact (1-9)

### 4.2 Risk Details

#### R001: Unauthorized Access to Personal Data

**Description**: Personnel or external actors gain unauthorized access to personal data.

**Likelihood**: Medium (appropriate controls in place, but risk exists)

**Impact**: High (could affect multiple data subjects, sensitive data)

**Data Subjects Affected**: All users of the system

**Consequences**:
- Privacy violation
- Identity theft potential
- Reputational damage
- Regulatory penalties

---

## 5. RISK MITIGATION MEASURES

### 5.1 Mitigation Strategy

| Risk ID | Mitigation Measure | Responsibility | Status | Residual Risk |
|---------|-------------------|----------------|--------|---------------|
| R001 | MFA + RBAC + Audit logs | Security Team | Implemented | 2 (Low) |
| R002 | Encryption + Monitoring | Security Team | Implemented | 2 (Low) |
| R003 | Purpose limitation policy | DPO | Implemented | 2 (Low) |
| R004 | Automated deletion rules | Engineering | Implemented | 1 (Low) |
| R005 | Sub-processor DPAs | Legal | Ongoing | 2 (Low) |

### 5.2 Technical Safeguards

- **Encryption**: AES-256 at rest, TLS 1.3 in transit
- **Access Control**: RBAC with least privilege
- **Authentication**: Multi-factor authentication mandatory
- **Monitoring**: 24/7 security monitoring and alerting
- **Backup**: Encrypted backups with tested recovery

### 5.3 Organizational Safeguards

- **Policies**: Data protection policies and procedures
- **Training**: Regular privacy and security training
- **Audits**: Annual third-party audits
- **DPO**: Dedicated Data Protection Officer
- **Incident Response**: Documented IR procedures

---

## 6. DATA SUBJECT CONSULTATION

### 6.1 Consultation Approach

**Method**: [e.g., User surveys, privacy notice review, stakeholder feedback]

**Date**: [DATE]

**Participants**: [Number and description]

### 6.2 Feedback Summary

**Concerns Raised**:
- [Concern 1]
- [Concern 2]
- [Concern 3]

**How Addressed**:
- [Response to concern 1]
- [Response to concern 2]
- [Response to concern 3]

---

## 7. SUPERVISORY AUTHORITY CONSULTATION

### 7.1 Prior Consultation Required?

**Question**: Does processing involve high risk despite mitigation measures?

**Answer**: ☐ Yes, prior consultation required
            ☒ No, residual risk is acceptable

**Justification**: [Explanation of decision]

### 7.2 If Consultation Required

**Authority**: [Name of supervisory authority]
**Date Consulted**: [DATE]
**Response**: [Summary of authority's response]
**Additional Measures**: [Any required changes]

---

## 8. ACCOUNTABILITY AND SIGN-OFF

### 8.1 Roles and Responsibilities

- **Processing Owner**: [NAME, TITLE]
- **DPIA Assessor**: [NAME, TITLE]
- **Data Protection Officer**: [NAME]
- **Security Officer**: [NAME]
- **Legal Counsel**: [NAME]

### 8.2 Review Schedule

**Initial Assessment**: [DATE]
**Next Review**: [DATE + 12 months]
**Review Triggers**:
- Material changes to processing
- New risks identified
- Regulatory changes
- Data breach incidents

### 8.3 Sign-Off

**DPO Approval**:
Signature: _________________________
Name: [NAME]
Date: [DATE]

**Processing Owner Approval**:
Signature: _________________________
Name: [NAME]
Date: [DATE]

---

## APPENDIX A: LUKHAS PROCESSING ACTIVITIES

### A.1 Reasoning Trace Storage

**Purpose**: Enable consciousness-inspired reasoning and debugging

**Data Categories**: User queries, system responses, reasoning steps

**Legal Basis**: Legitimate interest (service provision)

**Retention**: 90 days default, user-configurable

**Risks**:
- Queries may contain sensitive information
- Reasoning traces could reveal user patterns

**Mitigations**:
- User control over retention period
- Automatic PII detection and flagging
- Encryption at rest
- Access logging

**Residual Risk**: Low (2/9)

### A.2 Memory Fold Persistence

**Purpose**: Context preservation across sessions (Memory Folds)

**Data Categories**: Interaction history, user preferences, context data

**Legal Basis**: Consent + Legitimate interest

**Retention**: User-configurable, with temporal decay (Ebbinghaus curve)

**Risks**:
- Long-term storage of personal data
- Potential for outdated data
- Memory could contain sensitive information

**Mitigations**:
- Explicit consent for memory storage
- Biological forgetting curve (automatic decay)
- User dashboard for memory management
- Granular deletion controls
- Encryption with user-controlled keys

**Residual Risk**: Low (2/9)

### A.3 Analytics and Telemetry

**Purpose**: Service improvement and performance monitoring

**Data Categories**: Usage metrics, performance data (pseudonymized)

**Legal Basis**: Legitimate interest + Consent

**Retention**: 12 months maximum

**Risks**:
- Re-identification of pseudonymized data
- Privacy leakage through analytics

**Mitigations**:
- Privacy-preserving analytics (differential privacy)
- Pseudonymization and anonymization
- Opt-out available
- No cross-site tracking
- GDPR-compliant analytics only

**Residual Risk**: Low (1/9)

---

## APPENDIX B: RISK TREATMENT PLAN

| Risk ID | Deadline | Owner | Budget | Status |
|---------|----------|-------|--------|--------|
| R001 | Implemented | CISO | €50K | ✅ Complete |
| R002 | Implemented | CISO | €30K | ✅ Complete |
| R003 | Implemented | DPO | €10K | ✅ Complete |
| R004 | Implemented | CTO | €20K | ✅ Complete |
| R005 | Ongoing | Legal | €15K/yr | 🔄 Active |

---

**Generated**: 2025-11-08
**Version**: 1.0
**Template Only - Requires Privacy Professional Review**
