import sys
from pathlib import Path

from lukhas.bridge.api.direct_ai_router import DirectAIRouter


def _write_dummy_router(tmp_path: Path, returns_dict: bool = True):
    pkg_dir = tmp_path / "router"
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "__init__.py").write_text("")
    code = (
        "def multiverse_route(task, task_type, debug):\n"
        "    if debug:\n"
        "        # include some debug behavior\n"
        "        pass\n"
        + (
            "    return {'output': f'echo:{task} [{task_type}]'}\n"
            if returns_dict
            else "    return f'echo_str:{task} [{task_type}]'\n"
        )
    )
    (pkg_dir / "llm_multiverse_router.py").write_text(code)


def test_route_request_import_error_in_child(tmp_path, monkeypatch):
    # No router package at the path -> ImportError in child; ensure stderr propagates
    monkeypatch.setenv("LUKHAS_AI_ROUTER_PATH", str(tmp_path))
    monkeypatch.setenv("LUKHAS_PYTHON_PATH", sys.executable)
    router = DirectAIRouter()
    res = router.route_request("hello", structured=True)
    assert isinstance(res, dict)
    assert res["success"] is False
    assert "Router execution error" in res["error"]
    # stderr contains our message
    assert "Failed to import 'multiverse_route'" in res["error"] or res["stderr"]


def test_route_request_runtime_exception_in_child(tmp_path, monkeypatch):
    # Create a router that raises
    pkg_dir = tmp_path / "router"
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "__init__.py").write_text("")
    (pkg_dir / "llm_multiverse_router.py").write_text(
        "def multiverse_route(task, task_type, debug):\n" "    raise RuntimeError('boom')\n"
    )
    monkeypatch.setenv("LUKHAS_AI_ROUTER_PATH", str(tmp_path))
    monkeypatch.setenv("LUKHAS_PYTHON_PATH", sys.executable)
    router = DirectAIRouter()
    res = router.route_request("hello", structured=True)
    assert isinstance(res, dict)
    assert res["success"] is False
    assert "Router execution error" in res["error"]
    assert "boom" in res["error"] or res["stderr"]


def test_route_request_structured_success_with_temp_router(tmp_path, monkeypatch):
    _write_dummy_router(tmp_path, returns_dict=True)
    # Point router path and python to current interpreter
    monkeypatch.setenv("LUKHAS_AI_ROUTER_PATH", str(tmp_path))
    monkeypatch.setenv("LUKHAS_PYTHON_PATH", sys.executable)

    router = DirectAIRouter()
    res = router.route_request("hello", task_type="general", debug=False, structured=True)
    assert isinstance(res, dict)
    assert res["success"] is True
    assert "echo:" in res["output"]
    assert res["return_code"] == 0
    assert res["meta"]["task_type"] == "general"


def test_route_request_structured_file_not_found(monkeypatch):
    # Force an invalid python interpreter to simulate environment errors
    monkeypatch.setenv("LUKHAS_AI_ROUTER_PATH", str(Path.cwd()))
    monkeypatch.setenv("LUKHAS_PYTHON_PATH", "/non/existent/python-bin")
    router = DirectAIRouter()
    res = router.route_request("hi", structured=True)
    assert isinstance(res, dict)
    assert res["success"] is False
    assert "Python interpreter" in res["error"]
    assert res["return_code"] == -2


def test_route_request_unexpected_type_marked_as_error(tmp_path, monkeypatch):
    # Router returns an unexpected type -> child prints Router Error with exit 0
    pkg_dir = tmp_path / "router"
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "__init__.py").write_text("")
    (pkg_dir / "llm_multiverse_router.py").write_text(
        "def multiverse_route(task, task_type, debug):\n" "    return 123\n"
    )
    monkeypatch.setenv("LUKHAS_AI_ROUTER_PATH", str(tmp_path))
    monkeypatch.setenv("LUKHAS_PYTHON_PATH", sys.executable)
    router = DirectAIRouter()
    res = router.route_request("hello", task_type="general", structured=True)
    assert isinstance(res, dict)
    assert res["success"] is False
    # Non-zero return code from child process
    assert res["return_code"] != 0
    assert "Router execution error" in (res["error"] or "")
