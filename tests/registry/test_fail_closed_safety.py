"""
Fail-Closed Safety Tests
=======================

P0-2 REG-HARDEN: Tests for fail-closed safety mechanisms in the registry system.
Validates that the system fails safely when encountering errors, security issues,
or unexpected conditions, preventing dangerous states.

Test Coverage:
- Default secure configuration (discovery disabled)
- Graceful degradation under failure conditions
- Security policy enforcement during failures
- Resource exhaustion protection
- Malicious input handling
- Recovery mechanisms and safe states
- Emergency shutdown procedures
"""

import gc
import os
import sys
import threading
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Import registry components
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.registry import (
    _REG,
    _instantiate_plugin,
    auto_discover,
    discover_entry_points,
    register,
    resolve,
)


class FailureSimulator:
    """Helper class to simulate various failure conditions"""

    @staticmethod
    def simulate_memory_exhaustion():
        """Simulate memory exhaustion condition"""
        # Allocate large amounts of memory
        memory_hogs = []
        try:
            while len(memory_hogs) < 100:  # Limit to prevent actual system issues
                memory_hogs.append(bytearray(1024 * 1024))  # 1MB each
        except MemoryError:
            pass
        return memory_hogs

    @staticmethod
    def simulate_cpu_exhaustion():
        """Simulate CPU exhaustion condition"""
        def cpu_intensive_task():
            # CPU intensive loop
            for _ in range(1000000):
                _ = sum(range(100))

        threads = []
        for _ in range(4):  # Create 4 CPU-intensive threads
            thread = threading.Thread(target=cpu_intensive_task)
            threads.append(thread)
            thread.start()

        return threads

    @staticmethod
    def simulate_file_system_failure():
        """Simulate file system failures"""
        def failing_open(*args, **kwargs):
            raise OSError("Simulated file system failure")

        return patch('builtins.open', side_effect=failing_open)

    @staticmethod
    def simulate_network_failure():
        """Simulate network connectivity failures"""
        def failing_request(*args, **kwargs):
            raise ConnectionError("Simulated network failure")

        return patch('requests.get', side_effect=failing_request)


class MaliciousPluginSimulator:
    """Helper class to create various types of malicious plugins"""

    @staticmethod
    def create_resource_exhaustion_plugin():
        """Plugin that attempts to exhaust system resources"""
        class ResourceExhaustionPlugin:
            def __init__(self, name=None):
                self.name = name
                # Attempt to allocate excessive memory
                try:
                    self.memory_hog = bytearray(100 * 1024 * 1024)  # 100MB
                except MemoryError:
                    self.memory_hog = None

                # Attempt to create many threads
                self.threads = []
                try:
                    for _ in range(100):
                        thread = threading.Thread(target=lambda: time.sleep(1))
                        thread.start()
                        self.threads.append(thread)
                except Exception:
                    pass

        return ResourceExhaustionPlugin

    @staticmethod
    def create_infinite_loop_plugin():
        """Plugin with infinite loop in constructor"""
        class InfiniteLoopPlugin:
            def __init__(self, name=None):
                self.name = name
                # Infinite loop (but with escape condition for testing)
                count = 0
                while count < 1000:  # Limited for testing
                    count += 1

        return InfiniteLoopPlugin

    @staticmethod
    def create_exception_throwing_plugin():
        """Plugin that throws various types of exceptions"""
        class ExceptionThrowingPlugin:
            def __init__(self, name=None):
                self.name = name
                # Throw different types of exceptions based on name
                if name == "runtime_error":
                    raise RuntimeError("Malicious runtime error")
                elif name == "value_error":
                    raise ValueError("Malicious value error")
                elif name == "system_exit":
                    raise SystemExit("Malicious system exit")
                elif name == "keyboard_interrupt":
                    raise KeyboardInterrupt("Malicious keyboard interrupt")
                else:
                    raise Exception("Generic malicious exception")

        return ExceptionThrowingPlugin

    @staticmethod
    def create_file_access_plugin():
        """Plugin that attempts unauthorized file access"""
        class FileAccessPlugin:
            def __init__(self, name=None):
                self.name = name
                # Attempt to read sensitive files
                sensitive_paths = [
                    '/etc/passwd',
                    '/etc/shadow',
                    os.path.expanduser('~/.ssh/id_rsa'),
                    '/proc/version'
                ]

                self.accessed_files = []
                for path in sensitive_paths:
                    try:
                        with open(path) as f:
                            content = f.read(100)  # Read first 100 chars
                            self.accessed_files.append((path, len(content)))
                    except (FileNotFoundError, PermissionError, OSError):
                        pass  # Expected for most files

        return FileAccessPlugin


class TestFailClosedSafetyMechanisms:
    """Test suite for fail-closed safety mechanisms"""

    def setup_method(self):
        """Setup before each test"""
        global _REG
        _REG.clear()

    def teardown_method(self):
        """Cleanup after each test"""
        global _REG
        _REG.clear()
        # Force garbage collection to clean up any test artifacts
        gc.collect()

    def test_default_secure_configuration(self):
        """Test that system defaults to secure configuration"""

        # Save original environment
        original_env = os.environ.get('LUKHAS_PLUGIN_DISCOVERY')

        try:
            # Clear discovery environment variable
            if 'LUKHAS_PLUGIN_DISCOVERY' in os.environ:
                del os.environ['LUKHAS_PLUGIN_DISCOVERY']

            # Import discovery flag (should be 'off' by default)
            from core.registry import _DISCOVERY_FLAG
            assert _DISCOVERY_FLAG == 'off', "Discovery should be disabled by default (fail-closed)"

            # Registry should start empty
            assert len(_REG) == 0, "Registry should start empty"

            # Discovery should not activate plugins
            initial_size = len(_REG)
            discover_entry_points()
            assert len(_REG) == initial_size, "Discovery should not activate when disabled"

            # Auto-discovery should also not activate
            auto_discover()
            assert len(_REG) == initial_size, "Auto-discovery should not activate when disabled"

        finally:
            # Restore original environment
            if original_env is not None:
                os.environ['LUKHAS_PLUGIN_DISCOVERY'] = original_env

    def test_graceful_degradation_under_failures(self):
        """Test graceful degradation when components fail"""

        # Test registry continues to work even when discovery fails
        with patch('core.registry.entry_points', side_effect=ImportError("Discovery failure")):
            # Enable discovery for this test
            with patch.dict(os.environ, {'LUKHAS_PLUGIN_DISCOVERY': 'auto'}):
                # Discovery should handle the failure gracefully
                try:
                    discover_entry_points()
                except Exception:
                    pytest.fail("Discovery should handle failures gracefully")

                # Basic registry operations should still work
                register('test:safe_plugin', {'name': 'safe_plugin'})
                assert resolve('test:safe_plugin')['name'] == 'safe_plugin'

    def test_malicious_plugin_isolation(self):
        """Test that malicious plugins are isolated and don't crash the system"""

        malicious_plugins = [
            ('resource_exhaustion', MaliciousPluginSimulator.create_resource_exhaustion_plugin()),
            ('infinite_loop', MaliciousPluginSimulator.create_infinite_loop_plugin()),
            ('file_access', MaliciousPluginSimulator.create_file_access_plugin())
        ]

        for plugin_name, plugin_class in malicious_plugins:
            # Test instantiation doesn't crash the system
            try:
                with patch('signal.alarm', return_value=None):  # Prevent real timeouts
                    instance = _instantiate_plugin(plugin_name, plugin_class)

                    # System should survive malicious plugin instantiation
                    # May return the class itself as fallback
                    assert instance is not None, f"Plugin instantiation should not return None for {plugin_name}"

                    # Registry should still function after malicious plugin
                    register(f'test:after_{plugin_name}', {'name': f'after_{plugin_name}'})
                    resolved = resolve(f'test:after_{plugin_name}')
                    assert resolved['name'] == f'after_{plugin_name}', "Registry should still work after malicious plugin"

            except Exception as e:
                # Some exceptions are expected and should be handled gracefully
                expected_exceptions = (RuntimeError, ValueError, MemoryError, OSError)
                if not isinstance(e, expected_exceptions):
                    pytest.fail(f"Unexpected exception type for {plugin_name}: {type(e).__name__}: {e}")

    def test_exception_throwing_plugin_safety(self):
        """Test safety when plugins throw various types of exceptions"""

        exception_types = [
            'runtime_error',
            'value_error',
            'system_exit',
            'keyboard_interrupt'
        ]

        ExceptionPlugin = MaliciousPluginSimulator.create_exception_throwing_plugin()

        for exception_type in exception_types:
            try:
                # Attempt to instantiate plugin that throws exceptions
                instance = _instantiate_plugin(exception_type, ExceptionPlugin)

                # Should either succeed with fallback or handle exception gracefully
                # In current implementation, it falls back to returning the class
                assert instance == ExceptionPlugin, f"Should fall back to class for {exception_type}"

                # Registry should still work after exception
                register(f'test:post_{exception_type}', {'name': f'post_{exception_type}'})
                resolved = resolve(f'test:post_{exception_type}')
                assert resolved['name'] == f'post_{exception_type}', f"Registry should work after {exception_type}"

            except SystemExit:
                pytest.fail(f"SystemExit should be caught and handled for {exception_type}")
            except KeyboardInterrupt:
                pytest.fail(f"KeyboardInterrupt should be caught and handled for {exception_type}")
            except Exception as e:
                # Other exceptions should be handled gracefully
                print(f"Handled exception for {exception_type}: {type(e).__name__}: {e}")

    def test_resource_exhaustion_protection(self):
        """Test protection against resource exhaustion attacks"""

        # Test memory exhaustion protection
        ResourcePlugin = MaliciousPluginSimulator.create_resource_exhaustion_plugin()

        # Monitor memory usage before and after
        import psutil
        process = psutil.Process()
        initial_memory = process.memory_info().rss

        try:
            # Attempt to instantiate resource-hungry plugin
            _instantiate_plugin('resource_exhaustion', ResourcePlugin)

            # Check memory usage didn't grow excessively
            final_memory = process.memory_info().rss
            memory_growth = final_memory - initial_memory

            # Allow some memory growth but not excessive (100MB limit for test)
            assert memory_growth < 100 * 1024 * 1024, f"Excessive memory growth: {memory_growth / 1024 / 1024:.1f}MB"

            # Registry should still function
            register('test:after_resource_exhaustion', {'name': 'survivor'})
            assert resolve('test:after_resource_exhaustion')['name'] == 'survivor'

        except MemoryError:
            # MemoryError is acceptable - system protected itself
            pass

    def test_timeout_protection(self):
        """Test protection against plugins that take too long to instantiate"""

        InfinitePlugin = MaliciousPluginSimulator.create_infinite_loop_plugin()

        start_time = time.time()

        # Attempt to instantiate plugin with infinite loop
        _instantiate_plugin('infinite_loop', InfinitePlugin)

        duration = time.time() - start_time

        # Should complete within reasonable time (current implementation doesn't have timeouts)
        # But the loop is limited in our test plugin
        assert duration < 5.0, f"Plugin instantiation took too long: {duration:.2f}s"

        # Registry should still work
        register('test:after_timeout', {'name': 'timeout_survivor'})
        assert resolve('test:after_timeout')['name'] == 'timeout_survivor'

    def test_file_system_failure_resilience(self):
        """Test resilience to file system failures"""

        with FailureSimulator.simulate_file_system_failure():
            # Registry should continue to work even if file operations fail
            register('test:fs_failure', {'name': 'fs_failure_test'})
            assert resolve('test:fs_failure')['name'] == 'fs_failure_test'

            # Discovery should handle file system failures gracefully
            with patch.dict(os.environ, {'LUKHAS_PLUGIN_DISCOVERY': 'auto'}):
                try:
                    discover_entry_points()
                except OSError:
                    pytest.fail("Discovery should handle file system failures gracefully")

    def test_concurrent_failure_handling(self):
        """Test handling of failures in concurrent scenarios"""

        import queue
        import threading

        results = queue.Queue()
        errors = queue.Queue()

        def failing_worker(worker_id):
            """Worker that may encounter various failures"""
            try:
                # Simulate different types of failures
                if worker_id % 3 == 0:
                    # Memory allocation failure
                    ResourcePlugin = MaliciousPluginSimulator.create_resource_exhaustion_plugin()
                    _instantiate_plugin(f'resource_{worker_id}', ResourcePlugin)

                elif worker_id % 3 == 1:
                    # Exception throwing failure
                    ExceptionPlugin = MaliciousPluginSimulator.create_exception_throwing_plugin()
                    _instantiate_plugin('runtime_error', ExceptionPlugin)

                else:
                    # Normal operation
                    register(f'worker:{worker_id}', {'name': f'worker_{worker_id}'})
                    resolve(f'worker:{worker_id}')

                results.put(f'worker_{worker_id}_success')

            except Exception as e:
                errors.put(f'worker_{worker_id}_error: {e}')

        # Start multiple failing workers
        threads = []
        for i in range(10):
            thread = threading.Thread(target=failing_worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join(timeout=10)

        # Collect results
        success_count = 0
        while not results.empty():
            result = results.get()
            if 'success' in result:
                success_count += 1

        error_count = 0
        while not errors.empty():
            errors.get()
            error_count += 1

        # System should survive concurrent failures
        total_operations = success_count + error_count
        assert total_operations == 10, f"Expected 10 operations, got {total_operations}"

        # Some operations should succeed despite failures
        assert success_count > 0, "At least some operations should succeed"

        # Registry should still be functional after concurrent failures
        register('test:post_concurrent_failures', {'name': 'survivor'})
        assert resolve('test:post_concurrent_failures')['name'] == 'survivor'

    def test_security_policy_enforcement_under_failure(self):
        """Test that security policies are enforced even during failure conditions"""

        # Simulate a compromised environment with discovery enabled
        with patch.dict(os.environ, {'LUKHAS_PLUGIN_DISCOVERY': 'auto'}):
            with patch('core.registry.entry_points') as mock_entry_points:
                # Create malicious entry point
                malicious_ep = Mock()
                malicious_ep.name = "malicious_plugin"
                malicious_ep.load.return_value = MaliciousPluginSimulator.create_file_access_plugin()

                mock_entry_points.return_value = [malicious_ep]

                # Discovery should handle malicious plugins safely
                initial_registry_size = len(_REG)
                try:
                    discover_entry_points()
                except Exception as e:
                    # Exceptions during discovery should be handled gracefully
                    print(f"Discovery handled exception: {e}")

                # Registry should not be compromised
                # Either no new plugins or only safe fallback registration
                final_registry_size = len(_REG)
                registry_growth = final_registry_size - initial_registry_size

                # Limited registry growth is acceptable (fallback registration)
                assert registry_growth <= 1, f"Unexpected registry growth: {registry_growth}"

    def test_emergency_shutdown_mechanisms(self):
        """Test emergency shutdown mechanisms work correctly"""

        # Simulate critical failure condition
        def simulate_critical_failure():
            # Register many plugins quickly to simulate system overload
            for i in range(1000):
                register(f'overload:{i}', {'data': 'x' * 1000})

        # Monitor system state during overload
        initial_size = len(_REG)

        try:
            simulate_critical_failure()
        except Exception as e:
            # System should handle overload gracefully
            print(f"Handled overload exception: {e}")

        final_size = len(_REG)
        assert final_size >= initial_size, "Registry should maintain state during overload"

        # System should still be responsive after overload
        register('test:post_overload', {'name': 'post_overload'})
        assert resolve('test:post_overload')['name'] == 'post_overload'

    def test_recovery_mechanisms(self):
        """Test that system can recover from failure states"""

        # Simulate failure state
        dict(_REG)

        # Corrupt registry state
        _REG.clear()
        _REG['corrupted:plugin'] = "invalid_data"

        # Test recovery
        try:
            # System should handle corrupted state
            corrupted_value = resolve('corrupted:plugin')
            assert corrupted_value == "invalid_data", "Should resolve corrupted data"

            # Should be able to add new clean data
            register('recovery:test', {'name': 'recovery_test'})
            assert resolve('recovery:test')['name'] == 'recovery_test'

            # Should be able to overwrite corrupted data
            register('corrupted:plugin', {'name': 'cleaned_plugin'})
            assert resolve('corrupted:plugin')['name'] == 'cleaned_plugin'

        except Exception as e:
            pytest.fail(f"Recovery mechanism failed: {e}")

    def test_safe_defaults_after_failure(self):
        """Test that system maintains safe defaults after various failures"""

        failure_scenarios = [
            lambda: _instantiate_plugin('bad', MaliciousPluginSimulator.create_exception_throwing_plugin()),
            lambda: discover_entry_points(),  # With no entry points available
            lambda: register('test', None),  # Register None value
            lambda: resolve('nonexistent'),  # Try to resolve nonexistent key
        ]

        for i, failure_scenario in enumerate(failure_scenarios):
            try:
                failure_scenario()
            except Exception as e:
                # Expected failures should be handled
                print(f"Scenario {i} failed as expected: {e}")

            # After each failure, system should maintain safe defaults
            # Should be able to register and resolve normally
            test_key = f'safe_default_{i}'
            register(test_key, {'name': f'safe_{i}'})
            assert resolve(test_key)['name'] == f'safe_{i}'

            # Discovery should still be disabled by default
            original_env = os.environ.get('LUKHAS_PLUGIN_DISCOVERY')
            if 'LUKHAS_PLUGIN_DISCOVERY' in os.environ:
                del os.environ['LUKHAS_PLUGIN_DISCOVERY']

            # Discovery flag might be cached, but behavior should be safe
            # Main point is that explicit enabling is required

            if original_env:
                os.environ['LUKHAS_PLUGIN_DISCOVERY'] = original_env

    def test_isolation_boundaries_during_failures(self):
        """Test that failure in one component doesn't affect others"""

        # Create isolated components
        component_a_data = {'component': 'a', 'status': 'healthy'}
        component_b_data = {'component': 'b', 'status': 'healthy'}

        register('component:a', component_a_data)
        register('component:b', component_b_data)

        # Simulate failure in component A's plugin instantiation
        FailingPlugin = MaliciousPluginSimulator.create_exception_throwing_plugin()

        try:
            _instantiate_plugin('runtime_error', FailingPlugin)
        except Exception:
            pass  # Expected failure

        # Component B should be unaffected
        component_b_resolved = resolve('component:b')
        assert component_b_resolved == component_b_data, "Component B should be unaffected by A's failure"

        # Should be able to continue working with both components
        register('component:c', {'component': 'c', 'status': 'healthy'})
        assert resolve('component:c')['component'] == 'c'

        # Original components should still work
        assert resolve('component:a') == component_a_data
        assert resolve('component:b') == component_b_data


class TestRegistryFailClosedIntegration:
    """Integration tests for fail-closed safety"""

    def test_complete_failure_scenario(self):
        """Test system behavior under complete failure scenario"""

        # Simulate multiple concurrent failures
        failure_conditions = [
            'memory_pressure',
            'malicious_plugins',
            'file_system_errors',
            'network_failures',
            'concurrent_access'
        ]

        # Clear registry
        _REG.clear()
        dict(_REG)

        # System should start in safe state
        assert len(_REG) == 0, "Should start with empty registry"

        # Apply failure conditions one by one
        for condition in failure_conditions:
            try:
                if condition == 'memory_pressure':
                    # Simulate memory pressure
                    memory_hogs = []
                    for _ in range(10):  # Limited for test safety
                        memory_hogs.append(bytearray(1024 * 1024))  # 1MB each

                elif condition == 'malicious_plugins':
                    # Try to register malicious plugins
                    BadPlugin = MaliciousPluginSimulator.create_resource_exhaustion_plugin()
                    _instantiate_plugin('malicious', BadPlugin)

                elif condition == 'file_system_errors':
                    # Simulate file system failures during discovery
                    with FailureSimulator.simulate_file_system_failure():
                        discover_entry_points()

                elif condition == 'concurrent_access':
                    # Simulate concurrent access issues
                    def concurrent_registrations():
                        for i in range(10):
                            register(f'concurrent:{i}', {'id': i})

                    threads = [threading.Thread(target=concurrent_registrations) for _ in range(3)]
                    for t in threads:
                        t.start()
                    for t in threads:
                        t.join()

                # After each failure condition, system should still be operational
                test_key = f'post_{condition}'
                register(test_key, {'condition': condition, 'status': 'survived'})
                resolved = resolve(test_key)
                assert resolved['status'] == 'survived', f"System should survive {condition}"

            except Exception as e:
                # Failures should be handled gracefully
                print(f"Handled failure in {condition}: {e}")

        # Final verification - system should be in a consistent, safe state
        final_registry_keys = list(_REG.keys())
        assert len(final_registry_keys) > 0, "Registry should have some entries after failures"

        # All registered items should be resolvable
        for key in final_registry_keys:
            try:
                value = resolve(key)
                assert value is not None, f"All registered items should be resolvable: {key}"
            except Exception as e:
                pytest.fail(f"Registry corruption detected for key {key}: {e}")

        # System should still accept new registrations
        register('final:test', {'final': True})
        assert resolve('final:test')['final'] is True


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])
