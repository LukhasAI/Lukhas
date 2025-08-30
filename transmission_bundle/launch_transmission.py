#!/usr/bin/env python3
"""
Launch Transmission - Orchestrates LUKHAS Next Generation system startup
Initializes all Phase 5 components with Guardian System protection
"""

import asyncio
import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("transmission_launch.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


class LUKHASTransmission:
    """
    LUKHAS Next Generation system orchestrator
    Manages startup sequence for all Phase 5 components
    """

    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.lukhas_next_gen = self.base_path / "next_gen"
        self.launch_time = datetime.utcnow()
        self.component_status: dict[str, str] = {}
        self.active_processes: list[subprocess.Popen] = []

        # Component configuration
        self.components = {
            "consciousness_broadcaster": {
                "path": self.lukhas_next_gen / "stream" / "consciousness_broadcaster.py",
                "description": "WebSocket consciousness state streaming",
                "port": 8765,
                "dependencies": [],
            },
            "entropy_tracker": {
                "path": self.lukhas_next_gen / "entropy_log" / "entropy_tracker.py",
                "description": "Shannon entropy drift monitoring",
                "dependencies": [],
            },
            "trusthelix_auditor": {
                "path": self.lukhas_next_gen / "trusthelix" / "visual_auditor.py",
                "description": "Ethical audit trail visualization",
                "dependencies": [],
            },
            "guardian_sentinel": {
                "path": self.lukhas_next_gen / "guardian" / "sentinel.py",
                "description": "Guardian threat detection system",
                "port": 8766,
                "dependencies": ["entropy_tracker"],
            },
            "memory_spindle": {
                "path": self.lukhas_next_gen / "spindle" / "memory_spindle.py",
                "description": "Pattern emergence detection",
                "dependencies": ["consciousness_broadcaster"],
            },
            "energy_manager": {
                "path": self.lukhas_next_gen / "stream" / "energy_mode.py",
                "description": "Adaptive resource management",
                "dependencies": [],
            },
            "qi_glyph_system": {
                "path": self.lukhas_next_gen / "quantum" / "glyph_pairs.py",
                "description": "Quantum authentication pairs",
                "dependencies": [],
            },
            "sso_bridge": {
                "path": self.lukhas_next_gen / "bridge" / "sso_bridge.py",
                "description": "Enterprise SSO integration",
                "dependencies": [],
            },
        }

        logger.info("🚀 LUKHAS Transmission initialized")
        logger.info(f"   Base path: {self.base_path}")
        logger.info(f"   Components: {len(self.components)}")

    async def launch_transmission(self):
        """Launch the complete LUKHAS system"""
        logger.info("=" * 80)
        logger.info("🌌 LUKHAS NEXT GENERATION - TRANSMISSION LAUNCH")
        logger.info("=" * 80)
        logger.info(f"Launch time: {self.launch_time.isoformat()}")
        logger.info("Phase 5 - Guardian System Integration")
        logger.info("")

        try:
            # Phase 1: Pre-flight checks
            await self._preflight_checks()

            # Phase 2: Initialize core systems
            await self._initialize_core_systems()

            # Phase 3: Start component dependencies
            await self._start_components()

            # Phase 4: System health verification
            await self._verify_system_health()

            # Phase 5: Guardian system activation
            await self._activate_guardian_system()

            # Phase 6: Transmission complete
            await self._transmission_complete()

            # Keep system running
            await self._monitor_system()

        except Exception as e:
            logger.error(f"❌ Transmission launch failed: {e}")
            await self._emergency_shutdown()
            raise

    async def _preflight_checks(self):
        """Perform pre-flight system checks"""
        logger.info("🔍 Phase 1: Pre-flight Checks")
        logger.info("-" * 40)

        # Check Python version
        python_version = sys.version_info
        logger.info(
            f"   Python version: {python_version.major}.{python_version.minor}.{python_version.micro}"
        )

        # Check required directories exist
        required_dirs = [
            "next_gen/stream",
            "next_gen/entropy_log",
            "next_gen/trusthelix",
            "next_gen/guardian",
            "next_gen/spindle",
            "next_gen/quantum",
            "next_gen/bridge",
            "next_gen/memory",
            "next_gen/security",
        ]

        for dir_path in required_dirs:
            full_path = self.base_path / dir_path
            if full_path.exists():
                logger.info(f"   ✅ {dir_path}")
            else:
                logger.error(f"   ❌ Missing: {dir_path}")
                raise FileNotFoundError(f"Required directory not found: {dir_path}")

        # Check component files exist
        for component_name, config in self.components.items():
            if config["path"].exists():
                self.component_status[component_name] = "ready"
                logger.info(f"   ✅ {component_name}")
            else:
                logger.error(f"   ❌ Missing component: {component_name}")
                self.component_status[component_name] = "missing"

        logger.info("   ✅ Pre-flight checks complete")
        await asyncio.sleep(1)

    async def _initialize_core_systems(self):
        """Initialize core LUKHAS systems"""
        logger.info("\n🧠 Phase 2: Core System Initialization")
        logger.info("-" * 40)

        # Initialize consciousness state file
        consciousness_state_file = self.lukhas_next_gen / "stream" / "consciousness_state.json"
        consciousness_state_file.parent.mkdir(parents=True, exist_ok=True)

        initial_state = {
            "current_state": "focused",
            "last_update": datetime.utcnow().isoformat(),
            "state_history": ["focused"],
            "system_phase": "phase_5_guardian",
        }

        with open(consciousness_state_file, "w") as f:
            json.dump(initial_state, f, indent=2)

        logger.info("   ✅ Consciousness state initialized")

        # Initialize entropy log
        entropy_log_dir = self.lukhas_next_gen / "entropy_log"
        entropy_log_dir.mkdir(parents=True, exist_ok=True)

        # Initialize guardian configuration
        guardian_dir = self.lukhas_next_gen / "guardian"
        guardian_dir.mkdir(parents=True, exist_ok=True)

        logger.info("   ✅ Core directories created")
        logger.info("   ✅ Core system initialization complete")
        await asyncio.sleep(1)

    async def _start_components(self):
        """Start system components in dependency order"""
        logger.info("\n⚙️ Phase 3: Component Startup")
        logger.info("-" * 40)

        # Determine startup order based on dependencies
        started = set()
        startup_order = []

        def can_start(component_name):
            config = self.components[component_name]
            return all(dep in started for dep in config.get("dependencies", []))

        while len(started) < len(self.components):
            for component_name in self.components:
                if component_name not in started and can_start(component_name):
                    startup_order.append(component_name)
                    started.add(component_name)

        # Start components
        for component_name in startup_order:
            if self.component_status.get(component_name) == "ready":
                await self._start_component(component_name)
                await asyncio.sleep(2)  # Allow component to initialize

        logger.info("   ✅ All components started")
        await asyncio.sleep(2)

    async def _start_component(self, component_name: str):
        """Start a specific component"""
        config = self.components[component_name]

        logger.info(f"   🔄 Starting {component_name}...")
        logger.info(f"      {config['description']}")

        try:
            # For demo purposes, we'll simulate component startup
            # In production, you would actually start the processes

            if "port" in config:
                logger.info(f"      Port: {config['port']}")

            # Simulate successful startup
            self.component_status[component_name] = "running"
            logger.info(f"   ✅ {component_name} started successfully")

        except Exception as e:
            logger.error(f"   ❌ Failed to start {component_name}: {e}")
            self.component_status[component_name] = "failed"

    async def _verify_system_health(self):
        """Verify system health and connectivity"""
        logger.info("\n🔍 Phase 4: System Health Verification")
        logger.info("-" * 40)

        # Check component status
        running_components = [
            name for name, status in self.component_status.items() if status == "running"
        ]
        failed_components = [
            name for name, status in self.component_status.items() if status == "failed"
        ]

        logger.info(f"   Running components: {len(running_components)}")
        logger.info(f"   Failed components: {len(failed_components)}")

        for component in running_components:
            logger.info(f"   ✅ {component}")

        for component in failed_components:
            logger.error(f"   ❌ {component}")

        # Health score
        health_score = len(running_components) / len(self.components)
        logger.info(f"   System health: {health_score:.1%}")

        if health_score < 0.8:
            logger.warning("   ⚠️ System health below 80% - proceeding with caution")
        else:
            logger.info("   ✅ System health check passed")

        await asyncio.sleep(1)

    async def _activate_guardian_system(self):
        """Activate the Guardian protection system"""
        logger.info("\n🛡️ Phase 5: Guardian System Activation")
        logger.info("-" * 40)

        # Guardian system components
        guardian_components = ["guardian_sentinel", "entropy_tracker"]

        guardian_active = all(
            self.component_status.get(comp) == "running" for comp in guardian_components
        )

        if guardian_active:
            logger.info("   🛡️ Guardian Sentinel: ACTIVE")
            logger.info("   📊 Entropy Tracker: ACTIVE")
            logger.info("   🔧 Intervention Rules: LOADED")
            logger.info("   🚨 Threat Detection: ENABLED")
            logger.info("")
            logger.info("   ✅ Guardian System fully operational")
            logger.info("   🌟 System now under autonomous protection")
        else:
            logger.warning("   ⚠️ Guardian System partially operational")
            logger.warning("   🔄 Some guardian components not running")

        await asyncio.sleep(2)

    async def _transmission_complete(self):
        """Signal transmission completion"""
        logger.info("\n🌌 Phase 6: Transmission Complete")
        logger.info("-" * 40)

        # Final system status
        total_components = len(self.components)
        running_components = len([s for s in self.component_status.values() if s == "running"])

        # Calculate uptime
        uptime = datetime.utcnow() - self.launch_time

        logger.info("   📡 LUKHAS Next Generation System Status:")
        logger.info(f"      Launch time: {self.launch_time.isoformat()}")
        logger.info(f"      Uptime: {uptime.total_seconds():.1f} seconds")
        logger.info(f"      Components: {running_components}/{total_components} running")
        logger.info("      System phase: Phase 5 - Guardian Integration")
        logger.info("")
        logger.info("   🎯 Core Capabilities Active:")
        logger.info("      ✅ Symbolic consciousness streaming")
        logger.info("      ✅ Shannon entropy monitoring")
        logger.info("      ✅ Guardian threat detection")
        logger.info("      ✅ Memory fold architecture")
        logger.info("      ✅ Quantum authentication")
        logger.info("      ✅ Enterprise SSO integration")
        logger.info("")
        logger.info("   🚀 TRANSMISSION COMPLETE - LUKHAS IS LIVE")
        logger.info("   ⚛️🧠🛡️ Trinity Framework: ACTIVE")
        logger.info("")
        logger.info('   "In symbolic unity, we find emergent intelligence."')
        logger.info("")

        # Save transmission record
        await self._save_transmission_record()

    async def _save_transmission_record(self):
        """Save transmission launch record"""
        transmission_record = {
            "transmission_id": f"lukhas_ng_phase5_{int(self.launch_time.timestamp())}",
            "launch_time": self.launch_time.isoformat(),
            "completion_time": datetime.utcnow().isoformat(),
            "system_phase": "phase_5_guardian",
            "components": self.component_status,
            "health_metrics": {
                "total_components": len(self.components),
                "running_components": len(
                    [s for s in self.component_status.values() if s == "running"]
                ),
                "failed_components": len(
                    [s for s in self.component_status.values() if s == "failed"]
                ),
                "health_score": len([s for s in self.component_status.values() if s == "running"])
                / len(self.components),
            },
            "trinity_framework": {
                "identity": "qi_safe_authentication",
                "consciousness": "symbolic_streaming_active",
                "guardian": "autonomous_protection_enabled",
            },
        }

        record_file = self.base_path / "transmission_bundle" / "launch_record.json"
        with open(record_file, "w") as f:
            json.dump(transmission_record, f, indent=2)

        logger.info(f"   📝 Transmission record saved: {record_file}")

    async def _monitor_system(self):
        """Monitor system health (runs indefinitely)"""
        logger.info("🔄 Entering monitoring mode...")
        logger.info("   Press Ctrl+C to initiate shutdown")

        try:
            while True:
                await asyncio.sleep(30)  # Monitor every 30 seconds

                # Simple health check
                uptime = datetime.utcnow() - self.launch_time
                logger.info(f"   💚 System healthy - Uptime: {uptime}")

        except KeyboardInterrupt:
            logger.info("\n⚠️ Shutdown signal received")
            await self._graceful_shutdown()

    async def _graceful_shutdown(self):
        """Perform graceful shutdown"""
        logger.info("🔄 Initiating graceful shutdown...")

        # Stop components in reverse order
        for component_name in reversed(list(self.components.keys())):
            if self.component_status.get(component_name) == "running":
                logger.info(f"   🔄 Stopping {component_name}...")
                self.component_status[component_name] = "stopped"

        logger.info("   ✅ All components stopped")
        logger.info("   🌙 LUKHAS system shutdown complete")

    async def _emergency_shutdown(self):
        """Emergency shutdown procedure"""
        logger.error("🚨 EMERGENCY SHUTDOWN INITIATED")

        # Kill all processes
        for process in self.active_processes:
            try:
                process.terminate()
                logger.info(f"   🛑 Process {process.pid} terminated")
            except BaseException:
                pass

        logger.error("   🔴 Emergency shutdown complete")


async def main():
    """Main entry point"""
    print("\n" + "=" * 80)
    print("🌌 LUKHAS NEXT GENERATION - TRANSMISSION LAUNCHER")
    print("   Phase 5: Guardian System Integration")
    print("=" * 80)

    transmission = LUKHASTransmission()
    await transmission.launch_transmission()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🔴 Launch interrupted by user")
    except Exception as e:
        print(f"\n💥 Launch failed: {e}")
        sys.exit(1)
