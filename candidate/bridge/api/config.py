# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: config.py
# MODULE: core
# DESCRIPTION: Central configuration management for LUKHAS AGI system.
#              Provides environment-based configuration for all services
#              and components with secure defaults and validation.
# DEPENDENCIES: pydantic, typing, os
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════

import os
import secrets
import time
from typing import Optional

import streamlit as st
from pydantic import BaseSettings, Field, validator

from consciousness.qi import qi

# TAG:bridge
# TAG:api
# TAG:neuroplastic
# TAG:colony


class LukhasConfig(BaseSettings):
    """Central configuration for LUKHAS AGI system"""

    # Database Configuration
    database_url: str = Field(
        default_factory=lambda: os.getenv("DATABASE_URL", ""),
        description="Main PostgreSQL database connection",
    )

    # Security
    secret_key: str = Field(
        default_factory=lambda: os.getenv("LUKHAS_ID_SECRET", secrets.token_urlsafe(32)),
        description="Main secret key for cryptographic operations",
    )

    # API Endpoints - Use environment variables with sensible defaults
    api_base_url: str = Field(
        default_factory=lambda: os.getenv("API_BASE_URL", "http://localhost:8080"),
        description="Base URL for main API",
    )

    orchestration_api_url: str = Field(
        default_factory=lambda: os.getenv(
            "ORCHESTRATION_API_URL",
            "http://localhost:8080/api/v1/orchestration",
        ),
        description="Orchestration service endpoint",
    )

    memory_api_url: str = Field(
        default_factory=lambda: os.getenv("MEMORY_API_URL", "http://localhost:8080/api/v1/memory"),
        description="Memory service endpoint",
    )

    qi_api_url: str = Field(
        default_factory=lambda: os.getenv("QUANTUM_API_URL", "http://localhost:8080/api/v1/quantum"),
        description="Quantum service endpoint",
    )

    # External Services
    ollama_url: str = Field(
        default_factory=lambda: os.getenv("OLLAMA_URL", "http://localhost:11434"),
        description="Ollama LLM service endpoint",
    )

    # Application Settings
    debug: bool = Field(
        default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true",
        description="Debug mode flag",
    )

    environment: str = Field(
        default_factory=lambda: os.getenv("ENVIRONMENT", "development"),
        description="Runtime environment (development/staging/production)",
    )

    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY", description="OpenAI API key")

    # CORS Settings
    cors_origins: str = Field(
        default_factory=lambda: os.getenv(
            "LUKHAS_API_CORS_ORIGINS",
            "http://localhost:3000,http://localhost:5000,https://*.lukhas.ai",
        ),
        description="Allowed CORS origins (comma-separated)",
    )

    @validator("database_url")
    def validate_database_url(cls, v):
        """Ensure database URL is provided in production"""
        env = os.getenv("ENVIRONMENT", "development")
        if not v and env == "production":
            raise ValueError("DATABASE_URL must be set in production")
        return v

    @validator("secret_key")
    def validate_secret_strength(cls, v):
        """Ensure secret key is sufficiently strong"""
        if v and len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        return v

    @validator("environment")
    def validate_environment(cls, v):
        """Validate environment setting"""
        valid_envs = ["development", "staging", "production", "test"]
        if v not in valid_envs:
            raise ValueError(f"Environment must be one of: {', '.join(valid_envs)}")
        return v

    def get_cors_origins_list(self) -> list[str]:
        """Parse CORS origins string into list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == "production"

    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global configuration instance
_config: Optional[LukhasConfig] = None


def get_config() -> LukhasConfig:
    """Get global configuration instance (singleton pattern)"""
    global _config
    if _config is None:
        _config = LukhasConfig()
    return _config


# ═══════════════════════════════════════════════════════════════════════════
# HOW TO USE:
#   from candidate.core.common.config import get_config
#
#   config = get_config()
#   db_url = config.database_url
#   api_url = config.api_base_url
#
#   # Check environment
#   if config.is_production():
#       # Production-specific code
#
#   # Get CORS origins as list
#   allowed_origins = config.get_cors_origins_list()
# ═══════════════════════════════════════════════════════════════════════════
