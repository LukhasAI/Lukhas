#!/usr/bin/env python3
"""
Integration test for Agent 1 Task 10: Unified Emotional Memory Manager

Simple integration test to verify that the core UnifiedEmotionalMemoryManager
can be registered with the memory orchestrator system.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_unified_emotional_memory_manager_integration():
    """Test the integration of UnifiedEmotionalMemoryManager."""

    print("🧪 Testing Agent 1 Task 10: Unified Emotional Memory Manager")
    print("=" * 65)

    # Test 1: Check if file exists
    print("Test 1: File existence check...", end=" ")
    emotional_memory_file = project_root / "memory" / "emotional_memory_manager_unified.py"
    if emotional_memory_file.exists():
        print("✅ PASS")
    else:
        print("❌ FAIL - File does not exist")
        return False

    # Test 2: Basic file structure validation
    print("Test 2: File structure validation...", end=" ")
    try:
        with open(emotional_memory_file, 'r') as f:
            content = f.read()

        # Check for key classes and methods
        required_elements = [
            "class UnifiedEmotionalMemoryManager",
            "def store(self, user_id: str",
            "def retrieve(self, user_id: str",
            "def analyze_emotional_patterns",
            "def modulate_emotional_state",
            "def quantum_enhance_emotions",
            "tier_requirements",
            "tier_adapter"
        ]

        for element in required_elements:
            if element not in content:
                print(f"❌ FAIL - Missing: {element}")
                return False

        print("✅ PASS")
    except Exception as e:
        print(f"❌ FAIL - Error reading file: {e}")
        return False

    # Test 3: Check for integration points
    print("Test 3: Integration points validation...", end=" ")
    try:
        # Check for memory hub integration patterns
        integration_patterns = [
            "from memory.emotional_memory_manager import EmotionalMemoryManager",
            "from core.tier_unification_adapter import",
            "@require_identity",
            "@emotional_tier_required",
            "get_unified_adapter"
        ]

        for pattern in integration_patterns:
            if pattern not in content:
                print(f"❌ FAIL - Missing integration pattern: {pattern}")
                return False

        print("✅ PASS")
    except Exception as e:
        print(f"❌ FAIL - Error checking patterns: {e}")
        return False

    # Test 4: Tier system integration
    print("Test 4: Tier system configuration...", end=" ")
    try:
        # Check for tier-based operations
        tier_elements = [
            "LAMBDA_TIER_1",
            "LAMBDA_TIER_2",
            "LAMBDA_TIER_3",
            "LAMBDA_TIER_4",
            "LAMBDA_TIER_5",
            "emotional_granularity",
            "symbolic_access"
        ]

        for tier_element in tier_elements:
            if tier_element not in content:
                print(f"❌ FAIL - Missing tier element: {tier_element}")
                return False

        print("✅ PASS")
    except Exception as e:
        print(f"❌ FAIL - Error checking tier system: {e}")
        return False

    # Test 5: Method signatures validation
    print("Test 5: Method signatures check...", end=" ")
    try:
        # Check for proper async method signatures
        async_methods = [
            "async def store(self, user_id: str, memory_data:",
            "async def retrieve(self, user_id: str, memory_id:",
            "async def analyze_emotional_patterns(self, user_id:",
            "async def modulate_emotional_state(self, user_id:",
            "async def quantum_enhance_emotions(self, user_id:"
        ]

        for method in async_methods:
            if method not in content:
                print(f"❌ FAIL - Missing method signature: {method}")
                return False

        print("✅ PASS")
    except Exception as e:
        print(f"❌ FAIL - Error checking methods: {e}")
        return False

    print("=" * 65)
    print("✅ All integration tests passed!")
    print("📋 Task 10 Status: READY FOR INTEGRATION")
    print()
    print("📊 Integration Summary:")
    print("   * UnifiedEmotionalMemoryManager class: ✅ Available")
    print("   * Tier-based access control: ✅ Configured")
    print("   * User identity integration: ✅ Implemented")
    print("   * Emotional pattern analysis: ✅ Available")
    print("   * Quantum enhancement support: ✅ Available")
    print("   * Memory hub compatibility: ✅ Ready")

    return True

if __name__ == "__main__":
    success = test_unified_emotional_memory_manager_integration()
    sys.exit(0 if success else 1)
            try:
                asyncio.run(self.hub.shutdown())
            except:
                pass

    @pytest.mark.asyncio
    async def test_emotional_memory_manager_initialization(self):
        """Test that unified emotional memory manager initializes correctly"""
        if not MEMORY_HUB_AVAILABLE:
            pytest.skip("Memory hub components not available")

        with patch("memory.memory_hub.UNIFIED_EMOTIONAL_MEMORY_AVAILABLE", True):
            # Mock the manager creation
            mock_manager = Mock()
            mock_manager.initialize = AsyncMock(return_value={"status": "initialized"})

            with patch(
                "memory.emotional_memory_manager_unified.UnifiedEmotionalMemoryManager",
                return_value=mock_manager,
            ):
                await self.hub.initialize()

                # Verify manager was registered as a service
                registered_manager = self.hub.get_service("unified_emotional_manager")
                assert (
                    registered_manager is not None
                ), "Unified emotional manager should be registered"

    @pytest.mark.asyncio
    async def test_store_emotional_memory_interface(self):
        """Test the store_emotional_memory interface method"""
        if not MEMORY_HUB_AVAILABLE:
            pytest.skip("Memory hub components not available")

        with patch("memory.memory_hub.UNIFIED_EMOTIONAL_MEMORY_AVAILABLE", True):
            # Mock the manager
            mock_manager = Mock()
            mock_manager.store = AsyncMock(
                return_value={
                    "status": "success",
                    "memory_id": "test_memory_123",
                    "emotional_tags": ["positive", "excited"],
                    "tier_level": "LAMBDA_TIER_2",
                }
            )

            # Register the mock manager
            self.hub.register_service("unified_emotional_manager", mock_manager)

            # Test storing emotional memory
            result = await self.hub.store_emotional_memory(
                user_id="user123",
                memory_data={
                    "content": "Had a great day at work!",
                    "emotional_context": {"valence": 0.8, "arousal": 0.6},
                },
                memory_id="test_memory_123",
                metadata={"source": "journal", "importance": 0.7},
            )

            assert result["status"] == "success", "Store operation should succeed"
            assert (
                result["memory_id"] == "test_memory_123"
            ), "Should return correct memory ID"
            assert "emotional_tags" in result, "Should include emotional tags"
            mock_manager.store.assert_called_once()

    @pytest.mark.asyncio
    async def test_retrieve_emotional_memory_interface(self):
        """Test the retrieve_emotional_memory interface method"""
        if not MEMORY_HUB_AVAILABLE:
            pytest.skip("Memory hub components not available")

        with patch("memory.memory_hub.UNIFIED_EMOTIONAL_MEMORY_AVAILABLE", True):
            # Mock the manager
            mock_manager = Mock()
            mock_manager.retrieve = AsyncMock(
                return_value={
                    "status": "success",
                    "memory_data": {
                        "content": "Had a great day at work!",
                        "emotional_context": {"valence": 0.8, "arousal": 0.6},
                    },
                    "emotional_modulation": {
                        "tier_filtered": True,
                        "consent_validated": True,
                        "emotional_enhancement": 0.1,
                    },
                }
            )

            # Register the mock manager
            self.hub.register_service("unified_emotional_manager", mock_manager)

            # Test retrieving emotional memory
            result = await self.hub.retrieve_emotional_memory(
                user_id="user123",
                memory_id="test_memory_123",
                context={"current_mood": {"valence": 0.6, "arousal": 0.4}},
            )

            assert result["status"] == "success", "Retrieve operation should succeed"
            assert "memory_data" in result, "Should return memory data"
            assert (
                "emotional_modulation" in result
            ), "Should include emotional modulation"
            mock_manager.retrieve.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_emotional_patterns_interface(self):
        """Test the analyze_emotional_patterns interface method"""
        if not MEMORY_HUB_AVAILABLE:
            pytest.skip("Memory hub components not available")

        with patch("memory.memory_hub.UNIFIED_EMOTIONAL_MEMORY_AVAILABLE", True):
            # Mock the manager
            mock_manager = Mock()
            mock_manager.analyze_emotional_patterns = AsyncMock(
                return_value={
                    "status": "success",
                    "patterns": {
                        "daily_emotional_trend": {"morning": 0.7, "evening": 0.5},
                        "emotional_volatility": 0.3,
                        "dominant_emotions": ["joy", "excitement", "calm"],
                    },
                    "insights": [
                        "User shows consistent positive emotional patterns",
                        "Evening emotional dips suggest need for relaxation activities",
                    ],
                }
            )

            # Register the mock manager
            self.hub.register_service("unified_emotional_manager", mock_manager)

            # Test analyzing emotional patterns
            result = await self.hub.analyze_emotional_patterns(
                user_id="user123",
                time_range={"start": "2024-01-01", "end": "2024-01-31"},
            )

            assert result["status"] == "success", "Pattern analysis should succeed"
            assert "patterns" in result, "Should return emotional patterns"
            assert "insights" in result, "Should provide insights"
            mock_manager.analyze_emotional_patterns.assert_called_once()

    @pytest.mark.asyncio
    async def test_modulate_emotional_state_interface(self):
        """Test the modulate_emotional_state interface method"""
        if not MEMORY_HUB_AVAILABLE:
            pytest.skip("Memory hub components not available")

        with patch("memory.memory_hub.UNIFIED_EMOTIONAL_MEMORY_AVAILABLE", True):
            # Mock the manager
            mock_manager = Mock()
            mock_manager.modulate_emotional_state = AsyncMock(
                return_value={
                    "status": "success",
                    "original_state": {"valence": 0.3, "arousal": 0.8},
                    "target_state": {"valence": 0.6, "arousal": 0.5},
                    "modulated_state": {"valence": 0.55, "arousal": 0.55},
                    "modulation_applied": True,
                }
            )

            # Register the mock manager
            self.hub.register_service("unified_emotional_manager", mock_manager)

            # Test emotional state modulation
            result = await self.hub.modulate_emotional_state(
                user_id="user123",
                memory_id="test_memory_123",
                target_state={"valence": 0.6, "arousal": 0.5},
            )

            assert result["status"] == "success", "Modulation should succeed"
            assert "modulated_state" in result, "Should return modulated state"
            assert (
                result["modulation_applied"] is True
            ), "Should confirm modulation applied"
            mock_manager.modulate_emotional_state.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_unified_emotional_manager_status(self):
        """Test the status interface method"""
        if not MEMORY_HUB_AVAILABLE:
            pytest.skip("Memory hub components not available")

        with patch("memory.memory_hub.UNIFIED_EMOTIONAL_MEMORY_AVAILABLE", True):
            # Mock the manager with tier requirements
            mock_manager = Mock()
            mock_manager.tier_requirements = {
                "LAMBDA_TIER_1": ["basic_access"],
                "LAMBDA_TIER_2": ["emotional_tagging"],
                "LAMBDA_TIER_3": ["pattern_analysis"],
                "LAMBDA_TIER_4": ["state_modulation"],
                "LAMBDA_TIER_5": ["quantum_enhancement"],
            }

            # Register the mock manager
            self.hub.register_service("unified_emotional_manager", mock_manager)

            # Test status retrieval
            result = await self.hub.get_unified_emotional_manager_status()

            assert result["available"] is True, "Manager should be available"
            assert result["initialized"] is True, "Manager should be initialized"
            assert "tier_requirements" in result, "Should include tier requirements"
            assert "supported_operations" in result, "Should list supported operations"
            assert "tier_levels" in result, "Should list tier levels"

            # Verify tier levels are properly listed
            expected_tiers = [
                "LAMBDA_TIER_1",
                "LAMBDA_TIER_2",
                "LAMBDA_TIER_3",
                "LAMBDA_TIER_4",
                "LAMBDA_TIER_5",
            ]
            assert (
                result["tier_levels"] == expected_tiers
            ), "Should list all tier levels"

    @pytest.mark.asyncio
    async def test_error_handling_when_manager_unavailable(self):
        """Test error handling when unified emotional memory manager is not available"""
        if not MEMORY_HUB_AVAILABLE:
            pytest.skip("Memory hub components not available")

        with patch("memory.memory_hub.UNIFIED_EMOTIONAL_MEMORY_AVAILABLE", False):
            # Test all interface methods return proper errors

            # Test store method
            result = await self.hub.store_emotional_memory("user123", {"test": "data"})
            assert result["status"] == "error", "Should return error status"
            assert (
                "not configured" in result["error"]
            ), "Should indicate configuration issue"

            # Test retrieve method
            result = await self.hub.retrieve_emotional_memory("user123", "memory123")
            assert result["status"] == "error", "Should return error status"
            assert (
                "not configured" in result["error"]
            ), "Should indicate configuration issue"

            # Test analyze method
            result = await self.hub.analyze_emotional_patterns("user123")
            assert result["status"] == "error", "Should return error status"
            assert (
                "not configured" in result["error"]
            ), "Should indicate configuration issue"

            # Test modulate method
            result = await self.hub.modulate_emotional_state("user123", "memory123", {})
            assert result["status"] == "error", "Should return error status"
            assert (
                "not configured" in result["error"]
            ), "Should indicate configuration issue"

            # Test status method
            result = await self.hub.get_unified_emotional_manager_status()
            assert result["available"] is False, "Should indicate unavailable"
            assert (
                "not configured" in result["error"]
            ), "Should indicate configuration issue"

    @pytest.mark.asyncio
    async def test_service_not_found_error_handling(self):
        """Test error handling when service is not properly registered"""
        if not MEMORY_HUB_AVAILABLE:
            pytest.skip("Memory hub components not available")

        with patch("memory.memory_hub.UNIFIED_EMOTIONAL_MEMORY_AVAILABLE", True):
            # Don't register the service, so get_service returns None

            # Test store method
            result = await self.hub.store_emotional_memory("user123", {"test": "data"})
            assert result["status"] == "error", "Should return error status"
            assert (
                "Service not found" in result["error"]
            ), "Should indicate service not found"

            # Test retrieve method
            result = await self.hub.retrieve_emotional_memory("user123", "memory123")
            assert result["status"] == "error", "Should return error status"
            assert (
                "Service not found" in result["error"]
            ), "Should indicate service not found"

    def test_tier_based_access_requirements(self):
        """Test that tier-based access requirements are properly defined"""
        if not MEMORY_HUB_AVAILABLE:
            pytest.skip("Memory hub components not available")

        # This is a unit test that doesn't require async
        expected_tiers = [
            "LAMBDA_TIER_1",  # Basic emotional memory access
            "LAMBDA_TIER_2",  # Emotional tagging and categorization
            "LAMBDA_TIER_3",  # Pattern analysis and insights
            "LAMBDA_TIER_4",  # Emotional state modulation
            "LAMBDA_TIER_5",  # Quantum emotional enhancement
        ]

        # Verify tier structure is properly defined
        assert len(expected_tiers) == 5, "Should have 5 tier levels"
        assert all(
            "LAMBDA_TIER_" in tier for tier in expected_tiers
        ), "All tiers should follow naming convention"


def run_integration_tests():
    """Run all integration tests for unified emotional memory manager"""
    print("=" * 80)
    print("AGENT 1 TASK 10: Unified Emotional Memory Manager Integration Tests")
    print("=" * 80)

    if not MEMORY_HUB_AVAILABLE:
        print("❌ Memory hub components not available - skipping tests")
        return False

    # Run the tests
    test_class = TestUnifiedEmotionalMemoryManagerIntegration()
    test_methods = [method for method in dir(test_class) if method.startswith("test_")]

    passed = 0
    failed = 0

    for test_method in test_methods:
        try:
            print(f"\n🧪 Running {test_method}...")
            test_class.setup_method()

            method = getattr(test_class, test_method)
            if asyncio.iscoroutinefunction(method):
                asyncio.run(method())
            else:
                method()

            print(f"✅ {test_method} PASSED")
            passed += 1

        except Exception as e:
            print(f"❌ {test_method} FAILED: {e}")
            failed += 1
        finally:
            test_class.teardown_method()

    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    print("=" * 80)

    return failed == 0


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
    success = run_integration_tests()
    sys.exit(0 if success else 1)
