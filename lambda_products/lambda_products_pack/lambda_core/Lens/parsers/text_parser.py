#!/usr/bin/env python3
"""
Text Parser for ΛLens
Handles plain text files and extracts content
"""

import re
from typing import Any, Dict

from .base_parser import BaseParser


class TextParser(BaseParser):
    """Parser for plain text files"""

    async def parse(self, file_path: str) -> Dict[str, Any]:
        """Parse text file and extract content"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Get basic file info
            file_info = self._get_file_info(file_path)

            # Extract text statistics
            lines = content.split("\n")
            words = re.findall(r"\b\w+\b", content)
            sentences = re.split(r"[.!?]+", content)

            return {
                "text": content,
                "format": "text",
                "statistics": {
                    "lines": len(lines),
                    "words": len(words),
                    "sentences": len(sentences),
                    "characters": len(content)
                },
                "file_info": file_info
            }

        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, encoding="latin-1") as f:
                content = f.read()

            return {
                "text": content,
                "format": "text",
                "encoding": "latin-1",
                "file_info": self._get_file_info(file_path)
            }
        except Exception as e:
            raise ValueError(f"Failed to parse text file {file_path}: {e!s}")
