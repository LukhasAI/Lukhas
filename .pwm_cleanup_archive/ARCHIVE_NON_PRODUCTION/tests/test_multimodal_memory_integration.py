"""
Test suite for Multimodal Memory Integration
"""

from unittest.mock import AsyncMock

import pytest

from memory.memory_hub import MemoryHub
from memory.systems.multimodal_memory_integration import (
    MultimodalMemoryIntegration,
    create_multimodal_memory_integration,
)
from memory.systems.multimodal_memory_support import (
    ModalityType,
)


class TestMultimodalMemoryIntegration:
    """Test suite for multimodal memory integration with memory hub"""

    @pytest.fixture
    async def memory_hub(self):
        """Create a test memory hub instance"""
        hub = MemoryHub()
        return hub

    @pytest.fixture
    async def multimodal_integration(self):
        """Create a test multimodal memory integration instance"""
        config = {
            "enable_cross_modal_alignment": True,
            "unified_embedding_dim": 512,
            "modal_embedding_dim": 256,
            "max_memory_size_mb": 50,
        }
        integration = MultimodalMemoryIntegration(config)
        return integration

    @pytest.mark.asyncio
    async def test_multimodal_memory_registration(self, memory_hub):
        """Test that multimodal memory is registered in the hub"""
        # Verify multimodal memory service is registered
        assert "multimodal_memory" in memory_hub.services
        assert memory_hub.get_service("multimodal_memory") is not None

    @pytest.mark.asyncio
    async def test_multimodal_memory_initialization(self, memory_hub):
        """Test initialization of multimodal memory through hub"""
        # Initialize the hub
        await memory_hub.initialize()

        # Verify multimodal memory was initialized
        multimodal_service = memory_hub.get_service("multimodal_memory")
        assert multimodal_service is not None
        assert hasattr(multimodal_service, "is_initialized")
        assert multimodal_service.is_initialized is True

    @pytest.mark.asyncio
    async def test_modality_support_check(self, multimodal_integration):
        """Test checking supported modalities"""
        # Initialize the integration
        await multimodal_integration.initialize()

        # Get supported modalities
        supported = multimodal_integration.get_supported_modalities()

        # Verify structure
        assert isinstance(supported, dict)
        assert "text" in supported
        assert supported["text"] is True  # Text is always supported
        assert "image" in supported
        assert "audio" in supported
        assert "video" in supported

    @pytest.mark.asyncio
    async def test_create_text_memory(self, multimodal_integration):
        """Test creating a text-only memory"""
        # Initialize the integration
        await multimodal_integration.initialize()

        # Create text memory
        memory = await multimodal_integration.create_memory(
            text="This is a test memory",
            tags=["test", "text"],
            metadata={"source": "unit_test"},
        )

        # Verify memory structure
        assert "memory_id" in memory
        assert "modalities" in memory
        assert "text" in memory["modalities"]
        assert len(memory["modalities"]) == 1
        assert memory["tags"] == ["test", "text"]

    @pytest.mark.asyncio
    async def test_create_multimodal_memory(self, multimodal_integration):
        """Test creating a memory with multiple modalities"""
        # Initialize the integration
        await multimodal_integration.initialize()

        # Create sample data
        text_data = "Sample multimodal memory"
        image_data = b"fake_image_data"
        audio_data = b"fake_audio_data"

        # Create multimodal memory
        memory = await multimodal_integration.create_memory(
            text=text_data,
            image=image_data,
            audio=audio_data,
            tags=["multimodal", "test"],
        )

        # Verify memory structure
        assert "memory_id" in memory
        assert "modalities" in memory
        assert set(memory["modalities"]) == {"text", "image", "audio"}
        assert memory["tags"] == ["multimodal", "test"]

    @pytest.mark.asyncio
    async def test_retrieve_memory(self, multimodal_integration):
        """Test retrieving a stored memory"""
        # Initialize the integration
        await multimodal_integration.initialize()

        # Create a memory first
        memory = await multimodal_integration.create_memory(
            text="Retrievable memory", tags=["retrieval_test"]
        )

        memory_id = memory["memory_id"]

        # Retrieve the memory
        retrieved = await multimodal_integration.retrieve_memory(memory_id)

        # Verify retrieval
        assert retrieved is not None

    @pytest.mark.asyncio
    async def test_search_memories(self, multimodal_integration):
        """Test searching memories"""
        # Initialize the integration
        await multimodal_integration.initialize()

        # Create test memories
        await multimodal_integration.create_memory(
            text="Python programming tutorial", tags=["programming", "python"]
        )

        await multimodal_integration.create_memory(
            text="Machine learning basics", tags=["ml", "basics"]
        )

        # Search for memories
        results = await multimodal_integration.search_memories(
            query="python", modality=ModalityType.TEXT, top_k=5
        )

        # Verify search results
        assert isinstance(results, list)
        if len(results) > 0:
            assert "memory_id" in results[0]
            assert "score" in results[0]

    @pytest.mark.asyncio
    async def test_memory_statistics(self, multimodal_integration):
        """Test getting memory statistics"""
        # Initialize the integration
        await multimodal_integration.initialize()

        # Create some memories
        await multimodal_integration.create_memory(text="Text memory 1")
        await multimodal_integration.create_memory(
            text="Multimodal memory", image=b"fake_image"
        )

        # Get statistics
        stats = multimodal_integration.get_memory_statistics()

        # Verify statistics structure
        assert "total_memories" in stats
        assert stats["total_memories"] >= 2
        assert "modality_counts" in stats
        assert "total_size_mb" in stats

    @pytest.mark.asyncio
    async def test_awareness_update(self, multimodal_integration):
        """Test that multimodal memory responds to awareness updates"""
        # Initialize the integration
        await multimodal_integration.initialize()

        # Send awareness update
        awareness_state = {
            "level": "active",
            "timestamp": 12345.67,
            "connected_systems": 3,
            "memory_nodes": ["base", "quantum", "multimodal"],
        }

        # Update awareness
        await multimodal_integration.update_awareness(awareness_state)

        # Verify configuration was updated
        assert multimodal_integration.config["enable_cross_modal_alignment"] is True
        assert multimodal_integration.config["unified_embedding_dim"] == 1024

        # Test passive awareness
        awareness_state["level"] = "passive"
        await multimodal_integration.update_awareness(awareness_state)

        # Verify configuration was updated for passive mode
        assert multimodal_integration.config["enable_cross_modal_alignment"] is False
        assert multimodal_integration.config["unified_embedding_dim"] == 512

    @pytest.mark.asyncio
    async def test_memory_optimization(self, multimodal_integration):
        """Test memory optimization functionality"""
        # Initialize the integration
        await multimodal_integration.initialize()

        # Create some memories
        for i in range(5):
            await multimodal_integration.create_memory(
                text=f"Test memory {i}", tags=["optimization_test"]
            )

        # Run optimization
        await multimodal_integration.optimize_memory_storage()

        # This is mainly testing that optimization runs without error
        # In a real implementation, we could test actual optimization effects

    @pytest.mark.asyncio
    async def test_file_path_handling(self, multimodal_integration, tmp_path):
        """Test handling of file paths vs raw bytes"""
        # Initialize the integration
        await multimodal_integration.initialize()

        # Create a temporary file
        test_file = tmp_path / "test_data.txt"
        test_content = b"Test file content"
        test_file.write_bytes(test_content)

        # Test loading from path
        loaded_data = await multimodal_integration._load_file_if_path(str(test_file))
        assert loaded_data == test_content

        # Test with raw bytes
        raw_data = b"Raw byte data"
        loaded_raw = await multimodal_integration._load_file_if_path(raw_data)
        assert loaded_raw == raw_data

    @pytest.mark.asyncio
    async def test_hub_awareness_broadcast(self):
        """Test that memory hub broadcasts awareness to multimodal memory"""
        # Create hub with mocked multimodal service
        hub = MemoryHub()

        # Create mock multimodal service
        mock_multimodal = AsyncMock()
        mock_multimodal.update_awareness = AsyncMock()

        # Manually register the mock service
        hub.multimodal_memory = mock_multimodal
        hub.services["multimodal_memory"] = mock_multimodal

        # Broadcast awareness state
        await hub.broadcast_awareness_state()

        # Verify multimodal memory received the update
        mock_multimodal.update_awareness.assert_called_once()
        call_args = mock_multimodal.update_awareness.call_args[0][0]
        assert call_args["level"] == "active"
        assert "timestamp" in call_args
        assert "memory_nodes" in call_args

    @pytest.mark.asyncio
    async def test_configuration_options(self):
        """Test different configuration options"""
        # Test with custom config
        custom_config = {
            "enable_cross_modal_alignment": False,
            "unified_embedding_dim": 256,
            "max_memory_size_mb": 200,
            "image_quality": 95,
        }

        integration = create_multimodal_memory_integration(custom_config)

        # Verify config was applied
        assert integration.config["enable_cross_modal_alignment"] is False
        assert integration.config["unified_embedding_dim"] == 256
        assert integration.config["max_memory_size_mb"] == 200

    @pytest.mark.asyncio
    async def test_error_handling(self, multimodal_integration):
        """Test error handling in various scenarios"""
        # Test retrieving non-existent memory
        result = await multimodal_integration.retrieve_memory("non_existent_id")
        assert result is None

        # Test search with empty cache
        results = await multimodal_integration.search_memories("test query")
        assert isinstance(results, list)
        assert len(results) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
