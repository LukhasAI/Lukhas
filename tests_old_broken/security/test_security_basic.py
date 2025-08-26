"""
Basic security tests to validate our security infrastructure.
"""
import os
import sys
import subprocess
import pytest
from pathlib import Path


def test_security_scanners_available():
    """Test that security scanning tools are available."""
    # Check if safety is available
    try:
        result = subprocess.run(['safety', '--version'], 
                              capture_output=True, text=True, timeout=10)
        assert result.returncode == 0
        print(f"✅ Safety available: {result.stdout.strip()}")
    except (subprocess.SubprocessError, FileNotFoundError):
        pytest.skip("Safety scanner not available")

    # Check if pip-audit is available  
    try:
        result = subprocess.run(['pip-audit', '--version'], 
                              capture_output=True, text=True, timeout=10)
        assert result.returncode == 0
        print(f"✅ pip-audit available: {result.stdout.strip()}")
    except (subprocess.SubprocessError, FileNotFoundError):
        pytest.skip("pip-audit scanner not available")

    # Check if bandit is available
    try:
        result = subprocess.run(['bandit', '--version'], 
                              capture_output=True, text=True, timeout=10)
        assert result.returncode == 0
        print(f"✅ Bandit available: {result.stdout.strip()}")
    except (subprocess.SubprocessError, FileNotFoundError):
        pytest.skip("Bandit scanner not available")


def test_ollama_service_available():
    """Test that Ollama service is available for AI analysis."""
    try:
        result = subprocess.run(['ollama', 'list'], 
                              capture_output=True, text=True, timeout=15)
        assert result.returncode == 0
        print(f"✅ Ollama available with models")
        
        # Check if deepseek-coder is available
        if 'deepseek-coder:6.7b' in result.stdout:
            print("✅ DeepSeek Coder 6.7b model available")
        else:
            print("⚠️  DeepSeek Coder 6.7b model not found")
            
    except (subprocess.SubprocessError, FileNotFoundError):
        pytest.skip("Ollama service not available")


def test_security_vulnerability_fixer():
    """Test that our security vulnerability fixer script exists and is executable."""
    fixer_path = Path(__file__).parent.parent.parent / "scripts" / "fix_security_vulnerabilities.py"
    
    assert fixer_path.exists(), "Security vulnerability fixer script not found"
    assert fixer_path.is_file(), "Security vulnerability fixer is not a file"
    
    # Check if the script has the main components
    content = fixer_path.read_text()
    assert "SecurityFixer" in content, "SecurityFixer class not found"
    assert "analyze_fix_with_ollama" in content, "AI analysis function not found"
    assert "ollama" in content.lower(), "Ollama integration not found"
    
    print("✅ Security vulnerability fixer script validated")


def test_requirements_files_exist():
    """Test that requirements files exist and are readable."""
    root_path = Path(__file__).parent.parent.parent
    
    requirements_files = [
        "requirements.txt",
        "dashboard/backend/requirements.txt", 
        "tools/scripts/docker/requirements.txt",
        "config/requirements.txt",
        "core/orchestration/brain/config/requirements.txt"
    ]
    
    found_files = []
    for req_file in requirements_files:
        req_path = root_path / req_file
        if req_path.exists():
            found_files.append(req_file)
            print(f"✅ Found: {req_file}")
    
    assert len(found_files) > 0, "No requirements files found"
    print(f"✅ Found {len(found_files)} requirements files")


def test_security_reports_directory():
    """Test that security reports can be written."""
    root_path = Path(__file__).parent.parent.parent
    security_reports_dir = root_path / "/Users/agi_dev/LOCAL-REPOS/Lukhas/reports/security"
    
    # Create directory if it doesn't exist
    security_reports_dir.mkdir(exist_ok=True)
    
    assert security_reports_dir.exists(), "Security reports directory not accessible"
    assert security_reports_dir.is_dir(), "Security reports path is not a directory"
    
    # Test write permissions by creating a test file
    test_file = security_reports_dir / "test_write.txt"
    try:
        test_file.write_text("Security test write check")
        test_file.unlink()  # Clean up
        print("✅ Security reports directory is writable")
    except (OSError, PermissionError) as e:
        pytest.fail(f"Cannot write to security reports directory: {e}")


def test_python_environment_security():
    """Test basic Python environment security."""
    # Check Python version (should be reasonably recent)
    py_version = sys.version_info
    assert py_version.major >= 3, "Python 3 required for security"
    assert py_version.minor >= 8, "Python 3.8+ recommended for security features"
    print(f"✅ Python {py_version.major}.{py_version.minor}.{py_version.micro}")
    
    # Check that we're in a virtual environment (safer)
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    if in_venv:
        print("✅ Running in virtual environment")
    else:
        print("⚠️  Not in virtual environment - consider using venv for security")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
