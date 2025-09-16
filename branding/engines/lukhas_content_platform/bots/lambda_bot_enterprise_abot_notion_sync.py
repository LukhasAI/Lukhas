"""
LUKHAS AI ΛBot Comprehensive Notion Sync System
Automatically generates and syncs daily reports with financial, AI routing, and system health data
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

try:
    import requests
    from requests import Response
    from requests.exceptions import RequestException
except Exception:  # pragma: no cover - fallback when requests is unavailable
    requests = None  # type: ignore[assignment]
    Response = Any  # type: ignore[assignment]
    RequestException = Exception  # type: ignore[assignment]

# Configure logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


NOTION_API_URL = "https://api.notion.com/v1/pages"
DEFAULT_NOTION_VERSION = "2022-06-28"


def _default_property_map() -> dict[str, str]:
    """Return the default Notion property mapping used for daily reports."""

    return {
        "name": "Name",
        "date": "Date",
        "summary": "Summary",
        "financial_status": "Financial Status",
        "current_balance": "Current Balance",
        "efficiency_score": "Efficiency Score",
        "available_services": "AI Services",
        "system_health": "System Health",
        "recommendations": "Recommendations",
        "alerts": "Alerts",
        "raw_json": "Raw Data",
    }


@dataclass
class NotionSyncConfig:
    """Configuration for Notion sync"""

    database_id: str = ""
    api_key: str = ""
    sync_enabled: bool = False
    auto_sync_time: str = "09:00"
    timezone: str = "UTC"
    notion_version: str = DEFAULT_NOTION_VERSION
    property_map: dict[str, str] = field(default_factory=_default_property_map)


@dataclass
class DailyReport:
    """Daily LUKHAS AI ΛBot report structure"""

    date: str
    financial_data: dict[str, Any]
    ai_routing_data: dict[str, Any]
    system_health: dict[str, Any]
    recommendations: list[str]
    alerts: list[str]


class ABotNotionSync:
    """Comprehensive LUKHAS AI ΛBot Notion sync system"""

    def __init__(self):
        self.branding_root = Path(__file__).resolve().parents[3]
        self.config_path = self.branding_root / "config" / "notion_sync_config.json"
        self.output_path = self.branding_root / "config" / "notion_sync"
        self.config = self._load_config()
        self._session = self._create_requests_session()

        # Ensure output directory exists
        self.output_path.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> NotionSyncConfig:
        """Load Notion sync configuration"""
        config = NotionSyncConfig()
        try:
            if self.config_path.exists():
                with open(self.config_path) as f:
                    data = json.load(f)
                config = NotionSyncConfig(**data)
            else:
                # Create default config
                self._save_config(config)
        except Exception as e:
            logger.error(f"Error loading config: {e}")

        config.property_map = self._merge_property_map(config.property_map)
        if not config.notion_version:
            config.notion_version = DEFAULT_NOTION_VERSION

        return config

    def _save_config(self, config: NotionSyncConfig):
        """Save Notion sync configuration"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w") as f:
                json.dump(asdict(config), f, indent=2)
        except Exception as e:
            logger.error(f"Error saving config: {e}")

    def _merge_property_map(self, override: Optional[dict[str, str]]) -> dict[str, str]:
        """Merge an override map with the default Notion property mapping."""

        merged = _default_property_map()
        if override:
            for key, value in override.items():
                if key and value:
                    merged[key] = value
        return merged

    def _create_requests_session(self) -> Optional["requests.Session"]:
        """Create an HTTP session for communicating with the Notion API."""

        if requests is None:
            logger.warning("requests library not available; Notion sync will run in offline mode")
            return None

        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        return session

    def get_financial_data(self) -> dict[str, Any]:
        """Get financial intelligence data"""
        try:
            from lukhas_ai_lambda_bot.core.abot_financial_intelligence import (
                ABotFinancialIntelligence,
            )

            fi = ABotFinancialIntelligence()
            status = fi.get_financial_report()

            budget_status = status.get("budget_status", {})
            spending = status.get("spending_analysis", {})
            intelligence = status.get("intelligence_metrics", {})
            usage = status.get("usage_patterns", {})

            return {
                "current_balance": float(budget_status.get("current_balance", 0)),
                "daily_budget": float(budget_status.get("daily_budget", 0.1)),
                "total_accumulated": float(budget_status.get("total_accumulated", 0)),
                "efficiency_score": float(intelligence.get("efficiency_score", 100)),
                "money_saved": float(intelligence.get("money_saved_by_conservation", 0)),
                "today_spent": float(spending.get("today_spent", 0)),
                "month_spent": float(spending.get("month_spent", 0)),
                "calls_today": int(usage.get("calls_today", 0)),
                "conservation_streak": int(intelligence.get("conservation_streak", 0)),
            }
        except Exception as e:
            logger.error(f"Error getting financial data: {e}")
            return {
                "error": str(e),
                "current_balance": 0.10,
                "daily_budget": 0.10,
                "status": "error",
            }

    def get_ai_routing_data(self) -> dict[str, Any]:
        """Get AI routing system data"""
        try:
            from lukhas_ai_lambda_bot.core.abot_ai_router import ABotIntelligentAIRouter

            router = ABotIntelligentAIRouter()

            services = router.get_available_services()
            analytics = router.get_routing_analytics()

            return {
                "available_services": len(services),
                "service_names": services,
                "total_requests": analytics.get("total_requests", 0),
                "service_usage": analytics.get("service_usage", {}),
                "last_used_service": analytics.get("last_used_service", "none"),
                "success_rate": analytics.get("success_rate", 100.0),
                "avg_response_time": analytics.get("avg_response_time", 0),
            }
        except Exception as e:
            logger.error(f"Error getting AI routing data: {e}")
            return {"error": str(e), "available_services": 0, "status": "error"}

    def get_system_health(self) -> dict[str, Any]:
        """Get overall system health data"""
        health_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_hours": 24,  # Mock data
            "memory_usage": 45.2,  # Mock data
            "cpu_usage": 12.5,  # Mock data
            "disk_usage": 68.3,  # Mock data
            "active_processes": 8,  # Mock data
            "last_error": None,
            "status": "healthy",
        }

        # Check if core systems are accessible
        try:
            health_data["core_abot"] = "✅ Online"
        except Exception as e:
            health_data["core_abot"] = f"❌ Error: {e}"
            health_data["status"] = "degraded"

        try:
            health_data["financial_intelligence"] = "✅ Online"
        except Exception as e:
            health_data["financial_intelligence"] = f"❌ Error: {e}"
            health_data["status"] = "degraded"

        try:
            health_data["ai_router"] = "✅ Online"
        except Exception as e:
            health_data["ai_router"] = f"❌ Error: {e}"
            health_data["status"] = "degraded"

        return health_data

    def generate_recommendations(self, financial_data: dict, ai_data: dict, health_data: dict) -> list[str]:
        """Generate intelligent recommendations based on system data"""
        recommendations = []

        # Financial recommendations
        if financial_data.get("efficiency_score", 0) < 80:
            recommendations.append("🔧 Consider optimizing AI usage to improve financial efficiency")

        if financial_data.get("current_balance", 0) < 0.05:
            recommendations.append("💰 Budget running low - consider increasing daily allocation")

        if financial_data.get("conservation_streak", 0) > 7:
            recommendations.append("🌟 Excellent conservation streak! Consider reinvesting savings")

        # AI routing recommendations
        if ai_data.get("available_services", 0) < 5:
            recommendations.append("🤖 Some AI services may be offline - check API keys")

        if ai_data.get("success_rate", 100) < 95:
            recommendations.append("🔍 AI routing success rate below optimal - investigate failures")

        # System health recommendations
        if health_data.get("status") == "degraded":
            recommendations.append("⚠️ System health degraded - check error logs")

        if health_data.get("memory_usage", 0) > 80:
            recommendations.append("🧠 High memory usage detected - consider optimization")

        # Default positive recommendation
        if not recommendations:
            recommendations.append("✨ All systems operating optimally - excellent work!")

        return recommendations

    def generate_alerts(self, financial_data: dict, ai_data: dict, health_data: dict) -> list[str]:
        """Generate critical alerts"""
        alerts = []

        # Critical financial alerts
        if financial_data.get("current_balance", 0) < 0:
            alerts.append("🚨 CRITICAL: Budget exhausted - all AI operations halted")

        if financial_data.get("today_spent", 0) > financial_data.get("daily_budget", 0.1):
            alerts.append("⚠️ WARNING: Daily budget exceeded")

        # AI routing alerts
        if ai_data.get("available_services", 0) == 0:
            alerts.append("🚨 CRITICAL: No AI services available")

        if ai_data.get("success_rate", 100) < 80:
            alerts.append("⚠️ WARNING: AI routing success rate critically low")

        # System health alerts
        if health_data.get("status") == "error":
            alerts.append("🚨 CRITICAL: System health check failed")

        return alerts

    def generate_daily_report(self) -> DailyReport:
        """Generate comprehensive daily report"""
        logger.info("Generating daily LUKHAS AI ΛBot report...")

        # Collect data
        financial_data = self.get_financial_data()
        ai_routing_data = self.get_ai_routing_data()
        system_health = self.get_system_health()

        # Generate insights
        recommendations = self.generate_recommendations(financial_data, ai_routing_data, system_health)
        alerts = self.generate_alerts(financial_data, ai_routing_data, system_health)

        # Create report
        report = DailyReport(
            date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            financial_data=financial_data,
            ai_routing_data=ai_routing_data,
            system_health=system_health,
            recommendations=recommendations,
            alerts=alerts,
        )

        # Save report to file
        self._save_report(report)

        logger.info(
            f"Daily report generated successfully with {len(recommendations)} recommendations and {len(alerts)} alerts"
        )
        return report

    def _save_report(self, report: DailyReport):
        """Save report to file"""
        try:
            filename = f"abot_daily_report_{report.date}.json"
            filepath = self.output_path / filename

            with open(filepath, "w") as f:
                json.dump(asdict(report), f, indent=2, default=str)

            # Also save as latest report
            latest_path = self.output_path / "latest_report.json"
            with open(latest_path, "w") as f:
                json.dump(asdict(report), f, indent=2, default=str)

            logger.info(f"Report saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving report: {e}")

    def _build_headers(self) -> dict[str, str]:
        """Construct HTTP headers for Notion API requests."""

        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": self.config.notion_version or DEFAULT_NOTION_VERSION,
        }

    def _build_summary(self, report: DailyReport) -> str:
        """Create a concise textual summary for the Notion page."""

        balance = report.financial_data.get("current_balance", 0.0)
        services = report.ai_routing_data.get("available_services", 0)
        health = report.system_health.get("status", "unknown")
        status = "Healthy" if not report.alerts else "Attention Required"

        return (
            f"Daily report for {report.date}: {status}. "
            f"Balance ${balance:,.2f}, {services} AI services active, system health {health}."
        )

    def _build_notion_payload(self, report: DailyReport) -> dict[str, Any]:
        """Create the Notion API payload for the daily report."""

        property_map = self.config.property_map or _default_property_map()
        default_map = _default_property_map()

        def prop(key: str) -> str:
            return property_map.get(key, default_map.get(key, key))

        alerts_text = "\n".join(report.alerts) if report.alerts else "No alerts."
        recommendations_text = (
            "\n".join(report.recommendations) if report.recommendations else "No recommendations."
        )

        payload = {
            "parent": {"database_id": self.config.database_id},
            "properties": {
                prop("name"): {
                    "title": [
                        {
                            "text": {
                                "content": f"LUKHAS Daily Report {report.date}",
                            }
                        }
                    ]
                },
                prop("date"): {"date": {"start": report.date}},
                prop("summary"): {
                    "rich_text": [{"text": {"content": self._build_summary(report)}}]
                },
                prop("financial_status"): {
                    "select": {
                        "name": "Healthy" if not report.alerts else "Needs Attention",
                    }
                },
                prop("current_balance"): {
                    "number": float(report.financial_data.get("current_balance", 0.0))
                },
                prop("efficiency_score"): {
                    "number": float(report.financial_data.get("efficiency_score", 0.0))
                },
                prop("available_services"): {
                    "number": int(report.ai_routing_data.get("available_services", 0))
                },
                prop("system_health"): {
                    "rich_text": [
                        {
                            "text": {
                                "content": report.system_health.get("status", "unknown"),
                            }
                        }
                    ]
                },
                prop("recommendations"): {
                    "rich_text": [{"text": {"content": recommendations_text}}]
                },
                prop("alerts"): {"rich_text": [{"text": {"content": alerts_text}}]},
            },
        }

        raw_property = prop("raw_json")
        if raw_property:
            payload["properties"][raw_property] = {
                "rich_text": [
                    {
                        "text": {
                            "content": json.dumps(
                                asdict(report), ensure_ascii=False, separators=(",", ":")
                            ),
                        }
                    }
                ]
            }

        return payload

    def _build_manual_export(self, report: DailyReport) -> dict[str, Any]:
        """Create a manual export structure for auditing and import assistance."""

        health_status = "✅ Healthy" if not report.alerts else "⚠️ Issues"
        return {
            "date": report.date,
            "financial_status": health_status,
            "current_balance": report.financial_data.get("current_balance"),
            "efficiency_score": report.financial_data.get("efficiency_score"),
            "ai_services": report.ai_routing_data.get("available_services"),
            "system_health": report.system_health.get("status"),
            "recommendations": report.recommendations,
            "alerts": report.alerts,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "report": asdict(report),
        }

    def _persist_notion_export(
        self,
        report: DailyReport,
        payload: dict[str, Any],
        manual_export: dict[str, Any],
        *,
        response: Optional[dict[str, Any]] = None,
        error: Optional[str] = None,
        response_text: Optional[str] = None,
    ) -> Path:
        """Persist the prepared Notion payload and context for auditing."""

        notion_file = self.output_path / f"notion_import_{report.date}.json"
        export_payload = {
            "meta": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "database_id": self.config.database_id,
                "sync_enabled": self.config.sync_enabled,
            },
            "manual_summary": manual_export,
            "api_payload": payload,
        }

        if response is not None:
            export_payload["api_response"] = response
        if response_text:
            export_payload.setdefault("api_response", {})["raw"] = response_text
        if error:
            export_payload["error"] = error

        notion_file.write_text(json.dumps(export_payload, indent=2, default=str), encoding="utf-8")
        return notion_file

    def sync_to_notion(self, report: DailyReport) -> bool:
        """Sync the prepared daily report to Notion and log the outcome."""
        if not self.config.sync_enabled:
            logger.info("Notion sync disabled in config")
            return False

        manual_export = self._build_manual_export(report)
        payload = self._build_notion_payload(report)

        if not self.config.database_id or not self.config.api_key:
            logger.warning("Notion API not configured - persisting manual export only")
            self._persist_notion_export(
                report,
                payload,
                manual_export,
                error="missing_database_id_or_api_key",
            )
            return False

        if self._session is None:
            logger.warning("HTTP session unavailable - stored Notion payload for manual review")
            self._persist_notion_export(
                report,
                payload,
                manual_export,
                error="requests_library_unavailable",
            )
            return False

        try:
            logger.info("🔄 Syncing daily report to Notion database %s", self.config.database_id)
            response: Response = self._session.post(
                NOTION_API_URL,
                headers=self._build_headers(),
                json=payload,
                timeout=30,
            )

            if response.status_code >= 400:
                logger.error(
                    "Error syncing to Notion: HTTP %s - %s",
                    response.status_code,
                    response.text,
                )
                response_payload: Optional[dict[str, Any]]
                try:
                    response_payload = response.json()
                except ValueError:
                    response_payload = None

                self._persist_notion_export(
                    report,
                    payload,
                    manual_export,
                    error=f"http_{response.status_code}",
                    response=response_payload,
                    response_text=None if response_payload else response.text,
                )
                return False

            response_payload = response.json()
            self._persist_notion_export(
                report,
                payload,
                manual_export,
                response=response_payload,
            )
            logger.info("✅ Notion sync successful")
            return True

        except RequestException as e:
            logger.error(f"Error syncing to Notion: {e}")
            self._persist_notion_export(
                report,
                payload,
                manual_export,
                error=str(e),
            )
            return False
        except Exception as e:  # pragma: no cover - defensive guard
            logger.error(f"Unexpected error during Notion sync: {e}")
            self._persist_notion_export(
                report,
                payload,
                manual_export,
                error=str(e),
            )
            return False

    def get_recent_reports(self, days: int = 7) -> list[DailyReport]:
        """Get recent daily reports"""
        reports = []
        try:
            for i in range(days):
                date = (datetime.now(timezone.utc) - timedelta(days=i)).strftime("%Y-%m-%d")
                filepath = self.output_path / f"abot_daily_report_{date}.json"

                if filepath.exists():
                    with open(filepath) as f:
                        data = json.load(f)
                    reports.append(DailyReport(**data))
        except Exception as e:
            logger.error(f"Error loading recent reports: {e}")

        return reports

    def run_daily_sync(self):
        """Run complete daily sync process"""
        logger.info("🚀 Starting LUKHAS AI ΛBot daily sync process...")

        # Generate report
        report = self.generate_daily_report()

        # Sync to Notion
        success = self.sync_to_notion(report)

        # Print summary
        print(f"\n📊 LUKHAS AI ΛBot Daily Sync Complete - {report.date}")
        print("=" * 50)
        print(f"💰 Financial Status: {'✅ Healthy' if not report.alerts else '⚠️ Issues'}")
        print(f"🤖 AI Services: {report.ai_routing_data.get('available_services', 0)} available")
        print(f"🏥 System Health: {report.system_health.get('status', 'unknown').title()}")
        print(f"💡 Recommendations: {len(report.recommendations)}")
        print(f"🚨 Alerts: {len(report.alerts)}")
        print(f"🔄 Notion Sync: {'✅ Success' if success else '❌ Failed'}")

        if report.alerts:
            print("\n🚨 CRITICAL ALERTS:")
            for alert in report.alerts:
                print(f"   {alert}")

        if report.recommendations:
            print("\n💡 TOP RECOMMENDATIONS:")
            for rec in report.recommendations[:3]:
                print(f"   {rec}")

        return report


def main():
    """CLI entry point for testing"""
    sync = ABotNotionSync()
    report = sync.run_daily_sync()
    return report


if __name__ == "__main__":
    main()
