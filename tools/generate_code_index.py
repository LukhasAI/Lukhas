#!/usr/bin/env python3
"""
LUKHAS AI Code Index Generator
Scans source files to create comprehensive migration map
"""

import ast
import re
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path


class CodeIndexer:
    """Generate comprehensive code index for migration"""

    def __init__(self, root_path="."):
        self.root = Path(root_path)
        self.conn = sqlite3.connect("tools/code_index.sqlite")
        self.setup_database()

        # Exclude paths (build artifacts, virtual envs, etc)
        self.exclude_dirs = {
            ".venv", "venv", "env",
            "build", "dist", "__pycache__",
            ".git", ".pytest_cache", ".mypy_cache",
            "node_modules", "*.egg-info",
            ".tox", "htmlcov", "coverage",
            "docs/_build", "site-packages"
        }

        # Track duplicate modules
        self.bio_variants = defaultdict(list)
        self.memory_variants = defaultdict(list)
        self.duplicate_modules = defaultdict(list)

        # Import tracking
        self.import_graph = defaultdict(set)
        self.reverse_imports = defaultdict(set)

        # Module classification
        self.module_stats = {
            "total_files": 0,
            "total_lines": 0,
            "has_tests": 0,
            "has_types": 0,
            "trinity_modules": 0,
            "import_errors": []
        }

    def setup_database(self):
        """Create SQLite schema for code index"""
        cursor = self.conn.cursor()

        # Main file index
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY,
                path TEXT UNIQUE,
                module_path TEXT,
                lines INTEGER,
                has_tests BOOLEAN,
                has_types BOOLEAN,
                trinity_framework BOOLEAN,
                lane TEXT,  -- accepted/candidate/quarantine/archive
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Import relationships
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS imports (
                id INTEGER PRIMARY KEY,
                from_file TEXT,
                to_module TEXT,
                import_type TEXT,  -- absolute/relative/external
                line_number INTEGER,
                FOREIGN KEY (from_file) REFERENCES files(path)
            )
        """)

        # Duplicate tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS duplicates (
                id INTEGER PRIMARY KEY,
                module_type TEXT,  -- bio/memory/other
                variant_name TEXT,
                file_path TEXT,
                line_count INTEGER,
                has_unique_logic BOOLEAN
            )
        """)

        # Migration mappings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY,
                old_import TEXT,
                new_import TEXT,
                shim_required BOOLEAN,
                deprecation_date TEXT
            )
        """)

        self.conn.commit()

    def should_skip(self, path):
        """Check if path should be excluded"""
        path_str = str(path)

        # Skip excluded directories
        for part in path.parts:
            if part in self.exclude_dirs or part.startswith("."):
                return True

        # Skip test files in root (we'll handle test directories separately)
        if path.name.startswith("test_") or path.name.endswith("_test.py"):
            return False  # Don't skip tests, we want to track them

        # Skip generated files
        if any(pattern in path_str for pattern in ["_pb2.py", "_pb2_grpc.py", ".pyc"]):
            return True

        return False

    def classify_module(self, path):
        """Classify module into lane based on content and location"""
        path_str = str(path)

        # Check for bio variants
        if "bio" in path_str.lower():
            # Extract bio variant name
            parts = path.parts
            for i, part in enumerate(parts):
                if "bio" in part.lower():
                    variant = "_".join(parts[i:i+2]) if i+1 < len(parts) else part
                    self.bio_variants[variant].append(path_str)
                    break

        # Check for memory variants
        if "memory" in path_str.lower():
            parts = path.parts
            for i, part in enumerate(parts):
                if "memory" in part.lower():
                    variant = "_".join(parts[i:i+2]) if i+1 < len(parts) else part
                    self.memory_variants[variant].append(path_str)
                    break

        # Determine lane assignment
        if any(test in path_str for test in ["test", "tests", "testing"]):
            return "tests"  # Special category for tests
        elif any(core in path_str for core in ["core", "identity", "governance", "orchestration"]):
            return "accepted"
        elif any(exp in path_str for exp in ["quantum", "qim", "vivox", "universal_language"]):
            return "candidate"
        elif any(legacy in path_str for legacy in ["legacy", "old", "deprecated", "_old"]):
            return "quarantine"
        elif "archive" in path_str:
            return "archive"
        else:
            # Default classification based on imports and quality
            return self.classify_by_quality(path)

    def classify_by_quality(self, path):
        """Classify based on code quality indicators"""
        try:
            content = path.read_text(errors="ignore")

            # Check for quality indicators
            has_docstrings = '"""' in content or "'''" in content
            has_types = ": " in content and "->" in content  # Basic type hint check
            has_tests = "test_" in str(path) or "import pytest" in content
            has_trinity = any(marker in content for marker in ["⚛️", "🧠", "🛡️", "Trinity"])

            # Score the module
            score = sum([has_docstrings, has_types, has_tests, has_trinity])

            if score >= 3:
                return "accepted"
            elif score >= 2:
                return "candidate"
            elif score >= 1:
                return "quarantine"
            else:
                return "archive"

        except Exception:
            return "quarantine"

    def extract_imports(self, path):
        """Extract all imports from a Python file"""
        imports = []
        try:
            content = path.read_text(errors="ignore")
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append({
                            "module": alias.name,
                            "type": "absolute",
                            "line": node.lineno
                        })
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    level = node.level
                    import_type = "relative" if level > 0 else "absolute"

                    for alias in node.names:
                        full_import = f"{module}.{alias.name}" if module else alias.name
                        imports.append({
                            "module": full_import,
                            "type": import_type,
                            "line": node.lineno
                        })

                        # Track import relationships
                        self.import_graph[str(path)].add(full_import)
                        self.reverse_imports[full_import].add(str(path))

        except SyntaxError as e:
            self.module_stats["import_errors"].append({
                "file": str(path),
                "error": str(e)
            })
        except Exception:
            pass  # Ignore other parsing errors

        return imports

    def analyze_file(self, path):
        """Analyze a single Python file"""
        try:
            content = path.read_text(errors="ignore")
            lines = len(content.splitlines())

            # Extract metadata
            has_tests = "test_" in str(path) or "import pytest" in content
            has_types = bool(re.search(r":\s*\w+\s*[=,)]|->\s*\w+", content))
            has_trinity = any(marker in content for marker in ["⚛️", "🧠", "🛡️", "Trinity"])

            # Classify module
            lane = self.classify_module(path)

            # Convert to module path
            module_path = str(path.relative_to(self.root)).replace("/", ".").replace(".py", "")

            # Store in database
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO files
                (path, module_path, lines, has_tests, has_types, trinity_framework, lane)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (str(path), module_path, lines, has_tests, has_types, has_trinity, lane))

            # Extract and store imports
            imports = self.extract_imports(path)
            for imp in imports:
                cursor.execute("""
                    INSERT INTO imports (from_file, to_module, import_type, line_number)
                    VALUES (?, ?, ?, ?)
                """, (str(path), imp["module"], imp["type"], imp["line"]))

            self.conn.commit()

            # Update stats
            self.module_stats["total_files"] += 1
            self.module_stats["total_lines"] += lines
            if has_tests:
                self.module_stats["has_tests"] += 1
            if has_types:
                self.module_stats["has_types"] += 1
            if has_trinity:
                self.module_stats["trinity_modules"] += 1

        except Exception as e:
            print(f"Error analyzing {path}: {e}", file=sys.stderr)

    def find_duplicates(self):
        """Identify and catalog duplicate modules"""
        cursor = self.conn.cursor()

        # Process bio variants
        for variant, paths in self.bio_variants.items():
            if len(paths) > 1:
                for path in paths:
                    # Check if has unique logic
                    has_unique = self.check_unique_logic(path)
                    lines = len(Path(path).read_text(errors="ignore").splitlines())

                    cursor.execute("""
                        INSERT INTO duplicates (module_type, variant_name, file_path, line_count, has_unique_logic)
                        VALUES (?, ?, ?, ?, ?)
                    """, ("bio", variant, path, lines, has_unique))

        # Process memory variants
        for variant, paths in self.memory_variants.items():
            if len(paths) > 1:
                for path in paths:
                    has_unique = self.check_unique_logic(path)
                    lines = len(Path(path).read_text(errors="ignore").splitlines())

                    cursor.execute("""
                        INSERT INTO duplicates (module_type, variant_name, file_path, line_count, has_unique_logic)
                        VALUES (?, ?, ?, ?, ?)
                    """, ("memory", variant, path, lines, has_unique))

        self.conn.commit()

    def check_unique_logic(self, path):
        """Check if file has unique logic worth preserving"""
        try:
            content = Path(path).read_text(errors="ignore")

            # Check for unique patterns
            unique_patterns = [
                r"class\s+\w+\(.*\):",  # Unique classes
                r"def\s+\w+\(.*\):.*?return",  # Functions with logic
                r"@\w+",  # Decorators
                r"async\s+def",  # Async functions
            ]

            for pattern in unique_patterns:
                if re.search(pattern, content, re.DOTALL):
                    return True

            return False

        except Exception:
            return False

    def generate_migration_mappings(self):
        """Generate old->new import mappings"""
        cursor = self.conn.cursor()

        # Bio consolidation mappings
        cursor.execute("""
            INSERT INTO migrations (old_import, new_import, shim_required, deprecation_date)
            VALUES
                ('bio_core', 'lukhas.accepted.bio', true, '2025-11-01'),
                ('bio_orchestrator', 'lukhas.accepted.bio.orchestrator', true, '2025-11-01'),
                ('bio_symbolic', 'lukhas.accepted.bio.symbolic', true, '2025-11-01'),
                ('bio_quantum_radar_integration', 'lukhas.candidate.bio.quantum', true, '2025-11-01')
        """)

        # Memory consolidation mappings
        cursor.execute("""
            INSERT INTO migrations (old_import, new_import, shim_required, deprecation_date)
            VALUES
                ('memory.fold_manager', 'lukhas.accepted.memory.fold', true, '2025-11-01'),
                ('memory.memory_consolidation', 'lukhas.accepted.memory.consolidation', true, '2025-11-01'),
                ('memory.episodic', 'lukhas.accepted.memory.episodic', true, '2025-11-01')
        """)

        # Core module mappings
        cursor.execute("""
            INSERT INTO migrations (old_import, new_import, shim_required, deprecation_date)
            VALUES
                ('core.glyph', 'lukhas.accepted.core.glyph', true, '2025-11-01'),
                ('identity.core', 'lukhas.accepted.identity', true, '2025-11-01'),
                ('governance.guardian', 'lukhas.accepted.governance.guardian', true, '2025-11-01')
        """)

        # Candidate module mappings (feature-flagged)
        cursor.execute("""
            INSERT INTO migrations (old_import, new_import, shim_required, deprecation_date)
            VALUES
                ('universal_language', 'lukhas.candidate.ul', true, '2025-11-01'),
                ('vivox', 'lukhas.candidate.vivox', true, '2025-11-01'),
                ('qim', 'lukhas.candidate.qim', true, '2025-11-01')
        """)

        self.conn.commit()

    def scan_codebase(self):
        """Main scanning function"""
        print("🔍 Scanning LUKHAS AI codebase...")

        # Find all Python files
        py_files = []
        for path in self.root.rglob("*.py"):
            if not self.should_skip(path):
                py_files.append(path)

        print(f"📊 Found {len(py_files)} Python source files")

        # Analyze each file
        for i, path in enumerate(py_files, 1):
            if i % 100 == 0:
                print(f"  Processing file {i}/{len(py_files)}...")
            self.analyze_file(path)

        # Find duplicates
        print("🔎 Identifying duplicate modules...")
        self.find_duplicates()

        # Generate migration mappings
        print("🗺️ Generating migration mappings...")
        self.generate_migration_mappings()

        return self.module_stats

    def generate_reports(self):
        """Generate markdown reports"""
        cursor = self.conn.cursor()

        # Generate MAP.md
        map_content = """# LUKHAS AI Code Index Map
Generated: {}

## Overview
- Total Files: {}
- Total Lines: {}
- Files with Tests: {}
- Files with Types: {}
- Trinity Framework Modules: {}

## Lane Distribution
""".format(
            datetime.now().isoformat(),
            self.module_stats["total_files"],
            self.module_stats["total_lines"],
            self.module_stats["has_tests"],
            self.module_stats["has_types"],
            self.module_stats["trinity_modules"]
        )

        # Add lane statistics
        cursor.execute("""
            SELECT lane, COUNT(*) as count, SUM(lines) as total_lines
            FROM files
            GROUP BY lane
            ORDER BY count DESC
        """)

        for row in cursor.fetchall():
            map_content += f"- **{row[0]}**: {row[1]} files ({row[2]:,} lines)\n"

        # Add duplicate analysis
        map_content += "\n## Duplicate Modules Found\n\n### Bio Variants\n"
        cursor.execute("""
            SELECT variant_name, COUNT(*) as count, SUM(has_unique_logic) as unique_count
            FROM duplicates
            WHERE module_type = 'bio'
            GROUP BY variant_name
        """)

        for row in cursor.fetchall():
            map_content += f"- **{row[0]}**: {row[1]} variants ({row[2]} with unique logic)\n"

        map_content += "\n### Memory Variants\n"
        cursor.execute("""
            SELECT variant_name, COUNT(*) as count, SUM(has_unique_logic) as unique_count
            FROM duplicates
            WHERE module_type = 'memory'
            GROUP BY variant_name
        """)

        for row in cursor.fetchall():
            map_content += f"- **{row[0]}**: {row[1]} variants ({row[2]} with unique logic)\n"

        # Add import graph analysis
        map_content += "\n## Import Complexity\n"
        map_content += f"- Total Import Relationships: {len(self.import_graph)}\n"
        map_content += "- Modules with Most Dependencies: \n"

        # Find modules with most imports
        sorted_imports = sorted(self.import_graph.items(), key=lambda x: len(x[1]), reverse=True)[:10]
        for module, imports in sorted_imports:
            module_name = Path(module).stem
            map_content += f"  - {module_name}: {len(imports)} imports\n"

        # Write MAP.md
        map_path = self.root / "docs" / "AUDIT" / "MAP.md"
        map_path.parent.mkdir(parents=True, exist_ok=True)
        map_path.write_text(map_content)

        # Generate MIGRATION_GUIDE.md
        migration_content = f"""# LUKHAS AI Migration Guide
Generated: {datetime.now().isoformat()}

## Import Mappings

Use these mappings to update your imports:

### Core Modules
"""

        cursor.execute("""
            SELECT old_import, new_import, deprecation_date
            FROM migrations
            WHERE old_import not_like '%candidate%'
            ORDER BY old_import
        """)

        for row in cursor.fetchall():
            migration_content += f"- `{row[0]}` → `{row[1]}` (deprecated: {row[2]})\n"

        migration_content += "\n### Candidate Modules (Feature-Flagged)\n"

        cursor.execute("""
            SELECT old_import, new_import, deprecation_date
            FROM migrations
            WHERE new_import LIKE '%candidate%'
            ORDER BY old_import
        """)

        for row in cursor.fetchall():
            migration_content += f"- `{row[0]}` → `{row[1]}` (deprecated: {row[2]})\n"

        migration_content += """
## Migration Steps

1. **Update imports** using the mappings above
2. **Run tests** to verify functionality
3. **Enable feature flags** for candidate modules as needed
4. **Remove old imports** after testing

## Compatibility Shims

All old imports will continue working until **2025-11-01** via compatibility shims.

Example shim usage:
```python
# Old import (will show deprecation warning)
from lukhas.accepted.bio.core import BioEngine

# New import (recommended)
from lukhas.accepted.bio import BioEngine
```

## Feature Flags

For candidate modules, enable via environment variables:
- `UL_ENABLED=true` - Universal Language
- `VIVOX_LITE=true` - VIVOX consciousness system
- `QIM_SANDBOX=true` - Quantum-Inspired Module

## Need Help?

Check the following resources:
- `docs/ADR/ADR-0001-code-maturity-lanes.md` - Architecture decision
- `CODEOWNERS` - Module ownership
- `.github/PULL_REQUEST_TEMPLATE.md` - PR checklist
"""

        # Write MIGRATION_GUIDE.md
        guide_path = self.root / "docs" / "MIGRATION_GUIDE.md"
        guide_path.parent.mkdir(parents=True, exist_ok=True)
        guide_path.write_text(migration_content)

        print("✅ Generated reports:")
        print(f"   - {map_path}")
        print(f"   - {guide_path}")
        print("   - tools/code_index.sqlite")

    def close(self):
        """Close database connection"""
        self.conn.close()


def main():
    """Main entry point"""
    indexer = CodeIndexer()

    try:
        # Scan codebase
        stats = indexer.scan_codebase()

        # Generate reports
        indexer.generate_reports()

        # Print summary
        print("\n📈 Indexing Complete!")
        print(f"   - Files: {stats['total_files']:,}")
        print(f"   - Lines: {stats['total_lines']:,}")
        print(f"   - With Tests: {stats['has_tests']}")
        print(f"   - With Types: {stats['has_types']}")
        print(f"   - Trinity Modules: {stats['trinity_modules']}")

        if stats["import_errors"]:
            print(f"\n⚠️  Found {len(stats['import_errors'])} files with syntax errors")

    finally:
        indexer.close()


if __name__ == "__main__":
    main()
