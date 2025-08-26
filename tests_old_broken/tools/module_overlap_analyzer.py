#!/usr/bin/env python3
"""
Module Overlap and Integration Analyzer for LUKHAS AI
Identifies overlapping logic and potential GLYPH integration points
"""

import os
import ast
import re
from pathlib import Path
from collections import defaultdict
import json

class LUKHASModuleOverlapAnalyzer:
    """Analyze module overlap and integration opportunities via GLYPH"""
    
    def __init__(self):
        self.modules = {}
        self.functionality_map = defaultdict(list)
        self.glyph_ready = []
        self.integration_opportunities = []
        self.overlapping_logic = []
        
    def analyze_lukhas_modules(self):
        """Analyze all LUKHAS modules for overlap and integration"""
        print("🔮 LUKHAS Module Integration & Overlap Analysis")
        print("=" * 70)
        print("Analyzing modules for GLYPH integration and MATADA modularization...")
        print()
        
        # Analyze core modules
        self._analyze_core_modules()
        
        # Find overlapping functionality
        self._find_overlapping_logic()
        
        # Identify GLYPH integration points
        self._identify_glyph_integration()
        
        # Generate integration roadmap
        self._generate_integration_roadmap()
        
    def _analyze_core_modules(self):
        """Analyze core directory modules"""
        core_path = Path('core')
        
        # Categories of functionality
        functionality_patterns = {
            'consciousness': ['aware', 'conscious', 'reflect', 'think', 'cognit'],
            'memory': ['memory', 'store', 'recall', 'fold', 'remember'],
            'communication': ['message', 'communicate', 'send', 'receive', 'mailbox', 'event'],
            'identity': ['identity', 'auth', 'tier', 'access', 'permission'],
            'orchestration': ['orchestr', 'coordinate', 'manage', 'supervise', 'control'],
            'symbolic': ['symbol', 'glyph', 'token', 'semantic'],
            'neural': ['neural', 'network', 'brain', 'neuron'],
            'quantum': ['quantum', 'collapse', 'superposition', 'entangle'],
            'bio': ['bio', 'organic', 'evolve', 'adapt'],
            'swarm': ['swarm', 'colony', 'collective', 'hive'],
            'ethics': ['ethic', 'moral', 'govern', 'safe'],
            'integration': ['integrat', 'bridge', 'connect', 'adapt', 'interface']
        }
        
        # Scan all directories in core
        for subdir in core_path.iterdir():
            if not subdir.is_dir() or subdir.name.startswith('__'):
                continue
                
            module_info = {
                'path': str(subdir),
                'name': subdir.name,
                'files': [],
                'classes': [],
                'functions': [],
                'imports_glyph': False,
                'functionalities': set(),
                'integration_ready': False
            }
            
            # Analyze Python files in the directory
            for py_file in subdir.rglob('*.py'):
                if py_file.name == '__init__.py':
                    continue
                    
                try:
                    with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                    # Parse AST
                    try:
                        tree = ast.parse(content)
                        
                        # Extract classes and functions
                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef):
                                module_info['classes'].append(node.name)
                                
                                # Check class name for functionality
                                for func_type, patterns in functionality_patterns.items():
                                    if any(p in node.name.lower() for p in patterns):
                                        module_info['functionalities'].add(func_type)
                                        
                            elif isinstance(node, ast.FunctionDef):
                                module_info['functions'].append(node.name)
                                
                                # Check function name for functionality
                                for func_type, patterns in functionality_patterns.items():
                                    if any(p in node.name.lower() for p in patterns):
                                        module_info['functionalities'].add(func_type)
                        
                        # Check for GLYPH imports
                        if 'glyph' in content.lower() or 'GLYPH' in content:
                            module_info['imports_glyph'] = True
                            
                        # Check if module is integration-ready
                        if any(term in content for term in ['EventBus', 'MessageBus', 'glyph', 'symbolic']):
                            module_info['integration_ready'] = True
                            
                    except SyntaxError:
                        pass
                        
                    module_info['files'].append(py_file.name)
                    
                except Exception:
                    continue
            
            if module_info['files']:
                self.modules[subdir.name] = module_info
                
                # Map functionalities
                for func in module_info['functionalities']:
                    self.functionality_map[func].append(subdir.name)
    
    def _find_overlapping_logic(self):
        """Find modules with overlapping functionality"""
        print("\n🔄 OVERLAPPING LOGIC DETECTION:")
        print("-" * 50)
        
        for functionality, modules in self.functionality_map.items():
            if len(modules) > 1:
                overlap = {
                    'functionality': functionality,
                    'modules': modules,
                    'count': len(modules),
                    'integration_potential': 'high' if len(modules) > 3 else 'medium'
                }
                self.overlapping_logic.append(overlap)
                
                print(f"\n📍 {functionality.upper()} functionality found in {len(modules)} modules:")
                for mod in modules[:5]:  # Show first 5
                    glyph_status = "✅ GLYPH-ready" if self.modules[mod]['imports_glyph'] else "⚠️ Needs GLYPH"
                    print(f"   - core/{mod}/ {glyph_status}")
                if len(modules) > 5:
                    print(f"   ... and {len(modules)-5} more")
    
    def _identify_glyph_integration(self):
        """Identify modules ready for GLYPH integration"""
        print("\n\n🔮 GLYPH INTEGRATION READINESS:")
        print("-" * 50)
        
        glyph_ready = []
        needs_glyph = []
        
        for name, info in self.modules.items():
            if info['imports_glyph']:
                glyph_ready.append(name)
            elif info['classes'] or info['functions']:
                needs_glyph.append(name)
        
        print(f"\n✅ Modules already using GLYPH: {len(glyph_ready)}")
        for mod in glyph_ready[:10]:
            print(f"   - core/{mod}/")
            
        print(f"\n⚡ Modules ready for GLYPH integration: {len(needs_glyph)}")
        for mod in needs_glyph[:10]:
            functionalities = self.modules[mod]['functionalities']
            if functionalities:
                print(f"   - core/{mod}/ → {', '.join(functionalities)}")
    
    def _generate_integration_roadmap(self):
        """Generate integration roadmap for MATADA modularization"""
        print("\n\n🗺️ MATADA INTEGRATION ROADMAP:")
        print("-" * 50)
        
        # Group modules by integration priority
        priority_groups = {
            'critical': [],  # Core communication infrastructure
            'high': [],      # Heavily overlapping modules
            'medium': [],    # Some overlap
            'low': []        # Standalone modules
        }
        
        for name, info in self.modules.items():
            # Critical: communication and orchestration modules
            if 'communication' in info['functionalities'] or 'orchestration' in info['functionalities']:
                priority_groups['critical'].append(name)
            # High: modules with multiple overlaps
            elif len(info['functionalities']) >= 2:
                priority_groups['high'].append(name)
            # Medium: modules with some functionality
            elif info['functionalities']:
                priority_groups['medium'].append(name)
            else:
                priority_groups['low'].append(name)
        
        print("\n🎯 INTEGRATION PRIORITIES:")
        
        print("\n1️⃣ CRITICAL (Communication Infrastructure):")
        for mod in priority_groups['critical'][:10]:
            print(f"   core/{mod}/ → Connect to GLYPH message bus")
            
        print("\n2️⃣ HIGH PRIORITY (Overlapping Logic):")
        for overlap in self.overlapping_logic[:5]:
            if overlap['count'] > 2:
                print(f"   {overlap['functionality']}: Consolidate {overlap['count']} modules via GLYPH")
                
        print("\n3️⃣ MEDIUM PRIORITY (Functional Modules):")
        for mod in priority_groups['medium'][:5]:
            funcs = self.modules[mod]['functionalities']
            if funcs:
                print(f"   core/{mod}/ → Enable {', '.join(funcs)} via GLYPH")
        
        # MATADA specific recommendations
        print("\n\n🚀 MATADA MODULARIZATION STRATEGY:")
        print("-" * 50)
        print("\n1. GLYPH Engine as Universal Communication Layer:")
        print("   - All modules communicate via GLYPH tokens")
        print("   - Symbolic message passing between modules")
        print("   - Type-safe inter-module contracts")
        
        print("\n2. Module Categories to Consolidate:")
        for func, modules in sorted(self.functionality_map.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
            print(f"   - {func}: {len(modules)} modules → 1 unified service")
            
        print("\n3. Connection Points Needed:")
        unused_but_important = ['neural', 'quantum', 'bio_systems', 'swarm']
        for mod in unused_but_important:
            if mod in self.modules and mod not in priority_groups['critical']:
                print(f"   - Connect core/{mod}/ to main orchestration")
                
        print("\n4. Event-Driven Architecture:")
        print("   - EventBus for async communication")
        print("   - GLYPH tokens for message typing")
        print("   - Mailbox pattern for module isolation")
        
        # Summary statistics
        print("\n\n📊 SUMMARY STATISTICS:")
        print("-" * 50)
        total_modules = len(self.modules)
        glyph_ready = sum(1 for m in self.modules.values() if m['imports_glyph'])
        integration_ready = sum(1 for m in self.modules.values() if m['integration_ready'])
        
        print(f"Total modules analyzed: {total_modules}")
        print(f"GLYPH-ready modules: {glyph_ready} ({glyph_ready/total_modules*100:.1f}%)")
        print(f"Integration-ready: {integration_ready} ({integration_ready/total_modules*100:.1f}%)")
        print(f"Overlapping functionalities: {len(self.overlapping_logic)}")
        print(f"Unique functionality types: {len(self.functionality_map)}")
        
        # Key insight
        print("\n💡 KEY INSIGHT:")
        print("The LUKHAS architecture has all the pieces but needs GLYPH-based")
        print("integration to connect them. MATADA modularization can unify")
        print(f"{len(self.overlapping_logic)} overlapping functionalities into a")
        print("cohesive, message-driven architecture.")

def main():
    analyzer = LUKHASModuleOverlapAnalyzer()
    analyzer.analyze_lukhas_modules()

if __name__ == "__main__":
    main()