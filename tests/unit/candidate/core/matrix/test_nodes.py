"""Unit tests for MATRIZ cognitive nodes."""
import importlib.util
import os
import sys
import types

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
NODES_PATH = os.path.join(PROJECT_ROOT, "labs", "core", "matriz", "nodes")

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

PACKAGE_PREFIX = "lukhas_candidate"


def _ensure_package(name: str, path: str | None = None) -> types.ModuleType:
    module = sys.modules.get(name)
    if module is None:
        module = types.ModuleType(name)
        if path is not None:
            module.__path__ = [path]
        sys.modules[name] = module
    else:
        if path is not None:
            module.__path__ = [path]
    return module


_ensure_package(PACKAGE_PREFIX)
_ensure_package(f"{PACKAGE_PREFIX}.core")
_ensure_package(f"{PACKAGE_PREFIX}.core.matriz")
_ensure_package(f"{PACKAGE_PREFIX}.core.matriz.nodes", NODES_PATH)


def _load_module(module_name: str, file_name: str, is_package: bool = False):
    module_path = os.path.join(NODES_PATH, file_name)
    if is_package:
        spec = importlib.util.spec_from_file_location(module_name, module_path, submodule_search_locations=[NODES_PATH])
    else:
        spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec and spec.loader, f"Unable to load spec for {module_name}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


_nodes_pkg = _load_module(f"{PACKAGE_PREFIX}.core.matriz.nodes", "__init__.py", is_package=True)
MemoryNode = _nodes_pkg.MemoryNode
ThoughtNode = _nodes_pkg.ThoughtNode
DecisionNode = _nodes_pkg.DecisionNode


def test_memory_node_returns_matches():
    node = MemoryNode()
    input_data = {
        "query": "user profile",
        "memory_context": [
            {"id": "m1", "content": "User profile updated", "importance": 0.9, "recency": 0.8},
            {"id": "m2", "content": "System maintenance log", "importance": 0.2, "recency": 0.4},
        ],
    }

    result = node.process(input_data)

    assert result["answer"]["matches"], "Memory node should return at least one match"
    assert node.validate_output(result)
    assert result["matriz_node"]["state"]["confidence"] > 0


def test_thought_node_synthesizes_summary():
    node = ThoughtNode()
    memories = [
        {"id": "m1", "content": "User profile updated", "importance": 0.9},
        {"id": "m2", "content": "User requested email change", "importance": 0.7},
    ]

    result = node.process({"query": "user profile", "recall_matches": memories})

    assert "summary" in result["answer"]
    assert result["affect_delta"] >= 0
    assert node.validate_output(result)


def test_decision_node_selects_best_action():
    node = DecisionNode()
    actions = [
        {"name": "log_only", "score": 0.5, "risk": 0.1},
        {"name": "notify_team", "score": 0.8, "risk": 0.3},
    ]

    result = node.process({"candidate_actions": actions, "urgency": 0.6})

    assert result["answer"]["name"] == "notify_team"
    assert node.validate_output(result)
