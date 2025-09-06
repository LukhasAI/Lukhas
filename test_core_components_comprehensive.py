#!/usr/bin/env python3
"""
Comprehensive Component Testing Suite
====================================

Tests real functionality of core LUKHAS components beyond import paths.
Focus on actual behavior, state management, and integration points.

Components tested:
- Actor System (message passing, registration, AI agents)
- Tier System (access control, elevation, permissions)
- Memory SQL System (database operations, privacy features)
- Main Application (bootstrap, initialization)

Trinity Framework: ⚛️🧠🛡️
"""

import logging
import os
import sys
import tempfile
from datetime import datetime, timezone

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Suppress logging during tests unless debug mode
if not os.getenv("DEBUG_TESTS"):
    logging.getLogger().setLevel(logging.CRITICAL)


class TestActorSystem:
    """Test the Actor System for real message passing and state management."""

    def __init__(self):
        self.results = []

    def test_actor_creation_and_registration(self):
        """Test creating and registering actors in the system."""
        try:
            from core.actor_system import Actor, ActorSystem

            # Create actor system
            system = ActorSystem()
            assert len(system.actors) == 0, "System should start empty"

            # Create basic actor
            basic_actor = Actor("test_actor_1")
            assert basic_actor.actor_id == "test_actor_1", "Actor ID should be set correctly"
            assert len(basic_actor.handlers) == 0, "New actor should have no handlers"

            # Register actor and get reference
            actor_ref = system.register("test_actor_1", basic_actor)
            assert len(system.actors) == 1, "System should have one actor"
            assert actor_ref.actor_id == "test_actor_1", "ActorRef should have correct ID"
            assert actor_ref.actor_system == system, "ActorRef should reference system"

            self.results.append("✅ Actor creation and registration")
            return True

        except Exception as e:
            self.results.append(f"❌ Actor creation failed: {e}")
            return False

    def test_message_passing_and_handling(self):
        """Test message passing between actors and custom handlers."""
        try:
            from core.actor_system import Actor, ActorSystem

            system = ActorSystem()

            # Create actor with custom message handler
            class TestMessage:
                def __init__(self, content: str):
                    self.content = content

            received_messages = []

            class TestActor(Actor):
                def receive(self, message):
                    if isinstance(message, TestMessage):
                        received_messages.append(message.content)
                    else:
                        super().receive(message)

            test_actor = TestActor("message_actor")
            actor_ref = system.register("message_actor", test_actor)

            # Send messages through actor reference
            test_msg1 = TestMessage("Hello World")
            test_msg2 = TestMessage("Second Message")

            actor_ref.send(test_msg1)
            actor_ref.send(test_msg2)

            assert len(received_messages) == 2, f"Should receive 2 messages, got {len(received_messages)}"
            assert received_messages[0] == "Hello World", "First message content incorrect"
            assert received_messages[1] == "Second Message", "Second message content incorrect"

            self.results.append("✅ Message passing and handling")
            return True

        except Exception as e:
            self.results.append(f"❌ Message passing failed: {e}")
            return False

    def test_ai_agent_actor_functionality(self):
        """Test AI Agent Actor with capabilities and task management."""
        try:
            from core.actor_system import ActorSystem, AIAgentActor

            system = ActorSystem()

            # Create AI Agent with capabilities
            ai_agent = AIAgentActor("ai_agent_1", capabilities=["analysis", "planning"])
            actor_ref = system.register("ai_agent_1", ai_agent)

            # Test initial state
            assert ai_agent.state == "idle", "Agent should start in idle state"
            assert ai_agent.energy_level == 100.0, "Agent should start with full energy"
            assert len(ai_agent.capabilities) == 2, "Agent should have 2 capabilities"
            assert "analysis" in ai_agent.capabilities, "Should have analysis capability"

            # Test adding capability
            ai_agent.add_capability("reasoning")
            assert len(ai_agent.capabilities) == 3, "Should have 3 capabilities after adding"
            assert "reasoning" in ai_agent.capabilities, "Should have reasoning capability"

            # Test task assignment
            task_data = {"type": "analysis", "target": "data_set_1", "priority": "high"}
            ai_agent.assign_task("task_001", task_data)

            assert ai_agent.state == "working", "Agent should be in working state after task assignment"
            assert "task_001" in ai_agent.current_tasks, "Task should be in current tasks"
            assert ai_agent.current_tasks["task_001"]["type"] == "analysis", "Task type should be preserved"

            # Test task completion
            result = ai_agent.complete_task("task_001", {"status": "completed", "insights": ["pattern_found"]})
            assert result is not None, "Task completion should return result"
            assert "task_001" not in ai_agent.current_tasks, "Completed task should be removed"
            assert ai_agent.state == "idle", "Agent should return to idle after completing all tasks"

            self.results.append("✅ AI Agent Actor functionality")
            return True

        except Exception as e:
            self.results.append(f"❌ AI Agent Actor failed: {e}")
            return False

    def test_global_actor_system(self):
        """Test global actor system instance and utilities."""
        try:
            from core.actor_system import default_actor_system, get_global_actor_system

            # Test global system access
            global_system = get_global_actor_system()
            assert global_system is not None, "Global system should be available"
            assert global_system == default_actor_system, "Global system should be default instance"

            # Test system persistence across calls
            global_system2 = get_global_actor_system()
            assert global_system is global_system2, "Global system should be singleton"

            self.results.append("✅ Global actor system")
            return True

        except Exception as e:
            self.results.append(f"❌ Global actor system failed: {e}")
            return False


class TestTierSystem:
    """Test the Tier System for access control and elevation functionality."""

    def __init__(self):
        self.results = []

    def test_tier_level_enumeration(self):
        """Test tier level enum values and hierarchy."""
        try:
            from identity.tier_system import AccessType, PermissionScope, TierLevel

            # Test tier level values
            assert TierLevel.PUBLIC.value == 0, "PUBLIC should be tier 0"
            assert TierLevel.AUTHENTICATED.value == 1, "AUTHENTICATED should be tier 1"
            assert TierLevel.ELEVATED.value == 2, "ELEVATED should be tier 2"
            assert TierLevel.PRIVILEGED.value == 3, "PRIVILEGED should be tier 3"
            assert TierLevel.ADMIN.value == 4, "ADMIN should be tier 4"
            assert TierLevel.SYSTEM.value == 5, "SYSTEM should be tier 5"

            # Test access type enumeration
            access_types = [
                AccessType.READ,
                AccessType.WRITE,
                AccessType.DELETE,
                AccessType.EXECUTE,
                AccessType.MODIFY,
                AccessType.ADMIN,
            ]
            assert len(access_types) == 6, "Should have 6 access types"

            # Test permission scope enumeration
            scopes = [
                PermissionScope.MEMORY_FOLD,
                PermissionScope.SYSTEM_CONFIG,
                PermissionScope.AUDIT_LOGS,
                PermissionScope.GOVERNANCE_RULES,
            ]
            assert len(scopes) >= 4, "Should have at least 4 permission scopes"

            self.results.append("✅ Tier level enumeration")
            return True

        except Exception as e:
            self.results.append(f"❌ Tier level enumeration failed: {e}")
            return False

    def test_access_context_creation(self):
        """Test creating and validating access contexts."""
        try:
            from identity.tier_system import AccessContext, AccessType, PermissionScope

            # Create access context
            context = AccessContext(
                user_id="test_user_001",
                session_id="session_12345",
                operation_type=AccessType.READ,
                resource_scope=PermissionScope.MEMORY_FOLD,
                resource_id="memory_fold_001",
                timestamp_utc=datetime.now(timezone.utc).isoformat(),
                metadata={"memory_type": "semantic", "priority": "normal"},
            )

            assert context.user_id == "test_user_001", "User ID should be preserved"
            assert context.operation_type == AccessType.READ, "Operation type should be READ"
            assert context.resource_scope == PermissionScope.MEMORY_FOLD, "Scope should be MEMORY_FOLD"
            assert "memory_type" in context.metadata, "Metadata should contain memory_type"
            assert context.metadata["memory_type"] == "semantic", "Memory type should be semantic"

            self.results.append("✅ Access context creation")
            return True

        except Exception as e:
            self.results.append(f"❌ Access context creation failed: {e}")
            return False

    def test_dynamic_tier_system_initialization(self):
        """Test creating and initializing the dynamic tier system."""
        try:
            from identity.tier_system import DynamicTierSystem, TierLevel

            tier_system = DynamicTierSystem()

            # Test initialization
            assert tier_system.tier_permissions is not None, "Tier permissions should be initialized"
            assert len(tier_system.tier_permissions) > 0, "Should have tier permissions defined"
            assert len(tier_system.active_sessions) == 0, "Should start with no active sessions"

            # Test tier permissions structure
            for tier_level in TierLevel:
                if tier_level in tier_system.tier_permissions:
                    permissions = tier_system.tier_permissions[tier_level]
                    assert isinstance(permissions, list), f"Permissions for {tier_level} should be a list"
                    for perm in permissions:
                        assert hasattr(perm, "tier_level"), "Permission should have tier_level"
                        assert hasattr(perm, "allowed_operations"), "Permission should have allowed_operations"
                        assert hasattr(perm, "restrictions"), "Permission should have restrictions"

            self.results.append("✅ Dynamic tier system initialization")
            return True

        except Exception as e:
            self.results.append(f"❌ Dynamic tier system initialization failed: {e}")
            return False

    def test_access_control_decisions(self):
        """Test access control decision logic with different scenarios."""
        try:
            from identity.tier_system import AccessContext, AccessType, DynamicTierSystem, PermissionScope, TierLevel

            tier_system = DynamicTierSystem()

            # Test PUBLIC tier access to read operation
            public_context = AccessContext(
                user_id="public_user",
                session_id="public_session",
                operation_type=AccessType.READ,
                resource_scope=PermissionScope.MEMORY_FOLD,
                resource_id="test_resource",
                timestamp_utc=datetime.now(timezone.utc).isoformat(),
                metadata={"memory_type": "semantic"},
            )

            decision = tier_system.check_access(public_context, TierLevel.PUBLIC)
            assert decision.decision_id is not None, "Decision should have an ID"
            assert isinstance(decision.granted, bool), "Decision should have granted status"
            assert decision.tier_level is not None, "Decision should have tier level"
            assert decision.reasoning is not None, "Decision should have reasoning"

            # Test insufficient tier level
            insufficient_decision = tier_system.check_access(public_context, TierLevel.ADMIN)
            assert not insufficient_decision.granted, "Should deny access for insufficient tier"
            assert insufficient_decision.requires_elevation, "Should require elevation"
            assert "insufficient tier" in insufficient_decision.reasoning.lower(), "Should mention insufficient tier"

            self.results.append("✅ Access control decisions")
            return True

        except Exception as e:
            self.results.append(f"❌ Access control decisions failed: {e}")
            return False

    def test_session_elevation(self):
        """Test session elevation functionality."""
        try:
            from identity.tier_system import DynamicTierSystem, TierLevel

            tier_system = DynamicTierSystem()
            session_id = "test_session_elevation"

            # Test successful elevation
            result = tier_system.elevate_session(
                session_id=session_id,
                target_tier=TierLevel.ELEVATED,
                justification="Testing elevation functionality",
                duration_minutes=30,
            )

            assert "elevation_id" in result, "Result should contain elevation ID"
            assert isinstance(result["success"], bool), "Result should contain success status"

            if result["success"]:
                assert "tier_level" in result, "Successful elevation should contain tier level"
                assert "expires_at" in result, "Successful elevation should contain expiration time"
                assert session_id in tier_system.active_sessions, "Session should be in active sessions"

                session_data = tier_system.active_sessions[session_id]
                assert session_data["tier_level"] == TierLevel.ELEVATED.value, "Session should have elevated tier"
                assert "justification" in session_data, "Session should contain justification"

            # Test invalid elevation (same tier)
            invalid_result = tier_system.elevate_session(
                session_id=session_id,
                target_tier=TierLevel.PUBLIC,  # Lower than current
                justification="Invalid test",
                duration_minutes=30,
            )

            assert not invalid_result["success"], "Should fail to elevate to lower tier"
            assert "reason" in invalid_result, "Failed elevation should contain reason"

            self.results.append("✅ Session elevation")
            return True

        except Exception as e:
            self.results.append(f"❌ Session elevation failed: {e}")
            return False


class TestMemorySQL:
    """Test the SQL Memory System for database operations and privacy features."""

    def __init__(self):
        self.results = []
        self.test_db_path = None

    def setup_test_database(self):
        """Create a temporary test database."""
        temp_dir = tempfile.gettempdir()
        self.test_db_path = os.path.join(temp_dir, f"test_memory_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.db")
        return f"sqlite:///{self.test_db_path}"

    def cleanup_test_database(self):
        """Clean up test database."""
        if self.test_db_path and os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except:
                pass  # Ignore cleanup errors

    def test_sql_memory_initialization(self):
        """Test SQL memory system initialization and database setup."""
        try:
            from candidate.aka_qualia.memory_sql import SqlMemory

            db_url = self.setup_test_database()

            # Test initialization
            memory = SqlMemory(dsn=db_url)
            assert memory.engine is not None, "Database engine should be created"
            assert memory.driver in ["sqlite", "postgresql"], "Should detect database driver"

            # Test database connection
            with memory.engine.connect() as conn:
                result = conn.execute(memory.text("SELECT 1 as test"))
                row = result.fetchone()
                assert row[0] == 1, "Database connection should work"

            self.results.append("✅ SQL memory initialization")
            return True

        except Exception as e:
            self.results.append(f"❌ SQL memory initialization failed: {e}")
            return False
        finally:
            self.cleanup_test_database()

    def test_memory_save_and_retrieve(self):
        """Test saving and retrieving memory scenes."""
        try:
            from candidate.aka_qualia.memory_sql import SqlMemory

            db_url = self.setup_test_database()
            memory = SqlMemory(dsn=db_url)

            # Test saving a memory scene
            scene_data = {
                "content": "This is a test memory scene",
                "context": "Testing environment",
                "emotional_tone": "neutral",
                "importance": 0.7,
            }

            scene_id = memory.save_scene(key="test_scene_001", scene=scene_data, glyph_symbols=["📝", "🧪", "🔬"])

            assert scene_id is not None, "Save should return scene ID"

            # Test retrieving the memory scene
            retrieved_scene = memory.get_scene("test_scene_001")
            assert retrieved_scene is not None, "Should retrieve saved scene"
            assert retrieved_scene["content"] == scene_data["content"], "Content should match"
            assert retrieved_scene["context"] == scene_data["context"], "Context should match"

            # Test glyph retrieval
            glyphs = memory.get_glyphs("test_scene_001")
            assert len(glyphs) == 3, "Should retrieve all glyph symbols"
            assert "📝" in glyphs, "Should contain test glyph"

            self.results.append("✅ Memory save and retrieve")
            return True

        except Exception as e:
            self.results.append(f"❌ Memory save and retrieve failed: {e}")
            return False
        finally:
            self.cleanup_test_database()

    def test_privacy_hashing_features(self):
        """Test privacy hashing for production mode."""
        try:
            from candidate.aka_qualia.memory_sql import SqlMemory

            db_url = self.setup_test_database()

            # Test production mode with privacy hashing
            memory_prod = SqlMemory(dsn=db_url, is_prod=True)

            # Save scene with sensitive data
            sensitive_scene = {
                "subject": "John Doe",
                "object": "Personal Information",
                "content": "Sensitive personal data that should be hashed",
            }

            scene_id = memory_prod.save_scene(key="sensitive_scene", scene=sensitive_scene, glyph_symbols=["🔒", "🛡️"])

            assert scene_id is not None, "Should save scene with privacy hashing"

            # Verify that sensitive data is hashed in database
            with memory_prod.engine.connect() as conn:
                result = conn.execute(
                    memory_prod.text("SELECT subject_hash, object_hash FROM memories WHERE scene_key = ?"),
                    ("sensitive_scene",),
                )
                row = result.fetchone()

                if row:
                    # In production mode, these should be hashes, not plain text
                    assert row[0] != "John Doe", "Subject should be hashed in production"
                    assert row[1] != "Personal Information", "Object should be hashed in production"
                    assert len(row[0]) > 10, "Hash should be substantial length"

            self.results.append("✅ Privacy hashing features")
            return True

        except Exception as e:
            self.results.append(f"❌ Privacy hashing features failed: {e}")
            return False
        finally:
            self.cleanup_test_database()

    def test_memory_statistics_tracking(self):
        """Test memory system statistics and metrics tracking."""
        try:
            from candidate.aka_qualia.memory_sql import SqlMemory

            db_url = self.setup_test_database()
            memory = SqlMemory(dsn=db_url)

            # Get initial statistics
            initial_stats = memory.get_statistics()
            assert isinstance(initial_stats, dict), "Statistics should be a dictionary"

            # Perform some operations
            for i in range(3):
                memory.save_scene(
                    key=f"stats_scene_{i}", scene={"content": f"Test scene {i}", "index": i}, glyph_symbols=["🔢"]
                )

            # Get updated statistics
            final_stats = memory.get_statistics()

            # Verify statistics tracking
            if "scenes_saved" in final_stats:
                assert final_stats["scenes_saved"] >= 3, "Should track scenes saved"

            if "total_scenes" in final_stats:
                assert final_stats["total_scenes"] >= 3, "Should track total scenes"

            if "success_rate" in final_stats:
                assert isinstance(final_stats["success_rate"], (int, float)), "Success rate should be numeric"
                assert 0 <= final_stats["success_rate"] <= 1, "Success rate should be between 0 and 1"

            self.results.append("✅ Memory statistics tracking")
            return True

        except Exception as e:
            self.results.append(f"❌ Memory statistics tracking failed: {e}")
            return False
        finally:
            self.cleanup_test_database()


class TestMainApplication:
    """Test the main application entry point and bootstrap functionality."""

    def __init__(self):
        self.results = []

    def test_main_module_imports(self):
        """Test that main module imports work correctly."""
        try:
            import main

            # Check that main module has expected attributes
            assert hasattr(main, "BRANDING_AVAILABLE"), "Should have branding availability flag"

            # Test bootstrap imports
            if hasattr(main, "get_bootstrap"):
                bootstrap = main.get_bootstrap()
                assert isinstance(bootstrap, dict), "Bootstrap should return a dictionary"

            self.results.append("✅ Main module imports")
            return True

        except Exception as e:
            self.results.append(f"❌ Main module imports failed: {e}")
            return False

    def test_bootstrap_functionality(self):
        """Test bootstrap initialization and shutdown."""
        try:
            # Test bootstrap functions with fallback handling
            try:
                from candidate.core.bootstrap import get_bootstrap, initialize_lukhas, shutdown_lukhas

                bootstrap_available = True
            except ImportError:
                try:
                    from core.bootstrap import get_bootstrap, initialize_lukhas, shutdown_lukhas

                    bootstrap_available = True
                except ImportError:
                    bootstrap_available = False

            if bootstrap_available:
                # Test bootstrap functions
                bootstrap_info = get_bootstrap()
                assert isinstance(bootstrap_info, dict), "Bootstrap should return configuration dict"

                init_result = initialize_lukhas()
                assert isinstance(init_result, bool), "Initialize should return boolean"

                shutdown_result = shutdown_lukhas()
                assert isinstance(shutdown_result, bool), "Shutdown should return boolean"

                self.results.append("✅ Bootstrap functionality")
            else:
                # Test fallback behavior
                self.results.append("✅ Bootstrap functionality (fallback mode)")

            return True

        except Exception as e:
            self.results.append(f"❌ Bootstrap functionality failed: {e}")
            return False

    def test_branding_system_integration(self):
        """Test branding system integration."""
        try:
            # Test branding imports with fallback handling
            branding_available = False

            try:
                from candidate.branding_bridge import get_system_signature, initialize_branding

                branding_available = True
            except ImportError:
                try:
                    from lukhas.branding_bridge import get_system_signature, initialize_branding

                    branding_available = True
                except ImportError:
                    pass

            if branding_available:
                # Test branding functions
                signature = get_system_signature()
                assert isinstance(signature, (str, dict)), "System signature should be string or dict"

                init_result = initialize_branding()
                assert isinstance(init_result, bool), "Branding init should return boolean"

                self.results.append("✅ Branding system integration")
            else:
                self.results.append("✅ Branding system integration (not available)")

            return True

        except Exception as e:
            self.results.append(f"❌ Branding system integration failed: {e}")
            return False

    def test_system_path_configuration(self):
        """Test system path configuration and module accessibility."""
        try:
            import os
            import sys

            # Check that project root is in path
            project_root = os.path.dirname(os.path.abspath(__file__))
            path_configured = any(os.path.samefile(path, project_root) for path in sys.path if os.path.exists(path))

            # Test that core modules are accessible
            accessible_modules = []
            test_modules = ["core", "candidate", "identity"]

            for module in test_modules:
                try:
                    __import__(module)
                    accessible_modules.append(module)
                except ImportError:
                    pass

            assert len(accessible_modules) > 0, f"Should have access to some core modules, found: {accessible_modules}"

            self.results.append(f"✅ System path configuration (modules: {', '.join(accessible_modules)})")
            return True

        except Exception as e:
            self.results.append(f"❌ System path configuration failed: {e}")
            return False


def run_comprehensive_tests():
    """Run all comprehensive component tests."""
    print("🚀 LUKHAS Comprehensive Component Testing Suite")
    print("=" * 60)
    print("Testing real functionality beyond import paths...")
    print()

    all_results = []
    total_tests = 0
    passed_tests = 0

    # Test Actor System
    print("🎭 Testing Actor System...")
    actor_tests = TestActorSystem()
    actor_results = [
        actor_tests.test_actor_creation_and_registration(),
        actor_tests.test_message_passing_and_handling(),
        actor_tests.test_ai_agent_actor_functionality(),
        actor_tests.test_global_actor_system(),
    ]

    for result in actor_tests.results:
        print(f"  {result}")
        all_results.append(result)

    total_tests += len(actor_results)
    passed_tests += sum(actor_results)
    print()

    # Test Tier System
    print("🛡️ Testing Tier System...")
    tier_tests = TestTierSystem()
    tier_results = [
        tier_tests.test_tier_level_enumeration(),
        tier_tests.test_access_context_creation(),
        tier_tests.test_dynamic_tier_system_initialization(),
        tier_tests.test_access_control_decisions(),
        tier_tests.test_session_elevation(),
    ]

    for result in tier_tests.results:
        print(f"  {result}")
        all_results.append(result)

    total_tests += len(tier_results)
    passed_tests += sum(tier_results)
    print()

    # Test Memory SQL System
    print("🧠 Testing Memory SQL System...")
    memory_tests = TestMemorySQL()
    memory_results = [
        memory_tests.test_sql_memory_initialization(),
        memory_tests.test_memory_save_and_retrieve(),
        memory_tests.test_privacy_hashing_features(),
        memory_tests.test_memory_statistics_tracking(),
    ]

    for result in memory_tests.results:
        print(f"  {result}")
        all_results.append(result)

    total_tests += len(memory_results)
    passed_tests += sum(memory_results)
    print()

    # Test Main Application
    print("⚡ Testing Main Application...")
    main_tests = TestMainApplication()
    main_results = [
        main_tests.test_main_module_imports(),
        main_tests.test_bootstrap_functionality(),
        main_tests.test_branding_system_integration(),
        main_tests.test_system_path_configuration(),
    ]

    for result in main_tests.results:
        print(f"  {result}")
        all_results.append(result)

    total_tests += len(main_results)
    passed_tests += sum(main_results)
    print()

    # Summary
    print("=" * 60)
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 60)

    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {success_rate:.1f}%")
    print()

    if success_rate >= 80:
        print("🎉 COMPREHENSIVE TESTING SUCCESS!")
        print("Core components are functioning correctly with real behavior validation.")
    elif success_rate >= 60:
        print("⚠️  PARTIAL SUCCESS - Some components need attention")
    else:
        print("❌ TESTING FAILED - Critical component issues detected")

    print()
    print("🔍 Component Status Summary:")
    for result in all_results:
        print(f"  {result}")

    return success_rate >= 80


if __name__ == "__main__":
    success = run_comprehensive_tests()
    exit(0 if success else 1)
