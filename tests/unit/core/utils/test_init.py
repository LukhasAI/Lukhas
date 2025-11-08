import pytest

from core.utils import generate_symbolic_id, legacy_parse_lukhas_command


def test_generate_symbolic_id():
    """Tests that a unique symbolic ID is generated with the correct prefix."""
    prefix = "test_"
    symbolic_id = generate_symbolic_id(prefix)
    assert symbolic_id.startswith(prefix)
    assert len(symbolic_id) > len(prefix)


def test_legacy_parse_lukhas_command_valid():
    """Tests parsing a valid legacy command string."""
    command_string = "CMD:DO_ACTION PARAMS:{'key': 'value', 'num': 123}"
    parsed = legacy_parse_lukhas_command(command_string)
    assert parsed is not None
    assert parsed["command"] == "DO_ACTION"
    assert parsed["params"] == {"key": "value", "num": 123}


def test_legacy_parse_lukhas_command_invalid():
    """Tests that an invalid command string returns None."""
    assert legacy_parse_lukhas_command("INVALID_COMMAND") is None
    assert legacy_parse_lukhas_command("") is None


def test_legacy_parse_lukhas_command_malformed_params():
    """Tests a command with malformed parameters."""
    command_string = "CMD:BAD_PARAMS PARAMS:{'key': 'value'"
    parsed = legacy_parse_lukhas_command(command_string)
    assert parsed is not None
    assert parsed["command"] == "BAD_PARAMS"
    assert parsed["params"] == {"error": "param_parse_failed"}
