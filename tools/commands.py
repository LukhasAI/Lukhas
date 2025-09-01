"""
Tools Command Infrastructure
============================
Base infrastructure for LUKHAS AI development commands and workflows.
Provides a foundation for CLI tools, scripts, and automation workflows.
"""

import argparse
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from .utils import get_git_status, get_logger, get_system_info


class BaseCommand(ABC):
    """Base class for all LUKHAS development commands"""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.logger = get_logger(f"cmd.{name}")

    @abstractmethod
    def execute(self, args: argparse.Namespace) -> int:
        """Execute the command. Return 0 for success, non-zero for error."""

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Setup command-specific arguments. Override in subclasses."""

    def validate_args(self, args: argparse.Namespace) -> bool:
        """Validate command arguments. Override in subclasses."""
        return True

    def run(self, argv: Optional[list[str]] = None) -> int:
        """Run the command with argument parsing"""
        parser = argparse.ArgumentParser(prog=self.name, description=self.description)

        # Common arguments
        parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be done without executing",
        )

        # Command-specific arguments
        self.setup_parser(parser)

        try:
            args = parser.parse_args(argv)

            if args.verbose:
                import logging

                logging.getLogger("tools").setLevel(logging.DEBUG)

            if not self.validate_args(args):
                return 1

            return self.execute(args)

        except KeyboardInterrupt:
            self.logger.info("Command interrupted by user")
            return 130
        except Exception as e:
            self.logger.error(f"Command failed: {e}")
            if args.verbose if "args" in locals() else False:
                import traceback

                traceback.print_exc()
            return 1


class GitCommand(BaseCommand):
    """Base class for Git-related commands"""

    def __init__(self, name: str, description: str = ""):
        super().__init__(name, description)
        self.git_status = None

    def validate_args(self, args: argparse.Namespace) -> bool:
        """Validate Git repository state"""
        self.git_status = get_git_status()
        if self.git_status is None:
            self.logger.error("Not in a Git repository or Git not available")
            return False
        return super().validate_args(args)

    def is_clean(self) -> bool:
        """Check if working directory is clean"""
        return self.git_status.get("clean", False) if self.git_status else False

    def get_modified_files(self) -> list[str]:
        """Get list of modified files"""
        return self.git_status.get("modified", []) if self.git_status else []


class TestCommand(BaseCommand):
    """Base class for test-related commands"""

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--coverage", action="store_true", help="Include coverage reporting")
        parser.add_argument(
            "--pattern",
            "-p",
            type=str,
            default="test_*.py",
            help="Test file pattern (default: test_*.py)",
        )
        parser.add_argument(
            "--path",
            type=Path,
            default=Path("tests"),
            help="Test directory path (default: tests)",
        )


class LintCommand(BaseCommand):
    """Base class for linting commands"""

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--fix", action="store_true", help="Automatically fix issues where possible")
        parser.add_argument("--config", type=Path, help="Path to configuration file")


class CommandRegistry:
    """Registry for managing development commands"""

    def __init__(self):
        self.commands: dict[str, BaseCommand] = {}
        self.logger = get_logger("registry")

    def register(self, command: BaseCommand) -> None:
        """Register a command"""
        if command.name in self.commands:
            self.logger.warning(f"Overriding existing command: {command.name}")

        self.commands[command.name] = command
        self.logger.debug(f"Registered command: {command.name}")

    def get_command(self, name: str) -> Optional[BaseCommand]:
        """Get a command by name"""
        return self.commands.get(name)

    def list_commands(self) -> list[str]:
        """Get list of registered command names"""
        return list(self.commands.keys())

    def execute_command(self, name: str, argv: Optional[list[str]] = None) -> int:
        """Execute a command by name"""
        command = self.get_command(name)
        if not command:
            self.logger.error(f"Unknown command: {name}")
            return 1

        return command.run(argv)


# Global command registry
_registry = CommandRegistry()


def register_command(command: BaseCommand) -> None:
    """Register a command in the global registry"""
    _registry.register(command)


def get_command(name: str) -> Optional[BaseCommand]:
    """Get a command from the global registry"""
    return _registry.get_command(name)


def list_commands() -> list[str]:
    """List all registered commands"""
    return _registry.list_commands()


def execute_command(name: str, argv: Optional[list[str]] = None) -> int:
    """Execute a command from the global registry"""
    return _registry.execute_command(name, argv)


# Built-in commands


class StatusCommand(BaseCommand):
    """Show system and repository status"""

    def __init__(self):
        super().__init__("status", "Show LUKHAS system and Git status")

    def execute(self, args: argparse.Namespace) -> int:
        print("🔍 LUKHAS AI System Status")
        print("=" * 50)

        # System info
        system_info = get_system_info()
        print(f"Python: {system_info['python_version'].split()[0]}")
        print(f"Platform: {system_info['platform']}")
        print(f"Working Dir: {system_info['working_directory']}")

        # Git status
        git_status = get_git_status()
        if git_status:
            print(f"\nGit Branch: {git_status['branch']}")

            if git_status["clean"]:
                print("Status: ✅ Clean working directory")
            else:
                print("Status: ⚠️  Changes detected")
                if git_status["modified"]:
                    print(f"  Modified: {len(git_status['modified'])} files")
                if git_status["untracked"]:
                    print(f"  Untracked: {len(git_status['untracked'])} files")
                if git_status["staged"]:
                    print(f"  Staged: {len(git_status['staged'])} files")
        else:
            print("\nGit: Not available or not in repository")

        return 0


class ListCommand(BaseCommand):
    """List available commands"""

    def __init__(self):
        super().__init__("list", "List all available commands")

    def execute(self, args: argparse.Namespace) -> int:
        print("🛠️  Available LUKHAS Commands")
        print("=" * 50)

        for name in sorted(list_commands()):
            command = get_command(name)
            if command:
                print(f"  {name:<20} {command.description}")

        return 0


# Register built-in commands
register_command(StatusCommand())
register_command(ListCommand())


def main():
    """Main entry point for command line interface"""
    if len(sys.argv) < 2:
        print("Usage: python -m tools.commands <command> [args...]")
        print("\nAvailable commands:")
        execute_command("list")
        return 1

    command_name = sys.argv[1]
    command_args = sys.argv[2:] if len(sys.argv) > 2 else None

    return execute_command(command_name, command_args)


if __name__ == "__main__":
    sys.exit(main())
