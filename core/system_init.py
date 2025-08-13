"""
LUKHAS System Initialization - Production Ready
================================================
Provides robust system initialization with proper error handling,
module loading, and health checks.
"""

import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from core.config.env_validator import validate_environment
from core.module_manager import ModulePriority, ModuleStatus, get_module_manager

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Configure logging


def setup_logging(level: str = "INFO", log_file: Optional[str] = None):
    """Configure logging for the system"""
    log_format = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"

    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        handlers=handlers,
    )

    # Suppress noisy loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    return logging.getLogger(__name__)


class LUKHASSystem:
    """
    Main system class for LUKHAS initialization and management.
    Handles all startup, shutdown, and runtime operations.
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the LUKHAS system"""
        self.config_path = config_path or "lukhas_config.yaml"
        self.logger = setup_logging()
        self.module_manager = get_module_manager()
        self.start_time = None
        self.is_initialized = False
        self.health_status = {}
        self.config = {}

    def initialize(self, priority: ModulePriority = ModulePriority.HIGH) -> bool:
        """
        Initialize the complete LUKHAS system.

        Args:
            priority: Load modules up to this priority level

        Returns:
            True if initialization successful, False otherwise
        """
        self.logger.info("=" * 70)
        self.logger.info("🧠 LUKHAS  System Initialization")
        self.logger.info("=" * 70)

        self.start_time = time.time()

        try:
            # Step 1: Validate environment
            self.logger.info("Step 1: Validating environment...")
            if not self._validate_environment():
                self.logger.error("Environment validation failed")
                return False

            # Step 2: Load configuration
            self.logger.info("Step 2: Loading configuration...")
            if not self._load_configuration():
                self.logger.warning("Configuration loading failed, using defaults")

            # Step 3: Initialize modules
            self.logger.info("Step 3: Initializing modules...")
            module_report = self._initialize_modules(priority)

            # Step 4: Run health checks
            self.logger.info("Step 4: Running health checks...")
            self.health_status = self._run_health_checks()

            # Step 5: Initialize subsystems
            self.logger.info("Step 5: Initializing subsystems...")
            self._initialize_subsystems()

            # Calculate initialization time
            init_time = time.time() - self.start_time

            # Print summary
            self._print_summary(module_report, init_time)

            self.is_initialized = True
            return True

        except Exception as e:
            self.logger.error(f"System initialization failed: {e}")
            import traceback

            traceback.print_exc()
            return False

    def _validate_environment(self) -> bool:
        """Validate environment variables"""
        try:
            # Use the env_validator but don't fail on missing optional vars
            result = validate_environment()
            if not result:
                self.logger.warning(
                    "Some environment variables missing, using defaults"
                )
            return True  # Continue even with warnings
        except Exception as e:
            self.logger.error(f"Environment validation error: {e}")
            return False

    def _load_configuration(self) -> bool:
        """Load system configuration"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                import yaml

                with open(config_file) as f:
                    self.config = yaml.safe_load(f)
                self.logger.info(f"Configuration loaded from {self.config_path}")
                return True
            else:
                self.logger.warning(f"Config file {self.config_path} not found")
                return False
        except Exception as e:
            self.logger.error(f"Configuration loading error: {e}")
            return False

    def _initialize_modules(self, priority: ModulePriority) -> dict[str, Any]:
        """Initialize all modules through module manager"""
        results = self.module_manager.load_all(priority)

        # Count results
        loaded = sum(1 for r in results.values() if r.status == ModuleStatus.LOADED)
        fallback = sum(1 for r in results.values() if r.status == ModuleStatus.FALLBACK)
        failed = sum(1 for r in results.values() if r.status == ModuleStatus.FAILED)

        self.logger.info(
            f"Modules: {loaded} loaded, {fallback} fallback, {failed} failed"
        )

        # Log critical failures
        for name, info in results.items():
            if (
                info.status == ModuleStatus.FAILED
                and info.config.priority == ModulePriority.CRITICAL
            ):
                self.logger.error(f"Critical module {name} failed: {info.error}")

        return self.module_manager.get_status_report()

    def _run_health_checks(self) -> dict[str, bool]:
        """Run health checks on all modules"""
        health_results = self.module_manager.health_check()

        # Additional system health checks
        health_results.update(
            {
                "environment": self._check_environment_health(),
                "configuration": bool(self.config),
                "filesystem": self._check_filesystem_health(),
                "memory": self._check_memory_health(),
            }
        )

        healthy = sum(1 for v in health_results.values() if v)
        total = len(health_results)

        self.logger.info(f"Health check: {healthy}/{total} components healthy")

        return health_results

    def _check_environment_health(self) -> bool:
        """Check if critical environment variables are set"""
        critical_vars = ["OPENAI_API_KEY", "LUKHAS_ID_SECRET"]
        return all(os.getenv(var) for var in critical_vars)

    def _check_filesystem_health(self) -> bool:
        """Check if critical directories exist and are writable"""
        critical_dirs = ["data", "logs", "feedback_data"]
        for dir_name in critical_dirs:
            dir_path = Path(dir_name)
            dir_path.mkdir(exist_ok=True)
            if not dir_path.is_dir() or not os.access(dir_path, os.W_OK):
                return False
        return True

    def _check_memory_health(self) -> bool:
        """Check if system has sufficient memory"""
        try:
            import psutil

            memory = psutil.virtual_memory()
            # Require at least 1GB free memory
            return memory.available > 1024 * 1024 * 1024
        except ImportError:
            # If psutil not available, assume OK
            return True

    def _initialize_subsystems(self):
        """Initialize specific subsystems that need special setup"""
        # Initialize Signal Bus if available
        signal_module = self.module_manager.get_module("signal_system")
        if signal_module:
            try:
                import asyncio

                from orchestration.signals import get_signal_bus

                # Create event loop if needed
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                get_signal_bus()
                self.logger.info("Signal bus initialized")
            except Exception as e:
                self.logger.warning(f"Signal bus initialization failed: {e}")

        # Initialize Identity System if available
        identity_module = self.module_manager.get_module("identity_system")
        if identity_module:
            try:
                from governance.identity.interface import IdentityClient

                IdentityClient()
                self.logger.info("Identity system initialized")
            except Exception as e:
                self.logger.warning(f"Identity system initialization failed: {e}")

    def _print_summary(self, module_report: dict[str, Any], init_time: float):
        """Print initialization summary"""
        print("\n" + "=" * 70)
        print("🎉 LUKHAS System Initialization Complete")
        print("=" * 70)

        # Module summary
        print("\n📦 Module Status:")
        print(f"  ✅ Loaded: {module_report.get('loaded', 0)}")
        print(f"  📦 Fallback: {module_report.get('fallback', 0)}")
        print(f"  ❌ Failed: {module_report.get('failed', 0)}")

        # Health summary
        healthy = sum(1 for v in self.health_status.values() if v)
        print(f"\n💚 Health: {healthy}/{len(self.health_status)} components healthy")

        # Critical modules
        print("\n🔑 Critical Systems:")
        critical_modules = [
            "identity_system",
            "memory_systems",
            "signal_system",
        ]
        for module in critical_modules:
            if module in module_report["modules"]:
                status = module_report["modules"][module]["status"]
                icon = "✅" if status in ["loaded", "fallback"] else "❌"
                print(f"  {icon} {module}: {status}")

        # Timing
        print(f"\n⏱️  Initialization time: {init_time:.2f} seconds")
        print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        print("\n" + "=" * 70)
        print("System ready for operation")
        print("=" * 70 + "\n")

    def shutdown(self):
        """Gracefully shutdown the system"""
        self.logger.info("Shutting down LUKHAS system...")

        # Save state if needed
        self._save_state()

        # Cleanup modules
        # (module cleanup code here if needed)

        self.is_initialized = False
        self.logger.info("Shutdown complete")

    def _save_state(self):
        """Save system state for recovery"""
        state = {
            "shutdown_time": time.time(),
            "uptime": time.time() - self.start_time if self.start_time else 0,
            "health_status": self.health_status,
            "module_status": self.module_manager.get_status_report(),
        }

        state_file = Path("data/system_state.json")
        state_file.parent.mkdir(exist_ok=True)

        with open(state_file, "w") as f:
            json.dump(state, f, indent=2)

        self.logger.info(f"System state saved to {state_file}")

    def get_status(self) -> dict[str, Any]:
        """Get current system status"""
        return {
            "initialized": self.is_initialized,
            "uptime": time.time() - self.start_time if self.start_time else 0,
            "health": self.health_status,
            "modules": self.module_manager.get_status_report(),
        }


def initialize_lukhas(priority: str = "HIGH") -> LUKHASSystem:
    """
    Convenience function to initialize LUKHAS system.

    Args:
        priority: Module loading priority ("CRITICAL", "HIGH", "MEDIUM", "LOW",
    "OPTIONAL")

    Returns:
        Initialized LUKHASSystem instance
    """
    priority_map = {
        "CRITICAL": ModulePriority.CRITICAL,
        "HIGH": ModulePriority.HIGH,
        "MEDIUM": ModulePriority.MEDIUM,
        "LOW": ModulePriority.LOW,
        "OPTIONAL": ModulePriority.OPTIONAL,
    }

    priority_enum = priority_map.get(priority.upper(), ModulePriority.HIGH)

    system = LUKHASSystem()
    success = system.initialize(priority_enum)

    if not success:
        raise RuntimeError("System initialization failed")

    return system


# Context manager for system lifecycle


class LUKHASContext:
    """Context manager for LUKHAS system lifecycle"""

    def __init__(self, priority: str = "HIGH"):
        self.priority = priority
        self.system = None

    def __enter__(self) -> LUKHASSystem:
        self.system = initialize_lukhas(self.priority)
        return self.system

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.system:
            self.system.shutdown()


# Main entry point


def main():
    """Main entry point for system initialization"""
    import argparse

    parser = argparse.ArgumentParser(description="Initialize LUKHAS  System")
    parser.add_argument(
        "--priority",
        choices=["CRITICAL", "HIGH", "MEDIUM", "LOW", "OPTIONAL"],
        default="HIGH",
        help="Module loading priority level",
    )
    parser.add_argument(
        "--config",
        default="lukhas_config.yaml",
        help="Path to configuration file",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level)

    # Initialize system
    with LUKHASContext(args.priority):
        print("\n✨ LUKHAS system is running. Press Ctrl+C to shutdown.\n")
        try:
            # Keep system running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n👋 Shutting down...")


if __name__ == "__main__":
    main()
