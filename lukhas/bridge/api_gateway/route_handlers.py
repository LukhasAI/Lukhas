"""Shim: lukhas.bridge.api_gateway.route_handlers → candidate.bridge.api_gateway.route_handlers."""
try:
    from labs.bridge.api_gateway.route_handlers import *  # noqa: F403
except ImportError:
    try:
        from bridge.api_gateway.route_handlers import *  # noqa: F403
    except ImportError:
        pass
