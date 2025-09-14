#!/usr/bin/env python3
"""
LUKHAS AI - Comprehensive API Validation System
==============================================

Advanced validation system for API requests, responses, and orchestration
with security validation, rate limiting, and performance monitoring.

Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
Performance Target: <10ms validation latency
Supports: Request validation, response validation, security checks

Features:
- Multi-layer request validation with Pydantic models
- Security validation and sanitization
- Rate limiting and authentication validation
- Performance monitoring and metrics
- Healthcare data validation (HIPAA compliance)
- Function calling validation and security
- Error handling with detailed error codes
"""
import asyncio
import hashlib
import logging
import re
import time
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

try:
    import jwt
    from pydantic import (
        BaseModel,
        Field,
        ValidationError,
        validator,
    )  # MATRIZ Integration: Pydantic validation models for API expansion and data validation architecture

    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

logger = logging.getLogger(__name__)


# Validation Error Types
class ValidationErrorType(Enum):
    """Types of validation errors"""

    INVALID_FORMAT = "invalid_format"
    MISSING_FIELD = "missing_field"
    INVALID_VALUE = "invalid_value"
    SECURITY_VIOLATION = "security_violation"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    AUTHENTICATION_FAILED = "authentication_failed"
    AUTHORIZATION_FAILED = "authorization_failed"
    COST_LIMIT_EXCEEDED = "cost_limit_exceeded"
    CONTENT_POLICY_VIOLATION = "content_policy_violation"
    HIPAA_VIOLATION = "hipaa_violation"
    DATA_SIZE_EXCEEDED = "data_size_exceeded"
    FUNCTION_SECURITY_VIOLATION = "function_security_violation"


class ValidationSeverity(Enum):
    """Severity levels for validation errors"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationResult(BaseModel):
    """Result of validation operation"""

    is_valid: bool = Field(..., description="Whether validation passed")
    errors: list[dict[str, Any]] = Field(default_factory=list, description="Validation errors")
    warnings: list[dict[str, Any]] = Field(default_factory=list, description="Validation warnings")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Validation metadata")
    execution_time_ms: float = Field(0.0, description="Validation execution time")
    validator_version: str = Field("2.0.0", description="Validator version")

    def add_error(
        self,
        error_type: ValidationErrorType,
        message: str,
        field: Optional[str] = None,
        severity: ValidationSeverity = ValidationSeverity.ERROR,
    ):
        """Add validation error"""
        self.is_valid = False
        self.errors.append(
            {
                "type": error_type.value,
                "message": message,
                "field": field,
                "severity": severity.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    def add_warning(self, message: str, field: Optional[str] = None):
        """Add validation warning"""
        self.warnings.append(
            {
                "message": message,
                "field": field,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    def summary(self) -> dict[str, Any]:
        """Return a governance-friendly summary for reporting pipelines."""
        error_counts: dict[str, int] = {}
        for e in self.errors:
            t = e.get("type", "unknown")
            error_counts[t] = error_counts.get(t, 0) + 1
        severity_counts: dict[str, int] = {}
        for e in self.errors:
            s = e.get("severity", "error")
            severity_counts[s] = severity_counts.get(s, 0) + 1
        return {
            "is_valid": self.is_valid,
            "errors": len(self.errors),
            "warnings": len(self.warnings),
            "error_counts": error_counts,
            "severity_counts": severity_counts,
            "execution_time_ms": self.execution_time_ms,
            "version": self.validator_version,
        }


class SecurityValidator:
    """Security validation for API requests"""

    # Dangerous patterns that should be blocked
    DANGEROUS_PATTERNS = [
        r"<script[^>]*>.*?</script>",  # XSS
        r"javascript:",  # JavaScript injection
        r"data:text/html",  # Data URL injection
        r"eval\s*\(",  # Code evaluation
        r"exec\s*\(",  # Code execution
        r"system\s*\(",  # System calls
        r"import\s+os",  # OS imports
        r"__import__",  # Dynamic imports
        r"subprocess",  # Subprocess calls
        r"shell=True",  # Shell injection
        r"DROP\s+TABLE",  # SQL injection
        r"DELETE\s+FROM",  # SQL injection
        r"INSERT\s+INTO",  # SQL injection
        r"UPDATE\s+SET",  # SQL injection
        r"UNION\s+SELECT",  # SQL injection
    ]

    # Healthcare-specific patterns (PHI detection)
    PHI_PATTERNS = [
        r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
        r"\b\d{16}\b",  # Credit card
        r"\b[A-Z]{2}\d{8}\b",  # Medical record number pattern
        r"patient\s+id[:\s]+\w+",  # Patient ID
        r"medical\s+record[:\s]+\w+",  # Medical record
    ]

    def __init__(self, enable_hipaa: bool = True):
        self.enable_hipaa = enable_hipaa
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.DANGEROUS_PATTERNS]
        self.phi_patterns = (
            [re.compile(pattern, re.IGNORECASE) for pattern in self.PHI_PATTERNS] if enable_hipaa else []
        )

    def validate_content_security(self, content: str, context: str = "general") -> list[dict[str, Any]]:
        """Validate content for security issues"""
        issues = []

        # Check for dangerous patterns
        for pattern in self.compiled_patterns:
            matches = pattern.findall(content)
            if matches:
                issues.append(
                    {
                        "type": ValidationErrorType.SECURITY_VIOLATION.value,
                        "pattern": pattern.pattern,
                        "matches": len(matches),
                        "severity": ValidationSeverity.CRITICAL.value,
                        "context": context,
                    }
                )

        # Check for PHI if healthcare context
        if self.enable_hipaa and context in ["healthcare", "medical", "patient"]:
            for pattern in self.phi_patterns:
                matches = pattern.findall(content)
                if matches:
                    issues.append(
                        {
                            "type": ValidationErrorType.HIPAA_VIOLATION.value,
                            "pattern": "PHI_DETECTED",
                            "matches": len(matches),
                            "severity": ValidationSeverity.CRITICAL.value,
                            "context": "healthcare_phi",
                        }
                    )

        return issues

    def validate_function_security(self, function_def: dict[str, Any]) -> list[dict[str, Any]]:
        """Validate function definition for security"""
        issues = []

        function_name = function_def.get("name", "")
        function_def.get("description", "")
        function_code = function_def.get("implementation", "")

        # Check function name
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", function_name):
            issues.append(
                {
                    "type": ValidationErrorType.FUNCTION_SECURITY_VIOLATION.value,
                    "message": "Invalid function name format",
                    "severity": ValidationSeverity.ERROR.value,
                }
            )

        # Check for dangerous patterns in function code
        if function_code:
            security_issues = self.validate_content_security(function_code, "function")
            issues.extend(security_issues)

        # Check function permissions
        permissions = function_def.get("permissions", [])
        dangerous_permissions = ["file_system", "network", "system", "exec", "eval"]
        for perm in permissions:
            if perm in dangerous_permissions:
                issues.append(
                    {
                        "type": ValidationErrorType.FUNCTION_SECURITY_VIOLATION.value,
                        "message": f"Dangerous permission requested: {perm}",
                        "severity": ValidationSeverity.WARNING.value,
                    }
                )

        return issues


class RequestValidator:
    """Comprehensive request validation"""

    def __init__(self, max_content_length: int = 100000, max_function_count: int = 50):
        self.max_content_length = max_content_length
        self.max_function_count = max_function_count
        self.security_validator = SecurityValidator()

    async def validate_orchestration_request(
        self, request_data: dict[str, Any], context: Optional[dict[str, Any]] = None
    ) -> ValidationResult:
        """Validate orchestration API request"""
        start_time = time.perf_counter()
        result = ValidationResult(is_valid=True)

        try:
            # Basic structure validation
            required_fields = ["prompt"]
            for field in required_fields:
                if field not in request_data:
                    result.add_error(
                        ValidationErrorType.MISSING_FIELD,
                        f"Required field '{field}' is missing",
                        field=field,
                    )

            # Content length validation
            prompt = request_data.get("prompt", "")
            if len(prompt) > self.max_content_length:
                result.add_error(
                    ValidationErrorType.DATA_SIZE_EXCEEDED,
                    f"Prompt exceeds maximum length ({self.max_content_length} chars)",
                    field="prompt",
                )

            # Security validation
            if prompt:
                request_context = context.get("type", "general") if context else "general"
                security_issues = self.security_validator.validate_content_security(prompt, request_context)
                for issue in security_issues:
                    result.add_error(
                        ValidationErrorType(issue["type"]),
                        f"Security violation: {issue.get('pattern', 'unknown')}",
                        severity=ValidationSeverity(issue["severity"]),
                    )

            # Strategy validation
            strategy = request_data.get("strategy", "consensus")
            valid_strategies = [
                "single_best",
                "consensus",
                "fallback",
                "parallel",
                "competitive",
                "ensemble",
            ]
            if strategy not in valid_strategies:
                result.add_error(
                    ValidationErrorType.INVALID_VALUE,
                    f"Invalid strategy '{strategy}'. Must be one of: {valid_strategies}",
                    field="strategy",
                )

            # Provider validation
            providers = request_data.get("providers", [])
            valid_providers = ["openai", "anthropic", "google", "perplexity", "all"]
            for provider in providers:
                if provider not in valid_providers:
                    result.add_error(
                        ValidationErrorType.INVALID_VALUE,
                        f"Invalid provider '{provider}'. Must be one of: {valid_providers}",
                        field="providers",
                    )

            # Numeric field validation
            numeric_fields = {
                "max_latency_ms": {"min": 100, "max": 30000},
                "max_cost": {"min": 0.001, "max": 10.0},
                "min_confidence": {"min": 0.0, "max": 1.0},
            }

            for field, constraints in numeric_fields.items():
                if field in request_data:
                    value = request_data[field]
                    if not isinstance(value, (int, float)):
                        result.add_error(
                            ValidationErrorType.INVALID_FORMAT,
                            f"Field '{field}' must be numeric",
                            field=field,
                        )
                    elif value < constraints["min"] or value > constraints["max"]:
                        result.add_error(
                            ValidationErrorType.INVALID_VALUE,
                            f"Field '{field}' must be between {constraints['min']} and {constraints['max']}",
                            field=field,
                        )

            # Function validation
            if request_data.get("enable_functions", False):
                specific_functions = request_data.get("specific_functions", [])
                if len(specific_functions) > self.max_function_count:
                    result.add_error(
                        ValidationErrorType.DATA_SIZE_EXCEEDED,
                        f"Too many functions specified (max: {self.max_function_count})",
                        field="specific_functions",
                    )

        except Exception as e:
            result.add_error(
                ValidationErrorType.INVALID_FORMAT,
                f"Validation processing error: {e!s}",
                severity=ValidationSeverity.CRITICAL,
            )

        # Record execution time
        result.execution_time_ms = (time.perf_counter() - start_time) * 1000
        result.metadata = {
            "validator": "RequestValidator",
            "validation_type": "orchestration_request",
            "content_length": len(prompt) if prompt else 0,
            "function_count": len(request_data.get("specific_functions", [])),
        }

        return result

    async def validate_streaming_request(
        self, request_data: dict[str, Any], context: Optional[dict[str, Any]] = None
    ) -> ValidationResult:
        """Validate streaming API request"""
        start_time = time.perf_counter()
        result = ValidationResult(is_valid=True)

        try:
            # Basic validation (similar to orchestration but with streaming-specific rules)
            required_fields = ["prompt"]
            for field in required_fields:
                if field not in request_data:
                    result.add_error(
                        ValidationErrorType.MISSING_FIELD,
                        f"Required field '{field}' is missing",
                        field=field,
                    )

            # Provider validation for streaming (more restrictive)
            provider = request_data.get("provider", "openai")
            streaming_providers = ["openai", "anthropic"]
            if provider not in streaming_providers:
                result.add_error(
                    ValidationErrorType.INVALID_VALUE,
                    f"Provider '{provider}' does not support streaming. Supported: {streaming_providers}",
                    field="provider",
                )

            # Temperature validation
            temperature = request_data.get("temperature", 0.7)
            if not isinstance(temperature, (int, float)) or temperature < 0.0 or temperature > 2.0:
                result.add_error(
                    ValidationErrorType.INVALID_VALUE,
                    "Temperature must be between 0.0 and 2.0",
                    field="temperature",
                )

            # Max tokens validation
            max_tokens = request_data.get("max_tokens")
            if max_tokens is not None:
                if not isinstance(max_tokens, int) or max_tokens < 1 or max_tokens > 32000:
                    result.add_error(
                        ValidationErrorType.INVALID_VALUE,
                        "Max tokens must be between 1 and 32000",
                        field="max_tokens",
                    )

        except Exception as e:
            result.add_error(
                ValidationErrorType.INVALID_FORMAT,
                f"Streaming validation error: {e!s}",
                severity=ValidationSeverity.CRITICAL,
            )

        result.execution_time_ms = (time.perf_counter() - start_time) * 1000
        return result

    async def validate_function_registration(self, request_data: dict[str, Any]) -> ValidationResult:
        """Validate function registration request"""
        start_time = time.perf_counter()
        result = ValidationResult(is_valid=True)

        try:
            functions = request_data.get("functions", {})
            if not isinstance(functions, dict):
                result.add_error(
                    ValidationErrorType.INVALID_FORMAT,
                    "Functions must be a dictionary",
                    field="functions",
                )
                return result

            if len(functions) > self.max_function_count:
                result.add_error(
                    ValidationErrorType.DATA_SIZE_EXCEEDED,
                    f"Too many functions (max: {self.max_function_count})",
                    field="functions",
                )

            # Validate each function
            for func_name, func_def in functions.items():
                if not isinstance(func_def, dict):
                    result.add_error(
                        ValidationErrorType.INVALID_FORMAT,
                        f"Function definition for '{func_name}' must be a dictionary",
                    )
                    continue

                # Security validation for function
                security_issues = self.security_validator.validate_function_security({"name": func_name, **func_def})

                for issue in security_issues:
                    result.add_error(
                        ValidationErrorType(issue["type"]),
                        f"Function '{func_name}': {issue['message']}",
                        severity=ValidationSeverity(issue["severity"]),
                    )

                # Required function fields
                required_func_fields = ["description"]
                for field in required_func_fields:
                    if field not in func_def:
                        result.add_warning(f"Function '{func_name}' missing recommended field: {field}")

        except Exception as e:
            result.add_error(
                ValidationErrorType.INVALID_FORMAT,
                f"Function registration validation error: {e!s}",
                severity=ValidationSeverity.CRITICAL,
            )

        result.execution_time_ms = (time.perf_counter() - start_time) * 1000
        return result


class ResponseValidator:
    """Validate API responses"""

    def __init__(self):
        self.security_validator = SecurityValidator()

    async def validate_orchestration_response(
        self,
        response: dict[str, Any],
        original_request: Optional[dict[str, Any]] = None,
    ) -> ValidationResult:
        """Validate orchestration response"""
        start_time = time.perf_counter()
        result = ValidationResult(is_valid=True)

        try:
            # Required response fields
            required_fields = [
                "success",
                "content",
                "confidence_score",
                "primary_provider",
            ]
            for field in required_fields:
                if field not in response:
                    result.add_error(
                        ValidationErrorType.MISSING_FIELD,
                        f"Required response field '{field}' is missing",
                        field=field,
                    )

            # Validate response content
            content = response.get("content", "")
            if content:
                security_issues = self.security_validator.validate_content_security(content, "response")
                for issue in security_issues:
                    result.add_error(
                        ValidationErrorType(issue["type"]),
                        f"Response security issue: {issue.get('pattern', 'unknown')}",
                        severity=ValidationSeverity(issue["severity"]),
                    )

            # Validate confidence score
            confidence = response.get("confidence_score", 0.0)
            if not isinstance(confidence, (int, float)) or confidence < 0.0 or confidence > 1.0:
                result.add_error(
                    ValidationErrorType.INVALID_VALUE,
                    "Confidence score must be between 0.0 and 1.0",
                    field="confidence_score",
                )

            # Validate latency
            latency = response.get("latency_ms", 0.0)
            if latency > 30000:  # 30 seconds
                result.add_warning("Response latency is unusually high", field="latency_ms")

            # Validate cost
            cost = response.get("cost", 0.0)
            if cost > 5.0:  # $5 threshold for warning
                result.add_warning("Response cost is unusually high", field="cost")

            # Cross-validation with original request
            if original_request:
                min_confidence = original_request.get("min_confidence", 0.7)
                if confidence < min_confidence:
                    result.add_warning(f"Response confidence ({confidence}) below requested minimum ({min_confidence})")

        except Exception as e:
            result.add_error(
                ValidationErrorType.INVALID_FORMAT,
                f"Response validation error: {e!s}",
                severity=ValidationSeverity.CRITICAL,
            )

        result.execution_time_ms = (time.perf_counter() - start_time) * 1000
        return result


class HealthcareValidator:
    """Specialized validator for healthcare API requests (HIPAA compliance)"""

    def __init__(self):
        self.security_validator = SecurityValidator(enable_hipaa=True)

        # Healthcare-specific validation rules
        self.required_consent_types = [
            "data_processing",
            "medical_analysis",
            "data_storage",
            "third_party_sharing",
        ]

        self.phi_categories = ["demographic", "financial", "clinical", "administrative"]

    async def validate_healthcare_request(
        self,
        request_data: dict[str, Any],
        patient_context: Optional[dict[str, Any]] = None,
    ) -> ValidationResult:
        """Validate healthcare-specific API request"""
        start_time = time.perf_counter()
        result = ValidationResult(is_valid=True)

        try:
            # Consent validation
            consent = request_data.get("consent", {})
            if not consent:
                result.add_error(
                    ValidationErrorType.MISSING_FIELD,
                    "Healthcare requests require explicit consent",
                    field="consent",
                    severity=ValidationSeverity.CRITICAL,
                )
            else:
                for consent_type in self.required_consent_types:
                    if not consent.get(consent_type, False):
                        result.add_error(
                            ValidationErrorType.AUTHORIZATION_FAILED,
                            f"Missing required consent: {consent_type}",
                            field=f"consent.{consent_type}",
                            severity=ValidationSeverity.CRITICAL,
                        )

            # PHI validation
            content = request_data.get("prompt", "") + " " + str(request_data.get("context", {}))
            phi_issues = self.security_validator.validate_content_security(content, "healthcare")
            for issue in phi_issues:
                if issue["type"] == ValidationErrorType.HIPAA_VIOLATION.value:
                    result.add_error(
                        ValidationErrorType.HIPAA_VIOLATION,
                        "Potential PHI detected in request content",
                        severity=ValidationSeverity.CRITICAL,
                    )

            # Patient context validation
            if patient_context:
                required_patient_fields = [
                    "patient_id",
                    "consent_timestamp",
                    "data_classification",
                ]
                for field in required_patient_fields:
                    if field not in patient_context:
                        result.add_error(
                            ValidationErrorType.MISSING_FIELD,
                            f"Required patient context field '{field}' is missing",
                            field=f"patient_context.{field}",
                        )

            # Data retention validation
            retention_policy = request_data.get("data_retention")
            if not retention_policy:
                result.add_warning("No data retention policy specified")
            elif retention_policy.get("retain_days", 0) > 2555:  # 7 years
                result.add_warning("Data retention period exceeds typical healthcare limits")

            # Audit trail requirement
            if not request_data.get("audit_trail", {}).get("enabled", False):
                result.add_error(
                    ValidationErrorType.MISSING_FIELD,
                    "Audit trail is required for healthcare requests",
                    field="audit_trail.enabled",
                    severity=ValidationSeverity.ERROR,
                )

        except Exception as e:
            result.add_error(
                ValidationErrorType.INVALID_FORMAT,
                f"Healthcare validation error: {e!s}",
                severity=ValidationSeverity.CRITICAL,
            )

        result.execution_time_ms = (time.perf_counter() - start_time) * 1000
        result.metadata["validator"] = "HealthcareValidator"
        result.metadata["hipaa_compliant"] = result.is_valid

        return result


class AuthenticationValidator:
    """Validate authentication and authorization"""

    def __init__(self, jwt_secret: str = "lukhas-jwt-secret-change-in-production"):
        self.jwt_secret = jwt_secret
        self.valid_permissions = {
            "orchestration",
            "streaming",
            "functions",
            "healthcare",
            "admin",
            "metrics",
            "user_management",
        }
        self.tier_permissions = {
            "LAMBDA_TIER_1": ["orchestration"],
            "LAMBDA_TIER_2": ["orchestration", "streaming"],
            "LAMBDA_TIER_3": ["orchestration", "streaming", "functions"],
            "LAMBDA_TIER_4": [
                "orchestration",
                "streaming",
                "functions",
                "healthcare",
                "admin",
            ],
        }

    async def validate_jwt_token(self, token: str) -> ValidationResult:
        """Validate JWT authentication token"""
        result = ValidationResult(is_valid=True)

        if not JWT_AVAILABLE:
            result.add_error(
                ValidationErrorType.AUTHENTICATION_FAILED,
                "JWT validation not available - PyJWT not installed",
                severity=ValidationSeverity.CRITICAL,
            )
            return result

        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])

            # Validate token structure
            required_claims = ["user_id", "tier", "exp", "iat"]
            for claim in required_claims:
                if claim not in payload:
                    result.add_error(
                        ValidationErrorType.AUTHENTICATION_FAILED,
                        f"Missing required JWT claim: {claim}",
                        field=claim,
                    )

            # Validate tier
            tier = payload.get("tier")
            if tier not in self.tier_permissions:
                result.add_error(
                    ValidationErrorType.AUTHORIZATION_FAILED,
                    f"Invalid tier: {tier}",
                    field="tier",
                )

            result.metadata = {
                "user_id": payload.get("user_id"),
                "tier": tier,
                "permissions": self.tier_permissions.get(tier, []),
                "expires_at": payload.get("exp"),
            }

        except jwt.ExpiredSignatureError:
            result.add_error(
                ValidationErrorType.AUTHENTICATION_FAILED,
                "JWT token has expired",
                severity=ValidationSeverity.ERROR,
            )
        except jwt.InvalidTokenError as e:
            result.add_error(
                ValidationErrorType.AUTHENTICATION_FAILED,
                f"Invalid JWT token: {e!s}",
                severity=ValidationSeverity.ERROR,
            )
        except Exception as e:
            result.add_error(
                ValidationErrorType.AUTHENTICATION_FAILED,
                f"JWT validation error: {e!s}",
                severity=ValidationSeverity.CRITICAL,
            )

        return result

    async def validate_api_key(self, api_key: str, required_permissions: list[str]) -> ValidationResult:
        """Validate API key and permissions"""
        result = ValidationResult(is_valid=True)

        try:
            # Basic API key format validation
            if not api_key or len(api_key) < 20:
                result.add_error(
                    ValidationErrorType.AUTHENTICATION_FAILED,
                    "Invalid API key format",
                    severity=ValidationSeverity.ERROR,
                )
                return result

            # Hash-based validation (in production, check against database)
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()

            # Simulate key validation (replace with actual key lookup)
            valid_keys = {
                hashlib.sha256(b"lukhas-dev-key-long-enough").hexdigest(): {
                    "tier": "LAMBDA_TIER_4",
                    "user_id": "dev-user",
                    "permissions": self.tier_permissions["LAMBDA_TIER_4"],
                },
                hashlib.sha256(b"lukhas-test-key-long-enough").hexdigest(): {
                    "tier": "LAMBDA_TIER_2",
                    "user_id": "test-user",
                    "permissions": self.tier_permissions["LAMBDA_TIER_2"],
                },
            }

            key_info = valid_keys.get(key_hash)
            if not key_info:
                result.add_error(
                    ValidationErrorType.AUTHENTICATION_FAILED,
                    "Invalid API key",
                    severity=ValidationSeverity.ERROR,
                )
                return result

            # Check permissions
            user_permissions = set(key_info["permissions"])
            required_permissions_set = set(required_permissions)

            if not required_permissions_set.issubset(user_permissions):
                missing_perms = required_permissions_set - user_permissions
                result.add_error(
                    ValidationErrorType.AUTHORIZATION_FAILED,
                    f"Missing required permissions: {list(missing_perms)}",
                    severity=ValidationSeverity.ERROR,
                )

            result.metadata = key_info

        except Exception as e:
            result.add_error(
                ValidationErrorType.AUTHENTICATION_FAILED,
                f"API key validation error: {e!s}",
                severity=ValidationSeverity.CRITICAL,
            )

        return result


class ComprehensiveAPIValidator:
    """Main validator class that orchestrates all validation types"""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        config = config or {}

        self.request_validator = RequestValidator(
            max_content_length=config.get("max_content_length", 100000),
            max_function_count=config.get("max_function_count", 50),
        )
        self.response_validator = ResponseValidator()
        self.healthcare_validator = HealthcareValidator()
        self.auth_validator = AuthenticationValidator(
            jwt_secret=config.get("jwt_secret", "lukhas-jwt-secret-change-in-production")
        )

        # Performance tracking
        self.validation_metrics = {
            "total_validations": 0,
            "successful_validations": 0,
            "failed_validations": 0,
            "average_latency_ms": 0.0,
            "error_counts": {},
            "security_violations": 0,
            "hipaa_violations": 0,
        }

    async def validate_request(
        self,
        request_type: str,
        request_data: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
        auth_token: Optional[str] = None,
    ) -> ValidationResult:
        """Comprehensive request validation"""
        start_time = time.perf_counter()

        # Generate unique validation ID
        validation_id = str(uuid.uuid4())

        logger.info(f"🔍 Starting validation: {validation_id}")
        logger.info(f"   Type: {request_type}")
        logger.info(f"   Context: {context.get('type', 'general') if context else 'none'}")

        try:
            # Authentication validation
            auth_result = None
            if auth_token:
                if auth_token.startswith("Bearer "):
                    auth_result = await self.auth_validator.validate_jwt_token(auth_token[7:])
                else:
                    # Determine required permissions based on request type
                    required_permissions = self._get_required_permissions(request_type, context)
                    auth_result = await self.auth_validator.validate_api_key(auth_token, required_permissions)

                if not auth_result.is_valid:
                    self._update_metrics("failed", auth_result)
                    return auth_result

            # Request-specific validation
            if request_type == "orchestration":
                result = await self.request_validator.validate_orchestration_request(request_data, context)
            elif request_type == "streaming":
                result = await self.request_validator.validate_streaming_request(request_data, context)
            elif request_type == "function_registration":
                result = await self.request_validator.validate_function_registration(request_data)
            elif request_type == "healthcare":
                result = await self.healthcare_validator.validate_healthcare_request(
                    request_data, context.get("patient_context") if context else None
                )
            else:
                result = ValidationResult(is_valid=True)
                result.add_error(
                    ValidationErrorType.INVALID_VALUE,
                    f"Unknown request type: {request_type}",
                    severity=ValidationSeverity.ERROR,
                )

            # Add authentication metadata if available
            if auth_result and auth_result.metadata:
                result.metadata["authentication"] = auth_result.metadata

            # Record metrics
            result.metadata["validation_id"] = validation_id
            result.metadata["request_type"] = request_type

            # Update performance metrics
            total_time = (time.perf_counter() - start_time) * 1000
            result.execution_time_ms = total_time

            self._update_metrics("successful" if result.is_valid else "failed", result)

            logger.info(f"✅ Validation completed: {validation_id} ({total_time:.2f}ms)")
            logger.info(f"   Valid: {result.is_valid}")
            logger.info(f"   Errors: {len(result.errors)}")
            logger.info(f"   Warnings: {len(result.warnings)}")

            return result

        except Exception as e:
            error_result = ValidationResult(is_valid=False)
            error_result.add_error(
                ValidationErrorType.INVALID_FORMAT,
                f"Validation system error: {e!s}",
                severity=ValidationSeverity.CRITICAL,
            )
            error_result.execution_time_ms = (time.perf_counter() - start_time) * 1000
            error_result.metadata["validation_id"] = validation_id

            self._update_metrics("failed", error_result)

            logger.error(f"❌ Validation error: {validation_id} - {e!s}")
            return error_result

    def _get_required_permissions(self, request_type: str, context: Optional[dict[str, Any]]) -> list[str]:
        """Get required permissions for request type"""
        permission_map = {
            "orchestration": ["orchestration"],
            "streaming": ["streaming"],
            "function_registration": ["functions"],
            "healthcare": ["healthcare"],
        }

        permissions = permission_map.get(request_type, [])

        # Add context-specific permissions
        if context:
            if context.get("type") == "healthcare":
                permissions.append("healthcare")
            if context.get("admin_required"):
                permissions.append("admin")

        return permissions

    def _update_metrics(self, status: str, result: ValidationResult):
        """Update validation metrics"""
        self.validation_metrics["total_validations"] += 1

        if status == "successful":
            self.validation_metrics["successful_validations"] += 1
        else:
            self.validation_metrics["failed_validations"] += 1

        # Update average latency
        current_avg = self.validation_metrics["average_latency_ms"]
        total_validations = self.validation_metrics["total_validations"]
        new_avg = ((current_avg * (total_validations - 1)) + result.execution_time_ms) / total_validations
        self.validation_metrics["average_latency_ms"] = new_avg

        # Count error types
        for error in result.errors:
            error_type = error["type"]
            self.validation_metrics["error_counts"][error_type] = (
                self.validation_metrics["error_counts"].get(error_type, 0) + 1
            )

            if error_type == "security_violation":
                self.validation_metrics["security_violations"] += 1
            elif error_type == "hipaa_violation":
                self.validation_metrics["hipaa_violations"] += 1

    def get_validation_metrics(self) -> dict[str, Any]:
        """Get comprehensive validation metrics"""
        total = max(self.validation_metrics["total_validations"], 1)

        return {
            **self.validation_metrics,
            "success_rate": self.validation_metrics["successful_validations"] / total,
            "error_rate": self.validation_metrics["failed_validations"] / total,
            "performance_score": self._calculate_performance_score(),
            "security_score": self._calculate_security_score(),
        }

    def _calculate_performance_score(self) -> float:
        """Calculate performance score (0-1)"""
        # Based on success rate and latency
        total = max(self.validation_metrics["total_validations"], 1)
        success_rate = self.validation_metrics["successful_validations"] / total

        # Penalize high latency (target: <10ms)
        avg_latency = self.validation_metrics["average_latency_ms"]
        latency_score = max(0, 1 - (avg_latency / 50))  # 50ms = 0 score

        return (success_rate * 0.7) + (latency_score * 0.3)

    def _calculate_security_score(self) -> float:
        """Calculate security score (0-1)"""
        total = max(self.validation_metrics["total_validations"], 1)

        security_violations = self.validation_metrics["security_violations"]
        hipaa_violations = self.validation_metrics["hipaa_violations"]

        violation_rate = (security_violations + hipaa_violations) / total

        return max(0, 1 - (violation_rate * 2))  # Each violation reduces score by 0.5


# Global validator instance
_global_validator = None


def get_validator(config: Optional[dict[str, Any]] = None) -> ComprehensiveAPIValidator:
    """Get global validator instance"""
    global _global_validator
    if _global_validator is None:
        _global_validator = ComprehensiveAPIValidator(config)
    return _global_validator


# Convenience functions for common validation scenarios
async def validate_orchestration_request(
    request_data: dict[str, Any],
    context: Optional[dict[str, Any]] = None,
    auth_token: Optional[str] = None,
) -> ValidationResult:
    """Validate orchestration request"""
    validator = get_validator()
    return await validator.validate_request("orchestration", request_data, context, auth_token)


async def validate_streaming_request(
    request_data: dict[str, Any],
    context: Optional[dict[str, Any]] = None,
    auth_token: Optional[str] = None,
) -> ValidationResult:
    """Validate streaming request"""
    validator = get_validator()
    return await validator.validate_request("streaming", request_data, context, auth_token)


async def validate_healthcare_request(
    request_data: dict[str, Any],
    patient_context: Optional[dict[str, Any]] = None,
    auth_token: Optional[str] = None,
) -> ValidationResult:
    """Validate healthcare request"""
    context = {"type": "healthcare", "patient_context": patient_context}
    validator = get_validator()
    return await validator.validate_request("healthcare", request_data, context, auth_token)


async def validate_api_response(
    response_data: dict[str, Any], original_request: Optional[dict[str, Any]] = None
) -> ValidationResult:
    """Validate API response"""
    validator = get_validator()
    return await validator.response_validator.validate_orchestration_response(response_data, original_request)


# Security utilities
def sanitize_content(content: str, context: str = "general") -> str:
    """Sanitize content by removing dangerous patterns"""
    security_validator = SecurityValidator()

    # Remove dangerous patterns
    sanitized = content
    for pattern in security_validator.DANGEROUS_PATTERNS:
        sanitized = re.sub(pattern, "[FILTERED]", sanitized, flags=re.IGNORECASE)

    # Remove PHI if healthcare context
    if context in ["healthcare", "medical", "patient"]:
        for pattern in security_validator.PHI_PATTERNS:
            sanitized = re.sub(pattern, "[PHI_FILTERED]", sanitized, flags=re.IGNORECASE)

    return sanitized


def calculate_content_risk_score(content: str, context: str = "general") -> float:
    """Calculate risk score for content (0.0 = safe, 1.0 = high risk)"""
    security_validator = SecurityValidator()
    issues = security_validator.validate_content_security(content, context)

    if not issues:
        return 0.0

    # Calculate risk based on severity and count
    total_risk = 0.0
    for issue in issues:
        severity = issue.get("severity", "error")
        if severity == "critical":
            total_risk += 0.5
        elif severity == "error":
            total_risk += 0.3
        elif severity == "warning":
            total_risk += 0.1

    return min(1.0, total_risk)  # Cap at 1.0


# Performance monitoring integration
def get_validation_performance_metrics() -> dict[str, Any]:
    """Get validation performance metrics"""
    validator = get_validator()
    return validator.get_validation_metrics()


# Testing utilities for development
async def run_validation_tests() -> dict[str, Any]:
    """Run comprehensive validation tests"""
    validator = get_validator()

    test_results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tests": [],
        "overall_success": True,
    }

    # Test 1: Basic orchestration validation
    test_request = {
        "prompt": "Hello, world!",
        "strategy": "consensus",
        "providers": ["openai"],
        "enable_functions": True,
        "max_latency_ms": 5000,
        "max_cost": 0.10,
    }

    result = await validate_orchestration_request(test_request)
    test_results["tests"].append(
        {
            "name": "orchestration_validation",
            "success": result.is_valid,
            "execution_time_ms": result.execution_time_ms,
            "errors": len(result.errors),
            "warnings": len(result.warnings),
        }
    )

    if not result.is_valid:
        test_results["overall_success"] = False

    # Test 2: Security validation
    malicious_request = {
        "prompt": "<script>alert('xss')</script> DROP TABLE users;",
        "strategy": "single_best",
    }

    security_result = await validate_orchestration_request(malicious_request)
    test_results["tests"].append(
        {
            "name": "security_validation",
            "success": not security_result.is_valid,  # Should fail for malicious content
            "execution_time_ms": security_result.execution_time_ms,
            "security_violations": len([e for e in security_result.errors if e["type"] == "security_violation"]),
        }
    )

    # Test 3: Healthcare validation
    healthcare_request = {
        "prompt": "Analyze patient symptoms: fever, cough",
        "consent": {
            "data_processing": True,
            "medical_analysis": True,
            "data_storage": True,
            "third_party_sharing": False,
        },
        "audit_trail": {"enabled": True},
    }

    healthcare_result = await validate_healthcare_request(healthcare_request)
    test_results["tests"].append(
        {
            "name": "healthcare_validation",
            "success": healthcare_result.is_valid,
            "execution_time_ms": healthcare_result.execution_time_ms,
            "hipaa_compliant": healthcare_result.metadata.get("hipaa_compliant", False),
        }
    )

    if not healthcare_result.is_valid:
        test_results["overall_success"] = False

    # Test 4: Performance validation
    large_request = {
        "prompt": "A" * 50000,  # Large prompt
        "strategy": "consensus",
    }

    performance_result = await validate_orchestration_request(large_request)
    test_results["tests"].append(
        {
            "name": "performance_validation",
            "success": performance_result.execution_time_ms < 100,  # Should complete in <100ms
            "execution_time_ms": performance_result.execution_time_ms,
            "content_size": len(large_request["prompt"]),
        }
    )

    # Overall metrics
    test_results["metrics"] = get_validation_performance_metrics()
    test_results["performance_score"] = validator._calculate_performance_score()
    test_results["security_score"] = validator._calculate_security_score()

    return test_results


# Export main components
__all__ = [
    "AuthenticationValidator",
    "ComprehensiveAPIValidator",
    "HealthcareValidator",
    "RequestValidator",
    "ResponseValidator",
    "SecurityValidator",
    "ValidationErrorType",
    "ValidationResult",
    "ValidationSeverity",
    "calculate_content_risk_score",
    "get_validation_performance_metrics",
    "get_validator",
    "run_validation_tests",
    "sanitize_content",
    "validate_api_response",
    "validate_healthcare_request",
    "validate_orchestration_request",
    "validate_streaming_request",
]


# Main execution for testing
if __name__ == "__main__":

    async def main():
        """Run validation system tests"""
        logger.info("🔍 LUKHAS AI Comprehensive API Validation System")
        logger.info("🎯 Running Validation Tests")
        logger.info("=" * 70)

        try:
            test_results = await run_validation_tests()

            logger.info("\n" + "=" * 70)
            logger.info("🏁 VALIDATION TEST RESULTS")
            logger.info("=" * 70)

            for test in test_results["tests"]:
                status = "✅ PASS" if test["success"] else "❌ FAIL"
                logger.info(f"{status} {test['name']} ({test['execution_time_ms']:.2f}ms)")

                if "errors" in test:
                    logger.info(f"   Errors: {test['errors']}, Warnings: {test.get('warnings', 0)}")
                if "security_violations" in test:
                    logger.info(f"   Security violations: {test['security_violations']}")
                if "hipaa_compliant" in test:
                    logger.info(f"   HIPAA compliant: {test['hipaa_compliant']}")

            logger.info("\n📊 OVERALL METRICS:")
            metrics = test_results["metrics"]
            logger.info(f"   Success rate: {metrics['success_rate']:.1%}")
            logger.info(f"   Average latency: {metrics['average_latency_ms']:.2f}ms")
            logger.info(f"   Performance score: {test_results['performance_score']:.3f}")
            logger.info(f"   Security score: {test_results['security_score']:.3f}")

            if test_results["overall_success"]:
                logger.info("\n✅ ✅ ✅ ALL VALIDATION TESTS PASSED! ✅ ✅ ✅")
                logger.info("🎉 LUKHAS AI API Validation System is FULLY OPERATIONAL")
                return True
            else:
                logger.error("\n❌ ❌ ❌ SOME VALIDATION TESTS FAILED! ❌ ❌ ❌")
                return False

        except Exception as e:
            logger.critical(f"\n❌ CRITICAL VALIDATION ERROR: {e}")
            return False

    import sys

    success = asyncio.run(main())
    sys.exit(0 if success else 1)

# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: validation.py
# VERSION: 2.0.0
# TIER SYSTEM: LAMBDA_TIER_4 (Enterprise-grade validation)
# TRINITY FRAMEWORK: ⚛️ (Identity verification), 🧠 (Intelligence validation), 🛡️ (Guardian protection)
# CAPABILITIES: Comprehensive API validation system with multi-layer security validation,
#               HIPAA compliance checking, authentication/authorization validation,
#               performance monitoring, and advanced error handling.
# FUNCTIONS: validate_orchestration_request, validate_streaming_request, validate_healthcare_request,
#            validate_api_response, sanitize_content, calculate_content_risk_score
# CLASSES: ValidationResult, SecurityValidator, RequestValidator, ResponseValidator,
#          HealthcareValidator, AuthenticationValidator, ComprehensiveAPIValidator
# DECORATORS: Pydantic validators, async validation methods
# DEPENDENCIES: asyncio, logging, re, time, uuid, hashlib, datetime, typing,
#               pydantic (optional), jwt (optional)
# INTERFACES: Async validation API with comprehensive result objects
# ERROR HANDLING: Multi-level error categorization with severity levels,
#                 detailed error reporting and metrics tracking
# LOGGING: Structured logging with validation IDs and performance metrics
# AUTHENTICATION: JWT token validation, API key validation with tier-based permissions
# SECURITY: XSS prevention, SQL injection detection, PHI detection, function security validation
# HOW TO USE:
#   from candidate.bridge.api.validation import validate_orchestration_request
#   result = await validate_orchestration_request(request_data, context, auth_token)
# INTEGRATION NOTES: Designed for integration with FastAPI endpoints and orchestration systems.
#                    Provides comprehensive validation for all LUKHAS API operations.
# MAINTENANCE: Regular updates to security patterns and healthcare compliance rules.
#              Performance monitoring and optimization of validation latency.
# CONTACT: LUKHAS DEVELOPMENT TEAM
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════
