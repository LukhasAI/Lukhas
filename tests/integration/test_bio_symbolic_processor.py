#!/usr/bin/env python3
"""
Integration tests for Bio Symbolic Processor
"""
import pytest


def test_bio_symbolic_processor_import():
    """Test that bio_symbolic_processor can be imported"""
    from core.bio_symbolic_processor import BioSymbolicProcessor

    assert BioSymbolicProcessor is not None


def test_bio_symbolic_processor_basic():
    """Test basic bio symbolic processor functionality"""
    from core.bio_symbolic_processor import BioSymbolicProcessor

    # Basic instantiation test
    assert BioSymbolicProcessor is not None
