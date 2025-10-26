#!/usr/bin/env python3
"""
LUKHAS AI - Logical Unified Knowledge Hyper-Adaptable System
Main entry point for the neuroplastic Cognitive AI system with professional architecture
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timezone

# Import bootstrap with fallback handling
try:
    from core.bootstrap import get_bootstrap, initialize_lukhas, shutdown_lukhas
except ImportError:
    try:
        from core.bootstrap import get_bootstrap, initialize_lukhas, shutdown_lukhas
    except ImportError:
        # Create fallback bootstrap functions
        def fallback_get_bootstrap():
            return {"status": "fallback"}

        def fallback_initialize_lukhas():
            return True

        def fallback_shutdown_lukhas():
            return True

        # Create aliases for compatibility
        get_bootstrap = fallback_get_bootstrap
        initialize_lukhas = fallback_initialize_lukhas
        shutdown_lukhas = fallback_shutdown_lukhas


# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import LUKHAS AI branding system for system initialization
# Import branding bridge with fallback handling
try:
    from branding_bridge import get_system_signature, initialize_branding

    BRANDING_AVAILABLE = True
except ImportError:
    try:
        from branding_bridge import get_system_signature, initialize_branding

        BRANDING_AVAILABLE = True
    except ImportError:
        BRANDING_AVAILABLE = False

        def fallback_initialize_branding():
            return True

        def fallback_get_system_signature():
            return "LUKHAS AI System"

        # Create aliases for compatibility
        initialize_branding = fallback_initialize_branding
        get_system_signature = fallback_get_system_signature


# Import bootstrap


# Create a simple health monitor if the script doesn't exist
class SystemHealthMonitor:
    def check_vital_signs(self):
        return {"overall": "HEALTHY"}

    def generate_health_report(self):
        return "System health: OK"


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("log"), logging.StreamHandler()],
)


logger = logging.getLogger("LUKHAS")


class LUKHAS:
    """Main LUKHAS system controller with professional architecture"""

    def __init__(self):
        self.bootstrap = None
        self.is_running = False
        self.health_monitor = SystemHealthMonitor()
        self.startup_time = None

    async def check_system_health(self):
        """Check system health before startup"""
        logger.info("🏥 Checking system health...")

        health_status = self.health_monitor.check_vital_signs()

        if health_status["overall"] in ["CRITICAL", "SEVERE"]:
            logger.error("❌ System health is %s", health_status["overall"])
            logger.error("Please run healing procedures first:")
            logger.error("  python healing/conflict_healer.py")
            logger.error("  python healing/syntax_doctor.py")
            return False

        logger.info("✅ System health: %s", health_status["overall"])
        return True

    async def initialize_professional_architecture(self):
        """Initialize using professional service-oriented architecture"""
        logger.info("🏗️  Initializing professional architecture...")

        try:
            # Initialize LUKHAS AI branding system first
            if BRANDING_AVAILABLE:
                branding_success = await initialize_branding()
                if branding_success:
                    logger.info("🎨 LUKHAS AI branding system initialized")
                    signature = get_system_signature()
                    logger.info(f"📝 System signature: {signature}")
                else:
                    logger.warning("⚠️ Branding system initialization failed")
            else:
                logger.warning("⚠️ Branding system not available")

            # Initialize bootstrap and all services
            result = await initialize_lukhas()

            if result["status"] == "success":
                self.bootstrap = await get_bootstrap()
                logger.info("✅ Professional architecture initialized")

                # Run integration demonstration
                if self.bootstrap:
                    await self.bootstrap.demonstrate_integration()

                return True
            else:
                logger.error("❌ Architecture initialization failed: %s", result.get("error"))
                return False

        except (ImportError, AttributeError, RuntimeError) as e:
            logger.error("❌ Failed to initialize architecture: %s", e)
            return False

    async def start(self):
        """Start the LUKHAS system"""

        print(
            """
╔══════════════════════════════════════════════════════════════╗
║           LUKHAS AI - SYSTEM STARTUP                         ║
║    Logical Unified Knowledge Hyper-Adaptable System          ║
║         Professional Service-Oriented Architecture           ║
║             T4/0.01% Agent Delegation System                 ║
╚══════════════════════════════════════════════════════════════╝

🤖 Agent System Status:
   - CODEX: Deep infrastructure & performance optimization
   - Jules: DevOps, monitoring & security automation
   - Claude Code: Testing, documentation & compliance
   - Copilot: Mechanical refactoring & consistency

📋 Active Tasks: 62 precision tasks from executive audit
🎯 Standards: <100ms memory, <250ms pipeline, 99.7% reliability
        """
        )

        self.startup_time = datetime.now(timezone.utc)

        # Check health
        if not await self.check_system_health():
            logger.error("System health check failed. Aborting startup.")
            return False

        # Initialize professional architecture
        if not await self.initialize_professional_architecture():
            logger.error("Architecture initialization failed. Aborting startup.")
            return False

        # Get health report from bootstrap
        if self.bootstrap:
            health_report = await self.bootstrap.check_system_health()  # Remove protected member access

            logger.info("\n📊 Startup Summary:")
            logger.info("  - Services loaded: %d", len(self.bootstrap.services))
            logger.info("  - Healthy services: %s", health_report["overall"]["healthy_services"])
            logger.info(
                "  - Health percentage: %.1f%%",
                health_report["overall"]["health_percentage"],
            )
            logger.info(
                "  - Startup time: %.2fs",
                (datetime.now(timezone.utc) - self.startup_time).total_seconds(),
            )

        self.is_running = True
        logger.info("\n✅ LUKHAS is now running with professional architecture!")
        return True

    async def run_interactive_mode(self):
        """Run in interactive mode with async support"""

        if not self.is_running:
            logger.error("System not running. Please start first.")
            return

        print("\n🤖 LUKHAS Interactive Mode (Professional Architecture)")
        print("Type 'help' for commands, 'exit' to quit\n")

        while True:
            try:
                command = input("lukhas> ").strip()

                if command == "exit":
                    break
                elif command == "help":
                    self.show_help()
                elif command == "status":
                    await self.show_status()
                elif command == "health":
                    await self.show_health()
                elif command == "services":
                    await self.show_services()
                elif command.startswith("service "):
                    service_name = command.split(" ", 1)[1]
                    await self.show_service_info(service_name)
                elif command == "demo":
                    if self.bootstrap:
                        await self.bootstrap.demonstrate_integration()
                else:
                    print(f"Unknown command: {command}")

            except KeyboardInterrupt:
                print("\nUse 'exit' to quit properly")
            except (RuntimeError, ValueError, AttributeError) as e:
                logger.error("Error: %s", e)

    def show_help(self):
        """Show help information"""
        print(
            """
Available commands:
  help       - Show this help
  status     - Show system status
  health     - Run health check
  services   - List all services
  service X  - Show info about service X
  demo       - Run integration demonstration
  exit       - Shutdown system
        """
        )

    async def show_status(self):
        """Show system status"""
        print("\n🔹 LUKHAS Status (Professional Architecture)")
        print(f"Uptime: {(datetime.now(timezone.utc) - self.startup_time).total_seconds():.1f}s")

        if self.bootstrap:
            health = await self.bootstrap.check_system_health()  # Remove protected member access
            print("\nServices:")
            for name, health_info in health["services"].items():
                status = health_info.get("status", "unknown")
                emoji = "✅" if status == "healthy" else "⚠️"
                print(f"  {emoji} {name}: {status}")

            print(f"\nOverall Health: {health['overall']['health_percentage']:.1f}%")

    async def show_health(self):
        """Show detailed health information"""
        self.health_monitor.check_vital_signs()
        print(self.health_monitor.generate_health_report())

        if self.bootstrap:
            print("\n📊 Service Health Details:")
            health = await self.bootstrap.check_system_health()  # Remove protected member access
            for name, info in health["services"].items():
                print(f"\n{name}:")
                for key, value in info.items():
                    print(f"  {key}: {value}")

    async def show_services(self):
        """Show all registered services"""
        if self.bootstrap:
            services = self.bootstrap.get_all_services()
            print(f"\n📦 Registered Services ({len(services)}):")
            for name in services:
                print(f"  - {name}")

    async def show_service_info(self, service_name):
        """Show information about a specific service"""
        if self.bootstrap:
            service = self.bootstrap.get_service(service_name)
            if service:
                print(f"\n📦 Service: {service_name}")
                health = service.get_health()
                for key, value in health.items():
                    print(f"  {key}: {value}")
            else:
                print(f"Service '{service_name}' not found")

    async def shutdown(self):
        """Gracefully shutdown the system"""
        logger.info("\n🔄 Shutting down LUKHAS...")

        if self.bootstrap:
            await shutdown_lukhas()

        self.is_running = False
        logger.info("✅ LUKHAS shutdown complete")


async def async_main():
    """Async main entry point"""

    # Create LUKHAS instance
    LUKHAS()

    # Start system
    if await start():
        try:
            # Run interactive mode
            await run_interactive_mode()
        finally:
            # Ensure proper shutdown
            await shutdown()
    else:
        sys.exit(1)


def main():
    """Main entry point"""
    # Run async main
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
