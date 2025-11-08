#!/usr/bin/env python3
"""
Analyze file-level duplicates from Nov 3 audit and generate consolidation plan.
"""
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple


def parse_duplicate_report(report_path: str) -> List[Dict]:
    """Parse the SHA256 duplicate report."""
    with open(report_path) as f:
        content = f.read()

    duplicate_groups = []
    current_group = None

    for line in content.split('\n'):
        line = line.strip()

        # Start of new hash group
        if line.startswith('Hash:'):
            if current_group:
                duplicate_groups.append(current_group)
            current_group = {
                'hash': line.split(':')[1].strip(),
                'count': 0,
                'size_bytes': 0,  # Will be determined later
                'files': []
            }

        # Count line
        elif line.startswith('Count:') and current_group:
            count_match = re.search(r'(\d+)\s+files', line)
            if count_match:
                current_group['count'] = int(count_match.group(1))

        # File line
        elif line.startswith('- ./') and current_group:
            file_path = line[3:].strip()  # Remove "- ./"
            current_group['files'].append(file_path)

    # Add last group
    if current_group:
        duplicate_groups.append(current_group)

    return duplicate_groups

def categorize_duplicate(files: List[str]) -> str:
    """Categorize a duplicate group by file type and location."""
    if not files:
        return 'unknown'

    first_file = files[0].lower()

    if '__init__.py' in first_file:
        return 'init_files'
    elif any(x in first_file for x in ['/test_', '/tests/', '_test.py']):
        return 'test_files'
    elif any(x in first_file for x in ['.json', '.yaml', '.yml', '.toml', '.ini']):
        return 'config_files'
    elif any(x in first_file for x in ['.md', '.txt', '.rst']):
        return 'documentation'
    elif any(x in first_file for x in ['/archive/', '/quarantine/', '/products/', '/.venv/']):
        return 'excluded_dirs'
    elif any(x in first_file for x in ['_old', '_backup', '_copy', '_deprecated', '_legacy']):
        return 'legacy_markers'
    elif first_file.endswith('.py'):
        return 'python_code'
    else:
        return 'other'

def prioritize_files(files: List[str]) -> Tuple[str, List[str]]:
    """Determine which file to keep and which to archive."""
    scored_files = []

    for file_path in files:
        score = 0
        lower_path = file_path.lower()

        # Production lane priority
        if '/lukhas/' in lower_path and '/candidate/' not in lower_path:
            score += 100
        if '/core/' in lower_path:
            score += 50
        if '/matriz/' in lower_path:
            score += 40

        # Negative scores (archive candidates)
        if any(x in lower_path for x in ['/archive/', '/quarantine/', '/products/']):
            score -= 1000
        if any(x in lower_path for x in ['_old', '_backup', '_copy', '_deprecated', '_legacy']):
            score -= 500
        if '/.venv/' in lower_path or '/__pycache__/' in lower_path:
            score -= 2000
        if '/labs/' in lower_path:
            score -= 10  # Labs are experimental

        # Shorter paths preferred
        score -= len(file_path.split('/'))

        scored_files.append((score, file_path))

    scored_files.sort(reverse=True, key=lambda x: x[0])

    keep_file = scored_files[0][1]
    archive_files = [f[1] for f in scored_files[1:]]

    return keep_file, archive_files

def determine_action(category: str, file_count: int, files: List[str]) -> str:
    """Determine recommended action."""
    if category == 'init_files':
        return 'KEEP_ALL'
    elif category == 'excluded_dirs':
        return 'IGNORE'
    elif category == 'legacy_markers':
        return 'ARCHIVE'
    elif file_count == 2:
        return 'REVIEW_SIMPLE'
    elif file_count > 10:
        return 'INVESTIGATE_SYSTEMATIC'
    elif any('.venv' in f or '__pycache__' in f for f in files):
        return 'IGNORE'
    else:
        return 'CONSOLIDATE'

def estimate_file_size(file_path: str) -> int:
    """Estimate file size based on category."""
    # Rough estimates for common file types
    if '__init__.py' in file_path:
        return 50  # Most __init__.py are small or empty
    elif 'test_' in file_path or '/tests/' in file_path:
        return 2048  # Average test file ~2KB
    elif file_path.endswith('.md'):
        return 4096  # Average doc ~4KB
    elif file_path.endswith('.py'):
        return 3072  # Average Python file ~3KB
    elif file_path.endswith(('.json', '.yaml', '.yml')):
        return 1024  # Average config ~1KB
    else:
        return 1024  # Default 1KB

def main():
    """Main analysis function."""
    base_dir = Path(__file__).parent.parent.parent
    report_path = base_dir / 'release_artifacts' / 'repo_audit_v2' / 'hygiene' / 'duplicate_files_sha256.txt'
    output_dir = Path(__file__).parent.parent / 'reports'

    print(f"Loading duplicate report from: {report_path}")

    if not report_path.exists():
        print(f"ERROR: Report not found at {report_path}")
        return 1

    # Parse report
    duplicate_groups = parse_duplicate_report(str(report_path))
    print(f"Found {len(duplicate_groups)} duplicate groups")

    # Analyze and categorize
    categorized = {}
    total_files = 0
    total_wasted_bytes = 0

    actions = []

    for group in duplicate_groups:
        files = group['files']
        category = categorize_duplicate(files)

        if category not in categorized:
            categorized[category] = {'groups': 0, 'files': 0, 'wasted_bytes': 0}

        # Estimate size
        estimated_size = estimate_file_size(files[0] if files else '')
        group['size_bytes'] = estimated_size
        wasted = estimated_size * (len(files) - 1)

        categorized[category]['groups'] += 1
        categorized[category]['files'] += len(files)
        categorized[category]['wasted_bytes'] += wasted

        total_files += len(files)
        total_wasted_bytes += wasted

        # Determine keep/archive
        keep_file, archive_files = prioritize_files(files)
        action_type = determine_action(category, len(files), files)

        action = {
            'hash': group['hash'][:16],
            'category': category,
            'action': action_type,
            'file_count': len(files),
            'estimated_size_bytes': estimated_size,
            'wasted_bytes': wasted,
            'keep': keep_file,
            'archive': archive_files[:5],  # First 5 for brevity
            'archive_count': len(archive_files)
        }

        actions.append(action)

    # Generate report
    report = {
        'summary': {
            'total_duplicate_groups': len(duplicate_groups),
            'total_duplicate_files': total_files,
            'total_wasted_space_mb': round(total_wasted_bytes / 1024 / 1024, 2),
            'by_category': {}
        },
        'actions': actions
    }

    for category, stats in categorized.items():
        report['summary']['by_category'][category] = {
            'groups': stats['groups'],
            'files': stats['files'],
            'wasted_mb': round(stats['wasted_bytes'] / 1024 / 1024, 2)
        }

    # Save report
    output_file = output_dir / 'duplicate_consolidation_plan.json'
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\nConsolidation plan saved to: {output_file}")
    print("\nSummary:")
    print(f"  Total duplicate groups: {report['summary']['total_duplicate_groups']}")
    print(f"  Total duplicate files: {report['summary']['total_duplicate_files']}")
    print(f"  Estimated wasted space: {report['summary']['total_wasted_space_mb']:.2f} MB")
    print("\nBy category:")
    for category, stats in report['summary']['by_category'].items():
        print(f"  {category}: {stats['groups']} groups, {stats['files']} files, {stats['wasted_mb']:.2f} MB")

    # Action summary
    action_counts = {}
    for action in actions:
        action_type = action['action']
        action_counts[action_type] = action_counts.get(action_type, 0) + 1

    print("\nRecommended actions:")
    for action_type, count in sorted(action_counts.items()):
        print(f"  {action_type}: {count} groups")

    return 0

if __name__ == '__main__':
    exit(main())
