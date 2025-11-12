import sys
import unittest
from unittest.mock import patch

class TestRegistryLazyLoad(unittest.TestCase):

    def setUp(self):
        """Unload the module before each test to ensure a clean state."""
        self.module_name = 'labs.core.tags.registry'
        if self.module_name in sys.modules:
            del sys.modules[self.module_name]

    def tearDown(self):
        """Clean up by unloading the module again after each test."""
        if self.module_name in sys.modules:
            del sys.modules[self.module_name]

    def test_registry_is_not_instantiated_on_import(self):
        """Verify that the TagRegistry is not created when the module is imported."""
        # ACTION: Just import the module
        import labs.core.tags.registry as registry

        # ASSERTION: The internal instance variable should be None
        self.assertIsNone(registry._tag_registry_instance,
                          "TagRegistry instance should not be created on module import.")

    def test_get_tag_registry_triggers_instantiation(self):
        """Verify that calling get_tag_registry() creates the TagRegistry instance."""
        import labs.core.tags.registry as registry

        # Pre-condition check
        self.assertIsNone(registry._tag_registry_instance,
                          "TagRegistry instance should be None before first access.")

        # ACTION: Call the function that should trigger the instantiation
        tag_registry = registry.get_tag_registry()

        # ASSERTION: The instance should now exist and be of the correct type
        self.assertIsNotNone(registry._tag_registry_instance,
                             "TagRegistry instance should be created after access.")
        self.assertIsInstance(tag_registry, registry.TagRegistry,
                              "Returned object must be an instance of TagRegistry.")
        # Verify it's a singleton: subsequent calls return the same object
        self.assertIs(tag_registry, registry.get_tag_registry(),
                      "get_tag_registry() should return the same singleton instance.")

    def test_no_circular_imports(self):
        """Verify that the module can be imported without circular dependency errors."""
        try:
            # ACTION: Import the module
            import labs.core.tags.registry
        except ImportError as e:
            # ASSERTION: Fail if any ImportError occurs during import
            self.fail(f"Importing the registry module failed with an ImportError, which might indicate a circular dependency: {e}")
        except Exception as e:
            self.fail(f"An unexpected exception occurred during module import: {e}")

    def test_direct_access_to_class_does_not_instantiate(self):
        """Verify that accessing the TagRegistry class directly does not instantiate the singleton."""
        import labs.core.tags.registry as registry

        # ACTION: Access the class definition itself
        _ = registry.TagRegistry

        # ASSERTION: The internal instance variable should still be None
        self.assertIsNone(registry._tag_registry_instance,
                          "Accessing the TagRegistry class definition should not trigger instantiation.")

if __name__ == '__main__':
    unittest.main()
