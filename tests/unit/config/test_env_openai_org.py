from config.env import EnvironmentConfig, LUKHASConfig


def test_openai_org_id_from_environment(monkeypatch):
    monkeypatch.setenv("OPENAI_ORG_ID", "org-test")
    config = LUKHASConfig(EnvironmentConfig())

    assert config.openai_org_id == "org-test"


def test_openai_org_id_defaults_to_empty(monkeypatch):
    monkeypatch.delenv("OPENAI_ORG_ID", raising=False)
    config = LUKHASConfig(EnvironmentConfig())

    assert config.openai_org_id == ""
