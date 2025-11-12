# Privacy Policy
## LUKHAS AI Platform

**Effective Date**: {{EFFECTIVE_DATE}}
**Last Updated**: {{LAST_UPDATED}}
**Domain**: {{DOMAIN}}
**Region**: {{REGION}}

---

## 1. Introduction

LUKHAS AI ("we", "us", "our") respects your privacy and is committed to protecting your personal data. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use the LUKHAS AI platform (the "Service").

### 1.1 Our Commitment
- **Transparency**: Clear disclosure of data practices
- **Data Minimization**: Collect only what's necessary
- **Security**: Industry-standard protection measures
- **User Rights**: Respect your control over your data
- **Compliance**: Adhere to GDPR, CCPA, and applicable regulations

### 1.2 Controller Information
**Data Controller**: {{COMPANY_LEGAL_NAME}}
**Address**: {{STREET_ADDRESS}}, {{CITY}}, {{STATE_PROVINCE}} {{POSTAL_CODE}}, {{COUNTRY}}
{{#IF_EU}}
**Data Protection Officer**: {{DPO_EMAIL}}
{{/IF_EU}}
**Privacy Contact**: {{PRIVACY_EMAIL}}

---

## 2. Information We Collect

### 2.1 Account Information
When you create a Lambda ID (ΛiD), we collect:
- **Identity Data**: Email address, chosen username
- **Tier Assignment**: User tier level (0-5)
- **Authentication Credentials**:
  - Password hashes (never plaintext passwords)
  - WebAuthn public keys (for passkey authentication)
  - Multi-factor authentication tokens
- **Profile Information**: Optional display name, preferences
- **Account Metadata**: Registration date, last login, account status

### 2.2 Usage Data
When you use the Service, we automatically collect:
- **API Activity**: Requests made, endpoints accessed, response times
- **MATRIZ Interactions**: Reasoning queries, cognitive operations performed
- **Session Data**: Session duration, features used, tier transitions
- **Performance Metrics**: Latency measurements, error rates
- **Device Information**: Browser type/version, operating system, IP address
- **Log Data**: Timestamps, user actions, system events

### 2.3 Technical Data
- **Network Information**: IP address, geographic location (country/region)
- **Device Identifiers**: Browser fingerprints (for fraud prevention)
- **Cookies**: Session cookies, preference cookies (see Cookie Policy)
- **Authentication Tokens**: JWT tokens for API access
- **WebAuthn Credentials**: Public key credentials (stored encrypted)

### 2.4 Content Data
- **User Inputs**: Queries submitted to MATRIZ cognitive engine
- **Generated Outputs**: AI-generated responses and reasoning graphs
- **Memory Context**: Conversation history (if memory features enabled)
- **Uploaded Files**: Documents or data you provide for processing
- **Feedback**: Ratings, comments, error reports you submit

### 2.5 Guardian Compliance Data
- **Constitutional Checks**: Records of Guardian ethical compliance checks
- **Violation Logs**: Instances of policy violations (anonymized for analytics)
- **Audit Trails**: System decision logs for transparency and accountability

{{#IF_EU}}
### 2.6 Special Categories of Data
We do NOT intentionally collect sensitive personal data (racial origin, political opinions, health data, etc.). If you submit such data in inputs, we process it only as necessary for Service delivery and delete it per our retention policy.
{{/IF_EU}}

---

## 3. How We Use Your Information

### 3.1 Service Delivery
We use your data to:
- Authenticate you and manage your ΛiD account
- Provide MATRIZ cognitive services and reasoning capabilities
- Enforce tier-based access control and rate limits
- Generate personalized AI responses
- Maintain conversation memory and context
- Process API requests and return responses
- Enable Guardian constitutional compliance checks

### 3.2 Service Improvement
We use aggregated, anonymized data to:
- Improve MATRIZ cognitive algorithms
- Optimize performance (latency, throughput)
- Train and refine AI models
- Develop new features and capabilities
- Analyze usage patterns and trends
- Conduct research and development

### 3.3 Security and Fraud Prevention
We use data to:
- Detect and prevent unauthorized access
- Identify and block malicious activity
- Investigate security incidents
- Enforce our Terms of Service
- Protect against fraud and abuse
- Maintain system integrity

### 3.4 Communication
We may contact you to:
- Send service notifications and updates
- Respond to support requests
- Provide account security alerts
- Share product announcements (opt-out available)
- Notify you of Terms or Policy changes
- Send compliance-required communications

### 3.5 Legal Obligations
We process data when required to:
- Comply with legal obligations
- Respond to lawful government requests
- Enforce our legal rights
- Protect safety and security
- Meet regulatory reporting requirements

{{#IF_EU}}
### 3.6 Legal Basis (GDPR)
Our lawful bases for processing:
- **Consent**: You explicitly agreed (withdrawable)
- **Contract**: Necessary for Service delivery
- **Legitimate Interests**: Service improvement, security, fraud prevention
- **Legal Obligation**: Compliance with laws and regulations
{{/IF_EU}}

---

## 4. Data Sharing and Disclosure

### 4.1 We Do NOT Sell Your Data
We do not sell, rent, or trade your personal information to third parties for marketing purposes.

### 4.2 Service Providers
We share data with trusted service providers who assist with:
- **Cloud Infrastructure**: {{CLOUD_PROVIDER}} (data hosting, compute)
- **Authentication Services**: WebAuthn credential storage providers
- **Analytics**: Aggregated usage analytics (anonymized)
- **Payment Processing**: {{PAYMENT_PROCESSOR}} (for paid tiers)
- **Email Services**: Transactional email delivery
- **Security Tools**: DDoS protection, WAF, intrusion detection

All providers are contractually bound to protect your data and use it only for specified purposes.

### 4.3 Legal Disclosures
We may disclose data when required by:
- Court orders or subpoenas
- Legal processes or law enforcement requests
- National security or regulatory requirements
- Protection of rights, property, or safety

{{#IF_EU}}
### 4.4 International Transfers
For EU users, data is stored in EU data centers. Transfers outside the EU use:
- **Standard Contractual Clauses (SCCs)**: EU-approved transfer mechanisms
- **Adequacy Decisions**: Transfers to countries with adequate protections
- **Binding Corporate Rules**: For intra-company transfers
{{/IF_EU}}

{{#IF_US}}
### 4.4 US State Disclosures
We share data with:
- Service providers (business purposes only)
- Analytics partners (aggregated data)
- No data sales to third parties
{{/IF_US}}

---

## 5. Data Retention

### 5.1 Retention Periods
- **Active Accounts**: Data retained while account active
- **Inactive Accounts**: {{INACTIVE_RETENTION_DAYS}} days of inactivity, then archived
- **Deleted Accounts**: Data deleted within {{DELETION_DAYS}} days
- **Log Data**: Retained for {{LOG_RETENTION_DAYS}} days
- **Security Logs**: Retained for {{SECURITY_LOG_DAYS}} days
- **Legal Hold**: Data preserved longer if required by law

### 5.2 Deletion Procedures
When data is deleted:
- Active databases purged within {{DELETION_DAYS}} days
- Backups overwritten in next {{BACKUP_CYCLE}} cycle
- Anonymized analytics data may be retained indefinitely
- Legal obligations may require extended retention

---

## 6. Your Privacy Rights

{{#IF_EU}}
### 6.1 GDPR Rights (EU Users)
You have the right to:
- **Access**: Request copies of your personal data
- **Rectification**: Correct inaccurate data
- **Erasure**: Request deletion ("right to be forgotten")
- **Restriction**: Limit processing in certain circumstances
- **Portability**: Receive data in machine-readable format
- **Object**: Object to processing based on legitimate interests
- **Withdraw Consent**: Revoke consent at any time (future processing only)
- **Lodge Complaint**: Contact supervisory authority

**Exercise Rights**: Email {{DPO_EMAIL}} or use in-app Privacy Dashboard
**Response Time**: Within 30 days (may extend to 60 days if complex)
{{/IF_EU}}

{{#IF_US}}
### 6.1 CCPA/CPRA Rights (California Users)
You have the right to:
- **Know**: Request disclosure of data collected and shared
- **Access**: Request copies of your personal information
- **Delete**: Request deletion of your data
- **Opt-Out**: Opt out of "sale" of personal information (we don't sell)
- **Correct**: Request correction of inaccurate data
- **Limit Sensitive Data**: Limit use of sensitive personal information
- **Non-Discrimination**: No penalties for exercising rights

**Exercise Rights**: Email {{PRIVACY_EMAIL}} or call {{PRIVACY_PHONE}}
**Response Time**: Within 45 days (may extend to 90 days if complex)
**Free Requests**: Two free requests per 12-month period
{{/IF_US}}

{{#IF_GENERAL}}
### 6.1 General Privacy Rights
Depending on your jurisdiction, you may have rights to:
- Access your personal data
- Request corrections or deletions
- Opt out of certain processing
- Withdraw consent
- Lodge complaints with authorities

**Exercise Rights**: Contact {{PRIVACY_EMAIL}}
{{/IF_GENERAL}}

### 6.2 Account Controls
You can directly:
- Update profile information in account settings
- Delete your account (triggers data deletion)
- Manage WebAuthn passkeys and revoke credentials
- Export your data (JSON format)
- Control communication preferences
- Review API access logs

---

## 7. Data Security

### 7.1 Technical Safeguards
We implement:
- **Encryption in Transit**: TLS 1.3 for all connections
- **Encryption at Rest**: AES-256 for stored data
- **Database Security**: Encrypted databases, access controls
- **Authentication**: WebAuthn passkeys, multi-factor authentication
- **Network Security**: Firewalls, DDoS protection, WAF
- **Access Controls**: Role-based access, principle of least privilege
- **Logging**: Comprehensive audit logs for security monitoring

### 7.2 Organizational Safeguards
- **Security Training**: Regular employee security awareness training
- **Background Checks**: For employees with data access
- **Access Policies**: Strict data access and handling policies
- **Incident Response**: 24/7 security monitoring and incident response
- **Vendor Management**: Security assessments of third-party providers
- **Regular Audits**: Annual security audits and penetration testing

### 7.3 Data Breach Notification
In the event of a data breach:
{{#IF_EU}}
- Notification to supervisory authority within 72 hours (GDPR Article 33)
- Notification to affected users without undue delay if high risk
{{/IF_EU}}
{{#IF_US}}
- Notification to affected users in accordance with applicable state laws
- Notification to regulators as required
{{/IF_US}}
- Notification via email to your registered address
- Public disclosure if broadly affecting users

---

## 8. Cookies and Tracking

### 8.1 Cookies We Use
- **Essential Cookies**: Session management, authentication (required)
- **Preference Cookies**: Remember your settings (optional)
- **Analytics Cookies**: Aggregated usage analytics (optional, anonymized)
- **No Advertising Cookies**: We do not use advertising or tracking cookies

### 8.2 Cookie Controls
- Browser settings to block or delete cookies
- In-app cookie preferences dashboard
- Opt-out of analytics cookies (essential cookies required for functionality)

### 8.3 Do Not Track
We respect browser "Do Not Track" signals by disabling optional analytics cookies.

---

## 9. Children's Privacy

The Service is not intended for users under {{MINIMUM_AGE}} years old. We do not knowingly collect data from children. If you believe we have collected data from a child, contact {{PRIVACY_EMAIL}} and we will promptly delete it.

{{#IF_EU}}
**GDPR Requirement**: Users under 16 require parental consent (or lower age per member state law).
{{/IF_EU}}

---

## 10. AI-Specific Privacy Considerations

### 10.1 MATRIZ Training Data
- User inputs may be used to improve MATRIZ cognitive models
- Training data is aggregated and anonymized
- Opt-out available for sensitive use cases (enterprise tiers)
- Personal identifiers removed before model training

### 10.2 Guardian Transparency
- Guardian compliance checks are logged for transparency
- Compliance reports available in Privacy Dashboard
- Anonymized violation statistics published quarterly

### 10.3 Memory Systems
- Conversation memory is encrypted and isolated by ΛiD
- Memory data is not shared across users
- You can clear conversation memory at any time
- Memory data deleted with account deletion

---

## 11. Regional Variations

{{#IF_EU}}
### 11.1 EU-Specific Provisions
- **Data Residency**: EU data stored in {{EU_DATA_CENTER_LOCATION}}
- **DPO Contact**: {{DPO_EMAIL}}
- **Supervisory Authority**: {{SUPERVISORY_AUTHORITY_NAME}}
- **Cross-Border Transfers**: Via SCCs or adequacy decisions
- **EU AI Act**: Compliance with high-risk AI requirements (when applicable)
{{/IF_EU}}

{{#IF_US}}
### 11.1 US-Specific Provisions
- **CCPA/CPRA**: Full compliance for California residents
- **State Laws**: Compliance with Virginia, Colorado, Connecticut, Utah laws
- **Data Sales**: We do not sell personal information
- **Opt-Out Link**: [Do Not Sell My Personal Information]({{OPT_OUT_LINK}})
{{/IF_US}}

---

## 12. Third-Party Links

The Service may contain links to third-party websites or services. We are not responsible for their privacy practices. Review their privacy policies before providing information.

---

## 13. Changes to This Policy

### 13.1 Notification of Changes
We may update this Privacy Policy. Material changes will be notified via:
- Email to your registered address (30 days advance notice)
- In-app notification
- Website banner on {{DOMAIN}}
- Updated "Last Updated" date at top of policy

### 13.2 Review Requirement
Your continued use after changes constitutes acceptance. Review this policy periodically.

---

## 14. Contact Us

### 14.1 Privacy Inquiries
**Email**: {{PRIVACY_EMAIL}}
{{#IF_EU}}
**Data Protection Officer**: {{DPO_EMAIL}}
{{/IF_EU}}
{{#IF_US}}
**Privacy Hotline**: {{PRIVACY_PHONE}} (toll-free)
{{/IF_US}}

### 14.2 Mailing Address
{{COMPANY_LEGAL_NAME}}
Attention: Privacy Team
{{STREET_ADDRESS}}
{{CITY}}, {{STATE_PROVINCE}} {{POSTAL_CODE}}
{{COUNTRY}}

### 14.3 Supervisory Authority
{{#IF_EU}}
You have the right to lodge a complaint with your local supervisory authority:
**{{SUPERVISORY_AUTHORITY_NAME}}**
{{SUPERVISORY_AUTHORITY_WEBSITE}}
{{/IF_EU}}

---

## 15. Transparency Center

For more information about our privacy practices:
- **Transparency Reports**: Quarterly data request statistics at {{DOMAIN}}/transparency
- **Security Updates**: Security advisories at {{DOMAIN}}/security
- **Data Processing Agreement**: Enterprise DPA available at {{DOMAIN}}/legal/dpa
- **Subprocessors List**: Third-party processors at {{DOMAIN}}/legal/subprocessors

---

## Appendix A: Data Categories Summary

| Category | Examples | Purpose | Retention |
|----------|----------|---------|-----------|
| Identity | Email, ΛiD, username | Authentication, account management | Until deletion |
| Credentials | Password hash, WebAuthn keys | Secure authentication | Until deletion |
| Usage | API calls, sessions | Service delivery, analytics | {{LOG_RETENTION_DAYS}} days |
| Technical | IP, browser, device | Security, fraud prevention | {{LOG_RETENTION_DAYS}} days |
| Content | User inputs, outputs | MATRIZ processing, memory | User-controlled |
| Guardian | Compliance logs | Transparency, auditing | {{AUDIT_RETENTION_DAYS}} days |

---

## Appendix B: Legal Bases (GDPR)

| Processing Activity | Legal Basis |
|---------------------|-------------|
| Account creation & authentication | Contract performance |
| MATRIZ cognitive processing | Contract performance |
| Security & fraud prevention | Legitimate interests |
| Service improvement (anonymized) | Legitimate interests |
| Legal compliance (e.g., tax) | Legal obligation |
| Marketing (if opt-in) | Consent |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | {{VERSION_1_DATE}} | Initial Privacy Policy |
| {{CURRENT_VERSION}} | {{LAST_UPDATED}} | {{RECENT_CHANGES}} |

---

**This Privacy Policy is part of the LUKHAS Multi-Domain Legal Framework. For domain-specific variations, see:**
- *lukhas.eu: EU-specific privacy notice*
- *lukhas.us: US-specific privacy notice*
- *Other domains: International version*

---

**Last Updated**: {{LAST_UPDATED}}
