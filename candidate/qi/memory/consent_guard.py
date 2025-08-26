#!/usr/bin/env python3
"""
ConsentGuard: GDPR-compliant consent management with TEQ integration
Designed by: Gonzalo Dominguez - Lukhas AI
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Consent:
    user_id: str
    purpose: str
    granted: bool
    timestamp: float
    ttl_seconds: int = 86400 * 30  # 30 days default
    metadata: Dict[str, Any] | None = None

    def is_valid(self) -> bool:
        if not self.granted:
            return False
        return time.time() < (self.timestamp + self.ttl_seconds)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class ConsentGuard:
    def __init__(self, storage_path: str = "~/.lukhas/consent/ledger.jsonl"):
        self.storage_path = os.path.expanduser(storage_path)
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        self.cache: Dict[str, Consent] = {}
        self._load_cache()

    def _consent_key(self, user_id: str, purpose: str) -> str:
        """Generate unique key for consent lookup"""
        return hashlib.sha256(f"{user_id}:{purpose}".encode()).hexdigest()[:16]

    def _load_cache(self):
        """Load recent consents into memory cache"""
        if not os.path.exists(self.storage_path):
            return

        with open(self.storage_path) as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    consent = Consent(**data)
                    if consent.is_valid():
                        key = self._consent_key(consent.user_id, consent.purpose)
                        self.cache[key] = consent
                except:
                    continue

    def grant(self, user_id: str, purpose: str, ttl_seconds: int = 86400 * 30,
              metadata: Dict[str, Any] | None = None) -> Consent:
        """Grant consent for a specific purpose"""
        consent = Consent(
            user_id=user_id,
            purpose=purpose,
            granted=True,
            timestamp=time.time(),
            ttl_seconds=ttl_seconds,
            metadata=metadata or {}
        )

        # Persist to ledger
        with open(self.storage_path, 'a') as f:
            f.write(json.dumps(consent.to_dict()) + '\n')

        # Update cache
        key = self._consent_key(user_id, purpose)
        self.cache[key] = consent

        return consent

    def revoke(self, user_id: str, purpose: str) -> Consent:
        """Revoke consent for a specific purpose"""
        consent = Consent(
            user_id=user_id,
            purpose=purpose,
            granted=False,
            timestamp=time.time(),
            ttl_seconds=0
        )

        # Persist revocation
        with open(self.storage_path, 'a') as f:
            f.write(json.dumps(consent.to_dict()) + '\n')

        # Remove from cache
        key = self._consent_key(user_id, purpose)
        self.cache.pop(key, None)

        return consent

    def check(self, user_id: str, purpose: str) -> Tuple[bool, Optional[Consent]]:
        """Check if valid consent exists"""
        key = self._consent_key(user_id, purpose)

        # Check cache first
        if key in self.cache:
            consent = self.cache[key]
            if consent.is_valid():
                return True, consent
            else:
                # Expired, remove from cache
                del self.cache[key]

        # Check persistent storage
        if os.path.exists(self.storage_path):
            with open(self.storage_path) as f:
                # Read in reverse order (most recent first)
                lines = f.readlines()
                for line in reversed(lines):
                    try:
                        data = json.loads(line.strip())
                        if data['user_id'] == user_id and data['purpose'] == purpose:
                            consent = Consent(**data)
                            if consent.is_valid():
                                # Add to cache for next time
                                self.cache[key] = consent
                                return True, consent
                            elif not consent.granted:
                                # Explicitly revoked
                                return False, consent
                    except:
                        continue

        return False, None

    def list_active(self, user_id: Optional[str] = None) -> List[Consent]:
        """List all active consents, optionally filtered by user"""
        active = []
        seen = set()

        if os.path.exists(self.storage_path):
            with open(self.storage_path) as f:
                lines = f.readlines()
                for line in reversed(lines):
                    try:
                        data = json.loads(line.strip())
                        key = self._consent_key(data['user_id'], data['purpose'])

                        if key in seen:
                            continue
                        seen.add(key)

                        if user_id and data['user_id'] != user_id:
                            continue

                        consent = Consent(**data)
                        if consent.is_valid():
                            active.append(consent)
                    except:
                        continue

        return active

    def audit_trail(self, user_id: str, since_hours: int = 24 * 7) -> List[Dict[str, Any]]:
        """Get audit trail of consent changes for a user"""
        trail = []
        cutoff = time.time() - (since_hours * 3600)

        if os.path.exists(self.storage_path):
            with open(self.storage_path) as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        if data['user_id'] == user_id and data['timestamp'] >= cutoff:
                            trail.append(data)
                    except:
                        continue

        return sorted(trail, key=lambda x: x['timestamp'])

    def cleanup_expired(self) -> int:
        """Remove expired consents from cache and return count"""
        expired_keys = []
        for key, consent in self.cache.items():
            if not consent.is_valid():
                expired_keys.append(key)

        for key in expired_keys:
            del self.cache[key]

        return len(expired_keys)

# TEQ Integration Hook
def require_consent(guard: ConsentGuard, user_id: str, purpose: str) -> Tuple[bool, str]:
    """
    TEQ gate hook for consent checking
    Returns: (allowed, reason)
    """
    has_consent, consent = guard.check(user_id, purpose)

    if has_consent:
        remaining = consent.timestamp + consent.ttl_seconds - time.time()
        days_left = int(remaining / 86400)
        return True, f"Consent valid for {days_left} more days"
    else:
        if consent and not consent.granted:
            return False, f"Consent explicitly revoked at {datetime.fromtimestamp(consent.timestamp)}"
        else:
            return False, f"No consent on record for purpose: {purpose}"

def main():
    ap = argparse.ArgumentParser(description="ConsentGuard CLI - Designed by: Gonzalo Dominguez - Lukhas AI")
    ap.add_argument("--storage", default="~/.lukhas/consent/ledger.jsonl")

    sub = ap.add_subparsers(dest="cmd", help="Commands")

    # Grant consent
    grant_p = sub.add_parser("grant", help="Grant consent")
    grant_p.add_argument("--user", required=True)
    grant_p.add_argument("--purpose", required=True)
    grant_p.add_argument("--ttl-days", type=int, default=30)
    grant_p.add_argument("--metadata", help="JSON metadata")

    # Revoke consent
    revoke_p = sub.add_parser("revoke", help="Revoke consent")
    revoke_p.add_argument("--user", required=True)
    revoke_p.add_argument("--purpose", required=True)

    # Check consent
    check_p = sub.add_parser("check", help="Check consent status")
    check_p.add_argument("--user", required=True)
    check_p.add_argument("--purpose", required=True)

    # List active consents
    list_p = sub.add_parser("list", help="List active consents")
    list_p.add_argument("--user", help="Filter by user")

    # Audit trail
    audit_p = sub.add_parser("audit", help="Show audit trail")
    audit_p.add_argument("--user", required=True)
    audit_p.add_argument("--hours", type=int, default=168, help="Look back N hours")

    # Test consent flow
    test_p = sub.add_parser("test", help="Run consent tests")

    args = ap.parse_args()

    if not args.cmd:
        ap.print_help()
        return

    guard = ConsentGuard(args.storage)

    if args.cmd == "grant":
        metadata = json.loads(args.metadata) if args.metadata else {}
        consent = guard.grant(
            args.user,
            args.purpose,
            ttl_seconds=args.ttl_days * 86400,
            metadata=metadata
        )
        print(f"✅ Granted: {consent.user_id} -> {consent.purpose} (expires in {args.ttl_days} days)")

    elif args.cmd == "revoke":
        consent = guard.revoke(args.user, args.purpose)
        print(f"🚫 Revoked: {consent.user_id} -> {consent.purpose}")

    elif args.cmd == "check":
        has_consent, consent = guard.check(args.user, args.purpose)
        if has_consent:
            remaining = consent.timestamp + consent.ttl_seconds - time.time()
            days = int(remaining / 86400)
            print(f"✅ Valid consent (expires in {days} days)")
        else:
            if consent:
                print(f"🚫 Consent revoked at {datetime.fromtimestamp(consent.timestamp)}")
            else:
                print("❌ No consent on record")

    elif args.cmd == "list":
        consents = guard.list_active(args.user)
        if not consents:
            print("No active consents")
        else:
            for c in consents:
                remaining = c.timestamp + c.ttl_seconds - time.time()
                days = int(remaining / 86400)
                print(f"  • {c.user_id} -> {c.purpose} (expires in {days} days)")

    elif args.cmd == "audit":
        trail = guard.audit_trail(args.user, args.hours)
        if not trail:
            print(f"No consent changes in last {args.hours} hours")
        else:
            for event in trail:
                dt = datetime.fromtimestamp(event['timestamp'])
                action = "GRANTED" if event['granted'] else "REVOKED"
                print(f"[{dt}] {action}: {event['purpose']}")

    elif args.cmd == "test":
        print("Testing ConsentGuard...")

        # Test grant
        c1 = guard.grant("alice", "analytics", ttl_seconds=60)
        assert c1.granted
        print("✓ Grant works")

        # Test check
        ok, _ = guard.check("alice", "analytics")
        assert ok
        print("✓ Check finds valid consent")

        # Test revoke
        guard.revoke("alice", "analytics")
        ok, _ = guard.check("alice", "analytics")
        assert not ok
        print("✓ Revoke works")

        # Test expiry
        guard.grant("bob", "test", ttl_seconds=1)
        time.sleep(2)
        ok, _ = guard.check("bob", "test")
        assert not ok
        print("✓ Expiry works")

        # Test TEQ hook
        guard.grant("charlie", "model_access", ttl_seconds=3600)
        allowed, reason = require_consent(guard, "charlie", "model_access")
        assert allowed
        print(f"✓ TEQ hook works: {reason}")

        # Test TEQ hook denial
        allowed, reason = require_consent(guard, "charlie", "pii_processing")
        assert not allowed
        print(f"✓ TEQ hook denies: {reason}")

        print("\n✅ All ConsentGuard tests passed!")

if __name__ == "__main__":
    main()
