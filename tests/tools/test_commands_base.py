"""Tests for the lightweight command framework abstractions."""

from __future__ import annotations

import pytest
from tools.commands.base import BaseCommand, CommandExecutionError
from typing import List


class _RecorderCommand(BaseCommand):
    """Simple command used to assert dispatch behaviour in tests."""

    def __init__(self) -> None:
        super().__init__(name="recorder", description="Test command")
        self.invocations: List[List[str]] = []

    async def execute(self, args: List[str]) -> bool:
        self.invocations.append(list(args))
        return True


@pytest.mark.asyncio()
async def test_dispatch_to_registered_subcommand() -> None:
    command = _RecorderCommand()
    captured: List[List[str]] = []

    def _echo(args: List[str]) -> bool:
        captured.append(args)
        return True

    command.register_subcommand("echo", _echo)

    assert await command.dispatch(["echo", "payload"]) is True
    assert captured == [["payload"]]
    assert command.invocations == []


@pytest.mark.asyncio()
async def test_dispatch_falls_back_to_execute() -> None:
    command = _RecorderCommand()

    assert await command.dispatch(["unknown", "arg"]) is True
    assert command.invocations == [["unknown", "arg"]]


@pytest.mark.asyncio()
async def test_run_wraps_exceptions() -> None:
    class _BrokenCommand(BaseCommand):
        async def execute(self, args: List[str]) -> bool:  # pragma: no cover - exercised in test
            raise RuntimeError("boom")

    broken = _BrokenCommand()

    with pytest.raises(CommandExecutionError):
        await broken.run([])
