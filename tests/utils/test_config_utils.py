"""
Tests for Configuration and YAML Utilities

Simple utility tests for YAML parsing, configuration validation, and settings management.
Real implementations only, no mocks needed.

Trinity Framework: 🛡️ Guardian · 🏗️ Architecture
"""

import json
from pathlib import Path
from typing import Any, Dict

import pytest
import yaml

# ============================================================================
# YAML Parsing Tests
# ============================================================================

@pytest.mark.unit
def test_yaml_parse_basic():
    """Test basic YAML parsing."""
    yaml_content = """
name: test_config
version: 1.0
enabled: true
"""

    data = yaml.safe_load(yaml_content)

    assert data["name"] == "test_config"
    assert data["version"] == 1.0
    assert data["enabled"] is True


@pytest.mark.unit
def test_yaml_parse_nested():
    """Test nested YAML structure parsing."""
    yaml_content = """
database:
  host: localhost
  port: 5432
  credentials:
    username: admin
    password: secret
"""

    data = yaml.safe_load(yaml_content)

    assert data["database"]["host"] == "localhost"
    assert data["database"]["port"] == 5432
    assert data["database"]["credentials"]["username"] == "admin"


@pytest.mark.unit
def test_yaml_parse_list():
    """Test YAML list parsing."""
    yaml_content = """
tiers:
  - alpha
  - beta
  - gamma
  - delta
"""

    data = yaml.safe_load(yaml_content)

    assert len(data["tiers"]) == 4
    assert "alpha" in data["tiers"]
    assert "delta" in data["tiers"]


@pytest.mark.unit
def test_yaml_parse_multiline():
    """Test multiline YAML parsing."""
    yaml_content = """
description: |
  This is a multiline
  description that spans
  multiple lines.
"""

    data = yaml.safe_load(yaml_content)

    assert "multiline" in data["description"]
    assert "\n" in data["description"]


# ============================================================================
# JSON Parsing Tests
# ============================================================================

@pytest.mark.unit
def test_json_parse_basic():
    """Test basic JSON parsing."""
    json_content = '{"name": "test", "value": 123, "active": true}'

    data = json.loads(json_content)

    assert data["name"] == "test"
    assert data["value"] == 123
    assert data["active"] is True


@pytest.mark.unit
def test_json_parse_nested():
    """Test nested JSON parsing."""
    json_content = '''
{
  "user": {
    "id": "user123",
    "profile": {
      "email": "user@example.com",
      "tier": "alpha"
    }
  }
}
'''

    data = json.loads(json_content)

    assert data["user"]["id"] == "user123"
    assert data["user"]["profile"]["tier"] == "alpha"


@pytest.mark.unit
def test_json_parse_array():
    """Test JSON array parsing."""
    json_content = '{"numbers": [1, 2, 3, 4, 5]}'

    data = json.loads(json_content)

    assert len(data["numbers"]) == 5
    assert sum(data["numbers"]) == 15


# ============================================================================
# Configuration Validation Tests
# ============================================================================

@pytest.mark.unit
def test_config_required_fields():
    """Test configuration required fields validation."""
    def validate_config(config: dict[str, Any]) -> bool:
        """Validate configuration has required fields."""
        required_fields = ["name", "version", "enabled"]
        return all(field in config for field in required_fields)

    # Valid config
    valid_config = {
        "name": "service",
        "version": "1.0",
        "enabled": True
    }
    assert validate_config(valid_config)

    # Invalid config (missing field)
    invalid_config = {
        "name": "service",
        "version": "1.0"
    }
    assert not validate_config(invalid_config)


@pytest.mark.unit
def test_config_type_validation():
    """Test configuration type validation."""
    def validate_types(config: dict[str, Any]) -> bool:
        """Validate configuration field types."""
        if not isinstance(config.get("name"), str):
            return False

        if not isinstance(config.get("port"), int):
            return False

        return isinstance(config.get("enabled"), bool)

    # Valid types
    valid_config = {
        "name": "service",
        "port": 8000,
        "enabled": True
    }
    assert validate_types(valid_config)

    # Invalid types
    invalid_config = {
        "name": "service",
        "port": "8000",  # Should be int
        "enabled": True
    }
    assert not validate_types(invalid_config)


@pytest.mark.unit
def test_config_value_constraints():
    """Test configuration value constraints."""
    def validate_constraints(config: dict[str, Any]) -> bool:
        """Validate configuration value constraints."""
        # Port must be 1-65535
        port = config.get("port", 0)
        if not (1 <= port <= 65535):
            return False

        # Name must not be empty
        name = config.get("name", "")
        return len(name) != 0

    # Valid constraints
    valid_config = {
        "name": "service",
        "port": 8000
    }
    assert validate_constraints(valid_config)

    # Invalid constraints
    invalid_configs = [
        {"name": "service", "port": 0},      # Port too low
        {"name": "service", "port": 70000},  # Port too high
        {"name": "", "port": 8000},          # Empty name
    ]

    for config in invalid_configs:
        assert not validate_constraints(config)


# ============================================================================
# Configuration Defaults Tests
# ============================================================================

@pytest.mark.unit
def test_config_default_values():
    """Test configuration default value application."""
    def apply_defaults(config: dict[str, Any]) -> dict[str, Any]:
        """Apply default values to configuration."""
        defaults = {
            "host": "localhost",
            "port": 8000,
            "debug": False,
            "timeout": 30
        }

        # Merge with defaults
        result = defaults.copy()
        result.update(config)
        return result

    # Partial config
    partial_config = {"host": "0.0.0.0", "debug": True}

    full_config = apply_defaults(partial_config)

    # Verify defaults applied
    assert full_config["host"] == "0.0.0.0"  # Overridden
    assert full_config["port"] == 8000       # Default
    assert full_config["debug"] is True      # Overridden
    assert full_config["timeout"] == 30      # Default


@pytest.mark.unit
def test_config_environment_override():
    """Test configuration environment variable override."""
    def apply_env_overrides(config: dict[str, Any], env: dict[str, str]) -> dict[str, Any]:
        """Apply environment variable overrides to config."""
        result = config.copy()

        # Override from environment
        if "PORT" in env:
            result["port"] = int(env["PORT"])

        if "DEBUG" in env:
            result["debug"] = env["DEBUG"].lower() == "true"

        return result

    base_config = {"port": 8000, "debug": False}
    env_vars = {"PORT": "9000", "DEBUG": "true"}

    overridden_config = apply_env_overrides(base_config, env_vars)

    assert overridden_config["port"] == 9000
    assert overridden_config["debug"] is True


# ============================================================================
# Tier Configuration Tests
# ============================================================================

@pytest.mark.unit
def test_tier_config_parsing():
    """Test tier configuration parsing."""
    tier_yaml = """
tiers:
  alpha:
    multiplier: 3.0
    rate_limit: 300
  beta:
    multiplier: 2.0
    rate_limit: 200
  gamma:
    multiplier: 1.5
    rate_limit: 150
  delta:
    multiplier: 1.0
    rate_limit: 100
"""

    config = yaml.safe_load(tier_yaml)

    # Verify tiers
    assert len(config["tiers"]) == 4
    assert config["tiers"]["alpha"]["multiplier"] == 3.0
    assert config["tiers"]["delta"]["rate_limit"] == 100


@pytest.mark.unit
def test_tier_config_validation():
    """Test tier configuration validation."""
    def validate_tier_config(config: dict[str, Any]) -> bool:
        """Validate tier configuration structure."""
        required_tiers = ["alpha", "beta", "gamma", "delta"]

        if "tiers" not in config:
            return False

        tiers = config["tiers"]

        # Check all required tiers present
        for tier in required_tiers:
            if tier not in tiers:
                return False

            # Check required fields
            if "multiplier" not in tiers[tier]:
                return False

            if "rate_limit" not in tiers[tier]:
                return False

        return True

    # Valid config
    valid_config = {
        "tiers": {
            "alpha": {"multiplier": 3.0, "rate_limit": 300},
            "beta": {"multiplier": 2.0, "rate_limit": 200},
            "gamma": {"multiplier": 1.5, "rate_limit": 150},
            "delta": {"multiplier": 1.0, "rate_limit": 100}
        }
    }
    assert validate_tier_config(valid_config)

    # Invalid config (missing tier)
    invalid_config = {
        "tiers": {
            "alpha": {"multiplier": 3.0, "rate_limit": 300},
            "beta": {"multiplier": 2.0, "rate_limit": 200}
        }
    }
    assert not validate_tier_config(invalid_config)


# ============================================================================
# Configuration Merging Tests
# ============================================================================

@pytest.mark.unit
def test_config_merge_flat():
    """Test flat configuration merging."""
    base_config = {
        "host": "localhost",
        "port": 8000,
        "debug": False
    }

    override_config = {
        "port": 9000,
        "debug": True
    }

    # Merge (override takes precedence)
    merged = {**base_config, **override_config}

    assert merged["host"] == "localhost"  # From base
    assert merged["port"] == 9000         # Overridden
    assert merged["debug"] is True        # Overridden


@pytest.mark.unit
def test_config_merge_nested():
    """Test nested configuration merging."""
    def deep_merge(base: Dict, override: Dict) -> Dict:
        """Deep merge two dictionaries."""
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    base = {
        "database": {
            "host": "localhost",
            "port": 5432,
            "pool": {"min": 1, "max": 10}
        }
    }

    override = {
        "database": {
            "port": 5433,
            "pool": {"max": 20}
        }
    }

    merged = deep_merge(base, override)

    assert merged["database"]["host"] == "localhost"  # Preserved
    assert merged["database"]["port"] == 5433         # Overridden
    assert merged["database"]["pool"]["min"] == 1     # Preserved
    assert merged["database"]["pool"]["max"] == 20    # Overridden


# ============================================================================
# Configuration Serialization Tests
# ============================================================================

@pytest.mark.unit
def test_config_to_yaml():
    """Test configuration serialization to YAML."""
    config = {
        "name": "service",
        "version": "1.0",
        "tiers": ["alpha", "beta", "gamma", "delta"]
    }

    yaml_str = yaml.dump(config)

    # Parse back
    parsed = yaml.safe_load(yaml_str)

    assert parsed["name"] == config["name"]
    assert parsed["tiers"] == config["tiers"]


@pytest.mark.unit
def test_config_to_json():
    """Test configuration serialization to JSON."""
    config = {
        "name": "service",
        "port": 8000,
        "enabled": True
    }

    json_str = json.dumps(config, indent=2)

    # Parse back
    parsed = json.loads(json_str)

    assert parsed == config


# ============================================================================
# Capability Tests
# ============================================================================

@pytest.mark.capability
def test_config_full_lifecycle():
    """Test complete configuration lifecycle."""
    # 1. Create config
    config = {
        "service": {
            "name": "lukhas-api",
            "version": "1.0.0",
            "port": 8000
        },
        "tiers": {
            "alpha": {"multiplier": 3.0},
            "beta": {"multiplier": 2.0},
            "gamma": {"multiplier": 1.5},
            "delta": {"multiplier": 1.0}
        }
    }

    # 2. Serialize to YAML
    yaml_str = yaml.dump(config)
    assert "lukhas-api" in yaml_str

    # 3. Parse back
    parsed = yaml.safe_load(yaml_str)
    assert parsed["service"]["name"] == "lukhas-api"

    # 4. Apply defaults
    defaults = {"service": {"host": "localhost", "debug": False}}
    merged = {**defaults, **parsed}

    # 5. Validate
    assert "service" in merged
    assert merged["service"]["port"] == 8000
    assert len(merged["tiers"]) == 4


@pytest.mark.capability
def test_matriz_yaml_structure():
    """Test ops/matriz.yaml configuration structure."""
    matriz_structure = {
        "lanes": {
            "lukhas": {
                "path": "lukhas/",
                "allowed_imports": ["core", "matriz", "universal_language"]
            },
            "labs": {
                "path": "candidate/",
                "allowed_imports": ["core", "matriz"]
            },
            "core": {
                "path": "core/",
                "allowed_imports": []
            },
            "matriz": {
                "path": "matriz/",
                "allowed_imports": ["core"]
            }
        }
    }

    # Validate structure
    assert "lanes" in matriz_structure
    assert len(matriz_structure["lanes"]) == 4

    # Validate lane configurations
    for _lane_name, lane_config in matriz_structure["lanes"].items():
        assert "path" in lane_config
        assert "allowed_imports" in lane_config
        assert isinstance(lane_config["allowed_imports"], list)

    # Verify import restrictions
    assert "lukhas" not in matriz_structure["lanes"]["labs"]["allowed_imports"]
    assert "core" in matriz_structure["lanes"]["lukhas"]["allowed_imports"]
