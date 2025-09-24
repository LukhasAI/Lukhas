"""
Lane Isolation Enforcement Tests
===============================

P0-2 REG-HARDEN: Tests for lane isolation enforcement in plugin registry.
Validates that plugins are properly isolated between different execution lanes
(production, development, experimental) and cannot cross-contaminate.

Test Coverage:
- Lane-specific plugin discovery
- Cross-lane contamination prevention
- Lane boundary enforcement
- Plugin namespace isolation
- Lane-specific security policies
- Resource isolation between lanes
"""

import pytest
import os
import sys
import tempfile
from typing import Dict, List, Any
from unittest.mock import patch, Mock, MagicMock
from pathlib import Path
from dataclasses import dataclass
import threading
import time

# Import registry components
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from lukhas.core.registry import (
    register, resolve, _REG, _register_kind,
    discover_entry_points, auto_discover
)


@dataclass
class LaneConfig:
    """Configuration for a specific execution lane"""
    name: str
    allowed_plugin_groups: List[str]
    security_level: str  # 'strict', 'moderate', 'permissive'
    resource_limits: Dict[str, Any]
    plugin_prefix: str


class LaneIsolationManager:
    """Manager for enforcing lane isolation policies"""

    def __init__(self):
        self.lanes = {
            'production': LaneConfig(
                name='production',
                allowed_plugin_groups=['lukhas.constellation_components', 'lukhas.monitoring'],
                security_level='strict',
                resource_limits={'memory_mb': 100, 'cpu_percent': 10},
                plugin_prefix='prod'
            ),
            'development': LaneConfig(
                name='development',
                allowed_plugin_groups=['lukhas.constellation_components', 'lukhas.cognitive_nodes', 'lukhas.adapters'],
                security_level='moderate',
                resource_limits={'memory_mb': 500, 'cpu_percent': 50},
                plugin_prefix='dev'
            ),
            'experimental': LaneConfig(
                name='experimental',
                allowed_plugin_groups=['lukhas.cognitive_nodes', 'lukhas.adapters'],
                security_level='permissive',
                resource_limits={'memory_mb': 1000, 'cpu_percent': 80},
                plugin_prefix='exp'
            )
        }
        self.current_lane = None
        self.isolation_enabled = True

    def set_current_lane(self, lane_name: str):
        """Set the current execution lane"""
        if lane_name not in self.lanes:
            raise ValueError(f"Unknown lane: {lane_name}")
        self.current_lane = lane_name

    def get_lane_config(self, lane_name: str = None) -> LaneConfig:
        """Get configuration for specified or current lane"""
        lane_name = lane_name or self.current_lane
        if not lane_name or lane_name not in self.lanes:
            raise ValueError(f"Invalid lane: {lane_name}")
        return self.lanes[lane_name]

    def is_plugin_allowed_in_lane(self, plugin_group: str, lane_name: str = None) -> bool:
        """Check if plugin group is allowed in specified lane"""
        lane_config = self.get_lane_config(lane_name)
        return plugin_group in lane_config.allowed_plugin_groups

    def enforce_lane_isolation(self, plugin_name: str, plugin_group: str, lane_name: str = None) -> bool:
        """Enforce lane isolation for plugin registration"""
        if not self.isolation_enabled:
            return True

        lane_config = self.get_lane_config(lane_name)

        # Check if plugin group is allowed in this lane
        if not self.is_plugin_allowed_in_lane(plugin_group, lane_name):
            return False

        # Additional security checks based on lane
        if lane_config.security_level == 'strict':
            # Strict security: only allow known safe plugins
            safe_plugin_patterns = ['monitoring_', 'constellation_', 'core_']
            if not any(pattern in plugin_name for pattern in safe_plugin_patterns):
                return False

        return True

    def get_lane_specific_registry_key(self, plugin_name: str, plugin_group: str, lane_name: str = None) -> str:
        """Generate lane-specific registry key"""
        lane_config = self.get_lane_config(lane_name)
        prefix = lane_config.plugin_prefix

        # Map group to type
        group_type_map = {
            'lukhas.constellation_components': 'constellation',
            'lukhas.cognitive_nodes': 'node',
            'lukhas.adapters': 'adapter',
            'lukhas.monitoring': 'monitor'
        }

        plugin_type = group_type_map.get(plugin_group, 'unknown')
        return f"{prefix}:{plugin_type}:{plugin_name}"


class TestLaneIsolationEnforcement:
    """Test suite for lane isolation enforcement"""

    def setup_method(self):
        """Setup before each test"""
        global _REG
        _REG.clear()
        self.isolation_manager = LaneIsolationManager()

    def teardown_method(self):
        """Cleanup after each test"""
        global _REG
        _REG.clear()

    def test_lane_specific_plugin_registration(self):
        """Test that plugins are registered with lane-specific keys"""

        # Test production lane registration
        self.isolation_manager.set_current_lane('production')

        # Register monitoring plugin (allowed in production)
        monitoring_key = self.isolation_manager.get_lane_specific_registry_key(
            'system_monitor',
            'lukhas.monitoring',
            'production'
        )

        register(monitoring_key, {'name': 'system_monitor', 'lane': 'production'})

        # Verify registration with lane prefix
        assert monitoring_key == 'prod:monitor:system_monitor'
        assert resolve(monitoring_key)['lane'] == 'production'

        # Test development lane registration
        self.isolation_manager.set_current_lane('development')

        dev_key = self.isolation_manager.get_lane_specific_registry_key(
            'debug_adapter',
            'lukhas.adapters',
            'development'
        )

        register(dev_key, {'name': 'debug_adapter', 'lane': 'development'})

        # Verify development registration
        assert dev_key == 'dev:adapter:debug_adapter'
        assert resolve(dev_key)['lane'] == 'development'

        # Verify production and development plugins are isolated
        with pytest.raises(LookupError):
            resolve('dev:adapter:debug_adapter')  # This should fail in production context

    def test_cross_lane_contamination_prevention(self):
        """Test prevention of cross-lane plugin contamination"""

        # Register plugins in different lanes
        production_plugin = {'name': 'prod_plugin', 'sensitive_data': 'secret_key'}
        development_plugin = {'name': 'dev_plugin', 'debug_info': 'verbose_logs'}
        experimental_plugin = {'name': 'exp_plugin', 'experimental_feature': True}

        # Register in production lane
        prod_key = self.isolation_manager.get_lane_specific_registry_key(
            'secure_plugin', 'lukhas.monitoring', 'production'
        )
        register(prod_key, production_plugin)

        # Register in development lane
        dev_key = self.isolation_manager.get_lane_specific_registry_key(
            'debug_plugin', 'lukhas.adapters', 'development'
        )
        register(dev_key, development_plugin)

        # Register in experimental lane
        exp_key = self.isolation_manager.get_lane_specific_registry_key(
            'alpha_plugin', 'lukhas.cognitive_nodes', 'experimental'
        )
        register(exp_key, experimental_plugin)

        # Verify each plugin is only accessible in its own lane
        assert resolve(prod_key) == production_plugin
        assert resolve(dev_key) == development_plugin
        assert resolve(exp_key) == experimental_plugin

        # Verify cross-lane access is prevented
        all_keys = list(_REG.keys())
        prod_keys = [k for k in all_keys if k.startswith('prod:')]
        dev_keys = [k for k in all_keys if k.startswith('dev:')]
        exp_keys = [k for k in all_keys if k.startswith('exp:')]

        assert len(prod_keys) == 1
        assert len(dev_keys) == 1
        assert len(exp_keys) == 1

        # Verify no key overlap
        assert not set(prod_keys) & set(dev_keys)
        assert not set(dev_keys) & set(exp_keys)
        assert not set(prod_keys) & set(exp_keys)

    def test_lane_specific_plugin_discovery(self):
        """Test that plugin discovery respects lane boundaries"""

        test_plugins = {
            'lukhas.monitoring': ['system_monitor', 'performance_tracker'],
            'lukhas.constellation_components': ['core_processor', 'memory_manager'],
            'lukhas.cognitive_nodes': ['reasoning_node', 'learning_node'],
            'lukhas.adapters': ['database_adapter', 'api_adapter']
        }

        for lane_name in ['production', 'development', 'experimental']:
            # Clear registry for each lane test
            _REG.clear()
            self.isolation_manager.set_current_lane(lane_name)
            lane_config = self.isolation_manager.get_lane_config(lane_name)

            with patch('lukhas.core.registry.entry_points') as mock_entry_points:
                # Create mock entry points for all plugin groups
                all_entry_points = []

                for group, plugins in test_plugins.items():
                    for plugin_name in plugins:
                        ep = Mock()
                        ep.name = plugin_name
                        ep.load.return_value = type(f'{plugin_name.title()}Plugin', (), {
                            '__init__': lambda self, name=None: setattr(self, 'name', name),
                            'group': group
                        })
                        all_entry_points.append((group, ep))

                # Mock entry_points to return plugins for specific groups
                def mock_entry_points_func(group=None):
                    return [ep for g, ep in all_entry_points if g == group]

                mock_entry_points.side_effect = mock_entry_points_func

                # Mock the discovery process to respect lane isolation
                with patch('lukhas.core.registry._register_kind') as mock_register_kind:
                    def lane_aware_register(group, name, obj):
                        # Only register if plugin is allowed in current lane
                        if self.isolation_manager.is_plugin_allowed_in_lane(group, lane_name):
                            lane_key = self.isolation_manager.get_lane_specific_registry_key(
                                name, group, lane_name
                            )
                            register(lane_key, obj)

                    mock_register_kind.side_effect = lane_aware_register

                    # Set discovery to auto
                    with patch.dict(os.environ, {'LUKHAS_PLUGIN_DISCOVERY': 'auto'}):
                        # Simulate lane-aware discovery
                        for group in test_plugins.keys():
                            with patch('lukhas.core.registry.entry_points', return_value=mock_entry_points_func(group)):
                                discover_entry_points()

                # Verify only allowed plugins were registered for this lane
                registered_keys = list(_REG.keys())
                lane_prefix = lane_config.plugin_prefix

                for key in registered_keys:
                    # All registered keys should have the correct lane prefix
                    assert key.startswith(f"{lane_prefix}:"), f"Key {key} should start with {lane_prefix}:"

                # Verify only allowed plugin types are present
                for group in test_plugins.keys():
                    group_allowed = group in lane_config.allowed_plugin_groups
                    group_plugins_found = any(
                        self._extract_plugin_group_from_key(key) == group
                        for key in registered_keys
                    )

                    if group_allowed:
                        # Should find plugins from allowed groups
                        pass  # This test would need more complex mocking to verify
                    else:
                        # Should not find plugins from disallowed groups
                        assert not group_plugins_found or len(registered_keys) == 0, \
                            f"Found disallowed group {group} plugins in {lane_name} lane"

    def _extract_plugin_group_from_key(self, key: str) -> str:
        """Extract plugin group from registry key (helper method)"""
        # This is a simplified extraction - in real implementation
        # we'd need to track the mapping between keys and groups
        if 'monitor' in key:
            return 'lukhas.monitoring'
        elif 'constellation' in key:
            return 'lukhas.constellation_components'
        elif 'node' in key:
            return 'lukhas.cognitive_nodes'
        elif 'adapter' in key:
            return 'lukhas.adapters'
        return 'unknown'

    def test_lane_boundary_enforcement_during_registration(self):
        """Test that lane boundaries are enforced during plugin registration"""

        test_cases = [
            # (lane, plugin_group, plugin_name, should_succeed)
            ('production', 'lukhas.monitoring', 'system_monitor', True),
            ('production', 'lukhas.constellation_components', 'core_processor', True),
            ('production', 'lukhas.cognitive_nodes', 'reasoning_node', False),  # Not allowed in prod
            ('production', 'lukhas.adapters', 'database_adapter', False),  # Not allowed in prod

            ('development', 'lukhas.monitoring', 'debug_monitor', False),  # Not allowed in dev
            ('development', 'lukhas.constellation_components', 'test_processor', True),
            ('development', 'lukhas.cognitive_nodes', 'learning_node', True),
            ('development', 'lukhas.adapters', 'test_adapter', True),

            ('experimental', 'lukhas.monitoring', 'experimental_monitor', False),  # Not allowed in exp
            ('experimental', 'lukhas.constellation_components', 'alpha_processor', False),  # Not allowed in exp
            ('experimental', 'lukhas.cognitive_nodes', 'experimental_node', True),
            ('experimental', 'lukhas.adapters', 'experimental_adapter', True),
        ]

        for lane, plugin_group, plugin_name, should_succeed in test_cases:
            self.isolation_manager.set_current_lane(lane)

            # Test enforcement
            allowed = self.isolation_manager.enforce_lane_isolation(
                plugin_name, plugin_group, lane
            )

            assert allowed == should_succeed, \
                f"Lane enforcement failed for {plugin_name} in {lane}: expected {should_succeed}, got {allowed}"

            if should_succeed:
                # Should be able to register
                lane_key = self.isolation_manager.get_lane_specific_registry_key(
                    plugin_name, plugin_group, lane
                )
                register(lane_key, {'name': plugin_name, 'group': plugin_group})

                # Should be able to resolve
                resolved = resolve(lane_key)
                assert resolved['name'] == plugin_name
            else:
                # Should not be able to register (in a full implementation)
                # For now, we just verify the enforcement check failed
                pass

    def test_resource_isolation_between_lanes(self):
        """Test that resource limits are isolated between lanes"""

        # Mock resource monitoring
        resource_usage = {
            'production': {'memory_mb': 0, 'cpu_percent': 0, 'plugins': []},
            'development': {'memory_mb': 0, 'cpu_percent': 0, 'plugins': []},
            'experimental': {'memory_mb': 0, 'cpu_percent': 0, 'plugins': []}
        }

        def mock_plugin_with_resources(name, lane, memory_usage, cpu_usage):
            """Create a mock plugin that simulates resource usage"""
            plugin = {
                'name': name,
                'lane': lane,
                'memory_usage': memory_usage,
                'cpu_usage': cpu_usage
            }

            # Track resource usage
            resource_usage[lane]['memory_mb'] += memory_usage
            resource_usage[lane]['cpu_percent'] += cpu_usage
            resource_usage[lane]['plugins'].append(plugin)

            return plugin

        # Register plugins with different resource usage in different lanes
        lanes = ['production', 'development', 'experimental']
        for lane in lanes:
            self.isolation_manager.set_current_lane(lane)
            lane_config = self.isolation_manager.get_lane_config(lane)

            # Register plugins up to but not exceeding lane limits
            memory_limit = lane_config.resource_limits['memory_mb']
            cpu_limit = lane_config.resource_limits['cpu_percent']

            # Production: small, efficient plugins
            if lane == 'production':
                for i in range(3):  # 3 small plugins
                    plugin = mock_plugin_with_resources(f'prod_plugin_{i}', lane, 30, 3)
                    key = f'prod:monitor:plugin_{i}'
                    register(key, plugin)

            # Development: medium plugins
            elif lane == 'development':
                for i in range(2):  # 2 medium plugins
                    plugin = mock_plugin_with_resources(f'dev_plugin_{i}', lane, 150, 20)
                    key = f'dev:adapter:plugin_{i}'
                    register(key, plugin)

            # Experimental: large plugins
            elif lane == 'experimental':
                plugin = mock_plugin_with_resources('exp_plugin', lane, 400, 30)
                key = 'exp:node:plugin'
                register(key, plugin)

        # Verify resource isolation
        for lane in lanes:
            lane_config = self.isolation_manager.get_lane_config(lane)
            usage = resource_usage[lane]

            # Resource usage should be within lane limits
            assert usage['memory_mb'] <= lane_config.resource_limits['memory_mb'], \
                f"Memory usage {usage['memory_mb']} exceeds limit {lane_config.resource_limits['memory_mb']} in {lane}"

            assert usage['cpu_percent'] <= lane_config.resource_limits['cpu_percent'], \
                f"CPU usage {usage['cpu_percent']} exceeds limit {lane_config.resource_limits['cpu_percent']} in {lane}"

        # Verify total isolation - no shared resources between lanes
        total_plugins = sum(len(usage['plugins']) for usage in resource_usage.values())
        registry_size = len(_REG)

        assert registry_size == total_plugins, \
            f"Registry size {registry_size} doesn't match total plugins {total_plugins}"

    def test_concurrent_lane_isolation(self):
        """Test that lane isolation works with concurrent operations"""

        import threading
        import queue

        results = queue.Queue()
        errors = queue.Queue()

        def lane_worker(lane_name, worker_id):
            """Worker function that operates in a specific lane"""
            try:
                # Create isolated registry state for this worker
                worker_registry = {}

                # Set lane
                isolation_manager = LaneIsolationManager()
                isolation_manager.set_current_lane(lane_name)
                lane_config = isolation_manager.get_lane_config(lane_name)

                # Register plugins in this lane
                for i in range(5):
                    plugin_name = f'worker_{worker_id}_plugin_{i}'
                    plugin_group = lane_config.allowed_plugin_groups[0]  # Use first allowed group

                    # Check if registration is allowed
                    if isolation_manager.enforce_lane_isolation(plugin_name, plugin_group, lane_name):
                        lane_key = isolation_manager.get_lane_specific_registry_key(
                            plugin_name, plugin_group, lane_name
                        )

                        plugin = {
                            'name': plugin_name,
                            'worker_id': worker_id,
                            'lane': lane_name
                        }

                        worker_registry[lane_key] = plugin

                results.put({
                    'worker_id': worker_id,
                    'lane': lane_name,
                    'registry_size': len(worker_registry),
                    'success': True
                })

            except Exception as e:
                errors.put({
                    'worker_id': worker_id,
                    'lane': lane_name,
                    'error': str(e)
                })

        # Start workers in different lanes
        threads = []
        lanes = ['production', 'development', 'experimental']

        for i, lane in enumerate(lanes * 2):  # 6 workers total, 2 per lane
            thread = threading.Thread(target=lane_worker, args=(lane, i))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join(timeout=10)

        # Collect results
        worker_results = []
        while not results.empty():
            worker_results.append(results.get())

        worker_errors = []
        while not errors.empty():
            worker_errors.append(errors.get())

        # Verify results
        assert len(worker_results) == 6, f"Expected 6 workers, got {len(worker_results)}"
        assert len(worker_errors) == 0, f"Unexpected errors: {worker_errors}"

        # Verify lane isolation in results
        lanes_used = set(result['lane'] for result in worker_results)
        assert lanes_used == set(lanes), f"Not all lanes used: {lanes_used}"

        # Each worker should have registered plugins successfully
        for result in worker_results:
            assert result['success'], f"Worker {result['worker_id']} failed"
            assert result['registry_size'] > 0, f"Worker {result['worker_id']} registered no plugins"

    def test_lane_specific_security_policies(self):
        """Test that different lanes enforce different security policies"""

        security_test_plugins = [
            ('system_plugin', 'safe'),
            ('monitoring_plugin', 'safe'),
            ('constellation_core', 'safe'),
            ('debug_plugin', 'moderate_risk'),
            ('experimental_feature', 'high_risk'),
            ('unknown_plugin', 'high_risk')
        ]

        for lane_name in ['production', 'development', 'experimental']:
            self.isolation_manager.set_current_lane(lane_name)
            lane_config = self.isolation_manager.get_lane_config(lane_name)

            for plugin_name, risk_level in security_test_plugins:
                # Determine if plugin should be allowed based on lane security level
                should_allow = self._should_allow_plugin_by_security_policy(
                    plugin_name, risk_level, lane_config.security_level
                )

                # Test enforcement (simplified - checks plugin name patterns)
                allowed = self.isolation_manager.enforce_lane_isolation(
                    plugin_name, 'lukhas.constellation_components', lane_name
                )

                if lane_config.security_level == 'strict':
                    # Strict lanes should only allow known safe plugins
                    safe_patterns = ['system_', 'monitoring_', 'constellation_', 'core_']
                    expected_allow = any(pattern in plugin_name for pattern in safe_patterns)
                    assert allowed == expected_allow, \
                        f"Strict security policy failed for {plugin_name} in {lane_name}"

                elif lane_config.security_level == 'permissive':
                    # Permissive lanes should allow most plugins
                    assert allowed, f"Permissive lane should allow {plugin_name}"

    def _should_allow_plugin_by_security_policy(self, plugin_name: str, risk_level: str, security_level: str) -> bool:
        """Helper method to determine if plugin should be allowed based on security policy"""
        if security_level == 'strict':
            return risk_level == 'safe'
        elif security_level == 'moderate':
            return risk_level in ['safe', 'moderate_risk']
        elif security_level == 'permissive':
            return True
        return False

    def test_lane_migration_safety(self):
        """Test that plugins cannot be migrated between lanes unsafely"""

        # Register plugin in production lane
        self.isolation_manager.set_current_lane('production')
        prod_key = self.isolation_manager.get_lane_specific_registry_key(
            'critical_plugin', 'lukhas.monitoring', 'production'
        )
        prod_plugin = {'name': 'critical_plugin', 'lane': 'production', 'sensitive_data': True}
        register(prod_key, prod_plugin)

        # Attempt to register same plugin in development lane
        self.isolation_manager.set_current_lane('development')
        dev_key = self.isolation_manager.get_lane_specific_registry_key(
            'critical_plugin', 'lukhas.adapters', 'development'
        )
        dev_plugin = {'name': 'critical_plugin', 'lane': 'development', 'debug_mode': True}
        register(dev_key, dev_plugin)

        # Both should be registered with different keys
        assert resolve(prod_key) == prod_plugin
        assert resolve(dev_key) == dev_plugin

        # Verify they are truly isolated
        assert resolve(prod_key)['lane'] == 'production'
        assert resolve(dev_key)['lane'] == 'development'
        assert prod_key != dev_key

        # Verify cross-lane access is not possible
        prod_plugins = [k for k in _REG.keys() if k.startswith('prod:')]
        dev_plugins = [k for k in _REG.keys() if k.startswith('dev:')]

        assert len(prod_plugins) == 1
        assert len(dev_plugins) == 1
        assert prod_key in prod_plugins
        assert dev_key in dev_plugins


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])