import time
from typing import Any, Optional

import grpc
import streamlit as st
from interfaces.api.v1.grpc.lukhas_pb2_grpc import lukhas_pb2_grpc


class LukhasGRPCClient:
    """gRPC client for LUKHAS service."""

    def __init__(self, host: str = "localhost", port: int = 50051):
        self.address = f"{host}:{port}"
