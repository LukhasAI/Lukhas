"""Command framework primitives used by developer tooling."""

from __future__ import annotations

import asyncio
import logging
from typing import Awaitable, Callable, Dict, Iterable, Union

CommandHandler = Callable[[list[str]], Union[Awaitable[bool], bool]]

__all__ = ["BaseCommand", "CommandExecutionError", "CommandHandler"]


class CommandExecutionError(RuntimeError):
    """Raised when a command handler reports a failure."""


class BaseCommand:
    """Minimal asynchronous command harness for developer utilities."""

    def __init__(self, name: str | None = None, description: str | None = None) -> None:
        self.name = name or self.__class__.__name__.lower()
        self.description = (description or (self.__doc__ or "")).strip()
        self.logger = logging.getLogger(f"tools.commands.{self.name}")
        self.subcommands: Dict[str, CommandHandler] = {}

    async def execute(self, args: list[str]) -> bool:  # pragma: no cover - interface contract
        """Execute the command. Subclasses must override this."""

        raise NotImplementedError("BaseCommand.execute must be implemented by subclasses")

    # ΛTAG: command_dispatch
    async def dispatch(self, args: list[str]) -> bool:
        """Dispatch to a registered subcommand when available."""

        if not args:
            return await self.execute([])

        command = args[0]
        if command in self.subcommands:
            handler = self.subcommands[command]
            self.logger.debug("Dispatching subcommand '%s' with args=%s", command, args[1:])
            return await self._invoke(handler, args[1:])

        self.logger.debug("No subcommand match for '%s'; using primary executor", command)
        return await self.execute(args)

    def register_subcommand(self, name: str, handler: CommandHandler) -> None:
        """Register a subcommand handler."""

        if not name:
            raise ValueError("Subcommand name must be provided")
        self.subcommands[name] = handler

    def unregister_subcommand(self, name: str) -> None:
        """Remove a previously registered subcommand if it exists."""

        self.subcommands.pop(name, None)

    def list_subcommands(self) -> Iterable[str]:
        """Return the names of registered subcommands."""

        return tuple(self.subcommands.keys())

    async def run(self, args: list[str]) -> bool:
        """Public entry point that wraps :meth:`dispatch` with error handling."""

        try:
            return await self.dispatch(args)
        except CommandExecutionError:
            raise
        except Exception as exc:  # pragma: no cover - defensive logging path
            self.logger.error("Command '%s' failed: %s", self.name, exc, exc_info=True)
            raise CommandExecutionError(str(exc)) from exc

    async def _invoke(self, handler: CommandHandler, args: list[str]) -> bool:
        """Invoke a handler, awaiting coroutine results when necessary."""

        result = handler(args)
        if asyncio.iscoroutine(result):
            result = await result  # type: ignore[assignment]
        return bool(result)
