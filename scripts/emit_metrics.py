#!/usr/bin/env python3
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
import argparse
import json
import pathlib
import re


def main():
    """Aggregate documentation quality metrics and emit JSON.

    Args:
        --coverage: Path to Interrogate JSON output file.
        --offenders: Path to pydocstyle offenders text file.
        --spectral-junit: Path to Spectral JUnit XML results.
        --out: Output path for the consolidated metrics JSON.

    Returns:
        None: Prints the JSON to stdout and writes it to ``--out``.

    Raises:
        FileNotFoundError: If any required input file path is missing.

    Example:
        >>> # doctest: +SKIP
        >>> from pathlib import Path
        >>> Path('docs/audits').mkdir(parents=True, exist_ok=True)
        >>> Path('docs/audits/docstring_coverage.json').write_text('{"overall": 86}')
        20
        >>> Path('docs/audits/docstring_offenders.txt').write_text('')
        0
        >>> Path('docs/audits/openapi_lint_junit.xml').write_text('<testsuite></testsuite>')
        24
        >>> import sys
        >>> sys.argv = [
        ...   'emit_metrics',
        ...   '--coverage','docs/audits/docstring_coverage.json',
        ...   '--offenders','docs/audits/docstring_offenders.txt',
        ...   '--spectral-junit','docs/audits/openapi_lint_junit.xml',
        ...   '--out','docs/audits/metrics.json']
        >>> main()
    """
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
    pydocstyle_errors = (
        0 if offenders_txt.strip() == "" else len([ln for ln in offenders_txt.splitlines() if re.search(r":\d+:", ln)])
    )

    # Parse Spectral JUnit XML
    junit_xml = spec_path.read_text() if spec_path.exists() else ""
    spectral_errors = len(re.findall(r"<failure ", junit_xml))

    # Emit unified metrics
    out = {"doc_coverage": doc_coverage, "pydocstyle_errors": pydocstyle_errors, "spectral_errors": spectral_errors}

    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2))

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
