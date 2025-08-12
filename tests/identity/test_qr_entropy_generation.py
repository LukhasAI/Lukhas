"""
🔐 QR Entropy Generation Test Suite
=================================

Comprehensive unit tests for LUKHAS QR entropy generation with steganography.
Tests the QREntropyGenerator class for authentication QR codes with embedded entropy layers.

Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
"""

import base64
import hashlib
import io
import json
import pytest
import secrets
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Import system under test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'governance', 'identity', 'auth_backend'))

try:
    from qr_entropy_generator import QREntropyGenerator
except ImportError:
    pytest.skip("QREntropyGenerator not available", allow_module_level=True)

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    pytest.skip("PIL not available for image processing tests", allow_module_level=True)


class TestQREntropyGenerator:
    """Test suite for QR entropy generation with steganography"""
    
    @pytest.fixture
    def qr_generator(self):
        """Create QR entropy generator instance"""
        return QREntropyGenerator()
    
    @pytest.fixture
    def sample_entropy_data(self):
        """Generate sample entropy data for testing"""
        return secrets.token_bytes(64)  # 512 bits of entropy
    
    @pytest.fixture
    def sample_user_context(self):
        """Sample user context for testing"""
        return {
            'tier': 3,
            'geo_code': 'US',
            'device_trust': 0.8,
            'max_scans': 5
        }
    
    def test_qr_generator_initialization(self):
        """Test QR generator initialization with default settings"""
        generator = QREntropyGenerator()
        
        assert generator.entropy_layers == 3
        assert generator.refresh_interval == 2.0
        assert generator.max_code_lifetime == 300
        assert isinstance(generator.active_codes, dict)
        assert len(generator.stego_layers) == 3
        
        # Test steganography layers configuration
        assert 'layer_1' in generator.stego_layers
        assert 'layer_2' in generator.stego_layers
        assert 'layer_3' in generator.stego_layers
        
        for layer_name, config in generator.stego_layers.items():
            assert 'channel' in config
            assert 'bit_depth' in config
            assert 0 <= config['channel'] <= 2  # RGB channels
            assert 1 <= config['bit_depth'] <= 2  # Reasonable bit depths
    
    def test_qr_generator_with_encryption_key(self):
        """Test QR generator initialization with encryption key"""
        # Generate valid Fernet key (32 bytes, base64 encoded)
        from cryptography.fernet import Fernet
        encryption_key = Fernet.generate_key()
        generator = QREntropyGenerator(encryption_key=encryption_key)
        
        # Should initialize encryption if available
        assert hasattr(generator, 'cipher')
    
    def test_generate_authentication_qr_basic(self, qr_generator, sample_entropy_data):
        """Test basic QR code generation with entropy embedding"""
        session_id = "test_session_12345"
        
        start_time = time.time()
        result = qr_generator.generate_authentication_qr(session_id, sample_entropy_data)
        generation_time = time.time() - start_time
        
        # Verify successful generation
        assert result['success'] is True
        assert result['session_id'] == session_id
        assert 'qr_image_b64' in result
        assert 'refresh_token' in result
        assert 'expires_at' in result
        assert result['entropy_embedded'] is True
        assert result['layers_count'] == 3
        assert result['constitutional_validated'] is True
        assert result['guardian_approved'] is True
        
        # Verify performance requirement (<100ms for p95)
        assert result['generation_time_ms'] < 1000  # Generous limit for CI
        
        # Verify base64 encoded image
        image_data = base64.b64decode(result['qr_image_b64'])
        assert len(image_data) > 0
        
        # Verify session is stored
        assert session_id in qr_generator.active_codes
        code_data = qr_generator.active_codes[session_id]
        assert code_data['entropy_hash'] == hashlib.sha256(sample_entropy_data).hexdigest()[:16]
        assert code_data['refresh_token'] == result['refresh_token']
    
    def test_generate_authentication_qr_with_user_context(self, qr_generator, sample_entropy_data, sample_user_context):
        """Test QR generation with user context"""
        session_id = "test_session_with_context"
        
        result = qr_generator.generate_authentication_qr(
            session_id, 
            sample_entropy_data, 
            user_context=sample_user_context
        )
        
        assert result['success'] is True
        
        # Verify user context was incorporated
        code_data = qr_generator.active_codes[session_id]
        base_data = code_data['base_data']
        
        assert base_data['user_tier'] == sample_user_context['tier']
        assert base_data['geo_code'] == sample_user_context['geo_code']
        assert base_data['device_trust'] == sample_user_context['device_trust']
        assert code_data['max_scans'] == sample_user_context['max_scans']
    
    def test_generate_authentication_qr_error_handling(self, qr_generator):
        """Test error handling in QR generation"""
        # Test with invalid entropy data
        with patch.object(qr_generator, '_create_base_qr_image', side_effect=Exception("QR creation failed")):
            result = qr_generator.generate_authentication_qr("test_session", b"entropy")
            
            assert result['success'] is False
            assert 'error' in result
            assert 'QR generation failed' in result['error']
            assert result['constitutional_validated'] is False
    
    @pytest.mark.skipif(not PIL_AVAILABLE, reason="PIL not available")
    def test_embed_steganographic_layers(self, qr_generator, sample_entropy_data):
        """Test steganographic entropy embedding in QR images"""
        # Create a mock QR image
        base_image = Image.new('RGB', (100, 100), color='white')
        
        # Test steganography embedding
        stego_image = qr_generator.embed_steganographic_layers(base_image, sample_entropy_data)
        
        assert isinstance(stego_image, Image.Image)
        assert stego_image.size == base_image.size
        assert stego_image.mode == 'RGB'
        
        # Verify image data has been modified (contains entropy)
        base_pixels = list(base_image.getdata())
        stego_pixels = list(stego_image.getdata())
        
        # Should have some pixel differences due to steganography
        differences = sum(1 for b, s in zip(base_pixels, stego_pixels) if b != s)
        assert differences > 0  # Entropy should have modified some pixels
    
    def test_entropy_to_bits_conversion(self, qr_generator):
        """Test entropy data to bit array conversion"""
        # Test with known byte values
        test_bytes = b'\xff\x00\xaa'  # 11111111 00000000 10101010
        expected_bits = [1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0, 1,0,1,0,1,0,1,0]
        
        result_bits = qr_generator._entropy_to_bits(test_bytes)
        assert result_bits == expected_bits
    
    def test_embed_bits_in_channel(self, qr_generator):
        """Test LSB steganography bit embedding"""
        # Create test pixel data
        pixels = [(255, 128, 64), (200, 150, 100)]  # RGB pixels
        test_bits = [1, 0, 1, 1]  # Bits to embed
        
        # Embed in red channel (channel 0) with 2-bit depth
        result_pixels = qr_generator._embed_bits_in_channel(pixels, test_bits, channel=0, bit_depth=2)
        
        assert len(result_pixels) == len(pixels)
        
        # First pixel: red channel should have bits [1,0] embedded as bit0=1, bit1=0
        # This creates binary 01 (reading LSB first) = 1 decimal
        # Original: 255 (11111111) -> should become 11111101 = 253
        expected_red_1 = (255 & 0xFC) | 0x01  # Clear 2 LSBs, set to 01 (binary)
        assert result_pixels[0][0] == expected_red_1
        
        # Second pixel: red channel should have bits [1,1] = 3 in LSBs  
        # Original: 200 (11001000) -> should become 11001011 = 203
        expected_red_2 = (200 & 0xFC) | 0x03  # Clear 2 LSBs, set to 11 (binary)
        assert result_pixels[1][0] == expected_red_2
        
        # Other channels should remain unchanged
        assert result_pixels[0][1:] == pixels[0][1:]
        assert result_pixels[1][1:] == pixels[1][1:]
    
    def test_validate_qr_scan_valid(self, qr_generator, sample_entropy_data):
        """Test valid QR scan validation"""
        session_id = "test_scan_session"
        
        # Generate QR code first
        qr_result = qr_generator.generate_authentication_qr(session_id, sample_entropy_data)
        assert qr_result['success'] is True
        
        # Prepare scan data
        code_data = qr_generator.active_codes[session_id]
        scan_payload = {
            'challenge': code_data['base_data']['challenge'],
            'session_id': session_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        scan_data = json.dumps(scan_payload)
        
        # Test scan validation
        is_valid = qr_generator.validate_qr_scan(session_id, scan_data)
        assert is_valid is True
        
        # Verify scan count incremented
        assert qr_generator.active_codes[session_id]['scan_count'] == 1
        assert 'last_scan' in qr_generator.active_codes[session_id]
    
    def test_validate_qr_scan_invalid_session(self, qr_generator):
        """Test QR scan validation with invalid session"""
        is_valid = qr_generator.validate_qr_scan("nonexistent_session", "{}")
        assert is_valid is False
    
    def test_validate_qr_scan_expired(self, qr_generator, sample_entropy_data):
        """Test QR scan validation with expired session"""
        session_id = "expired_session"
        
        # Generate QR code
        qr_result = qr_generator.generate_authentication_qr(session_id, sample_entropy_data)
        assert qr_result['success'] is True
        
        # Manually expire the session
        code_data = qr_generator.active_codes[session_id]
        past_time = datetime.utcnow() - timedelta(minutes=10)
        code_data['base_data']['expires_at'] = past_time.isoformat()
        
        # Test validation
        scan_payload = {'challenge': code_data['base_data']['challenge']}
        is_valid = qr_generator.validate_qr_scan(session_id, json.dumps(scan_payload))
        
        assert is_valid is False
        assert session_id not in qr_generator.active_codes  # Should be cleaned up
    
    def test_validate_qr_scan_max_scans_exceeded(self, qr_generator, sample_entropy_data):
        """Test QR scan validation when max scans exceeded"""
        session_id = "max_scans_session"
        user_context = {'max_scans': 2}
        
        # Generate QR code
        qr_result = qr_generator.generate_authentication_qr(
            session_id, sample_entropy_data, user_context=user_context
        )
        assert qr_result['success'] is True
        
        # Prepare scan data
        code_data = qr_generator.active_codes[session_id]
        scan_payload = {'challenge': code_data['base_data']['challenge']}
        scan_data = json.dumps(scan_payload)
        
        # Perform allowed scans
        assert qr_generator.validate_qr_scan(session_id, scan_data) is True  # Scan 1
        assert qr_generator.validate_qr_scan(session_id, scan_data) is True  # Scan 2
        
        # Third scan should fail
        assert qr_generator.validate_qr_scan(session_id, scan_data) is False
        
        # Session should be invalidated
        assert qr_generator.active_codes[session_id]['invalidated'] is True
        assert qr_generator.active_codes[session_id]['invalidation_reason'] == 'scan_limit_exceeded'
    
    def test_validate_qr_scan_challenge_mismatch(self, qr_generator, sample_entropy_data):
        """Test QR scan validation with challenge mismatch"""
        session_id = "challenge_mismatch_session"
        
        # Generate QR code
        qr_result = qr_generator.generate_authentication_qr(session_id, sample_entropy_data)
        assert qr_result['success'] is True
        
        # Use wrong challenge
        scan_payload = {'challenge': 'wrong_challenge'}
        scan_data = json.dumps(scan_payload)
        
        is_valid = qr_generator.validate_qr_scan(session_id, scan_data)
        assert is_valid is False
    
    def test_constitutional_validation(self, qr_generator):
        """Test Trinity Framework constitutional validation (🛡️ Guardian)"""
        # Valid data
        valid_qr_data = {
            'session_id': 'valid_session_123',
            'timestamp': datetime.utcnow().isoformat(),
            'challenge': 'valid_challenge'
        }
        valid_entropy = b'valid_entropy_data'
        
        result = qr_generator._constitutional_validation(valid_qr_data, valid_entropy)
        assert result is True
        
        # Test suspicious patterns
        suspicious_qr_data = {
            'session_id': 'session_with_<script>alert("xss")</script>',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        result = qr_generator._constitutional_validation(suspicious_qr_data, valid_entropy)
        assert result is False
        
        # Test oversized entropy
        oversized_entropy = b'x' * 2048  # 2KB entropy (over 1KB limit)
        result = qr_generator._constitutional_validation(valid_qr_data, oversized_entropy)
        assert result is False
        
        # Test invalid session ID
        invalid_session_data = {
            'session_id': '1234567',  # Too short (< 8 chars)
            'timestamp': datetime.utcnow().isoformat()
        }
        
        result = qr_generator._constitutional_validation(invalid_session_data, valid_entropy)
        assert result is False
    
    def test_cleanup_expired_codes(self, qr_generator, sample_entropy_data):
        """Test cleanup of expired QR codes"""
        # Generate multiple QR codes
        session1 = "session_1"
        session2 = "session_2"
        session3 = "session_3"
        
        qr_generator.generate_authentication_qr(session1, sample_entropy_data)
        qr_generator.generate_authentication_qr(session2, sample_entropy_data)
        qr_generator.generate_authentication_qr(session3, sample_entropy_data)
        
        assert len(qr_generator.active_codes) == 3
        
        # Manually expire some sessions
        past_time = datetime.utcnow() - timedelta(minutes=10)
        qr_generator.active_codes[session1]['base_data']['expires_at'] = past_time.isoformat()
        qr_generator.active_codes[session2]['base_data']['expires_at'] = past_time.isoformat()
        
        # Trigger cleanup
        qr_generator._cleanup_expired_codes()
        
        # Only session3 should remain
        assert len(qr_generator.active_codes) == 1
        assert session3 in qr_generator.active_codes
        assert session1 not in qr_generator.active_codes
        assert session2 not in qr_generator.active_codes
    
    def test_refresh_qr_code(self, qr_generator, sample_entropy_data):
        """Test QR code refresh functionality"""
        session_id = "refresh_test_session"
        
        # Generate initial QR code
        qr_result = qr_generator.generate_authentication_qr(session_id, sample_entropy_data)
        refresh_token = qr_result['refresh_token']
        original_expires_at = qr_result['expires_at']
        
        # Wait a bit to ensure time difference
        time.sleep(0.1)
        
        # Refresh QR code
        refresh_result = qr_generator.refresh_qr_code(session_id, refresh_token)
        
        assert refresh_result['success'] is True
        assert 'new_expires_at' in refresh_result
        assert 'new_challenge' in refresh_result
        
        # Verify expiration time was extended
        new_expires_at = refresh_result['new_expires_at']
        assert new_expires_at > original_expires_at
        
        # Verify challenge was updated
        code_data = qr_generator.active_codes[session_id]
        assert code_data['base_data']['challenge'] == refresh_result['new_challenge']
    
    def test_refresh_qr_code_invalid_session(self, qr_generator):
        """Test QR code refresh with invalid session"""
        result = qr_generator.refresh_qr_code("nonexistent_session", "fake_token")
        
        assert result['success'] is False
        assert result['error'] == 'Session not found'
    
    def test_refresh_qr_code_invalid_token(self, qr_generator, sample_entropy_data):
        """Test QR code refresh with invalid refresh token"""
        session_id = "invalid_token_session"
        
        # Generate QR code
        qr_result = qr_generator.generate_authentication_qr(session_id, sample_entropy_data)
        
        # Try refresh with wrong token
        result = qr_generator.refresh_qr_code(session_id, "wrong_token")
        
        assert result['success'] is False
        assert result['error'] == 'Invalid refresh token'
    
    def test_get_active_sessions(self, qr_generator, sample_entropy_data):
        """Test getting active sessions"""
        # Initially no sessions
        active = qr_generator.get_active_sessions()
        assert len(active) == 0
        
        # Generate some sessions
        session1 = "active_session_1"
        session2 = "active_session_2"
        
        qr_generator.generate_authentication_qr(session1, sample_entropy_data)
        qr_generator.generate_authentication_qr(session2, sample_entropy_data)
        
        # Get active sessions
        active = qr_generator.get_active_sessions()
        
        assert len(active) == 2
        assert session1 in active
        assert session2 in active
        
        # Verify session data format
        for session_id, data in active.items():
            assert 'expires_at' in data
            assert 'scan_count' in data
            assert 'max_scans' in data
            assert 'created_at' in data
            assert data['scan_count'] == 0  # No scans yet
    
    def test_performance_requirements(self, qr_generator, sample_entropy_data):
        """Test that QR generation meets performance requirements"""
        session_id = "performance_test"
        num_iterations = 10
        
        generation_times = []
        
        for i in range(num_iterations):
            start_time = time.time()
            result = qr_generator.generate_authentication_qr(
                f"{session_id}_{i}", sample_entropy_data
            )
            generation_time = (time.time() - start_time) * 1000  # Convert to ms
            
            assert result['success'] is True
            generation_times.append(generation_time)
        
        # Calculate p95 latency
        generation_times.sort()
        p95_index = int(0.95 * len(generation_times))
        p95_latency = generation_times[p95_index]
        
        # Verify p95 latency meets requirement (<100ms)
        # Note: Being generous for CI environment, but should be much faster in production
        assert p95_latency < 500, f"P95 latency {p95_latency:.2f}ms exceeds requirement"
        
        # Average should be even better
        avg_latency = sum(generation_times) / len(generation_times)
        assert avg_latency < 200, f"Average latency {avg_latency:.2f}ms too high"
    
    def test_trinity_framework_integration(self, qr_generator, sample_entropy_data):
        """Test Trinity Framework integration (⚛️🧠🛡️)"""
        session_id = "trinity_test_session"
        
        result = qr_generator.generate_authentication_qr(session_id, sample_entropy_data)
        
        # Verify Trinity compliance indicators
        assert result['constitutional_validated'] is True  # 🛡️ Guardian validation
        assert result['guardian_approved'] is True
        
        # Verify session data includes Trinity elements
        code_data = qr_generator.active_codes[session_id]
        base_data = code_data['base_data']
        
        # ⚛️ Identity - Session integrity
        assert 'session_id' in base_data
        assert len(base_data['session_id']) >= 8
        
        # 🧠 Consciousness - Temporal awareness
        assert 'timestamp' in base_data
        assert 'expires_at' in base_data
        timestamp = datetime.fromisoformat(base_data['timestamp'])
        expires_at = datetime.fromisoformat(base_data['expires_at'])
        assert expires_at > timestamp
        
        # 🛡️ Guardian - Security challenge
        assert 'challenge' in base_data
        assert len(base_data['challenge']) >= 32  # Strong challenge