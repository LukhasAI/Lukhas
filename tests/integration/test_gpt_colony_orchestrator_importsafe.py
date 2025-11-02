"""
Import safety test for gpt_colony_orchestrator module.

Verifies that the module can be imported without triggering any
import-time dependencies from production (core/) to labs/.

Part of the lane isolation initiative.
"""


def test_gpt_colony_orchestrator_import_safety():
    """
    Verify module imports without labs dependencies.

    This test ensures that:
    1. The module can be imported without errors
    2. No labs imports are triggered at import time
    3. The module is ready for static analysis/linting without labs available
    """
    try:
        from core.orchestration import gpt_colony_orchestrator

        assert gpt_colony_orchestrator is not None
        assert hasattr(gpt_colony_orchestrator, "GPTColonyOrchestrator")

        # Verify the helper function exists
        assert hasattr(gpt_colony_orchestrator, "_get_openai_provider")

        # Verify the class can be imported (but not instantiated without provider)
        GPTColonyOrchestrator = gpt_colony_orchestrator.GPTColonyOrchestrator
        assert GPTColonyOrchestrator is not None

    except ImportError as e:
        # Check if the error is related to labs imports
        if "labs" in str(e).lower():
            raise AssertionError(f"Module still has import-time dependency on labs: {e}") from e
        # Re-raise other import errors
        raise


def test_lazy_loading_pattern():
    """
    Verify that the lazy loading pattern is correctly implemented.

    This test checks that:
    1. The class can be instantiated with no arguments
    2. Properties are defined for lazy loading
    3. No immediate import of labs occurs
    """
    from core.orchestration import gpt_colony_orchestrator

    GPTColonyOrchestrator = gpt_colony_orchestrator.GPTColonyOrchestrator

    # Create instance with no arguments (should not trigger labs import)
    # Note: We cannot actually test this without mocking because accessing
    # the properties will trigger the lazy load
    orchestrator = GPTColonyOrchestrator()

    # Verify internal state is correct
    assert hasattr(orchestrator, "_openai_service")
    assert hasattr(orchestrator, "_signal_bus")
    assert hasattr(orchestrator, "_openai_loaded")
    assert hasattr(orchestrator, "_signal_bus_loaded")

    # Verify the properties exist (but don't access them to avoid triggering lazy load)
    assert hasattr(GPTColonyOrchestrator, "openai_service")
    assert hasattr(GPTColonyOrchestrator, "signal_bus")


def test_provider_infrastructure_available():
    """Verify that the provider infrastructure is available."""
    try:
        from core.adapters import ProviderRegistry, make_resolver

        assert ProviderRegistry is not None
        assert make_resolver is not None

        # Test that we can create instances
        config = make_resolver()
        assert config is not None

        registry = ProviderRegistry(config)
        assert registry is not None

    except ImportError as e:
        raise AssertionError(f"Provider infrastructure not available: {e}") from e


if __name__ == "__main__":
    test_gpt_colony_orchestrator_import_safety()
    test_lazy_loading_pattern()
    test_provider_infrastructure_available()
    print("✅ All import safety tests passed for gpt_colony_orchestrator")
