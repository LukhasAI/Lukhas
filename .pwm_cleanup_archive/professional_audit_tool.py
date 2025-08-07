#!/usr/bin/env python3
"""
LUKHAS Professional System Audit Tool
Generates comprehensive connectivity report with metadata for commercial modularization
"""

import os
import ast
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict
import hashlib

class ProfessionalAuditor:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.files_data = {}
        self.module_map = defaultdict(list)
        self.import_graph = defaultdict(set)
        self.scatter_analysis = defaultdict(list)
        self.personality_files = set()
        self.commercial_modules = {}
        
        # System categories for proper organization
        self.system_categories = {
            'dream': ['dream', 'oneiric', 'rem', 'sleep'],
            'memory': ['memory', 'recall', 'episodic', 'semantic', 'fold'],
            'consciousness': ['consciousness', 'awareness', 'cognitive', 'reflection'],
            'bio': ['bio', 'biological', 'organic', 'mitochondria', 'endocrine'],
            'quantum': ['quantum', 'superposition', 'entangle', 'wave'],
            'identity': ['identity', 'auth', 'biometric', 'glyph'],
            'creativity': ['creativity', 'creative', 'haiku', 'artistic'],
            'ethics': ['ethics', 'ethical', 'moral', 'governance'],
            'learning': ['learning', 'learn', 'meta_learning', 'adaptation'],
            'security': ['security', 'privacy', 'zkp', 'encrypt'],
            'api': ['api', 'endpoint', 'rest', 'commerce'],
            'bridge': ['bridge', 'adapter', 'connector', 'integration'],
            'core': ['core', 'foundation', 'base', 'fundamental']
        }
        
        # Personality-critical patterns
        self.personality_patterns = [
            'creative_personality', 'brain', 'lukhas', 'voice', 'haiku',
            'dream_narrator', 'emotional', 'affect', 'personality'
        ]
        
        # Commercial potential indicators
        self.commercial_indicators = {
            'high': ['api', 'endpoint', 'service', 'client', 'interface', 'export'],
            'medium': ['adapter', 'bridge', 'integration', 'manager', 'handler'],
            'low': ['test', 'mock', 'internal', 'private', 'debug']
        }

    def audit_system(self):
        """Main audit entry point"""
        print("Starting comprehensive LUKHAS system audit...")
        
        # Phase 1: Collect all Python files
        self._collect_files()
        
        # Phase 2: Analyze each file
        self._analyze_files()
        
        # Phase 3: Detect scattered systems
        self._detect_scatter()
        
        # Phase 4: Identify personality files
        self._identify_personality_files()
        
        # Phase 5: Assess commercial potential
        self._assess_commercial_potential()
        
        # Phase 6: Generate consolidation plan
        consolidation_plan = self._generate_consolidation_plan()
        
        # Phase 7: Create final report
        report = self._create_report(consolidation_plan)
        
        return report

    def _collect_files(self):
        """Collect all Python files excluding test/cache directories"""
        for path in self.root_path.rglob("*.py"):
            if any(skip in str(path) for skip in ['__pycache__', '.git', 'node_modules', 'venv']):
                continue
                
            relative_path = path.relative_to(self.root_path)
            self.files_data[str(relative_path)] = {
                'path': str(relative_path),
                'size': path.stat().st_size,
                'name': path.name,
                'parent': str(relative_path.parent),
                'system': None,
                'imports': [],
                'exports': [],
                'classes': [],
                'functions': [],
                'dependencies': set(),
                'commercial_potential': 'low',
                'personality_critical': False,
                'scatter_status': 'unknown',
                'proposed_location': None,
                'consolidation_action': 'keep',
                'duplicate_of': None,
                'merge_candidates': []
            }

    def _analyze_files(self):
        """Analyze file contents for metadata"""
        for file_path, data in self.files_data.items():
            full_path = self.root_path / file_path
            
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse AST
                try:
                    tree = ast.parse(content)
                    self._extract_ast_info(tree, data, content)
                except:
                    # Fallback to regex for problematic files
                    self._extract_regex_info(content, data)
                
                # Determine system membership
                data['system'] = self._determine_system(file_path, content)
                
                # Check if file is misplaced
                data['scatter_status'] = self._check_scatter(file_path, data['system'])
                
            except Exception as e:
                data['error'] = str(e)

    def _extract_ast_info(self, tree, data, content):
        """Extract information from AST"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    data['imports'].append(alias.name)
                    self._add_dependency(data, alias.name)
                    
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    import_str = f"{module}.{alias.name}" if module else alias.name
                    data['imports'].append(import_str)
                    self._add_dependency(data, module)
                    
            elif isinstance(node, ast.ClassDef):
                data['classes'].append(node.name)
                if any(base.id == 'ABC' for base in node.bases if isinstance(base, ast.Name)):
                    data['exports'].append(node.name)
                    
            elif isinstance(node, ast.FunctionDef):
                data['functions'].append(node.name)
                if not node.name.startswith('_'):
                    data['exports'].append(node.name)

    def _extract_regex_info(self, content, data):
        """Fallback regex extraction"""
        # Extract imports
        import_pattern = r'(?:from\s+(\S+)\s+)?import\s+([^;\n]+)'
        for match in re.finditer(import_pattern, content):
            module = match.group(1) or ''
            imports = match.group(2)
            if module:
                data['imports'].append(module)
                self._add_dependency(data, module)
        
        # Extract classes
        class_pattern = r'class\s+(\w+)'
        data['classes'] = re.findall(class_pattern, content)
        
        # Extract functions
        func_pattern = r'def\s+(\w+)'
        data['functions'] = re.findall(func_pattern, content)

    def _add_dependency(self, data, module):
        """Add dependency tracking"""
        if module and not module.startswith('.'):
            # Track internal dependencies
            for system in self.system_categories:
                if module.startswith(system):
                    data['dependencies'].add(system)
                    break

    def _determine_system(self, file_path: str, content: str) -> str:
        """Determine which system a file belongs to"""
        path_lower = file_path.lower()
        content_lower = content.lower()
        
        # Check path-based assignment
        for system, keywords in self.system_categories.items():
            if any(keyword in path_lower for keyword in keywords):
                return system
        
        # Check content-based assignment
        for system, keywords in self.system_categories.items():
            keyword_count = sum(1 for keyword in keywords if keyword in content_lower)
            if keyword_count >= 2:  # At least 2 keywords to assign
                return system
        
        # Default assignment based on directory
        parts = file_path.split('/')
        if len(parts) > 0 and parts[0] in self.system_categories:
            return parts[0]
            
        return 'misc'

    def _check_scatter(self, file_path: str, system: str) -> str:
        """Check if file is in the wrong location"""
        parts = file_path.split('/')
        if len(parts) == 0:
            return 'unknown'
            
        current_dir = parts[0]
        
        # Special cases
        if system == 'dream' and current_dir not in ['dream', 'creativity']:
            return 'scattered'
        elif system == 'memory' and current_dir != 'memory':
            return 'scattered'
        elif system in ['consciousness', 'bio', 'quantum', 'identity'] and current_dir != system:
            return 'scattered'
            
        return 'correct'

    def _detect_scatter(self):
        """Detect scattered system components"""
        for file_path, data in self.files_data.items():
            if data['scatter_status'] == 'scattered':
                self.scatter_analysis[data['system']].append(file_path)
                
                # Propose new location
                if data['system'] == 'dream':
                    data['proposed_location'] = f"dream/{'/'.join(file_path.split('/')[1:])}"
                else:
                    data['proposed_location'] = f"{data['system']}/{'/'.join(file_path.split('/')[1:])}"

    def _identify_personality_files(self):
        """Identify personality-critical files"""
        for file_path, data in self.files_data.items():
            # Check filename
            if any(pattern in file_path.lower() for pattern in self.personality_patterns):
                data['personality_critical'] = True
                self.personality_files.add(file_path)
                continue
                
            # Check exports
            for export in data['exports']:
                if any(pattern in export.lower() for pattern in self.personality_patterns):
                    data['personality_critical'] = True
                    self.personality_files.add(file_path)
                    break

    def _assess_commercial_potential(self):
        """Assess commercial potential of modules"""
        for file_path, data in self.files_data.items():
            # Skip test files
            if 'test' in file_path.lower():
                data['commercial_potential'] = 'low'
                continue
                
            # Check indicators
            high_score = sum(1 for indicator in self.commercial_indicators['high'] 
                           if indicator in file_path.lower() or 
                           any(indicator in func for func in data['functions']))
            
            medium_score = sum(1 for indicator in self.commercial_indicators['medium']
                             if indicator in file_path.lower())
            
            low_score = sum(1 for indicator in self.commercial_indicators['low']
                          if indicator in file_path.lower())
            
            # Determine potential
            if high_score >= 2 or (file_path.startswith('api/') and not data['personality_critical']):
                data['commercial_potential'] = 'high'
            elif high_score >= 1 or medium_score >= 2:
                data['commercial_potential'] = 'medium'
            else:
                data['commercial_potential'] = 'low'

    def _generate_consolidation_plan(self) -> Dict[str, Any]:
        """Generate file consolidation recommendations"""
        consolidation = {
            'merge_groups': defaultdict(list),
            'delete_candidates': [],
            'move_operations': []
        }
        
        # Find duplicate functionality
        function_map = defaultdict(list)
        for file_path, data in self.files_data.items():
            for func in data['functions']:
                if not func.startswith('_'):
                    function_map[func].append(file_path)
        
        # Identify merge candidates
        for func, files in function_map.items():
            if len(files) > 1:
                # Group by system
                system_groups = defaultdict(list)
                for f in files:
                    system_groups[self.files_data[f]['system']].append(f)
                
                for system, group in system_groups.items():
                    if len(group) > 1:
                        consolidation['merge_groups'][f"{system}_{func}"] = group
                        
                        # Mark files for merging
                        primary = min(group, key=lambda x: len(x))  # Shortest path as primary
                        for f in group:
                            if f != primary:
                                self.files_data[f]['consolidation_action'] = 'merge'
                                self.files_data[f]['merge_candidates'].append(primary)
        
        # Identify move operations
        for file_path, data in self.files_data.items():
            if data['scatter_status'] == 'scattered' and data['proposed_location']:
                consolidation['move_operations'].append({
                    'from': file_path,
                    'to': data['proposed_location'],
                    'reason': f"Scattered {data['system']} component"
                })
                data['consolidation_action'] = 'move'
        
        # Identify deletion candidates (empty or near-empty files)
        for file_path, data in self.files_data.items():
            if (data['size'] < 100 and 
                len(data['functions']) == 0 and 
                len(data['classes']) == 0 and
                '__init__' not in file_path):
                consolidation['delete_candidates'].append(file_path)
                data['consolidation_action'] = 'delete'
        
        return consolidation

    def _create_report(self, consolidation_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Create final comprehensive report"""
        report = {
            'summary': {
                'total_files': len(self.files_data),
                'scattered_files': sum(1 for d in self.files_data.values() if d['scatter_status'] == 'scattered'),
                'personality_critical_files': len(self.personality_files),
                'high_commercial_potential': sum(1 for d in self.files_data.values() if d['commercial_potential'] == 'high'),
                'proposed_merges': len(consolidation_plan['merge_groups']),
                'proposed_moves': len(consolidation_plan['move_operations']),
                'proposed_deletions': len(consolidation_plan['delete_candidates'])
            },
            'scatter_analysis': dict(self.scatter_analysis),
            'commercial_modules': self._identify_commercial_modules(),
            'personality_preservation': {
                'critical_files': list(self.personality_files),
                'keep_together': self._group_personality_files()
            },
            'consolidation_plan': consolidation_plan,
            'proposed_structure': self._propose_new_structure(),
            'files_metadata': self.files_data
        }
        
        return report

    def _identify_commercial_modules(self) -> Dict[str, Any]:
        """Identify modules suitable for commercialization"""
        modules = defaultdict(lambda: {
            'files': [],
            'exports': [],
            'dependencies': set(),
            'personality_dependent': False
        })
        
        for file_path, data in self.files_data.items():
            if data['commercial_potential'] in ['high', 'medium']:
                system = data['system']
                modules[system]['files'].append(file_path)
                modules[system]['exports'].extend(data['exports'])
                modules[system]['dependencies'].update(data['dependencies'])
                
                if data['personality_critical']:
                    modules[system]['personality_dependent'] = True
        
        # Convert sets to lists for JSON serialization
        for module in modules.values():
            module['dependencies'] = list(module['dependencies'])
            
        return dict(modules)

    def _group_personality_files(self) -> List[List[str]]:
        """Group personality files that must stay together"""
        groups = []
        
        # Dream narrator group
        dream_group = [f for f in self.personality_files if 'dream' in f.lower()]
        if dream_group:
            groups.append(dream_group)
            
        # Voice/haiku group
        voice_group = [f for f in self.personality_files 
                      if any(x in f.lower() for x in ['voice', 'haiku', 'creative'])]
        if voice_group:
            groups.append(voice_group)
            
        # Brain/consciousness group
        brain_group = [f for f in self.personality_files 
                      if any(x in f.lower() for x in ['brain', 'consciousness', 'awareness'])]
        if brain_group:
            groups.append(brain_group)
            
        return groups

    def _propose_new_structure(self) -> Dict[str, List[str]]:
        """Propose new directory structure"""
        structure = {
            'dream/': [
                'core/',
                'engine/',
                'visualization/',
                'oneiric/',
                'sandbox/',
                'commercial_api/'
            ],
            'memory/': [
                'core/',
                'episodic/',
                'semantic/',
                'fold_system/',
                'consolidation/',
                'commercial_api/'
            ],
            'consciousness/': [
                'core/',
                'awareness/',
                'reflection/',
                'quantum_integration/',
                'commercial_api/'
            ],
            'bio/': [
                'core/',
                'symbolic/',
                'mitochondria/',
                'oscillators/',
                'commercial_api/'
            ],
            'quantum/': [
                'core/',
                'processing/',
                'security/',
                'attention/',
                'commercial_api/'
            ],
            'identity/': [
                'core/',
                'auth/',
                'biometric/',
                'glyph_system/',
                'commercial_api/'
            ],
            'commercial_apis/': [
                'dream_commerce/',
                'memory_services/',
                'quantum_processing/',
                'bio_simulation/',
                'identity_verification/'
            ],
            'personality/': [
                'brain/',
                'voice/',
                'creative_core/',
                'emotional_system/',
                'narrative_engine/'
            ]
        }
        
        return structure


def main():
    """Run the professional audit"""
    auditor = ProfessionalAuditor('.')
    report = auditor.audit_system()
    
    # Save report
    with open('LUKHAS_PROFESSIONAL_AUDIT.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    # Save summary
    with open('AUDIT_SUMMARY.md', 'w') as f:
        f.write("# LUKHAS System Professional Audit Summary\n\n")
        f.write("## Overview\n")
        f.write(f"- Total Files: {report['summary']['total_files']}\n")
        f.write(f"- Scattered Files: {report['summary']['scattered_files']}\n")
        f.write(f"- Personality Critical: {report['summary']['personality_critical_files']}\n")
        f.write(f"- High Commercial Potential: {report['summary']['high_commercial_potential']}\n\n")
        
        f.write("## Proposed Changes\n")
        f.write(f"- Files to Merge: {report['summary']['proposed_merges']} groups\n")
        f.write(f"- Files to Move: {report['summary']['proposed_moves']}\n")
        f.write(f"- Files to Delete: {report['summary']['proposed_deletions']}\n\n")
        
        f.write("## Scattered Systems\n")
        for system, files in report['scatter_analysis'].items():
            f.write(f"\n### {system.upper()} ({len(files)} scattered files)\n")
            for file in files[:5]:  # Show first 5
                f.write(f"- {file}\n")
            if len(files) > 5:
                f.write(f"- ... and {len(files) - 5} more\n")
        
        f.write("\n## Commercial Modules\n")
        for module, data in report['commercial_modules'].items():
            if data['files']:
                f.write(f"\n### {module.upper()}\n")
                f.write(f"- Files: {len(data['files'])}\n")
                f.write(f"- Exports: {len(data['exports'])}\n")
                f.write(f"- Personality Dependent: {data['personality_dependent']}\n")
        
        f.write("\n## Proposed New Structure\n")
        f.write("```\n")
        for dir, subdirs in report['proposed_structure'].items():
            f.write(f"{dir}\n")
            for subdir in subdirs:
                f.write(f"  {subdir}\n")
        f.write("```\n")
    
    print("Audit complete! Check LUKHAS_PROFESSIONAL_AUDIT.json and AUDIT_SUMMARY.md")


if __name__ == "__main__":
    main()