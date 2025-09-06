#!/usr/bin/env python3
"""
Widget Factory for ΛLens
Maps GLYPH symbols to UI widgets
"""

from typing import Any

from ..symbols.glyph_types import GlyphSymbol, SymbolType


class WidgetFactory:
    """Factory for creating UI widgets from GLYPH symbols"""

    # Widget presets with their properties
    WIDGET_PRESETS = {
        "MetricCard": {
            "label": "Metric Card",
            "description": "Display a single metric with title and value",
            "icon": "📊",
            "properties_schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "title": "Title"},
                    "value": {"type": "string", "title": "Value"},
                    "unit": {"type": "string", "title": "Unit"},
                    "change": {"type": "string", "title": "Change"},
                    "changeType": {
                        "type": "string",
                        "enum": ["positive", "negative", "neutral"],
                        "title": "Change Type",
                    },
                },
                "required": ["title", "value"],
            },
        },
        "BarCompare": {
            "label": "Bar Chart",
            "description": "Compare values using bars",
            "icon": "📊",
            "properties_schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "title": "Chart Title"},
                    "data": {
                        "type": "array",
                        "title": "Data Points",
                        "items": {
                            "type": "object",
                            "properties": {"name": {"type": "string"}, "value": {"type": "number"}},
                        },
                    },
                    "orientation": {"type": "string", "enum": ["horizontal", "vertical"], "default": "vertical"},
                },
                "required": ["title", "data"],
            },
        },
        "ForceGraph": {
            "label": "Force Graph",
            "description": "Display relationships between entities",
            "icon": "🔗",
            "properties_schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "title": "Graph Title"},
                    "nodes": {
                        "type": "array",
                        "title": "Nodes",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "label": {"type": "string"},
                                "group": {"type": "string"},
                            },
                        },
                    },
                    "links": {
                        "type": "array",
                        "title": "Links",
                        "items": {
                            "type": "object",
                            "properties": {
                                "source": {"type": "string"},
                                "target": {"type": "string"},
                                "value": {"type": "number", "default": 1},
                            },
                        },
                    },
                },
                "required": ["nodes", "links"],
            },
        },
        "TextBlock": {
            "label": "Text Block",
            "description": "Display formatted text content",
            "icon": "📄",
            "properties_schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "title": "Title"},
                    "content": {"type": "string", "title": "Content"},
                    "format": {"type": "string", "enum": ["plain", "markdown", "html"], "default": "plain"},
                },
                "required": ["content"],
            },
        },
        "CodeSnippet": {
            "label": "Code Snippet",
            "description": "Display code with syntax highlighting",
            "icon": "💻",
            "properties_schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "title": "Title"},
                    "code": {"type": "string", "title": "Code"},
                    "language": {"type": "string", "title": "Language"},
                    "showLineNumbers": {"type": "boolean", "default": True},
                },
                "required": ["code"],
            },
        },
    }

    def __init__(self):
        self.widget_mappings = self._create_symbol_mappings()

    def _create_symbol_mappings(self) -> dict[str, list[str]]:
        """Create mappings from symbol types to suitable widgets"""
        return {
            SymbolType.DOCUMENT.value: ["TextBlock", "MetricCard"],
            SymbolType.CODE.value: ["CodeSnippet", "TextBlock"],
            SymbolType.DATA.value: ["MetricCard", "BarCompare", "TextBlock"],
            SymbolType.CONCEPT.value: ["TextBlock", "MetricCard"],
            SymbolType.ENTITY.value: ["TextBlock", "MetricCard"],
            SymbolType.RELATIONSHIP.value: ["ForceGraph", "BarCompare"],
            SymbolType.WARNING.value: ["MetricCard", "TextBlock"],
            SymbolType.SUCCESS.value: ["MetricCard", "TextBlock"],
            SymbolType.PROCESS.value: ["MetricCard", "ForceGraph"],
            SymbolType.GLYPH.value: ["TextBlock", "MetricCard"],
        }

    def suggest_widgets(self, symbols: list[GlyphSymbol]) -> list[dict[str, Any]]:
        """Suggest appropriate widgets for a list of symbols"""
        suggestions = []

        for symbol in symbols:
            # Get suitable widget types for this symbol
            suitable_widgets = self.widget_mappings.get(symbol.type.value, ["TextBlock"])

            for widget_type in suitable_widgets:
                widget_config = self._create_widget_config(symbol, widget_type)
                if widget_config:
                    suggestions.append(widget_config)

        # Remove duplicates and limit suggestions
        unique_suggestions = []
        seen = set()
        for suggestion in suggestions[:20]:  # Limit to 20 suggestions
            key = (suggestion["widget_type"], suggestion["symbol_id"])
            if key not in seen:
                unique_suggestions.append(suggestion)
                seen.add(key)

        return unique_suggestions

    def _create_widget_config(self, symbol: GlyphSymbol, widget_type: str) -> dict[str, Any]:
        """Create widget configuration for a symbol"""
        preset = self.WIDGET_PRESETS.get(widget_type)
        if not preset:
            return None

        config = {
            "widget_type": widget_type,
            "symbol_id": symbol.id,
            "label": f"{preset['label']} - {symbol.content[:30]}...",
            "properties": self._generate_properties(symbol, widget_type),
            "position": symbol.position,
            "metadata": {"symbol_type": symbol.type.value, "confidence": symbol.confidence, "created_from": symbol.id},
        }

        return config

    def _generate_properties(self, symbol: GlyphSymbol, widget_type: str) -> dict[str, Any]:
        """Generate widget properties based on symbol content"""
        if widget_type == "MetricCard":
            return self._create_metric_card_properties(symbol)
        elif widget_type == "TextBlock":
            return self._create_text_block_properties(symbol)
        elif widget_type == "CodeSnippet":
            return self._create_code_snippet_properties(symbol)
        elif widget_type == "BarCompare":
            return self._create_bar_chart_properties(symbol)
        elif widget_type == "ForceGraph":
            return self._create_force_graph_properties(symbol)
        else:
            return {}

    def _create_metric_card_properties(self, symbol: GlyphSymbol) -> dict[str, Any]:
        """Create properties for MetricCard widget"""
        content = symbol.content

        # Try to extract numeric value
        import re

        numbers = re.findall(r"\d+\.?\d*", content)

        return {
            "title": symbol.type.value,
            "value": numbers[0] if numbers else content[:20],
            "unit": "",
            "change": "",
            "changeType": "neutral",
        }

    def _create_text_block_properties(self, symbol: GlyphSymbol) -> dict[str, Any]:
        """Create properties for TextBlock widget"""
        return {"title": symbol.type.value, "content": symbol.content, "format": "plain"}

    def _create_code_snippet_properties(self, symbol: GlyphSymbol) -> dict[str, Any]:
        """Create properties for CodeSnippet widget"""
        return {
            "title": "Code",
            "code": symbol.content,
            "language": symbol.metadata.get("language", "text"),
            "showLineNumbers": True,
        }

    def _create_bar_chart_properties(self, symbol: GlyphSymbol) -> dict[str, Any]:
        """Create properties for BarCompare widget"""
        # This is a simplified implementation
        return {
            "title": "Data Comparison",
            "data": [{"name": "Item 1", "value": 10}, {"name": "Item 2", "value": 20}],
            "orientation": "vertical",
        }

    def _create_force_graph_properties(self, symbol: GlyphSymbol) -> dict[str, Any]:
        """Create properties for ForceGraph widget"""
        # This is a simplified implementation
        return {
            "title": "Relationships",
            "nodes": [{"id": "1", "label": "Node 1", "group": "A"}, {"id": "2", "label": "Node 2", "group": "B"}],
            "links": [{"source": "1", "target": "2", "value": 1}],
        }

    def get_widget_presets(self) -> dict[str, dict[str, Any]]:
        """Get all available widget presets"""
        return self.WIDGET_PRESETS.copy()
