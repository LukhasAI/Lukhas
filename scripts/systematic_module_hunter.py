#!/usr/bin/env python3
"""
🔍 LUKHAS Systematic Module Hunter
Comprehensive system-by-system testing with global search for missing components
Never accepts missing modules - always searches globally first
Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""

import importlib
import re
import sys
import time
from pathlib import Path
from typing import Any, Optional


class SystematicModuleHunter:
    """Hunt down every module and class systematically"""

    def __init__(self):
        self.results = {}
        self.missing_classes = {}
        self.found_classes = {}
        self.search_cache = {}
        self.base_path = Path(__file__).parent

    def log_info(self, message: str):
        print(f"ℹ️  {message}")

    def log_success(self, message: str):
        print(f"✅ {message}")

    def log_warning(self, message: str):
        print(f"⚠️  {message}")

    def log_error(self, message: str):
        print(f"❌ {message}")

    def log_search(self, message: str):
        print(f"🔍 {message}")

    def global_search_class(self, class_name: str) -> list[str]:
        """Search for a class name globally in all Python files"""
        if class_name in self.search_cache:
            return self.search_cache[class_name]

        self.log_search(f"Hunting for class '{class_name}' globally...")

        found_locations = []

        # Search in all Python files
        python_files = list(self.base_path.rglob("*.py"))

        for py_file in python_files:
            try:
                with open(py_file, encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                    # Look for class definitions
                    class_pattern = rf"class\s+{re.escape(class_name)}\s*[\(::]"
                    if re.search(class_pattern, content, re.MULTILINE):
                        relative_path = py_file.relative_to(self.base_path)
                        found_locations.append(str(relative_path))
                        self.log_search(f"  📍 Found class definition: {relative_path}")

                    # Look for imports
                    import_patterns = [
                        rf"from\s+[\w\.]+\s+import\s+.*{re.escape(class_name)}",
                        rf"import\s+.*{re.escape(class_name)}",
                    ]

                    for pattern in import_patterns:
                        if re.search(pattern, content, re.MULTILINE):
                            relative_path = py_file.relative_to(self.base_path)
                            if str(relative_path) not in found_locations:
                                found_locations.append(f"{relative_path} (import)")
                                self.log_search(f"  📦 Found import reference: {relative_path}")

            except Exception:
                # Skip files that can't be read
                continue

        self.search_cache[class_name] = found_locations

        if found_locations:
            self.log_success(f"Found {len(found_locations)} references to '{class_name}'")
        else:
            self.log_warning(f"Class '{class_name}' not found anywhere in codebase")

        return found_locations

    def global_search_module(self, module_name: str) -> list[str]:
        """Search for a module name globally"""
        self.log_search(f"Hunting for module '{module_name}' globally...")

        found_locations = []

        # Convert module path to file path
        module_parts = module_name.split(".")

        # Look for direct file match
        possible_files = [
            self.base_path / f"{'/'.join(module_parts)}.py",
            self.base_path / f"{'/'.join(module_parts)}/__init__.py",
        ]

        for possible_file in possible_files:
            if possible_file.exists():
                relative_path = possible_file.relative_to(self.base_path)
                found_locations.append(str(relative_path))
                self.log_search(f"  📁 Found module file: {relative_path}")

        # Search for references in Python files
        python_files = list(self.base_path.rglob("*.py"))

        for py_file in python_files:
            try:
                with open(py_file, encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                    # Look for module imports
                    import_patterns = [
                        rf"from\s+{re.escape(module_name)}\s+import",
                        rf"import\s+{re.escape(module_name)}",
                    ]

                    for pattern in import_patterns:
                        if re.search(pattern, content, re.MULTILINE):
                            relative_path = py_file.relative_to(self.base_path)
                            ref_path = f"{relative_path} (reference)"
                            if ref_path not in found_locations:
                                found_locations.append(ref_path)
                                self.log_search(f"  📦 Found module reference: {relative_path}")
            except:
                continue

        if found_locations:
            self.log_success(f"Found {len(found_locations)} references to module '{module_name}'")
        else:
            self.log_warning(f"Module '{module_name}' not found anywhere in codebase")

        return found_locations

    def test_module_with_hunting(self, module_name: str, expected_classes: Optional[list[str]] = None) -> dict[str, Any]:
        """Test a module and hunt for missing classes"""
        self.log_info(f"Testing module: {module_name}")

        result = {
            "module_name": module_name,
            "status": "unknown",
            "classes": [],
            "missing_classes": {},
            "found_classes": {},
            "error": None,
        }

        try:
            # Try to import the module
            module = importlib.import_module(module_name)
            result["status"] = "success"
            result["classes"] = [
                name
                for name in dir(module)
                if not name.startswith("_") and hasattr(getattr(module, name, None), "__class__")
            ]
            self.log_success(f"Module loaded: {module_name}")

            # If we have expected classes, check for them
            if expected_classes:
                for class_name in expected_classes:
                    if hasattr(module, class_name):
                        result["found_classes"][class_name] = "available"
                        self.log_success(f"  ✅ Class found: {class_name}")
                    else:
                        # Hunt for the missing class globally
                        locations = self.global_search_class(class_name)
                        result["missing_classes"][class_name] = locations
                        if locations:
                            self.log_warning(f"  ⚠️  Class '{class_name}' not in module but found elsewhere")
                        else:
                            self.log_error(f"  ❌ Class '{class_name}' completely missing from codebase")

        except ImportError as e:
            result["status"] = "import_error"
            result["error"] = str(e)
            self.log_error(f"Import failed: {module_name} - {e}")

            # Hunt for the module globally
            locations = self.global_search_module(module_name)
            result["module_locations"] = locations

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            self.log_error(f"Module error: {module_name} - {e}")

        return result

    def test_colony_system(self):
        """Test colony system with comprehensive hunting"""
        print("\n" + "=" * 80)
        print("🏘️ TESTING COLONY SYSTEM")
        print("=" * 80)

        colony_modules = {
            "candidate.core.colonies.base_colony": [
                "BaseColony",
                "Colony",
                "ColonyBase",
            ],
            "candidate.core.colonies.reasoning_colony": ["ReasoningColony"],
            "candidate.core.colonies.creativity_colony": ["CreativityColony"],
            "candidate.core.colonies.memory_colony": ["MemoryColony"],
            "candidate.core.colonies.oracle_colony": ["OracleColony"],
            "candidate.core.colonies.ethics_swarm_colony": ["EthicsSwarmColony"],
            "candidate.core.colonies.temporal_colony": ["TemporalColony"],
            "candidate.core.colonies.governance_colony": [
                "GovernanceColony",
                "GovernanceColonyEnhanced",
            ],
        }

        colony_results = {}

        for module_name, expected_classes in colony_modules.items():
            result = self.test_module_with_hunting(module_name, expected_classes)
            colony_results[module_name] = result
            print()  # spacing

        self.results["colony_system"] = colony_results

        # Summary
        working_count = len([r for r in colony_results.values() if r["status"] == "success"])
        total_count = len(colony_results)
        print(f"\n📊 Colony System Summary: {working_count}/{total_count} modules working")

    def test_consciousness_system(self):
        """Test consciousness system with comprehensive hunting"""
        print("\n" + "=" * 80)
        print("🧠 TESTING CONSCIOUSNESS SYSTEM")
        print("=" * 80)

        consciousness_modules = {
            "candidate.consciousness": ["Consciousness", "ConsciousnessCore"],
            "candidate.consciousness.creativity.creative_core": [
                "CreativeCore",
                "CreativityEngine",
            ],
            "candidate.consciousness.reflection.orchestration_service": ["OrchestrationService"],
            "candidate.consciousness.reflection.colony_orchestrator": [
                "ColonyOrchestrator",
                "QIUserContext",
            ],
            "candidate.consciousness.awareness.symbolic_qi_attention": [
                "SymbolicQIAttention",
                "BioOrchestrator",
            ],
            "candidate.consciousness.neuroplastic_connector": ["NeuroplasticConnector"],
            "candidate.consciousness.matriz_adapter": ["MatrizAdapter"],
        }

        consciousness_results = {}

        for module_name, expected_classes in consciousness_modules.items():
            result = self.test_module_with_hunting(module_name, expected_classes)
            consciousness_results[module_name] = result
            print()

        self.results["consciousness_system"] = consciousness_results

        working_count = len([r for r in consciousness_results.values() if r["status"] == "success"])
        total_count = len(consciousness_results)
        print(f"\n📊 Consciousness System Summary: {working_count}/{total_count} modules working")

    def test_qi_system(self):
        """Test QI system with comprehensive hunting"""
        print("\n" + "=" * 80)
        print("⚛️ TESTING QI (QUANTUM INTELLIGENCE) SYSTEM")
        print("=" * 80)

        qi_modules = {
            "qi": ["get_qi_status"],
            "qi.bio.bio_integration": ["BioIntegration", "BioQIBridge"],
            "qi.processing.qi_coordinator": ["QICoordinator"],
            "qi.systems.consciousness_integration": ["ConsciousnessIntegration"],
            "qi.coordination.coordinator": ["QICoordinator", "Coordinator"],
            "qi.awareness_system.core_awareness": ["CoreAwareness", "AwarenessSystem"],
            "candidate.qi.qi_integration_manager": ["QIIntegrationManager"],
        }

        qi_results = {}

        for module_name, expected_classes in qi_modules.items():
            result = self.test_module_with_hunting(module_name, expected_classes)
            qi_results[module_name] = result
            print()

        self.results["qi_system"] = qi_results

        working_count = len([r for r in qi_results.values() if r["status"] == "success"])
        total_count = len(qi_results)
        print(f"\n📊 QI System Summary: {working_count}/{total_count} modules working")

    def test_dream_system(self):
        """Test dream system with comprehensive hunting"""
        print("\n" + "=" * 80)
        print("🌙 TESTING DREAM SYSTEM")
        print("=" * 80)

        dream_modules = {
            "candidate.emotion.dreamseed_upgrade": ["DreamseedUpgrade", "DreamCore"],
            "symbolic.vocabularies.dream_vocabulary": ["DreamVocabulary"],
            "branding.vocabularies.dream_vocabulary": ["BrandingDreamVocabulary"],
        }

        dream_results = {}

        for module_name, expected_classes in dream_modules.items():
            result = self.test_module_with_hunting(module_name, expected_classes)
            dream_results[module_name] = result
            print()

        self.results["dream_system"] = dream_results

        working_count = len([r for r in dream_results.values() if r["status"] == "success"])
        total_count = len(dream_results)
        print(f"\n📊 Dream System Summary: {working_count}/{total_count} modules working")

    def test_bio_symbolic_system(self):
        """Test bio-symbolic system with comprehensive hunting"""
        print("\n" + "=" * 80)
        print("🧬 TESTING BIO-SYMBOLIC SYSTEM")
        print("=" * 80)

        bio_modules = {
            "bio.core.symbolic_bio_symbolic": ["SymbolicBioSymbolic", "BioSymbolic"],
            "bio.core.symbolic_bio_symbolic_orchestrator": ["BioSymbolicOrchestrator"],
            "candidate.core.integration.neuro_symbolic_fusion_layer": ["NeuroSymbolicFusionLayer"],
            "bio.bio_utilities": ["BioUtilities"],
        }

        bio_results = {}

        for module_name, expected_classes in bio_modules.items():
            result = self.test_module_with_hunting(module_name, expected_classes)
            bio_results[module_name] = result
            print()

        self.results["bio_symbolic_system"] = bio_results

        working_count = len([r for r in bio_results.values() if r["status"] == "success"])
        total_count = len(bio_results)
        print(f"\n📊 Bio-Symbolic System Summary: {working_count}/{total_count} modules working")

    def run_systematic_hunt(self):
        """Run comprehensive systematic testing with hunting"""
        print("🎯 LUKHAS SYSTEMATIC MODULE HUNTER")
        print("=" * 80)
        print("🔍 Never accepting missing modules - hunting everything globally!")
        print("=" * 80)

        start_time = time.time()

        # Test each system
        self.test_colony_system()
        self.test_consciousness_system()
        self.test_qi_system()
        self.test_dream_system()
        self.test_bio_symbolic_system()

        # Generate comprehensive report
        self.generate_hunt_report(time.time() - start_time)

    def generate_hunt_report(self, duration: float):
        """Generate comprehensive hunt report"""
        print("\n" + "=" * 80)
        print("📊 SYSTEMATIC HUNT REPORT")
        print("=" * 80)

        total_modules = 0
        working_modules = 0
        total_missing_classes = 0
        total_found_elsewhere = 0

        for system_name, system_results in self.results.items():
            system_working = 0
            system_total = len(system_results)
            system_missing = 0
            system_found_elsewhere = 0

            for module_result in system_results.values():
                if module_result["status"] == "success":
                    system_working += 1

                system_missing += len(module_result.get("missing_classes", {}))
                system_found_elsewhere += len(
                    [cls for cls, locations in module_result.get("missing_classes", {}).items() if locations]
                )

            total_modules += system_total
            working_modules += system_working
            total_missing_classes += system_missing
            total_found_elsewhere += system_found_elsewhere

            success_rate = (system_working / system_total * 100) if system_total > 0 else 0
            print(f"\n🔍 {system_name.replace('_', ' ').title()}:")
            print(f"   📦 Modules: {system_working}/{system_total} ({success_rate:.1f}%)")
            print(f"   🔍 Missing classes: {system_missing}")
            print(f"   📍 Found elsewhere: {system_found_elsewhere}")

        print("\n🎯 OVERALL HUNT RESULTS:")
        overall_success = (working_modules / total_modules * 100) if total_modules > 0 else 0
        print(f"   📦 Working modules: {working_modules}/{total_modules} ({overall_success:.1f}%)")
        print(f"   🔍 Total missing classes: {total_missing_classes}")
        print(f"   📍 Classes found elsewhere: {total_found_elsewhere}")
        print(f"   ⏱️  Hunt duration: {duration:.2f}s")
        print(f"   🧬 Files searched: {len(list(self.base_path.rglob('*.py')))}")

        # Key findings
        print("\n🔬 KEY HUNT FINDINGS:")
        if total_found_elsewhere > 0:
            recovery_rate = (total_found_elsewhere / total_missing_classes * 100) if total_missing_classes > 0 else 0
            print(f"   ✅ Recovery rate: {recovery_rate:.1f}% of missing classes found elsewhere")
        else:
            print("   ❌ No missing classes found elsewhere - may need creation")

        print("\n📋 NEXT ACTIONS:")
        if total_found_elsewhere > 0:
            print("   1. 🔄 Fix import paths for classes found elsewhere")
        print("   2. 🏗️  Create missing classes that don't exist anywhere")
        print("   3. 🔧 Fix dependency issues for existing modules")


if __name__ == "__main__":
    # Add current directory to Python path
    sys.path.insert(0, str(Path(__file__).parent))

    hunter = SystematicModuleHunter()
    hunter.run_systematic_hunt()
