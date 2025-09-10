#!/usr/bin/env python3
"""
LUKHAS Module Discovery System

Dynamic module registry and discovery system for runtime module management.
Integrates with the module schema system to provide live module information.

Copyright (c) 2025 LUKHAS AI. All rights reserved.
"""

import json
import time
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set

import yaml


@dataclass
class ModuleInfo:
    """Runtime module information"""
    name: str
    layer: str
    status: str
    tier: int
    owner: str
    lifecycle: str
    api_version: str
    entry_points: List[str]
    dependencies: List[str]
    health_status: str = "unknown"
    last_seen: Optional[datetime] = None
    metrics: Dict = None
    
    def __post_init__(self):
        if self.metrics is None:
            self.metrics = {}


class ModuleRegistry:
    """Central registry for all LUKHAS modules"""
    
    def __init__(self, schemas_dir: Path):
        self.schemas_dir = Path(schemas_dir)
        self.modules = {}
        self.dependency_graph = defaultdict(set)
        self.reverse_deps = defaultdict(set)
        self.last_update = None
        self._load_schemas()
    
    def _load_schemas(self) -> None:
        """Load all module schemas into registry"""
        print("🔄 Loading module schemas...")
        
        schema_files = list(self.schemas_dir.glob("*.yaml"))
        schema_files = [f for f in schema_files if f.name != 'module_schema_template.yaml']
        
        for schema_file in schema_files:
            try:
                with open(schema_file, 'r') as f:
                    schema = yaml.safe_load(f)
                
                identity = schema.get('identity', {})
                ownership = schema.get('ownership', {})
                contracts = schema.get('contracts', {}).get('api', {})
                runtime = schema.get('runtime', {}).get('processes', {})
                dependencies = schema.get('dependencies', {}).get('internal', {})
                
                module_info = ModuleInfo(
                    name=identity.get('name', ''),
                    layer=identity.get('layer', 'unknown'),
                    status=identity.get('status', 'unknown'),
                    tier=identity.get('tier', 5),
                    owner=ownership.get('owner', '@unknown'),
                    lifecycle=ownership.get('lifecycle', 'unknown'),
                    api_version=contracts.get('version', 'v1.0'),
                    entry_points=runtime.get('entrypoints', []),
                    dependencies=dependencies.get('requires', [])
                )
                
                if module_info.name:
                    self.modules[module_info.name] = module_info
                    
                    # Build dependency graph
                    for dep in module_info.dependencies:
                        self.dependency_graph[module_info.name].add(dep)
                        self.reverse_deps[dep].add(module_info.name)
                
            except Exception as e:
                print(f"Warning: Could not load schema {schema_file.name}: {e}")
        
        self.last_update = datetime.now(timezone.utc)
        print(f"✅ Loaded {len(self.modules)} modules")
    
    def discover_modules(self, filters: Dict = None) -> List[ModuleInfo]:
        """Discover modules based on filters"""
        if filters is None:
            filters = {}
        
        results = []
        for module in self.modules.values():
            if self._matches_filters(module, filters):
                results.append(module)
        
        return results
    
    def _matches_filters(self, module: ModuleInfo, filters: Dict) -> bool:
        """Check if module matches search filters"""
        for key, value in filters.items():
            module_value = getattr(module, key, None)
            
            if isinstance(value, str):
                if value not in str(module_value):
                    return False
            elif isinstance(value, list):
                if module_value not in value:
                    return False
            elif module_value != value:
                return False
        
        return True
    
    def get_module(self, name: str) -> Optional[ModuleInfo]:
        """Get module by name"""
        return self.modules.get(name)
    
    def get_dependencies(self, module_name: str, recursive: bool = False) -> Set[str]:
        """Get module dependencies"""
        if module_name not in self.modules:
            return set()
        
        deps = set(self.dependency_graph.get(module_name, set()))
        
        if recursive:
            all_deps = deps.copy()
            for dep in deps:
                all_deps.update(self.get_dependencies(dep, recursive=True))
            return all_deps
        
        return deps
    
    def get_dependents(self, module_name: str, recursive: bool = False) -> Set[str]:
        """Get modules that depend on this module"""
        if module_name not in self.modules:
            return set()
        
        dependents = set(self.reverse_deps.get(module_name, set()))
        
        if recursive:
            all_dependents = dependents.copy()
            for dep in dependents:
                all_dependents.update(self.get_dependents(dep, recursive=True))
            return all_dependents
        
        return dependents
    
    def get_critical_modules(self) -> List[ModuleInfo]:
        """Get all tier 1 (critical) modules"""
        return [m for m in self.modules.values() if m.tier == 1]
    
    def get_modules_by_layer(self, layer: str) -> List[ModuleInfo]:
        """Get modules by architecture layer"""
        return [m for m in self.modules.values() if m.layer == layer]
    
    def get_modules_by_owner(self, owner: str) -> List[ModuleInfo]:
        """Get modules by owner"""
        return [m for m in self.modules.values() if m.owner == owner]
    
    def validate_deployment_order(self) -> List[List[str]]:
        """Generate module deployment order based on dependencies"""
        # Topological sort for deployment ordering
        in_degree = {}
        for module in self.modules:
            in_degree[module] = 0
        
        for module, deps in self.dependency_graph.items():
            for dep in deps:
                if dep in in_degree:
                    in_degree[module] += 1
        
        # Generate deployment waves
        waves = []
        remaining = set(self.modules.keys())
        
        while remaining:
            # Find modules with no dependencies in current wave
            current_wave = []
            for module in remaining:
                if in_degree[module] == 0:
                    current_wave.append(module)
            
            if not current_wave:
                # Circular dependency detected
                waves.append(list(remaining))  # Deploy remaining in parallel
                break
            
            waves.append(current_wave)
            
            # Update in-degrees for next wave
            for module in current_wave:
                remaining.remove(module)
                for dependent in self.reverse_deps.get(module, set()):
                    if dependent in remaining:
                        in_degree[dependent] -= 1
        
        return waves
    
    def generate_module_map(self) -> Dict:
        """Generate comprehensive module map"""
        return {
            "metadata": {
                "generated": datetime.now(timezone.utc).isoformat(),
                "total_modules": len(self.modules),
                "last_schema_update": self.last_update.isoformat() if self.last_update else None
            },
            "modules": {
                name: {
                    "info": asdict(module),
                    "dependencies": list(self.get_dependencies(name)),
                    "dependents": list(self.get_dependents(name)),
                    "deployment_critical": module.tier <= 2
                }
                for name, module in self.modules.items()
            },
            "statistics": {
                "by_layer": self._count_by_attribute("layer"),
                "by_tier": self._count_by_attribute("tier"),
                "by_lifecycle": self._count_by_attribute("lifecycle"),
                "by_owner": self._count_by_attribute("owner")
            },
            "deployment_waves": self.validate_deployment_order()
        }
    
    def _count_by_attribute(self, attr: str) -> Dict:
        """Count modules by attribute value"""
        counts = defaultdict(int)
        for module in self.modules.values():
            value = getattr(module, attr, 'unknown')
            counts[str(value)] += 1
        return dict(counts)
    
    def health_check(self) -> Dict:
        """Perform health check on module registry"""
        now = datetime.now(timezone.utc)
        
        issues = []
        warnings = []
        
        # Check for missing critical modules
        critical_modules = self.get_critical_modules()
        if len(critical_modules) < 5:
            issues.append("Less than 5 tier-1 critical modules found")
        
        # Check for orphaned modules
        for module_name, module in self.modules.items():
            deps = self.get_dependencies(module_name)
            missing_deps = [dep for dep in deps if dep not in self.modules]
            if missing_deps:
                warnings.append(f"{module_name} has missing dependencies: {missing_deps}")
        
        # Check for circular dependencies
        waves = self.validate_deployment_order()
        if len(waves) > 20:  # Heuristic for complex dependency graph
            warnings.append("Complex dependency graph detected (>20 deployment waves)")
        
        return {
            "status": "healthy" if not issues else "degraded",
            "timestamp": now.isoformat(),
            "total_modules": len(self.modules),
            "critical_modules": len(critical_modules),
            "issues": issues,
            "warnings": warnings,
            "deployment_complexity": len(waves)
        }


class ModuleDiscoveryAPI:
    """HTTP API wrapper for module discovery"""
    
    def __init__(self, registry: ModuleRegistry):
        self.registry = registry
    
    def search_modules(self, query: str, filters: Dict = None) -> List[Dict]:
        """Search modules by name or description"""
        if filters is None:
            filters = {}
        
        # Add text search to filters
        modules = self.registry.discover_modules(filters)
        
        if query:
            query = query.lower()
            modules = [
                m for m in modules 
                if query in m.name.lower() or query in m.owner.lower()
            ]
        
        return [asdict(m) for m in modules]
    
    def get_module_details(self, module_name: str) -> Optional[Dict]:
        """Get detailed module information"""
        module = self.registry.get_module(module_name)
        if not module:
            return None
        
        return {
            "module": asdict(module),
            "dependencies": list(self.registry.get_dependencies(module_name)),
            "dependents": list(self.registry.get_dependents(module_name)),
            "recursive_dependencies": list(self.registry.get_dependencies(module_name, recursive=True)),
            "recursive_dependents": list(self.registry.get_dependents(module_name, recursive=True))
        }
    
    def get_system_overview(self) -> Dict:
        """Get high-level system overview"""
        critical = self.registry.get_critical_modules()
        
        layers = {}
        for layer in ["foundational", "infrastructure", "application", "interface"]:
            layers[layer] = len(self.registry.get_modules_by_layer(layer))
        
        return {
            "total_modules": len(self.registry.modules),
            "critical_modules": len(critical),
            "layers": layers,
            "health": self.registry.health_check(),
            "last_update": self.registry.last_update.isoformat() if self.registry.last_update else None
        }


def main():
    """CLI interface for module discovery"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LUKHAS Module Discovery System")
    parser.add_argument("--schemas-dir", default="modules", help="Module schemas directory")
    parser.add_argument("--command", choices=["list", "search", "deps", "health", "map"], 
                       default="list", help="Command to execute")
    parser.add_argument("--module", help="Module name for specific operations")
    parser.add_argument("--query", help="Search query")
    parser.add_argument("--layer", help="Filter by architecture layer")
    parser.add_argument("--tier", type=int, help="Filter by tier")
    parser.add_argument("--owner", help="Filter by owner")
    parser.add_argument("--output", help="Output file for results")
    
    args = parser.parse_args()
    
    print("🚀 LUKHAS Module Discovery System")
    print("-" * 40)
    
    # Initialize registry
    registry = ModuleRegistry(Path(args.schemas_dir))
    api = ModuleDiscoveryAPI(registry)
    
    # Execute command
    result = None
    
    if args.command == "list":
        filters = {}
        if args.layer:
            filters["layer"] = args.layer
        if args.tier:
            filters["tier"] = args.tier
        if args.owner:
            filters["owner"] = args.owner
        
        modules = registry.discover_modules(filters)
        print(f"\nFound {len(modules)} modules:")
        for module in sorted(modules, key=lambda m: m.name):
            print(f"  {module.name} ({module.layer}, tier {module.tier}) - {module.owner}")
        result = [asdict(m) for m in modules]
    
    elif args.command == "search":
        if not args.query:
            print("Error: --query required for search command")
            return
        
        modules = api.search_modules(args.query)
        print(f"\nSearch results for '{args.query}':")
        for module in modules:
            print(f"  {module['name']} - {module['owner']}")
        result = modules
    
    elif args.command == "deps":
        if not args.module:
            print("Error: --module required for deps command")
            return
        
        details = api.get_module_details(args.module)
        if not details:
            print(f"Module '{args.module}' not found")
            return
        
        print(f"\nDependency information for {args.module}:")
        print(f"Dependencies: {details['dependencies']}")
        print(f"Dependents: {details['dependents']}")
        result = details
    
    elif args.command == "health":
        health = registry.health_check()
        print(f"\nSystem Health: {health['status'].upper()}")
        print(f"Total Modules: {health['total_modules']}")
        print(f"Critical Modules: {health['critical_modules']}")
        
        if health['issues']:
            print("\nIssues:")
            for issue in health['issues']:
                print(f"  ❌ {issue}")
        
        if health['warnings']:
            print("\nWarnings:")
            for warning in health['warnings']:
                print(f"  ⚠️  {warning}")
        
        result = health
    
    elif args.command == "map":
        module_map = registry.generate_module_map()
        print(f"\nGenerated module map with {module_map['metadata']['total_modules']} modules")
        print(f"Deployment waves: {len(module_map['deployment_waves'])}")
        result = module_map
    
    # Save output if requested
    if args.output and result:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\n💾 Results saved to {args.output}")


if __name__ == "__main__":
    main()