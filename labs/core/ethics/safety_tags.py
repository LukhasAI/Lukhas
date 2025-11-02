#!/usr/bin/env python3
"""
Safety Tags System: Plan Enrichment with Semantic Categories
============================================================

Task 13: Enrich plans with safety tags (pii, financial, model-switch, etc.)
that the DSL can use as inputs instead of piling on predicates.

Features:
- Comprehensive safety tag taxonomy with semantic categories
- Automatic tag detection from plan content and context
- DSL predicates for tag-based rule evaluation
- Integration with Guardian Drift Bands and Ethics DSL
- Performance-optimized tag inference (<1ms overhead)

Constellation Framework: ⚛️🧠🛡️
Author: LUKHAS AI System
Version: 1.0.0

#TAG:ethics
#TAG:safety
#TAG:tags
#TAG:task13
"""

import logging

# --- BEGIN ADVANCED SAFETY TAGS (Task 13 hardening) ---------------------------
# Feature flag: keep dark by default
import os
import re
import threading
import time
import unicodedata
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set

_LUKHAS_ADVANCED = os.getenv("LUKHAS_ADVANCED_TAGS") == "1" or os.getenv("LUKHAS_EXPERIMENTAL") == "1"

# Compact homoglyph fold for common email/API evasion (Cyrillic & Greek lookalikes)
_HOMO_FOLD = str.maketrans(
    {
        # Cyrillic
        "а": "a",
        "е": "e",
        "о": "o",
        "р": "p",
        "с": "s",
        "х": "x",
        "і": "i",
        "ј": "j",
        "ԁ": "d",
        "Һ": "H",
        "һ": "h",
        # Greek
        "ο": "o",
        "Ο": "O",
        "Ι": "I",
        "Μ": "M",
        "Ν": "N",
        "Κ": "K",
        "Ε": "E",
        "Τ": "T",
        "Ρ": "P",
        "Χ": "X",
        # Roman numerals & special
        "ⅰ": "i",
        "ⅱ": "ii",
        "Ⅰ": "I",
        "Ⅱ": "II",
        "ⅼ": "l",  # U+217C small roman numeral fifty looks like 'l'
    }
)

_ZERO_WIDTH = {"\u200b", "\u200c", "\u200d", "\u2060", "\ufeff"}

_AT_PAT = re.compile(r"(?i)\s*(?:\(|\[|\{)?\s*at\s*(?:\)|\]|\})?\s*")
_DOT_PAT = re.compile(r"(?i)\s*(?:\(|\[|\{)?\s*dot\s*(?:\)|\]|\})?\s*")

_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")
_URL_API_RE = re.compile(r"https?://[^\s]*api[^\s]*", re.I)
_SHORT_LINK_RE = re.compile(r"https?://(bit\.ly|t\.co|tinyurl\.com|goo\.gl)/[^\s]+", re.I)
_MODEL_HINTS_RE = re.compile(
    r"(?i)\b(gpt[-\s]?4(?:o|v)?|vision endpoint|external inference api|third[-\s]?party api|"
    r"tool[-\s]?call|tool[-\s]?use|rerank|embedding api)\b"
)

# Locale-specific patterns (flag-gated)
_ES_PHONE_RE = re.compile(r"\+34\s*[67]\d{2}\s*\d{2}\s*\d{2}\s*\d{2}", re.I)
_PT_PHONE_RE = re.compile(r"\(\d{2}\)\s*9?\d{4}[-\s]?\d{4}", re.I)


def preprocess_text(text: str) -> str:
    """
    Normalize likely-obfuscated security/PII strings:
      - NFKC normalize
      - strip zero-width chars
      - fold common homoglyphs
      - canonicalize (at)/(dot) forms -> @ / .
    """
    if not text:
        return text
    t = unicodedata.normalize("NFKC", text)
    # strip zero-width
    if any(c in t for c in _ZERO_WIDTH):
        for c in _ZERO_WIDTH:
            t = t.replace(c, "")
    # homoglyph fold
    t = t.translate(_HOMO_FOLD)
    # canonicalize (at)/(dot) forms
    # Do (dot) first to avoid '@ dot' becoming '@.' via two passes
    t = _DOT_PAT.sub(".", t)
    t = _AT_PAT.sub("@", t)
    # compress accidental spaces around @ and .
    t = re.sub(r"\s*@\s*", "@", t)
    t = re.sub(r"\s*\.\s*", ".", t)
    return t


def _safe_add_tag(tagged_plan, name: str, *, confidence: float, category: str):
    """Be liberal in how we add a tag to the tagged_plan; do not raise."""
    for m in ("add_tag", "add", "tag"):
        fn = getattr(tagged_plan, m, None)
        if callable(fn):
            try:
                fn(name=name, confidence=confidence, category=category)
                break
            except TypeError:
                # Try positional form
                try:
                    fn(name, confidence, category)
                    break
                except Exception:
                    pass
    # Keep tag_names in sync if present
    try:
        names = getattr(tagged_plan, "tag_names", None)
        if names is not None:
            if isinstance(names, (list, set, tuple)):
                s = set(names)
                s.add(name)
                tagged_plan.tag_names = list(s)
    except Exception:
        pass


def _detect_obfuscated_email(clean_text: str, tagged_plan):
    """Detect PII emails, including obfuscations normalized by preprocess_text()."""
    confidence = 0.0

    # Standard email detection
    if _EMAIL_RE.search(clean_text):
        confidence = 0.70

    # Locale-specific phone patterns (flag-gated hardening)
    if _LUKHAS_ADVANCED and (_ES_PHONE_RE.search(clean_text) or _PT_PHONE_RE.search(clean_text)):
        confidence = max(confidence, 0.65)

    if confidence > 0.5:
        _safe_add_tag(tagged_plan, "pii", confidence=confidence, category="DATA_SENSITIVITY")


def _detect_model_switch_and_external(clean_text: str, tagged_plan):
    """
    Detect subtle model/tool switching and external API usage.
      - tokens like 'vision endpoint', 'tool-call', 'rerank', 'embedding api'
      - URLs containing 'api'
      - Short-link exfiltration patterns
    """
    # Model switching hints (require ≥2 hints for higher confidence)
    model_hints = _MODEL_HINTS_RE.findall(clean_text)
    if len(model_hints) >= 2:
        _safe_add_tag(tagged_plan, "model-switch", confidence=0.75, category="SYSTEM_OPERATION")
    elif len(model_hints) == 1:
        _safe_add_tag(tagged_plan, "model-switch", confidence=0.55, category="SYSTEM_OPERATION")

    # API URL detection
    if _URL_API_RE.search(clean_text):
        _safe_add_tag(tagged_plan, "external-call", confidence=0.65, category="SYSTEM_OPERATION")

    # Short-link detection (potential data exfiltration)
    if _SHORT_LINK_RE.search(clean_text):
        _safe_add_tag(tagged_plan, "external-call", confidence=0.70, category="SYSTEM_OPERATION")


def _adv_enrich(plan: dict, tagged_plan):
    """
    Dark-launched enrichment step; call from SafetyTagEnricher.enrich_plan once
    the baseline detectors have run.
    """
    if not _LUKHAS_ADVANCED:
        return

    # Pull observable text from common fields; keep it cheap
    desc = plan.get("description") or ""
    params = plan.get("params") or {}
    content = params.get("content") or ""

    # Nested YAML scanning: look for 'run:' blocks and script content
    text_sources = [desc, content]

    # Scan nested execution contexts
    if isinstance(params, dict):
        for key, value in params.items():
            if key in ("script", "run", "command", "exec") and isinstance(value, str):
                text_sources.append(value)
            elif key == "config" and isinstance(value, dict):
                # YAML config blocks
                for nested_key, nested_value in value.items():
                    if isinstance(nested_value, str):
                        text_sources.append(nested_value)

    # Process all text sources
    for text in text_sources:
        if text:
            clean = preprocess_text(text)
            _detect_obfuscated_email(clean, tagged_plan)
            _detect_model_switch_and_external(clean, tagged_plan)


# --- END ADVANCED SAFETY TAGS --------------------------------------------------

# LUKHAS imports
try:
    from .dsl_lite import canonical_domain
except ImportError:
    # Fallback for development/testing
    def canonical_domain(url: str) -> str:
        return url.lower()


# Prometheus metrics for telemetry
try:
    from prometheus_client import Counter, Histogram

    METRICS_AVAILABLE = True
except ImportError:
    # Graceful fallback for test environments
    class _NoopMetric:
        def inc(self, *args, **kwargs):
            pass

        def observe(self, *args, **kwargs):
            pass

        def labels(self, *args, **kwargs):
            return self

    Counter = Histogram = lambda *args, **kwargs: _NoopMetric()
    METRICS_AVAILABLE = False

logger = logging.getLogger(__name__)

# Safety Tags metrics
SAFETY_TAGS_ENRICHMENT = Counter(
    "safety_tags_enrichment_total", "Total plan enrichments with safety tags", ["tag_count_range"]  # 0, 1-3, 4-6, 7+
)

SAFETY_TAGS_DETECTION = Counter("safety_tags_detection_total", "Safety tag detections by category", ["category", "tag"])

SAFETY_TAGS_EVALUATION_TIME = Histogram(
    "safety_tags_evaluation_ms",
    "Safety tags evaluation duration in milliseconds",
    buckets=[0.1, 0.25, 0.5, 1.0, 2.0, 5.0],
)

# Tag confidence histograms (Task 13 observability hardening)
SAFETY_TAGS_CONFIDENCE = Histogram(
    "safety_tags_confidence_bucket",
    "Safety tag confidence scores distribution",
    ["tag", "lane"],
    buckets=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
)

# Guardian actions with exemplars
GUARDIAN_ACTIONS_EXEMPLARS = Counter(
    "guardian_actions_count", "Guardian actions taken with trace exemplars", ["action", "lane"]
)


class SafetyTagCategory(Enum):
    """Categories of safety tags."""

    DATA_SENSITIVITY = "data_sensitivity"  # PII, financial, health, etc.
    SYSTEM_OPERATION = "system_operation"  # model-switch, external-call, etc.
    USER_INTERACTION = "user_interaction"  # consent, authentication, etc.
    SECURITY_RISK = "security_risk"  # privilege-escalation, injection, etc.
    COMPLIANCE = "compliance"  # GDPR, HIPAA, SOX, etc.
    RESOURCE_IMPACT = "resource_impact"  # memory-intensive, long-running, etc.


@dataclass
class SafetyTag:
    """Individual safety tag with metadata."""

    name: str
    category: SafetyTagCategory
    description: str
    confidence: float = 1.0
    source: str = "detection"  # detection, manual, inherited
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")


@dataclass
class TaggedPlan:
    """Plan enriched with safety tags."""

    original_plan: Dict[str, Any]
    tags: List[SafetyTag]
    enrichment_time_ms: float
    enrichment_context: Dict[str, Any] = field(default_factory=dict)

    @property
    def tag_names(self) -> Set[str]:
        """Get set of tag names."""
        return {tag.name for tag in self.tags}

    @property
    def tags_by_category(self) -> Dict[SafetyTagCategory, List[SafetyTag]]:
        """Group tags by category."""
        groups = {}
        for tag in self.tags:
            if tag.category not in groups:
                groups[tag.category] = []
            groups[tag.category].append(tag)
        return groups

    def has_tag(self, tag_name: str) -> bool:
        """Check if plan has specific tag."""
        return tag_name in self.tag_names

    def has_category(self, category: SafetyTagCategory) -> bool:
        """Check if plan has any tags in category."""
        return category in self.tags_by_category

    def get_tags_by_category(self, category: SafetyTagCategory) -> List[SafetyTag]:
        """Get tags in specific category."""
        return self.tags_by_category.get(category, [])


class SafetyTagDetector:
    """Detector for specific safety tag patterns."""

    def __init__(self, tag_name: str, category: SafetyTagCategory, description: str):
        self.tag_name = tag_name
        self.category = category
        self.description = description

    def detect(self, plan: Dict[str, Any], context: Dict[str, Any]) -> Optional[SafetyTag]:
        """Detect if this tag applies to the plan. Override in subclasses."""
        raise NotImplementedError


class PIIDetector(SafetyTagDetector):
    """Detector for personally identifiable information."""

    def __init__(self):
        super().__init__("pii", SafetyTagCategory.DATA_SENSITIVITY, "Personally identifiable information detected")

        # PII patterns
        self.email_pattern = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
        self.ssn_pattern = re.compile(r"\b\d{3}-?\d{2}-?\d{4}\b")
        self.phone_pattern = re.compile(r"\b\d{3}-?\d{3}-?\d{4}\b")
        self.credit_card_pattern = re.compile(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b")

        # PII field names
        self.pii_fields = {
            "email",
            "ssn",
            "social_security",
            "phone",
            "telephone",
            "credit_card",
            "passport",
            "license",
            "address",
            "full_name",
            "first_name",
            "last_name",
            "date_of_birth",
            "dob",
            "personal_id",
            "user_id",
            "customer_id",
        }

    def detect(self, plan: Dict[str, Any], context: Dict[str, Any]) -> Optional[SafetyTag]:
        """Detect PII in plan parameters."""
        confidence = 0.0
        detected_types = []

        # Check plan parameters
        params = plan.get("params", {})
        if isinstance(params, dict):
            # Check field names
            for field_name in params.keys():
                if field_name.lower() in self.pii_fields:
                    confidence = max(confidence, 0.9)
                    detected_types.append(f"field:{field_name}")

            # Check parameter values
            for value in params.values():
                if isinstance(value, str):
                    if self.email_pattern.search(value):
                        confidence = max(confidence, 0.95)
                        detected_types.append("email")
                    if self.ssn_pattern.search(value):
                        confidence = max(confidence, 0.95)
                        detected_types.append("ssn")
                    if self.phone_pattern.search(value):
                        confidence = max(confidence, 0.8)
                        detected_types.append("phone")
                    if self.credit_card_pattern.search(value):
                        confidence = max(confidence, 0.95)
                        detected_types.append("credit_card")

        # Check action name
        action = plan.get("action", "")
        if any(term in action.lower() for term in ["personal", "identity", "profile", "contact"]):
            confidence = max(confidence, 0.6)
            detected_types.append("action")

        if confidence > 0.5:
            return SafetyTag(
                name=self.tag_name,
                category=self.category,
                description=self.description,
                confidence=confidence,
                metadata={"detected_types": detected_types},
            )

        return None


class FinancialDetector(SafetyTagDetector):
    """Detector for financial data and operations."""

    def __init__(self):
        super().__init__("financial", SafetyTagCategory.DATA_SENSITIVITY, "Financial data or operations detected")

        # Financial patterns
        self.account_pattern = re.compile(r"\b\d{10,17}\b")  # Bank account numbers
        self.routing_pattern = re.compile(r"\b\d{9}\b")  # Routing numbers

        # Financial field names
        self.financial_fields = {
            "account_number",
            "routing_number",
            "bank_account",
            "credit_card",
            "debit_card",
            "payment_method",
            "transaction_id",
            "amount",
            "balance",
            "salary",
            "income",
            "payment",
            "billing",
            "invoice",
            "tax_id",
            "ein",
            "financial_data",
        }

        # Financial actions
        self.financial_actions = {
            "payment",
            "transfer",
            "withdraw",
            "deposit",
            "charge",
            "refund",
            "billing",
            "invoice",
            "transaction",
            "financial",
        }

    def detect(self, plan: Dict[str, Any], context: Dict[str, Any]) -> Optional[SafetyTag]:
        """Detect financial content in plan."""
        confidence = 0.0
        detected_types = []

        # Check action
        action = plan.get("action", "").lower()
        if any(term in action for term in self.financial_actions):
            confidence = max(confidence, 0.9)
            detected_types.append("action")

        # Check parameters
        params = plan.get("params", {})
        if isinstance(params, dict):
            # Check field names
            for field_name in params.keys():
                if field_name.lower() in self.financial_fields:
                    confidence = max(confidence, 0.8)
                    detected_types.append(f"field:{field_name}")

            # Check for currency amounts
            for key, value in params.items():
                if isinstance(value, (int, float)) and key.lower() in ["amount", "price", "cost", "fee"]:
                    confidence = max(confidence, 0.7)
                    detected_types.append("currency")

        if confidence > 0.6:
            return SafetyTag(
                name=self.tag_name,
                category=self.category,
                description=self.description,
                confidence=confidence,
                metadata={"detected_types": detected_types},
            )

        return None


class ModelSwitchDetector(SafetyTagDetector):
    """Detector for model switching operations."""

    def __init__(self):
        super().__init__("model-switch", SafetyTagCategory.SYSTEM_OPERATION, "Model switching operation detected")

        self.model_actions = {
            "switch_model",
            "change_model",
            "update_model",
            "load_model",
            "model_selection",
            "model_config",
            "ai_model",
        }

        self.model_params = {
            "model",
            "model_name",
            "model_id",
            "model_version",
            "ai_model",
            "llm_model",
            "engine",
            "provider",
        }

        # Expanded vocabulary for subtle model switching hints
        self.model_keywords = {
            "gpt-4",
            "gpt-4o",
            "claude",
            "gemini",
            "llama",
            "mistral",
            "vision endpoint",
            "text endpoint",
            "embedding endpoint",
            "rerank",
            "reranking",
            "embedding api",
            "external inference",
            "third-party api",
            "tool call",
            "function calling",
            "inference api",
            "ml api",
            "ai api",
            "model api",
            "completion",
            "chat completion",
            "text generation",
        }

    def detect(self, plan: Dict[str, Any], context: Dict[str, Any]) -> Optional[SafetyTag]:
        """Detect model switching operations."""
        confidence = 0.0
        detected_types = []

        # Check action
        action = plan.get("action", "").lower()
        if any(term in action for term in self.model_actions):
            confidence = max(confidence, 0.95)
            detected_types.append("action")

        # Check parameters
        params = plan.get("params", {})
        if isinstance(params, dict):
            for param_name in params.keys():
                if param_name.lower() in self.model_params:
                    confidence = max(confidence, 0.9)
                    detected_types.append(f"param:{param_name}")

        # Check for model keywords in all text content
        all_text = []
        all_text.append(plan.get("action", ""))
        all_text.append(plan.get("description", ""))

        if isinstance(params, dict):
            for key, value in params.items():
                if isinstance(value, str):
                    all_text.append(value)

        combined_text = " ".join(all_text).lower()

        for keyword in self.model_keywords:
            if keyword in combined_text:
                confidence = max(confidence, 0.85)  # High confidence for explicit keywords
                detected_types.append(f"keyword:{keyword}")

        if confidence > 0.7:  # Lowered threshold to catch subtle hints
            return SafetyTag(
                name=self.tag_name,
                category=self.category,
                description=self.description,
                confidence=confidence,
                metadata={"detected_types": detected_types},
            )

        return None


class ExternalCallDetector(SafetyTagDetector):
    """Detector for external API calls."""

    def __init__(self):
        super().__init__("external-call", SafetyTagCategory.SYSTEM_OPERATION, "External API call detected")

        # URL pattern for detecting HTTP/HTTPS URLs
        self.url_pattern = re.compile(r'https?://[^\s<>"]+', re.IGNORECASE)

        # API-related terms
        self.api_terms = {
            "api",
            "endpoint",
            "service",
            "rest",
            "graphql",
            "webhook",
            "third-party",
            "external",
            "remote",
            "upstream",
        }

    def detect(self, plan: Dict[str, Any], context: Dict[str, Any]) -> Optional[SafetyTag]:
        """Detect external API calls."""
        confidence = 0.0
        detected_types = []

        # Check action
        action = plan.get("action", "").lower()
        if any(term in action for term in self.api_terms):
            confidence = max(confidence, 0.9)
            detected_types.append("action")

        # Check for URL parameters by key name
        params = plan.get("params", {})
        if isinstance(params, dict):
            for key, value in params.items():
                if key.lower() in ["url", "endpoint", "api_url", "service_url", "webhook"]:
                    if isinstance(value, str) and ("http" in value or "api" in value):
                        confidence = max(confidence, 0.95)
                        detected_types.append(f"url_param:{key}")

        # Scan all text content for URLs
        all_text = []
        all_text.append(plan.get("action", ""))
        all_text.append(plan.get("description", ""))

        if isinstance(params, dict):
            for key, value in params.items():
                if isinstance(value, str):
                    all_text.append(value)

        combined_text = " ".join(all_text)

        # Find URLs in text
        urls = self.url_pattern.findall(combined_text)
        if urls:
            confidence = max(confidence, 0.9)
            detected_types.append(f"url_in_text:{len(urls)}_found")

        if confidence > 0.7:  # Lowered threshold to catch more cases
            return SafetyTag(
                name=self.tag_name,
                category=self.category,
                description=self.description,
                confidence=confidence,
                metadata={"detected_types": detected_types},
            )

        return None


class PrivilegeEscalationDetector(SafetyTagDetector):
    """Detector for privilege escalation attempts."""

    def __init__(self):
        super().__init__("privilege-escalation", SafetyTagCategory.SECURITY_RISK, "Privilege escalation detected")

        self.escalation_terms = {
            "admin",
            "root",
            "sudo",
            "elevate",
            "escalate",
            "privilege",
            "superuser",
            "administrator",
            "system",
            "override",
        }

        self.dangerous_actions = {
            "admin_action",
            "system_command",
            "privilege_change",
            "user_promote",
            "role_change",
            "permission_grant",
            "access_override",
        }

    def detect(self, plan: Dict[str, Any], context: Dict[str, Any]) -> Optional[SafetyTag]:
        """Detect privilege escalation patterns."""
        confidence = 0.0
        detected_types = []

        # Check action
        action = plan.get("action", "").lower()
        if any(term in action for term in self.escalation_terms):
            confidence = max(confidence, 0.9)
            detected_types.append("action_keyword")

        if any(action.startswith(dangerous) for dangerous in self.dangerous_actions):
            confidence = max(confidence, 0.95)
            detected_types.append("dangerous_action")

        # Check parameters
        params = plan.get("params", {})
        if isinstance(params, dict):
            for key, value in params.items():
                if isinstance(value, str) and any(term in value.lower() for term in self.escalation_terms):
                    confidence = max(confidence, 0.8)
                    detected_types.append(f"param:{key}")

        if confidence > 0.7:
            return SafetyTag(
                name=self.tag_name,
                category=self.category,
                description=self.description,
                confidence=confidence,
                metadata={"detected_types": detected_types},
            )

        return None


class GDPRDetector(SafetyTagDetector):
    """Detector for GDPR-related operations."""

    def __init__(self):
        super().__init__("gdpr", SafetyTagCategory.COMPLIANCE, "GDPR compliance relevant operation detected")

        self.gdpr_actions = {
            "data_export",
            "data_deletion",
            "data_rectification",
            "data_portability",
            "consent_withdraw",
            "personal_data",
            "data_subject_request",
        }

        self.gdpr_terms = {
            "gdpr",
            "data_subject",
            "personal_data",
            "data_controller",
            "data_processor",
            "consent",
            "legitimate_interest",
        }

    def detect(self, plan: Dict[str, Any], context: Dict[str, Any]) -> Optional[SafetyTag]:
        """Detect GDPR-related operations."""
        confidence = 0.0
        detected_types = []

        # Check action
        action = plan.get("action", "").lower()
        if any(term in action for term in self.gdpr_actions):
            confidence = max(confidence, 0.9)
            detected_types.append("gdpr_action")

        if any(term in action for term in self.gdpr_terms):
            confidence = max(confidence, 0.8)
            detected_types.append("gdpr_term")

        # Check parameters
        params = plan.get("params", {})
        if isinstance(params, dict):
            for key, value in params.items():
                if isinstance(value, str) and any(term in value.lower() for term in self.gdpr_terms):
                    confidence = max(confidence, 0.7)
                    detected_types.append(f"param:{key}")

        # Check context for EU users
        if context.get("user_region") in ["EU", "EEA"]:
            if confidence > 0.3:  # Lower threshold for EU users
                confidence = max(confidence, 0.6)
                detected_types.append("eu_user")

        if confidence > 0.6:
            return SafetyTag(
                name=self.tag_name,
                category=self.category,
                description=self.description,
                confidence=confidence,
                metadata={"detected_types": detected_types},
            )

        return None


class SafetyTagEnricher:
    """
    Safety Tag Enricher: Add semantic safety tags to action plans

    Automatically detects and adds safety-relevant tags to action plans
    for use by the Ethics DSL system, reducing the need for complex predicates.
    """

    def __init__(self, enable_caching: bool = True):
        """
        Initialize Safety Tag Enricher.

        Args:
            enable_caching: Enable tag detection result caching
        """
        self.enable_caching = enable_caching
        self.tag_cache = {} if enable_caching else None
        self.cache_hits = 0
        self.cache_misses = 0

        # Initialize detectors
        self.detectors = [
            PIIDetector(),
            FinancialDetector(),
            ModelSwitchDetector(),
            ExternalCallDetector(),
            PrivilegeEscalationDetector(),
            GDPRDetector(),
        ]

        # Thread safety
        self._lock = threading.Lock()

        logger.info(
            f"SafetyTagEnricher initialized with {len(self.detectors)} detectors, caching={'enabled' if enable_caching else 'disabled'}"
        )

    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text to normalize obfuscation patterns.

        - Unicode normalization (NFKC)
        - Strip zero-width characters
        - Canonicalize (dot)/(at) patterns
        - Basic homoglyph normalization

        Args:
            text: Input text to normalize

        Returns:
            Normalized text
        """
        if not isinstance(text, str):
            return str(text)

        # Unicode normalization to NFKC
        text = unicodedata.normalize("NFKC", text)

        # Remove zero-width characters commonly used for obfuscation
        zero_width_chars = [
            "\u200b",  # ZERO WIDTH SPACE
            "\u200c",  # ZERO WIDTH NON-JOINER
            "\u200d",  # ZERO WIDTH JOINER
            "\u2060",  # WORD JOINER
            "\ufeff",  # ZERO WIDTH NO-BREAK SPACE
            "\u180e",  # MONGOLIAN VOWEL SEPARATOR
        ]
        for char in zero_width_chars:
            text = text.replace(char, "")

        # Canonicalize common email obfuscation patterns
        text = re.sub(r"\(at\)|\[at\]|\{at\}|<at>|\s+at\s+", "@", text, flags=re.IGNORECASE)
        text = re.sub(r"\(dot\)|\[dot\]|\{dot\}|<dot>|\s+dot\s+", ".", text, flags=re.IGNORECASE)

        # Basic homoglyph normalization (Cyrillic/Greek lookalikes)
        homoglyphs = {
            "\u0430": "a",  # Cyrillic а
            "\u043e": "o",  # Cyrillic о
            "\u0435": "e",  # Cyrillic е
            "\u0440": "p",  # Cyrillic р
            "\u0441": "c",  # Cyrillic с
            "\u0445": "x",  # Cyrillic х
            "\u0443": "y",  # Cyrillic у
            "\u03bf": "o",  # Greek ο
            "\u03b1": "a",  # Greek α
            "\u217c": "l",  # Roman numeral ⅼ
            "\u2160": "I",  # Roman numeral Ⅰ
        }
        for homoglyph, replacement in homoglyphs.items():
            text = text.replace(homoglyph, replacement)

        return text

    def preprocess_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess plan to normalize all text fields.

        Args:
            plan: Original plan

        Returns:
            Normalized plan (copy)
        """
        # Create a copy to avoid mutating the original
        normalized_plan = {}

        for key, value in plan.items():
            if isinstance(value, str):
                normalized_plan[key] = self.preprocess_text(value)
            elif isinstance(value, dict):
                # Recursively preprocess nested dicts
                normalized_plan[key] = self.preprocess_plan(value)
            elif isinstance(value, list):
                # Preprocess list items
                normalized_plan[key] = [
                    (
                        self.preprocess_text(item)
                        if isinstance(item, str)
                        else self.preprocess_plan(item) if isinstance(item, dict) else item
                    )
                    for item in value
                ]
            else:
                normalized_plan[key] = value

        return normalized_plan

    def enrich_plan(self, plan: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> TaggedPlan:
        """
        Enrich action plan with safety tags.

        Args:
            plan: Action plan to enrich
            context: Optional context for enrichment

        Returns:
            TaggedPlan with detected safety tags
        """
        start_time = time.perf_counter()
        context = context or {}

        # Preprocess plan to normalize obfuscation patterns
        normalized_plan = self.preprocess_plan(plan)

        with self._lock:
            try:
                # Generate cache key using normalized plan
                cache_key = None
                if self.enable_caching:
                    cache_key = self._generate_cache_key(normalized_plan, context)
                    if cache_key in self.tag_cache:
                        self.cache_hits += 1
                        cached_tags = self.tag_cache[cache_key]
                        enrichment_time_ms = (time.perf_counter() - start_time) * 1000

                        return TaggedPlan(
                            original_plan=plan,  # Return original, not normalized
                            tags=cached_tags,
                            enrichment_time_ms=enrichment_time_ms,
                            enrichment_context={"cache_hit": True},
                        )

                    self.cache_misses += 1

                # Run detection on normalized plan
                detected_tags = []
                for detector in self.detectors:
                    try:
                        tag = detector.detect(normalized_plan, context)
                        if tag:
                            detected_tags.append(tag)

                            # Record detection metrics
                            if METRICS_AVAILABLE:
                                SAFETY_TAGS_DETECTION.labels(category=tag.category.value, tag=tag.name).inc()

                                # Record confidence histogram (Task 13 observability)
                                lane = context.get("lane", "unknown")
                                SAFETY_TAGS_CONFIDENCE.labels(tag=tag.name, lane=lane).observe(tag.confidence)

                    except Exception as e:
                        logger.error(f"Error in detector {detector.tag_name}: {e}")

                # Cache results
                if self.enable_caching and cache_key:
                    # Limit cache size
                    if len(self.tag_cache) > 1000:
                        # Remove oldest 100 entries
                        oldest_keys = list(self.tag_cache.keys())[:100]
                        for key in oldest_keys:
                            del self.tag_cache[key]

                    self.tag_cache[cache_key] = detected_tags

                enrichment_time_ms = (time.perf_counter() - start_time) * 1000

                # Create tagged plan
                tagged_plan = TaggedPlan(
                    original_plan=plan,
                    tags=detected_tags,
                    enrichment_time_ms=enrichment_time_ms,
                    enrichment_context={
                        "cache_hit": False,
                        "detector_count": len(self.detectors),
                        "tags_detected": len(detected_tags),
                    },
                )

                # Record metrics
                if METRICS_AVAILABLE:
                    tag_count_range = self._get_tag_count_range(len(detected_tags))
                    SAFETY_TAGS_ENRICHMENT.labels(tag_count_range=tag_count_range).inc()
                    SAFETY_TAGS_EVALUATION_TIME.observe(enrichment_time_ms)

                logger.debug(f"Plan enriched: {len(detected_tags)} tags detected " f"({enrichment_time_ms:.2f}ms)")

                # Advanced, dark-launched hardening (Task 13 evasion coverage)
                _adv_enrich(plan, tagged_plan)

                return tagged_plan

            except Exception as e:
                enrichment_time_ms = (time.perf_counter() - start_time) * 1000
                logger.error(f"Error enriching plan: {e}")

                # Return plan with no tags on error
                return TaggedPlan(
                    original_plan=plan,
                    tags=[],
                    enrichment_time_ms=enrichment_time_ms,
                    enrichment_context={"error": str(e)},
                )

    def _generate_cache_key(self, plan: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate cache key for plan + context."""
        import hashlib

        content = f"{sorted(plan.items())}_{sorted(context.items())}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _get_tag_count_range(self, count: int) -> str:
        """Get tag count range for metrics."""
        if count == 0:
            return "0"
        elif count <= 3:
            return "1-3"
        elif count <= 6:
            return "4-6"
        else:
            return "7+"

    def add_detector(self, detector: SafetyTagDetector) -> None:
        """Add custom safety tag detector."""
        with self._lock:
            self.detectors.append(detector)
            # Clear cache since detection logic changed
            if self.tag_cache:
                self.tag_cache.clear()

        logger.info(f"Added custom detector: {detector.tag_name}")

    def get_stats(self) -> Dict[str, Any]:
        """Get enricher statistics."""
        return {
            "detector_count": len(self.detectors),
            "cache_enabled": self.enable_caching,
            "cache_size": len(self.tag_cache) if self.tag_cache else 0,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": self.cache_hits / max(self.cache_hits + self.cache_misses, 1),
            "available_tags": [detector.tag_name for detector in self.detectors],
        }


# Factory function for easy instantiation
def create_safety_tag_enricher(enable_caching: bool = True) -> SafetyTagEnricher:
    """
    Create Safety Tag Enricher with default detectors.

    Args:
        enable_caching: Enable tag detection result caching

    Returns:
        Configured SafetyTagEnricher instance
    """
    return SafetyTagEnricher(enable_caching=enable_caching)


# Export main classes
__all__ = [
    "SafetyTag",
    "SafetyTagCategory",
    "SafetyTagDetector",
    "TaggedPlan",
    "SafetyTagEnricher",
    "PIIDetector",
    "FinancialDetector",
    "ModelSwitchDetector",
    "ExternalCallDetector",
    "PrivilegeEscalationDetector",
    "GDPRDetector",
    "create_safety_tag_enricher",
]
