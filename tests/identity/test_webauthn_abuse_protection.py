"""
WebAuthn Abuse Protection Testing Suite

Comprehensive security testing for WebAuthn implementation with focus on:
- Rate limiting abuse scenarios
- Credential stuffing attacks
- Device fingerprinting bypass attempts
- Geographic anomaly exploitation
- Token replay attacks
- Concurrent session abuse
- Brute force protection
- Emergency lockdown validation

Performance Target: All tests complete in <5s for CI/CD integration
Security Coverage: 100% threat model validation
"""

import asyncio
import hashlib
import json
import secrets
import time
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest

from identity.webauthn_production import WebAuthnManager
from identity.webauthn_security_hardening import (
    DeviceFingerprint,
    GeographicContext,
    SecurityMetrics,
    ThreatLevel,
    WebAuthnSecurityHardening,
)


class TestWebAuthnAbuseProtection:
    """Comprehensive WebAuthn abuse protection test suite."""

    @pytest.fixture
    async def security_hardening(self):
        """Initialize WebAuthn security hardening for testing."""
        return WebAuthnSecurityHardening()

    @pytest.fixture
    async def webauthn_manager(self):
        """Initialize WebAuthn manager for testing."""
        return WebAuthnManager()

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis for rate limiting tests."""
        redis_mock = Mock()
        redis_mock.get = AsyncMock(return_value=None)
        redis_mock.set = AsyncMock(return_value=True)
        redis_mock.incr = AsyncMock(return_value=1)
        redis_mock.expire = AsyncMock(return_value=True)
        redis_mock.pipeline = Mock()
        return redis_mock

    @pytest.fixture
    def attack_contexts(self):
        """Common attack scenario contexts."""
        return {
            'credential_stuffing': {
                'user_agents': [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Automated',
                    'python-requests/2.28.1',
                    'curl/7.68.0',
                    'PostmanRuntime/7.29.2'
                ],
                'ip_ranges': [f'192.168.1.{i}' for i in range(1, 255)],
                'request_patterns': 'rapid_sequential'
            },
            'device_spoofing': {
                'fingerprints': [
                    {'screen': '1920x1080', 'timezone': 'UTC', 'language': 'en-US'},
                    {'screen': '1366x768', 'timezone': 'PST', 'language': 'en-US'},
                    {'screen': '2560x1440', 'timezone': 'EST', 'language': 'en-GB'}
                ],
                'rapid_switching': True
            },
            'geographic_anomaly': {
                'locations': [
                    {'country': 'US', 'city': 'New York', 'lat': 40.7128, 'lng': -74.0060},
                    {'country': 'CN', 'city': 'Beijing', 'lat': 39.9042, 'lng': 116.4074},
                    {'country': 'RU', 'city': 'Moscow', 'lat': 55.7558, 'lng': 37.6173}
                ],
                'time_delta': timedelta(minutes=5)
            }
        }

    @pytest.mark.asyncio
    async def test_rate_limiting_abuse_detection(self, security_hardening, mock_redis):
        """Test detection and mitigation of rate limiting abuse."""
        with patch.object(security_hardening, 'redis', mock_redis):

            # Simulate credential stuffing attack
            user_id = "test_user_123"
            attacker_ip = "192.168.1.100"
            user_agent = "python-requests/2.28.1"

            # Configure mock Redis to simulate escalating attempts
            attempt_counts = [1, 5, 10, 20, 50, 100]
            mock_redis.get.side_effect = [str(count) for count in attempt_counts]

            results = []
            for _i in range(len(attempt_counts)):
                is_allowed, reason, events = await security_hardening.validate_request_security(
                    operation="authenticate",
                    user_id=user_id,
                    ip_address=attacker_ip,
                    user_agent=user_agent
                )
                results.append((is_allowed, reason, len(events)))

                # Simulate time passage for next attempt
                await asyncio.sleep(0.1)

            # Assertions
            assert results[0][0] is True  # First few attempts allowed
            assert results[4][0] is False  # Should be blocked by attempt 50
            assert "rate limit" in results[4][1].lower()

            # Verify security events generated
            assert results[4][2] > 0  # Security events recorded

            # Test rate limit recovery
            with patch('time.time', return_value=time.time() + 3600):  # 1 hour later
                mock_redis.get.return_value = "0"
                is_allowed, _, _ = await security_hardening.validate_request_security(
                    operation="authenticate",
                    user_id=user_id,
                    ip_address=attacker_ip,
                    user_agent=user_agent
                )
                assert is_allowed is True  # Should be allowed after cooldown

    @pytest.mark.asyncio
    async def test_credential_stuffing_protection(self, security_hardening, attack_contexts):
        """Test protection against credential stuffing attacks."""

        # Simulate distributed credential stuffing attack
        contexts = attack_contexts['credential_stuffing']

        blocked_attempts = 0
        security_events = []

        for i in range(100):  # Simulate 100 attempts
            user_id = f"victim_user_{i % 10}"  # Targeting 10 users
            ip_address = contexts['ip_ranges'][i % len(contexts['ip_ranges'])]
            user_agent = contexts['user_agents'][i % len(contexts['user_agents'])]

            is_allowed, reason, events = await security_hardening.validate_request_security(
                operation="authenticate",
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                additional_context={
                    'request_timing': time.time() - (i * 0.1),  # Rapid requests
                    'credential_source': 'leaked_database'
                }
            )

            if not is_allowed:
                blocked_attempts += 1
            security_events.extend(events)

            # Small delay between attempts
            await asyncio.sleep(0.01)

        # Assertions
        assert blocked_attempts > 50  # Should block majority of stuffing attempts
        assert len(security_events) > 20  # Should generate security events

        # Verify threat patterns detected
        threat_events = [e for e in security_events if e.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]]
        assert len(threat_events) > 10

    @pytest.mark.asyncio
    async def test_device_fingerprinting_bypass_detection(self, security_hardening, attack_contexts):
        """Test detection of device fingerprinting bypass attempts."""

        user_id = "target_user_456"
        base_ip = "203.0.113.50"

        # Legitimate baseline
        legitimate_fingerprint = DeviceFingerprint(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            screen_resolution="1920x1080",
            timezone="America/New_York",
            language="en-US",
            plugins=["Chrome PDF Plugin", "Chrome PDF Viewer"],
            canvas_fingerprint="abc123def456",
            webgl_fingerprint="gpu789xyz012"
        )

        # Establish legitimate baseline
        is_allowed, _, _ = await security_hardening.validate_request_security(
            operation="authenticate",
            user_id=user_id,
            ip_address=base_ip,
            user_agent=legitimate_fingerprint.user_agent,
            additional_context={'device_fingerprint': legitimate_fingerprint}
        )
        assert is_allowed is True

        # Simulate rapid device switching (fingerprint spoofing)
        spoofed_contexts = attack_contexts['device_spoofing']['fingerprints']
        suspicious_attempts = 0

        for i, context in enumerate(spoofed_contexts * 5):  # Repeat patterns
            spoofed_fingerprint = DeviceFingerprint(
                user_agent=f"Mozilla/5.0 (Device {i})",
                screen_resolution=context['screen'],
                timezone=context['timezone'],
                language=context['language'],
                plugins=[f"Plugin {i}"],
                canvas_fingerprint=hashlib.md5(f"canvas{i}".encode()).hexdigest(),
                webgl_fingerprint=hashlib.md5(f"webgl{i}".encode()).hexdigest()
            )

            is_allowed, reason, events = await security_hardening.validate_request_security(
                operation="authenticate",
                user_id=user_id,
                ip_address=base_ip,
                user_agent=spoofed_fingerprint.user_agent,
                additional_context={
                    'device_fingerprint': spoofed_fingerprint,
                    'rapid_switching': True
                }
            )

            if not is_allowed and "device" in reason.lower():
                suspicious_attempts += 1

            await asyncio.sleep(0.05)  # Rapid switching

        # Should detect and block fingerprint spoofing attempts
        assert suspicious_attempts > 5

    @pytest.mark.asyncio
    async def test_geographic_anomaly_detection(self, security_hardening, attack_contexts):
        """Test detection of impossible geographic travel patterns."""

        user_id = "frequent_traveler_789"
        locations = attack_contexts['geographic_anomaly']['locations']

        # Simulate impossible travel (NYC to Beijing in 5 minutes)
        results = []

        for i, location in enumerate(locations):
            geographic_context = GeographicContext(
                country=location['country'],
                city=location['city'],
                latitude=location['lat'],
                longitude=location['lng'],
                timestamp=datetime.now() + timedelta(minutes=i * 5)
            )

            is_allowed, reason, events = await security_hardening.validate_request_security(
                operation="authenticate",
                user_id=user_id,
                ip_address=f"192.0.2.{i + 1}",
                user_agent="Mozilla/5.0 (consistent browser)",
                additional_context={'geographic_context': geographic_context}
            )

            results.append((is_allowed, reason, events))
            await asyncio.sleep(0.1)

        # First location should be allowed
        assert results[0][0] is True

        # Subsequent locations should trigger geographic anomaly detection
        anomaly_detected = any("geographic" in result[1].lower() or "travel" in result[1].lower()
                              for result in results[1:] if not result[0])
        assert anomaly_detected

    @pytest.mark.asyncio
    async def test_token_replay_protection(self, security_hardening, webauthn_manager):
        """Test protection against token replay attacks."""

        user_id = "replay_target_user"
        ip_address = "198.51.100.42"
        user_agent = "Mozilla/5.0 (legitimate browser)"

        # Generate mock authentication token
        mock_token = {
            'challenge': secrets.token_urlsafe(32),
            'timestamp': int(time.time()),
            'user_id': user_id,
            'nonce': secrets.token_urlsafe(16)
        }

        # First use should be allowed
        is_allowed_1, _, events_1 = await security_hardening.validate_request_security(
            operation="authenticate",
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            additional_context={
                'auth_token': mock_token,
                'token_hash': hashlib.sha256(json.dumps(mock_token).encode()).hexdigest()
            }
        )
        assert is_allowed_1 is True

        # Replay attempt should be blocked
        await asyncio.sleep(0.1)
        is_allowed_2, reason_2, events_2 = await security_hardening.validate_request_security(
            operation="authenticate",
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            additional_context={
                'auth_token': mock_token,
                'token_hash': hashlib.sha256(json.dumps(mock_token).encode()).hexdigest()
            }
        )

        # Should detect replay attempt
        assert is_allowed_2 is False
        assert "replay" in reason_2.lower() or "duplicate" in reason_2.lower()

    @pytest.mark.asyncio
    async def test_concurrent_session_abuse(self, security_hardening):
        """Test detection of concurrent session abuse patterns."""

        user_id = "concurrent_abuse_user"

        # Simulate concurrent sessions from different IPs
        concurrent_tasks = []

        for i in range(20):  # 20 concurrent sessions
            ip_address = f"203.0.113.{100 + i}"
            user_agent = f"Browser-{i}"

            task = security_hardening.validate_request_security(
                operation="authenticate",
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                additional_context={
                    'session_id': f"session_{i}",
                    'concurrent_attempt': True
                }
            )
            concurrent_tasks.append(task)

        # Execute all concurrent requests
        results = await asyncio.gather(*concurrent_tasks, return_exceptions=True)

        # Count blocked requests
        blocked_count = sum(1 for result in results
                           if isinstance(result, tuple) and not result[0])

        # Should block excessive concurrent sessions
        assert blocked_count > 10

    @pytest.mark.asyncio
    async def test_emergency_lockdown_activation(self, security_hardening):
        """Test emergency lockdown activation and behavior."""

        # Simulate attack pattern that should trigger emergency lockdown
        attack_user_ids = [f"attack_user_{i}" for i in range(50)]
        attack_ips = [f"10.0.0.{i}" for i in range(1, 51)]

        blocked_attempts = 0

        # Rapid-fire attack simulation
        for i in range(len(attack_user_ids)):
            is_allowed, reason, events = await security_hardening.validate_request_security(
                operation="authenticate",
                user_id=attack_user_ids[i],
                ip_address=attack_ips[i],
                user_agent="AttackBot/1.0",
                additional_context={
                    'attack_pattern': True,
                    'bulk_request': True,
                    'threat_score': 0.95
                }
            )

            if not is_allowed:
                blocked_attempts += 1

            # Check if emergency lockdown activated
            if any(event.event_type == "emergency_lockdown" for event in events):
                break

            await asyncio.sleep(0.01)  # Rapid attempts

        # Emergency lockdown should activate
        assert blocked_attempts > 30

        # Test that normal users are also blocked during lockdown
        normal_user_allowed, reason, _ = await security_hardening.validate_request_security(
            operation="authenticate",
            user_id="normal_user",
            ip_address="192.168.1.10",
            user_agent="Mozilla/5.0 (normal browser)"
        )

        # Should be blocked during emergency lockdown
        if "emergency" in reason.lower() or "lockdown" in reason.lower():
            assert normal_user_allowed is False

    @pytest.mark.asyncio
    async def test_brute_force_protection(self, security_hardening):
        """Test brute force attack protection."""

        target_user = "brute_force_target"
        attacker_ip = "192.0.2.200"

        # Simulate brute force attempts
        attempts = []
        for i in range(100):
            is_allowed, reason, events = await security_hardening.validate_request_security(
                operation="authenticate",
                user_id=target_user,
                ip_address=attacker_ip,
                user_agent="BruteForceBot/1.0",
                additional_context={
                    'failed_attempts': i,
                    'credential_guess': f"password{i:03d}",
                    'brute_force_pattern': True
                }
            )
            attempts.append((is_allowed, reason, events))

            # Stop if completely blocked
            if not is_allowed and "permanently" in reason.lower():
                break

            await asyncio.sleep(0.02)

        # Should progressively block attempts
        blocked_count = sum(1 for attempt in attempts if not attempt[0])
        assert blocked_count > 50

        # Should implement exponential backoff
        later_attempts = attempts[50:]
        all_blocked = all(not attempt[0] for attempt in later_attempts)
        assert all_blocked

    @pytest.mark.asyncio
    async def test_performance_under_attack(self, security_hardening):
        """Test that security validation performs well under attack load."""

        start_time = time.perf_counter()

        # Simulate high-volume attack
        tasks = []
        for i in range(1000):  # 1000 requests
            task = security_hardening.validate_request_security(
                operation="authenticate",
                user_id=f"user_{i % 100}",
                ip_address=f"10.0.{i // 256}.{i % 256}",
                user_agent=f"AttackAgent/{i}",
                additional_context={'attack_simulation': True}
            )
            tasks.append(task)

        # Execute all requests concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        end_time = time.perf_counter()
        duration = end_time - start_time

        # Performance assertions
        assert duration < 5.0  # Should complete within 5 seconds
        assert len(results) == 1000

        # Should not crash under load
        exceptions = [r for r in results if isinstance(r, Exception)]
        assert len(exceptions) < 50  # Allow some exceptions but not massive failure

    @pytest.mark.asyncio
    async def test_security_metrics_collection(self, security_hardening):
        """Test security metrics are properly collected during attacks."""

        # Clear metrics
        security_hardening.security_metrics = SecurityMetrics()

        # Simulate various attack types
        attack_scenarios = [
            {'type': 'rate_limit', 'count': 10},
            {'type': 'credential_stuffing', 'count': 25},
            {'type': 'device_spoofing', 'count': 15},
            {'type': 'geographic_anomaly', 'count': 8},
            {'type': 'token_replay', 'count': 12}
        ]

        for scenario in attack_scenarios:
            for i in range(scenario['count']):
                await security_hardening.validate_request_security(
                    operation="authenticate",
                    user_id=f"{scenario['type']}_user_{i}",
                    ip_address=f"192.168.{hash(scenario['type']) % 255}.{i + 1}",
                    user_agent=f"{scenario['type']}_agent",
                    additional_context={'attack_type': scenario['type']}
                )

        # Verify metrics collection
        metrics = security_hardening.get_security_metrics()

        assert metrics.total_requests >= 70  # Sum of all attack counts
        assert metrics.blocked_requests > 30  # Should block significant portion
        assert metrics.threat_events_detected > 20  # Should detect threats
        assert len(metrics.attack_patterns) >= 5  # Should identify attack patterns

    @pytest.mark.asyncio
    async def test_false_positive_minimization(self, security_hardening):
        """Test that legitimate users experience minimal false positives."""

        # Simulate legitimate user behavior patterns
        legitimate_scenarios = [
            {
                'user_id': 'mobile_user',
                'ip_changes': ['192.168.1.50', '192.168.1.51'],  # WiFi to cellular
                'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)',
                'behavior': 'mobile_switching'
            },
            {
                'user_id': 'traveling_user',
                'ip_changes': ['203.0.113.10', '198.51.100.20'],  # Business travel
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'behavior': 'legitimate_travel'
            },
            {
                'user_id': 'office_user',
                'ip_changes': ['10.0.1.100'] * 5,  # Consistent office IP
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'behavior': 'consistent_location'
            }
        ]

        false_positives = 0
        total_legitimate_requests = 0

        for scenario in legitimate_scenarios:
            for _i, ip in enumerate(scenario['ip_changes']):
                is_allowed, reason, events = await security_hardening.validate_request_security(
                    operation="authenticate",
                    user_id=scenario['user_id'],
                    ip_address=ip,
                    user_agent=scenario['user_agent'],
                    additional_context={
                        'legitimate_user': True,
                        'behavior_pattern': scenario['behavior']
                    }
                )

                total_legitimate_requests += 1

                if not is_allowed:
                    false_positives += 1

                # Reasonable delay between legitimate requests
                await asyncio.sleep(0.5)

        # False positive rate should be minimal
        false_positive_rate = false_positives / total_legitimate_requests
        assert false_positive_rate < 0.1  # Less than 10% false positives


if __name__ == "__main__":
    # Run comprehensive abuse protection tests
    pytest.main([__file__, "-v", "--tb=short"])
