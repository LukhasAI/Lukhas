import ipaddress
import re
from dataclasses import dataclass, field
from datetime import datetime, time
from functools import lru_cache
from typing import Any, Dict, List, Optional, Set

# Order for data classification levels
CLASS_ORDER = {"public": 0, "internal": 1, "restricted": 2, "secret": 3}


@dataclass(frozen=True)
class Context:
    """Represents the context of a request for a policy decision."""

    tenant_id: str
    user_id: Optional[str]
    roles: Set[str]
    scopes: Set[str]
    action: str
    resource: str
    model: Optional[str]
    ip: str
    time_utc: datetime
    data_classification: str
    policy_etag: str
    trace_id: str


@dataclass
class Decision:
    """Represents the outcome of a policy decision."""

    allow: bool
    rule_id: Optional[str]
    reason: str
    obligations: List[Dict[str, Any]] = field(default_factory=list)
    audit: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Rule:
    """Represents a single policy rule."""

    id: str
    effect: str  # "Allow" | "Deny"
    subjects: Dict[str, Any]
    actions: List[str]
    resources: List[str]
    conditions: Dict[str, Any]
    obligations: List[Dict[str, Any]]

    def matches_action(self, action: str) -> bool:
        """Checks if the rule's actions match the given action."""
        return "*" in self.actions or action in self.actions

    def matches_subject(self, ctx: Context) -> bool:
        """Checks if the rule's subjects match the given context."""
        subject_clauses = self.subjects.get("any", [])
        if not subject_clauses:
            return True  # An empty subject clause list can be treated as a match for any subject

        for clause in subject_clauses:
            # An empty clause matches everything
            if not clause:
                return True
            if clause.get("org_id") and clause["org_id"] != ctx.tenant_id:
                continue
            if "user_id" in clause and clause["user_id"] != ctx.user_id:
                continue
            if "scopes_any" in clause and not (ctx.scopes & set(clause["scopes_any"])):
                continue
            if "scopes_all" in clause and not set(clause["scopes_all"]).issubset(ctx.scopes):
                continue
            # If we get here, all conditions in the clause passed
            return True
        return False

    def matches_resource(self, res: str) -> bool:
        """Checks if the rule's resources match the given resource string."""
        for pat in self.resources:
            if pat == "*" or _match_resource(pat, res):
                return True
        return False

    def matches_conditions(self, ctx: Context) -> bool:
        """Checks if the rule's conditions match the given context."""
        c = self.conditions or {}
        if c.get("tenant_must_match") and not ctx.tenant_id:  # Simple truthiness check
            return False
        if "time_before" in c and not _before(ctx.time_utc, c["time_before"]):
            return False
        if "time_after" in c and not _after(ctx.time_utc, c["time_after"]):
            return False
        if "ip_cidr_any" in c and not any(_ip_in_cidr(ctx.ip, cidr) for cidr in c["ip_cidr_any"]):
            return False
        if "model_in" in c and (ctx.model not in set(c["model_in"])):
            return False
        if "data_classification_max" in c:
            if CLASS_ORDER.get(ctx.data_classification, 99) > CLASS_ORDER.get(
                c["data_classification_max"], -1
            ):
                return False
        return True


# Helper functions for matching, cached for performance


@lru_cache(maxsize=1024)
def _compile_resource(pat: str) -> re.Pattern:
    """Compiles a simple wildcard pattern to a regex."""
    # "indexes/*" -> r"^indexes/[^/]+$"
    # "tenants/**/data" -> r"^tenants/.*/data$"
    esc = re.escape(pat).replace(r"\*\*", ".*").replace(r"\*", "[^/]+")
    return re.compile("^" + esc + "$")


def _match_resource(pat: str, res: str) -> bool:
    """Matches a resource string against a compiled regex pattern."""
    return bool(_compile_resource(pat).match(res))


@lru_cache(maxsize=512)
def _ip_in_cidr(ip: str, cidr: str) -> bool:
    """Checks if an IP address is within a CIDR block."""
    try:
        return ipaddress.ip_address(ip) in ipaddress.ip_network(cidr, strict=False)
    except ValueError:
        return False  # Invalid IP or CIDR


def _parse_hhmmz(s: str) -> time:
    """Parses a time string like '23:00Z' into a time object."""
    try:
        hh, mm = map(int, s.rstrip("Z").split(":"))
        return time(hh, mm)
    except (ValueError, AttributeError):
        return time(0, 0)  # Default value on parse error


def _before(dt: datetime, hhmmz: str) -> bool:
    """Checks if a datetime's time is before the given time string."""
    return dt.time() <= _parse_hhmmz(hhmmz)


def _after(dt: datetime, hhmmz: str) -> bool:
    """Checks if a datetime's time is after the given time string."""
    return dt.time() >= _parse_hhmmz(hhmmz)
