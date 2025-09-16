from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.ci.build_manifest import TodoManifestBuilder
from tools.ci.lock_batches import BatchLocker
from tools.ci.split_batches import BatchSplitter


def test_extract_todo_text_handles_language_block():
    section = (
        "**File**: `candidate/core/module.py`\n"
        "**TODO Text:** ```python\nImplement deterministic control\n```"
    )
    builder = TodoManifestBuilder()
    assert builder._extract_todo_text(section) == "Implement deterministic control"


def test_generate_task_id_sanitizes_module():
    builder = TodoManifestBuilder()
    task_id = builder._generate_task_id("high", "candidate/core/module.py", "Add features")
    parts = task_id.split("-")
    assert parts[0] == "TODO"
    assert parts[1] == "HIGH"
    assert parts[2] == "CANDIDATE"
    assert parts[-1].isalnum() and len(parts[-1]) == 8


def test_cross_check_codebase_deduplicates(tmp_path: Path):
    grep_file = tmp_path / "grep.txt"
    grep_file.write_text("./candidate/core/module.py:10: TODO refine logic\n")
    builder = TodoManifestBuilder()
    todos = [
        {
            "task_id": "TODO-HIGH-CANDIDATE-CORE-12345678",
            "priority": "high",
            "title": "Refine logic",
            "file": "./candidate/core/module.py",
            "line_hint": 10,
            "module": "candidate/core",
            "trinity": "Identity",
            "status": "open",
            "source": "med_todos.md",
            "evidence": {"grep": None, "last_commit": None},
            "acceptance": [],
            "risk": "med",
            "est": {"type": "logic", "size": "S"},
        }
    ]
    result = builder.cross_check_codebase(str(grep_file), todos)
    assert len(result) == 1
    assert result[0]["evidence"]["grep"].endswith("TODO refine logic")


def test_validate_task_id_enforces_format():
    locker = BatchLocker()
    assert locker._validate_task_id("TODO-HIGH-CANDIDATE-1234abcd")
    assert not locker._validate_task_id("TODO-HIGH-candidate-1234abcd")
    assert not locker._validate_task_id("TODO-HIGH-CANDIDATE-1234abcz")


def test_splitter_loads_strategy(tmp_path: Path):
    strategy_file = tmp_path / "strategy.yaml"
    strategy_file.write_text(
        "agent_capabilities:\n  jules01:\n    types: [logic]\n    max_batch: 5\n    priorities: [high]\n"
    )
    splitter = BatchSplitter(str(strategy_file))
    assert splitter.strategy["agent_capabilities"]["jules01"]["max_batch"] == 5
