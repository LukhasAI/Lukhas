#!/usr/bin/env python3
"""
Comprehensive tests for the Universal Language runtime.
"""

import unittest
import timeit
from unittest.mock import MagicMock, patch
from universal_language.compositional import (
    SymbolComposer,
    SymbolProgram,
    SymbolProgramSynthesizer,
)
from universal_language.multimodal import ModalityProcessor, ModalityType

class TestSymbolProgramRuntime(unittest.TestCase):
    """Tests for the SymbolProgram class runtime behavior."""

    def test_program_execution(self):
        """Test basic program execution."""
        program = SymbolProgram(["a", "b", "c"])
        self.assertEqual(program.execute(), {"result": "executed", "symbols": ["a", "b", "c"]})

    def test_execution_empty_program(self):
        """Test execution of a program with no symbols."""
        program = SymbolProgram()
        self.assertEqual(program.execute(), {"result": "executed", "symbols": []})

    def test_memory_and_state(self):
        """Test the program's internal state (memory)."""
        program = SymbolProgram()
        self.assertEqual(program.symbols, [])
        self.assertEqual(program.context, {})
        program.add_symbol("start")
        self.assertEqual(program.symbols, ["start"])
        program.context["status"] = "running"
        self.assertEqual(program.context, {"status": "running"})

    def test_add_invalid_symbol_type(self):
        """Test adding a non-string symbol to the program."""
        program = SymbolProgram()
        # The current implementation allows this, but we test the behavior.
        program.add_symbol(123)
        self.assertEqual(program.symbols, [123])

    def test_resource_limits(self):
        """Test the program's resource limits."""
        program = SymbolProgram(max_symbols=2)
        program.add_symbol("a")
        program.add_symbol("b")
        with self.assertRaises(MemoryError):
            program.add_symbol("c")


class TestSymbolComposerRuntime(unittest.TestCase):
    """Tests for the SymbolComposer class runtime behavior."""

    def test_composition_and_state(self):
        """Test composing programs and tracking state."""
        composer = SymbolComposer()
        self.assertEqual(composer.compositions, [])
        program1 = composer.compose(["a", "b"])
        self.assertIsInstance(program1, SymbolProgram)
        self.assertIn(program1, composer.compositions)
        self.assertEqual(len(composer.compositions), 1)
        program2 = composer.compose(["c", "d"])
        self.assertIn(program2, composer.compositions)
        self.assertEqual(len(composer.compositions), 2)

    def test_compose_empty_symbols(self):
        """Test composing a program with an empty list of symbols."""
        composer = SymbolComposer()
        program = composer.compose([])
        self.assertEqual(program.symbols, [])

    def test_exception_on_invalid_input(self):
        """Test that composing with invalid input raises an exception."""
        composer = SymbolComposer()
        with self.assertRaises(TypeError):
            composer.compose("not_a_list")
        with self.assertRaises(TypeError):
            composer.compose(123)


class TestSymbolProgramSynthesizerRuntime(unittest.TestCase):
    """Tests for the SymbolProgramSynthesizer class runtime behavior."""

    def test_synthesis_and_state(self):
        """Test synthesizing programs and tracking state."""
        synthesizer = SymbolProgramSynthesizer()
        self.assertEqual(synthesizer.synthesized_programs, [])
        spec1 = {"symbols": ["x", "y"]}
        program1 = synthesizer.synthesize(spec1)
        self.assertIsInstance(program1, SymbolProgram)
        self.assertIn(program1, synthesizer.synthesized_programs)
        self.assertEqual(len(synthesizer.synthesized_programs), 1)
        spec2 = {"symbols": ["z"]}
        program2 = synthesizer.synthesize(spec2)
        self.assertIn(program2, synthesizer.synthesized_programs)
        self.assertEqual(len(synthesizer.synthesized_programs), 2)

    def test_synthesis_with_default_symbols(self):
        """Test synthesizing a program with a default specification."""
        synthesizer = SymbolProgramSynthesizer()
        program = synthesizer.synthesize({})
        self.assertEqual(program.symbols, ["default"])

    def test_exception_on_invalid_spec(self):
        """Test that synthesizing with an invalid spec raises an exception."""
        synthesizer = SymbolProgramSynthesizer()
        with self.assertRaises(AttributeError):
            synthesizer.synthesize("not_a_dict")
        with self.assertRaises(AttributeError):
            synthesizer.synthesize(None)


class TestModalityProcessorRuntime(unittest.TestCase):
    """Tests for the ModalityProcessor class runtime behavior."""

    def setUp(self):
        """Set up a new processor for each test."""
        self.processor = ModalityProcessor()

    def test_state_and_memory(self):
        """Test the processor's internal state and memory."""
        self.assertEqual(self.processor.processed_items, [])
        self.assertEqual(self.processor.get_processed_count(), 0)
        self.processor.process("test", ModalityType.TEXT)
        self.assertEqual(len(self.processor.processed_items), 1)
        self.assertEqual(self.processor.get_processed_count(), 1)
        self.assertEqual(self.processor.get_processed_count(ModalityType.TEXT), 1)
        self.processor.process({"data": "image"}, ModalityType.IMAGE)
        self.assertEqual(self.processor.get_processed_count(), 2)
        self.assertEqual(self.processor.get_processed_count(ModalityType.IMAGE), 1)

    def test_processing_all_modalities(self):
        """Test processing for all supported modality types."""
        for modality in ModalityType:
            self.processor.process(f"data_for_{modality.value}", modality)
        self.assertEqual(self.processor.get_processed_count(), len(ModalityType))

    def test_process_color_modality_with_hex(self):
        """Test processing of the COLOR modality with a hex code."""
        data = "#FF0000"
        result = self.processor.process(data, ModalityType.COLOR)
        self.assertTrue(result["metadata"]["hex_parsed"])

    def test_exception_on_invalid_modality(self):
        """Test that an invalid modality raises an exception."""
        with self.assertRaises(AttributeError):
            self.processor.process("test", "invalid_modality")
        with self.assertRaises(AttributeError):
            self.processor.process("test", None)


class TestPerformanceCharacteristics(unittest.TestCase):
    """Performance benchmarks for the Universal Language runtime."""

    def setUp(self):
        """Set up instances for benchmarking."""
        self.program = SymbolProgram(list(range(100)))
        self.composer = SymbolComposer()
        self.synthesizer = SymbolProgramSynthesizer()
        self.processor = ModalityProcessor()

    def test_benchmark_program_execution(self):
        """Benchmark the execution time of a SymbolProgram."""
        execution_time = timeit.timeit(self.program.execute, number=1000)
        self.assertLess(execution_time, 0.1)

    def test_benchmark_symbol_composition(self):
        """Benchmark the composition time of a SymbolComposer."""
        composition_time = timeit.timeit(
            lambda: self.composer.compose(list(range(100))), number=1000
        )
        self.assertLess(composition_time, 0.1)

    def test_benchmark_program_synthesis(self):
        """Benchmark the synthesis time of a SymbolProgramSynthesizer."""
        spec = {"symbols": list(range(100))}
        synthesis_time = timeit.timeit(
            lambda: self.synthesizer.synthesize(spec), number=1000
        )
        self.assertLess(synthesis_time, 0.1)

    def test_benchmark_modality_processing(self):
        """Benchmark the processing time of a ModalityProcessor."""
        processing_time = timeit.timeit(
            lambda: self.processor.process("test data", ModalityType.TEXT), number=1000
        )
        self.assertLess(processing_time, 0.1)


if __name__ == "__main__":
    unittest.main()


class TestMockedExecutionEnvironment(unittest.TestCase):
    """Tests with a mocked execution environment."""

    @patch("universal_language.compositional.SymbolProgram")
    def test_composer_with_mocked_program(self, MockSymbolProgram):
        """Test SymbolComposer with a mocked SymbolProgram."""
        mock_instance = MockSymbolProgram.return_value
        mock_instance.execute.return_value = {"result": "mocked"}
        composer = SymbolComposer()
        program = composer.compose(["a", "b"])
        self.assertEqual(program.execute(), {"result": "mocked"})

    @patch("universal_language.compositional.SymbolProgram")
    def test_synthesizer_with_mocked_program(self, MockSymbolProgram):
        """Test SymbolProgramSynthesizer with a mocked SymbolProgram."""
        mock_instance = MockSymbolProgram.return_value
        mock_instance.execute.return_value = {"result": "synthesized_mock"}
        synthesizer = SymbolProgramSynthesizer()
        program = synthesizer.synthesize({"symbols": ["x", "y"]})
        self.assertEqual(program.execute(), {"result": "synthesized_mock"})
