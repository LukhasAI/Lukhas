"""LUKHAS AI Products Package.

Consolidated products organized by functional domain:

- intelligence/   - Analytics, monitoring, and tracking systems
- communication/  - Messaging, attention, and social systems
- content/        - Content generation and creativity engines
- infrastructure/ - Core systems, legacy integration, and cloud platforms
- security/       - Security, privacy, and financial systems
- experience/     - Voice, UX, language, and visualization systems
- enterprise/     - Business-grade infrastructure and intelligence
- automation/     - AI agent frameworks and development tools
- shared/         - Common utilities and cross-product components

All lambda_core/ and lambda_products/ layers have been eliminated for simplicity.
"""
import logging
import time
from typing import Any, Optional

import streamlit as st

# Product category imports for easier access
from . import automation, communication, content, enterprise, experience, infrastructure, intelligence, security, shared

# Version info
__version__ = "2.0.0"
__author__ = "LUKHAS AI Team"

logger = logging.getLogger(__name__)


def get_products_catalog() -> dict[str, Any]:
    """Get comprehensive products catalog"""
    return {
        "version": __version__,
        "categories": {
            "intelligence": "Analytics, monitoring, and tracking systems",
            "communication": "Messaging, attention, and social systems",
            "content": "Content generation and creativity engines",
            "infrastructure": "Core systems, legacy integration, and cloud platforms",
            "security": "Security, privacy, and financial systems",
            "experience": "Voice, UX, language, and visualization systems",
            "enterprise": "Business-grade infrastructure and intelligence",
            "automation": "AI agent frameworks and development tools",
            "shared": "Common utilities and cross-product components",
        },
        "total_categories": 9,
        "status": "operational",
    }


def create_product_instance(
    category: str, product_type: str, config: Optional[dict[str, Any]] = None
) -> dict[str, Any]:
    """Create a product instance from the catalog"""
    catalog = get_products_catalog()

    if category not in catalog["categories"]:
        return {"status": "error", "error": f"Unknown category: {category}"}

    try:
        instance = {
            "category": category,
            "product_type": product_type,
            "config": config or {},
            "description": catalog["categories"][category],
            "created_at": __import__("time").time(),
            "status": "created",
            "instance_id": f"{category}_{product_type}_{hash(str(config))}",
        }
        logger.info(f"Product instance created: {category}/{product_type}")
        return instance
    except Exception as e:
        logger.error(f"Product instance creation failed: {e}")
        return {"status": "error", "error": str(e)}


def get_product_health() -> dict[str, Any]:
    """Get health status of all product categories"""
    health_status = {}

    for category in [
        "intelligence",
        "communication",
        "content",
        "infrastructure",
        "security",
        "experience",
        "enterprise",
        "automation",
        "shared",
    ]:
        try:
            # Check if category module is accessible
            category_module = getattr(sys.modules[__name__], category, None)
            health_status[category] = {
                "available": category_module is not None,
                "status": "operational" if category_module else "unavailable",
            }
        except Exception as e:
            health_status[category] = {"available": False, "status": "error", "error": str(e)}

    operational_count = sum(1 for status in health_status.values() if status["available"])

    return {
        "overall_health": f"{operational_count}/9 categories operational",
        "health_percentage": (operational_count / 9) * 100,
        "categories": health_status,
        "status": "healthy" if operational_count > 6 else "degraded" if operational_count > 3 else "critical",
    }


import sys

__all__ = [
    "__author__",
    # Version info
    "__version__",
    "automation",
    "communication",
    "content",
    "create_product_instance",
    "enterprise",
    "experience",
    "get_product_health",
    # Functional interfaces
    "get_products_catalog",
    "infrastructure",
    # Product categories
    "intelligence",
    "security",
    "shared",
]