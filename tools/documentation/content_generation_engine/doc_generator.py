"""
Documentation Generation Engine
Implements intelligent documentation generation with Lukhas AGI capabilities.
"""

import ast
import logging
from pathlib import Path
from typing import Any, Optional

import jinja2
from pydantic import BaseModel

from ..symbolic_knowledge_core.knowledge_graph import (
    NodeType,
    RelationshipType,
    SKGNode,
    SystemKnowledgeGraph,
)

logger = logging.getLogger(__name__)


class DocSection(BaseModel):
    """Represents a section of generated documentation."""

    title: str
    content: str
    section_type: str
    metadata: dict[str, Any] = {}
    subsections: list["DocSection"] = []
    importance_score: float = 1.0
    complexity_level: int = 1


class DocumentationConfig(BaseModel):
    """Configuration for documentation generation."""

    output_format: str = "markdown"
    include_examples: bool = True
    complexity_level: int = 1
    cultural_context: Optional[str] = None
    voice_enabled: bool = False
    bio_oscillator_data: Optional[dict[str, Any]] = None
    template_overrides: Optional[dict[str, str]] = None


class DocGenerator:
    """
    Core documentation generation engine that integrates with Lukhas AGI capabilities.
    """

    def __init__(self, skg: SystemKnowledgeGraph, template_dir: Optional[str] = None):
        self.skg = skg

        # Set up template engine
        template_path = template_dir or Path(__file__).parent / "templates"
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(template_path)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Register custom filters
        self.template_env.filters["format_type"] = self._format_type_name
        self.template_env.filters["sanitize_markdown"] = self._sanitize_markdown

        logger.info(f"DocGenerator initialized with template path: {template_path}")

    def generate_documentation(
        self, source_path: str, config: DocumentationConfig
    ) -> str:
        """
        Generate comprehensive documentation for a given source.
        Uses Lukhas's intelligence to structure and present information optimally.
        """
        try:
            # Analyze source and build knowledge graph
            self._analyze_source(source_path)

            # Generate documentation sections
            sections = self._generate_sections(config)

            # Apply Lukhas's knowledge evolution patterns
            sections = self._enhance_with_lucas_patterns(sections, config)

            # Generate final documentation
            doc_content = self._render_documentation(sections, config)

            logger.info(f"Generated documentation for {source_path}")
            return doc_content

        except Exception as e:
            logger.error(f"Documentation generation failed: {str(e)}", exc_info=True)
            raise

    def _analyze_source(self, source_path: str):
        """Analyze source code and build the knowledge graph."""
        if source_path.endswith(".py"):
            self._analyze_python_file(source_path)
        # Add handlers for other file types as needed

    def _analyze_python_file(self, file_path: str):
        """Analyze a Python file and update the knowledge graph."""
        try:
            with open(file_path, encoding="utf-8") as f:
                tree = ast.parse(f.read())

            # Process module-level docstring
            if ast.get_docstring(tree):
                module_node = SKGNode(
                    id=file_path,
                    node_type=NodeType.MODULE,
                    name=Path(file_path).stem,
                    description=ast.get_docstring(tree),
                    source_location=file_path,
                )
                self.skg.add_node(module_node)

            # Process classes and functions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self._process_class(node, file_path)
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    self._process_function(node, file_path)

        except Exception as e:
            logger.error(f"Failed to analyze Python file {file_path}: {str(e)}")
            raise

    def _process_class(self, node: ast.ClassDef, file_path: str):
        """Process a class definition and add it to the knowledge graph."""
        class_id = f"{file_path}::{node.name}"

        # Create class node
        class_node = SKGNode(
            id=class_id,
            node_type=NodeType.CLASS,
            name=node.name,
            description=ast.get_docstring(node),
            source_location=file_path,
            properties={
                "line_number": node.lineno,
                "decorators": [
                    d.id for d in node.decorator_list if isinstance(d, ast.Name)
                ],
                "bases": [b.id for b in node.bases if isinstance(b, ast.Name)],
            },
        )
        self.skg.add_node(class_node)

        # Process methods
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._process_function(item, file_path, class_id)

    def _process_function(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        file_path: str,
        parent_id: Optional[str] = None,
    ):
        """Process a function definition and add it to the knowledge graph."""
        func_id = f"{parent_id or file_path}::{node.name}"

        # Extract return type hint if present
        returns_type = None
        if node.returns:
            returns_type = self._extract_type_hint(node.returns)

        # Process arguments
        args_info = self._process_arguments(node.args)

        # Create function node
        func_node = SKGNode(
            id=func_id,
            node_type=NodeType.FUNCTION,
            name=node.name,
            description=ast.get_docstring(node),
            source_location=file_path,
            properties={
                "line_number": node.lineno,
                "is_async": isinstance(node, ast.AsyncFunctionDef),
                "decorators": [
                    d.id for d in node.decorator_list if isinstance(d, ast.Name)
                ],
                "arguments": args_info,
                "returns": returns_type,
            },
        )
        self.skg.add_node(func_node)

        # Add relationship to parent if exists
        if parent_id:
            self.skg.add_relationship(
                SKGRelationship(
                    source_id=parent_id,
                    target_id=func_id,
                    type=RelationshipType.CONTAINS,
                )
            )

    def _extract_type_hint(self, node: ast.AST) -> str:
        """Extract type hint information from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Subscript):
            # Handle generic types like List[str]
            if isinstance(node.value, ast.Name):
                base = node.value.id
                if isinstance(node.slice, ast.Name):
                    return f"{base}[{node.slice.id}]"
        return "Any"

    def _process_arguments(self, args: ast.arguments) -> dict[str, Any]:
        """Process function arguments and their type hints."""
        processed_args = []

        for arg in args.args:
            arg_info = {
                "name": arg.arg,
                "type": (
                    self._extract_type_hint(arg.annotation) if arg.annotation else "Any"
                ),
            }
            processed_args.append(arg_info)

        return {
            "args": processed_args,
            "kwonly": len(args.kwonlyargs),
            "varargs": args.vararg.arg if args.vararg else None,
            "kwargs": args.kwarg.arg if args.kwarg else None,
        }

    def _generate_sections(self, config: DocumentationConfig) -> list[DocSection]:
        """Generate documentation sections from the knowledge graph."""
        sections = []

        # Generate module documentation
        for module in self.skg.find_nodes_by_type(NodeType.MODULE):
            module_section = self._generate_module_section(module, config)
            sections.append(module_section)

        return sections

    def _generate_module_section(
        self, module_node: SKGNode, config: DocumentationConfig
    ) -> DocSection:
        """Generate documentation section for a module."""
        # Create main module section
        module_section = DocSection(
            title=f"Module: {module_node.name}",
            content=module_node.description or "",
            section_type="module",
            metadata={"source_location": module_node.source_location},
        )

        # Add classes
        for class_node in self.skg.get_connected_nodes(
            module_node.id, RelationshipType.CONTAINS
        ):
            if class_node.node_type == NodeType.CLASS:
                class_section = self._generate_class_section(class_node, config)
                module_section.subsections.append(class_section)

        return module_section

    def _generate_class_section(
        self, class_node: SKGNode, config: DocumentationConfig
    ) -> DocSection:
        """Generate documentation section for a class."""
        # Create class section
        class_section = DocSection(
            title=f"Class: {class_node.name}",
            content=class_node.description or "",
            section_type="class",
            metadata={
                "source_location": class_node.source_location,
                "properties": class_node.properties,
            },
        )

        # Add methods
        for method_node in self.skg.get_connected_nodes(
            class_node.id, RelationshipType.CONTAINS
        ):
            if method_node.node_type == NodeType.FUNCTION:
                method_section = self._generate_function_section(method_node, config)
                class_section.subsections.append(method_section)

        return class_section

    def _generate_function_section(
        self, func_node: SKGNode, config: DocumentationConfig
    ) -> DocSection:
        """Generate documentation section for a function/method."""
        props = func_node.properties

        # Build signature
        signature = self._build_function_signature(
            func_node.name, props.get("arguments", {})
        )

        # Create function section
        return DocSection(
            title=f"{'async ' if props.get('is_async') else ''}{'Method' if props.get('is_method') else 'Function'}: {signature}",
            content=func_node.description or "",
            section_type="function",
            metadata={
                "source_location": func_node.source_location,
                "properties": props,
            },
        )

    def _build_function_signature(self, name: str, args_info: dict[str, Any]) -> str:
        """Build a function signature string."""
        parts = []

        # Add positional and keyword arguments
        for arg in args_info.get("args", []):
            arg_str = arg["name"]
            if arg.get("type"):
                arg_str += f": {arg['type']}"
            parts.append(arg_str)

        # Add *args if present
        if args_info.get("varargs"):
            parts.append(f"*{args_info['varargs']}")

        # Add **kwargs if present
        if args_info.get("kwargs"):
            parts.append(f"**{args_info['kwargs']}")

        return f"{name}({', '.join(parts)})"

    def _enhance_with_lucas_patterns(
        self, sections: list[DocSection], config: DocumentationConfig
    ) -> list[DocSection]:
        """
        Apply Lukhas AGI patterns to enhance documentation quality.
        This could include:
        - Adjusting complexity based on bio-oscillator data
        - Adding cultural context
        - Preparing for voice synthesis
        """
        enhanced_sections = []
        for section in sections:
            # Adjust complexity if bio-oscillator data is available
            if config.bio_oscillator_data:
                optimal_complexity = self._calculate_optimal_complexity(
                    section, config.bio_oscillator_data
                )
                section.complexity_level = optimal_complexity

            # Add cultural context if specified
            if config.cultural_context:
                section = self._add_cultural_context(section, config.cultural_context)

            # Prepare for voice synthesis if enabled
            if config.voice_enabled:
                section = self._prepare_for_voice(section)

            enhanced_sections.append(section)

        return enhanced_sections

    def _calculate_optimal_complexity(
        self, section: DocSection, bio_data: dict[str, Any]
    ) -> int:
        """Calculate optimal complexity level based on bio-oscillator data."""
        # This would integrate with Lukhas's bio-oscillator
        base_complexity = section.complexity_level
        attention_level = bio_data.get("attention_level", 1.0)
        cognitive_load = bio_data.get("cognitive_load", 0.5)

        optimal = base_complexity * attention_level * (1 - cognitive_load)
        return max(1, min(5, round(optimal)))

    def _add_cultural_context(
        self, section: DocSection, cultural_context: str
    ) -> DocSection:
        """Add cultural context to documentation content."""
        # This would use Lukhas's cultural adaptation system
        # For now, just add cultural-specific examples or explanations
        if section.content:
            section.content += (
                f"\n\nCultural Note: Adapted for {cultural_context} context."
            )
        return section

    def _prepare_for_voice(self, section: DocSection) -> DocSection:
        """Prepare content for voice synthesis."""
        # Add voice synthesis markers
        if section.title:
            section.title = f"<voice-emphasis>{section.title}</voice-emphasis>"
        return section

    def _render_documentation(
        self, sections: list[DocSection], config: DocumentationConfig
    ) -> str:
        """Render final documentation using templates."""
        template_name = f"documentation.{config.output_format}.jinja2"
        template = self.template_env.get_template(template_name)

        return template.render(sections=sections, config=config)

    @staticmethod
    def _format_type_name(type_name: str) -> str:
        """Format type names for documentation."""
        return f"`{type_name}`"

    @staticmethod
    def _sanitize_markdown(text: str) -> str:
        """Sanitize text for markdown output."""
        if not text:
            return ""
        # Basic markdown sanitization
        return text.replace("<", "&lt;").replace(">", "&gt;")
