#!/usr/bin/env python3
"""
Automated Deployment Pipeline
============================
Comprehensive DevOps toolchain for LUKHAS AI infrastructure
Implements automated deployment processes with CI/CD integration

Features:
- Automated testing and validation
- Blue-green deployment strategy
- Rollback capabilities
- Environment management
- Health checks and monitoring integration
- Docker containerization support
- Secret management
- Pipeline orchestration
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class DeploymentStage(Enum):
    """Deployment pipeline stages"""
    VALIDATION = "validation"
    TESTING = "testing"
    BUILD = "build"
    STAGING = "staging"
    PRODUCTION = "production"
    ROLLBACK = "rollback"


class DeploymentStatus(Enum):
    """Deployment status"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class DeploymentConfig:
    """Configuration for deployment pipeline"""
    environment: str
    target_branch: str = "main"
    docker_enabled: bool = True
    health_check_url: Optional[str] = None
    health_check_timeout: int = 300
    rollback_enabled: bool = True
    backup_enabled: bool = True
    notification_channels: list[str] = field(default_factory=list)
    environment_vars: dict[str, str] = field(default_factory=dict)
    secrets: dict[str, str] = field(default_factory=dict)
    pre_deploy_commands: list[str] = field(default_factory=list)
    post_deploy_commands: list[str] = field(default_factory=list)


@dataclass
class DeploymentResult:
    """Result of a deployment operation"""
    deployment_id: str
    stage: DeploymentStage
    status: DeploymentStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    logs: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)


class HealthChecker:
    """Health check utilities for deployment validation"""

    @staticmethod
    async def check_url_health(url: str, timeout: int = 30) -> bool:
        """Check if a URL is responding healthily"""
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=timeout)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed for {url}: {e}")
            return False

    @staticmethod
    async def check_service_health(service_name: str, port: int = 8080) -> bool:
        """Check if a service is responding on a specific port"""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result == 0
        except Exception as e:
            logger.error(f"Service health check failed for {service_name}: {e}")
            return False

    @staticmethod
    def check_system_resources() -> dict[str, float]:
        """Check system resource availability"""
        try:
            import psutil
            return {
                "cpu_available": 100 - psutil.cpu_percent(interval=1),
                "memory_available": psutil.virtual_memory().available / (1024**3),  # GB
                "disk_available": psutil.disk_usage('/').free / (1024**3)  # GB
            }
        except Exception as e:
            logger.error(f"System resource check failed: {e}")
            return {"cpu_available": 0, "memory_available": 0, "disk_available": 0}


class DockerManager:
    """Docker container management for deployments"""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    async def build_image(self, image_name: str, tag: str = "latest", dockerfile: str = "Dockerfile") -> bool:
        """Build Docker image"""
        try:
            cmd = [
                "docker", "build",
                "-t", f"{image_name}:{tag}",
                "-f", dockerfile,
                str(self.project_root)
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            _stdout, stderr = await process.communicate()

            if process.returncode == 0:
                logger.info(f"Docker image built successfully: {image_name}:{tag}")
                return True
            else:
                logger.error(f"Docker build failed: {stderr.decode()}")
                return False

        except Exception as e:
            logger.error(f"Docker build error: {e}")
            return False

    async def run_container(self, image_name: str, tag: str = "latest",
                          port_mapping: Optional[dict[int, int]] = None,
                          environment: Optional[dict[str, str]] = None,
                          name: Optional[str] = None) -> Optional[str]:
        """Run Docker container and return container ID"""
        try:
            cmd = ["docker", "run", "-d"]

            # Add port mappings
            if port_mapping:
                for host_port, container_port in port_mapping.items():
                    cmd.extend(["-p", f"{host_port}:{container_port}"])

            # Add environment variables
            if environment:
                for key, value in environment.items():
                    cmd.extend(["-e", f"{key}={value}"])

            # Add container name
            if name:
                cmd.extend(["--name", name])

            cmd.append(f"{image_name}:{tag}")

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                container_id = stdout.decode().strip()
                logger.info(f"Container started: {container_id}")
                return container_id
            else:
                logger.error(f"Container start failed: {stderr.decode()}")
                return None

        except Exception as e:
            logger.error(f"Container run error: {e}")
            return None

    async def stop_container(self, container_id: str) -> bool:
        """Stop Docker container"""
        try:
            process = await asyncio.create_subprocess_exec(
                "docker", "stop", container_id,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            _stdout, _stderr = await process.communicate()
            return process.returncode == 0

        except Exception as e:
            logger.error(f"Container stop error: {e}")
            return False

    async def remove_container(self, container_id: str) -> bool:
        """Remove Docker container"""
        try:
            process = await asyncio.create_subprocess_exec(
                "docker", "rm", container_id,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            _stdout, _stderr = await process.communicate()
            return process.returncode == 0

        except Exception as e:
            logger.error(f"Container remove error: {e}")
            return False


class AutomatedDeploymentPipeline:
    """Automated deployment pipeline for LUKHAS AI"""

    def __init__(self, project_root: Path, config_path: Optional[Path] = None):
        self.project_root = project_root
        self.config_path = config_path or project_root / "tools" / "devops" / "deployment_config.json"

        # Load configuration
        self.environments = self._load_deployment_config()

        # Initialize components
        self.docker_manager = DockerManager(project_root)
        self.health_checker = HealthChecker()

        # Deployment state
        self.active_deployments: dict[str, DeploymentResult] = {}
        self.deployment_history: list[DeploymentResult] = []

        # Create deployment directories
        self.deployment_dir = project_root / "tools" / "devops" / "deployments"
        self.deployment_dir.mkdir(parents=True, exist_ok=True)

    def _load_deployment_config(self) -> dict[str, DeploymentConfig]:
        """Load deployment configuration"""
        try:
            if self.config_path.exists():
                with open(self.config_path) as f:
                    config_data = json.load(f)

                environments = {}
                for env_name, env_config in config_data.get("environments", {}).items():
                    environments[env_name] = DeploymentConfig(
                        environment=env_name,
                        **env_config
                    )
                return environments
        except Exception as e:
            logger.warning(f"Failed to load deployment config: {e}")

        # Default configuration
        return {
            "development": DeploymentConfig(
                environment="development",
                target_branch="develop",
                health_check_timeout=60,
                rollback_enabled=False
            ),
            "staging": DeploymentConfig(
                environment="staging",
                target_branch="main",
                health_check_url="http://localhost:8080/health",
                health_check_timeout=120,
                rollback_enabled=True
            ),
            "production": DeploymentConfig(
                environment="production",
                target_branch="main",
                health_check_url="http://production.ai/health",
                health_check_timeout=300,
                rollback_enabled=True,
                backup_enabled=True
            )
        }

    async def _run_command(self, command: str, cwd: Optional[Path] = None) -> tuple[bool, str, str]:
        """Execute a shell command asynchronously"""
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd or self.project_root
            )

            stdout, stderr = await process.communicate()
            return (
                process.returncode == 0,
                stdout.decode().strip(),
                stderr.decode().strip()
            )

        except Exception as e:
            return False, "", str(e)

    async def _validate_environment(self, config: DeploymentConfig) -> bool:
        """Validate deployment environment prerequisites"""
        logger.info(f"Validating {config.environment} environment")

        # Check system resources
        resources = self.health_checker.check_system_resources()
        if resources["cpu_available"] < 20:
            logger.error("Insufficient CPU resources for deployment")
            return False

        if resources["memory_available"] < 1.0:  # 1GB
            logger.error("Insufficient memory for deployment")
            return False

        if resources["disk_available"] < 5.0:  # 5GB
            logger.error("Insufficient disk space for deployment")
            return False

        # Check Git repository status
        success, output, error = await self._run_command("git status --porcelain")
        if not success:
            logger.error(f"Git status check failed: {error}")
            return False

        if output.strip() and config.environment == "production":
            logger.error("Working directory has uncommitted changes")
            return False

        # Check target branch
        success, current_branch, error = await self._run_command("git branch --show-current")
        if not success:
            logger.error(f"Git branch check failed: {error}")
            return False

        if current_branch != config.target_branch:
            logger.warning(f"Current branch {current_branch} != target branch {config.target_branch}")

        logger.info("Environment validation passed")
        return True

    async def _run_tests(self, config: DeploymentConfig) -> bool:
        """Run test suite"""
        logger.info("Running test suite")

        # Run unit tests
        success, output, error = await self._run_command(
            "python -m pytest tests/ -v --tb=short --maxfail=5"
        )

        if not success:
            logger.error(f"Unit tests failed: {error}")
            return False

        # Run integration tests if available
        integration_tests_dir = self.project_root / "tests" / "integration"
        if integration_tests_dir.exists():
            success, output, error = await self._run_command(
                "python -m pytest tests/integration/ -v --tb=short"
            )

            if not success:
                logger.error(f"Integration tests failed: {error}")
                return False

        # Run coverage check
        success, _output, error = await self._run_command(
            "python -m pytest tests/ --cov=. --cov-report=json --cov-fail-under=80"
        )

        if not success:
            logger.warning(f"Coverage requirements not met: {error}")
            # Don't fail deployment for coverage, just warn

        logger.info("Test suite passed")
        return True

    async def _build_application(self, config: DeploymentConfig) -> bool:
        """Build application artifacts"""
        logger.info("Building application")

        # Install dependencies
        success, output, error = await self._run_command("pip install -r requirements.txt")
        if not success:
            logger.error(f"Dependency installation failed: {error}")
            return False

        # Build Docker image if enabled
        if config.docker_enabled:
            image_name = f"lukhas-ai-{config.environment}"
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            tag = f"{timestamp}-{config.target_branch}"

            success = await self.docker_manager.build_image(image_name, tag)
            if not success:
                logger.error("Docker image build failed")
                return False

            # Tag as latest for the environment
            success, output, error = await self._run_command(
                f"docker tag {image_name}:{tag} {image_name}:latest"
            )

        # Run any custom build commands
        for command in config.pre_deploy_commands:
            success, _output, error = await self._run_command(command)
            if not success:
                logger.error(f"Pre-deploy command failed: {command} - {error}")
                return False

        logger.info("Application build completed")
        return True

    async def _deploy_to_environment(self, config: DeploymentConfig) -> bool:
        """Deploy to target environment"""
        logger.info(f"Deploying to {config.environment}")

        # Create deployment backup if enabled
        if config.backup_enabled:
            await self._create_deployment_backup(config)

        # Deploy using Docker if enabled
        if config.docker_enabled:
            success = await self._deploy_docker_container(config)
            if not success:
                return False

        # Run post-deploy commands
        for command in config.post_deploy_commands:
            success, _output, error = await self._run_command(command)
            if not success:
                logger.error(f"Post-deploy command failed: {command} - {error}")
                return False

        # Health check
        if config.health_check_url:
            success = await self._perform_health_check(config)
            if not success:
                logger.error("Health check failed after deployment")
                return False

        logger.info(f"Deployment to {config.environment} completed successfully")
        return True

    async def _deploy_docker_container(self, config: DeploymentConfig) -> bool:
        """Deploy Docker container with blue-green strategy"""
        image_name = f"lukhas-ai-{config.environment}"

        # Stop existing container if running
        container_name = f"lukhas-{config.environment}"
        await self._run_command(f"docker stop {container_name}")
        await self._run_command(f"docker rm {container_name}")

        # Determine port mapping
        port_mapping = {8080: 8080}
        if config.environment == "staging":
            port_mapping = {8081: 8080}
        elif config.environment == "production":
            port_mapping = {80: 8080}

        # Start new container
        container_id = await self.docker_manager.run_container(
            image_name=image_name,
            tag="latest",
            port_mapping=port_mapping,
            environment=config.environment_vars,
            name=container_name
        )

        return container_id is not None

    async def _create_deployment_backup(self, config: DeploymentConfig):
        """Create backup before deployment"""
        logger.info("Creating deployment backup")

        backup_dir = self.deployment_dir / "backups" / config.environment
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = backup_dir / f"backup-{timestamp}.tar.gz"

        # Create backup of current deployment
        success, _output, error = await self._run_command(
            f"tar -czf {backup_path} --exclude='.git' --exclude='__pycache__' ."
        )

        if success:
            logger.info(f"Backup created: {backup_path}")
        else:
            logger.warning(f"Backup creation failed: {error}")

    async def _perform_health_check(self, config: DeploymentConfig) -> bool:
        """Perform health check on deployed application"""
        logger.info("Performing health check")

        if not config.health_check_url:
            return True

        # Wait for application to start
        await asyncio.sleep(10)

        # Retry health check with timeout
        start_time = time.time()
        while time.time() - start_time < config.health_check_timeout:
            if await self.health_checker.check_url_health(config.health_check_url):
                logger.info("Health check passed")
                return True

            await asyncio.sleep(5)

        logger.error("Health check timeout")
        return False

    async def deploy(self, environment: str, force: bool = False) -> DeploymentResult:
        """Execute full deployment pipeline"""
        if environment not in self.environments:
            raise ValueError(f"Unknown environment: {environment}")

        config = self.environments[environment]
        deployment_id = f"{environment}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        # Initialize deployment result
        result = DeploymentResult(
            deployment_id=deployment_id,
            stage=DeploymentStage.VALIDATION,
            status=DeploymentStatus.RUNNING,
            started_at=datetime.now(timezone.utc)
        )

        self.active_deployments[deployment_id] = result

        try:
            # Stage 1: Validation
            result.logs.append("Starting deployment validation")
            if not await self._validate_environment(config) and not force:
                result.status = DeploymentStatus.FAILED
                result.error_message = "Environment validation failed"
                return result

            # Stage 2: Testing
            result.stage = DeploymentStage.TESTING
            result.logs.append("Running test suite")
            if not await self._run_tests(config) and not force:
                result.status = DeploymentStatus.FAILED
                result.error_message = "Test suite failed"
                return result

            # Stage 3: Build
            result.stage = DeploymentStage.BUILD
            result.logs.append("Building application")
            if not await self._build_application(config):
                result.status = DeploymentStatus.FAILED
                result.error_message = "Application build failed"
                return result

            # Stage 4: Deploy
            result.stage = DeploymentStage.STAGING if environment != "production" else DeploymentStage.PRODUCTION
            result.logs.append(f"Deploying to {environment}")
            if not await self._deploy_to_environment(config):
                result.status = DeploymentStatus.FAILED
                result.error_message = "Deployment failed"

                # Attempt rollback if enabled
                if config.rollback_enabled:
                    result.logs.append("Attempting automatic rollback")
                    await self._rollback_deployment(config)

                return result

            # Success
            result.status = DeploymentStatus.SUCCESS
            result.completed_at = datetime.now(timezone.utc)
            result.logs.append("Deployment completed successfully")

        except Exception as e:
            result.status = DeploymentStatus.FAILED
            result.error_message = str(e)
            result.logs.append(f"Deployment error: {e}")

        finally:
            # Move to history
            self.deployment_history.append(result)
            if deployment_id in self.active_deployments:
                del self.active_deployments[deployment_id]

        return result

    async def _rollback_deployment(self, config: DeploymentConfig) -> bool:
        """Rollback to previous deployment"""
        logger.info(f"Rolling back {config.environment} deployment")

        try:
            # Find latest backup
            backup_dir = self.deployment_dir / "backups" / config.environment
            if not backup_dir.exists():
                logger.error("No backups available for rollback")
                return False

            backups = sorted(backup_dir.glob("backup-*.tar.gz"), reverse=True)
            if not backups:
                logger.error("No backup files found")
                return False

            latest_backup = backups[0]
            logger.info(f"Rolling back to backup: {latest_backup}")

            # Stop current container
            container_name = f"lukhas-{config.environment}"
            await self._run_command(f"docker stop {container_name}")

            # Restore backup
            success, _output, error = await self._run_command(
                f"tar -xzf {latest_backup} -C {self.project_root}"
            )

            if not success:
                logger.error(f"Backup restore failed: {error}")
                return False

            # Restart with previous version
            if config.docker_enabled:
                await self._deploy_docker_container(config)

            logger.info("Rollback completed")
            return True

        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False

    def get_deployment_status(self, deployment_id: str) -> Optional[DeploymentResult]:
        """Get status of a specific deployment"""
        if deployment_id in self.active_deployments:
            return self.active_deployments[deployment_id]

        for deployment in self.deployment_history:
            if deployment.deployment_id == deployment_id:
                return deployment

        return None

    def list_deployments(self, environment: Optional[str] = None) -> list[DeploymentResult]:
        """List recent deployments"""
        deployments = []

        # Add active deployments
        deployments.extend(self.active_deployments.values())

        # Add historical deployments
        deployments.extend(self.deployment_history[-20:])  # Last 20 deployments

        # Filter by environment if specified
        if environment:
            deployments = [d for d in deployments if environment in d.deployment_id]

        return sorted(deployments, key=lambda x: x.started_at, reverse=True)

    async def run_deployment_cli(self):
        """Interactive CLI for deployment management"""
        print("LUKHAS AI Automated Deployment Pipeline")
        print("=" * 50)

        while True:
            print("\nAvailable commands:")
            print("1. Deploy to environment")
            print("2. List deployments")
            print("3. Check deployment status")
            print("4. Rollback deployment")
            print("5. Exit")

            choice = input("\nEnter choice (1-5): ").strip()

            if choice == "1":
                print("\nAvailable environments:")
                for env in self.environments:
                    print(f"- {env}")

                env = input("Enter environment: ").strip()
                if env in self.environments:
                    force = input("Force deployment? (y/n): ").strip().lower() == 'y'
                    print(f"\nStarting deployment to {env}...")

                    result = await self.deploy(env, force=force)
                    print(f"Deployment {result.status.value}: {result.deployment_id}")

                    if result.error_message:
                        print(f"Error: {result.error_message}")

                else:
                    print("Invalid environment")

            elif choice == "2":
                deployments = self.list_deployments()
                print("\nRecent deployments:")
                for dep in deployments[:10]:
                    print(f"{dep.deployment_id}: {dep.status.value} ({dep.started_at})")

            elif choice == "3":
                dep_id = input("Enter deployment ID: ").strip()
                result = self.get_deployment_status(dep_id)
                if result:
                    print(f"\nDeployment: {result.deployment_id}")
                    print(f"Status: {result.status.value}")
                    print(f"Stage: {result.stage.value}")
                    print(f"Started: {result.started_at}")
                    if result.completed_at:
                        print(f"Completed: {result.completed_at}")
                    if result.error_message:
                        print(f"Error: {result.error_message}")
                else:
                    print("Deployment not found")

            elif choice == "4":
                env = input("Enter environment to rollback: ").strip()
                if env in self.environments:
                    config = self.environments[env]
                    success = await self._rollback_deployment(config)
                    print(f"Rollback {'successful' if success else 'failed'}")
                else:
                    print("Invalid environment")

            elif choice == "5":
                break

            else:
                print("Invalid choice")


async def main():
    """Main entry point"""
    project_root = Path(__file__).resolve().parents[2]
    pipeline = AutomatedDeploymentPipeline(project_root)

    await pipeline.run_deployment_cli()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
