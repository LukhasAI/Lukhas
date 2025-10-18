import asyncio
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

for module_name in ["labs", "labs.core", "labs.core.task_manager"]:
    sys.modules.pop(module_name, None)

from labs.core.task_manager import LukhλsTaskManager, TaskPriority  # noqa: E402


@pytest.mark.asyncio
async def test_symbol_validation_handler(tmp_path: Path) -> None:
    manager = LukhλsTaskManager(config_path=str(tmp_path / "missing_config.json"))

    task_id = manager.create_task(
        name="validate symbols",
        description="ensure glyph tags",
        handler="symbol_validation",
        parameters={"symbols": ["VALID_SYMBOL", "bad-symbol", "#GLYPH"]},
        priority=TaskPriority.HIGH,
    )

    await manager.execute_task(task_id)
    result = manager.tasks[task_id].result

    assert "VALID_SYMBOL" in result["valid_symbols"]
    assert "bad-symbol" in result["invalid_symbols"]
    assert result["driftScore"] < 1.0


@pytest.mark.asyncio
async def test_design_and_file_handlers(tmp_path: Path) -> None:
    design_root = tmp_path / "design-system"
    design_root.mkdir()
    (design_root / "tokens.json").write_text("{}", encoding="utf-8")
    (design_root / "palette.yaml").write_text("primary: blue", encoding="utf-8")

    data_file = tmp_path / "data.bin"
    data_file.write_bytes(b"lukh\x00s")

    manager = LukhλsTaskManager(config_path=str(tmp_path / "missing.json"))

    design_task = manager.create_task(
        name="design sweep",
        description="scan design assets",
        handler="design_system",
        parameters={"design_root": str(design_root)},
    )

    file_task = manager.create_task(
        name="file sweep",
        description="process attachments",
        handler="file_processing",
        parameters={"paths": [str(data_file)]},
    )

    await asyncio.gather(manager.execute_task(design_task), manager.execute_task(file_task))

    design_result = manager.tasks[design_task].result
    file_result = manager.tasks[file_task].result

    assert design_result["asset_counts"]["json"] == 1
    assert design_result["asset_counts"]["yaml"] == 1
    assert file_result["processed"][0]["exists"] is True
    assert file_result["total_size"] == data_file.stat().st_size
