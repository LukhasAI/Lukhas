from typing import Any, Optional

import grpc
from interfaces.api.v1.grpc.lukhas_pb2_grpc import lukhas_pb2_grpc


class LukhasGRPCClient:
    """gRPC client for LUKHAS service."""

    def __init__(self, host: str = "localhost", port: int = 50051):
        self.address = f"{host}:{port}"
        self.channel: grpc.aio.Channel | None = None
        self.stub: lukhas_pb2_grpc.LukhasServiceStub | None = None

    async def __aenter__(self):
        self.channel = grpc.aio.insecure_channel(self.address)
        self.stub = lukhas_pb2_grpc.LukhasServiceStub(self.channel)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.channel:
            await self.channel.close()

    async def process(
        self,
        text: str,
        mode: str = "hybrid",
        context: Optional[dict[str, Any]] = None,
        options: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        request = lukhas_pb2.ProcessRequest()
        request.input_text = text
        mode_map = {
            "symbolic": lukhas_pb2.PROCESSING_MODE_SYMBOLIC,
            "causal": lukhas_pb2.PROCESSING_MODE_CAUSAL,
            "hybrid": lukhas_pb2.PROCESSING_MODE_HYBRID,
        }
        request.mode = mode_map.get(mode, lukhas_pb2.PROCESSING_MODE_HYBRID)
        if context:
            for k, v in context.items():
                request.context[k] = v
        if options:
            for k, v in options.items():
                request.options[k] = v
        if not self.stub:
            raise RuntimeError("Client not connected")
        response = await self.stub.Process(request)
        return {
            "request_id": response.request_id,
            "result": dict(response.result),
            "processing_time_ms": response.processing_time_ms,
        }
