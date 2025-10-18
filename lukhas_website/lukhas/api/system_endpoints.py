#!/usr/bin/env python3
"""
LUKHAS System API Endpoints

Provides system status and introspection endpoints:
- /system/plugins - Plugin registry status
- /system/health - System health check
- /system/flags - Feature flag status

Usage:
    from api.system_endpoints import get_plugins_status, get_system_health
"""

import json
import os
from datetime import datetime
from typing import Any, Dict

try:
    from lukhas.core.registry import get_plugin_registry
    REGISTRY_AVAILABLE = True
except ImportError:
    REGISTRY_AVAILABLE = False

try:
    from lukhas.core.import_router import ModuleRouter
    ROUTER_AVAILABLE = True
except ImportError:
    ROUTER_AVAILABLE = False


def get_plugins_status() -> Dict[str, Any]:
    """
    GET /system/plugins endpoint

    Returns comprehensive plugin registry status including:
    - Registered plugin counts by kind
    - Discovery mode and status
    - Plugin health metrics
    - Registry coverage validation
    """
    if not REGISTRY_AVAILABLE:
        return {
            "status": "unavailable",
            "error": "Registry module not available",
            "timestamp": datetime.utcnow().isoformat()
        }

    # Get plugin registry instance
    registry = get_plugin_registry()

    # Get registered plugins
    registered_plugins = registry.list_plugins()

    # Classify plugins by type/kind
    plugin_kinds = {}
    plugin_details = []

    for name, plugin_info in registered_plugins.items():
        kind = plugin_info.category
        plugin_kinds[kind] = plugin_kinds.get(kind, 0) + 1

        plugin_details.append({
            "name": plugin_info.name,
            "kind": kind,
            "type": plugin_info.category,
            "version": plugin_info.version,
            "description": plugin_info.description,
            "author": plugin_info.author,
            "healthy": True,  # Assume healthy if discovered
            "dependencies": plugin_info.dependencies
        })

    # Check discovery status
    discovery_flag = os.getenv("LUKHAS_PLUGIN_DISCOVERY", "off").lower()
    discovery_status = {
        "mode": discovery_flag,
        "enabled": discovery_flag == "auto",
        "registry_count": len(registered_plugins)
    }

    # Coverage validation - check for expected core kinds
    expected_kinds = ["CognitiveNode", "MemorySystem", "GuardianAgent", "MATRIZProcessor"]
    coverage = {
        "expected_kinds": expected_kinds,
        "found_kinds": list(plugin_kinds.keys()),
        "missing_kinds": [k for k in expected_kinds if k not in plugin_kinds],
        "coverage_rate": len([k for k in expected_kinds if k in plugin_kinds]) / len(expected_kinds) * 100
    }

    return {
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "discovery": discovery_status,
        "registry": {
            "total_plugins": len(registered_plugins),
            "plugin_kinds": plugin_kinds,
            "registry_size_bytes": _estimate_registry_size(registered_plugins)
        },
        "coverage": coverage,
        "plugins": plugin_details[:10],  # Limit to first 10 for brevity
        "total_plugin_count": len(plugin_details)
    }


def get_system_health() -> Dict[str, Any]:
    """
    GET /system/health endpoint

    Returns overall system health including:
    - Registry status
    - Router status
    - Feature flags
    - Critical system components
    """
    health_checks = {
        "registry": _check_registry_health(),
        "router": _check_router_health(),
        "features": _check_feature_flags(),
        "governance": _check_governance_health()
    }

    # Calculate overall health
    healthy_components = sum(1 for check in health_checks.values() if check.get("status") == "healthy")
    total_components = len(health_checks)
    overall_health = "healthy" if healthy_components == total_components else "degraded"

    return {
        "status": overall_health,
        "timestamp": datetime.utcnow().isoformat(),
        "components": health_checks,
        "summary": {
            "healthy_components": healthy_components,
            "total_components": total_components,
            "health_percentage": (healthy_components / total_components) * 100
        }
    }


def get_feature_flags() -> Dict[str, Any]:
    """
    GET /system/flags endpoint

    Returns current feature flag configuration
    """
    # Read from claude-code.json if available
    try:
        with open("claude-code.json", "r") as f:
            config = json.load(f)
            feature_flags = config.get("featureFlags", {})
    except Exception:
        feature_flags = {}

    # Also check environment variables
    env_flags = {
        "LUKHAS_LANE": os.getenv("LUKHAS_LANE", "experimental"),
        "LUKHAS_PLUGIN_DISCOVERY": os.getenv("LUKHAS_PLUGIN_DISCOVERY", "off"),
        "ENFORCE_ETHICS_DSL": os.getenv("ENFORCE_ETHICS_DSL", "0"),
        "LUKHAS_ADVANCED_TAGS": os.getenv("LUKHAS_ADVANCED_TAGS", "0"),
        "LUKHAS_CANARY_PERCENT": os.getenv("LUKHAS_CANARY_PERCENT", "0")
    }

    return {
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "config_flags": feature_flags,
        "env_flags": env_flags,
        "active_lane": env_flags["LUKHAS_LANE"],
        "guardian_enabled": feature_flags.get("ENFORCE_ETHICS_DSL") == "1" or env_flags["ENFORCE_ETHICS_DSL"] == "1",
        "canary_percentage": int(feature_flags.get("LUKHAS_CANARY_PERCENT", env_flags["LUKHAS_CANARY_PERCENT"]))
    }


def _check_plugin_health(plugin: Any) -> bool:
    """Check if a plugin appears healthy"""
    try:
        # Basic health checks
        if hasattr(plugin, 'health_check'):
            return plugin.health_check()

        # Check if it's a callable
        if callable(plugin):
            return True

        # Check if it has expected methods
        if hasattr(plugin, 'process') or hasattr(plugin, 'execute') or hasattr(plugin, 'run'):
            return True

        return True  # Default to healthy if no issues detected
    except Exception:
        return False


def _check_registry_health() -> Dict[str, Any]:
    """Check registry system health"""
    if not REGISTRY_AVAILABLE:
        return {"status": "unavailable", "error": "Registry not available"}

    try:
        plugin_count = len(_REG) if _REG else 0  # noqa: F821  # TODO: _REG
        discovery_mode = _DISCOVERY_FLAG  # noqa: F821  # TODO: _DISCOVERY_FLAG

        # Registry is healthy if it can store/retrieve plugins
        test_key = "_health_check_test"
        _REG[test_key] = "test_value"  # noqa: F821  # TODO: _REG
        can_write = _REG.get(test_key) == "test_value"  # noqa: F821  # TODO: _REG
        del _REG[test_key]  # noqa: F821  # TODO: _REG

        return {
            "status": "healthy" if can_write else "degraded",
            "plugin_count": plugin_count,
            "discovery_mode": discovery_mode,
            "can_read_write": can_write
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def _check_router_health() -> Dict[str, Any]:
    """Check import router health"""
    if not ROUTER_AVAILABLE:
        return {"status": "unavailable", "error": "Router not available"}

    try:
        router = ModuleRouter()
        # Test basic functionality
        known_module = "lukhas.core.registry"
        resolved = router.resolve_module_path(known_module)

        return {
            "status": "healthy" if resolved else "degraded",
            "can_resolve": resolved is not None,
            "cache_size": len(router._resolve_cache),
            "import_cache_size": len(router._import_cache)
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def _check_feature_flags() -> Dict[str, Any]:
    """Check feature flag system health"""
    try:
        flags = get_feature_flags()

        # Basic validation
        has_config = len(flags.get("config_flags", {})) > 0
        has_env = len(flags.get("env_flags", {})) > 0
        lane_set = flags.get("active_lane") != "unknown"

        return {
            "status": "healthy" if (has_config or has_env) and lane_set else "degraded",
            "config_available": has_config,
            "env_available": has_env,
            "lane_configured": lane_set
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def _check_governance_health() -> Dict[str, Any]:
    """Check governance system health"""
    try:
        # Check for guardian emergency disable file
        emergency_disable_path = "/tmp/guardian_emergency_disable"
        emergency_active = os.path.exists(emergency_disable_path)

        # Check if ethics enforcement is enabled
        flags = get_feature_flags()
        ethics_enabled = flags.get("guardian_enabled", False)

        return {
            "status": "healthy" if not emergency_active else "emergency_disabled",
            "ethics_enforcement": ethics_enabled,
            "emergency_disable_active": emergency_active,
            "canary_percentage": flags.get("canary_percentage", 0)
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def _estimate_registry_size(registry: Dict) -> int:
    """Estimate registry memory usage in bytes"""
    try:
        import sys
        total_size = 0
        for key, value in registry.items():
            total_size += sys.getsizeof(key)
            total_size += sys.getsizeof(value)
        return total_size
    except Exception:
        return 0


# Flask/FastAPI-compatible route handlers
def plugins_endpoint():
    """Flask/FastAPI route handler for /system/plugins"""
    return get_plugins_status()


def health_endpoint():
    """Flask/FastAPI route handler for /system/health"""
    return get_system_health()


def flags_endpoint():
    """Flask/FastAPI route handler for /system/flags"""
    return get_feature_flags()


# Simple test server for standalone testing
if __name__ == "__main__":
    print("🔍 Testing LUKHAS System API Endpoints...")
    print("=" * 50)

    print("\n📊 Plugins Status:")
    plugins = get_plugins_status()
    print(json.dumps(plugins, indent=2))

    print("\n❤️ System Health:")
    health = get_system_health()
    print(json.dumps(health, indent=2))

    print("\n🏳️ Feature Flags:")
    flags = get_feature_flags()
    print(json.dumps(flags, indent=2))
