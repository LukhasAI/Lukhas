#!/usr/bin/env python3
"""
Unit tests for the compositional module in Universal Language.
"""

import unittest
from universal_language.compositional import (
    SymbolProgram,
    SymbolComposer,
    SymbolProgramSynthesizer,
)


class TestSymbolProgram(unittest.TestCase):
    """Tests for the SymbolProgram class."""

    def test_initialization_with_symbols(self):
        """Test that a SymbolProgram can be initialized with a list of symbols."""
        program = SymbolProgram(["a", "b", "c"])
        self.assertEqual(program.symbols, ["a", "b", "c"])

    def test_initialization_without_symbols(self):
        """Test that a SymbolProgram can be initialized without any symbols."""
        program = SymbolProgram()
        self.assertEqual(program.symbols, [])

    def test_add_symbol(self):
        """Test that a symbol can be added to a SymbolProgram."""
        program = SymbolProgram()
        program.add_symbol("a")
        self.assertEqual(program.symbols, ["a"])

    def test_execute(self):
        """Test that a SymbolProgram can be executed."""
        program = SymbolProgram(["a", "b"])
        result = program.execute()
        self.assertEqual(result, {"result": "executed", "symbols": ["a", "b"]})


class TestSymbolComposer(unittest.TestCase):
    """Tests for the SymbolComposer class."""

    def test_compose(self):
        """Test that a SymbolComposer can compose a SymbolProgram."""
        composer = SymbolComposer()
        program = composer.compose(["a", "b"])
        self.assertIsInstance(program, SymbolProgram)
        self.assertEqual(program.symbols, ["a", "b"])
        self.assertIn(program, composer.compositions)


class TestSymbolProgramSynthesizer(unittest.TestCase):
    """Tests for the SymbolProgramSynthesizer class."""

    def test_synthesize_with_symbols(self):
        """Test that a SymbolProgramSynthesizer can synthesize a program."""
        synthesizer = SymbolProgramSynthesizer()
        program = synthesizer.synthesize({"symbols": ["a", "b"]})
        self.assertIsInstance(program, SymbolProgram)
        self.assertEqual(program.symbols, ["a", "b"])
        self.assertIn(program, synthesizer.synthesized_programs)

    def test_synthesize_without_symbols(self):
        """Test that a SymbolProgramSynthesizer can synthesize a program with default symbols."""
        synthesizer = SymbolProgramSynthesizer()
        program = synthesizer.synthesize({})
        self.assertIsInstance(program, SymbolProgram)
        self.assertEqual(program.symbols, ["default"])
        self.assertIn(program, synthesizer.synthesized_programs)


if __name__ == "__main__":
    unittest.main()
