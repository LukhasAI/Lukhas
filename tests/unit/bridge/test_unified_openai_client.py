from bridge.llm_wrappers import unified_openai_client as client_module


class DummyClient:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


def test_unified_openai_client_prefers_config(monkeypatch):
    dummy_config = type("Cfg", (), {"openai_api_key": "cfg-key", "openai_org_id": "cfg-org"})()
    original_config = client_module._config
    monkeypatch.setattr(client_module, "OpenAI", DummyClient)
    monkeypatch.setattr(client_module, "AsyncOpenAI", DummyClient)
    client_module._config = dummy_config

    try:
        client = client_module.UnifiedOpenAIClient()
    finally:
        client_module._config = original_config

    assert client.api_key == "cfg-key"
    assert client.organization == "cfg-org"
    assert client.client.kwargs["organization"] == "cfg-org"


def test_unified_openai_client_uses_environment_when_config_missing(monkeypatch):
    original_config = client_module._config
    monkeypatch.setattr(client_module, "OpenAI", DummyClient)
    monkeypatch.setattr(client_module, "AsyncOpenAI", DummyClient)
    monkeypatch.setenv("OPENAI_API_KEY", "env-key")
    monkeypatch.setenv("OPENAI_ORG_ID", "env-org")
    client_module._config = None

    try:
        client = client_module.UnifiedOpenAIClient()
    finally:
        client_module._config = original_config

    assert client.api_key == "env-key"
    assert client.organization == "env-org"
    assert client.client.kwargs["organization"] == "env-org"


def test_unified_openai_client_handles_absent_org(monkeypatch):
    original_config = client_module._config
    monkeypatch.setattr(client_module, "OpenAI", DummyClient)
    monkeypatch.setattr(client_module, "AsyncOpenAI", DummyClient)
    monkeypatch.setenv("OPENAI_API_KEY", "env-key")
    monkeypatch.delenv("OPENAI_ORG_ID", raising=False)
    client_module._config = None

    try:
        client = client_module.UnifiedOpenAIClient()
    finally:
        client_module._config = original_config

    assert client.api_key == "env-key"
    assert client.organization is None
    assert "organization" not in client.client.kwargs
