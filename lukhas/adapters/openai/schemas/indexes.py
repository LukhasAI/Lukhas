"""
SPDX-License-Identifier: Apache-2.0

lukhas/adapters/openai/schemas/indexes.py

Pydantic models for memory index management API endpoints.
Provides request/response schemas with validation for CRUD operations.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class IndexCreateRequest(BaseModel):
    """Request to create a new index."""
    name: str = Field(..., description="Unique name for the index", min_length=1, max_length=128)
    metric: str = Field(
        default="angular",
        description="Distance metric: 'angular' (cosine similarity) or 'euclidean'",
    )
    trees: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of trees for Annoy index (more trees = better accuracy, slower build)",
    )
    dimension: Optional[int] = Field(
        default=None,
        ge=1,
        le=16384,
        description="Vector dimension (auto-detected on first add if not specified)",
    )
    
    @field_validator("metric")
    @classmethod
    def validate_metric(cls, v: str) -> str:
        """Validate metric is 'angular' or 'euclidean'."""
        if v not in ("angular", "euclidean"):
            raise ValueError("Metric must be 'angular' or 'euclidean'")
        return v
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name is alphanumeric with hyphens/underscores."""
        if not all(c.isalnum() or c in ("-", "_") for c in v):
            raise ValueError("Name must be alphanumeric with hyphens or underscores")
        return v


class IndexResponse(BaseModel):
    """Response containing index metadata."""
    id: str = Field(..., description="Unique index identifier")
    name: str = Field(..., description="Index name")
    metric: str = Field(..., description="Distance metric")
    dimension: Optional[int] = Field(None, description="Vector dimension")
    vector_count: int = Field(..., description="Number of vectors in index")
    created_at: float = Field(..., description="Creation timestamp (Unix epoch)")
    updated_at: float = Field(..., description="Last update timestamp (Unix epoch)")


class VectorAddRequest(BaseModel):
    """Request to add vectors to an index."""
    vectors: List[Dict[str, Any]] = Field(
        ...,
        description="List of vectors to add",
        min_length=1,
        max_length=1000,
    )
    
    @field_validator("vectors")
    @classmethod
    def validate_vectors(cls, v: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate each vector has 'id' and 'vector' fields."""
        for i, vec in enumerate(v):
            if "id" not in vec:
                raise ValueError(f"Vector at index {i} missing 'id' field")
            if "vector" not in vec:
                raise ValueError(f"Vector at index {i} missing 'vector' field")
            if not isinstance(vec["vector"], list):
                raise ValueError(f"Vector at index {i} 'vector' field must be a list")
            if not all(isinstance(x, (int, float)) for x in vec["vector"]):
                raise ValueError(f"Vector at index {i} contains non-numeric values")
        return v


class VectorAddResponse(BaseModel):
    """Response after adding vectors."""
    index_id: str = Field(..., description="Index identifier")
    added_count: int = Field(..., description="Number of vectors successfully added")
    failed_count: int = Field(default=0, description="Number of vectors that failed to add")
    errors: Optional[List[str]] = Field(None, description="Error messages for failed vectors")


class VectorSearchRequest(BaseModel):
    """Request to search for nearest neighbors."""
    vector: List[float] = Field(
        ...,
        description="Query vector",
        min_length=1,
        max_length=16384,
    )
    k: int = Field(
        default=10,
        ge=1,
        le=1000,
        description="Number of nearest neighbors to return",
    )
    include_vectors: bool = Field(
        default=False,
        description="Include vector embeddings in response",
    )
    
    @field_validator("vector")
    @classmethod
    def validate_vector(cls, v: List[float]) -> List[float]:
        """Validate vector contains only numeric values."""
        if not all(isinstance(x, (int, float)) for x in v):
            raise ValueError("Vector must contain only numeric values")
        return v


class VectorSearchResult(BaseModel):
    """Single search result."""
    id: str = Field(..., description="Item identifier")
    score: Optional[float] = Field(None, description="Similarity score")
    vector: Optional[List[float]] = Field(None, description="Vector embedding (if requested)")


class VectorSearchResponse(BaseModel):
    """Response containing search results."""
    index_id: str = Field(..., description="Index identifier")
    query_time_ms: float = Field(..., description="Query processing time in milliseconds")
    results: List[VectorSearchResult] = Field(..., description="Search results (nearest neighbors)")
    k: int = Field(..., description="Requested number of neighbors")


class IndexListResponse(BaseModel):
    """Response containing list of indexes."""
    indexes: List[IndexResponse] = Field(..., description="List of all indexes")
    total_count: int = Field(..., description="Total number of indexes")
    total_vectors: int = Field(..., description="Total vectors across all indexes")


class VectorDeleteResponse(BaseModel):
    """Response after deleting a vector."""
    index_id: str = Field(..., description="Index identifier")
    vector_id: str = Field(..., description="Deleted vector identifier")
    success: bool = Field(..., description="Whether deletion was successful")


class IndexDeleteResponse(BaseModel):
    """Response after deleting an index."""
    index_id: str = Field(..., description="Deleted index identifier")
    success: bool = Field(..., description="Whether deletion was successful")
