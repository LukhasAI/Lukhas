#!/usr/bin/env python3
"""
Module: emit_metrics.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

"""
Emit unified documentation quality metrics.

Aggregates interrogate coverage, pydocstyle errors, and Spectral lint results
into a single JSON metrics file for dashboard consumption.

Usage:
    python scripts/emit_metrics.py \
      --coverage docs/audits/docstring_coverage.json \
      --offenders docs/audits/docstring_offenders.txt \
      --spectral-junit docs/audits/openapi_lint_junit.xml \
      --out docs/audits/metrics.json

Author: LUKHAS Development Team
Last Updated: 2025-10-19
"""
import json
import argparse
import re
import pathlib


def main():
    p = argparse.ArgumentParser(description="Emit unified documentation metrics")
    p.add_argument("--coverage", required=True, help="Path to interrogate JSON output")
    p.add_argument("--offenders", required=True, help="Path to pydocstyle error file")
    p.add_argument("--spectral-junit", required=True, help="Path to Spectral JUnit XML")
    p.add_argument("--out", required=True, help="Output metrics JSON path")
    args = p.parse_args()

    cov_path = pathlib.Path(args.coverage)
    off_path = pathlib.Path(args.offenders)
    spec_path = pathlib.Path(args.spectral_junit)

    # Parse interrogate coverage
    cov = json.loads(cov_path.read_text()) if cov_path.exists() else {}
    doc_coverage = (
        cov.get("overall")
        or cov.get("results", {}).get("percentage")
        or cov.get("summary", {}).get("percent_covered")
        or 0
    )

    # Parse pydocstyle errors
    offenders_txt = off_path.read_text() if off_path.exists() else ""
    pydocstyle_errors = 0 if offenders_txt.strip() == "" else len([
        ln for ln in offenders_txt.splitlines() if re.search(r":\d+:", ln)
    ])

    # Parse Spectral JUnit XML
    junit_xml = spec_path.read_text() if spec_path.exists() else ""
    spectral_errors = len(re.findall(r'<failure ', junit_xml))

    # Emit unified metrics
    out = {
        "doc_coverage": doc_coverage,
        "pydocstyle_errors": pydocstyle_errors,
        "spectral_errors": spectral_errors
    }

    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2))

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
