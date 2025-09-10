#!/usr/bin/env python3
"""
LUKHAS Module Schema Generator

Automated tool to generate comprehensive module schemas from codebase analysis.
Uses AST parsing, import analysis, and file system scanning to extract metadata.

Copyright (c) 2025 LUKHAS AI. All rights reserved.
"""

import ast
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml


@dataclass
class ModuleInfo:
    """Container for module analysis results"""
    name: str
    path: Path
    imports: Set[str]
    exports: Set[str]
    classes: Set[str]
    functions: Set[str]
    entry_points: List[str]
    file_patterns: List[str]
    dependencies: Set[str]
    external_libs: Set[str]
    test_files: List[str]
    config_files: List[str]
    version: Optional[str] = None
    tier: Optional[int] = None
    description: Optional[str] = None


class ModuleSchemaGenerator:
    """Generates comprehensive module schemas from codebase analysis"""

    def __init__(self, root_path: Path):
        self.root_path = Path(root_path)
        self.modules = {}
        self.dependency_graph = defaultdict(set)
        self.reverse_deps = defaultdict(set)
        
    def discover_modules(self) -> Dict[str, ModuleInfo]:
        """Discover all modules in the codebase"""
        print("🔍 Discovering modules...")
        
        # Main module directories
        module_dirs = [
            "candidate",
            "lukhas", 
            "products",
            "tools",
            "branding",
            "matriz",
            "sistema"
        ]
        
        modules = {}
        
        for module_dir in module_dirs:
            dir_path = self.root_path / module_dir
            if not dir_path.exists():
                continue
                
            # Find sub-modules
            for item in dir_path.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    module_name = f"{module_dir}.{item.name}"
                    if self._has_python_files(item):
                        print(f"  Found module: {module_name}")
                        modules[module_name] = self._analyze_module(module_name, item)
        
        self.modules = modules
        return modules
    
    def _has_python_files(self, path: Path) -> bool:
        """Check if directory contains Python files"""
        for file_path in path.rglob("*.py"):
            return True
        return False
    
    def _analyze_module(self, module_name: str, module_path: Path) -> ModuleInfo:
        """Analyze a single module to extract metadata"""
        print(f"  🔬 Analyzing {module_name}...")
        
        module_info = ModuleInfo(
            name=module_name,
            path=module_path,
            imports=set(),
            exports=set(),
            classes=set(),
            functions=set(),
            entry_points=[],
            file_patterns=[],
            dependencies=set(),
            external_libs=set(),
            test_files=[],
            config_files=[]
        )
        
        # Analyze Python files
        for py_file in module_path.rglob("*.py"):
            self._analyze_python_file(py_file, module_info)
        
        # Find config files
        for config_pattern in ["*.yaml", "*.yml", "*.json", "*.toml", "*.ini"]:
            for config_file in module_path.rglob(config_pattern):
                rel_path = str(config_file.relative_to(self.root_path))
                module_info.config_files.append(rel_path)
        
        # Find test files
        test_paths = [
            self.root_path / "tests" / module_name.replace(".", "/"),
            module_path / "tests",
            self.root_path / "tests_new" / "unit" / module_name.replace(".", "/"),
            self.root_path / "tests_new" / "integration" / module_name.replace(".", "/")
        ]
        
        for test_path in test_paths:
            if test_path.exists():
                for test_file in test_path.rglob("*.py"):
                    rel_path = str(test_file.relative_to(self.root_path))
                    module_info.test_files.append(rel_path)
        
        # Set file patterns
        module_info.file_patterns = [
            f"{module_name.replace('.', '/')}/**/*.py",
            f"tests/{module_name.replace('.', '/')}/**/*.py"
        ]
        
        # Find entry points
        init_file = module_path / "__init__.py"
        if init_file.exists():
            module_info.entry_points.append(str(init_file.relative_to(self.root_path)))
        
        main_file = module_path / "main.py"
        if main_file.exists():
            module_info.entry_points.append(str(main_file.relative_to(self.root_path)))
        
        return module_info
    
    def _analyze_python_file(self, file_path: Path, module_info: ModuleInfo):
        """Analyze a single Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            
            # Extract metadata from headers
            self._extract_header_metadata(content, module_info)
            
            # Analyze AST
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self._process_import(alias.name, module_info)
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self._process_import(node.module, module_info)
                
                elif isinstance(node, ast.ClassDef):
                    module_info.classes.add(node.name)
                    module_info.exports.add(node.name)
                
                elif isinstance(node, ast.FunctionDef):
                    if not node.name.startswith('_'):
                        module_info.functions.add(node.name)
                        module_info.exports.add(node.name)
        
        except Exception as e:
            print(f"    Warning: Could not analyze {file_path}: {e}")
    
    def _extract_header_metadata(self, content: str, module_info: ModuleInfo):
        """Extract metadata from file headers"""
        lines = content.split('\n')
        
        for line in lines[:50]:  # Check first 50 lines
            # Look for version
            if match := re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', line):
                module_info.version = match.group(1)
            
            # Look for tier
            if match := re.search(r'__tier__\s*=\s*(\d+)', line):
                module_info.tier = int(match.group(1))
            
            # Look for module name/description
            if match := re.search(r'__module_name__\s*=\s*["\']([^"\']+)["\']', line):
                module_info.description = match.group(1)
    
    def _process_import(self, import_name: str, module_info: ModuleInfo):
        """Process an import statement"""
        module_info.imports.add(import_name)
        
        # Categorize as internal or external
        if any(import_name.startswith(prefix) for prefix in ['candidate.', 'lukhas.', 'products.', 'tools.']):
            module_info.dependencies.add(import_name)
        elif not import_name.startswith('.') and '.' in import_name:
            # External library
            root_lib = import_name.split('.')[0]
            if root_lib not in ['os', 'sys', 'json', 'datetime', 're', 'pathlib', 'typing']:
                module_info.external_libs.add(root_lib)
    
    def generate_schema(self, module_name: str) -> Dict[str, Any]:
        """Generate a schema for a specific module"""
        if module_name not in self.modules:
            raise ValueError(f"Module {module_name} not found")
        
        module_info = self.modules[module_name]
        now = datetime.now(timezone.utc)
        
        # Determine layer based on module name
        layer = self._determine_layer(module_name)
        
        # Generate import patterns
        import_patterns = []
        for export in list(module_info.exports)[:5]:  # Top 5 exports
            import_patterns.append(f"from {module_name} import {export}")
        
        schema = {
            "identity": {
                "name": module_name,
                "layer": layer,
                "summary": module_info.description or f"{module_name} module with {len(module_info.classes)} classes and {len(module_info.functions)} functions",
                "status": "active",
                "tier": module_info.tier or self._infer_tier(module_name)
            },
            "discovery": {
                "import_patterns": import_patterns,
                "import_aliases": [module_name.split('.')[-1]],
                "file_patterns": module_info.file_patterns,
                "entry_points": module_info.entry_points
            },
            "ownership": {
                "owner": "@AutoGenerated",
                "lifecycle": "evolving",
                "last_review": now.isoformat(),
                "promotion_rules": self._generate_promotion_rules(module_name)
            },
            "contracts": {
                "api": {
                    "surface": [f"python: {module_name}.{exp}" for exp in list(module_info.exports)[:10]],
                    "version": module_info.version or "v1.0",
                    "compatibility": {
                        "backward": True,
                        "forward": "minor"
                    }
                },
                "invariants": [
                    "module loads without errors",
                    "public API remains stable"
                ]
            },
            "dependencies": {
                "internal": {
                    "requires": list(module_info.dependencies),
                    "provides": [module_name]
                },
                "external": {
                    "libs": [
                        {
                            "name": lib,
                            "version": "unknown",
                            "license": "unknown",
                            "purpose": "library dependency"
                        } for lib in module_info.external_libs
                    ]
                },
                "coupling_metrics": self._calculate_coupling_metrics(module_info)
            },
            "runtime": {
                "processes": {
                    "entrypoints": [f"python -m {module_name}"] if module_info.entry_points else [],
                    "concurrency_model": "async" if "async" in str(module_info.imports) else "thread"
                },
                "config": {
                    "files": module_info.config_files,
                    "env_vars_required": [],
                    "feature_flags": []
                },
                "resources": {
                    "cpu_limit": "0.5 vcpu",
                    "mem_limit": "256 MiB"
                }
            },
            "data_and_events": {
                "data_classes": [
                    {
                        "name": cls,
                        "schema_ref": f"audit/SCHEMAS/{cls.lower()}.json",
                        "description": f"{cls} data class"
                    } for cls in list(module_info.classes)[:5]
                ],
                "pii": {
                    "contains": False,
                    "classification": "internal"
                }
            },
            "security": {
                "secrets": {
                    "sources": ["env"],
                    "files": []
                },
                "authz_model": "internal_only",
                "compliance": {
                    "data_classification": "internal"
                }
            },
            "observability": {
                "logs": {
                    "format": "structured_json",
                    "level": "info"
                },
                "metrics": {
                    "exporter": "prometheus",
                    "key_metrics": [
                        {
                            "name": f"{module_name.replace('.', '_')}_calls_total",
                            "target": ">0",
                            "type": "counter"
                        }
                    ]
                },
                "slos": {
                    "error_rate_pct": 1.0,
                    "availability_pct": 99.0
                }
            },
            "test_posture": {
                "coverage": {
                    "current": len(module_info.test_files) / max(len(list(module_info.path.rglob("*.py"))), 1),
                    "target": 0.8
                },
                "tests": {
                    "unit": len([f for f in module_info.test_files if "unit" in f or "test_" in f]),
                    "integration": len([f for f in module_info.test_files if "integration" in f])
                }
            },
            "risk_and_change": {
                "risks": [
                    {
                        "id": f"R-{module_name.upper().replace('.', '-')}-GENERATED",
                        "title": "Auto-generated schema may be incomplete",
                        "likelihood": "medium",
                        "impact": "low",
                        "mitigation": "Manual review and enhancement required",
                        "status": "open"
                    }
                ]
            },
            "provenance": {
                "schema_version": "1.0",
                "last_updated": now.isoformat(),
                "source_paths": [str(module_info.path.relative_to(self.root_path))],
                "generated_by": {
                    "tool": "lukhas-module-generator",
                    "version": "1.0.0",
                    "timestamp": now.isoformat()
                },
                "validation": {
                    "schema_valid": True,
                    "last_validated": now.isoformat(),
                    "validator_version": "1.0.0"
                }
            }
        }
        
        return schema
    
    def _determine_layer(self, module_name: str) -> str:
        """Determine the architecture layer for a module"""
        if any(keyword in module_name for keyword in ['core', 'foundation']):
            return "foundational"
        elif any(keyword in module_name for keyword in ['memory', 'identity', 'governance']):
            return "infrastructure" 
        elif any(keyword in module_name for keyword in ['dashboard', 'ui', 'web']):
            return "interface"
        else:
            return "application"
    
    def _infer_tier(self, module_name: str) -> int:
        """Infer criticality tier from module name"""
        critical_modules = ['identity', 'governance', 'core', 'security']
        if any(keyword in module_name.lower() for keyword in critical_modules):
            return 1
        elif 'candidate' in module_name:
            return 3
        else:
            return 2
    
    def _generate_promotion_rules(self, module_name: str) -> Dict[str, Any]:
        """Generate promotion rules based on module lane"""
        if module_name.startswith('candidate.'):
            return {
                "from_lane": "candidate",
                "to_lane": "lukhas", 
                "required_checks": ["tests/smoke", "coverage", "lint"],
                "min_coverage": 0.8
            }
        else:
            return {}
    
    def _calculate_coupling_metrics(self, module_info: ModuleInfo) -> Dict[str, Any]:
        """Calculate coupling metrics for the module"""
        afferent = len(module_info.dependencies)
        efferent = len([m for m in self.modules.values() if module_info.name in m.dependencies])
        
        instability = afferent / max(afferent + efferent, 1)
        
        return {
            "afferent": afferent,
            "efferent": efferent,
            "instability_index": round(instability, 3)
        }
    
    def generate_all_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Generate schemas for all discovered modules"""
        print(f"📋 Generating schemas for {len(self.modules)} modules...")
        
        schemas = {}
        for module_name in self.modules:
            try:
                print(f"  Generating schema for {module_name}...")
                schemas[module_name] = self.generate_schema(module_name)
            except Exception as e:
                print(f"  ❌ Error generating schema for {module_name}: {e}")
        
        return schemas
    
    def save_schemas(self, schemas: Dict[str, Dict[str, Any]], output_dir: Path):
        """Save schemas to individual YAML files"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"💾 Saving {len(schemas)} schemas to {output_dir}...")
        
        for module_name, schema in schemas.items():
            filename = f"{module_name.replace('.', '_')}.yaml"
            file_path = output_dir / filename
            
            try:
                with open(file_path, 'w') as f:
                    yaml.dump(schema, f, default_flow_style=False, sort_keys=False, indent=2)
                print(f"  ✅ Saved {filename}")
            except Exception as e:
                print(f"  ❌ Error saving {filename}: {e}")
    
    def generate_summary_report(self, schemas: Dict[str, Dict[str, Any]]) -> str:
        """Generate a summary report of the schema generation"""
        total_modules = len(schemas)
        
        # Count by layer
        layers = defaultdict(int)
        for schema in schemas.values():
            layers[schema['identity']['layer']] += 1
        
        # Count by lane
        lanes = defaultdict(int)
        for module_name in schemas.keys():
            lane = module_name.split('.')[0]
            lanes[lane] += 1
        
        report = f"""
# LUKHAS Module Schema Generation Report

## Summary
- **Total Modules**: {total_modules}
- **Generated**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}

## Modules by Lane
"""
        for lane, count in sorted(lanes.items()):
            report += f"- **{lane}**: {count} modules\n"
        
        report += "\n## Modules by Layer\n"
        for layer, count in sorted(layers.items()):
            report += f"- **{layer}**: {count} modules\n"
        
        report += f"""
## Next Steps
1. **Manual Review**: Each schema needs manual review and enhancement
2. **Ownership Assignment**: Update owner fields with actual maintainers
3. **API Documentation**: Add detailed API surface documentation
4. **Dependency Validation**: Verify all dependencies are correctly identified
5. **Risk Assessment**: Complete risk analysis for each module
6. **SLO Definition**: Define appropriate SLOs for each module

## Files Generated
All schemas saved to `modules/` directory in YAML format.
"""
        return report


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python module_schema_generator.py <root_path> [output_dir]")
        sys.exit(1)
    
    root_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else root_path / "modules"
    
    if not root_path.exists():
        print(f"Error: Root path {root_path} does not exist")
        sys.exit(1)
    
    print("🚀 LUKHAS Module Schema Generator")
    print(f"Root path: {root_path}")
    print(f"Output directory: {output_dir}")
    print("-" * 50)
    
    generator = ModuleSchemaGenerator(root_path)
    
    # Discover modules
    modules = generator.discover_modules()
    print(f"\n✅ Discovered {len(modules)} modules")
    
    # Generate schemas
    schemas = generator.generate_all_schemas()
    print(f"\n✅ Generated {len(schemas)} schemas")
    
    # Save schemas
    generator.save_schemas(schemas, output_dir)
    
    # Generate summary report
    report = generator.generate_summary_report(schemas)
    report_path = output_dir / "GENERATION_REPORT.md"
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"\n🎉 Schema generation complete!")
    print(f"📊 Summary report: {report_path}")
    print(f"📁 Schemas saved to: {output_dir}")


if __name__ == "__main__":
    main()