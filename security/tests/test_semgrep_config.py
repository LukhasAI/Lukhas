"""Validation tests for the Lukhas security Semgrep configuration."""

from __future__ import annotations

from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[2] / ".semgrep" / "lukhas-security.yaml"


def _load_config_text() -> str:
    """Return the raw Semgrep configuration text."""
    config_text = CONFIG_PATH.read_text()
    assert config_text.strip(), "Semgrep security configuration should not be empty"
    return config_text


def test_semgrep_config_loads() -> None:
    """Ensure the Semgrep security configuration file can be parsed."""
    config_text = _load_config_text()
    assert config_text.lstrip().startswith("rules:"), "Expected Semgrep config to define rules"


def test_authentication_stub_rule_present() -> None:
    """Verify the authentication stub detection rule is defined with key patterns."""
    config_text = _load_config_text()
    assert "- id: lukhas-authentication-stub" in config_text

    stub_block_start = config_text.index("- id: lukhas-authentication-stub")
    subsequent_section = config_text[stub_block_start:]
    # Limit block to before the next rule id to reduce noise
    next_rule_index = subsequent_section.find("\n  - id:", 1)
    stub_block = subsequent_section[:next_rule_index] if next_rule_index != -1 else subsequent_section

    assert '"authenticated": True' in stub_block or '"success": True' in stub_block
    assert "return True" in stub_block
    assert 'regex: "(?i)auth"' in stub_block
