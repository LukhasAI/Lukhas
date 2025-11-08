import os
import subprocess
from unittest.mock import MagicMock, mock_open, patch

import pytest

from bridge.llm_wrappers.env_loader import (
    get_api_key,
    get_azure_openai_config,
    get_from_keychain,
    get_openai_config,
    load_lukhas_env,
)


# --- Fixtures ---

@pytest.fixture
def clean_environ():
    """Fixture to ensure a clean os.environ for each test."""
    original_environ = os.environ.copy()
    os.environ.clear()
    yield
    os.environ.clear()
    os.environ.update(original_environ)


@pytest.fixture
def mock_env_file(tmp_path):
    """Creates a temporary .env file for testing."""
    env_content = """
# This is a comment
OPENAI_API_KEY=sk-env-openai-key
ANTHROPIC_API_KEY = sk-env-anthropic-key
AZURE_OPENAI_API_KEY=sk-env-azure-key

INVALID_LINE
    """
    env_file = tmp_path / ".env"
    env_file.write_text(env_content)
    return str(env_file)


# --- Tests for load_lukhas_env ---

def test_load_lukhas_env_finds_and_loads_file(clean_environ, mock_env_file):
    """Tests that the function finds a .env file and loads its content."""
    # Patch the list of files to search to *only* include our mock file
    with patch('bridge.llm_wrappers.env_loader.ENV_FILE_PATHS', [mock_env_file]):
        env_vars = load_lukhas_env()

    assert "OPENAI_API_KEY" in env_vars
    assert env_vars["OPENAI_API_KEY"] == "sk-env-openai-key"
    assert "ANTHROPIC_API_KEY" in env_vars
    assert env_vars["ANTHROPIC_API_KEY"] == "sk-env-anthropic-key"
    # Check that os.environ is also populated
    assert os.environ.get("OPENAI_API_KEY") == "sk-env-openai-key"


def test_load_lukhas_env_ignores_comments_and_malformed_lines(clean_environ, mock_env_file):
    """Tests that comments and invalid lines are correctly ignored."""
    with patch('bridge.llm_wrappers.env_loader.ENV_FILE_PATHS', [mock_env_file]):
        env_vars = load_lukhas_env()

    assert "INVALID_LINE" not in env_vars
    assert "# This is a comment" not in "".join(env_vars.keys())


def test_load_lukhas_env_handles_missing_files_gracefully(clean_environ):
    """Tests that the function runs without error when no .env file is found."""
    # Use a fake path that doesn't exist
    with patch('bridge.llm_wrappers.env_loader.ENV_FILE_PATHS', ['/nonexistent/.env']):
        env_vars = load_lukhas_env()
    assert env_vars == {}


def test_load_lukhas_env_file_read_exception(clean_environ):
    """Tests that an exception during file reading is caught and printed."""
    fake_path = '/nonexistent/.env'
    with patch('bridge.llm_wrappers.env_loader.ENV_FILE_PATHS', [fake_path]):
        # Mock exists to be true, so it tries to open the file
        with patch('os.path.exists', return_value=True):
            # Mock open to raise an error
            with patch('builtins.open', side_effect=IOError("Permission denied")):
                # Mock print to capture the output
                with patch('builtins.print') as mock_print:
                    load_lukhas_env()

    mock_print.assert_any_call(f"Warning: Could not load {fake_path}: Permission denied")


# --- Tests for get_from_keychain ---

@patch('subprocess.run')
def test_get_from_keychain_success(mock_subprocess_run):
    """Tests successful retrieval of a key from the keychain."""
    mock_result = MagicMock()
    mock_result.stdout = "sk-keychain-secret-key\n"
    mock_subprocess_run.return_value = mock_result

    key = get_from_keychain("LUKHASAI.TEST_API_KEY")

    mock_subprocess_run.assert_called_once_with(
        ['security', 'find-generic-password', '-s', "LUKHASAI.TEST_API_KEY", '-w'],
        capture_output=True, text=True, check=True
    )
    assert key == "sk-keychain-secret-key"


@patch('subprocess.run')
def test_get_from_keychain_not_found(mock_subprocess_run):
    """Tests handling of a missing entry in the keychain."""
    mock_subprocess_run.side_effect = subprocess.CalledProcessError(1, "security")

    key = get_from_keychain("LUKHASAI.MISSING_KEY")
    assert key is None


@patch('subprocess.run')
def test_get_from_keychain_security_command_not_found(mock_subprocess_run):
    """Tests handling of the 'security' command not being available."""
    mock_subprocess_run.side_effect = FileNotFoundError

    key = get_from_keychain("LUKHASAI.TEST_API_KEY")
    assert key is None


@patch('subprocess.run')
def test_get_from_keychain_generic_exception(mock_subprocess_run, caplog):
    """Tests that a generic exception is caught and logged."""
    mock_subprocess_run.side_effect = Exception("A generic error occurred")

    with caplog.at_level("DEBUG"):
        key = get_from_keychain("LUKHASAI.TEST_API_KEY")

    assert key is None
    assert "Keychain retrieval failed" in caplog.text
    assert "A generic error occurred" in caplog.text


# --- Tests for get_api_key (Priority Logic) ---

@patch('bridge.llm_wrappers.env_loader.get_from_keychain')
@patch('bridge.llm_wrappers.env_loader.load_lukhas_env')
def test_get_api_key_priority_env_over_keychain(mock_load_env, mock_get_keychain, clean_environ):
    """Tests that a valid key in the .env file takes priority over the keychain."""
    os.environ['ANTHROPIC_API_KEY'] = 'sk-env-anthropic-key'
    mock_load_env.return_value = {'ANTHROPIC_API_KEY': 'sk-env-anthropic-key'}
    mock_get_keychain.return_value = 'sk-keychain-anthropic-key'

    api_key = get_api_key('anthropic')

    assert api_key == 'sk-env-anthropic-key'
    mock_get_keychain.assert_not_called()


@patch('bridge.llm_wrappers.env_loader.get_from_keychain')
@patch('bridge.llm_wrappers.env_loader.load_lukhas_env')
def test_get_api_key_falls_back_to_keychain(mock_load_env, mock_get_keychain, clean_environ):
    """Tests that the keychain is used when the .env key is missing or a placeholder."""
    # Scenario 1: Key is not in the environment at all
    mock_load_env.return_value = {}
    mock_get_keychain.return_value = 'sk-keychain-anthropic-key'
    api_key = get_api_key('anthropic')
    assert api_key == 'sk-keychain-anthropic-key'
    mock_get_keychain.assert_called_once_with("LUKHASAI.ANTHROPIC_API_KEY")

    # Scenario 2: Key is a placeholder value
    mock_get_keychain.reset_mock()
    os.environ['ANTHROPIC_API_KEY'] = 'sk-ant-REPLACE_WITH_YOUR_KEY'
    mock_load_env.return_value = {'ANTHROPIC_API_KEY': 'sk-ant-REPLACE_WITH_YOUR_KEY'}
    api_key = get_api_key('anthropic')
    assert api_key == 'sk-keychain-anthropic-key'
    mock_get_keychain.assert_called_once_with("LUKHASAI.ANTHROPIC_API_KEY")


@patch('bridge.llm_wrappers.env_loader.get_from_keychain')
@patch('bridge.llm_wrappers.env_loader.load_lukhas_env')
def test_get_api_key_sets_environ_from_keychain(mock_load_env, mock_get_keychain, clean_environ):
    """Tests that a key retrieved from the keychain is set in the environment."""
    mock_load_env.return_value = {}
    mock_get_keychain.return_value = 'sk-keychain-openai-key'

    assert 'OPENAI_API_KEY' not in os.environ
    api_key = get_api_key('openai')
    assert api_key == 'sk-keychain-openai-key'
    assert os.environ.get('OPENAI_API_KEY') == 'sk-keychain-openai-key'


@patch('bridge.llm_wrappers.env_loader.get_from_keychain')
@patch('bridge.llm_wrappers.env_loader.load_lukhas_env')
def test_get_api_key_returns_none_when_not_found(mock_load_env, mock_get_keychain, clean_environ):
    """Tests that None is returned when the key is in neither .env nor keychain."""
    mock_load_env.return_value = {}
    mock_get_keychain.return_value = None

    api_key = get_api_key('perplexity') # Perplexity is not in keychain mapping

    assert api_key is None
    mock_get_keychain.assert_not_called() # Should not be called for perplexity

    api_key_anthropic = get_api_key('anthropic') # Anthropic is in keychain mapping
    assert api_key_anthropic is None
    mock_get_keychain.assert_called_once() # Should be called for anthropic


@pytest.mark.parametrize("service_name, expected_env_var", [
    ("openai", "OPENAI_API_KEY"),
    ("anthropic", "ANTHROPIC_API_KEY"),
    ("azure", "AZURE_OPENAI_API_KEY"),
    ("gemini", "GOOGLE_API_KEY"),
    ("perplexity", "PERPLEXITY_API_KEY"),
])
def test_get_api_key_service_mappings(service_name, expected_env_var, clean_environ):
    """Tests all service name to environment variable mappings."""
    os.environ[expected_env_var] = f'sk-test-{service_name}-key'
    with patch('bridge.llm_wrappers.env_loader.load_lukhas_env'):
        api_key = get_api_key(service_name)
    assert api_key == f'sk-test-{service_name}-key'


# --- Tests for Config Functions ---

@patch('bridge.llm_wrappers.env_loader.get_api_key')
def test_get_openai_config(mock_get_api_key):
    """Tests that the OpenAI config dictionary is assembled correctly."""
    def side_effect(key):
        return {
            "openai": "sk-openai-test-key",
            "openai_org": "org-test-id",
            "openai_project": "proj-test-id",
        }.get(key)
    mock_get_api_key.side_effect = side_effect

    config = get_openai_config()

    assert config == {
        "api_key": "sk-openai-test-key",
        "org_id": "org-test-id",
        "project_id": "proj-test-id",
    }
    assert mock_get_api_key.call_count == 3


@patch('bridge.llm_wrappers.env_loader.get_api_key')
def test_get_azure_openai_config(mock_get_api_key):
    """Tests that the Azure OpenAI config dictionary is assembled correctly."""
    def side_effect(key):
        return {
            "azure": "sk-azure-test-key",
            "azure_endpoint": "https://test.openai.azure.com/",
            "azure_org": "org-azure-test-id",
            "azure_project": "proj-azure-test-id",
        }.get(key)
    mock_get_api_key.side_effect = side_effect

    config = get_azure_openai_config()

    assert config == {
        "api_key": "sk-azure-test-key",
        "endpoint": "https://test.openai.azure.com/",
        "org_id": "org-azure-test-id",
        "project_id": "proj-azure-test-id",
    }
    assert mock_get_api_key.call_count == 4


@patch('bridge.llm_wrappers.env_loader.get_api_key', return_value=None)
def test_get_openai_config_partial(mock_get_api_key):
    """Tests that the config function handles partially missing values."""
    config = get_openai_config()
    assert config == {
        "api_key": None,
        "org_id": None,
        "project_id": None,
    }
