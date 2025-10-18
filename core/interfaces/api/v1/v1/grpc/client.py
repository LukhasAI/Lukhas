


class LukhasGRPCClient:
    """gRPC client for LUKHAS service."""

    def __init__(self, host: str = "localhost", port: int = 50051):
        self.address = f"{host}:{port}"
