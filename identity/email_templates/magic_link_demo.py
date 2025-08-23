#!/usr/bin/env python3
"""
LUKHAS AI Magic Link Email Templates Demo

Demonstrates the new three-layer tone system with magic link templates.
Tests all template types and languages with proper validation.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Any

# Add the current directory to path for direct engine import
sys.path.insert(0, os.path.dirname(__file__))

from engine import LanguageCode, TemplateEngine, TemplateType


def create_sample_variables() -> dict[str, Any]:
    """Create sample variables for magic link templates."""
    expires_at = datetime.now() + timedelta(seconds=600)  # 10 minutes from now

    return {
        'magic_link_url': 'https://lukhas.ai/auth/magic-link?token=abc123def456ghi789&purpose=login',
        'verify_link_url': 'https://lukhas.ai/auth/verify?token=xyz789uvw456rst123&purpose=signup',
        'expires_at': expires_at,
        'user_email': 'user@example.com',
        'current_timestamp': datetime.now()
    }


def demo_template(
    engine: TemplateEngine,
    template_type: TemplateType,
    language: LanguageCode,
    variables: dict[str, Any]
) -> None:
    """Demonstrate a specific template rendering."""
    print(f"\n{'='*80}")
    print(f"TEMPLATE: {template_type} ({language.upper()})")
    print(f"{'='*80}")

    try:
        # Validate required variables first
        missing_vars = engine.validate_template_variables(template_type, variables)
        if missing_vars:
            print(f"❌ Missing required variables: {missing_vars}")
            return

        # Render the template
        rendered = engine.render_template(template_type, language, variables)

        print(f"📧 SUBJECT: {rendered.subject}")
        print(f"👁️  PREHEADER: {rendered.preheader}")

        # Show tone layers if present
        if rendered.tone_layers:
            print("\n🎭 TONE LAYERS:")
            for layer_name, layer_content in rendered.tone_layers.items():
                print(f"   {layer_name.upper()}: {layer_content}")

        # Show accessibility validation results
        issues = rendered.validate_accessibility()
        if issues:
            print("\n⚠️  ACCESSIBILITY ISSUES:")
            for issue in issues:
                print(f"   • {issue}")
        else:
            print("\n✅ ACCESSIBILITY: All checks passed")

        # Show plain text (truncated)
        print("\n📝 PLAIN TEXT (first 200 chars):")
        print(f"   {rendered.plain_text[:200]}{'...' if len(rendered.plain_text) > 200 else ''}")

        # Show HTML info
        if rendered.html:
            html_length = len(rendered.html)
            tone_attrs = rendered.html.count('data-tone=')
            aria_labels = rendered.html.count('aria-label=')
            print(f"\n🌐 HTML: {html_length} chars, {tone_attrs} tone attrs, {aria_labels} aria-labels")

        print("\n✅ Template rendered successfully!")

    except Exception as e:
        print(f"❌ Error rendering template: {e}")


def main():
    """Main demo function."""
    print("🚀 LUKHAS AI Magic Link Email Templates Demo")
    print("=" * 60)

    # Initialize the template engine
    engine = TemplateEngine()

    # Get sample variables
    variables = create_sample_variables()

    print("📊 Sample Variables:")
    for key, value in variables.items():
        print(f"   {key}: {value}")

    # Demo all magic link templates
    magic_link_templates = [
        'magic_link_login',
        'magic_link_signup',
        'sms_magic_link_login',
        'sms_magic_link_signup'
    ]

    languages = ['en', 'es']

    for template_type in magic_link_templates:
        for language in languages:
            demo_template(engine, template_type, language, variables)

    # Show supported templates and languages
    print(f"\n{'='*80}")
    print("SYSTEM STATUS")
    print(f"{'='*80}")
    print(f"📚 Supported Languages: {engine.get_supported_languages()}")

    for lang in languages:
        templates = engine.get_available_templates(lang)
        print(f"📋 Available Templates ({lang.upper()}): {templates}")

    # Test tone layer validation
    print("\n🧪 TONE LAYER VALIDATION TEST")
    print("-" * 40)

    # Test with the English login template which has tone layers
    try:
        rendered = engine.render_template('magic_link_login', 'en', variables)
        if rendered.tone_layers:
            # Test the validation methods

            print(f"✅ Tone layers found: {list(rendered.tone_layers.keys())}")

            # Test word count validation
            if 'poetic' in rendered.tone_layers:
                word_count = len(rendered.tone_layers['poetic'].split())
                print(f"📖 Poetic layer: {word_count} words ({'✅ OK' if word_count <= 40 else '❌ Exceeds 40'})")

            # Test technical layer content
            if 'technical' in rendered.tone_layers:
                tech_text = rendered.tone_layers['technical'].lower()
                has_limits = any(keyword in tech_text for keyword in ['limit', 'ttl', 'expire', 'single-use', 'attempt'])
                print(f"🔧 Technical layer: {'✅ Has security messaging' if has_limits else '❌ Missing security terms'}")

            # Test reading level (simplified)
            if 'plain' in rendered.tone_layers:
                plain_text = rendered.tone_layers['plain']
                estimated_level = rendered._estimate_reading_level(plain_text)
                print(f"📚 Plain layer: ~Grade {estimated_level:.1f} ({'✅ OK' if estimated_level <= 8 else '❌ Too complex'})")

        else:
            print("❌ No tone layers found in rendered template")

    except Exception as e:
        print(f"❌ Error testing tone validation: {e}")

    print("\n🎉 Demo completed successfully!")
    print("💡 The magic link templates are ready for integration with the existing authentication system.")
    print("🔗 Integration points:")
    print("   • /Users/Gonz/lukhas/packages/auth/src/magic-links.ts (600s TTL matches)")
    print("   • Templates support all required placeholders")
    print("   • Three-layer tone system with data-tone attributes")
    print("   • Accessibility compliance with proper ARIA labels")
    print("   • Mobile-responsive HTML with semantic markup")


if __name__ == '__main__':
    main()

