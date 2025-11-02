#!/usr/bin/env python3
"""
LUKHAS Consciousness Component Contract Generator
Analyzes consciousness components and generates contracts
"""

import ast
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class ConsciousnessContractGenerator:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.consciousness_dir = self.root_path / "candidate" / "consciousness"
        self.contracts_dir = self.root_path / "contracts" / "consciousness"
        self.contracts_dir.mkdir(parents=True, exist_ok=True)

    def analyze_component_file(self, file_path: Path) -> Dict:
        """Analyze a Python consciousness component file"""
        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            # Parse AST
            tree = ast.parse(content)

            # Extract component info
            component_info = {
                "classes": [],
                "functions": [],
                "imports": [],
                "async_methods": [],
                "performance_hints": [],
                "trinity_references": []
            }

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    component_info["classes"].append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    component_info["functions"].append(node.name)
                    if isinstance(node, ast.AsyncFunctionDef):
                        component_info["async_methods"].append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        component_info["imports"].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        component_info["imports"].append(node.module)

            # Analyze content for patterns
            if "async " in content:
                component_info["processing_mode"] = "asynchronous"
            elif "stream" in content.lower():
                component_info["processing_mode"] = "stream"
            else:
                component_info["processing_mode"] = "synchronous"

            # Look for Constellation Framework references
            if any("identity" in imp.lower() for imp in component_info["imports"]):
                component_info["trinity_references"].append("identity")
            if any("guardian" in imp.lower() for imp in component_info["imports"]):
                component_info["trinity_references"].append("guardian")

            # Look for performance patterns
            if "cache" in content.lower():
                component_info["performance_hints"].append("caching")
            if "batch" in content.lower():
                component_info["performance_hints"].append("batching")

            return component_info

        except Exception as e:
            return {"error": f"Failed to analyze {file_path}: {e}"}

    def determine_component_type(self, file_path: Path, analysis: Dict) -> str:
        """Determine the component type based on file path and analysis"""
        path_str = str(file_path).lower()

        if "engine" in path_str:
            return "CONSCIOUSNESS_ENGINE"
        elif "cognitive" in path_str or "reflection" in path_str:
            return "COGNITIVE_PROCESSOR"
        elif "awareness" in path_str:
            return "AWARENESS_MODULE"
        elif "decision" in path_str:
            return "DECISION_MAKER"
        elif "emotion" in path_str:
            return "EMOTION_PROCESSOR"
        elif "memory" in path_str:
            return "MEMORY_INTERFACE"
        elif "constellation" in path_str or "bridge" in path_str:
            return "TRINITY_BRIDGE"
        elif "orchestration" in path_str:
            return "ORCHESTRATION_NODE"
        elif "symbolic" in path_str:
            return "SYMBOLIC_PROCESSOR"
        elif "creativity" in path_str or "creative" in path_str:
            return "CREATIVITY_ENGINE"
        elif "dream" in path_str:
            return "DREAM_PROCESSOR"
        else:
            return "COGNITIVE_PROCESSOR"  # Default

    def determine_lane(self, file_path: Path) -> str:
        """Determine lane based on file path"""
        path_str = str(file_path)
        if "/candidate/core/" in path_str:
            return "integration"
        elif "/candidate/" in path_str:
            return "development"
        elif "/lukhas/" in path_str:
            return "production"
        else:
            return "development"  # Default

    def generate_component_contract(self, file_path: Path) -> Dict:
        """Generate a contract for a consciousness component"""
        analysis = self.analyze_component_file(file_path)

        if "error" in analysis:
            return analysis

        # Generate component ID from file path
        rel_path = file_path.relative_to(self.root_path)
        component_id = str(rel_path).replace("/", ".").replace(".py", "")

        # Determine component properties
        component_type = self.determine_component_type(file_path, analysis)
        lane = self.determine_lane(file_path)

        # Generate contract
        contract = {
            "schema_version": "2.0.0",
            "component_id": component_id,
            "component_type": component_type,
            "lane": lane,
            "constellation_integration": {
                "identity_coupling": "identity" in analysis.get("trinity_references", []),
                "consciousness_role": "primary" if "engine" in str(file_path).lower() else "secondary",
                "guardian_validation": "guardian" in analysis.get("trinity_references", []) or component_type in ["CONSCIOUSNESS_ENGINE", "DECISION_MAKER"]
            },
            "cognitive_processing": {
                "processing_mode": analysis.get("processing_mode", "synchronous"),
                "input_types": self._infer_input_types(component_type, analysis),
                "output_types": self._infer_output_types(component_type, analysis),
                "cascade_prevention": True  # Default to true for all consciousness components
            },
            "performance_contract": {
                "latency_target": "<250ms",
                "throughput_target": 50.0,
                "availability_target": 0.997,
                "memory_limit": "100MB"
            },
            "governance": {
                "ethics_validation": "required" if component_type in ["CONSCIOUSNESS_ENGINE", "DECISION_MAKER"] else "optional",
                "consent_required": component_type in ["CONSCIOUSNESS_ENGINE", "MEMORY_INTERFACE"],
                "audit_level": "full" if component_type in ["CONSCIOUSNESS_ENGINE"] else "metadata",
                "privacy_classification": "confidential" if component_type in ["CONSCIOUSNESS_ENGINE", "MEMORY_INTERFACE"] else "internal"
            },
            "dependencies": [],  # Would need deeper analysis
            "metadata": {
                "created_date": "2025-09-20",
                "last_updated": datetime.now().isoformat(),
                "maintainer": "LUKHAS Consciousness Team",
                "documentation_url": f"https://docs.ai/consciousness/{component_id.replace('.', '/')}",
                "test_coverage": 85.0  # Default estimate
            }
        }

        return contract

    def _infer_input_types(self, component_type: str, analysis: Dict) -> List[str]:
        """Infer input types based on component type and analysis"""
        base_inputs = ["CONTEXT_INFO"]

        type_inputs = {
            "CONSCIOUSNESS_ENGINE": ["SENSORY_INPUT", "MEMORY_DATA", "EMOTIONAL_STATE"],
            "COGNITIVE_PROCESSOR": ["MEMORY_DATA", "CONTEXT_INFO"],
            "REFLECTION_SYSTEM": ["REFLECTION_PROMPT", "MEMORY_DATA"],
            "AWARENESS_MODULE": ["SENSORY_INPUT", "CONTEXT_INFO"],
            "DECISION_MAKER": ["DECISION_REQUEST", "CONTEXT_INFO"],
            "EMOTION_PROCESSOR": ["EMOTIONAL_STATE", "SENSORY_INPUT"],
            "MEMORY_INTERFACE": ["MEMORY_DATA"],
            "CREATIVITY_ENGINE": ["CREATIVE_STIMULUS", "EMOTIONAL_STATE"],
            "DREAM_PROCESSOR": ["DREAM_STATE", "MEMORY_DATA"]
        }

        return base_inputs + type_inputs.get(component_type, [])

    def _infer_output_types(self, component_type: str, analysis: Dict) -> List[str]:
        """Infer output types based on component type and analysis"""
        type_outputs = {
            "CONSCIOUSNESS_ENGINE": ["CONSCIOUSNESS_STATE", "EMOTIONAL_RESPONSE"],
            "COGNITIVE_PROCESSOR": ["AWARENESS_SIGNAL"],
            "REFLECTION_SYSTEM": ["REFLECTION_RESULT"],
            "AWARENESS_MODULE": ["AWARENESS_SIGNAL"],
            "DECISION_MAKER": ["DECISION_OUTPUT"],
            "EMOTION_PROCESSOR": ["EMOTIONAL_RESPONSE"],
            "MEMORY_INTERFACE": ["MEMORY_UPDATE"],
            "CREATIVITY_ENGINE": ["CREATIVE_EXPRESSION"],
            "DREAM_PROCESSOR": ["DREAM_CONTENT"]
        }

        return type_outputs.get(component_type, ["CONSCIOUSNESS_STATE"])

    def scan_consciousness_components(self) -> Dict:
        """Scan all consciousness components and generate contracts"""
        results = {
            "scan_timestamp": datetime.now().isoformat(),
            "total_files": 0,
            "contracts_generated": 0,
            "errors": [],
            "summary": {}
        }

        if not self.consciousness_dir.exists():
            results["error"] = "Consciousness directory not found"
            return results

        py_files = list(self.consciousness_dir.rglob("*.py"))
        results["total_files"] = len(py_files)

        component_types = {}

        for py_file in py_files:
            if py_file.name == "__init__.py":
                continue

            try:
                contract = self.generate_component_contract(py_file)

                if "error" not in contract:
                    # Save contract
                    contract_name = py_file.stem + ".json"
                    contract_path = self.contracts_dir / contract_name

                    with open(contract_path, 'w') as f:
                        json.dump(contract, f, indent=2)

                    results["contracts_generated"] += 1

                    # Track component types
                    comp_type = contract["component_type"]
                    if comp_type not in component_types:
                        component_types[comp_type] = 0
                    component_types[comp_type] += 1
                else:
                    results["errors"].append(contract["error"])

            except Exception as e:
                results["errors"].append(f"Failed to process {py_file}: {e}")

        results["summary"] = {
            "component_types": component_types,
            "success_rate": results["contracts_generated"] / results["total_files"] if results["total_files"] > 0 else 0
        }

        return results


def main():
    generator = ConsciousnessContractGenerator(".")
    results = generator.scan_consciousness_components()

    print("Consciousness Component Contract Generation Results:")
    print(f"Total files scanned: {results['total_files']}")
    print(f"Contracts generated: {results['contracts_generated']}")
    print(f"Success rate: {results['summary']['success_rate']:.1%}")

    if results["errors"]:
        print(f"\nErrors ({len(results['errors'])}):")
        for error in results["errors"][:5]:  # Show first 5 errors
            print(f"  - {error}")

    print("\nComponent type distribution:")
    for comp_type, count in results["summary"]["component_types"].items():
        print(f"  {comp_type}: {count}")

    # Save full results
    with open("temp_consciousness_contracts_report.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\nFull results saved to: temp_consciousness_contracts_report.json")


if __name__ == "__main__":
    main()
