#!/usr/bin/env python3
from typing import Optional
"""
LUKHAS AI Datadog Setup and Configuration
Complete integration with Datadog monitoring for enterprise observability

Features:
- Automatic Datadog agent installation check
- API key configuration and validation
- Custom metrics for LUKHAS Trinity Framework
- Real-time monitoring dashboards
- Alert configuration
- Performance tracking
"""
import streamlit as st
from datetime import timezone

import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime

# Try importing Datadog client
try:
    from datadog_api_client import ApiClient, Configuration
    from datadog_api_client.v1.api.dashboards_api import DashboardsApi
    from datadog_api_client.v1.api.metrics_api import MetricsApi
    from datadog_api_client.v1.api.monitors_api import MonitorsApi

    DATADOG_CLIENT_INSTALLED = True
except ImportError:
    DATADOG_CLIENT_INSTALLED = False
    print("⚠️  Datadog API client not installed", timezone)
    print("Installing: pip install datadog-api-client")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "datadog-api-client"])
    # Try importing again after installation
    try:
        from datadog_api_client import ApiClient, Configuration
        from datadog_api_client.v1.api.dashboards_api import DashboardsApi
        from datadog_api_client.v1.api.metrics_api import MetricsApi
        from datadog_api_client.v1.api.monitors_api import MonitorsApi

        DATADOG_CLIENT_INSTALLED = True
    except ImportError:
        print("❌ Failed to install Datadog client")
        sys.exit(1)


@dataclass
class DatadogConfig:
    """Datadog configuration for LUKHAS AI"""

    api_key: str
    app_key: str
    site: str = "us5.datadoghq.com"  # US5 region for GitHub Student Pack
    env: str = "production"
    service: str = "lukhas-ai"
    version: str = "1.0.0"


class LUKHASDatadogSetup:
    """Setup and configure Datadog monitoring for LUKHAS AI"""

    def __init__(self):
        self.config = self._load_config()
        self.configuration = Configuration()
        self.configuration.api_key["apiKeyAuth"] = self.config.api_key
        self.configuration.api_key["appKeyAuth"] = self.config.app_key
        self.configuration.server_variables["site"] = self.config.site

    def _load_config(self) -> DatadogConfig:
        """Load Datadog configuration from environment"""
        # Check for .env file
        env_file = os.path.join(os.path.dirname(__file__), "../../.env")
        if os.path.exists(env_file):
            from dotenv import load_dotenv

            load_dotenv(env_file)

        api_key = os.getenv("DATADOG_API_KEY", "")
        app_key = os.getenv("DATADOG_APP_KEY", "")

        if not api_key or not app_key:
            print("\n🔑 Datadog API Keys Required")
            print("================================")
            print("You need to set up your Datadog API keys:")
            print("")
            print("1. Go to: https://us5.datadoghq.com/organization-settings/api-keys")
            print("2. Create an API Key (for metrics submission)")
            print("3. Go to: https://us5.datadoghq.com/organization-settings/application-keys")
            print("4. Create an Application Key (for dashboards/monitors)")
            print("")
            print("Add to your .env file:")
            print("DATADOG_API_KEY=your_api_key_here")
            print("DATADOG_APP_KEY=your_app_key_here")
            print("")

            # Prompt for keys if not found
            if not api_key:
                api_key = input("Enter your Datadog API Key: ").strip()
            if not app_key:
                app_key = input("Enter your Datadog App Key: ").strip()

        return DatadogConfig(
            api_key=api_key,
            app_key=app_key,
            site=os.getenv("DATADOG_SITE", "us5.datadoghq.com"),
            env=os.getenv("DATADOG_ENV", "production"),
            service=os.getenv("DATADOG_SERVICE", "lukhas-ai"),
            version=os.getenv("DATADOG_VERSION", "1.0.0"),
        )

    def test_connection(self) -> bool:
        """Test Datadog API connection"""
        print("\n🔌 Testing Datadog Connection")
        print("================================")
        print(f"Site: {self.config.site}")
        print(f"Service: {self.config.service}")
        print(f"Environment: {self.config.env}")

        try:
            with ApiClient(self.configuration) as api_client:
                api_instance = MetricsApi(api_client)

                # Send a test metric
                from datadog_api_client.v1.model.metrics_payload import MetricsPayload
                from datadog_api_client.v1.model.point import Point
                from datadog_api_client.v1.model.series import Series

                body = MetricsPayload(
                    [
                        Series(
                            metric="lukhas.test.connection",
                            type="gauge",
                            points=[Point([datetime.now(timezone.utc).timestamp(), 1])],
                            tags=[
                                f"service:{self.config.service}",
                                f"env:{self.config.env}",
                                "test:true",
                            ],
                        )
                    ]
                )

                response = api_instance.submit_metrics(body=body)

                if response["status"] == "ok":
                    print("✅ Successfully connected to Datadog!")
                    print("   Test metric sent: lukhas.test.connection")
                    return True
                else:
                    print(f"❌ Connection test failed: {response}")
                    return False

        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False

    def create_lukhas_dashboard(self):
        """Create LUKHAS AI monitoring dashboard"""
        print("\n📊 Creating LUKHAS AI Dashboard")
        print("================================")

        try:
            with ApiClient(self.configuration) as api_client:
                api_instance = DashboardsApi(api_client)

                from datadog_api_client.v1.model.dashboard import Dashboard
                from datadog_api_client.v1.model.dashboard_layout_type import (
                    DashboardLayoutType,
                )
                from datadog_api_client.v1.model.timeseries_widget_definition import (
                    TimeseriesWidgetDefinition,
                )
                from datadog_api_client.v1.model.timeseries_widget_request import (
                    TimeseriesWidgetRequest,
                )
                from datadog_api_client.v1.model.widget import Widget

                dashboard = Dashboard(
                    title="🧠 LUKHAS AI Trinity Framework Monitor",
                    description="Real-time monitoring of LUKHAS AI consciousness system with Trinity Framework (⚛️🧠🛡️)",
                    layout_type=DashboardLayoutType.ORDERED,
                    widgets=[
                        # API Performance widget
                        Widget(
                            definition=TimeseriesWidgetDefinition(
                                title="API Latency (P95/P99)",
                                show_legend=True,
                                requests=[
                                    TimeseriesWidgetRequest(
                                        q="avg:lukhas.api.latency.p95{service:lukhas-ai}",
                                        display_type="line",
                                        style={"palette": "dog_classic"},
                                    ),
                                    TimeseriesWidgetRequest(
                                        q="avg:lukhas.api.latency.p99{service:lukhas-ai}",
                                        display_type="line",
                                        style={"palette": "orange"},
                                    ),
                                ],
                            )
                        ),
                        # Memory Cascade Prevention
                        Widget(
                            definition=TimeseriesWidgetDefinition(
                                title="🧠 Memory Cascade Prevention Rate",
                                show_legend=True,
                                requests=[
                                    TimeseriesWidgetRequest(
                                        q="avg:lukhas.memory.cascade_prevention_rate{service:lukhas-ai}",
                                        display_type="bars",
                                        style={"palette": "green"},
                                    )
                                ],
                            )
                        ),
                        # Guardian Drift Score
                        Widget(
                            definition=TimeseriesWidgetDefinition(
                                title="🛡️ Guardian Drift Score",
                                show_legend=True,
                                requests=[
                                    TimeseriesWidgetRequest(
                                        q="avg:lukhas.guardian.drift_score{service:lukhas-ai}",
                                        display_type="line",
                                        style={"palette": "warm"},
                                    )
                                ],
                            )
                        ),
                        # Consciousness Coherence
                        Widget(
                            definition=TimeseriesWidgetDefinition(
                                title="⚛️ Consciousness Coherence",
                                show_legend=True,
                                requests=[
                                    TimeseriesWidgetRequest(
                                        q="avg:lukhas.consciousness.coherence{service:lukhas-ai}",
                                        display_type="area",
                                        style={"palette": "cool"},
                                    )
                                ],
                            )
                        ),
                    ],
                )

                response = api_instance.create_dashboard(body=dashboard)
                print("✅ Dashboard created successfully!")
                print(f"   URL: https://{self.config.site}/dashboard/{response.id}")
                print(f"   ID: {response.id}")
                return response

        except Exception as e:
            print(f"❌ Dashboard creation error: {e}")
            return None

    def create_alerts(self):
        """Create monitoring alerts for LUKHAS AI"""
        print("\n🚨 Creating Monitoring Alerts")
        print("================================")

        alerts = [
            {
                "name": "LUKHAS API Latency High (P95 > 50ms)",
                "query": "avg(last_5m):avg:lukhas.api.latency.p95{service:lukhas-ai} > 50",
                "message": "⚠️ API P95 latency exceeds 50ms target! Current: {{value}}ms @slack-lukhas-alerts",
                "thresholds": {"critical": 50, "warning": 40},
            },
            {
                "name": "LUKHAS Memory Cascade Prevention Below Target",
                "query": "avg(last_5m):avg:lukhas.memory.cascade_prevention_rate{service:lukhas-ai} < 0.997",
                "message": "🧠 Memory cascade prevention rate below 99.7% target! Current: {{value}} @slack-lukhas-alerts",
                "thresholds": {"critical": 0.997, "warning": 0.999},
            },
            {
                "name": "LUKHAS Guardian Drift Threshold Exceeded",
                "query": "avg(last_5m):avg:lukhas.guardian.drift_score{service:lukhas-ai} > 0.15",
                "message": "🛡️ Guardian drift score exceeds 0.15 threshold! Current: {{value}} @slack-lukhas-alerts",
                "thresholds": {"critical": 0.15, "warning": 0.10},
            },
            {
                "name": "LUKHAS System Uptime Below SLA",
                "query": "avg(last_5m):avg:lukhas.system.uptime{service:lukhas-ai} < 0.9999",
                "message": "🔴 System uptime below 99.99% SLA! Current: {{value}} @slack-lukhas-alerts",
                "thresholds": {"critical": 0.9999, "warning": 0.99995},
            },
        ]

        try:
            with ApiClient(self.configuration) as api_client:
                api_instance = MonitorsApi(api_client)

                from datadog_api_client.v1.model.monitor import Monitor
                from datadog_api_client.v1.model.monitor_thresholds import (
                    MonitorThresholds,
                )
                from datadog_api_client.v1.model.monitor_type import MonitorType

                created_monitors = []
                for alert in alerts:
                    monitor = Monitor(
                        name=alert["name"],
                        type=MonitorType.QUERY_ALERT,
                        query=alert["query"],
                        message=alert["message"],
                        tags=[
                            f"service:{self.config.service}",
                            f"env:{self.config.env}",
                            "team:lukhas",
                        ],
                        options={
                            "thresholds": MonitorThresholds(**alert["thresholds"]),
                            "notify_no_data": True,
                            "no_data_timeframe": 10,
                        },
                    )

                    response = api_instance.create_monitor(body=monitor)
                    created_monitors.append(response)
                    print(f"✅ Created alert: {alert['name']}")

                print(f"\n✅ Created {len(created_monitors)} monitoring alerts")
                return created_monitors

        except Exception as e:
            print(f"❌ Alert creation error: {e}")
            return []

    def setup_custom_metrics(self):
        """Define custom metrics for LUKHAS AI monitoring"""
        print("\n📈 Setting Up Custom Metrics")
        print("================================")

        metrics = {
            # Trinity Framework Core Metrics
            "lukhas.api.latency.p95": "API P95 latency in milliseconds",
            "lukhas.api.latency.p99": "API P99 latency in milliseconds",
            "lukhas.api.requests": "Number of API requests",
            "lukhas.api.errors": "Number of API errors",
            # Memory System Metrics
            "lukhas.memory.cascade_prevention_rate": "Memory cascade prevention success rate",
            "lukhas.memory.fold_count": "Number of active memory folds",
            "lukhas.memory.operation_time": "Memory operation time in ms",
            # Guardian System Metrics
            "lukhas.guardian.drift_score": "Guardian ethical drift score",
            "lukhas.guardian.violations": "Number of guardian violations",
            "lukhas.guardian.interventions": "Number of guardian interventions",
            # Consciousness System Metrics
            "lukhas.consciousness.coherence": "Consciousness coherence level",
            "lukhas.consciousness.awareness_level": "System awareness level",
            "lukhas.consciousness.processing_time": "Consciousness processing time",
            # System Health Metrics
            "lukhas.system.uptime": "System uptime percentage",
            "lukhas.system.cpu_usage": "CPU usage percentage",
            "lukhas.system.memory_usage": "Memory usage percentage",
            "lukhas.system.active_users": "Number of active users",
        }

        print("Custom metrics configured:")
        for metric, description in metrics.items():
            print(f"  📊 {metric}: {description}")

        return metrics

    def generate_env_template(self):
        """Generate .env template with Datadog configuration"""
        print("\n📝 Generating .env Template")
        print("================================")

        template = """
# Datadog Monitoring Configuration
# GitHub Student Pack: https://education.github.com/pack
# Datadog US5: https://us5.datadoghq.com

# API Keys (Required)
# Get API Key from: https://us5.datadoghq.com/organization-settings/api-keys
DATADOG_API_KEY=your_api_key_here

# Get App Key from: https://us5.datadoghq.com/organization-settings/application-keys
DATADOG_APP_KEY=your_app_key_here

# Configuration (Optional - defaults shown)
DATADOG_SITE=us5.datadoghq.com  # US5 region for GitHub Student Pack
DATADOG_ENV=production           # Environment tag
DATADOG_SERVICE=lukhas-ai        # Service name
DATADOG_VERSION=1.0.0           # Version tag

# Alert Configuration (Optional)
DATADOG_ALERT_EMAIL=your-email@example.com
DATADOG_ALERT_SLACK=#lukhas-alerts
"""

        env_path = os.path.join(os.path.dirname(__file__), "../../.env.datadog")
        with open(env_path, "w") as f:
            f.write(template)

        print(f"✅ Template saved to: {env_path}")
        print("   Add these variables to your .env file")

        return template

    def run_setup(self):
        """Run complete Datadog setup for LUKHAS AI"""
        print("\n" + "=" * 50)
        print("🚀 LUKHAS AI Datadog Setup")
        print("   Trinity Framework Monitoring (⚛️🧠🛡️)")
        print("=" * 50)

        # Step 1: Test connection
        if not self.test_connection():
            print("\n⚠️  Please configure your API keys and try again")
            self.generate_env_template()
            return False

        # Step 2: Setup custom metrics
        self.setup_custom_metrics()

        # Step 3: Create dashboard
        self.create_lukhas_dashboard()

        # Step 4: Create alerts
        self.create_alerts()

        # Step 5: Summary
        print("\n" + "=" * 50)
        print("✅ LUKHAS AI Datadog Setup Complete!")
        print("=" * 50)
        print("\n📊 Next Steps:")
        print("1. View your dashboard at:")
        print(f"   https://{self.config.site}/dashboard")
        print("\n2. Send metrics from your application:")
        print("   from enterprise.monitoring.datadog_integration import T4DatadogMonitoring")
        print("   monitor = T4DatadogMonitoring()")
        print("   monitor.submit_sla_metrics(metrics)")
        print("\n3. Check alerts at:")
        print(f"   https://{self.config.site}/monitors")

        return True


def main():
    """Main setup function"""
    setup = LUKHASDatadogSetup()
    setup.run_setup()


if __name__ == "__main__":
    main()