from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import logging

class DreamEvent:
    def __init__(self, event_type, data, progress_percent):
        self.type = event_type
        self.data = data
        self.progress_percent = progress_percent

    def to_dict(self):
        return self.data

class DreamEngine:
    async def stream_generate(self, user_id: str):
        yield DreamEvent("dream_start", {"message": f"Dream generation started for {user_id}"}, 0)
        await asyncio.sleep(0.2)

        for i in range(1, 10):
            yield DreamEvent(
                "dream_progress",
                {"status": "generating", "step": i},
                i * 10
            )
            await asyncio.sleep(0.1)

        await asyncio.sleep(0.2)
        yield DreamEvent("dream_complete", {"narrative": "A beautiful dream about flying."}, 100)

async def authenticate_websocket(token: str):
    if token == "valid-token":
        return {"id": "user123"}
    return None

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/ws/dreams/stream")
async def dream_stream_websocket(websocket: WebSocket, token: str):
    user = await authenticate_websocket(token)
    if not user:
        await websocket.close(code=1008)
        return

    await websocket.accept()

    try:
        async for event in generate_dream_stream(user):
            await websocket.send_json({
                "type": event["type"],
                "data": event["data"],
                "progress": event["progress_percent"]
            })
    except WebSocketDisconnect:
        # This is expected when the client closes the connection
        pass
    finally:
        logger.info(f"Client disconnected: {user['id']}")

async def generate_dream_stream(user: dict):
    dream_engine = DreamEngine()
    async for event in dream_engine.stream_generate(user["id"]):
        yield {
            "type": event.type,
            "data": event.to_dict(),
            "progress_percent": event.progress_percent
        }
