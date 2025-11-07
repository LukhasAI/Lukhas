#!/usr/bin/env python3
"""
Generate Complete Module Inventory for MATRIZ Audit

Scans all Python packages (directories with __init__.py) and creates
comprehensive inventory for MATRIZ compliance documentation.

Usage:
    python scripts/generate_complete_inventory.py \\
        --scan candidate/ lukhas/ \\
        --output docs/audits/COMPLETE_MODULE_INVENTORY.json \\
        --verbose
"""

import ast
import json
from datetime import datetime, timezone
from pathlib import Path


class ModuleInventoryGenerator:
    """Generate comprehensive inventory of all Python modules"""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.inventory = []
        self.stats = {
            "total_modules": 0,
            "candidate_modules": 0,
            "lukhas_modules": 0,
            "with_manifests": 0,
            "without_manifests": 0,
            "matriz_nodes": {}
        }

    def scan_directory(self, directory: Path, lane: str) -> None:
        """Scan directory for Python packages"""
        print(f"Scanning {directory} (lane: {lane})...")

        for root, dirs, files in os.walk(directory):
            # Skip common non-module directories
            dirs[:] = [d for d in dirs if d not in [
                '__pycache__', '.pytest_cache', 'node_modules',
                '.git', '.venv', 'venv', 'dist', 'build', '*.egg-info'
            ]]

            # Check if this is a Python package
            if '__init__.py' in files:
                module_path = Path(root)
                relative_path = module_path.relative_to(self.base_path)

                module_info = self._analyze_module(module_path, relative_path, lane)
                self.inventory.append(module_info)

                # Update stats
                self.stats["total_modules"] += 1
                if lane == "candidate":
                    self.stats["candidate_modules"] += 1
                elif lane == "lukhas":
                    self.stats["lukhas_modules"] += 1

                if module_info["has_manifest"]:
                    self.stats["with_manifests"] += 1
                else:
                    self.stats["without_manifests"] += 1

                matriz_node = module_info["matriz_node"]
                self.stats["matriz_nodes"][matriz_node] = \
                    self.stats["matriz_nodes"].get(matriz_node, 0) + 1

    def _analyze_module(self, module_path: Path, relative_path: Path, lane: str) -> Dict[str, Any]:
        """Analyze a single module and extract metadata"""

        # Basic info
        module_name = str(relative_path).replace(os.sep, '.')

        # Check for manifest
        manifest_path = module_path / "module.manifest.json"
        has_manifest = manifest_path.exists()

        # Count Python files
        python_files = list(module_path.glob("*.py"))
        python_file_count = len(python_files)

        # Count subdirectories (sub-packages)
        subdirs = [d for d in module_path.iterdir()
                  if d.is_dir() and (d / "__init__.py").exists()]
        subdir_count = len(subdirs)

        # Infer MATRIZ node from path
        matriz_node = self._infer_matriz_node(relative_path)

        # Infer Constellation star
        constellation_star = self._infer_constellation_star(relative_path)

        # Extract capabilities from __init__.py
        capabilities = self._extract_capabilities(module_path / "__init__.py")

        # Check for tests
        has_tests = (module_path / "tests").exists() or \
                   (module_path.parent / "tests" / module_path.name).exists()

        return {
            "module_name": module_name,
            "path": str(relative_path),
            "lane": lane,
            "type": "package",
            "has_manifest": has_manifest,
            "has_init": True,
            "python_files": python_file_count,
            "subdirectories": subdir_count,
            "matriz_node": matriz_node,
            "constellation_star": constellation_star,
            "primary_capability": capabilities[0] if capabilities else "TBD",
            "capabilities": capabilities,
            "has_tests": has_tests,
            "dependencies": [],  # TODO: Extract from imports
            "status": "documented" if has_manifest else "needs_documentation",
            "priority": self._determine_priority(relative_path, has_manifest)
        }

    def _infer_matriz_node(self, path: Path) -> str:
        """Infer MATRIZ pipeline node from module path"""
        path_str = str(path).lower()

        # Memory node
        if any(x in path_str for x in ['memory', 'fold', 'temporal', 'storage']):
            return "memory"

        # Attention node
        if any(x in path_str for x in ['attention', 'focus', 'awareness']):
            return "attention"

        # Thought node
        if any(x in path_str for x in ['reasoning', 'thought', 'consciousness', 'cognitive', 'decision']):
            return "thought"

        # Risk node
        if any(x in path_str for x in ['guardian', 'ethics', 'governance', 'compliance', 'drift', 'risk']):
            return "risk"

        # Intent node
        if any(x in path_str for x in ['orchestration', 'coordination', 'intent', 'planning']):
            return "intent"

        # Action node
        if any(x in path_str for x in ['api', 'bridge', 'adapter', 'action', 'execution', 'interface']):
            return "action"

        # Default to supporting
        return "supporting"

    def _infer_constellation_star(self, path: Path) -> str:
        """Infer Constellation Framework star from module path"""
        path_str = str(path).lower()

        if any(x in path_str for x in ['identity', 'auth', 'lambda', 'λid']):
            return "⚛️ Anchor (Identity)"
        elif any(x in path_str for x in ['memory', 'fold', 'temporal']):
            return "✦ Trail (Memory)"
        elif any(x in path_str for x in ['vision', 'interface', 'ui', 'pattern']):
            return "🔬 Horizon (Vision)"
        elif any(x in path_str for x in ['guardian', 'ethics', 'governance']):
            return "🛡️ Watch (Guardian)"
        elif any(x in path_str for x in ['consciousness', 'awareness', 'dream']):
            return "🌊 Flow (Consciousness)"
        elif any(x in path_str for x in ['creative', 'innovation', 'spark']):
            return "⚡ Spark (Creativity)"
        elif any(x in path_str for x in ['voice', 'persona', 'personality']):
            return "🎭 Persona (Voice)"
        elif any(x in path_str for x in ['quantum', 'oracle', 'prediction']):
            return "🔮 Oracle (Quantum)"
        else:
            return "Supporting"

    def _extract_capabilities(self, init_file: Path) -> List[str]:
        """Extract capabilities from __init__.py docstring and exports"""
        capabilities = []

        if not init_file.exists():
            return capabilities

        try:
            with open(init_file, encoding='utf-8') as f:
                content = f.read()

                # Parse AST
                tree = ast.parse(content)

                # Extract module docstring
                docstring = ast.get_docstring(tree)
                if docstring:
                    # Look for capability keywords
                    doc_lower = docstring.lower()
                    if 'authentication' in doc_lower:
                        capabilities.append('authentication')
                    if 'memory' in doc_lower:
                        capabilities.append('memory_management')
                    if 'api' in doc_lower:
                        capabilities.append('api_interface')
                    if 'processing' in doc_lower:
                        capabilities.append('data_processing')

                # Check for __all__ exports
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if (isinstance(target, ast.Name) and target.id == '__all__') and isinstance(node.value, ast.List):
                                export_count = len(node.value.elts)
                                if export_count > 0:
                                    capabilities.append(f'{export_count}_exports')

        except Exception as e:
            print(f"Warning: Could not parse {init_file}: {e}")

        return capabilities if capabilities else ["general_module"]

    def _determine_priority(self, path: Path, has_manifest: bool) -> str:
        """Determine priority for documentation/audit"""
        if has_manifest:
            return "documented"

        path_str = str(path).lower()

        # Critical modules
        if any(x in path_str for x in ['matriz', 'identity', 'guardian', 'auth', 'api', 'core.orchestration']):
            return "critical"

        # High priority
        if any(x in path_str for x in ['consciousness', 'memory', 'governance', 'bridge']):
            return "high"

        # Medium priority
        if any(x in path_str for x in ['interface', 'adapter', 'cognitive']):
            return "medium"

        # Low priority
        return "low"

    def generate_inventory(self, scan_dirs: List[str]) -> Dict[str, Any]:
        """Generate complete inventory"""
        print("Generating complete module inventory...")
        print(f"Base path: {self.base_path}")

        for scan_dir in scan_dirs:
            dir_path = self.base_path / scan_dir
            if not dir_path.exists():
                print(f"Warning: Directory {dir_path} does not exist, skipping")
                continue

            # Determine lane from directory name
            lane = scan_dir.rstrip('/').split('/')[-1]
            self.scan_directory(dir_path, lane)

        # Sort inventory by module name
        self.inventory.sort(key=lambda x: x["module_name"])

        # Create final inventory document
        inventory_doc = {
            "schema_version": "1.0.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generator": "generate_complete_inventory.py",
            "total_modules": self.stats["total_modules"],
            "statistics": self.stats,
            "inventory": self.inventory
        }

        return inventory_doc

    def save_inventory(self, output_path: Path, inventory: Dict[str, Any]) -> None:
        """Save inventory to JSON file"""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(inventory, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Inventory saved to: {output_path}")
        print("\n📊 Statistics:")
        print(f"   Total modules: {self.stats['total_modules']}")
        print(f"   Candidate modules: {self.stats['candidate_modules']}")
        print(f"   Lukhas modules: {self.stats['lukhas_modules']}")
        print(f"   With manifests: {self.stats['with_manifests']}")
        print(f"   Without manifests: {self.stats['without_manifests']}")
        print("\n   MATRIZ Node Distribution:")
        for node, count in sorted(self.stats['matriz_nodes'].items(), key=lambda x: x[1], reverse=True):
            print(f"     {node}: {count}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate complete module inventory for MATRIZ audit'
    )
    parser.add_argument(
        '--scan',
        nargs='+',
        default=['candidate', 'lukhas'],
        help='Directories to scan for modules (default: candidate lukhas)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='docs/audits/COMPLETE_MODULE_INVENTORY.json',
        help='Output file path (default: docs/audits/COMPLETE_MODULE_INVENTORY.json)'
    )
    parser.add_argument(
        '--base-path',
        type=str,
        default='.',
        help='Base repository path (default: current directory)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    # Initialize generator
    base_path = Path(args.base_path).resolve()
    generator = ModuleInventoryGenerator(base_path)

    # Generate inventory
    inventory = generator.generate_inventory(args.scan)

    # Save inventory
    output_path = base_path / args.output
    generator.save_inventory(output_path, inventory)

    print("\n✅ Complete! Inventory ready for MATRIZ audit.")
    print("   Next step: Generate gap analysis")
    print("   Command: python scripts/analyze_documentation_gaps.py")


if __name__ == "__main__":
    main()
