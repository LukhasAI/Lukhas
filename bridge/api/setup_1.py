"""

#TAG:bridge
#TAG:api
#TAG:neuroplastic
#TAG:colony


Setup script for LUKHAS Consciousness Platform API
"""

from setuptools import setup, find_packages

setup(
    name="consciousness-platform",
    version="1.0.0",
    description="Consciousness simulation and awareness tracking",
    author="LUKHAS AI",
    author_email="api@lukhas.ai",
    packages=find_packages(),
    install_requires=['asyncio', 'dataclasses', 'typing', 'enum'],
    extras_require={
        'advanced': ['numpy', 'scikit-learn']
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
