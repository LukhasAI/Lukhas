# LUKHAS AI Identity Email Templates

Comprehensive email template system for LUKHAS AI identity operations including guardian invitations, account recovery workflows, and alias rotation notifications.

## Features

- **Multi-language Support**: English and Spanish templates
- **Accessibility Compliance**: WCAG 2.1 AA standards with proper semantic HTML
- **Security-Focused**: Enumeration-safe messaging and proper security warnings
- **Brand Compliance**: Follows LUKHAS branding standards (LUKHΛS for display, Lukhas for plain text)
- **Template Validation**: Built-in validation for accessibility and brand compliance
- **Flexible Engine**: Extensible template rendering with variable substitution

## Template Types

### Guardian Invitations
- **File**: `guardian_invitation.json`
- **Purpose**: Notify guardians about account recovery requests
- **Features**: TTL warnings, approve/decline links, security notices
- **Languages**: English, Spanish

### Recovery Notifications

#### Recovery Started
- **File**: `recovery_started.json`
- **Purpose**: Confirm recovery process has begun
- **Features**: Guardian count, approval requirements, process timeline

#### Recovery Approved
- **File**: `recovery_approved.json`
- **Purpose**: Provide ephemeral session access after approval
- **Features**: Temporary access links, security steps, TTL warnings

#### Recovery Denied
- **File**: `recovery_denied.json`
- **Purpose**: Notify user of denied recovery requests
- **Features**: Enumeration-safe reasons, alternative options, support guidance

### Alias Rotation
- **File**: `alias_rotation.json`
- **Purpose**: Confirm ΛiD alias rotation completion
- **Features**: Old/new alias display, security benefits, version tracking

## Directory Structure

```
identity/email_templates/
├── __init__.py                 # Package initialization
├── engine.py                   # Core template rendering engine
├── guardian.py                 # Guardian invitation templates
├── recovery.py                 # Account recovery templates
├── alias.py                    # Alias rotation templates
├── examples.py                 # Usage examples and demos
├── README.md                   # This documentation
└── templates/
    ├── en/                     # English templates
    │   ├── guardian_invitation.json
    │   ├── recovery_started.json
    │   ├── recovery_approved.json
    │   ├── recovery_denied.json
    │   └── alias_rotation.json
    └── es/                     # Spanish templates
        ├── guardian_invitation.json
        ├── recovery_started.json
        ├── recovery_approved.json
        ├── recovery_denied.json
        └── alias_rotation.json
```

## Quick Start

```python
from identity.email_templates import GuardianTemplates, RecoveryTemplates, AliasRotationTemplates
from datetime import timedelta

# Guardian invitation
guardian_templates = GuardianTemplates()
invitation = guardian_templates.create_invitation(
    requestor_display_name="Alice Johnson",
    guardian_name="Bob Smith",
    recovery_ticket_id="REC-2025-08-23-A7F3D9E1",
    approve_url="https://lukhas.ai/recovery/approve?token=abc123",
    decline_url="https://lukhas.ai/recovery/decline?token=abc123",
    ticket_ttl=timedelta(hours=48),
    language='en'
)

# Recovery started notification
recovery_templates = RecoveryTemplates()
started = recovery_templates.create_started_notification(
    user_display_name="Alice Johnson",
    recovery_ticket_id="REC-2025-08-23-A7F3D9E1",
    guardian_count=5,
    required_approvals=3,
    language='en'
)

# Alias rotation confirmation
alias_templates = AliasRotationTemplates()
rotation = alias_templates.create_rotation_confirmation(
    user_display_name="Alice Johnson",
    old_alias="lid#LUKHAS/EU/v1.a7f3d9e1-4b2c",
    new_alias="lid#LUKHAS/EU/v2.b8e4c0f2-5c3d",
    initiated_by="system_rotation",
    language='en'
)

# Access rendered content
print(f"Subject: {invitation.subject}")
print(f"HTML: {invitation.html}")
print(f"Plain Text: {invitation.plain_text}")
```

## Template Variables

### Guardian Invitations
- `{{requestor_display_name}}` - Name of person requesting recovery
- `{{guardian_name}}` - Name of the guardian being contacted
- `{{recovery_ticket_id}}` - Unique recovery ticket identifier
- `{{approve_url}}` - URL to approve the request
- `{{decline_url}}` - URL to decline the request
- `{{ticket_ttl_h}}` - Time-to-live in hours
- `{{request_timestamp}}` - When the request was made

### Recovery Notifications
- `{{user_display_name}}` - User's display name
- `{{recovery_ticket_id}}` - Recovery ticket identifier
- `{{guardian_count}}` - Number of guardians notified
- `{{required_approvals}}` - Approvals needed
- `{{session_url}}` - Temporary recovery session URL
- `{{session_ttl_h}}` - Session time-to-live
- `{{denial_reason}}` - Reason for recovery denial
- `{{request_timestamp}}` - Timestamp of the request

### Alias Rotation
- `{{user_display_name}}` - User's display name
- `{{old_alias}}` - Previous ΛiD alias
- `{{new_alias}}` - New ΛiD alias
- `{{initiated_by}}` - Who/what initiated rotation
- `{{rotation_timestamp}}` - When rotation occurred

### Global Variables
- `{{company_display}}` - LUKHΛS (for headers/logos)
- `{{company_plain}}` - Lukhas (for body text)
- `{{product_display}}` - ΛiD (for UI contexts)
- `{{product_plain}}` - lid (for APIs/accessibility)
- `{{support_email}}` - support@lukhas.ai
- `{{security_email}}` - security@lukhas.ai
- `{{current_year}}` - Current year for copyright

## Branding Compliance

### Lambda Symbol Usage
- **Display Contexts**: Use Λ in `LUKHΛS` and `ΛiD` for logos, headers, wordmarks
- **Plain Text**: Use `Lukhas` and `lid` in body text, URLs, alt text
- **Accessibility**: Include `aria-label` attributes for screen readers

### Example Compliance
```html
<!-- Correct: Display context -->
<div class="logo" aria-label="Lukhas">LUKHΛS</div>
<span aria-label="Lambda Identity">ΛiD</span>

<!-- Correct: Plain text context -->
<p>Contact Lukhas support for help with your lid account.</p>
<a href="https://lukhas.ai/lid/settings">Manage Settings</a>
```

## Security Features

### Enumeration Protection
- Recovery denial reasons don't reveal account details
- Generic error messages for invalid requests
- Time-consistent responses regardless of account existence

### URL Validation
- HTTPS requirement for all action URLs
- Session URL security validation
- Anti-CSRF token support

### TTL Management
- Configurable time-to-live for different security levels
- Clear expiration warnings in templates
- Graceful handling of expired tokens

## Accessibility Standards

### WCAG 2.1 AA Compliance
- Semantic HTML structure (`<main>`, `<article>`, `<header>`)
- Proper heading hierarchy (H1, H2, H3)
- Alt text for all images
- Color contrast ratios ≥ 4.5:1
- Screen reader compatible markup

### Responsive Design
- Mobile-first CSS approach
- Scalable fonts and touch targets
- Collapsible layouts for small screens

## Internationalization

### Supported Languages
- **English** (`en`) - Primary language
- **Spanish** (`es`) - Secondary language

### Adding New Languages
1. Create language directory: `templates/{lang_code}/`
2. Translate all JSON template files
3. Update `TemplateEngine.get_supported_languages()`
4. Test with examples script

### Translation Guidelines
- Maintain same variable placeholders
- Preserve HTML structure and classes
- Adapt cultural references appropriately
- Test with native speakers

## Development

### Running Examples
```bash
cd identity/email_templates
python examples.py
```

### Template Validation
```python
from identity.email_templates import TemplateEngine

engine = TemplateEngine()
template = engine.render_template('guardian_invitation', 'en', variables)

# Check accessibility
issues = template.validate_accessibility()
if issues:
    print(f"Accessibility issues: {issues}")
```

### Adding New Templates

1. **Create Template Files**
   ```json
   {
     "subject": "Your subject with {{variables}}",
     "preheader": "Preview text with {{variables}}",
     "plain_text": "Plain text version...",
     "html": "<!DOCTYPE html>..."
   }
   ```

2. **Update Engine**
   - Add template type to `TemplateType` enum
   - Add required variables to `validate_template_variables()`

3. **Create Wrapper Class**
   ```python
   class NewTemplates:
       def create_template(self, **kwargs) -> EmailTemplate:
           # Validation and rendering logic
   ```

### Testing Guidelines

- Test all language combinations
- Validate HTML rendering in multiple email clients
- Check accessibility with screen readers
- Verify brand compliance with policy scripts
- Test variable substitution edge cases

## Integration Examples

### With Django
```python
from django.core.mail import send_mail
from identity.email_templates import GuardianTemplates

def send_guardian_invitation(user, guardian, recovery_id):
    templates = GuardianTemplates()

    email = templates.create_invitation(
        requestor_display_name=user.display_name,
        guardian_name=guardian.name,
        recovery_ticket_id=recovery_id,
        approve_url=f"https://lukhas.ai/recovery/approve/{recovery_id}",
        decline_url=f"https://lukhas.ai/recovery/decline/{recovery_id}",
        language=guardian.preferred_language or 'en'
    )

    send_mail(
        subject=email.subject,
        message=email.plain_text,
        html_message=email.html,
        from_email='noreply@lukhas.ai',
        recipient_list=[guardian.email]
    )
```

### With FastAPI
```python
from fastapi import FastAPI
from identity.email_templates import RecoveryTemplates

app = FastAPI()

@app.post("/recovery/notify-approved")
async def notify_recovery_approved(user_id: str, session_token: str):
    templates = RecoveryTemplates()

    email = templates.create_approved_notification(
        user_display_name=user.display_name,
        session_url=f"https://lukhas.ai/recovery/session/{session_token}",
        session_ttl=timedelta(hours=1),
        language=user.preferred_language or 'en'
    )

    await email_service.send(
        to=user.email,
        subject=email.subject,
        html=email.html,
        text=email.plain_text
    )
```

## Performance Considerations

- Templates are rendered on-demand (no caching by default)
- JSON template files are small and load quickly
- HTML generation is lightweight with minimal CSS
- Variable substitution is O(n) where n = number of variables

## Security Considerations

- All template variables are sanitized
- HTML entities are escaped in variable substitution
- No user-controlled content in template structure
- HTTPS URLs enforced for all action links
- Time-based tokens recommended for all URLs

## Support

For questions about the email template system:

- **Technical Issues**: Contact the Identity & Authentication team
- **Template Content**: Review with UX Content team
- **Security Concerns**: Escalate to Security team
- **Accessibility**: Consult with Accessibility team

---

**Version**: 1.0.0
**Last Updated**: 2025-08-23
**Maintainer**: Identity & Authentication Specialist
