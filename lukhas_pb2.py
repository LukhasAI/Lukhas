"""
⚠️  PROTOBUF STUB - SHOULD BE AUTO-GENERATED ⚠️

This is a compatibility stub for Protocol Buffers.

🎯 REAL PROTOBUF FILE FOUND AT:
   - candidate/core/interfaces/api/v1/grpc/system.proto (REAL PROTO DEFINITION)

📋 TODO FOR AGENT INTEGRATION:
   1. Run: protoc --python_out=. candidate/core/interfaces/api/v1/grpc/system.proto
   2. This will generate proper lukhas_pb2.py with all message classes
   3. Replace this stub with generated protobuf module

🔍 EXPECTED MESSAGES FROM PROTO FILE:
   - ProcessRequest, ProcessResponse, SymbolicState
   - HealthRequest, HealthResponse
   - ProcessingMode enum with SYMBOLIC/CAUSAL/HYBRID modes
   - LukhasService GRPC service definition

⚠️  DO NOT DEVELOP ON THIS STUB - GENERATE FROM .proto FILE ⚠️

GENERATE COMMAND:
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
protoc --python_out=. candidate/core/interfaces/api/v1/grpc/system.proto
"""

# Processing modes (from system.proto)
PROCESSING_MODE_UNSPECIFIED = 0
PROCESSING_MODE_SYMBOLIC = 1
PROCESSING_MODE_CAUSAL = 2
PROCESSING_MODE_HYBRID = 3


class ProcessRequest:
    """Stub ProcessRequest protobuf message"""

    def __init__(self):
        self.mode = PROCESSING_MODE_SYMBOLIC
        self.data = ""
        self.metadata = {}

    def SerializeToString(self) -> bytes:
        """Serialize to bytes (stub)"""
        return b""

    def ParseFromString(self, data: bytes):
        """Parse from bytes (stub)"""
        pass


class ProcessResponse:
    """Stub ProcessResponse protobuf message"""

    def __init__(self):
        self.success = True
        self.result = ""
        self.error = ""
        self.metadata = {}

    def SerializeToString(self) -> bytes:
        """Serialize to bytes (stub)"""
        return b""

    def ParseFromString(self, data: bytes):
        """Parse from bytes (stub)"""
        pass


class HealthRequest:
    """Stub HealthRequest protobuf message"""

    def __init__(self):
        self.service = ""

    def SerializeToString(self) -> bytes:
        """Serialize to bytes (stub)"""
        return b""

    def ParseFromString(self, data: bytes):
        """Parse from bytes (stub)"""
        pass


class HealthResponse:
    """Stub HealthResponse protobuf message"""

    def __init__(self):
        self.status = "SERVING"

    def SerializeToString(self) -> bytes:
        """Serialize to bytes (stub)"""
        return b""

    def ParseFromString(self, data: bytes):
        """Parse from bytes (stub)"""
        pass


__all__ = [
    "ProcessRequest",
    "ProcessResponse",
    "HealthRequest",
    "HealthResponse",
    "PROCESSING_MODE_SYMBOLIC",
    "PROCESSING_MODE_CAUSAL",
    "PROCESSING_MODE_HYBRID",
]
