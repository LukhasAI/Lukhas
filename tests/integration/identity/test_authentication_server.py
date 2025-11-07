# tests/integration/identity/test_authentication_server.py

import asyncio
import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import nacl.encoding
import pytest
from nacl.signing import SigningKey

from governance.identity.auth_backend.authentication_server import (
    AuthenticationServer,
    DataSubjectRight,
)


@pytest.fixture
async def server():
    """Fixture to create an AuthenticationServer instance."""
    s = AuthenticationServer()
    await s.initialize()
    return s


@pytest.fixture
def signing_key():
    """Fixture to generate a signing key for tests."""
    return SigningKey.generate()


@pytest.fixture
def user_id():
    """Fixture for a test user ID."""
    return "test_user_123"


@pytest.mark.asyncio
async def test_session_creation_and_initial_message(server, user_id, signing_key):
    """
    T1.1: Verify session creation and initial handshake.
    """
    # Mock the websocket connection
    websocket = AsyncMock()
    websocket.recv.side_effect = [
        json.dumps(
            {
                "user_id": user_id,
                "device_public_key": signing_key.verify_key.encode(encoder=nacl.encoding.HexEncoder).decode("ascii"),
            }
        ),
        json.dumps({"type": "disconnect"}),
    ]

    # Mock the internal time and session ID generation for predictability
    server._get_datetime_now = MagicMock(return_value=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc))
    server._generate_session_id = MagicMock(return_value="test_session_id_123")

    # Run the client connection handler
    await server.handle_client_connection(websocket, "/")

    # Assert that a session was created
    assert "test_session_id_123" in server.active_sessions
    # Assert that the initial session ID message was sent
    websocket.send.assert_called_with(json.dumps({"session_id": "test_session_id_123"}))


@pytest.mark.asyncio
async def test_invalid_user_id_rejection(server):
    """
    T2.1: Ensure connection is rejected for invalid user ID.
    """
    websocket = AsyncMock()
    # Send handshake with an invalid (empty) user ID
    websocket.recv.return_value = json.dumps(
        {"user_id": "", "device_public_key": "a" * 64}
    )  # a 32-byte key hex-encoded

    await server.handle_client_connection(websocket, "/")

    # Assert an error message was sent and the connection was closed
    websocket.send.assert_called_with(json.dumps({"error": "Invalid user ID"}))
    assert not server.active_sessions


@pytest.mark.asyncio
async def test_rate_limit_exceeded(server, user_id, signing_key):
    """
    T3.1: Verify rate limiting on entropy updates.
    """
    # Setup a valid session
    server.active_sessions["test_session"] = MagicMock()
    server.device_verify_keys[user_id] = signing_key.verify_key

    # Mock the websocket to send rapid entropy updates
    payload = json.dumps({"device_id": user_id, "entropy_value": 0.5, "nonce": "nonce_1"})
    signature = signing_key.sign(payload.encode()).signature.hex()
    entropy_update_msg = json.dumps(
        {
            "type": "entropy_update",
            "payload": payload,
            "signed_packet": signature,
        }
    )

    # Make the first 10 calls succeed, then exceed the limit
    recv_side_effects = [entropy_update_msg] * 11 + [asyncio.sleep(10)]
    websocket = AsyncMock()
    websocket.recv.side_effect = recv_side_effects

    # Mock time to control rate limit window
    server._get_time = MagicMock(side_effect=[1.0] * 10 + [1.1])  # 11th call is within 10s

    # Mock replay protection to always succeed
    server.replay_protection.add_nonce = MagicMock(return_value=True)

    await server.handle_client_connection(websocket, "/")

    # Assert that the 11th message resulted in a rate limit error
    # Check the calls made to websocket.send
    error_call = json.dumps({"error": "Rate limit exceeded for device"})
    assert error_call in [call.args[0] for call in websocket.send.call_args_list]


@pytest.mark.asyncio
async def test_gdpr_data_access_request(server, user_id):
    """
    T4.1: Test GDPR data access request (Article 15).
    """
    # Initialize a privacy profile for the user
    await server.initialize_user_privacy_profile(user_id, jurisdiction="EU")

    # Mock datetime for consistent timestamps
    fixed_dt = datetime(2025, 6, 15, 10, 0, 0, tzinfo=timezone.utc)
    server._get_datetime_now = MagicMock(return_value=fixed_dt)

    # Perform the data access request
    result = await server.handle_data_subject_request(user_id, DataSubjectRight.ACCESS, {})

    # Assert the request was successful and contains expected data
    assert result["success"]
    assert result["request_id"] is not None
    assert "personal_data" in result["data"]
    assert "processing_information" in result["data"]
    assert result["data"]["personal_data"]["privacy_profile"]["jurisdiction"] == "EU"
    assert result["generated_at"] == fixed_dt.isoformat()


@pytest.mark.asyncio
async def test_session_expiry(server):
    """
    T5.1: Ensure inactive sessions are correctly expired.
    """
    # Mock time
    server._get_time = MagicMock(side_effect=[1000.0, 5000.0])  # Initial time, then much later time

    # Create an active session
    server.active_sessions["stale_session"] = MagicMock(last_active=1000.0)
    server.active_sessions["active_session"] = MagicMock(last_active=4000.0)

    server.expire_sessions()

    # Assert that the stale session was removed and the active one remains
    assert "stale_session" not in server.active_sessions
    assert "active_session" in server.active_sessions


def test_create_golden_file_on_successful_login(server, user_id, signing_key, tmp_path):
    """
    T6.1: Create a golden file for a successful login event for contract testing.
    """
    # Define a successful login event
    payload = json.dumps({"device_id": user_id, "entropy_value": 0.9, "nonce": "golden_nonce"})
    signature = signing_key.sign(payload.encode()).signature.hex()
    successful_login_event = {
        "type": "entropy_update",
        "payload": payload,
        "signed_packet": signature,
    }

    # Create golden file path
    golden_file_path = tmp_path / "successful_login_golden.json"

    # Write the successful event to the golden file
    with open(golden_file_path, "w") as f:
        json.dump(successful_login_event, f, indent=2)

    # Verify the file was created and has content
    assert golden_file_path.exists()
    with open(golden_file_path) as f:
        content = json.load(f)
        assert content == successful_login_event
