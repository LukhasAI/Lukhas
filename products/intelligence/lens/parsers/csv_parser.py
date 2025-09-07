#!/usr/bin/env python3
"""
CSV Parser for ΛLens
Handles CSV files and extracts tabular data
"""
import csv
import re
from typing import Any, Dict, List

import streamlit as st

from .base_parser import BaseParser


class CSVParser(BaseParser):
    """Parser for CSV files"""

    async def parse(self, file_path: str) -> dict[str, Any]:
        """Parse CSV file and extract data"""
        try:
            file_info = self._get_file_info(file_path)

            # Try to detect delimiter and encoding
            delimiter = self._detect_delimiter(file_path)
            encoding = self._detect_encoding(file_path)

            with open(file_path, encoding=encoding) as f:
                # Read sample to detect if it has headers
                sample_reader = csv.reader(f, delimiter=delimiter)
                sample_rows = []
                for i, row in enumerate(sample_reader):
                    sample_rows.append(row)
                    if i >= 10:  # Read first 10 rows
                        break

            # Reset file pointer
            with open(file_path, encoding=encoding) as f:
                # Determine if first row is headers
                has_headers = self._detect_headers(sample_rows)

                # Read all data
                reader = csv.DictReader(f, delimiter=delimiter) if has_headers else csv.reader(f, delimiter=delimiter)

                rows = []
                headers = []

                if has_headers:
                    headers = reader.fieldnames or []
                    for row in reader:
                        rows.append(row)
                else:
                    for row in reader:
                        rows.append(row)
                    # Generate generic headers
                    if rows:
                        headers = [f"col_{i + 1}" for i in range(len(rows[0]))]

                # Analyze data types
                column_types = self._analyze_column_types(rows, headers, has_headers)

                return {
                    "data": rows,
                    "format": "csv",
                    "headers": headers,
                    "has_headers": has_headers,
                    "row_count": len(rows),
                    "column_count": len(headers),
                    "column_types": column_types,
                    "delimiter": delimiter,
                    "encoding": encoding,
                    "file_info": file_info,
                }

        except Exception as e:
            raise ValueError(f"Failed to parse CSV file {file_path}: {e!s}")

    def _detect_delimiter(self, file_path: str) -> str:
        """Detect CSV delimiter"""
        with open(file_path, encoding="utf-8") as f:
            sample = f.read(1024)

        # Try different delimiters
        delimiters = [",", ";", "\t", "|"]
        delimiter_counts = {}

        for delimiter in delimiters:
            count = sample.count(delimiter)
            if count > 0:
                delimiter_counts[delimiter] = count

        # Return delimiter with highest count, default to comma
        return max(delimiter_counts, key=delimiter_counts.get) if delimiter_counts else ","

    def _detect_encoding(self, file_path: str) -> str:
        """Detect file encoding"""
        try:
            import chardet

            with open(file_path, "rb") as f:
                raw_data = f.read(10000)
            result = chardet.detect(raw_data)
            return result["encoding"] or "utf-8"
        except ImportError:
            return "utf-8"

    def _detect_headers(self, sample_rows: list[list[str]]) -> bool:
        """Detect if first row contains headers"""
        if len(sample_rows) < 2:
            return False

        first_row = sample_rows[0]
        second_row = sample_rows[1] if len(sample_rows) > 1 else []

        # Check if first row looks like headers (contains strings, second row has mixed types)
        first_row_types = [self._infer_type(cell) for cell in first_row]
        second_row_types = [self._infer_type(cell) for cell in second_row]

        # Headers are likely if first row is mostly strings and second row has variety
        first_row_string_ratio = sum(1 for t in first_row_types if t == "string") / len(first_row_types)
        second_row_type_variety = len(set(second_row_types))

        return first_row_string_ratio > 0.7 and second_row_type_variety > 1

    def _infer_type(self, value: str) -> str:
        """Infer data type of a string value"""
        value = value.strip()
        if not value:
            return "empty"

        try:
            int(value)
            return "integer"
        except ValueError:
            pass

        try:
            float(value)
            return "float"
        except ValueError:
            pass

        # Check for date-like patterns
        if re.match(r"\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}", value):
            return "date"

        return "string"

    def _analyze_column_types(self, rows: list[Any], headers: list[str], has_headers: bool) -> dict[str, str]:
        """Analyze data types for each column"""
        if not rows:
            return {}

        column_types = {}

        for i, header in enumerate(headers):
            if has_headers:
                # Dict format
                values = [row.get(header, "") for row in rows if isinstance(row, dict)]
            else:
                # List format
                values = [row[i] if i < len(row) else "" for row in rows]

            # Sample types from first few values
            sample_values = values[:100]  # Sample first 100 rows
            types = [self._infer_type(str(val)) for val in sample_values]

            # Determine most common type
            type_counts = {}
            for t in types:
                type_counts[t] = type_counts.get(t, 0) + 1

            most_common_type = max(type_counts, key=type_counts.get)
            column_types[header] = most_common_type

        return column_types
