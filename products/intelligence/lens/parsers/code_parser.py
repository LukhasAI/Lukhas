#!/usr/bin/env python3
"""
Code Parser for ΛLens
Handles source code files and extracts functions, classes, and structure
"""
import re
from typing import Any

from .base_parser import BaseParser


class CodeParser(BaseParser):
    """Parser for source code files"""

    # Language patterns for different programming languages
    LANGUAGE_PATTERNS = {
        "python": {
            "function": r"^\s*def\s+(\w+)\s*\(",
            "class": r"^\s*class\s+(\w+)",
            "import": r"^\s*(?:from\s+\w+\s+)?import\s+(.+)",
            "comment": r"^\s*#.*",
        },
        "javascript": {
            "function": r"^\s*(?:function\s+(\w+)|const\s+(\w+)\s*=.*=>|(\w+)\s*\([^)]*\)\s*{)",
            "class": r"^\s*class\s+(\w+)",
            "import": r"^\s*import\s+(.+?)\s+from",
            "comment": r"^\s*//.*|/\*.*?\*/",
        },
        "java": {
            "function": r"^\s*(?:public|private|protected)?\s*\w+\s+(\w+)\s*\(",
            "class": r"^\s*(?:public|private|protected)?\s*class\s+(\w+)",
            "import": r"^\s*import\s+(.+);",
            "comment": r"^\s*//.*|/\*.*?\*/",
        },
    }

    async def parse(self, file_path: str) -> dict[str, Any]:
        """Parse code file and extract structure"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Get basic file info
            file_info = self._get_file_info(file_path)

            # Detect language from extension
            extension = file_info["extension"]
            language = self._detect_language(extension)

            # Extract code elements
            elements = self._extract_elements(content, language)

            return {
                "code": content,
                "format": "code",
                "language": language,
                "elements": elements,
                "file_info": file_info,
            }

        except Exception as e:
            raise ValueError(f"Failed to parse code file {file_path}: {e!s}")

    def _detect_language(self, extension: str) -> str:
        """Detect programming language from file extension"""
        language_map = {
            "py": "python",
            "js": "javascript",
            "ts": "javascript",
            "java": "java",
            "cpp": "cpp",
            "c": "c",
            "cs": "csharp",
            "php": "php",
            "rb": "ruby",
            "go": "go",
            "rs": "rust",
        }
        return language_map.get(extension, "unknown")

    def _extract_elements(self, content: str, language: str) -> dict[str, list[dict[str, Any]]]:
        """Extract functions, classes, and other elements from code"""
        lines = content.split("\n")
        patterns = self.LANGUAGE_PATTERNS.get(language, {})

        elements = {"functions": [], "classes": [], "imports": [], "comments": []}

        for i, line in enumerate(lines):
            # Extract functions
            if "function" in patterns:
                func_match = re.search(patterns["function"], line)
                if func_match:
                    func_name = func_match.group(1) or func_match.group(2) or func_match.group(3)
                    if func_name:
                        elements["functions"].append({"name": func_name, "line": i + 1, "signature": line.strip()})

            # Extract classes
            if "class" in patterns:
                class_match = re.search(patterns["class"], line)
                if class_match:
                    elements["classes"].append({"name": class_match.group(1), "line": i + 1, "signature": line.strip()})

            # Extract imports
            if "import" in patterns:
                import_match = re.search(patterns["import"], line)
                if import_match:
                    elements["imports"].append({"statement": import_match.group(1), "line": i + 1})

            # Extract comments
            if "comment" in patterns and re.search(patterns["comment"], line):
                elements["comments"].append({"content": line.strip(), "line": i + 1})

        return elements