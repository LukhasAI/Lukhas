#!/usr/bin/env python3
"""
Analyze duplicate files from previous audit and generate actionable recommendations.
"""
import json
from pathlib import Path
from typing import Any, Dict, List


def load_duplicate_report(report_path: str) -> Dict[str, Any]:
    """Load the duplicate report JSON."""
    with open(report_path, 'r') as f:
        return json.load(f)

def categorize_duplicates(duplicates: List[Dict]) -> Dict[str, List[Dict]]:
    """Categorize duplicates by type and importance."""
    categories = {
        'init_files': [],           # __init__.py files (expected)
        'test_files': [],           # Test files
        'config_files': [],         # Configuration files
        'documentation': [],        # .md, .txt files
        'python_code': [],          # .py files (non-test, non-init)
        'archive_candidates': [],   # Files in archive/, old/, backup/ dirs
        'other': []
    }

    for dup_group in duplicates:
        files = dup_group.get('files', [])
        if not files:
            continue

        first_file = files[0].lower()

        # Categorize by file path/name
        if '__init__.py' in first_file:
            categories['init_files'].append(dup_group)
        elif any(x in first_file for x in ['/test_', '/tests/', '_test.py']):
            categories['test_files'].append(dup_group)
        elif any(x in first_file for x in ['.json', '.yaml', '.yml', '.toml', '.ini', '.env']):
            categories['config_files'].append(dup_group)
        elif any(x in first_file for x in ['.md', '.txt', '.rst']):
            categories['documentation'].append(dup_group)
        elif any(x in first_file for x in ['/archive/', '/old/', '/backup/', '/.venv/', '_old', '_backup']):
            categories['archive_candidates'].append(dup_group)
        elif first_file.endswith('.py'):
            categories['python_code'].append(dup_group)
        else:
            categories['other'].append(dup_group)

    return categories

def calculate_space_impact(dup_group: Dict) -> int:
    """Calculate wasted space for a duplicate group."""
    size = dup_group.get('size_bytes', 0)
    count = len(dup_group.get('files', []))
    # Wasted space = size * (count - 1), since we keep one
    return size * (count - 1)

def prioritize_which_to_keep(files: List[str]) -> tuple:
    """Determine which file to keep and which to archive."""
    # Priority rules:
    # 1. Keep production lane (lukhas/) over candidate/
    # 2. Keep core/ over matriz/
    # 3. Keep files not in archive/ or backup/ dirs
    # 4. Keep shorter paths (typically main versions)
    # 5. Keep files with more recent indicators in path

    scored_files = []
    for file_path in files:
        score = 0
        lower_path = file_path.lower()

        # Positive scores (keep)
        if '/lukhas/' in lower_path and '/candidate/' not in lower_path:
            score += 100
        if '/core/' in lower_path:
            score += 50
        if '/tests/' in lower_path:
            score += 30
        if '/docs/' in lower_path:
            score += 20

        # Negative scores (archive)
        if any(x in lower_path for x in ['/archive/', '/quarantine/', '/products/']):
            score -= 1000
        if any(x in lower_path for x in ['_old', '_backup', '_copy', '_deprecated', '_legacy']):
            score -= 500
        if '/.venv/' in lower_path or '/__pycache__/' in lower_path:
            score -= 2000

        # Shorter paths preferred (typically main versions)
        path_length_penalty = len(file_path.split('/'))
        score -= path_length_penalty

        scored_files.append((score, file_path))

    # Sort by score descending
    scored_files.sort(reverse=True, key=lambda x: x[0])

    keep_file = scored_files[0][1]
    archive_files = [f[1] for f in scored_files[1:]]

    return keep_file, archive_files

def generate_recommendations(categories: Dict[str, List[Dict]]) -> Dict[str, Any]:
    """Generate actionable recommendations for each category."""
    recommendations = {
        'summary': {
            'total_duplicate_groups': 0,
            'total_files': 0,
            'total_wasted_space_mb': 0.0,
            'by_category': {}
        },
        'actions': []
    }

    total_wasted_bytes = 0
    total_groups = 0
    total_files = 0

    for category_name, dup_groups in categories.items():
        if not dup_groups:
            continue

        category_wasted = 0
        category_file_count = 0

        for dup_group in dup_groups:
            files = dup_group.get('files', [])
            wasted = calculate_space_impact(dup_group)

            category_wasted += wasted
            category_file_count += len(files)
            total_wasted_bytes += wasted
            total_groups += 1
            total_files += len(files)

            # Determine which to keep and which to archive
            keep_file, archive_files = prioritize_which_to_keep(files)

            action = {
                'category': category_name,
                'hash': dup_group.get('hash', 'unknown')[:16],
                'size_bytes': dup_group.get('size_bytes', 0),
                'file_count': len(files),
                'wasted_bytes': wasted,
                'keep': keep_file,
                'archive': archive_files,
                'recommendation': determine_action(category_name, files)
            }

            recommendations['actions'].append(action)

        recommendations['summary']['by_category'][category_name] = {
            'groups': len(dup_groups),
            'files': category_file_count,
            'wasted_mb': round(category_wasted / 1024 / 1024, 2)
        }

    recommendations['summary']['total_duplicate_groups'] = total_groups
    recommendations['summary']['total_files'] = total_files
    recommendations['summary']['total_wasted_space_mb'] = round(total_wasted_bytes / 1024 / 1024, 2)

    return recommendations

def determine_action(category: str, files: List[str]) -> str:
    """Determine recommended action for duplicate group."""
    if category == 'init_files':
        return "KEEP_ALL - Standard Python package structure"
    elif category == 'archive_candidates':
        return "ARCHIVE - Already in archive/backup directories"
    elif any('.venv' in f or '__pycache__' in f for f in files):
        return "IGNORE - Build artifacts, not in git"
    elif len(files) == 2:
        return "REVIEW - Simple duplicate, safe to consolidate"
    elif len(files) > 5:
        return "INVESTIGATE - Many copies, may indicate systematic issue"
    else:
        return "CONSOLIDATE - Keep primary, archive others"

def main():
    """Main analysis function."""
    base_dir = Path(__file__).parent.parent.parent
    report_path = base_dir / 'tools' / 'analysis' / 'duplicate_report.json'
    output_dir = Path(__file__).parent.parent / 'reports'

    print(f"Loading duplicate report from: {report_path}")

    if not report_path.exists():
        print(f"ERROR: Duplicate report not found at {report_path}")
        return 1

    # Load the report
    report = load_duplicate_report(report_path)
    duplicates = report.get('duplicates', [])

    print(f"Found {len(duplicates)} duplicate groups")

    # Categorize duplicates
    print("\nCategorizing duplicates...")
    categories = categorize_duplicates(duplicates)

    for cat_name, dup_list in categories.items():
        if dup_list:
            print(f"  {cat_name}: {len(dup_list)} groups")

    # Generate recommendations
    print("\nGenerating recommendations...")
    recommendations = generate_recommendations(categories)

    # Save recommendations
    output_file = output_dir / 'duplicate_consolidation_plan.json'
    with open(output_file, 'w') as f:
        json.dump(recommendations, f, indent=2)

    print(f"\nRecommendations saved to: {output_file}")
    print("\nSummary:")
    print(f"  Total duplicate groups: {recommendations['summary']['total_duplicate_groups']}")
    print(f"  Total duplicate files: {recommendations['summary']['total_files']}")
    print(f"  Total wasted space: {recommendations['summary']['total_wasted_space_mb']:.2f} MB")
    print("\nBy category:")
    for cat_name, stats in recommendations['summary']['by_category'].items():
        print(f"  {cat_name}: {stats['groups']} groups, {stats['files']} files, {stats['wasted_mb']:.2f} MB")

    return 0

if __name__ == '__main__':
    exit(main())
