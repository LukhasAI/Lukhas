#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conflict Healer - Automatically resolves Git merge conflicts
Part of the LUKHAS Emergency Surgery Suite
"""

import os
import re
import shutil
from datetime import datetime
from typing import List, Tuple, Optional

class ConflictHealer:
    """Heals Git merge conflicts in Python file"""
    
    def __init__(self, backup_dir='healing/backups'):
        self.backup_dir = backup_dir
        self.conflicts_healed = 0
        self.files_processed = []
        os.makedirs(backup_dir, exist_ok=True)
        
    def find_conflict_files(self) -> List[str]:
        """Find all files with merge conflict"""
        conflict_files = []
        
        for root, dirs, files in os.walk('.'):
            # Skip venv and git directories
            if '.venv' in root or '.git' in root or '.pwm_cleanup_archive' in root:
                continue
                
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        if '<<<<<<< HEAD' in content:
                            conflict_files.append(file_path)
                    except:
                        pass
        
        return conflict_files
    
    def backup_file(self, file_path: str):
        """Create backup of file before healing"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = os.path.basename(file_path).replace('.py', f'_{timestamp}.py')
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def heal_conflict(self, file_path: str, strategy: str = 'smart') -> bool:
        """
        Heal merge conflicts in a file
        
        Strategies:
        - 'smart': Keep the most complete/functional version
        - 'ours': Keep HEAD version
        - 'theirs': Keep incoming version
        - 'merge': Try to merge both versions intelligently
        """
        
        print(f"<� Healing {file_path}...")
        
        # Backup first
        backup_path = self.backup_file(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all conflicts
            conflict_pattern = r'<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> [^\n]+'
            conflicts = list(re.finditer(conflict_pattern, content, re.DOTALL))
            
            if not conflicts:
                return False
            
            # Process each conflict
            healed_content = content
            offset = 0
            
            for match in conflicts:
                ours = match.group(1)
                theirs = match.group(2)
                
                # Choose resolution based on strategy
                if strategy == 'smart':
                    resolution = self.smart_merge(ours, theirs)
                elif strategy == 'ours':
                    resolution = ours
                elif strategy == 'theirs':
                    resolution = theirs
                else:  # merge
                    resolution = self.merge_versions(ours, theirs)
                
                # Replace conflict with resolution
                start = match.start() + offset
                end = match.end() + offset
                healed_content = healed_content[:start] + resolution + healed_content[end:]
                
                # Adjust offset for next conflict
                offset += len(resolution) - (end - start)
            
            # Write healed content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(healed_content)
            
            self.conflicts_healed += len(conflicts)
            self.files_processed.append(file_path)
            
            print(f"   Healed {len(conflicts)} conflicts")
            return True
            
        except Exception as e:
            print(f"  L Failed to heal: {str(e)}")
            # Restore from backup
            shutil.copy2(backup_path, file_path)
            return False
    
    def smart_merge(self, ours: str, theirs: str) -> str:
        """Intelligently choose between version"""
        
        # Check for LUKHAS-specific patterns
        ours_has_lukhas = 'lukhas' in ours.lower() or 'LUKHAS' in ours
        theirs_has_lukhas = 'lukhas' in theirs.lower() or 'LUKHAS' in theirs
        
        # Prefer LUKHAS version
        if ours_has_lukhas and not theirs_has_lukhas:
            return ours
        elif theirs_has_lukhas and not ours_has_lukhas:
            return theirs
        
        # Check for more complete code
        ours_lines = len(ours.strip().split('\n'))
        theirs_lines = len(theirs.strip().split('\n'))
        
        # Prefer longer version (usually more complete)
        if ours_lines > theirs_lines * 1.5:
            return ours
        elif theirs_lines > ours_lines * 1.5:
            return theirs
        
        # Check for syntax completeness
        ours_complete = self.check_syntax_completeness(ours)
        theirs_complete = self.check_syntax_completeness(theirs)
        
        if ours_complete and not theirs_complete:
            return ours
        elif theirs_complete and not ours_complete:
            return theirs
        
        # Default to theirs (incoming changes)
        return theirs
    
    def check_syntax_completeness(self, code: str) -> bool:
        """Check if code snippet has balanced brackets/paren"""
        
        brackets = {'(': ')', '[': ']', '{': '}'}
        stack = []
        
        for char in code:
            if char in brackets:
                stack.append(brackets[char])
            elif char in brackets.values():
                if not stack or stack.pop() != char:
                    return False
        
        return len(stack) == 0
    
    def merge_versions(self, ours: str, theirs: str) -> str:
        """Try to merge both version"""
        
        # Simple merge: concatenate with a comment
        merged = f"""# MERGED: Combined both versions
# === Original HEAD version ===
{ours}
# === Incoming version ===
{theirs}
# === End merge ==="""
        
        return merged
    
    def heal_all(self, strategy: str = 'smart') -> dict:
        """Heal all conflicts in the codebase"""
        
        print("<� Starting Conflict Healing Process...")
        
        # Find all conflict files
        conflict_files = self.find_conflict_files()
        
        if not conflict_files:
            print(" No conflicts found! System is healthy.")
            return {
                'status': 'healthy',
                'files_processed': 0,
                'conflicts_healed': 0
            }
        
        print(f"Found {len(conflict_files)} files with conflicts")
        
        # Heal each file
        success_count = 0
        for file_path in conflict_files:
            if self.heal_conflict(file_path, strategy):
                success_count += 1
        
        # Generate report
        report = {
            'status': 'healed' if success_count == len(conflict_files) else 'partial',
            'files_processed': success_count,
            'files_failed': len(conflict_files) - success_count,
            'conflicts_healed': self.conflicts_healed,
            'backup_location': self.backup_dir
        }
        
        print(f"\n Healing Complete!")
        print(f"  - Files healed: {success_count}/{len(conflict_files)}")
        print(f"  - Conflicts resolved: {self.conflicts_healed}")
        print(f"  - Backups saved to: {self.backup_dir}")
        
        return report


def main():
    """Run the conflict healer"""
    
    print("""
TPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW
Q          LUKHAS CONFLICT HEALER                  Q
Q     "Healing the wounds of merge conflicts"      Q
ZPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP]
    """)
    
    healer = ConflictHealer()
    
    # Check for conflicts first
    conflicts = healer.find_conflict_files()
    
    if not conflicts:
        print(" No conflicts found! Your code is healthy.")
        return
    
    print(f"\n=
 Found {len(conflicts)} files with conflicts:")
    for i, file in enumerate(conflicts[:10], 1):
        print(f"  {i}. {file}")
    
    if len(conflicts) > 10:
        print(f"  ... and {len(conflicts) - 10} more")
    
    # Ask for confirmation
    print("\n�  This will modify your files! Backups will be created.")
    response = input("Proceed with healing? (y/n): ")
    
    if response.lower() == 'y':
        # Run healing
        report = healer.heal_all(strategy='smart')
        
        # Save report
        import json
        report_path = f"healing/healing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n=� Healing report saved to: {report_path}")
    else:
        print("Healing cancelled.")


if __name__ == "__main__":
    main()