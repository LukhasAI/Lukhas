#!/usr/bin/env python3
"""
Configuration validation tool for LUKHAS modules.
Validates YAML configs against schemas and detects potential secrets.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from typing import Any, Dict, List

import yaml

try:
    import jsonschema
except ImportError:
    print("❌ jsonschema package required: pip install jsonschema")
    sys.exit(1)

class ConfigValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []

        # Load schemas
        self.schemas = {}
        schema_dir = pathlib.Path(__file__).parent.parent / "schemas"

        for schema_file in ["config.schema.json", "logging.schema.json"]:
            schema_path = schema_dir / schema_file
            if schema_path.exists():
                with open(schema_path) as f:
                    schema_name = schema_file.replace(".schema.json", "")
                    self.schemas[schema_name] = json.load(f)

        # Secret detection patterns
        self.secret_patterns = [
            (r"(?i)(secret|token|password|api[_-]?key|private[_-]?key)\s*:\s*['\"]?([A-Za-z0-9+/]{12,})['\"]?", "Potential secret"),
            (r"(?i)(bearer|auth)\s*:\s*['\"]?([A-Za-z0-9+/]{20,})['\"]?", "Potential auth token"),
            (r"(?i)(password|passwd|pwd)\s*:\s*['\"]?([A-Za-z0-9!@#$%^&*]{8,})['\"]?", "Potential password"),
            (r"(?i)(cert|certificate|crt)\s*:\s*['\"]?(-----BEGIN[^-]+-----[A-Za-z0-9+/\s=]*-----END[^-]+-----)['\"]?", "Potential certificate"),
        ]

    def validate_yaml_file(self, file_path: pathlib.Path, schema_name: str) -> bool:
        """Validate a YAML file against a schema."""
        try:
            with open(file_path) as f:
                content = yaml.safe_load(f)

            if schema_name in self.schemas:
                try:
                    jsonschema.validate(content, self.schemas[schema_name])
                    return True
                except jsonschema.ValidationError as e:
                    self.errors.append(f"{file_path}: Schema validation failed - {e.message}")
                    return False
            else:
                self.warnings.append(f"{file_path}: No schema available for {schema_name}")
                return True

        except yaml.YAMLError as e:
            self.errors.append(f"{file_path}: YAML parse error - {e}")
            return False
        except Exception as e:
            self.errors.append(f"{file_path}: Unexpected error - {e}")
            return False

    def detect_secrets(self, file_path: pathlib.Path) -> List[str]:
        """Detect potential secrets in a file."""
        secrets_found = []

        try:
            with open(file_path) as f:
                content = f.read()

            for pattern, description in self.secret_patterns:
                matches = re.finditer(pattern, content, re.MULTILINE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    secrets_found.append(f"{file_path}:{line_num} - {description}: {match.group(1)}")

        except Exception as e:
            self.warnings.append(f"{file_path}: Could not scan for secrets - {e}")

        return secrets_found

    def validate_module_configs(self, module_path: pathlib.Path) -> Dict[str, Any]:
        """Validate all config files in a module."""
        results = {
            "module": module_path.name,
            "config_valid": False,
            "logging_valid": False,
            "environment_valid": False,
            "secrets_found": []
        }

        config_dir = module_path / "config"
        if not config_dir.exists():
            return results

        # Validate config.yaml
        config_file = config_dir / "config.yaml"
        if config_file.exists():
            results["config_valid"] = self.validate_yaml_file(config_file, "config")
            results["secrets_found"].extend(self.detect_secrets(config_file))

        # Validate logging.yaml
        logging_file = config_dir / "logging.yaml"
        if logging_file.exists():
            results["logging_valid"] = self.validate_yaml_file(logging_file, "logging")
            results["secrets_found"].extend(self.detect_secrets(logging_file))

        # Check environment.yaml for secrets (should not have real values)
        env_file = config_dir / "environment.yaml"
        if env_file.exists():
            results["environment_valid"] = self.validate_environment_file(env_file)
            results["secrets_found"].extend(self.detect_secrets(env_file))

        return results

    def validate_environment_file(self, env_file: pathlib.Path) -> bool:
        """Validate environment.yaml contains only placeholder values."""
        try:
            with open(env_file) as f:
                content = yaml.safe_load(f)

            if not isinstance(content, dict):
                return True

            # Check for non-placeholder values
            for key, value in self._flatten_dict(content).items():
                if isinstance(value, str):
                    # Allow placeholder patterns
                    if re.match(r'^(\$\{[A-Z_]+\}|<[A-Z_]+>|TBD|PLACEHOLDER|EXAMPLE)$', value):
                        continue
                    # Flag potentially real values
                    if len(value) > 10 and not value.isupper():
                        self.warnings.append(f"{env_file}: Possible real value in environment: {key}")

            return True
        except Exception as e:
            self.errors.append(f"{env_file}: Environment validation error - {e}")
            return False

    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """Flatten nested dictionary."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

def main():
    """Main validation function."""
    validator = ConfigValidator()

    # Find all module directories
    root_path = pathlib.Path(".")
    module_dirs = [d for d in root_path.iterdir()
                   if d.is_dir() and not d.name.startswith('.') and (d / "config").exists()]

    if not module_dirs:
        print("No module directories with config/ found")
        return 0

    print(f"🔍 Validating configurations for {len(module_dirs)} modules...")

    total_modules = 0
    valid_modules = 0
    total_secrets = 0

    for module_dir in sorted(module_dirs):
        results = validator.validate_module_configs(module_dir)
        total_modules += 1

        if results["config_valid"] and results["logging_valid"] and results["environment_valid"]:
            valid_modules += 1
            status = "✅"
        else:
            status = "❌"

        secrets_count = len(results["secrets_found"])
        total_secrets += secrets_count

        print(f"{status} {results['module']}: "
              f"config={results['config_valid']}, "
              f"logging={results['logging_valid']}, "
              f"env={results['environment_valid']}, "
              f"secrets={secrets_count}")

        # Show secrets found
        for secret in results["secrets_found"]:
            print(f"   🔐 {secret}")

    print("\n📊 Summary:")
    print(f"   Modules validated: {total_modules}")
    print(f"   Valid modules: {valid_modules}")
    print(f"   Invalid modules: {total_modules - valid_modules}")
    print(f"   Potential secrets found: {total_secrets}")

    # Show errors and warnings
    if validator.errors:
        print(f"\n❌ Errors ({len(validator.errors)}):")
        for error in validator.errors:
            print(f"   {error}")

    if validator.warnings:
        print(f"\n⚠️  Warnings ({len(validator.warnings)}):")
        for warning in validator.warnings:
            print(f"   {warning}")

    # Exit code based on results
    if validator.errors or total_secrets > 0:
        print("\n💥 Validation failed due to errors or secrets detected")
        return 1
    elif total_modules - valid_modules > 0:
        print("\n⚠️  Some modules have invalid configurations")
        return 1
    else:
        print("\n✅ All configurations are valid and secure")
        return 0

if __name__ == "__main__":
    sys.exit(main())
