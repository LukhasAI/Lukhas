"""
LUKHAS Protocol Buffer Module
============================

Provides access to LUKHAS gRPC protocol buffer definitions.
This is an alias module that imports from the actual implementation.
"""

# Import all protocol buffer definitions
try:
    from candidate.core.interfaces.api.v1.grpc.pb2 import *
    from candidate.core.interfaces.api.v1.grpc import pb2
    
    # Make all pb2 components available directly
    locals().update(pb2.__dict__)
    
    # Ensure common protocol buffer classes are available
    if hasattr(pb2, 'ProcessRequest'):
        ProcessRequest = pb2.ProcessRequest
    if hasattr(pb2, 'ProcessResponse'):
        ProcessResponse = pb2.ProcessResponse
    if hasattr(pb2, 'HealthRequest'):
        HealthRequest = pb2.HealthRequest
    if hasattr(pb2, 'HealthResponse'):
        HealthResponse = pb2.HealthResponse
    
    __all__ = [name for name in dir(pb2) if not name.startswith('_')]
    
except ImportError as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Could not import LUKHAS protocol buffers: {e}")
    
    # Provide minimal stubs for protocol buffer classes
    class ProcessRequest:
        def __init__(self):
            pass
    
    class ProcessResponse:
        def __init__(self):
            pass
    
    class HealthRequest:
        def __init__(self):
            pass
    
    class HealthResponse:
        def __init__(self):
            pass
    
    __all__ = ['ProcessRequest', 'ProcessResponse', 'HealthRequest', 'HealthResponse']
