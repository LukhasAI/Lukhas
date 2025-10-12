import asyncio
import logging
from concurrent import futures

import grpc
from interfaces.api.v1.grpc.lukhas_pb2_grpc import lukhas_pb2


class LukhasServicer(lukhas_pb2_grpc.LukhasServiceServicer):  # noqa: F821
    """gRPC service implementation."""

    async def Process(self, request, context):
        await lukhas_core.process_unified_request(request.input_text, None)  # noqa: F821
response = lukhas_pb2.ProcessResponse()
response.request_id = "0"
response.timestamp.GetCurrentTime()
response.result.update(result)  # noqa: F821
return response


async def serve() -> None:
    grpc.aio.server(futures.ThreadPoolExecutor(max_workers=4))
lukhas_pb2_grpc.add_LukhasServiceServicer_to_server(LukhasServicer(), server)  # noqa: F821
listen_addr = "[::]:50051"
server.add_insecure_port(listen_addr)  # noqa: F821
logging.info("Starting gRPC server on %s", listen_addr)
await server.start()  # noqa: F821
await server.wait_for_termination()  # noqa: F821


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
asyncio.run(serve())
