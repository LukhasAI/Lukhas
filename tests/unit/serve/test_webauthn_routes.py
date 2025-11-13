"""
Comprehensive unit tests for serve/webauthn_routes.py

Tests WebAuthn API endpoints including:
- Challenge creation
- Response verification
- Request validation
- Error handling
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from serve.webauthn_routes import (
    ChallengeRequest,
    VerifyRequest,
    create_challenge,
    router,
    verify_response,
)


# Create a test client for the router
@pytest.fixture
def client():
    """Fixture providing a FastAPI test client."""
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestChallengeRequest:
    """Test ChallengeRequest schema validation."""

    def test_valid_challenge_request(self):
        """Test creating valid ChallengeRequest."""
        request = ChallengeRequest(
            user_id="test_user",
            rp_id="example.com",
            origin="https://example.com",
        )
        assert request.user_id == "test_user"
        assert request.rp_id == "example.com"
        assert request.origin == "https://example.com"

    def test_whitespace_stripping(self):
        """Test that whitespace is stripped from fields."""
        request = ChallengeRequest(
            user_id="  test_user  ",
            rp_id="  example.com  ",
            origin="  https://example.com  ",
        )
        assert request.user_id == "test_user"
        assert request.rp_id == "example.com"
        assert request.origin == "https://example.com"

    def test_missing_user_id_raises_validation_error(self):
        """Test that missing user_id raises ValidationError."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            ChallengeRequest(
                rp_id="example.com",
                origin="https://example.com",
            )

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("user_id",) for e in errors)

    def test_empty_user_id_raises_validation_error(self):
        """Test that empty user_id raises ValidationError."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            ChallengeRequest(
                user_id="",
                rp_id="example.com",
                origin="https://example.com",
            )

    def test_empty_rp_id_raises_validation_error(self):
        """Test that empty rp_id raises ValidationError."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            ChallengeRequest(
                user_id="test_user",
                rp_id="",
                origin="https://example.com",
            )

    def test_empty_origin_raises_validation_error(self):
        """Test that empty origin raises ValidationError."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            ChallengeRequest(
                user_id="test_user",
                rp_id="example.com",
                origin="",
            )

    def test_extra_fields_forbidden(self):
        """Test that extra fields are forbidden."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            ChallengeRequest(
                user_id="test_user",
                rp_id="example.com",
                origin="https://example.com",
                extra_field="not allowed",
            )

        errors = exc_info.value.errors()
        assert any("extra_forbidden" in str(e["type"]) for e in errors)


class TestVerifyRequest:
    """Test VerifyRequest schema validation."""

    def test_valid_verify_request_minimal(self):
        """Test creating valid VerifyRequest without expected_challenge."""
        request = VerifyRequest(
            response={"challenge": "test-challenge", "user_verified": True}
        )
        assert request.response["challenge"] == "test-challenge"
        assert request.expected_challenge is None

    def test_valid_verify_request_with_expected_challenge(self):
        """Test creating valid VerifyRequest with expected_challenge."""
        request = VerifyRequest(
            response={"challenge": "test-challenge"},
            expected_challenge="expected-challenge",
        )
        assert request.expected_challenge == "expected-challenge"

    def test_empty_response_dict(self):
        """Test VerifyRequest with empty response dict."""
        request = VerifyRequest(response={})
        assert request.response == {}

    def test_complex_response_object(self):
        """Test VerifyRequest with complex response object."""
        complex_response = {
            "challenge": "test-challenge",
            "user_verified": True,
            "authenticatorData": "base64-data",
            "signature": "base64-signature",
            "clientDataJSON": "base64-json",
        }
        request = VerifyRequest(response=complex_response)
        assert request.response["authenticatorData"] == "base64-data"

    def test_missing_response_raises_validation_error(self):
        """Test that missing response raises ValidationError."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            VerifyRequest(expected_challenge="test")

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("response",) for e in errors)

    def test_extra_fields_forbidden(self):
        """Test that extra fields are forbidden."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            VerifyRequest(
                response={"challenge": "test"},
                expected_challenge="test",
                extra_field="not allowed",
            )

        errors = exc_info.value.errors()
        assert any("extra_forbidden" in str(e["type"]) for e in errors)


class TestCreateChallengeEndpoint:
    """Test create_challenge endpoint."""

    @pytest.mark.asyncio
    async def test_create_challenge_success(self):
        """Test successful challenge creation."""
        with patch("serve.webauthn_routes.webauthn_adapter") as mock_adapter:
            mock_adapter.start_challenge.return_value = {
                "challenge": "test-challenge-123",
                "rpId": "example.com",
                "origin": "https://example.com",
                "user": {
                    "id": "dGVzdF91c2Vy",
                    "name": "test_user",
                    "displayName": "test_user",
                },
            }

            payload = ChallengeRequest(
                user_id="test_user",
                rp_id="example.com",
                origin="https://example.com",
            )

            result = await create_challenge(payload)

            assert result["challenge"] == "test-challenge-123"
            assert result["rpId"] == "example.com"
            mock_adapter.start_challenge.assert_called_once_with(
                user_id="test_user",
                rp_id="example.com",
                origin="https://example.com",
            )

    @pytest.mark.asyncio
    async def test_create_challenge_with_value_error(self):
        """Test challenge creation with ValueError from adapter."""
        with patch("serve.webauthn_routes.webauthn_adapter") as mock_adapter:
            mock_adapter.start_challenge.side_effect = ValueError("Invalid user_id")

            payload = ChallengeRequest(
                user_id="",
                rp_id="example.com",
                origin="https://example.com",
            )

            with pytest.raises(HTTPException) as exc_info:
                await create_challenge(payload)

            assert exc_info.value.status_code == 400
            assert "Invalid user_id" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_create_challenge_api_integration(self, client):
        """Test challenge creation via API."""
        with patch("serve.webauthn_routes.webauthn_adapter") as mock_adapter:
            mock_adapter.start_challenge.return_value = {
                "challenge": "api-challenge-123",
                "rpId": "example.com",
            }

            response = client.post(
                "/id/webauthn/challenge",
                json={
                    "user_id": "test_user",
                    "rp_id": "example.com",
                    "origin": "https://example.com",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["challenge"] == "api-challenge-123"

    @pytest.mark.asyncio
    async def test_create_challenge_invalid_payload(self, client):
        """Test challenge creation with invalid payload."""
        response = client.post(
            "/id/webauthn/challenge",
            json={
                "user_id": "",  # Empty user_id should fail validation
                "rp_id": "example.com",
                "origin": "https://example.com",
            },
        )

        assert response.status_code == 422  # Validation error


class TestVerifyResponseEndpoint:
    """Test verify_response endpoint."""

    @pytest.mark.asyncio
    async def test_verify_response_success(self):
        """Test successful response verification."""
        with patch("serve.webauthn_routes.webauthn_adapter") as mock_adapter:
            mock_adapter.verify_response.return_value = {
                "ok": True,
                "user_verified": True,
                "challenge_validated": True,
            }

            payload = VerifyRequest(
                response={
                    "challenge": "test-challenge",
                    "user_verified": True,
                },
                expected_challenge="test-challenge",
            )

            result = await verify_response(payload)

            assert result["ok"] is True
            assert result["user_verified"] is True
            mock_adapter.verify_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_verify_response_without_expected_challenge(self):
        """Test verification without expected_challenge."""
        with patch("serve.webauthn_routes.webauthn_adapter") as mock_adapter:
            mock_adapter.verify_response.return_value = {
                "ok": True,
                "user_verified": True,
            }

            payload = VerifyRequest(
                response={"challenge": "test-challenge"},
                expected_challenge=None,
            )

            result = await verify_response(payload)

            assert result["ok"] is True
            # Verify that expected_challenge=None was passed to adapter
            call_args = mock_adapter.verify_response.call_args
            assert call_args[1]["expected_challenge"] is None

    @pytest.mark.asyncio
    async def test_verify_response_failed_verification(self):
        """Test failed verification."""
        with patch("serve.webauthn_routes.webauthn_adapter") as mock_adapter:
            mock_adapter.verify_response.return_value = {
                "ok": False,
                "user_verified": False,
            }

            payload = VerifyRequest(
                response={"challenge": "wrong-challenge"},
                expected_challenge="expected-challenge",
            )

            result = await verify_response(payload)

            assert result["ok"] is False
            assert result["user_verified"] is False

    @pytest.mark.asyncio
    async def test_verify_response_with_type_error(self):
        """Test verification with TypeError from adapter."""
        with patch("serve.webauthn_routes.webauthn_adapter") as mock_adapter:
            mock_adapter.verify_response.side_effect = TypeError("Invalid response type")

            payload = VerifyRequest(
                response={"challenge": "test"},
            )

            with pytest.raises(HTTPException) as exc_info:
                await verify_response(payload)

            assert exc_info.value.status_code == 400
            assert "Invalid response type" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_verify_response_with_value_error(self):
        """Test verification with ValueError from adapter."""
        with patch("serve.webauthn_routes.webauthn_adapter") as mock_adapter:
            mock_adapter.verify_response.side_effect = ValueError("Missing challenge")

            payload = VerifyRequest(
                response={},
            )

            with pytest.raises(HTTPException) as exc_info:
                await verify_response(payload)

            assert exc_info.value.status_code == 400
            assert "Missing challenge" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_verify_response_api_integration(self, client):
        """Test response verification via API."""
        with patch("serve.webauthn_routes.webauthn_adapter") as mock_adapter:
            mock_adapter.verify_response.return_value = {
                "ok": True,
                "user_verified": True,
            }

            response = client.post(
                "/id/webauthn/verify",
                json={
                    "response": {
                        "challenge": "test-challenge",
                        "user_verified": True,
                    },
                    "expected_challenge": "test-challenge",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["ok"] is True
            assert data["user_verified"] is True

    @pytest.mark.asyncio
    async def test_verify_response_result_casting(self):
        """Test that result values are properly cast to bool."""
        with patch("serve.webauthn_routes.webauthn_adapter") as mock_adapter:
            # Return values that need casting
            mock_adapter.verify_response.return_value = {
                "ok": 1,  # Truthy int
                "user_verified": 0,  # Falsy int
            }

            payload = VerifyRequest(
                response={"challenge": "test"},
            )

            result = await verify_response(payload)

            # Should be cast to bool
            assert result["ok"] is True
            assert result["user_verified"] is False


class TestWebAuthnAdapterIntegration:
    """Test integration with webauthn_adapter."""

    @pytest.mark.asyncio
    async def test_challenge_creation_calls_adapter_correctly(self):
        """Test that challenge creation calls adapter with correct parameters."""
        with patch("serve.webauthn_routes.webauthn_adapter") as mock_adapter:
            mock_adapter.start_challenge.return_value = {"challenge": "test"}

            payload = ChallengeRequest(
                user_id="user123",
                rp_id="app.example.com",
                origin="https://app.example.com",
            )

            await create_challenge(payload)

            mock_adapter.start_challenge.assert_called_once_with(
                user_id="user123",
                rp_id="app.example.com",
                origin="https://app.example.com",
            )

    @pytest.mark.asyncio
    async def test_verify_calls_adapter_with_dict_response(self):
        """Test that verify calls adapter with dict (not Pydantic model)."""
        with patch("serve.webauthn_routes.webauthn_adapter") as mock_adapter:
            mock_adapter.verify_response.return_value = {"ok": True, "user_verified": True}

            payload = VerifyRequest(
                response={"challenge": "test", "extra": "data"},
            )

            await verify_response(payload)

            # Should pass dict, not Pydantic model
            call_args = mock_adapter.verify_response.call_args
            response_arg = call_args[1]["response"]
            assert isinstance(response_arg, dict)
            assert response_arg["challenge"] == "test"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_challenge_with_special_characters_in_user_id(self):
        """Test challenge creation with special characters in user_id."""
        with patch("serve.webauthn_routes.webauthn_adapter") as mock_adapter:
            mock_adapter.start_challenge.return_value = {"challenge": "test"}

            payload = ChallengeRequest(
                user_id="user+name@example.com",
                rp_id="example.com",
                origin="https://example.com",
            )

            result = await create_challenge(payload)
            assert result is not None

    @pytest.mark.asyncio
    async def test_challenge_with_subdomain_rp_id(self):
        """Test challenge creation with subdomain in rp_id."""
        with patch("serve.webauthn_routes.webauthn_adapter") as mock_adapter:
            mock_adapter.start_challenge.return_value = {"challenge": "test"}

            payload = ChallengeRequest(
                user_id="test_user",
                rp_id="app.subdomain.example.com",
                origin="https://app.subdomain.example.com",
            )

            result = await create_challenge(payload)
            assert result is not None

    @pytest.mark.asyncio
    async def test_verify_with_empty_response_dict(self):
        """Test verification with empty response dict."""
        with patch("serve.webauthn_routes.webauthn_adapter") as mock_adapter:
            mock_adapter.verify_response.side_effect = ValueError("Missing challenge")

            payload = VerifyRequest(response={})

            with pytest.raises(HTTPException) as exc_info:
                await verify_response(payload)

            assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_verify_with_complex_response_structure(self):
        """Test verification with complex nested response structure."""
        with patch("serve.webauthn_routes.webauthn_adapter") as mock_adapter:
            mock_adapter.verify_response.return_value = {
                "ok": True,
                "user_verified": True,
            }

            complex_response = {
                "challenge": "test",
                "authenticatorData": {"nested": {"data": "value"}},
                "clientDataJSON": {"type": "webauthn.get", "challenge": "test"},
            }

            payload = VerifyRequest(response=complex_response)

            result = await verify_response(payload)
            assert result["ok"] is True

    @pytest.mark.asyncio
    async def test_challenge_with_localhost_origin(self):
        """Test challenge creation with localhost origin."""
        with patch("serve.webauthn_routes.webauthn_adapter") as mock_adapter:
            mock_adapter.start_challenge.return_value = {"challenge": "test"}

            payload = ChallengeRequest(
                user_id="test_user",
                rp_id="localhost",
                origin="http://localhost:3000",
            )

            result = await create_challenge(payload)
            assert result is not None

    @pytest.mark.asyncio
    async def test_verify_result_handles_missing_user_verified(self):
        """Test that missing user_verified in adapter result is handled."""
        with patch("serve.webauthn_routes.webauthn_adapter") as mock_adapter:
            # Return result without user_verified field
            mock_adapter.verify_response.return_value = {
                "ok": True,
                # user_verified is missing
            }

            payload = VerifyRequest(
                response={"challenge": "test"},
            )

            result = await verify_response(payload)

            # Should default to False when missing
            assert "user_verified" in result
            assert isinstance(result["user_verified"], bool)


class TestRouterConfiguration:
    """Test router configuration and endpoints."""

    def test_router_exists(self):
        """Test that router is properly configured."""
        assert router is not None

    def test_challenge_endpoint_registered(self, client):
        """Test that challenge endpoint is registered."""
        # This will fail with 422 due to missing body, but shows endpoint exists
        response = client.post("/id/webauthn/challenge", json={})
        # 422 means validation error, endpoint exists
        assert response.status_code == 422

    def test_verify_endpoint_registered(self, client):
        """Test that verify endpoint is registered."""
        # This will fail with 422 due to missing body, but shows endpoint exists
        response = client.post("/id/webauthn/verify", json={})
        # 422 means validation error, endpoint exists
        assert response.status_code == 422
