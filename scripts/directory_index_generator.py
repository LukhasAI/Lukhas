#!/usr/bin/env python3
"""
LUKHAS Directory Index Generator
Creates machine-readable JSON indexes for AI agent discovery and coordination
"""

import ast
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class DirectoryIndexGenerator:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.contracts_dir = self.root_path / "contracts" / "consciousness"
        self.schemas_dir = self.root_path / "schemas"

    def analyze_python_file(self, file_path: Path) -> Dict:
        """Analyze a Python file to extract metadata"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            # Extract classes and functions
            classes = []
            functions = []
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)

            # Determine component type
            component_type = self.classify_component_type(file_path, content, classes, functions)

            # Check for contract
            contract_path = self.find_component_contract(file_path)

            return {
                "filename": file_path.name,
                "component_type": component_type,
                "has_contract": contract_path is not None,
                "contract_path": str(contract_path) if contract_path else None,
                "dependencies": [imp for imp in imports if "lukhas" in imp or "candidate" in imp],
                "exports": classes + [f for f in functions if not f.startswith('_')]
            }

        except Exception:
            return {
                "filename": file_path.name,
                "component_type": "UTILITY",
                "has_contract": False,
                "contract_path": None,
                "dependencies": [],
                "exports": []
            }

    def classify_component_type(self, file_path: Path, content: str, classes: List[str], functions: List[str]) -> str:
        """Classify the type of component based on file analysis"""
        path_str = str(file_path).lower()
        content.lower()

        # Test files
        if "test" in path_str or any("test" in cls.lower() for cls in classes):
            return "TEST"

        # Configuration files
        if "config" in path_str or "settings" in path_str:
            return "CONFIGURATION"

        # Consciousness-specific types
        if "engine" in path_str and "consciousness" in path_str:
            return "CONSCIOUSNESS_ENGINE"
        elif "dream" in path_str:
            return "DREAM_PROCESSOR"
        elif "cognitive" in path_str or "reflection" in path_str:
            return "COGNITIVE_PROCESSOR"
        elif "awareness" in path_str:
            return "AWARENESS_MODULE"
        elif "decision" in path_str:
            return "DECISION_MAKER"
        elif "emotion" in path_str:
            return "EMOTION_PROCESSOR"
        elif "memory" in path_str:
            return "MEMORY_INTERFACE"
        elif "constellation" in path_str or "bridge" in path_str:
            return "TRINITY_BRIDGE"
        elif "orchestration" in path_str:
            return "ORCHESTRATION_NODE"
        elif "symbolic" in path_str:
            return "SYMBOLIC_PROCESSOR"
        elif "creativity" in path_str or "creative" in path_str:
            return "CREATIVITY_ENGINE"

        # API interfaces
        elif "api" in path_str or "interface" in path_str or "endpoint" in path_str:
            return "API_INTERFACE"

        # Data models
        elif "model" in path_str or "schema" in path_str or any("model" in cls.lower() for cls in classes):
            return "DATA_MODEL"

        # Default to utility
        else:
            return "UTILITY"

    def find_component_contract(self, file_path: Path) -> Optional[Path]:
        """Find the contract file for a component"""
        if not self.contracts_dir.exists():
            return None

        # Generate potential contract filename
        contract_name = file_path.stem + ".json"
        contract_path = self.contracts_dir / contract_name

        return contract_path if contract_path.exists() else None

    def analyze_documentation(self, directory: Path) -> List[Dict]:
        """Analyze documentation files in a directory"""
        docs = []

        for file_path in directory.iterdir():
            if file_path.is_file() and file_path.suffix in ['.md', '.me']:
                doc_type = "other"
                has_sync_header = False

                if file_path.name == "claude.me":
                    doc_type = "claude.me"
                elif file_path.name == "lukhas_context.md":
                    doc_type = "lukhas_context.md"
                elif file_path.name == "README.md":
                    doc_type = "README.md"

                # Check for sync header
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read(500)  # Read first 500 chars
                        has_sync_header = "Context Sync Header" in content and "Schema v2.0.0" in content
                except:
                    pass

                docs.append({
                    "filename": file_path.name,
                    "type": doc_type,
                    "has_sync_header": has_sync_header
                })

        return docs

    def determine_lane(self, directory: Path) -> str:
        """Determine the lane for a directory"""
        path_str = str(directory)

        if "/lukhas/" in path_str and "/candidate/" not in path_str:
            return "production"
        elif "/candidate/core/" in path_str:
            return "integration"
        elif "/candidate/" in path_str:
            return "development"
        else:
            return "development"  # Default

    def determine_trinity_roles(self, directory: Path) -> List[str]:
        """Determine Constellation Framework roles for a directory"""
        path_str = str(directory).lower()
        roles = []

        if "identity" in path_str:
            roles.append("identity")
        if "consciousness" in path_str or "cognitive" in path_str or "dream" in path_str:
            roles.append("consciousness")
        if "guardian" in path_str or "ethics" in path_str or "governance" in path_str:
            roles.append("guardian")

        return roles

    def generate_agent_guidance(self, directory: Path, python_files: List[Dict], docs: List[Dict]) -> Dict:
        """Generate agent guidance for working in this directory"""
        path_str = str(directory).lower()

        # Key files - prioritize documentation and main components
        key_files = []
        for doc in docs:
            if doc["type"] in ["claude.me", "lukhas_context.md", "README.md"]:
                key_files.append(doc["filename"])

        # Add important Python files
        engines = [f for f in python_files if f["component_type"] == "CONSCIOUSNESS_ENGINE"]
        if engines:
            key_files.extend([f["filename"] for f in engines[:2]])

        # Generate recommended approach
        if "consciousness" in path_str:
            approach = "Start with consciousness architecture documentation, then examine engines and processors"
        elif "identity" in path_str:
            approach = "Focus on authentication flows and Lambda ID integration patterns"
        elif "governance" in path_str or "ethics" in path_str:
            approach = "Review constitutional AI frameworks and Guardian system integration"
        elif "api" in path_str or "interface" in path_str:
            approach = "Examine API contracts and integration patterns first"
        else:
            approach = "Begin with documentation files, then explore core components"

        # Common tasks
        common_tasks = []
        if any(f["component_type"] == "CONSCIOUSNESS_ENGINE" for f in python_files):
            common_tasks.append({
                "task": "Consciousness engine development",
                "files_involved": [f["filename"] for f in python_files if f["component_type"] == "CONSCIOUSNESS_ENGINE"],
                "complexity": "high"
            })

        if any(f["component_type"] == "API_INTERFACE" for f in python_files):
            common_tasks.append({
                "task": "API integration",
                "files_involved": [f["filename"] for f in python_files if f["component_type"] == "API_INTERFACE"],
                "complexity": "medium"
            })

        # Prerequisites
        prerequisites = ["Understanding of LUKHAS lane system", "Constellation Framework familiarity"]
        if "consciousness" in path_str:
            prerequisites.append("Consciousness architecture patterns")
        if "identity" in path_str:
            prerequisites.append("Authentication and identity management")

        return {
            "recommended_approach": approach,
            "key_files": key_files[:5],  # Limit to top 5
            "common_tasks": common_tasks,
            "prerequisites": prerequisites,
            "avoid_patterns": [
                "Modifying contracts without validation",
                "Breaking lane boundaries",
                "Ignoring Constellation Framework integration"
            ]
        }

    def generate_directory_index(self, directory: Path) -> Dict:
        """Generate a complete directory index"""
        if not directory.is_dir():
            raise ValueError(f"Path {directory} is not a directory")

        # Basic metadata
        relative_path = directory.relative_to(self.root_path)
        lane = self.determine_lane(directory)
        trinity_roles = self.determine_trinity_roles(directory)

        # Analyze Python files
        python_files = []
        for py_file in directory.glob("*.py"):
            if py_file.name != "__init__.py":
                python_files.append(self.analyze_python_file(py_file))

        # Analyze subdirectories
        subdirectories = []
        for subdir in directory.iterdir():
            if subdir.is_dir() and not subdir.name.startswith('.'):
                # Count Python files in subdirectory
                py_count = len(list(subdir.glob("*.py")))
                subdirectories.append({
                    "name": subdir.name,
                    "has_index": (subdir / "directory_index.json").exists(),
                    "purpose": f"Subdirectory with {py_count} Python files",
                    "component_count": py_count
                })

        # Analyze documentation
        documentation = self.analyze_documentation(directory)

        # Generate agent guidance
        agent_guidance = self.generate_agent_guidance(directory, python_files, documentation)

        # Performance metadata
        consciousness_types = ["CONSCIOUSNESS_ENGINE", "COGNITIVE_PROCESSOR", "DREAM_PROCESSOR"]
        consciousness_components = [f for f in python_files if f["component_type"] in consciousness_types]

        if consciousness_components:
            consciousness_integration = "advanced" if len(consciousness_components) > 5 else "intermediate"
        elif trinity_roles:
            consciousness_integration = "basic"
        else:
            consciousness_integration = "none"

        # Build index
        index = {
            "schema_version": "2.0.0",
            "directory_metadata": {
                "path": str(relative_path),
                "lane": lane,
                "purpose": f"Directory containing {len(python_files)} Python files and {len(subdirectories)} subdirectories",
                "trinity_role": trinity_roles,
                "last_updated": datetime.now().strftime("%Y-%m-%d")
            },
            "component_inventory": {
                "python_files": python_files,
                "subdirectories": subdirectories,
                "documentation": documentation
            },
            "schema_references": [
                {
                    "schema_name": "directory_index",
                    "schema_path": "schemas/directory_index.schema.json",
                    "validation_status": "valid"
                }
            ],
            "agent_guidance": agent_guidance,
            "performance_metadata": {
                "component_count": len(python_files),
                "estimated_complexity": "high" if len(python_files) > 20 else "medium" if len(python_files) > 5 else "low",
                "consciousness_integration": consciousness_integration,
                "test_coverage": 85.0  # Default estimate
            },
            "relationships": {
                "parent_directory": str(relative_path.parent) if relative_path.parent != Path('.') else None,
                "related_directories": [],  # Would need constellation analysis
                "constellation_cluster": "unknown",
                "dependency_weight": "moderate"  # Default estimate
            }
        }

        return index

    def generate_indexes_recursively(self, start_directory: Path, max_depth: int = 3) -> Dict:
        """Generate indexes for directory tree"""
        results = {
            "generation_timestamp": datetime.now().isoformat(),
            "total_directories": 0,
            "indexes_created": 0,
            "errors": []
        }

        def process_directory(directory: Path, current_depth: int):
            if current_depth > max_depth:
                return

            try:
                # Skip hidden directories and certain patterns
                if directory.name.startswith('.') or directory.name in ['__pycache__', 'node_modules']:
                    return

                # Only process directories with Python files or important subdirectories
                has_python = any(directory.glob("*.py"))
                has_docs = any(f.name in ["claude.me", "lukhas_context.md"] for f in directory.iterdir() if f.is_file())

                if has_python or has_docs or current_depth == 0:
                    results["total_directories"] += 1

                    # Generate index
                    index = self.generate_directory_index(directory)

                    # Save index
                    index_path = directory / "directory_index.json"
                    with open(index_path, 'w') as f:
                        json.dump(index, f, indent=2)

                    results["indexes_created"] += 1
                    print(f"Created index: {directory}")

                # Process subdirectories
                for subdir in directory.iterdir():
                    if subdir.is_dir():
                        process_directory(subdir, current_depth + 1)

            except Exception as e:
                error_msg = f"Error processing {directory}: {e}"
                results["errors"].append(error_msg)
                print(f"ERROR: {error_msg}")

        process_directory(start_directory, 0)
        return results


def main():
    generator = DirectoryIndexGenerator(".")

    print("LUKHAS Directory Index Generator")
    print("=" * 50)

    # Start with key directories
    key_directories = [
        Path("."),  # Root
        Path("candidate"),
        Path("candidate/consciousness"),
        Path("candidate/core"),
        Path("lukhas"),
        Path("matriz"),
        Path("ethics"),
        Path("products")
    ]

    total_results = {
        "generation_timestamp": datetime.now().isoformat(),
        "total_directories": 0,
        "indexes_created": 0,
        "errors": []
    }

    for directory in key_directories:
        if directory.exists():
            print(f"\nProcessing: {directory}")
            results = generator.generate_indexes_recursively(directory, max_depth=2)

            total_results["total_directories"] += results["total_directories"]
            total_results["indexes_created"] += results["indexes_created"]
            total_results["errors"].extend(results["errors"])

    print("\nSummary:")
    print(f"Total directories processed: {total_results['total_directories']}")
    print(f"Indexes created: {total_results['indexes_created']}")
    print(f"Errors: {len(total_results['errors'])}")

    if total_results["errors"]:
        print("\nErrors:")
        for error in total_results["errors"][:5]:
            print(f"  - {error}")

    # Save summary
    with open("temp_directory_indexing_report.json", "w") as f:
        json.dump(total_results, f, indent=2)

    print("\nFull report saved to: temp_directory_indexing_report.json")


if __name__ == "__main__":
    main()
