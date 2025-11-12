import asyncio
import logging
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from .dream_engine import DreamEngine

router = APIRouter()
logger = logging.getLogger(__name__)

# TODO: Integrate proper authentication (e.g., database, cache, or external provider)
# Remove mock credentials from production code. See CodeQL rule: hardcoded credentials.


async def authenticate_websocket(token: str) -> dict | None:
    """Authentication logic for WebSocket connections.
    TODO: Implement real authentication. This is a placeholder.
    """
    # raise NotImplementedError("Authentication integration required")
    return None  # Always fails until proper authentication is implemented
async def get_token(websocket: WebSocket) -> str:
    """Dependency to extract and validate token from query params."""
    token = websocket.query_params.get("token")
    if not token:
        raise WebSocketDisconnect("Missing token")
    return token


@router.websocket("/ws/dreams/stream")
async def dream_stream_websocket(websocket: WebSocket, token: str = Depends(get_token)):
    # Authenticate
    user = await authenticate_websocket(token)
    if not user:
        await websocket.close(code=1008, reason="Authentication failed")
        return

    await websocket.accept()

    try:
        dream_engine = DreamEngine()
        async for event in dream_engine.stream_generate(user["id"]):
            await websocket.send_json(
                {
                    "type": event["type"],
                    "data": event["data"],
                    "progress": event["progress"],
                }
            )
    except WebSocketDisconnect:
        logger.info(f"Client disconnected: {user['id']}")
