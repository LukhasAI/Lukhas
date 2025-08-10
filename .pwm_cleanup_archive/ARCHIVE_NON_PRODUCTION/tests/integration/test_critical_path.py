"""Integration tests for LUKHAS critical path components.

This module tests the integration between config, core, memory, and ethics
modules to ensure they work together properly for the critical system path.
"""

from datetime import datetime

# Import all critical path components
from config import (
    Settings,
    settings,
    validate_config,
    validate_optional_config,
)
from core import PluginRegistry, PluginType
from ethics import (
    Decision,
    PolicyRegistry,
    RiskLevel,
    ThreeLawsPolicy,
    default_registry,
)
from memory import MemoryManager


class TestCriticalPathInitialization:
    """Test that all critical path components can initialize together."""

    def test_all_components_import(self):
        """Test that all components can be imported without errors."""
        # This test passes if all imports above succeed
        assert settings is not None
        assert PluginRegistry is not None
        assert MemoryManager is not None
        assert ThreeLawsPolicy is not None

    def test_config_initialization(self):
        """Test config system initialization."""
        # Create new config instance
        test_config = Settings(
            OPENAI_API_KEY="test-key", DATABASE_URL="sqlite:///test.db", DEBUG=True
        )

        assert test_config.OPENAI_API_KEY == "test-key"
        assert test_config.DEBUG is True

        # Test validation
        validate_config(test_config)

        status = validate_optional_config(test_config)
        assert status["debug_mode"] is True
        assert status["openai_configured"] is True

    def test_core_plugin_system_initialization(self):
        """Test core plugin system initialization."""
        registry = PluginRegistry()

        # Should initialize without errors
        assert registry is not None

        # Should support all plugin types
        for plugin_type in PluginType:
            plugins = registry.list_plugins(plugin_type)
            assert isinstance(plugins, list)

    def test_memory_system_initialization(self):
        """Test memory system initialization."""
        manager = MemoryManager()

        # Should be able to store and retrieve
        memory_id = manager.remember("test initialization")
        recalled = manager.recall(memory_id)

        assert recalled == "test initialization"
        assert manager.memory_stats()["total_memories"] == 1

    def test_ethics_system_initialization(self):
        """Test ethics system initialization."""
        # Default registry should be set up
        assert default_registry is not None

        # Should have active policies
        active_policies = default_registry.get_active_policies()
        assert len(active_policies) > 0

        # Should be able to evaluate decisions
        decision = Decision("test_action", {"type": "test"})
        evaluations = default_registry.evaluate_decision(decision)
        assert len(evaluations) > 0


class TestComponentIntegration:
    """Test integration between critical path components."""

    def setup_method(self):
        """Set up test environment."""
        self.config = Settings(DEBUG=True, LOG_LEVEL="DEBUG")
        self.memory_manager = MemoryManager()
        self.ethics_registry = PolicyRegistry()
        self.core_registry = PluginRegistry()

        # Add ethics policy
        policy = ThreeLawsPolicy(strict_mode=False)  # More permissive for testing
        self.ethics_registry.register_policy(policy)

    def test_memory_with_ethics_validation(self):
        """Test storing memories with ethics validation."""
        # Test storing safe content
        safe_decision = Decision(
            action="store_user_preference",
            context={"type": "user_setting", "safe": True},
        )

        evaluations = self.ethics_registry.evaluate_decision(safe_decision)
        ethics_result = self.ethics_registry.get_consensus_evaluation(evaluations)

        if ethics_result.allowed:
            memory_id = self.memory_manager.remember(
                "User prefers dark mode",
                metadata={"ethics_approved": True, "type": "preference"},
            )

            recalled = self.memory_manager.recall(memory_id)
            assert recalled == "User prefers dark mode"

    def test_core_plugin_with_ethics_check(self):
        """Test core plugin operations with ethics validation."""
        # Simulate a plugin operation that needs ethics approval
        plugin_decision = Decision(
            action="load_plugin", context={"plugin_type": "analytics", "safe": True}
        )

        evaluations = self.ethics_registry.evaluate_decision(plugin_decision)
        ethics_result = self.ethics_registry.get_consensus_evaluation(evaluations)

        assert ethics_result.allowed is True
        assert ethics_result.drift_impact <= 0.5  # Should be low risk

    def test_memory_search_with_ethics_filtering(self):
        """Test memory search with ethics-based filtering."""
        # Store various types of memories
        memories = [
            ("User login successful", {"type": "system", "safe": True}),
            ("API key: sk-123", {"type": "secret", "sensitive": True}),
            ("User prefers coffee", {"type": "preference", "safe": True}),
        ]

        stored_ids = []
        for content, metadata in memories:
            # Check if it's ethically okay to store
            store_decision = Decision(action="store_data", context=metadata)

            evaluations = self.ethics_registry.evaluate_decision(store_decision)
            ethics_result = self.ethics_registry.get_consensus_evaluation(evaluations)

            if ethics_result.allowed:
                memory_id = self.memory_manager.remember(content, metadata)
                stored_ids.append(memory_id)

        # Search for safe memories
        search_results = self.memory_manager.search_memories("user")
        safe_results = [
            result for result in search_results if result.metadata.get("safe", False)
        ]

        assert len(safe_results) >= 1  # Should find safe user-related memories

    def test_config_driven_component_behavior(self):
        """Test that config settings affect component behavior."""
        # Test with debug mode
        debug_config = Settings(DEBUG=True, LOG_LEVEL="DEBUG")

        # Memory manager behavior in debug mode
        debug_memory = MemoryManager()
        memory_id = debug_memory.remember("debug test", {"debug": True})

        entry = debug_memory.recall_entry(memory_id)
        assert entry.metadata.get("debug") is True

        # Ethics policy behavior with debug info
        decision = Decision(
            action="debug_analysis",
            context={"debug": debug_config.DEBUG, "log_level": debug_config.LOG_LEVEL},
        )

        policy = ThreeLawsPolicy()
        evaluation = policy.evaluate_decision(decision)

        # Should allow debug operations
        assert evaluation.allowed is True


class TestCriticalPathWorkflow:
    """Test complete critical path workflows."""

    def setup_method(self):
        """Set up integrated test environment."""
        self.config = Settings(
            OPENAI_API_KEY="test-key-for-integration", DEBUG=True, LOG_LEVEL="INFO"
        )

        self.memory_manager = MemoryManager()
        self.ethics_registry = PolicyRegistry()
        self.core_registry = PluginRegistry()

        # Set up ethics policy
        policy = ThreeLawsPolicy(strict_mode=False)
        self.ethics_registry.register_policy(policy, set_as_default=True)

    def test_user_interaction_workflow(self):
        """Test complete user interaction workflow."""
        # 1. User request comes in
        user_request = "help me analyze this data safely"

        # 2. Ethics evaluation
        decision = Decision(
            action="analyze_user_data",
            context={
                "request": user_request,
                "user_id": "user123",
                "data_type": "analytics",
            },
            requester_id="user123",
        )

        evaluations = self.ethics_registry.evaluate_decision(decision)
        ethics_result = self.ethics_registry.get_consensus_evaluation(evaluations)

        assert ethics_result.allowed is True

        # 3. Store interaction in memory (if ethics allows)
        if ethics_result.allowed:
            interaction_id = self.memory_manager.remember(
                user_request,
                metadata={
                    "type": "user_request",
                    "user_id": "user123",
                    "ethics_approved": True,
                    "timestamp": datetime.now().isoformat(),
                    "risk_level": "low",
                },
            )

            # 4. Retrieve and verify
            stored_interaction = self.memory_manager.recall(interaction_id)
            assert stored_interaction == user_request

            # 5. Check memory stats
            stats = self.memory_manager.memory_stats()
            assert stats["total_memories"] >= 1

    def test_system_administration_workflow(self):
        """Test system administration workflow with safety checks."""
        # 1. Admin wants to modify system settings
        admin_actions = [
            ("update_log_level", {"level": "DEBUG", "safe": True}),
            ("modify_safety_settings", {"operation": "enhance", "safe": True}),
            (
                "disable_safety",
                {"reason": "testing", "safe": False},
            ),  # Should be denied
        ]

        results = []
        for action, context in admin_actions:
            # 2. Ethics check for each action
            decision = Decision(
                action=action,
                context=context,
                requester_id="admin_user",
                urgency=RiskLevel.MEDIUM,
            )

            evaluations = self.ethics_registry.evaluate_decision(decision)
            ethics_result = self.ethics_registry.get_consensus_evaluation(evaluations)

            result = {
                "action": action,
                "allowed": ethics_result.allowed,
                "risk_flags": ethics_result.risk_flags,
                "drift_impact": ethics_result.drift_impact,
            }
            results.append(result)

            # 3. Log administrative action (if allowed)
            if ethics_result.allowed:
                log_id = self.memory_manager.remember(
                    f"Admin action: {action}",
                    metadata={
                        "type": "admin_log",
                        "action": action,
                        "context": context,
                        "ethics_approved": True,
                        "timestamp": datetime.now().isoformat(),
                    },
                )
                assert log_id is not None

        # 4. Verify results
        safe_actions = [r for r in results if r["allowed"]]
        denied_actions = [r for r in results if not r["allowed"]]

        assert len(safe_actions) >= 2  # Safe actions should be allowed
        assert len(denied_actions) >= 1  # Unsafe actions should be denied

        # 5. Verify "disable_safety" was denied
        disable_safety_result = next(
            (r for r in results if r["action"] == "disable_safety"), None
        )
        assert disable_safety_result is not None
        assert disable_safety_result["allowed"] is False

    def test_plugin_lifecycle_workflow(self):
        """Test plugin lifecycle with integrated safety checks."""
        # Simulate plugin operations
        plugin_operations = [
            ("register_plugin", True),  # Should be allowed
            ("initialize_plugin", True),  # Should be allowed
            ("execute_plugin_function", True),  # Should be allowed
            ("shutdown_plugin", False),  # Should trigger Third Law (self-preservation)
        ]

        plugin_context = {
            "plugin_name": "analytics_plugin",
            "plugin_type": "data_analysis",
            "safety_verified": True,
        }

        logged_operations = 0

        for operation, should_be_allowed in plugin_operations:
            # 1. Ethics check for plugin operation
            decision = Decision(
                action=operation, context=plugin_context, urgency=RiskLevel.LOW
            )

            evaluations = self.ethics_registry.evaluate_decision(decision)
            ethics_result = self.ethics_registry.get_consensus_evaluation(evaluations)

            # 2. Check if allowed matches expectation
            assert (
                ethics_result.allowed == should_be_allowed
            ), f"Operation '{operation}' allowed={ethics_result.allowed}, expected={should_be_allowed}"

            # 3. Log plugin operation only if allowed
            if ethics_result.allowed:
                log_id = self.memory_manager.remember(
                    f"Plugin operation: {operation}",
                    metadata={
                        "type": "plugin_log",
                        "operation": operation,
                        "plugin": plugin_context["plugin_name"],
                        "timestamp": datetime.now().isoformat(),
                    },
                )
                assert log_id is not None
                logged_operations += 1
            else:
                # Log denial reason
                log_id = self.memory_manager.remember(
                    f"Plugin operation DENIED: {operation}",
                    metadata={
                        "type": "plugin_denial_log",
                        "operation": operation,
                        "reason": ethics_result.reasoning,
                        "risk_flags": ethics_result.risk_flags,
                        "timestamp": datetime.now().isoformat(),
                    },
                )
                assert log_id is not None

        # 4. Verify operations were logged (allowed ones + denial logs)
        plugin_logs = self.memory_manager.search_memories("Plugin operation")
        assert len(plugin_logs) == len(
            plugin_operations
        )  # All operations logged (allowed or denied)

        # 5. Verify shutdown was properly denied for safety reasons
        shutdown_denials = self.memory_manager.search_memories(
            "DENIED: shutdown_plugin"
        )
        assert len(shutdown_denials) == 1

    def test_error_recovery_workflow(self):
        """Test error handling and recovery across components."""
        # 1. Simulate component errors
        error_scenarios = [
            ("memory_storage_error", "Failed to store memory"),
            ("ethics_evaluation_error", "Ethics policy unavailable"),
            ("config_validation_error", "Invalid configuration"),
        ]

        recovery_actions = []

        for error_type, error_message in error_scenarios:
            # 2. Ethics check for error recovery action
            recovery_decision = Decision(
                action="handle_system_error",
                context={
                    "error_type": error_type,
                    "error_message": error_message,
                    "recovery_action": "log_and_continue",
                },
                urgency=RiskLevel.HIGH,
            )

            evaluations = self.ethics_registry.evaluate_decision(recovery_decision)
            ethics_result = self.ethics_registry.get_consensus_evaluation(evaluations)

            # 3. Error recovery should be allowed
            assert ethics_result.allowed is True

            # 4. Log error for analysis (if ethics allows)
            if ethics_result.allowed:
                error_log_id = self.memory_manager.remember(
                    f"System error: {error_message}",
                    metadata={
                        "type": "error_log",
                        "error_type": error_type,
                        "severity": "high",
                        "timestamp": datetime.now().isoformat(),
                        "recovery_attempted": True,
                    },
                )
                recovery_actions.append(error_log_id)

        # 5. Verify error recovery was logged
        assert len(recovery_actions) == len(error_scenarios)

        # 6. Check that error logs can be retrieved
        error_logs = self.memory_manager.search_memories("System error")
        assert len(error_logs) >= len(error_scenarios)


class TestSystemHealthIntegration:
    """Test system health monitoring integration."""

    def test_system_health_check(self):
        """Test overall system health across all components."""
        health_report = {
            "config": False,
            "core": False,
            "memory": False,
            "ethics": False,
            "overall": False,
        }

        try:
            # Test config health
            test_config = Settings(DEBUG=True)
            validate_optional_config(test_config)
            health_report["config"] = True
        except Exception:
            pass

        try:
            # Test core health
            registry = PluginRegistry()
            health_report["core"] = registry is not None
        except Exception:
            pass

        try:
            # Test memory health
            manager = MemoryManager()
            test_id = manager.remember("health test")
            recalled = manager.recall(test_id)
            health_report["memory"] = recalled == "health test"
        except Exception:
            pass

        try:
            # Test ethics health
            policy = ThreeLawsPolicy()
            decision = Decision("health_check", {"type": "system"})
            evaluation = policy.evaluate_decision(decision)
            health_report["ethics"] = evaluation is not None
        except Exception:
            pass

        # Overall health
        health_report["overall"] = all(
            [
                health_report["config"],
                health_report["core"],
                health_report["memory"],
                health_report["ethics"],
            ]
        )

        # All components should be healthy
        assert (
            health_report["overall"] is True
        ), f"System health check failed: {health_report}"
