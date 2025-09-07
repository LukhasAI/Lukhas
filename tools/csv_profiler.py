#!/usr/bin/env python3
"""Tiny CSV profiler: prints header and sample data types.

Usage: python3 tools/csv_profiler.py /path/to/file.csv
"""
import csv
import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: csv_profiler.py <csv-file>")
        sys.exit(2)
    path = sys.argv[1]
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        print("Headers:", headers)
        rows = []
        for i, r in enumerate(reader):
            rows.append(r)
            if i >= 4:
                break
        print("Sample rows:")
        for r in rows:
            print(r)


if __name__ == "__main__":
    main()
