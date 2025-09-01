#!/usr/bin/env python3
"""
XR Renderer for ΛLens
Generates glTF/WebXR scene descriptions
"""

import json
from typing import Any, Dict

from ..symbols.glyph_types import GlyphSymbol


class XRRenderer:
    """Renders dashboards for AR/VR viewing"""

    def __init__(self):
        self.scene_scale = 1.0

    async def render(self, dashboard: Any) -> Dict[str, Any]:
        """Render dashboard as XR scene"""
        # Create glTF structure
        gltf = {
            "asset": {"version": "2.0", "generator": "ΛLens XR Renderer 1.0"},
            "scene": 0,
            "scenes": [{"name": "ΛLens Dashboard", "nodes": []}],
            "nodes": [],
            "meshes": [],
            "materials": [],
            "buffers": [],
            "bufferViews": [],
            "accessors": [],
        }

        # Add nodes for each symbol
        for i, symbol in enumerate(dashboard.symbols):
            node = self._create_symbol_node(symbol, i)
            gltf["nodes"].append(node)
            gltf["scenes"][0]["nodes"].append(i)

            # Create mesh for the symbol
            mesh = self._create_symbol_mesh(symbol, i)
            gltf["meshes"].append(mesh)

            # Create material
            material = self._create_symbol_material(symbol)
            gltf["materials"].append(material)

        return gltf

    def _create_symbol_node(self, symbol: GlyphSymbol, index: int) -> Dict[str, Any]:
        """Create a glTF node for a symbol"""
        node = {
            "name": f"symbol_{symbol.id}",
            "mesh": index,
            "translation": list(symbol.position) if symbol.position else [0, 0, 0],
            "scale": [self.scene_scale] * 3,
            "extras": {
                "symbol_type": symbol.type.value,
                "content": symbol.content,
                "confidence": symbol.confidence,
                "lambda": True,
            },
        }

        return node

    def _create_symbol_mesh(self, symbol: GlyphSymbol, index: int) -> Dict[str, Any]:
        """Create a mesh for a symbol"""
        # Create a simple cube mesh for each symbol
        # In a real implementation, you'd create more sophisticated geometry

        # Cube vertices (8 vertices)
        vertices = [
            -0.5,
            -0.5,
            0.5,  # 0
            0.5,
            -0.5,
            0.5,  # 1
            0.5,
            0.5,
            0.5,  # 2
            -0.5,
            0.5,
            0.5,  # 3
            -0.5,
            -0.5,
            -0.5,  # 4
            0.5,
            -0.5,
            -0.5,  # 5
            0.5,
            0.5,
            -0.5,  # 6
            -0.5,
            0.5,
            -0.5,  # 7
        ]

        # Cube indices (36 indices for 12 triangles)
        indices = [
            0,
            1,
            2,
            2,
            3,
            0,  # Front
            1,
            5,
            6,
            6,
            2,
            1,  # Right
            5,
            4,
            7,
            7,
            6,
            5,  # Back
            4,
            0,
            3,
            3,
            7,
            4,  # Left
            3,
            2,
            6,
            6,
            7,
            3,  # Top
            4,
            5,
            1,
            1,
            0,
            4,  # Bottom
        ]

        mesh = {
            "name": f"mesh_{symbol.id}",
            "primitives": [
                {
                    "attributes": {
                        "POSITION": len(indices) * 2,  # Position accessor index
                        "NORMAL": len(indices) * 2 + 1,  # Normal accessor index
                    },
                    "indices": len(indices) * 2 + 2,  # Index accessor index
                    "material": index,
                }
            ],
        }

        return mesh

    def _create_symbol_material(self, symbol: GlyphSymbol) -> Dict[str, Any]:
        """Create material for a symbol"""
        # Base colors for different symbol types
        base_colors = {
            "📄": [0.6, 0.8, 1.0, 1.0],  # Light blue
            "💻": [0.8, 0.6, 1.0, 1.0],  # Light purple
            "📊": [0.6, 1.0, 0.6, 1.0],  # Light green
            "💡": [1.0, 0.8, 0.6, 1.0],  # Light orange
            "👤": [1.0, 0.6, 0.8, 1.0],  # Light pink
            "🔗": [0.8, 0.6, 1.0, 1.0],  # Light purple
            "⚠️": [1.0, 0.8, 0.6, 1.0],  # Light orange
            "✅": [0.6, 1.0, 0.6, 1.0],  # Light green
            "🔄": [0.6, 0.8, 1.0, 1.0],  # Light blue
            "🔮": [0.8, 0.6, 1.0, 1.0],  # Light purple
        }

        color = base_colors.get(symbol.type.value, [1.0, 1.0, 1.0, 1.0])

        # Adjust color based on confidence
        if symbol.confidence < 0.8:
            # Make less confident symbols more transparent
            color[3] = symbol.confidence

        material = {
            "name": f"material_{symbol.id}",
            "pbrMetallicRoughness": {"baseColorFactor": color, "metallicFactor": 0.0, "roughnessFactor": 0.5},
            "emissiveFactor": [0.0, 0.0, 0.0],
        }

        return material

    async def export_gltf(self, dashboard: Any) -> bytes:
        """Export dashboard as glTF binary"""
        gltf_dict = await self.render(dashboard)

        # Convert to JSON bytes
        gltf_json = json.dumps(gltf_dict, indent=2).encode("utf-8")

        # In a real implementation, you'd create proper glTF binary format
        # For now, return JSON
        return gltf_json

    async def export_webxr(self, dashboard: Any, output_path: str) -> str:
        """Export dashboard for WebXR viewing"""
        gltf_data = await self.export_gltf(dashboard)

        with open(output_path, "wb") as f:
            f.write(gltf_data)

        return output_path
