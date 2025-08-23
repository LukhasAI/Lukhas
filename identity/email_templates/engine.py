"""
LUKHAS AI Email Template Engine

Centralized engine for rendering identity-related email templates with:
- Branding compliance enforcement
- Accessibility standards adherence  
- Internationalization support
- Security-focused messaging
"""

import os
import re
from typing import Dict, List, Optional, Union, Literal
from datetime import datetime, timedelta
from dataclasses import dataclass
from pathlib import Path

LanguageCode = Literal['en', 'es']
TemplateType = Literal['guardian_invitation', 'recovery_started', 'recovery_approved', 'recovery_denied', 'alias_rotation', 'magic_link_login', 'magic_link_signup', 'sms_magic_link_login', 'sms_magic_link_signup']

@dataclass
class EmailTemplate:
    """Structured email template with all required components."""
    subject: str
    preheader: str
    plain_text: str
    html: str
    language: LanguageCode
    template_type: TemplateType
    tone_layers: Optional[Dict[str, str]] = None  # For three-layer tone system
    
    def validate_accessibility(self) -> List[str]:
        """Validate template meets accessibility standards."""
        issues = []
        
        # Check for proper alt text in HTML
        if self.html and 'img' in self.html:
            if not re.search(r'alt="[^"]*"', self.html):
                issues.append("Images missing alt text")
                
        # Check for semantic HTML structure
        if self.html and not any(tag in self.html for tag in ['<main>', '<header>', '<article>']):
            issues.append("Missing semantic HTML structure")
            
        # Check for LUKHΛS vs Lukhas usage
        if 'LUKHΛS' in self.plain_text:
            issues.append("Lambda symbol used in plain text - should be 'Lukhas'")
            
        # Check for proper aria-labels with "Lukhas ID" not "ΛiD"
        if self.html and 'ΛiD' in re.findall(r'aria-label="([^"]*)', self.html):
            issues.append("Lambda symbol used in aria-label - should be 'Lukhas ID'")
            
        # Validate three-layer tone system if present
        if self.tone_layers:
            issues.extend(self._validate_tone_layers())
            
        return issues
    
    def _validate_tone_layers(self) -> List[str]:
        """Validate three-layer tone system compliance."""
        issues = []
        
        if not self.tone_layers:
            return issues
            
        # Check for required tone layers
        required_tones = {'poetic', 'technical', 'plain'}
        missing_tones = required_tones - set(self.tone_layers.keys())
        if missing_tones:
            issues.append(f"Missing tone layers: {', '.join(missing_tones)}")
            
        # Validate poetic layer word limit (≤40 words)
        if 'poetic' in self.tone_layers:
            poetic_text = self.tone_layers['poetic']
            word_count = len(poetic_text.split())
            if word_count > 40:
                issues.append(f"Poetic layer exceeds 40 words ({word_count} words)")
                
        # Validate technical layer has proper limits/dependencies messaging
        if 'technical' in self.tone_layers:
            technical_text = self.tone_layers['technical'].lower()
            if not any(keyword in technical_text for keyword in ['limit', 'ttl', 'expire', 'single-use', 'attempt']):
                issues.append("Technical layer missing required security/limits messaging")
                
        # Validate plain layer readability (Flesch-Kincaid ≤ Grade 8)
        if 'plain' in self.tone_layers:
            plain_text = self.tone_layers['plain']
            if self._estimate_reading_level(plain_text) > 8:
                issues.append("Plain layer exceeds Grade 8 reading level")
                
        return issues
    
    def _estimate_reading_level(self, text: str) -> float:
        """Estimate Flesch-Kincaid Grade Level (simplified approximation)."""
        import re
        
        sentences = len(re.split(r'[.!?]+', text.strip()))
        words = len(text.split())
        syllables = sum(self._count_syllables(word) for word in text.split())
        
        if sentences == 0 or words == 0:
            return 0
            
        # Flesch-Kincaid Grade Level formula (simplified)
        grade_level = 0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59
        return max(0, grade_level)
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified algorithm)."""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel
            
        # Handle silent e
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
            
        return max(1, syllable_count)

class TemplateEngine:
    """Centralized email template rendering engine."""
    
    def __init__(self, base_dir: Optional[str] = None):
        """Initialize template engine with base directory."""
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent
        self.templates_dir = self.base_dir / "templates"
        
        # Brand compliance settings
        self.brand_config = {
            'company_display': 'LUKHΛS',  # For logos/headers only
            'company_plain': 'Lukhas',     # For body text/URLs  
            'product_display': 'ΛiD',     # For UI contexts only
            'product_plain': 'lid',       # For APIs/accessibility
            'support_email': 'support@lukhas.ai',
            'security_email': 'security@lukhas.ai'
        }
        
        # Security messaging standards
        self.security_config = {
            'max_ttl_hours': 72,
            'default_ttl_hours': 24,
            'warning_color': '#ff6b35',
            'success_color': '#2ecc71',
            'info_color': '#3498db'
        }
    
    def render_template(
        self,
        template_type: TemplateType,
        language: LanguageCode,
        variables: Dict[str, Union[str, int, datetime, timedelta]]
    ) -> EmailTemplate:
        """Render email template with provided variables."""
        
        # Load base template
        template_path = self.templates_dir / language / f"{template_type}.json"
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
            
        import json
        with open(template_path, 'r', encoding='utf-8') as f:
            template_data = json.load(f)
        
        # Process variables for security and branding compliance
        processed_vars = self._process_variables(variables, language)
        
        # Render each component
        tone_layers = None
        if 'tone_layers' in template_data:
            tone_layers = {
                layer: self._render_string(content, processed_vars)
                for layer, content in template_data['tone_layers'].items()
            }
            
        rendered = EmailTemplate(
            subject=self._render_string(template_data['subject'], processed_vars),
            preheader=self._render_string(template_data['preheader'], processed_vars),
            plain_text=self._render_string(template_data['plain_text'], processed_vars),
            html=self._render_string(template_data['html'], processed_vars),
            language=language,
            template_type=template_type,
            tone_layers=tone_layers
        )
        
        # Validate accessibility and branding compliance
        issues = rendered.validate_accessibility()
        if issues:
            raise ValueError(f"Template accessibility issues: {', '.join(issues)}")
            
        return rendered
    
    def _process_variables(
        self,
        variables: Dict[str, Union[str, int, datetime, timedelta]], 
        language: LanguageCode
    ) -> Dict[str, str]:
        """Process template variables for security and branding compliance."""
        processed = {}
        
        for key, value in variables.items():
            if isinstance(value, datetime):
                # Format timestamps appropriately for locale
                if language == 'es':
                    processed[key] = value.strftime('%d de %B de %Y a las %H:%M UTC')
                else:
                    processed[key] = value.strftime('%B %d, %Y at %H:%M UTC')
                    
            elif isinstance(value, timedelta):
                # Convert to hours for TTL display
                hours = int(value.total_seconds() / 3600)
                if language == 'es':
                    processed[f"{key}_h"] = f"{hours} horas" if hours != 1 else "1 hora"
                else:
                    processed[f"{key}_h"] = f"{hours} hours" if hours != 1 else "1 hour"
                processed[key] = str(hours)
                
            else:
                processed[key] = self._sanitize_variable(str(value))
        
        # Add brand constants
        processed.update({
            'company_display': self.brand_config['company_display'],
            'company_plain': self.brand_config['company_plain'], 
            'product_display': self.brand_config['product_display'],
            'product_plain': self.brand_config['product_plain'],
            'support_email': self.brand_config['support_email'],
            'security_email': self.brand_config['security_email'],
            'current_year': str(datetime.now().year)
        })
        
        return processed
    
    def _sanitize_variable(self, value: str) -> str:
        """Sanitize template variables for security."""
        # Remove HTML tags for plain text safety
        value = re.sub(r'<[^>]*>', '', value)
        
        # Escape special characters that could break template rendering
        value = value.replace('{', '&#123;').replace('}', '&#125;')
        
        # Truncate extremely long values
        if len(value) > 500:
            value = value[:497] + "..."
            
        return value
    
    def _render_string(self, template_str: str, variables: Dict[str, str]) -> str:
        """Render template string with variable substitution."""
        result = template_str
        
        # Replace variables using {{ }} syntax
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, value)
        
        # Check for unreplaced placeholders
        remaining = re.findall(r'{{(\w+)}}', result)
        if remaining:
            raise ValueError(f"Unreplaced template variables: {remaining}")
            
        return result
    
    def validate_template_variables(
        self, 
        template_type: TemplateType, 
        variables: Dict[str, str]
    ) -> List[str]:
        """Validate that all required variables are provided."""
        required_vars = {
            'guardian_invitation': [
                'requestor_display_name', 'guardian_name', 'ticket_ttl_h',
                'approve_url', 'decline_url', 'request_timestamp'
            ],
            'recovery_started': [
                'user_display_name', 'recovery_ticket_id', 'request_timestamp',
                'guardian_count', 'required_approvals'
            ],
            'recovery_approved': [
                'user_display_name', 'session_url', 'session_ttl_h',
                'request_timestamp'
            ],
            'recovery_denied': [
                'user_display_name', 'denial_reason', 'request_timestamp'
            ],
            'alias_rotation': [
                'user_display_name', 'old_alias', 'new_alias', 
                'rotation_timestamp', 'initiated_by'
            ],
            'magic_link_login': [
                'magic_link_url', 'expires_at', 'user_email'
            ],
            'magic_link_signup': [
                'verify_link_url', 'expires_at', 'user_email'
            ],
            'sms_magic_link_login': [
                'magic_link_url', 'expires_at'
            ],
            'sms_magic_link_signup': [
                'verify_link_url', 'expires_at'
            ]
        }
        
        missing = []
        if template_type in required_vars:
            for var in required_vars[template_type]:
                if var not in variables:
                    missing.append(var)
                    
        return missing

    def get_supported_languages(self) -> List[LanguageCode]:
        """Get list of supported language codes."""
        if not self.templates_dir.exists():
            return []
        
        languages = []
        for item in self.templates_dir.iterdir():
            if item.is_dir() and item.name in ['en', 'es']:
                languages.append(item.name)
                
        return sorted(languages)
    
    def get_available_templates(self, language: LanguageCode) -> List[TemplateType]:
        """Get available template types for a language."""
        lang_dir = self.templates_dir / language
        if not lang_dir.exists():
            return []
            
        templates = []
        for template_file in lang_dir.glob("*.json"):
            template_name = template_file.stem
            if template_name in [
                'guardian_invitation', 'recovery_started', 'recovery_approved', 'recovery_denied', 'alias_rotation',
                'magic_link_login', 'magic_link_signup', 'sms_magic_link_login', 'sms_magic_link_signup'
            ]:
                templates.append(template_name)
                
        return sorted(templates)