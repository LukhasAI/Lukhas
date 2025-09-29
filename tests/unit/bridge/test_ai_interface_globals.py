import lukhas.bridge.api.ai_interface as ai_interface


def test_global_ai_code_structured(monkeypatch):
    monkeypatch.setattr(ai_interface, "ROUTER_AVAILABLE", True, raising=False)
    monkeypatch.setattr(
        ai_interface,
        "multiverse_route",
        lambda task, task_type, debug: {"output": f"unit:{task_type}"},
        raising=False,
    )

    res = ai_interface.ai_code("sum two numbers", language="python", structured=True)
    assert isinstance(res, dict)
    assert res["success"] is True
    assert res["output"].startswith("unit:")


def test_global_ai_chat_unavailable_structured(monkeypatch):
    monkeypatch.setattr(ai_interface, "ROUTER_AVAILABLE", False, raising=False)
    monkeypatch.setattr(ai_interface, "multiverse_route", None, raising=False)
    res = ai_interface.ai_chat("hello", structured=True)
    assert isinstance(res, dict)
    assert res["success"] is False
    assert "not available" in res["error"].lower()


def test_global_ai_audit_docs_research_structured(monkeypatch):
    monkeypatch.setattr(ai_interface, "ROUTER_AVAILABLE", True, raising=False)
    monkeypatch.setattr(
        ai_interface,
        "multiverse_route",
        lambda task, task_type, debug: {"output": f"ok:{task_type}"},
        raising=False,
    )
    out_audit = ai_interface.ai_audit("audit-this", structured=True)
    assert out_audit["success"] and out_audit["output"].startswith("ok:")
    out_docs = ai_interface.ai_docs("docs-this", structured=True)
    assert out_docs["success"] and out_docs["output"].startswith("ok:")
    out_research = ai_interface.ai_research("research-this", structured=True)
    assert out_research["success"] and out_research["output"].startswith("ok:")
