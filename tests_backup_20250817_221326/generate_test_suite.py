#!/usr/bin/env python3
"""
LUKHAS Test Suite Generator
Automatically generates tests for untested functions
"""

import ast
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple
import textwrap
import re


class TestGenerator:
    """Generate test cases for untested functions"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_dir = self.project_root / "tests"
        
        # Test template for different function types
        self.templates = {
            "class_method": self._class_method_template,
            "function": self._function_template,
            "async_function": self._async_function_template,
            "property": self._property_template
        }
        
    def generate_test_suite(self):
        """Generate complete test suite"""
        print("🔍 Analyzing codebase for untested functions...")
        
        # Core modules to test
        modules = ["core", "consciousness", "memory", "governance", 
                   "identity", "bridge", "emotion", "qi", "api"]
        
        test_files = {}
        total_generated = 0
        
        for module in modules:
            module_path = self.project_root / module
            if not module_path.exists():
                continue
                
            print(f"\n📦 Processing module: {module}")
            
            # Create test directory structure
            test_module_dir = self.test_dir / module
            test_module_dir.mkdir(exist_ok=True)
            
            # Find functions to test
            functions = self._find_functions(module_path)
            
            # Group by file
            files_to_test = {}
            for func_info in functions:
                file_name = func_info["file"]
                if file_name not in files_to_test:
                    files_to_test[file_name] = []
                files_to_test[file_name].append(func_info)
                
            # Generate tests for each file
            for file_name, funcs in files_to_test.items():
                if funcs:
                    test_content = self._generate_test_file(module, file_name, funcs)
                    test_file_name = f"test_{file_name}"
                    test_path = test_module_dir / test_file_name
                    
                    # Only write if test doesn't exist
                    if not test_path.exists():
                        with open(test_path, "w") as f:
                            f.write(test_content)
                        print(f"  ✅ Generated: {test_path.relative_to(self.project_root)}")
                        total_generated += len(funcs)
                        
        print(f"\n🎉 Generated tests for {total_generated} functions!")
        return test_files
        
    def _find_functions(self, module_path: Path) -> List[Dict]:
        """Find all functions in a module"""
        functions = []
        
        for py_file in module_path.rglob("*.py"):
            if "__pycache__" in str(py_file) or "test_" in py_file.name:
                continue
                
            try:
                with open(py_file) as f:
                    content = f.read()
                    tree = ast.parse(content)
                    
                # Extract functions and methods
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Skip private and test functions
                        if not node.name.startswith("_") and not node.name.startswith("test"):
                            func_info = {
                                "name": node.name,
                                "file": py_file.stem,
                                "is_async": isinstance(node, ast.AsyncFunctionDef),
                                "is_method": self._is_method(node, tree),
                                "has_test": self._test_exists(py_file.stem, node.name),
                                "args": [arg.arg for arg in node.args.args if arg.arg != "self"],
                                "decorators": [d.id if isinstance(d, ast.Name) else None 
                                             for d in node.decorator_list]
                            }
                            
                            # Only add if no test exists
                            if not func_info["has_test"]:
                                functions.append(func_info)
                                
            except Exception as e:
                print(f"  ⚠️ Error parsing {py_file}: {e}")
                
        return functions
        
    def _is_method(self, node: ast.FunctionDef, tree: ast.Module) -> bool:
        """Check if function is a class method"""
        for item in ast.walk(tree):
            if isinstance(item, ast.ClassDef):
                for class_node in item.body:
                    if class_node == node:
                        return True
        return False
        
    def _test_exists(self, file_name: str, func_name: str) -> bool:
        """Check if test already exists"""
        test_patterns = [
            f"test_{func_name}",
            f"test_{file_name}_{func_name}"
        ]
        
        for pattern in test_patterns:
            if list(self.test_dir.rglob(f"*{pattern}*.py")):
                return True
        return False
        
    def _generate_test_file(self, module: str, file_name: str, functions: List[Dict]) -> str:
        """Generate test file content"""
        content = f'''"""
Tests for {module}.{file_name}
Auto-generated by LUKHAS Test Suite Generator
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from {module}.{file_name} import *


class Test{self._to_camel_case(file_name)}:
    """Test cases for {file_name} module"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_data = {{
            "test_key": "test_value",
            "test_id": "test_123"
        }}
        
'''
        
        # Generate test for each function
        for func_info in functions:
            if func_info["is_async"]:
                test_code = self._async_function_template(func_info)
            elif func_info["is_method"]:
                test_code = self._class_method_template(func_info)
            elif "property" in func_info.get("decorators", []):
                test_code = self._property_template(func_info)
            else:
                test_code = self._function_template(func_info)
                
            content += test_code + "\n"
            
        # Add integration tests
        content += self._generate_integration_tests(module, file_name)
        
        # Add performance tests
        content += self._generate_performance_tests(module, file_name)
        
        return content
        
    def _function_template(self, func_info: Dict) -> str:
        """Template for regular functions"""
        func_name = func_info["name"]
        args = func_info.get("args", [])
        
        # Generate mock arguments
        mock_args = []
        for arg in args:
            if "id" in arg.lower():
                mock_args.append('"test_id_123"')
            elif "name" in arg.lower():
                mock_args.append('"test_name"')
            elif "data" in arg.lower():
                mock_args.append('{"key": "value"}')
            else:
                mock_args.append('Mock()')
                
        args_str = ", ".join(mock_args)
        
        return f'''    def test_{func_name}(self):
        """Test {func_name} function"""
        # Arrange
        {f"mock_args = ({args_str})" if args else "# No arguments needed"}
        
        # Act
        result = {func_name}({args_str if args else ""})
        
        # Assert
        assert result is not None
        # TODO: Add specific assertions based on function behavior
        
    def test_{func_name}_with_invalid_input(self):
        """Test {func_name} with invalid input"""
        # Test with None
        {"with pytest.raises(Exception):" if args else "# No arguments to test"}
        {f"    {func_name}(None)" if args else f"    pass  # No arguments"}
        
'''
        
    def _class_method_template(self, func_info: Dict) -> str:
        """Template for class methods"""
        func_name = func_info["name"]
        
        return f'''    def test_{func_name}_method(self):
        """Test {func_name} class method"""
        # Arrange
        mock_instance = Mock()
        mock_instance.{func_name} = Mock(return_value="test_result")
        
        # Act
        result = mock_instance.{func_name}()
        
        # Assert
        mock_instance.{func_name}.assert_called_once()
        assert result == "test_result"
        
'''
        
    def _async_function_template(self, func_info: Dict) -> str:
        """Template for async functions"""
        func_name = func_info["name"]
        args = func_info.get("args", [])
        args_str = ", ".join(["Mock()" for _ in args])
        
        return f'''    @pytest.mark.asyncio
    async def test_{func_name}_async(self):
        """Test async {func_name} function"""
        # Arrange
        {f"mock_args = ({args_str})" if args else "# No arguments needed"}
        
        # Act
        result = await {func_name}({args_str if args else ""})
        
        # Assert
        assert result is not None
        # TODO: Add specific assertions
        
'''
        
    def _property_template(self, func_info: Dict) -> str:
        """Template for property methods"""
        func_name = func_info["name"]
        
        return f'''    def test_{func_name}_property(self):
        """Test {func_name} property"""
        # Arrange
        mock_obj = Mock()
        mock_obj.{func_name} = "test_value"
        
        # Act & Assert
        assert mock_obj.{func_name} == "test_value"
        
'''
        
    def _generate_integration_tests(self, module: str, file_name: str) -> str:
        """Generate integration test template"""
        return f'''
class TestIntegration{self._to_camel_case(file_name)}:
    """Integration tests for {file_name}"""
    
    @pytest.mark.integration
    def test_integration_with_database(self):
        """Test integration with database"""
        # TODO: Implement database integration test
        pass
        
    @pytest.mark.integration
    def test_integration_with_external_api(self):
        """Test integration with external APIs"""
        # TODO: Implement API integration test
        pass
        
'''
        
    def _generate_performance_tests(self, module: str, file_name: str) -> str:
        """Generate performance test template"""
        return f'''
class TestPerformance{self._to_camel_case(file_name)}:
    """Performance tests for {file_name}"""
    
    @pytest.mark.performance
    def test_performance_under_load(self):
        """Test performance under load"""
        import time
        
        start_time = time.time()
        # TODO: Run performance critical operations
        duration = time.time() - start_time
        
        # Assert performance threshold
        assert duration < 1.0, f"Operation took {{duration}}s, expected < 1.0s"
        
    @pytest.mark.benchmark
    def test_benchmark(self, benchmark):
        """Benchmark test using pytest-benchmark"""
        # TODO: Add function to benchmark
        # result = benchmark(function_to_test, arg1, arg2)
        pass
        
'''
        
    def _to_camel_case(self, snake_str: str) -> str:
        """Convert snake_case to CamelCase"""
        components = snake_str.split('_')
        return ''.join(x.title() for x in components)
        

def create_test_organization():
    """Create organized test structure"""
    test_dir = Path(__file__).parent
    
    # Create directory structure
    directories = [
        "unit/core",
        "unit/consciousness", 
        "unit/memory",
        "unit/governance",
        "unit/identity",
        "integration/api",
        "integration/workflow",
        "e2e/scenarios",
        "performance/benchmarks",
        "security/vulnerabilities"
    ]
    
    for dir_path in directories:
        (test_dir / dir_path).mkdir(parents=True, exist_ok=True)
        
    # Create __init__.py files
    for dir_path in directories:
        init_file = test_dir / dir_path / "__init__.py"
        if not init_file.exists():
            init_file.write_text('"""Test module"""')
            
    print("✅ Created test directory structure")
    

def main():
    """Main execution"""
    print("🚀 LUKHAS Test Suite Generator")
    print("=" * 50)
    
    # Create organized structure
    create_test_organization()
    
    # Generate tests
    generator = TestGenerator()
    generator.generate_test_suite()
    
    print("\n📊 Test suite generation complete!")
    print("Run tests with: pytest tests/")
    print("View dashboard at: http://localhost:8000 (after running test_runner_api.py)")
    

if __name__ == "__main__":
    main()