import candidate.bridge.api.ai_interface as ai_interface


def test_ai_interface_structured_success(monkeypatch):
    # Make router available and provide a dummy multiverse_route
    monkeypatch.setattr(ai_interface, "ROUTER_AVAILABLE", True, raising=False)
    monkeypatch.setattr(
        ai_interface,
        "multiverse_route",
        lambda task, task_type, debug: {"output": f"ok:{task_type}"},
        raising=False,
    )

    ai = ai_interface.LukhusAI("TestComponent")
    res = ai.generate_response("ping", ai_interface.LukhusAITaskType.GENERAL, structured=True)
    assert isinstance(res, dict)
    assert res["success"] is True
    assert res["output"].startswith("ok:")
    assert res["meta"]["task_type"] == ai_interface.LukhusAITaskType.GENERAL.value


def test_ai_interface_structured_router_unavailable(monkeypatch):
    # Simulate unavailable router
    monkeypatch.setattr(ai_interface, "ROUTER_AVAILABLE", False, raising=False)
    monkeypatch.setattr(ai_interface, "multiverse_route", None, raising=False)

    ai = ai_interface.LukhusAI("TestComponent")
    res = ai.generate_response("ping", ai_interface.LukhusAITaskType.GENERAL, structured=True)
    assert isinstance(res, dict)
    assert res["success"] is False
    assert "not available" in res["error"].lower()


def test_ai_interface_audit_log_written(monkeypatch, tmp_path):
    # Configure audit log path
    log_path = tmp_path / "ai_interface_audit.log"
    monkeypatch.setenv("LUKHAS_AI_AUDIT_LOG_PATH", str(log_path))
    # Mock router
    monkeypatch.setattr(ai_interface, "ROUTER_AVAILABLE", True, raising=False)
    monkeypatch.setattr(
        ai_interface,
        "multiverse_route",
        lambda task, task_type, debug: {"output": f"ok:{task_type}"},
        raising=False,
    )
    ai = ai_interface.LukhusAI("AuditComponent")
    res = ai.generate_response("ping", ai_interface.LukhusAITaskType.GENERAL, structured=True)
    assert res["success"] is True
    # Verify a line is written
    assert log_path.exists()
    lines = log_path.read_text().strip().splitlines()
    assert any("AuditComponent" in line for line in lines)
