#!/usr/bin/env python3
"""
Markdown Parser for ΛLens
Handles Markdown files and extracts structure
"""
import re
from typing import Any

from .base_parser import BaseParser


class MarkdownParser(BaseParser):
    """Parser for Markdown files"""

    async def parse(self, file_path: str) -> dict[str, Any]:
        """Parse Markdown file and extract structure"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            file_info = self._get_file_info(file_path)

            # Extract Markdown elements
            elements = self._extract_markdown_elements(content)

            return {"text": content, "format": "markdown", "elements": elements, "file_info": file_info}

        except Exception as e:
            raise ValueError(f"Failed to parse Markdown file {file_path}: {e!s}")

    def _extract_markdown_elements(self, content: str) -> dict[str, list[dict[str, Any]]]:
        """Extract headers, links, code blocks, etc. from Markdown"""
        lines = content.split("\n")

        elements = {"headers": [], "links": [], "code_blocks": [], "lists": [], "images": []}

        in_code_block = False
        code_block_start = 0

        for i, line in enumerate(lines):
            # Headers
            header_match = re.match(r"^(#{1,6})\s+(.+)$", line)
            if header_match:
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                elements["headers"].append({"level": level, "title": title, "line": i + 1})

            # Links
            link_matches = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", line)
            for text, url in link_matches:
                elements["links"].append({"text": text, "url": url, "line": i + 1})

            # Images
            image_matches = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", line)
            for alt, src in image_matches:
                elements["images"].append({"alt": alt, "src": src, "line": i + 1})

            # Code blocks
            if line.strip().startswith("```"):
                if not in_code_block:
                    in_code_block = True
                    code_block_start = i + 1
                else:
                    in_code_block = False
                    code_block_content = "\n".join(lines[code_block_start:i])
                    elements["code_blocks"].append(
                        {
                            "content": code_block_content,
                            "start_line": code_block_start,
                            "end_line": i + 1,
                            "language": self._extract_code_language(lines[code_block_start - 1]),
                        }
                    )

            # Lists (basic detection)
            if not in_code_block and re.match(r"^[\s]*[-*+]\s+", line):
                elements["lists"].append({"content": line.strip(), "line": i + 1, "type": "unordered"})
            elif not in_code_block and re.match(r"^[\s]*\d+\.\s+", line):
                elements["lists"].append({"content": line.strip(), "line": i + 1, "type": "ordered"})

        return elements

    def _extract_code_language(self, fence_line: str) -> str:
        """Extract programming language from code fence"""
        match = re.search(r"```\s*(\w+)", fence_line)
        return match.group(1) if match else "text"
