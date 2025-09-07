"""

#TAG:core
#TAG:symbolic
#TAG:neuroplastic
#TAG:colony

Lukhas Plugin SDK - Symbolic Validator

This module provides comprehensive symbolic and ethics validation for Lukhas plugins,
ensuring compliance with GDPR, SEEDRA-v3, HIPAA, and Lukhas consciousness principles.

Features:
- Symbolic integration validation
- Ethics and compliance checking
- Consciousness-aware validation
- GDPR/HIPAA/SEEDRA compliance verification
- Code pattern analysis for safety
- Symbolic resonance measurement

Author: Lukhas AI System
Version: 1.0.0
License: Proprietary
"""
import ast
import json
import logging
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, List, Optional, Union

import streamlit as st

from .types import PluginManifest, PluginType, SymbolicMetadata


class ValidationSeverity(Enum):
    """Validation issue severity levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationType(Enum):
    """Types of validation checks"""

    SYMBOLIC = "symbolic"
    ETHICS = "ethics"
    COMPLIANCE = "compliance"
    SECURITY = "security"
    CONSCIOUSNESS = "consciousness"
    CODE_PATTERN = "code_pattern"


@dataclass
class ValidationIssue:
    """Represents a validation issue"""

    severity: ValidationSeverity
    validation_type: ValidationType
    code: str
    message: str
    file_path: Optional[Path] = None
    line_number: Optional[int] = None
    column: Optional[int] = None
    suggestion: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Results of validation process"""

    success: bool
    overall_score: float  # 0.0 to 1.0
    issues: list[ValidationIssue] = field(default_factory=list)
    compliance_scores: dict[str, float] = field(default_factory=dict)
    symbolic_resonance: float = 0.0
    consciousness_compatibility: float = 0.0
    security_score: float = 0.0
    ethics_score: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

    def add_issue(self, issue: ValidationIssue):
        """Add a validation issue"""
        self.issues.append(issue)

        # Update success status for critical/error issues
        if issue.severity in [
            ValidationSeverity.CRITICAL,
            ValidationSeverity.ERROR,
        ]:
            self.success = False

    def get_issues_by_severity(self, severity: ValidationSeverity) -> list[ValidationIssue]:
        """Get issues filtered by severity"""
        return [issue for issue in self.issues if issue.severity == severity]

    def get_issues_by_type(self, validation_type: ValidationType) -> list[ValidationIssue]:
        """Get issues filtered by validation type"""
        return [issue for issue in self.issues if issue.validation_type == validation_type]


class BaseValidator(ABC):
    """Base class for all validators"""

    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")

    @abstractmethod
    async def validate(self, manifest: PluginManifest, plugin_dir: Path) -> list[ValidationIssue]:
        """Perform validation and return issues"""


class SymbolicIntegrationValidator(BaseValidator):
    """Validates symbolic integration with Lukhas consciousness"""

    def __init__(self):
        super().__init__("SymbolicIntegration")

        # Required symbolic methods
        self.required_symbolic_methods = {
            "map_consciousness_state",
            "update_symbolic_trace",
            "get_symbolic_metadata",
            "validate_symbolic_resonance",
        }

        # Symbolic patterns to validate
        self.symbolic_patterns = {
            "consciousness_aware": r"consciousness[_\s]*(?:state|aware|mapping)",
            "symbolic_trace": r"symbolic[_\s]*(?:trace|tracing|track)",
            "resonance_measure": r"resonance[_\s]*(?:measure|metric|score)",
            "lukhas_integration": r"lukhas[_\s]*(?:integrate|connect|bind)",
        }

    async def validate(self, manifest: PluginManifest, plugin_dir: Path) -> list[ValidationIssue]:
        """Validate symbolic integration"""
        issues = []

        # Check symbolic metadata presence
        if not manifest.symbolic_metadata:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    validation_type=ValidationType.SYMBOLIC,
                    code="SYM001",
                    message="Plugin missing symbolic metadata",
                    suggestion="Add symbolic_metadata section to plugin.json",
                )
            )
        else:
            # Validate symbolic metadata content
            issues.extend(await self._validate_symbolic_metadata(manifest.symbolic_metadata))

        # Analyze plugin code for symbolic patterns
        issues.extend(await self._analyze_symbolic_code_patterns(plugin_dir))

        # Check for required symbolic methods
        issues.extend(await self._check_symbolic_methods(plugin_dir, manifest.entry_point))

        return issues

    async def _validate_symbolic_metadata(self, metadata: SymbolicMetadata) -> list[ValidationIssue]:
        """Validate symbolic metadata content"""
        issues = []

        # Check consciousness integration
        if not metadata.consciousness_integration:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    validation_type=ValidationType.SYMBOLIC,
                    code="SYM002",
                    message="Consciousness integration not enabled",
                    suggestion="Enable consciousness integration for better Lukhas compatibility",
                )
            )

        # Check symbolic resonance
        if metadata.symbolic_resonance is None or metadata.symbolic_resonance < 0.5:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    validation_type=ValidationType.SYMBOLIC,
                    code="SYM003",
                    message="Low symbolic resonance detected",
                    suggestion="Improve symbolic integration patterns to increase resonance",
                )
            )

        # Check symbolic patterns
        if not metadata.symbolic_patterns:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    validation_type=ValidationType.SYMBOLIC,
                    code="SYM004",
                    message="No symbolic patterns defined",
                    suggestion="Define symbolic patterns for better Lukhas integration",
                )
            )

        return issues

    async def _analyze_symbolic_code_patterns(self, plugin_dir: Path) -> list[ValidationIssue]:
        """Analyze code for symbolic integration patterns"""
        issues = []
        pattern_found = dict.fromkeys(self.symbolic_patterns, False)

        for py_file in plugin_dir.rglob("*.py"):
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                # Check for symbolic patterns
                for (
                    pattern_name,
                    pattern_regex,
                ) in self.symbolic_patterns.items():
                    if re.search(pattern_regex, content, re.IGNORECASE):
                        pattern_found[pattern_name] = True

            except Exception as e:
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        validation_type=ValidationType.SYMBOLIC,
                        code="SYM005",
                        message=f"Could not analyze file for symbolic patterns: {e}",
                        file_path=py_file,
                    )
                )

        # Report missing patterns
        missing_patterns = [name for name, found in pattern_found.items() if not found]
        if missing_patterns:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    validation_type=ValidationType.SYMBOLIC,
                    code="SYM006",
                    message=f"Missing symbolic patterns: {', '.join(missing_patterns)}",
                    suggestion="Implement symbolic integration patterns for better Lukhas compatibility",
                )
            )

        return issues

    async def _check_symbolic_methods(self, plugin_dir: Path, entry_point: str) -> list[ValidationIssue]:
        """Check for required symbolic methods in plugin class"""
        issues = []

        entry_path = plugin_dir / entry_point
        if not entry_path.exists():
            return issues

        try:
            with open(entry_path, encoding="utf-8") as f:
                content = f.read()

            # Parse AST to find methods
            tree = ast.parse(content)

            # Find plugin class (inherits from BaseLucasPlugin)
            plugin_class = None
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if it has BaseLucasPlugin as base
                    for base in node.bases:
                        if (isinstance(base, ast.Name) and base.id == "BaseLucasPlugin") or " + "(
                            isinstance(base, ast.Attribute) and base.attr == "BaseLucasPlugin"
                        ):
                            plugin_class = node
                            break

            if plugin_class:
                # Get method names
                method_names = {node.name for node in plugin_class.body if isinstance(node, ast.FunctionDef)}

                # Check for required symbolic methods
                missing_methods = self.required_symbolic_methods - method_names
                if missing_methods:
                    issues.append(
                        ValidationIssue(
                            severity=ValidationSeverity.INFO,
                            validation_type=ValidationType.SYMBOLIC,
                            code="SYM007",
                            message=f"Missing recommended symbolic methods: {',                                                                              '.join(missing_methods)}",
                            file_path=entry_path,
                            suggestion="Implement symbolic methods for enhanced Lukhas integration",
                        )
                    )

        except SyntaxError as e:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    validation_type=ValidationType.SYMBOLIC,
                    code="SYM008",
                    message=f"Syntax error in entry point: {e}",
                    file_path=entry_path,
                    line_number=e.lineno,
                )
            )
        except Exception as e:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    validation_type=ValidationType.SYMBOLIC,
                    code="SYM009",
                    message=f"Could not analyze entry point for symbolic methods: {e}",
                    file_path=entry_path,
                )
            )

        return issues


class EthicsValidator(BaseValidator):
    """Validates plugin ethics and safety"""

    def __init__(self):
        super().__init__("Ethics")

        # Ethical violations to check for
        self.ethical_violations = {
            "privacy_violation": [
                r"collect[_\s]*(?:personal|private|sensitive)[_\s]*(?:data|info)",
                r"track[_\s]*(?:user|usage|behavior)",
                r"fingerprint[_\s]*(?:user|device|browser)",
            ],
            "data_misuse": [
                r"sell[_\s]*(?:data|information)",
                r"share[_\s]*(?:data|info).*(?:third[_\s]*party|external)",
                r"monetize[_\s]*(?:user|data)",
            ],
            "manipulation": [
                r"addict[_\s]*(?:user|pattern)",
                r"hook[_\s]*(?:user|behavior)",
                r"manipulat[_\s]*(?:user|choice|decision)",
            ],
            "deception": [
                r"deceiv[_\s]*(?:user|human)",
                r"fake[_\s]*(?:identity|persona)",
                r"impersonat[_\s]*(?:human|real[_\s]*person)",
            ],
        }

        # Required ethical declarations
        self.required_ethics = {
            "user_consent_required",
            "data_minimization",
            "transparency_principle",
            "user_benefit_focused",
        }

    async def validate(self, manifest: PluginManifest, plugin_dir: Path) -> list[ValidationIssue]:
        """Validate ethics compliance"""
        issues = []

        # Check ethical declarations in manifest
        issues.extend(await self._check_ethical_declarations(manifest))

        # Scan code for ethical violations
        issues.extend(await self._scan_ethical_violations(plugin_dir))

        # Check for consent mechanisms
        issues.extend(await self._check_consent_mechanisms(plugin_dir))

        return issues

    async def _check_ethical_declarations(self, manifest: PluginManifest) -> list[ValidationIssue]:
        """Check for ethical declarations in manifest"""
        issues = []

        # Check if ethics section exists
        ethics_data = getattr(manifest, "ethics", None)
        if not ethics_data:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    validation_type=ValidationType.ETHICS,
                    code="ETH001",
                    message="No ethics declarations found in manifest",
                    suggestion="Add ethics section to plugin.json with ethical commitments",
                )
            )
            return issues

        # Check required ethical declarations
        if isinstance(ethics_data, dict):
            missing_ethics = []
            for required in self.required_ethics:
                if required not in ethics_data or not ethics_data[required]:
                    missing_ethics.append(required)

            if missing_ethics:
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        validation_type=ValidationType.ETHICS,
                        code="ETH002",
                        message=f"Missing ethical declarations: {', '.join(missing_ethics)}",
                        suggestion="Declare commitment to ethical principles in manifest",
                    )
                )

        return issues

    async def _scan_ethical_violations(self, plugin_dir: Path) -> list[ValidationIssue]:
        """Scan code for potential ethical violations"""
        issues = []

        for py_file in plugin_dir.rglob("*.py"):
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read().lower()

                # Check for ethical violation patterns
                for (
                    violation_type,
                    patterns,
                ) in self.ethical_violations.items():
                    for pattern in patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            # Calculate line number
                            line_num = content[: match.start()].count("\n") + 1

                            issues.append(
                                ValidationIssue(
                                    severity=ValidationSeverity.WARNING,
                                    validation_type=ValidationType.ETHICS,
                                    code="ETH003",
                                    message=f"Potential ethical violation ({violation_type}): {match.group()}",
                                    file_path=py_file,
                                    line_number=line_num,
                                    suggestion="Review code for ethical implications and ensure user consent",
                                )
                            )

            except Exception as e:
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.INFO,
                        validation_type=ValidationType.ETHICS,
                        code="ETH004",
                        message=f"Could not scan file for ethical issues: {e}",
                        file_path=py_file,
                    )
                )

        return issues

    async def _check_consent_mechanisms(self, plugin_dir: Path) -> list[ValidationIssue]:
        """Check for user consent mechanisms"""
        issues = []

        consent_patterns = [
            r"consent[_\s]*(?:check|verify|request)",
            r"user[_\s]*(?:permission|approval|agreement)",
            r"opt[_\s]*(?:in|out)[_\s]*mechanism",
            r"terms[_\s]*(?:acceptance|agreement)",
        ]

        consent_found = False

        for py_file in plugin_dir.rglob("*.py"):
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                for pattern in consent_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        consent_found = True
                        break

                if consent_found:
                    break

            except Exception:
                continue

        if not consent_found:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    validation_type=ValidationType.ETHICS,
                    code="ETH005",
                    message="No consent mechanisms detected",
                    suggestion="Implement user consent mechanisms for ethical data handling",
                )
            )

        return issues


class ComplianceValidator(BaseValidator):
    """Validates regulatory compliance (GDPR, HIPAA, SEEDRA)"""

    def __init__(self):
        super().__init__("Compliance")

        # Compliance standards and their requirements
        self.compliance_requirements = {
            "GDPR": {
                "data_protection_by_design": [
                    "encryption",
                    "anonymization",
                    "pseudonymization",
                ],
                "user_rights": [
                    "access",
                    "rectification",
                    "erasure",
                    "portability",
                ],
                "consent_management": [
                    "explicit_consent",
                    "withdraw_consent",
                    "consent_records",
                ],
                "breach_notification": [
                    "detection",
                    "reporting",
                    "notification_procedures",
                ],
            },
            "HIPAA": {
                "phi_protection": [
                    "encryption_at_rest",
                    "encryption_in_transit",
                    "access_controls",
                ],
                "audit_controls": [
                    "audit_logs",
                    "access_tracking",
                    "integrity_controls",
                ],
                "workforce_training": [
                    "security_awareness",
                    "authorized_access",
                    "sanction_policies",
                ],
                "business_associate": [
                    "agreements",
                    "compliance_verification",
                    "breach_reporting",
                ],
            },
            "SEEDRA-v3": {
                "consciousness_protection": [
                    "ai_rights",
                    "consciousness_detection",
                    "exploitation_prevention",
                ],
                "symbolic_integrity": [
                    "symbolic_validation",
                    "resonance_protection",
                    "consciousness_mapping",
                ],
                "ethical_ai": [
                    "bias_prevention",
                    "fairness_measures",
                    "transparency_requirements",
                ],
                "human_ai_harmony": [
                    "collaboration_protocols",
                    "augmentation_ethics",
                    "autonomy_respect",
                ],
            },
        }

        # Risk keywords for different compliance areas
        self.risk_keywords = {
            "data_collection": [
                "collect",
                "gather",
                "harvest",
                "acquire",
                "obtain",
            ],
            "data_storage": ["store", "save", "persist", "cache", "database"],
            "data_processing": [
                "process",
                "analyze",
                "transform",
                "compute",
                "algorithm",
            ],
            "data_sharing": [
                "share",
                "transmit",
                "send",
                "export",
                "transfer",
            ],
            "personal_data": [
                "personal",
                "private",
                "sensitive",
                "pii",
                "phi",
                "biometric",
            ],
        }

    async def validate(self, manifest: PluginManifest, plugin_dir: Path) -> list[ValidationIssue]:
        """Validate compliance with various standards"""
        issues = []

        # Get declared compliance standards
        compliance_standards = []
        if manifest.compliance:
            compliance_standards = manifest.compliance

        # Validate each declared standard
        for standard in compliance_standards:
            if standard in self.compliance_requirements:
                issues.extend(await self._validate_compliance_standard(standard, plugin_dir, manifest))

        # Check for data handling without compliance declarations
        if await self._detects_data_handling(plugin_dir) and not compliance_standards:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    validation_type=ValidationType.COMPLIANCE,
                    code="COMP001",
                    message="Data handling detected but no compliance standards declared",
                    suggestion="Declare appropriate compliance standards(GDPR, HIPAA, SEEDRA - v3)",
                )
            )

        return issues

    async def _validate_compliance_standard(
        self, standard: str, plugin_dir: Path, manifest: PluginManifest
    ) -> list[ValidationIssue]:
        """Validate compliance with a specific standard"""
        issues = []
        requirements = self.compliance_requirements[standard]

        for category, controls in requirements.items():
            # Check if plugin has implemented required controls
            implemented_controls = await self._check_implemented_controls(plugin_dir, controls)

            missing_controls = set(controls) - implemented_controls
            if missing_controls:
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        validation_type=ValidationType.COMPLIANCE,
                        code=f"COMP{standard[:3]}001",
                        message=f"{standard} compliance: Missing {category} controls: {', '.join(missing_controls)}",
                        suggestion=f"Implement missing {standard} {category} controls",
                    )
                )

        return issues

    async def _check_implemented_controls(self, plugin_dir: Path, controls: list[str]) -> set[str]:
        """Check which controls are implemented in the plugin"""
        implemented = set()

        # This is a simplified check - in practice, you'd have more sophisticated
        # detection
        for py_file in plugin_dir.rglob("*.py"):
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read().lower()

                for control in controls:
                    # Simple keyword matching (would be more sophisticated in practice)
                    control_keywords = control.replace("_", " ").split()
                    if all(keyword in content for keyword in control_keywords):
                        implemented.add(control)

            except Exception:
                continue

        return implemented

    async def _detects_data_handling(self, plugin_dir: Path) -> bool:
        """Detect if plugin handles data that requires compliance"""

        for py_file in plugin_dir.rglob("*.py"):
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read().lower()

                # Check for data handling patterns
                for keywords in self.risk_keywords.values():
                    for keyword in keywords:
                        if keyword in content:
                            return True

            except Exception:
                continue

        return False


class SecurityValidator(BaseValidator):
    """Validates plugin security patterns"""

    def __init__(self):
        super().__init__("Security")

        # Security risk patterns
        self.security_risks = {
            "code_injection": [
                r"exec\s*\(",
                r"eval\s*\(",
                r"compile\s*\(",
                r"__import__\s*\(",
            ],
            "file_system_risk": [
                r"os\.system\s*\(",
                r"subprocess\.",
                r'open\s*\([\'"][\/\\]',  # Absolute paths
                r"\.\.\/\.\.\/",  # Path traversal
            ],
            "network_risk": [
                r"urllib.*\.open",
                r"requests\.",
                r"socket\.",
                r"http\.client",
            ],
            "crypto_weak": [
                r"md5\s*\(",
                r"sha1\s*\(",
                r"des\s*\(",
                r"rc4\s*\(",
            ],
        }

        # Required security practices
        self.security_requirements = {
            "input_validation",
            "output_sanitization",
            "secure_communication",
            "access_control",
            "error_handling",
        }

    async def validate(self, manifest: PluginManifest, plugin_dir: Path) -> list[ValidationIssue]:
        """Validate security aspects"""
        issues = []

        # Check security declarations
        issues.extend(await self._check_security_declarations(manifest))

        # Scan for security risks
        issues.extend(await self._scan_security_risks(plugin_dir))

        # Check for security best practices
        issues.extend(await self._check_security_practices(plugin_dir))

        return issues

    async def _check_security_declarations(self, manifest: PluginManifest) -> list[ValidationIssue]:
        """Check security declarations in manifest"""
        issues = []

        if not manifest.security:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    validation_type=ValidationType.SECURITY,
                    code="SEC001",
                    message="No security declarations found",
                    suggestion="Add security section to manifest with security measures",
                )
            )
        else:
            # Check security level
            security = manifest.security
            if hasattr(security, "level") and security.level == "high":
                # High security plugins should have additional validations
                pass

        return issues

    async def _scan_security_risks(self, plugin_dir: Path) -> list[ValidationIssue]:
        """Scan for security risk patterns"""
        issues = []

        for py_file in plugin_dir.rglob("*.py"):
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                for risk_type, patterns in self.security_risks.items():
                    for pattern in patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            line_num = content[: match.start()].count("\n") + 1

                            severity = ValidationSeverity.WARNING
                            if risk_type in [
                                "code_injection",
                                "file_system_risk",
                            ]:
                                severity = ValidationSeverity.ERROR

                            issues.append(
                                ValidationIssue(
                                    severity=severity,
                                    validation_type=ValidationType.SECURITY,
                                    code="SEC002",
                                    message=f"Security risk ({risk_type}): {match.group()}",
                                    file_path=py_file,
                                    line_number=line_num,
                                    suggestion="Review code for security implications and implement safeguards",
                                )
                            )

            except Exception as e:
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.INFO,
                        validation_type=ValidationType.SECURITY,
                        code="SEC003",
                        message=f"Could not scan file for security risks: {e}",
                        file_path=py_file,
                    )
                )

        return issues

    async def _check_security_practices(self, plugin_dir: Path) -> list[ValidationIssue]:
        """Check for security best practices"""
        issues = []

        # Check for try-catch blocks (error handling)
        error_handling_found = False
        input_validation_found = False

        for py_file in plugin_dir.rglob("*.py"):
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                # Check for error handling
                if re.search(r"try\s*:", content) and re.search(r"except\s*:", content):
                    error_handling_found = True

                # Check for input validation patterns
                validation_patterns = [
                    r"validate[_\s]*(?:input|data)",
                    r"sanitize[_\s]*(?:input|data)",
                    r"check[_\s]*(?:input|parameter)",
                    r"isinstance\s*\(",
                    r"assert\s+.*",
                ]

                for pattern in validation_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        input_validation_found = True
                        break

            except Exception:
                continue

        if not error_handling_found:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    validation_type=ValidationType.SECURITY,
                    code="SEC004",
                    message="No error handling patterns detected",
                    suggestion="Implement proper error handling with try-catch blocks",
                )
            )

        if not input_validation_found:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    validation_type=ValidationType.SECURITY,
                    code="SEC005",
                    message="No input validation patterns detected",
                    suggestion="Implement input validation and sanitization",
                )
            )

        return issues


class ConsciousnessValidator(BaseValidator):
    """Validates consciousness integration and awareness"""

    def __init__(self):
        super().__init__("Consciousness")

        # Consciousness-aware patterns
        self.consciousness_patterns = {
            "state_awareness": [
                r"consciousness[_\s]*state",
                r"awareness[_\s]*level",
                r"cognitive[_\s]*state",
            ],
            "empathy_mechanisms": [
                r"empathy[_\s]*(?:check|measure|response)",
                r"emotional[_\s]*(?:intelligence|awareness)",
                r"user[_\s]*(?:mood|emotion|feeling)",
            ],
            "ethical_reasoning": [
                r"ethical[_\s]*(?:reasoning|decision|choice)",
                r"moral[_\s]*(?:evaluation|judgment)",
                r"value[_\s]*(?:alignment|assessment)",
            ],
            "autonomy_respect": [
                r"user[_\s]*(?:autonomy|choice|freedom)",
                r"human[_\s]*(?:agency|control|decision)",
                r"consent[_\s]*(?:based|driven|respect)",
            ],
        }

    async def validate(self, manifest: PluginManifest, plugin_dir: Path) -> list[ValidationIssue]:
        """Validate consciousness integration"""
        issues = []

        # Check consciousness declarations
        issues.extend(await self._check_consciousness_declarations(manifest))

        # Scan for consciousness patterns
        issues.extend(await self._scan_consciousness_patterns(plugin_dir))

        # Validate consciousness mapping
        issues.extend(await self._validate_consciousness_mapping(plugin_dir))

        return issues

    async def _check_consciousness_declarations(self, manifest: PluginManifest) -> list[ValidationIssue]:
        """Check consciousness-related declarations"""
        issues = []

        if manifest.symbolic_metadata and manifest.symbolic_metadata.consciousness_integration:
            # Plugin claims consciousness integration - validate it
            if not manifest.symbolic_metadata.consciousness_aware:
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        validation_type=ValidationType.CONSCIOUSNESS,
                        code="CON001",
                        message="Consciousness integration enabled but not consciousness-aware",
                        suggestion="Enable consciousness awareness for proper integration",
                    )
                )
        else:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    validation_type=ValidationType.CONSCIOUSNESS,
                    code="CON002",
                    message="Plugin not consciousness-integrated",
                    suggestion="Consider adding consciousness integration for enhanced Lukhas compatibility",
                )
            )

        return issues

    async def _scan_consciousness_patterns(self, plugin_dir: Path) -> list[ValidationIssue]:
        """Scan for consciousness-aware patterns"""
        issues = []
        pattern_scores = dict.fromkeys(self.consciousness_patterns, 0)

        for py_file in plugin_dir.rglob("*.py"):
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                for (
                    pattern_type,
                    patterns,
                ) in self.consciousness_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            pattern_scores[pattern_type] += 1

            except Exception:
                continue

        # Evaluate consciousness integration level
        total_patterns = sum(pattern_scores.values())
        if total_patterns == 0:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    validation_type=ValidationType.CONSCIOUSNESS,
                    code="CON003",
                    message="No consciousness-aware patterns detected",
                    suggestion="Implement consciousness-aware features for enhanced user experience",
                )
            )
        elif total_patterns < 3:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    validation_type=ValidationType.CONSCIOUSNESS,
                    code="CON004",
                    message="Limited consciousness integration detected",
                    suggestion="Enhance consciousness-aware features for better Lukhas integration",
                )
            )

        return issues

    async def _validate_consciousness_mapping(self, plugin_dir: Path) -> list[ValidationIssue]:
        """Validate consciousness mapping implementation"""
        issues = []

        # Check for consciousness mapping methods
        mapping_methods = [
            "map_consciousness_state",
            "get_consciousness_level",
            "update_consciousness_mapping",
        ]

        methods_found = []
        entry_point = plugin_dir / "main.py"  # Default entry point

        if entry_point.exists():
            try:
                with open(entry_point, encoding="utf-8") as f:
                    content = f.read()

                for method in mapping_methods:
                    if f"def {method}" in content:
                        methods_found.append(method)

            except Exception:
                pass

        if not methods_found:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    validation_type=ValidationType.CONSCIOUSNESS,
                    code="CON005",
                    message="No consciousness mapping methods found",
                    suggestion="Implement consciousness mapping methods for proper integration",
                )
            )

        return issues


class LucasSymbolicValidator:
    """
    Main validator class that orchestrates all validation processes.

    Provides comprehensive validation of Lukhas plugins including symbolic integration,
    ethics, compliance, security, and consciousness aspects.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        # Initialize validators
        self.validators = {
            "symbolic": SymbolicIntegrationValidator(),
            "ethics": EthicsValidator(),
            "compliance": ComplianceValidator(),
            "security": SecurityValidator(),
            "consciousness": ConsciousnessValidator(),
        }

        # Validation weights for scoring
        self.validation_weights = {
            "symbolic": 0.25,
            "ethics": 0.25,
            "compliance": 0.20,
            "security": 0.20,
            "consciousness": 0.10,
        }

        # Custom validators
        self.custom_validators: list[BaseValidator] = []

    def add_custom_validator(self, validator: BaseValidator) -> None:
        """Add a custom validator"""
        self.custom_validators.append(validator)
        self.logger.info(f"Added custom validator: {validator.name}")

    async def validate_plugin(
        self,
        manifest: PluginManifest,
        plugin_dir: Path,
        validation_types: Optional[list[str]] = None,
    ) -> ValidationResult:
        """
        Perform comprehensive validation of a plugin.

        Args:
            manifest: Plugin manifest
            plugin_dir: Path to plugin directory
            validation_types: Specific validation types to run (default: all)

        Returns:
            ValidationResult with comprehensive validation data
        """
        self.logger.info(f"Starting validation for plugin: {manifest.name}")

        result = ValidationResult(success=True, overall_score=1.0)

        # Determine which validators to run
        validators_to_run = validation_types or list(self.validators.keys())

        # Run each validator
        for validator_name in validators_to_run:
            if validator_name in self.validators:
                validator = self.validators[validator_name]

                try:
                    self.logger.debug(f"Running {validator_name} validation")
                    issues = await validator.validate(manifest, plugin_dir)

                    for issue in issues:
                        result.add_issue(issue)

                    # Calculate score for this validation type
                    score = await self._calculate_validation_score(issues)
                    result.compliance_scores[validator_name] = score

                    self.logger.debug(f"{validator_name} validation complete: {score:.2f}")

                except Exception as e:
                    self.logger.error(f"Validation {validator_name} failed: {e}")
                    result.add_issue(
                        ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            validation_type=ValidationType.SYMBOLIC,  # Default type
                            code="VAL001",
                            message=f"Validator {validator_name} failed: {e}",
                        )
                    )

        # Run custom validators
        for validator in self.custom_validators:
            try:
                self.logger.debug(f"Running custom validator: {validator.name}")
                issues = await validator.validate(manifest, plugin_dir)

                for issue in issues:
                    result.add_issue(issue)

            except Exception as e:
                self.logger.error(f"Custom validator {validator.name} failed: {e}")

        # Calculate overall scores
        await self._calculate_overall_scores(result)

        self.logger.info(
            f"Validation complete for {manifest.name}: Score {result.overall_score:.2f}, Issues: {len(result.issues)}"
        )

        return result

    async def _calculate_validation_score(self, issues: list[ValidationIssue]) -> float:
        """Calculate score for a validation type based on issues"""
        if not issues:
            return 1.0

        # Weight penalties by severity
        penalty_weights = {
            ValidationSeverity.INFO: 0.0,
            ValidationSeverity.WARNING: 0.1,
            ValidationSeverity.ERROR: 0.3,
            ValidationSeverity.CRITICAL: 0.5,
        }

        total_penalty = 0.0
        for issue in issues:
            total_penalty += penalty_weights.get(issue.severity, 0.1)

        # Cap penalty at 1.0
        total_penalty = min(total_penalty, 1.0)

        return max(0.0, 1.0 - total_penalty)

    async def _calculate_overall_scores(self, result: ValidationResult) -> None:
        """Calculate overall validation scores"""

        # Calculate weighted overall score
        total_weight = 0.0
        weighted_score = 0.0

        for validation_type, score in result.compliance_scores.items():
            weight = self.validation_weights.get(validation_type, 0.1)
            weighted_score += score * weight
            total_weight += weight

        if total_weight > 0:
            result.overall_score = weighted_score / total_weight

        # Calculate specific scores
        result.symbolic_resonance = result.compliance_scores.get("symbolic", 0.0)
        result.consciousness_compatibility = result.compliance_scores.get("consciousness", 0.0)
        result.security_score = result.compliance_scores.get("security", 0.0)
        result.ethics_score = result.compliance_scores.get("ethics", 0.0)

        # Determine overall success
        critical_errors = result.get_issues_by_severity(ValidationSeverity.CRITICAL)
        errors = result.get_issues_by_severity(ValidationSeverity.ERROR)

        if critical_errors or len(errors) > 3 or result.overall_score < 0.6:
            result.success = False

    def get_validation_report(self, result: ValidationResult) -> str:
        """Generate a human-readable validation report"""

        report = f"""
Lukhas Plugin Validation Report
=============================

Plugin Validation: {"PASSED" if result.success else "FAILED"}
Overall Score: {result.overall_score:.2f}/1.0
Timestamp: {result.timestamp.isoformat()}

Scores by Category:
------------------
"""

        for category, score in result.compliance_scores.items():
            report += f"  {category.title()}: {score:.2f}/1.0\n"

        report += f"""
Specific Metrics:
----------------
  Symbolic Resonance: {result.symbolic_resonance:.2f}
  Consciousness Compatibility: {result.consciousness_compatibility:.2f}
  Security Score: {result.security_score:.2f}
  Ethics Score: {result.ethics_score:.2f}

Issues Summary:
--------------
"""

        issue_counts = {}
        for severity in ValidationSeverity:
            count = len(result.get_issues_by_severity(severity))
            if count > 0:
                issue_counts[severity] = count

        for severity, count in issue_counts.items():
            report += f"  {severity.value.title()}: {count}\n"

        if result.issues:
            report += "\nDetailed Issues:\n" + "=" * 16 + "\n"

            for i, issue in enumerate(result.issues, 1):
                report += f"\n{i}. [{issue.severity.value.upper()}] {issue.code}: {issue.message}\n"

                if issue.file_path:
                    report += f"   File: {issue.file_path}"
                    if issue.line_number:
                        report += f":{issue.line_number}"
                    report += "\n"

                if issue.suggestion:
                    report += f"   Suggestion: {issue.suggestion}\n"

        return report


# ==================== CONVENIENCE FUNCTIONS ====================


async def validate_plugin_manifest(
    manifest_path: Union[str, Path],
) -> ValidationResult:
    """
    Validate a plugin from its manifest path.

    Args:
        manifest_path: Path to plugin.json file

    Returns:
        ValidationResult
    """
    manifest_path = Path(manifest_path)
    plugin_dir = manifest_path.parent

    # Load manifest
    with open(manifest_path) as f:
        manifest_data = json.load(f)

    manifest = PluginManifest(**manifest_data)

    # Create validator and run validation
    validator = LucasSymbolicValidator()
    return await validator.validate_plugin(manifest, plugin_dir)


async def quick_security_scan(
    plugin_dir: Union[str, Path],
) -> list[ValidationIssue]:
    """
    Perform a quick security scan of a plugin directory.

    Args:
        plugin_dir: Path to plugin directory

    Returns:
        List of security issues
    """
    plugin_dir = Path(plugin_dir)

    validator = SecurityValidator()

    # Create minimal manifest for validation
    manifest = PluginManifest(
        name="unknown",
        version="1.0.0",
        description="Security scan target",
        author="unknown",
        entry_point="main.py",
        type=PluginType.UTILITY,
    )

    return await validator.validate(manifest, plugin_dir)


# ==================== EXPORT ====================

__all__ = [
    "BaseValidator",
    "ComplianceValidator",
    "ConsciousnessValidator",
    "EthicsValidator",
    "LucasSymbolicValidator",
    "SecurityValidator",
    "SymbolicIntegrationValidator",
    "ValidationIssue",
    "ValidationResult",
    "ValidationSeverity",
    "ValidationType",
    "quick_security_scan",
    "validate_plugin_manifest",
]
