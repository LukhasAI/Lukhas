# Terms of Service
## LUKHAS AI Platform

**Effective Date**: 2025-01-15
**Last Updated**: 2025-11-12
**Domain**: lukhas.eu
**Region**: European Union

---

## 1. Agreement to Terms

By accessing and using the LUKHAS AI platform (the "Service") provided by LUKHAS AI ("we", "us", "our"), you acknowledge that you have read, understood, and agree to be bound by these Terms of Service ("Terms"). If you do not agree to these Terms, do not use the Service.

### 1.1 Governing Law

These Terms are governed by the laws of the European Union and Netherlands. All disputes shall be resolved in accordance with EU regulations including GDPR and the EU AI Act.

---

## 2. Service Description

### 2.1 LUKHAS AI Platform
LUKHAS AI is a cognitive architecture platform implementing the MATRIZ framework (Memory, Attention, Thought, Action, Decision, Awareness) for transparent and explainable AI operations.

### 2.2 Identity System
Our platform uses the Lambda ID (ΛiD) authentication system with tier-based access control:
- **Tier 0 (GUEST)**: Public access to documentation and basic features
- **Tier 1 (VISITOR)**: Registered users with rate-limited API access
- **Tier 2 (FRIEND)**: Verified users with extended session capabilities
- **Tier 3 (TRUSTED)**: Multi-factor authenticated users with elevated privileges
- **Tier 4 (INNER_CIRCLE)**: Administrative capabilities
- **Tier 5 (ROOT_DEV)**: Full system access (LUKHAS team only)

### 2.3 Service Components
The Service includes:
- **Identity Management**: ΛiD authentication and authorization
- **MATRIZ Cognitive Engine**: Transparent reasoning and decision-making
- **Guardian System**: Constitutional AI compliance and ethical enforcement
- **Memory Systems**: Persistent context and state management
- **API Access**: Programmatic access to LUKHAS capabilities
- **Documentation**: Technical guides and reference materials

---

## 3. Account Registration and Security

### 3.1 Account Creation
To access certain features, you must create an account with a valid Lambda ID. You agree to:
- Provide accurate, current, and complete information
- Maintain and promptly update your account information
- Maintain the security of your authentication credentials
- Accept responsibility for all activities under your account

### 3.2 WebAuthn/Passkey Support
We support WebAuthn passkey authentication for enhanced security. When enabled:
- Your passkey is stored locally on your device
- We store only public key credentials (never private keys)
- You can manage and revoke credentials at any time
- Multi-device passkey synchronization is available through your operating system

### 3.3 Account Termination
We reserve the right to suspend or terminate accounts that:
- Violate these Terms
- Engage in fraudulent or malicious activity
- Abuse system resources or rate limits
- Violate third-party rights
- Threaten system security or stability

---

## 4. Acceptable Use Policy

### 4.1 Permitted Use
You may use the Service for:
- Legitimate AI development and research
- Building applications with LUKHAS APIs
- Testing and evaluating MATRIZ capabilities
- Educational and learning purposes
- Commercial applications (subject to licensing terms)

### 4.2 Prohibited Activities
You may NOT:
- Reverse engineer, decompile, or disassemble the Service
- Circumvent authentication, rate limiting, or tier restrictions
- Use the Service for illegal purposes or to violate third-party rights
- Attempt to gain unauthorized access to systems or data
- Engage in denial-of-service attacks or resource abuse
- Misrepresent yourself or your affiliation
- Violate export control or sanctions regulations
- Use the Service to train competing AI models without permission
- Submit malicious code, malware, or exploits
- Scrape or harvest data without authorization

### 4.3 AI-Specific Restrictions
When using LUKHAS AI capabilities:
- Do not attempt to manipulate Guardian compliance checks
- Do not use outputs to harm individuals or groups
- Do not generate or promote illegal content
- Respect intellectual property in training data and outputs
- Comply with applicable AI regulations (EU AI Act, etc.)

---

## 5. Intellectual Property

### 5.1 LUKHAS Ownership
LUKHAS AI retains all rights, title, and interest in:
- The MATRIZ cognitive architecture
- Lambda ID (ΛiD) authentication system
- Guardian constitutional AI framework
- LUKHAS branding, trademarks, and logos
- Platform source code and algorithms
- Documentation and technical specifications
- All improvements and derivatives

### 5.2 User Content
You retain ownership of content you submit to the Service. By submitting content, you grant us:
- A worldwide, non-exclusive, royalty-free license
- To process, store, and analyze your content
- To improve Service quality and capabilities
- To generate aggregated, anonymized statistics

### 5.3 Open Source
Certain components may be provided under open source licenses. Those licenses govern your use of those specific components and take precedence over these Terms for those components.

### 5.4 Trademark Usage
Use of LUKHAS trademarks requires our prior written approval. See our Brand Guidelines for permitted uses.

---

## 6. Privacy and Data Protection

### 6.1 Data Collection
We collect and process data as described in our Privacy Policy. Key principles:
- **Transparency**: Clear disclosure of data practices
- **Minimization**: Collect only necessary data
- **Security**: Implement industry-standard protections
- **User Rights**: Respect access, deletion, and portability rights

### 6.2 GDPR Compliance
For EU users, we comply with GDPR requirements:
- **Lawful basis**: Consent, contract performance, legitimate interests
- **Data residency**: EU data stored in EU data centers
- **DPO contact**: dpo@lukhas.eu
- **User rights**: Access, rectification, erasure, portability, objection
- **Response time**: User rights requests processed within 30 days
- **Data breaches**: Notification within 72 hours per GDPR Article 33

### 6.3 Data Security
We implement:
- Encryption in transit (TLS 1.3)
- Encryption at rest (AES-256)
- Secure authentication (WebAuthn, passkeys)
- Regular security audits and penetration testing
- Incident response procedures

---

## 7. Service Availability and Performance

### 7.1 Availability Targets
We strive for:
- **Uptime**: 99.9% availability (excluding planned maintenance)
- **Latency**: P95 reasoning latency < 250ms
- **Throughput**: ≥50 operations/second per user tier
- **Maintenance windows**: Announced 48 hours in advance

### 7.2 No Warranty
THE SERVICE IS PROVIDED "AS IS" WITHOUT WARRANTIES OF ANY KIND, EXPRESS OR IMPLIED. WE DO NOT GUARANTEE:
- Uninterrupted or error-free operation
- Specific performance benchmarks in all scenarios
- Compatibility with all systems or configurations
- Results or outputs meeting your specific requirements

---

## 8. Fees and Payment

### 8.1 Pricing
{{#IF_PAID_SERVICE}}
Pricing varies by tier and usage:
- **Tier 0-1**: Free tier with rate limits
- **Tier 2**: {{TIER_2_PRICE}} with extended capabilities
- **Tier 3-4**: Custom enterprise pricing

All prices are in EUR and exclude applicable taxes.
{{/IF_PAID_SERVICE}}

{{#IF_FREE_SERVICE}}
The Service is currently provided free of charge. We reserve the right to introduce fees with 90 days notice.
{{/IF_FREE_SERVICE}}

### 8.2 Payment Terms
- Subscriptions billed {{BILLING_PERIOD}}
- Usage overages billed monthly in arrears
- Payment due within {{PAYMENT_DAYS}} days of invoice
- Late payments subject to {{LATE_FEE}}% monthly interest
- No refunds for partial periods or unused services

### 8.3 Taxes
You are responsible for all applicable taxes, duties, and government charges.

---

## 9. Limitation of Liability

### 9.1 Liability Cap
TO THE MAXIMUM EXTENT PERMITTED BY LAW, LUKHAS AI'S TOTAL LIABILITY SHALL NOT EXCEED:
- The amount you paid us in the 12 months prior to the claim, OR
- €10,000, whichever is GREATER

### 9.2 Excluded Damages
WE ARE NOT LIABLE FOR:
- Indirect, incidental, special, consequential, or punitive damages
- Loss of profits, revenue, data, or business opportunities
- Service interruptions or data loss
- Third-party actions or content
- Your violation of these Terms

### 9.3 Exceptions
Some jurisdictions do not allow limitation of liability for certain damages. In such jurisdictions, our liability is limited to the maximum extent permitted by law.

---

## 10. Indemnification

You agree to indemnify, defend, and hold harmless LUKHAS AI, its officers, directors, employees, and agents from any claims, damages, losses, or expenses (including legal fees) arising from:
- Your use of the Service
- Your violation of these Terms
- Your violation of third-party rights
- Your User Content
- Your violation of applicable laws or regulations

---

## 11. Dispute Resolution

### 11.1 Informal Resolution
Before filing a claim, contact us at legal-eu@lukhas.eu to attempt informal resolution.

{{#IF_ARBITRATION}}
### 11.2 Binding Arbitration
Any disputes shall be resolved by binding arbitration under {{ARBITRATION_RULES}}. You waive the right to participate in class actions.
{{/IF_ARBITRATION}}

### 11.2 EU Dispute Resolution
EU users have the right to lodge complaints with supervisory authorities and to seek judicial remedies per GDPR Article 79.

---

## 12. Changes to Terms

### 12.1 Modification Rights
We may modify these Terms at any time. Material changes will be notified via:
- Email to your registered address (30 days advance notice)
- In-app notification
- Website banner on lukhas.eu

### 12.2 Continued Use
Your continued use after changes constitutes acceptance. If you disagree with changes, discontinue use and contact us to terminate your account.

---

## 13. Termination

### 13.1 Termination by You
You may terminate your account at any time through account settings or by contacting support-eu@lukhas.eu.

### 13.2 Termination by Us
We may terminate or suspend access immediately if:
- You violate these Terms
- Required by law or regulatory order
- Service discontinuation (with 90 days notice)
- Security or legal risk

### 13.3 Effects of Termination
Upon termination:
- Your access rights immediately cease
- We may delete your data per our retention policies
- Outstanding fees remain due
- Sections 5 (IP), 9 (Liability), 10 (Indemnification), and 11 (Disputes) survive

---

## 14. Miscellaneous

### 14.1 Entire Agreement
These Terms, our Privacy Policy, and Security Policy constitute the entire agreement between you and LUKHAS AI.

### 14.2 Severability
If any provision is found invalid or unenforceable, the remaining provisions continue in full force.

### 14.3 No Waiver
Our failure to enforce any right or provision does not constitute a waiver.

### 14.4 Assignment
You may not assign these Terms without our consent. We may assign these Terms to affiliates or successors.

### 14.5 Force Majeure
We are not liable for delays or failures due to circumstances beyond reasonable control.

### 14.6 Export Compliance
You must comply with all export control laws and regulations.

---

## 15. Contact Information

**General Inquiries**: support-eu@lukhas.eu
**Legal/Compliance**: legal-eu@lukhas.eu
**Security Issues**: security-eu@lukhas.eu

**Data Protection Officer**: dpo@lukhas.eu

**Mailing Address**:
LUKHAS AI Europe B.V.
Strawinskylaan 1
Amsterdam, North Holland 1077 XX
Netherlands

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-01-15 | Initial Terms of Service |
| 1.0 | 2025-11-12 | Initial legal framework publication |

---

**By using the LUKHAS AI Service, you acknowledge that you have read, understood, and agree to be bound by these Terms of Service.**

---

*This document is part of the LUKHAS Multi-Domain Legal Framework. For domain-specific variations, see:*
- *lukhas.eu: EU-specific legal pack*
- *lukhas.us: US-specific legal pack*
- *Other domains: International version*
