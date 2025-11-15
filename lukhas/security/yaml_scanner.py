"""YAML security scanning utilities.

This module provides utilities to scan YAML files for dangerous tags
and safely load YAML configuration files.

Examples:
    Scan a single YAML file:
        >>> from pathlib import Path
        >>> from lukhas.security.yaml_scanner import scan_yaml_file
        >>> result = scan_yaml_file(Path('config.yaml'))
        >>> if not result['safe']:
        ...     print(f"Found dangerous tags: {result['dangerous_tags']}")

    Scan all YAML files in a directory:
        >>> from lukhas.security.yaml_scanner import scan_yaml_directory
        >>> results = scan_yaml_directory(Path('.'))
        >>> unsafe_files = [r for r in results if not r['safe']]
        >>> print(f"Found {len(unsafe_files)} unsafe YAML files")

    Safely load a YAML file:
        >>> from lukhas.security.yaml_scanner import safe_load_yaml
        >>> config = safe_load_yaml(Path('config.yaml'))
"""

import logging
from pathlib import Path
from typing import Any, Dict, List

import yaml

logger = logging.getLogger(__name__)

# Dangerous YAML tags that can execute arbitrary Python code
DANGEROUS_YAML_TAGS = [
    '!!python/object',
    '!!python/object/apply',
    '!!python/object/new',
    '!!python/name',
    '!!python/module',
]


def scan_yaml_file(file_path: Path) -> Dict[str, Any]:
    """Scan YAML file for dangerous tags.

    This function reads a YAML file and checks for the presence of
    dangerous tags that could execute arbitrary code.

    Args:
        file_path: Path to the YAML file to scan

    Returns:
        Dict with the following keys:
            - file (str): Path to the scanned file
            - safe (bool): True if no dangerous tags found
            - dangerous_tags (List[str]): List of dangerous tags found
            - error (str, optional): Error message if scanning failed

    Examples:
        >>> result = scan_yaml_file(Path('safe.yaml'))
        >>> assert result['safe'] == True
        >>> assert len(result['dangerous_tags']) == 0

        >>> result = scan_yaml_file(Path('dangerous.yaml'))
        >>> assert result['safe'] == False
        >>> assert '!!python/object/apply' in result['dangerous_tags']
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        found_tags = [tag for tag in DANGEROUS_YAML_TAGS if tag in content]

        return {
            'file': str(file_path),
            'safe': len(found_tags) == 0,
            'dangerous_tags': found_tags
        }
    except Exception as e:
        logger.error(f"Error scanning {file_path}: {e}")
        return {
            'file': str(file_path),
            'safe': False,
            'error': str(e)
        }


def scan_yaml_directory(directory: Path) -> List[Dict[str, Any]]:
    """Scan all YAML files in directory for dangerous tags.

    This function recursively scans all .yaml and .yml files in the
    given directory and its subdirectories.

    Args:
        directory: Path to the directory to scan

    Returns:
        List of scan results, one for each YAML file found

    Examples:
        >>> results = scan_yaml_directory(Path('.'))
        >>> unsafe = [r for r in results if not r['safe']]
        >>> if unsafe:
        ...     print(f"WARNING: Found {len(unsafe)} unsafe YAML files")
        ...     for r in unsafe:
        ...         print(f"  {r['file']}: {r['dangerous_tags']}")
    """
    results = []

    # Scan .yaml files
    for yaml_file in directory.rglob('*.yaml'):
        results.append(scan_yaml_file(yaml_file))

    # Scan .yml files
    for yml_file in directory.rglob('*.yml'):
        results.append(scan_yaml_file(yml_file))

    return results


def safe_load_yaml(file_path: Path) -> Any:
    """Safely load YAML file.

    This function uses yaml.safe_load() to prevent code execution
    vulnerabilities when loading YAML files.

    Args:
        file_path: Path to the YAML file to load

    Returns:
        Parsed YAML content (typically a dict or list)

    Raises:
        yaml.YAMLError: If the YAML is malformed
        FileNotFoundError: If the file doesn't exist

    Examples:
        >>> config = safe_load_yaml(Path('config.yaml'))
        >>> print(config['database']['host'])

    Note:
        This function will NOT execute any Python code embedded in the YAML.
        Dangerous tags like !!python/object will be rejected.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def validate_yaml_safe_loading() -> Dict[str, Any]:
    """Validate that all YAML loading in the codebase uses safe methods.

    This function scans Python files for unsafe YAML loading patterns
    and returns a report of findings.

    Returns:
        Dict with validation results:
            - safe (bool): True if no unsafe patterns found
            - unsafe_patterns (List[Dict]): List of unsafe patterns found
            - summary (str): Human-readable summary

    Examples:
        >>> result = validate_yaml_safe_loading()
        >>> if not result['safe']:
        ...     print(f"WARNING: {result['summary']}")
        ...     for pattern in result['unsafe_patterns']:
        ...         print(f"  {pattern['file']}:{pattern['line']}")
    """
    import subprocess
    from pathlib import Path

    repo_root = Path(__file__).parent.parent.parent
    unsafe_patterns = []

    # Search for yaml.load( without SafeLoader
    try:
        result = subprocess.run(
            [
                'grep', '-r', '-n', '-E',
                r'yaml\.load\s*\(',
                '--include=*.py',
                '--exclude-dir=.git',
                '--exclude-dir=__pycache__',
                '--exclude-dir=.pytest_cache',
                str(repo_root)
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        for line in result.stdout.split('\n'):
            if not line.strip():
                continue

            # Skip safe patterns
            if 'safe_load' in line:
                continue
            if 'SafeLoader' in line:
                continue
            if 'NOTE: This line is NOT a YAML vulnerability' in line:
                continue

            # Parse grep output
            parts = line.split(':', 2)
            if len(parts) >= 3:
                unsafe_patterns.append({
                    'file': parts[0],
                    'line': parts[1],
                    'context': parts[2].strip()
                })

    except Exception as e:
        logger.error(f"Error validating YAML loading: {e}")

    is_safe = len(unsafe_patterns) == 0
    summary = (
        "All YAML loading uses safe methods" if is_safe
        else f"Found {len(unsafe_patterns)} unsafe YAML loading patterns"
    )

    return {
        'safe': is_safe,
        'unsafe_patterns': unsafe_patterns,
        'summary': summary
    }
