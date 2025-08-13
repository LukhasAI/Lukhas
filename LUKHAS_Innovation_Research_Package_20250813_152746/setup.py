#!/usr/bin/env python3
"""
Setup script for LUKHAS Innovation System Research Package
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="lukhas-innovation-system",
    version="1.0.0",
    author="LUKHAS Research Consortium",
    author_email="research@lukhas.ai",
    description="LUKHAS AI Self-Innovation System with Drift Protection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lukhas/innovation-system",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: Proprietary",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "openai>=1.0.0",
        "python-dotenv>=0.19.0",
        "pydantic>=2.0.0",
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
    ],
    extras_require={
        "dev": [
            "black>=23.0.0",
            "ruff>=0.0.261",
            "mypy>=1.0.0",
            "pytest-cov>=4.0.0",
        ],
        "full": [
            "anthropic>=0.18.0",
            "google-generativeai>=0.3.0",
            "fastapi>=0.95.0",
            "uvicorn>=0.20.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "lukhas-test=src.run_tests:main",
            "lukhas-analyze=src.analyze_pass_rate_factors:main",
        ],
    },
)