import pytest

def test_ethics_import_performance(benchmark):
    """Benchmark the import time of the 'ethics' module."""
    benchmark(lambda: __import__('governance.ethics'))

def test_guardian_system_import_performance(benchmark):
    """Benchmark the import time of the 'guardian_system' module."""
    benchmark(lambda: __import__('governance.guardian_system'))

def test_identity_import_performance(benchmark):
    """Benchmark the import time of the 'identity' module."""
    benchmark(lambda: __import__('governance.identity'))
