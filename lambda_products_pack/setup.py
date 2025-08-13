"""
Setup configuration for LUKHAS Lambda Products Suite
Enterprise-ready AI modules for integration with Lukhas
"""

import os

from setuptools import find_packages, setup


# Read README for long description
def read_readme():
    with open("README.md", encoding="utf-8") as f:
        return f.read()


# Read requirements
def read_requirements():
    requirements = []
    if os.path.exists("requirements.txt"):
        with open("requirements.txt") as f:
            requirements = [
                line.strip() for line in f if line.strip() and not line.startswith("#")
            ]
    return requirements


setup(
    name="lukhas-lambda-products",
    version="2.0.0",
    author="LUKHAS AI Team",
    author_email="dev@lukhas.ai",
    description="Lambda Products Suite - Enterprise AI modules for symbolic intelligence",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/lukhas/lambda-products",
    license="Proprietary",
    # Package configuration
    packages=find_packages(exclude=["tests", "tests.*", "docs", "docs.*"]),
    include_package_data=True,
    python_requires=">=3.9",
    # Dependencies
    install_requires=[
        "asyncio>=3.4.3",
        "aiohttp>=3.8.0",
        "pydantic>=2.0.0",
        "python-dotenv>=0.19.0",
        "PyYAML>=6.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "typing-extensions>=4.0.0",
    ],
    # Optional dependencies for different features
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "": [
            # Dependencies for Lukhas  integration
            "lukhas->=1.0.0",
        ],
        "quantum": [
            # Quantum computing features
            "qiskit>=0.39.0",
            "cirq>=1.0.0",
        ],
        "ml": [
            # Machine learning enhancements
            "transformers>=4.25.0",
            "torch>=1.13.0",
            "tensorflow>=2.10.0",
        ],
    },
    # Entry points for plugin discovery
    entry_points={
        "lukhas.plugins": [
            # Core Lambda Products
            "nias = lambda_products.NIΛS.core.nias_plugin:NIASPlugin",
            "abas = lambda_products.ΛBAS.core.abas_plugin:ABASPlugin",
            "dast = lambda_products.DΛST.core.dast_plugin:DASTPlugin",
            "wallet = lambda_products.WΛLLET.core.wallet_plugin:WalletPlugin",
            "lens = lambda_products.ΛLens.core.lens_plugin:LensPlugin",
            "trace = lambda_products.ΛTrace.core.trace_plugin:TracePlugin",
            "nimbus = lambda_products.ΛNimbus.core.nimbus_plugin:NimbusPlugin",
            "poetica = lambda_products.POETICΛ.core.poetica_plugin:PoeticaPlugin",
            "voice = lambda_products.VoiceΛ.core.voice_plugin:VoicePlugin",
            "journal = lambda_products.JOURNΛL.core.journal_plugin:JournalPlugin",
            "weaver = lambda_products.WEΛVER.core.weaver_plugin:WeaverPlugin",
            "echo = lambda_products.ECHOΛ.core.echo_plugin:EchoPlugin",
        ],
        "console_scripts": [
            # CLI tools
            "lambda-products = lambda_products.cli:main",
            "nias-cli = lambda_products.NIΛS.cli:main",
            "abas-cli = lambda_products.ΛBAS.cli:main",
            "dast-cli = lambda_products.DΛST.cli:main",
        ],
    },
    # Package metadata
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    # Project URLs
    project_urls={
        "Documentation": "https://docs.lukhas.ai/lambda-products",
        "Bug Reports": "https://github.com/lukhas/lambda-products/issues",
        "Source": "https://github.com/lukhas/lambda-products",
        "Enterprise": "https://lukhas.ai/enterprise",
    },
    # Additional package data
    package_data={
        "lambda_products": [
            "config/*.yaml",
            "config/*.json",
            "data/*.json",
            "templates/*.html",
            "static/*",
        ],
    },
    # Zip safe flag
    zip_safe=False,
)
