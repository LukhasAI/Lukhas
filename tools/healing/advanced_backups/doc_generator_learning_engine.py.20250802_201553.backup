# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: doc_generator_learning_engine.py
# MODULE: learning.doc_generator_learning_engine
# DESCRIPTION: Implements an intelligent documentation generation engine that learns
#              and adapts, integrating with LUKHAS AI capabilities and knowledge graph.
# DEPENDENCIES: typing, pathlib, ast, jinja2, pydantic, structlog, symbolic_knowledge_core
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════
# ΛORIGIN_AGENT: Jules-04
# ΛTASK_ID: 171-176
# ΛCOMMIT_WINDOW: pre-audit
# ΛAPPROVED_BY: Human Overseer (GRDM)
# ΛUDIT: Standardized header/footer, added comments, normalized logger to structlog, applied ΛTAGs. Corrected class name conflicts.

"""
Documentation Generation Engine
Implements intelligent documentation generation with Lukhas AI capabilities.
"""

import structlog # ΛTRACE: Using structlog for structured logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import ast
import jinja2
from pydantic import BaseModel

# AIMPORT_TODO: Verify this relative import path is correct and standard.
# Consider if symbolic_knowledge_core should be a top-level import if it's a separate package.
# Assuming SystemKnowledgeGraph, NodeType, RelationshipType, SKGNode, SKGRelationship are correctly imported
from ..symbolic_knowledge_core.knowledge_graph import (
    SystemKnowledgeGraph,
    NodeType,
    RelationshipType,
    SKGNode,
    SKGRelationship # Added SKGRelationship as it's used
)

# ΛTRACE: Initialize logger for learning phase
logger = structlog.get_logger().bind(tag="learning_phase")

# # Data model for a documentation section
# ΛEXPOSE: This model defines the structure of documentation sections, likely used by other components.
class DocSection(BaseModel): # Renamed from DocGeneratorLearningEngine to avoid conflict
    """Represents a section of generated documentation."""
    title: str
    content: str
    section_type: str # e.g., 'module', 'class', 'function'
    metadata: Dict[str, Any] = {}
    subsections: List['DocSection'] = [] # type: ignore # Self-referential, Pydantic handles this
    importance_score: float = 1.0
    complexity_level: int = 1

# # Data model for documentation generation configuration
# ΛEXPOSE: Configuration settings for the documentation engine.
class DocumentationConfig(BaseModel): # Renamed from DocGeneratorLearningEngine
    """Configuration for documentation generation."""
    # ΛSEED: Default config values act as seeds for generation behavior.
    output_format: str = "markdown"
    include_examples: bool = True
    complexity_level: int = 1
    cultural_context: Optional[str] = None
    voice_enabled: bool = False
    bio_oscillator_data: Optional[Dict[str, Any]] = None
    template_overrides: Optional[Dict[str, str]] = None

class DocGeneratorLearningEngine:
    """
# # Core Documentation Generation Engine class
# ΛEXPOSE: Main class for generating documentation.
class DocGeneratorLearningEngine:
    """
    Core documentation generation engine that integrates with Lukhas AI capabilities.
    Learns from source code structure and (potentially) usage patterns to improve documentation.
    """

    # # Initialization
    def __init__(self,
                 skg: SystemKnowledgeGraph,
                 template_dir: Optional[str] = None):
        # ΛNOTE: Initializes with a SystemKnowledgeGraph and template directory.
        # ΛSEED: The initial SystemKnowledgeGraph (skg) can be considered a seed of knowledge.
        self.skg = skg

        template_path = template_dir or Path(__file__).parent / "templates"
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(template_path)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        self.template_env.filters['format_type'] = self._format_type_name
        self.template_env.filters['sanitize_markdown'] = self._sanitize_markdown
        # ΛTRACE: DocGeneratorLearningEngine initialized
        logger.info("doc_generator_learning_engine_initialized", template_path=str(template_path), skg_node_count=len(self.skg.nodes) if self.skg and hasattr(self.skg, 'nodes') else 0)

    # # Main documentation generation method
    # ΛEXPOSE: Primary method to generate documentation.
    def generate_documentation(self,
                            source_path: str,
                            config: DocumentationConfig) -> str:
        """
        Generate comprehensive documentation for a given source.
        Uses Lukhas's intelligence to structure and present information optimally.
        """
        # ΛDREAM_LOOP: The process of analysis, generation, and enhancement can be seen as a learning loop if it adapts over time.
        # ΛTRACE: Starting documentation generation
        logger.info("documentation_generation_start", source_path=source_path, config=config.model_dump_json())
        try:
            self._analyze_source(source_path)
            sections = self._generate_sections(config)
            # ΛDREAM_LOOP: Enhancement patterns could adapt based on feedback or observed utility.
            sections = self._enhance_with_lukhas_patterns(sections, config) # Corrected: Lukhas
            doc_content = self._render_documentation(sections, config)
            # ΛTRACE: Documentation generation successful
            logger.info("documentation_generation_success", source_path=source_path, output_length=len(doc_content))
            return doc_content
        except Exception as e:
            # ΛTRACE: Documentation generation failed
            logger.error("documentation_generation_failed", source_path=source_path, error=str(e), exc_info=True)
            raise

    # # Analyze source code (Python specific for now)
    def _analyze_source(self, source_path: str):
        """Analyze source code and build the knowledge graph."""
        # ΛNOTE: Currently supports Python files. Could be extended.
        # ΛTRACE: Analyzing source
        logger.debug("analyzing_source_start", source_path=source_path)
        if source_path.endswith('.py'):
            self._analyze_python_file(source_path)
        # ΛTRACE: Source analysis finished
        logger.debug("analyzing_source_end", source_path=source_path)

    # # Analyze a Python file using AST
    def _analyze_python_file(self, file_path: str):
        """Analyze a Python file and update the knowledge graph."""
        # ΛNOTE: Uses AST (Abstract Syntax Tree) for Python code analysis.
        # ΛTRACE: Analyzing Python file
        logger.debug("analyzing_python_file_start", file_path=file_path)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
                tree = ast.parse(source_code)

            module_docstring = ast.get_docstring(tree)
            module_node_id = file_path
            module_node = SKGNode(
                id=module_node_id,
                node_type=NodeType.MODULE,
                name=Path(file_path).stem,
                description=module_docstring if module_docstring else "",
                source_location=file_path
            )
            self.skg.add_node(module_node)
            # ΛTRACE: Added module node to SKG
            logger.debug("module_node_added_to_skg", node_id=module_node_id, name=module_node.name)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self._process_class(node, file_path, module_node_id)
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Check if it's a top-level function (not a method within a class)
                    is_top_level_function = True
                    for parent in ast.walk(tree): # More robust parent check
                        if hasattr(parent, 'body'):
                            if isinstance(parent.body, list) and node in parent.body and isinstance(parent, ast.ClassDef):
                                is_top_level_function = False
                                break
                        if hasattr(parent, 'orelse') and isinstance(parent.orelse, list) and node in parent.orelse: # e.g. in if/else, for/else
                             if isinstance(parent, ast.ClassDef):
                                is_top_level_function = False
                                break
                    if is_top_level_function and not any(isinstance(p, ast.ClassDef) for p in ast.iter_parents(node)): # Simpler check for direct parent
                         self._process_function(node, file_path, module_node_id)


        except Exception as e:
            # ΛTRACE: Python file analysis failed
            logger.error("python_file_analysis_failed", file_path=file_path, error=str(e), exc_info=True)
            raise

    # # Process a class definition
    def _process_class(self, node: ast.ClassDef, file_path: str, module_id: str):
        """Process a class definition and add it to the knowledge graph."""
        # ΛNOTE: Extracts class information including docstrings, decorators, and base classes.
        class_id = f"{module_id}::{node.name}"
        class_node = SKGNode(
            id=class_id, node_type=NodeType.CLASS, name=node.name,
            description=ast.get_docstring(node) or "",
            source_location=file_path,
            properties={
                "line_number": node.lineno,
                "decorators": [d.id for d in node.decorator_list if isinstance(d, ast.Name)],
                "bases": [b.id for b in node.bases if isinstance(b, ast.Name)]
            }
        )
        self.skg.add_node(class_node)
        # ΛTRACE: Added class node to SKG
        logger.debug("class_node_added_to_skg", node_id=class_id, name=node.name)
        self.skg.add_relationship(SKGRelationship(source_id=module_id, target_id=class_id, type=RelationshipType.CONTAINS))

        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._process_function(item, file_path, class_id)

    # # Process a function or method definition
    def _process_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef, file_path: str, parent_id: str):
        """Process a function definition and add it to the knowledge graph."""
        # ΛNOTE: Extracts function/method details like signature, docstring, async status, decorators.
        func_id = f"{parent_id}::{node.name}"
        returns_type = self._extract_type_hint(node.returns) if node.returns else "Any"
        args_info = self._process_arguments(node.args)
        parent_node = self.skg.get_node_by_id(parent_id)
        is_method_flag = parent_node.node_type == NodeType.CLASS if parent_node else False


        func_node = SKGNode(
            id=func_id, node_type=NodeType.FUNCTION, name=node.name,
            description=ast.get_docstring(node) or "",
            source_location=file_path,
            properties={
                "line_number": node.lineno, "is_async": isinstance(node, ast.AsyncFunctionDef),
                "decorators": [d.id for d in node.decorator_list if isinstance(d, ast.Name)],
                "arguments": args_info, "returns": returns_type,
                "is_method": is_method_flag
            }
        )
        self.skg.add_node(func_node)
        # ΛTRACE: Added function/method node to SKG
        logger.debug("function_node_added_to_skg", node_id=func_id, name=node.name, parent_id=parent_id, is_method=is_method_flag)
        self.skg.add_relationship(SKGRelationship(source_id=parent_id, target_id=func_id, type=RelationshipType.CONTAINS))

    # # Extract type hint from AST node
    def _extract_type_hint(self, node: Optional[ast.AST]) -> str:
        """Extract type hint information from AST node."""
        # ΛNOTE: Helper to parse type hints from code.
        if node is None: return "Any"
        if isinstance(node, ast.Name): return node.id
        elif isinstance(node, ast.Subscript):
            base_node = node.value
            slice_node = node.slice
            base_str = self._extract_type_hint(base_node)
            slice_str = self._extract_type_hint(slice_node)
            return f"{base_str}[{slice_str}]"
        elif isinstance(node, ast.Constant) and node.value is None: return "None"
        elif isinstance(node, ast.Tuple): # For Tuple[int, str]
            elements = [self._extract_type_hint(el) for el in node.elts]
            return f"Tuple[{', '.join(elements)}]"
        # ΛCAUTION: This might not cover all complex type hint cases (e.g., Union, Callable).
        # ΛTRACE: Extracted type hint (or default)
        # logger.debug("type_hint_extracted", raw_node_type=type(node).__name__, extracted_hint="complex")
        return ast.unparse(node) if hasattr(ast, 'unparse') else "Any" # Fallback to unparse or Any

    # # Process function arguments
    def _process_arguments(self, args: ast.arguments) -> Dict[str, Any]:
        """Process function arguments and their type hints."""
        # ΛNOTE: Extracts argument names and type hints.
        processed_args = []
        # Positional and keyword arguments
        all_args = args.posonlyargs + args.args
        for arg in all_args:
            processed_args.append({"name": arg.arg, "type": self._extract_type_hint(arg.annotation)})
        # Keyword-only arguments
        for arg in args.kwonlyargs:
             processed_args.append({"name": arg.arg, "type": self._extract_type_hint(arg.annotation), "kwonly": True})

        # ΛTRACE: Processed function arguments
        # logger.debug("function_arguments_processed", num_args=len(processed_args))
        return {
            "args": processed_args,
            "vararg": {"name": args.vararg.arg, "type": self._extract_type_hint(args.vararg.annotation)} if args.vararg else None,
            "kwarg": {"name": args.kwarg.arg, "type": self._extract_type_hint(args.kwarg.annotation)} if args.kwarg else None,
        }

    # # Generate documentation sections from SKG
    def _generate_sections(self, config: DocumentationConfig) -> List[DocSection]:
        """Generate documentation sections from the knowledge graph."""
        # ΛNOTE: Traverses the SKG to create a hierarchical structure of DocSection objects.
        # ΛTRACE: Generating documentation sections from SKG
        logger.info("generating_sections_from_skg_start")
        sections = []
        if self.skg:
            for module_node in self.skg.find_nodes_by_type(NodeType.MODULE):
                sections.append(self._generate_module_section(module_node, config))
        # ΛTRACE: Documentation sections generated
        logger.info("generating_sections_from_skg_end", num_top_level_sections=len(sections))
        return sections

    # # Generate section for a module
    def _generate_module_section(self, module_node: SKGNode, config: DocumentationConfig) -> DocSection:
        """Generate documentation section for a module."""
        # ΛNOTE: Creates a DocSection for a module, including its classes and top-level functions.
        # ΛTRACE: Generating module section
        logger.debug("generating_module_section_start", module_name=module_node.name)
        subsections = []
        if self.skg:
            for connected_node_id in self.skg.get_connected_nodes(module_node.id, RelationshipType.CONTAINS):
                connected_node = self.skg.get_node_by_id(connected_node_id)
                if connected_node:
                    if connected_node.node_type == NodeType.CLASS:
                        subsections.append(self._generate_class_section(connected_node, config))
                    elif connected_node.node_type == NodeType.FUNCTION:
                        subsections.append(self._generate_function_section(connected_node, config))

        module_section = DocSection(
            title=f"Module: {module_node.name}", content=module_node.description or "",
            section_type="module", metadata={"source_location": module_node.source_location},
            subsections=subsections
        )
        # ΛTRACE: Module section generated
        logger.debug("generating_module_section_end", module_name=module_node.name, num_subsections=len(module_section.subsections))
        return module_section

    # # Generate section for a class
    def _generate_class_section(self, class_node: SKGNode, config: DocumentationConfig) -> DocSection:
        """Generate documentation section for a class."""
        # ΛNOTE: Creates a DocSection for a class, including its methods.
        # ΛTRACE: Generating class section
        logger.debug("generating_class_section_start", class_name=class_node.name)
        subsections = []
        if self.skg:
            for method_node_id in self.skg.get_connected_nodes(class_node.id, RelationshipType.CONTAINS):
                method_node = self.skg.get_node_by_id(method_node_id)
                if method_node and method_node.node_type == NodeType.FUNCTION:
                    subsections.append(self._generate_function_section(method_node, config))

        class_section = DocSection(
            title=f"Class: {class_node.name}", content=class_node.description or "",
            section_type="class", metadata={"source_location": class_node.source_location, "properties": class_node.properties},
            subsections=subsections
        )
        # ΛTRACE: Class section generated
        logger.debug("generating_class_section_end", class_name=class_node.name, num_methods=len(class_section.subsections))
        return class_section

    # # Generate section for a function/method
    def _generate_function_section(self, func_node: SKGNode, config: DocumentationConfig) -> DocSection:
        """Generate documentation section for a function/method."""
        # ΛNOTE: Creates a DocSection for a function or method.
        # ΛTRACE: Generating function/method section
        logger.debug("generating_function_section_start", func_name=func_node.name)
        props = func_node.properties if func_node.properties else {}
        signature = self._build_function_signature(func_node.name, props.get("arguments", {}))
        title_prefix = "Method" if props.get("is_method") else "Function"
        if props.get("is_async"): title_prefix = f"async {title_prefix.lower()}"

        return DocSection(
            title=f"{title_prefix}: {signature}", content=func_node.description or "",
            section_type="function", metadata={"source_location": func_node.source_location, "properties": props}
        )

    # # Build function signature string
    def _build_function_signature(self, name: str, args_info: Dict[str, Any]) -> str:
        """Build a function signature string."""
        # ΛNOTE: Formats a human-readable function signature.
        parts = []
        for arg_detail in args_info.get("args", []):
            arg_str = arg_detail["name"]
            if arg_detail.get("type") and arg_detail["type"] != "Any":
                arg_str += f": {arg_detail['type']}"
            if arg_detail.get("kwonly"): # Not standard but for clarity if needed
                 arg_str = f"*, {arg_str}" # Simplified representation
            parts.append(arg_str)

        if args_info.get("vararg"):
            vararg_info = args_info["vararg"]
            vararg_str = f"*{vararg_info['name']}"
            if vararg_info.get("type") and vararg_info["type"] != "Any":
                vararg_str += f": {vararg_info['type']}"
            parts.append(vararg_str)

        if args_info.get("kwarg"):
            kwarg_info = args_info["kwarg"]
            kwarg_str = f"**{kwarg_info['name']}"
            if kwarg_info.get("type") and kwarg_info["type"] != "Any":
                kwarg_str += f": {kwarg_info['type']}"
            parts.append(kwarg_str)

        return f"{name}({', '.join(parts)})"

    # # Enhance documentation with LUKHAS patterns
    def _enhance_with_lukhas_patterns(self, sections: List[DocSection], config: DocumentationConfig) -> List[DocSection]: # Corrected: Lukhas
        """
        Apply Lukhas AI patterns to enhance documentation quality.
        """
        # ΛNOTE: Placeholder for more advanced LUKHAS AI enhancements.
        # ΛDREAM_LOOP: This step could involve adaptive learning based on documentation effectiveness or user feedback.
        # ΛTRACE: Enhancing sections with LUKHAS patterns
        logger.info("enhancing_sections_with_lukhas_patterns_start", num_sections=len(sections))
        enhanced_sections = []
        for section in sections:
            current_section = section.model_copy(deep=True) # Use model_copy for Pydantic models
            if config.bio_oscillator_data: # ΛNOTE: Using bio-oscillator data for adaptive complexity.
                current_section.complexity_level = self._calculate_optimal_complexity(current_section, config.bio_oscillator_data)
            if config.cultural_context:
                current_section = self._add_cultural_context(current_section, config.cultural_context)
            if config.voice_enabled:
                current_section = self._prepare_for_voice(current_section)
            if current_section.subsections: # Recursively enhance subsections
                current_section.subsections = self._enhance_with_lukhas_patterns(current_section.subsections, config)
            enhanced_sections.append(current_section)
        # ΛTRACE: Sections enhanced
        logger.info("enhancing_sections_with_lukhas_patterns_end", num_enhanced_sections=len(enhanced_sections))
        return enhanced_sections

    # # Calculate optimal complexity (placeholder)
    def _calculate_optimal_complexity(self, section: DocSection, bio_data: Dict[str, Any]) -> int:
        """Calculate optimal complexity level based on bio-oscillator data."""
        # ΛCAUTION: Simplified calculation. Real integration would be more complex.
        # ΛTRACE: Calculating optimal complexity
        logger.debug("calculating_optimal_complexity", section_title=section.title, bio_data_keys=list(bio_data.keys()))
        base_complexity = section.complexity_level
        attention_level = bio_data.get("attention_level", 1.0)
        cognitive_load = bio_data.get("cognitive_load", 0.5)
        optimal = base_complexity * attention_level * (1 - cognitive_load)
        return max(1, min(5, round(optimal)))

    # # Add cultural context (placeholder)
    def _add_cultural_context(self, section: DocSection, cultural_context: str) -> DocSection:
        """Add cultural context to documentation content."""
        # ΛCAUTION: Basic placeholder for cultural adaptation.
        # ΛTRACE: Adding cultural context
        logger.debug("adding_cultural_context", section_title=section.title, context=cultural_context)
        if section.content: # Ensure content is not None
            section.content += f"\n\nCultural Note ({cultural_context}): This information may be interpreted differently based on regional customs."
        return section

    # # Prepare content for voice synthesis (placeholder)
    def _prepare_for_voice(self, section: DocSection) -> DocSection:
        """Prepare content for voice synthesis."""
        # ΛCAUTION: Very basic SSML-like tagging.
        # ΛTRACE: Preparing for voice synthesis
        logger.debug("preparing_for_voice", section_title=section.title)
        if section.title:
            section.title = f"<speak><emphasis level='strong'>{self._sanitize_markdown(section.title)}</emphasis></speak>"
        return section

    # # Render final documentation using Jinja2 templates
    def _render_documentation(self, sections: List[DocSection], config: DocumentationConfig) -> str:
        """Render final documentation using templates."""
        # ΛNOTE: Uses Jinja2 for flexible templating.
        # ΛTRACE: Rendering documentation
        logger.info("rendering_documentation_start", num_sections=len(sections), output_format=config.output_format)
        template_name = f"documentation.{config.output_format}.jinja2"
        try:
            template = self.template_env.get_template(template_name)
        except jinja2.exceptions.TemplateNotFound:
            # ΛTRACE: Template not found, using default.
            logger.warn("template_not_found_fallback", template_name=template_name, fallback_template="default.markdown.jinja2")
            default_template_name = "default.markdown.jinja2" # Ensure this exists or handle more gracefully
            try:
                template = self.template_env.get_template(default_template_name)
            except jinja2.exceptions.TemplateNotFound:
                logger.error("default_template_not_found_critical", template_name=default_template_name)
                return f"Error: Critical default template '{default_template_name}' not found. Cannot render documentation."


        rendered_doc = template.render(sections=sections, config=config.model_dump()) # Use model_dump for pydantic
        # ΛTRACE: Documentation rendered
        logger.info("rendering_documentation_end", output_length=len(rendered_doc))
        return rendered_doc

    # # Jinja2 filter for formatting type names
    @staticmethod
    def _format_type_name(type_name: Optional[str]) -> str: # Made type_name optional
        if not type_name: return ""
        return f"`{type_name}`"

    # # Jinja2 filter for sanitizing Markdown
    @staticmethod
    def _sanitize_markdown(text: Optional[str]) -> str: # Made text optional
        if not text: return ""
        return text.replace("<", "&lt;").replace(">", "&gt;") # Basic sanitization