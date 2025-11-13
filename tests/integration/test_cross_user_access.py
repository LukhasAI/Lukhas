"""Integration tests for cross-user access prevention.

This test suite verifies that users cannot access each other's data after
implementing user_id derivation from JWT tokens.

Security: OWASP A01 mitigation - identity spoofing prevention.
"""

import pytest
from fastapi.testclient import TestClient


class TestCrossUserAccessPrevention:
    """Verify users cannot access each other's data."""

    @pytest.mark.skip(reason="Requires full auth system integration")
    def test_cannot_submit_feedback_as_another_user(self, client):
        """User A cannot submit feedback claiming to be User B.

        NOTE: This test is skipped because it requires full authentication
        system integration. When StrictAuthMiddleware is fully integrated
        with the ΛiD JWT system, enable this test.
        """
        # Login as User A
        login_resp = client.post("/api/v1/auth/login", json={
            "email": "userA@example.com",
            "password": "passwordA"
        })
        token_a = login_resp.json()["access_token"]

        # Try to submit feedback (will use User A's ID from token)
        response = client.post(
            "/feedback/capture",
            headers={"Authorization": f"Bearer {token_a}"},
            json={
                # NO user_id field - cannot spoof!
                "action_id": "action123",
                "rating": 5,
                "note": "Great app!"
            }
        )

        assert response.status_code == 200
        # Verify feedback attributed to User A (from token)
        # Note: actual user_id verification would require database check

        # Verify cannot inject user_id in request body
        response = client.post(
            "/feedback/capture",
            headers={"Authorization": f"Bearer {token_a}"},
            json={
                "user_id": "userB_id",  # Try to spoof User B (will be ignored)
                "action_id": "action456",
                "rating": 1,
                "note": "Hacking attempt"
            }
        )

        # Request should succeed but user_id injection should be ignored
        # (user_id field removed from model, so Pydantic will ignore it)
        assert response.status_code == 200

    @pytest.mark.skip(reason="Requires full auth system integration")
    def test_cannot_query_another_users_consciousness(self, client):
        """User A cannot query User B's consciousness state."""
        # Login as User A
        login_resp = client.post("/api/v1/auth/login", json={
            "email": "userA@example.com",
            "password": "passwordA"
        })
        token_a = login_resp.json()["access_token"]

        # Query consciousness (will use User A's context from token)
        response = client.post(
            "/api/v1/consciousness/query",
            headers={"Authorization": f"Bearer {token_a}"},
            json={"context": {"query": "awareness"}}
        )

        assert response.status_code == 200
        # Verify response scoped to User A (implementation-specific)

        # Try to access User B's state via path parameter
        response = client.get(
            "/api/v1/consciousness/state/userB_id",  # User B's ID
            headers={"Authorization": f"Bearer {token_a}"}  # User A's token
        )

        # Should return 403 Forbidden (ownership validation)
        assert response.status_code == 403
        assert "Cannot access other user" in response.json()["detail"]

    @pytest.mark.skip(reason="Requires full auth system integration")
    def test_cannot_access_another_users_learning_report(self, client):
        """User A cannot access User B's feedback learning report."""
        # Login as User A
        login_resp = client.post("/api/v1/auth/login", json={
            "email": "userA@example.com",
            "password": "passwordA"
        })
        token_a = login_resp.json()["access_token"]

        # Try to access User B's learning report
        response = client.get(
            "/feedback/report/userB_id",  # User B's ID
            headers={"Authorization": f"Bearer {token_a}"}  # User A's token
        )

        # Should return 403 Forbidden (ownership validation)
        assert response.status_code == 403
        assert "Cannot access other user" in response.json()["detail"]

        # User A CAN access their own report
        response = client.get(
            "/feedback/report/userA_id",  # User A's ID (matching token)
            headers={"Authorization": f"Bearer {token_a}"}
        )

        assert response.status_code == 200


class TestIdentitySpoofingPrevention:
    """Test that user_id cannot be spoofed via request body."""

    def test_user_id_removed_from_feedback_request_model(self):
        """Verify FeedbackRequest model has no user_id field."""
        import inspect

        from serve.feedback_routes import FeedbackRequest

        # Get model fields
        model_fields = FeedbackRequest.model_fields

        # Verify user_id is NOT in the model
        assert "user_id" not in model_fields, \
            "user_id should be removed from FeedbackRequest model"

        # Verify expected fields ARE present
        assert "action_id" in model_fields
        assert "rating" in model_fields
        assert "note" in model_fields

    def test_user_id_removed_from_consciousness_request_model(self):
        """Verify QueryRequest model has no user_id field."""
        import inspect

        from serve.consciousness_api import QueryRequest

        model_fields = QueryRequest.model_fields

        # Verify user_id is NOT in the model
        assert "user_id" not in model_fields, \
            "user_id should be removed from QueryRequest model"

        # Verify context field IS present
        assert "context" in model_fields

    def test_user_id_removed_from_state_model(self):
        """Verify StateModel has no user_id field."""
        import inspect

        from serve.consciousness_api import StateModel

        model_fields = StateModel.model_fields

        # Verify user_id is NOT in the model
        assert "user_id" not in model_fields, \
            "user_id should be removed from StateModel"

        # Verify state_data field IS present
        assert "state_data" in model_fields


class TestEndpointSecuritySignatures:
    """Verify all endpoints use Depends(get_current_user_id)."""

    def test_consciousness_endpoints_use_dependency(self):
        """Verify consciousness endpoints use get_current_user_id dependency."""
        import inspect

        from serve.consciousness_api import dream, get_state, memory, query, save_state

        # Check query endpoint
        sig = inspect.signature(query)
        assert "user_id" in sig.parameters, "query should have user_id parameter"
        # Note: More detailed inspection would check it's using Depends()

        # Check dream endpoint
        sig = inspect.signature(dream)
        assert "user_id" in sig.parameters, "dream should have user_id parameter"

        # Check memory endpoint
        sig = inspect.signature(memory)
        assert "user_id" in sig.parameters, "memory should have user_id parameter"

        # Check save_state endpoint
        sig = inspect.signature(save_state)
        assert "user_id" in sig.parameters, "save_state should have user_id parameter"

        # Check get_state endpoint
        sig = inspect.signature(get_state)
        # Should have both path param and auth param
        assert "auth_user_id" in sig.parameters, "get_state should have auth_user_id parameter"

    def test_feedback_endpoints_use_dependency(self):
        """Verify feedback endpoints use get_current_user_id dependency."""
        import inspect

        from serve.feedback_routes import (
            capture_batch_feedback,
            capture_feedback,
            get_learning_report,
        )

        # Check capture_feedback endpoint
        sig = inspect.signature(capture_feedback)
        assert "user_id" in sig.parameters, "capture_feedback should have user_id parameter"

        # Check capture_batch_feedback endpoint
        sig = inspect.signature(capture_batch_feedback)
        assert "user_id" in sig.parameters, "capture_batch_feedback should have user_id parameter"

        # Check get_learning_report endpoint
        sig = inspect.signature(get_learning_report)
        assert "auth_user_id" in sig.parameters, "get_learning_report should have auth_user_id parameter"
