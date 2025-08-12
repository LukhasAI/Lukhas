"""
LUKHAS Consent Fabric Service
============================
Implements capability-based consent with macaroon tokens.
Core consent management service for the Unified Consent Graph (UCG).

System-wide guardrails applied:
1. Canonical identity is ΛID = {namespace?}:{username}
2. Data minimization: metadata-only reads by default
3. Capability tokens: short-lived, least-privilege JWT with caveats
4. Everything has logs, audit trail, and revocation paths

ACK GUARDRAILS
"""

import asyncio
import hashlib
import json
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

import asyncpg
from pydantic import BaseModel, Field, validator

# Mock macaroon library (in production use pymacaroons)
try:
    from pymacaroons import Macaroon
    MACAROONS_AVAILABLE = True
except ImportError:
    MACAROONS_AVAILABLE = False
    print("WARNING: pymacaroons not available, using mock implementation")


class ConsentGrantRequest(BaseModel):
    """Request model for granting consent"""
    lid: str = Field(..., description="Canonical ΛID")
    service: str = Field(..., description="Service name (gmail, drive, etc.)")
    scopes: List[str] = Field(..., description="Requested scopes")
    purpose: str = Field(..., description="Human-readable purpose")
    ttl_minutes: int = Field(60, description="Time-to-live in minutes")
    resource_pattern: Optional[str] = Field(None, description="Resource filter pattern")

    @validator('scopes')
    def validate_scopes(cls, v):
        if not v or len(v) == 0:
            raise ValueError("At least one scope required")
        return v

    @validator('ttl_minutes')
    def validate_ttl(cls, v):
        if v < 1 or v > 1440:  # Max 24 hours
            raise ValueError("TTL must be between 1 and 1440 minutes")
        return v


class ConsentRevokeRequest(BaseModel):
    """Request model for revoking consent"""
    lid: str = Field(..., description="Canonical ΛID")
    grant_id: Optional[str] = Field(None, description="Specific grant ID to revoke")
    service: Optional[str] = Field(None, description="Service name filter")
    scopes: Optional[List[str]] = Field(None, description="Scope name filters")
    reason: str = Field("User requested", description="Revocation reason")


class CapabilityToken(BaseModel):
    """Capability token with macaroon caveats"""
    token: str = Field(..., description="Macaroon token string")
    expires_at: datetime = Field(..., description="Token expiration")
    scopes: List[str] = Field(..., description="Granted scopes")
    resource_ids: Optional[List[str]] = Field(None, description="Specific resource IDs")
    caveats: Dict[str, Any] = Field(..., description="Token caveats/restrictions")


class ConsentLedgerEntry(BaseModel):
    """Human-readable consent ledger entry"""
    grant_id: str
    service: str
    purpose: str
    scopes: List[str]
    granted_at: datetime
    expires_at: datetime
    last_used_at: Optional[datetime]
    use_count: int
    status: str
    active_tokens: int


class ConsentService:
    """
    Core consent management service implementing Unified Consent Graph.
    Handles consent grants, capability tokens, and audit trails.
    """

    def __init__(self, db_url: str = "postgresql://localhost/lukhas"):
        self.db_url = db_url
        self.db_pool = None

        # Macaroon signing key (in production: use KMS/HSM)
        self.macaroon_key = secrets.token_bytes(32)

        # Default security policies
        self.max_token_ttl = timedelta(hours=4)
        self.default_metadata_ttl = timedelta(hours=4)
        self.default_content_ttl = timedelta(minutes=30)
        self.default_admin_ttl = timedelta(minutes=5)

    async def initialize(self):
        """Initialize database connection pool"""
        self.db_pool = await asyncpg.create_pool(
            self.db_url,
            min_size=2,
            max_size=10,
            command_timeout=30
        )

    async def close(self):
        """Close database connections"""
        if self.db_pool:
            await self.db_pool.close()

    async def grant_consent(
        self,
        request: ConsentGrantRequest,
        client_ip: Optional[str] = None,
        client_context: Dict[str, Any] = None
    ) -> Tuple[str, CapabilityToken]:
        """
        Grant consent and issue capability token.
        
        Returns:
            (grant_id, capability_token) tuple
        """
        start_time = time.perf_counter()

        async with self.db_pool.acquire() as conn:
            try:
                # Validate service and scopes exist
                service_info = await self._validate_service_and_scopes(conn, request.service, request.scopes)

                # Determine TTL based on scope levels
                effective_ttl = self._calculate_effective_ttl(service_info['scope_levels'], request.ttl_minutes)

                # Create consent grant using database function
                grant_id = await conn.fetchval("""
                    SELECT consent.grant_consent($1, $2, $3, $4, $5, $6, $7, $8)
                """,
                    request.lid,
                    request.service,
                    request.scopes,
                    request.purpose,
                    effective_ttl,
                    request.resource_pattern,
                    client_ip,
                    json.dumps(client_context or {})
                )

                # Generate capability token
                capability_token = await self._issue_capability_token(
                    conn, grant_id, request.lid, request.service,
                    request.scopes, effective_ttl, request.resource_pattern,
                    client_ip
                )

                # Log performance
                processing_time = (time.perf_counter() - start_time) * 1000
                await self._log_audit_event(
                    conn, 'grant', request.lid, request.service,
                    grant_id=grant_id, scopes=request.scopes, purpose=request.purpose,
                    client_ip=client_ip, processing_time_ms=processing_time, success=True
                )

                return str(grant_id), capability_token

            except Exception as e:
                # Log failure
                processing_time = (time.perf_counter() - start_time) * 1000
                await self._log_audit_event(
                    conn, 'grant', request.lid, request.service,
                    scopes=request.scopes, purpose=request.purpose,
                    client_ip=client_ip, processing_time_ms=processing_time,
                    success=False, error_message=str(e)
                )
                raise

    async def revoke_consent(
        self,
        request: ConsentRevokeRequest,
        client_ip: Optional[str] = None
    ) -> int:
        """
        Revoke consent grants and invalidate tokens.
        
        Returns:
            Number of grants revoked
        """
        start_time = time.perf_counter()

        async with self.db_pool.acquire() as conn:
            try:
                # Use database function for revocation
                revoked_count = await conn.fetchval("""
                    SELECT consent.revoke_consent($1, $2, $3, $4, $5)
                """,
                    request.lid,
                    request.grant_id,
                    request.service,
                    request.scopes,
                    request.reason
                )

                # Log the revocation
                processing_time = (time.perf_counter() - start_time) * 1000
                await self._log_audit_event(
                    conn, 'revoke', request.lid, request.service,
                    scopes=request.scopes, purpose=request.reason,
                    client_ip=client_ip, processing_time_ms=processing_time,
                    success=True, metadata={'revoked_count': revoked_count}
                )

                return revoked_count

            except Exception as e:
                # Log failure
                processing_time = (time.perf_counter() - start_time) * 1000
                await self._log_audit_event(
                    conn, 'revoke', request.lid, request.service,
                    scopes=request.scopes, purpose=request.reason,
                    client_ip=client_ip, processing_time_ms=processing_time,
                    success=False, error_message=str(e)
                )
                raise

    async def get_consent_ledger(
        self,
        lid: str,
        service: Optional[str] = None,
        active_only: bool = True
    ) -> List[ConsentLedgerEntry]:
        """
        Get human-readable consent ledger for user.
        """
        async with self.db_pool.acquire() as conn:
            query = """
                SELECT grant_id, service_name, purpose, granted_scopes, 
                       granted_at, expires_at, last_used_at, use_count,
                       status, active_tokens
                FROM consent.active_grants_summary
                WHERE user_lid = $1
            """
            params = [lid]

            if service:
                query += " AND service_name = $2"
                params.append(service)

            if active_only:
                query += f" AND status = ${'3' if service else '2'}"
                params.append('active')

            query += " ORDER BY granted_at DESC"

            rows = await conn.fetch(query, *params)

            return [
                ConsentLedgerEntry(
                    grant_id=str(row['grant_id']),
                    service=row['service_name'],
                    purpose=row['purpose'],
                    scopes=row['granted_scopes'],
                    granted_at=row['granted_at'],
                    expires_at=row['expires_at'],
                    last_used_at=row['last_used_at'],
                    use_count=row['use_count'],
                    status=row['status'],
                    active_tokens=row['active_tokens']
                )
                for row in rows
            ]

    async def verify_capability_token(
        self,
        token: str,
        required_scopes: List[str],
        resource_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify capability token and check caveats.
        
        Returns:
            Token claims if valid, raises exception if invalid
        """
        start_time = time.perf_counter()

        try:
            # Parse macaroon token
            if MACAROONS_AVAILABLE:
                macaroon = Macaroon.deserialize(token)
                claims = self._verify_macaroon(macaroon, required_scopes, resource_id)
            else:
                # Mock verification for development
                claims = self._mock_verify_token(token, required_scopes, resource_id)

            # Update token usage
            async with self.db_pool.acquire() as conn:
                await self._record_token_usage(conn, claims['token_id'], resource_id)

            return claims

        except Exception as e:
            # Log verification failure
            async with self.db_pool.acquire() as conn:
                processing_time = (time.perf_counter() - start_time) * 1000
                await self._log_audit_event(
                    conn, 'verify', 'unknown', 'unknown',
                    scopes=required_scopes,
                    resource_identifier=resource_id,
                    processing_time_ms=processing_time,
                    success=False, error_message=str(e)
                )
            raise ValueError(f"Token verification failed: {str(e)}")

    async def escalate_to_content(
        self,
        lid: str,
        service: str,
        resource_id: str,
        purpose: str,
        ttl_minutes: int = 30
    ) -> CapabilityToken:
        """
        Escalate from metadata-only to content access for specific resource.
        """
        # Determine content scopes based on service
        content_scopes = self._get_content_escalation_scopes(service)

        # Create narrow grant for specific resource
        request = ConsentGrantRequest(
            lid=lid,
            service=service,
            scopes=content_scopes,
            purpose=f"Content access: {purpose}",
            ttl_minutes=min(ttl_minutes, 30),  # Max 30min for content access
            resource_pattern=resource_id
        )

        grant_id, capability_token = await self.grant_consent(request)

        # Log escalation
        async with self.db_pool.acquire() as conn:
            await self._log_audit_event(
                conn, 'escalate', lid, service,
                scopes=content_scopes, purpose=purpose,
                resource_identifier=resource_id, success=True
            )

        return capability_token

    async def cleanup_expired(self) -> Dict[str, int]:
        """Clean up expired grants and tokens"""
        async with self.db_pool.acquire() as conn:
            result = await conn.fetchrow("SELECT * FROM consent.cleanup_expired()")
            return {
                'expired_grants': result['expired_grants'],
                'expired_tokens': result['expired_tokens']
            }

    # Private helper methods

    async def _validate_service_and_scopes(self, conn, service_name: str, scopes: List[str]) -> Dict:
        """Validate that service and scopes exist"""
        service_query = """
            SELECT s.service_id, s.service_name, s.max_scope_level,
                   array_agg(sc.scope_name) as available_scopes,
                   array_agg(sc.scope_level) as scope_levels
            FROM consent.services s
            LEFT JOIN consent.scopes sc ON s.service_id = sc.service_id
            WHERE s.service_name = $1
            GROUP BY s.service_id, s.service_name, s.max_scope_level
        """

        service_info = await conn.fetchrow(service_query, service_name)
        if not service_info:
            raise ValueError(f"Service not found: {service_name}")

        # Check that all requested scopes are available
        available_scopes = service_info['available_scopes'] or []
        for scope in scopes:
            if scope not in available_scopes:
                raise ValueError(f"Scope '{scope}' not available for service '{service_name}'")

        return dict(service_info)

    def _calculate_effective_ttl(self, scope_levels: List[str], requested_ttl: int) -> int:
        """Calculate effective TTL based on scope security levels"""
        max_level = 'metadata'

        for level in scope_levels:
            if level == 'admin':
                max_level = 'admin'
                break
            elif level == 'content' and max_level == 'metadata':
                max_level = 'content'

        # Enforce security limits based on scope level
        if max_level == 'admin':
            return min(requested_ttl, 5)  # Max 5 minutes for admin
        elif max_level == 'content':
            return min(requested_ttl, 30)  # Max 30 minutes for content
        else:
            return min(requested_ttl, 240)  # Max 4 hours for metadata

    async def _issue_capability_token(
        self, conn, grant_id: str, lid: str, service: str,
        scopes: List[str], ttl_minutes: int, resource_pattern: Optional[str],
        client_ip: Optional[str]
    ) -> CapabilityToken:
        """Issue capability token with macaroon caveats"""

        expires_at = datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)

        # Create macaroon with caveats
        if MACAROONS_AVAILABLE:
            macaroon = Macaroon(
                location='https://consent.lukhas.com',
                identifier=f'grant:{grant_id}',
                key=self.macaroon_key
            )

            # Add caveats
            macaroon.add_first_party_caveat(f'lid = {lid}')
            macaroon.add_first_party_caveat(f'service = {service}')
            macaroon.add_first_party_caveat(f'scopes = {",".join(scopes)}')
            macaroon.add_first_party_caveat(f'expires_at = {expires_at.isoformat()}')

            if resource_pattern:
                macaroon.add_first_party_caveat(f'resource_pattern = {resource_pattern}')
            if client_ip:
                macaroon.add_first_party_caveat(f'client_ip = {client_ip}')

            token_str = macaroon.serialize()
        else:
            # Mock token for development
            token_data = {
                'grant_id': str(grant_id),
                'lid': lid,
                'service': service,
                'scopes': scopes,
                'expires_at': expires_at.isoformat(),
                'resource_pattern': resource_pattern,
                'client_ip': client_ip
            }
            token_str = f"mock_macaroon_{secrets.token_urlsafe(32)}_{json.dumps(token_data)}"

        # Store token in database
        token_hash = hashlib.sha256(token_str.encode()).hexdigest()

        await conn.execute("""
            INSERT INTO consent.capability_tokens 
            (grant_id, token_hash, macaroon_data, scopes, expires_at, client_ip)
            VALUES ($1, $2, $3, $4, $5, $6)
        """, grant_id, token_hash, token_str, scopes, expires_at, client_ip)

        # Build caveats dict
        caveats = {
            'service': service,
            'ttl_minutes': ttl_minutes,
            'resource_pattern': resource_pattern,
            'client_ip': client_ip
        }

        return CapabilityToken(
            token=token_str,
            expires_at=expires_at,
            scopes=scopes,
            resource_ids=[resource_pattern] if resource_pattern else None,
            caveats=caveats
        )

    def _verify_macaroon(self, macaroon, required_scopes: List[str], resource_id: Optional[str]) -> Dict[str, Any]:
        """Verify macaroon caveats (production implementation)"""
        # In production: implement full macaroon verification
        # For now, extract basic claims
        identifier = macaroon.identifier
        if not identifier.startswith('grant:'):
            raise ValueError("Invalid macaroon identifier")

        grant_id = identifier.split(':', 1)[1]

        # Check caveats (simplified)
        caveat_dict = {}
        for caveat in macaroon.caveats:
            if ' = ' in caveat.caveat_id:
                key, value = caveat.caveat_id.split(' = ', 1)
                caveat_dict[key] = value

        # Verify expiration
        if 'expires_at' in caveat_dict:
            expires_at = datetime.fromisoformat(caveat_dict['expires_at'])
            if datetime.now(timezone.utc) > expires_at:
                raise ValueError("Token expired")

        # Verify scopes
        if 'scopes' in caveat_dict:
            granted_scopes = caveat_dict['scopes'].split(',')
            for scope in required_scopes:
                if scope not in granted_scopes:
                    raise ValueError(f"Scope '{scope}' not granted")

        return {
            'token_id': grant_id,
            'lid': caveat_dict.get('lid'),
            'service': caveat_dict.get('service'),
            'scopes': caveat_dict.get('scopes', '').split(','),
            'resource_pattern': caveat_dict.get('resource_pattern')
        }

    def _mock_verify_token(self, token: str, required_scopes: List[str], resource_id: Optional[str]) -> Dict[str, Any]:
        """Mock token verification for development"""
        if not token.startswith('mock_macaroon_'):
            raise ValueError("Invalid mock token format")

        try:
            # Extract JSON data from mock token
            parts = token.split('_', 2)
            if len(parts) < 3:
                raise ValueError("Invalid mock token structure")

            token_data = json.loads(parts[2])

            # Check expiration
            expires_at = datetime.fromisoformat(token_data['expires_at'])
            if datetime.now(timezone.utc) > expires_at:
                raise ValueError("Token expired")

            # Check scopes
            granted_scopes = token_data['scopes']
            for scope in required_scopes:
                if scope not in granted_scopes:
                    raise ValueError(f"Scope '{scope}' not granted")

            return {
                'token_id': token_data['grant_id'],
                'lid': token_data['lid'],
                'service': token_data['service'],
                'scopes': token_data['scopes'],
                'resource_pattern': token_data.get('resource_pattern')
            }

        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Invalid mock token data: {e}")

    def _get_content_escalation_scopes(self, service: str) -> List[str]:
        """Get appropriate content scopes for escalation"""
        escalation_map = {
            'gmail': ['email.read.content'],
            'drive': ['files.read.content'],
            'dropbox': ['files.read.content'],
            'icloud': ['files.read.content']
        }
        return escalation_map.get(service, ['content.read'])

    async def _record_token_usage(self, conn, token_id: str, resource_id: Optional[str]):
        """Record token usage for audit trail"""
        await conn.execute("""
            UPDATE consent.capability_tokens 
            SET last_used_at = NOW(), use_count = use_count + 1
            WHERE token_hash = $1
        """, token_id)

        # Log usage
        await self._log_audit_event(
            conn, 'use', 'token_user', 'token_service',
            resource_identifier=resource_id, success=True
        )

    async def _log_audit_event(
        self, conn, event_type: str, user_lid: str, service_name: str,
        grant_id: Optional[str] = None, scopes: Optional[List[str]] = None,
        purpose: Optional[str] = None, resource_identifier: Optional[str] = None,
        client_ip: Optional[str] = None, processing_time_ms: Optional[float] = None,
        success: bool = True, error_message: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """Log audit event"""
        await conn.execute("""
            INSERT INTO consent.audit_log (
                event_type, user_lid, service_name, grant_id, scopes, purpose,
                resource_identifier, client_ip, processing_time_ms, success, 
                error_message, metadata
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
        """,
            event_type, user_lid, service_name, grant_id, scopes, purpose,
            resource_identifier, client_ip, processing_time_ms, success,
            error_message, json.dumps(metadata or {})
        )


# Usage example and testing
async def demonstrate_consent_service():
    """Demonstrate consent service functionality"""
    print("🔐 LUKHAS Consent Service Demonstration")
    print("=" * 45)

    service = ConsentService("postgresql://localhost/lukhas_test")
    await service.initialize()

    try:
        # Grant consent
        print("📝 Granting consent for Gmail metadata access...")
        request = ConsentGrantRequest(
            lid="gonzo",
            service="gmail",
            scopes=["email.read.headers"],
            purpose="Unified inbox display",
            ttl_minutes=120
        )

        grant_id, token = await service.grant_consent(request, client_ip="192.168.1.100")
        print(f"✅ Grant ID: {grant_id}")
        print(f"🎟️  Token expires at: {token.expires_at}")

        # Verify token
        print("\n🔍 Verifying capability token...")
        claims = await service.verify_capability_token(
            token.token,
            ["email.read.headers"]
        )
        print(f"✅ Token valid for: {claims['scopes']}")

        # Get consent ledger
        print("\n📋 Getting consent ledger...")
        ledger = await service.get_consent_ledger("gonzo")
        for entry in ledger:
            print(f"  • {entry.service}: {', '.join(entry.scopes)} (expires: {entry.expires_at})")

        # Escalate to content access
        print("\n📈 Escalating to content access...")
        content_token = await service.escalate_to_content(
            "gonzo", "gmail", "thread_123", "Read specific email", 15
        )
        print(f"🎟️  Content token: {content_token.scopes}")

        # Revoke consent
        print("\n🚫 Revoking consent...")
        revoke_request = ConsentRevokeRequest(
            lid="gonzo",
            service="gmail",
            reason="Demo cleanup"
        )
        revoked_count = await service.revoke_consent(revoke_request)
        print(f"✅ Revoked {revoked_count} grants")

    finally:
        await service.close()

    print("\n🎉 Consent service demonstration complete!")


if __name__ == "__main__":
    asyncio.run(demonstrate_consent_service())
