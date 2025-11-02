"""Tests for API vault path configuration handling."""

import sys
from importlib import util
from pathlib import Path
from types import ModuleType

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENV_MODULE_PATH = PROJECT_ROOT / "config" / "env.py"


# ΛTAG: config_test
def _load_env_module() -> ModuleType:
    """Load the config.env module directly from its file path."""

    spec = util.spec_from_file_location("config.env", ENV_MODULE_PATH)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive guard
        raise ImportError("Unable to load config.env module specification")

    module = util.module_from_spec(spec)
    sys.modules.setdefault("config.env", module)
    parent_module = sys.modules.setdefault("config", ModuleType("config"))
    setattr(parent_module, "env", module)
    spec.loader.exec_module(module)
    return module


env_module = _load_env_module()

# ΛTAG: config_test


def _reset_env_config_cache(monkeypatch) -> None:
    """Reset cached environment configuration for deterministic tests."""
    monkeypatch.setattr(env_module, "_config_instance", None, raising=False)


def test_api_vault_path_defaults_to_repo_directory(monkeypatch) -> None:
    """Default path should resolve to the repository var/api_vault directory."""
    monkeypatch.delenv("LUKHAS_API_VAULT_PATH", raising=False)
    _reset_env_config_cache(monkeypatch)

    config = env_module.get_lukhas_config()

    assert config.api_vault_path == (PROJECT_ROOT / "var" / "api_vault")


def test_api_vault_path_respects_environment_override(monkeypatch, tmp_path) -> None:
    """Environment variable should override the default API vault location."""
    desired_path = tmp_path / "secure" / "vault"
    monkeypatch.setenv("LUKHAS_API_VAULT_PATH", str(desired_path))
    _reset_env_config_cache(monkeypatch)

    config = env_module.get_lukhas_config()

    assert config.api_vault_path == desired_path
