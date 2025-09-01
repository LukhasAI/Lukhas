#!/usr/bin/env python3
"""
Web 2D Renderer for ΛLens
Generates JSON model for the React UI
"""

import json
from typing import Any, Dict

from ..symbols.glyph_types import GlyphSymbol


class Web2DRenderer:
    """Renders dashboards for 2D web display"""

    def __init__(self):
        self.canvas_width = 1200
        self.canvas_height = 800

    async def render(self, dashboard: Any) -> Dict[str, Any]:
        """Render dashboard as 2D web format"""
        # Convert dashboard to web-compatible format
        web_dashboard = {
            "version": "1.0.0",
            "title": dashboard.metadata.get("title", "ΛLens Dashboard"),
            "description": dashboard.metadata.get("description", ""),
            "canvas": {
                "width": self.canvas_width,
                "height": self.canvas_height
            },
            "widgets": [],
            "layout": {
                "type": "grid",
                "columns": 3,
                "rows": 2
            }
        }

        # Convert symbols to widgets
        for i, symbol in enumerate(dashboard.symbols):
            widget = self._symbol_to_widget(symbol, i)
            web_dashboard["widgets"].append(widget)

        # Add relationships as connections
        web_dashboard["connections"] = dashboard.relationships

        return web_dashboard

    def _symbol_to_widget(self, symbol: GlyphSymbol, index: int) -> Dict[str, Any]:
        """Convert a GLYPH symbol to a web widget"""
        # Calculate position in grid layout
        col = index % 3
        row = index // 3

        x = col * (self.canvas_width // 3) + 50
        y = row * (self.canvas_height // 2) + 50

        widget = {
            "id": f"widget_{symbol.id}",
            "type": self._map_symbol_to_widget_type(symbol),
            "position": {
                "x": x,
                "y": y,
                "width": 300,
                "height": 200
            },
            "properties": {
                "title": symbol.type.value,
                "content": symbol.content,
                "symbolId": symbol.id,
                "confidence": symbol.confidence
            },
            "style": {
                "backgroundColor": self._get_background_color(symbol.type),
                "borderColor": self._get_border_color(symbol.confidence),
                "borderWidth": 2
            }
        }

        return widget

    def _map_symbol_to_widget_type(self, symbol: GlyphSymbol) -> str:
        """Map symbol type to widget type"""
        type_mapping = {
            "📄": "TextCard",
            "💻": "CodeCard",
            "📊": "DataCard",
            "💡": "ConceptCard",
            "👤": "EntityCard",
            "🔗": "RelationshipCard",
            "⚠️": "WarningCard",
            "✅": "SuccessCard",
            "🔄": "ProcessCard",
            "🔮": "GlyphCard"
        }

        return type_mapping.get(symbol.type.value, "GenericCard")

    def _get_background_color(self, symbol_type: Any) -> str:
        """Get background color based on symbol type"""
        color_mapping = {
            "📄": "#e3f2fd",  # Light blue
            "💻": "#f3e5f5",  # Light purple
            "📊": "#e8f5e8",  # Light green
            "💡": "#fff3e0",  # Light orange
            "👤": "#fce4ec",  # Light pink
            "🔗": "#f3e5f5",  # Light purple
            "⚠️": "#fff3e0",  # Light orange
            "✅": "#e8f5e8",  # Light green
            "🔄": "#e3f2fd",  # Light blue
            "🔮": "#f3e5f5"   # Light purple
        }

        return color_mapping.get(symbol_type.value, "#ffffff")

    def _get_border_color(self, confidence: float) -> str:
        """Get border color based on confidence"""
        if confidence >= 0.8:
            return "#4caf50"  # Green
        elif confidence >= 0.6:
            return "#ff9800"  # Orange
        else:
            return "#f44336"  # Red

    async def export_json(self, dashboard: Any, output_path: str) -> str:
        """Export dashboard as JSON file"""
        web_dashboard = await self.render(dashboard)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(web_dashboard, f, indent=2, ensure_ascii=False)

        return output_path
