"""
⚡ Identity Module Performance Test Suite
========================================

Comprehensive performance tests for LUKHAS Identity module.
Validates <100ms p95 latency requirements and system scalability.

Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
"""

import concurrent.futures
import gc
import os
import secrets
import statistics

# Import system under test
import sys
import time
from datetime import datetime, timedelta

import psutil
import pytest

identity_path = os.path.join(os.path.dirname(__file__), '..', '..', 'identity')
governance_path = os.path.join(os.path.dirname(__file__), '..', '..', 'governance', 'identity')
sys.path.extend([identity_path, governance_path])

try:
    from candidate.governance.identity.auth_backend.qr_entropy_generator import QREntropyGenerator
    from candidate.governance.identity.core.auth.oauth2_oidc_provider import OAuth2OIDCProvider
    from candidate.governance.identity.core.auth.webauthn_manager import WebAuthnManager
    from identity_core import AccessTier, IdentityCore
    COMPONENTS_AVAILABLE = True
except ImportError as e:
    COMPONENTS_AVAILABLE = False
    pytest.skip(f"Identity components not available: {e}", allow_module_level=True)


class PerformanceMetrics:
    """Utility class for collecting and analyzing performance metrics"""

    def __init__(self):
        self.reset()

    def reset(self):
        self.times = []
        self.memory_usage = []
        self.start_time = None
        self.end_time = None

    def start_measurement(self):
        gc.collect()  # Clean garbage before measurement
        self.start_time = time.time()
        self.memory_usage.append(psutil.Process().memory_info().rss / 1024 / 1024)  # MB

    def end_measurement(self):
        self.end_time = time.time()
        if self.start_time:
            self.times.append((self.end_time - self.start_time) * 1000)  # Convert to ms
        self.memory_usage.append(psutil.Process().memory_info().rss / 1024 / 1024)  # MB

    def get_stats(self):
        if not self.times:
            return {}

        times_sorted = sorted(self.times)
        return {
            'count': len(self.times),
            'min_ms': min(self.times),
            'max_ms': max(self.times),
            'mean_ms': statistics.mean(self.times),
            'median_ms': statistics.median(self.times),
            'p95_ms': times_sorted[int(0.95 * len(times_sorted))],
            'p99_ms': times_sorted[int(0.99 * len(times_sorted))],
            'std_dev_ms': statistics.stdev(self.times) if len(self.times) > 1 else 0,
            'total_time_s': sum(self.times) / 1000,
            'throughput_ops_per_sec': len(self.times) / (sum(self.times) / 1000) if sum(self.times) > 0 else 0,
            'memory_peak_mb': max(self.memory_usage) if self.memory_usage else 0,
            'memory_delta_mb': (self.memory_usage[-1] - self.memory_usage[0]) if len(self.memory_usage) >= 2 else 0
        }

    def print_stats(self, operation_name="Operation"):
        stats = self.get_stats()
        if not stats:
            print(f"No {operation_name} metrics available")
            return

        print(f"\n📊 {operation_name} Performance Metrics:")
        print(f"  Operations: {stats['count']}")
        print(f"  Mean: {stats['mean_ms']:.2f}ms")
        print(f"  Median: {stats['median_ms']:.2f}ms")
        print(f"  P95: {stats['p95_ms']:.2f}ms")
        print(f"  P99: {stats['p99_ms']:.2f}ms")
        print(f"  Min/Max: {stats['min_ms']:.2f}ms / {stats['max_ms']:.2f}ms")
        print(f"  Std Dev: {stats['std_dev_ms']:.2f}ms")
        print(f"  Throughput: {stats['throughput_ops_per_sec']:.2f} ops/sec")
        print(f"  Memory Peak: {stats['memory_peak_mb']:.2f}MB")
        print(f"  Memory Delta: {stats['memory_delta_mb']:.2f}MB")


class TestIdentityPerformance:
    """Performance test suite for Identity module components"""

    @pytest.fixture
    def identity_core(self):
        """Create identity core for performance testing"""
        return IdentityCore(data_dir="perf_test_data")

    @pytest.fixture
    def webauthn_manager(self):
        """Create WebAuthn manager for performance testing"""
        config = {
            'rp_id': 'perf.candidate.ai',
            'rp_name': 'LUKHAS Performance Test',
            'origin': 'https://perf.candidate.ai'
        }
        return WebAuthnManager(config=config)

    @pytest.fixture
    def oauth_provider(self):
        """Create OAuth provider for performance testing"""
        config = {
            'issuer': 'https://perf.candidate.ai',
            'rp_id': 'perf.candidate.ai'
        }
        return OAuth2OIDCProvider(config=config)

    @pytest.fixture
    def qr_generator(self):
        """Create QR generator for performance testing"""
        return QREntropyGenerator()

    def test_token_creation_performance(self, identity_core):
        """Test token creation performance with <100ms p95 requirement"""
        metrics = PerformanceMetrics()
        num_iterations = 1000

        print(f"🚀 Testing token creation performance ({num_iterations} iterations)")

        for i in range(num_iterations):
            user_id = f'perf_user_{i:08d}'
            tier = AccessTier(f"T{(i % 5) + 1}")
            metadata = {
                'consent': True,
                'trinity_score': 0.7 + (i % 4) * 0.1,
                'drift_score': (i % 10) * 0.05
            }

            metrics.start_measurement()
            token = identity_core.create_token(user_id, tier, metadata)
            metrics.end_measurement()

            # Verify token was created successfully
            assert token.startswith(f"LUKHAS-{tier.value}-")

        stats = metrics.get_stats()
        metrics.print_stats("Token Creation")

        # Performance assertions
        assert stats['p95_ms'] < 100, f"Token creation P95 latency {stats['p95_ms']:.2f}ms exceeds 100ms requirement"
        assert stats['mean_ms'] < 50, f"Token creation mean latency {stats['mean_ms']:.2f}ms too high"
        assert stats['throughput_ops_per_sec'] > 100, f"Token creation throughput {stats['throughput_ops_per_sec']:.2f} ops/sec too low"
        assert stats['memory_delta_mb'] < 50, f"Memory usage increased by {stats['memory_delta_mb']:.2f}MB"

    def test_token_validation_performance(self, identity_core):
        """Test token validation performance with <100ms p95 requirement"""
        metrics = PerformanceMetrics()
        num_tokens = 500

        # Pre-create tokens for validation
        tokens = []
        for i in range(num_tokens):
            user_id = f'validation_user_{i:08d}'
            tier = AccessTier(f"T{(i % 5) + 1}")
            token = identity_core.create_token(user_id, tier, {'consent': True})
            tokens.append(token)

        print(f"🔍 Testing token validation performance ({num_tokens} tokens)")

        # Test validation performance
        for token in tokens:
            metrics.start_measurement()
            is_valid, metadata = identity_core.validate_symbolic_token(token)
            metrics.end_measurement()

            assert is_valid is True
            assert 'user_id' in metadata

        stats = metrics.get_stats()
        metrics.print_stats("Token Validation")

        # Performance assertions
        assert stats['p95_ms'] < 100, f"Token validation P95 latency {stats['p95_ms']:.2f}ms exceeds 100ms requirement"
        assert stats['mean_ms'] < 25, f"Token validation mean latency {stats['mean_ms']:.2f}ms too high"
        assert stats['throughput_ops_per_sec'] > 200, f"Token validation throughput {stats['throughput_ops_per_sec']:.2f} ops/sec too low"

    def test_tier_resolution_performance(self, identity_core):
        """Test tier resolution performance with <100ms p95 requirement"""
        metrics = PerformanceMetrics()
        num_iterations = 2000

        print(f"⚖️ Testing tier resolution performance ({num_iterations} iterations)")

        for i in range(num_iterations):
            metadata = {
                'user_id': f'tier_test_user_{i:08d}',
                'tier': f"T{(i % 5) + 1}",
                'consent': i % 3 == 0,  # Vary consent to test different paths
                'trinity_score': 0.5 + (i % 6) * 0.1,
                'drift_score': (i % 10) * 0.1,
                'cultural_profile': 'universal' if i % 2 == 0 else 'eu_privacy'
            }

            metrics.start_measurement()
            tier, permissions = identity_core.resolve_access_tier(metadata)
            metrics.end_measurement()

            assert isinstance(tier, AccessTier)
            assert isinstance(permissions, dict)
            assert len(permissions) >= 9  # All permission fields

        stats = metrics.get_stats()
        metrics.print_stats("Tier Resolution")

        # Performance assertions
        assert stats['p95_ms'] < 100, f"Tier resolution P95 latency {stats['p95_ms']:.2f}ms exceeds 100ms requirement"
        assert stats['mean_ms'] < 10, f"Tier resolution mean latency {stats['mean_ms']:.2f}ms too high"
        assert stats['throughput_ops_per_sec'] > 500, f"Tier resolution throughput {stats['throughput_ops_per_sec']:.2f} ops/sec too low"

    def test_glyph_generation_performance(self, identity_core):
        """Test identity glyph generation performance"""
        metrics = PerformanceMetrics()
        num_iterations = 1000

        print(f"✨ Testing glyph generation performance ({num_iterations} iterations)")

        for i in range(num_iterations):
            user_seed = f'glyph_user_{i:08d}'
            entropy = secrets.token_bytes(32) if i % 2 == 0 else None

            metrics.start_measurement()
            glyphs = identity_core.generate_identity_glyph(user_seed, entropy)
            metrics.end_measurement()

            assert isinstance(glyphs, list)
            assert len(glyphs) >= 3
            assert any(g in ['⚛️', '🧠', '🛡️'] for g in glyphs)  # Trinity glyphs

        stats = metrics.get_stats()
        metrics.print_stats("Glyph Generation")

        # Performance assertions (more lenient for cryptographic operations)
        assert stats['p95_ms'] < 100, f"Glyph generation P95 latency {stats['p95_ms']:.2f}ms exceeds 100ms requirement"
        assert stats['mean_ms'] < 50, f"Glyph generation mean latency {stats['mean_ms']:.2f}ms too high"
        assert stats['throughput_ops_per_sec'] > 50, f"Glyph generation throughput {stats['throughput_ops_per_sec']:.2f} ops/sec too low"

    def test_webauthn_registration_performance(self, webauthn_manager):
        """Test WebAuthn registration options generation performance"""
        metrics = PerformanceMetrics()
        num_iterations = 500

        print(f"🔐 Testing WebAuthn registration performance ({num_iterations} iterations)")

        for i in range(num_iterations):
            user_id = f'webauthn_user_{i:08d}'
            user_name = f'webauthn{i}@perf.test'
            display_name = f'WebAuthn User {i}'
            user_tier = (i % 5) + 1

            metrics.start_measurement()
            result = webauthn_manager.generate_registration_options(
                user_id, user_name, display_name, user_tier
            )
            metrics.end_measurement()

            assert result['success'] is True
            assert 'registration_id' in result
            assert 'options' in result
            assert result['guardian_approved'] is True

        stats = metrics.get_stats()
        metrics.print_stats("WebAuthn Registration")

        # Performance assertions
        assert stats['p95_ms'] < 100, f"WebAuthn registration P95 latency {stats['p95_ms']:.2f}ms exceeds 100ms requirement"
        assert stats['mean_ms'] < 50, f"WebAuthn registration mean latency {stats['mean_ms']:.2f}ms too high"
        assert stats['throughput_ops_per_sec'] > 20, f"WebAuthn registration throughput {stats['throughput_ops_per_sec']:.2f} ops/sec too low"

    def test_webauthn_authentication_performance(self, webauthn_manager):
        """Test WebAuthn authentication options generation performance"""
        metrics = PerformanceMetrics()
        num_iterations = 500

        # Pre-populate some credentials for authentication testing
        from candidate.governance.identity.core.auth.webauthn_manager import WebAuthnCredential
        for i in range(0, min(50, num_iterations), 5):  # Every 5th user gets credentials
            user_id = f'webauthn_user_{i:08d}'
            credential = WebAuthnCredential({
                'credential_id': f'cred_{i}',
                'user_id': user_id,
                'tier_level': (i % 5) + 1,
                'authenticator_data': {'transports': ['internal']}
            })
            webauthn_manager.credentials[user_id] = [credential]

        print(f"🔓 Testing WebAuthn authentication performance ({num_iterations} iterations)")

        for i in range(num_iterations):
            user_id = f'webauthn_user_{i:08d}' if i % 5 == 0 else None  # Some with existing creds
            tier_level = (i % 5) + 1

            metrics.start_measurement()
            result = webauthn_manager.generate_authentication_options(user_id, tier_level)
            metrics.end_measurement()

            assert result['success'] is True
            assert 'authentication_id' in result
            assert 'options' in result

        stats = metrics.get_stats()
        metrics.print_stats("WebAuthn Authentication")

        # Performance assertions
        assert stats['p95_ms'] < 100, f"WebAuthn authentication P95 latency {stats['p95_ms']:.2f}ms exceeds 100ms requirement"
        assert stats['mean_ms'] < 50, f"WebAuthn authentication mean latency {stats['mean_ms']:.2f}ms too high"
        assert stats['throughput_ops_per_sec'] > 25, f"WebAuthn authentication throughput {stats['throughput_ops_per_sec']:.2f} ops/sec too low"

    def test_oauth_authorization_performance(self, oauth_provider):
        """Test OAuth2 authorization request performance"""
        metrics = PerformanceMetrics()
        num_iterations = 300

        # Pre-register OAuth clients
        from candidate.governance.identity.core.auth.oauth2_oidc_provider import OAuthClient
        clients = []
        for i in range(10):  # 10 clients for testing
            client_data = {
                'client_id': f'perf_client_{i}',
                'client_secret': f'secret_{i}',
                'client_name': f'Performance Test Client {i}',
                'redirect_uris': [f'https://perfclient{i}.test.com/callback'],
                'allowed_scopes': ['openid', 'profile', 'email', 'lukhas:basic'],
                'grant_types': ['authorization_code'],
                'response_types': ['code'],
                'tier_level': (i % 5) + 1
            }
            client = OAuthClient(client_data)
            oauth_provider.clients[client.client_id] = client
            clients.append(client)

        print(f"🔑 Testing OAuth2 authorization performance ({num_iterations} iterations)")

        for i in range(num_iterations):
            client = clients[i % len(clients)]
            request_params = {
                'client_id': client.client_id,
                'redirect_uri': client.redirect_uris[0],
                'response_type': 'code',
                'scope': 'openid profile email',
                'state': f'state_{i}',
                'nonce': f'nonce_{i}'
            }

            user_id = f'oauth_user_{i:08d}'
            user_tier = (i % 5) + 1

            metrics.start_measurement()
            result = oauth_provider.handle_authorization_request(
                request_params, user_id, user_tier
            )
            metrics.end_measurement()

            assert 'error' not in result
            assert 'code' in result

        stats = metrics.get_stats()
        metrics.print_stats("OAuth2 Authorization")

        # Performance assertions
        assert stats['p95_ms'] < 100, f"OAuth2 authorization P95 latency {stats['p95_ms']:.2f}ms exceeds 100ms requirement"
        assert stats['mean_ms'] < 50, f"OAuth2 authorization mean latency {stats['mean_ms']:.2f}ms too high"
        assert stats['throughput_ops_per_sec'] > 15, f"OAuth2 authorization throughput {stats['throughput_ops_per_sec']:.2f} ops/sec too low"

    def test_oauth_token_request_performance(self, oauth_provider):
        """Test OAuth2 token request performance"""
        metrics = PerformanceMetrics()
        num_iterations = 200

        # Pre-setup client
        from candidate.governance.identity.core.auth.oauth2_oidc_provider import OAuthClient
        client = OAuthClient({
            'client_id': 'token_perf_client',
            'client_secret': 'token_perf_secret',
            'client_name': 'Token Performance Client',
            'redirect_uris': ['https://tokenperf.test.com/callback'],
            'allowed_scopes': ['openid', 'profile', 'email'],
            'grant_types': ['authorization_code'],
            'response_types': ['code']
        })
        oauth_provider.clients[client.client_id] = client

        # Pre-create authorization codes
        auth_codes = []
        for i in range(num_iterations):
            auth_code = f"perf_ac_{secrets.token_urlsafe(16)}"
            oauth_provider.authorization_codes[auth_code] = {
                'client_id': client.client_id,
                'user_id': f'token_user_{i:08d}',
                'user_tier': (i % 5) + 1,
                'scope': ['openid', 'profile', 'email'],
                'redirect_uri': 'https://tokenperf.test.com/callback',
                'issued_at': datetime.utcnow().isoformat(),
                'expires_at': (datetime.utcnow() + timedelta(minutes=10)).isoformat()
            }
            auth_codes.append(auth_code)

        print(f"💰 Testing OAuth2 token request performance ({num_iterations} iterations)")

        for i, auth_code in enumerate(auth_codes):
            token_request = {
                'grant_type': 'authorization_code',
                'code': auth_code,
                'redirect_uri': 'https://tokenperf.test.com/callback',
                'client_id': client.client_id,
                'client_secret': client.client_secret
            }

            metrics.start_measurement()
            result = oauth_provider.handle_token_request(token_request)
            metrics.end_measurement()

            assert 'error' not in result
            assert 'access_token' in result
            assert 'id_token' in result  # OpenID Connect

        stats = metrics.get_stats()
        metrics.print_stats("OAuth2 Token Request")

        # Performance assertions
        assert stats['p95_ms'] < 100, f"OAuth2 token request P95 latency {stats['p95_ms']:.2f}ms exceeds 100ms requirement"
        assert stats['mean_ms'] < 50, f"OAuth2 token request mean latency {stats['mean_ms']:.2f}ms too high"
        assert stats['throughput_ops_per_sec'] > 10, f"OAuth2 token request throughput {stats['throughput_ops_per_sec']:.2f} ops/sec too low"

    def test_qr_generation_performance(self, qr_generator):
        """Test QR code generation with steganography performance"""
        metrics = PerformanceMetrics()
        num_iterations = 100  # Lower count due to image processing complexity

        print(f"📱 Testing QR generation performance ({num_iterations} iterations)")

        for i in range(num_iterations):
            session_id = f'qr_perf_session_{i:08d}'
            entropy_data = secrets.token_bytes(64)
            user_context = {
                'tier': (i % 5) + 1,
                'device_trust': 0.8,
                'max_scans': 5
            }

            metrics.start_measurement()
            result = qr_generator.generate_authentication_qr(
                session_id, entropy_data, user_context
            )
            metrics.end_measurement()

            assert result['success'] is True
            assert result['entropy_embedded'] is True
            assert result['constitutional_validated'] is True

        stats = metrics.get_stats()
        metrics.print_stats("QR Generation")

        # Performance assertions (more lenient due to image processing)
        assert stats['p95_ms'] < 1000, f"QR generation P95 latency {stats['p95_ms']:.2f}ms exceeds 1000ms limit"
        assert stats['mean_ms'] < 500, f"QR generation mean latency {stats['mean_ms']:.2f}ms too high"
        assert stats['throughput_ops_per_sec'] > 2, f"QR generation throughput {stats['throughput_ops_per_sec']:.2f} ops/sec too low"

    def test_qr_validation_performance(self, qr_generator):
        """Test QR code validation performance"""
        metrics = PerformanceMetrics()
        num_iterations = 200

        # Pre-generate QR codes for validation
        qr_sessions = []
        for i in range(num_iterations):
            session_id = f'qr_validation_session_{i:08d}'
            entropy_data = secrets.token_bytes(32)
            result = qr_generator.generate_authentication_qr(session_id, entropy_data)

            code_data = qr_generator.active_codes[session_id]
            scan_data = json.dumps({
                'challenge': code_data['base_data']['challenge'],
                'session_id': session_id,
                'timestamp': datetime.utcnow().isoformat()
            })

            qr_sessions.append((session_id, scan_data))

        print(f"✅ Testing QR validation performance ({num_iterations} iterations)")

        for session_id, scan_data in qr_sessions:
            metrics.start_measurement()
            is_valid = qr_generator.validate_qr_scan(session_id, scan_data)
            metrics.end_measurement()

            assert is_valid is True

        stats = metrics.get_stats()
        metrics.print_stats("QR Validation")

        # Performance assertions
        assert stats['p95_ms'] < 100, f"QR validation P95 latency {stats['p95_ms']:.2f}ms exceeds 100ms requirement"
        assert stats['mean_ms'] < 50, f"QR validation mean latency {stats['mean_ms']:.2f}ms too high"
        assert stats['throughput_ops_per_sec'] > 20, f"QR validation throughput {stats['throughput_ops_per_sec']:.2f} ops/sec too low"

    def test_concurrent_performance(self, identity_core, webauthn_manager, oauth_provider, qr_generator):
        """Test performance under concurrent load"""
        num_threads = 10
        operations_per_thread = 50
        total_operations = num_threads * operations_per_thread

        print(f"🔄 Testing concurrent performance ({num_threads} threads, {operations_per_thread} ops each)")

        def worker_thread(thread_id, results_dict):
            """Worker function for concurrent testing"""
            thread_metrics = PerformanceMetrics()

            for i in range(operations_per_thread):
                op_id = thread_id * operations_per_thread + i
                user_id = f'concurrent_user_{op_id:08d}'

                # Mixed operations to simulate real-world usage
                try:
                    # 1. Token creation and validation
                    thread_metrics.start_measurement()
                    token = identity_core.create_token(
                        user_id, AccessTier('T3'), {'consent': True, 'trinity_score': 0.7}
                    )
                    is_valid, metadata = identity_core.validate_symbolic_token(token)
                    assert is_valid is True
                    thread_metrics.end_measurement()

                    # 2. WebAuthn registration (every 3rd operation)
                    if i % 3 == 0:
                        thread_metrics.start_measurement()
                        webauthn_result = webauthn_manager.generate_registration_options(
                            user_id, f'{user_id}@test.com', f'User {op_id}', 3
                        )
                        assert webauthn_result['success'] is True
                        thread_metrics.end_measurement()

                    # 3. QR generation (every 5th operation)
                    if i % 5 == 0:
                        thread_metrics.start_measurement()
                        qr_result = qr_generator.generate_authentication_qr(
                            f'concurrent_qr_{op_id}', secrets.token_bytes(32)
                        )
                        assert qr_result['success'] is True
                        thread_metrics.end_measurement()

                except Exception as e:
                    print(f"Thread {thread_id} operation {i} failed: {e}")

            results_dict[thread_id] = thread_metrics

        # Execute concurrent operations
        results = {}
        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = []
            for thread_id in range(num_threads):
                future = executor.submit(worker_thread, thread_id, results)
                futures.append(future)

            # Wait for all threads to complete
            concurrent.futures.wait(futures)

        end_time = time.time()
        total_time = end_time - start_time

        # Aggregate results
        all_times = []
        total_memory_delta = 0

        for thread_id, metrics in results.items():
            stats = metrics.get_stats()
            if stats:
                all_times.extend(metrics.times)
                total_memory_delta += stats.get('memory_delta_mb', 0)

        # Calculate overall statistics
        if all_times:
            all_times.sort()
            overall_stats = {
                'total_operations': len(all_times),
                'total_time_s': total_time,
                'mean_ms': statistics.mean(all_times),
                'p95_ms': all_times[int(0.95 * len(all_times))],
                'p99_ms': all_times[int(0.99 * len(all_times))],
                'throughput_ops_per_sec': len(all_times) / total_time,
                'memory_delta_mb': total_memory_delta
            }

            print("\n📊 Concurrent Performance Results:")
            print(f"  Total Operations: {overall_stats['total_operations']}")
            print(f"  Total Time: {overall_stats['total_time_s']:.2f}s")
            print(f"  Mean Latency: {overall_stats['mean_ms']:.2f}ms")
            print(f"  P95 Latency: {overall_stats['p95_ms']:.2f}ms")
            print(f"  P99 Latency: {overall_stats['p99_ms']:.2f}ms")
            print(f"  Throughput: {overall_stats['throughput_ops_per_sec']:.2f} ops/sec")
            print(f"  Memory Delta: {overall_stats['memory_delta_mb']:.2f}MB")

            # Performance assertions for concurrent load
            assert overall_stats['p95_ms'] < 200, f"Concurrent P95 latency {overall_stats['p95_ms']:.2f}ms exceeds 200ms limit"
            assert overall_stats['throughput_ops_per_sec'] > 50, f"Concurrent throughput {overall_stats['throughput_ops_per_sec']:.2f} ops/sec too low"
            assert overall_stats['memory_delta_mb'] < 100, f"Memory usage increased by {overall_stats['memory_delta_mb']:.2f}MB"

        print("✅ Concurrent performance test completed successfully")

    def test_memory_usage_scalability(self, identity_core):
        """Test memory usage scalability with large number of tokens"""
        print("🧠 Testing memory usage scalability")

        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB

        # Create tokens in batches and measure memory growth
        batch_size = 1000
        num_batches = 5
        memory_measurements = [initial_memory]

        for batch in range(num_batches):
            print(f"  Creating batch {batch + 1}/{num_batches} ({batch_size} tokens)")

            batch_start = time.time()

            for i in range(batch_size):
                user_id = f'memory_test_user_{batch * batch_size + i:08d}'
                tier = AccessTier(f"T{(i % 5) + 1}")
                token = identity_core.create_token(
                    user_id, tier, {'consent': True, 'trinity_score': 0.7}
                )

                # Validate some tokens to simulate real usage
                if i % 10 == 0:
                    is_valid, _ = identity_core.validate_symbolic_token(token)
                    assert is_valid is True

            batch_time = time.time() - batch_start
            current_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            memory_measurements.append(current_memory)

            print(f"    Batch {batch + 1} completed in {batch_time:.2f}s, Memory: {current_memory:.2f}MB")

        # Analyze memory growth
        total_tokens = num_batches * batch_size
        final_memory = memory_measurements[-1]
        memory_growth = final_memory - initial_memory
        memory_per_token = memory_growth / total_tokens if total_tokens > 0 else 0

        print("\n📈 Memory Usage Analysis:")
        print(f"  Initial Memory: {initial_memory:.2f}MB")
        print(f"  Final Memory: {final_memory:.2f}MB")
        print(f"  Memory Growth: {memory_growth:.2f}MB")
        print(f"  Total Tokens: {total_tokens}")
        print(f"  Memory per Token: {memory_per_token:.4f}MB")

        # Memory usage assertions
        assert memory_per_token < 0.01, f"Memory per token {memory_per_token:.4f}MB too high"  # 10KB per token max
        assert memory_growth < 200, f"Total memory growth {memory_growth:.2f}MB exceeds 200MB limit"

        # Clean up and verify garbage collection
        gc.collect()
        time.sleep(1)  # Allow GC to complete
        after_gc_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        print(f"  After GC: {after_gc_memory:.2f}MB")

        print("✅ Memory scalability test completed")

    def test_sustained_load_performance(self, identity_core, webauthn_manager):
        """Test performance under sustained load over time"""
        print("⏱️ Testing sustained load performance (60 seconds)")

        duration_seconds = 60
        start_time = time.time()
        end_time = start_time + duration_seconds

        operation_count = 0
        latencies = []
        error_count = 0

        while time.time() < end_time:
            try:
                op_start = time.time()

                # Rotate between different operations
                if operation_count % 3 == 0:
                    # Token operations
                    user_id = f'sustained_user_{operation_count:08d}'
                    token = identity_core.create_token(
                        user_id, AccessTier('T2'), {'consent': True}
                    )
                    is_valid, _ = identity_core.validate_symbolic_token(token)
                    assert is_valid is True

                elif operation_count % 3 == 1:
                    # WebAuthn registration
                    user_id = f'sustained_webauthn_{operation_count:08d}'
                    result = webauthn_manager.generate_registration_options(
                        user_id, f'{user_id}@test.com', f'User {operation_count}', 2
                    )
                    assert result['success'] is True

                else:
                    # Tier resolution
                    metadata = {
                        'user_id': f'sustained_tier_{operation_count:08d}',
                        'tier': f"T{(operation_count % 5) + 1}",
                        'consent': True,
                        'trinity_score': 0.7
                    }
                    tier, permissions = identity_core.resolve_access_tier(metadata)
                    assert isinstance(tier, AccessTier)

                op_time = (time.time() - op_start) * 1000  # ms
                latencies.append(op_time)
                operation_count += 1

            except Exception as e:
                error_count += 1
                print(f"Operation {operation_count} failed: {e}")

        actual_duration = time.time() - start_time

        # Calculate sustained performance metrics
        if latencies:
            latencies.sort()
            sustained_stats = {
                'duration_s': actual_duration,
                'total_operations': operation_count,
                'error_count': error_count,
                'error_rate': error_count / operation_count * 100 if operation_count > 0 else 0,
                'throughput_ops_per_sec': operation_count / actual_duration,
                'mean_latency_ms': statistics.mean(latencies),
                'p95_latency_ms': latencies[int(0.95 * len(latencies))],
                'p99_latency_ms': latencies[int(0.99 * len(latencies))]
            }

            print("\n📊 Sustained Load Results:")
            print(f"  Duration: {sustained_stats['duration_s']:.2f}s")
            print(f"  Operations: {sustained_stats['total_operations']}")
            print(f"  Errors: {sustained_stats['error_count']}")
            print(f"  Error Rate: {sustained_stats['error_rate']:.2f}%")
            print(f"  Throughput: {sustained_stats['throughput_ops_per_sec']:.2f} ops/sec")
            print(f"  Mean Latency: {sustained_stats['mean_latency_ms']:.2f}ms")
            print(f"  P95 Latency: {sustained_stats['p95_latency_ms']:.2f}ms")
            print(f"  P99 Latency: {sustained_stats['p99_latency_ms']:.2f}ms")

            # Sustained performance assertions
            assert sustained_stats['error_rate'] < 1.0, f"Error rate {sustained_stats['error_rate']:.2f}% too high"
            assert sustained_stats['throughput_ops_per_sec'] > 30, f"Sustained throughput {sustained_stats['throughput_ops_per_sec']:.2f} ops/sec too low"
            assert sustained_stats['p95_latency_ms'] < 200, f"Sustained P95 latency {sustained_stats['p95_latency_ms']:.2f}ms too high"

            print("✅ Sustained load test completed successfully")

    def test_performance_regression_detection(self, identity_core):
        """Test for performance regression detection"""
        print("🔍 Testing performance regression detection")

        # Baseline performance measurement
        baseline_operations = 1000
        baseline_metrics = PerformanceMetrics()

        for i in range(baseline_operations):
            user_id = f'baseline_user_{i:08d}'

            baseline_metrics.start_measurement()
            token = identity_core.create_token(
                user_id, AccessTier('T3'), {'consent': True, 'trinity_score': 0.7}
            )
            is_valid, _ = identity_core.validate_symbolic_token(token)
            assert is_valid is True
            baseline_metrics.end_measurement()

        baseline_stats = baseline_metrics.get_stats()
        print(f"  Baseline P95 latency: {baseline_stats['p95_ms']:.2f}ms")
        print(f"  Baseline throughput: {baseline_stats['throughput_ops_per_sec']:.2f} ops/sec")

        # Simulate system under additional load
        current_operations = 1000
        current_metrics = PerformanceMetrics()

        # Add some system stress (simulate memory pressure)
        stress_data = [secrets.token_bytes(1024) for _ in range(1000)]  # 1MB of random data

        for i in range(current_operations):
            user_id = f'current_user_{i:08d}'

            current_metrics.start_measurement()
            token = identity_core.create_token(
                user_id, AccessTier('T3'), {'consent': True, 'trinity_score': 0.7}
            )
            is_valid, _ = identity_core.validate_symbolic_token(token)
            assert is_valid is True
            current_metrics.end_measurement()

        current_stats = current_metrics.get_stats()
        print(f"  Current P95 latency: {current_stats['p95_ms']:.2f}ms")
        print(f"  Current throughput: {current_stats['throughput_ops_per_sec']:.2f} ops/sec")

        # Calculate regression metrics
        latency_regression = (current_stats['p95_ms'] - baseline_stats['p95_ms']) / baseline_stats['p95_ms'] * 100
        throughput_regression = (baseline_stats['throughput_ops_per_sec'] - current_stats['throughput_ops_per_sec']) / baseline_stats['throughput_ops_per_sec'] * 100

        print(f"  Latency regression: {latency_regression:.2f}%")
        print(f"  Throughput regression: {throughput_regression:.2f}%")

        # Regression assertions (allow some variance due to system conditions)
        assert latency_regression < 50, f"P95 latency regression {latency_regression:.2f}% exceeds 50% threshold"
        assert throughput_regression < 25, f"Throughput regression {throughput_regression:.2f}% exceeds 25% threshold"

        # Clean up stress data
        del stress_data
        gc.collect()

        print("✅ Performance regression test completed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
