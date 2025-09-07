"""
LUKHΛS Meta Log Route
=====================

Protected endpoint for viewing consent and system logs with symbolic tracking.
Displays Trinity Framework activity and glyph sequences.

Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
"""
from typing import List
import streamlit as st
from datetime import timezone

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from identity import AuthContext, get_current_user, require_t3_or_above

logger = logging.getLogger(__name__, timezone)

# Create router for log endpoints
log_router = APIRouter(prefix="/api/meta", tags=["meta-logs"])


def load_consent_logs(limit: int = 50) -> list[dict[str, Any]]:
    """
    Load consent logs from file with symbolic data.

    Returns:
        List of consent log entries with glyphs and Trinity data
    """
    logs = []

    # Primary source: consent log
    consent_log_path = Path("data/consent_log.jsonl")

    if consent_log_path.exists():
        try:
            with open(consent_log_path) as f:
                lines = f.readlines()
                # Get last N entries
                for line in lines[-limit:]:
                    try:
                        entry = json.loads(line.strip())
                        logs.append(entry)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.error(f"Error reading consent log: {e}")

    # Fallback: memory log
    if not logs:
        memory_log_path = Path("data/memory_log.json")
        if memory_log_path.exists():
            try:
                with open(memory_log_path) as f:
                    memory_data = json.load(f)
                    # Convert memory entries to log format
                    for entry in list(memory_data.get("entries", []))[-limit:]:
                        logs.append(
                            {
                                "timestamp": entry.get("timestamp", ""),
                                "action": "memory_fold",
                                "email": "system",
                                "glyphs": ["🧠", "💭"],
                                "trinity_framework": ["⚛️", "🧠", "🛡️"],
                                "data": entry,
                            }
                        )
            except Exception as e:
                logger.error(f"Error reading memory log: {e}")

    return logs


def enrich_log_entry(entry: dict[str, Any]) -> dict[str, Any]:
    """
    Enrich log entry with symbolic interpretation.

    Adds:
    - Glyph meanings
    - Trinity alignment
    - Risk indicators
    """
    enriched = entry.copy()

    # Add glyph interpretations
    glyph_meanings = {
        "⚛️": "Identity Core",
        "🧠": "Consciousness Active",
        "🛡️": "Guardian Protection",
        "🔐": "Security Layer",
        "🌍": "Cultural Awareness",
        "💭": "Memory Formation",
        "🔮": "Quantum Processing",
        "✨": "Dream State",
        "🌟": "Ethical Alignment",
    }

    enriched["glyph_meanings"] = {
        glyph: glyph_meanings.get(glyph, "Unknown Symbol") for glyph in entry.get("glyphs", [])
    }

    # Calculate Trinity alignment
    trinity_glyphs = entry.get("trinity_framework", [])
    trinity_score = len(set(trinity_glyphs) & {"⚛️", "🧠", "🛡️"}) / 3.0
    enriched["trinity_alignment"] = trinity_score

    # Add risk indicators
    action = entry.get("action", "")
    risk_level = "low"
    if "fail" in action or "error" in action:
        risk_level = "high"
    elif "drift" in action or "anomaly" in action:
        risk_level = "medium"

    enriched["risk_level"] = risk_level
    enriched["risk_indicator"] = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(risk_level, "⚪")

    return enriched


@log_router.get("/log")
async def get_meta_logs(limit: int = 50, user: AuthContext = Depends(require_t3_or_above)):
    """
    Get system logs with symbolic tracking.

    Requires T3+ tier for access to consciousness logs.

    Returns:
        - Log entries with glyphs and Trinity data
        - Enriched symbolic interpretations
        - Risk indicators and alignment scores
    """
    try:
        # Load raw logs
        logs = load_consent_logs(limit)

        # Enrich each entry
        enriched_logs = [enrich_log_entry(log) for log in logs]

        # Calculate summary statistics
        total_entries = len(enriched_logs)
        trinity_aligned = sum(1 for log in enriched_logs if log.get("trinity_alignment", 0) >= 0.7)
        risk_distribution = {
            "low": sum(1 for log in enriched_logs if log.get("risk_level") == "low"),
            "medium": sum(1 for log in enriched_logs if log.get("risk_level") == "medium"),
            "high": sum(1 for log in enriched_logs if log.get("risk_level") == "high"),
        }

        # Get unique glyphs used
        all_glyphs = set()
        for log in enriched_logs:
            all_glyphs.update(log.get("glyphs", []))

        return {
            "success": True,
            "user_tier": user.tier,
            "logs": enriched_logs,
            "summary": {
                "total_entries": total_entries,
                "trinity_aligned": trinity_aligned,
                "trinity_percentage": ((trinity_aligned / total_entries * 100) if total_entries > 0 else 0),
                "risk_distribution": risk_distribution,
                "unique_glyphs": list(all_glyphs),
                "time_range": {
                    "oldest": enriched_logs[0]["timestamp"] if enriched_logs else None,
                    "newest": enriched_logs[-1]["timestamp"] if enriched_logs else None,
                },
            },
            "viewer_context": {
                "tier": user.tier,
                "glyphs": user.glyphs,
                "trinity_score": user.trinity_score,
                "can_see_guardian_logs": user.tier == "T5",
            },
        }

    except Exception as e:
        logger.error(f"Error fetching meta logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch logs: {e!s}")


@log_router.get("/log/guardian")
async def get_guardian_logs(limit: int = 20, user: AuthContext = Depends(get_current_user)):
    """
    Get Guardian-specific intervention logs.

    Requires T5 (Guardian) tier for access.

    Returns Guardian decisions, interventions, and drift corrections.
    """
    if user.tier != "T5":
        raise HTTPException(status_code=403, detail="Guardian logs require T5 access")

    try:
        guardian_logs = []

        # Check for Guardian audit logs
        guardian_path = Path("guardian_audit/logs")
        if guardian_path.exists():
            for log_file in sorted(guardian_path.glob("*.json"))[-limit:]:
                try:
                    with open(log_file) as f:
                        log_data = json.load(f)
                        guardian_logs.append(
                            {
                                "timestamp": log_data.get("timestamp", ""),
                                "type": "guardian_intervention",
                                "action": log_data.get("action", ""),
                                "drift_score": log_data.get("drift_score", 0),
                                "intervention": log_data.get("intervention", {}),
                                "glyphs": ["🛡️", "⚡", "🔍"],
                                "trinity_framework": ["⚛️", "🧠", "🛡️"],
                                "severity": log_data.get("severity", "medium"),
                            }
                        )
                except Exception as e:
                    logger.error(f"Error reading guardian log {log_file}: {e}")

        # Enrich Guardian logs
        enriched_guardian_logs = [enrich_log_entry(log) for log in guardian_logs]

        return {
            "success": True,
            "guardian_tier_confirmed": True,
            "logs": enriched_guardian_logs,
            "guardian_summary": {
                "total_interventions": len(enriched_guardian_logs),
                "severity_distribution": {
                    "low": sum(1 for log in enriched_guardian_logs if log.get("severity") == "low"),
                    "medium": sum(1 for log in enriched_guardian_logs if log.get("severity") == "medium"),
                    "high": sum(1 for log in enriched_guardian_logs if log.get("severity") == "high"),
                    "critical": sum(1 for log in enriched_guardian_logs if log.get("severity") == "critical"),
                },
                "average_drift": (
                    sum(log.get("drift_score", 0) for log in enriched_guardian_logs) / len(enriched_guardian_logs)
                    if enriched_guardian_logs
                    else 0
                ),
            },
            "guardian_glyphs": ["🛡️", "⚔️", "🔮", "⚡", "🌟"],
        }

    except Exception as e:
        logger.error(f"Error fetching guardian logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch guardian logs: {e!s}")


@log_router.get("/log/export")
async def export_logs(format: str = "json", user: AuthContext = Depends(require_t3_or_above)):
    """
    Export logs in various formats.

    Formats:
    - json: Raw JSON data
    - csv: Comma-separated values
    - symbolic: Glyph-focused format
    """
    try:
        logs = load_consent_logs(100)  # Get more for export
        enriched_logs = [enrich_log_entry(log) for log in logs]

        if format == "json":
            return {
                "format": "json",
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "exported_by": user.email,
                "data": enriched_logs,
            }

        elif format == "csv":
            # Convert to CSV format
            csv_lines = ["timestamp,email,action,glyphs,trinity_score,risk_level"]
            for log in enriched_logs:
                glyphs_str = " ".join(log.get("glyphs", []))
                csv_lines.append(
                    f"{log.get('timestamp', '')},{log.get('email', '')},{log.get('action', '')},"
                    f"{glyphs_str},{log.get('trinity_alignment', 0)},{log.get('risk_level', '')}"
                )

            return {"format": "csv", "data": "\n".join(csv_lines)}

        elif format == "symbolic":
            # Symbolic representation
            symbolic_logs = []
            for log in enriched_logs:
                symbolic_logs.append(
                    {
                        "glyphs": " ".join(log.get("glyphs", [])),
                        "trinity": " ".join(log.get("trinity_framework", [])),
                        "risk": log.get("risk_indicator", "⚪"),
                        "action": log.get("action", ""),
                        "time": (
                            log.get("timestamp", "").split("T")[1].split(".")[0]
                            if "T" in log.get("timestamp", "")
                            else ""
                        ),
                    }
                )

            return {
                "format": "symbolic",
                "legend": {
                    "⚛️": "Identity",
                    "🧠": "Consciousness",
                    "🛡️": "Guardian",
                    "🟢": "Low Risk",
                    "🟡": "Medium Risk",
                    "🔴": "High Risk",
                },
                "data": symbolic_logs,
            }

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format: {format}. Use json, csv, or symbolic",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export logs: {e!s}")
