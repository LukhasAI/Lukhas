#!/usr/bin/env python3
"""
PDF Parser for ΛLens
Handles PDF files and extracts text content
"""

from typing import Any

from .base_parser import BaseParser


class PDFParser(BaseParser):
    """Parser for PDF files"""

    async def parse(self, file_path: str) -> dict[str, Any]:
        """Parse PDF file and extract content"""
        try:
            # Try to import PyPDF2
            import PyPDF2
        except ImportError:
            # Fallback to basic file reading
            return await self._parse_basic(file_path)

        try:
            file_info = self._get_file_info(file_path)

            with open(file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)

                # Extract text from all pages
                text_content = []
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    text_content.append({"page_number": page_num + 1, "content": text, "characters": len(text)})

                # Combine all text
                full_text = "\n".join([page["content"] for page in text_content])

                return {
                    "text": full_text,
                    "format": "pdf",
                    "pages": text_content,
                    "total_pages": len(text_content),
                    "file_info": file_info,
                }

        except Exception:
            # Fallback to basic parsing
            return await self._parse_basic(file_path)

    async def _parse_basic(self, file_path: str) -> dict[str, Any]:
        """Basic PDF parsing when PyPDF2 is not available"""
        file_info = self._get_file_info(file_path)

        # Read raw bytes (limited)
        with open(file_path, "rb") as f:
            raw_content = f.read(1024)  # Read first 1KB

        return {
            "text": f"PDF file: {file_info['filename']} (PyPDF2 not available for full parsing)",
            "format": "pdf",
            "raw_preview": raw_content.hex()[:100],
            "file_info": file_info,
            "parsing_note": "Install PyPDF2 for full PDF text extraction: pip install PyPDF2",
        }
