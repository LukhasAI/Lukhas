#!/usr/bin/env python3
"""Pytest Collection Error Analyzer - Future-proof error pattern detection.

Usage:
    python tools/error_analysis/pytest_error_analyzer.py artifacts/pytest_collect_*.txt

Outputs:
    - Categorized error patterns with counts
    - Suggested fix templates
    - Priority-ranked fix recommendations
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


class ErrorPattern:
    """Represents a categorized error pattern."""

    def __init__(self, category: str, detail: str, file: str, line: str = ""):
        self.category = category
        self.detail = detail
        self.file = file
        self.line = line

    def __hash__(self):
        return hash((self.category, self.detail))

    def __eq__(self, other):
        return (self.category, self.detail) == (other.category, other.detail)

    def __repr__(self):
        return f"{self.category}: {self.detail}"


class PytestErrorAnalyzer:
    """Analyzes pytest collection errors and suggests fixes."""

    # Error pattern regex definitions
    PATTERNS = {  # TODO[T4-ISSUE]: {"code":"RUF012","ticket":"GH-1031","owner":"consciousness-team","status":"planned","reason":"Mutable class attribute needs ClassVar annotation for type safety","estimate":"15m","priority":"medium","dependencies":"typing imports","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_tools_error_analysis_pytest_error_analyzer_py_L43"}
        'module_not_found': re.compile(r"ModuleNotFoundError: No module named '([^']+)'"),
        'cannot_import': re.compile(r"cannot import name '([^']+)' from '([^']+)'"),
        'no_attribute': re.compile(r"module '([^']+)' has no attribute '([^']+)'"),
        'no_path': re.compile(r"module '([^']+)' has no attribute '__path__'"),
        'not_package': re.compile(r"'([^']+)' is not a package"),
        'failed_assertion': re.compile(r"Failed: '([^']+)'"),
        'type_error': re.compile(r"TypeError: (.+)"),
        'attribute_error': re.compile(r"AttributeError: (.+)"),
        'import_error': re.compile(r"ImportError: (.+)"),
    }

    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.errors: list[ErrorPattern] = []
        self.error_counts: Counter = Counter()
        self.fix_suggestions: dict[str, list[str]] = defaultdict(list)

    def parse(self) -> None:
        """Parse pytest collection log for error patterns."""
        with open(self.log_file) as f:
            content = f.read()

        # Extract test file paths
        re.findall(r"ERROR (tests/[^\s]+)", content)

        # Parse error patterns
        for pattern_name, regex in self.PATTERNS.items():
            for match in regex.finditer(content):
                if pattern_name == 'module_not_found':
                    error = ErrorPattern('ModuleNotFound', match.group(1), '')
                elif pattern_name == 'cannot_import':
                    error = ErrorPattern('CannotImport', f"{match.group(1)} from {match.group(2)}", '')
                elif pattern_name == 'no_attribute':
                    error = ErrorPattern('NoAttribute', f"{match.group(1)}.{match.group(2)}", '')
                elif pattern_name == 'no_path':
                    error = ErrorPattern('NoPath', match.group(1), '')
                elif pattern_name == 'not_package':
                    error = ErrorPattern('NotPackage', match.group(1), '')
                else:
                    error = ErrorPattern(pattern_name.title().replace('_', ''), match.group(1), '')

                self.errors.append(error)
                self.error_counts[error] += 1

    def generate_fix_suggestions(self) -> None:
        """Generate fix suggestions for each error pattern."""
        for error, _count in self.error_counts.most_common():
            if error.category == 'ModuleNotFound':
                self.fix_suggestions[str(error)].append(
                    self._generate_bridge_fix(error.detail)
                )
            elif error.category == 'CannotImport':
                parts = error.detail.split(' from ')
                if len(parts) == 2:
                    symbol, module = parts
                    self.fix_suggestions[str(error)].append(
                        self._generate_export_fix(module, symbol)
                    )
            elif error.category == 'NoAttribute':
                parts = error.detail.split('.')
                if len(parts) >= 2:
                    module, attr = '.'.join(parts[:-1]), parts[-1]
                    self.fix_suggestions[str(error)].append(
                        self._generate_attribute_fix(module, attr)
                    )
            elif error.category == 'NoPath':
                self.fix_suggestions[str(error)].append(
                    self._generate_package_fix(error.detail)
                )

    def _generate_bridge_fix(self, module_name: str) -> str:
        """Generate bridge creation template."""
        parts = module_name.split('.')
        path = '/'.join(parts)

        return f"""
# Fix: Create bridge for {module_name}
mkdir -p {path}
cat > {path}/__init__.py <<'BRIDGE'
\"\"\"Bridge for {module_name}.\"\"\"
from importlib import import_module
__all__ = []

def _try(n: str):
    try: return import_module(n)
    except Exception: return None

# Search order: website → candidate → root
for n in (
    "lukhas_website.lukhas.{module_name}",
    "candidate.{module_name}",
    "{module_name}",
):
    m = _try(n)
    if m:
        for k in dir(m):
            if not k.startswith("_"):
                globals()[k] = getattr(m, k); __all__.append(k)
        break
BRIDGE
"""

    def _generate_export_fix(self, module: str, symbol: str) -> str:
        """Generate export addition template."""
        module_path = module.replace('.', '/')

        return f"""
# Fix: Add {symbol} export to {module}
cat >> {module_path}/__init__.py <<'EXPORT'

# Add {symbol} for test compatibility
try:
    from labs.{module} import {symbol}
except ImportError:
    # Stub fallback
    class {symbol}:
        def __init__(self, *a, **kw): pass

__all__.append("{symbol}")
EXPORT
"""

    def _generate_attribute_fix(self, module: str, attr: str) -> str:
        """Generate attribute addition template."""
        return f"""
# Fix: Ensure {module} exports {attr}
# Check backend module and add to bridge/export list:
# 1. Read {module}/__init__.py
# 2. Add '{attr}' to __all__ or import statement
# 3. If not available, add stub:
#    {attr} = None  # or appropriate stub
"""

    def _generate_package_fix(self, module: str) -> str:
        """Generate package conversion fix."""
        parts = module.split('.')
        path = '/'.join(parts)

        return f"""
# Fix: Convert {module} from module.py to package/
# 1. Check if {path}.py exists
# 2. If yes: mv {path}.py {path}_backup.py
# 3. Create package: mkdir -p {path}
# 4. Move content: mv {path}_backup.py {path}/__init__.py
"""

    def report(self, top_n: int = 20) -> str:
        """Generate comprehensive error analysis report."""
        lines = ["=" * 80]
        lines.append("PYTEST COLLECTION ERROR ANALYSIS")
        lines.append("=" * 80)
        lines.append(f"Log file: {self.log_file}")
        lines.append(f"Total unique error patterns: {len(self.error_counts)}")
        lines.append(f"Total error occurrences: {sum(self.error_counts.values())}")
        lines.append("")

        lines.append(f"TOP {top_n} ERROR PATTERNS (by frequency):")
        lines.append("-" * 80)

        for i, (error, count) in enumerate(self.error_counts.most_common(top_n), 1):
            lines.append(f"\n{i}. [{error.category}] {error.detail}")
            lines.append(f"   Occurrences: {count}")

            if str(error) in self.fix_suggestions:
                lines.append("   Suggested fix:")
                for suggestion in self.fix_suggestions[str(error)][:1]:  # Show first suggestion
                    for line in suggestion.strip().split('\n')[:8]:  # First 8 lines
                        lines.append(f"   {line}")
                    if len(suggestion.strip().split('\n')) > 8:
                        lines.append("   ...")

        lines.append("\n" + "=" * 80)
        lines.append("PRIORITY FIX RECOMMENDATIONS:")
        lines.append("=" * 80)

        # Group by category and sort by total impact
        category_impact = defaultdict(int)
        for error, count in self.error_counts.items():
            category_impact[error.category] += count

        for i, (category, count) in enumerate(sorted(category_impact.items(), key=lambda x: x[1], reverse=True)[:10], 1):
            lines.append(f"{i}. Fix {category} errors: {count} total occurrences")

        return '\n'.join(lines)

    def export_json(self, output_path: Path) -> None:
        """Export analysis results as JSON."""
        data = {
            "log_file": str(self.log_file),
            "total_errors": sum(self.error_counts.values()),
            "unique_patterns": len(self.error_counts),
            "errors": [
                {
                    "category": str(error.category),
                    "detail": error.detail,
                    "count": count,
                    "fix_suggestions": self.fix_suggestions.get(str(error), [])
                }
                for error, count in self.error_counts.most_common()
            ],
            "category_summary": {
                category: sum(count for e, count in self.error_counts.items() if e.category == category)
                for category in {e.category for e in self.error_counts}
            }
        }

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)


def main():
    if len(sys.argv) < 2:
        print("Usage: pytest_error_analyzer.py <pytest_collection_log>")
        sys.exit(1)

    log_file = Path(sys.argv[1])
    if not log_file.exists():
        print(f"Error: {log_file} not found")
        sys.exit(1)

    analyzer = PytestErrorAnalyzer(log_file)
    analyzer.parse()
    analyzer.generate_fix_suggestions()

    # Print report
    print(analyzer.report(top_n=15))

    # Export JSON
    json_output = log_file.parent / f"{log_file.stem}_analysis.json"
    analyzer.export_json(json_output)
    print(f"\nDetailed analysis exported to: {json_output}")


if __name__ == '__main__':
    main()
