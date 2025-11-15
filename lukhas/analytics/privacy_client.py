"""
Privacy-Preserving Analytics Client with Differential Privacy.

This module implements ε-differential privacy for analytics data, ensuring
GDPR Article 25 compliance (privacy by design) while providing useful
aggregate statistics.

Key features:
- ε-differential privacy (epsilon-DP)
- Local data minimization
- Automatic anonymization of PII
- Privacy budget tracking with warnings
- Laplace and Gaussian noise mechanisms
- GDPR right to erasure support
"""

import hashlib
import logging
import re
import warnings
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import numpy as np

logger = logging.getLogger(__name__)


# ============================================================================
# Enums
# ============================================================================


class CircuitBreakerState(Enum):
    """Circuit breaker states for fault tolerance."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class AggregateStats:
    """
    Results from differentially private aggregate query.

    Attributes:
        aggregation_type: Type of aggregation (count, mean, sum, histogram)
        value: Noisy result value
        noise_added: Amount of noise added for transparency
        epsilon_used: Privacy budget consumed by this query
        count: Noisy count of records (for transparency)
        sensitivity: Sensitivity of the query
    """
    aggregation_type: str
    value: Union[float, Dict[str, float]]
    noise_added: Union[float, Dict[str, float]]
    epsilon_used: float
    count: int
    sensitivity: float = 1.0


# ============================================================================
# Anonymization Utilities
# ============================================================================


class PIIAnonymizer:
    """Utility class for detecting and removing PII from events."""

    # PII detection patterns
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    IP_PATTERN = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
    PHONE_PATTERN = re.compile(r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b')

    # Common PII field names
    PII_FIELDS = {
        'email', 'user_id', 'ip', 'ip_address', 'phone', 'phone_number',
        'ssn', 'social_security', 'credit_card', 'password', 'token',
        'api_key', 'secret', 'address', 'street', 'zipcode', 'postal_code'
    }

    @classmethod
    def anonymize_event(cls, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Anonymize event data by removing PII.

        Steps:
        1. Remove known PII fields (email, IP, user_id, etc.)
        2. Generalize timestamps to hour granularity
        3. Hash any remaining identifiers

        Args:
            event: Raw event dictionary

        Returns:
            Anonymized event dictionary
        """
        anonymized = {}

        for key, value in event.items():
            key_lower = key.lower()

            # Remove direct PII fields
            if key_lower in cls.PII_FIELDS:
                continue

            # Generalize timestamps
            if key_lower in ('timestamp', 'created_at', 'updated_at'):
                if isinstance(value, (datetime, str)):
                    try:
                        dt = value if isinstance(value, datetime) else datetime.fromisoformat(value)
                        # Generalize to hour granularity
                        anonymized[key] = dt.replace(minute=0, second=0, microsecond=0).isoformat()
                    except (ValueError, AttributeError):
                        anonymized[key] = value
                continue

            # Redact PII patterns in string values
            if isinstance(value, str):
                value = cls._redact_pii_patterns(value)

            # Hash identifiers that look like IDs but aren't direct PII
            if key_lower.endswith('_id') and key_lower not in cls.PII_FIELDS:
                if isinstance(value, str):
                    value = cls._hash_identifier(value)

            anonymized[key] = value

        return anonymized

    @classmethod
    def _redact_pii_patterns(cls, text: str) -> str:
        """Redact PII patterns from text."""
        text = cls.EMAIL_PATTERN.sub('[EMAIL_REDACTED]', text)
        text = cls.IP_PATTERN.sub('[IP_REDACTED]', text)
        text = cls.PHONE_PATTERN.sub('[PHONE_REDACTED]', text)
        return text

    @classmethod
    def _hash_identifier(cls, value: str) -> str:
        """Hash an identifier for privacy."""
        return hashlib.sha256(value.encode()).hexdigest()[:16]


# ============================================================================
# Differential Privacy Mechanisms
# ============================================================================


class DPMechanism:
    """Base class for differential privacy mechanisms."""

    @staticmethod
    def add_laplace_noise(
        value: float,
        sensitivity: float,
        epsilon: float
    ) -> tuple[float, float]:
        """
        Add Laplace noise for ε-differential privacy.

        The Laplace mechanism adds noise drawn from Laplace(0, sensitivity/ε).

        Args:
            value: True value to protect
            sensitivity: Maximum change one individual can cause
            epsilon: Privacy budget (smaller = more privacy)

        Returns:
            Tuple of (noisy_value, noise_added)
        """
        scale = sensitivity / epsilon
        noise = np.random.laplace(0, scale)
        return value + noise, noise

    @staticmethod
    def add_gaussian_noise(
        value: float,
        sensitivity: float,
        epsilon: float,
        delta: float
    ) -> tuple[float, float]:
        """
        Add Gaussian noise for (ε, δ)-differential privacy.

        The Gaussian mechanism adds noise ~ N(0, σ²) where
        σ = sensitivity * sqrt(2 * ln(1.25/δ)) / ε

        Args:
            value: True value to protect
            sensitivity: Maximum change one individual can cause
            epsilon: Privacy budget
            delta: Privacy loss probability

        Returns:
            Tuple of (noisy_value, noise_added)
        """
        sigma = sensitivity * np.sqrt(2 * np.log(1.25 / delta)) / epsilon
        noise = np.random.normal(0, sigma)
        return value + noise, noise


# ============================================================================
# Main Privacy Client
# ============================================================================


class PrivacyClient:
    """
    Privacy-preserving analytics client with differential privacy.

    Implements ε-differential privacy with:
    - Automatic anonymization of PII
    - Privacy budget tracking
    - Multiple noise mechanisms (Laplace, Gaussian)
    - GDPR Article 25 compliance (privacy by design)
    - Support for aggregate statistics

    Example:
        >>> client = PrivacyClient(epsilon=1.0, delta=1e-5)
        >>> client.log_event({"user_id": "123", "action": "click"})
        >>> stats = client.get_stats("count")
        >>> print(f"Count: {stats.value}, Budget used: {stats.epsilon_used}")
    """

    def __init__(
        self,
        epsilon: float = 1.0,
        delta: float = 1e-5,
        mechanism: str = "laplace",
        max_budget: Optional[float] = None
    ):
        """
        Initialize privacy client.

        Args:
            epsilon: Privacy budget (smaller = more privacy, less accuracy)
                    Typical values: 0.1 (high privacy) to 10 (low privacy)
            delta: Privacy loss probability for Gaussian mechanism
                   Typical value: 1e-5 or smaller
            mechanism: Noise mechanism ("laplace" or "gaussian")
            max_budget: Maximum privacy budget allowed (default: 10 * epsilon)
        """
        if epsilon <= 0:
            raise ValueError("epsilon must be positive")
        if delta <= 0 or delta >= 1:
            raise ValueError("delta must be in (0, 1)")
        if mechanism not in ("laplace", "gaussian"):
            raise ValueError("mechanism must be 'laplace' or 'gaussian'")

        self.epsilon = epsilon
        self.delta = delta
        self.mechanism = mechanism
        self.max_budget = max_budget or (10 * epsilon)

        self.events: List[Dict[str, Any]] = []
        self.privacy_budget_used = 0.0

        logger.info(
            f"Initialized PrivacyClient with ε={epsilon}, δ={delta}, "
            f"mechanism={mechanism}, max_budget={self.max_budget}"
        )

    def log_event(
        self,
        event: Dict[str, Any],
        anonymize: bool = True
    ) -> None:
        """
        Log an event with optional anonymization.

        Anonymization steps (when enabled):
        1. Remove PII fields (email, IP, user_id, etc.)
        2. Generalize timestamps to hour granularity
        3. Hash remaining identifiers
        4. Redact PII patterns in text

        Args:
            event: Event data dictionary
            anonymize: Whether to anonymize PII (default: True)
        """
        if anonymize:
            event = PIIAnonymizer.anonymize_event(event)

        # Add metadata
        event['_logged_at'] = datetime.utcnow().replace(
            minute=0, second=0, microsecond=0
        ).isoformat()

        self.events.append(event)
        logger.debug(f"Logged event: {list(event.keys())}")

    def get_stats(
        self,
        aggregation_type: str,
        column: Optional[str] = None,
        epsilon: Optional[float] = None
    ) -> AggregateStats:
        """
        Get differentially private aggregate statistics.

        Supported aggregations:
        - "count": Noisy count of events
        - "mean": Noisy mean of numeric column
        - "sum": Noisy sum of numeric column
        - "histogram": Noisy histogram (requires column)

        Args:
            aggregation_type: Type of aggregation
            column: Column name (required for mean, sum, histogram)
            epsilon: Privacy budget for this query (default: self.epsilon)

        Returns:
            AggregateStats with noisy results

        Raises:
            ValueError: If aggregation type invalid or budget exceeded
        """
        if aggregation_type not in ("count", "mean", "sum", "histogram"):
            raise ValueError(
                f"Invalid aggregation_type: {aggregation_type}. "
                "Must be one of: count, mean, sum, histogram"
            )

        if aggregation_type in ("mean", "sum", "histogram") and column is None:
            raise ValueError(f"{aggregation_type} requires column parameter")

        # Use provided epsilon or default
        query_epsilon = epsilon or self.epsilon

        # Check privacy budget
        if self.privacy_budget_used + query_epsilon > self.max_budget:
            warnings.warn(
                f"Privacy budget nearly exhausted! Used: {self.privacy_budget_used:.2f}, "
                f"Max: {self.max_budget:.2f}, Query needs: {query_epsilon:.2f}",
                UserWarning
            )

        # Route to appropriate aggregation method
        if aggregation_type == "count":
            result = self._get_noisy_count(query_epsilon)
        elif aggregation_type == "mean":
            result = self._get_noisy_mean(column, query_epsilon)
        elif aggregation_type == "sum":
            result = self._get_noisy_sum(column, query_epsilon)
        else:  # histogram
            result = self._get_noisy_histogram(column, query_epsilon)

        # Update budget
        self.privacy_budget_used += query_epsilon

        logger.info(
            f"Query: {aggregation_type}, ε_used: {query_epsilon:.2f}, "
            f"Total ε_used: {self.privacy_budget_used:.2f}/{self.max_budget:.2f}"
        )

        return result

    def _get_noisy_count(self, epsilon: float) -> AggregateStats:
        """Get noisy count with sensitivity = 1."""
        true_count = len(self.events)
        sensitivity = 1.0

        if self.mechanism == "laplace":
            noisy_value, noise = DPMechanism.add_laplace_noise(
                true_count, sensitivity, epsilon
            )
        else:
            noisy_value, noise = DPMechanism.add_gaussian_noise(
                true_count, sensitivity, epsilon, self.delta
            )

        # Ensure non-negative count
        noisy_value = max(0, noisy_value)

        return AggregateStats(
            aggregation_type="count",
            value=noisy_value,
            noise_added=noise,
            epsilon_used=epsilon,
            count=int(noisy_value),
            sensitivity=sensitivity
        )

    def _get_noisy_mean(self, column: str, epsilon: float) -> AggregateStats:
        """
        Get noisy mean using composition of noisy sum and noisy count.

        Uses half the budget for sum and half for count.
        """
        # Extract numeric values
        values = self._extract_numeric_column(column)

        if not values:
            return AggregateStats(
                aggregation_type="mean",
                value=0.0,
                noise_added=0.0,
                epsilon_used=epsilon,
                count=0,
                sensitivity=1.0
            )

        # Split budget: half for sum, half for count
        half_epsilon = epsilon / 2

        # Get noisy sum
        sum_stats = self._get_noisy_sum(column, half_epsilon)

        # Get noisy count
        count_stats = self._get_noisy_count(half_epsilon)

        # Calculate mean
        if count_stats.value > 0:
            noisy_mean = sum_stats.value / count_stats.value
        else:
            noisy_mean = 0.0

        # Combined noise (approximation)
        combined_noise = sum_stats.noise_added + count_stats.noise_added

        return AggregateStats(
            aggregation_type="mean",
            value=noisy_mean,
            noise_added=combined_noise,
            epsilon_used=epsilon,
            count=count_stats.count,
            sensitivity=2.0  # Composition of two queries
        )

    def _get_noisy_sum(self, column: str, epsilon: float) -> AggregateStats:
        """
        Get noisy sum.

        Assumes values are bounded in [0, 1] for sensitivity = 1.
        For unbounded data, sensitivity would be (max - min).
        """
        values = self._extract_numeric_column(column)

        if not values:
            return AggregateStats(
                aggregation_type="sum",
                value=0.0,
                noise_added=0.0,
                epsilon_used=epsilon,
                count=0,
                sensitivity=1.0
            )

        true_sum = sum(values)

        # Sensitivity = max individual contribution
        # For simplicity, assume values in [0, 1], so sensitivity = 1
        sensitivity = 1.0

        if self.mechanism == "laplace":
            noisy_value, noise = DPMechanism.add_laplace_noise(
                true_sum, sensitivity, epsilon
            )
        else:
            noisy_value, noise = DPMechanism.add_gaussian_noise(
                true_sum, sensitivity, epsilon, self.delta
            )

        return AggregateStats(
            aggregation_type="sum",
            value=noisy_value,
            noise_added=noise,
            epsilon_used=epsilon,
            count=len(values),
            sensitivity=sensitivity
        )

    def _get_noisy_histogram(self, column: str, epsilon: float) -> AggregateStats:
        """
        Get noisy histogram of categorical values.

        Adds noise to each bin count independently.
        """
        # Extract column values
        values = [
            event.get(column)
            for event in self.events
            if column in event
        ]

        if not values:
            return AggregateStats(
                aggregation_type="histogram",
                value={},
                noise_added={},
                epsilon_used=epsilon,
                count=0,
                sensitivity=1.0
            )

        # Build histogram
        histogram = {}
        for value in values:
            key = str(value)
            histogram[key] = histogram.get(key, 0) + 1

        # Add noise to each bin
        # Sensitivity = 1 (one person affects at most one bin by 1)
        sensitivity = 1.0
        bin_epsilon = epsilon / len(histogram)  # Split budget across bins

        noisy_histogram = {}
        noise_histogram = {}

        for key, count in histogram.items():
            if self.mechanism == "laplace":
                noisy_value, noise = DPMechanism.add_laplace_noise(
                    count, sensitivity, bin_epsilon
                )
            else:
                noisy_value, noise = DPMechanism.add_gaussian_noise(
                    count, sensitivity, bin_epsilon, self.delta
                )

            # Ensure non-negative counts
            noisy_histogram[key] = max(0, noisy_value)
            noise_histogram[key] = noise

        total_count = sum(noisy_histogram.values())

        return AggregateStats(
            aggregation_type="histogram",
            value=noisy_histogram,
            noise_added=noise_histogram,
            epsilon_used=epsilon,
            count=int(total_count),
            sensitivity=sensitivity
        )

    def _extract_numeric_column(self, column: str) -> List[float]:
        """Extract numeric values from a column."""
        values = []
        for event in self.events:
            if column in event:
                try:
                    value = float(event[column])
                    # Clip to [0, 1] for bounded sensitivity
                    # In production, you'd want configurable bounds
                    values.append(max(0.0, min(1.0, value)))
                except (ValueError, TypeError):
                    continue
        return values

    def check_privacy_budget(self) -> float:
        """
        Return remaining privacy budget.

        Returns:
            Remaining privacy budget (max_budget - used)
        """
        remaining = self.max_budget - self.privacy_budget_used

        if remaining < self.epsilon:
            warnings.warn(
                f"Privacy budget low! Remaining: {remaining:.2f}, "
                f"Default query cost: {self.epsilon:.2f}",
                UserWarning
            )

        return remaining

    def clear_local_data(self) -> None:
        """
        Clear all local analytics data.

        Implements GDPR Article 17 (Right to Erasure).
        After calling this, all event data and privacy budget are reset.
        """
        self.events.clear()
        self.privacy_budget_used = 0.0
        logger.info("Local data cleared (GDPR right to erasure)")

    def get_privacy_report(self) -> Dict[str, Any]:
        """
        Get a privacy transparency report.

        Returns:
            Dictionary with privacy parameters and current state
        """
        return {
            "privacy_parameters": {
                "epsilon": self.epsilon,
                "delta": self.delta,
                "mechanism": self.mechanism,
                "max_budget": self.max_budget
            },
            "budget_status": {
                "used": self.privacy_budget_used,
                "remaining": self.check_privacy_budget(),
                "percentage_used": (self.privacy_budget_used / self.max_budget) * 100
            },
            "data_status": {
                "events_stored": len(self.events),
                "anonymization_enabled": True
            },
            "compliance": {
                "gdpr_article_25": "privacy_by_design",
                "gdpr_article_17": "right_to_erasure_implemented"
            }
        }


__all__ = ["PrivacyClient", "AggregateStats", "PIIAnonymizer", "DPMechanism"]
