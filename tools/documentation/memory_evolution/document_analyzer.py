"""
Document Structure Analyzer for DocuTutor.
Analyzes document structure and quality metrics.
"""
import re
from collections import Counter

import streamlit as st


class DocumentStructureAnalyzer:
    def __init__(self):
        self.section_patterns = [
            r"#{1,6}\s+.+",  # Markdown headers
            r"[A-Z][A-Za-z\s]+:",  # Title-case labels
            r"\d+\.\s+.+",  # Numbered sections
        ]
        self.code_block_patterns = [
            r"```[\s\S]*?```",  # Code blocks
            r"`[^`]+`",  # Inline code
        ]

    def analyze_structure(self, content: str) -> dict:
        """Analyze document structure and return quality metrics."""
        metrics = {
            "section_depth": self._analyze_section_depth(content),
            "code_quality": self._analyze_code_blocks(content),
            "link_density": self._analyze_link_density(content),
            "readability": self._analyze_readability(content),
            "formatting": self._analyze_formatting(content),
        }

        # Calculate overall structure score
        weights = {
            "section_depth": 0.25,
            "code_quality": 0.2,
            "link_density": 0.15,
            "readability": 0.25,
            "formatting": 0.15,
        }

        overall_score = sum(metrics[key] * weights[key] for key in weights)

        return {**metrics, "overall_score": overall_score}

    def _analyze_section_depth(self, content: str) -> float:
        """Analyze section hierarchy depth and organization."""
        sections = []
        for pattern in self.section_patterns:
            sections.extend(re.findall(pattern, content))

        if not sections:
            return 0.0

        # Count section depths
        depths = Counter(len(re.match(r"#+", section).group(0)) for section in sections if section.startswith("#"))

        # Calculate depth score
        max_depth = max(depths.keys()) if depths else 0
        depth_variety = len(depths)
        sections_per_level = sum(depths.values()) / len(depths) if depths else 0

        return min(
            1.0,
            (0.3 * min(3, max_depth) / 3 + 0.4 * min(3, depth_variety) / 3 + 0.3 * min(5, sections_per_level) / 5),
        )

    def _analyze_code_blocks(self, content: str) -> float:
        """Analyze code block quality and formatting."""
        code_blocks = []
        for pattern in self.code_block_patterns:
            code_blocks.extend(re.findall(pattern, content))

        if not code_blocks:
            return 1.0  # Perfect score for non-code documentation

        # Analyze code blocks
        scores = []
        for block in code_blocks:
            # Strip markdown markers
            code = re.sub(r"```\w*\n|```$", "", block)

            # Calculate metrics
            lines = code.split("\n")
            if not lines:
                continue

            indent_consistency = len({len(line) - len(line.lstrip()) for line in lines if line.strip()}) <= 2

            has_comments = any(re.search(r"#|//|/\*|\*/", line) for line in lines)

            avg_line_length = sum(len(line) for line in lines) / len(lines)
            good_length = 20 <= avg_line_length <= 100

            score = 0.4 * indent_consistency + 0.3 * has_comments + 0.3 * good_length
            scores.append(score)

        return sum(scores) / len(scores) if scores else 0.0

    def _analyze_link_density(self, content: str) -> float:
        """Analyze link and reference density."""
        # Count markdown links and references
        links = len(re.findall(r"\[([^\]]+)\]\(([^\)]+)\)", content))
        references = len(re.findall(r"\[([^\]]+)\]\[([^\]]+)\]", content))
        words = len(content.split())

        if words == 0:
            return 0.0

        # Calculate optimal link density (1 link per 50-100 words)
        density = (links + references) / (words / 75)
        return min(1.0, density if density <= 1.0 else 1.0 / density)

    def _analyze_readability(self, content: str) -> float:
        """Analyze text readability."""
        sentences = re.split(r"[.!?]+", content)
        if not sentences:
            return 0.0

        # Calculate average sentence length
        avg_sentence_length = sum(len(s.split()) for s in sentences if s.strip()) / len(sentences)

        # Penalize very short or very long sentences
        length_score = 1.0 - abs(avg_sentence_length - 20) / 30

        # Check for formatting variety
        has_lists = bool(re.search(r"[-*]\s+\w+", content))
        has_emphasis = bool(re.search(r"\*\w+\*|_\w+_", content))
        has_structure = bool(re.search(r"#{1,6}\s+\w+", content))

        format_score = 0.4 * has_lists + 0.3 * has_emphasis + 0.3 * has_structure

        return min(1.0, 0.6 * max(0, length_score) + 0.4 * format_score)

    def _analyze_formatting(self, content: str) -> float:
        """Analyze document formatting consistency."""
        # Check consistent spacing
        consistent_spacing = len({len(line) - len(line.lstrip()) for line in content.split("\n") if line.strip()}) <= 2

        # Check list formatting
        list_items = re.findall(r"[-*]\s+\w+", content)
        consistent_lists = len({line[0] for line in list_items}) <= 1 if list_items else True

        # Check header formatting
        headers = re.findall(r"#{1,6}\s+\w+", content)
        consistent_headers = (
            len({len(h) - len(h.lstrip("#")) for h in headers}) == len({re.sub(r"#+\s+", "", h) for h in headers})
            if headers
            else True
        )

        return 0.4 * consistent_spacing + 0.3 * consistent_lists + 0.3 * consistent_headers
