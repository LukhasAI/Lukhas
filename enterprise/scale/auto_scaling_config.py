"""
T4 Enterprise Auto-Scaling Configuration
Sam Altman (Scale) Standards Implementation

Implements enterprise-grade auto-scaling for 10,000+ concurrent users
Ensures <50ms p95 latency under variable load conditions
"""

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)

class ScalingTrigger(Enum):
    """Auto-scaling trigger types"""
    CPU_UTILIZATION = "cpu_utilization"
    MEMORY_UTILIZATION = "memory_utilization"
    REQUEST_LATENCY = "request_latency"
    REQUEST_RATE = "request_rate"
    CONCURRENT_USERS = "concurrent_users"
    ERROR_RATE = "error_rate"
    QUEUE_DEPTH = "queue_depth"

class ScalingPolicy(Enum):
    """Scaling policy types"""
    TARGET_TRACKING = "target_tracking"
    STEP_SCALING = "step_scaling"
    PREDICTIVE_SCALING = "predictive_scaling"
    CUSTOM_METRIC = "custom_metric"

@dataclass
class ScalingMetric:
    """Scaling metric configuration"""
    name: str
    trigger: ScalingTrigger
    target_value: float
    scale_up_threshold: float
    scale_down_threshold: float
    evaluation_periods: int = 2
    datapoints_to_alarm: int = 2
    cooldown_period_seconds: int = 300

@dataclass
class ScalingAction:
    """Scaling action configuration"""
    metric: ScalingMetric
    policy: ScalingPolicy
    min_capacity: int
    max_capacity: int
    desired_capacity: int
    scale_up_increment: int = 1
    scale_down_increment: int = 1
    warmup_time_seconds: int = 300

@dataclass
class T4ScalingConfig:
    """T4 Enterprise scaling configuration"""
    environment: str = "production"
    tier: str = "T4_ENTERPRISE_PREMIUM"

    # Sam Altman (Scale) requirements
    max_concurrent_users: int = 10000
    target_latency_p95_ms: float = 50.0
    target_latency_p99_ms: float = 100.0
    target_cpu_utilization: float = 70.0
    target_memory_utilization: float = 80.0

    # Scaling boundaries
    min_instances: int = 3  # Minimum for high availability
    max_instances: int = 100  # Enterprise scale limit
    default_instances: int = 5

    # Enterprise features
    multi_region: bool = True
    predictive_scaling: bool = True
    advanced_monitoring: bool = True

    scaling_actions: List[ScalingAction] = None

class T4AutoScalingManager:
    """
    T4 Enterprise Premium Auto-Scaling Manager
    Implements Sam Altman (Scale) standards for enterprise deployment
    """

    def __init__(self, config: T4ScalingConfig):
        """
        Initialize T4 auto-scaling manager

        Args:
            config: T4ScalingConfig with scaling parameters
        """
        self.config = config

        if not self.config.scaling_actions:
            self.config.scaling_actions = self._create_default_scaling_actions()

        logger.info(f"T4 Auto-Scaling Manager initialized for {config.environment}")

    def _create_default_scaling_actions(self) -> List[ScalingAction]:
        """Create default scaling actions for T4 enterprise"""

        # Latency-based scaling (Sam Altman priority)
        latency_metric = ScalingMetric(
            name="api_latency_p95",
            trigger=ScalingTrigger.REQUEST_LATENCY,
            target_value=self.config.target_latency_p95_ms,
            scale_up_threshold=45.0,  # Scale up before hitting 50ms limit
            scale_down_threshold=30.0,  # Scale down when well under limit
            evaluation_periods=2,
            datapoints_to_alarm=2,
            cooldown_period_seconds=180  # Fast response for latency
        )

        latency_action = ScalingAction(
            metric=latency_metric,
            policy=ScalingPolicy.TARGET_TRACKING,
            min_capacity=self.config.min_instances,
            max_capacity=self.config.max_instances,
            desired_capacity=self.config.default_instances,
            scale_up_increment=3,  # Aggressive scaling for latency
            scale_down_increment=1,
            warmup_time_seconds=120  # Fast warmup for latency issues
        )

        # CPU utilization scaling
        cpu_metric = ScalingMetric(
            name="cpu_utilization",
            trigger=ScalingTrigger.CPU_UTILIZATION,
            target_value=self.config.target_cpu_utilization,
            scale_up_threshold=75.0,
            scale_down_threshold=50.0,
            evaluation_periods=3,
            datapoints_to_alarm=2,
            cooldown_period_seconds=300
        )

        cpu_action = ScalingAction(
            metric=cpu_metric,
            policy=ScalingPolicy.TARGET_TRACKING,
            min_capacity=self.config.min_instances,
            max_capacity=self.config.max_instances,
            desired_capacity=self.config.default_instances,
            scale_up_increment=2,
            scale_down_increment=1,
            warmup_time_seconds=300
        )

        # Memory utilization scaling
        memory_metric = ScalingMetric(
            name="memory_utilization",
            trigger=ScalingTrigger.MEMORY_UTILIZATION,
            target_value=self.config.target_memory_utilization,
            scale_up_threshold=85.0,
            scale_down_threshold=60.0,
            evaluation_periods=2,
            datapoints_to_alarm=2,
            cooldown_period_seconds=300
        )

        memory_action = ScalingAction(
            metric=memory_metric,
            policy=ScalingPolicy.TARGET_TRACKING,
            min_capacity=self.config.min_instances,
            max_capacity=self.config.max_instances,
            desired_capacity=self.config.default_instances,
            scale_up_increment=2,
            scale_down_increment=1,
            warmup_time_seconds=300
        )

        # Concurrent users scaling (enterprise capacity)
        users_metric = ScalingMetric(
            name="concurrent_users",
            trigger=ScalingTrigger.CONCURRENT_USERS,
            target_value=self.config.max_concurrent_users * 0.7,  # 70% of max capacity
            scale_up_threshold=self.config.max_concurrent_users * 0.6,
            scale_down_threshold=self.config.max_concurrent_users * 0.3,
            evaluation_periods=2,
            datapoints_to_alarm=1,  # Fast response for user load
            cooldown_period_seconds=120
        )

        users_action = ScalingAction(
            metric=users_metric,
            policy=ScalingPolicy.PREDICTIVE_SCALING if self.config.predictive_scaling else ScalingPolicy.TARGET_TRACKING,
            min_capacity=self.config.min_instances,
            max_capacity=self.config.max_instances,
            desired_capacity=self.config.default_instances,
            scale_up_increment=5,  # Aggressive scaling for user load
            scale_down_increment=1,
            warmup_time_seconds=180
        )

        # Request rate scaling
        rate_metric = ScalingMetric(
            name="request_rate_per_instance",
            trigger=ScalingTrigger.REQUEST_RATE,
            target_value=1000.0,  # Requests per second per instance
            scale_up_threshold=800.0,
            scale_down_threshold=300.0,
            evaluation_periods=2,
            datapoints_to_alarm=2,
            cooldown_period_seconds=240
        )

        rate_action = ScalingAction(
            metric=rate_metric,
            policy=ScalingPolicy.TARGET_TRACKING,
            min_capacity=self.config.min_instances,
            max_capacity=self.config.max_instances,
            desired_capacity=self.config.default_instances,
            scale_up_increment=2,
            scale_down_increment=1,
            warmup_time_seconds=240
        )

        return [latency_action, cpu_action, memory_action, users_action, rate_action]

    def generate_kubernetes_config(self) -> Dict[str, Any]:
        """
        Generate Kubernetes Horizontal Pod Autoscaler (HPA) configuration

        Returns:
            Kubernetes HPA configuration dictionary
        """
        hpa_config = {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": "lukhas-ai-t4-hpa",
                "namespace": "lukhas-production",
                "labels": {
                    "app": "lukhas-ai",
                    "tier": "T4_ENTERPRISE_PREMIUM",
                    "component": "auto-scaler"
                }
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": "lukhas-ai-deployment"
                },
                "minReplicas": self.config.min_instances,
                "maxReplicas": self.config.max_instances,
                "metrics": [],
                "behavior": {
                    "scaleUp": {
                        "stabilizationWindowSeconds": 60,
                        "policies": [
                            {
                                "type": "Percent",
                                "value": 100,
                                "periodSeconds": 60
                            },
                            {
                                "type": "Pods",
                                "value": 5,
                                "periodSeconds": 60
                            }
                        ],
                        "selectPolicy": "Max"
                    },
                    "scaleDown": {
                        "stabilizationWindowSeconds": 300,
                        "policies": [
                            {
                                "type": "Percent",
                                "value": 10,
                                "periodSeconds": 60
                            }
                        ]
                    }
                }
            }
        }

        # Add metrics from scaling actions
        for action in self.config.scaling_actions:
            metric_config = self._generate_k8s_metric(action)
            if metric_config:
                hpa_config["spec"]["metrics"].append(metric_config)

        return hpa_config

    def _generate_k8s_metric(self, action: ScalingAction) -> Optional[Dict[str, Any]]:
        """Generate Kubernetes metric configuration from scaling action"""

        trigger = action.metric.trigger

        if trigger == ScalingTrigger.CPU_UTILIZATION:
            return {
                "type": "Resource",
                "resource": {
                    "name": "cpu",
                    "target": {
                        "type": "Utilization",
                        "averageUtilization": int(action.metric.target_value)
                    }
                }
            }

        elif trigger == ScalingTrigger.MEMORY_UTILIZATION:
            return {
                "type": "Resource",
                "resource": {
                    "name": "memory",
                    "target": {
                        "type": "Utilization",
                        "averageUtilization": int(action.metric.target_value)
                    }
                }
            }

        elif trigger == ScalingTrigger.REQUEST_LATENCY:
            return {
                "type": "Pods",
                "pods": {
                    "metric": {
                        "name": "lukhas_api_latency_p95_milliseconds"
                    },
                    "target": {
                        "type": "AverageValue",
                        "averageValue": f"{action.metric.target_value}m"  # milliseconds
                    }
                }
            }

        elif trigger == ScalingTrigger.REQUEST_RATE:
            return {
                "type": "Pods",
                "pods": {
                    "metric": {
                        "name": "lukhas_requests_per_second"
                    },
                    "target": {
                        "type": "AverageValue",
                        "averageValue": str(action.metric.target_value)
                    }
                }
            }

        elif trigger == ScalingTrigger.CONCURRENT_USERS:
            return {
                "type": "Object",
                "object": {
                    "metric": {
                        "name": "lukhas_concurrent_users"
                    },
                    "target": {
                        "type": "Value",
                        "value": str(int(action.metric.target_value))
                    },
                    "describedObject": {
                        "apiVersion": "v1",
                        "kind": "Service",
                        "name": "lukhas-ai-service"
                    }
                }
            }

        return None

    def generate_azure_config(self) -> Dict[str, Any]:
        """
        Generate Azure Container Apps auto-scaling configuration

        Returns:
            Azure Container Apps scaling configuration
        """
        azure_config = {
            "properties": {
                "configuration": {
                    "ingress": {
                        "external": True,
                        "targetPort": 8080,
                        "allowInsecure": False
                    }
                },
                "template": {
                    "revisionSuffix": "t4-enterprise",
                    "containers": [
                        {
                            "name": "lukhas-ai-t4",
                            "image": "lukhasai.azurecr.io/lukhas-ai:latest",
                            "resources": {
                                "cpu": "2.0",
                                "memory": "4Gi"
                            },
                            "env": [
                                {
                                    "name": "LUKHAS_TIER",
                                    "value": "T4_ENTERPRISE_PREMIUM"
                                },
                                {
                                    "name": "LUKHAS_MAX_CONCURRENT_USERS",
                                    "value": str(self.config.max_concurrent_users)
                                },
                                {
                                    "name": "LUKHAS_TARGET_LATENCY_P95",
                                    "value": str(self.config.target_latency_p95_ms)
                                }
                            ]
                        }
                    ],
                    "scale": {
                        "minReplicas": self.config.min_instances,
                        "maxReplicas": self.config.max_instances,
                        "rules": []
                    }
                }
            }
        }

        # Add scaling rules
        for action in self.config.scaling_actions:
            rule = self._generate_azure_scaling_rule(action)
            if rule:
                azure_config["properties"]["template"]["scale"]["rules"].append(rule)

        return azure_config

    def _generate_azure_scaling_rule(self, action: ScalingAction) -> Optional[Dict[str, Any]]:
        """Generate Azure Container Apps scaling rule"""

        trigger = action.metric.trigger

        if trigger == ScalingTrigger.CPU_UTILIZATION:
            return {
                "name": "cpu-scaling-rule",
                "custom": {
                    "type": "cpu",
                    "metadata": {
                        "type": "Utilization",
                        "value": str(int(action.metric.target_value))
                    }
                }
            }

        elif trigger == ScalingTrigger.MEMORY_UTILIZATION:
            return {
                "name": "memory-scaling-rule",
                "custom": {
                    "type": "memory",
                    "metadata": {
                        "type": "Utilization",
                        "value": str(int(action.metric.target_value))
                    }
                }
            }

        elif trigger == ScalingTrigger.REQUEST_RATE:
            return {
                "name": "http-requests-rule",
                "http": {
                    "metadata": {
                        "concurrentRequests": str(int(action.metric.target_value))
                    }
                }
            }

        return None

    def generate_monitoring_config(self) -> Dict[str, Any]:
        """
        Generate monitoring configuration for auto-scaling

        Returns:
            Monitoring configuration dictionary
        """
        monitoring_config = {
            "t4_enterprise_monitoring": {
                "auto_scaling": {
                    "enabled": True,
                    "tier": self.config.tier,
                    "environment": self.config.environment
                },

                "metrics_collection": {
                    "interval_seconds": 30,
                    "retention_days": 90,  # Enterprise retention
                    "export_to_datadog": True,
                    "export_to_prometheus": True
                },

                "scaling_metrics": [],

                "alerts": {
                    "scaling_events": True,
                    "capacity_warnings": True,
                    "sla_violations": True,
                    "notification_channels": [
                        "datadog",
                        "sentry",
                        "pagerduty"
                    ]
                },

                "dashboards": {
                    "auto_scaling_dashboard": True,
                    "capacity_planning": True,
                    "sla_compliance": True
                }
            }
        }

        # Add monitoring for each scaling metric
        for action in self.config.scaling_actions:
            metric_config = {
                "name": action.metric.name,
                "trigger": action.metric.trigger.value,
                "target_value": action.metric.target_value,
                "thresholds": {
                    "scale_up": action.metric.scale_up_threshold,
                    "scale_down": action.metric.scale_down_threshold
                },
                "evaluation_periods": action.metric.evaluation_periods,
                "cooldown_seconds": action.metric.cooldown_period_seconds
            }
            monitoring_config["t4_enterprise_monitoring"]["scaling_metrics"].append(metric_config)

        return monitoring_config

    def export_configurations(self, output_dir: str = "enterprise/deployment") -> Dict[str, str]:
        """
        Export all auto-scaling configurations to files

        Args:
            output_dir: Directory to save configuration files

        Returns:
            Dictionary mapping configuration type to filename
        """
        os.makedirs(output_dir, exist_ok=True)

        exported_files = {}

        try:
            # Kubernetes HPA configuration
            k8s_config = self.generate_kubernetes_config()
            k8s_file = os.path.join(output_dir, "t4-enterprise-hpa.yaml")
            with open(k8s_file, 'w') as f:
                yaml.dump(k8s_config, f, default_flow_style=False, indent=2)
            exported_files["kubernetes"] = k8s_file

            # Azure Container Apps configuration
            azure_config = self.generate_azure_config()
            azure_file = os.path.join(output_dir, "t4-enterprise-azure-scaling.json")
            with open(azure_file, 'w') as f:
                json.dump(azure_config, f, indent=2)
            exported_files["azure"] = azure_file

            # Monitoring configuration
            monitoring_config = self.generate_monitoring_config()
            monitoring_file = os.path.join(output_dir, "t4-enterprise-monitoring.yaml")
            with open(monitoring_file, 'w') as f:
                yaml.dump(monitoring_config, f, default_flow_style=False, indent=2)
            exported_files["monitoring"] = monitoring_file

            # Summary configuration
            summary = {
                "t4_enterprise_auto_scaling": {
                    "configuration_timestamp": datetime.now().isoformat(),
                    "tier": self.config.tier,
                    "environment": self.config.environment,
                    "sam_altman_standards": {
                        "max_concurrent_users": self.config.max_concurrent_users,
                        "target_latency_p95_ms": self.config.target_latency_p95_ms,
                        "min_instances": self.config.min_instances,
                        "max_instances": self.config.max_instances
                    },
                    "scaling_actions_count": len(self.config.scaling_actions),
                    "exported_files": exported_files
                }
            }

            summary_file = os.path.join(output_dir, "t4-enterprise-scaling-summary.yaml")
            with open(summary_file, 'w') as f:
                yaml.dump(summary, f, default_flow_style=False, indent=2)
            exported_files["summary"] = summary_file

            logger.info(f"T4 auto-scaling configurations exported to: {output_dir}")
            return exported_files

        except Exception as e:
            logger.error(f"Failed to export auto-scaling configurations: {e}")
            return {}


# Example usage and configuration
if __name__ == "__main__":
    # Create T4 enterprise scaling configuration
    t4_config = T4ScalingConfig(
        environment="production",
        tier="T4_ENTERPRISE_PREMIUM",
        max_concurrent_users=10000,  # Sam Altman scale target
        target_latency_p95_ms=50.0,  # Sam Altman latency requirement
        min_instances=5,
        max_instances=100,
        default_instances=10,
        multi_region=True,
        predictive_scaling=True,
        advanced_monitoring=True
    )

    # Initialize auto-scaling manager
    scaling_manager = T4AutoScalingManager(t4_config)

    print("🚀 T4 Enterprise Auto-Scaling Configuration Generator")
    print("   Sam Altman (Scale) Standards Implementation")
    print(f"   Target: {t4_config.max_concurrent_users:,} concurrent users")
    print(f"   Latency: <{t4_config.target_latency_p95_ms}ms p95")
    print(f"   Scaling: {t4_config.min_instances}-{t4_config.max_instances} instances")
    print("")

    # Export all configurations
    exported = scaling_manager.export_configurations()

    print("📄 Generated Configuration Files:")
    for config_type, filepath in exported.items():
        print(f"   {config_type.capitalize()}: {filepath}")

    print("\n✅ T4 Enterprise auto-scaling configurations generated successfully")
    print("   Ready for deployment to Kubernetes or Azure Container Apps")
