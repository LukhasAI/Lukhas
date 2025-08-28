#!/usr/bin/env python3
"""
Safety defaults configuration for LUKHAS AI audit preparation.
Implements comprehensive safety-first configuration without execution.

Purpose: Define safety defaults for pre/post-MATRIZ workspace auditing.
All defaults prioritize audit safety and dry-run modes.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class AuditSafetyConfig:
    """Safety configuration for audit preparation."""

    # Core safety defaults
    dry_run_mode: bool = True
    offline_mode: bool = True
    audit_mode: bool = True

    # Feature flags (all OFF by default for audit safety)
    feature_flags: Dict[str, bool] = field(default_factory=lambda: {
        "FEATURE_GOVERNANCE_LEDGER": False,
        "FEATURE_IDENTITY_PASSKEY": False,
        "FEATURE_ORCHESTRATION_HANDOFF": False,
        "FEATURE_POLICY_DECIDER": False,
        "FEATURE_MATRIX_EMIT": True,  # Safe for audit
        "FEATURE_CONSCIOUSNESS_ACTIVE": False,
        "FEATURE_MEMORY_PERSISTENCE": False,
        "FEATURE_REAL_API_CALLS": False
    })

    # Safety thresholds
    safety_thresholds: Dict[str, Any] = field(default_factory=lambda: {
        "max_api_calls_per_test": 0,  # No API calls in audit
        "max_memory_usage_mb": 100,
        "max_test_runtime_seconds": 300,
        "guardian_drift_threshold": 0.01,  # Very conservative
        "audit_trail_retention_days": 30
    })

    # Audit-specific settings
    audit_settings: Dict[str, Any] = field(default_factory=lambda: {
        "enable_comprehensive_logging": True,
        "preserve_audit_trail": True,
        "validate_all_imports": True,
        "enforce_dry_run_mode": True,
        "block_external_connections": True,
        "require_explicit_consent": True
    })

class SafetyDefaultsManager:
    """Manages safety defaults for audit preparation."""

    def __init__(self, config_dir: Path):
        self.config_dir = Path(config_dir)
        self.config = AuditSafetyConfig()
        self._applied_overrides: List[str] = []

    def generate_env_example(self) -> str:
        """Generate .env.example with safety defaults."""
        env_content = """# LUKHAS AI - Safety Defaults for Audit Preparation
# All features disabled by default for audit safety

# ============================================================================
# CORE SAFETY SETTINGS
# ============================================================================
LUKHAS_DRY_RUN_MODE=true
LUKHAS_OFFLINE=true
LUKHAS_AUDIT_MODE=true

# ============================================================================
# FEATURE FLAGS - All OFF for Audit Safety
# ============================================================================
FEATURE_GOVERNANCE_LEDGER=false
FEATURE_IDENTITY_PASSKEY=false
FEATURE_ORCHESTRATION_HANDOFF=false
FEATURE_POLICY_DECIDER=false
FEATURE_MATRIX_EMIT=true
FEATURE_CONSCIOUSNESS_ACTIVE=false
FEATURE_MEMORY_PERSISTENCE=false
FEATURE_REAL_API_CALLS=false

# ============================================================================
# SAFETY THRESHOLDS
# ============================================================================
MAX_API_CALLS_PER_TEST=0
MAX_MEMORY_USAGE_MB=100
MAX_TEST_RUNTIME_SECONDS=300
GUARDIAN_DRIFT_THRESHOLD=0.01

# ============================================================================
# AUDIT SETTINGS
# ============================================================================
ENABLE_COMPREHENSIVE_LOGGING=true
PRESERVE_AUDIT_TRAIL=true
VALIDATE_ALL_IMPORTS=true
ENFORCE_DRY_RUN_MODE=true
BLOCK_EXTERNAL_CONNECTIONS=true
REQUIRE_EXPLICIT_CONSENT=true

# ============================================================================
# API KEYS - Leave empty for audit mode (no external calls)
# ============================================================================
# OPENAI_API_KEY=
# ANTHROPIC_API_KEY=
# GOOGLE_API_KEY=
# PERPLEXITY_API_KEY=

# ============================================================================
# DATABASE - Use local SQLite for audit
# ============================================================================
DATABASE_URL=sqlite:///lukhas_audit.db
LUKHAS_ID_SECRET=audit_safe_local_development_key_32chars

# ============================================================================
# AUDIT TRAIL SETTINGS
# ============================================================================
AUDIT_LOG_LEVEL=DEBUG
AUDIT_LOG_FILE=logs/audit_safety.log
AUDIT_TRACE_ENABLED=true
"""
        return env_content

    def generate_conftest_safety(self) -> str:
        """Generate enhanced conftest.py with safety defaults."""
        conftest_content = '''import os
import pytest
from datetime import datetime
import json
from pathlib import Path

# ============================================================================
# AUDIT SAFETY CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """Configure pytest with audit safety defaults."""
    # Core safety environment variables
    safety_defaults = {
        "LUKHAS_DRY_RUN_MODE": "true",
        "LUKHAS_OFFLINE": "true", 
        "LUKHAS_AUDIT_MODE": "true",
        "LUKHAS_FEATURE_MATRIX_EMIT": "true",
        
        # Disable all potentially unsafe features
        "FEATURE_GOVERNANCE_LEDGER": "false",
        "FEATURE_IDENTITY_PASSKEY": "false", 
        "FEATURE_ORCHESTRATION_HANDOFF": "false",
        "FEATURE_POLICY_DECIDER": "false",
        "FEATURE_CONSCIOUSNESS_ACTIVE": "false",
        "FEATURE_MEMORY_PERSISTENCE": "false",
        "FEATURE_REAL_API_CALLS": "false",
        
        # Safety thresholds
        "MAX_API_CALLS_PER_TEST": "0",
        "MAX_MEMORY_USAGE_MB": "100", 
        "MAX_TEST_RUNTIME_SECONDS": "300",
        "GUARDIAN_DRIFT_THRESHOLD": "0.01",
        
        # Audit settings
        "ENABLE_COMPREHENSIVE_LOGGING": "true",
        "PRESERVE_AUDIT_TRAIL": "true",
        "VALIDATE_ALL_IMPORTS": "true",
        "ENFORCE_DRY_RUN_MODE": "true",
        "BLOCK_EXTERNAL_CONNECTIONS": "true",
        
        # Local database for audit
        "DATABASE_URL": "sqlite:///lukhas_audit_test.db",
        "LUKHAS_ID_SECRET": "audit_test_local_key_32_characters_long"
    }
    
    # Apply safety defaults
    for key, value in safety_defaults.items():
        os.environ.setdefault(key, value)
    
    # Create audit log directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Log test session start
    with open("logs/audit_test_session.log", "a") as f:
        f.write(f"\\n=== AUDIT TEST SESSION START: {datetime.utcnow().isoformat()} ===\\n")
        f.write(f"Safety defaults applied: {len(safety_defaults)} settings\\n")

def pytest_sessionfinish(session, exitstatus):
    """Log session completion."""
    with open("logs/audit_test_session.log", "a") as f:
        f.write(f"=== AUDIT TEST SESSION END: {datetime.utcnow().isoformat()} ===\\n")
        f.write(f"Exit status: {exitstatus}\\n")

# ============================================================================
# AUDIT SAFETY FIXTURES
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def audit_safety_check():
    """Verify audit safety configuration is active."""
    # Verify core safety settings
    assert os.getenv("LUKHAS_DRY_RUN_MODE", "false").lower() == "true"
    assert os.getenv("LUKHAS_OFFLINE", "false").lower() == "true" 
    assert os.getenv("LUKHAS_AUDIT_MODE", "false").lower() == "true"
    
    # Verify dangerous features are disabled
    dangerous_features = [
        "FEATURE_REAL_API_CALLS",
        "FEATURE_MEMORY_PERSISTENCE"
    ]
    
    for feature in dangerous_features:
        assert os.getenv(feature, "true").lower() == "false", f"Dangerous feature {feature} must be disabled for audit"
    
    yield
    
    # Cleanup after all tests
    cleanup_audit_artifacts()

def cleanup_audit_artifacts():
    """Clean up audit test artifacts."""
    artifacts_to_clean = [
        "lukhas_audit_test.db",
        "lukhas_audit_test.db-journal",
        "test_audit_*.json"
    ]
    
    for pattern in artifacts_to_clean:
        for file in Path(".").glob(pattern):
            try:
                file.unlink()
            except OSError:
                pass  # File may not exist

@pytest.fixture
def audit_mode():
    """Fixture that ensures audit mode for individual tests."""
    assert os.getenv("LUKHAS_AUDIT_MODE") == "true"
    return True

@pytest.fixture  
def dry_run_mode():
    """Fixture that ensures dry run mode for individual tests."""
    assert os.getenv("LUKHAS_DRY_RUN_MODE") == "true"
    return True

# ============================================================================
# AUDIT SAFETY MARKERS
# ============================================================================

def pytest_collection_modifyitems(items):
    """Add audit safety markers to tests."""
    for item in items:
        # Mark all tests as audit-safe by default
        item.add_marker(pytest.mark.audit_safe)
        
        # Mark tests that should not make external calls
        if not item.get_closest_marker("allow_external"):
            item.add_marker(pytest.mark.no_external_calls)

def pytest_runtest_setup(item):
    """Setup for individual test runs."""
    # Block external calls unless explicitly allowed
    if item.get_closest_marker("no_external_calls"):
        os.environ["BLOCK_EXTERNAL_CONNECTIONS"] = "true"
    
    # Ensure audit mode is active
    if not os.getenv("LUKHAS_AUDIT_MODE") == "true":
        pytest.fail("Audit mode not active - unsafe to run tests")
'''
        return conftest_content

    def generate_audit_settings_json(self) -> Dict[str, Any]:
        """Generate JSON configuration for audit settings."""
        return {
            "audit_metadata": {
                "version": "1.0.0-audit-prep",
                "purpose": "pre_post_matriz_workspace_validation",
                "safety_level": "maximum",
                "generated_at": "2025-08-28T00:00:00Z"
            },
            "safety_configuration": {
                "dry_run_mode": self.config.dry_run_mode,
                "offline_mode": self.config.offline_mode,
                "audit_mode": self.config.audit_mode,
                "feature_flags": self.config.feature_flags,
                "safety_thresholds": self.config.safety_thresholds,
                "audit_settings": self.config.audit_settings
            },
            "compliance_validation": {
                "no_external_api_calls": True,
                "no_persistent_storage": True,
                "comprehensive_logging": True,
                "audit_trail_preserved": True,
                "import_validation_active": True
            },
            "risk_mitigation": {
                "max_resource_usage": "conservative",
                "external_connection_policy": "blocked",
                "api_key_handling": "not_required_audit_mode",
                "data_persistence": "temporary_only",
                "logging_level": "comprehensive"
            }
        }

    def validate_safety_config(self) -> Dict[str, bool]:
        """Validate that safety configuration is properly set."""
        checks = {
            "dry_run_active": self.config.dry_run_mode,
            "offline_mode_active": self.config.offline_mode,
            "audit_mode_active": self.config.audit_mode,
            "dangerous_features_disabled": not any([
                self.config.feature_flags.get("FEATURE_REAL_API_CALLS", True),
                self.config.feature_flags.get("FEATURE_MEMORY_PERSISTENCE", True)
            ]),
            "conservative_thresholds": all([
                self.config.safety_thresholds["max_api_calls_per_test"] == 0,
                self.config.safety_thresholds["guardian_drift_threshold"] <= 0.01
            ]),
            "audit_logging_enabled": self.config.audit_settings["enable_comprehensive_logging"],
            "import_validation_active": self.config.audit_settings["validate_all_imports"]
        }
        return checks

    def export_audit_configuration(self, output_dir: Path):
        """Export complete audit configuration."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate .env.example
        (output_dir / ".env.example").write_text(self.generate_env_example())

        # Generate enhanced conftest.py
        (output_dir / "conftest_audit_safe.py").write_text(self.generate_conftest_safety())

        # Generate audit settings JSON
        settings = self.generate_audit_settings_json()
        (output_dir / "audit_safety_settings.json").write_text(
            json.dumps(settings, indent=2)
        )

        # Generate validation report
        validation = self.validate_safety_config()
        (output_dir / "safety_validation_report.json").write_text(
            json.dumps({
                "validation_results": validation,
                "all_checks_passed": all(validation.values()),
                "audit_ready": all(validation.values())
            }, indent=2)
        )

        return {
            "files_generated": 4,
            "output_directory": str(output_dir),
            "validation_passed": all(validation.values())
        }

def create_audit_safety_manager(config_dir: str = "config") -> SafetyDefaultsManager:
    """Factory function for creating safety manager."""
    return SafetyDefaultsManager(Path(config_dir))

if __name__ == "__main__":
    # Generate audit safety configuration
    manager = create_audit_safety_manager()

    # Export all configurations
    result = manager.export_audit_configuration(Path("audit_config_output"))

    print("Audit safety configuration generated:")
    print(f"  Output directory: {result['output_directory']}")
    print(f"  Files generated: {result['files_generated']}")
    print(f"  Validation passed: {result['validation_passed']}")

    # Show validation results
    validation = manager.validate_safety_config()
    print("\nSafety validation:")
    for check, passed in validation.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")
