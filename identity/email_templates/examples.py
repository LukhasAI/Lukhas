"""
LUKHAS AI Identity Email Templates - Usage Examples

Demonstrates how to use the email template system for various identity operations
including guardian invitations, recovery notifications, and alias rotations.
"""

from datetime import datetime, timedelta
from .engine import TemplateEngine
from .guardian import GuardianTemplates  
from .recovery import RecoveryTemplates
from .alias import AliasRotationTemplates

def example_guardian_invitation():
    """Example: Create guardian invitation email."""
    print("=== Guardian Invitation Example ===")
    
    guardian_templates = GuardianTemplates()
    
    try:
        # Create guardian invitation
        template = guardian_templates.create_invitation(
            requestor_display_name="Alice Johnson",
            guardian_name="Bob Smith",
            recovery_ticket_id="REC-2025-08-23-A7F3D9E1",
            approve_url="https://lukhas.ai/recovery/approve?token=abc123def456",
            decline_url="https://lukhas.ai/recovery/decline?token=abc123def456",
            ticket_ttl=timedelta(hours=48),
            language='en'
        )
        
        print(f"Subject: {template.subject}")
        print(f"Preheader: {template.preheader}")
        print(f"Language: {template.language}")
        print(f"Template Type: {template.template_type}")
        print("\nPlain Text Preview (first 200 chars):")
        print(template.plain_text[:200] + "...")
        
        # Validate accessibility
        issues = template.validate_accessibility()
        if issues:
            print(f"\nAccessibility Issues: {issues}")
        else:
            print("\n✓ Accessibility validation passed")
            
    except Exception as e:
        print(f"Error: {e}")
    
    print()

def example_recovery_started():
    """Example: Create recovery started notification."""
    print("=== Recovery Started Example ===")
    
    recovery_templates = RecoveryTemplates()
    
    try:
        template = recovery_templates.create_started_notification(
            user_display_name="Alice Johnson",
            recovery_ticket_id="REC-2025-08-23-A7F3D9E1", 
            guardian_count=5,
            required_approvals=3,
            language='en'
        )
        
        print(f"Subject: {template.subject}")
        print(f"Preheader: {template.preheader}")
        print("\nPlain Text Preview (first 300 chars):")
        print(template.plain_text[:300] + "...")
        
    except Exception as e:
        print(f"Error: {e}")
        
    print()

def example_recovery_approved():
    """Example: Create recovery approved notification with ephemeral session."""
    print("=== Recovery Approved Example ===")
    
    recovery_templates = RecoveryTemplates()
    
    try:
        template = recovery_templates.create_approved_notification(
            user_display_name="Alice Johnson",
            session_url="https://lukhas.ai/recovery/session?token=xyz789abc123&expires=1692792000",
            session_ttl=timedelta(hours=1),
            language='en'
        )
        
        print(f"Subject: {template.subject}")
        print(f"Preheader: {template.preheader}")
        print("\nPlain Text Preview (first 300 chars):")
        print(template.plain_text[:300] + "...")
        
        # Validate session URL
        url_validation = recovery_templates.validate_session_url(
            "https://lukhas.ai/recovery/session?token=xyz789abc123&expires=1692792000"
        )
        print(f"\nSession URL Validation: {url_validation}")
        
    except Exception as e:
        print(f"Error: {e}")
        
    print()

def example_recovery_denied():
    """Example: Create recovery denied notification."""
    print("=== Recovery Denied Example ===")
    
    recovery_templates = RecoveryTemplates()
    
    try:
        # Get enumeration-safe denial reasons
        denial_reasons = recovery_templates.get_enumeration_safe_denial_reasons('en')
        selected_reason = denial_reasons[0]  # Use first reason
        
        template = recovery_templates.create_denied_notification(
            user_display_name="Alice Johnson",
            denial_reason=selected_reason,
            language='en'
        )
        
        print(f"Subject: {template.subject}")
        print(f"Denial Reason Used: {selected_reason}")
        print("\nPlain Text Preview (first 300 chars):")
        print(template.plain_text[:300] + "...")
        
        print(f"\nAvailable Denial Reasons:")
        for i, reason in enumerate(denial_reasons, 1):
            print(f"  {i}. {reason}")
            
    except Exception as e:
        print(f"Error: {e}")
        
    print()

def example_alias_rotation():
    """Example: Create alias rotation confirmation."""
    print("=== Alias Rotation Example ===")
    
    alias_templates = AliasRotationTemplates()
    
    try:
        old_alias = "lid#LUKHAS/EU/v1.a7f3d9e1-4b2c"
        new_alias = "lid#LUKHAS/EU/v2.b8e4c0f2-5c3d"
        
        # Validate rotation first
        validation = alias_templates.validate_alias_rotation(old_alias, new_alias)
        print(f"Rotation Validation: {validation}")
        
        if validation['old_alias_valid_format'] and validation['new_alias_valid_format']:
            template = alias_templates.create_rotation_confirmation(
                user_display_name="Alice Johnson",
                old_alias=old_alias,
                new_alias=new_alias,
                initiated_by="system_rotation",
                language='en'
            )
            
            print(f"\nSubject: {template.subject}")
            print(f"Preheader: {template.preheader}")
            print("\nPlain Text Preview (first 300 chars):")
            print(template.plain_text[:300] + "...")
            
        else:
            print("Alias validation failed - cannot create template")
            
    except Exception as e:
        print(f"Error: {e}")
        
    print()

def example_spanish_templates():
    """Example: Create templates in Spanish."""
    print("=== Spanish Templates Example ===")
    
    guardian_templates = GuardianTemplates()
    
    try:
        # Create Spanish guardian invitation
        template = guardian_templates.create_invitation(
            requestor_display_name="Alice Johnson",
            guardian_name="Bob Smith", 
            recovery_ticket_id="REC-2025-08-23-A7F3D9E1",
            approve_url="https://lukhas.ai/recovery/approve?token=abc123def456",
            decline_url="https://lukhas.ai/recovery/decline?token=abc123def456",
            language='es'  # Spanish
        )
        
        print(f"Asunto (Subject): {template.subject}")
        print(f"Preencabezado (Preheader): {template.preheader}")
        print("\nVista previa del texto plano (primeros 200 caracteres):")
        print(template.plain_text[:200] + "...")
        
    except Exception as e:
        print(f"Error: {e}")
        
    print()

def example_template_engine_features():
    """Example: Demonstrate template engine features."""
    print("=== Template Engine Features ===")
    
    engine = TemplateEngine()
    
    # Show supported languages
    languages = engine.get_supported_languages()
    print(f"Supported Languages: {languages}")
    
    # Show available templates for each language
    for lang in languages:
        templates = engine.get_available_templates(lang)
        print(f"Templates available in {lang}: {templates}")
    
    # Validate template variables
    missing_vars = engine.validate_template_variables(
        'guardian_invitation', 
        {'requestor_display_name': 'Alice', 'guardian_name': 'Bob'}  # Missing required vars
    )
    print(f"\nMissing variables for guardian_invitation: {missing_vars}")
    
    print()

def run_all_examples():
    """Run all email template examples."""
    print("LUKHAS AI Identity Email Templates - Examples\n")
    print("=" * 60)
    
    example_guardian_invitation()
    example_recovery_started()
    example_recovery_approved()
    example_recovery_denied()
    example_alias_rotation()
    example_spanish_templates()
    example_template_engine_features()
    
    print("=" * 60)
    print("All examples completed!")

if __name__ == "__main__":
    run_all_examples()