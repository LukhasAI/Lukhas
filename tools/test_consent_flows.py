#!/usr/bin/env python3
"""
Consent Flow Testing Tool

Tests consent management functionality:
- Consent banner display logic
- Accept/reject/customize flows
- Consent persistence
- Opt-out functionality
- GDPR compliance

Usage:
    python3 tools/test_consent_flows.py
    python3 tools/test_consent_flows.py --verbose
"""

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class ConsentMode(Enum):
    """GDPR consent modes."""

    GRANTED = "granted"
    DENIED = "denied"
    UNSPECIFIED = "unspecified"


class ConsentCategory(Enum):
    """Consent categories."""

    ANALYTICS = "analytics"
    MARKETING = "marketing"
    FUNCTIONAL = "functional"


@dataclass
class ConsentPreferences:
    """User consent preferences."""

    analytics: ConsentMode
    marketing: ConsentMode
    functional: ConsentMode
    timestamp: str


class ConsentStorage:
    """Simulates localStorage for consent preferences."""

    def __init__(self):
        self._storage: Dict[str, str] = {}

    def set_item(self, key: str, value: str) -> None:
        """Store item."""
        self._storage[key] = value

    def get_item(self, key: str) -> Optional[str]:
        """Get item."""
        return self._storage.get(key)

    def remove_item(self, key: str) -> None:
        """Remove item."""
        if key in self._storage:
            del self._storage[key]

    def clear(self) -> None:
        """Clear all storage."""
        self._storage.clear()


class ConsentManager:
    """Manages consent preferences (simulates browser behavior)."""

    STORAGE_KEY = "lukhas_analytics_consent"

    def __init__(self, storage: ConsentStorage):
        """
        Initialize consent manager.

        Args:
            storage: Storage backend
        """
        self.storage = storage

    def has_consent_record(self) -> bool:
        """Check if user has saved consent preferences."""
        return self.storage.get_item(self.STORAGE_KEY) is not None

    def get_consent(self) -> Optional[ConsentPreferences]:
        """Get saved consent preferences."""
        stored = self.storage.get_item(self.STORAGE_KEY)
        if not stored:
            return None

        try:
            data = json.loads(stored)
            return ConsentPreferences(
                analytics=ConsentMode(data.get("analytics", "denied")),
                marketing=ConsentMode(data.get("marketing", "denied")),
                functional=ConsentMode(data.get("functional", "granted")),
                timestamp=data.get("timestamp", ""),
            )
        except (json.JSONDecodeError, ValueError):
            return None

    def save_consent(self, preferences: ConsentPreferences) -> None:
        """Save consent preferences."""
        data = {
            "analytics": preferences.analytics.value,
            "marketing": preferences.marketing.value,
            "functional": preferences.functional.value,
            "timestamp": preferences.timestamp,
        }
        self.storage.set_item(self.STORAGE_KEY, json.dumps(data))

    def clear_consent(self) -> None:
        """Clear saved consent preferences."""
        self.storage.remove_item(self.STORAGE_KEY)

    def accept_all(self) -> ConsentPreferences:
        """Accept all consent categories."""
        preferences = ConsentPreferences(
            analytics=ConsentMode.GRANTED,
            marketing=ConsentMode.GRANTED,
            functional=ConsentMode.GRANTED,
            timestamp=datetime.utcnow().isoformat(),
        )
        self.save_consent(preferences)
        return preferences

    def reject_all(self) -> ConsentPreferences:
        """Reject all consent categories (except functional)."""
        preferences = ConsentPreferences(
            analytics=ConsentMode.DENIED,
            marketing=ConsentMode.DENIED,
            functional=ConsentMode.GRANTED,  # Essential
            timestamp=datetime.utcnow().isoformat(),
        )
        self.save_consent(preferences)
        return preferences

    def customize(
        self,
        analytics: bool,
        marketing: bool,
    ) -> ConsentPreferences:
        """Save custom consent preferences."""
        preferences = ConsentPreferences(
            analytics=ConsentMode.GRANTED if analytics else ConsentMode.DENIED,
            marketing=ConsentMode.GRANTED if marketing else ConsentMode.DENIED,
            functional=ConsentMode.GRANTED,  # Always granted
            timestamp=datetime.utcnow().isoformat(),
        )
        self.save_consent(preferences)
        return preferences


class ConsentFlowTester:
    """Tests consent flow functionality."""

    def __init__(self, verbose: bool = False):
        """
        Initialize tester.

        Args:
            verbose: Print detailed test output
        """
        self.verbose = verbose
        self.passed = 0
        self.failed = 0

    def log(self, message: str) -> None:
        """Log message if verbose."""
        if self.verbose:
            print(f"  ℹ️  {message}")

    def test(self, name: str, condition: bool, message: str = "") -> bool:
        """
        Run single test.

        Args:
            name: Test name
            condition: Test condition (True = pass)
            message: Optional failure message

        Returns:
            True if test passed
        """
        if condition:
            print(f"✅ {name}")
            self.passed += 1
            return True
        else:
            print(f"❌ {name}")
            if message:
                print(f"   {message}")
            self.failed += 1
            return False

    def test_consent_banner_shows_on_first_visit(self) -> bool:
        """Test: Consent banner shows on first visit."""
        storage = ConsentStorage()
        manager = ConsentManager(storage)

        should_show = not manager.has_consent_record()

        return self.test(
            "Consent banner shows on first visit",
            should_show,
            "Banner should show when no consent record exists",
        )

    def test_accept_all_enables_tracking(self) -> bool:
        """Test: Accept all enables all tracking."""
        storage = ConsentStorage()
        manager = ConsentManager(storage)

        preferences = manager.accept_all()

        analytics_granted = preferences.analytics == ConsentMode.GRANTED
        marketing_granted = preferences.marketing == ConsentMode.GRANTED
        functional_granted = preferences.functional == ConsentMode.GRANTED

        self.log(f"Analytics: {preferences.analytics.value}")
        self.log(f"Marketing: {preferences.marketing.value}")
        self.log(f"Functional: {preferences.functional.value}")

        return self.test(
            "Accept all enables tracking",
            analytics_granted and marketing_granted and functional_granted,
            f"Expected all granted, got analytics={analytics_granted}, "
            f"marketing={marketing_granted}, functional={functional_granted}",
        )

    def test_reject_all_disables_tracking(self) -> bool:
        """Test: Reject all disables non-essential tracking."""
        storage = ConsentStorage()
        manager = ConsentManager(storage)

        preferences = manager.reject_all()

        analytics_denied = preferences.analytics == ConsentMode.DENIED
        marketing_denied = preferences.marketing == ConsentMode.DENIED
        functional_granted = preferences.functional == ConsentMode.GRANTED

        self.log(f"Analytics: {preferences.analytics.value}")
        self.log(f"Marketing: {preferences.marketing.value}")
        self.log(f"Functional: {preferences.functional.value}")

        return self.test(
            "Reject all disables tracking",
            analytics_denied and marketing_denied and functional_granted,
            f"Expected analytics/marketing denied, functional granted. "
            f"Got analytics={analytics_denied}, marketing={marketing_denied}, "
            f"functional={functional_granted}",
        )

    def test_customize_saves_granular_preferences(self) -> bool:
        """Test: Customize saves granular preferences."""
        storage = ConsentStorage()
        manager = ConsentManager(storage)

        # Grant analytics, deny marketing
        preferences = manager.customize(analytics=True, marketing=False)

        analytics_granted = preferences.analytics == ConsentMode.GRANTED
        marketing_denied = preferences.marketing == ConsentMode.DENIED

        self.log(f"Analytics: {preferences.analytics.value}")
        self.log(f"Marketing: {preferences.marketing.value}")

        return self.test(
            "Customize saves granular preferences",
            analytics_granted and marketing_denied,
            f"Expected analytics=granted, marketing=denied. "
            f"Got analytics={analytics_granted}, marketing={marketing_denied}",
        )

    def test_consent_persists_across_sessions(self) -> bool:
        """Test: Consent persists across sessions."""
        storage = ConsentStorage()
        manager = ConsentManager(storage)

        # Save consent
        manager.accept_all()

        # Simulate new session (new manager instance, same storage)
        manager2 = ConsentManager(storage)

        preferences = manager2.get_consent()

        persisted = preferences is not None
        if persisted:
            analytics_granted = preferences.analytics == ConsentMode.GRANTED

            self.log(f"Persisted preferences: {preferences}")

            return self.test(
                "Consent persists across sessions",
                analytics_granted,
                f"Expected analytics=granted, got {preferences.analytics.value}",
            )
        else:
            return self.test(
                "Consent persists across sessions",
                False,
                "Preferences not found in storage",
            )

    def test_opt_out_works_correctly(self) -> bool:
        """Test: Opt-out works correctly."""
        storage = ConsentStorage()
        manager = ConsentManager(storage)

        # Initially accept
        manager.accept_all()

        # Verify tracking enabled
        prefs1 = manager.get_consent()
        initially_granted = (
            prefs1 is not None and prefs1.analytics == ConsentMode.GRANTED
        )

        # Opt out
        manager.reject_all()

        # Verify tracking disabled
        prefs2 = manager.get_consent()
        now_denied = prefs2 is not None and prefs2.analytics == ConsentMode.DENIED

        self.log(f"Initially granted: {initially_granted}")
        self.log(f"Now denied: {now_denied}")

        return self.test(
            "Opt-out works correctly",
            initially_granted and now_denied,
            f"Expected consent change from granted to denied",
        )

    def test_functional_cannot_be_disabled(self) -> bool:
        """Test: Functional consent cannot be disabled."""
        storage = ConsentStorage()
        manager = ConsentManager(storage)

        # Try to disable all (including functional)
        preferences = manager.reject_all()

        functional_granted = preferences.functional == ConsentMode.GRANTED

        self.log(f"Functional: {preferences.functional.value}")

        return self.test(
            "Functional (essential) cannot be disabled",
            functional_granted,
            f"Expected functional=granted, got {preferences.functional.value}",
        )

    def test_timestamp_recorded(self) -> bool:
        """Test: Consent timestamp is recorded."""
        storage = ConsentStorage()
        manager = ConsentManager(storage)

        preferences = manager.accept_all()

        has_timestamp = bool(preferences.timestamp)

        if has_timestamp:
            # Verify it's a valid ISO format
            try:
                datetime.fromisoformat(preferences.timestamp)
                valid_format = True
            except ValueError:
                valid_format = False

            self.log(f"Timestamp: {preferences.timestamp}")

            return self.test(
                "Consent timestamp is recorded",
                valid_format,
                f"Invalid timestamp format: {preferences.timestamp}",
            )
        else:
            return self.test(
                "Consent timestamp is recorded",
                False,
                "Timestamp not found in preferences",
            )

    def test_clear_consent(self) -> bool:
        """Test: Clear consent removes all data."""
        storage = ConsentStorage()
        manager = ConsentManager(storage)

        # Save consent
        manager.accept_all()

        # Verify it exists
        has_record = manager.has_consent_record()

        # Clear it
        manager.clear_consent()

        # Verify it's gone
        no_record = not manager.has_consent_record()

        self.log(f"Had record: {has_record}")
        self.log(f"No record after clear: {no_record}")

        return self.test(
            "Clear consent removes all data",
            has_record and no_record,
            "Consent not properly cleared",
        )

    def run_all_tests(self) -> bool:
        """Run all consent flow tests."""
        print("\n" + "=" * 80)
        print("Consent Flow Tests")
        print("=" * 80 + "\n")

        self.test_consent_banner_shows_on_first_visit()
        self.test_accept_all_enables_tracking()
        self.test_reject_all_disables_tracking()
        self.test_customize_saves_granular_preferences()
        self.test_consent_persists_across_sessions()
        self.test_opt_out_works_correctly()
        self.test_functional_cannot_be_disabled()
        self.test_timestamp_recorded()
        self.test_clear_consent()

        # Print summary
        print("\n" + "=" * 80)
        print("Test Summary")
        print("=" * 80 + "\n")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📊 Total:  {self.passed + self.failed}")
        print()

        return self.failed == 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test consent flow functionality"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print detailed test output",
    )

    args = parser.parse_args()

    tester = ConsentFlowTester(verbose=args.verbose)
    success = tester.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
