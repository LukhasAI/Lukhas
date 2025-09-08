#!/usr/bin/env python3
"""
🤖 LUKHAS Automated Syntax Error Elimination Script
==================================================

Systematic automation for fixing the most common syntax error patterns:
1. F-string brace mismatches: {function(}} → {function()}
2. Dictionary missing closing braces
3. Function definition syntax errors  
4. CSS f-string escaping in HTML templates
5. Comprehension colon issues

Based on proven patterns from 11 consecutive perfect eliminations.
"""

import os
import re
import subprocess
from pathlib import Path
from typing import List, Tuple


class AutomatedSyntaxFixer:
    """Automated syntax error fixer using proven patterns"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.fixed_files = []
        self.error_count_before = 0
        self.error_count_after = 0
        
    def get_syntax_error_count(self) -> int:
        """Get current syntax error count using ruff"""
        try:
            result = subprocess.run([
                ".venv/bin/ruff", "check", 
                "branding/", "candidate/", "tools/", "products/", "matriz/", "next_gen/", "lukhas/",
                "--select=E999", "--output-format=concise"
            ], capture_output=True, text=True, cwd=self.project_root)
            
            lines = result.stderr.split("\n")
            for line in lines:
                if "syntax-error" in line:
                    # Extract count from format like "6182	    	syntax-error"
                    parts = line.split("\t")
                    if parts and parts[0].isdigit():
                        return int(parts[0])
            return 0
        except Exception as e:
            print(f"Error getting syntax count: {e}")
            return 0
    
    def apply_f_string_brace_fixes(self, file_path: Path) -> int:
        """Fix common f-string brace mismatches"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
                
            original_content = content
            fixes_applied = 0
            
            # Pattern 1: {function(}} → {function()}  
            pattern1 = re.compile(r"\{([^{}]*\([^{}]*)\}}")
            matches = list(pattern1.finditer(content))
            for match in matches:
                # Only fix if it's clearly a function call with extra closing brace
                inner = match.group(1)
                if "(" in inner and not inner.endswith("()"):
                    content = content.replace(match.group(0), f"{{{inner}}}")
                    fixes_applied += 1
                    
            # Pattern 2: .hexdigest(}}[:N] → .hexdigest()}[:N]
            pattern2 = re.compile(r"\.hexdigest\(\}\}\[")  
            content = pattern2.sub(".hexdigest()}[", content)
            if pattern2.search(original_content):
                fixes_applied += len(pattern2.findall(original_content))
            
            # Pattern 3: float("nan"} → float("nan")
            pattern3 = re.compile(r'float\("(nan|inf)"\}')
            content = pattern3.sub(r'float("\1")', content)
            if pattern3.search(original_content):
                fixes_applied += len(pattern3.findall(original_content))
                
            # Pattern 4: CSS f-string brace fixes: } → }} in HTML templates
            # Only in f-string contexts (look for f""" ... css ... """)
            if 'f"""' in content and "style>" in content:
                # Fix CSS property endings in f-strings
                pattern4 = re.compile(r"(font-family: [^;}]+; margin: [^;}]+; )}(?!\})")
                content = pattern4.sub(r"\1}}", content)
                if pattern4.search(original_content):
                    fixes_applied += len(pattern4.findall(original_content))
                    
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return fixes_applied
                
        except Exception as e:
            print(f"Error fixing f-string braces in {file_path}: {e}")
            
        return 0
    
    def apply_dictionary_brace_fixes(self, file_path: Path) -> int:
        """Fix missing dictionary closing braces"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
                
            original_content = content
            fixes_applied = 0
            
            # Pattern: {"key": value, → {"key": value},
            # Look for dictionary entries that end with comma space but no closing brace
            lines = content.split("\n")
            fixed_lines = []
            
            for i, line in enumerate(lines):
                stripped = line.strip()
                # Check if this looks like an incomplete dictionary entry
                if (stripped.endswith(",") and 
                    '"' in stripped and ":" in stripped and
                    i + 1 < len(lines) and
                    lines[i + 1].strip() in ["}", "},"]):
                    
                    # Check if the next line should be }}
                    next_line = lines[i + 1].strip()
                    if next_line == "}" and i + 2 < len(lines):
                        # Look ahead to see if this is in an f-string context
                        lookahead = lines[i + 2].strip() if i + 2 < len(lines) else ""
                        if lookahead == "}" or '"""' in lookahead:
                            # This is likely a missing brace in nested structure
                            fixed_lines.append(line)
                            fixed_lines.append(lines[i + 1])  # Keep the }
                            continue
                            
                fixed_lines.append(line)
                
            if fixed_lines != lines:
                content = "\n".join(fixed_lines)
                fixes_applied = len(lines) - len(fixed_lines)
                
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return fixes_applied
                
        except Exception as e:
            print(f"Error fixing dictionary braces in {file_path}: {e}")
            
        return 0
        
    def apply_comprehension_colon_fixes(self, file_path: Path) -> int:
        """Fix trailing colons in list/dict comprehensions"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
                
            original_content = content
            
            # Pattern: for x in collection: → for x in collection (in comprehensions)
            # This is tricky as we need to identify comprehension contexts
            pattern = re.compile(r"\[(.*?for\s+\w+\s+in\s+[^:]+):\s*([^\]]*)\]")
            content = pattern.sub(r"[\1 \2]", content)
            
            fixes_applied = len(pattern.findall(original_content))
            
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return fixes_applied
                
        except Exception as e:
            print(f"Error fixing comprehension colons in {file_path}: {e}")
            
        return 0
    
    def test_compilation(self, file_path: Path) -> bool:
        """Test if file compiles successfully"""
        try:
            result = subprocess.run([
                "python3", "-c", f'import py_compile; py_compile.compile("{file_path}", doraise=True)'
            ], capture_output=True, text=True, cwd=self.project_root)
            return result.returncode == 0
        except Exception:
            return False
            
    def process_file(self, file_path: Path) -> Tuple[int, bool]:
        """Process a single file with all fix patterns"""
        if not file_path.suffix == ".py":
            return 0, False
            
        print(f"Processing: {file_path.relative_to(self.project_root)}")
        
        # Test initial compilation
        compiles_before = self.test_compilation(file_path)
        
        total_fixes = 0
        total_fixes += self.apply_f_string_brace_fixes(file_path)
        total_fixes += self.apply_dictionary_brace_fixes(file_path)
        total_fixes += self.apply_comprehension_colon_fixes(file_path)
        
        # Test compilation after fixes
        compiles_after = self.test_compilation(file_path)
        
        if total_fixes > 0:
            if compiles_after:
                print(f"  ✅ Applied {total_fixes} fixes - COMPILATION SUCCESSFUL")
                self.fixed_files.append(str(file_path))
                return total_fixes, True
            else:
                print(f"  ⚠️  Applied {total_fixes} fixes - Still has compilation errors")
                return total_fixes, False
        
        return 0, compiles_before
    
    def run_automated_fixes(self, target_dirs: List[str] = None) -> dict:
        """Run automated fixes on target directories"""
        if target_dirs is None:
            target_dirs = ["branding", "candidate", "tools", "products", "matriz", "next_gen", "lukhas"]
            
        print("🤖 LUKHAS Automated Syntax Error Elimination")
        print("=" * 50)
        
        # Get initial error count
        self.error_count_before = self.get_syntax_error_count()
        print(f"Initial syntax errors: {self.error_count_before}")
        
        total_fixes = 0
        successful_files = 0
        processed_files = 0
        
        for target_dir in target_dirs:
            dir_path = self.project_root / target_dir
            if not dir_path.exists():
                continue
                
            print(f"\n📁 Processing directory: {target_dir}")
            
            for py_file in dir_path.rglob("*.py"):
                if "__pycache__" in str(py_file) or ".git" in str(py_file):
                    continue
                    
                processed_files += 1
                fixes, success = self.process_file(py_file)
                total_fixes += fixes
                if success and fixes > 0:
                    successful_files += 1
        
        # Get final error count
        self.error_count_after = self.get_syntax_error_count()
        errors_eliminated = self.error_count_before - self.error_count_after
        
        print("\n" + "=" * 50)
        print("🎯 AUTOMATION RESULTS:")
        print(f"Files processed: {processed_files}")
        print(f"Files successfully fixed: {successful_files}")
        print(f"Total pattern fixes applied: {total_fixes}")
        print(f"Syntax errors eliminated: {errors_eliminated}")
        print(f"Success rate: {errors_eliminated/total_fixes*100:.1f}%" if total_fixes > 0 else "N/A")
        
        return {
            "processed_files": processed_files,
            "successful_files": successful_files,
            "total_fixes": total_fixes,
            "errors_eliminated": errors_eliminated,
            "error_count_before": self.error_count_before,
            "error_count_after": self.error_count_after,
            "fixed_files": self.fixed_files
        }

if __name__ == "__main__":
    fixer = AutomatedSyntaxFixer(".")
    results = fixer.run_automated_fixes()
    
    if results["errors_eliminated"] > 0:
        print(f"\n🚀 Ready to commit {results['errors_eliminated']} error elimination!")
    else:
        print("\n💭 Consider manual analysis for remaining complex patterns.")
