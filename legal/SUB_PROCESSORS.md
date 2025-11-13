# LUKHAS Sub-Processors List

**Last Updated**: 2025-11-08
**Version**: 1.0

⚠️ **NOTICE**: This list is subject to change with 30 days' advance notice to customers. Customers may object to new sub-processors on reasonable data protection grounds.

---

## 1. CLOUD INFRASTRUCTURE PROVIDERS

### 1.1 Amazon Web Services (AWS)

**Purpose**: Cloud hosting and infrastructure
**Data Categories**: All Personal Data processed through LUKHAS
**Location**: European Union (primary), United States (backup)
**Transfer Mechanism**: EU-US adequacy decision + AWS GDPR DPA
**Security Certifications**: ISO 27001, SOC 2, PCI DSS
**DPA Status**: ✅ Executed
**Last Review**: 2025-01-15

**Contact**: aws-privacy@amazon.com

---

### 1.2 Google Cloud Platform

**Purpose**: Additional cloud infrastructure and analytics processing
**Data Categories**: Usage metrics (pseudonymized), system logs
**Location**: European Union
**Transfer Mechanism**: EU-based processing only
**Security Certifications**: ISO 27001, SOC 2, ISO 27017, ISO 27018
**DPA Status**: ✅ Executed
**Last Review**: 2025-01-15

**Contact**: cloud-privacy@google.com

---

### 1.3 Microsoft Azure

**Purpose**: Backup infrastructure and enterprise deployment options
**Data Categories**: Backup copies of Personal Data (encrypted)
**Location**: European Union
**Transfer Mechanism**: EU-based processing
**Security Certifications**: ISO 27001, SOC 2, ISO 27018
**DPA Status**: ✅ Executed
**Last Review**: 2025-01-15

**Contact**: azureprivacy@microsoft.com

---

## 2. DATABASE AND STORAGE SERVICES

### 2.1 PostgreSQL (Self-Hosted)

**Purpose**: Primary data storage
**Data Categories**: All structured Personal Data
**Location**: EU data centers (AWS/GCP/Azure)
**Transfer Mechanism**: Not applicable (self-hosted)
**Security Certifications**: N/A (infrastructure provider certified)
**DPA Status**: N/A (open-source, self-hosted)
**Last Review**: N/A

**Note**: We maintain direct control over PostgreSQL instances.

---

### 2.2 Redis (Self-Hosted)

**Purpose**: Caching and session management
**Data Categories**: Temporary session data, cache data
**Location**: EU data centers
**Transfer Mechanism**: Not applicable (self-hosted)
**Security Certifications**: N/A (infrastructure provider certified)
**DPA Status**: N/A (open-source, self-hosted)
**Last Review**: N/A

**Note**: We maintain direct control over Redis instances.

---

## 3. SECURITY AND MONITORING

### 3.1 Prometheus (Self-Hosted)

**Purpose**: System monitoring and metrics
**Data Categories**: System metrics (no Personal Data)
**Location**: EU data centers
**Transfer Mechanism**: Not applicable
**Security Certifications**: N/A (self-hosted)
**DPA Status**: N/A
**Last Review**: N/A

**Note**: Prometheus does not process Personal Data.

---

### 3.2 Grafana (Self-Hosted)

**Purpose**: Metrics visualization
**Data Categories**: System metrics (no Personal Data)
**Location**: EU data centers
**Transfer Mechanism**: Not applicable
**Security Certifications**: N/A (self-hosted)
**DPA Status**: N/A
**Last Review**: N/A

**Note**: Grafana does not process Personal Data.

---

## 4. COMMUNICATION SERVICES

### 4.1 SendGrid (Twilio)

**Purpose**: Transactional email delivery
**Data Categories**: Email addresses, email content
**Location**: United States
**Transfer Mechanism**: EU-US Standard Contractual Clauses
**Security Certifications**: SOC 2, ISO 27001
**DPA Status**: ✅ Executed
**Last Review**: 2025-01-15

**Contact**: privacy@sendgrid.com

**Emails Sent**:
- Account verification
- Password reset
- Service notifications
- Security alerts

---

### 4.2 Mailgun

**Purpose**: Alternative email provider (backup)
**Data Categories**: Email addresses, email content
**Location**: European Union
**Transfer Mechanism**: EU-based processing
**Security Certifications**: SOC 2
**DPA Status**: ✅ Executed
**Last Review**: 2025-01-15

**Contact**: privacy@mailgun.com

---

## 5. DEVELOPMENT AND SUPPORT TOOLS

### 5.1 GitHub

**Purpose**: Code repository and version control (internal only)
**Data Categories**: None (public repository, no customer data)
**Location**: United States
**Transfer Mechanism**: Not applicable (no Personal Data)
**Security Certifications**: SOC 2
**DPA Status**: N/A
**Last Review**: N/A

**Note**: Customer data never stored in GitHub.

---

## 6. ANALYTICS (Privacy-Preserving Only)

### 6.1 Internal Analytics (Self-Hosted)

**Purpose**: Usage analytics and service improvement
**Data Categories**: Pseudonymized usage metrics
**Location**: EU data centers
**Transfer Mechanism**: Not applicable (self-hosted)
**Security Certifications**: N/A (self-hosted)
**DPA Status**: N/A
**Last Review**: N/A

**Note**: We do NOT use Google Analytics, Meta Pixel, or third-party tracking services. All analytics are privacy-preserving and self-hosted.

---

## 7. SUB-PROCESSOR UPDATE PROCESS

### 7.1 Adding New Sub-Processors

LUKHAS AI shall:
1. Conduct due diligence on prospective sub-processor
2. Execute Data Processing Agreement with sub-processor
3. Provide **30 days' advance notice** to customers
4. Allow customers to object on reasonable data protection grounds
5. Update this list within 5 business days of engagement

### 7.2 Customer Notification

Customers will be notified via:
- Email to primary contact
- Dashboard notification
- Update to this public list

### 7.3 Customer Objection

Customers may object by:
- Email: privacy@lukhas.ai
- Support ticket
- Account dashboard

**Deadline**: Within 30 days of notification

**Valid Grounds**:
- Non-compliance with GDPR
- Inadequate security measures
- Lack of appropriate safeguards for international transfers
- Conflict with customer's data protection obligations

### 7.4 Resolution

If customer objects:
1. LUKHAS AI will discuss concerns with customer
2. LUKHAS AI will seek alternative sub-processor if possible
3. If no alternative available, customer may terminate Services Agreement

---

## 8. SUB-PROCESSOR MANAGEMENT

### 8.1 Due Diligence

Before engaging any sub-processor, LUKHAS AI:
- Reviews security certifications (ISO 27001, SOC 2 minimum)
- Evaluates data protection practices
- Assesses compliance with GDPR and other regulations
- Reviews subprocessing agreements
- Conducts vendor risk assessment

### 8.2 Contracts

All sub-processors must:
- Execute GDPR-compliant Data Processing Agreement
- Implement appropriate technical and organizational measures
- Allow audit rights
- Notify LUKHAS AI of data breaches within 24 hours
- Return or delete data upon termination

### 8.3 Monitoring

LUKHAS AI:
- Reviews sub-processor security annually
- Monitors compliance through audits and certifications
- Maintains updated contact information
- Tracks DPA renewal dates

---

## 9. CONTACT INFORMATION

**For Sub-Processor Related Questions**:
- Email: privacy@lukhas.ai
- Data Protection Officer: dpo@lukhas.ai
- Phone: [PHONE]

**To Object to a Sub-Processor**:
- Email: privacy@lukhas.ai (Subject: "Sub-Processor Objection")
- Include: Customer name, sub-processor name, grounds for objection

---

**Effective Date**: 2025-11-08
**Next Review**: 2026-01-08 (quarterly)

**Changelog**:
- 2025-11-08: Initial list published
