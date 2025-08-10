"""
Test suite for LUKHAS Unified Grammar Compliance.

Validates that modules comply with the Unified Grammar v1.0.0 specification.
"""

import ast
from pathlib import Path
from typing import List

import pytest
from core_unified_grammar.common.base_module import BaseLukhasModule


class TestGrammarCompliance:
    """Test modules comply with Unified Grammar specification."""

    def get_module_files(self) -> List[Path]:
        """Get all module implementation files."""
        base_path = Path(
            "/Users/agi_dev/Downloads/Consolidation-Repo/lukhas_unified_grammar"
        )
        module_files = []

        # Core module files
        modules = [
            "bio",
            "dream",
            "emotion",
            "governance",
            "identity",
            "memory",
            "vision",
            "voice",
        ]
        for module in modules:
            core_file = base_path / module / "core.py"
            if core_file.exists():
                module_files.append(core_file)

        return module_files

    def test_module_structure(self):
        """Test all modules follow correct directory structure."""
        base_path = Path(
            "/Users/agi_dev/Downloads/Consolidation-Repo/lukhas_unified_grammar"
        )

        required_modules = ["bio", "dream", "voice", "vision", "identity"]

        for module_name in required_modules:
            module_path = base_path / module_name

            # Check required files/directories
            assert module_path.exists(), f"Module directory missing: {module_name}"
            assert (
                module_path / "__init__.py"
            ).exists(), f"Missing __init__.py in {module_name}"
            assert (
                module_path / "core.py"
            ).exists(), f"Missing core.py in {module_name}"

            # Check optional but recommended directories
            if (module_path / "symbolic").exists():
                assert (module_path / "symbolic" / "__init__.py").exists()
                assert (module_path / "symbolic" / "vocabulary.py").exists()

            if (module_path / "examples").exists():
                assert (module_path / "examples" / "__init__.py").exists()

    def test_module_inheritance(self):
        """Test all modules inherit from BaseLukhasModule."""
        from core_unified_grammar.bio.core import LucasBioModule
        from core_unified_grammar.dream.core import LucasDreamModule
        from core_unified_grammar.vision.core import LucasVisionModule
        from core_unified_grammar.voice.core import LucasVoiceModule

        modules = [
            LucasDreamModule,
            LucasBioModule,
            LucasVoiceModule,
            LucasVisionModule,
        ]

        for module_class in modules:
            assert issubclass(
                module_class, BaseLukhasModule
            ), f"{module_class.__name__} must inherit from BaseLukhasModule"

    def test_required_methods(self):
        """Test all modules implement required methods."""
        from core_unified_grammar.bio.core import LucasBioModule
        from core_unified_grammar.dream.core import LucasDreamModule

        required_methods = ["startup", "shutdown", "process", "get_health_status"]

        modules = [LucasDreamModule(), LucasBioModule()]

        for module in modules:
            for method_name in required_methods:
                assert hasattr(
                    module, method_name
                ), f"{module.name} missing required method: {method_name}"

                method = getattr(module, method_name)
                assert callable(method), f"{module.name}.{method_name} must be callable"

    def test_module_naming_convention(self):
        """Test modules follow naming conventions."""
        from core_unified_grammar.bio.core import LucasBioModule
        from core_unified_grammar.dream.core import LucasDreamModule
        from core_unified_grammar.vision.core import LucasVisionModule
        from core_unified_grammar.voice.core import LucasVoiceModule

        modules = [
            ("dream", LucasDreamModule),
            ("bio", LucasBioModule),
            ("voice", LucasVoiceModule),
            ("vision", LucasVisionModule),
        ]

        for module_type, module_class in modules:
            # Class name should be Lukhas{Type}Module
            expected_name = f"Lukhas{module_type.capitalize()}Module"
            assert (
                module_class.__name__ == expected_name
            ), f"Expected class name: {expected_name}, got: {module_class.__name__}"

            # Instance name should contain module type
            instance = module_class()
            assert (
                module_type in instance.name.lower()
            ), f"Module name should contain '{module_type}'"

    def test_symbolic_logging(self):
        """Test modules use symbolic logging."""
        module_files = self.get_module_files()

        for file_path in module_files:
            if not file_path.exists():
                continue

            content = file_path.read_text()

            # Check for symbolic logging patterns
            has_symbolic = (
                "log_symbolic" in content
                or "self.logger.symbolic" in content
                or "await self.log_symbolic" in content
            )

            assert has_symbolic, f"{file_path.name} should use symbolic logging"

    def test_configuration_pattern(self):
        """Test modules follow configuration patterns."""
        from core_unified_grammar.bio.core import (
            LucasBioConfig,
            LucasBioModule,
        )
        from core_unified_grammar.dream.core import (
            LucasDreamConfig,
            LucasDreamModule,
        )

        # Test config classes exist
        assert LucasDreamConfig is not None
        assert LucasBioConfig is not None

        # Test modules accept config
        dream = LucasDreamModule({"test": "value"})
        assert dream.config["test"] == "value"

        bio = LucasBioModule(LucasBioConfig(health_monitoring_enabled=False))
        assert hasattr(bio.config, "health_monitoring_enabled")

    def test_tier_support(self):
        """Test modules support tier-based access."""
        from core_unified_grammar.bio.core import LucasBioModule
        from core_unified_grammar.dream.core import LucasDreamModule

        modules = [LucasDreamModule(), LucasBioModule()]

        for module in modules:
            # Should have tier_required attribute
            assert hasattr(
                module, "tier_required"
            ), f"{module.name} missing tier_required"
            assert isinstance(
                module.tier_required, int
            ), f"{module.name} tier_required must be int"
            assert (
                1 <= module.tier_required <= 5
            ), f"{module.name} tier_required out of range"

            # Should have check_tier_access method
            assert hasattr(
                module, "check_tier_access"
            ), f"{module.name} missing check_tier_access"


class TestVocabularyCompliance:
    """Test symbolic vocabulary compliance."""

    def test_vocabulary_structure(self):
        """Test vocabularies follow correct structure."""
        vocab_path = Path(
            "/Users/agi_dev/Downloads/Consolidation-Repo/lukhas/symbolic/vocabularies"
        )

        vocab_files = [
            "bio_vocabulary.py",
            "dream_vocabulary.py",
            "identity_vocabulary.py",
            "voice_vocabulary.py",
            "vision_vocabulary.py",
        ]

        for vocab_file in vocab_files:
            file_path = vocab_path / vocab_file
            assert file_path.exists(), f"Missing vocabulary file: {vocab_file}"

            # Check file has proper structure
            content = file_path.read_text()

            # Should have module docstring
            assert '"""' in content[:200], f"{vocab_file} missing module docstring"

            # Should define vocabulary constant
            module_name = vocab_file.replace("_vocabulary.py", "").upper()
            assert (
                f"{module_name}_VOCABULARY" in content
            ), f"{vocab_file} missing {module_name}_VOCABULARY"

    def test_vocabulary_entries(self):
        """Test vocabulary entries are well-formed."""
        from symbolic.vocabularies import bio_vocabulary

        vocab = bio_vocabulary.BIO_VOCABULARY

        for key, entry in vocab.items():
            # Check required fields
            assert isinstance(entry, dict), f"{key} entry must be dict"
            assert "emoji" in entry, f"{key} missing emoji"
            assert "symbol" in entry, f"{key} missing symbol"
            assert "meaning" in entry, f"{key} missing meaning"
            assert "guardian_weight" in entry, f"{key} missing guardian_weight"

            # Validate types
            assert isinstance(entry["emoji"], str), f"{key} emoji must be string"
            assert isinstance(entry["symbol"], str), f"{key} symbol must be string"
            assert isinstance(entry["meaning"], str), f"{key} meaning must be string"
            assert isinstance(
                entry["guardian_weight"], (int, float)
            ), f"{key} guardian_weight must be number"


class TestExampleCompliance:
    """Test examples follow best practices."""

    def test_examples_exist(self):
        """Test modules have usage examples."""
        base_path = Path(
            "/Users/agi_dev/Downloads/Consolidation-Repo/lukhas_unified_grammar"
        )

        modules_with_examples = ["bio", "voice", "vision", "identity"]

        for module_name in modules_with_examples:
            examples_dir = base_path / module_name / "examples"

            if examples_dir.exists():
                # Should have at least one example file
                example_files = list(examples_dir.glob("*.py"))
                assert (
                    len(example_files) > 0
                ), f"No examples found in {module_name}/examples/"

                # Example files should have proper structure
                for example_file in example_files:
                    content = example_file.read_text()

                    # Should have main function
                    assert (
                        "def main" in content or "async def main" in content
                    ), f"{example_file.name} missing main function"

                    # Should have if __name__ == "__main__"
                    assert (
                        'if __name__ == "__main__"' in content
                    ), f"{example_file.name} missing main guard"

    def test_examples_are_runnable(self):
        """Test examples can be parsed (syntax check)."""
        base_path = Path(
            "/Users/agi_dev/Downloads/Consolidation-Repo/lukhas_unified_grammar"
        )

        for module_dir in base_path.iterdir():
            if not module_dir.is_dir() or module_dir.name.startswith("."):
                continue

            examples_dir = module_dir / "examples"
            if not examples_dir.exists():
                continue

            for example_file in examples_dir.glob("*.py"):
                try:
                    # Parse the file to check syntax
                    content = example_file.read_text()
                    ast.parse(content)
                except SyntaxError as e:
                    pytest.fail(f"Syntax error in {example_file}: {e}")


class TestDocumentationCompliance:
    """Test documentation standards."""

    def test_module_docstrings(self):
        """Test all modules have proper docstrings."""
        module_files = TestGrammarCompliance().get_module_files()

        for file_path in module_files:
            if not file_path.exists():
                continue

            content = file_path.read_text()

            # Parse AST to check docstrings
            tree = ast.parse(content)

            # Module should have docstring
            assert (
                ast.get_docstring(tree) is not None
            ), f"{file_path.name} missing module docstring"

            # Find main class
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and "Module" in node.name:
                    # Class should have docstring
                    assert (
                        ast.get_docstring(node) is not None
                    ), f"{file_path.name}: {node.name} missing class docstring"

    def test_grammar_documentation(self):
        """Test Unified Grammar documentation exists."""
        base_path = Path(
            "/Users/agi_dev/Downloads/Consolidation-Repo/lukhas_unified_grammar"
        )

        required_docs = [
            "LUKHAS_UNIFIED_GRAMMAR.md",
            "UNIFIED_GRAMMAR_INTEGRATION_PLAN.md",
        ]

        for doc_name in required_docs:
            doc_path = base_path / doc_name
            assert doc_path.exists(), f"Missing documentation: {doc_name}"

            # Check document has content
            content = doc_path.read_text()
            assert len(content) > 1000, f"{doc_name} seems too short"
            assert "## " in content, f"{doc_name} missing section headers"
