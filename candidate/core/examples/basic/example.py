#!/usr/bin/env python3
"""Demonstration entry-point for the LUKHAS task manager."""

from __future__ import annotations

import asyncio
from pathlib import Path

from candidate.core.task_manager import LukhλsTaskManager, TaskPriority


async def _run_symbol_validation_example() -> None:
    """Execute a small end-to-end task using the task manager."""

    manager = LukhλsTaskManager()
    sample_doc = Path("/tmp/lukhas_symbol_demo.txt")
    sample_doc.write_text("#ΛTAG:demo\n#INVALID-symbol\n#VALID_SYMBOL", encoding="utf-8")

    try:
        task_id = manager.create_task(
            name="Demo Symbol Validation",
            description="Validate inline ΛTAG annotations",
            handler="symbol_validation",
            parameters={"document": sample_doc.read_text(encoding="utf-8")},
            priority=TaskPriority.HIGH,
        )

        await manager.execute_task(task_id)
        task = manager.tasks[task_id]
        print(f"Task Result → {task.result}")
    finally:
        sample_doc.unlink(missing_ok=True)


def main() -> None:
    """Run the asynchronous demo synchronously for CLI usage."""

    asyncio.run(_run_symbol_validation_example())


if __name__ == "__main__":
    main()
