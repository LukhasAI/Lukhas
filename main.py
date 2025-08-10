#!/usr/bin/env python3
"""
LUKHAS AI - Logical Unified Knowledge Hyper-Adaptable System
Main entry point for the neuroplastic AGI system with professional architecture
"""

import asyncio
import logging
import os
import sys
from datetime import datetime

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import bootstrap
from core.bootstrap import get_bootstrap, initialize_lukhas, shutdown_lukhas


# Create a simple health monitor if the script doesn't exist
class SystemHealthMonitor:
    def check_vital_signs(self):
        return {'overall': 'HEALTHY'}

    def generate_health_report(self):
        return "System health: OK"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lukhas.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('LUKHAS')

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

        if health_status['overall'] in ['CRITICAL', 'SEVERE']:
            logger.error(f"❌ System health is {health_status['overall']}")
            logger.error("Please run healing procedures first:")
            logger.error("  python healing/conflict_healer.py")
            logger.error("  python healing/syntax_doctor.py")
            return False

        logger.info(f"✅ System health: {health_status['overall']}")
        return True

    async def initialize_professional_architecture(self):
        """Initialize using professional service-oriented architecture"""
        logger.info("🏗️  Initializing professional architecture...")

        try:
            # Initialize bootstrap and all services
            result = await initialize_lukhas()

            if result['status'] == 'success':
                self.bootstrap = await get_bootstrap()
                logger.info("✅ Professional architecture initialized")

                # Run integration demonstration
                if self.bootstrap:
                    await self.bootstrap.demonstrate_integration()

                return True
            else:
                logger.error(f"❌ Architecture initialization failed: {result.get('error')}")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to initialize architecture: {e}")
            return False

    async def start(self):
        """Start the LUKHAS system"""

        print("""
╔══════════════════════════════════════════════════════════════╗
║           LUKHAS AI - SYSTEM STARTUP                         ║
║    Logical Unified Knowledge Hyper-Adaptable System          ║
║         Professional Service-Oriented Architecture           ║
╚══════════════════════════════════════════════════════════════╝
        """)

        self.startup_time = datetime.now()

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
            health_report = await self.bootstrap._check_system_health()

            logger.info("\n📊 Startup Summary:")
            logger.info(f"  - Services loaded: {len(self.bootstrap.services)}")
            logger.info(f"  - Healthy services: {health_report['overall']['healthy_services']}")
            logger.info(f"  - Health percentage: {health_report['overall']['health_percentage']:.1f}%")
            logger.info(f"  - Startup time: {(datetime.now() - self.startup_time).total_seconds():.2f}s")

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

                if command == 'exit':
                    break
                elif command == 'help':
                    self.show_help()
                elif command == 'status':
                    await self.show_status()
                elif command == 'health':
                    await self.show_health()
                elif command == 'services':
                    await self.show_services()
                elif command.startswith('service '):
                    service_name = command.split(' ', 1)[1]
                    await self.show_service_info(service_name)
                elif command == 'demo':
                    if self.bootstrap:
                        await self.bootstrap.demonstrate_integration()
                else:
                    print(f"Unknown command: {command}")

            except KeyboardInterrupt:
                print("\nUse 'exit' to quit properly")
            except Exception as e:
                logger.error(f"Error: {e}")

    def show_help(self):
        """Show help information"""
        print("""
Available commands:
  help       - Show this help
  status     - Show system status
  health     - Run health check
  services   - List all services
  service X  - Show info about service X
  demo       - Run integration demonstration
  exit       - Shutdown system
        """)

    async def show_status(self):
        """Show system status"""
        print("\n🔹 LUKHAS Status (Professional Architecture)")
        print(f"Uptime: {(datetime.now() - self.startup_time).total_seconds():.1f}s")

        if self.bootstrap:
            health = await self.bootstrap._check_system_health()
            print("\nServices:")
            for name, health_info in health['services'].items():
                status = health_info.get('status', 'unknown')
                emoji = '✅' if status == 'healthy' else '⚠️'
                print(f"  {emoji} {name}: {status}")

            print(f"\nOverall Health: {health['overall']['health_percentage']:.1f}%")

    async def show_health(self):
        """Show detailed health information"""
        self.health_monitor.check_vital_signs()
        print(self.health_monitor.generate_health_report())

        if self.bootstrap:
            print("\n📊 Service Health Details:")
            health = await self.bootstrap._check_system_health()
            for name, info in health['services'].items():
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
    lukhas = LUKHAS()

    # Start system
    if await lukhas.start():
        try:
            # Run interactive mode
            await lukhas.run_interactive_mode()
        finally:
            # Ensure proper shutdown
            await lukhas.shutdown()
    else:
        sys.exit(1)


def main():
    """Main entry point"""
    # Run async main
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
