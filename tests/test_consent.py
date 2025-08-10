"""
Unit Tests for LUKHAS Consent Fabric
====================================
Tests for consent grants, capability tokens, and audit trails.
"""

import asyncio
import json
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch, MagicMock

from consent.service import (
    ConsentService, ConsentGrantRequest, ConsentRevokeRequest,
    CapabilityToken, ConsentLedgerEntry
)
from consent.api import router as consent_router


class TestConsentService:
    """Test suite for ConsentService"""
    
    @pytest.fixture
    async def service(self):
        """Create test consent service with mocked database"""
        service = ConsentService("postgresql://test")
        
        # Mock database pool
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        service.db_pool = mock_pool
        
        yield service, mock_conn
        
        if service.db_pool:
            await service.close()
    
    @pytest.mark.asyncio
    async def test_grant_consent_metadata_scope(self, service):
        """Test granting consent for metadata-only scope"""
        consent_service, mock_conn = service
        
        # Mock service validation
        mock_conn.fetchrow.return_value = {
            'service_id': 'uuid-123',
            'service_name': 'gmail',
            'max_scope_level': 'content',
            'available_scopes': ['email.read.headers', 'email.read.content'],
            'scope_levels': ['metadata', 'content']
        }
        
        # Mock grant creation
        mock_conn.fetchval.return_value = 'grant-uuid-456'
        mock_conn.execute.return_value = None
        
        # Test request
        request = ConsentGrantRequest(
            lid="gonzo",
            service="gmail",
            scopes=["email.read.headers"],
            purpose="Unified inbox display",
            ttl_minutes=240
        )
        
        grant_id, token = await consent_service.grant_consent(request)
        
        # Assertions
        assert grant_id == "grant-uuid-456"
        assert isinstance(token, CapabilityToken)
        assert token.scopes == ["email.read.headers"]
        assert "gmail" in token.caveats["service"]
        
        # Verify database calls
        mock_conn.fetchval.assert_called()  # grant_consent function called
        mock_conn.execute.assert_called()  # token storage called
    
    @pytest.mark.asyncio
    async def test_grant_consent_content_scope_limited_ttl(self, service):
        """Test that content scopes get limited TTL"""
        consent_service, mock_conn = service
        
        # Mock service with content scopes
        mock_conn.fetchrow.return_value = {
            'service_id': 'uuid-123',
            'service_name': 'gmail',
            'max_scope_level': 'content',
            'available_scopes': ['email.read.content'],
            'scope_levels': ['content']
        }
        
        mock_conn.fetchval.return_value = 'grant-uuid-789'
        mock_conn.execute.return_value = None
        
        # Request long TTL for content scope
        request = ConsentGrantRequest(
            lid="gonzo",
            service="gmail",
            scopes=["email.read.content"],
            purpose="Read specific email",
            ttl_minutes=480  # 8 hours requested
        )
        
        grant_id, token = await consent_service.grant_consent(request)
        
        # TTL should be limited to 30 minutes for content
        token_expiry = token.expires_at
        now = datetime.now(timezone.utc)
        time_diff = token_expiry - now
        
        assert time_diff.total_seconds() <= 30 * 60 + 60  # 30 min + 1 min tolerance
        assert token.caveats["ttl_minutes"] <= 30
    
    @pytest.mark.asyncio
    async def test_grant_consent_admin_scope_very_limited_ttl(self, service):
        """Test that admin scopes get very short TTL"""
        consent_service, mock_conn = service
        
        # Mock service with admin scopes
        mock_conn.fetchrow.return_value = {
            'service_id': 'uuid-123',
            'service_name': 'gmail',
            'max_scope_level': 'admin',
            'available_scopes': ['email.delete'],
            'scope_levels': ['admin']
        }
        
        mock_conn.fetchval.return_value = 'grant-uuid-admin'
        mock_conn.execute.return_value = None
        
        # Request admin scope
        request = ConsentGrantRequest(
            lid="gonzo", 
            service="gmail",
            scopes=["email.delete"],
            purpose="Delete specific email",
            ttl_minutes=60  # 1 hour requested
        )
        
        grant_id, token = await consent_service.grant_consent(request)
        
        # TTL should be limited to 5 minutes for admin
        assert token.caveats["ttl_minutes"] <= 5
    
    @pytest.mark.asyncio
    async def test_grant_consent_invalid_service(self, service):
        """Test granting consent for non-existent service"""
        consent_service, mock_conn = service
        
        # Mock service not found
        mock_conn.fetchrow.return_value = None
        
        request = ConsentGrantRequest(
            lid="gonzo",
            service="nonexistent",
            scopes=["fake.scope"],
            purpose="Test",
            ttl_minutes=60
        )
        
        with pytest.raises(ValueError, match="Service not found"):
            await consent_service.grant_consent(request)
    
    @pytest.mark.asyncio
    async def test_revoke_consent(self, service):
        """Test revoking consent grants"""
        consent_service, mock_conn = service
        
        # Mock revocation
        mock_conn.fetchval.return_value = 2  # 2 grants revoked
        mock_conn.execute.return_value = None  # audit log
        
        request = ConsentRevokeRequest(
            lid="gonzo",
            service="gmail",
            reason="User requested"
        )
        
        revoked_count = await consent_service.revoke_consent(request)
        
        assert revoked_count == 2
        mock_conn.fetchval.assert_called()  # revoke_consent function
        mock_conn.execute.assert_called()  # audit log
    
    @pytest.mark.asyncio
    async def test_get_consent_ledger(self, service):
        """Test getting consent ledger for user"""
        consent_service, mock_conn = service
        
        # Mock ledger data
        mock_conn.fetch.return_value = [
            {
                'grant_id': 'uuid-1',
                'service_name': 'gmail',
                'purpose': 'Inbox display',
                'granted_scopes': ['email.read.headers'],
                'granted_at': datetime.now(timezone.utc),
                'expires_at': datetime.now(timezone.utc) + timedelta(hours=4),
                'last_used_at': None,
                'use_count': 0,
                'status': 'active',
                'active_tokens': 1
            },
            {
                'grant_id': 'uuid-2', 
                'service_name': 'drive',
                'purpose': 'File listing',
                'granted_scopes': ['files.list.metadata'],
                'granted_at': datetime.now(timezone.utc) - timedelta(hours=1),
                'expires_at': datetime.now(timezone.utc) + timedelta(hours=3),
                'last_used_at': datetime.now(timezone.utc) - timedelta(minutes=30),
                'use_count': 5,
                'status': 'active',
                'active_tokens': 1
            }
        ]
        
        ledger = await consent_service.get_consent_ledger("gonzo")
        
        assert len(ledger) == 2
        assert all(isinstance(entry, ConsentLedgerEntry) for entry in ledger)
        assert ledger[0].service == 'gmail'
        assert ledger[1].service == 'drive'
        assert ledger[1].use_count == 5
    
    @pytest.mark.asyncio
    async def test_verify_capability_token_valid(self, service):
        """Test verifying valid capability token"""
        consent_service, mock_conn = service
        
        # Mock token verification
        mock_conn.execute.return_value = None  # usage update
        
        # Create mock token
        test_token_data = {
            'grant_id': 'grant-123',
            'lid': 'gonzo',
            'service': 'gmail',
            'scopes': ['email.read.headers'],
            'expires_at': (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
            'resource_pattern': None,
            'client_ip': '192.168.1.100'
        }
        mock_token = f"mock_macaroon_test_{json.dumps(test_token_data)}"
        
        claims = await consent_service.verify_capability_token(
            mock_token, 
            ['email.read.headers']
        )
        
        assert claims['lid'] == 'gonzo'
        assert claims['service'] == 'gmail'
        assert 'email.read.headers' in claims['scopes']
    
    @pytest.mark.asyncio
    async def test_verify_capability_token_expired(self, service):
        """Test verifying expired capability token"""
        consent_service, mock_conn = service
        
        # Create expired token
        test_token_data = {
            'grant_id': 'grant-123',
            'lid': 'gonzo', 
            'service': 'gmail',
            'scopes': ['email.read.headers'],
            'expires_at': (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),  # Expired
            'resource_pattern': None,
            'client_ip': '192.168.1.100'
        }
        mock_token = f"mock_macaroon_test_{json.dumps(test_token_data)}"
        
        with pytest.raises(ValueError, match="Token expired"):
            await consent_service.verify_capability_token(
                mock_token,
                ['email.read.headers']
            )
    
    @pytest.mark.asyncio
    async def test_verify_capability_token_insufficient_scope(self, service):
        """Test verifying token with insufficient scopes"""
        consent_service, mock_conn = service
        
        # Token with limited scopes
        test_token_data = {
            'grant_id': 'grant-123',
            'lid': 'gonzo',
            'service': 'gmail', 
            'scopes': ['email.read.headers'],  # Only headers
            'expires_at': (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
            'resource_pattern': None,
            'client_ip': '192.168.1.100'
        }
        mock_token = f"mock_macaroon_test_{json.dumps(test_token_data)}"
        
        # Request content access (not granted)
        with pytest.raises(ValueError, match="Scope 'email.read.content' not granted"):
            await consent_service.verify_capability_token(
                mock_token,
                ['email.read.content']  # Requesting content access
            )
    
    @pytest.mark.asyncio
    async def test_escalate_to_content(self, service):
        """Test escalating from metadata to content access"""
        consent_service, mock_conn = service
        
        # Mock service validation and grant creation for escalation
        mock_conn.fetchrow.return_value = {
            'service_id': 'uuid-gmail',
            'service_name': 'gmail',
            'max_scope_level': 'content',
            'available_scopes': ['email.read.content'],
            'scope_levels': ['content']
        }
        
        mock_conn.fetchval.return_value = 'escalation-grant-uuid'
        mock_conn.execute.return_value = None
        
        # Test escalation
        token = await consent_service.escalate_to_content(
            lid="gonzo",
            service="gmail",
            resource_id="thread_12345",
            purpose="Read specific email thread",
            ttl_minutes=15
        )
        
        assert isinstance(token, CapabilityToken)
        assert "email.read.content" in token.scopes
        assert token.caveats["ttl_minutes"] <= 30  # Content access limited
        assert "thread_12345" in token.resource_ids
    
    @pytest.mark.asyncio
    async def test_cleanup_expired(self, service):
        """Test cleanup of expired grants and tokens"""
        consent_service, mock_conn = service
        
        # Mock cleanup results
        mock_conn.fetchrow.return_value = {
            'expired_grants': 5,
            'expired_tokens': 12
        }
        
        result = await consent_service.cleanup_expired()
        
        assert result['expired_grants'] == 5
        assert result['expired_tokens'] == 12


class TestConsentAPI:
    """Test suite for Consent API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client with mocked service"""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        
        app = FastAPI()
        
        # Mock the consent service dependency
        def mock_get_consent_service():
            mock_service = AsyncMock(spec=ConsentService)
            return mock_service
        
        # Override dependency
        consent_router.dependency_overrides[
            consent_router.dependencies[0]  # get_consent_service
        ] = mock_get_consent_service
        
        app.include_router(consent_router)
        
        return TestClient(app), mock_get_consent_service()
    
    def test_grant_consent_endpoint(self, client):
        """Test POST /consent/grant endpoint"""
        test_client, mock_service = client
        
        # Mock service response
        mock_token = CapabilityToken(
            token="mock_token_123",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            scopes=["email.read.headers"],
            resource_ids=None,
            caveats={"service": "gmail", "ttl_minutes": 60}
        )
        
        mock_service.grant_consent.return_value = ("grant-123", mock_token)
        
        response = test_client.post("/consent/grant", json={
            "lid": "gonzo",
            "service": "gmail",
            "scopes": ["email.read.headers"],
            "purpose": "Unified inbox",
            "ttl_minutes": 60
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["grant_id"] == "grant-123"
        assert data["capability_token"]["scopes"] == ["email.read.headers"]
    
    def test_revoke_consent_endpoint(self, client):
        """Test POST /consent/revoke endpoint"""
        test_client, mock_service = client
        
        # Mock service response
        mock_service.revoke_consent.return_value = 3
        
        response = test_client.post("/consent/revoke", json={
            "lid": "gonzo",
            "service": "gmail",
            "reason": "Test revocation"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["revoked_count"] == 3
        assert "Successfully revoked 3" in data["message"]
    
    def test_get_ledger_endpoint(self, client):
        """Test GET /consent/ledger endpoint"""
        test_client, mock_service = client
        
        # Mock ledger entries
        mock_entries = [
            ConsentLedgerEntry(
                grant_id="uuid-1",
                service="gmail",
                purpose="Inbox display",
                scopes=["email.read.headers"],
                granted_at=datetime.now(timezone.utc),
                expires_at=datetime.now(timezone.utc) + timedelta(hours=4),
                last_used_at=None,
                use_count=0,
                status="active",
                active_tokens=1
            )
        ]
        
        mock_service.get_consent_ledger.return_value = mock_entries
        
        response = test_client.get("/consent/ledger?lid=gonzo")
        
        assert response.status_code == 200
        data = response.json()
        assert data["lid"] == "gonzo"
        assert data["total_entries"] == 1
        assert len(data["entries"]) == 1
        assert data["entries"][0]["service"] == "gmail"
    
    def test_escalate_endpoint(self, client):
        """Test POST /consent/escalate endpoint"""
        test_client, mock_service = client
        
        # Mock escalation response
        mock_token = CapabilityToken(
            token="escalation_token_456",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
            scopes=["email.read.content"],
            resource_ids=["thread_12345"],
            caveats={"service": "gmail", "ttl_minutes": 30}
        )
        
        mock_service.escalate_to_content.return_value = mock_token
        
        response = test_client.post("/consent/escalate", json={
            "lid": "gonzo",
            "service": "gmail",
            "resource_id": "thread_12345",
            "purpose": "Read specific email",
            "ttl_minutes": 15
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["capability_token"]["scopes"] == ["email.read.content"]
        assert data["capability_token"]["resource_ids"] == ["thread_12345"]
    
    def test_verify_token_endpoint_valid(self, client):
        """Test POST /consent/verify endpoint with valid token"""
        test_client, mock_service = client
        
        # Mock verification success
        mock_claims = {
            'lid': 'gonzo',
            'service': 'gmail',
            'scopes': ['email.read.headers'],
            'token_id': 'token-123'
        }
        mock_service.verify_capability_token.return_value = mock_claims
        
        response = test_client.post("/consent/verify", json={
            "token": "valid_token_123",
            "required_scopes": ["email.read.headers"],
            "resource_id": "optional_resource"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["claims"]["lid"] == "gonzo"
        assert data["error"] is None
    
    def test_verify_token_endpoint_invalid(self, client):
        """Test POST /consent/verify endpoint with invalid token"""
        test_client, mock_service = client
        
        # Mock verification failure
        mock_service.verify_capability_token.side_effect = ValueError("Token expired")
        
        response = test_client.post("/consent/verify", json={
            "token": "expired_token_456",
            "required_scopes": ["email.read.headers"]
        })
        
        assert response.status_code == 200  # API doesn't return error status for invalid tokens
        data = response.json()
        assert data["valid"] is False
        assert "Token expired" in data["error"]
    
    def test_health_endpoint(self, client):
        """Test GET /consent/health endpoint"""
        test_client, _ = client
        
        response = test_client.get("/consent/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "LUKHAS Consent Fabric"
    
    def test_info_endpoint(self, client):
        """Test GET /consent/info endpoint"""
        test_client, _ = client
        
        response = test_client.get("/consent/info")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "LUKHAS Consent Fabric"
        assert "Metadata-first consent" in data["features"]
        assert "endpoints" in data
        assert "grant" in data["endpoints"]


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])