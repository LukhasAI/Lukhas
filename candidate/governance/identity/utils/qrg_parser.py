"""
QR-G and GLYMPH Parsing Tools
=============================

Utilities for parsing and validating QR-G codes and GLYMPH symbols
within the LUKHAS ecosystem.

Features:
- QR-G code parsing and validation
- GLYMPH symbol interpretation
- Format validation
- Security checks
"""
import json
import re


class QRGParser:
    """Parse and validate QR-G codes"""

    def __init__(self, config):
        self.config = config
        self.valid_patterns = {}

    def parse_qr_code(self, qr_data: str) -> dict:
        """Parse QR-G code data"""
        # ΛTAG: qrg_parse
        try:
            if qr_data.startswith("{"):
                return json.loads(qr_data)
            key, value = qr_data.split("|", 1)
            return {"type": key, "payload": value}
        except Exception as e:
            raise ValueError(f"Invalid QR-G data: {e}")

    def validate_qr_format(self, qr_data: str) -> bool:
        """Validate QR-G code format"""
        # ΛTAG: qrg_format_validation
        pattern = self.config.get("qr_format", r"^[A-Z0-9|:{}\s]+$")
        return bool(re.match(pattern, qr_data))

    def extract_metadata(self, qr_data: str) -> dict:
        """Extract metadata from QR-G code"""
        # ΛTAG: qrg_metadata
        parsed = self.parse_qr_code(qr_data)
        return parsed.get("metadata", {}) if isinstance(parsed, dict) else {}


class GLYMPHParser:
    """Parse and interpret GLYMPH symbols"""

    def __init__(self, config):
        self.config = config
        self.symbol_map = {}

    def parse_glymph(self, glymph_data: str) -> dict:
        """Parse GLYMPH symbol data"""
        # ΛTAG: glymph_parse
        tokens = glymph_data.split("-")
        return {"tokens": tokens}

    def interpret_symbols(self, symbol_sequence: str) -> str:
        """Interpret sequence of GLYMPH symbols"""
        # ΛTAG: glymph_interpret
        mapping = self.config.get("symbol_map", {})
        return " ".join(mapping.get(t, t) for t in symbol_sequence.split("-"))

    def validate_glymph_sequence(self, sequence: str) -> bool:
        """Validate GLYMPH symbol sequence"""
        # ΛTAG: glymph_validate
        allowed = self.config.get("allowed_symbols", set())
        return all(sym in allowed for sym in sequence.split("-"))