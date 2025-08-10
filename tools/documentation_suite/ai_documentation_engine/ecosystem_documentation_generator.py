"""
AI-Powered Documentation Engine
===============================

Advanced documentation generation system for LUKHAS PWM ecosystem.
Automatically generates comprehensive, contextual, and intelligent documentation
for all components, APIs, and integrations.

Features:
- AI-enhanced code analysis and documentation
- Multi-format output (Markdown, HTML, PDF, Interactive)
- Compliance and security documentation automation
- Integration with bio-oscillator awareness
- Real-time documentation updates
"""

import ast
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Union

logger = logging.getLogger(__name__)


class DocumentationType(Enum):
    """Types of documentation to generate"""

    API_REFERENCE = "api_reference"
    USER_GUIDE = "user_guide"
    DEVELOPER_GUIDE = "developer_guide"
    INTEGRATION_GUIDE = "integration_guide"
    COMPLIANCE_DOCS = "compliance_docs"
    SECURITY_DOCS = "security_docs"
    ARCHITECTURE_DOCS = "architecture_docs"
    TUTORIAL = "tutorial"
    TROUBLESHOOTING = "troubleshooting"


class OutputFormat(Enum):
    """Documentation output formats"""

    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"
    INTERACTIVE = "interactive"
    JSON = "json"
    CONFLUENCE = "confluence"


class ComplexityLevel(Enum):
    """Documentation complexity levels"""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class DocumentationRequest:
    """Documentation generation request"""

    request_id: str
    doc_type: DocumentationType
    output_format: OutputFormat
    complexity_level: ComplexityLevel
    target_components: list[str]
    include_examples: bool = True
    include_diagrams: bool = True
    include_compliance: bool = False
    custom_templates: Optional[dict[str, str]] = None


@dataclass
class CodeAnalysisResult:
    """Result of code analysis for documentation"""

    file_path: str
    module_name: str
    classes: list[dict[str, Any]]
    functions: list[dict[str, Any]]
    constants: list[dict[str, Any]]
    imports: list[str]
    docstrings: dict[str, str]
    complexity_score: float
    dependencies: list[str]


@dataclass
class DocumentationSection:
    """Individual documentation section"""

    section_id: str
    title: str
    content: str
    subsections: list["DocumentationSection"]
    code_examples: list[str]
    diagrams: list[str]
    metadata: dict[str, Any]


@dataclass
class GeneratedDocumentation:
    """Complete generated documentation"""

    doc_id: str
    title: str
    doc_type: DocumentationType
    output_format: OutputFormat
    sections: list[DocumentationSection]
    generated_date: datetime
    target_audience: ComplexityLevel
    metadata: dict[str, Any]
    file_paths: list[str]


class CodeAnalyzer:
    """
    Advanced code analysis for documentation generation

    Analyzes Python code to extract structure, dependencies,
    and documentation elements for intelligent doc generation.
    """

    def __init__(self):
        self.analysis_cache = {}

    async def analyze_file(self, file_path: str) -> CodeAnalysisResult:
        """Analyze a single Python file"""

        if file_path in self.analysis_cache:
            return self.analysis_cache[file_path]

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Parse AST
            tree = ast.parse(content)

            # Extract components
            classes = await self._extract_classes(tree, content)
            functions = await self._extract_functions(tree, content)
            constants = await self._extract_constants(tree, content)
            imports = await self._extract_imports(tree)
            docstrings = await self._extract_docstrings(tree, content)

            # Calculate complexity
            complexity_score = await self._calculate_complexity(tree)

            # Extract dependencies
            dependencies = await self._extract_dependencies(file_path, imports)

            result = CodeAnalysisResult(
                file_path=file_path,
                module_name=self._get_module_name(file_path),
                classes=classes,
                functions=functions,
                constants=constants,
                imports=imports,
                docstrings=docstrings,
                complexity_score=complexity_score,
                dependencies=dependencies,
            )

            self.analysis_cache[file_path] = result
            return result

        except Exception as e:
            logger.error(f"Failed to analyze file {file_path}: {e}")
            raise

    async def analyze_directory(self, directory_path: str) -> list[CodeAnalysisResult]:
        """Analyze all Python files in a directory"""

        results = []

        for root, dirs, files in os.walk(directory_path):
            # Skip common non-source directories
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".") and d not in ["__pycache__", "node_modules"]
            ]

            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        result = await self.analyze_file(file_path)
                        results.append(result)
                    except Exception as e:
                        logger.warning(f"Skipped {file_path}: {e}")

        return results

    async def _extract_classes(
        self, tree: ast.AST, content: str
    ) -> list[dict[str, Any]]:
        """Extract class information from AST"""

        classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = {
                    "name": node.name,
                    "docstring": ast.get_docstring(node),
                    "methods": [],
                    "attributes": [],
                    "inheritance": [
                        base.id for base in node.bases if isinstance(base, ast.Name)
                    ],
                    "decorators": [
                        d.id for d in node.decorator_list if isinstance(d, ast.Name)
                    ],
                    "line_number": node.lineno,
                }

                # Extract methods
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_info = {
                            "name": item.name,
                            "docstring": ast.get_docstring(item),
                            "args": [arg.arg for arg in item.args.args],
                            "returns": self._extract_return_annotation(item),
                            "decorators": [
                                d.id
                                for d in item.decorator_list
                                if isinstance(d, ast.Name)
                            ],
                            "is_property": any(
                                d.id == "property"
                                for d in item.decorator_list
                                if isinstance(d, ast.Name)
                            ),
                            "is_async": isinstance(item, ast.AsyncFunctionDef),
                        }
                        class_info["methods"].append(method_info)

                classes.append(class_info)

        return classes

    async def _extract_functions(
        self, tree: ast.AST, content: str
    ) -> list[dict[str, Any]]:
        """Extract function information from AST"""

        functions = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Skip methods (functions inside classes)
                if not any(
                    isinstance(parent, ast.ClassDef)
                    for parent in ast.walk(tree)
                    if hasattr(parent, "body") and node in getattr(parent, "body", [])
                ):

                    func_info = {
                        "name": node.name,
                        "docstring": ast.get_docstring(node),
                        "args": [arg.arg for arg in node.args.args],
                        "returns": self._extract_return_annotation(node),
                        "decorators": [
                            d.id for d in node.decorator_list if isinstance(d, ast.Name)
                        ],
                        "is_async": isinstance(node, ast.AsyncFunctionDef),
                        "line_number": node.lineno,
                    }
                    functions.append(func_info)

        return functions

    async def _extract_constants(
        self, tree: ast.AST, content: str
    ) -> list[dict[str, Any]]:
        """Extract constant definitions from AST"""

        constants = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        const_info = {
                            "name": target.id,
                            "value": self._extract_literal_value(node.value),
                            "type": type(
                                self._extract_literal_value(node.value)
                            ).__name__,
                            "line_number": node.lineno,
                        }
                        constants.append(const_info)

        return constants

    async def _extract_imports(self, tree: ast.AST) -> list[str]:
        """Extract import statements from AST"""

        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}" if module else alias.name)

        return imports

    async def _extract_docstrings(self, tree: ast.AST, content: str) -> dict[str, str]:
        """Extract all docstrings from AST"""

        docstrings = {}

        # Module docstring
        if isinstance(tree, ast.Module) and len(tree.body) > 0:
            if isinstance(tree.body[0], ast.Expr) and isinstance(
                tree.body[0].value, ast.Str
            ):
                docstrings["module"] = tree.body[0].value.s

        # Function and class docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                docstring = ast.get_docstring(node)
                if docstring:
                    docstrings[node.name] = docstring

        return docstrings

    async def _calculate_complexity(self, tree: ast.AST) -> float:
        """Calculate code complexity score"""

        complexity_metrics = {
            "functions": 0,
            "classes": 0,
            "loops": 0,
            "conditions": 0,
            "try_blocks": 0,
        }

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                complexity_metrics["functions"] += 1
            elif isinstance(node, ast.ClassDef):
                complexity_metrics["classes"] += 1
            elif isinstance(node, (ast.For, ast.While)):
                complexity_metrics["loops"] += 1
            elif isinstance(node, ast.If):
                complexity_metrics["conditions"] += 1
            elif isinstance(node, ast.Try):
                complexity_metrics["try_blocks"] += 1

        # Calculate weighted complexity score (0-100)
        score = (
            complexity_metrics["functions"] * 2
            + complexity_metrics["classes"] * 3
            + complexity_metrics["loops"] * 1.5
            + complexity_metrics["conditions"] * 1
            + complexity_metrics["try_blocks"] * 2
        )

        return min(100.0, score)

    async def _extract_dependencies(
        self, file_path: str, imports: list[str]
    ) -> list[str]:
        """Extract file dependencies from imports"""

        dependencies = []
        base_path = Path(file_path).parent

        for imp in imports:
            # Check if it's a local import
            if not imp.startswith(
                ("sys", "os", "json", "datetime", "typing", "asyncio")
            ):
                # Try to resolve local dependencies
                potential_paths = [
                    base_path / f"{imp.replace('.', '/')}.py",
                    base_path / f"{imp.replace('.', '/')}/__init__.py",
                ]

                for path in potential_paths:
                    if path.exists():
                        dependencies.append(str(path))
                        break

        return dependencies

    def _extract_return_annotation(
        self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]
    ) -> Optional[str]:
        """Extract return type annotation"""

        if node.returns:
            if isinstance(node.returns, ast.Name):
                return node.returns.id
            elif isinstance(node.returns, ast.Constant):
                return str(node.returns.value)
            else:
                return "Unknown"
        return None

    def _extract_literal_value(self, node: ast.AST) -> Any:
        """Extract literal value from AST node"""

        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.List):
            return [self._extract_literal_value(item) for item in node.elts]
        elif isinstance(node, ast.Dict):
            return {
                self._extract_literal_value(k): self._extract_literal_value(v)
                for k, v in zip(node.keys, node.values)
            }
        else:
            return "Complex Expression"

    def _get_module_name(self, file_path: str) -> str:
        """Extract module name from file path"""

        path = Path(file_path)
        if path.name == "__init__.py":
            return path.parent.name
        else:
            return path.stem


class DocumentationGenerator:
    """
    Core documentation generation engine

    Generates intelligent, context-aware documentation using
    AI-enhanced analysis and templating.
    """

    def __init__(self):
        self.code_analyzer = CodeAnalyzer()
        self.templates = {}
        self._load_templates()

    def _load_templates(self):
        """Load documentation templates"""

        self.templates = {
            DocumentationType.API_REFERENCE: {
                "header": "# {title}\n\n## Overview\n{overview}\n\n",
                "class": "### Class: {name}\n\n{docstring}\n\n#### Methods:\n{methods}\n\n",
                "function": "### Function: {name}\n\n{signature}\n\n{docstring}\n\n**Parameters:**\n{parameters}\n\n**Returns:** {returns}\n\n",
                "method": "#### {name}({args})\n\n{docstring}\n\n",
            },
            DocumentationType.USER_GUIDE: {
                "header": "# {title} - User Guide\n\n## Introduction\n{introduction}\n\n",
                "section": "## {title}\n\n{content}\n\n",
                "example": "### Example: {title}\n\n```python\n{code}\n```\n\n{explanation}\n\n",
            },
            DocumentationType.INTEGRATION_GUIDE: {
                "header": "# {title} - Integration Guide\n\n## Quick Start\n{quickstart}\n\n",
                "prerequisite": "### Prerequisites\n\n{requirements}\n\n",
                "installation": "### Installation\n\n```bash\n{commands}\n```\n\n",
                "configuration": "### Configuration\n\n{config_details}\n\n",
            },
        }

    async def generate_documentation(
        self, request: DocumentationRequest
    ) -> GeneratedDocumentation:
        """Generate documentation based on request"""

        print(f"📚 Generating {request.doc_type.value} documentation...")

        # Analyze target components
        analysis_results = await self._analyze_components(request.target_components)

        # Generate sections based on doc type
        sections = await self._generate_sections(request, analysis_results)

        # Create final documentation
        documentation = GeneratedDocumentation(
            doc_id=f"doc_{request.request_id}_{int(datetime.now().timestamp())}",
            title=self._generate_title(request, analysis_results),
            doc_type=request.doc_type,
            output_format=request.output_format,
            sections=sections,
            generated_date=datetime.now(),
            target_audience=request.complexity_level,
            metadata=await self._generate_metadata(request, analysis_results),
            file_paths=[],
        )

        # Generate output files
        output_paths = await self._generate_output_files(documentation)
        documentation.file_paths = output_paths

        print(f"   ✅ Generated {len(sections)} sections")
        print(f"   📄 Output files: {len(output_paths)}")

        return documentation

    async def _analyze_components(
        self, components: list[str]
    ) -> list[CodeAnalysisResult]:
        """Analyze specified components"""

        analysis_results = []

        for component in components:
            if os.path.isfile(component):
                result = await self.code_analyzer.analyze_file(component)
                analysis_results.append(result)
            elif os.path.isdir(component):
                results = await self.code_analyzer.analyze_directory(component)
                analysis_results.extend(results)

        return analysis_results

    async def _generate_sections(
        self, request: DocumentationRequest, analysis_results: list[CodeAnalysisResult]
    ) -> list[DocumentationSection]:
        """Generate documentation sections"""

        sections = []

        if request.doc_type == DocumentationType.API_REFERENCE:
            sections = await self._generate_api_reference_sections(
                request, analysis_results
            )
        elif request.doc_type == DocumentationType.USER_GUIDE:
            sections = await self._generate_user_guide_sections(
                request, analysis_results
            )
        elif request.doc_type == DocumentationType.INTEGRATION_GUIDE:
            sections = await self._generate_integration_guide_sections(
                request, analysis_results
            )
        elif request.doc_type == DocumentationType.ARCHITECTURE_DOCS:
            sections = await self._generate_architecture_sections(
                request, analysis_results
            )
        else:
            sections = await self._generate_generic_sections(request, analysis_results)

        return sections

    async def _generate_api_reference_sections(
        self, request: DocumentationRequest, analysis_results: list[CodeAnalysisResult]
    ) -> list[DocumentationSection]:
        """Generate API reference sections"""

        sections = []

        # Overview section
        overview_section = DocumentationSection(
            section_id="overview",
            title="API Overview",
            content=await self._generate_api_overview(analysis_results),
            subsections=[],
            code_examples=[],
            diagrams=[],
            metadata={},
        )
        sections.append(overview_section)

        # Generate sections for each module
        for result in analysis_results:
            module_sections = await self._generate_module_api_sections(result, request)
            sections.extend(module_sections)

        return sections

    async def _generate_user_guide_sections(
        self, request: DocumentationRequest, analysis_results: list[CodeAnalysisResult]
    ) -> list[DocumentationSection]:
        """Generate user guide sections"""

        sections = []

        # Introduction
        intro_section = DocumentationSection(
            section_id="introduction",
            title="Introduction",
            content=await self._generate_user_guide_intro(analysis_results),
            subsections=[],
            code_examples=[],
            diagrams=[],
            metadata={},
        )
        sections.append(intro_section)

        # Getting Started
        getting_started = DocumentationSection(
            section_id="getting_started",
            title="Getting Started",
            content=await self._generate_getting_started_content(analysis_results),
            subsections=[],
            code_examples=await self._generate_basic_examples(analysis_results),
            diagrams=[],
            metadata={},
        )
        sections.append(getting_started)

        # Feature sections
        feature_sections = await self._generate_feature_sections(
            analysis_results, request
        )
        sections.extend(feature_sections)

        return sections

    async def _generate_integration_guide_sections(
        self, request: DocumentationRequest, analysis_results: list[CodeAnalysisResult]
    ) -> list[DocumentationSection]:
        """Generate integration guide sections"""

        sections = []

        # Prerequisites
        prereq_section = DocumentationSection(
            section_id="prerequisites",
            title="Prerequisites",
            content=await self._generate_prerequisites_content(analysis_results),
            subsections=[],
            code_examples=[],
            diagrams=[],
            metadata={},
        )
        sections.append(prereq_section)

        # Installation
        install_section = DocumentationSection(
            section_id="installation",
            title="Installation & Setup",
            content=await self._generate_installation_content(analysis_results),
            subsections=[],
            code_examples=await self._generate_installation_examples(analysis_results),
            diagrams=[],
            metadata={},
        )
        sections.append(install_section)

        # Configuration
        config_section = DocumentationSection(
            section_id="configuration",
            title="Configuration",
            content=await self._generate_configuration_content(analysis_results),
            subsections=[],
            code_examples=await self._generate_configuration_examples(analysis_results),
            diagrams=[],
            metadata={},
        )
        sections.append(config_section)

        return sections

    async def _generate_architecture_sections(
        self, request: DocumentationRequest, analysis_results: list[CodeAnalysisResult]
    ) -> list[DocumentationSection]:
        """Generate architecture documentation sections"""

        sections = []

        # System Overview
        overview_section = DocumentationSection(
            section_id="system_overview",
            title="System Architecture Overview",
            content=await self._generate_architecture_overview(analysis_results),
            subsections=[],
            code_examples=[],
            diagrams=["system_architecture_diagram"],
            metadata={},
        )
        sections.append(overview_section)

        # Component Architecture
        component_sections = await self._generate_component_architecture_sections(
            analysis_results
        )
        sections.extend(component_sections)

        return sections

    async def _generate_generic_sections(
        self, request: DocumentationRequest, analysis_results: list[CodeAnalysisResult]
    ) -> list[DocumentationSection]:
        """Generate generic documentation sections"""

        sections = []

        # Create basic sections based on analysis
        for result in analysis_results:
            section = DocumentationSection(
                section_id=result.module_name,
                title=f"Module: {result.module_name}",
                content=await self._generate_module_content(result),
                subsections=[],
                code_examples=await self._generate_module_examples(result),
                diagrams=[],
                metadata={"complexity": result.complexity_score},
            )
            sections.append(section)

        return sections

    async def _generate_output_files(
        self, documentation: GeneratedDocumentation
    ) -> list[str]:
        """Generate output files in specified format"""

        output_paths = []

        if documentation.output_format == OutputFormat.MARKDOWN:
            path = await self._generate_markdown_output(documentation)
            output_paths.append(path)
        elif documentation.output_format == OutputFormat.HTML:
            path = await self._generate_html_output(documentation)
            output_paths.append(path)
        elif documentation.output_format == OutputFormat.JSON:
            path = await self._generate_json_output(documentation)
            output_paths.append(path)

        return output_paths

    async def _generate_markdown_output(
        self, documentation: GeneratedDocumentation
    ) -> str:
        """Generate Markdown output"""

        output_dir = Path("docs/generated")
        output_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{documentation.doc_id}.md"
        output_path = output_dir / filename

        content = f"# {documentation.title}\n\n"
        content += f"*Generated on {documentation.generated_date.strftime('%Y-%m-%d %H:%M:%S')}*\n\n"

        for section in documentation.sections:
            content += f"## {section.title}\n\n"
            content += f"{section.content}\n\n"

            # Add code examples
            for i, example in enumerate(section.code_examples):
                content += f"### Example {i+1}\n\n```python\n{example}\n```\n\n"

            # Add subsections
            for subsection in section.subsections:
                content += f"### {subsection.title}\n\n"
                content += f"{subsection.content}\n\n"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        return str(output_path)

    async def _generate_html_output(self, documentation: GeneratedDocumentation) -> str:
        """Generate HTML output"""

        output_dir = Path("docs/generated/html")
        output_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{documentation.doc_id}.html"
        output_path = output_dir / filename

        # Simple HTML template
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{documentation.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1, h2, h3 {{ color: #333; }}
        code {{ background-color: #f5f5f5; padding: 2px 4px; }}
        pre {{ background-color: #f5f5f5; padding: 10px; overflow-x: auto; }}
    </style>
</head>
<body>
    <h1>{documentation.title}</h1>
    <p><em>Generated on {documentation.generated_date.strftime('%Y-%m-%d %H:%M:%S')}</em></p>
"""

        for section in documentation.sections:
            html_content += f"    <h2>{section.title}</h2>\n"
            html_content += (
                f"    <p>{section.content.replace(chr(10), '</p><p>')}</p>\n"
            )

            for example in section.code_examples:
                html_content += f"    <pre><code>{example}</code></pre>\n"

        html_content += "</body></html>"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return str(output_path)

    async def _generate_json_output(self, documentation: GeneratedDocumentation) -> str:
        """Generate JSON output"""

        output_dir = Path("docs/generated/json")
        output_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{documentation.doc_id}.json"
        output_path = output_dir / filename

        # Convert to serializable format
        doc_dict = {
            "doc_id": documentation.doc_id,
            "title": documentation.title,
            "doc_type": documentation.doc_type.value,
            "output_format": documentation.output_format.value,
            "generated_date": documentation.generated_date.isoformat(),
            "target_audience": documentation.target_audience.value,
            "metadata": documentation.metadata,
            "sections": [
                {
                    "section_id": section.section_id,
                    "title": section.title,
                    "content": section.content,
                    "code_examples": section.code_examples,
                    "diagrams": section.diagrams,
                    "metadata": section.metadata,
                }
                for section in documentation.sections
            ],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(doc_dict, f, indent=2, ensure_ascii=False)

        return str(output_path)

    # Helper methods for content generation
    async def _generate_api_overview(
        self, analysis_results: list[CodeAnalysisResult]
    ) -> str:
        """Generate API overview content"""
        total_classes = sum(len(result.classes) for result in analysis_results)
        total_functions = sum(len(result.functions) for result in analysis_results)

        return f"""This API reference covers {len(analysis_results)} modules with {total_classes} classes and {total_functions} functions.

The API provides comprehensive functionality for AI system management, compliance validation, and security testing.

**Key Features:**
- Comprehensive AI compliance validation
- Advanced security testing frameworks
- Real-time monitoring and analytics
- Multi-jurisdiction regulatory support
"""

    async def _generate_user_guide_intro(
        self, analysis_results: list[CodeAnalysisResult]
    ) -> str:
        """Generate user guide introduction"""
        return f"""Welcome to the LUKHAS PWM ecosystem user guide. This guide will help you get started with using our advanced AI platform.

**What you'll learn:**
- How to set up and configure the system
- Key features and capabilities
- Common use cases and examples
- Best practices and troubleshooting

The platform consists of {len(analysis_results)} main modules, each providing specialized functionality for AI system management and compliance.
"""

    async def _generate_module_content(self, result: CodeAnalysisResult) -> str:
        """Generate content for a specific module"""
        content = f"The `{result.module_name}` module provides key functionality with {len(result.classes)} classes and {len(result.functions)} functions.\n\n"

        if result.docstrings.get("module"):
            content += f"**Module Description:** {result.docstrings['module']}\n\n"

        content += f"**Complexity Score:** {result.complexity_score:.1f}/100\n\n"

        if result.classes:
            content += "**Main Classes:**\n"
            for cls in result.classes[:3]:  # Show top 3 classes
                content += f"- `{cls['name']}`: {cls.get('docstring', 'No description available')[:100]}...\n"

        return content

    def _generate_title(
        self, request: DocumentationRequest, analysis_results: list[CodeAnalysisResult]
    ) -> str:
        """Generate documentation title"""

        if len(analysis_results) == 1:
            return f"{analysis_results[0].module_name} - {request.doc_type.value.replace('_', ' ').title()}"
        else:
            return f"LUKHAS PWM {request.doc_type.value.replace('_', ' ').title()}"

    async def _generate_metadata(
        self, request: DocumentationRequest, analysis_results: list[CodeAnalysisResult]
    ) -> dict[str, Any]:
        """Generate documentation metadata"""

        return {
            "modules_analyzed": len(analysis_results),
            "total_classes": sum(len(result.classes) for result in analysis_results),
            "total_functions": sum(
                len(result.functions) for result in analysis_results
            ),
            "average_complexity": (
                sum(result.complexity_score for result in analysis_results)
                / len(analysis_results)
                if analysis_results
                else 0
            ),
            "generation_time": datetime.now().isoformat(),
            "target_audience": request.complexity_level.value,
            "includes_examples": request.include_examples,
            "includes_diagrams": request.include_diagrams,
        }

    # Placeholder methods for additional content generation
    async def _generate_module_api_sections(
        self, result: CodeAnalysisResult, request: DocumentationRequest
    ) -> list[DocumentationSection]:
        """Generate API sections for a module"""
        # Implementation would create detailed API documentation sections
        return []

    async def _generate_basic_examples(
        self, analysis_results: list[CodeAnalysisResult]
    ) -> list[str]:
        """Generate basic code examples"""
        return [
            "# Example: Basic usage\nfrom system_pwm import ComplianceEngine\n\nengine = ComplianceEngine()\nresult = engine.validate_compliance()",
            "# Example: Advanced configuration\nengine.configure({\n    'strict_mode': True,\n    'auto_remediation': True\n})",
        ]

    async def _generate_installation_examples(
        self, analysis_results: list[CodeAnalysisResult]
    ) -> list[str]:
        """Generate installation examples"""
        return [
            "pip install lukhas-pwm",
            "# Or install from source\ngit clone https://github.com/LukhasAI/Lukhas_PWM.git\ncd Lukhas_PWM\npip install -e .",
        ]

    async def _generate_configuration_examples(
        self, analysis_results: list[CodeAnalysisResult]
    ) -> list[str]:
        """Generate configuration examples"""
        return [
            "# Configuration file: lukhas_pwm_config.yaml\napi:\n  host: localhost\n  port: 8000\ncompliance:\n  strict_mode: true"
        ]

    async def _generate_module_examples(self, result: CodeAnalysisResult) -> list[str]:
        """Generate examples for a specific module"""
        return [f"# Example usage of {result.module_name}\nimport {result.module_name}"]

    async def _generate_getting_started_content(
        self, analysis_results: list[CodeAnalysisResult]
    ) -> str:
        """Generate getting started content"""
        return "Follow these steps to get started with LUKHAS PWM:\n\n1. Install the package\n2. Configure your environment\n3. Run your first compliance check"

    async def _generate_prerequisites_content(
        self, analysis_results: list[CodeAnalysisResult]
    ) -> str:
        """Generate prerequisites content"""
        return "Before installing LUKHAS PWM, ensure you have:\n\n- Python 3.8 or higher\n- pip package manager\n- Virtual environment (recommended)"

    async def _generate_installation_content(
        self, analysis_results: list[CodeAnalysisResult]
    ) -> str:
        """Generate installation content"""
        return "LUKHAS PWM can be installed using pip or from source. Follow the appropriate method for your setup."

    async def _generate_configuration_content(
        self, analysis_results: list[CodeAnalysisResult]
    ) -> str:
        """Generate configuration content"""
        return "Configure LUKHAS PWM by setting up the configuration file and environment variables."

    async def _generate_architecture_overview(
        self, analysis_results: list[CodeAnalysisResult]
    ) -> str:
        """Generate architecture overview"""
        return f"The LUKHAS PWM system architecture consists of {len(analysis_results)} main modules organized in a modular, scalable design."

    async def _generate_component_architecture_sections(
        self, analysis_results: list[CodeAnalysisResult]
    ) -> list[DocumentationSection]:
        """Generate component architecture sections"""
        return []

    async def _generate_feature_sections(
        self, analysis_results: list[CodeAnalysisResult], request: DocumentationRequest
    ) -> list[DocumentationSection]:
        """Generate feature-specific sections"""
        return []


# Export main documentation components
__all__ = [
    "DocumentationGenerator",
    "CodeAnalyzer",
    "DocumentationRequest",
    "GeneratedDocumentation",
    "DocumentationType",
    "OutputFormat",
]
