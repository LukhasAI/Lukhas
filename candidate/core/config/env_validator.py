"""
Environment Variable Validator
==============================
Ensures all required environment variables are set with proper values.
Provides secure defaults and validation for sensitive configuration.
"""
import streamlit as st

import logging
import os
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class EnvVarType(Enum):
    """Types of environment variables for validation"""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    URL = "url"
    SECRET = "secret"  # Sensitive data that shouldn't be logged
    PATH = "path"


@dataclass
class EnvVarConfig:
    """Configuration for an environment variable"""

    name: str
    var_type: EnvVarType
    required: bool = True
    default: Optional[Any] = None
    description: str = ""
    min_length: Optional[int] = None  # For strings/secrets
    min_value: Optional[float] = None  # For numbers
    max_value: Optional[float] = None  # For numbers
    allowed_values: list[Any] = field(default_factory=list)


class EnvValidator:
    """Validates and manages environment variables"""

    # Core configuration variables
    REQUIRED_VARS = [
        EnvVarConfig(
            name="OPENAI_API_KEY",
            var_type=EnvVarType.SECRET,
            required=True,
            min_length=32,
            description="OpenAI API key for GPT integration",
        ),
        EnvVarConfig(
            name="DATABASE_URL",
            var_type=EnvVarType.URL,
            required=False,
            default="sqlite:///lukhas.db",
            description="Database connection string",
        ),
        EnvVarConfig(
            name="LUKHAS_ID_SECRET",
            var_type=EnvVarType.SECRET,
            required=True,
            min_length=32,
            description="Security key for identity system",
        ),
        EnvVarConfig(
            name="ETHICS_ENFORCEMENT_LEVEL",
            var_type=EnvVarType.STRING,
            required=False,
            default="strict",
            allowed_values=["strict", "moderate", "lenient"],
            description="Ethics enforcement level",
        ),
        EnvVarConfig(
            name="DREAM_SIMULATION_ENABLED",
            var_type=EnvVarType.BOOLEAN,
            required=False,
            default=True,
            description="Enable dream simulation features",
        ),
        EnvVarConfig(
            name="QUANTUM_PROCESSING_ENABLED",
            var_type=EnvVarType.BOOLEAN,
            required=False,
            default=True,
            description="Enable quantum processing features",
        ),
        EnvVarConfig(
            name="LOG_LEVEL",
            var_type=EnvVarType.STRING,
            required=False,
            default="INFO",
            allowed_values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            description="Logging level",
        ),
        EnvVarConfig(
            name="API_RATE_LIMIT",
            var_type=EnvVarType.INTEGER,
            required=False,
            default=100,
            min_value=1,
            max_value=10000,
            description="API rate limit per minute",
        ),
        EnvVarConfig(
            name="MEMORY_FOLD_LIMIT",
            var_type=EnvVarType.INTEGER,
            required=False,
            default=1000,
            min_value=100,
            max_value=10000,
            description="Maximum memory folds",
        ),
        EnvVarConfig(
            name="DRIFT_THRESHOLD",
            var_type=EnvVarType.FLOAT,
            required=False,
            default=0.15,
            min_value=0.0,
            max_value=1.0,
            description="Ethical drift detection threshold",
        ),
    ]

    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.validated_vars: dict[str, Any] = {}

    def validate_all(self) -> bool:
        """
        Validate all required environment variables.
        Returns True if all validations pass, False otherwise.
        """
        self.errors = []
        self.warnings = []

        for config in self.REQUIRED_VARS:
            self._validate_var(config)

        if self.errors:
            logger.error(f"Environment validation failed with {len(self.errors)} errors")
            for error in self.errors:
                logger.error(f"  - {error}")

        if self.warnings:
            for warning in self.warnings:
                logger.warning(f"  - {warning}")

        return len(self.errors) == 0

    def _validate_var(self, config: EnvVarConfig) -> Optional[Any]:
        """Validate a single environment variable"""
        value = os.getenv(config.name)

        # Check if required but missing
        if value is None:
            if config.required:
                self.errors.append(f"{config.name} is required but not set. {config.description}")
                return None
            else:
                # Use default value
                value = config.default
                self.validated_vars[config.name] = value
                return value

        # Validate based on type
        try:
            validated_value = self._validate_type(value, config)
            self.validated_vars[config.name] = validated_value
            return validated_value
        except ValueError as e:
            self.errors.append(f"{config.name}: {e!s}")
            return None

    def _validate_type(self, value: str, config: EnvVarConfig) -> Any:
        """Validate and convert value based on type"""
        if config.var_type == EnvVarType.STRING:
            if config.min_length and len(value) < config.min_length:
                raise ValueError(f"Must be at least {config.min_length} characters")
            if config.allowed_values and value not in config.allowed_values:
                raise ValueError(f"Must be one of: {config.allowed_values}")
            return value

        elif config.var_type == EnvVarType.SECRET:
            if config.min_length and len(value) < config.min_length:
                raise ValueError(f"Secret must be at least {config.min_length} characters")
            # Don't log the actual secret value
            return value

        elif config.var_type == EnvVarType.INTEGER:
            try:
                int_value = int(value)
                if config.min_value is not None and int_value < config.min_value:
                    raise ValueError(f"Must be >= {config.min_value}")
                if config.max_value is not None and int_value > config.max_value:
                    raise ValueError(f"Must be <= {config.max_value}")
                return int_value
            except ValueError:
                raise ValueError("Must be a valid integer")

        elif config.var_type == EnvVarType.FLOAT:
            try:
                float_value = float(value)
                if config.min_value is not None and float_value < config.min_value:
                    raise ValueError(f"Must be >= {config.min_value}")
                if config.max_value is not None and float_value > config.max_value:
                    raise ValueError(f"Must be <= {config.max_value}")
                return float_value
            except ValueError:
                raise ValueError("Must be a valid float")

        elif config.var_type == EnvVarType.BOOLEAN:
            return value.lower() in ["true", "1", "yes", "on"]

        elif config.var_type == EnvVarType.URL:
            # Basic URL validation
            if not value.startswith(("http://", "https://", "sqlite://", "postgresql://")):
                raise ValueError("Must be a valid URL")
            return value

        elif config.var_type == EnvVarType.PATH:
            # Check if path exists
            if not os.path.exists(value):
                self.warnings.append(f"{config.name}: Path {value} does not exist")
            return value

        return value

    def get(self, name: str, default: Any = None) -> Any:
        """Get a validated environment variable value"""
        return self.validated_vars.get(name, default)

    def get_all(self) -> dict[str, Any]:
        """Get all validated environment variables"""
        return self.validated_vars.copy()

    def create_env_example(self) -> str:
        """Generate .env.example content"""
        lines = [
            "# LUKHAS  Environment Configuration",
            "# Copy this file to .env and fill in your values",
            "# Generated by env_validator.py",
            "",
        ]

        for config in self.REQUIRED_VARS:
            lines.append(f"# {config.description}")
            if config.required:
                lines.append("# REQUIRED")
            else:
                lines.append("# OPTIONAL")

            if config.allowed_values:
                lines.append(f"# Allowed values: {', '.join(map(str, config.allowed_values)}")
            if config.min_length:
                lines.append(f"# Minimum length: {config.min_length}")
            if config.min_value is not None:
                lines.append(f"# Minimum value: {config.min_value}")
            if config.max_value is not None:
                lines.append(f"# Maximum value: {config.max_value}")

            # Generate example value
            if config.var_type == EnvVarType.SECRET:
                example = "your-secret-key-here"
            elif config.var_type == EnvVarType.URL:
                example = "postgresql://user:pass@localhost/dbname"
            elif config.default is not None:
                example = str(config.default)
            else:
                example = "your-value-here"

            lines.append(f"{config.name}={example}")
            lines.append("")

        return "\n".join(lines)


def validate_environment() -> bool:
    """
    Main validation function to be called at startup.
    Returns True if environment is valid, False otherwise.
    """
    validator = EnvValidator()

    if not validator.validate_all():
        print("\n⚠️  Environment validation failed!")
        print("Please ensure all required environment variables are set.")
        print("You can copy .env.example to .env and fill in your values.")
        return False

    print("✅ Environment validation passed")
    return True


def create_env_example_file():
    """Create or update .env.example file"""
    validator = EnvValidator()
    example_content = validator.create_env_example()
    from pathlib import Path

    # Allow env override, else write to repo root
    env_example_path = os.getenv("LUKHAS_ENV_EXAMPLE_PATH")
    if not env_example_path:
        repo_root = Path(__file__).resolve().parents[3]
        env_example_path = str(repo_root / ".env.example")
    with open(env_example_path, "w") as f:
        f.write(example_content)

    print(f"✅ Created {env_example_path}")


if __name__ == "__main__":
    # If run directly, validate environment and optionally create .env.example
    if "--create-example" in sys.argv:
        create_env_example_file()

    if validate_environment():
        sys.exit(0)
    else:
        sys.exit(1)
