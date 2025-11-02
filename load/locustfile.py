"""
Locust Load Testing - Python Alternative to k6

Purpose: Python-based load testing with web UI for real-time monitoring
Usage:
    locust -f load/locustfile.py --host=http://localhost:8000
    # Open http://localhost:8089 to configure test

Installation:
    pip install locust
"""

import json
import random

from locust import HttpUser, between, events, task
from locust.runners import MasterRunner


class LukhasAPIUser(HttpUser):
    """
    Simulates a user interacting with LUKHAS API endpoints.
    """

    # Wait 0.5-2 seconds between tasks
    wait_time = between(0.5, 2)

    # Test data
    test_inputs = [
        "Analyze this consciousness pattern",
        "Generate a symbolic representation",
        "Process this quantum state",
        "What is the meaning of consciousness?",
        "Explain the MATRIZ cognitive architecture",
    ]

    models = [
        "lukhas-consciousness-v1",
        "lukhas-vision-v1",
        "lukhas-quantum-v1",
    ]

    def on_start(self):
        """Called when a user starts. Setup any user-specific state."""
        self.api_key = "test-key"  # Override with env var in production
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    @task(3)  # Weight: 30% of requests
    def health_check(self):
        """Lightweight health check endpoint."""
        with self.client.get("/health", catch_response=True, name="/health (GET)") as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")

    @task(5)  # Weight: 50% of requests
    def create_response(self):
        """Standard response generation via /v1/responses."""
        payload = {
            "input": random.choice(self.test_inputs),
            "tools": [],
            "stream": False,
        }

        with self.client.post(
            "/v1/responses", json=payload, headers=self.headers, catch_response=True, name="/v1/responses (POST)"
        ) as response:
            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    if "id" in data and "created" in data:
                        response.success()
                    else:
                        response.failure("Response missing required fields")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"Request failed: {response.status_code}")

    @task(2)  # Weight: 20% of requests
    def chat_completion(self):
        """OpenAI-compatible chat completion."""
        payload = {
            "model": random.choice(self.models),
            "messages": [
                {"role": "system", "content": "You are a consciousness-aware AI assistant."},
                {"role": "user", "content": random.choice(self.test_inputs)},
            ],
            "max_tokens": 100,
            "temperature": 0.7,
        }

        with self.client.post(
            "/v1/chat/completions",
            json=payload,
            headers=self.headers,
            catch_response=True,
            name="/v1/chat/completions (POST)",
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "choices" in data and len(data["choices"]) > 0:
                        response.success()
                    else:
                        response.failure("No choices in response")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"Chat completion failed: {response.status_code}")


class LukhasHeavyUser(HttpUser):
    """
    Simulates a heavy user with more demanding requests.
    Use this class to test system under high load with complex requests.
    """

    wait_time = between(1, 3)

    def on_start(self):
        self.api_key = "test-key"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    @task
    def complex_chat(self):
        """Complex multi-turn conversation."""
        payload = {
            "model": "lukhas-consciousness-v1",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a consciousness-aware AI assistant with deep knowledge of cognitive science.",
                },
                {"role": "user", "content": "Explain the relationship between consciousness and quantum mechanics."},
                {
                    "role": "assistant",
                    "content": "Consciousness and quantum mechanics intersect in fascinating ways...",
                },
                {"role": "user", "content": "Can you elaborate on quantum coherence in biological systems?"},
            ],
            "max_tokens": 500,
            "temperature": 0.8,
        }

        with self.client.post(
            "/v1/chat/completions",
            json=payload,
            headers=self.headers,
            catch_response=True,
            name="/v1/chat/completions [COMPLEX] (POST)",
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 429:
                # Rate limited - expected under heavy load
                response.success()
            else:
                response.failure(f"Complex chat failed: {response.status_code}")


# Event handlers for logging
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Fired when the test starts."""
    print("=" * 70)
    print("LUKHAS Load Test Starting")
    print("=" * 70)
    print(f"Host: {environment.host}")
    if isinstance(environment.runner, MasterRunner):
        print("Running in distributed mode (master)")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Fired when the test stops."""
    print("=" * 70)
    print("LUKHAS Load Test Completed")
    print("=" * 70)
    stats = environment.stats
    print(f"Total requests: {stats.total.num_requests}")
    print(f"Total failures: {stats.total.num_failures}")
    print(f"Avg response time: {stats.total.avg_response_time:.2f}ms")
    print(f"Min response time: {stats.total.min_response_time:.2f}ms")
    print(f"Max response time: {stats.total.max_response_time:.2f}ms")
    print(f"Requests/sec: {stats.total.total_rps:.2f}")


# Custom load shape (optional) - uncomment to use
# from locust import LoadTestShape
#
# class SpikeLoadShape(LoadTestShape):
#     """
#     Custom load shape for spike testing.
#     Stages: baseline → spike → sustain → recovery
#     """
#     stages = [
#         {"duration": 30, "users": 10, "spawn_rate": 1},   # Baseline
#         {"duration": 90, "users": 200, "spawn_rate": 10}, # Spike
#         {"duration": 210, "users": 200, "spawn_rate": 1}, # Sustain
#         {"duration": 270, "users": 10, "spawn_rate": 5},  # Recovery
#     ]
#
#     def tick(self):
#         run_time = self.get_run_time()
#
#         for stage in self.stages:
#             if run_time < stage["duration"]:
#                 return (stage["users"], stage["spawn_rate"])
#
#         return None  # Test ends
