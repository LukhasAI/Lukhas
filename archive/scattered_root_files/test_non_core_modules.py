#!/usr/bin/env python3
"""
🧬 LUKHAS Non-Core Module Testing Suite
Comprehensive testing for dream, colony, consciousness, and sub-core modules
Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""

import importlib
import sys
import time
from pathlib import Path


class NonCoreModuleTester:
    """Test all non-core LUKHAS modules"""

    def __init__(self):
        self.results = {
            "colonies": {},
            "consciousness": {},
            "creativity": {},
            "dream_systems": {},
            "bio_symbolic": {},
            "qi_modules": {},
            "candidate_modules": {},
            "errors": [],
            "warnings": [],
        }
        self.base_path = Path(__file__).parent

    def log_info(self, message: str):
        """Log info message"""
        print(f"ℹ️  {message}")

    def log_success(self, message: str):
        """Log success message"""
        print(f"✅ {message}")

    def log_warning(self, message: str):
        """Log warning message"""
        print(f"⚠️  {message}")
        self.results["warnings"].append(message)

    def log_error(self, message: str):
        """Log error message"""
        print(f"❌ {message}")
        self.results["errors"].append(message)

    def test_colony_modules(self):
        """Test colony system modules"""
        self.log_info("Testing Colony System Modules...")

        colony_modules = [
            "candidate.core.colonies.base_colony",
            "candidate.core.colonies.reasoning_colony",
            "candidate.core.colonies.creativity_colony",
            "candidate.core.colonies.memory_colony",
            "candidate.core.colonies.oracle_colony",
            "candidate.core.colonies.ethics_swarm_colony",
            "candidate.core.colonies.temporal_colony",
            "candidate.core.colonies.governance_colony",
        ]

        for module_name in colony_modules:
            try:
                module = importlib.import_module(module_name)
                self.results["colonies"][module_name] = {
                    "status": "success",
                    "classes": [
                        name
                        for name in dir(module)
                        if not name.startswith("_") and hasattr(getattr(module, name, None), "__class__")
                    ],
                }
                self.log_success(f"Colony module: {module_name}")
            except ImportError as e:
                self.results["colonies"][module_name] = {
                    "status": "import_error",
                    "error": str(e),
                }
                self.log_warning(f"Colony module not available: {module_name} ({e})")
            except Exception as e:
                self.results["colonies"][module_name] = {
                    "status": "error",
                    "error": str(e),
                }
                self.log_error(f"Colony module error: {module_name} ({e})")

    def test_consciousness_modules(self):
        """Test consciousness system modules"""
        self.log_info("Testing Consciousness System Modules...")

        consciousness_modules = [
            "candidate.consciousness",
            "candidate.consciousness.creativity.creative_core",
            "candidate.consciousness.reflection.orchestration_service",
            "candidate.consciousness.reflection.colony_orchestrator",
            "candidate.consciousness.awareness.symbolic_qi_attention",
            "candidate.consciousness.neuroplastic_connector",
            "candidate.consciousness.matriz_adapter",
        ]

        for module_name in consciousness_modules:
            try:
                module = importlib.import_module(module_name)
                self.results["consciousness"][module_name] = {
                    "status": "success",
                    "classes": [
                        name
                        for name in dir(module)
                        if not name.startswith("_") and hasattr(getattr(module, name, None), "__class__")
                    ],
                }
                self.log_success(f"Consciousness module: {module_name}")
            except ImportError as e:
                self.results["consciousness"][module_name] = {
                    "status": "import_error",
                    "error": str(e),
                }
                self.log_warning(f"Consciousness module not available: {module_name} ({e})")
            except Exception as e:
                self.results["consciousness"][module_name] = {
                    "status": "error",
                    "error": str(e),
                }
                self.log_error(f"Consciousness module error: {module_name} ({e})")

    def test_dream_systems(self):
        """Test dream-related modules"""
        self.log_info("Testing Dream System Modules...")

        dream_modules = [
            "candidate.emotion.dreamseed_upgrade",
            "symbolic.vocabularies.dream_vocabulary",
            "branding.vocabularies.dream_vocabulary",
        ]

        for module_name in dream_modules:
            try:
                module = importlib.import_module(module_name)
                self.results["dream_systems"][module_name] = {
                    "status": "success",
                    "classes": [
                        name
                        for name in dir(module)
                        if not name.startswith("_") and hasattr(getattr(module, name, None), "__class__")
                    ],
                }
                self.log_success(f"Dream module: {module_name}")
            except ImportError as e:
                self.results["dream_systems"][module_name] = {
                    "status": "import_error",
                    "error": str(e),
                }
                self.log_warning(f"Dream module not available: {module_name} ({e})")
            except Exception as e:
                self.results["dream_systems"][module_name] = {
                    "status": "error",
                    "error": str(e),
                }
                self.log_error(f"Dream module error: {module_name} ({e})")

    def test_bio_symbolic_modules(self):
        """Test bio-symbolic system modules"""
        self.log_info("Testing Bio-Symbolic System Modules...")

        bio_modules = [
            "bio.core.symbolic_bio_symbolic",
            "bio.core.symbolic_bio_symbolic_orchestrator",
            "candidate.core.integration.neuro_symbolic_fusion_layer",
        ]

        for module_name in bio_modules:
            try:
                module = importlib.import_module(module_name)
                self.results["bio_symbolic"][module_name] = {
                    "status": "success",
                    "classes": [
                        name
                        for name in dir(module)
                        if not name.startswith("_") and hasattr(getattr(module, name, None), "__class__")
                    ],
                }
                self.log_success(f"Bio-symbolic module: {module_name}")
            except ImportError as e:
                self.results["bio_symbolic"][module_name] = {
                    "status": "import_error",
                    "error": str(e),
                }
                self.log_warning(f"Bio-symbolic module not available: {module_name} ({e})")
            except Exception as e:
                self.results["bio_symbolic"][module_name] = {
                    "status": "error",
                    "error": str(e),
                }
                self.log_error(f"Bio-symbolic module error: {module_name} ({e})")

    def test_qi_modules(self):
        """Test qi (quantum intelligence) system modules"""
        self.log_info("Testing QI (Quantum Intelligence) System Modules...")

        qi_modules = [
            "qi",
            "qi.bio.bio_integration",
            "qi.processing.qi_coordinator",
            "qi.systems.consciousness_integration",
            "qi.coordination.coordinator",
            "qi.awareness_system.core_awareness",
            "candidate.qi.qi_integration_manager",
        ]

        for module_name in qi_modules:
            try:
                module = importlib.import_module(module_name)
                self.results["qi_modules"][module_name] = {
                    "status": "success",
                    "classes": [
                        name
                        for name in dir(module)
                        if not name.startswith("_") and hasattr(getattr(module, name, None), "__class__")
                    ],
                }
                self.log_success(f"QI module: {module_name}")
            except ImportError as e:
                self.results["qi_modules"][module_name] = {
                    "status": "import_error",
                    "error": str(e),
                }
                self.log_warning(f"QI module not available: {module_name} ({e})")
            except Exception as e:
                self.results["qi_modules"][module_name] = {
                    "status": "error",
                    "error": str(e),
                }
                self.log_error(f"QI module error: {module_name} ({e})")

    def test_candidate_core_modules(self):
        """Test candidate core system modules"""
        self.log_info("Testing Candidate Core System Modules...")

        candidate_modules = [
            "candidate.core.core_system",
            "candidate.core.integration.connectivity_engine",
            "candidate.core.integration.system_coordinator",
            "candidate.core.integration.executive_decision_integrator",
            "candidate.core.symbolic_arbitration",
        ]

        for module_name in candidate_modules:
            try:
                module = importlib.import_module(module_name)
                self.results["candidate_modules"][module_name] = {
                    "status": "success",
                    "classes": [
                        name
                        for name in dir(module)
                        if not name.startswith("_") and hasattr(getattr(module, name, None), "__class__")
                    ],
                }
                self.log_success(f"Candidate core module: {module_name}")
            except ImportError as e:
                self.results["candidate_modules"][module_name] = {
                    "status": "import_error",
                    "error": str(e),
                }
                self.log_warning(f"Candidate core module not available: {module_name} ({e})")
            except Exception as e:
                self.results["candidate_modules"][module_name] = {
                    "status": "error",
                    "error": str(e),
                }
                self.log_error(f"Candidate core module error: {module_name} ({e})")

    def check_directory_structures(self):
        """Check if key directories exist"""
        self.log_info("Checking Directory Structures...")

        key_directories = [
            "candidate/core/colonies",
            "candidate/consciousness",
            "candidate/emotion",
            "bio",
            "qi",
            "symbolic",
            "creativity",
        ]

        for dir_path in key_directories:
            full_path = self.base_path / dir_path
            if full_path.exists():
                file_count = len(list(full_path.rglob("*.py")))
                self.log_success(f"Directory exists: {dir_path} ({file_count} Python files)")
            else:
                self.log_warning(f"Directory not found: {dir_path}")

    def run_comprehensive_test(self):
        """Run all tests"""
        print("🧬 LUKHAS Non-Core Module Testing Suite")
        print("=" * 60)

        start_time = time.time()

        # Check directory structures first
        self.check_directory_structures()
        print()

        # Test all module categories
        self.test_colony_modules()
        print()

        self.test_consciousness_modules()
        print()

        self.test_dream_systems()
        print()

        self.test_bio_symbolic_modules()
        print()

        self.test_qi_modules()
        print()

        self.test_candidate_core_modules()
        print()

        # Generate summary
        self.generate_summary(time.time() - start_time)

    def generate_summary(self, duration: float):
        """Generate test summary"""
        print("📊 Test Summary")
        print("=" * 30)

        total_modules = 0
        successful_modules = 0

        for category, modules in self.results.items():
            if category in ["errors", "warnings"]:
                continue

            category_total = len(modules)
            category_success = len([m for m in modules.values() if m.get("status") == "success"])
            total_modules += category_total
            successful_modules += category_success

            if category_total > 0:
                success_rate = (category_success / category_total) * 100
                print(f"📦 {category.title(}: {category_success}/{category_total} ({success_rate:.1f}%)")

        print()
        overall_success_rate = (successful_modules / total_modules * 100) if total_modules > 0 else 0
        print(f"🎯 Overall: {successful_modules}/{total_modules} ({overall_success_rate:.1f}%)")
        print(f"⚠️  Warnings: {len(self.results['warnings']}")
        print(f"❌ Errors: {len(self.results['errors']}")
        print(f"⏱️  Duration: {duration:.2f}s")

        if overall_success_rate >= 70:
            print("🟢 System Status: GOOD")
        elif overall_success_rate >= 50:
            print("🟡 System Status: MODERATE")
        else:
            print("🔴 System Status: NEEDS ATTENTION")


if __name__ == "__main__":
    # Add current directory to Python path
    sys.path.insert(0, str(Path(__file__).parent))

    tester = NonCoreModuleTester()
    tester.run_comprehensive_test()
