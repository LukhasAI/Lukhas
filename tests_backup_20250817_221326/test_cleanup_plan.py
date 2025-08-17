#!/usr/bin/env python3
"""
LUKHAS Test Cleanup and Organization Plan
Created: 2025-08-17
Purpose: Analyze and reorganize test suite
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
import ast

class TestAnalyzer:
    """Analyze test coverage and identify gaps"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_dir = self.project_root / "tests"
        self.obsolete_patterns = [
            r"STUB",
            r"obsolete",
            r"deprecated", 
            r"backup",
            r"old_",
            r"_old",
            r"temp_",
            r"_temp"
        ]
        
        # Core modules that need testing
        self.core_modules = [
            "core",
            "consciousness", 
            "memory",
            "governance",
            "identity",
            "bridge",
            "emotion",
            "qi",
            "api"
        ]
        
    def find_obsolete_tests(self) -> List[Path]:
        """Find tests that should be removed"""
        obsolete = []
        
        for test_file in self.test_dir.rglob("*.py"):
            # Check filename patterns
            for pattern in self.obsolete_patterns:
                if re.search(pattern, test_file.name, re.IGNORECASE):
                    obsolete.append(test_file)
                    break
                    
            # Check for empty test files
            if test_file.stat().st_size < 100:  # Less than 100 bytes
                obsolete.append(test_file)
                
        return list(set(obsolete))
    
    def find_functions_without_tests(self) -> Dict[str, List[str]]:
        """Find functions that don't have tests"""
        untested = {}
        
        for module in self.core_modules:
            module_path = self.project_root / module
            if not module_path.exists():
                continue
                
            untested[module] = []
            
            # Find all Python files in module
            for py_file in module_path.rglob("*.py"):
                if "__pycache__" in str(py_file):
                    continue
                    
                # Parse file to find functions
                try:
                    with open(py_file) as f:
                        tree = ast.parse(f.read())
                        
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            func_name = node.name
                            # Skip private functions and __init__
                            if not func_name.startswith("_"):
                                # Check if test exists
                                test_name = f"test_{func_name}"
                                if not self._test_exists(module, test_name):
                                    untested[module].append(f"{py_file.name}::{func_name}")
                                    
                except Exception:
                    pass  # Skip files that can't be parsed
                    
        return {k: v for k, v in untested.items() if v}
    
    def _test_exists(self, module: str, test_name: str) -> bool:
        """Check if a test exists for a function"""
        test_patterns = [
            self.test_dir / module / f"*{test_name}*.py",
            self.test_dir / f"test_{module}*.py",
            self.test_dir / "unit" / f"*{test_name}*.py",
            self.test_dir / "integration" / f"*{test_name}*.py"
        ]
        
        for pattern in test_patterns:
            if list(Path(pattern.parent).glob(pattern.name)):
                return True
        return False
    
    def create_test_structure(self) -> Dict[str, Dict]:
        """Create logical test suite structure"""
        structure = {
            "unit": {
                "description": "Fast, isolated unit tests",
                "modules": {}
            },
            "integration": {
                "description": "Module interaction tests",
                "modules": {}
            },
            "e2e": {
                "description": "End-to-end system tests",
                "modules": {}
            },
            "performance": {
                "description": "Performance and load tests",
                "modules": {}
            },
            "security": {
                "description": "Security and vulnerability tests",
                "modules": {}
            }
        }
        
        # Organize tests by module and type
        for module in self.core_modules:
            structure["unit"]["modules"][module] = []
            structure["integration"]["modules"][module] = []
            
        return structure
    
    def generate_cleanup_script(self) -> str:
        """Generate script to clean up tests"""
        obsolete = self.find_obsolete_tests()
        
        script = """#!/bin/bash
# LUKHAS Test Cleanup Script
# Generated: 2025-08-17

set -e

echo "🧹 Cleaning up obsolete tests..."
echo "================================"

# Archive directory for obsolete tests
ARCHIVE_DIR="$HOME/LOCAL-REPOS/lukhas-archive/2025-08-17-obsolete-tests"
mkdir -p "$ARCHIVE_DIR"

"""
        
        for test_file in obsolete:
            rel_path = test_file.relative_to(self.project_root)
            script += f"""
# Archive {rel_path}
echo "  Archiving: {rel_path}"
mv "{test_file}" "$ARCHIVE_DIR/"
"""
        
        script += """
echo ""
echo "✅ Cleanup complete!"
echo f"  Archived {len(obsolete)} obsolete test files"
echo "  Location: $ARCHIVE_DIR"
"""
        
        return script
    
    def generate_report(self) -> str:
        """Generate comprehensive test analysis report"""
        obsolete = self.find_obsolete_tests()
        untested = self.find_functions_without_tests()
        
        report = f"""# LUKHAS Test Analysis Report
Generated: 2025-08-17

## Summary
- Obsolete tests found: {len(obsolete)}
- Modules with untested functions: {len(untested)}
- Total untested functions: {sum(len(v) for v in untested.values())}

## Obsolete Tests to Remove
"""
        
        for test_file in obsolete[:20]:  # Show first 20
            report += f"- {test_file.relative_to(self.project_root)}\n"
            
        if len(obsolete) > 20:
            report += f"... and {len(obsolete) - 20} more\n"
            
        report += "\n## Functions Without Tests\n"
        
        for module, functions in untested.items():
            report += f"\n### {module} ({len(functions)} untested)\n"
            for func in functions[:10]:  # Show first 10
                report += f"- {func}\n"
            if len(functions) > 10:
                report += f"... and {len(functions) - 10} more\n"
                
        report += """
## Recommended Test Structure

```
tests/
├── unit/               # Fast, isolated tests
│   ├── test_core/
│   ├── test_consciousness/
│   ├── test_memory/
│   └── test_governance/
├── integration/        # Module interaction tests
│   ├── test_api_flow/
│   ├── test_data_flow/
│   └── test_auth_flow/
├── e2e/               # End-to-end scenarios
│   ├── test_user_journey/
│   └── test_system_flow/
├── performance/       # Load and stress tests
│   └── test_benchmarks/
└── security/          # Security tests
    └── test_vulnerabilities/
```

## Next Steps
1. Run cleanup script to remove obsolete tests
2. Generate test templates for untested functions
3. Organize tests into logical structure
4. Create interactive test dashboard
"""
        
        return report
    

def main():
    """Run test analysis"""
    analyzer = TestAnalyzer()
    
    # Generate report
    report = analyzer.generate_report()
    report_path = Path("tests/test_analysis_report.md")
    with open(report_path, "w") as f:
        f.write(report)
    print(f"📊 Report generated: {report_path}")
    
    # Generate cleanup script
    script = analyzer.generate_cleanup_script()
    script_path = Path("scripts/cleanup_obsolete_tests.sh")
    with open(script_path, "w") as f:
        f.write(script)
    os.chmod(script_path, 0o755)
    print(f"🧹 Cleanup script generated: {script_path}")
    
    # Generate test structure
    structure = analyzer.create_test_structure()
    structure_path = Path("tests/test_structure.json")
    with open(structure_path, "w") as f:
        json.dump(structure, f, indent=2)
    print(f"📁 Test structure generated: {structure_path}")
    

if __name__ == "__main__":
    main()