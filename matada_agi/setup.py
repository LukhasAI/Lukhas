#!/usr/bin/env python3
"""Setup configuration for MATADA-AGI"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="matada-agi",
    version="0.1.0",
    author="LUKHAS AI Systems",
    author_email="contact@lukhas.ai",
    description="Modular Adaptive Temporal Attention Dynamic Architecture for AGI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lukhas/matada-agi",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.10",
    install_requires=[
        "numpy>=1.24.0",
        "dataclasses-json>=0.6.0",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "pydantic>=2.0.0",
        "networkx>=3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
            "mypy>=1.5.0",
        ],
        "viz": [
            "streamlit>=1.28.0",
            "matplotlib>=3.7.0",
            "plotly>=5.17.0",
        ],
    },
)