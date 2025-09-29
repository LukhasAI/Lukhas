#!/usr/bin/env python3
"""
MATRIZ Audit Aggregator

Merges all audit data sources (inventory, validation, imports, lanes) into
comprehensive audit reports and generates suggested move operations.
"""

import json
import pathlib
from typing import List, Dict, Any
import argparse
import sys
from datetime import datetime


def load_artifact(file_path: pathlib.Path, description: str) -> Dict[str, Any]:
    """Load an artifact file with error handling."""
    try:
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        else:
            print(f"Warning: {description} not found at {file_path}")
            return {}
    except json.JSONDecodeError as e:
        print(f"Warning: Failed to parse {description}: {e}")
        return {}


def merge_module_data(inventory: Dict[str, Any], validation: Dict[str, Any],
                     imports: Dict[str, Any], lanes: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Merge data from all sources for each module."""
    modules = []

    # Get base module list from inventory
    inventory_modules = inventory.get('modules', [])
    validation_modules = validation.get('modules', {})
    import_issues = imports.get('bad_imports', [])
    lane_assessments = {a['module']: a for a in lanes.get('assessments', [])}

    # Group import issues by file
    import_issues_by_file = {}
    for issue in import_issues:
        file_path = issue['file']
        if file_path not in import_issues_by_file:
            import_issues_by_file[file_path] = []
        import_issues_by_file[file_path].append(issue)

    for module_data in inventory_modules:
        module_name = module_data['module']

        # Get validation data
        validation_info = validation_modules.get(module_name, {})

        # Get import issues for this module's files
        module_import_issues = []
        for path in module_data.get('paths', []):
            for file_path, issues in import_issues_by_file.items():
                if file_path.startswith(path):
                    module_import_issues.extend(issues)

        # Get lane assessment
        lane_info = lane_assessments.get(module_name, {})

        # Compile comprehensive module info
        merged_module = {
            'module': module_name,
            'paths': module_data.get('paths', []),
            'contracts': module_data.get('contracts', []),
            'has_contract': module_data.get('has_contract', False),

            # Validation status
            'validation': {
                'schema_ok': validation_info.get('schema_ok', False),
                'identity_ok': validation_info.get('identity_ok', False),
                'tokenization_ok': validation_info.get('tokenization_ok', False),
                'valid': validation_info.get('valid', False),
                'error_count': validation_info.get('error_count', 0),
                'errors': validation_info.get('errors', [])
            },

            # Import issues
            'import_issues': {
                'count': len(module_import_issues),
                'issues': module_import_issues
            },

            # Lane assessment
            'lane': {
                'provisional': lane_info.get('provisional_lane', 'L1'),
                'name': lane_info.get('lane_name', 'Experimental'),
                'confidence': lane_info.get('confidence', 0.5),
                'characteristics': lane_info.get('characteristics', {})
            }
        }

        modules.append(merged_module)

    return modules


def generate_move_suggestions(modules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate suggested git mv operations based on lane assignments."""
    suggestions = []

    for module in modules:
        module_name = module['module']
        current_paths = module['paths']
        provisional_lane = module['lane']['provisional']

        # Skip if no clear improvement
        if provisional_lane in ['L0', 'L1'] or not current_paths:
            continue

        # Suggest consolidation if module has multiple paths
        if len(current_paths) > 1:
            # Suggest primary location based on lane
            if provisional_lane == 'L4':
                target_path = f"lukhas/accepted/{module_name}"
            elif provisional_lane == 'L3':
                target_path = f"lukhas/candidate/{module_name}"
            elif provisional_lane == 'L5':
                target_path = f"lukhas/core/{module_name}"
            else:
                target_path = f"lukhas/{module_name}"

            suggestion = {
                'module': module_name,
                'type': 'consolidate',
                'current_paths': current_paths,
                'suggested_target': target_path,
                'lane': provisional_lane,
                'operations': []
            }

            # Generate specific git mv commands
            for i, path in enumerate(current_paths):
                if i == 0:  # First path becomes the target
                    if path != target_path:
                        suggestion['operations'].append({
                            'command': f'git mv {path} {target_path}',
                            'type': 'primary_move'
                        })
                else:  # Subsequent paths get merged
                    suggestion['operations'].append({
                        'command': f'git mv {path}/* {target_path}/',
                        'type': 'merge_move'
                    })

            if suggestion['operations']:
                suggestions.append(suggestion)

    return suggestions


def compute_summary_stats(modules: List[Dict[str, Any]], validation: Dict[str, Any],
                         imports: Dict[str, Any], lanes: Dict[str, Any]) -> Dict[str, Any]:
    """Compute overall summary statistics."""
    total_modules = len(modules)

    # Contract stats
    with_contracts = len([m for m in modules if m['has_contract']])
    without_contracts = total_modules - with_contracts

    # Validation stats
    validation_summary = validation.get('summary', {})
    schema_ok = len([m for m in modules if m['validation']['schema_ok']])
    identity_ok = len([m for m in modules if m['validation']['identity_ok']])

    # Import issues
    import_summary = imports.get('summary', {})
    modules_with_import_issues = len([m for m in modules if m['import_issues']['count'] > 0])

    # Lane distribution
    lane_distribution = lanes.get('lane_distribution', {})

    return {
        'total_modules': total_modules,
        'contracts': {
            'with_contracts': with_contracts,
            'without_contracts': without_contracts,
            'percentage_with_contracts': round(with_contracts / total_modules * 100, 1) if total_modules > 0 else 0
        },
        'validation': {
            'schema_ok': schema_ok,
            'identity_ok': identity_ok,
            'total_validated': validation_summary.get('total', 0),
            'validation_success_rate': round(schema_ok / total_modules * 100, 1) if total_modules > 0 else 0
        },
        'imports': {
            'modules_with_issues': modules_with_import_issues,
            'total_bad_imports': import_summary.get('total_bad_imports', 0),
            'circular_imports': import_summary.get('circular_import_chains', 0)
        },
        'lanes': lane_distribution
    }


def main():
    parser = argparse.ArgumentParser(description='Aggregate MATRIZ audit data and generate reports')
    parser.add_argument('--root', default='.', help='Root directory (default: current directory)')
    parser.add_argument('--artifacts-dir', default='artifacts', help='Artifacts directory')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    root_path = pathlib.Path(args.root).resolve()
    artifacts_dir = pathlib.Path(args.artifacts_dir)

    if args.verbose:
        print(f"Aggregating audit data from: {artifacts_dir}")

    # Load all data sources
    inventory = load_artifact(artifacts_dir / 'matriz_inventory.json', 'Module inventory')
    validation = load_artifact(artifacts_dir / 'matrix_validation_results.json', 'Validation results')
    imports = load_artifact(artifacts_dir / 'matriz_imports.json', 'Import analysis')
    lanes = load_artifact(artifacts_dir / 'matriz_lanes.json', 'Lane assessments')

    # Ensure output directory exists
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # Merge all data
    modules = merge_module_data(inventory, validation, imports, lanes)

    # Generate move suggestions
    move_suggestions = generate_move_suggestions(modules)

    # Compute summary statistics
    summary_stats = compute_summary_stats(modules, validation, imports, lanes)

    # Create comprehensive audit report
    audit_data = {
        'timestamp': datetime.now().isoformat() + 'Z',
        'summary': summary_stats,
        'modules': modules,
        'data_sources': {
            'inventory_loaded': bool(inventory),
            'validation_loaded': bool(validation),
            'imports_loaded': bool(imports),
            'lanes_loaded': bool(lanes)
        }
    }

    # Write main audit file
    with open(artifacts_dir / 'matriz_audit.json', 'w') as f:
        json.dump(audit_data, f, indent=2)

    # Write move suggestions
    with open(artifacts_dir / 'matriz_moves.plan.jsonl', 'w') as f:
        for suggestion in move_suggestions:
            f.write(json.dumps(suggestion) + '\n')

    if args.verbose:
        print(f"Aggregation complete:")
        print(f"  Total modules: {summary_stats['total_modules']}")
        print(f"  With contracts: {summary_stats['contracts']['with_contracts']} ({summary_stats['contracts']['percentage_with_contracts']}%)")
        print(f"  Schema validation: {summary_stats['validation']['schema_ok']} OK")
        print(f"  Import issues: {summary_stats['imports']['modules_with_issues']} modules affected")
        print(f"  Move suggestions: {len(move_suggestions)}")
        print(f"  Audit data written to: {artifacts_dir / 'matriz_audit.json'}")
        print(f"  Move plan written to: {artifacts_dir / 'matriz_moves.plan.jsonl'}")

    return 0


if __name__ == '__main__':
    sys.exit(main())