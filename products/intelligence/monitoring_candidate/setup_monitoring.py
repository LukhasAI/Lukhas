#!/usr/bin/env python3
"""
Setup script for LUKHAS  monitoring infrastructure
Configures and starts all monitoring components
"""
import argparse
import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class MonitoringSetup:
    """Setup and manage monitoring infrastructure"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path) if config_path else Path("monitoring_config.yaml")
        self.services = {}
        self.base_dir = Path(__file__).parent

    def load_config(self) -> dict[str, Any]:
        """Load monitoring configuration"""
        default_config = {
            "unified_dashboard": {
                "enabled": True,
                "host": "0.0.0.0",
                "port": 3000,
                "refresh_rate": 5,
            },
            "meta_dashboard": {"enabled": True, "port": 5042},
            "metrics_collection": {
                "enabled": True,
                "interval": 1,
                "retention_hours": 24,
            },
            "alerting": {
                "enabled": True,
                "thresholds": {
                    "drift_critical": 0.8,
                    "memory_usage_high": 85.0,
                    "response_time_slow": 1000,
                    "error_rate_high": 0.05,
                },
            },
            "integrations": {
                "prometheus": False,
                "grafana": False,
                "slack_webhooks": False,
            },
        }

        if self.config_path.exists():
            import yaml

            with open(self.config_path) as f:
                user_config = yaml.safe_load(f)
                # Merge with defaults
                for key, value in user_config.items():
                    if isinstance(value, dict) and key in default_config:
                        default_config[key].update(value)
                    else:
                        default_config[key] = value
        else:
            self.save_default_config(default_config)

        return default_config

    def save_default_config(self, config: dict[str, Any]):
        """Save default configuration file"""
        import yaml

        logger.info(f"Creating default config at {self.config_path}")
        with open(self.config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False)

    def check_dependencies(self) -> bool:
        """Check if all required dependencies are installed"""
        required_packages = ["fastapi", "uvicorn", "websockets", "psutil", "pyyaml"]

        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            logger.error(f"Missing required packages: {', '.join(missing_packages)}")
            logger.info(f"Install with: pip install {' '.join(missing_packages)}")
            return False

        logger.info("✅ All dependencies satisfied")
        return True

    def setup_data_directories(self):
        """Create necessary data directories"""
        directories = ["data", "logs", "config", "templates", "static"]

        for dir_name in directories:
            dir_path = self.base_dir / dir_name
            dir_path.mkdir(exist_ok=True)
            logger.info(f"📁 Created directory: {dir_path}")

    def start_unified_dashboard(self, config: dict[str, Any]):
        """Start the unified monitoring dashboard"""
        if not config["unified_dashboard"]["enabled"]:
            logger.info("🔴 Unified dashboard disabled in config")
            return

        logger.info("🚀 Starting Unified Dashboard...")

        dashboard_config = config["unified_dashboard"]

        # Import and start dashboard
        try:
            from .unified_dashboard import start_dashboard

            # Start in background process for production
            if config.get("production", False):
                cmd = [
                    sys.executable,
                    str(self.base_dir / "unified_dashboard.py"),
                    "--host",
                    dashboard_config["host"],
                    "--port",
                    str(dashboard_config["port"]),
                ]

                process = subprocess.Popen(cmd)
                self.services["unified_dashboard"] = process
                logger.info(f"✅ Unified Dashboard started (PID: {process.pid})")
            else:
                # Start directly for development
                start_dashboard(
                    host=dashboard_config["host"],
                    port=dashboard_config["port"],
                    dev=True,
                )

        except Exception as e:
            logger.error(f"❌ Failed to start Unified Dashboard: {e}")

    def start_meta_dashboard(self, config: dict[str, Any]):
        """Start the meta/symbolic dashboard"""
        if not config["meta_dashboard"]["enabled"]:
            logger.info("🔴 Meta dashboard disabled in config")
            return

        logger.info("🚀 Starting Meta Dashboard...")

        try:
            # Check if meta dashboard exists
            meta_dashboard_path = self.base_dir.parent / "meta_dashboard" / "dashboard_server.py"

            if meta_dashboard_path.exists():
                cmd = [sys.executable, str(meta_dashboard_path)]
                process = subprocess.Popen(cmd)
                self.services["meta_dashboard"] = process
                logger.info(f"✅ Meta Dashboard started (PID: {process.pid})")
            else:
                logger.warning("⚠️ Meta dashboard not found, skipping")

        except Exception as e:
            logger.error(f"❌ Failed to start Meta Dashboard: {e}")

    def setup_prometheus_integration(self, config: dict[str, Any]):
        """Setup Prometheus metrics export"""
        if not config["integrations"]["prometheus"]:
            return

        logger.info("📊 Setting up Prometheus integration...")

        # Create prometheus config
        prometheus_config = {
            "global": {"scrape_interval": "15s"},
            "scrape_configs": [
                {
                    "job_name": "lukhas-",
                    "static_configs": [{"targets": [f"localhost:{config['unified_dashboard']['port']}"]}],
                    "metrics_path": "/metrics",
                }
            ],
        }

        # Save prometheus config
        import yaml

        config_dir = self.base_dir / "config"
        with open(config_dir / "prometheus.yml", "w") as f:
            yaml.dump(prometheus_config, f)

        logger.info("✅ Prometheus configuration created")

    def create_monitoring_scripts(self):
        """Create utility scripts for monitoring"""
        scripts = {
            "start_monitoring.sh": """#!/bin/bash
# Start all LUKHAS  monitoring services
echo "🚀 Starting LUKHAS  Monitoring..."
python3 monitoring/setup_monitoring.py --start-all
""",
            "stop_monitoring.sh": """#!/bin/bash
# Stop all monitoring services
echo "🛑 Stopping LUKHAS  Monitoring..."
pkill -f "unified_dashboard"
pkill -f "meta_dashboard"
pkill -f "prometheus"
echo "✅ All monitoring services stopped"
""",
            "monitoring_status.py": """#!/usr/bin/env python3
import requests
import json

def check_service_status():
    services = {
        "Unified Dashboard": "http://localhost:3000/health",
        "Meta Dashboard": "http://localhost:5042/api/health"
    }

    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: Online")
            else:
                print(f"⚠️ {name}: Issues (HTTP {response.status_code})")
        except:
            print(f"❌ {name}: Offline")

if __name__ == "__main__":
    check_service_status()
""",
        }

        scripts_dir = self.base_dir / "scripts"
        scripts_dir.mkdir(exist_ok=True)

        for filename, content in scripts.items():
            script_path = scripts_dir / filename
            with open(script_path, "w") as f:
                f.write(content)

            # Make shell scripts executable
            if filename.endswith(".sh"):
                script_path.chmod(0o755)

            logger.info(f"📝 Created script: {script_path}")

    def create_systemd_services(self, config: dict[str, Any]):
        """Create systemd service files for production deployment"""
        services = {
            "lukhas--dashboard": {
                "description": "LUKHAS  Unified Dashboard",
                "command": f"{sys.executable} {self.base_dir}/unified_dashboard.py",
                "port": config["unified_dashboard"]["port"],
            }
        }

        systemd_dir = self.base_dir / "systemd"
        systemd_dir.mkdir(exist_ok=True)

        for service_name, service_config in services.items():
            service_content = f"""[Unit]
Description={service_config["description"]}
After=network.target

[Service]
Type=simple
User=lukhas
WorkingDirectory={self.base_dir.parent}
Environment=PATH={sys.executable.rsplit("/", 1)[0]}
Environment=PYTHONPATH={self.base_dir.parent}
ExecStart={service_config["command"]}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

            service_file = systemd_dir / f"{service_name}.service"
            with open(service_file, "w") as f:
                f.write(service_content)

            logger.info(f"🔧 Created systemd service: {service_file}")

        # Instructions
        logger.info("📋 To install systemd services:")
        logger.info(f"   sudo cp {systemd_dir}/*.service /etc/systemd/system/")
        logger.info("   sudo systemctl daemon-reload")
        logger.info("   sudo systemctl enable lukhas--dashboard")
        logger.info("   sudo systemctl start lukhas--dashboard")

    def run_setup(self, args):
        """Run the complete setup process"""
        logger.info("🔧 Starting LUKHAS  Monitoring Setup...")

        # Check dependencies
        if not self.check_dependencies():
            sys.exit(1)

        # Load configuration
        config = self.load_config()
        logger.info(f"📋 Configuration loaded from {self.config_path}")

        # Setup directories
        self.setup_data_directories()

        # Create utility scripts
        if args.create_scripts:
            self.create_monitoring_scripts()

        # Create systemd services
        if args.create_systemd:
            self.create_systemd_services(config)

        # Setup integrations
        if config["integrations"]["prometheus"]:
            self.setup_prometheus_integration(config)

        # Start services
        if args.start_all or args.start_unified:
            self.start_unified_dashboard(config)

        if args.start_all or args.start_meta:
            self.start_meta_dashboard(config)

        logger.info("✅ LUKHAS  Monitoring Setup Complete!")

        if self.services:
            logger.info("🚀 Running services:")
            for name, process in self.services.items():
                logger.info(f"   - {name} (PID: {process.pid})")

            # Wait for services
            if args.wait:
                try:
                    logger.info("⏳ Monitoring services... (Ctrl+C to stop)")
                    while True:
                        time.sleep(5)
                        # Check service health
                        for name, process in list(self.services.items()):
                            if process.poll() is not None:
                                logger.error(f"❌ Service {name} stopped unexpectedly")
                                del self.services[name]
                except KeyboardInterrupt:
                    logger.info("\n🛑 Shutting down services...")
                    for process in self.services.values():
                        process.terminate()


def main():
    parser = argparse.ArgumentParser(description="Setup LUKHAS  monitoring infrastructure")

    parser.add_argument(
        "--config",
        "-c",
        help="Path to configuration file",
        default="monitoring_config.yaml",
    )

    parser.add_argument("--start-all", action="store_true", help="Start all monitoring services")

    parser.add_argument("--start-unified", action="store_true", help="Start unified dashboard only")

    parser.add_argument("--start-meta", action="store_true", help="Start meta dashboard only")

    parser.add_argument(
        "--create-scripts",
        action="store_true",
        help="Create monitoring utility scripts",
    )

    parser.add_argument("--create-systemd", action="store_true", help="Create systemd service files")

    parser.add_argument("--wait", action="store_true", help="Wait and monitor running services")

    args = parser.parse_args()

    # Setup monitoring
    setup = MonitoringSetup(args.config)
    setup.run_setup(args)


if __name__ == "__main__":
    main()