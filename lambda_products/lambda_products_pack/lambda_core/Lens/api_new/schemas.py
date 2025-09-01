#!/usr/bin/env python3
"""
ΛLens API Schemas
Pydantic models for API request/response validation
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class JobRequest(BaseModel):
    """Request model for job creation"""

    source_type: Optional[str] = Field(
        default="auto", description="Type of source file", enum=["text", "code", "data", "image", "auto"]
    )

    policies: Optional[dict[str, bool]] = Field(
        default_factory=lambda: {"LLM_off": True, "redact_on": False, "offline_only": True},
        description="Security and processing policies",
    )

    parser_opts: Optional[dict[str, Any]] = Field(default_factory=dict, description="Parser-specific options")

    target_forms: Optional[list[str]] = Field(
        default_factory=lambda: ["web2d"], description="Desired output formats", items={"enum": ["web2d", "xr"]}
    )

    symbol_style: Optional[str] = Field(
        default="modern", description="Visual style for symbols", enum=["modern", "classic"]
    )

    max_symbols: Optional[int] = Field(
        default=1000, description="Maximum number of symbols to generate", ge=1, le=10000
    )


class JobResponse(BaseModel):
    """Response model for job creation"""

    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Job status")
    message: str = Field(..., description="Status message")


class PhotonNode(BaseModel):
    """Photon document node model"""

    id: str = Field(..., description="Unique node identifier")
    kind: str = Field(..., description="Node type/kind")
    label: str = Field(..., description="Human-readable label")
    properties: Optional[dict[str, Any]] = Field(default_factory=dict, description="Node properties")
    data_binding: Optional[dict[str, Any]] = Field(default_factory=dict, description="Data binding configuration")
    access_tag: Optional[str] = Field(default=None, description="ΛID access tag")


class PhotonEdge(BaseModel):
    """Photon document edge model"""

    id: str = Field(..., description="Unique edge identifier")
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    kind: str = Field(..., description="Edge type/kind")
    label: Optional[str] = Field(default=None, description="Edge label")


class PhotonLayout(BaseModel):
    """Photon document layout model"""

    positions_2d: Optional[dict[str, dict[str, float]]] = Field(
        default_factory=dict, description="2D positions for nodes"
    )
    positions_3d: Optional[dict[str, dict[str, float]]] = Field(
        default_factory=dict, description="3D positions for nodes"
    )


class PhotonDocument(BaseModel):
    """Complete Photon document model"""

    photon_version: str = Field(default="1.0.0", description="Photon document version")

    title: str = Field(..., description="Document title", max_length=100)

    description: str = Field(..., description="Document description", max_length=500)

    theme: Optional[str] = Field(default="system", description="UI theme", enum=["dark", "light", "system"])

    nodes: list[PhotonNode] = Field(default_factory=list, description="Document nodes")

    edges: list[PhotonEdge] = Field(default_factory=list, description="Document edges")

    layout: Optional[PhotonLayout] = Field(default_factory=PhotonLayout, description="Layout configuration")

    provenance: Optional[dict[str, Any]] = Field(default_factory=dict, description="Data provenance information")


class WidgetPreset(BaseModel):
    """Widget preset model"""

    id: str = Field(..., description="Unique preset identifier")
    label: str = Field(..., description="Human-readable name")
    description: Optional[str] = Field(default=None, description="Preset description")
    icon: Optional[str] = Field(default=None, description="Icon identifier")
    properties_schema: dict[str, Any] = Field(..., description="JSON Schema for widget properties")


class WidgetPresetsResponse(BaseModel):
    """Response model for widget presets"""

    presets: list[WidgetPreset] = Field(..., description="Available widget presets")


class ExportRequest(BaseModel):
    """Request model for dashboard export"""

    format: str = Field(..., description="Export format", enum=["gltf", "json", "photon"])

    options: Optional[dict[str, Any]] = Field(default_factory=dict, description="Export-specific options")


class HealthResponse(BaseModel):
    """Health check response model"""

    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: Optional[str] = Field(default=None, description="Service version")
    uptime: Optional[float] = Field(default=None, description="Service uptime in seconds")
