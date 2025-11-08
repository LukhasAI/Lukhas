#!/usr/bin/env python3
"""
Feature Flags Validation Tool.

Validates feature flags configuration against schema and best practices.

Usage:
    python tools/validate_flags.py
    python tools/validate_flags.py branding/features/flags.yaml
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lukhas.features.flags_service import FlagType

# ANSI color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


class FlagValidator:
    """Validator for feature flags configuration."""

    REQUIRED_FIELDS = ["type", "enabled", "description", "owner", "created_at"]
    OPTIONAL_FIELDS = [
        "jira_ticket",
        "fallback",
        "percentage",
        "allowed_domains",
        "allowed_user_hashes",
        "enable_after",
        "disable_after",
        "allowed_environments",
    ]

    def __init__(self, config_path: str):
        """
        Initialize validator.

        Args:
            config_path: Path to flags YAML configuration
        """
        self.config_path = config_path
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.config: Optional[Dict[str, Any]] = None

    def validate(self) -> bool:
        """
        Validate flags configuration.

        Returns:
            True if validation passes, False otherwise
        """
        # Check file exists
        if not Path(self.config_path).exists():
            self.errors.append(f"Configuration file not found: {self.config_path}")
            return False

        # Load YAML
        try:
            with open(self.config_path, "r") as f:
                self.config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            self.errors.append(f"Invalid YAML: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Error reading file: {e}")
            return False

        if not self.config:
            self.errors.append("Empty configuration file")
            return False

        # Validate structure
        self._validate_structure()
        self._validate_flags()

        return len(self.errors) == 0

    def _validate_structure(self) -> None:
        """Validate overall configuration structure."""
        if "flags" not in self.config:
            self.errors.append("Missing 'flags' section in configuration")
            return

        if not isinstance(self.config["flags"], dict):
            self.errors.append("'flags' section must be a dictionary")
            return

        if len(self.config["flags"]) == 0:
            self.warnings.append("No flags defined in configuration")

    def _validate_flags(self) -> None:
        """Validate individual flags."""
        if "flags" not in self.config:
            return

        for flag_name, flag_config in self.config["flags"].items():
            self._validate_flag(flag_name, flag_config)

    def _validate_flag(self, flag_name: str, flag_config: Dict[str, Any]) -> None:
        """
        Validate individual flag configuration.

        Args:
            flag_name: Name of the flag
            flag_config: Flag configuration dictionary
        """
        prefix = f"Flag '{flag_name}':"

        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in flag_config:
                self.errors.append(f"{prefix} Missing required field '{field}'")

        # Validate flag type
        if "type" in flag_config:
            flag_type = flag_config["type"]
            try:
                FlagType(flag_type)
            except ValueError:
                self.errors.append(
                    f"{prefix} Invalid flag type '{flag_type}'. "
                    f"Must be one of: {[t.value for t in FlagType]}"
                )

        # Validate enabled field
        if "enabled" in flag_config:
            if not isinstance(flag_config["enabled"], bool):
                self.errors.append(f"{prefix} 'enabled' must be a boolean")

        # Validate description
        if "description" in flag_config:
            if not flag_config["description"]:
                self.warnings.append(f"{prefix} Empty description")
            elif len(flag_config["description"]) < 10:
                self.warnings.append(f"{prefix} Description is too short (< 10 chars)")

        # Validate owner
        if "owner" in flag_config:
            owner = flag_config["owner"]
            if not owner:
                self.warnings.append(f"{prefix} Empty owner field")
            elif "@" not in owner:
                self.warnings.append(
                    f"{prefix} Owner should be an email address (contains @)"
                )

        # Validate created_at
        if "created_at" in flag_config:
            created_at = flag_config["created_at"]
            try:
                datetime.fromisoformat(str(created_at))
            except ValueError:
                self.errors.append(
                    f"{prefix} Invalid created_at date format. "
                    "Use ISO format (YYYY-MM-DD)"
                )

        # Type-specific validation
        if "type" in flag_config:
            self._validate_type_specific(flag_name, flag_config)

    def _validate_type_specific(
        self, flag_name: str, flag_config: Dict[str, Any]
    ) -> None:
        """
        Validate type-specific configuration.

        Args:
            flag_name: Name of the flag
            flag_config: Flag configuration dictionary
        """
        prefix = f"Flag '{flag_name}':"
        flag_type = flag_config.get("type")

        if flag_type == "percentage":
            # Validate percentage field
            if "percentage" not in flag_config:
                self.errors.append(f"{prefix} Missing 'percentage' field for percentage flag")
            else:
                percentage = flag_config["percentage"]
                if not isinstance(percentage, int):
                    self.errors.append(f"{prefix} 'percentage' must be an integer")
                elif percentage < 0 or percentage > 100:
                    self.errors.append(
                        f"{prefix} 'percentage' must be between 0 and 100"
                    )

        elif flag_type == "user_targeting":
            # Validate targeting fields
            has_domains = "allowed_domains" in flag_config
            has_hashes = "allowed_user_hashes" in flag_config

            if not has_domains and not has_hashes:
                self.errors.append(
                    f"{prefix} User targeting flag must have "
                    "'allowed_domains' or 'allowed_user_hashes'"
                )

            if has_domains:
                domains = flag_config["allowed_domains"]
                if not isinstance(domains, list):
                    self.errors.append(f"{prefix} 'allowed_domains' must be a list")
                elif len(domains) == 0:
                    self.warnings.append(f"{prefix} Empty 'allowed_domains' list")

            if has_hashes:
                hashes = flag_config["allowed_user_hashes"]
                if not isinstance(hashes, list):
                    self.errors.append(f"{prefix} 'allowed_user_hashes' must be a list")
                elif len(hashes) == 0:
                    self.warnings.append(f"{prefix} Empty 'allowed_user_hashes' list")
                else:
                    # Validate hash format (SHA-256 is 64 hex chars)
                    for hash_val in hashes:
                        if not isinstance(hash_val, str) or len(hash_val) != 64:
                            self.errors.append(
                                f"{prefix} Invalid user hash format. "
                                "Must be 64-character SHA-256 hex string"
                            )

        elif flag_type == "time_based":
            # Validate time fields
            has_enable = "enable_after" in flag_config
            has_disable = "disable_after" in flag_config

            if not has_enable and not has_disable:
                self.errors.append(
                    f"{prefix} Time-based flag must have "
                    "'enable_after' or 'disable_after'"
                )

            if has_enable:
                try:
                    datetime.fromisoformat(
                        flag_config["enable_after"].replace("Z", "+00:00")
                    )
                except ValueError:
                    self.errors.append(
                        f"{prefix} Invalid 'enable_after' format. "
                        "Use ISO format (YYYY-MM-DDTHH:MM:SSZ)"
                    )

            if has_disable:
                try:
                    datetime.fromisoformat(
                        flag_config["disable_after"].replace("Z", "+00:00")
                    )
                except ValueError:
                    self.errors.append(
                        f"{prefix} Invalid 'disable_after' format. "
                        "Use ISO format (YYYY-MM-DDTHH:MM:SSZ)"
                    )

        elif flag_type == "environment":
            # Validate environment field
            if "allowed_environments" not in flag_config:
                self.errors.append(
                    f"{prefix} Missing 'allowed_environments' field for environment flag"
                )
            else:
                envs = flag_config["allowed_environments"]
                if not isinstance(envs, list):
                    self.errors.append(f"{prefix} 'allowed_environments' must be a list")
                elif len(envs) == 0:
                    self.warnings.append(f"{prefix} Empty 'allowed_environments' list")
                else:
                    # Validate environment names
                    valid_envs = ["dev", "staging", "prod", "test"]
                    for env in envs:
                        if env not in valid_envs:
                            self.warnings.append(
                                f"{prefix} Unknown environment '{env}'. "
                                f"Common values: {valid_envs}"
                            )

    def print_results(self) -> None:
        """Print validation results."""
        print(f"\n{'=' * 60}")
        print(f"Feature Flags Validation: {self.config_path}")
        print(f"{'=' * 60}\n")

        if len(self.errors) == 0 and len(self.warnings) == 0:
            print(f"{GREEN}✓ Validation passed!{RESET}")
            print(f"  All flags are valid.")
        else:
            if len(self.errors) > 0:
                print(f"{RED}✗ Validation failed with {len(self.errors)} error(s):{RESET}")
                for error in self.errors:
                    print(f"  {RED}ERROR:{RESET} {error}")
                print()

            if len(self.warnings) > 0:
                print(f"{YELLOW}⚠ {len(self.warnings)} warning(s):{RESET}")
                for warning in self.warnings:
                    print(f"  {YELLOW}WARNING:{RESET} {warning}")
                print()

        # Print summary
        if self.config and "flags" in self.config:
            total_flags = len(self.config["flags"])
            enabled_flags = sum(
                1 for flag in self.config["flags"].values() if flag.get("enabled", False)
            )
            print(f"Summary:")
            print(f"  Total flags: {total_flags}")
            print(f"  Enabled flags: {enabled_flags}")
            print(f"  Disabled flags: {total_flags - enabled_flags}")

        print()


def main() -> int:
    """
    Main entry point.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Get config path from args or use default
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        # Try to find default config
        repo_root = Path(__file__).parent.parent
        config_path = repo_root / "branding" / "features" / "flags.yaml"

    # Validate
    validator = FlagValidator(str(config_path))
    is_valid = validator.validate()
    validator.print_results()

    return 0 if is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
