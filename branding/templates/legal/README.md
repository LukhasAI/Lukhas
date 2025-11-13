# Legal Templates for LUKHAS Websites

This directory contains the master legal document templates for all LUKHAS domains across the λWecosystem.

## Overview

These templates are designed to be:
- **Comprehensive**: Cover all legal requirements for GDPR, CCPA, EU AI Act, and international regulations
- **Flexible**: Support regional variations (EU, US, general)
- **Consistent**: Unified legal framework across all domains
- **Maintainable**: Template variables for easy customization

## Available Templates

### 1. Terms of Service (`TERMS_OF_SERVICE.md`)
Complete terms of service covering:
- Service description and features
- Account registration and security (Lambda ID, WebAuthn)
- Acceptable use policy and AI-specific restrictions
- Intellectual property rights
- Privacy and data protection
- Service availability and performance
- Fees and payment terms
- Limitation of liability
- Dispute resolution
- Regional variations (EU/US specific sections)

**Key Features**:
- Tier-based access control (ΛiD Tiers 0-5)
- WebAuthn/passkey authentication coverage
- MATRIZ cognitive architecture disclosures
- Guardian constitutional AI compliance
- Export compliance and sanctions
- GDPR and CCPA compliance sections

### 2. Privacy Policy (`PRIVACY_POLICY.md`)
Comprehensive privacy notice covering:
- Information collection (account, usage, technical, content)
- Data use and processing purposes
- Data sharing and disclosure practices
- Data retention policies
- User privacy rights (GDPR, CCPA)
- Data security measures
- Cookies and tracking
- Children's privacy
- AI-specific privacy considerations
- Regional variations

**Key Features**:
- GDPR Article 13/14 compliance
- CCPA/CPRA disclosure requirements
- EU data residency commitments
- DPO contact information (EU)
- Privacy rights exercise procedures
- Transparency center references

### 3. Security Policy (`SECURITY_POLICY.md`)
Detailed security practices and commitments:
- Data security (encryption, classification, isolation)
- Identity and access management (ΛiD, MFA, sessions)
- Infrastructure security (cloud, network, application, API)
- Monitoring and logging
- Incident response procedures
- Vulnerability management and disclosure
- Compliance and certifications
- Third-party security
- Guardian constitutional AI security
- Backup and disaster recovery
- Employee and physical security
- User security best practices

**Key Features**:
- Responsible disclosure program
- Bug bounty information (if applicable)
- Security transparency commitments
- Compliance framework alignment (ISO 27001, SOC 2, NIST)
- Incident severity matrix

## Template Variables

All templates use `{{VARIABLE_NAME}}` syntax for customization. Key variables include:

### Required Variables
- `{{EFFECTIVE_DATE}}` - Policy effective date (YYYY-MM-DD)
- `{{LAST_UPDATED}}` - Last modification date (YYYY-MM-DD)
- `{{DOMAIN}}` - Domain name (e.g., lukhas.ai, lukhas.eu)
- `{{REGION}}` - Geographic region (EU, US, International)
- `{{COMPANY_LEGAL_NAME}}` - Legal entity name
- `{{STREET_ADDRESS}}` - Mailing address
- `{{CITY}}`, `{{STATE_PROVINCE}}`, `{{POSTAL_CODE}}`, `{{COUNTRY}}`

### Contact Variables
- `{{SUPPORT_EMAIL}}` - General support email
- `{{LEGAL_EMAIL}}` - Legal inquiries email
- `{{SECURITY_EMAIL}}` - Security reports email
- `{{PRIVACY_EMAIL}}` - Privacy inquiries email
- `{{DPO_EMAIL}}` - Data Protection Officer (EU only)

### Service Variables
- `{{CLOUD_PROVIDER}}` - Cloud infrastructure provider
- `{{PAYMENT_PROCESSOR}}` - Payment processing provider
- `{{EMAIL_PROVIDER}}` - Transactional email provider
- `{{ANALYTICS_PROVIDER}}` - Analytics service (anonymized)

### Configuration Variables
- `{{JWT_EXPIRY_MINUTES}}` - JWT token expiration (default: 60)
- `{{SESSION_TIMEOUT_MINUTES}}` - Session timeout (default: 30)
- `{{LOG_RETENTION_DAYS}}` - Log retention period (default: 90)
- `{{BACKUP_RETENTION_DAYS}}` - Backup retention (default: 30)
- `{{API_KEY_ROTATION_DAYS}}` - Recommended key rotation (default: 90)

### Regional Conditional Blocks
Templates support conditional sections using:
- `{{#IF_EU}}...{{/IF_EU}}` - EU-specific content
- `{{#IF_US}}...{{/IF_US}}` - US-specific content
- `{{#IF_GENERAL}}...{{/IF_GENERAL}}` - International/default content

## Usage Instructions

### For Individual Domains

1. **Copy template to domain directory**:
   ```bash
   cp branding/templates/legal/TERMS_OF_SERVICE.md branding/websites/lukhas.ai/legal/
   ```

2. **Replace template variables**:
   - Use find-and-replace for `{{VARIABLE_NAME}}` patterns
   - Remove unused conditional blocks
   - Customize for domain-specific requirements

3. **Validate content**:
   - Ensure all variables replaced
   - Remove placeholder text
   - Review for accuracy and completeness
   - Legal review (mandatory)

4. **Publish**:
   - Add to domain website structure
   - Link from footer and registration flows
   - Update sitemap

### For Automated Deployment

See `branding/automation/legal_template_processor.py` (if implemented) for automated template processing with YAML configuration:

```yaml
# Example: lukhas.ai configuration
domain: lukhas.ai
region: International
effective_date: 2025-01-01
contacts:
  support: support@lukhas.ai
  legal: legal@lukhas.ai
  security: security@lukhas.ai
services:
  cloud_provider: AWS
  payment_processor: Stripe
```

## Domain-Specific Variations

### lukhas.eu (EU Compliance Portal)
**Required customizations**:
- Include ALL `{{#IF_EU}}` sections
- Set `{{DPO_EMAIL}}` to EU Data Protection Officer
- Specify `{{EU_DATA_CENTER_LOCATION}}` (e.g., Frankfurt, Dublin)
- Add `{{SUPERVISORY_AUTHORITY_NAME}}` and contact
- Include Data Processing Agreement (DPA) links
- Add multi-language versions (major EU languages)

**Additional documents**:
- Data Processing Agreement (DPA)
- Subprocessor list
- Quarterly transparency reports
- EU AI Act compliance documentation

### lukhas.us (US Compliance Portal)
**Required customizations**:
- Include ALL `{{#IF_US}}` sections
- CCPA/CPRA specific disclosures
- "Do Not Sell My Personal Information" link
- State-specific privacy rights (CA, VA, CO, CT, UT)
- US jurisdiction and governing law

**Additional documents**:
- State-specific privacy notices (if needed)
- Accessibility statement (ADA compliance)

### lukhas.ai (Flagship Platform)
**Required customizations**:
- Include `{{#IF_GENERAL}}` sections
- International jurisdiction
- Link to regional compliance portals (lukhas.eu, lukhas.us)
- Focus on technical capabilities and MATRIZ features

### lukhas.dev (Developer Platform)
**Required customizations**:
- Enhanced API security sections
- Developer-specific terms (API usage, rate limits)
- Open source license disclosures
- SDK and library terms

### lukhas.id (Identity Portal)
**Required customizations**:
- Detailed Lambda ID (ΛiD) authentication coverage
- WebAuthn/passkey specific terms
- Identity verification processes
- Multi-factor authentication policies

## Legal Review Requirements

**Before publishing any legal document**:
1. ✅ All template variables replaced
2. ✅ Content reviewed for domain-specific accuracy
3. ✅ Legal counsel review (MANDATORY)
4. ✅ Compliance team approval (EU/US as applicable)
5. ✅ Executive sign-off for material terms
6. ✅ Version control and changelog maintained
7. ✅ User notification plan for material changes

## Version Control

All legal documents MUST be version controlled:
- Track all changes via Git commits
- Maintain version number in document
- Update `{{LAST_UPDATED}}` date
- Document changes in Version History table
- Notify users of material changes (30 days advance)

## Update Schedule

### Regular Reviews
- **Quarterly**: Review for regulatory changes
- **Annually**: Comprehensive legal review
- **As needed**: When introducing new features or services

### Trigger Updates
Update legal documents when:
- New data processing activities added
- Service architecture changes
- New regulatory requirements
- New geographic regions added
- Material changes to user rights or obligations
- Security incident lessons learned
- Third-party service changes

## Compliance Checklist

### GDPR (EU)
- [ ] Legal bases for processing documented
- [ ] User rights procedures defined
- [ ] Data retention periods specified
- [ ] DPO contact provided
- [ ] Data breach notification procedures
- [ ] International transfer mechanisms (SCCs)
- [ ] Cookie consent management

### CCPA/CPRA (US)
- [ ] Categories of personal information disclosed
- [ ] Purposes for collection disclosed
- [ ] Third-party sharing disclosed
- [ ] User rights (access, deletion, opt-out) defined
- [ ] "Do Not Sell" mechanism provided
- [ ] Non-discrimination policy stated

### EU AI Act (High-Risk AI)
- [ ] Transparency obligations met
- [ ] Human oversight described
- [ ] Accuracy and robustness commitments
- [ ] Risk management procedures
- [ ] Data governance practices
- [ ] Record-keeping obligations

### SOC 2 Type II
- [ ] Security controls documented
- [ ] Availability commitments
- [ ] Confidentiality measures
- [ ] Privacy practices aligned

## Contact for Legal Template Issues

**Template Maintenance**: legal@lukhas.ai
**Legal Questions**: legal@lukhas.ai
**Compliance Questions**: compliance@lukhas.ai
**EU DPO**: dpo-eu@lukhas.eu
**US Privacy**: privacy-us@lukhas.us

## Related Documents

- **Brand Guidelines**: `branding/BRAND_GUIDELINES.md`
- **Domain Registry**: `branding/config/domain_registry.yaml`
- **Multi-Domain Strategy**: See domain-specific `BRAND_GUIDE.md` files
- **Claims Registry**: `docs/audits/claims_registry.md` (for evidence-based claims)
- **Transparency Reports**: Published quarterly at each domain's `/transparency` page

## License

These legal templates are proprietary to LUKHAS AI and are provided for internal use across the λWecosystem. Not for external distribution or reuse without permission.

---

**Version**: 1.0
**Created**: 2025-11-12
**Last Updated**: 2025-11-12
**Maintained by**: LUKHAS Legal Team
