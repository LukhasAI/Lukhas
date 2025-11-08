#!/usr/bin/env python3
"""
Feature Flags Migration Tool.

Migrates feature flags from old configuration format to new schema.

Usage:
    python tools/migrate_flags.py old_config.yaml new_config.yaml
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import yaml

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# ANSI color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


class FlagMigrator:
    """Migrates feature flags to new schema."""

    def __init__(self, input_path: str, output_path: str):
        """
        Initialize migrator.

        Args:
            input_path: Path to old configuration
            output_path: Path to write new configuration
        """
        self.input_path = input_path
        self.output_path = output_path
        self.old_config: Dict[str, Any] = {}
        self.new_config: Dict[str, Any] = {
            "version": "1.0",
            "flags": {},
            "metadata": {
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "schema_version": "1.0",
                "migrated_from": input_path,
            },
        }

    def migrate(self) -> bool:
        """
        Perform migration.

        Returns:
            True if migration successful, False otherwise
        """
        # Load old config
        try:
            with open(self.input_path, "r") as f:
                self.old_config = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"{RED}Error: Input file not found: {self.input_path}{RESET}")
            return False
        except yaml.YAMLError as e:
            print(f"{RED}Error: Invalid YAML in input file: {e}{RESET}")
            return False
        except Exception as e:
            print(f"{RED}Error reading input file: {e}{RESET}")
            return False

        if not self.old_config:
            print(f"{RED}Error: Empty input configuration{RESET}")
            return False

        # Migrate flags
        self._migrate_flags()

        # Write new config
        try:
            with open(self.output_path, "w") as f:
                yaml.dump(
                    self.new_config,
                    f,
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True,
                )
            print(f"{GREEN}✓ Migration successful!{RESET}")
            print(f"  Output written to: {self.output_path}")
            return True

        except Exception as e:
            print(f"{RED}Error writing output file: {e}{RESET}")
            return False

    def _migrate_flags(self) -> None:
        """Migrate flag configurations."""
        # Handle different input formats
        if "flags" in self.old_config:
            # Already has flags section
            old_flags = self.old_config["flags"]
        else:
            # Assume entire config is flags
            old_flags = self.old_config

        migrated_count = 0
        for flag_name, flag_config in old_flags.items():
            migrated_flag = self._migrate_flag(flag_name, flag_config)
            if migrated_flag:
                self.new_config["flags"][flag_name] = migrated_flag
                migrated_count += 1

        self.new_config["metadata"]["total_flags"] = migrated_count
        print(f"{BLUE}Migrated {migrated_count} flag(s){RESET}")

    def _migrate_flag(
        self, flag_name: str, flag_config: Any
    ) -> Dict[str, Any]:
        """
        Migrate individual flag configuration.

        Args:
            flag_name: Name of the flag
            flag_config: Old flag configuration

        Returns:
            New flag configuration
        """
        # Handle simple boolean flags (just true/false)
        if isinstance(flag_config, bool):
            return {
                "type": "boolean",
                "enabled": flag_config,
                "description": f"Migrated flag: {flag_name}",
                "owner": "team@lukhas.ai",
                "created_at": datetime.now().strftime("%Y-%m-%d"),
                "jira_ticket": "MIGRATED",
                "fallback": False,
            }

        # Handle dictionary configs
        if not isinstance(flag_config, dict):
            print(
                f"{YELLOW}Warning: Skipping flag '{flag_name}' "
                f"with unsupported type: {type(flag_config)}{RESET}"
            )
            return {}

        # Build new config with defaults
        new_flag: Dict[str, Any] = {
            "type": flag_config.get("type", "boolean"),
            "enabled": flag_config.get("enabled", False),
            "description": flag_config.get(
                "description", f"Migrated flag: {flag_name}"
            ),
            "owner": flag_config.get("owner", "team@lukhas.ai"),
            "created_at": flag_config.get(
                "created_at", datetime.now().strftime("%Y-%m-%d")
            ),
            "jira_ticket": flag_config.get("jira_ticket", "MIGRATED"),
            "fallback": flag_config.get("fallback", False),
        }

        # Migrate type-specific fields
        flag_type = new_flag["type"]

        if flag_type == "percentage":
            new_flag["percentage"] = flag_config.get("percentage", 0)

        elif flag_type == "user_targeting":
            if "allowed_domains" in flag_config:
                new_flag["allowed_domains"] = flag_config["allowed_domains"]
            if "allowed_user_hashes" in flag_config:
                new_flag["allowed_user_hashes"] = flag_config["allowed_user_hashes"]

        elif flag_type == "time_based":
            if "enable_after" in flag_config:
                new_flag["enable_after"] = flag_config["enable_after"]
            if "disable_after" in flag_config:
                new_flag["disable_after"] = flag_config["disable_after"]

        elif flag_type == "environment":
            if "allowed_environments" in flag_config:
                new_flag["allowed_environments"] = flag_config["allowed_environments"]

        return new_flag


def main() -> int:
    """
    Main entry point.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(
        description="Migrate feature flags to new schema"
    )
    parser.add_argument(
        "input",
        help="Path to old configuration file",
    )
    parser.add_argument(
        "output",
        help="Path to write new configuration file",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite output file if it exists",
    )

    args = parser.parse_args()

    # Check if output file exists
    if Path(args.output).exists() and not args.force:
        print(
            f"{RED}Error: Output file already exists: {args.output}{RESET}"
        )
        print(f"Use --force to overwrite")
        return 1

    # Perform migration
    migrator = FlagMigrator(args.input, args.output)
    success = migrator.migrate()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
