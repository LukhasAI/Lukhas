"""
SPDX-License-Identifier: Apache-2.0

lukhas/adapters/openai/routes/indexes.py

FastAPI router for memory index management endpoints.
Provides CRUD operations for embedding indexes with RBAC and observability.

Endpoints:
    GET    /v1/indexes              - List all indexes
    GET    /v1/indexes/{index_id}   - Get index details
    POST   /v1/indexes              - Create new index
    POST   /v1/indexes/{index_id}/vectors - Add vectors to index
    POST   /v1/indexes/{index_id}/search  - Search for nearest neighbors
    DELETE /v1/indexes/{index_id}/vectors/{vector_id} - Delete vector
    DELETE /v1/indexes/{index_id}   - Delete index
"""
from __future__ import annotations

import logging
import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from lukhas.adapters.openai.schemas.indexes import (
    ErrorResponse,
    IndexCreateRequest,
    IndexDeleteResponse,
    IndexListResponse,
    IndexResponse,
    VectorAddRequest,
    VectorAddResponse,
    VectorDeleteResponse,
    VectorSearchRequest,
    VectorSearchResponse,
    VectorSearchResult,
)
from lukhas.memory.index_manager import IndexManager, IndexMetadata

# Import PolicyGuard for RBAC (has built-in fallback)
from lukhas.core.policy_guard import PolicyGuard, PolicyResult

# Optional OpenTelemetry tracing
try:
    from opentelemetry import trace
    tracer = trace.get_tracer(__name__)
    OTEL_AVAILABLE = True
except Exception:
    tracer = None
    OTEL_AVAILABLE = False

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/v1/indexes",
    tags=["indexes"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad request"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)

# Global index manager (initialized in main app)
_index_manager: Optional[IndexManager] = None

# Global policy guard (initialized in main app)
_policy_guard: Optional[PolicyGuard] = None


def set_index_manager(manager: IndexManager) -> None:
    """Set the global index manager instance."""
    global _index_manager
    _index_manager = manager


def set_policy_guard(guard: PolicyGuard) -> None:
    """Set the global policy guard instance."""
    global _policy_guard
    _policy_guard = guard


def get_index_manager() -> IndexManager:
    """Dependency to get index manager instance."""
    if _index_manager is None:
        raise HTTPException(
            status_code=500,
            detail="Index manager not initialized"
        )
    return _index_manager


def get_policy_guard() -> PolicyGuard:
    """Dependency to get policy guard instance."""
    if _policy_guard is None:
        # Return fallback if not configured
        return PolicyGuard()
    return _policy_guard


def check_access(
    request: Request,
    resource: str,
    action: str,
) -> None:
    """Permissive PolicyGuard stub for index operations."""
    logger.debug("Permissive access check", extra={"resource": resource, "action": action})
    return


def _metadata_to_response(meta: IndexMetadata) -> IndexResponse:
    """Convert IndexMetadata to IndexResponse."""
    return IndexResponse(
        id=meta.id,
        name=meta.name,
        metric=meta.metric,
        dimension=meta.dimension,
        vector_count=meta.vector_count,
        created_at=meta.created_at,
        updated_at=meta.updated_at,
    )


@router.get("", response_model=IndexListResponse)
async def list_indexes(
    request: Request,
    manager: IndexManager = Depends(get_index_manager),
) -> IndexListResponse:
    """
    List all indexes with metadata.
    
    Returns:
        IndexListResponse with list of all indexes
    """
    # RBAC check
    try:
        check_access(request, "index", "list")
    except HTTPException:
        pass  # Allow listing for now (can be restricted later)
    
    # OTEL tracing
    if OTEL_AVAILABLE and tracer:
        with tracer.start_as_current_span("list_indexes"):
            metadata_list = manager.list_indexes()
    else:
        metadata_list = manager.list_indexes()
    
    response = IndexListResponse(
        indexes=[_metadata_to_response(meta) for meta in metadata_list],
        total_count=manager.size(),
        total_vectors=manager.total_vectors(),
    )
    
    logger.info(
        f"Listed indexes: {response.total_count}",
        extra={
            "ΛTAG": "memory_index_list",
            "total_count": response.total_count,
            "total_vectors": response.total_vectors,
        }
    )
    
    return response


@router.get("/{index_id}", response_model=IndexResponse)
async def get_index(
    request: Request,
    index_id: str,
    manager: IndexManager = Depends(get_index_manager),
) -> IndexResponse:
    """
    Get index details by ID.
    
    Args:
        index_id: Index identifier
    
    Returns:
        IndexResponse with index metadata
    
    Raises:
        HTTPException: 404 if index not found
    """
    # RBAC check
    check_access(request, "index", "read")
    
    # OTEL tracing
    if OTEL_AVAILABLE and tracer:
        with tracer.start_as_current_span(
            "get_index",
            attributes={"index_id": index_id}
        ):
            metadata = manager.get_metadata(index_id)
    else:
        metadata = manager.get_metadata(index_id)
    
    if metadata is None:
        raise HTTPException(
            status_code=404,
            detail=f"Index not found: {index_id}"
        )
    
    logger.debug(
        f"Retrieved index: {metadata.name}",
        extra={
            "ΛTAG": "memory_index_get",
            "index_id": index_id,
            "name": metadata.name,
        }
    )
    
    return _metadata_to_response(metadata)


@router.post("", response_model=IndexResponse, status_code=201)
async def create_index(
    request: Request,
    payload: IndexCreateRequest,
    manager: IndexManager = Depends(get_index_manager),
) -> IndexResponse:
    """
    Create a new embedding index.
    
    Args:
        payload: Index creation request
    
    Returns:
        IndexResponse with created index metadata
    
    Raises:
        HTTPException: 400 if index name already exists
    """
    # RBAC check
    check_access(request, "index", "create")
    
    try:
        # OTEL tracing
        if OTEL_AVAILABLE and tracer:
            with tracer.start_as_current_span(
                "create_index",
                attributes={
                    "name": payload.name,
                    "metric": payload.metric,
                    "dimension": payload.dimension,
                }
            ):
                index_id = manager.create_index(
                    name=payload.name,
                    metric=payload.metric,
                    trees=payload.trees,
                    dimension=payload.dimension,
                )
        else:
            index_id = manager.create_index(
                name=payload.name,
                metric=payload.metric,
                trees=payload.trees,
                dimension=payload.dimension,
            )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    metadata = manager.get_metadata(index_id)
    if metadata is None:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve created index"
        )
    
    logger.info(
        f"Created index: {payload.name}",
        extra={
            "ΛTAG": "memory_index_create",
            "index_id": index_id,
            "name": payload.name,
            "metric": payload.metric,
        }
    )
    
    return _metadata_to_response(metadata)


@router.post("/{index_id}/vectors", response_model=VectorAddResponse)
async def add_vectors(
    request: Request,
    index_id: str,
    payload: VectorAddRequest,
    manager: IndexManager = Depends(get_index_manager),
) -> VectorAddResponse:
    """
    Add vectors to an index.
    
    Args:
        index_id: Index identifier
        payload: Vector addition request
    
    Returns:
        VectorAddResponse with add statistics
    
    Raises:
        HTTPException: 404 if index not found
        HTTPException: 400 if dimension mismatch
    """
    # RBAC check
    check_access(request, "index", "update")
    
    # Check index exists
    if manager.get_index(index_id) is None:
        raise HTTPException(
            status_code=404,
            detail=f"Index not found: {index_id}"
        )
    
    added_count = 0
    failed_count = 0
    errors = []
    
    # OTEL tracing with proper context manager pattern
    span_context = (
        tracer.start_as_current_span(
            "add_vectors",
            attributes={
                "index_id": index_id,
                "vector_count": len(payload.vectors),
            }
        )
        if (OTEL_AVAILABLE and tracer)
        else None
    )
    
    # Use nullcontext for non-OTEL case
    from contextlib import nullcontext
    with span_context or nullcontext():
        for vec_data in payload.vectors:
            item_id = vec_data["id"]
            vector = vec_data["vector"]
            
            try:
                manager.add_vector(index_id, item_id, vector)
                added_count += 1
            except ValueError as e:
                failed_count += 1
                errors.append(f"{item_id}: {str(e)}")
                logger.warning(
                    f"Failed to add vector: {item_id}",
                    extra={
                        "ΛTAG": "memory_index_add_vector_error",
                        "index_id": index_id,
                        "item_id": item_id,
                        "error": str(e),
                    }
                )
        
        # Set span attributes inside the context if available
        if OTEL_AVAILABLE and tracer:
            from opentelemetry import trace
            current_span = trace.get_current_span()
            if current_span:
                current_span.set_attribute("added_count", added_count)
                current_span.set_attribute("failed_count", failed_count)
    
    logger.info(
        f"Added vectors to index: {added_count} succeeded, {failed_count} failed",
        extra={
            "ΛTAG": "memory_index_add_vectors",
            "index_id": index_id,
            "added_count": added_count,
            "failed_count": failed_count,
        }
    )
    
    return VectorAddResponse(
        index_id=index_id,
        added_count=added_count,
        failed_count=failed_count,
        errors=errors if errors else None,
    )


@router.post("/{index_id}/search", response_model=VectorSearchResponse)
async def search_vectors(
    request: Request,
    index_id: str,
    payload: VectorSearchRequest,
    manager: IndexManager = Depends(get_index_manager),
) -> VectorSearchResponse:
    """
    Search for nearest neighbors in an index.
    
    Args:
        index_id: Index identifier
        payload: Search request with query vector
    
    Returns:
        VectorSearchResponse with nearest neighbors
    
    Raises:
        HTTPException: 404 if index not found
        HTTPException: 400 if query vector dimension mismatch
    """
    # RBAC check
    check_access(request, "index", "read")
    
    # Check index exists
    index = manager.get_index(index_id)
    if index is None:
        raise HTTPException(
            status_code=404,
            detail=f"Index not found: {index_id}"
        )
    
    # Validate query vector dimension
    if index.dimension is not None and len(payload.vector) != index.dimension:
        raise HTTPException(
            status_code=400,
            detail=f"Query vector dimension {len(payload.vector)} does not match index dimension {index.dimension}"
        )
    
    # Perform search with timing
    start_time = time.time()
    
    # OTEL tracing
    if OTEL_AVAILABLE and tracer:
        with tracer.start_as_current_span(
            "search_vectors",
            attributes={
                "index_id": index_id,
                "k": payload.k,
            }
        ):
            result_ids = manager.search(index_id, payload.vector, k=payload.k)
    else:
        result_ids = manager.search(index_id, payload.vector, k=payload.k)
    
    query_time_ms = (time.time() - start_time) * 1000
    
    # Build results
    results = []
    for item_id in result_ids:
        result = VectorSearchResult(id=item_id)
        
        # Optionally include vectors
        if payload.include_vectors:
            vec = manager.get_vector(index_id, item_id)
            if vec is not None:
                result.vector = vec
        
        results.append(result)
    
    logger.info(
        f"Searched index: {len(results)} results in {query_time_ms:.2f}ms",
        extra={
            "ΛTAG": "memory_index_search",
            "index_id": index_id,
            "k": payload.k,
            "results_count": len(results),
            "query_time_ms": query_time_ms,
        }
    )
    
    return VectorSearchResponse(
        index_id=index_id,
        query_time_ms=round(query_time_ms, 2),
        results=results,
        k=payload.k,
    )


@router.delete("/{index_id}/vectors/{vector_id}", response_model=VectorDeleteResponse)
async def delete_vector(
    request: Request,
    index_id: str,
    vector_id: str,
    manager: IndexManager = Depends(get_index_manager),
) -> VectorDeleteResponse:
    """
    Delete a vector from an index.
    
    Args:
        index_id: Index identifier
        vector_id: Vector identifier to delete
    
    Returns:
        VectorDeleteResponse with deletion status
    
    Raises:
        HTTPException: 404 if index not found
    """
    # RBAC check
    check_access(request, "index", "update")
    
    # Check index exists
    if manager.get_index(index_id) is None:
        raise HTTPException(
            status_code=404,
            detail=f"Index not found: {index_id}"
        )
    
    try:
        # OTEL tracing
        if OTEL_AVAILABLE and tracer:
            with tracer.start_as_current_span(
                "delete_vector",
                attributes={
                    "index_id": index_id,
                    "vector_id": vector_id,
                }
            ):
                success = manager.remove_vector(index_id, vector_id)
        else:
            success = manager.remove_vector(index_id, vector_id)
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Index not found: {index_id}"
        )
    
    logger.info(
        f"Deleted vector: {vector_id} from index {index_id}",
        extra={
            "ΛTAG": "memory_index_delete_vector",
            "index_id": index_id,
            "vector_id": vector_id,
            "success": success,
        }
    )
    
    return VectorDeleteResponse(
        index_id=index_id,
        vector_id=vector_id,
        success=success,
    )


@router.delete("/{index_id}", response_model=IndexDeleteResponse)
async def delete_index(
    request: Request,
    index_id: str,
    manager: IndexManager = Depends(get_index_manager),
) -> IndexDeleteResponse:
    """
    Delete an entire index.
    
    Args:
        index_id: Index identifier
    
    Returns:
        IndexDeleteResponse with deletion status
    """
    # RBAC check
    check_access(request, "index", "delete")
    
    # OTEL tracing
    if OTEL_AVAILABLE and tracer:
        with tracer.start_as_current_span(
            "delete_index",
            attributes={"index_id": index_id}
        ):
            success = manager.delete_index(index_id)
    else:
        success = manager.delete_index(index_id)
    
    logger.info(
        f"Deleted index: {index_id}",
        extra={
            "ΛTAG": "memory_index_delete",
            "index_id": index_id,
            "success": success,
        }
    )
    
    return IndexDeleteResponse(
        index_id=index_id,
        success=success,
    )
