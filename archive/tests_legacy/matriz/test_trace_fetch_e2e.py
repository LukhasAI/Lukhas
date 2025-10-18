"""
Comprehensive test suite for GET /v1/matriz/trace/{trace_id} endpoint.

This test suite validates the trace fetching API endpoint including:
- Authentication and authorization
- Trace retrieval functionality
- Error handling for various scenarios
- Response model validation
- Integration with TraceMemoryLogger
- Health check and recent traces endpoints

Author: LUKHAS AI Testing Team
Created: 2025-08-27
Version: 1.0.0
"""

import json
import os
import tempfile
import time
import unittest
import uuid
from datetime import datetime, timezone
from typing import Any

from starlette.testclient import TestClient

# Import the FastAPI app from serve module
from serve.main import app

# Import models for validation
from serve.models.trace_models import (
    ExecutionTraceResponse,
    TraceErrorResponse,
    TraceNotFoundResponse,
    TraceValidationErrorResponse,
)

# Import storage provider for test data setup
from serve.storage.trace_provider import (
    FileTraceStorageProvider,
    reset_default_trace_provider,
)

# Try to import TraceMemoryLogger, handle gracefully if not available
try:
    from core.orchestration.brain.trace_memory_logger import TraceMemoryLogger
except ImportError:
    TraceMemoryLogger = None


class TestTraceAPI(unittest.TestCase):
    """Test suite for the MATRIZ trace API endpoints."""

    def setUp(self):
        """Set up test client, temporary storage, and authentication credentials."""
        # Reset the storage provider singleton to ensure clean state
        reset_default_trace_provider()

        # Initialize test client
        self.client = TestClient(app)

        # Create temporary directory for test traces
        self.temp_dir = tempfile.mkdtemp()
        self.storage_location = os.path.join(self.temp_dir, "traces")
        os.makedirs(self.storage_location, exist_ok=True)

        # Set up environment variables for testing
        os.environ["LUKHAS_TRACE_STORAGE"] = self.storage_location
        os.environ["LUKHAS_API_KEY"] = "test_api_key_12345"

        # Authentication headers
        self.valid_auth_headers = {"X-API-Key": "test_api_key_12345"}
        self.invalid_auth_headers = {"X-API-Key": "invalid_key"}
        self.no_auth_headers = {}

        # Initialize storage provider
        self.storage_provider = FileTraceStorageProvider(self.storage_location)

        # Create test traces
        self.test_traces = self._create_test_traces()

    def tearDown(self):
        """Clean up temporary files and reset environment variables."""
        # Clean up temporary directory
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

        # Reset environment variables
        if "LUKHAS_TRACE_STORAGE" in os.environ:
            del os.environ["LUKHAS_TRACE_STORAGE"]
        if "LUKHAS_API_KEY" in os.environ:
            del os.environ["LUKHAS_API_KEY"]

    def _create_test_traces(self) -> list[dict[str, Any]]:
        """
        Create dummy trace data for testing.

        Returns:
            List of test trace dictionaries
        """
        traces = []
        current_time = datetime.now(timezone.utc)

        for i in range(5):
            trace_id = str(uuid.uuid4())
            trace_data = {
                "trace_id": trace_id,
                "timestamp": current_time.isoformat(),
                "unix_time": current_time.timestamp(),
                "level": i % 8,  # Levels 0-7
                "level_name": [
                    "SYSTEM",
                    "CORE",
                    "SYMBOLIC",
                    "EMOTIONAL",
                    "ETHICAL",
                    "INTERACTION",
                    "DEBUG",
                    "VERBOSE",
                ][i % 8],
                "message": f"Test trace message {i}",
                "source_component": f"test_component_{i}",
                "tags": [f"test_tag_{i}", "automated_test"],
                "metadata": {"test_run": True, "sequence_number": i, "test_type": "unit_test"},
                "emotional": {
                    "valence": 0.5 + (i * 0.1),
                    "arousal": 0.3 + (i * 0.05),
                    "dominance": 0.4 + (i * 0.02),
                },
                "ethical_score": min(1.0, 0.8 + (i * 0.05)),
                "execution_context": {
                    "environment": "test",
                    "user_id": f"test_user_{i}",
                    "session_id": f"test_session_{i}",
                },
                "performance_metrics": {
                    "execution_time_ms": 10.5 + i,
                    "memory_usage_mb": 5.2 + (i * 0.5),
                },
                "related_traces": [] if i == 0 else [traces[i - 1]["trace_id"]],
            }
            traces.append(trace_data)

        # Write traces to storage using JSONL format
        all_traces_file = os.path.join(self.storage_location, "all_traces.jsonl")
        with open(all_traces_file, "w") as f:
            for trace in traces:
                f.write(json.dumps(trace) + "\n")

        return traces

    def test_fetch_existing_trace_success(self):
        """
        Test successful retrieval of an existing trace.

        Verifies:
        - 200 status code
        - All expected fields present in response
        - Correct trace data returned
        - Proper response model validation
        """
        # Get the first test trace ID
        test_trace = self.test_traces[0]
        trace_id = test_trace["trace_id"]

        # Make request to fetch trace
        response = self.client.get(f"/v1/matriz/trace/{trace_id}", headers=self.valid_auth_headers)

        # Verify successful response
        self.assertEqual(response.status_code, 200)

        # Parse response data
        response_data = response.json()

        # Verify all required fields are present
        expected_fields = [
            "trace_id",
            "timestamp",
            "unix_time",
            "level",
            "level_name",
            "message",
            "source_component",
            "tags",
            "metadata",
            "emotional",
            "ethical_score",
            "execution_context",
            "performance_metrics",
            "related_traces",
        ]

        for field in expected_fields:
            self.assertIn(field, response_data, f"Field '{field}' missing from response")

        # Verify specific field values match test data
        self.assertEqual(response_data["trace_id"], trace_id)
        self.assertEqual(response_data["message"], test_trace["message"])
        self.assertEqual(response_data["level"], test_trace["level"])
        self.assertEqual(response_data["source_component"], test_trace["source_component"])
        self.assertEqual(response_data["tags"], test_trace["tags"])

        # Verify nested objects
        self.assertIsInstance(response_data["metadata"], dict)
        self.assertIsInstance(response_data["emotional"], dict)
        self.assertIsInstance(response_data["execution_context"], dict)
        self.assertIsInstance(response_data["performance_metrics"], dict)

        # Verify Pydantic model validation by creating response object
        trace_response = ExecutionTraceResponse(**response_data)
        self.assertEqual(trace_response.trace_id, trace_id)

    def test_fetch_nonexistent_trace_404(self):
        """
        Test requesting a trace that doesn't exist returns 404.

        Verifies:
        - 404 status code
        - Proper error message format
        - TraceNotFoundResponse model structure
        """
        # Generate a random UUID that doesn't exist
        nonexistent_id = str(uuid.uuid4())

        # Make request for nonexistent trace
        response = self.client.get(f"/v1/matriz/trace/{nonexistent_id}", headers=self.valid_auth_headers)

        # Verify 404 response
        self.assertEqual(response.status_code, 404)

        # Parse error response
        error_data = response.json()

        # Verify error response structure
        self.assertIn("error", error_data)
        self.assertIn("message", error_data)
        self.assertIn("trace_id", error_data)

        self.assertEqual(error_data["error"], "trace_not_found")
        self.assertEqual(error_data["trace_id"], nonexistent_id)
        self.assertIn("No trace found", error_data["message"])

        # Verify Pydantic model validation
        error_response = TraceNotFoundResponse(**error_data)
        self.assertEqual(error_response.trace_id, nonexistent_id)

    def test_fetch_invalid_uuid_400(self):
        """
        Test requesting a trace with malformed UUID returns 400.

        Verifies:
        - 400 status code
        - Validation error message
        - TraceValidationErrorResponse model structure
        """
        # Use malformed UUID
        invalid_id = "not-a-valid-uuid"

        # Make request with invalid UUID
        response = self.client.get(f"/v1/matriz/trace/{invalid_id}", headers=self.valid_auth_headers)

        # Verify 400 response
        self.assertEqual(response.status_code, 400)

        # Parse error response
        error_data = response.json()

        # Verify validation error structure (FastAPI wraps in 'detail')
        if "detail" in error_data:
            error_detail = error_data["detail"]
            self.assertIn("error", error_detail)
            self.assertIn("message", error_detail)
            self.assertIn("field", error_detail)
            self.assertIn("value", error_detail)

            self.assertEqual(error_detail["error"], "validation_error")
            self.assertEqual(error_detail["field"], "trace_id")
            self.assertEqual(error_detail["value"], invalid_id)
            self.assertIn("Invalid trace ID format", error_detail["message"])
        else:
            self.assertIn("error", error_data)
            self.assertEqual(error_data["error"], "validation_error")

    def test_fetch_trace_authentication_required(self):
        """
        Test that trace endpoint requires authentication when API key is configured.

        Verifies:
        - 401 status code when no auth header provided
        - Proper error message format
        """
        # Get test trace ID
        trace_id = self.test_traces[0]["trace_id"]

        # Make request without authentication
        response = self.client.get(f"/v1/matriz/trace/{trace_id}")

        # Verify 401 response
        self.assertEqual(response.status_code, 401)

        # Parse error response
        error_data = response.json()

        # Verify error structure (FastAPI wraps custom errors in 'detail')
        if "detail" in error_data:
            error_detail = error_data["detail"]
            self.assertIn("error", error_detail)
            self.assertIn("message", error_detail)
            self.assertEqual(error_detail["error"], "unauthorized")
        else:
            self.assertIn("error", error_data)
            self.assertEqual(error_data["error"], "unauthorized")

    def test_fetch_trace_invalid_auth_401(self):
        """
        Test that trace endpoint rejects invalid authentication.

        Verifies:
        - 401 status code with invalid credentials
        - Proper error handling
        """
        # Get test trace ID
        trace_id = self.test_traces[0]["trace_id"]

        # Make request with invalid authentication
        response = self.client.get(f"/v1/matriz/trace/{trace_id}", headers=self.invalid_auth_headers)

        # Verify 401 response
        self.assertEqual(response.status_code, 401)

        # Parse error response
        error_data = response.json()

        # Verify error structure (FastAPI wraps custom errors in 'detail')
        if "detail" in error_data:
            error_detail = error_data["detail"]
            self.assertIn("error", error_detail)
            self.assertEqual(error_detail["error"], "unauthorized")
        else:
            self.assertIn("error", error_data)
            self.assertEqual(error_data["error"], "unauthorized")

    def test_fetch_recent_traces_endpoint(self):
        """
        Test the /v1/matriz/trace/recent endpoint functionality.

        Verifies:
        - Successful response with valid auth
        - Returns list of traces
        - Respects limit parameter
        - Optional filtering by level and tag
        """
        # Test basic recent traces request
        response = self.client.get("/v1/matriz/trace/recent", headers=self.valid_auth_headers)

        # Verify successful response
        self.assertEqual(response.status_code, 200)

        # Parse response
        traces = response.json()

        # Verify response is a list
        self.assertIsInstance(traces, list)

        # Verify traces have expected structure
        if traces:  # Only check if traces exist
            first_trace = traces[0]
            expected_fields = ["trace_id", "timestamp", "level", "message", "source_component"]
            for field in expected_fields:
                self.assertIn(field, first_trace)

        # Test with limit parameter
        response_limited = self.client.get("/v1/matriz/trace/recent?limit=2", headers=self.valid_auth_headers)

        self.assertEqual(response_limited.status_code, 200)
        limited_traces = response_limited.json()
        self.assertLessEqual(len(limited_traces), 2)

        # Test with level filter
        response_filtered = self.client.get("/v1/matriz/trace/recent?level=0", headers=self.valid_auth_headers)

        self.assertEqual(response_filtered.status_code, 200)
        filtered_traces = response_filtered.json()

        # Verify all returned traces have the requested level
        for trace in filtered_traces:
            self.assertEqual(trace["level"], 0)

    def test_fetch_trace_health_check(self):
        """
        Test the /v1/matriz/trace/health endpoint functionality.

        Verifies:
        - Health check returns status information
        - Contains expected health metrics
        - Responds appropriately to storage status
        """
        # Make health check request
        response = self.client.get("/v1/matriz/trace/health")

        # Verify response (should work without auth for health check)
        self.assertIn(response.status_code, [200, 503])  # Healthy or unhealthy

        # Parse response
        health_data = response.json()

        # Verify health response structure
        self.assertIn("status", health_data)
        self.assertIn(health_data["status"], ["healthy", "unhealthy"])

        # If healthy, verify additional metrics are present
        if health_data["status"] == "healthy":
            expected_fields = ["storage_location", "storage_accessible"]
            for field in expected_fields:
                self.assertIn(field, health_data)

    def test_storage_provider_integration(self):
        """
        Test that the storage provider integration is working correctly.

        Verifies:
        - Storage provider can be instantiated
        - Test data is properly written and readable
        - Health check functionality works
        """
        # Test storage provider initialization
        provider = FileTraceStorageProvider(self.storage_location)
        self.assertIsNotNone(provider)

        # Test health check
        import asyncio

        health_result = asyncio.run(provider.health_check())
        self.assertIn("status", health_result)

        # Test trace retrieval
        if self.test_traces:
            trace_id = self.test_traces[0]["trace_id"]
            trace_data = asyncio.run(provider.get_trace_by_id(trace_id))

            # Should find the trace if TraceMemoryLogger is available
            if TraceMemoryLogger is not None:
                self.assertIsNotNone(trace_data)
                self.assertEqual(trace_data["trace_id"], trace_id)

    def test_trace_response_model_validation(self):
        """
        Test Pydantic model validation for trace responses.

        Verifies:
        - ExecutionTraceResponse validates correctly with full data
        - TraceNotFoundResponse validates error responses
        - TraceErrorResponse handles general errors
        - TraceValidationErrorResponse handles validation errors
        """
        # Test ExecutionTraceResponse with full trace data
        trace_data = self.test_traces[0]
        trace_response = ExecutionTraceResponse(**trace_data)

        # Verify required fields
        self.assertEqual(trace_response.trace_id, trace_data["trace_id"])
        self.assertEqual(trace_response.message, trace_data["message"])
        self.assertEqual(trace_response.level, trace_data["level"])

        # Test TraceNotFoundResponse
        not_found_data = {
            "error": "trace_not_found",
            "message": "Test not found message",
            "trace_id": str(uuid.uuid4()),
        }
        not_found_response = TraceNotFoundResponse(**not_found_data)
        self.assertEqual(not_found_response.error, "trace_not_found")

        # Test TraceErrorResponse
        error_data = {
            "error": "internal_error",
            "message": "Test error message",
            "details": {"test": "data"},
        }
        error_response = TraceErrorResponse(**error_data)
        self.assertEqual(error_response.error, "internal_error")

        # Test TraceValidationErrorResponse
        validation_error_data = {
            "error": "validation_error",
            "message": "Test validation error",
            "field": "test_field",
            "value": "test_value",
        }
        validation_response = TraceValidationErrorResponse(**validation_error_data)
        self.assertEqual(validation_response.field, "test_field")

    def test_edge_cases_and_error_handling(self):
        """
        Test edge cases and comprehensive error handling.

        Verifies:
        - Very long trace IDs
        - Special characters in trace IDs
        - Boundary conditions for limits
        - Malformed JSON responses are handled gracefully
        """
        # Test with very long string as trace ID
        very_long_id = "a" * 1000
        response = self.client.get(f"/v1/matriz/trace/{very_long_id}", headers=self.valid_auth_headers)
        self.assertEqual(response.status_code, 400)  # Should be validation error

        # Test with special characters
        special_char_id = "trace@#$%^&*()"
        response = self.client.get(f"/v1/matriz/trace/{special_char_id}", headers=self.valid_auth_headers)
        self.assertEqual(response.status_code, 400)  # Should be validation error

        # Test recent traces with invalid level
        response = self.client.get("/v1/matriz/trace/recent?level=999", headers=self.valid_auth_headers)
        self.assertEqual(response.status_code, 400)  # Should be validation error

        # Test recent traces with excessive limit
        response = self.client.get("/v1/matriz/trace/recent?limit=10000", headers=self.valid_auth_headers)
        self.assertEqual(response.status_code, 200)
        # Limit should be capped at 100
        traces = response.json()
        self.assertLessEqual(len(traces), 100)

    def test_concurrent_trace_access(self):
        """
        Test concurrent access to trace endpoints to ensure thread safety.

        Verifies:
        - Multiple simultaneous requests don't cause issues
        - Consistent responses under load
        """
        import threading

        # Test data
        trace_id = self.test_traces[0]["trace_id"]
        results = []
        errors = []

        def make_request():
            try:
                response = self.client.get(f"/v1/matriz/trace/{trace_id}", headers=self.valid_auth_headers)
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))

        # Create multiple threads
        threads = []
        for _i in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # Verify results
        self.assertEqual(len(errors), 0, f"Concurrent access errors: {errors}")
        self.assertTrue(all(status == 200 for status in results), f"Some requests failed: {results}")


class TestTraceAPIWithoutAuth(unittest.TestCase):
    """Test suite for trace API when authentication is not configured."""

    def setUp(self):
        """Set up test client without authentication requirements."""
        # Reset the storage provider singleton to ensure clean state
        reset_default_trace_provider()

        self.client = TestClient(app)

        # Create temporary directory for test traces
        self.temp_dir = tempfile.mkdtemp()
        self.storage_location = os.path.join(self.temp_dir, "traces")
        os.makedirs(self.storage_location, exist_ok=True)

        # Don't set LUKHAS_API_KEY to test unauthenticated access
        os.environ.pop("LUKHAS_API_KEY", None)
        os.environ["LUKHAS_TRACE_STORAGE"] = self.storage_location

        # Create minimal test trace
        self.test_trace_id = str(uuid.uuid4())
        trace_data = {
            "trace_id": self.test_trace_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "unix_time": time.time(),
            "level": 0,
            "level_name": "SYSTEM",
            "message": "Test trace without auth",
            "source_component": "test",
            "tags": ["test"],
            "metadata": {},
            "emotional": None,
            "ethical_score": None,
        }

        # Write test trace
        all_traces_file = os.path.join(self.storage_location, "all_traces.jsonl")
        with open(all_traces_file, "w") as f:
            f.write(json.dumps(trace_data) + "\n")

    def tearDown(self):
        """Clean up temporary files."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

        if "LUKHAS_TRACE_STORAGE" in os.environ:
            del os.environ["LUKHAS_TRACE_STORAGE"]

    def test_trace_access_without_required_auth(self):
        """
        Test trace access when no authentication is required.

        Verifies that endpoints work when LUKHAS_API_KEY is not set.
        """
        # Test trace retrieval without auth headers
        response = self.client.get(f"/v1/matriz/trace/{self.test_trace_id}")

        # Should succeed when no API key is configured
        self.assertEqual(response.status_code, 200)

        # Test health check
        response = self.client.get("/v1/matriz/trace/health")
        self.assertIn(response.status_code, [200, 503])

        # Test recent traces
        response = self.client.get("/v1/matriz/trace/recent")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    # Run the test suite
    unittest.main(verbosity=2)
