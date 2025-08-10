"""
Integration tests for core LUKHAS modules.
"""

import pytest


@pytest.mark.integration
class TestCoreIntegration:
    """Test integration between core modules."""

    def test_memory_consciousness_integration(
        self, mock_consciousness, test_memory_entry
    ):
        """Test integration between memory and consciousness systems."""
        # Placeholder test
        assert mock_consciousness.awareness_level > 0
        assert test_memory_entry["id"] is not None

    def test_symbolic_emotion_integration(self, symbolic_state, emotion_vector):
        """Test integration between symbolic and emotion systems."""
        # Placeholder test
        assert len(symbolic_state["glyphs"]) > 0
        assert emotion_vector["valence"] >= 0

    def test_tag_propagation(self):
        """Test that symbolic tags are propagated through a colony."""
        import asyncio

        from core.colonies.reasoning_colony import ReasoningColony

        colony = ReasoningColony("test_colony")
        from core.symbolism.tags import TagPermission, TagScope

        task_data = {
            "type": "test_task",
            "tags": {
                "emotional_tone": (
                    "curious",
                    TagScope.LOCAL,
                    TagPermission.PUBLIC,
                    None,
                ),
                "directive_hash": (
                    "a1b2c3d4",
                    TagScope.GLOBAL,
                    TagPermission.PROTECTED,
                    3600,
                ),
            },
        }

        async def run_task():
            await colony.start()
            await colony.execute_task("test_task_id", task_data)
            await colony.stop()

        asyncio.run(run_task())

        from core.symbolism.tags import TagPermission, TagScope

        assert colony.symbolic_carryover["emotional_tone"][0] == "curious"
        assert colony.symbolic_carryover["emotional_tone"][1] == TagScope.LOCAL
        assert colony.symbolic_carryover["emotional_tone"][2] == TagPermission.PUBLIC
        assert colony.symbolic_carryover["directive_hash"][0] == "a1b2c3d4"
        assert colony.symbolic_carryover["directive_hash"][1] == TagScope.GLOBAL
        assert colony.symbolic_carryover["directive_hash"][2] == TagPermission.PROTECTED
        assert len(colony.tag_propagation_log) == 2
        assert colony.tag_propagation_log[0]["tag"] == "emotional_tone"
        assert colony.tag_propagation_log[0]["value"] == "curious"
        assert colony.tag_propagation_log[0]["scope"] == "local"
        assert colony.tag_propagation_log[0]["permission"] == "public"
        assert colony.tag_propagation_log[0]["source"] == "test_colony"

    def test_scoped_collision(self):
        """Test that tags with the same name but different scopes do not collide."""
        import asyncio

        from core.colonies.reasoning_colony import ReasoningColony
        from core.symbolism.tags import TagPermission, TagScope

        colony1 = ReasoningColony("colony1")
        colony2 = ReasoningColony("colony2")

        task_data1 = {
            "type": "test_task",
            "tags": {
                "test_tag": ("value1", TagScope.LOCAL, TagPermission.PRIVATE, None)
            },
        }

        task_data2 = {
            "type": "test_task",
            "tags": {
                "test_tag": ("value2", TagScope.GLOBAL, TagPermission.PUBLIC, None)
            },
        }

        async def run_tasks():
            await colony1.start()
            await colony2.start()
            await colony1.execute_task("task1", task_data1)
            await colony2.execute_task("task2", task_data2)
            colony1.link_symbolic_contexts(colony2)
            await colony1.stop()
            await colony2.stop()

        asyncio.run(run_tasks())

        assert colony1.symbolic_carryover["test_tag"][0] == "value2"
        assert colony1.symbolic_carryover["test_tag"][1] == TagScope.GLOBAL
        assert colony1.symbolic_carryover["test_tag"][2] == TagPermission.PUBLIC

    def test_tag_expiry(self):
        """Test that tags expire correctly."""
        import asyncio
        import time

        from core.colonies.reasoning_colony import ReasoningColony
        from core.symbolism.tags import TagPermission, TagScope

        colony = ReasoningColony("test_colony")

        task_data = {
            "type": "test_task",
            "tags": {
                "short_lived_tag": ("value", TagScope.LOCAL, TagPermission.PUBLIC, 0.1)
            },
        }

        async def run_task():
            await colony.start()
            await colony.execute_task("task1", task_data)
            time.sleep(0.2)
            colony.prune_expired_tags()
            await colony.stop()

        asyncio.run(run_task())

        assert "short_lived_tag" not in colony.symbolic_carryover

    def test_tag_escalation(self):
        """Test the tag escalation protocol."""
        import asyncio

        from core.colonies.reasoning_colony import ReasoningColony
        from core.symbolism.tags import TagPermission, TagScope

        colony = ReasoningColony("test_colony")

        task_data = {
            "type": "test_task",
            "tags": {
                "private_tag": (
                    "initial_value",
                    TagScope.LOCAL,
                    TagPermission.PRIVATE,
                    None,
                )
            },
        }

        async def run_task():
            await colony.start()
            await colony.execute_task("task1", task_data)

            # Try to override the private tag - should fail
            override_result = colony.override_tag(
                "private_tag", "new_value", TagScope.LOCAL, TagPermission.PUBLIC
            )
            assert not override_result
            assert colony.symbolic_carryover["private_tag"][0] == "initial_value"

            # Escalate the permission
            escalation_result = colony.request_permission_escalation(
                "private_tag", TagPermission.PROTECTED
            )
            assert escalation_result

            # Try to override again - should still fail because we haven't changed the permission yet
            override_result = colony.override_tag(
                "private_tag", "new_value", TagScope.LOCAL, TagPermission.PUBLIC
            )
            assert not override_result
            assert colony.symbolic_carryover["private_tag"][0] == "initial_value"

            # Manually override the permission for the test
            colony.symbolic_carryover["private_tag"] = (
                "initial_value",
                TagScope.LOCAL,
                TagPermission.PROTECTED,
                colony.symbolic_carryover["private_tag"][3],
                None,
            )

            # Try to override again - should succeed
            override_result = colony.override_tag(
                "private_tag", "new_value", TagScope.LOCAL, TagPermission.PUBLIC, None
            )
            assert override_result
            assert colony.symbolic_carryover["private_tag"][0] == "new_value"
            assert colony.symbolic_carryover["private_tag"][2] == TagPermission.PUBLIC

            await colony.stop()

        asyncio.run(run_task())
