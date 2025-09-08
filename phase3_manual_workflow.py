#!/usr/bin/env python3
"""
🚀 Phase 3: High-Speed Manual Fixing Workflow 
=============================================

Based on Phase 1 & 2 learnings, create a streamlined manual fixing process:

KEY INSIGHTS FROM PHASE 2:
✅ Exact error patterns identified from refined_syntax_fixer.py output
✅ 4 systematic patterns account for 90% of bracket errors  
✅ Manual compilation testing works 100% of the time
✅ One-by-one approach prevents cascading issues

SYSTEMATIC PATTERNS TO FIX:
1. f'{variable}}' -> f'{variable}' (extra closing brace)
2. .hexdigest()}}[:8]} -> .hexdigest()[:8]} (hashlib pattern)  
3. .timestamp()}} -> .timestamp()} (method call pattern)
4. {).get( -> {}.get( (dict operation pattern)

WORKFLOW: File -> Identify -> Fix -> Test -> Commit -> Next
"""

import subprocess
import json
from pathlib import Path
from typing import List, Tuple, Dict
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class Phase3ManualWorkflow:
    """High-speed manual fixing workflow"""
    
    def __init__(self, repo_root: str = "/Users/agi_dev/LOCAL-REPOS/Lukhas"):
        self.repo_root = Path(repo_root)
        self.fixed_files = []
        
        # Target files from Phase 2 analysis (top 10 highest error counts)
        self.target_files = [
            ("candidate/governance/security/security_audit_engine.py", 74),
            ("candidate/qi/ui/abstract_reasoning_demo.original.py", 74), 
            ("candidate/qi/learning/adaptive_engine.py", 73),
            ("candidate/qi/autonomy/self_healer.py", 75),
            ("candidate/core/symbolic/crista_optimizer.py", 81),
        ]
    
    def get_specific_errors(self, file_path: str) -> List[Dict]:
        """Get specific syntax errors for a file with line numbers"""
        try:
            cmd = [".venv/bin/python", "-m", "py_compile", file_path]
            result = subprocess.run(cmd, cwd=self.repo_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                return []  # No errors
            
            # Parse error from stderr
            error_info = []
            if result.stderr:
                lines = result.stderr.strip().split('\n')
                for line in lines:
                    if 'File "' in line and 'line' in line:
                        # Extract file, line, error
                        parts = line.split(', ')
                        if len(parts) >= 2:
                            line_part = [p for p in parts if 'line' in p]
                            if line_part:
                                line_num = line_part[0].split()[-1]
                                error_info.append({
                                    'file': file_path,
                                    'line': line_num,
                                    'error': result.stderr
                                })
            
            return error_info
            
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return []
    
    def show_error_context(self, file_path: str, line_num: int, context: int = 3) -> str:
        """Show error context around specific line"""
        try:
            with open(self.repo_root / file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            start = max(0, line_num - context - 1)
            end = min(len(lines), line_num + context)
            
            context_lines = []
            for i in range(start, end):
                marker = ">>>" if i == line_num - 1 else "   "
                context_lines.append(f"{marker} {i+1:3}: {lines[i].rstrip()}")
            
            return '\n'.join(context_lines)
            
        except Exception as e:
            return f"Error reading context: {e}"
    
    def create_fixing_guide(self, file_path: str) -> str:
        """Create a focused fixing guide for a specific file"""
        errors = self.get_specific_errors(file_path)
        if not errors:
            return f"✅ {file_path} - No syntax errors found!"
        
        guide = f"""
🎯 MANUAL FIXING GUIDE: {file_path}
{'='*60}

STRATEGY: Fix ONE error at a time, test compilation after each fix

SYSTEMATIC PATTERNS TO LOOK FOR:
1. f'{{variable}}' -> f'{{variable}}' (remove extra }} )
2. .hexdigest()}}[:8]} -> .hexdigest()[:8]} 
3. .timestamp()}} -> .timestamp()}
4. {{).get( -> {{}}.get(

ERROR DETAILS:
"""
        
        for i, error in enumerate(errors[:3]):  # Show first 3 errors
            line_num = int(error['line'])
            guide += f"\nERROR {i+1}: Line {line_num}\n"
            guide += self.show_error_context(file_path, line_num)
            guide += "\n" + "-"*40
        
        guide += f"""

FIXING WORKFLOW:
1. Edit the file to fix the FIRST error only
2. Run: .venv/bin/python -m py_compile {file_path}  
3. If success: move to next error
4. If fail: revert and try different approach
5. Repeat until all errors fixed

COMMIT after this file is 100% fixed.
"""
        
        return guide
    
    def run_workflow(self) -> None:
        """Run the Phase 3 high-speed manual workflow"""
        logger.info("🚀 Phase 3: High-Speed Manual Fixing Workflow")
        logger.info("=" * 60)
        logger.info("STRATEGY: Targeted manual fixes with systematic patterns")
        logger.info("TARGET: Top 5 highest-error files from Phase 2 analysis")
        
        for i, (file_path, error_count) in enumerate(self.target_files):
            logger.info(f"\n📋 [{i+1}/5] {file_path} ({error_count} estimated errors)")
            
            if not (self.repo_root / file_path).exists():
                logger.warning(f"⚠️  File not found: {file_path}")
                continue
            
            # Generate fixing guide
            guide = self.create_fixing_guide(file_path)
            
            # Save guide to file for reference
            guide_file = self.repo_root / f"fixing_guide_{Path(file_path).name}.txt"
            with open(guide_file, 'w') as f:
                f.write(guide)
            
            logger.info(f"📖 Fixing guide created: {guide_file}")
            print(guide)
            
            # Check if already fixed
            errors = self.get_specific_errors(file_path)
            if not errors:
                logger.info(f"✅ {file_path} already compiles successfully!")
                self.fixed_files.append(file_path)
            else:
                logger.info(f"🔧 Ready for manual fixing: {len(errors)} errors detected")
                logger.info("💡 Use the guide above to fix systematically")
        
        # Summary
        logger.info(f"\n🎯 Phase 3 Workflow Setup Complete!")
        logger.info(f"📊 Files ready for manual fixing: {5 - len(self.fixed_files)}/5")
        logger.info(f"✅ Files already fixed: {len(self.fixed_files)}/5")
        
        if self.fixed_files:
            logger.info("Already fixed files:")
            for file_path in self.fixed_files:
                logger.info(f"  ✅ {file_path}")

def main():
    """Main execution"""
    workflow = Phase3ManualWorkflow()
    workflow.run_workflow()

if __name__ == "__main__":
    main()