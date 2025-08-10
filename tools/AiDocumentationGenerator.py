#!/usr/bin/env python3
"""
LUKHlukhasS AI System - AI-Powered Documentation Generator
File: ai_documentation_generator.py
Path: tools/ai_documentation_generator.py
Created: 2025-06-05 12:00:00
Author: LUKHlukhasS AI Team
Version: 1.0

This file is part of the LUKHlukhasS (LUKHlukhasS Universal Knowledge & Holistic AI System)
Advanced Cognitive Architecture for Artificial General Intelligence

Copyright (c) 2025 LUKHlukhasS AI Research. All rights reserved.
Licensed under the LUKHlukhasS Core License - see LICENSE.md for details.
"""

import argparse
import ast
import asyncio
import json
import logging
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from typing import Optional

# Global constant for symbolic memory directory
SYMBOLIC_MEMORY_DIR = ".lukhas"
os.makedirs(SYMBOLIC_MEMORY_DIR, exist_ok=True)

# OpenAI imports and configuration
try:
    from openai import OpenAI

    HAS_OPENAI = True

    # Load environment variables manually

    def load_env():
        env_path = Path(".env")
        if env_path.exists():
            with open(env_path, encoding="utf-8") as f:
                for line in f:
                    if line.strip() and not line.startswith("#"):
                        key, value = line.strip().split("=", 1)
                        os.environ[key] = value

    load_env()

    # Configure OpenAI client
    openai_client = None
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        openai_client = OpenAI(api_key=openai_api_key)
    else:
        print("Warning: OPENAI_API_KEY not found in environment variables")
        HAS_OPENAI = False

except ImportError:
    HAS_OPENAI = False
    openai_client = None
    print("Warning: OpenAI not installed. Install with: pip install openai")


@dataclass
class CodeAnalysis:
    """Comprehensive code analysis structure"""

    file_path: str
    module_name: str
    classes: list[dict[str, Any]]
    functions: list[dict[str, Any]]
    imports: list[str]
    exports: list[str]
    dependencies: list[str]
    constants: list[str]
    docstrings: list[str]
    complexity_score: int
    paradigm: str  # 'symbolic', 'neural', 'quantum', 'hybrid'
    lukhας_components: list[str]  # DAST, NIAS, ABAS, Lukhas_ID, etc.


@dataclass
class DocumentationSection:
    """Rich documentation section"""

    title: str
    content: str
    metadata: Optional[dict[str, Any]] = None


class AIDocumentationGenerator:
    """AI-powered documentation generator with LUKHlukhasS consciousness"""

    def __init__(
        self, custom_api_key: Optional[str] = None, model: str = "gpt-4-turbo-preview"
    ):
        self.api_key = custom_api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.logger = logging.getLogger("LukhasDocGen")
        self.client = None

        # LUKHlukhasS-specific patterns
        self.lukhας_patterns = {
            "symbolic": r"symbolic|memoria|reflection|dast|arbitrat",
            "neural": r"neural|learning|cognitive|brain|spine",
            "quantum": r"quantum|oscillator|consensus|enhanced",
            "identity": r"lambda_identity|Lukhas_ID|identity|auth|verification",
            "systems": r"nias|abas|dast|engine|orchestrator",
            "commercial": r"vendor|affiliate|commercial|payment",
        }

        # Documentation templates
        self.templates = self._load_templates()

        if not HAS_OPENAI:
            self.logger.error(
                "❌ OpenAI package not installed. Install with: pip install openai"
            )
            return

        if not self.api_key:
            self.logger.error(
                "❌ OpenAI API key not found. Set OPENAI_API_KEY environment variable"
            )
            return

        try:
            self.client = OpenAI(api_key=self.api_key)
            # Test the client with a simple request
            self.client.models.list()
            self.logger.info("✅ AI Documentation Generator initialized with OpenAI")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize OpenAI client: {str(e)}")
            self.client = None

    def log_symbolic_memory(self, filename, summary, tags):
        memory = {
            "file": filename,
            "summary": summary,
            "tags": tags,
            "timestamp": datetime.utcnow().isoformat(),
        }
        with open(os.path.join(SYMBOLIC_MEMORY_DIR, "memoria.jsonl"), "a") as f:
            f.write(json.dumps(memory) + "\n")

    def write_symbolic_trail(self, components):
        trail = {"timestamp": datetime.utcnow().isoformat(), "components": components}
        with open(os.path.join(SYMBOLIC_MEMORY_DIR, "symbolic_trail.jsonl"), "a") as f:
            f.write(json.dumps(trail, indent=2) + "\n")

    def run(self, target_path):
        """
        Run documentation generation for a file or directory, with symbolic memory logging.
        """
        # Determine if target_path is file or directory
        path = Path(target_path)
        all_collected_components = []
        py_files = list(path.rglob("*.py")) if path.is_dir() else [path]
        for file in py_files:
            try:
                loop = asyncio.get_event_loop()
                analysis = loop.run_until_complete(self.analyze_file(file))
                doc_sections = loop.run_until_complete(
                    self.generate_documentation_sections(analysis)
                )
                # Compose a summary for symbolic memory
                doc_summary = next(
                    (
                        section
                        for section in doc_sections
                        if section.title == "Overview"
                    ),
                    None,
                )
                summary_text = doc_summary.content[:512] if doc_summary else ""
                self.log_symbolic_memory(
                    str(file), summary_text, tags=["docgen", "symbolic", "GPT"]
                )
                # Collect for symbolic trail
                components = {
                    "file": str(file),
                    "module": analysis.module_name,
                    "paradigm": analysis.paradigm,
                    "lukhας_components": analysis.lukhας_components,
                    "complexity": analysis.complexity_score,
                }
                all_collected_components.append(components)
            except Exception as e:
                self.logger.error(f"Failed to process {file}: {e}")
        self.write_symbolic_trail(all_collected_components)

    def upload_to_lukhas_sync(self, target_path):
        """
        Placeholder for uploading documentation to LUKHlukhasS sync endpoint.
        """
        self.logger.info(
            f"Uploading documentation for {target_path} to LUKHlukhasS sync endpoint (not implemented)."
        )

    def _load_templates(self) -> dict[str, str]:
        """Load LUKHlukhasS documentation templates"""
        return {
            "overview": """# {title} Overview\n\n{description}\n\n## Purpose\n\n{purpose}\n\n## Features\n\n{features}""",
            "api": """# API Documentation\n\n## Classes\n\n{classes}\n\n## Functions\n\n{functions}""",
            "usage": """# Usage Guide\n\n## Installation\n\n{installation}\n\n## Examples\n\n{examples}""",
        }

    async def analyze_file(self, file_path: Path) -> CodeAnalysis:
        """Perform comprehensive code analysis"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            # Basic analysis
            classes = []
            functions = []
            imports = []
            constants = []
            docstrings = []

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(
                        {
                            "name": node.name,
                            "docstring": ast.get_docstring(node),
                            "methods": [
                                m.name
                                for m in node.body
                                if isinstance(m, ast.FunctionDef)
                            ],
                        }
                    )
                elif isinstance(node, ast.FunctionDef):
                    functions.append(
                        {
                            "name": node.name,
                            "docstring": ast.get_docstring(node),
                            "args": [a.arg for a in node.args.args],
                        }
                    )
                elif isinstance(node, ast.Import):
                    imports.extend(n.name for n in node.names)
                elif isinstance(node, ast.ImportFrom):
                    imports.append(f"{node.module}.{node.names[0].name}")
                elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                    docstrings.append(node.value)

            # Analyze LUKHlukhasS components
            lukhας_components = []
            for pattern_name, pattern in self.lukhας_patterns.items():
                if re.search(pattern, content, re.I):
                    lukhας_components.append(pattern_name)

            # Determine paradigm
            paradigm = "hybrid"
            if any(c in lukhας_components for c in ["symbolic"]):
                paradigm = "symbolic"
            elif any(c in lukhας_components for c in ["neural"]):
                paradigm = "neural"
            elif any(c in lukhας_components for c in ["quantum"]):
                paradigm = "quantum"

            return CodeAnalysis(
                file_path=str(file_path),
                module_name=file_path.stem,
                classes=classes,
                functions=functions,
                imports=imports,
                exports=[f["name"] for f in functions] + [c["name"] for c in classes],
                dependencies=imports,
                constants=constants,
                docstrings=docstrings,
                complexity_score=len(classes) + len(functions),
                paradigm=paradigm,
                lukhας_components=lukhας_components,
            )

        except Exception as e:
            self.logger.error(f"Failed to analyze {file_path}: {str(e)}")
            raise

    async def generate_documentation_sections(
        self, analysis: CodeAnalysis
    ) -> list[DocumentationSection]:
        """Generate documentation sections using OpenAI"""
        if not self.client:
            return []

        sections = []

        try:
            # Generate overview
            overview_prompt = f"""Generate a comprehensive overview for the Python module {analysis.module_name}.

            Module information:
            - Paradigm: {analysis.paradigm}
            - LUKHlukhasS Components: {', '.join(analysis.lukhας_components)}
            - Classes: {len(analysis.classes)}
            - Functions: {len(analysis.functions)}

            Format as markdown with sections for Purpose, Features, and Integration with LUKHlukhasS AI System.
            Focus on how this module contributes to the LUKHlukhasS architecture and consciousness."""

            overview_response = await self._generate_with_openai(overview_prompt)
            sections.append(
                DocumentationSection(
                    title="Overview",
                    content=overview_response,
                    metadata={"paradigm": analysis.paradigm},
                )
            )

            # Generate API documentation
            if analysis.classes or analysis.functions:
                api_prompt = f"""Generate API documentation for the following Python module components:

                Classes:
                {json.dumps(analysis.classes, indent=2)}

                Functions:
                {json.dumps(analysis.functions, indent=2)}

                Format as markdown with clear examples and LUKHlukhasS integration notes."""

                api_response = await self._generate_with_openai(api_prompt)
                sections.append(
                    DocumentationSection(
                        title="API Documentation",
                        content=api_response,
                        metadata={
                            "components": len(analysis.classes)
                            + len(analysis.functions)
                        },
                    )
                )

            # Generate usage guide
            usage_prompt = f"""Create a usage guide for the module {analysis.module_name}.

            Include:
            - Setup instructions
            - Basic usage examples
            - Integration with other LUKHlukhasS components
            - Common patterns and best practices

            Consider the {analysis.paradigm} paradigm and these LUKHlukhasS components: {', '.join(analysis.lukhας_components)}"""

            usage_response = await self._generate_with_openai(usage_prompt)
            sections.append(
                DocumentationSection(
                    title="Usage Guide",
                    content=usage_response,
                    metadata={"type": "guide"},
                )
            )

        except Exception as e:
            self.logger.error(f"Failed to generate documentation: {str(e)}")

        return sections

    async def _generate_with_openai(self, prompt: str) -> str:
        """Generate content using OpenAI"""
        if not self.client:
            return "Error: OpenAI client not initialized"

        try:
            response = await asyncio.to_thread(
                lambda: self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are the LUKHlukhasS AI documentation system,
                            specializing in comprehensive and philosophically aware technical documentation.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                )
            )
            if response and response.choices and len(response.choices) > 0:
                return response.choices[0].message.content or ""
            return "Error: No response from OpenAI API"
        except Exception as e:
            self.logger.error(f"OpenAI API error: {str(e)}")
            return f"Error generating content: {str(e)}"

    async def generate_comprehensive_docs(
        self, source_path: Path, output_dir: Path
    ) -> dict[str, Any]:
        """Generate comprehensive documentation for all Python files in a directory"""
        self.logger.info("🚀 Starting comprehensive documentation generation...")

        # Convert to Path objects if not already
        source_path = Path(source_path)
        output_dir = Path(output_dir)

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Find Python files
        python_files = []
        if source_path.is_file():
            if source_path.suffix == ".py":
                python_files.append(source_path)
        else:
            python_files = list(source_path.rglob("*.py"))

        self.logger.info(f"📂 Found {len(python_files)} Python files")

        # Initialize results
        results = {"documented_files": 0, "sections_generated": 0, "failed_files": 0}

        # Document each file
        self.logger.info(f"📝 Documenting {len(python_files)} files")
        for file_path in python_files:
            try:
                # Analyze file
                analysis = await self.analyze_file(file_path)

                # Generate documentation sections
                sections = await self.generate_documentation_sections(analysis)

                # Write documentation file
                doc_path = output_dir / f"{file_path.stem}_documentation.md"
                with open(doc_path, "w", encoding="utf-8") as f:
                    f.write(f"# {file_path.name} Documentation\n\n")
                    for section in sections:
                        f.write(f"## {section.title}\n\n{section.content}\n\n")

                results["documented_files"] += 1
                results["sections_generated"] += len(sections)

            except Exception as e:
                self.logger.error(f"❌ Failed to document {file_path}: {str(e)}")
                results["failed_files"] += 1

        self.logger.info("✅ Documentation generation complete!")
        self.logger.info(
            f"📊 Generated {results['sections_generated']} sections for {results['documented_files']} files"
        )

        return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="🧠 LUKHlukhasS AI Documentation Generator"
    )
    parser.add_argument(
        "--source", required=True, help="Source directory or file to analyze"
    )
    parser.add_argument(
        "--output", required=True, help="Output directory for documentation"
    )
    parser.add_argument(
        "--api-key", help="OpenAI API key (or set OPENAI_API_KEY env var)"
    )
    parser.add_argument(
        "--model", default="gpt-4-turbo-preview", help="OpenAI model to use"
    )
    parser.add_argument(
        "--style",
        choices=["standard", "symbolic", "corporate", "debug"],
        default="standard",
        help="Documentation style to use",
    )
    parser.add_argument(
        "--upload-to-lukhas-api",
        action="store_true",
        help="Upload documentation to LUKHlukhasS sync endpoint",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    args = parser.parse_args()

    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    async def main():
        # Initialize generator
        generator = AIDocumentationGenerator(
            custom_api_key=args.api_key, model=args.model
        )

        source_dir = Path(args.source)
        output_dir = Path(args.output)

        if not source_dir.exists():
            print(f"❌ Source directory/file does not exist: {source_dir}")
            return 1

        print(f"🚀 Generating documentation for {source_dir}")
        print(f"📁 Output directory: {output_dir}")

        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)

        # Run documentation generation
        results = await generator.generate_comprehensive_docs(source_dir, output_dir)

        if args.upload_to_lukhas_api:
            generator.upload_to_lukhas_sync(source_dir)

        print("\n✅ Documentation generation complete!")
        print(f"📊 Files processed: {results['documented_files']}")
        print(f"📄 Sections generated: {results['sections_generated']}")
        print(f"❌ Failed files: {results['failed_files']}")

        if results["failed_files"] > 0:
            print("\n⚠️ Some files failed to process. Check logs for details.")
            return 1
        return 0

    sys.exit(asyncio.run(main()))
