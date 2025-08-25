"""
Settings Validator - BATCH 7 Completion
"""
import os
import json
from typing import Dict, Any, List
from pathlib import Path

class SettingsValidator:
    """Validate LUKHAS configuration settings"""

    def __init__(self):
        self.validation_rules = {
            "api_keys": self._validate_api_keys,
            "paths": self._validate_paths,
            "thresholds": self._validate_thresholds,
            "features": self._validate_features
        }

    def validate_config(self, config: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate configuration and return errors"""
        errors = {}

        for section, validator in self.validation_rules.items():
            if section in config:
                section_errors = validator(config[section])
                if section_errors:
                    errors[section] = section_errors

        return errors

    def _validate_api_keys(self, keys: Dict) -> List[str]:
        """Validate API keys configuration"""
        errors = []
        required_keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]

        for key in required_keys:
            if key not in keys or not keys[key]:
                errors.append(f"Missing required API key: {key}")

        return errors

    def _validate_paths(self, paths: Dict) -> List[str]:
        """Validate file paths"""
        errors = []
        for name, path in paths.items():
            if not Path(path).exists():
                errors.append(f"Path does not exist: {name} -> {path}")
        return errors

    def _validate_thresholds(self, thresholds: Dict) -> List[str]:
        """Validate threshold values"""
        errors = []
        for name, value in thresholds.items():
            if not isinstance(value, (int, float)) or value < 0:
                errors.append(f"Invalid threshold: {name} = {value}")
        return errors

    def _validate_features(self, features: Dict) -> List[str]:
        """Validate feature flags"""
        errors = []
        for name, enabled in features.items():
            if not isinstance(enabled, bool):
                errors.append(f"Feature flag must be boolean: {name} = {enabled}")
        return errors

# Usage example
if __name__ == "__main__":
    validator = SettingsValidator()
    test_config = {
        "api_keys": {"OPENAI_API_KEY": "test"},
        "thresholds": {"drift_threshold": 0.15}
    }
    errors = validator.validate_config(test_config)
    print(f"Validation errors: {errors}")
