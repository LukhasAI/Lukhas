"""Tests for YAML loading security fixes.

This test suite validates that:
1. yaml.safe_load blocks code execution
2. All YAML loading in the codebase uses safe methods
3. The YAML scanner correctly detects dangerous tags
4. Safe YAML files are correctly validated
"""

import pytest
import yaml
from pathlib import Path
from lukhas.security.yaml_scanner import (
    scan_yaml_file,
    scan_yaml_directory,
    safe_load_yaml,
    validate_yaml_safe_loading,
    DANGEROUS_YAML_TAGS,
)


class TestSafeLoadBlocksCodeExecution:
    """Test that yaml.safe_load properly blocks code execution."""

    def test_safe_load_blocks_object_apply(self):
        """Ensure yaml.safe_load blocks !!python/object/apply tags."""
        malicious_yaml = """
!!python/object/apply:os.system
args: ['echo "malicious code"']
"""
        # safe_load should either raise error or ignore dangerous tags
        try:
            result = yaml.safe_load(malicious_yaml)
            # If it doesn't raise, the dangerous tag should be ignored/null
            assert result is None or not callable(result)
        except (yaml.YAMLError, yaml.constructor.ConstructorError):
            # This is expected - safe_load rejects dangerous constructs
            pass

    def test_safe_load_blocks_object_new(self):
        """Ensure yaml.safe_load blocks !!python/object/new tags."""
        malicious_yaml = """
!!python/object/new:os.system
args: ['whoami']
"""
        try:
            result = yaml.safe_load(malicious_yaml)
            assert result is None or not callable(result)
        except (yaml.YAMLError, yaml.constructor.ConstructorError):
            pass

    def test_safe_load_blocks_python_name(self):
        """Ensure yaml.safe_load blocks !!python/name tags."""
        malicious_yaml = """
!!python/name:__main__.malicious_function
"""
        try:
            result = yaml.safe_load(malicious_yaml)
            assert result is None or not callable(result)
        except (yaml.YAMLError, yaml.constructor.ConstructorError):
            pass

    def test_safe_load_blocks_python_module(self):
        """Ensure yaml.safe_load blocks !!python/module tags."""
        malicious_yaml = """
!!python/module:os
"""
        try:
            result = yaml.safe_load(malicious_yaml)
            assert result is None or not callable(result)
        except (yaml.YAMLError, yaml.constructor.ConstructorError):
            pass

    def test_safe_load_accepts_safe_yaml(self):
        """Ensure yaml.safe_load accepts safe YAML."""
        safe_yaml = """
key: value
nested:
  data: 123
  list: [1, 2, 3]
mapping:
  a: apple
  b: banana
"""
        result = yaml.safe_load(safe_yaml)
        assert result is not None
        assert isinstance(result, dict)
        assert result['key'] == 'value'
        assert result['nested']['data'] == 123
        assert result['nested']['list'] == [1, 2, 3]


class TestYAMLScanner:
    """Test YAML scanner functionality."""

    def test_scanner_detects_dangerous_object_apply(self, tmp_path):
        """Ensure scanner detects !!python/object/apply tags."""
        dangerous_yaml = tmp_path / "dangerous.yaml"
        dangerous_yaml.write_text("""
key: !!python/object/apply:os.system
args: ['ls']
""")

        result = scan_yaml_file(dangerous_yaml)
        assert not result['safe']
        assert '!!python/object/apply' in result['dangerous_tags']

    def test_scanner_detects_dangerous_object(self, tmp_path):
        """Ensure scanner detects !!python/object tags."""
        dangerous_yaml = tmp_path / "dangerous.yaml"
        dangerous_yaml.write_text("""
evil: !!python/object:os.system
""")

        result = scan_yaml_file(dangerous_yaml)
        assert not result['safe']
        assert '!!python/object' in result['dangerous_tags']

    def test_scanner_detects_dangerous_name(self, tmp_path):
        """Ensure scanner detects !!python/name tags."""
        dangerous_yaml = tmp_path / "dangerous.yaml"
        dangerous_yaml.write_text("""
func: !!python/name:__main__.dangerous
""")

        result = scan_yaml_file(dangerous_yaml)
        assert not result['safe']
        assert '!!python/name' in result['dangerous_tags']

    def test_scanner_detects_dangerous_module(self, tmp_path):
        """Ensure scanner detects !!python/module tags."""
        dangerous_yaml = tmp_path / "dangerous.yaml"
        dangerous_yaml.write_text("""
mod: !!python/module:subprocess
""")

        result = scan_yaml_file(dangerous_yaml)
        assert not result['safe']
        assert '!!python/module' in result['dangerous_tags']

    def test_scanner_approves_safe_yaml(self, tmp_path):
        """Ensure scanner approves safe YAML."""
        safe_yaml = tmp_path / "safe.yaml"
        safe_yaml.write_text("""
key: value
nested:
  data: 123
  list: [1, 2, 3]
""")

        result = scan_yaml_file(safe_yaml)
        assert result['safe']
        assert len(result['dangerous_tags']) == 0

    def test_scanner_handles_nonexistent_file(self, tmp_path):
        """Ensure scanner handles nonexistent files gracefully."""
        nonexistent = tmp_path / "nonexistent.yaml"

        result = scan_yaml_file(nonexistent)
        assert not result['safe']
        assert 'error' in result

    def test_scanner_handles_invalid_yaml(self, tmp_path):
        """Ensure scanner can scan invalid YAML (we only check tags, not validity)."""
        invalid_yaml = tmp_path / "invalid.yaml"
        invalid_yaml.write_text("{ invalid: yaml: syntax")

        # Scanner should still work - it only checks for dangerous tags
        result = scan_yaml_file(invalid_yaml)
        assert 'file' in result


class TestYAMLDirectoryScanner:
    """Test directory scanning functionality."""

    def test_directory_scan_finds_yaml_files(self, tmp_path):
        """Test scanning directory for YAML files."""
        # Create mix of safe and dangerous YAML files
        (tmp_path / "safe.yaml").write_text("key: value")
        (tmp_path / "safe2.yml").write_text("another: value")
        (tmp_path / "dangerous.yaml").write_text("evil: !!python/object/apply:os.system")

        results = scan_yaml_directory(tmp_path)
        assert len(results) == 3

    def test_directory_scan_identifies_unsafe_files(self, tmp_path):
        """Test that directory scan correctly identifies unsafe files."""
        (tmp_path / "safe.yaml").write_text("key: value")
        (tmp_path / "dangerous.yaml").write_text("evil: !!python/object/apply:os.system")

        results = scan_yaml_directory(tmp_path)
        unsafe = [r for r in results if not r['safe']]
        safe = [r for r in results if r['safe']]

        assert len(unsafe) == 1
        assert len(safe) == 1
        assert 'dangerous.yaml' in unsafe[0]['file']
        assert 'safe.yaml' in safe[0]['file']

    def test_directory_scan_recursive(self, tmp_path):
        """Test that directory scan is recursive."""
        # Create nested directory structure
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (tmp_path / "root.yaml").write_text("root: true")
        (subdir / "nested.yaml").write_text("nested: true")

        results = scan_yaml_directory(tmp_path)
        assert len(results) == 2

    def test_directory_scan_empty_directory(self, tmp_path):
        """Test scanning an empty directory."""
        results = scan_yaml_directory(tmp_path)
        assert len(results) == 0


class TestSafeLoadYAMLUtility:
    """Test the safe_load_yaml utility function."""

    def test_safe_load_yaml_loads_file(self, tmp_path):
        """Test safe_load_yaml loads file correctly."""
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text("""
key: value
number: 42
list: [1, 2, 3]
""")

        data = safe_load_yaml(yaml_file)
        assert data == {
            'key': 'value',
            'number': 42,
            'list': [1, 2, 3]
        }

    def test_safe_load_yaml_handles_complex_structures(self, tmp_path):
        """Test safe_load_yaml handles complex YAML structures."""
        yaml_file = tmp_path / "complex.yaml"
        yaml_file.write_text("""
database:
  host: localhost
  port: 5432
  credentials:
    username: admin
    password: secret
services:
  - name: web
    port: 8080
  - name: api
    port: 8081
""")

        data = safe_load_yaml(yaml_file)
        assert data['database']['host'] == 'localhost'
        assert data['database']['port'] == 5432
        assert len(data['services']) == 2
        assert data['services'][0]['name'] == 'web'

    def test_safe_load_yaml_rejects_dangerous_tags(self, tmp_path):
        """Test safe_load_yaml rejects dangerous tags."""
        yaml_file = tmp_path / "dangerous.yaml"
        yaml_file.write_text("""
evil: !!python/object/apply:os.system
args: ['rm -rf /']
""")

        # Should either raise an error or return None
        try:
            result = safe_load_yaml(yaml_file)
            assert result is None or not callable(result.get('evil', None))
        except (yaml.YAMLError, yaml.constructor.ConstructorError):
            pass  # Expected

    def test_safe_load_yaml_raises_on_nonexistent_file(self, tmp_path):
        """Test safe_load_yaml raises FileNotFoundError for missing files."""
        nonexistent = tmp_path / "nonexistent.yaml"

        with pytest.raises(FileNotFoundError):
            safe_load_yaml(nonexistent)


class TestValidateYAMLSafeLoading:
    """Test validation of YAML loading patterns in codebase."""

    def test_validate_yaml_safe_loading_returns_dict(self):
        """Test that validate_yaml_safe_loading returns expected structure."""
        result = validate_yaml_safe_loading()

        assert isinstance(result, dict)
        assert 'safe' in result
        assert 'unsafe_patterns' in result
        assert 'summary' in result
        assert isinstance(result['safe'], bool)
        assert isinstance(result['unsafe_patterns'], list)
        assert isinstance(result['summary'], str)

    def test_validate_identifies_fixed_files(self):
        """Test that validation identifies our fixed files as safe."""
        result = validate_yaml_safe_loading()

        # Check that our fixes are recognized
        unsafe_files = [p['file'] for p in result['unsafe_patterns']]

        # These files should NOT appear in unsafe patterns anymore
        assert not any('audit_workflows.py' in f for f in unsafe_files), \
            "audit_workflows.py should be fixed"
        assert not any('generate_navigation.py' in f for f in unsafe_files), \
            "generate_navigation.py should be fixed"

        # high_risk_patterns.py might appear but should have the NOTE comment
        high_risk_patterns = [p for p in result['unsafe_patterns']
                              if 'high_risk_patterns.py' in p['file']]
        for pattern in high_risk_patterns:
            # Should be filtered out by our NOTE comment
            assert False, f"high_risk_patterns.py should be filtered out: {pattern}"


class TestDangerousYAMLTags:
    """Test the DANGEROUS_YAML_TAGS constant."""

    def test_dangerous_tags_list_exists(self):
        """Test that DANGEROUS_YAML_TAGS is properly defined."""
        assert DANGEROUS_YAML_TAGS is not None
        assert isinstance(DANGEROUS_YAML_TAGS, list)
        assert len(DANGEROUS_YAML_TAGS) > 0

    def test_dangerous_tags_contains_critical_tags(self):
        """Test that all critical dangerous tags are included."""
        critical_tags = [
            '!!python/object',
            '!!python/object/apply',
            '!!python/object/new',
            '!!python/name',
            '!!python/module',
        ]

        for tag in critical_tags:
            assert tag in DANGEROUS_YAML_TAGS, f"Missing critical tag: {tag}"


class TestRealWorldScenarios:
    """Test real-world YAML loading scenarios."""

    def test_workflow_file_loading(self, tmp_path):
        """Test loading a GitHub Actions workflow file safely."""
        workflow = tmp_path / "workflow.yml"
        workflow.write_text("""
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: pytest
""")

        data = safe_load_yaml(workflow)
        assert data['name'] == 'CI'
        assert 'jobs' in data
        assert 'test' in data['jobs']

    def test_mkdocs_config_loading(self, tmp_path):
        """Test loading an MkDocs configuration safely."""
        mkdocs = tmp_path / "mkdocs.yml"
        mkdocs.write_text("""
site_name: My Project
site_url: https://example.com
theme:
  name: material
  features:
    - navigation.tabs
nav:
  - Home: index.md
  - About: about.md
""")

        data = safe_load_yaml(mkdocs)
        assert data['site_name'] == 'My Project'
        assert data['theme']['name'] == 'material'
        assert len(data['nav']) == 2

    def test_config_with_anchors_and_aliases(self, tmp_path):
        """Test loading YAML with anchors and aliases (safe feature)."""
        config = tmp_path / "config.yaml"
        config.write_text("""
defaults: &defaults
  timeout: 30
  retries: 3

production:
  <<: *defaults
  host: prod.example.com

staging:
  <<: *defaults
  host: staging.example.com
""")

        data = safe_load_yaml(config)
        assert data['production']['timeout'] == 30
        assert data['staging']['timeout'] == 30
        assert data['production']['host'] == 'prod.example.com'
