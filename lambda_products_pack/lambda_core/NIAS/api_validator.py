#!/usr/bin/env python3
"""
Enhanced API Validator for NIAS Dream Commerce
Provides comprehensive request validation with detailed error reporting
"""

import asyncio
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional


class ValidationError(Exception):
    """Custom validation error with detailed information"""

    def __init__(self, field: str, message: str, value: Any = None):
        self.field = field
        self.message = message
        self.value = value
        super().__init__(f"{field}: {message}")


class ValidationType(Enum):
    """Types of validation rules"""

    REQUIRED = "required"
    TYPE = "type"
    PATTERN = "pattern"
    RANGE = "range"
    LENGTH = "length"
    ENUM = "enum"
    CUSTOM = "custom"


@dataclass
class ValidationRule:
    """Single validation rule"""

    field: str
    validation_type: ValidationType
    params: dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None


@dataclass
class ValidationSchema:
    """Complete validation schema for an endpoint"""

    name: str
    rules: list[ValidationRule]
    allow_extra_fields: bool = False
    custom_validators: list[Callable] = field(default_factory=list)


class APIValidator:
    """
    Enhanced API Validator with comprehensive validation capabilities

    Features:
    - Type validation
    - Pattern matching
    - Range checking
    - Custom validators
    - Detailed error reporting
    - Schema caching
    """

    def __init__(self):
        self.schemas = self._initialize_schemas()
        self.validation_cache = {}
        self.error_history = []

    def _initialize_schemas(self) -> dict[str, ValidationSchema]:
        """Initialize validation schemas for all endpoints"""
        return {
            "user_registration": ValidationSchema(
                name="user_registration",
                rules=[
                    ValidationRule(
                        field="username",
                        validation_type=ValidationType.REQUIRED,
                        params={},
                    ),
                    ValidationRule(
                        field="username",
                        validation_type=ValidationType.LENGTH,
                        params={"min": 3, "max": 50},
                        error_message="Username must be between 3 and 50 characters",
                    ),
                    ValidationRule(
                        field="username",
                        validation_type=ValidationType.PATTERN,
                        params={"pattern": r"^[a-zA-Z0-9_-]+$"},
                        error_message="Username can only contain letters, numbers, underscores, and hyphens",
                    ),
                    ValidationRule(
                        field="email",
                        validation_type=ValidationType.REQUIRED,
                        params={},
                    ),
                    ValidationRule(
                        field="email",
                        validation_type=ValidationType.PATTERN,
                        params={
                            "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                        },
                        error_message="Invalid email format",
                    ),
                    ValidationRule(
                        field="age",
                        validation_type=ValidationType.TYPE,
                        params={"type": int},
                    ),
                    ValidationRule(
                        field="age",
                        validation_type=ValidationType.RANGE,
                        params={"min": 13, "max": 120},
                        error_message="Age must be between 13 and 120",
                    ),
                    ValidationRule(
                        field="preferences",
                        validation_type=ValidationType.TYPE,
                        params={"type": dict},
                    ),
                ],
            ),
            "dream_initiation": ValidationSchema(
                name="dream_initiation",
                rules=[
                    ValidationRule(
                        field="user_id",
                        validation_type=ValidationType.REQUIRED,
                        params={},
                    ),
                    ValidationRule(
                        field="dream_type",
                        validation_type=ValidationType.REQUIRED,
                        params={},
                    ),
                    ValidationRule(
                        field="dream_type",
                        validation_type=ValidationType.ENUM,
                        params={
                            "values": ["lucid", "guided", "free", "narrative", "visual"]
                        },
                        error_message="Dream type must be one of: lucid, guided, free, narrative, visual",
                    ),
                    ValidationRule(
                        field="duration",
                        validation_type=ValidationType.REQUIRED,
                        params={},
                    ),
                    ValidationRule(
                        field="duration",
                        validation_type=ValidationType.TYPE,
                        params={"type": (int, float)},
                    ),
                    ValidationRule(
                        field="duration",
                        validation_type=ValidationType.RANGE,
                        params={"min": 10, "max": 120},
                        error_message="Duration must be between 10 and 120 minutes",
                    ),
                    ValidationRule(
                        field="intensity",
                        validation_type=ValidationType.REQUIRED,
                        params={},
                    ),
                    ValidationRule(
                        field="intensity",
                        validation_type=ValidationType.TYPE,
                        params={"type": (int, float)},
                    ),
                    ValidationRule(
                        field="intensity",
                        validation_type=ValidationType.RANGE,
                        params={"min": 0.1, "max": 1.0},
                        error_message="Intensity must be between 0.1 and 1.0",
                    ),
                ],
            ),
            "vendor_request": ValidationSchema(
                name="vendor_request",
                rules=[
                    ValidationRule(
                        field="vendor_id",
                        validation_type=ValidationType.REQUIRED,
                        params={},
                    ),
                    ValidationRule(
                        field="vendor_id",
                        validation_type=ValidationType.PATTERN,
                        params={"pattern": r"^vendor_[a-zA-Z0-9]{8,}$"},
                        error_message="Invalid vendor ID format",
                    ),
                    ValidationRule(
                        field="request_type",
                        validation_type=ValidationType.REQUIRED,
                        params={},
                    ),
                    ValidationRule(
                        field="request_type",
                        validation_type=ValidationType.ENUM,
                        params={
                            "values": [
                                "create_seed",
                                "update_seed",
                                "delete_seed",
                                "get_analytics",
                            ]
                        },
                        error_message="Invalid request type",
                    ),
                    ValidationRule(
                        field="tier",
                        validation_type=ValidationType.ENUM,
                        params={
                            "values": [
                                "trial",
                                "basic",
                                "professional",
                                "enterprise",
                                "strategic",
                            ]
                        },
                        error_message="Invalid vendor tier",
                    ),
                ],
            ),
            "user_metrics": ValidationSchema(
                name="user_metrics",
                rules=[
                    ValidationRule(
                        field="user_id",
                        validation_type=ValidationType.REQUIRED,
                        params={},
                    ),
                    ValidationRule(
                        field="metric_type",
                        validation_type=ValidationType.ENUM,
                        params={"values": ["engagement", "dreams", "rewards", "all"]},
                        error_message="Invalid metric type",
                    ),
                    ValidationRule(
                        field="date_range",
                        validation_type=ValidationType.TYPE,
                        params={"type": dict},
                    ),
                ],
            ),
        }

    async def validate_request(
        self, schema_name: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Validate request data against a schema

        Args:
            schema_name: Name of the validation schema
            data: Request data to validate

        Returns:
            Validated and cleaned data

        Raises:
            ValidationError: If validation fails
        """
        if schema_name not in self.schemas:
            raise ValidationError("schema", f"Unknown schema: {schema_name}")

        schema = self.schemas[schema_name]
        errors = []
        cleaned_data = {}

        # Apply validation rules
        for rule in schema.rules:
            try:
                value = await self._apply_rule(rule, data)
                if value is not None:
                    cleaned_data[rule.field] = value
            except ValidationError as e:
                errors.append(e)

        # Check for extra fields if not allowed
        if not schema.allow_extra_fields:
            field_names = {rule.field for rule in schema.rules}
            extra_fields = set(data.keys()) - field_names
            if extra_fields:
                for field in extra_fields:
                    errors.append(
                        ValidationError(
                            field, f"Unexpected field: {field}", data[field]
                        )
                    )

        # Apply custom validators
        for validator in schema.custom_validators:
            try:
                await validator(cleaned_data)
            except ValidationError as e:
                errors.append(e)

        # Handle errors
        if errors:
            self._record_errors(errors)
            raise self._create_composite_error(errors)

        return cleaned_data

    async def _apply_rule(self, rule: ValidationRule, data: dict[str, Any]) -> Any:
        """
        Apply a single validation rule

        Args:
            rule: Validation rule to apply
            data: Data to validate

        Returns:
            Validated value

        Raises:
            ValidationError: If validation fails
        """
        field_value = data.get(rule.field)

        # Check required fields
        if rule.validation_type == ValidationType.REQUIRED:
            if field_value is None or field_value == "":
                raise ValidationError(
                    rule.field, rule.error_message or f"{rule.field} is required"
                )
            return field_value

        # Skip other validations if field is not present
        if field_value is None:
            return None

        # Type validation
        if rule.validation_type == ValidationType.TYPE:
            expected_type = rule.params["type"]
            if not isinstance(field_value, expected_type):
                raise ValidationError(
                    rule.field,
                    rule.error_message
                    or f"{rule.field} must be of type {expected_type.__name__}",
                    field_value,
                )

        # Pattern validation
        elif rule.validation_type == ValidationType.PATTERN:
            pattern = rule.params["pattern"]
            if not re.match(pattern, str(field_value)):
                raise ValidationError(
                    rule.field,
                    rule.error_message
                    or f"{rule.field} does not match required pattern",
                    field_value,
                )

        # Range validation
        elif rule.validation_type == ValidationType.RANGE:
            min_val = rule.params.get("min")
            max_val = rule.params.get("max")

            if min_val is not None and field_value < min_val:
                raise ValidationError(
                    rule.field,
                    rule.error_message or f"{rule.field} must be at least {min_val}",
                    field_value,
                )

            if max_val is not None and field_value > max_val:
                raise ValidationError(
                    rule.field,
                    rule.error_message or f"{rule.field} must be at most {max_val}",
                    field_value,
                )

        # Length validation
        elif rule.validation_type == ValidationType.LENGTH:
            min_len = rule.params.get("min")
            max_len = rule.params.get("max")
            value_len = len(str(field_value))

            if min_len is not None and value_len < min_len:
                raise ValidationError(
                    rule.field,
                    rule.error_message
                    or f"{rule.field} must be at least {min_len} characters",
                    field_value,
                )

            if max_len is not None and value_len > max_len:
                raise ValidationError(
                    rule.field,
                    rule.error_message
                    or f"{rule.field} must be at most {max_len} characters",
                    field_value,
                )

        # Enum validation
        elif rule.validation_type == ValidationType.ENUM:
            allowed_values = rule.params["values"]
            if field_value not in allowed_values:
                raise ValidationError(
                    rule.field,
                    rule.error_message
                    or f"{rule.field} must be one of {allowed_values}",
                    field_value,
                )

        return field_value

    def _record_errors(self, errors: list[ValidationError]):
        """Record validation errors for analysis"""
        error_record = {
            "timestamp": datetime.now().isoformat(),
            "errors": [
                {
                    "field": e.field,
                    "message": e.message,
                    "value": str(e.value) if e.value is not None else None,
                }
                for e in errors
            ],
        }
        self.error_history.append(error_record)

        # Keep only last 100 errors
        if len(self.error_history) > 100:
            self.error_history = self.error_history[-100:]

    def _create_composite_error(self, errors: list[ValidationError]) -> ValidationError:
        """Create a composite error from multiple validation errors"""
        if len(errors) == 1:
            return errors[0]

        error_messages = [f"{e.field}: {e.message}" for e in errors]
        return ValidationError(
            "multiple_fields", f"Validation failed: {'; '.join(error_messages)}"
        )

    async def validate_with_retry(
        self,
        schema_name: str,
        data: dict[str, Any],
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> dict[str, Any]:
        """
        Validate with retry logic for transient failures

        Args:
            schema_name: Schema to validate against
            data: Data to validate
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries (with exponential backoff)

        Returns:
            Validated data
        """
        last_error = None

        for attempt in range(max_retries):
            try:
                return await self.validate_request(schema_name, data)
            except ValidationError as e:
                last_error = e
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (2**attempt))

        raise last_error

    def get_error_statistics(self) -> dict[str, Any]:
        """Get statistics about validation errors"""
        if not self.error_history:
            return {"total_errors": 0, "most_common_fields": [], "recent_errors": []}

        # Count errors by field
        field_counts = {}
        for record in self.error_history:
            for error in record["errors"]:
                field = error["field"]
                field_counts[field] = field_counts.get(field, 0) + 1

        # Get most common error fields
        most_common = sorted(field_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total_errors": len(self.error_history),
            "most_common_fields": most_common,
            "recent_errors": self.error_history[-5:],
        }

    def add_custom_schema(self, schema: ValidationSchema):
        """Add a custom validation schema"""
        self.schemas[schema.name] = schema

    def clear_cache(self):
        """Clear validation cache"""
        self.validation_cache.clear()

    def export_schemas(self) -> dict[str, Any]:
        """Export all validation schemas as JSON"""
        export_data = {}
        for name, schema in self.schemas.items():
            export_data[name] = {
                "name": schema.name,
                "allow_extra_fields": schema.allow_extra_fields,
                "rules": [
                    {
                        "field": rule.field,
                        "type": rule.validation_type.value,
                        "params": rule.params,
                        "error_message": rule.error_message,
                    }
                    for rule in schema.rules
                ],
            }
        return export_data


if __name__ == "__main__":

    async def test_validator():
        """Test the API validator"""
        validator = APIValidator()

        print("=" * 80)
        print("🔍 API VALIDATOR TEST")
        print("=" * 80)

        # Test valid user registration
        print("\n🧪 Testing valid user registration...")
        valid_user = {
            "username": "test_user123",
            "email": "test@example.com",
            "age": 25,
            "preferences": {"theme": "dark"},
        }

        try:
            result = await validator.validate_request("user_registration", valid_user)
            print(f"✅ Valid user data: {result}")
        except ValidationError as e:
            print(f"❌ Validation failed: {e}")

        # Test invalid email
        print("\n🧪 Testing invalid email...")
        invalid_email = {"username": "test_user", "email": "not-an-email", "age": 25}

        try:
            result = await validator.validate_request(
                "user_registration", invalid_email
            )
            print(f"✅ Valid: {result}")
        except ValidationError as e:
            print(f"✅ Correctly rejected: {e}")

        # Test dream initiation
        print("\n🧪 Testing dream initiation...")
        dream_request = {
            "user_id": "user_123",
            "dream_type": "lucid",
            "duration": 45,
            "intensity": 0.7,
        }

        try:
            result = await validator.validate_request("dream_initiation", dream_request)
            print(f"✅ Valid dream request: {result}")
        except ValidationError as e:
            print(f"❌ Validation failed: {e}")

        # Test invalid dream type
        print("\n🧪 Testing invalid dream type...")
        invalid_dream = {
            "user_id": "user_123",
            "dream_type": "nightmare",  # Not in allowed values
            "duration": 45,
            "intensity": 0.7,
        }

        try:
            result = await validator.validate_request("dream_initiation", invalid_dream)
            print(f"✅ Valid: {result}")
        except ValidationError as e:
            print(f"✅ Correctly rejected: {e}")

        # Get error statistics
        print("\n📊 Error Statistics:")
        stats = validator.get_error_statistics()
        print(f"Total errors: {stats['total_errors']}")
        print(f"Most common error fields: {stats['most_common_fields']}")

        print("\n" + "=" * 80)
        print("✅ API Validator Test Complete")
        print("=" * 80)

    # Run test
    import asyncio

    asyncio.run(test_validator())
