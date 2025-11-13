#!/usr/bin/env python3
"""
Legal Template Processor for LUKHAS Websites
Processes legal document templates with domain-specific variables
"""

import re
from datetime import date
from pathlib import Path

# Domain configurations
DOMAIN_CONFIGS = {
    "lukhas.ai": {
        "domain": "lukhas.ai",
        "region": "International",
        "company_legal_name": "LUKHAS AI Inc.",
        "street_address": "123 Innovation Drive",
        "city": "San Francisco",
        "state_province": "CA",
        "postal_code": "94103",
        "country": "United States",
        "support_email": "support@lukhas.ai",
        "legal_email": "legal@lukhas.ai",
        "security_email": "security@lukhas.ai",
        "privacy_email": "privacy@lukhas.ai",
        "cloud_provider": "AWS (US-East, EU-Central regions)",
        "payment_processor": "Stripe",
        "email_provider": "SendGrid",
        "analytics_provider": "Self-hosted (anonymized)",
        "currency": "USD",
        "jurisdiction": "Delaware, United States",
        "liability_cap_amount": "$10,000",
        "use_eu_sections": False,
        "use_us_sections": False,
        "use_general_sections": True,
    },
    "lukhas.eu": {
        "domain": "lukhas.eu",
        "region": "European Union",
        "company_legal_name": "LUKHAS AI Europe B.V.",
        "street_address": "Strawinskylaan 1",
        "city": "Amsterdam",
        "state_province": "North Holland",
        "postal_code": "1077 XX",
        "country": "Netherlands",
        "support_email": "support-eu@lukhas.eu",
        "legal_email": "legal-eu@lukhas.eu",
        "security_email": "security-eu@lukhas.eu",
        "privacy_email": "privacy-eu@lukhas.eu",
        "dpo_email": "dpo@lukhas.eu",
        "cloud_provider": "AWS (EU-Central-1 Frankfurt)",
        "payment_processor": "Stripe (EU entity)",
        "email_provider": "SendGrid (EU region)",
        "analytics_provider": "Self-hosted EU (anonymized)",
        "currency": "EUR",
        "jurisdiction": "Netherlands and European Union",
        "eu_member_state": "Netherlands",
        "eu_data_center_location": "Frankfurt, Germany (AWS eu-central-1)",
        "supervisory_authority_name": "Autoriteit Persoonsgegevens (Dutch DPA)",
        "supervisory_authority_website": "https://autoriteitpersoonsgegevens.nl",
        "liability_cap_amount": "€10,000",
        "use_eu_sections": True,
        "use_us_sections": False,
        "use_general_sections": False,
    },
    "lukhas.us": {
        "domain": "lukhas.us",
        "region": "United States",
        "company_legal_name": "LUKHAS AI Inc.",
        "street_address": "123 Innovation Drive",
        "city": "San Francisco",
        "state_province": "CA",
        "postal_code": "94103",
        "country": "United States",
        "support_email": "support-us@lukhas.us",
        "legal_email": "legal-us@lukhas.us",
        "security_email": "security-us@lukhas.us",
        "privacy_email": "privacy-us@lukhas.us",
        "privacy_phone": "1-800-LUKHAS-1",
        "cloud_provider": "AWS (US-East-1, US-West-2)",
        "payment_processor": "Stripe",
        "email_provider": "SendGrid",
        "analytics_provider": "Self-hosted (anonymized)",
        "currency": "USD",
        "jurisdiction": "California and United States",
        "us_state": "California",
        "liability_cap_amount": "$10,000",
        "opt_out_link": "https://lukhas.us/ccpa/do-not-sell",
        "use_eu_sections": False,
        "use_us_sections": True,
        "use_general_sections": False,
    },
}

# Common variables for all domains
COMMON_VARS = {
    "effective_date": "2025-01-15",
    "last_updated": date.today().isoformat(),
    "version_1_date": "2025-01-15",
    "current_version": "1.0",
    "recent_changes": "Initial legal framework publication",
    "jwt_expiry_minutes": "60",
    "session_timeout_minutes": "30",
    "log_retention_days": "90",
    "security_log_retention_days": "365",
    "audit_log_retention_days": "2555",  # 7 years
    "system_log_retention_days": "90",
    "compliance_log_retention_days": "2555",
    "backup_retention_days": "30",
    "api_key_rotation_days": "90",
    "inactive_retention_days": "180",
    "deletion_days": "30",
    "backup_cycle": "30-day",
    "key_rotation_days": "90",
    "bcrypt_cost": "12",
    "password_history": "5",
    "password_expiry_days": "90",
    "failed_auth_threshold": "5",
    "failed_auth_window": "15",
    "access_review_frequency": "quarterly",
    "critical_response_hours": "1",
    "general_response_hours": "24",
    "vulnerability_response_hours": "24",
    "escalation_hours": "4",
    "emergency_contact": "security-emergency@lukhas.ai",
    "escalation_email": "security-escalation@lukhas.ai",
    "critical_patch_days": "7",
    "high_patch_days": "30",
    "medium_patch_days": "90",
    "low_patch_days": "180",
    "pentest_frequency": "annual",
    "rto_hours": "4",
    "rpo_minutes": "15",
    "backup_regions": "multiple AWS regions",
    "dr_drill_frequency": "quarterly",
    "minimum_age": "18",
    "policy_version": "1.0",
    "next_review_date": "2025-04-15",
    "pgp_key_id": "0x1234567890ABCDEF",
    "pgp_key_fingerprint": "1234 5678 90AB CDEF 1234 5678 90AB CDEF 1234 5678",
    "paid_service": False,
    "free_service": True,
    "bug_bounty": False,
    "arbitration": False,
}


def process_conditionals(content, config):
    """Process conditional blocks based on configuration"""

    # Process {{#IF_EU}} blocks
    if config.get("use_eu_sections"):
        content = re.sub(r'\{\{#IF_EU\}\}(.*?)\{\{/IF_EU\}\}', r'\1', content, flags=re.DOTALL)
    else:
        content = re.sub(r'\{\{#IF_EU\}\}.*?\{\{/IF_EU\}\}', '', content, flags=re.DOTALL)

    # Process {{#IF_US}} blocks
    if config.get("use_us_sections"):
        content = re.sub(r'\{\{#IF_US\}\}(.*?)\{\{/IF_US\}\}', r'\1', content, flags=re.DOTALL)
    else:
        content = re.sub(r'\{\{#IF_US\}\}.*?\{\{/IF_US\}\}', '', content, flags=re.DOTALL)

    # Process {{#IF_GENERAL}} blocks
    if config.get("use_general_sections"):
        content = re.sub(r'\{\{#IF_GENERAL\}\}(.*?)\{\{/IF_GENERAL\}\}', r'\1', content, flags=re.DOTALL)
    else:
        content = re.sub(r'\{\{#IF_GENERAL\}\}.*?\{\{/IF_GENERAL\}\}', '', content, flags=re.DOTALL)

    # Process other conditional blocks
    for key, value in config.items():
        if key.startswith("use_") or not isinstance(value, bool):
            continue

        pattern_name = key.upper()
        if value:
            content = re.sub(f'{{{{#IF_{pattern_name}}}}}(.*?){{{{/IF_{pattern_name}}}}}', r'\1', content, flags=re.DOTALL)
        else:
            content = re.sub(f'{{{{#IF_{pattern_name}}}}}.*?{{{{/IF_{pattern_name}}}}}', '', content, flags=re.DOTALL)

    return content


def replace_variables(content, config):
    """Replace template variables with actual values"""
    # Merge common and domain-specific configs
    all_vars = {**COMMON_VARS, **config}

    # Replace all {{VARIABLE_NAME}} patterns
    for key, value in all_vars.items():
        if isinstance(value, bool):
            continue  # Skip boolean flags

        pattern = f"{{{{{key.upper()}}}}}"
        content = content.replace(pattern, str(value))

    return content


def process_template(template_path, output_path, config):
    """Process a single template file"""
    print(f"Processing {template_path.name} for {config['domain']}...")

    # Read template
    with open(template_path) as f:
        content = f.read()

    # Process conditionals
    content = process_conditionals(content, config)

    # Replace variables
    content = replace_variables(content, config)

    # Clean up extra blank lines
    content = re.sub(r'\n{3,}', '\n\n', content)

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(content)

    print(f"  ✓ Created {output_path}")


def main():
    """Main processing function"""
    # Get paths
    repo_root = Path(__file__).parent.parent
    templates_dir = repo_root / "templates" / "legal"
    websites_dir = repo_root / "websites"

    # Template files to process
    templates = [
        "TERMS_OF_SERVICE.md",
        "PRIVACY_POLICY.md",
        "SECURITY_POLICY.md",
    ]

    # Process each domain
    for domain_name, config in DOMAIN_CONFIGS.items():
        print(f"\n{'='*60}")
        print(f"Processing domain: {domain_name}")
        print(f"{'='*60}")

        domain_dir = websites_dir / domain_name / "legal"
        domain_dir.mkdir(parents=True, exist_ok=True)

        for template_name in templates:
            template_path = templates_dir / template_name
            output_path = domain_dir / template_name.lower().replace("_", "-")

            if template_path.exists():
                process_template(template_path, output_path, config)
            else:
                print(f"  ✗ Template not found: {template_path}")

    print(f"\n{'='*60}")
    print("✓ Legal template processing complete!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
