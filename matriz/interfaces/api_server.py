#!/usr/bin/env python3
"""
MATRIZ-AGI FastAPI Server
Production-ready REST API with WebSocket support for MATRIZ cognitive system

Features:
- RESTful endpoints for query processing
- WebSocket real-time interaction
- CORS configuration for web clients
- Health monitoring and diagnostics
- Node inspection and system introspection
- Complete OpenAPI/Swagger documentation
- Comprehensive error handling and validation
- Request/response logging and tracing
"""

import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Optional

import uvicorn
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, Field, validator
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

# Import MATRIZ components
from MATRIZ.core.orchestrator import CognitiveOrchestrator
from MATRIZ.nodes.fact_node import FactNode
from MATRIZ.nodes.math_node import MathNode
from MATRIZ.nodes.validator_node import ValidatorNode

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global orchestrator instance
orchestrator: Optional[CognitiveOrchestrator] = None
websocket_connections: list[WebSocket] = []


# Pydantic models for request/response validation
class QueryRequest(BaseModel):
    """Request model for cognitive query processing"""

    query: str = Field(..., min_length=1, max_length=10000, description="Query to process")
    trace_id: Optional[str] = Field(None, description="Optional execution trace ID")
    context: Optional[dict[str, Any]] = Field(
        default_factory=dict, description="Additional context"
    )
    include_trace: bool = Field(default=True, description="Include detailed execution trace")
    include_nodes: bool = Field(default=True, description="Include MATRIZ nodes in response")

    @validator("query")
    def validate_query(cls, v):
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()

    @validator("trace_id")
    def validate_trace_id(cls, v):
        if v and len(v) < 8:
            raise ValueError("Trace ID must be at least 8 characters")
        return v


class QueryResponse(BaseModel):
    """Response model for cognitive query processing"""

    answer: str = Field(..., description="Processing result")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in result")
    processing_time: float = Field(..., ge=0.0, description="Processing time in seconds")
    trace_id: str = Field(..., description="Execution trace identifier")
    timestamp: str = Field(..., description="ISO timestamp of processing")
    matriz_nodes: Optional[list[dict[str, Any]]] = Field(None, description="Generated MATRIZ nodes")
    trace: Optional[dict[str, Any]] = Field(None, description="Detailed execution trace")
    reasoning_chain: Optional[list[str]] = Field(None, description="Human-readable reasoning steps")


class HealthResponse(BaseModel):
    """Health check response model"""

    status: str = Field(..., description="Service status")
    timestamp: str = Field(..., description="ISO timestamp")
    version: str = Field(..., description="API version")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    registered_nodes: int = Field(..., description="Number of registered cognitive nodes")
    total_queries: int = Field(..., description="Total queries processed")
    active_websockets: int = Field(..., description="Number of active WebSocket connections")
    lane: str = Field(..., description="Active LUKHAS lane label")
    within_latency_budget: bool = Field(..., description="Latency budget compliance (250ms p95)")
    last_latency_ms: Optional[float] = Field(
        None, description="Most recent pipeline latency in milliseconds"
    )
    node_health_snapshot: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        description="Per-node health summary",
    )
    issues: list[str] = Field(default_factory=list, description="Active health concerns")


class NodeInfo(BaseModel):
    """Information about a cognitive node"""

    name: str = Field(..., description="Node name")
    capabilities: list[str] = Field(..., description="Node capabilities")
    tenant: str = Field(..., description="Node tenant")
    processing_history_count: int = Field(..., description="Number of processed items")


class SystemInfo(BaseModel):
    """System information and diagnostics"""

    nodes: list[NodeInfo] = Field(..., description="Registered cognitive nodes")
    matriz_graph_size: int = Field(..., description="Number of nodes in MATRIZ graph")
    execution_trace_count: int = Field(..., description="Number of execution traces")
    memory_nodes: int = Field(..., description="Nodes in context memory")


class WebSocketMessage(BaseModel):
    """WebSocket message format"""

    type: str = Field(..., description="Message type: query, response, error, ping, pong")
    data: Optional[dict[str, Any]] = Field(None, description="Message data")
    trace_id: Optional[str] = Field(None, description="Trace identifier")
    timestamp: str = Field(..., description="ISO timestamp")


# Global state tracking
start_time = time.time()
total_queries = 0


def _compute_orchestrator_health() -> dict[str, Any]:
    """Construct an orchestrator health snapshot for status endpoints."""
    lane = os.getenv("LUKHAS_LANE", "experimental").lower() or "unknown"

    snapshot: dict[str, Any] = {
        "lane": lane,
        "status": "critical",
        "registered_nodes": 0,
        "within_latency_budget": False,
        "last_latency_ms": None,
        "node_health_snapshot": {},
        "issues": [],
    }

    if orchestrator is None:
        snapshot["issues"].append("orchestrator_not_initialized")
        return snapshot

    registered_nodes = len(orchestrator.available_nodes)
    snapshot["registered_nodes"] = registered_nodes
    snapshot["node_health_snapshot"] = {
        name: {
            "capabilities": getattr(node, "capabilities", []),
            "healthy": True,
        }
        for name, node in orchestrator.available_nodes.items()
    }

    if registered_nodes == 0:
        snapshot["issues"].append("no_nodes_registered")
    else:
        snapshot["status"] = "healthy"

    if orchestrator.execution_trace:
        last_trace = orchestrator.execution_trace[-1]
        last_latency_ms = last_trace.processing_time * 1000
        snapshot["last_latency_ms"] = last_latency_ms
        within_budget = last_latency_ms <= 250
        snapshot["within_latency_budget"] = within_budget
        if not within_budget:
            snapshot["issues"].append("latency_budget_exceeded")
            snapshot["status"] = "degraded"
    else:
        snapshot["within_latency_budget"] = True
        if snapshot["status"] == "healthy" and total_queries == 0:
            snapshot["issues"].append("no_queries_processed")

    if snapshot["status"] == "critical" and not snapshot["issues"]:
        snapshot["issues"].append("unknown_issue")

    return snapshot


def get_orchestrator() -> CognitiveOrchestrator:
    """Dependency to get the orchestrator instance"""
    global orchestrator
    if orchestrator is None:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")
    return orchestrator


async def initialize_orchestrator():
    """Initialize the cognitive orchestrator with default nodes"""
    global orchestrator

    logger.info("Initializing MATRIZ Cognitive Orchestrator...")

    try:
        orchestrator = CognitiveOrchestrator()

        # Register cognitive nodes
        math_node = MathNode(tenant="api_server", precision=8)
        fact_node = FactNode(tenant="api_server")
        validator_node = ValidatorNode(tenant="api_server")

        orchestrator.register_node("math", math_node)
        orchestrator.register_node("facts", fact_node)
        orchestrator.register_node("validator", validator_node)

        logger.info("✓ Orchestrator initialized successfully")
        logger.info(f"✓ Registered {len(orchestrator.available_nodes)} cognitive nodes")

    except Exception as e:
        logger.error(f"Failed to initialize orchestrator: {e!s}")
        raise


async def cleanup_orchestrator():
    """Cleanup orchestrator resources"""
    global orchestrator
    if orchestrator:
        logger.info("Cleaning up orchestrator...")
        # Close any open resources if needed
        orchestrator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    # Startup
    await initialize_orchestrator()
    logger.info("MATRIZ-AGI FastAPI server started")

    yield

    # Shutdown
    await cleanup_orchestrator()
    logger.info("MATRIZ-AGI FastAPI server stopped")


# Create FastAPI application
app = FastAPI(
    title="MATRIZ-AGI Cognitive API",
    description="""
    Production-ready REST API for MATRIZ Autonomous General Intelligence system.

    This API provides access to cognitive processing capabilities through MATRIZ nodes:
    - Mathematical computation and expression evaluation
    - Fact-based question answering
    - Query validation and quality assessment
    - Real-time processing via WebSocket
    - Complete execution tracing and audit trails

    All processing follows the MATRIZ format for full interpretability and governance.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    servers=[
        {"url": "http://localhost:8000", "description": "Development server"},
        {
            "url": "https://api.matriz-agi.example.com",
            "description": "Production server",
        },
    ],
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc!s}", exc_info=True)
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trace_id": str(uuid.uuid4()),
        },
    )


# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to documentation"""
    return RedirectResponse(url="/docs")


# Health check endpoints
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Basic health check endpoint"""
    global total_queries, start_time, websocket_connections, orchestrator
    snapshot = _compute_orchestrator_health()

    return HealthResponse(
        status=snapshot["status"],
        timestamp=datetime.now(timezone.utc).isoformat(),
        version="1.0.0",
        uptime_seconds=time.time() - start_time,
        registered_nodes=snapshot["registered_nodes"],
        total_queries=total_queries,
        active_websockets=len(websocket_connections),
        lane=snapshot["lane"],
        within_latency_budget=snapshot["within_latency_budget"],
        last_latency_ms=snapshot["last_latency_ms"],
        node_health_snapshot=snapshot["node_health_snapshot"],
        issues=snapshot["issues"],
    )


@app.get("/health/ready", tags=["Health"])
async def readiness_check():
    """Readiness check for container orchestration"""
    snapshot = _compute_orchestrator_health()
    if snapshot["status"] == "critical":
        raise HTTPException(
            status_code=503,
            detail={"status": "not_ready", "issues": snapshot["issues"]},
        )

    return {
        "status": "ready",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "lane": snapshot["lane"],
        "within_latency_budget": snapshot["within_latency_budget"],
        "issues": snapshot["issues"],
    }


@app.get("/health/live", tags=["Health"])
async def liveness_check():
    """Liveness check for container orchestration"""
    snapshot = _compute_orchestrator_health()
    return {
        "status": "alive",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "lane": snapshot["lane"],
    }


# Query processing endpoints
@app.post("/query", response_model=QueryResponse, tags=["Cognitive Processing"])
async def process_query(
    request: QueryRequest,
    background_tasks: BackgroundTasks,
    orch: CognitiveOrchestrator = Depends(get_orchestrator),  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_matriz_interfaces_api_server_py_L370"}
):
    """
    Process a cognitive query through MATRIZ nodes

    This endpoint routes queries through the appropriate cognitive nodes based on
    intent analysis and returns complete results with tracing information.
    """
    global total_queries

    start_time_req = time.time()
    trace_id = request.trace_id or str(uuid.uuid4())

    logger.info(f"Processing query: {request.query[:100]}... (trace: {trace_id})")

    try:
        # Process through orchestrator
        result = orch.process_query(request.query)

        # Update global stats
        total_queries += 1

        # Prepare response
        response_data = {
            "answer": result.get("answer", "No answer provided"),
            "confidence": result.get("confidence", 0.0),
            "processing_time": time.time() - start_time_req,
            "trace_id": trace_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Include optional data based on request
        if request.include_nodes:
            response_data["matriz_nodes"] = result.get("matriz_nodes", [])

        if request.include_trace:
            response_data["trace"] = result.get("trace", {})
            response_data["reasoning_chain"] = result.get("reasoning_chain", [])

        # Log successful processing
        logger.info(
            f"Query processed successfully (trace: {trace_id}, time: {response_data['processing_time']:.3f}s)"
        )

        # Send to WebSocket clients in background
        if websocket_connections:
            background_tasks.add_task(
                broadcast_to_websockets,
                {
                    "type": "query_processed",
                    "data": {
                        "query": request.query,
                        "answer": response_data["answer"],
                        "confidence": response_data["confidence"],
                        "trace_id": trace_id,
                    },
                    "timestamp": response_data["timestamp"],
                },
            )

        return QueryResponse(**response_data)

    except Exception as e:
        logger.error(f"Query processing failed (trace: {trace_id}): {e!s}")
        raise HTTPException(  # TODO[T4-ISSUE]: {"code": "B904", "ticket": "GH-1031", "owner": "consciousness-team", "status": "planned", "reason": "Exception re-raise pattern - needs review for proper chaining (raise...from)", "estimate": "15m", "priority": "medium", "dependencies": "none", "id": "matriz_interfaces_api_server_py_L434"}
            status_code=500,
            detail={
                "error": "Query processing failed",
                "message": str(e),
                "trace_id": trace_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )


# System introspection endpoints
@app.get("/system/info", response_model=SystemInfo, tags=["System"])
async def system_info(orch: CognitiveOrchestrator = Depends(get_orchestrator)):  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_matriz_interfaces_api_server_py_L447"}
    """Get comprehensive system information and diagnostics"""

    nodes = []
    for name, node in orch.available_nodes.items():
        nodes.append(
            NodeInfo(
                name=name,
                capabilities=node.capabilities,
                tenant=node.tenant,
                processing_history_count=len(node.processing_history),
            )
        )

    return SystemInfo(
        nodes=nodes,
        matriz_graph_size=len(orch.matriz_graph),
        execution_trace_count=len(orch.execution_trace),
        memory_nodes=len(orch.context_memory),
    )


@app.get("/system/nodes", tags=["System"])
async def list_nodes(orch: CognitiveOrchestrator = Depends(get_orchestrator)):  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_matriz_interfaces_api_server_py_L470"}
    """List all registered cognitive nodes"""
    nodes = {}
    for name, node in orch.available_nodes.items():
        nodes[name] = {
            "name": node.node_name,
            "capabilities": node.capabilities,
            "tenant": node.tenant,
            "class": node.__class__.__name__,
            "processing_history_count": len(node.processing_history),
        }
    return {"nodes": nodes}


@app.get("/system/nodes/{node_name}", tags=["System"])
async def get_node_details(node_name: str, orch: CognitiveOrchestrator = Depends(get_orchestrator)):  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_matriz_interfaces_api_server_py_L485"}
    """Get detailed information about a specific cognitive node"""
    if node_name not in orch.available_nodes:
        raise HTTPException(status_code=404, detail=f"Node '{node_name}' not found")

    node = orch.available_nodes[node_name]

    return {
        "name": node.node_name,
        "capabilities": node.capabilities,
        "tenant": node.tenant,
        "class": node.__class__.__name__,
        "processing_history_count": len(node.processing_history),
        "recent_traces": node.get_trace()[-5:] if node.get_trace() else [],
    }


@app.get("/system/graph", tags=["System"])
async def get_matriz_graph(
    orch: CognitiveOrchestrator = Depends(get_orchestrator), limit: int = 100  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_matriz_interfaces_api_server_py_L504"}
):
    """Get the MATRIZ graph nodes (limited for performance)"""
    nodes = list(orch.matriz_graph.values())[-limit:]
    return {
        "total_nodes": len(orch.matriz_graph),
        "returned_nodes": len(nodes),
        "nodes": nodes,
    }


@app.get("/system/trace", tags=["System"])
async def get_execution_trace(
    orch: CognitiveOrchestrator = Depends(get_orchestrator), limit: int = 50  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_matriz_interfaces_api_server_py_L517"}
):
    """Get recent execution traces"""
    traces = orch.execution_trace[-limit:]
    return {
        "total_traces": len(orch.execution_trace),
        "returned_traces": len(traces),
        "traces": [
            {
                "timestamp": trace.timestamp.isoformat(),
                "node_id": trace.node_id,
                "processing_time": trace.processing_time,
                "validation_result": trace.validation_result,
                "reasoning_chain": trace.reasoning_chain,
            }
            for trace in traces
        ],
    }


@app.get("/system/causal/{node_id}", tags=["System"])
async def get_causal_chain(node_id: str, orch: CognitiveOrchestrator = Depends(get_orchestrator)):  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_matriz_interfaces_api_server_py_L538"}
    """Get the causal chain for a specific MATRIZ node"""
    chain = orch.get_causal_chain(node_id)
    return {"node_id": node_id, "chain_length": len(chain), "causal_chain": chain}


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time interaction

    Supports:
    - Real-time query processing
    - System status updates
    - Processing notifications
    - Bidirectional communication
    """
    await websocket.accept()
    websocket_connections.append(websocket)
    client_id = str(uuid.uuid4())[:8]

    logger.info(f"WebSocket client connected: {client_id}")

    # Send welcome message
    await websocket.send_json(
        {
            "type": "connected",
            "data": {
                "client_id": client_id,
                "message": "Connected to MATRIZ-AGI WebSocket",
                "available_nodes": (
                    list(orchestrator.available_nodes.keys()) if orchestrator else []
                ),
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )

    try:
        while True:
            # Receive message from client
            message = await websocket.receive_json()

            try:
                # Parse message
                ws_message = WebSocketMessage(**message)
                logger.info(f"WebSocket message from {client_id}: {ws_message.type}")

                if ws_message.type == "ping":
                    # Respond to ping
                    await websocket.send_json(
                        {
                            "type": "pong",
                            "data": ws_message.data,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        }
                    )

                elif ws_message.type == "query":
                    # Process query
                    query_data = ws_message.data or {}
                    query_text = query_data.get("query", "")

                    if not query_text:
                        await websocket.send_json(
                            {
                                "type": "error",
                                "data": {"error": "No query provided"},
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                            }
                        )
                        continue

                    # Process through orchestrator
                    start_time_ws = time.time()
                    result = orchestrator.process_query(query_text)
                    processing_time = time.time() - start_time_ws

                    # Send response
                    await websocket.send_json(
                        {
                            "type": "response",
                            "data": {
                                "answer": result.get("answer", "No answer"),
                                "confidence": result.get("confidence", 0.0),
                                "processing_time": processing_time,
                                "matriz_nodes": result.get("matriz_nodes", []),
                                "reasoning_chain": result.get("reasoning_chain", []),
                            },
                            "trace_id": ws_message.trace_id or str(uuid.uuid4()),
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        }
                    )

                    global total_queries
                    total_queries += 1

                elif ws_message.type == "system_info":
                    # Send system information
                    nodes = {}
                    if orchestrator:
                        for name, node in orchestrator.available_nodes.items():
                            nodes[name] = {
                                "capabilities": node.capabilities,
                                "processing_history_count": len(node.processing_history),
                            }

                    await websocket.send_json(
                        {
                            "type": "system_info",
                            "data": {
                                "nodes": nodes,
                                "matriz_graph_size": (
                                    len(orchestrator.matriz_graph) if orchestrator else 0
                                ),
                                "execution_trace_count": (
                                    len(orchestrator.execution_trace) if orchestrator else 0
                                ),
                                "total_queries": total_queries,
                                "uptime_seconds": time.time() - start_time,
                            },
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        }
                    )

                else:
                    # Unknown message type
                    await websocket.send_json(
                        {
                            "type": "error",
                            "data": {"error": f"Unknown message type: {ws_message.type}"},
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        }
                    )

            except Exception as e:
                logger.error(f"WebSocket message processing error: {e!s}")
                await websocket.send_json(
                    {
                        "type": "error",
                        "data": {"error": str(e)},
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )

    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected: {client_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e!s}")
    finally:
        if websocket in websocket_connections:
            websocket_connections.remove(websocket)


async def broadcast_to_websockets(message: dict[str, Any]):
    """Broadcast message to all connected WebSocket clients"""
    if not websocket_connections:
        return

    # Send to all connected clients
    disconnected = []
    for websocket in websocket_connections:
        try:
            await websocket.send_json(message)
        except Exception:
            # Client disconnected
            disconnected.append(websocket)

    # Remove disconnected clients
    for ws in disconnected:
        if ws in websocket_connections:
            websocket_connections.remove(ws)


# Development server function
def run_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
    log_level: str = "info",
):
    """
    Run the FastAPI server with uvicorn

    Args:
        host: Host to bind to
        port: Port to listen on
        reload: Enable auto-reload for development
        log_level: Logging level
    """
    logger.info(f"Starting MATRIZ-AGI FastAPI server on {host}:{port}")

    uvicorn.run(
        "matriz.interfaces.api_server:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
        access_log=True,
    )


# CLI entry point
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="MATRIZ-AGI FastAPI Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--log-level", default="info", help="Log level")

    args = parser.parse_args()

    run_server(host=args.host, port=args.port, reload=args.reload, log_level=args.log_level)
