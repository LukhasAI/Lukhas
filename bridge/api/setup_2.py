"""

#TAG:bridge
#TAG:api
#TAG:neuroplastic
#TAG:colony


Setup script for LUKHAS Memory Services API
"""

from setuptools import setup, find_packages

setup(
    name="memory-services",
    version="1.0.0",
    description="Enterprise memory storage and retrieval",
    author="LUKHAS AI",
    author_email="api@lukhas.ai",
    packages=find_packages(),
    install_requires=['asyncio', 'dataclasses', 'typing', 'datetime'],
    extras_require={
        'advanced': ['redis', 'postgresql']
    },
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
