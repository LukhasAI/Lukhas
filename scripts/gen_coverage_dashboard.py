#!/usr/bin/env python3
"""
Module: gen_coverage_dashboard.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

"""
Generate documentation coverage dashboard from metrics JSON.

Creates a Markdown dashboard with current docstring coverage, pydocstyle errors,
and Spectral OpenAPI lint errors with links to detailed artifacts.

Usage:
    python scripts/gen_coverage_dashboard.py \
      --metrics docs/audits/metrics.json \
      --out docs/audits/coverage_dashboard.md

Author: LUKHAS Development Team
Last Updated: 2025-10-19
"""
import json
import argparse
import pathlib


def main():
    p = argparse.ArgumentParser(description="Generate coverage dashboard")
    p.add_argument("--metrics", required=True, help="Path to metrics.json")
    p.add_argument("--out", required=True, help="Output Markdown path")
    args = p.parse_args()

    metrics = json.loads(pathlib.Path(args.metrics).read_text())

    doc_coverage = metrics.get('doc_coverage', 0)
    pydocstyle_errors = metrics.get('pydocstyle_errors', 0)
    spectral_errors = metrics.get('spectral_errors', 0)

    # Determine status emojis
    cov_emoji = "✅" if doc_coverage >= 85 else "⚠️" if doc_coverage >= 70 else "❌"
    style_emoji = "✅" if pydocstyle_errors == 0 else "⚠️" if pydocstyle_errors < 10 else "❌"
    spec_emoji = "✅" if spectral_errors == 0 else "⚠️" if spectral_errors < 5 else "❌"

    md = f"""# Documentation Coverage Dashboard

**Generated**: {pathlib.Path().cwd()}
**Status**: Auto-updated by CI

---

## 📊 Metrics

| Metric | Value | Status |
|--------|-------|--------|
| **Docstring Coverage** | {doc_coverage:.1f}% | {cov_emoji} |
| **pydocstyle Errors** | {pydocstyle_errors} | {style_emoji} |
| **Spectral OpenAPI Errors** | {spectral_errors} | {spec_emoji} |

---

## 📈 Thresholds

- **Docstring Coverage**: ≥85% (target)
- **pydocstyle Errors**: 0 (target)
- **Spectral Errors**: 0 (target)

---

## 📂 Artifacts

- [docstring_coverage.json](docstring_coverage.json) - Interrogate raw output
- [docstring_offenders.txt](docstring_offenders.txt) - pydocstyle error list
- [openapi_lint_junit.xml](openapi_lint_junit.xml) - Spectral JUnit XML
- [metrics.json](metrics.json) - Unified metrics (this dashboard source)

---

## 🎯 Next Steps

{'### ✅ All targets met! No action required.' if doc_coverage >= 85 and pydocstyle_errors == 0 and spectral_errors == 0 else f"""
### Improvements Needed

{f'- **Docstring Coverage**: Increase from {doc_coverage:.1f}% to ≥85%' if doc_coverage < 85 else ''}
{f'- **pydocstyle**: Fix {pydocstyle_errors} style violations' if pydocstyle_errors > 0 else ''}
{f'- **Spectral**: Fix {spectral_errors} OpenAPI lint errors' if spectral_errors > 0 else ''}
"""}

---

*Last updated by CI pipeline*
"""

    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md)

    print(f"✅ Wrote dashboard to {args.out}")


if __name__ == "__main__":
    main()
