import sys
from unittest.mock import MagicMock

# Mock missing modules to allow for testing in environments where these are not available.
# This is particularly useful for CI/CD pipelines or isolated testing setups.
MOCKED_MODULES = [
    "core.interfaces.api.v1.v1.common.api_key_cache",
    "core.policy_guard",
    "matriz.core.async_orchestrator",
    "matriz.core.memory_system"
]

for module_name in MOCKED_MODULES:
    if module_name not in sys.modules:
        sys.modules[module_name] = MagicMock()


from locust import HttpUser, between, task


class APIUser(HttpUser):
    """
    Simulates a user interacting with the LUKHAS API.
    """
    wait_time = between(0.1, 0.5)  # Wait time between tasks

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers = {
            "Authorization": "Bearer sk-lukhas-premium-dummy-key",
            "Content-Type": "application/json",
        }

    @task(10)
    def chat_completions(self):
        """
        Task to test the MATRIZ query endpoint (/v1/chat/completions).
        """
        payload = {
            "model": "lukhas-matriz-v1",
            "messages": [
                {"role": "user", "content": "What is the capital of France?"}
            ],
        }
        self.client.post(
            "/v1/chat/completions",
            json=payload,
            headers=self.headers,
            name="/v1/chat/completions",
        )

    @task(5)
    def embeddings(self):
        """
        Task to test the memory operations endpoint (/v1/embeddings).
        """
        payload = {
            "model": "lukhas-consciousness-v1",
            "input": "This is a test sentence for embedding.",
        }
        self.client.post(
            "/v1/embeddings",
            json=payload,
            headers=self.headers,
            name="/v1/embeddings",
        )

    @task(2)
    def responses(self):
        """
        Task to test the generic responses endpoint (/v1/responses).
        """
        payload = {
            "model": "lukhas-mini",
            "input": "A test input for the responses endpoint",
        }
        self.client.post(
            "/v1/responses",
            json=payload,
            headers=self.headers,
            name="/v1/responses",
        )

    @task(2)
    def models_list(self):
        """
        Task to test the models list endpoint.
        """
        self.client.get("/v1/models", headers=self.headers, name="/v1/models")

    def on_start(self):
        """
        Called when a Locust user starts before any task is scheduled.
        """
        # In a real-world scenario, you might perform a login action here
        # and store the session token. For this test, we use a static bearer token.
        pass
