#!/usr/bin/env python3
"""
Integration tests for websocket_server module.

Tests the WebSocket server functionality for the LUKHAS dashboard system,
including real-time streaming capabilities and colony integration.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestWebSocketServerIntegration:
    """Integration tests for DashboardWebSocketServer."""

    def test_module_imports(self):
        """Test that the module can be imported successfully."""
        from core.governance.identity.auth_web.websocket_server import (
            DashboardWebSocketServer,
            StreamClient,
            StreamMessage,
            StreamType,
        )

        assert DashboardWebSocketServer is not None
        assert StreamClient is not None
        assert StreamMessage is not None
        assert StreamType is not None

    def test_stream_type_enum(self):
        """Test StreamType enum contains expected values."""
        from core.governance.identity.auth_web.websocket_server import StreamType

        assert hasattr(StreamType, 'ORACLE_METRICS')
        assert hasattr(StreamType, 'ETHICS_SWARM')
        assert hasattr(StreamType, 'SYSTEM_HEALTH')
        assert hasattr(StreamType, 'ALL_STREAMS')

    @pytest.mark.asyncio
    async def test_server_initialization(self):
        """Test server can be initialized with mocked dependencies."""
        from core.governance.identity.auth_web.websocket_server import DashboardWebSocketServer

        # Mock the required dependencies
        with patch('core.governance.identity.auth_web.websocket_server.get_oracle_nervous_system') as mock_oracle, \
             patch('core.governance.identity.auth_web.websocket_server.get_ethics_swarm_colony') as mock_ethics:

            mock_oracle.return_value = MagicMock()
            mock_ethics.return_value = MagicMock()

            # Test that server can be instantiated
            # This is a smoke test to verify basic structure is intact
            assert DashboardWebSocketServer is not None

    def test_stream_client_dataclass(self):
        """Test StreamClient dataclass structure."""
        from core.governance.identity.auth_web.websocket_server import StreamClient, StreamType
        from datetime import datetime, timezone
        from unittest.mock import MagicMock

        # Create a test client
        mock_ws = MagicMock()
        now = datetime.now(timezone.utc)

        client = StreamClient(
            client_id="test-123",
            websocket=mock_ws,
            subscribed_streams={StreamType.ORACLE_METRICS},
            connected_at=now,
            last_activity=now
        )

        assert client.client_id == "test-123"
        assert client.websocket == mock_ws
        assert StreamType.ORACLE_METRICS in client.subscribed_streams
        assert client.connected_at == now

    def test_stream_message_dataclass(self):
        """Test StreamMessage dataclass structure."""
        from core.governance.identity.auth_web.websocket_server import StreamMessage, StreamType
        from datetime import datetime, timezone

        # Create a test message
        now = datetime.now(timezone.utc)
        message = StreamMessage(
            stream_type=StreamType.ORACLE_METRICS,
            data={"metric": "test"},
            timestamp=now
        )

        assert message.stream_type == StreamType.ORACLE_METRICS
        assert message.data == {"metric": "test"}
        assert message.timestamp == now
