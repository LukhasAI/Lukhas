#!/usr/bin/env python3
"""
FastAPI webhook receiver for AI agent status updates.
Receives webhooks from Jules/Codex and enqueues tasks to Redis.
"""
import asyncio
import logging
import uuid
from typing import Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.queue.redis_queue import RedisTaskQueue, Task, TaskPriority, TaskType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LUKHAS AI Webhook Receiver",
    description="Receives AI agent status updates and enqueues tasks to Redis",
    version="1.0.0"
)


class WebhookPayload(BaseModel):
    """Webhook payload from AI agents"""
    agent: str = Field(..., description="Agent name (jules/codex/gemini/ollama)")
    session_id: Optional[str] = Field(None, description="Agent session ID")
    status: str = Field(..., description="Status (waiting_for_user/error/completed/failed)")
    message: Optional[str] = Field(None, description="Status message")
    error: Optional[str] = Field(None, description="Error message if failed")
    pr_number: Optional[int] = Field(None, description="Associated PR number")
    file_paths: list[str] = Field(default_factory=list, description="Related files")
    context: dict[str, Any] = Field(default_factory=dict, description="Additional context")


def map_status_to_priority(status: str, error: Optional[str] = None) -> TaskPriority:
    """
    Map agent status to task priority.

    Priority mapping:
    - error/failed + architectural violation → CRITICAL
    - error/failed → HIGH
    - waiting_for_user → MEDIUM
    - completed/other → LOW
    """
    status_lower = status.lower()

    if status_lower in ("error", "failed"):
        # Check if error mentions architectural violation
        if error and any(keyword in error.lower() for keyword in
                        ["trinity", "architecture", "import", "boundary"]):
            return TaskPriority.CRITICAL
        return TaskPriority.HIGH

    if status_lower == "waiting_for_user":
        return TaskPriority.MEDIUM

    return TaskPriority.LOW


def map_status_to_task_type(status: str, message: Optional[str] = None) -> str:
    """Map status to task type"""
    status_lower = status.lower()

    # Check message content for architectural violations
    if message:
        msg_lower = message.lower()
        if any(keyword in msg_lower for keyword in ["trinity", "architecture", "import", "boundary"]):
            return TaskType.ARCHITECTURAL_VIOLATION
        if "test" in msg_lower:
            return TaskType.TEST_CREATION
        if "bug" in msg_lower or "fix" in msg_lower:
            return TaskType.BUG_FIX
        if "doc" in msg_lower:
            return TaskType.DOCUMENTATION
        if "refactor" in msg_lower:
            return TaskType.REFACTORING

    # Default mapping by status
    if status_lower in ("error", "failed"):
        return TaskType.BUG_FIX

    return TaskType.TODO_COMMENT


@app.post("/webhook/ai-status")
async def receive_ai_status(payload: WebhookPayload):
    """
    Receive AI agent status webhook and enqueue task to Redis.

    Example payload:
    {
        "agent": "jules",
        "session_id": "sessions/123",
        "status": "waiting_for_user",
        "message": "Plan created, awaiting approval",
        "pr_number": 42,
        "file_paths": ["bridge/queue/redis_queue.py"],
        "context": {"session_url": "https://..."}
    }
    """
    logger.info(f"Received webhook from {payload.agent}: {payload.status}")

    try:
        # Map status to priority and task type
        priority = map_status_to_priority(payload.status, payload.error)
        task_type = map_status_to_task_type(payload.status, payload.message)

        # Create task
        task = Task(
            task_id=str(uuid.uuid4()),
            task_type=task_type,
            priority=priority,
            agent=payload.agent,
            prompt=payload.message or f"Handle {payload.status} from {payload.agent}",
            context={
                "session_id": payload.session_id,
                "status": payload.status,
                "error": payload.error,
                **payload.context
            },
            pr_number=payload.pr_number,
            file_paths=payload.file_paths,
            created_at=datetime.utcnow()
        )

        # Enqueue to Redis
        async with RedisTaskQueue() as queue:
            await queue.enqueue(task)

        logger.info(
            f"✅ Enqueued task {task.task_id[:8]}... "
            f"(priority={priority.name}, type={task_type})"
        )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "task_id": task.task_id,
                "priority": priority.name,
                "message": f"Task enqueued successfully"
            }
        )

    except Exception as e:
        logger.error(f"❌ Failed to enqueue task: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to enqueue task: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        async with RedisTaskQueue() as queue:
            size = await queue.queue_size()

        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "redis_connected": True,
                "queue_size": size,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "redis_connected": False,
                "error": str(e)
            }
        )


@app.get("/queue/status")
async def queue_status():
    """Get current queue status"""
    try:
        async with RedisTaskQueue() as queue:
            size = await queue.queue_size()
            tasks = await queue.peek(count=20)

        return JSONResponse(
            status_code=200,
            content={
                "queue_size": size,
                "tasks": tasks,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Failed to get queue status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="LUKHAS AI Webhook Receiver")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")

    args = parser.parse_args()

    logger.info(f"🚀 Starting LUKHAS AI Webhook Receiver on {args.host}:{args.port}")
    logger.info("📡 Listening for webhooks at POST /webhook/ai-status")

    uvicorn.run(
        "ai_webhook_receiver:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )
