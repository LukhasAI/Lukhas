#!/usr/bin/env python3
"""
MATRIZ Report Generator

Generates human-readable reports from audit data, including:
- Comprehensive audit report (Markdown)
- Module location mapping (Markdown table and CSV)
"""

import argparse
import csv
import json
import pathlib
import sys
from typing import Any, Dict


def generate_audit_report(audit_data: Dict[str, Any], output_path: pathlib.Path):
    """Generate comprehensive audit report in Markdown."""
    summary = audit_data.get('summary', {})
    modules = audit_data.get('modules', [])

    # Build heatmap data
    heatmap_data = []
    for module in modules:
        module_name = module['module']
        validation = module.get('validation', {})
        lane = module.get('lane', {})
        import_issues = module.get('import_issues', {})

        row = {
            'Module': module_name,
            'Schema': '✅' if validation.get('schema_ok') else '❌',
            'Identity': '✅' if validation.get('identity_ok') else '❌',
            'OSV': '⚠️',  # Placeholder - would need OSV data
            'Telemetry': '⚠️',  # Placeholder - would need telemetry data
            'Policy': '✅' if validation.get('valid') else '❌',
            'Lane': lane.get('provisional', 'L1'),
            'Import Issues': '⚠️' if import_issues.get('count', 0) > 0 else '✅'
        }
        heatmap_data.append(row)

    # Sort by module name
    heatmap_data.sort(key=lambda x: x['Module'])

    # Generate markdown report
    lines = [
        "# MATRIZ Audit Report",
        f"Generated: {audit_data.get('timestamp', 'N/A')}",
        "",
        "## Executive Summary",
        "",
        f"- **Total Modules**: {summary.get('total_modules', 0)}",
        f"- **Modules with Contracts**: {summary.get('contracts', {}).get('with_contracts', 0)} ({summary.get('contracts', {}).get('percentage_with_contracts', 0)}%)",
        f"- **Schema Validation Success**: {summary.get('validation', {}).get('schema_ok', 0)} modules",
        f"- **Modules with Import Issues**: {summary.get('imports', {}).get('modules_with_issues', 0)}",
        f"- **Bad Import Patterns**: {summary.get('imports', {}).get('total_bad_imports', 0)}",
        "",
        "## Lane Distribution",
        ""
    ]

    # Add lane distribution
    lanes = summary.get('lanes', {})
    lane_names = {
        'L0': 'Archive',
        'L1': 'Experimental',
        'L2': 'Development',
        'L3': 'Candidate',
        'L4': 'Accepted',
        'L5': 'Core'
    }

    for lane_id in ['L5', 'L4', 'L3', 'L2', 'L1', 'L0']:
        count = lanes.get(lane_id, 0)
        lane_name = lane_names.get(lane_id, 'Unknown')
        lines.append(f"- **{lane_id} ({lane_name})**: {count} modules")

    lines.extend([
        "",
        "## Module Status Heatmap",
        "",
        "| Module | Schema | Identity | OSV | Telemetry | Policy | Lane | Import Issues |",
        "|--------|--------|----------|-----|-----------|--------|------|---------------|"
    ])

    # Add heatmap rows
    for row in heatmap_data:
        line = f"| `{row['Module']}` | {row['Schema']} | {row['Identity']} | {row['OSV']} | {row['Telemetry']} | {row['Policy']} | {row['Lane']} | {row['Import Issues']} |"
        lines.append(line)

    lines.extend([
        "",
        "## Top Issues",
        ""
    ])

    # Find modules with multiple issues
    problematic_modules = []
    for module in modules:
        issues = []
        validation = module.get('validation', {})
        import_issues = module.get('import_issues', {})

        if not validation.get('schema_ok'):
            issues.append('Schema validation failed')
        if not validation.get('identity_ok'):
            issues.append('Identity validation failed')
        if import_issues.get('count', 0) > 0:
            issues.append(f"{import_issues['count']} import issues")

        if issues:
            problematic_modules.append({
                'module': module['module'],
                'issues': issues,
                'severity': len(issues)
            })

    # Sort by severity
    problematic_modules.sort(key=lambda x: x['severity'], reverse=True)

    if problematic_modules:
        lines.append("### Modules Requiring Attention")
        lines.append("")
        for item in problematic_modules[:10]:  # Top 10
            issues_str = ", ".join(item['issues'])
            lines.append(f"- **{item['module']}**: {issues_str}")
    else:
        lines.append("No critical issues detected.")

    lines.extend([
        "",
        "## Suggested Actions",
        "",
        "### Phase 1: Critical Fixes",
        "1. Address schema validation failures",
        "2. Fix bad import patterns (`lukhas.*`, `accepted.*`)",
        "3. Resolve identity configuration issues",
        "",
        "### Phase 2: Organization",
        "1. Consolidate modules with multiple paths",
        "2. Move modules to appropriate lanes",
        "3. Add contracts to modules without them",
        "",
        "### Phase 3: Quality Assurance",
        "1. Add test coverage to modules lacking tests",
        "2. Implement OSV scanning for security",
        "3. Set up telemetry for monitoring",
        "",
        "---",
        "*This report was generated by the MATRIZ audit system.*"
    ])

    # Write the report
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))


def generate_location_reports(audit_data: Dict[str, Any], md_path: pathlib.Path, csv_path: pathlib.Path):
    """Generate module location reports in both Markdown and CSV formats."""
    modules = audit_data.get('modules', [])

    # Prepare data
    location_data = []
    for module in modules:
        module_name = module['module']
        contracts = module.get('contracts', [])
        paths = module.get('paths', [])

        # Format contracts and paths for display
        contracts_str = '; '.join(contracts) if contracts else '—'
        paths_str = '; '.join(paths) if paths else '—'

        location_data.append({
            'module': module_name,
            'contracts': contracts_str,
            'paths': paths_str
        })

    # Sort by module name
    location_data.sort(key=lambda x: x['module'])

    # Generate Markdown table
    md_lines = [
        "# Where is which (module locations)",
        "",
        "This table shows the current location of each MATRIZ module and its associated contracts.",
        "",
        "| Module | Contract(s) | Current Paths |",
        "|--------|-------------|---------------|"
    ]

    for item in location_data:
        contracts_display = item['contracts'].replace(';', '<br>') if item['contracts'] != '—' else '—'
        paths_display = item['paths'].replace(';', '<br>') if item['paths'] != '—' else '—'
        md_lines.append(f"| `{item['module']}` | {contracts_display} | {paths_display} |")

    md_lines.extend([
        "",
        f"**Total modules**: {len(location_data)}",
        "",
        f"*Generated: {audit_data.get('timestamp', 'N/A')}*"
    ])

    # Write Markdown file
    with open(md_path, 'w') as f:
        f.write('\n'.join(md_lines))

    # Write CSV file
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['module', 'contracts', 'paths'])
        writer.writeheader()
        writer.writerows(location_data)


def main():
    parser = argparse.ArgumentParser(description='Generate human-readable MATRIZ audit reports')
    parser.add_argument('--audit-file', default='artifacts/matriz_audit.json', help='Input audit file')
    parser.add_argument('--artifacts-dir', default='artifacts', help='Output artifacts directory')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    audit_file = pathlib.Path(args.audit_file)
    artifacts_dir = pathlib.Path(args.artifacts_dir)

    if args.verbose:
        print(f"Generating reports from: {audit_file}")

    # Load audit data
    try:
        with open(audit_file, 'r') as f:
            audit_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Audit file not found: {audit_file}")
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse audit file: {e}")
        return 1

    # Ensure output directory exists
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # Generate reports
    audit_report_path = artifacts_dir / 'matriz_audit_report.md'
    location_md_path = artifacts_dir / 'where_is_which.md'
    location_csv_path = artifacts_dir / 'where_is_which.csv'

    generate_audit_report(audit_data, audit_report_path)
    generate_location_reports(audit_data, location_md_path, location_csv_path)

    if args.verbose:
        print("Reports generated:")
        print(f"  Audit report: {audit_report_path}")
        print(f"  Location table (MD): {location_md_path}")
        print(f"  Location table (CSV): {location_csv_path}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
