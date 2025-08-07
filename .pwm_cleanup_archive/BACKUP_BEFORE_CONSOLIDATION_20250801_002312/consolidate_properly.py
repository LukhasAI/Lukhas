#!/usr/bin/env python3
"""
Proper consolidation script that actually moves files and creates a lean structure
This will consolidate directories with 1-2 files into logical parent directories
"""

import os
import shutil
import re
from pathlib import Path
from typing import Dict, List, Tuple
import ast

class ProperConsolidator:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.moves = []
        self.import_updates = {}
        self.files_to_update = set()
        
    def analyze_directory_structure(self) -> Dict[str, List[Path]]:
        """Analyze and identify directories that need consolidation"""
        consolidation_targets = {}
        
        # Define consolidation rules
        rules = {
            # Bio module - consolidate ALL bio files to bio/core/
            'bio/core/': [
                'bio/processing/*.py',
                'bio/integration/*.py',
                'bio/orchestration/*.py',
                'bio/endocrine/*.py',
                'bio/symbolic/core/*.py',
                'bio/symbolic/*.py',
                'bio/systems/*.py',
                'bio/systems/orchestration/*.py',
                'bio/systems/orchestration/adapters/*.py',
                'bio/mitochondria/*.py',
                'bio/oscillators/*.py'
            ],
            
            # Core module - consolidate utilities to core/utils/
            'core/utils/': [
                'core/tracing/*.py',
                'core/common/*.py',
                'core/user_interaction/*.py',
                'core/grow/*.py',
                'core/think/*.py',
                'core/bio_orchestrator/*.py',
                'core/orchestration/*.py',
                'core/sustainability/*.py',
                'core/visuals/*.py'
            ],
            
            # Core AGI - consolidate AI features
            'core/agi/': [
                'core/adaptive_ai/*.py',
                'core/adaptive_ai/Meta_Learning/*.py'
            ],
            
            # Core identity - consolidate identity features
            'core/identity/': [
                'core/identity/vault/*.py'
            ],
            
            # LUKHAS personality - flatten structure
            'personality/': [
                'personality/emotional_system/*.py',
                'personality/narrative_engine/*.py',
                'personality/creative_core/*.py',
                'personality/brain/*.py'
            ],
            
            # Quantum consolidation
            'quantum/core/': [
                'quantum/attention/*.py',
                'quantum/economics/*.py',
                'quantum/superposition/*.py',
                'quantum/memory/*.py',
                'quantum/architecture/*.py'
            ],
            
            # Features consolidation
            'features/core/': [
                'features/common/*.py',
                'features/analytics/*.py',
                'features/analytics/archetype/*.py'
            ]
        }
        
        for target, patterns in rules.items():
            consolidation_targets[target] = []
            for pattern in patterns:
                base_dir = Path(pattern).parent
                if base_dir.exists():
                    files = list(base_dir.glob(Path(pattern).name))
                    # Exclude __init__.py files from the count
                    non_init_files = [f for f in files if f.name != '__init__.py']
                    if non_init_files:
                        consolidation_targets[target].extend(non_init_files)
                        
        return consolidation_targets
        
    def plan_moves(self, consolidation_targets: Dict[str, List[Path]]) -> List[Tuple[Path, Path]]:
        """Plan all file moves"""
        moves = []
        
        for target_dir, files in consolidation_targets.items():
            target_path = Path(target_dir)
            
            for file in files:
                if file.exists() and file.is_file():
                    # Determine new filename to avoid conflicts
                    new_name = file.name
                    
                    # If file comes from a meaningful subdirectory, prefix it
                    parent_name = file.parent.name
                    if parent_name not in ['core', 'bio', 'quantum', 'features']:
                        # Don't prefix with generic names
                        if parent_name not in ['processing', 'integration', 'common', 'utils']:
                            if not new_name.startswith(parent_name):
                                new_name = f"{parent_name}_{new_name}"
                    
                    new_path = target_path / new_name
                    
                    # Handle conflicts
                    if new_path.exists() and new_path != file:
                        base = new_path.stem
                        ext = new_path.suffix
                        counter = 1
                        while new_path.exists():
                            new_path = target_path / f"{base}_{counter}{ext}"
                            counter += 1
                    
                    if new_path != file:  # Only move if actually changing location
                        moves.append((file, new_path))
                        
                        # Record import mapping
                        old_import = self._path_to_import(file)
                        new_import = self._path_to_import(new_path)
                        self.import_updates[old_import] = new_import
                        
        return moves
        
    def _path_to_import(self, path: Path) -> str:
        """Convert file path to import path"""
        parts = path.parts
        # Remove .py extension
        if path.suffix == '.py':
            path = path.with_suffix('')
        
        # Convert to dot notation
        import_path = '.'.join(path.parts)
        
        # Remove leading ./ if present
        import_path = import_path.replace('./', '')
        
        return import_path
        
    def find_files_with_imports(self) -> List[Path]:
        """Find all Python files that might need import updates"""
        python_files = []
        
        for root, dirs, files in os.walk('.'):
            # Skip archive and hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and 'ARCHIVE' not in d]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
                    
        return python_files
        
    def update_imports_in_file(self, file_path: Path) -> bool:
        """Update imports in a single file"""
        try:
            content = file_path.read_text()
            original_content = content
            
            # Update imports using regex
            for old_import, new_import in self.import_updates.items():
                # Handle various import styles
                patterns = [
                    (f'from {old_import} import', f'from {new_import} import'),
                    (f'import {old_import}', f'import {new_import}'),
                    (f'from {old_import}', f'from {new_import}'),
                ]
                
                for old_pattern, new_pattern in patterns:
                    content = re.sub(
                        re.escape(old_pattern),
                        new_pattern,
                        content
                    )
            
            if content != original_content:
                if not self.dry_run:
                    file_path.write_text(content)
                return True
                
        except Exception as e:
            print(f"Error updating {file_path}: {e}")
            
        return False
        
    def execute_moves(self, moves: List[Tuple[Path, Path]]) -> Dict[str, int]:
        """Execute the planned moves"""
        stats = {
            'moved': 0,
            'errors': 0,
            'directories_removed': 0
        }
        
        for src, dst in moves:
            try:
                if not self.dry_run:
                    # Create target directory
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Move file
                    shutil.move(str(src), str(dst))
                    
                print(f"{'Would move' if self.dry_run else 'Moved'}: {src} -> {dst}")
                stats['moved'] += 1
                
            except Exception as e:
                print(f"Error moving {src}: {e}")
                stats['errors'] += 1
                
        return stats
        
    def cleanup_empty_directories(self) -> int:
        """Remove empty directories after consolidation"""
        removed = 0
        
        # Directories to check for removal
        check_dirs = [
            'bio/processing', 'bio/integration', 'bio/orchestration',
            'bio/endocrine', 'bio/symbolic', 'bio/mitochondria',
            'bio/systems/orchestration', 'bio/systems',
            'bio/oscillators',
            'core/tracing', 'core/common', 'core/user_interaction',
            'core/grow', 'core/think', 'core/bio_orchestrator',
            'core/adaptive_ai', 'core/orchestration', 'core/sustainability',
            'core/visuals', 'core/identity/vault',
            'personality/emotional_system', 'personality/narrative_engine',
            'personality/creative_core', 'personality/brain',
            'quantum/attention', 'quantum/economics', 'quantum/superposition',
            'features/analytics/archetype', 'features/analytics', 'features/common'
        ]
        
        for dir_path in check_dirs:
            path = Path(dir_path)
            if path.exists() and path.is_dir():
                # Check if directory is empty or only has __init__.py
                files = list(path.iterdir())
                py_files = [f for f in files if f.suffix == '.py' and f.name != '__init__.py']
                
                if not py_files:  # No Python files except maybe __init__.py
                    if not self.dry_run:
                        shutil.rmtree(path)
                    print(f"{'Would remove' if self.dry_run else 'Removed'} empty directory: {path}")
                    removed += 1
                    
        return removed
        
    def generate_import_mapping_report(self) -> str:
        """Generate a report of all import changes"""
        report = "# Import Mapping Report\n\n"
        report += "The following imports need to be updated:\n\n"
        
        for old, new in sorted(self.import_updates.items()):
            report += f"- `{old}` -> `{new}`\n"
            
        return report
        
    def run(self):
        """Run the consolidation process"""
        print("🔍 Analyzing directory structure...")
        consolidation_targets = self.analyze_directory_structure()
        
        # Report what we found
        total_files = sum(len(files) for files in consolidation_targets.values())
        print(f"\nFound {total_files} files to consolidate")
        
        print("\n📋 Planning moves...")
        moves = self.plan_moves(consolidation_targets)
        self.moves = moves
        
        if not moves:
            print("No files need to be moved!")
            return
            
        print(f"\nPlanned {len(moves)} file moves")
        
        if self.dry_run:
            print("\n--- DRY RUN MODE ---")
            print("No files will actually be moved\n")
            
        # Show planned moves
        print("\n📦 Consolidation Plan:")
        for target_dir in consolidation_targets:
            moves_to_target = [(s, d) for s, d in moves if str(d).startswith(target_dir)]
            if moves_to_target:
                print(f"\n{target_dir}")
                for src, dst in moves_to_target[:5]:  # Show first 5
                    print(f"  ← {src}")
                if len(moves_to_target) > 5:
                    print(f"  ... and {len(moves_to_target) - 5} more files")
                    
        # Execute moves
        print("\n🚀 Executing moves...")
        stats = self.execute_moves(moves)
        
        # Update imports
        print("\n🔧 Updating imports...")
        python_files = self.find_files_with_imports()
        updated_files = 0
        
        for file in python_files:
            if self.update_imports_in_file(file):
                updated_files += 1
                
        print(f"{'Would update' if self.dry_run else 'Updated'} imports in {updated_files} files")
        
        # Cleanup empty directories
        print("\n🧹 Cleaning up empty directories...")
        removed_dirs = self.cleanup_empty_directories()
        
        # Generate report
        print("\n📄 Generating import mapping report...")
        report = self.generate_import_mapping_report()
        report_path = Path('CONSOLIDATION_IMPORT_MAP.md')
        
        if not self.dry_run:
            report_path.write_text(report)
            
        # Summary
        print("\n✅ Consolidation Summary:")
        print(f"  - Files moved: {stats['moved']}")
        print(f"  - Import updates: {updated_files}")
        print(f"  - Directories removed: {removed_dirs}")
        print(f"  - Errors: {stats['errors']}")
        
        if self.dry_run:
            print("\n⚠️  This was a DRY RUN. No changes were made.")
            print("Run with --execute to actually perform the consolidation")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Properly consolidate LUKHAS directory structure")
    parser.add_argument('--execute', action='store_true', help='Actually perform the consolidation (default is dry run)')
    args = parser.parse_args()
    
    consolidator = ProperConsolidator(dry_run=not args.execute)
    consolidator.run()


if __name__ == "__main__":
    main()