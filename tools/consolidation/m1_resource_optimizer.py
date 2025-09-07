#!/usr/bin/env python3
from typing import Any

"""
LUKHAS M1 Resource-Efficient Consolidator
Optimized consolidation for M1 MacBook constraints
"""

import gc
import json
import os
import shutil
import time
from pathlib import Path

import psutil

# M1 MacBook optimization settings
M1_SETTINGS = {
    "max_memory_gb": 8,  # Conservative for M1 base model
    "chunk_size_mb": 50,  # Process files in chunks
    "parallel_workers": 4,  # Efficient for M1's performance cores
    "gc_threshold": 100,  # Trigger garbage collection frequently
    "batch_size": 100,  # Files per batch
}


class M1ResourceOptimizer:
    """Resource-efficient consolidation for M1 MacBook"""

    def __init__(self, base_path: Path = Path(".")):
        self.base_path = base_path
        self.stats = {
            "files_processed": 0,
            "memory_saved_mb": 0,
            "duplicates_removed": 0,
            "time_saved_seconds": 0,
        }
        self._configure_for_m1()

    def _configure_for_m1(self):
        """Configure Python for M1 efficiency"""
        # Set garbage collection thresholds
        gc.set_threshold(
            M1_SETTINGS["gc_threshold"],
            M1_SETTINGS["gc_threshold"] // 10,
            M1_SETTINGS["gc_threshold"] // 100,
        )

        # Limit process priority to prevent system slowdown
        try:
            os.nice(10# Lower priority
        except BaseException:
            pass

    def get_memory_usage(self) -> dict[str, float]:
        """Get current memory usage"""
        memory = psutil.virtual_memory()
        return {
            "used_gb": memory.used / (1024**3),
            "available_gb": memory.available / (1024**3),
            "percent": memory.percent,
        }

    def consolidate_with_memory_limit(
        self, source_dirs: list[str], target_dirs: dict[str, str]
    ):
        """Consolidate directories with memory constraints"""
        print("🎯 M1-Optimized Consolidation Starting...")
        print(f"Memory: {self.get_memory_usage()}['available_gb']:.1f}GB available")

        for source, target in zip(source_dirs, target_dirs.values()):
            self._consolidate_directory_chunked(source, target)

    def _consolidate_directory_chunked(self, source: str, target: str):
        """Consolidate directory in memory-efficient chunks"""
        source_path = self.base_path / source
        target_path = self.base_path / target

        if not source_path.exists():
            return

        # Get all files
        all_files = list(source_path.rglob("*"))
        total_files = len([f for f in all_files if f.is_file()])

        print(f"\n📁 Consolidating {source} → {target}")
        print(f"   Files: {total_files}")

        # Process in chunks
        chunk_size = M1_SETTINGS["batch_size"]
        for i in range(0, total_files, chunk_size):
            chunk_files = all_files[i : i + chunk_size]
            self._process_chunk(chunk_files, source_path, target_path)

            # Check memory and clean if needed
            if self.get_memory_usage()["percent"] > 70:
                gc.collect()
                time.sleep(0.1# Brief pause for system

    def _process_chunk(self, files: list[Path], source_base: Path, target_base: Path):
        """Process a chunk of files"""
        for file_path in files:
            if file_path.is_file():
                relative_path = file_path.relative_to(source_base)
                target_path = target_base / relative_path

                # Create target directory
                target_path.parent.mkdir(parents=True, exist_ok=True)

                # Move file efficiently
                shutil.move(str(file_path), str(target_path))
                self.stats["files_processed"] += 1


class LivingArchitecturePreserver:
    """Preserves LUKHAS's living architecture during consolidation"""

    def __init__(self):
        self.living_concepts = {
            "growth_patterns": ["organic_evolution", "adaptive_structure"],
            "consciousness_nodes": ["awareness_points", "reflection_hubs"],
            "memory_helixes": ["dna_structure", "emotional_vectors"],
            "dream_portals": ["multiverse_gateways", "parallel_explorers"],
        }

    def preserve_living_connections(self, module_path: Path) -> dict[str, Any]:
        """Preserve living architecture connections"""
        preservation_map = {
            "preserved_concepts": [],
            "connection_points": [],
            "growth_potential": [],
        }

        # Scan for living architecture patterns
        for py_file in module_path.rglob("*.py"):
            try:
                content = py_file.read_text()

                # Check for living concepts
                for concept_type, patterns in self.living_concepts.items():
                    for pattern in patterns:
                        if pattern in content or pattern.replace("_", "") in content:
                            preservation_map["preserved_concepts"].append(
                                {
                                    "file": str(py_file.relative_to(module_path)),
                                    "concept": pattern,
                                    "type": concept_type,
                                }
                            )

                # Find connection points (imports between modules)
                if "from " in content and " import " in content:
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith(("from ", "import ")):
                            preservation_map["connection_points"].append(
                                {
                                    "file": str(py_file.relative_to(module_path)),
                                    "import": line.strip(),
                                }
                            )
            except BaseException:
                continue

        return preservation_map


class ModularServiceMaintainer:
    """Maintains modular structure for current services"""

    def __init__(self):
        self.core_services = {
            "consciousness_platform": {
                "modules": ["consciousness", "awareness", "reflection"],
                "port": 8100,
            },
            "dream_commerce": {
                "modules": ["dream", "creativity", "emergence"],
                "port": 8200,
            },
            "memory_services": {"modules": ["memory", "fold", "cascade"], "port": 8300},
        }

    def maintain_service_structure(self, base_path: Path) -> dict[str, Any]:
        """Ensure services remain modular and functional"""
        service_report = {}

        for service_name, config in self.core_services.items():
            service_path = (
                base_path
                / "/Users/agi_dev/LOCAL-REPOS/Lukhas/deployment/platforms"
                / service_name
            )

            service_report[service_name] = {
                "exists": service_path.exists(),
                "modules_found": [],
                "missing_modules": [],
                "port": config["port"],
            }

            # Check required modules
            for module in config["modules"]:
                module_found = False

                # Check in service directory
                if (service_path / module).exists() or (base_path / module).exists():
                    module_found = True

                if module_found:
                    service_report[service_name]["modules_found"].append(module)
                else:
                    service_report[service_name]["missing_modules"].append(module)

        return service_report


def create_m1_optimization_config() -> dict[str, Any]:
    """Create M1-specific optimization configuration"""
    return {
        "memory_optimization": {
            "use_memory_mapping": True,
            "chunk_processing": True,
            "aggressive_gc": True,
            "max_file_size_mb": 100,
        },
        "performance_optimization": {
            "use_arm64_optimized": True,
            "parallel_cores": 4,
            "efficiency_cores": 4,
            "avoid_thermal_throttle": True,
        },
        "storage_optimization": {
            "use_apfs_clones": True,
            "minimize_writes": True,
            "batch_operations": True,
        },
    }


def main():
    """Run M1-optimized consolidation"""
    print(
        """
╔═══════════════════════════════════════════════════════╗
║        LUKHAS M1-Optimized Consolidator v1.0          ║
║                                                       ║
║  Resource-efficient consolidation for M1 MacBook      ║
╚═══════════════════════════════════════════════════════╝
    """
    )

    # Check if running on M1
    import platform

    is_m1 = platform.machine() == "arm64" and platform.system() == "Darwin"

    print(f"\n💻 System: {platform.platform()}")
    print(f"🎯 M1 Optimized: {'Yes' if is_m1 else 'No (Generic mode)}'}")

    # Initialize components
    optimizer = M1ResourceOptimizer()
    preserver = LivingArchitecturePreserver()
    maintainer = ModularServiceMaintainer()

    # Show current memory status
    memory = optimizer.get_memory_usage()
    print("\n📊 Memory Status:")
    print(f"   Used: {memory['used_gb']:.1f}GB")
    print(f"   Available: {memory['available_gb']:.1f}GB")
    print(f"   Usage: {memory['percent']:.1f}%")

    # Check living architecture
    print("\n🌱 Checking Living Architecture...")
    base_path = Path(".")

    # Preserve living connections in key modules
    for module in ["consciousness", "memory", "dream"]:
        module_path = base_path / module
        if module_path.exists():
            preservation = preserver.preserve_living_connections(module_path)
            print(
                f"   {module}: {len(preservation['preserved_concepts'])} living concepts"
            )

    # Check modular services
    print("\n🔧 Checking Modular Services...")
    service_report = maintainer.maintain_service_structure(base_path)

    for service, info in service_report.items():
        status = "✅" if info["exists"] else "⚠️"
        print(
            f"   {status} {service}: {len(info['modules_found'])}/{len(info['modules_found']) + len(info['missing_modules'])} modules"
        )

    # Create optimization config
    config = create_m1_optimization_config()
    config_path = base_path / "config" / "m1_optimization.json"
    config_path.parent.mkdir(exist_ok=True)

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"\n📄 M1 optimization config saved to: {config_path}")

    print("\n✅ M1 optimization complete!")
    print("\n💡 Recommendations:")
    print("   • Use chunk processing for large operations")
    print("   • Monitor memory usage during consolidation")
    print("   • Leverage M1's efficiency cores for background tasks")
    print("   • Keep services modular for easy scaling")


if __name__ == "__main__":
    main()
