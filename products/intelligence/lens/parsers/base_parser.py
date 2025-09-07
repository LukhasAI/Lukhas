#!/usr/bin/env python3
"""
Base Parser Module for ΛLens
Abstract base class for all file parsers
"""
import time
from abc import ABC, abstractmethod
from typing import Any

import streamlit as st


class BaseParser(ABC):
    """Base class for file parsers"""

    @abstractmethod
    async def parse(self, file_path: str) -> dict[str, Any]:
        """Parse file and return structured content"""
        pass

    def _get_file_info(self, file_path: str) -> dict[str, Any]:
        """Get basic file information"""
        from pathlib import Path

        path = Path(file_path)
        stat = path.stat()

        return {
            "filename": path.name,
            "extension": path.suffix.lower().strip("."),
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "path": str(path.absolute()),
        }
