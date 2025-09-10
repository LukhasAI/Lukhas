#!/usr/bin/env python3
"""
Data Parser for ΛLens
Handles structured data files like JSON, YAML, and XML
"""
import json
import xml.etree.ElementTree as ET
from typing import Any

from .base_parser import BaseParser


class DataParser(BaseParser):
    """Parser for structured data files"""

    async def parse(self, file_path: str) -> dict[str, Any]:
        """Parse data file and extract structure"""
        try:
            file_info = self._get_file_info(file_path)
            extension = file_info["extension"]

            if extension in ["json"]:
                return await self._parse_json(file_path, file_info)
            elif extension in ["yaml", "yml"]:
                return await self._parse_yaml(file_path, file_info)
            elif extension in ["xml"]:
                return await self._parse_xml(file_path, file_info)
            else:
                # Try JSON as fallback
                return await self._parse_json(file_path, file_info)

        except Exception as e:
            raise ValueError(f"Failed to parse data file {file_path}: {e!s}")

    async def _parse_json(self, file_path: str, file_info: dict[str, Any]) -> dict[str, Any]:
        """Parse JSON file"""
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        # Analyze structure
        structure = self._analyze_structure(data)

        return {"data": data, "format": "json", "structure": structure, "file_info": file_info}

    async def _parse_yaml(self, file_path: str, file_info: dict[str, Any]) -> dict[str, Any]:
        """Parse YAML file"""
        try:
            import yaml
        except ImportError:
            raise ValueError("PyYAML not installed. Install with: pip install PyYAML")

        with open(file_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        structure = self._analyze_structure(data)

        return {"data": data, "format": "yaml", "structure": structure, "file_info": file_info}

    async def _parse_xml(self, file_path: str, file_info: dict[str, Any]) -> dict[str, Any]:
        """Parse XML file"""
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Convert to dict structure
        data = self._xml_to_dict(root)

        return {"data": data, "format": "xml", "root_tag": root.tag, "file_info": file_info}

    def _analyze_structure(self, data: Any) -> dict[str, Any]:
        """Analyze the structure of parsed data"""
        if isinstance(data, dict):
            return {
                "type": "object",
                "keys": list(data.keys()),
                "size": len(data),
                "nested_types": {k: self._get_type_name(v) for k, v in data.items()},
            }
        elif isinstance(data, list):
            return {
                "type": "array",
                "length": len(data),
                "element_types": list(set(self._get_type_name(item) for item in data[:10])),  # Sample first 10
            }
        else:
            return {"type": self._get_type_name(data)}

    def _get_type_name(self, obj: Any) -> str:
        """Get a readable type name for an object"""
        if isinstance(obj, dict):
            return "object"
        elif isinstance(obj, list):
            return "array"
        elif isinstance(obj, str):
            return "string"
        elif isinstance(obj, int):
            return "integer"
        elif isinstance(obj, float):
            return "number"
        elif isinstance(obj, bool):
            return "boolean"
        elif obj is None:
            return "null"
        else:
            return type(obj).__name__

    def _xml_to_dict(self, element: ET.Element) -> dict[str, Any]:
        """Convert XML element to dictionary"""
        result = {}

        # Add attributes
        if element.attrib:
            result["@attributes"] = element.attrib

        # Add text content
        if element.text and element.text.strip():
            result["#text"] = element.text.strip()

        # Add child elements
        for child in element:
            child_dict = self._xml_to_dict(child)
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_dict)
            else:
                result[child.tag] = child_dict

        return {element.tag: result} if result else {element.tag: None}