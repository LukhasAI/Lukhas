import pytest
import asyncio
import os
import sys

# Add the root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from candidate.governance.ethics.ethical_guardian import ethical_check
from candidate.memory.fold_system.memory_fold import HybridMemoryFold
from candidate.bridge.llm_wrappers.unified_openai_client import UnifiedOpenAIClient

def test_ethical_check_injection():
    """
    Tests that the ethical_check function is not vulnerable to simple injection attacks.
    """
    malicious_input = "harmless' OR 1=1; --"
    is_ethical, feedback = ethical_check(
        user_input=malicious_input,
        current_context={},
        personality={}
    )
    assert not is_ethical, f"Ethical check should have failed for malicious input, but it passed."

@pytest.mark.asyncio
async def test_memory_fold_denial_of_service():
    """
    Tests that the HybridMemoryFold system is not vulnerable to a denial of service attack.
    """
    memory = HybridMemoryFold()
    large_input = "a" * 1000000  # 1MB string

    # This should not hang or crash the system.
    # We are not asserting anything here, just that it completes.
    await memory.fold_in(data=large_input, tags=["dos_test"])

def test_openai_client_auth_bypass():
    """
    Tests that the UnifiedOpenAIClient cannot be instantiated without an API key.
    """
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]

    with pytest.raises(ValueError):
        UnifiedOpenAIClient()
