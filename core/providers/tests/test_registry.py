from __future__ import annotations

import threading
import time
import unittest

from core.providers.registry import ProviderRegistry, registry


class TestProviderRegistry(unittest.TestCase):
    def setUp(self):
        # Use a fresh registry for each test to ensure isolation
        self.registry = ProviderRegistry()
        # Also clear the global registry for decorator tests
        registry._providers.clear()


    def test_register_and_get_provider(self):
        provider = {"name": "TestProvider"}
        self.registry.register("test_provider", provider)
        retrieved_provider = self.registry.get("test_provider")
        self.assertEqual(retrieved_provider, provider)

    def test_get_provider_with_default(self):
        default_provider = {"name": "DefaultProvider"}
        retrieved_provider = self.registry.get("non_existent", default=default_provider)
        self.assertEqual(retrieved_provider, default_provider)
        retrieved_provider = self.registry.get("non_existent")
        self.assertIsNone(retrieved_provider)

    def test_has_provider(self):
        self.assertFalse(self.registry.has("test_provider"))
        self.registry.register("test_provider", {})
        self.assertTrue(self.registry.has("test_provider"))

    def test_list_providers(self):
        self.assertEqual(self.registry.list_providers(), [])
        self.registry.register("provider_a", {})
        self.registry.register("provider_b", {})
        self.assertEqual(self.registry.list_providers(), ["provider_a", "provider_b"])

    def test_namespace_isolation(self):
        provider1 = {"name": "Provider1"}
        provider2 = {"name": "Provider2"}
        self.registry.register("provider", provider1, namespace="ns1")
        self.registry.register("provider", provider2, namespace="ns2")
        self.assertEqual(self.registry.get("provider", namespace="ns1"), provider1)
        self.assertEqual(self.registry.get("provider", namespace="ns2"), provider2)
        self.assertTrue(self.registry.has("provider", namespace="ns1"))
        self.assertTrue(self.registry.has("provider", namespace="ns2"))
        self.assertFalse(self.registry.has("provider"))
        self.assertEqual(self.registry.list_providers(namespace="ns1"), ["provider"])
        self.assertEqual(self.registry.list_providers(namespace="ns2"), ["provider"])
        self.assertEqual(self.registry.list_providers(), [])

    def test_thread_safety(self):
        def register_providers(thread_id):
            for i in range(100):
                provider_name = f"provider_{thread_id}_{i}"
                self.registry.register(provider_name, i)
                time.sleep(0.001)

        threads = [threading.Thread(target=register_providers, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(self.registry.list_providers()), 100 * 5)
        for i in range(5):
            for j in range(100):
                provider_name = f"provider_{i}_{j}"
                self.assertTrue(self.registry.has(provider_name))
                self.assertEqual(self.registry.get(provider_name), j)

    def test_decorator(self):
        @registry.register_provider("my_provider")
        class MyProvider:
            pass

        self.assertTrue(registry.has("my_provider"))
        self.assertEqual(registry.get("my_provider"), MyProvider)

    def test_decorator_with_namespace(self):
        @registry.register_provider("my_provider", namespace="my_ns")
        class MyProvider:
            pass

        self.assertTrue(registry.has("my_provider", namespace="my_ns"))
        self.assertEqual(registry.get("my_provider", namespace="my_ns"), MyProvider)
        self.assertFalse(registry.has("my_provider"))

    def test_decorator_returns_class(self):
        class OriginalProvider:
            pass

        decorated_provider = registry.register_provider("my_provider")(OriginalProvider)
        self.assertEqual(decorated_provider, OriginalProvider)


if __name__ == "__main__":
    unittest.main()
