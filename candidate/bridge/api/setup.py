"""

#TAG:bridge
#TAG:api
#TAG:neuroplastic
#TAG:colony

Setup script for LUKHAS Dream Commerce API
"""
import streamlit as st
from setuptools import find_packages, setup

setup(
    name="dream-commerce",
    version="1.0.0",
    description="Commercial API for dream generation and analysis",
    author="LUKHAS AI",
    author_email="api@lukhas.ai",
    packages=find_packages(),
    install_requires=["asyncio", "dataclasses", "typing"],
    extras_require={"advanced": ["numpy", "torch"]},
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
