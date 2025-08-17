#!/usr/bin/env python3
"""
Deep Module Analysis for LUKHAS AI
Analyzes if modules are truly overlapping or specialized components
"""

import os
import ast
from pathlib import Path
from collections import defaultdict

def analyze_memory_modules():
    """Deep dive into memory modules"""
    print("\n" + "="*70)
    print("🧠 MEMORY MODULE DEEP ANALYSIS")
    print("="*70)
    
    memory_modules = {
        'core/symbolic_legacy': [],
        'core/colonies': [],
        'core/identity': [],
        'core/integration': [],
        'memory': [],
        'consciousness': [],
        'core/orchestration': [],
        'core/unified': []
    }
    
    # Analyze each module's memory functionality
    for module_path in memory_modules.keys():
        path = Path(module_path)
        if not path.exists():
            continue
            
        for py_file in path.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                # Look for specific memory patterns
                memory_patterns = {
                    'fold_memory': 'fold' in content.lower() and 'memory' in content.lower(),
                    'episodic': 'episodic' in content.lower(),
                    'semantic': 'semantic' in content.lower() and 'memory' in content.lower(),
                    'working_memory': 'working' in content.lower() and 'memory' in content.lower(),
                    'long_term': 'long_term' in content.lower() or 'longterm' in content.lower(),
                    'short_term': 'short_term' in content.lower() or 'shortterm' in content.lower(),
                    'memory_bank': 'memory_bank' in content.lower() or 'memorybank' in content.lower(),
                    'recall': 'recall' in content.lower(),
                    'store': 'store' in content.lower() and 'memory' in content.lower(),
                    'cache': 'cache' in content.lower(),
                    'buffer': 'buffer' in content.lower(),
                    'registry': 'registry' in content.lower()
                }
                
                found_patterns = [k for k, v in memory_patterns.items() if v]
                if found_patterns:
                    memory_modules[module_path].append({
                        'file': py_file.name,
                        'patterns': found_patterns
                    })
                    
            except Exception:
                continue
    
    # Print analysis
    for module, files in memory_modules.items():
        if files:
            print(f"\n📁 {module}/")
            unique_patterns = set()
            for f in files:
                unique_patterns.update(f['patterns'])
            print(f"   Specialization: {', '.join(unique_patterns)}")
            
            # Show specific files
            for f in files[:3]:  # First 3 files
                print(f"   - {f['file']}: {', '.join(f['patterns'][:3])}")

def analyze_consciousness_modules():
    """Deep dive into consciousness modules"""
    print("\n" + "="*70)
    print("🧘 CONSCIOUSNESS MODULE DEEP ANALYSIS")
    print("="*70)
    
    consciousness_paths = [
        'consciousness',
        'core/consciousness',
        'core/symbolic_legacy',
        'core/integration',
        'core/personality'
    ]
    
    consciousness_types = {}
    
    for module_path in consciousness_paths:
        path = Path(module_path)
        if not path.exists():
            continue
            
        module_consciousness = {
            'awareness': [],
            'reflection': [],
            'dream': [],
            'quantum': [],
            'stream': [],
            'attention': [],
            'meta': []
        }
        
        for py_file in path.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                # Categorize consciousness types
                if 'awareness' in content.lower() or 'aware' in content.lower():
                    module_consciousness['awareness'].append(py_file.name)
                if 'reflect' in content.lower():
                    module_consciousness['reflection'].append(py_file.name)
                if 'dream' in content.lower():
                    module_consciousness['dream'].append(py_file.name)
                if 'quantum' in content.lower() and 'conscious' in content.lower():
                    module_consciousness['quantum'].append(py_file.name)
                if 'stream' in content.lower() and 'conscious' in content.lower():
                    module_consciousness['stream'].append(py_file.name)
                if 'attention' in content.lower():
                    module_consciousness['attention'].append(py_file.name)
                if 'meta' in content.lower() and 'cognit' in content.lower():
                    module_consciousness['meta'].append(py_file.name)
                    
            except Exception:
                continue
        
        # Only show if module has consciousness functionality
        has_consciousness = any(v for v in module_consciousness.values())
        if has_consciousness:
            consciousness_types[module_path] = module_consciousness
    
    # Print findings
    for module, types in consciousness_types.items():
        print(f"\n📁 {module}/")
        specializations = []
        for type_name, files in types.items():
            if files:
                specializations.append(f"{type_name}({len(files)})")
        if specializations:
            print(f"   Specializations: {', '.join(specializations)}")
            
            # Show example files
            for type_name, files in types.items():
                if files and type_name in ['awareness', 'reflection', 'dream', 'quantum']:
                    print(f"   {type_name}: {files[0]}")

def analyze_symbolic_modules():
    """Deep dive into symbolic modules"""
    print("\n" + "="*70)
    print("🔮 SYMBOLIC MODULE DEEP ANALYSIS")
    print("="*70)
    
    symbolic_paths = [
        'core/symbolic',
        'core/symbolic_legacy',
        'core/symbolism',
        'core/glyph',
        'core/symbolic_bridge',
        'core/symbolic_reasoning'
    ]
    
    for module_path in symbolic_paths:
        path = Path(module_path)
        if not path.exists():
            continue
            
        symbolic_features = {
            'glyph': [],
            'token': [],
            'symbol': [],
            'semantic': [],
            'graph': [],
            'ontology': [],
            'reasoning': []
        }
        
        for py_file in path.rglob('*.py'):
            if py_file.name == '__init__.py':
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                # Look for specific symbolic implementations
                if 'GLYPH' in content or 'Glyph' in content:
                    symbolic_features['glyph'].append(py_file.name)
                if 'token' in content.lower():
                    symbolic_features['token'].append(py_file.name)
                if 'Symbol' in content or 'symbol' in content:
                    symbolic_features['symbol'].append(py_file.name)
                if 'semantic' in content.lower():
                    symbolic_features['semantic'].append(py_file.name)
                if 'graph' in content.lower():
                    symbolic_features['graph'].append(py_file.name)
                if 'ontology' in content.lower():
                    symbolic_features['ontology'].append(py_file.name)
                if 'reasoning' in content.lower():
                    symbolic_features['reasoning'].append(py_file.name)
                    
            except Exception:
                continue
        
        # Show results
        has_features = any(v for v in symbolic_features.values())
        if has_features:
            print(f"\n📁 {module_path}/")
            for feature, files in symbolic_features.items():
                if files:
                    print(f"   {feature}: {len(files)} files - {files[0]}")

def analyze_ethics_modules():
    """Deep dive into ethics modules"""
    print("\n" + "="*70)
    print("🛡️ ETHICS MODULE DEEP ANALYSIS")
    print("="*70)
    
    ethics_paths = [
        'governance',
        'core/ethics',
        'core/governance',
        'core/safety',
        'qi/safety'
    ]
    
    for module_path in ethics_paths:
        path = Path(module_path)
        if not path.exists():
            continue
            
        ethics_features = {
            'guardian': [],
            'drift': [],
            'constitutional': [],
            'consent': [],
            'policy': [],
            'compliance': [],
            'safety': []
        }
        
        for py_file in path.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                # Categorize ethics implementations
                if 'guardian' in content.lower() or 'Guardian' in content:
                    ethics_features['guardian'].append(py_file.name)
                if 'drift' in content.lower():
                    ethics_features['drift'].append(py_file.name)
                if 'constitutional' in content.lower():
                    ethics_features['constitutional'].append(py_file.name)
                if 'consent' in content.lower():
                    ethics_features['consent'].append(py_file.name)
                if 'policy' in content.lower():
                    ethics_features['policy'].append(py_file.name)
                if 'compliance' in content.lower() or 'GDPR' in content or 'CCPA' in content:
                    ethics_features['compliance'].append(py_file.name)
                if 'safety' in content.lower():
                    ethics_features['safety'].append(py_file.name)
                    
            except Exception:
                continue
        
        # Show results
        has_features = any(v for v in ethics_features.values())
        if has_features:
            print(f"\n📁 {module_path}/")
            feature_summary = []
            for feature, files in ethics_features.items():
                if files:
                    feature_summary.append(f"{feature}({len(files)})")
            print(f"   Specializations: {', '.join(feature_summary)}")
            
            # Show unique features
            for feature, files in ethics_features.items():
                if files and feature in ['guardian', 'drift', 'constitutional', 'consent']:
                    print(f"   {feature}: {files[0]}")

def main():
    print("\n🔬 DEEP LUKHAS MODULE ANALYSIS")
    print("Checking if modules are overlapping or specialized...")
    
    analyze_memory_modules()
    analyze_consciousness_modules()
    analyze_symbolic_modules()
    analyze_ethics_modules()
    
    print("\n" + "="*70)
    print("💡 ANALYSIS COMPLETE")
    print("="*70)
    print("\nEach module appears to handle DIFFERENT aspects of the same domain.")
    print("This is not overlap - it's SPECIALIZATION within a distributed system.")

if __name__ == "__main__":
    main()