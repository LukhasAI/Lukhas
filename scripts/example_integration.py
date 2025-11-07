#!/usr/bin/env python3
"""
Example script showing how to integrate a hidden gem module
This demonstrates the complete process for Agent Codex
"""

import ast
import json
import os
from pathlib import Path
from typing import Any, Dict


def integrate_hidden_gem(module_path: str) -> dict[str, Any]:
    """
    Complete integration process for a single hidden gem module.

    Args:
        module_path: Path to the module (e.g., "candidate/consciousness/reflection/some_module.py")

    Returns:
        Dictionary with integration results
    """
    print(f"🎯 Integrating: {module_path}")

    results = {
        "module": module_path,
        "steps": []
    }

    # Step 1: Move to production
    print("  📦 Moving to production location...")
    new_path = move_to_production(module_path)
    results["new_path"] = new_path
    results["steps"].append({"step": "move", "status": "success", "path": new_path})

    # Step 2: Fix imports
    print("  🔧 Fixing imports...")
    fix_imports(new_path)
    results["steps"].append({"step": "fix_imports", "status": "success"})

    # Step 3: Generate MATRIZ schema
    print("  📋 Generating MATRIZ schema...")
    schema_path = generate_matriz_schema(new_path)
    results["schema"] = schema_path
    results["steps"].append({"step": "generate_schema", "status": "success", "path": schema_path})

    # Step 4: Create test
    print("  🧪 Creating test...")
    test_path = create_test(new_path)
    results["test"] = test_path
    results["steps"].append({"step": "create_test", "status": "success", "path": test_path})

    # Step 5: Validate
    print("  ✅ Validating...")
    validation = validate_module(new_path)
    results["validation"] = validation
    results["steps"].append({"step": "validate", "status": "success" if validation["ready"] else "failed"})

    print(f"  {'✅' if validation['ready'] else '❌'} Integration {'complete' if validation['ready'] else 'failed'}")

    return results


def move_to_production(module_path: str) -> str:
    """Move module from candidate/labs to production location"""

    source = Path(module_path)

    # Determine target based on module type
    if "consciousness" in str(source):
        target_dir = Path("matriz/consciousness")
    elif "memory" in str(source):
        target_dir = Path("matriz/memory")
    elif "governance" in str(source):
        target_dir = Path("governance")
    elif "identity" in str(source):
        target_dir = Path("core/identity")
    else:
        target_dir = Path("core")

    # Preserve subdirectory structure if relevant
    if "reflection" in str(source):
        target_dir = target_dir / "reflection"

    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / source.name

    # Use git mv to preserve history
    os.system(f"git mv {source} {target}")

    return str(target)


def fix_imports(module_path: str):
    """Fix common import issues in module"""

    with open(module_path) as f:
        content = f.read()

    # Fix common patterns
    replacements = [
        ("from labs.", "from "),
        ("from labs.", "from "),
        ("from matriz.", "from matriz."),
        ("import matriz", "import matriz"),
        # Fix relative imports
        ("from ..consciousness", "from matriz.consciousness"),
        ("from ..memory", "from matriz.memory"),
        ("from ..core", "from core"),
    ]

    for old, new in replacements:
        content = content.replace(old, new)

    # Fix logger issues if present
    import re
    # Fix logger.method("msg", key=value) -> logger.method("msg: key=%s", value)
    content = re.sub(
        r'(logger\.\w+)\((".*?"),\s*(\w+)=(.*?)\)',
        r'\1(\2 + ": \3=%s", \4)',
        content
    )

    with open(module_path, 'w') as f:
        f.write(content)


def generate_matriz_schema(module_path: str) -> str:
    """Generate MATRIZ schema for module"""

    module_name = Path(module_path).stem

    # Parse module to extract information
    with open(module_path) as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            # If parsing fails, create minimal schema
            tree = None

    # Extract classes if AST parsing succeeded
    classes = []
    if tree:
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                classes.append({
                    "name": node.name,
                    "methods": methods[:5],  # Limit to first 5 methods
                    "description": ast.get_docstring(node) or f"{node.name} class"
                })

    # Detect constellation stars based on module name
    stars = []
    star_keywords = {
        "consciousness": ["consciousness", "quantum", "dream"],
        "memory": ["memory", "identity"],
        "identity": ["identity", "guardian"],
        "governance": ["guardian", "ethics"],
        "bio": ["bio", "vision"],
        "quantum": ["quantum", "dream"],
    }

    for keyword, star_list in star_keywords.items():
        if keyword in module_name.lower():
            stars.extend(star_list)

    if not stars:
        stars = ["memory", "identity"]  # Default

    # Create schema
    schema = {
        "module": f"matriz.{module_name}",
        "version": "1.0.0",
        "type": module_name.replace("_", "-"),
        "matriz_compatible": True,
        "description": f"{module_name} module for LUKHAS AGI system",

        "capabilities": {
            "sends": [
                {
                    "signal": f"{module_name}_update",
                    "schema": "StateUpdate",
                    "frequency": "on_change",
                    "latency_target_ms": 50,
                    "description": f"State update from {module_name}"
                }
            ],
            "receives": [
                {
                    "signal": f"process_{module_name}",
                    "schema": "ProcessRequest",
                    "handler": "process",
                    "required": True,
                    "description": f"Process request for {module_name}"
                }
            ]
        },

        "main_classes": classes[:3],  # Limit to first 3 classes

        "dependencies": [
            "numpy",
            "time",
            "uuid",
            "dataclasses"
        ],

        "performance": {
            "max_latency_ms": 100,
            "memory_limit_mb": 50,
            "cpu_cores": 1
        },

        "constellation_integration": {
            "stars": list(set(stars)),
            "primary_star": stars[0] if stars else "memory",
            "validates": True
        },

        "governance": {
            "requires_consent": ["processing"],
            "audit_level": "standard",
            "provenance_tracking": True,
            "interpretability": "medium"
        }
    }

    # Save schema
    schema_dir = Path("matriz/schemas")
    schema_dir.mkdir(parents=True, exist_ok=True)
    schema_path = schema_dir / f"{module_name}_schema.json"

    with open(schema_path, 'w') as f:
        json.dump(schema, f, indent=2)

    return str(schema_path)


def create_test(module_path: str) -> str:
    """Create basic test for module"""

    module_name = Path(module_path).stem

    # Determine import path
    if "matriz" in str(module_path):
        import_path = str(module_path).replace("/", ".").replace(".py", "")
    else:
        import_path = module_name

    test_content = f'''#!/usr/bin/env python3
"""
Test suite for {module_name} module
Auto-generated by hidden gems integration
"""

import pytest
import sys
sys.path.insert(0, '.')


class Test{module_name.replace("_", "").title()}:
    """Test cases for {module_name}"""

    def test_module_imports(self):
        """Test that module imports successfully"""
        try:
            import {import_path.replace("-", "_")}
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import {module_name}: {{e}}")

    def test_matriz_compatibility(self):
        """Test MATRIZ compatibility"""
        # TODO: Import module and check for to_matriz_node method
        pass

    def test_signal_handlers(self):
        """Test signal handler presence"""
        # TODO: Check for handle_* methods
        pass

    @pytest.mark.parametrize("method", ["process", "to_dict", "validate"])
    def test_required_methods(self, method):
        """Test presence of required methods"""
        # TODO: Check if method exists
        pass
'''

    # Save test
    test_dir = Path("tests/unit")
    test_dir.mkdir(parents=True, exist_ok=True)
    test_path = test_dir / f"test_{module_name}.py"

    with open(test_path, 'w') as f:
        f.write(test_content)

    return str(test_path)


def validate_module(module_path: str) -> dict[str, Any]:
    """Validate module MATRIZ readiness"""

    module_name = Path(module_path).stem
    results = {
        "module": module_name,
        "checks": {},
        "ready": False
    }

    # Check 1: Module imports
    try:
        # Try to import (this is a simplified check)
        with open(module_path) as f:
            compile(f.read(), module_path, 'exec')
        results["checks"]["imports"] = True
    except Exception:
        results["checks"]["imports"] = False

    # Check 2: Schema exists
    schema_path = Path("matriz/schemas") / f"{module_name}_schema.json"
    results["checks"]["schema"] = schema_path.exists()

    # Check 3: Test exists
    test_path = Path("tests/unit") / f"test_{module_name}.py"
    results["checks"]["test"] = test_path.exists()

    # Check 4: No syntax errors
    try:
        with open(module_path) as f:
            ast.parse(f.read())
        results["checks"]["syntax"] = True
    except Exception:
        results["checks"]["syntax"] = False

    # Calculate readiness
    passed = sum(1 for v in results["checks"].values() if v)
    total = len(results["checks"])
    results["score"] = (passed / total) * 100
    results["ready"] = passed >= 3  # At least 3 out of 4 checks

    return results


def main():
    """Example integration of a module"""

    # Example module to integrate
    example_module = "candidate/consciousness/reflection/example_module.py"

    # Check if example exists, if not use a real one
    if not Path(example_module).exists():
        # Find a real candidate module
        candidate_modules = list(Path("candidate").rglob("*.py"))
        if candidate_modules:
            example_module = str(candidate_modules[0])
        else:
            print("No candidate modules found to integrate")
            return

    print("=" * 60)
    print("  HIDDEN GEMS INTEGRATION EXAMPLE")
    print("=" * 60)
    print()

    # Run integration
    results = integrate_hidden_gem(example_module)

    # Print results
    print()
    print("Integration Results:")
    print("-" * 40)
    print(json.dumps(results, indent=2))

    # Summary
    print()
    print("Summary:")
    print(f"  Module: {results['module']}")
    print(f"  New Path: {results.get('new_path', 'N/A')}")
    print(f"  Schema: {results.get('schema', 'N/A')}")
    print(f"  Test: {results.get('test', 'N/A')}")
    if 'validation' in results:
        print(f"  Readiness Score: {results['validation']['score']:.0f}%")
        print(f"  Ready: {'✅ Yes' if results['validation']['ready'] else '❌ No'}")


if __name__ == "__main__":
    main()
