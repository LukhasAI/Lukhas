#!/usr/bin/env python3
"""
Lukhas PWM Setup Configuration
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text() if readme_path.exists() else ""

setup(
    name="lukhas-pwm",
    version="2.0.0",
    author="LUKHAS AI",
    description="Production-ready consciousness-aware AI platform with Lambda Products",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/lukhas-pwm",
    packages=find_packages(exclude=["tests*", "docs*", "examples*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "fastapi>=0.100.0",
        "pydantic>=2.0.0",
        "asyncio",
        "aiohttp>=3.9.0",
        "numpy>=1.24.0",
        "cryptography>=41.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.11.0",
            "mypy>=1.7.0",
        ],
        "lambda": [
            "msgpack>=1.0.5",
            "orjson>=3.9.0",
            "prometheus-client>=0.19.0",
        ],
        "ml": [
            "scikit-learn>=1.3.0",
            "pandas>=2.0.0",
            "scipy>=1.11.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "lukhas=main:main",
            "lukhas-test=COMPLETE_SYSTEM_TEST:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.json", "*.md", "*.html"],
    },
)
