"""Tool Security Incidents API ⚛️🛡️
View and manage tool governance security incidents.
"""

import time

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from lukhas_pwm.audit.tool_analytics import get_analytics, read_incidents

router = APIRouter(prefix="/tools", tags=["incidents"])


@router.get("/incidents")
def get_tool_incidents(limit: int = Query(100, ge=1, le=1000)):
    """Get recent tool security incidents"""
    incidents = read_incidents(limit=limit)
    analytics = get_analytics()

    return JSONResponse(
        content={
            "incidents": incidents,
            "total_count": len(incidents),
            "analytics_summary": analytics.get_analytics_summary(),
            "governance_status": {
                "monitoring": "active",
                "auto_tightening": "enabled",
                "incident_response": "automatic",
            },
        }
    )


@router.get("/incidents/stats")
def get_incident_statistics():
    """Get statistics about tool security incidents"""
    incidents = read_incidents(limit=1000)
    analytics = get_analytics()

    # Calculate statistics
    tool_attempts = {}
    recent_24h = []
    current_time = time.time()

    for incident in incidents:
        tool = incident.get("attempted_tool", "unknown")
        tool_attempts[tool] = tool_attempts.get(tool, 0) + 1

        # Check if within 24 hours
        if current_time - incident.get("timestamp", 0) < 86400:
            recent_24h.append(incident)

    return JSONResponse(
        content={
            "total_incidents": len(incidents),
            "incidents_24h": len(recent_24h),
            "most_attempted_tools": sorted(
                tool_attempts.items(), key=lambda x: x[1], reverse=True
            )[:10],
            "current_analytics": analytics.get_analytics_summary(),
            "recommendations": generate_recommendations(incidents, analytics),
        }
    )


def generate_recommendations(incidents, analytics):
    """Generate security recommendations based on incidents"""
    recommendations = []

    if len(incidents) > 10:
        recommendations.append(
            {
                "level": "warning",
                "message": "High number of blocked tool attempts detected",
                "action": "Review prompt templates and user education",
            }
        )

    # Check for repeated attempts
    tool_attempts = {}
    for incident in incidents[-50:]:  # Last 50 incidents
        tool = incident.get("attempted_tool", "unknown")
        tool_attempts[tool] = tool_attempts.get(tool, 0) + 1

    for tool, count in tool_attempts.items():
        if count > 5:
            recommendations.append(
                {
                    "level": "info",
                    "message": f"Tool '{tool}' frequently attempted but not allowed",
                    "action": f"Consider adding '{tool}' to allowlist if legitimate use case",
                }
            )

    if not recommendations:
        recommendations.append(
            {
                "level": "success",
                "message": "Tool governance operating normally",
                "action": "Continue monitoring",
            }
        )

    return recommendations


# Add time import for statistics
