#!/usr/bin/env python3
"""
🎭 LUKHAS AI Branding Folder Consolidator
========================================

Automatically consolidates the entire branding/ folder into readable formats:
- Markdown documentation
- JSON configuration export
- YAML settings export
- Python code extraction

Usage:
    python consolidate_branding.py [--format md|json|yaml|all] [--output filename]

Trinity Framework Compliant ⚛️🧠🛡️
"""

import argparse
import ast
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class BrandingConsolidator:
    """🎭 Consolidates LUKHAS AI branding folder into readable formats"""

    def __init__(self, branding_root: str = "branding"):
        self.branding_root = Path(branding_root)
        self.consolidated_data = {}
        self.trinity_compliance = True

    def consolidate_all(self) -> Dict[str, Any]:
        """Consolidate entire branding folder"""
        print("🔄 Starting branding consolidation...")

        # Extract different file types
        python_modules = self._extract_python_modules()
        yaml_configs = self._extract_yaml_configs()
        json_configs = self._extract_json_configs()
        markdown_docs = self._extract_markdown_docs()

        # Build consolidated structure
        self.consolidated_data = {
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "source_directory": str(self.branding_root),
                "trinity_framework": "⚛️🧠🛡️",
                "total_files_processed": len(python_modules)
                + len(yaml_configs)
                + len(json_configs)
                + len(markdown_docs),
                "constitutional_ai_compliant": True,
            },
            "directory_structure": self._get_directory_structure(),
            "python_modules": python_modules,
            "configurations": {"yaml_files": yaml_configs, "json_files": json_configs},
            "documentation": markdown_docs,
            "vocabularies": self._extract_vocabularies(),
            "tone_guidelines": self._extract_tone_guidelines(),
            "brand_assets": self._extract_brand_assets(),
            "enforcement_rules": self._extract_enforcement_rules(),
            "api_integrations": self._extract_api_integrations(),
            "trinity_compliance_summary": self._assess_trinity_compliance(),
        }

        print(
            f"✅ Consolidation complete: {self.consolidated_data['metadata']['total_files_processed']} files processed"
        )
        return self.consolidated_data

    def _get_directory_structure(self) -> Dict[str, Any]:
        """Extract directory structure"""
        structure = {}

        for root, dirs, files in os.walk(self.branding_root):
            rel_path = os.path.relpath(root, self.branding_root)
            if rel_path == ".":
                rel_path = "root"

            structure[rel_path] = {
                "directories": dirs,
                "files": {
                    "python": [f for f in files if f.endswith(".py")],
                    "yaml": [f for f in files if f.endswith((".yaml", ".yml"))],
                    "json": [f for f in files if f.endswith(".json")],
                    "markdown": [f for f in files if f.endswith(".md")],
                    "other": [
                        f
                        for f in files
                        if not f.endswith((".py", ".yaml", ".yml", ".json", ".md"))
                    ],
                },
            }

        return structure

    def _extract_python_modules(self) -> Dict[str, Dict]:
        """Extract Python module information"""
        modules = {}

        for py_file in self.branding_root.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            rel_path = str(py_file.relative_to(self.branding_root))

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                # Parse AST for structure analysis
                module_info = self._analyze_python_module(content, py_file)
                modules[rel_path] = module_info

            except Exception as e:
                modules[rel_path] = {"error": f"Failed to process: {str(e)}"}

        return modules

    def _analyze_python_module(self, content: str, file_path: Path) -> Dict:
        """Analyze Python module structure"""
        try:
            tree = ast.parse(content)

            classes = []
            functions = []
            imports = []
            docstring = ast.get_docstring(tree)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(
                        {
                            "name": node.name,
                            "methods": [
                                n.name
                                for n in node.body
                                if isinstance(n, ast.FunctionDef)
                            ],
                            "docstring": ast.get_docstring(node),
                        }
                    )
                elif isinstance(node, ast.FunctionDef):
                    if not any(
                        node in cls.body
                        for cls in ast.walk(tree)
                        if isinstance(cls, ast.ClassDef)
                    ):
                        functions.append(
                            {
                                "name": node.name,
                                "args": [arg.arg for arg in node.args.args],
                                "docstring": ast.get_docstring(node),
                            }
                        )
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        imports.extend([alias.name for alias in node.names])
                    else:
                        imports.append(f"from {node.module or ''}")

            # Check for Trinity Framework compliance
            trinity_symbols = ["⚛️", "🧠", "🛡️"]
            has_trinity = any(symbol in content for symbol in trinity_symbols)

            return {
                "file_size": file_path.stat().st_size,
                "lines_of_code": len(content.splitlines()),
                "docstring": docstring,
                "classes": classes,
                "functions": functions,
                "imports": list(set(imports)),
                "trinity_compliant": has_trinity,
                "consciousness_aware": "consciousness" in content.lower(),
                "guardian_integrated": "guardian" in content.lower(),
                "last_modified": datetime.fromtimestamp(
                    file_path.stat().st_mtime
                ).isoformat(),
            }

        except Exception as e:
            return {
                "analysis_error": str(e),
                "raw_content_lines": len(content.splitlines()),
            }

    def _extract_yaml_configs(self) -> Dict[str, Any]:
        """Extract YAML configuration files"""
        configs = {}

        for yaml_file in self.branding_root.rglob("*.yaml"):
            rel_path = str(yaml_file.relative_to(self.branding_root))

            try:
                with open(yaml_file, encoding="utf-8") as f:
                    content = yaml.safe_load(f)
                configs[rel_path] = content
            except Exception as e:
                configs[rel_path] = {"error": f"Failed to parse YAML: {str(e)}"}

        for yml_file in self.branding_root.rglob("*.yml"):
            rel_path = str(yml_file.relative_to(self.branding_root))

            try:
                with open(yml_file, encoding="utf-8") as f:
                    content = yaml.safe_load(f)
                configs[rel_path] = content
            except Exception as e:
                configs[rel_path] = {"error": f"Failed to parse YML: {str(e)}"}

        return configs

    def _extract_json_configs(self) -> Dict[str, Any]:
        """Extract JSON configuration files"""
        configs = {}

        for json_file in self.branding_root.rglob("*.json"):
            rel_path = str(json_file.relative_to(self.branding_root))

            try:
                with open(json_file, encoding="utf-8") as f:
                    content = json.load(f)
                configs[rel_path] = content
            except Exception as e:
                configs[rel_path] = {"error": f"Failed to parse JSON: {str(e)}"}

        return configs

    def _extract_markdown_docs(self) -> Dict[str, str]:
        """Extract Markdown documentation"""
        docs = {}

        for md_file in self.branding_root.rglob("*.md"):
            rel_path = str(md_file.relative_to(self.branding_root))

            try:
                with open(md_file, encoding="utf-8") as f:
                    content = f.read()
                docs[rel_path] = content
            except Exception as e:
                docs[rel_path] = f"Error reading file: {str(e)}"

        return docs

    def _extract_vocabularies(self) -> Dict[str, Any]:
        """Extract vocabulary and language definitions"""
        vocab_data = {}
        vocab_dir = self.branding_root / "vocabularies"

        if vocab_dir.exists():
            for vocab_file in vocab_dir.iterdir():
                if vocab_file.is_file():
                    rel_path = str(vocab_file.relative_to(self.branding_root))

                    if vocab_file.suffix == ".py":
                        # Extract vocabulary from Python files
                        try:
                            with open(vocab_file) as f:
                                content = f.read()

                            # Look for vocabulary dictionaries/lists
                            vocab_patterns = re.findall(
                                r"(\w+_VOCABULARY)\s*=\s*({.*?}|\[.*?\])",
                                content,
                                re.DOTALL,
                            )
                            if vocab_patterns:
                                vocab_data[rel_path] = dict(vocab_patterns)
                            else:
                                vocab_data[rel_path] = {
                                    "type": "python_module",
                                    "content_preview": content[:200],
                                }

                        except Exception as e:
                            vocab_data[rel_path] = {"error": str(e)}

                    elif vocab_file.suffix in [".yaml", ".yml"]:
                        try:
                            with open(vocab_file) as f:
                                vocab_data[rel_path] = yaml.safe_load(f)
                        except Exception as e:
                            vocab_data[rel_path] = {"error": str(e)}

                    elif vocab_file.suffix == ".json":
                        try:
                            with open(vocab_file) as f:
                                vocab_data[rel_path] = json.load(f)
                        except Exception as e:
                            vocab_data[rel_path] = {"error": str(e)}

        return vocab_data

    def _extract_tone_guidelines(self) -> Dict[str, Any]:
        """Extract tone and voice guidelines"""
        tone_data = {}
        tone_dir = self.branding_root / "tone"

        if tone_dir.exists():
            for item in tone_dir.rglob("*"):
                if item.is_file() and item.suffix in [
                    ".py",
                    ".yaml",
                    ".yml",
                    ".md",
                    ".json",
                ]:
                    rel_path = str(item.relative_to(self.branding_root))

                    try:
                        if item.suffix == ".py":
                            with open(item) as f:
                                content = f.read()
                            tone_data[rel_path] = {
                                "type": "python",
                                "preview": content[:300],
                            }

                        elif item.suffix in [".yaml", ".yml"]:
                            with open(item) as f:
                                tone_data[rel_path] = yaml.safe_load(f)

                        elif item.suffix == ".json":
                            with open(item) as f:
                                tone_data[rel_path] = json.load(f)

                        elif item.suffix == ".md":
                            with open(item) as f:
                                tone_data[rel_path] = f.read()

                    except Exception as e:
                        tone_data[rel_path] = {"error": str(e)}

        return tone_data

    def _extract_brand_assets(self) -> Dict[str, Any]:
        """Extract brand assets and visual elements"""
        assets = {}

        for asset_dir in ["assets", "visual", "design"]:
            asset_path = self.branding_root / asset_dir
            if asset_path.exists():
                for item in asset_path.rglob("*"):
                    if item.is_file():
                        rel_path = str(item.relative_to(self.branding_root))
                        assets[rel_path] = {
                            "file_type": item.suffix,
                            "size_bytes": item.stat().st_size,
                            "last_modified": datetime.fromtimestamp(
                                item.stat().st_mtime
                            ).isoformat(),
                        }

        return assets

    def _extract_enforcement_rules(self) -> Dict[str, Any]:
        """Extract brand enforcement and validation rules"""
        enforcement = {}
        enforcement_dir = self.branding_root / "enforcement"

        if enforcement_dir.exists():
            for item in enforcement_dir.rglob("*.py"):
                rel_path = str(item.relative_to(self.branding_root))

                try:
                    with open(item) as f:
                        content = f.read()

                    # Extract validation rules and patterns
                    enforcement[rel_path] = {
                        "functions": len(re.findall(r"def\s+\w+", content)),
                        "classes": len(re.findall(r"class\s+\w+", content)),
                        "validation_patterns": len(
                            re.findall(r"validate|check|verify", content, re.IGNORECASE)
                        ),
                        "trinity_integrated": "⚛️" in content
                        or "🧠" in content
                        or "🛡️" in content,
                        "content_preview": content[:200],
                    }

                except Exception as e:
                    enforcement[rel_path] = {"error": str(e)}

        return enforcement

    def _extract_api_integrations(self) -> Dict[str, Any]:
        """Extract API integration patterns"""
        integrations = {}
        api_dir = self.branding_root / "apis"

        if api_dir.exists():
            for item in api_dir.rglob("*.py"):
                rel_path = str(item.relative_to(self.branding_root))

                try:
                    with open(item) as f:
                        content = f.read()

                    integrations[rel_path] = {
                        "api_endpoints": len(
                            re.findall(
                                r"@\w+\.route|async\s+def\s+\w+|def\s+\w+.*api", content
                            )
                        ),
                        "imports": len(
                            re.findall(r"^import|^from", content, re.MULTILINE)
                        ),
                        "classes": len(re.findall(r"class\s+\w+", content)),
                        "trinity_compliant": "trinity" in content.lower()
                        or "⚛️🧠🛡️" in content,
                        "consciousness_aware": "consciousness" in content.lower(),
                    }

                except Exception as e:
                    integrations[rel_path] = {"error": str(e)}

        return integrations

    def _assess_trinity_compliance(self) -> Dict[str, Any]:
        """Assess overall Trinity Framework compliance"""
        total_files = 0
        compliant_files = 0

        for root, dirs, files in os.walk(self.branding_root):
            for file in files:
                if file.endswith((".py", ".md", ".yaml", ".yml")):
                    total_files += 1
                    file_path = os.path.join(root, file)

                    try:
                        with open(file_path, encoding="utf-8") as f:
                            content = f.read()

                        if any(symbol in content for symbol in ["⚛️", "🧠", "🛡️"]) or any(
                            term in content.lower()
                            for term in ["trinity", "constitutional", "consciousness"]
                        ):
                            compliant_files += 1

                    except:
                        pass  # Skip files that can't be read

        compliance_rate = (
            (compliant_files / total_files * 100) if total_files > 0 else 0
        )

        return {
            "total_files_assessed": total_files,
            "trinity_compliant_files": compliant_files,
            "compliance_rate_percentage": round(compliance_rate, 2),
            "compliance_level": (
                "excellent"
                if compliance_rate > 80
                else "good" if compliance_rate > 60 else "needs_improvement"
            ),
            "trinity_symbols_used": ["⚛️", "🧠", "🛡️"],
            "assessment_timestamp": datetime.utcnow().isoformat(),
        }

    def export_markdown(self, output_file: Optional[str] = None) -> str:
        """Export consolidated data as Markdown"""
        if not self.consolidated_data:
            self.consolidate_all()

        md_content = f"""# 🎭 LUKHAS AI Branding System - Complete Consolidation

**Generated**: {self.consolidated_data['metadata']['generated_at']}  
**Source**: {self.consolidated_data['metadata']['source_directory']}  
**Trinity Framework**: {self.consolidated_data['metadata']['trinity_framework']}  
**Files Processed**: {self.consolidated_data['metadata']['total_files_processed']}

---

## 📊 System Overview

### Trinity Compliance Assessment
- **Total Files Assessed**: {self.consolidated_data['trinity_compliance_summary']['total_files_assessed']}
- **Trinity Compliant**: {self.consolidated_data['trinity_compliance_summary']['trinity_compliant_files']}
- **Compliance Rate**: {self.consolidated_data['trinity_compliance_summary']['compliance_rate_percentage']}%
- **Compliance Level**: {self.consolidated_data['trinity_compliance_summary']['compliance_level']}

### File Distribution
"""

        # Add directory structure
        md_content += "\n### 📁 Directory Structure\n```\n"
        for path, info in self.consolidated_data["directory_structure"].items():
            md_content += f"{path}/\n"
            for file_type, files in info["files"].items():
                if files:
                    md_content += f"  {file_type}: {len(files)} files\n"
        md_content += "```\n"

        # Add Python modules summary
        md_content += f"\n### 🐍 Python Modules ({len(self.consolidated_data['python_modules'])} files)\n\n"
        for module_path, module_info in self.consolidated_data[
            "python_modules"
        ].items():
            if "error" not in module_info:
                md_content += f"**{module_path}**\n"
                md_content += f"- Lines: {module_info.get('lines_of_code', 'N/A')}\n"
                md_content += f"- Classes: {len(module_info.get('classes', [])}\n"
                md_content += f"- Functions: {len(module_info.get('functions', [])}\n"
                md_content += f"- Trinity Compliant: {'✅' if module_info.get('trinity_compliant')} else '❌'}\n\n"

        # Add vocabularies summary
        if self.consolidated_data["vocabularies"]:
            md_content += f"\n### 📚 Vocabularies ({len(self.consolidated_data['vocabularies'])} files)\n\n"
            for vocab_path, vocab_data in self.consolidated_data[
                "vocabularies"
            ].items():
                md_content += f"**{vocab_path}**\n"
                if isinstance(vocab_data, dict) and "error" not in vocab_data:
                    md_content += f"- Type: {vocab_data.get('type', 'vocabulary')}\n"
                md_content += "\n"

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(md_content)
            print(f"✅ Markdown export saved to: {output_file}")

        return md_content

    def export_json(self, output_file: Optional[str] = None) -> str:
        """Export consolidated data as JSON"""
        if not self.consolidated_data:
            self.consolidate_all()

        json_content = json.dumps(self.consolidated_data, indent=2, ensure_ascii=False)

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(json_content)
            print(f"✅ JSON export saved to: {output_file}")

        return json_content

    def export_yaml(self, output_file: Optional[str] = None) -> str:
        """Export consolidated data as YAML"""
        if not self.consolidated_data:
            self.consolidate_all()

        yaml_content = yaml.dump(
            self.consolidated_data, default_flow_style=False, allow_unicode=True
        )

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(yaml_content)
            print(f"✅ YAML export saved to: {output_file}")

        return yaml_content


def main():
    parser = argparse.ArgumentParser(description="🎭 LUKHAS AI Branding Consolidator")
    parser.add_argument(
        "--format",
        choices=["md", "json", "yaml", "all"],
        default="md",
        help="Output format (default: md)",
    )
    parser.add_argument("--output", type=str, help="Output filename (optional)")
    parser.add_argument(
        "--branding-dir",
        type=str,
        default="branding",
        help="Branding directory path (default: branding)",
    )

    args = parser.parse_args()

    print("🎭 LUKHAS AI Branding Consolidator")
    print("=" * 40)
    print("Trinity Framework: ⚛️🧠🛡️")
    print(f"Source Directory: {args.branding_dir}")
    print(f"Output Format: {args.format}")
    print()

    consolidator = BrandingConsolidator(args.branding_dir)

    if args.format == "all":
        # Export all formats
        base_name = args.output or "lukhas_branding_consolidated"
        consolidator.export_markdown(f"{base_name}.md")
        consolidator.export_json(f"{base_name}.json")
        consolidator.export_yaml(f"{base_name}.yaml")
        print(f"\n🎉 All formats exported with base name: {base_name}")

    elif args.format == "md":
        output_file = args.output or "LUKHAS_BRANDING_CONSOLIDATED.md"
        consolidator.export_markdown(output_file)

    elif args.format == "json":
        output_file = args.output or "lukhas_branding_consolidated.json"
        consolidator.export_json(output_file)

    elif args.format == "yaml":
        output_file = args.output or "lukhas_branding_consolidated.yaml"
        consolidator.export_yaml(output_file)

    print("\n✅ Branding consolidation complete!")
    print(
        f"📊 Files processed: {consolidator.consolidated_data['metadata']['total_files_processed']}"
    )
    print(
        f"🎯 Trinity compliance: {consolidator.consolidated_data['trinity_compliance_summary']['compliance_rate_percentage']}%"
    )


if __name__ == "__main__":
    main()
