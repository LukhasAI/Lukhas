"""
Memory Service FastAPI Application
==================================

High-performance FastAPI service for distributed memory operations.
Implements T4/0.01% excellence SLOs with comprehensive observability,
backpressure control, and circuit breaker protection.

Features:
- RESTful API with OpenAPI documentation
- Async/await for high concurrency
- Circuit breaker and backpressure integration
- Prometheus metrics endpoint
- Health checks and readiness probes
- Request/response validation with Pydantic
- Rate limiting and abuse protection
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field

from .adapters.vector_store_base import VectorStoreFactory, VectorStoreType
from .api_read import MemoryReadService, SearchQuery, SearchResponse, SearchType
from .api_write import BatchWriteOperation, MemoryWriteService, WriteOperation, WriteResult
from .backpressure import AdaptiveBackpressure, BackpressureFactory, BackpressureMode
from .circuit_breaker import CircuitBreakerError, CircuitBreakerFactory, CircuitBreakerRegistry
from .metrics import export_prometheus_metrics, get_t4_compliance_report, time_async_operation

logger = logging.getLogger(__name__)


# Request/Response Models
class SearchRequest(BaseModel):
    """Memory search request"""
    query: str = Field(..., min_length=1, max_length=10000)
    search_type: SearchType = SearchType.HYBRID
    top_k: int = Field(default=10, ge=1, le=1000)
    metadata_filter: Optional[Dict[str, Any]] = None
    include_content: bool = True
    include_vectors: bool = False
    fold_ids: Optional[List[str]] = None
    min_score: Optional[float] = Field(None, ge=0.0, le=1.0)


class UpsertRequest(BaseModel):
    """Memory upsert request"""
    fold_id: Optional[str] = None
    content: str = Field(..., min_length=1, max_length=100000)
    metadata: Optional[Dict[str, Any]] = None
    ttl_seconds: Optional[int] = Field(None, gt=0, le=86400*30)  # Max 30 days
    embedding: Optional[List[float]] = None


class BatchUpsertRequest(BaseModel):
    """Batch memory upsert request"""
    operations: List[UpsertRequest] = Field(..., min_items=1, max_items=1000)
    atomic: bool = True


class DeleteRequest(BaseModel):
    """Memory delete request"""
    fold_ids: List[str] = Field(..., min_items=1, max_items=1000)
    soft_delete: bool = True


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: float
    version: str
    components: Dict[str, Any]


class MetricsResponse(BaseModel):
    """Metrics response"""
    timestamp: float
    t4_compliance: Dict[str, Any]
    circuit_breakers: Dict[str, Any]
    backpressure: Dict[str, Any]


# Global service instances
read_service: Optional[MemoryReadService] = None
write_service: Optional[MemoryWriteService] = None
circuit_breakers: Optional[CircuitBreakerRegistry] = None
backpressure: Optional[AdaptiveBackpressure] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    await startup_services()
    yield
    # Shutdown
    await shutdown_services()


async def startup_services():
    """Initialize all services"""
    global read_service, write_service, circuit_breakers, backpressure

    try:
        logger.info("Starting memory services...")

        # Initialize circuit breakers
        circuit_breakers = CircuitBreakerRegistry()
        read_breaker = circuit_breakers.create_breaker(
            'memory_read',
            CircuitBreakerFactory.create_memory_service_config()
        )
        write_breaker = circuit_breakers.create_breaker(
            'memory_write',
            CircuitBreakerFactory.create_memory_service_config()
        )

        # Initialize backpressure
        backpressure_configs = BackpressureFactory.create_memory_service_config()
        backpressure = AdaptiveBackpressure(backpressure_configs)

        # Initialize vector store (using PostgreSQL for production)
        vector_store_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'lukhas_memory',
            'user': 'lukhas_user',
            'password': 'secure_password',
            'table_name': 'memory_vectors',
            'vector_dimensions': 1536,
            'pool_size': 20
        }

        vector_store = VectorStoreFactory.create(
            VectorStoreType.POSTGRESQL,
            vector_store_config
        )

        await vector_store.initialize()

        # Initialize read service
        read_service = MemoryReadService(
            vector_store=vector_store,
            circuit_breaker=read_breaker,
            backpressure=backpressure
        )

        # Initialize write service
        write_service = MemoryWriteService(
            vector_store=vector_store,
            circuit_breaker=write_breaker,
            backpressure=backpressure
        )

        logger.info("Memory services initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise


async def shutdown_services():
    """Cleanup all services"""
    global read_service, write_service

    try:
        logger.info("Shutting down memory services...")

        if read_service and read_service.vector_store:
            await read_service.vector_store.close()

        if write_service and write_service.vector_store:
            await write_service.vector_store.close()

        logger.info("Memory services shut down successfully")

    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# FastAPI application
app = FastAPI(
    title="LUKHAS Memory Service",
    description="High-performance distributed memory service with T4/0.01% excellence",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency for service availability
async def get_services():
    """Dependency to ensure services are available"""
    if not read_service or not write_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Services not initialized"
        )
    return read_service, write_service


# Exception handlers
@app.exception_handler(CircuitBreakerError)
async def circuit_breaker_handler(request: Request, exc: CircuitBreakerError):
    """Handle circuit breaker errors"""
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "error": "service_unavailable",
            "message": str(exc),
            "retry_after": getattr(exc, 'retry_after', None)
        },
        headers={"Retry-After": str(int(getattr(exc, 'retry_after', 60)))}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred",
            "request_id": getattr(request.state, 'request_id', 'unknown')
        }
    )


# Health and monitoring endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check"""
    components = {}

    # Check read service
    if read_service:
        try:
            read_healthy = await read_service.health_check()
            components['read_service'] = {'healthy': read_healthy}
        except Exception as e:
            components['read_service'] = {'healthy': False, 'error': str(e)}
    else:
        components['read_service'] = {'healthy': False, 'error': 'Not initialized'}

    # Check write service
    if write_service:
        try:
            write_healthy = await write_service.health_check()
            components['write_service'] = {'healthy': write_healthy}
        except Exception as e:
            components['write_service'] = {'healthy': False, 'error': str(e)}
    else:
        components['write_service'] = {'healthy': False, 'error': 'Not initialized'}

    # Check circuit breakers
    if circuit_breakers:
        cb_health = await circuit_breakers.health_check_all()
        components['circuit_breakers'] = cb_health
    else:
        components['circuit_breakers'] = {'healthy': False}

    # Check backpressure
    if backpressure:
        bp_health = await backpressure.health_check()
        components['backpressure'] = bp_health
    else:
        components['backpressure'] = {'healthy': False}

    # Determine overall health
    overall_healthy = all(
        comp.get('healthy', False) for comp in components.values()
    )

    return HealthResponse(
        status="healthy" if overall_healthy else "unhealthy",
        timestamp=time.time(),
        version="1.0.0",
        components=components
    )


@app.get("/ready")
async def readiness_check():
    """Kubernetes readiness probe"""
    if not read_service or not write_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Services not ready"
        )

    return {"status": "ready", "timestamp": time.time()}


@app.get("/metrics/prometheus", response_class=PlainTextResponse)
async def prometheus_metrics():
    """Prometheus metrics endpoint"""
    return export_prometheus_metrics()


@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Detailed metrics endpoint"""
    t4_compliance = get_t4_compliance_report()

    circuit_breaker_metrics = {}
    if circuit_breakers:
        circuit_breaker_metrics = await circuit_breakers.get_all_metrics()

    backpressure_metrics = {}
    if backpressure:
        backpressure_metrics = await backpressure.get_metrics()

    return MetricsResponse(
        timestamp=time.time(),
        t4_compliance=t4_compliance,
        circuit_breakers=circuit_breaker_metrics,
        backpressure=backpressure_metrics
    )


# Memory service endpoints
@app.post("/v1/memory/search", response_model=SearchResponse)
async def search_memory(
    request: SearchRequest,
    services = Depends(get_services)  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_services_memory_api_service_py_L345"}
) -> SearchResponse:
    """Search memory with semantic, keyword, or hybrid search"""
    read_svc, _ = services

    async with time_async_operation('search'):
        # Convert request to SearchQuery
        search_query = SearchQuery(
            query_text=request.query,
            search_type=request.search_type,
            top_k=request.top_k,
            metadata_filter=request.metadata_filter,
            include_content=request.include_content,
            include_vectors=request.include_vectors,
            fold_ids=request.fold_ids,
            min_score=request.min_score
        )

        try:
            response = await read_svc.search(search_query)
            return response

        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Search operation failed: {e!s}"
            )


@app.post("/v1/memory/upsert", response_model=WriteResult)
async def upsert_memory(
    request: UpsertRequest,
    services = Depends(get_services)  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_services_memory_api_service_py_L378"}
) -> WriteResult:
    """Upsert memory fold with content and metadata"""
    _, write_svc = services

    async with time_async_operation('upsert'):
        try:
            result = await write_svc.upsert_memory_fold(
                fold_id=request.fold_id,
                content=request.content,
                metadata=request.metadata,
                ttl_seconds=request.ttl_seconds,
                embedding=request.embedding
            )

            return result

        except Exception as e:
            logger.error(f"Upsert failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Upsert operation failed: {e!s}"
            )


@app.post("/v1/memory/batch-upsert")
async def batch_upsert_memory(
    request: BatchUpsertRequest,
    services = Depends(get_services)  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_services_memory_api_service_py_L406"}
):
    """Batch upsert multiple memory folds"""
    _, write_svc = services

    async with time_async_operation('batch_upsert'):
        try:
            # Convert requests to WriteOperations
            operations = []
            for req in request.operations:
                op = WriteOperation(
                    fold_id=req.fold_id,
                    content=req.content,
                    metadata=req.metadata,
                    ttl_seconds=req.ttl_seconds,
                    embedding=req.embedding
                )
                operations.append(op)

            batch_op = BatchWriteOperation(
                operations=operations,
                atomic=request.atomic
            )

            result = await write_svc.batch_upsert(batch_op)
            return result

        except Exception as e:
            logger.error(f"Batch upsert failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Batch upsert operation failed: {e!s}"
            )


@app.delete("/v1/memory/delete")
async def delete_memory(
    request: DeleteRequest,
    services = Depends(get_services)  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_services_memory_api_service_py_L444"}
):
    """Delete memory folds by ID"""
    _, write_svc = services

    async with time_async_operation('delete'):
        try:
            result = await write_svc.delete_memory_folds(
                fold_ids=request.fold_ids,
                soft_delete=request.soft_delete
            )

            return result

        except Exception as e:
            logger.error(f"Delete failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Delete operation failed: {e!s}"
            )


@app.get("/v1/memory/fold/{fold_id}")
async def get_memory_fold(
    fold_id: str,
    include_vector: bool = False,
    services = Depends(get_services)  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_services_memory_api_service_py_L470"}
):
    """Get memory fold by ID"""
    read_svc, _ = services

    async with time_async_operation('get_fold'):
        try:
            fold = await read_svc.get_memory_fold(fold_id, include_vector)

            if not fold:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Memory fold {fold_id} not found"
                )

            return fold

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Get fold failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Get fold operation failed: {e!s}"
            )


@app.get("/v1/memory/stats")
async def get_memory_stats(services = Depends(get_services)):  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_services_memory_api_service_py_L498"}
    """Get memory service statistics"""
    read_svc, write_svc = services

    try:
        read_stats = await read_svc.get_service_stats()
        write_stats = await write_svc.get_service_stats()

        return {
            "timestamp": time.time(),
            "read_service": read_stats,
            "write_service": write_stats
        }

    except Exception as e:
        logger.error(f"Get stats failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Get stats operation failed: {e!s}"
        )


# Administrative endpoints
@app.post("/admin/circuit-breaker/{breaker_name}/reset")
async def reset_circuit_breaker(breaker_name: str):
    """Reset a circuit breaker"""
    if not circuit_breakers:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Circuit breakers not initialized"
        )

    breaker = circuit_breakers.get_breaker(breaker_name)
    if not breaker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Circuit breaker {breaker_name} not found"
        )

    await breaker.reset()
    return {"message": f"Circuit breaker {breaker_name} reset"}


@app.post("/admin/backpressure/mode/{mode}")
async def set_backpressure_mode(mode: str):
    """Set backpressure mode"""
    if not backpressure:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Backpressure not initialized"
        )

    try:
        bp_mode = BackpressureMode(mode.lower())
        await backpressure.set_mode(bp_mode)
        return {"message": f"Backpressure mode set to {mode}"}

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid backpressure mode: {mode}"
        )


# Development server
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    uvicorn.run(
        "api_service:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
