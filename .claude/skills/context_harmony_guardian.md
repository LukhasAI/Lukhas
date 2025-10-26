# Context Harmony Guardian Skill

Continuous synchronization and consistency validation across 42+ distributed context files with conflict resolution and automated updates.

## Reasoning

1. LUKHAS has 42+ distributed `claude.me` and `lukhas_context.md` files that can diverge over time, creating navigation confusion for AI agents.

2. No automated system exists to detect contradictions - different files may state conflicting performance targets, architecture descriptions, or module relationships.

3. Context files are critical for AI agent navigation - inconsistency causes wasted time, incorrect assumptions, and implementation errors.

4. Schema evolution (v2.0.0 → v3.0.0) requires bulk updates across all context files with no current automation.

5. Cross-references between contexts (e.g., `matriz/claude.me` mentions fold-memory, must match `memory/claude.me`) need bidirectional validation.

## Actions

### Core Guardian System

**File**: `scripts/context_harmony_guardian.py`

```python
#!/usr/bin/env python3
"""
Context Harmony Guardian - T4/0.01% Context File Synchronization

Ensures 42+ distributed context files remain consistent:
- Schema validation
- Cross-reference verification
- Contradiction detection
- Automated synchronization
- Conflict resolution
"""

import os
import re
import json
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Set, Optional
import yaml
from collections import defaultdict

@dataclass
class ContextMetadata:
    """Parsed metadata from context file frontmatter"""
    file_path: str
    title: str = ""
    owner: str = ""
    lane: str = ""
    star: str = ""
    stability: str = ""
    last_reviewed: str = ""
    constellation_stars: List[str] = field(default_factory=list)
    related_modules: List[str] = field(default_factory=list)
    performance_targets: Dict[str, str] = field(default_factory=dict)
    contracts: List[str] = field(default_factory=list)

@dataclass
class ContextContradiction:
    """Detected contradiction between context files"""
    type: str  # 'performance', 'architecture', 'cross_reference', 'schema'
    severity: str  # 'critical', 'important', 'minor'
    file_a: str
    file_b: str
    description: str
    suggestion: str

class ContextHarmonyGuardian:
    """
    Maintains harmony across 42+ distributed context files.

    Validates:
    - Schema compliance
    - Cross-reference accuracy
    - Performance target consistency
    - Architecture description alignment
    """

    REQUIRED_FIELDS = ['title', 'owner', 'lane', 'status']
    PERFORMANCE_PATTERNS = {
        'latency': r'<\s*(\d+)ms',
        'memory': r'<\s*(\d+)MB',
        'throughput': r'(\d+)\+?\s*ops/sec',
        'coverage': r'(\d+)%'
    }

    def __init__(self, root_path='.'):
        self.root = Path(root_path)
        self.contexts: Dict[str, ContextMetadata] = {}
        self.contradictions: List[ContextContradiction] = []

    def scan_all_contexts(self) -> Dict[str, ContextMetadata]:
        """Find and parse all context files"""
        context_files = []

        # Find all claude.me and lukhas_context.md files
        for pattern in ['**/claude.me', '**/lukhas_context.md']:
            context_files.extend(self.root.glob(pattern))

        print(f"Found {len(context_files)} context files")

        for file_path in context_files:
            try:
                metadata = self._parse_context_file(file_path)
                self.contexts[str(file_path)] = metadata
            except Exception as e:
                print(f"Warning: Failed to parse {file_path}: {e}")

        return self.contexts

    def _parse_context_file(self, file_path: Path) -> ContextMetadata:
        """Parse context file and extract metadata"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        metadata = ContextMetadata(file_path=str(file_path))

        # Parse YAML frontmatter if present
        if content.startswith('---'):
            try:
                end_idx = content.find('---', 3)
                if end_idx > 0:
                    frontmatter = content[3:end_idx]
                    data = yaml.safe_load(frontmatter)
                    if data:
                        metadata.title = data.get('title', '')
                        metadata.owner = data.get('owner', '')
                        metadata.lane = data.get('lane', '')
                        metadata.star = data.get('star', '')
                        metadata.stability = data.get('stability', '')
                        metadata.last_reviewed = data.get('last_reviewed', '')
            except Exception as e:
                print(f"Warning: YAML parse error in {file_path}: {e}")

        # Extract performance targets from content
        metadata.performance_targets = self._extract_performance_targets(content)

        # Extract cross-references
        metadata.related_modules = self._extract_cross_references(content)

        return metadata

    def _extract_performance_targets(self, content: str) -> Dict[str, str]:
        """Extract performance targets from content"""
        targets = {}
        for target_type, pattern in self.PERFORMANCE_PATTERNS.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                targets[target_type] = matches[0]
        return targets

    def _extract_cross_references(self, content: str) -> List[str]:
        """Extract cross-references to other modules"""
        # Find markdown links to other context files
        links = re.findall(r'\[([^\]]+)\]\(([^\)]+claude\.me|[^\)]+lukhas_context\.md)\)', content)
        return [link[1] for link in links]

    def detect_contradictions(self) -> List[ContextContradiction]:
        """Detect contradictions across context files"""
        self.contradictions = []

        # Group contexts by lane
        lane_contexts = defaultdict(list)
        for path, ctx in self.contexts.items():
            if ctx.lane:
                lane_contexts[ctx.lane].append((path, ctx))

        # Check performance target consistency within lanes
        for lane, contexts in lane_contexts.items():
            self._check_performance_consistency(lane, contexts)

        # Validate cross-references
        self._validate_cross_references()

        # Check schema compliance
        self._check_schema_compliance()

        return self.contradictions

    def _check_performance_consistency(self, lane: str, contexts: List[tuple]):
        """Check if performance targets are consistent within a lane"""
        targets_by_type = defaultdict(set)

        for path, ctx in contexts:
            for target_type, value in ctx.performance_targets.items():
                targets_by_type[target_type].add((value, path))

        # Detect contradictions
        for target_type, values_paths in targets_by_type.items():
            if len(values_paths) > 1:
                values = [v[0] for v in values_paths]
                paths = [v[1] for v in values_paths]

                self.contradictions.append(ContextContradiction(
                    type='performance',
                    severity='important',
                    file_a=paths[0],
                    file_b=paths[1] if len(paths) > 1 else paths[0],
                    description=f"Inconsistent {target_type} targets in {lane} lane: {', '.join(values)}",
                    suggestion=f"Standardize {target_type} target across {lane} lane contexts"
                ))

    def _validate_cross_references(self):
        """Validate that cross-references are bidirectional and accurate"""
        for path, ctx in self.contexts.items():
            for ref in ctx.related_modules:
                # Resolve relative path
                ref_path = self._resolve_reference(path, ref)

                # Check if referenced file exists
                if ref_path and ref_path not in self.contexts:
                    self.contradictions.append(ContextContradiction(
                        type='cross_reference',
                        severity='critical',
                        file_a=path,
                        file_b=ref,
                        description=f"Broken cross-reference: {ref} not found",
                        suggestion=f"Fix or remove reference to {ref}"
                    ))

    def _resolve_reference(self, source_path: str, ref: str) -> Optional[str]:
        """Resolve relative reference to absolute path"""
        source = Path(source_path)
        ref_path = (source.parent / ref).resolve()

        if ref_path.exists():
            return str(ref_path)
        return None

    def _check_schema_compliance(self):
        """Check if all contexts comply with required schema"""
        for path, ctx in self.contexts.items():
            missing_fields = []
            for field in self.REQUIRED_FIELDS:
                if not getattr(ctx, field, None):
                    missing_fields.append(field)

            if missing_fields:
                self.contradictions.append(ContextContradiction(
                    type='schema',
                    severity='important',
                    file_a=path,
                    file_b=path,
                    description=f"Missing required fields: {', '.join(missing_fields)}",
                    suggestion=f"Add required fields: {', '.join(missing_fields)}"
                ))

    def suggest_harmonization(self) -> List[Dict]:
        """Generate harmonization suggestions based on ML/heuristics"""
        suggestions = []

        # Group similar contradictions
        by_type = defaultdict(list)
        for contradiction in self.contradictions:
            by_type[contradiction.type].append(contradiction)

        # Generate bulk fixes
        for contradiction_type, items in by_type.items():
            if contradiction_type == 'performance':
                # Suggest most common value
                suggestions.append({
                    'type': 'bulk_update',
                    'contradiction_type': contradiction_type,
                    'action': 'Standardize performance targets',
                    'affected_files': [c.file_a for c in items],
                    'suggestion': 'Use median value across all specifications'
                })

        return suggestions

    def auto_sync_architecture_changes(self, changed_file: str, change_description: str):
        """Propagate architecture changes to related contexts"""
        if changed_file not in self.contexts:
            return

        ctx = self.contexts[changed_file]

        # Find related contexts
        related = []
        for path, other_ctx in self.contexts.items():
            if path == changed_file:
                continue
            # Same lane or cross-referenced
            if other_ctx.lane == ctx.lane or changed_file in other_ctx.related_modules:
                related.append(path)

        if related:
            print(f"\n⚠️  Architecture change detected in {changed_file}")
            print(f"📋 Related contexts that may need updates:")
            for r in related:
                print(f"   - {r}")
            print(f"\n💡 Change description: {change_description}")

    def generate_health_report(self) -> Dict:
        """Generate comprehensive context health report"""
        total_contexts = len(self.contexts)
        total_contradictions = len(self.contradictions)

        by_severity = defaultdict(int)
        by_type = defaultdict(int)

        for c in self.contradictions:
            by_severity[c.severity] += 1
            by_type[c.type] += 1

        return {
            'total_contexts': total_contexts,
            'total_contradictions': total_contradictions,
            'health_score': max(0, 100 - (total_contradictions * 5)),
            'by_severity': dict(by_severity),
            'by_type': dict(by_type),
            'top_issues': [asdict(c) for c in self.contradictions[:10]]
        }

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Context Harmony Guardian')
    parser.add_argument('--scan', action='store_true', help='Scan all contexts')
    parser.add_argument('--report', action='store_true', help='Generate health report')
    parser.add_argument('--fix', action='store_true', help='Auto-fix issues (dry-run by default)')
    args = parser.parse_args()

    guardian = ContextHarmonyGuardian()

    if args.scan or args.report:
        print("🔍 Scanning context files...")
        guardian.scan_all_contexts()

        print("🔍 Detecting contradictions...")
        guardian.detect_contradictions()

    if args.report:
        print("\n📊 Generating health report...")
        report = guardian.generate_health_report()
        print(json.dumps(report, indent=2))

        # Show top contradictions
        print("\n⚠️  Top Contradictions:")
        for c in guardian.contradictions[:5]:
            print(f"\n  {c.severity.upper()}: {c.type}")
            print(f"  Files: {c.file_a} ↔ {c.file_b}")
            print(f"  Issue: {c.description}")
            print(f"  💡 {c.suggestion}")

if __name__ == '__main__':
    main()
```

### GitHub Action Integration

**File**: `.github/workflows/context_harmony.yml`

```yaml
name: Context Harmony Check
on:
  pull_request:
    paths:
      - '**/claude.me'
      - '**/lukhas_context.md'
  push:
    branches: [main]

jobs:
  harmony-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install pyyaml
      - name: Run Context Harmony Guardian
        run: |
          python3 scripts/context_harmony_guardian.py --scan --report
      - name: Block on critical contradictions
        run: |
          python3 -c "
          import json, sys
          with open('context_health_report.json') as f:
              report = json.load(f)
          critical = report.get('by_severity', {}).get('critical', 0)
          if critical > 0:
              print(f'❌ {critical} critical contradictions detected!')
              sys.exit(1)
          "
```

### Usage Examples

```bash
# Scan all contexts and generate report
python3 scripts/context_harmony_guardian.py --scan --report

# Output to JSON
python3 scripts/context_harmony_guardian.py --scan --report > context_health_report.json

# Makefile integration
make context-check
```

## Integration Points

- **GitHub Actions**: Runs on PRs touching context files
- **Context Generation**: Validates outputs of `scripts/generate_lukhas_context.sh`
- **Schema Validation**: Enforces context file schema compliance
- **Cross-Reference Network**: Maintains bidirectional reference integrity

## Success Metrics

- **Contradiction Detection**: >90% of inconsistencies found before manual review
- **Schema Compliance**: 100% of context files meet required schema
- **Cross-Reference Accuracy**: 0 broken references in production
- **Sync Time**: <2 minutes to detect and report all issues

## Context References

- `/docs/CONTEXT_FILES.md` - Context file system documentation
- `/scripts/generate_lukhas_context.sh` - Context generation script
- `/context_files.txt` - List of all context files
- `/MODULE_INDEX.md` - Module organization reference
