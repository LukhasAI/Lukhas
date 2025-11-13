
import os
import time

import jwt
import numpy as np
from locust import HttpUser, between, events, task

# --- Configuration ---
API_KEY = os.getenv("LUKHAS_API_KEY", "your-lukhas-api-key-here")
JWT_SECRET = os.getenv("JWT_SECRET", "your-jwt-private-key-here-at-least-32-characters")
JWT_ALGORITHM = "HS256"
TARGET_HOST = os.getenv("TARGET_HOST", "http://127.0.0.1:8000")

# --- Custom Metrics ---
latencies = []

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Reset stats at the start of a test run."""
    latencies.clear()
    print("--- Starting new test run. Custom metrics initialized. ---")

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, context, **kwargs):
    """Record latency for each request."""
    latencies.append(response_time)

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Aggregate and print performance stats at the end of a test run."""
    if latencies:
        # Performance metrics
        p50_latency = np.percentile(latencies, 50)
        p95_latency = np.percentile(latencies, 95)
        p99_latency = np.percentile(latencies, 99)

        print("--- Test run finished ---")
        print(f"P50 Latency: {p50_latency:.2f} ms")
        print(f"P95 Latency: {p95_latency:.2f} ms")
        print(f"P99 Latency: {p99_latency:.2f} ms")
        print("-------------------------")

# --- Authentication Helpers ---
def generate_jwt():
    """Generates a JWT for authenticated endpoints."""
    payload = {
        "user_id": "performance-tester",
        "exp": time.time() + 3600  # Token valid for 1 hour
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

# --- Base User Class ---
class BaseApiUser(HttpUser):
    host = TARGET_HOST
    wait_time = between(0.5, 2.5)
    abstract = True

# --- User Classes for Different APIs ---
class OpenAiApiUser(BaseApiUser):
    """User for OpenAI-compatible endpoints requiring JWT authentication."""
    jwt_token = None

    def on_start(self):
        self.jwt_token = generate_jwt()

    @task(3)
    def chat_completions(self):
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        payload = {
            "model": "lukhas-matriz-v1",
            "messages": [{"role": "user", "content": "Tell me a short story."}]
        }
        self.client.post("/v1/chat/completions", json=payload, headers=headers, name="/v1/chat/completions")

    @task(1)
    def chat_completions_streaming(self):
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        payload = {
            "model": "lukhas-matriz-v1",
            "messages": [{"role": "user", "content": "Stream a story."}],
            "stream": True
        }
        with self.client.post("/v1/chat/completions", json=payload, headers=headers, stream=True, name="/v1/chat/completions [stream]", catch_response=True) as response:
            if response.status_code != 200:
                response.failure("Streaming connection failed")

    @task(2)
    def embeddings(self):
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        payload = {
            "model": "lukhas-matriz-v1",
            "input": "This is a test sentence for embeddings generation."
        }
        self.client.post("/v1/embeddings", json=payload, headers=headers, name="/v1/embeddings")

class DreamsApiUser(BaseApiUser):
    """User for the Dreams API requiring an API key."""

    @task
    def create_dream(self):
        headers = {"X-API-Key": API_KEY}
        payload = {
            "seed": f"dream-seed-{time.time()}",
            "constraints": {"max_steps": 5, "complexity": "medium"}
        }
        self.client.post("/v1/dreams", json=payload, headers=headers, name="/v1/dreams")

class GeneralApiUser(BaseApiUser):
    """User for general, unauthenticated or lightly authenticated endpoints."""

    @task(5)
    def health_check(self):
        self.client.get("/healthz", name="/healthz")

    @task(1)
    def list_models(self):
        headers = {"Authorization": f"Bearer {generate_jwt()}"}
        self.client.get("/v1/models", headers=headers, name="/v1/models")

class MetricsUser(BaseApiUser):
    """User for querying the /metrics endpoint."""

    @task
    def get_metrics(self):
        self.client.get("/metrics", name="/metrics")
