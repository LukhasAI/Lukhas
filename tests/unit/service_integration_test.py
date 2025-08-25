import pytest
import os
import sys

# Add the root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from candidate.bridge.llm_wrappers.unified_openai_client import UnifiedOpenAIClient

def test_unified_openai_client_config_integration():
    """
    Tests that the UnifiedOpenAIClient correctly integrates with constructor-based configuration.
    """
    client = UnifiedOpenAIClient(
        api_key="test_api_key",
        organization="test_org_id",
        project="test_project_id"
    )

    assert client.api_key == "test_api_key"
    assert client.organization == "test_org_id"
    assert client.project == "test_project_id"

    # Check that the underlying clients are configured correctly
    assert client.client.api_key == "test_api_key"
    assert client.client.organization == "test_org_id"
    assert client.async_client.api_key == "test_api_key"
    assert client.async_client.organization == "test_org_id"

def test_unified_openai_client_no_api_key():
    """
    Tests that the UnifiedOpenAIClient raises a ValueError when no API key is provided.
    """
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]

    with pytest.raises(ValueError):
        UnifiedOpenAIClient()
