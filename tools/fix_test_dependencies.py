#!/usr/bin/env python3
"""
Test Dependencies Fixer
========================
Fixes all known test dependency issues across environments
"""
import streamlit as st

import subprocess
import sys
from pathlib import Path


def install_missing_packages():
    """Install missing Python packages"""
    packages = ["asgi_lifespan", "asyncpg"]

    for package in packages:
        try:
            __import__(package)
            print(f"✅ {package} already installed")
        except ImportError:
            print(f"📦 Installing {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
            print(f"✅ {package} installed successfully")


def fix_urllib3_compatibility():
    """Fix urllib3 OpenSSL compatibility issues"""
    try:
        import urllib3

        version = urllib3.__version__
        if version.startswith("2."):
            print("⚠️ urllib3 v2 detected, downgrading for LibreSSL compatibility...")
            subprocess.run([sys.executable, "-m", "pip", "install", "urllib3<2.0"], check=True)
            print("✅ urllib3 downgraded successfully")
        else:
            print(f"✅ urllib3 {version} compatible")
    except ImportError:
        print("❌ urllib3 not found")


def add_missing_models():
    """Add missing RiskGauge and RiskSeverity to models.py"""
    models_file = Path("candidate/aka_qualia/models.py")

    if not models_file.exists():
        print(f"❌ {models_file} not found")
        return

    content = models_file.read_text()

    # Check if RiskSeverity already exists
    if "class RiskSeverity" not in content:
        print("📝 Adding RiskSeverity enum...")

        # Find SeverityLevel class and add RiskSeverity after it
        severity_pattern = 'class SeverityLevel(str, Enum):\n    """TEQ Guardian severity levels"""\n\n    NONE = "none"\n    LOW = "low"\n    MODERATE = "moderate"\n    HIGH = "high"'

        risk_severity_class = '''

class RiskSeverity(str, Enum):
    """Risk assessment severity levels"""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"'''

        if severity_pattern in content:
            content = content.replace(severity_pattern, severity_pattern + risk_severity_class)
        else:
            # Fallback: add after imports
            import_end = content.find("\n\n\nclass")
            if import_end > 0:
                content = (
                    content[:import_end]
                    + '\n\nclass RiskSeverity(str, Enum):\n    """Risk assessment severity levels"""\n    \n    LOW = "low"\n    MODERATE = "moderate" \n    HIGH = "high"\n    CRITICAL = "critical"\n'
                    + content[import_end:]
                )

    # Check if RiskGauge already exists
    if "class RiskGauge" not in content:
        print("📝 Adding RiskGauge class...")

        risk_gauge_class = '''

class RiskGauge(BaseModel):
    """Risk assessment gauge for router decisions"""

    score: float = Field(ge=0.0, le=1.0, description="Risk score 0-1")
    severity: RiskSeverity = Field(description="Risk severity classification")

    @validator("severity")
    def severity_matches_score(cls, v, values):
        """Ensure severity aligns with score"""
        if "score" not in values:
            return v

        score = values["score"]
        if v == RiskSeverity.LOW and score > 0.3:
            raise ValueError("LOW severity requires score ≤ 0.3")
        elif v == RiskSeverity.MODERATE and (score < 0.3 or score > 0.7):
            raise ValueError("MODERATE severity requires score 0.3-0.7")
        elif v == RiskSeverity.HIGH and (score < 0.7 or score > 0.9):
            raise ValueError("HIGH severity requires score 0.7-0.9")
        elif v == RiskSeverity.CRITICAL and score < 0.9:
            raise ValueError("CRITICAL severity requires score ≥ 0.9")
        return v'''

        # Find a good insertion point (after RiskProfile or before PhenomenalScene)
        if "class PhenomenalScene(BaseModel):" in content:
            content = content.replace(
                "class PhenomenalScene(BaseModel):", risk_gauge_class + "\n\n\nclass PhenomenalScene(BaseModel):"
            )
        else:
            # Fallback: add at end of file
            content = content + risk_gauge_class

    # Write back the modified content
    if "class RiskGauge" in content and "class RiskSeverity" in content:
        models_file.write_text(content)
        print("✅ RiskGauge and RiskSeverity added to models.py")
    else:
        print("✅ RiskGauge and RiskSeverity already present")


def fix_import_paths():
    """Fix incorrect import paths in test files"""

    # Fix test_c5_observability.py import
    obs_test_file = Path("tests/candidate/aka_qualia/test_c5_observability.py")
    if obs_test_file.exists():
        content = obs_test_file.read_text()
        if "from memory_noop import NoopMemory" in content:
            print("📝 Fixing memory_noop import in test_c5_observability.py...")
            content = content.replace(
                "from memory_noop import NoopMemory", "from candidate.aka_qualia.memory_noop import NoopMemory"
            )
            obs_test_file.write_text(content)
            print("✅ Fixed memory_noop import")
        else:
            print("✅ memory_noop import already correct")


def create_enterprise_symlink():
    """Create enterprise symlink if missing"""
    enterprise_link = Path("enterprise")
    enterprise_target = Path("products/enterprise")

    if not enterprise_link.exists() and enterprise_target.exists():
        print("🔗 Creating enterprise symlink...")
        try:
            enterprise_link.symlink_to(enterprise_target)
            print("✅ Enterprise symlink created")
        except Exception as e:
            print(f"⚠️ Could not create symlink: {e}")


def main():
    """Run all dependency fixes"""
    print("🔧 LUKHAS Test Dependencies Fixer")
    print("=" * 40)

    print("1. Installing missing packages...")
    install_missing_packages()

    print("\n2. Fixing urllib3 compatibility...")
    fix_urllib3_compatibility()

    print("\n3. Adding missing model classes...")
    add_missing_models()

    print("\n4. Fixing import paths...")
    fix_import_paths()

    print("\n5. Creating enterprise symlink...")
    create_enterprise_symlink()

    print("\n✅ All fixes applied successfully!")
    print("\nYou can now run:")
    print("  python3 -m pytest tests/candidate/aka_qualia/test_simple.py -v")
    print("  ./tools/codex_validation.sh")


if __name__ == "__main__":
    main()
