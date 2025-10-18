#!/usr/bin/env python3
"""
Comprehensive Module Enrichment Tool
====================================

True T4/0.01% enrichment by mining actual module content, context files,
and generating rich metadata from real implementations.
"""

import ast
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


class ModuleContentMiner:
    """Extract rich content from module files for T4/0.01% enrichment."""

    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)

    def mine_python_entrypoints(self, module_path: Path) -> List[str]:
        """Extract actual entrypoints from Python files."""
        entrypoints = []

        # Check __init__.py for __all__ exports
        init_file = module_path / "__init__.py"
        if init_file.exists():
            try:
                with open(init_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Parse AST to find __all__ definitions
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name) and target.id == '__all__':
                                if isinstance(node.value, ast.List):
                                    for item in node.value.elts:
                                        if isinstance(item, ast.Str):
                                            entrypoints.append(f"{module_path.name}.{item.s}")
                                        elif isinstance(item, ast.Constant) and isinstance(item.value, str):
                                            entrypoints.append(f"{module_path.name}.{item.value}")

                # Also look for class and function definitions
                for node in ast.walk(tree):
                    if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                        if not node.name.startswith('_'):  # Skip private
                            entrypoints.append(f"{module_path.name}.{node.name}")

            except Exception as e:
                print(f"Warning: Could not parse {init_file}: {e}")

        # Scan other Python files in the module
        for py_file in module_path.glob("*.py"):
            if py_file.name.startswith('_') or py_file.name == "__init__.py":
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                        if not node.name.startswith('_'):
                            entrypoints.append(f"{module_path.name}.{py_file.stem}.{node.name}")

            except Exception as e:
                print(f"Warning: Could not parse {py_file}: {e}")

        return sorted(list(set(entrypoints)))

    def mine_description_from_docstring(self, module_path: Path) -> Optional[str]:
        """Extract rich description from module docstrings."""
        init_file = module_path / "__init__.py"
        if not init_file.exists():
            return None

        try:
            with open(init_file, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)
            if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Str):
                docstring = tree.body[0].value.s
                # Extract first meaningful paragraph
                lines = [line.strip() for line in docstring.split('\n') if line.strip()]
                if lines:
                    # Find the main description (usually after title)
                    for i, line in enumerate(lines):
                        if i > 0 and len(line) > 50 and not line.endswith('='):
                            return line
                    return lines[0] if lines else None

        except Exception as e:
            print(f"Warning: Could not extract docstring from {init_file}: {e}")

        return None

    def mine_context_files(self, module_path: Path) -> Dict[str, str]:
        """Mine lukhas_context.md and claude.me for rich content."""
        context_data = {}

        # Check for context files in module and candidate areas
        context_files = [
            module_path / "lukhas_context.md",
            module_path / "claude.me",
            self.repo_root / "labs" / module_path.name / "lukhas_context.md",
            self.repo_root / "labs" / module_path.name / "claude.me",
            self.repo_root / "labs" / "core" / module_path.name / "lukhas_context.md",
            self.repo_root / "labs" / "core" / module_path.name / "claude.me",
        ]

        for context_file in context_files:
            if context_file.exists():
                try:
                    with open(context_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    context_data[context_file.name] = content
                except Exception as e:
                    print(f"Warning: Could not read {context_file}: {e}")

        return context_data

    def extract_constellation_role(self, content: str) -> Optional[str]:
        """Extract constellation framework role from content."""
        # Look for constellation patterns
        patterns = [
            r'constellation[_\s]+role[:\s]+([a-z_\-]+)',
            r'constellation[_\s]+framework[:\s]+([⚛️🧠🛡️🌟✨🔄🎯⭐]+)',
            r'anchor[_\-]star[_\-]([a-z]+)',
            r'trail[_\-]star[_\-]([a-z]+)',
            r'watch[_\-]star[_\-]([a-z]+)',
            r'horizon[_\-]star[_\-]([a-z]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, content.lower())
            if match:
                return match.group(1)

        return None

    def extract_tags_from_content(self, module_name: str, content: str, entrypoints: List[str]) -> List[str]:
        """Extract meaningful tags from module content."""
        tags = [module_name]

        # Domain-specific tag mapping
        domain_tags = {
            'consciousness': ['consciousness', 'awareness', 'cognition', 'phenomenological'],
            'memory': ['memory', 'temporal', 'fold-architecture', 'episodic', 'semantic'],
            'identity': ['identity', 'authentication', 'oauth2', 'webauthn', 'security'],
            'governance': ['governance', 'ethics', 'constitutional-ai', 'guardian', 'policy'],
            'matriz': ['bio-symbolic', 'quantum-inspired', 'symbolic-reasoning'],
            'brain': ['cognitive', 'orchestration', 'intelligence', 'monitoring'],
            'api': ['api', 'rest', 'graphql', 'endpoints'],
            'bridge': ['integration', 'adapters', 'connectors'],
            'orchestration': ['orchestration', 'coordination', 'workflow'],
            'quantum': ['quantum', 'quantum-inspired', 'superposition'],
            'core': ['core', 'infrastructure', 'coordination'],
        }

        # Add domain-specific tags
        for domain, domain_tag_list in domain_tags.items():
            if domain in module_name.lower():
                tags.extend(domain_tag_list)

        # Extract from content
        content_lower = content.lower()
        if 'webauthn' in content_lower or 'fido2' in content_lower:
            tags.extend(['webauthn', 'passkey'])
        if 'oauth' in content_lower:
            tags.append('oauth2')
        if 'consciousness' in content_lower:
            tags.append('consciousness')
        if 'fold' in content_lower and 'memory' in content_lower:
            tags.append('fold-architecture')
        if 't4' in content_lower or 'experimental' in content_lower:
            tags.append('t4-experimental')

        # Check entrypoints for patterns
        entrypoint_text = ' '.join(entrypoints).lower()
        if 'monitor' in entrypoint_text:
            tags.append('monitoring')
        if 'auth' in entrypoint_text:
            tags.append('authentication')
        if 'orchestr' in entrypoint_text:
            tags.append('orchestration')

        return sorted(list(set(tags)))

    def generate_rich_description(self, module_name: str, docstring: Optional[str],
                                context_data: Dict[str, str], entrypoints: List[str]) -> str:
        """Generate rich T4/0.01% description."""

        # Use docstring if available and rich
        if docstring and len(docstring) > 50:
            return docstring

        # Mine from context files
        for filename, content in context_data.items():
            if 'lukhas_context.md' in filename:
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                for line in lines:
                    if len(line) > 50 and not line.startswith('#') and not line.endswith('='):
                        return line

        # Generate from module analysis
        domain_descriptions = {
            'consciousness': f"Advanced consciousness processing engine implementing awareness patterns, decision-making algorithms, and phenomenological processing with {len(entrypoints)} entrypoints for cognitive state management.",
            'memory': f"Comprehensive memory management system with fold-based architecture, temporal persistence, and consciousness-memory coupling for episodic and semantic memory operations across {len(entrypoints)} components.",
            'identity': f"Identity and authentication infrastructure providing λID Core Identity System, WebAuthn/FIDO2 integration, OAuth2/OIDC flows, and secure credential management with namespace isolation via {len(entrypoints)} entrypoints.",
            'governance': f"Governance framework implementing policy engines, ethical decision systems, Guardian System integration, and constitutional AI principles for autonomous governance operations with {len(entrypoints)} components.",
            'matriz': f"MATRIZ core processing engine providing bio-symbolic adaptation, consciousness data flows, quantum-inspired algorithms, and symbolic reasoning for AGI development with {len(entrypoints)} processing nodes.",
            'brain': f"High-level cognitive orchestration, intelligence monitoring, and unified consciousness coordination for advanced AI brain architecture with {len(entrypoints)} cognitive components.",
            'core': f"Core orchestration and infrastructure layer providing system coordination, symbolic network integration, consciousness-core coupling, and fundamental LUKHAS primitives with {len(entrypoints)} core functions.",
            'api': f"API gateway and service mesh providing REST/GraphQL endpoints, multi-AI orchestration, and external service integration with {len(entrypoints)} API interfaces.",
            'bridge': f"Integration bridge and adapter framework for external services, legacy system modernization, and service mesh connectivity with {len(entrypoints)} connector components.",
            'orchestration': f"System orchestration and workflow coordination providing multi-service integration, pipeline management, and distributed system coordination with {len(entrypoints)} orchestration functions.",
        }

        # Match module name to domain
        for domain, description in domain_descriptions.items():
            if domain in module_name.lower():
                return description

        # Fallback to generic but informative
        return f"LUKHAS {module_name} module implementing specialized {module_name} functionality with {len(entrypoints)} components for integrated system operations."

    def detect_dependencies(self, module_path: Path, entrypoints: List[str]) -> List[str]:
        """Detect logical module dependencies."""
        dependencies = []

        # Common dependency patterns
        entrypoint_text = ' '.join(entrypoints).lower()
        if 'identity' in entrypoint_text or 'auth' in entrypoint_text:
            if module_path.name != 'identity':
                dependencies.append('identity')
        if 'core' in entrypoint_text or 'orchestr' in entrypoint_text:
            if module_path.name not in ['core', 'orchestration']:
                dependencies.append('core')
        if 'memory' in entrypoint_text:
            if module_path.name != 'memory':
                dependencies.append('memory')

        # Module-specific dependencies
        module_deps = {
            'governance': ['identity', 'core'],
            'memory': ['core'],
            'consciousness': ['memory', 'core'],
            'brain': ['consciousness', 'orchestration', 'core'],
            'api': ['identity', 'core'],
            'bridge': ['api', 'core'],
        }

        if module_path.name in module_deps:
            dependencies.extend(module_deps[module_path.name])

        return sorted(list(set(dependencies)))

    def generate_observability_spans(self, module_name: str, entrypoints: List[str]) -> List[str]:
        """Generate observability spans for the module."""
        base_spans = [f"lukhas.{module_name}.operation"]

        # Add specific spans based on module type
        entrypoint_text = ' '.join(entrypoints).lower()
        if 'auth' in entrypoint_text:
            base_spans.append(f"lukhas.{module_name}.auth")
        if 'process' in entrypoint_text:
            base_spans.append(f"lukhas.{module_name}.processing")
        if 'monitor' in entrypoint_text:
            base_spans.append(f"lukhas.{module_name}.monitoring")
        if 'memory' in entrypoint_text or 'fold' in entrypoint_text:
            base_spans.extend([f"lukhas.{module_name}.fold", f"lukhas.{module_name}.retrieval"])
        if 'consciousness' in entrypoint_text or 'aware' in entrypoint_text:
            base_spans.append(f"lukhas.{module_name}.consciousness")

        return sorted(list(set(base_spans)))


def enrich_single_module(module_path: Path, miner: ModuleContentMiner) -> Dict[str, Any]:
    """Enrich a single module with T4/0.01% quality metadata."""

    manifest_file = module_path / "module.manifest.json"
    if not manifest_file.exists():
        print(f"Skipping {module_path.name}: no manifest found")
        return {}

    # Load existing manifest
    try:
        with open(manifest_file, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
    except Exception as e:
        print(f"Error loading {manifest_file}: {e}")
        return {}

    print(f"🔍 Enriching {module_path.name}...")

    # Mine content
    entrypoints = miner.mine_python_entrypoints(module_path)
    docstring_desc = miner.mine_description_from_docstring(module_path)
    context_data = miner.mine_context_files(module_path)

    # Combine all content for analysis
    all_content = ""
    if docstring_desc:
        all_content += docstring_desc + " "
    for content in context_data.values():
        all_content += content + " "

    # Generate enriched metadata
    rich_description = miner.generate_rich_description(module_path.name, docstring_desc, context_data, entrypoints)
    tags = miner.extract_tags_from_content(module_path.name, all_content, entrypoints)
    dependencies = miner.detect_dependencies(module_path, entrypoints)
    observability_spans = miner.generate_observability_spans(module_path.name, entrypoints)
    constellation_role = miner.extract_constellation_role(all_content)

    # Update manifest with rich metadata
    manifest["description"] = rich_description
    manifest["runtime"]["entrypoints"] = entrypoints[:20]  # Limit to top 20
    manifest["tags"] = tags
    manifest["dependencies"] = dependencies
    manifest["observability"]["required_spans"] = observability_spans

    # Add constellation role if detected
    if constellation_role:
        if "x_legacy" not in manifest:
            manifest["x_legacy"] = {}
        if "directory_metadata" not in manifest["x_legacy"]:
            manifest["x_legacy"]["directory_metadata"] = {}
        manifest["x_legacy"]["directory_metadata"]["constellation_role"] = constellation_role

    # Enhance team ownership based on module type
    team_mapping = {
        'consciousness': 'Consciousness',
        'memory': 'Memory',
        'identity': 'Identity',
        'governance': 'Governance',
        'matriz': 'MATRIZ',
        'brain': 'Brain',
        'core': 'Core',
        'api': 'API',
        'bridge': 'Integration',
        'orchestration': 'Orchestration',
    }

    if module_path.name.lower() in team_mapping:
        manifest["ownership"]["team"] = team_mapping[module_path.name.lower()]

    # Save enriched manifest
    try:
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        print(f"✅ Enriched {module_path.name}: {len(entrypoints)} entrypoints, {len(tags)} tags")
        return {"entrypoints": len(entrypoints), "tags": len(tags), "description_length": len(rich_description)}
    except Exception as e:
        print(f"❌ Error saving {manifest_file}: {e}")
        return {}


def main():
    """Main enrichment process."""
    repo_root = Path.cwd()
    miner = ModuleContentMiner(str(repo_root))

    print("🚀 Starting comprehensive T4/0.01% module enrichment...")

    # Find all modules with manifests
    manifest_files = list(repo_root.glob("*/module.manifest.json"))
    print(f"Found {len(manifest_files)} modules to enrich")

    # Priority modules first (the ones we know have rich content)
    priority_modules = ['brain', 'consciousness', 'memory', 'identity', 'governance', 'matriz', 'core', 'api', 'bridge', 'orchestration']

    enriched_count = 0
    total_entrypoints = 0
    total_tags = 0

    # Process priority modules first
    for module_name in priority_modules:
        module_path = repo_root / module_name
        if module_path.exists() and (module_path / "module.manifest.json").exists():
            result = enrich_single_module(module_path, miner)
            if result:
                enriched_count += 1
                total_entrypoints += result.get("entrypoints", 0)
                total_tags += result.get("tags", 0)

    # Process remaining modules
    for manifest_file in manifest_files:
        module_path = manifest_file.parent
        if module_path.name not in priority_modules:
            result = enrich_single_module(module_path, miner)
            if result:
                enriched_count += 1
                total_entrypoints += result.get("entrypoints", 0)
                total_tags += result.get("tags", 0)

    print("\n🎯 T4/0.01% enrichment complete:")
    print(f"   📦 Modules enriched: {enriched_count}")
    print(f"   🔌 Total entrypoints: {total_entrypoints}")
    print(f"   🏷️  Total tags: {total_tags}")
    print(f"   ✨ Average entrypoints per module: {total_entrypoints / enriched_count:.1f}")


if __name__ == "__main__":
    main()
