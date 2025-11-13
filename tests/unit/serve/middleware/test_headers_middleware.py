
import time

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from serve.middleware.headers import HeadersMiddleware

# A simple app to test the middleware
app = FastAPI()

# Add the middleware to the app
app.add_middleware(HeadersMiddleware)

# A simple endpoint
@app.get("/test")
async def dummy_route():
    return {"message": "Hello, world!"}

client = TestClient(app)

def test_headers_middleware():
    """Test that the HeadersMiddleware adds the expected headers to the response."""
    response = client.get("/test")

    assert response.status_code == 200

    # Check for the presence of the headers
    assert "X-Trace-Id" in response.headers
    assert "X-Request-Id" in response.headers
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert "X-RateLimit-Reset" in response.headers
    assert "x-ratelimit-limit-requests" in response.headers
    assert "x-ratelimit-remaining-requests" in response.headers
    assert "x-ratelimit-reset-requests" in response.headers

    # Check the values of the headers
    assert response.headers["X-Trace-Id"] == response.headers["X-Request-Id"]
    assert response.headers["X-RateLimit-Limit"] == "60"
    assert response.headers["X-RateLimit-Remaining"] == "59"
    assert response.headers["x-ratelimit-limit-requests"] == "60"
    assert response.headers["x-ratelimit-remaining-requests"] == "59"

    # Check that the reset time is in the future
    current_time = int(time.time())
    assert int(response.headers["X-RateLimit-Reset"]) > current_time
    assert int(response.headers["x-ratelimit-reset-requests"]) > current_time
