#!/usr/bin/env python3
"""
0.01% Isolated Modules Analysis - Hidden Gems Discovery

Analyzes Python modules to find hidden gems worth integrating while filtering out
noise (tests, docs, external code). Uses multi-factor scoring to prioritize modules
by complexity, documentation, architecture compatibility, and AGI value.

Output formats:
- CSV: Full scored table for filtering
- Top 20 MD: Actionable integration suggestions
- Dependency graph JSON: For visualization
- Categorized MD: Lists by action type
- Integration roadmap MD: Phased implementation plan
"""

import ast
import csv
import json
import subprocess
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

# Exclusion patterns (external, tests, build artifacts)
EXCLUDE_PATTERNS = {
    'tests', 'docs', '__pycache__', 'node_modules', '.venv', 'venv',
    '.git', '.pytest_cache', 'dist', 'build', '.egg-info',
    'agents_external',  # External dependencies
    'benchmarks', 'prototypes',  # Trivial code
}

# Include patterns (LUKHAS AI code only)
INCLUDE_ROOTS = {
    'archive', 'candidate', 'labs', 'core', 'matriz',
    'serve', 'consciousness', 'bio', 'quantum', 'memory',
    'identity', 'governance', 'bridge', 'api', 'config',
}

# AGI/Visionary keywords
AGI_KEYWORDS = {
    'consciousness', 'quantum', 'bio', 'memoria', 'glyph',
    'dream', 'reflection', 'awareness', 'colony', 'swarm',
    'self_improvement', 'self_healing', 'adaptive', 'evolution',
}

CLASS_PATTERN_KEYWORDS = {'Engine', 'Manager', 'System', 'Controller', 'Orchestrator'}


@dataclass
class ModuleMetrics:
    """Metrics for a Python module."""
    path: str
    module_name: str
    loc: int
    classes: int
    functions: int
    has_module_doc: bool
    class_doc_ratio: float
    func_doc_ratio: float
    has_nearby_readme: bool
    imports_core: bool
    imports_matriz: bool
    imports_serve: bool
    has_engine_class: bool
    has_agi_keywords: bool
    in_archive: bool
    in_candidate_labs: bool
    last_modified_days: int
    score: float
    category: str
    integration_suggestion: str


def should_skip(path: Path) -> bool:
    """Check if path should be excluded from analysis."""
    parts = path.parts
    return any(p in EXCLUDE_PATTERNS or p.startswith('.') for p in parts)


def should_include(path: Path, root: Path) -> bool:
    """Check if path is in LUKHAS AI code (not external)."""
    try:
        rel = path.relative_to(root)
        first_part = rel.parts[0] if rel.parts else ''
        return first_part in INCLUDE_ROOTS
    except ValueError:
        return False


def get_git_last_modified(file_path: Path) -> Optional[int]:
    """Get days since last git modification."""
    try:
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%ct', str(file_path)],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0 and result.stdout.strip():
            timestamp = int(result.stdout.strip())
            modified_date = datetime.fromtimestamp(timestamp)
            days_ago = (datetime.now() - modified_date).days
            return days_ago
    except (subprocess.TimeoutExpired, ValueError, FileNotFoundError):
        pass

    # Fallback to file mtime
    try:
        modified_date = datetime.fromtimestamp(file_path.stat().st_mtime)
        return (datetime.now() - modified_date).days
    except:
        return 999  # Very old


def analyze_module(file_path: Path, root: Path) -> Optional[ModuleMetrics]:
    """Analyze a Python module and extract metrics."""
    try:
        code = file_path.read_text(encoding='utf-8')
        tree = ast.parse(code)
    except Exception:
        return None

    # Count lines (exclude blank lines)
    loc = len([line for line in code.splitlines() if line.strip()])

    # Extract metrics
    classes = []
    functions = []
    imports_core = False
    imports_matriz = False
    imports_serve = False
    has_module_doc = bool(ast.get_docstring(tree))

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(node)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not any(isinstance(p, ast.ClassDef) for p in ast.walk(tree) if node in ast.walk(p)):
                functions.append(node)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.ImportFrom) and node.module:
                if node.module.startswith('core'):
                    imports_core = True
                elif node.module.startswith('matriz') or node.module.startswith('MATRIZ'):
                    imports_matriz = True
                elif node.module.startswith('serve'):
                    imports_serve = True
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith('core'):
                        imports_core = True
                    elif alias.name.startswith('matriz') or alias.name.startswith('MATRIZ'):
                        imports_matriz = True
                    elif alias.name.startswith('serve'):
                        imports_serve = True

    # Documentation ratios
    class_doc_ratio = sum(1 for c in classes if ast.get_docstring(c)) / len(classes) if classes else 0
    func_doc_ratio = sum(1 for f in functions if ast.get_docstring(f)) / len(functions) if functions else 0

    # Check for nearby README/CLAUDE.md
    has_nearby_readme = False
    check_dir = file_path.parent
    for _ in range(3):  # Check up to 3 levels up
        if any((check_dir / name).exists() for name in ['README.md', 'CLAUDE.md', 'claude.me']):
            has_nearby_readme = True
            break
        check_dir = check_dir.parent
        if check_dir == root:
            break

    # Check for Engine/Manager/System classes
    has_engine_class = any(
        any(keyword in cls.name for keyword in CLASS_PATTERN_KEYWORDS)
        for cls in classes
    )

    # Check for AGI keywords in code
    code_lower = code.lower()
    has_agi_keywords = any(keyword in code_lower for keyword in AGI_KEYWORDS)

    # Path analysis
    rel_path = file_path.relative_to(root)
    module_name = '.'.join(rel_path.parts[:-1] + (rel_path.stem,))
    in_archive = 'archive' in rel_path.parts
    in_candidate_labs = any(p in rel_path.parts for p in ['candidate', 'labs'])

    # Git history
    last_modified_days = get_git_last_modified(file_path)

    # Calculate score
    score = calculate_score(
        loc, len(classes), len(functions),
        has_module_doc, class_doc_ratio, func_doc_ratio, has_nearby_readme,
        imports_core, imports_matriz, imports_serve,
        has_engine_class, has_agi_keywords,
        in_archive, in_candidate_labs, last_modified_days
    )

    # Categorize
    if score >= 70:
        category = 'hidden_gem'
    elif score >= 50:
        category = 'experimental'
    elif score >= 30:
        category = 'archival'
    else:
        category = 'dead_code'

    # Generate integration suggestion
    integration_suggestion = generate_integration_suggestion(
        module_name, rel_path, has_engine_class, imports_core, imports_matriz,
        in_archive, in_candidate_labs
    )

    return ModuleMetrics(
        path=str(rel_path),
        module_name=module_name,
        loc=loc,
        classes=len(classes),
        functions=len(functions),
        has_module_doc=has_module_doc,
        class_doc_ratio=class_doc_ratio,
        func_doc_ratio=func_doc_ratio,
        has_nearby_readme=has_nearby_readme,
        imports_core=imports_core,
        imports_matriz=imports_matriz,
        imports_serve=imports_serve,
        has_engine_class=has_engine_class,
        has_agi_keywords=has_agi_keywords,
        in_archive=in_archive,
        in_candidate_labs=in_candidate_labs,
        last_modified_days=last_modified_days,
        score=score,
        category=category,
        integration_suggestion=integration_suggestion
    )


def calculate_score(
    loc: int, classes: int, functions: int,
    has_module_doc: bool, class_doc_ratio: float, func_doc_ratio: float, has_nearby_readme: bool,
    imports_core: bool, imports_matriz: bool, imports_serve: bool,
    has_engine_class: bool, has_agi_keywords: bool,
    in_archive: bool, in_candidate_labs: bool, last_modified_days: int
) -> float:
    """Calculate module score (0-100) based on multiple factors."""
    score = 0.0

    # Complexity (0-30 pts)
    if loc < 100:
        score += 0
    elif loc < 500:
        score += 10
    elif loc < 1000:
        score += 20
    else:
        score += 30

    if classes == 0:
        score += 0
    elif classes <= 3:
        score += 5
    else:
        score += 10

    if functions < 5:
        score += 0
    elif functions < 15:
        score += 5
    else:
        score += 10

    # Documentation (0-20 pts)
    score += 5 if has_module_doc else 0
    score += 5 * class_doc_ratio
    score += 5 * func_doc_ratio
    score += 5 if has_nearby_readme else 0

    # Architecture Compatibility (0-25 pts)
    score += 10 if imports_core else 0
    score += 10 if imports_matriz else 0
    score += 5 if imports_serve else 0

    # AGI/Visionary Value (0-25 pts)
    score += 5 if has_engine_class else 0
    score += 5 if has_agi_keywords else 0

    # Bonus for self-improvement/healing patterns
    score += 5 if 'self_improvement' in str(has_agi_keywords) or 'self_healing' in str(has_agi_keywords) else 0

    # Bonus points
    score += 5 if in_candidate_labs else 0
    score += 5 if last_modified_days < 180 else 0  # Modified in last 6 months

    return min(score, 100)  # Cap at 100


def generate_integration_suggestion(
    module_name: str, rel_path: Path, has_engine_class: bool,
    imports_core: bool, imports_matriz: bool,
    in_archive: bool, in_candidate_labs: bool
) -> str:
    """Generate actionable integration suggestion."""
    suggestions = []

    if 'identity' in module_name.lower():
        suggestions.append("Wire into serve.identity_api for authentication/namespace isolation")
    elif 'bio' in module_name.lower() and 'energy' in module_name.lower():
        suggestions.append("Create bio.energy module for ATP/energy modeling")
    elif 'memory' in module_name.lower() and 'dream' in module_name.lower():
        suggestions.append("Revive as memory.dream_trace for consciousness tracing")
    elif 'self_improvement' in module_name.lower() or 'self_healing' in module_name.lower():
        suggestions.append("Wire into matriz.self_evolution for AGI capabilities")
    elif has_engine_class:
        suggestions.append("Integrate as standalone engine component")
    elif imports_matriz:
        suggestions.append("Wire into MATRIZ cognitive pipeline")
    elif imports_core:
        suggestions.append("Promote to core module or wire into existing core system")
    elif in_archive:
        suggestions.append("Revive and modernize for current architecture")
    elif in_candidate_labs:
        suggestions.append("Test thoroughly, then promote to production lane")
    else:
        suggestions.append("Evaluate for integration or mark for deletion")

    return suggestions[0] if suggestions else "Needs evaluation"


def generate_outputs(modules: list[ModuleMetrics], output_dir: Path):
    """Generate all output formats."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. CSV: Full scored table
    csv_path = output_dir / 'isolated_modules_scored.csv'
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'module', 'score', 'category', 'loc', 'classes', 'functions',
            'imports_core', 'imports_matriz', 'archive', 'candidate_labs',
            'last_modified_days', 'integration_suggestion'
        ])
        writer.writeheader()
        for m in sorted(modules, key=lambda x: x.score, reverse=True):
            writer.writerow({
                'module': m.module_name,
                'score': f'{m.score:.1f}',
                'category': m.category,
                'loc': m.loc,
                'classes': m.classes,
                'functions': m.functions,
                'imports_core': 'yes' if m.imports_core else 'no',
                'imports_matriz': 'yes' if m.imports_matriz else 'no',
                'archive': 'yes' if m.in_archive else 'no',
                'candidate_labs': 'yes' if m.in_candidate_labs else 'no',
                'last_modified_days': m.last_modified_days,
                'integration_suggestion': m.integration_suggestion
            })

    # 2. Top 20 Markdown
    top20_path = output_dir / 'hidden_gems_top20.md'
    top20 = sorted(modules, key=lambda x: x.score, reverse=True)[:20]

    with open(top20_path, 'w') as f:
        f.write("# Top 20 Hidden Gems - Integration Roadmap\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Total modules analyzed**: {len(modules)}\n\n")
        f.write("---\n\n")

        for i, m in enumerate(top20, 1):
            f.write(f"## {i}. {m.path} (Score: {m.score:.1f})\n\n")
            f.write(f"**Category**: {m.category.replace('_', ' ').title()}\n\n")
            f.write(f"**Why**: {m.loc} LOC, {m.classes} classes, {m.functions} functions")
            if m.imports_core:
                f.write(", imports core")
            if m.imports_matriz:
                f.write(", imports MATRIZ")
            if m.has_agi_keywords:
                f.write(", AGI/visionary keywords")
            f.write("\n\n")
            f.write(f"**Integration**: {m.integration_suggestion}\n\n")

            deps = []
            if m.imports_core:
                deps.append("core.*")
            if m.imports_matriz:
                deps.append("matriz.*")
            if m.imports_serve:
                deps.append("serve.*")
            if deps:
                f.write(f"**Dependencies**: {', '.join(deps)}\n\n")

            # Estimate effort
            if m.loc < 200:
                effort = "1-2 hours"
            elif m.loc < 500:
                effort = "2-4 hours"
            elif m.loc < 1000:
                effort = "4-8 hours"
            else:
                effort = "1-2 days"
            f.write(f"**Effort**: {effort}\n\n")
            f.write("---\n\n")

    # 3. Dependency graph JSON
    graph_path = output_dir / 'dependency_graph.json'
    nodes = []
    edges = []

    for m in modules:
        nodes.append({
            'id': m.module_name,
            'score': m.score,
            'category': m.category,
            'loc': m.loc
        })

        # Add edges for imports
        if m.imports_core:
            edges.append({'source': m.module_name, 'target': 'core', 'type': 'imports'})
        if m.imports_matriz:
            edges.append({'source': m.module_name, 'target': 'matriz', 'type': 'imports'})
        if m.imports_serve:
            edges.append({'source': m.module_name, 'target': 'serve', 'type': 'imports'})

    with open(graph_path, 'w') as f:
        json.dump({'nodes': nodes, 'edges': edges}, f, indent=2)

    # 4. Categorized Markdown
    cat_path = output_dir / 'categorized_modules.md'
    by_category = defaultdict(list)
    for m in modules:
        by_category[m.category].append(m)

    with open(cat_path, 'w') as f:
        f.write("# Categorized Isolated Modules\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Total modules**: {len(modules)}\n\n")

        for cat_name, cat_desc in [
            ('hidden_gem', 'Hidden Gems (Score 70-100) - Immediate integration candidates'),
            ('experimental', 'Experimental (Score 50-69) - Needs testing, potential value'),
            ('archival', 'Archival (Score 30-49) - Revive with effort'),
            ('dead_code', 'Dead Code (Score 0-29) - Delete candidates'),
        ]:
            mods = sorted(by_category.get(cat_name, []), key=lambda x: x.score, reverse=True)
            f.write(f"## {cat_desc}\n\n")
            f.write(f"**Count**: {len(mods)} modules\n\n")

            for m in mods[:50]:  # Limit to 50 per category
                f.write(f"- `{m.path}` (Score: {m.score:.1f}) - {m.integration_suggestion}\n")

            if len(mods) > 50:
                f.write(f"\n*... and {len(mods) - 50} more*\n")
            f.write("\n")

    # 5. Integration Roadmap
    roadmap_path = output_dir / 'integration_roadmap.md'
    gems = [m for m in modules if m.category == 'hidden_gem']

    # Group by domain
    identity_gems = [m for m in gems if 'identity' in m.module_name.lower() or 'auth' in m.module_name.lower()]
    bio_gems = [m for m in gems if 'bio' in m.module_name.lower()]
    memory_gems = [m for m in gems if 'memory' in m.module_name.lower()]
    agi_gems = [m for m in gems if 'self_improvement' in m.module_name.lower() or 'self_healing' in m.module_name.lower()]
    other_gems = [m for m in gems if m not in identity_gems + bio_gems + memory_gems + agi_gems]

    with open(roadmap_path, 'w') as f:
        f.write("# Integration Roadmap - Priority Order\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Total hidden gems**: {len(gems)}\n\n")
        f.write("---\n\n")

        phase = 1
        for domain_name, domain_gems in [
            ('Identity & Auth', identity_gems),
            ('Bio-Inspired Systems', bio_gems),
            ('Memory & Consciousness', memory_gems),
            ('AGI Capabilities', agi_gems),
            ('Core Systems', other_gems),
        ]:
            if domain_gems:
                f.write(f"## Phase {phase}: {domain_name}\n\n")
                for m in sorted(domain_gems, key=lambda x: x.score, reverse=True):
                    f.write(f"- [ ] `{m.path}` → {m.integration_suggestion}\n")
                f.write("\n")
                phase += 1

    print("\n✅ Generated 5 output files:")
    print(f"   1. {csv_path} - Full scored table")
    print(f"   2. {top20_path} - Top 20 with integration suggestions")
    print(f"   3. {graph_path} - Dependency graph JSON")
    print(f"   4. {cat_path} - Categorized modules")
    print(f"   5. {roadmap_path} - Integration roadmap")


def main():
    root = Path(__file__).parent.parent
    output_dir = root / 'docs' / 'audits'

    print("🔍 Analyzing LUKHAS isolated modules for hidden gems...")
    print(f"📁 Scanning: {root}")
    print(f"📊 Output directory: {output_dir}\n")

    # Find all Python files
    python_files = [
        p for p in root.rglob('*.py')
        if not should_skip(p) and should_include(p, root) and p.name != 'setup.py'
    ]

    print(f"Found {len(python_files)} Python files in LUKHAS code\n")

    # Analyze modules
    modules = []
    for i, py_file in enumerate(python_files, 1):
        if i % 100 == 0:
            print(f"  Analyzed {i}/{len(python_files)} files...")

        metrics = analyze_module(py_file, root)
        if metrics:
            modules.append(metrics)

    print(f"\n✅ Analyzed {len(modules)} modules successfully\n")

    # Generate outputs
    generate_outputs(modules, output_dir)

    # Summary statistics
    by_category = defaultdict(int)
    for m in modules:
        by_category[m.category] += 1

    print("\n📊 Summary Statistics:")
    print(f"   Hidden Gems (70-100): {by_category['hidden_gem']}")
    print(f"   Experimental (50-69): {by_category['experimental']}")
    print(f"   Archival (30-49): {by_category['archival']}")
    print(f"   Dead Code (0-29): {by_category['dead_code']}")

    top_gem = max(modules, key=lambda x: x.score)
    print(f"\n🏆 Top Hidden Gem: {top_gem.path} (Score: {top_gem.score:.1f})")
    print(f"   {top_gem.integration_suggestion}")

    print("\n📖 See docs/audits/hidden_gems_top20.md for full report")


if __name__ == '__main__':
    main()
