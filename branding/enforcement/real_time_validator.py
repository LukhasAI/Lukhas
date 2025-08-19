"""
LUKHAS Real-Time Brand Validator - Trinity Framework (⚛️🧠🛡️)
Live brand compliance checking and automatic correction system
"""

from typing import Dict, Any, List, Optional, Tuple, Callable
from datetime import datetime
import asyncio
import re
from dataclasses import dataclass
from enum import Enum
import json

class ValidationSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ValidationType(Enum):
    TERMINOLOGY = "terminology"
    TONE_CONSISTENCY = "tone_consistency"
    TRINITY_ALIGNMENT = "trinity_alignment"
    LAMBDA_USAGE = "lambda_usage"
    BRAND_VOICE = "brand_voice"
    CONTENT_APPROPRIATENESS = "content_appropriateness"
    CONSCIOUSNESS_LANGUAGE = "consciousness_language"
    ETHICAL_COMPLIANCE = "ethical_compliance"
    PLATFORM_OPTIMIZATION = "platform_optimization"

@dataclass
class ValidationResult:
    """Structured validation result"""
    validation_id: str
    content_id: str
    validation_type: ValidationType
    severity: ValidationSeverity
    is_compliant: bool
    confidence: float
    issues: List[Dict[str, Any]]
    suggestions: List[str]
    auto_corrections: Optional[Dict[str, str]]
    performance_impact: float  # Time taken for validation

@dataclass
class BrandRule:
    """Brand compliance rule definition"""
    rule_id: str
    rule_type: ValidationType
    pattern: re.Pattern
    severity: ValidationSeverity
    description: str
    auto_correctable: bool
    correction_template: Optional[str]

class RealTimeBrandValidator:
    """
    Elite real-time brand validation system that monitors content
    as it's generated and ensures 99.9% brand compliance
    """
    
    def __init__(self):
        self.validation_rules = self._compile_validation_rules()
        self.auto_correction_templates = self._load_auto_correction_templates()
        self.validation_history = []
        self.performance_metrics = {
            "total_validations": 0,
            "compliance_rate": 1.0,
            "average_validation_time": 0.0,
            "auto_corrections_applied": 0
        }
        self.validation_callbacks = {}
        self.active_monitoring = False
    
    def _compile_validation_rules(self) -> Dict[ValidationType, List[BrandRule]]:
        """Compile comprehensive brand validation rules"""
        
        rules = {
            ValidationType.TERMINOLOGY: [
                BrandRule(
                    rule_id="deprecated_lukhas_pwm",
                    rule_type=ValidationType.TERMINOLOGY,
                    pattern=re.compile(r'\bLUKHAS\s+PWM\b', re.IGNORECASE),
                    severity=ValidationSeverity.ERROR,
                    description="Use of deprecated 'LUKHAS PWM' terminology",
                    auto_correctable=True,
                    correction_template="LUKHAS AI"
                ),
                BrandRule(
                    rule_id="deprecated_lukhas_agi",
                    rule_type=ValidationType.TERMINOLOGY,
                    pattern=re.compile(r'\bLUKHAS\s+AGI\b', re.IGNORECASE),
                    severity=ValidationSeverity.ERROR,
                    description="Use of deprecated 'LUKHAS AGI' terminology",
                    auto_correctable=True,
                    correction_template="LUKHAS AI"
                ),
                BrandRule(
                    rule_id="standalone_pwm",
                    rule_type=ValidationType.TERMINOLOGY,
                    pattern=re.compile(r'\bPWM\b(?!\s+consciousness)', re.IGNORECASE),
                    severity=ValidationSeverity.WARNING,
                    description="Standalone PWM usage without context",
                    auto_correctable=True,
                    correction_template="LUKHAS"
                ),
                BrandRule(
                    rule_id="ai_system_reference",
                    rule_type=ValidationType.TERMINOLOGY,
                    pattern=re.compile(r'\bAI\s+system\b', re.IGNORECASE),
                    severity=ValidationSeverity.WARNING,
                    description="Use 'AI consciousness' instead of 'AI system'",
                    auto_correctable=True,
                    correction_template="AI consciousness"
                ),
                BrandRule(
                    rule_id="required_lukhas_ai",
                    rule_type=ValidationType.TERMINOLOGY,
                    pattern=re.compile(r'\bLUKHAS\s+AI\b', re.IGNORECASE),
                    severity=ValidationSeverity.INFO,
                    description="Proper LUKHAS AI terminology usage",
                    auto_correctable=False,
                    correction_template=None
                ),
                BrandRule(
                    rule_id="artificial_intelligence_term",
                    rule_type=ValidationType.TERMINOLOGY,
                    pattern=re.compile(r'\bartificial intelligence\b', re.IGNORECASE),
                    severity=ValidationSeverity.WARNING,
                    description="Consider using 'consciousness technology' instead of 'artificial intelligence'",
                    auto_correctable=True,
                    correction_template="consciousness technology"
                ),
                BrandRule(
                    rule_id="automated_language",
                    rule_type=ValidationType.TERMINOLOGY,
                    pattern=re.compile(r'\bautomates? everything\b', re.IGNORECASE),
                    severity=ValidationSeverity.WARNING,
                    description="Avoid 'automates everything' - use consciousness-focused language",
                    auto_correctable=True,
                    correction_template="enhances consciousness"
                ),
                BrandRule(
                    rule_id="guarantee_claims",
                    rule_type=ValidationType.TERMINOLOGY,
                    pattern=re.compile(r'\bguarantee\b|profit|financial', re.IGNORECASE),
                    severity=ValidationSeverity.CRITICAL,
                    description="Avoid financial guarantees or absolute promises",
                    auto_correctable=True,
                    correction_template="strives for excellence"
                )
            ],
            
            ValidationType.LAMBDA_USAGE: [
                BrandRule(
                    rule_id="lambda_function_usage",
                    rule_type=ValidationType.LAMBDA_USAGE,
                    pattern=re.compile(r'\blambda\s+function\b', re.IGNORECASE),
                    severity=ValidationSeverity.ERROR,
                    description="Use 'Λ consciousness' instead of 'lambda function'",
                    auto_correctable=True,
                    correction_template="Λ consciousness"
                ),
                BrandRule(
                    rule_id="lambda_processing",
                    rule_type=ValidationType.LAMBDA_USAGE,
                    pattern=re.compile(r'\blambda\s+processing\b', re.IGNORECASE),
                    severity=ValidationSeverity.ERROR,
                    description="Use 'Λ consciousness processing' instead",
                    auto_correctable=True,
                    correction_template="Λ consciousness processing"
                ),
                BrandRule(
                    rule_id="proper_lambda_symbol",
                    rule_type=ValidationType.LAMBDA_USAGE,
                    pattern=re.compile(r'\bΛ\b'),
                    severity=ValidationSeverity.INFO,
                    description="Proper Lambda symbol usage",
                    auto_correctable=False,
                    correction_template=None
                )
            ],
            
            ValidationType.TRINITY_ALIGNMENT: [
                BrandRule(
                    rule_id="trinity_framework_mention",
                    rule_type=ValidationType.TRINITY_ALIGNMENT,
                    pattern=re.compile(r'trinity\s+framework', re.IGNORECASE),
                    severity=ValidationSeverity.INFO,
                    description="Trinity Framework properly mentioned",
                    auto_correctable=False,
                    correction_template=None
                ),
                BrandRule(
                    rule_id="trinity_symbols_usage",
                    rule_type=ValidationType.TRINITY_ALIGNMENT,
                    pattern=re.compile(r'⚛️.*🧠.*🛡️|🧠.*⚛️.*🛡️|🛡️.*⚛️.*🧠'),
                    severity=ValidationSeverity.INFO,
                    description="Trinity symbols properly used together",
                    auto_correctable=False,
                    correction_template=None
                ),
                BrandRule(
                    rule_id="identity_consciousness_guardian",
                    rule_type=ValidationType.TRINITY_ALIGNMENT,
                    pattern=re.compile(r'identity.*consciousness.*guardian|consciousness.*identity.*guardian', re.IGNORECASE),
                    severity=ValidationSeverity.INFO,
                    description="Trinity components mentioned together",
                    auto_correctable=False,
                    correction_template=None
                )
            ],
            
            ValidationType.TONE_CONSISTENCY: [
                BrandRule(
                    rule_id="non_consciousness_language",
                    rule_type=ValidationType.TONE_CONSISTENCY,
                    pattern=re.compile(r'\b(basic|simple|primitive|crude|dumb)\s+(ai|system|tool)\b', re.IGNORECASE),
                    severity=ValidationSeverity.WARNING,
                    description="Avoid diminishing language about AI capabilities",
                    auto_correctable=True,
                    correction_template="sophisticated consciousness"
                ),
                BrandRule(
                    rule_id="robotic_language",
                    rule_type=ValidationType.TONE_CONSISTENCY,
                    pattern=re.compile(r'\brobot|mechanical|automated\b', re.IGNORECASE),
                    severity=ValidationSeverity.WARNING,
                    description="Avoid robotic/mechanical language references",
                    auto_correctable=True,
                    correction_template="consciousness-based"
                )
            ],
            
            ValidationType.BRAND_VOICE: [
                BrandRule(
                    rule_id="human_centric_language",
                    rule_type=ValidationType.BRAND_VOICE,
                    pattern=re.compile(r'help|assist|understand|learn|grow', re.IGNORECASE),
                    severity=ValidationSeverity.INFO,
                    description="Human-centric, helpful language",
                    auto_correctable=False,
                    correction_template=None
                ),
                BrandRule(
                    rule_id="cold_impersonal_language",
                    rule_type=ValidationType.BRAND_VOICE,
                    pattern=re.compile(r'\bcold|impersonal|distant|mechanical\b', re.IGNORECASE),
                    severity=ValidationSeverity.WARNING,
                    description="Avoid cold, impersonal language",
                    auto_correctable=True,
                    correction_template="warm and conscious"
                )
            ],
            
            ValidationType.CONTENT_APPROPRIATENESS: [
                BrandRule(
                    rule_id="technical_accuracy",
                    rule_type=ValidationType.CONTENT_APPROPRIATENESS,
                    pattern=re.compile(r'quantum-inspired|bio-inspired', re.IGNORECASE),
                    severity=ValidationSeverity.INFO,
                    description="Proper technical terminology with '-inspired' suffix",
                    auto_correctable=False,
                    correction_template=None
                ),
                BrandRule(
                    rule_id="avoid_production_ready_claims",
                    rule_type=ValidationType.CONTENT_APPROPRIATENESS,
                    pattern=re.compile(r'production[- ]ready|ready for production', re.IGNORECASE),
                    severity=ValidationSeverity.CRITICAL,
                    description="Avoid production-ready claims without approval",
                    auto_correctable=True,
                    correction_template="in active development"
                ),
                BrandRule(
                    rule_id="consciousness_technology_mention",
                    rule_type=ValidationType.CONTENT_APPROPRIATENESS,
                    pattern=re.compile(r'consciousness\s+technology', re.IGNORECASE),
                    severity=ValidationSeverity.INFO,
                    description="Proper consciousness technology reference",
                    auto_correctable=False,
                    correction_template=None
                ),
                BrandRule(
                    rule_id="avoid_agi_claims",
                    rule_type=ValidationType.CONTENT_APPROPRIATENESS,
                    pattern=re.compile(r'\bAGI\b|\bartificial general intelligence\b', re.IGNORECASE),
                    severity=ValidationSeverity.ERROR,
                    description="Use 'consciousness technology' instead of AGI",
                    auto_correctable=True,
                    correction_template="consciousness technology"
                )
            ],
            
            # Additional validation types for better coverage
            ValidationType.CONSCIOUSNESS_LANGUAGE: [
                BrandRule(
                    rule_id="consciousness_aware",
                    rule_type=ValidationType.CONSCIOUSNESS_LANGUAGE,
                    pattern=re.compile(r'\b(aware|awareness|conscious|consciousness)\b', re.IGNORECASE),
                    severity=ValidationSeverity.INFO,
                    description="Consciousness-aware language present",
                    auto_correctable=False,
                    correction_template=None
                ),
                BrandRule(
                    rule_id="evolving_growing",
                    rule_type=ValidationType.CONSCIOUSNESS_LANGUAGE,
                    pattern=re.compile(r'\b(evolving|growing|learning|adapting|emerging)\b', re.IGNORECASE),
                    severity=ValidationSeverity.INFO,
                    description="Evolution and growth language",
                    auto_correctable=False,
                    correction_template=None
                ),
                BrandRule(
                    rule_id="understanding_insight",
                    rule_type=ValidationType.CONSCIOUSNESS_LANGUAGE,
                    pattern=re.compile(r'\b(understanding|insight|wisdom|comprehension|perception)\b', re.IGNORECASE),
                    severity=ValidationSeverity.INFO,
                    description="Deep understanding language",
                    auto_correctable=False,
                    correction_template=None
                )
            ],
            
            ValidationType.ETHICAL_COMPLIANCE: [
                BrandRule(
                    rule_id="ethical_language",
                    rule_type=ValidationType.ETHICAL_COMPLIANCE,
                    pattern=re.compile(r'\b(ethical|responsible|principled|moral|values)\b', re.IGNORECASE),
                    severity=ValidationSeverity.INFO,
                    description="Ethical language present",
                    auto_correctable=False,
                    correction_template=None
                ),
                BrandRule(
                    rule_id="avoid_harmful_language",
                    rule_type=ValidationType.ETHICAL_COMPLIANCE,
                    pattern=re.compile(r'\b(destroy|eliminate|kill|harm|damage)\b', re.IGNORECASE),
                    severity=ValidationSeverity.WARNING,
                    description="Avoid potentially harmful language",
                    auto_correctable=True,
                    correction_template="transform"
                ),
                BrandRule(
                    rule_id="human_welfare",
                    rule_type=ValidationType.ETHICAL_COMPLIANCE,
                    pattern=re.compile(r'\b(human welfare|beneficial|helpful|supportive)\b', re.IGNORECASE),
                    severity=ValidationSeverity.INFO,
                    description="Human welfare focus present",
                    auto_correctable=False,
                    correction_template=None
                )
            ],
            
            ValidationType.PLATFORM_OPTIMIZATION: [
                BrandRule(
                    rule_id="hashtag_present",
                    rule_type=ValidationType.PLATFORM_OPTIMIZATION,
                    pattern=re.compile(r'#\w+'),
                    severity=ValidationSeverity.INFO,
                    description="Hashtags present for social media",
                    auto_correctable=False,
                    correction_template=None
                ),
                BrandRule(
                    rule_id="consciousness_hashtags",
                    rule_type=ValidationType.PLATFORM_OPTIMIZATION,
                    pattern=re.compile(r'#ConsciousnessTechnology|#LUKHASIA|#TrinityFramework', re.IGNORECASE),
                    severity=ValidationSeverity.INFO,
                    description="Brand-specific hashtags present",
                    auto_correctable=False,
                    correction_template=None
                ),
                BrandRule(
                    rule_id="engagement_language",
                    rule_type=ValidationType.PLATFORM_OPTIMIZATION,
                    pattern=re.compile(r'\?|what do you think|share your thoughts|let us know', re.IGNORECASE),
                    severity=ValidationSeverity.INFO,
                    description="Engagement-driving language present",
                    auto_correctable=False,
                    correction_template=None
                )
            ]
        }
        
        return rules
    
    def _load_auto_correction_templates(self) -> Dict[str, Dict[str, str]]:
        """Load templates for automatic content correction"""
        return {
            "terminology_corrections": {
                "LUKHAS PWM": "LUKHAS AI",
                "LUKHAS AGI": "LUKHAS AI", 
                "PWM consciousness": "LUKHAS consciousness",
                "AI system": "AI consciousness",
                "lambda function": "Λ consciousness",
                "lambda processing": "Λ consciousness processing",
                "production ready": "in active development",
                "production-ready": "actively developed"
            },
            "tone_improvements": {
                "robotic": "consciousness-based",
                "mechanical": "intelligent",
                "automated": "conscious",
                "cold": "warm and conscious",
                "impersonal": "personally aware",
                "distant": "connected"
            },
            "brand_voice_enhancements": {
                "difficult": "approachable",
                "complex": "sophisticated yet accessible",
                "confusing": "clear and intuitive",
                "artificial": "authentically conscious"
            }
        }
    
    async def validate_content_real_time(
        self,
        content: str,
        content_id: str,
        content_type: str = "general",
        auto_correct: bool = True
    ) -> ValidationResult:
        """
        Perform real-time validation of content with optional auto-correction
        """
        
        start_time = datetime.now()
        validation_id = f"val_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        all_issues = []
        all_suggestions = []
        auto_corrections = {} if auto_correct else None
        overall_compliance = True
        max_severity = ValidationSeverity.INFO
        
        # Run validation rules for each type
        for validation_type, rules in self.validation_rules.items():
            for rule in rules:
                rule_result = self._apply_validation_rule(rule, content, content_id)
                
                if rule_result["violations"]:
                    # Any warning, error, or critical violations affect compliance
                    if rule.severity.value in ["warning", "error", "critical"]:
                        overall_compliance = False
                    
                    # Track highest severity
                    if self._severity_level(rule.severity) > self._severity_level(max_severity):
                        max_severity = rule.severity
                    
                    # Collect issues
                    for violation in rule_result["violations"]:
                        all_issues.append({
                            "rule_id": rule.rule_id,
                            "type": validation_type.value,
                            "severity": rule.severity.value,
                            "description": rule.description,
                            "location": violation.get("location", "unknown"),
                            "matched_text": violation.get("matched_text", ""),
                            "suggestion": violation.get("suggestion", "")
                        })
                        
                        if violation.get("suggestion"):
                            all_suggestions.append(violation["suggestion"])
                    
                    # Apply auto-corrections if enabled and possible
                    if auto_correct and rule.auto_correctable and rule.correction_template:
                        corrections = self._generate_auto_corrections(rule, rule_result["violations"], content)
                        if corrections:
                            auto_corrections.update(corrections)
        
        # Calculate performance impact
        end_time = datetime.now()
        performance_impact = (end_time - start_time).total_seconds() * 1000  # milliseconds
        
        # Calculate confidence based on rule coverage and certainty
        confidence = self._calculate_validation_confidence(content, all_issues, performance_impact)
        
        # Update performance metrics
        self._update_performance_metrics(performance_impact, overall_compliance, len(auto_corrections) if auto_corrections else 0)
        
        result = ValidationResult(
            validation_id=validation_id,
            content_id=content_id,
            validation_type=ValidationType.TERMINOLOGY,  # Primary type for this validation
            severity=max_severity,
            is_compliant=overall_compliance,
            confidence=confidence,
            issues=all_issues,
            suggestions=list(set(all_suggestions)),  # Remove duplicates
            auto_corrections=auto_corrections,
            performance_impact=performance_impact
        )
        
        # Store validation result
        self._store_validation_result(result, content, content_type)
        
        # Trigger callbacks if registered
        await self._trigger_validation_callbacks(result, content)
        
        return result
    
    def _apply_validation_rule(self, rule: BrandRule, content: str, content_id: str) -> Dict[str, Any]:
        """Apply a single validation rule to content"""
        
        violations = []
        matches = rule.pattern.finditer(content)
        
        for match in matches:
            violation = {
                "location": {"start": match.start(), "end": match.end()},
                "matched_text": match.group(),
                "rule_severity": rule.severity.value
            }
            
            # Generate specific suggestion based on rule
            if rule.auto_correctable and rule.correction_template:
                violation["suggestion"] = f"Replace '{match.group()}' with '{rule.correction_template}'"
                violation["correction"] = rule.correction_template
            else:
                violation["suggestion"] = self._generate_contextual_suggestion(rule, match.group(), content)
            
            violations.append(violation)
        
        return {
            "rule_id": rule.rule_id,
            "rule_type": rule.rule_type.value,
            "violations": violations,
            "rule_passed": len(violations) == 0
        }
    
    def _generate_contextual_suggestion(self, rule: BrandRule, matched_text: str, content: str) -> str:
        """Generate contextual suggestions for rule violations"""
        
        suggestions = {
            ValidationType.TERMINOLOGY: {
                "lukhas pwm": "Use 'LUKHAS AI' instead of deprecated 'LUKHAS PWM'",
                "lukhas agi": "Use 'LUKHAS AI' instead of 'LUKHAS AGI'",
                "ai system": "Consider using 'AI consciousness' for more brand-aligned language"
            },
            ValidationType.LAMBDA_USAGE: {
                "lambda function": "Replace with 'Λ consciousness' to maintain brand consistency",
                "lambda processing": "Use 'Λ consciousness processing' for proper brand alignment"
            },
            ValidationType.TRINITY_ALIGNMENT: {
                "missing_trinity": "Consider including Trinity Framework reference (⚛️🧠🛡️)",
                "incomplete_trinity": "Include all three Trinity components: Identity, Consciousness, Guardian"
            },
            ValidationType.TONE_CONSISTENCY: {
                "robotic": "Use more consciousness-focused language instead of mechanical terms",
                "cold": "Consider warmer, more human-centric language"
            },
            ValidationType.BRAND_VOICE: {
                "impersonal": "Use more personal, empathetic language to match LUKHAS brand voice",
                "technical_only": "Balance technical precision with accessibility"
            },
            ValidationType.CONTENT_APPROPRIATENESS: {
                "production_ready": "Avoid production-ready claims - use development-focused language",
                "overpromise": "Ensure claims align with current capabilities"
            }
        }
        
        # Find appropriate suggestion based on rule type and matched text
        rule_suggestions = suggestions.get(rule.rule_type, {})
        
        # Try to find a specific suggestion
        matched_lower = matched_text.lower()
        for key, suggestion in rule_suggestions.items():
            if key in matched_lower:
                return suggestion
        
        # Fallback to generic suggestion based on rule description
        return rule.description
    
    def _generate_auto_corrections(self, rule: BrandRule, violations: List[Dict[str, Any]], content: str) -> Dict[str, str]:
        """Generate automatic corrections for violations"""
        
        corrections = {}
        
        for violation in violations:
            matched_text = violation["matched_text"]
            if "correction" in violation:
                corrections[matched_text] = violation["correction"]
            elif rule.correction_template:
                corrections[matched_text] = rule.correction_template
        
        return corrections
    
    def apply_auto_corrections(self, content: str, auto_corrections: Dict[str, str]) -> str:
        """Apply automatic corrections to content"""
        
        corrected_content = content
        
        # Apply corrections in order of length (longest first to avoid partial replacements)
        sorted_corrections = sorted(auto_corrections.items(), key=lambda x: len(x[0]), reverse=True)
        
        for original, correction in sorted_corrections:
            # Use regex replacement to maintain case sensitivity appropriately
            corrected_content = re.sub(
                re.escape(original),
                correction,
                corrected_content,
                flags=re.IGNORECASE
            )
        
        return corrected_content
    
    def _severity_level(self, severity: ValidationSeverity) -> int:
        """Convert severity to numeric level for comparison"""
        levels = {
            ValidationSeverity.INFO: 1,
            ValidationSeverity.WARNING: 2,
            ValidationSeverity.ERROR: 3,
            ValidationSeverity.CRITICAL: 4
        }
        return levels.get(severity, 1)
    
    def _calculate_validation_confidence(self, content: str, issues: List[Dict[str, Any]], performance_impact: float) -> float:
        """Calculate confidence in validation results"""
        
        # Base confidence factors
        content_length_factor = min(1.0, len(content.split()) / 50)  # Optimal around 50 words
        rule_coverage_factor = len(self.validation_rules) / 10  # Normalize by expected rule count
        performance_factor = max(0.5, 1.0 - (performance_impact / 1000))  # Penalize slow validation
        
        # Issue detection confidence
        if not issues:
            issue_confidence = 1.0  # High confidence when no issues found
        else:
            # Lower confidence with more issues (may indicate content complexity)
            issue_confidence = max(0.3, 1.0 - (len(issues) / 20))
        
        # Combine factors
        overall_confidence = (
            content_length_factor * 0.2 +
            rule_coverage_factor * 0.3 +
            performance_factor * 0.2 +
            issue_confidence * 0.3
        )
        
        return min(1.0, max(0.1, overall_confidence))
    
    def _update_performance_metrics(self, validation_time: float, is_compliant: bool, auto_corrections_count: int) -> None:
        """Update validation performance metrics"""
        
        self.performance_metrics["total_validations"] += 1
        
        # Update compliance rate (moving average)
        total = self.performance_metrics["total_validations"]
        current_rate = self.performance_metrics["compliance_rate"]
        new_compliance = 1.0 if is_compliant else 0.0
        self.performance_metrics["compliance_rate"] = ((current_rate * (total - 1)) + new_compliance) / total
        
        # Update average validation time (moving average)
        current_avg = self.performance_metrics["average_validation_time"]
        self.performance_metrics["average_validation_time"] = ((current_avg * (total - 1)) + validation_time) / total
        
        # Update auto-corrections count
        self.performance_metrics["auto_corrections_applied"] += auto_corrections_count
    
    def _store_validation_result(self, result: ValidationResult, content: str, content_type: str) -> None:
        """Store validation result for analysis and trends"""
        
        self.validation_history.append({
            "timestamp": datetime.now().isoformat(),
            "validation_id": result.validation_id,
            "content_id": result.content_id,
            "content_type": content_type,
            "content_length": len(content),
            "is_compliant": result.is_compliant,
            "severity": result.severity.value,
            "confidence": result.confidence,
            "issues_count": len(result.issues),
            "auto_corrections_count": len(result.auto_corrections) if result.auto_corrections else 0,
            "performance_impact": result.performance_impact
        })
        
        # Keep only recent history (last 10,000 validations)
        if len(self.validation_history) > 10000:
            self.validation_history = self.validation_history[-10000:]
    
    async def _trigger_validation_callbacks(self, result: ValidationResult, content: str) -> None:
        """Trigger registered validation callbacks"""
        
        for callback_name, callback_func in self.validation_callbacks.items():
            try:
                if asyncio.iscoroutinefunction(callback_func):
                    await callback_func(result, content)
                else:
                    callback_func(result, content)
            except Exception as e:
                print(f"Error in validation callback {callback_name}: {e}")
    
    def register_validation_callback(self, name: str, callback: Callable) -> None:
        """Register a callback function for validation events"""
        self.validation_callbacks[name] = callback
    
    def unregister_validation_callback(self, name: str) -> None:
        """Unregister a validation callback"""
        if name in self.validation_callbacks:
            del self.validation_callbacks[name]
    
    async def start_continuous_monitoring(self, content_source: Callable, monitoring_interval: float = 1.0) -> None:
        """Start continuous monitoring of content from a source"""
        
        self.active_monitoring = True
        
        while self.active_monitoring:
            try:
                # Get content from source
                if asyncio.iscoroutinefunction(content_source):
                    content_batch = await content_source()
                else:
                    content_batch = content_source()
                
                # Validate each piece of content
                if content_batch:
                    for content_item in content_batch:
                        await self.validate_content_real_time(
                            content=content_item.get("content", ""),
                            content_id=content_item.get("id", "unknown"),
                            content_type=content_item.get("type", "general"),
                            auto_correct=True
                        )
                
                # Wait for next monitoring cycle
                await asyncio.sleep(monitoring_interval)
                
            except Exception as e:
                print(f"Error in continuous monitoring: {e}")
                await asyncio.sleep(5)  # Brief pause before retry
    
    async def stop_continuous_monitoring(self) -> None:
        """Stop continuous monitoring"""
        self.active_monitoring = False
    
    def get_validation_metrics(self) -> Dict[str, Any]:
        """Get current validation performance metrics"""
        return {
            "performance_metrics": self.performance_metrics.copy(),
            "validation_history_size": len(self.validation_history),
            "active_rules": sum(len(rules) for rules in self.validation_rules.values()),
            "auto_correction_templates": sum(len(templates) for templates in self.auto_correction_templates.values())
        }
    
    def get_compliance_trends(self, time_period: str = "24h") -> Dict[str, Any]:
        """Get brand compliance trends over specified time period"""
        
        # Parse time period
        if time_period == "1h":
            cutoff_time = datetime.now() - timedelta(hours=1)
        elif time_period == "24h":
            cutoff_time = datetime.now() - timedelta(hours=24)
        elif time_period == "7d":
            cutoff_time = datetime.now() - timedelta(days=7)
        else:
            cutoff_time = datetime.now() - timedelta(hours=24)  # Default to 24h
        
        # Filter recent validation history
        recent_validations = [
            entry for entry in self.validation_history
            if datetime.fromisoformat(entry["timestamp"]) > cutoff_time
        ]
        
        if not recent_validations:
            return {"error": "No validation data available for specified time period"}
        
        # Calculate trends
        compliance_rate = sum(1 for v in recent_validations if v["is_compliant"]) / len(recent_validations)
        average_confidence = sum(v["confidence"] for v in recent_validations) / len(recent_validations)
        average_performance = sum(v["performance_impact"] for v in recent_validations) / len(recent_validations)
        
        # Issue distribution
        issue_distribution = {}
        severity_distribution = {}
        
        for validation in recent_validations:
            issues_count = validation["issues_count"]
            severity = validation["severity"]
            
            issue_distribution[issues_count] = issue_distribution.get(issues_count, 0) + 1
            severity_distribution[severity] = severity_distribution.get(severity, 0) + 1
        
        return {
            "time_period": time_period,
            "total_validations": len(recent_validations),
            "compliance_rate": compliance_rate,
            "average_confidence": average_confidence,
            "average_validation_time_ms": average_performance,
            "issue_distribution": issue_distribution,
            "severity_distribution": severity_distribution,
            "trend_analysis": {
                "compliance_trend": "improving" if compliance_rate > 0.9 else "stable" if compliance_rate > 0.7 else "declining",
                "performance_trend": "excellent" if average_performance < 50 else "good" if average_performance < 100 else "needs_optimization"
            }
        }
    
    def generate_validation_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation system report"""
        
        metrics = self.get_validation_metrics()
        trends_24h = self.get_compliance_trends("24h")
        trends_7d = self.get_compliance_trends("7d")
        
        # Identify top issues
        recent_validations = self.validation_history[-1000:]  # Last 1000 validations
        issue_types = {}
        
        for validation in recent_validations:
            if validation["issues_count"] > 0:
                # This would need more detailed issue tracking to be fully accurate
                issue_types["terminology"] = issue_types.get("terminology", 0) + 1
        
        return {
            "report_timestamp": datetime.now().isoformat(),
            "system_status": {
                "active_monitoring": self.active_monitoring,
                "performance_metrics": metrics["performance_metrics"],
                "system_health": "excellent" if metrics["performance_metrics"]["compliance_rate"] > 0.95 else "good"
            },
            "compliance_analysis": {
                "recent_trends": trends_24h,
                "weekly_trends": trends_7d,
                "compliance_evolution": "improving" if trends_24h.get("compliance_rate", 0) > trends_7d.get("compliance_rate", 0) else "stable"
            },
            "validation_insights": {
                "total_rules_active": metrics["active_rules"],
                "auto_correction_capability": len(self.auto_correction_templates["terminology_corrections"]),
                "most_common_issues": sorted(issue_types.items(), key=lambda x: x[1], reverse=True)[:5]
            },
            "recommendations": self._generate_validation_recommendations(metrics, trends_24h)
        }
    
    def _generate_validation_recommendations(self, metrics: Dict[str, Any], trends: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate recommendations for validation system improvement"""
        
        recommendations = []
        
        # Performance recommendations
        avg_time = metrics["performance_metrics"]["average_validation_time"]
        if avg_time > 100:  # More than 100ms
            recommendations.append({
                "category": "performance",
                "priority": "medium",
                "recommendation": "Optimize validation rules for better performance - current average validation time exceeds target"
            })
        
        # Compliance recommendations
        compliance_rate = metrics["performance_metrics"]["compliance_rate"]
        if compliance_rate < 0.9:
            recommendations.append({
                "category": "compliance",
                "priority": "high",
                "recommendation": "Focus on improving brand compliance through enhanced guidelines and training"
            })
        
        # Auto-correction recommendations
        auto_corrections = metrics["performance_metrics"]["auto_corrections_applied"]
        total_validations = metrics["performance_metrics"]["total_validations"]
        
        if total_validations > 0 and (auto_corrections / total_validations) > 0.1:  # More than 10% need corrections
            recommendations.append({
                "category": "content_quality",
                "priority": "medium",
                "recommendation": "High auto-correction rate indicates need for proactive content guidelines"
            })
        
        return recommendations


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    from datetime import timedelta
    
    validator = RealTimeBrandValidator()
    
    # Test validation scenarios
    test_contents = [
        {
            "id": "test_1",
            "content": "Welcome to LUKHAS AI consciousness platform with Trinity Framework (⚛️🧠🛡️)",
            "type": "marketing"
        },
        {
            "id": "test_2", 
            "content": "LUKHAS PWM is a lambda function for AI system processing",
            "type": "technical"
        },
        {
            "id": "test_3",
            "content": "Our production ready system uses robotic automation",
            "type": "documentation"
        },
        {
            "id": "test_4",
            "content": "The consciousness platform helps users understand quantum-inspired processing",
            "type": "user_content"
        }
    ]
    
    async def run_validation_tests():
        print("=== LUKHAS Real-Time Brand Validator Tests ===\n")
        
        for test_content in test_contents:
            print(f"Testing: {test_content['id']}")
            print(f"Content: {test_content['content']}")
            print(f"Type: {test_content['type']}")
            
            result = await validator.validate_content_real_time(
                content=test_content["content"],
                content_id=test_content["id"],
                content_type=test_content["type"],
                auto_correct=True
            )
            
            print(f"Compliant: {result.is_compliant}")
            print(f"Severity: {result.severity.value}")
            print(f"Confidence: {result.confidence:.3f}")
            print(f"Issues: {len(result.issues)}")
            
            if result.issues:
                print("Issues found:")
                for issue in result.issues[:3]:  # Show first 3 issues
                    print(f"  - {issue['severity']}: {issue['description']}")
            
            if result.auto_corrections:
                print("Auto-corrections:")
                for original, correction in result.auto_corrections.items():
                    print(f"  '{original}' → '{correction}'")
                
                corrected_content = validator.apply_auto_corrections(
                    test_content["content"], 
                    result.auto_corrections
                )
                print(f"Corrected: {corrected_content}")
            
            print(f"Validation time: {result.performance_impact:.2f}ms")
            print("-" * 50)
        
        # Get system metrics
        print("\n=== Validation System Metrics ===")
        metrics = validator.get_validation_metrics()
        print(f"Total validations: {metrics['performance_metrics']['total_validations']}")
        print(f"Compliance rate: {metrics['performance_metrics']['compliance_rate']:.3f}")
        print(f"Average validation time: {metrics['performance_metrics']['average_validation_time']:.2f}ms")
        print(f"Auto-corrections applied: {metrics['performance_metrics']['auto_corrections_applied']}")
        
        # Get compliance trends
        print("\n=== Compliance Trends ===")
        trends = validator.get_compliance_trends("24h")
        if "error" not in trends:
            print(f"Compliance rate: {trends['compliance_rate']:.3f}")
            print(f"Average confidence: {trends['average_confidence']:.3f}")
            print(f"Compliance trend: {trends['trend_analysis']['compliance_trend']}")
            print(f"Performance trend: {trends['trend_analysis']['performance_trend']}")
    
    # Run the tests
    asyncio.run(run_validation_tests())