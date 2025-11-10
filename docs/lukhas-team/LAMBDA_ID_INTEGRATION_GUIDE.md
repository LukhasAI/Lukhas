# ΛiD Integration Guide for lukhas.team

**Complete Integration of LUKHAS Identity System with next-auth v5**

**Created**: 2025-11-10
**Status**: Integration Design Complete
**Purpose**: Step-by-step guide for integrating ΛiD passkey authentication

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Existing ΛiD System Analysis](#existing-λid-system-analysis)
3. [Architecture Overview](#architecture-overview)
4. [PostgreSQL Migration](#postgresql-migration)
5. [Backend Implementation](#backend-implementation)
6. [Frontend Implementation](#frontend-implementation)
7. [Security Considerations](#security-considerations)
8. [Testing Strategy](#testing-strategy)
9. [Deployment Guide](#deployment-guide)

---

## Executive Summary

### What is ΛiD?

**ΛiD** (Lambda Identity) is LUKHAS AI's consciousness-aware identity system that uses **FIDO2 WebAuthn passkeys** for passwordless authentication.

**Key Features**:
- 🔐 **Passkey-only** - No passwords, ever
- 🧠 **Consciousness-aware** - Tracks identity across distributed cognitive components
- 🛡️ **Guardian-protected** - Constitutional AI enforcement
- ⚡ **Fast** - <100ms authentication
- 📱 **Multi-device** - Passkeys sync via iCloud/Google Password Manager

**Current Status**:
- ✅ WebAuthn verification logic (`lukhas/identity/webauthn_verify.py`)
- ✅ API endpoints (`serve/webauthn_routes.py`)
- ⚠️ **In-memory storage** (needs PostgreSQL migration)
- ❌ No frontend integration yet

**Goal**:
Integrate ΛiD with lukhas.team frontend using **next-auth v5** and migrate to **PostgreSQL** for credential storage.

---

## Existing ΛiD System Analysis

### Current Implementation

#### File: `lukhas/identity/webauthn_verify.py`

**Location**: `/Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas/identity/webauthn_verify.py`

**Key Components**:

```python
# WebAuthn Credential Model
class WebAuthnCredential:
    """Represents a FIDO2 credential"""
    def __init__(
        self,
        credential_id: bytes,
        public_key: bytes,
        sign_count: int,
        user_lambda_id: str,
        created_at: datetime,
    ):
        self.credential_id = credential_id
        self.public_key = public_key
        self.sign_count = sign_count
        self.user_lambda_id = user_lambda_id
        self.created_at = created_at
        self.last_used = created_at

# In-Memory Storage (TO BE REPLACED)
class WebAuthnCredentialStore:
    """In-memory credential storage"""
    def __init__(self):
        self._credentials: Dict[str, WebAuthnCredential] = {}

    def save_credential(self, credential: WebAuthnCredential):
        """Save credential (currently in-memory)"""
        key = base64url_encode(credential.credential_id)
        self._credentials[key] = credential

    def get_credential(self, credential_id: bytes) -> Optional[WebAuthnCredential]:
        """Retrieve credential"""
        key = base64url_encode(credential_id)
        return self._credentials.get(key)

# Verification Function
def verify_assertion(
    credential_id: bytes,
    assertion_response: dict,
    expected_origin: str,
    expected_rp_id: str,
) -> dict:
    """
    Verify WebAuthn assertion

    Returns:
        dict: {
            "verified": bool,
            "lambda_id": str,
            "sign_count": int,
        }
    """
    # 1. Retrieve credential from store
    credential = store.get_credential(credential_id)
    if not credential:
        raise ValueError("Credential not found")

    # 2. Verify origin and RP ID
    if assertion_response["origin"] != expected_origin:
        raise ValueError("Invalid origin")

    # 3. Verify signature using public key
    # (Uses cryptography library for ECDSA verification)
    ...

    # 4. Update sign count (replay attack prevention)
    if assertion_response["sign_count"] <= credential.sign_count:
        raise ValueError("Sign count not incremented - possible replay attack")

    credential.sign_count = assertion_response["sign_count"]
    credential.last_used = datetime.now()

    return {
        "verified": True,
        "lambda_id": credential.user_lambda_id,
        "sign_count": credential.sign_count,
    }
```

**Strengths**:
- ✅ Proper FIDO2 WebAuthn verification
- ✅ Sign count tracking (replay attack prevention)
- ✅ Clean separation of concerns

**Weaknesses**:
- ❌ **In-memory storage** - Data lost on restart
- ❌ No multi-device support (can't share credentials across servers)
- ❌ No backup/recovery mechanism

---

#### File: `serve/webauthn_routes.py`

**Location**: `/Users/agi_dev/LOCAL-REPOS/Lukhas/serve/webauthn_routes.py`

**API Endpoints**:

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/id/webauthn", tags=["authentication"])

class RegistrationRequest(BaseModel):
    email: str
    display_name: str

class RegistrationResponse(BaseModel):
    challenge: str  # Base64-encoded random challenge
    user_id: str    # Lambda ID
    rp_id: str      # Relying Party ID (lukhas.team)
    rp_name: str    # "LUKHAS AI"

@router.post("/register/begin", response_model=RegistrationResponse)
async def begin_registration(request: RegistrationRequest):
    """
    Step 1 of passkey registration

    Returns challenge for WebAuthn credential creation
    """
    # Generate random challenge
    challenge = secrets.token_bytes(32)

    # Create or retrieve Lambda ID
    lambda_id = f"λ{uuid.uuid4().hex[:12]}"  # e.g., λa3f2e9b1c4d5

    # Store challenge temporarily (60s TTL)
    await redis_client.setex(
        f"webauthn:challenge:{lambda_id}",
        60,
        base64url_encode(challenge),
    )

    return {
        "challenge": base64url_encode(challenge),
        "user_id": lambda_id,
        "rp_id": "lukhas.team",
        "rp_name": "LUKHAS AI",
    }

@router.post("/register/complete")
async def complete_registration(credential_data: dict):
    """
    Step 2 of passkey registration

    Stores credential after browser creates it
    """
    # Verify challenge
    lambda_id = credential_data["user_id"]
    stored_challenge = await redis_client.get(f"webauthn:challenge:{lambda_id}")

    if not stored_challenge:
        raise HTTPException(400, "Challenge expired")

    # Extract credential details
    credential = WebAuthnCredential(
        credential_id=base64url_decode(credential_data["id"]),
        public_key=credential_data["public_key"],
        sign_count=0,
        user_lambda_id=lambda_id,
        created_at=datetime.now(),
    )

    # Save to store (currently in-memory)
    store.save_credential(credential)

    return {"lambda_id": lambda_id, "registered": True}

@router.post("/authenticate/begin")
async def begin_authentication(email: str):
    """
    Step 1 of passkey authentication

    Returns challenge for WebAuthn assertion
    """
    # Generate challenge
    challenge = secrets.token_bytes(32)

    # Store challenge (60s TTL)
    await redis_client.setex(
        f"webauthn:auth_challenge:{email}",
        60,
        base64url_encode(challenge),
    )

    # Get user's registered credentials
    # TODO: Look up credentials by email from database
    credentials = []  # Empty for now

    return {
        "challenge": base64url_encode(challenge),
        "allowCredentials": credentials,  # List of registered credential IDs
    }

@router.post("/authenticate/complete")
async def complete_authentication(assertion: dict):
    """
    Step 2 of passkey authentication

    Verifies assertion and returns session token
    """
    # Verify challenge
    email = assertion["email"]
    stored_challenge = await redis_client.get(f"webauthn:auth_challenge:{email}")

    if not stored_challenge:
        raise HTTPException(400, "Challenge expired")

    # Verify assertion using lukhas.identity
    result = verify_assertion(
        credential_id=base64url_decode(assertion["credential_id"]),
        assertion_response=assertion["response"],
        expected_origin="https://lukhas.team",
        expected_rp_id="lukhas.team",
    )

    if not result["verified"]:
        raise HTTPException(401, "Authentication failed")

    # Create session token (JWT)
    token = create_jwt_token(lambda_id=result["lambda_id"])

    return {
        "lambda_id": result["lambda_id"],
        "token": token,
        "email": email,
    }
```

**Strengths**:
- ✅ Complete registration/authentication flow
- ✅ Temporary challenge storage in Redis
- ✅ FastAPI + Pydantic validation

**Weaknesses**:
- ❌ No user lookup by email (hardcoded empty credentials)
- ❌ Relies on in-memory WebAuthnCredentialStore
- ❌ No session management (token creation not implemented)

---

## Architecture Overview

### Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  ΛiD Authentication Flow                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Frontend (Next.js + next-auth v5)                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. User clicks "Sign in with Passkey"               │  │
│  │     ↓                                                 │  │
│  │  2. next-auth calls custom ΛiD provider              │  │
│  │     ↓                                                 │  │
│  │  3. Fetch challenge from LUKHAS API                  │  │
│  │     GET /id/webauthn/authenticate/begin              │  │
│  │     ← {challenge, allowCredentials}                  │  │
│  │     ↓                                                 │  │
│  │  4. Browser WebAuthn API (passkey prompt)            │  │
│  │     navigator.credentials.get(...)                   │  │
│  │     ← User approves with Face ID/Touch ID            │  │
│  │     ← {assertion, credential_id, signature}          │  │
│  │     ↓                                                 │  │
│  │  5. Send assertion to LUKHAS API                     │  │
│  │     POST /id/webauthn/authenticate/complete          │  │
│  │     ← {lambda_id, token, email}                      │  │
│  │     ↓                                                 │  │
│  │  6. next-auth creates session (JWT)                  │  │
│  │     Session stored in Redis                           │  │
│  │     Cookie set (httpOnly, secure, sameSite)          │  │
│  │     ↓                                                 │  │
│  │  7. Redirect to lukhas.team dashboard                │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  Backend (FastAPI + PostgreSQL)                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  ΛiD Verification Pipeline                           │  │
│  │                                                       │  │
│  │  1. POST /authenticate/begin                         │  │
│  │     ↓                                                 │  │
│  │  2. Look up user by email in PostgreSQL              │  │
│  │     SELECT * FROM users WHERE email = ?              │  │
│  │     ↓                                                 │  │
│  │  3. Get user's registered credentials                │  │
│  │     SELECT * FROM webauthn_credentials               │  │
│  │         WHERE lambda_id = ?                          │  │
│  │     ↓                                                 │  │
│  │  4. Generate random challenge                        │  │
│  │     Store in Redis (60s TTL)                         │  │
│  │     ↓                                                 │  │
│  │  5. Return {challenge, allowCredentials}             │  │
│  │                                                       │  │
│  │  POST /authenticate/complete                         │  │
│  │     ↓                                                 │  │
│  │  6. Retrieve challenge from Redis                    │  │
│  │     ↓                                                 │  │
│  │  7. Get credential from PostgreSQL                   │  │
│  │     SELECT * FROM webauthn_credentials               │  │
│  │         WHERE credential_id = ?                      │  │
│  │     ↓                                                 │  │
│  │  8. Verify assertion (lukhas.identity)               │  │
│  │     verify_assertion(...)                            │  │
│  │     - Verify origin & RP ID                          │  │
│  │     - Verify signature (ECDSA)                       │  │
│  │     - Check sign count (replay prevention)           │  │
│  │     ↓                                                 │  │
│  │  9. Update sign count in PostgreSQL                  │  │
│  │     UPDATE webauthn_credentials                      │  │
│  │         SET sign_count = ?, last_used = NOW()        │  │
│  │     ↓                                                 │  │
│  │  10. Create JWT session token                        │  │
│  │      Store in Redis (30 days TTL)                    │  │
│  │      ↓                                                 │  │
│  │  11. Return {lambda_id, token, email}                │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  Database (PostgreSQL)                                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  users                                               │  │
│  │  ├─ lambda_id (PK)                                   │  │
│  │  ├─ email (UNIQUE)                                   │  │
│  │  ├─ display_name                                     │  │
│  │  ├─ team_id (FK)                                     │  │
│  │  └─ created_at                                       │  │
│  │                                                       │  │
│  │  webauthn_credentials                                │  │
│  │  ├─ id (PK)                                          │  │
│  │  ├─ credential_id (UNIQUE, indexed)                 │  │
│  │  ├─ lambda_id (FK → users)                          │  │
│  │  ├─ public_key                                       │  │
│  │  ├─ sign_count                                       │  │
│  │  ├─ device_name                                      │  │
│  │  ├─ created_at                                       │  │
│  │  └─ last_used                                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## PostgreSQL Migration

### Schema Design

#### Table: `users`

```sql
CREATE TABLE users (
    lambda_id VARCHAR(255) PRIMARY KEY,  -- e.g., λa3f2e9b1c4d5
    email VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(255),
    team_id UUID REFERENCES teams(id),
    avatar_url TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_team ON users(team_id);
```

#### Table: `webauthn_credentials`

```sql
CREATE TABLE webauthn_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Credential identification
    credential_id BYTEA UNIQUE NOT NULL,  -- Base64-encoded credential ID
    lambda_id VARCHAR(255) REFERENCES users(lambda_id) ON DELETE CASCADE,

    -- Cryptographic data
    public_key BYTEA NOT NULL,  -- COSE-encoded public key
    sign_count BIGINT DEFAULT 0,  -- Incrementing counter (replay prevention)

    -- Device metadata
    device_name VARCHAR(255),  -- "MacBook Pro", "iPhone 14"
    device_type VARCHAR(50),   -- "platform" (Touch ID) or "cross-platform" (YubiKey)
    aaguid UUID,  -- Authenticator Attestation GUID

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_used TIMESTAMPTZ DEFAULT NOW(),

    -- Backup eligibility (for passkey sync)
    backup_eligible BOOLEAN DEFAULT FALSE,
    backup_state BOOLEAN DEFAULT FALSE,

    -- Transports (usb, nfc, ble, internal)
    transports TEXT[]
);

CREATE INDEX idx_webauthn_cred_id ON webauthn_credentials(credential_id);
CREATE INDEX idx_webauthn_lambda_id ON webauthn_credentials(lambda_id);
CREATE INDEX idx_webauthn_last_used ON webauthn_credentials(last_used DESC);
```

#### Table: `webauthn_challenges` (Temporary Storage)

**Note**: Challenges are stored in Redis (60s TTL), but we keep a PostgreSQL table for audit/debugging.

```sql
CREATE TABLE webauthn_challenges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    challenge BYTEA NOT NULL,
    lambda_id VARCHAR(255) REFERENCES users(lambda_id),
    purpose VARCHAR(50) NOT NULL,  -- 'registration' or 'authentication'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    used BOOLEAN DEFAULT FALSE
);

-- Auto-delete expired challenges (TimescaleDB or cron job)
CREATE INDEX idx_challenges_expires ON webauthn_challenges(expires_at);
```

---

### Alembic Migration Script

**File**: `alembic/versions/001_add_webauthn_tables.py`

```python
"""Add WebAuthn tables

Revision ID: 001
Revises:
Create Date: 2025-11-10
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, BYTEA, JSONB

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('lambda_id', sa.String(255), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('display_name', sa.String(255)),
        sa.Column('team_id', UUID(as_uuid=True)),
        sa.Column('avatar_url', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('last_login', sa.DateTime(timezone=True)),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('metadata', JSONB, server_default='{}'),
    )

    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_team', 'users', ['team_id'])

    # Create webauthn_credentials table
    op.create_table(
        'webauthn_credentials',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('credential_id', BYTEA, nullable=False, unique=True),
        sa.Column('lambda_id', sa.String(255), sa.ForeignKey('users.lambda_id', ondelete='CASCADE'), nullable=False),
        sa.Column('public_key', BYTEA, nullable=False),
        sa.Column('sign_count', sa.BigInteger(), default=0),
        sa.Column('device_name', sa.String(255)),
        sa.Column('device_type', sa.String(50)),
        sa.Column('aaguid', UUID(as_uuid=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('last_used', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('backup_eligible', sa.Boolean(), default=False),
        sa.Column('backup_state', sa.Boolean(), default=False),
        sa.Column('transports', sa.ARRAY(sa.Text())),
    )

    op.create_index('idx_webauthn_cred_id', 'webauthn_credentials', ['credential_id'])
    op.create_index('idx_webauthn_lambda_id', 'webauthn_credentials', ['lambda_id'])
    op.create_index('idx_webauthn_last_used', 'webauthn_credentials', [sa.text('last_used DESC')])

    # Create webauthn_challenges table
    op.create_table(
        'webauthn_challenges',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('challenge', BYTEA, nullable=False),
        sa.Column('lambda_id', sa.String(255), sa.ForeignKey('users.lambda_id')),
        sa.Column('purpose', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used', sa.Boolean(), default=False),
    )

    op.create_index('idx_challenges_expires', 'webauthn_challenges', ['expires_at'])

def downgrade():
    op.drop_table('webauthn_challenges')
    op.drop_table('webauthn_credentials')
    op.drop_table('users')
```

**Run Migration**:
```bash
alembic upgrade head
```

---

### Updated Credential Store (PostgreSQL)

**File**: `lukhas/identity/webauthn_store_postgres.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import base64

from serve.lukhas_team.models import User, WebAuthnCredential as DBCredential
from serve.lukhas_team.database import AsyncSessionLocal

class WebAuthnCredentialStorePostgres:
    """PostgreSQL-backed credential store"""

    async def save_credential(
        self,
        credential_id: bytes,
        lambda_id: str,
        public_key: bytes,
        sign_count: int = 0,
        device_name: Optional[str] = None,
        device_type: Optional[str] = None,
    ):
        """Save credential to PostgreSQL"""
        async with AsyncSessionLocal() as db:
            credential = DBCredential(
                credential_id=credential_id,
                lambda_id=lambda_id,
                public_key=public_key,
                sign_count=sign_count,
                device_name=device_name,
                device_type=device_type,
            )
            db.add(credential)
            await db.commit()

    async def get_credential(self, credential_id: bytes) -> Optional[dict]:
        """Retrieve credential from PostgreSQL"""
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(DBCredential).where(DBCredential.credential_id == credential_id)
            )
            credential = result.scalar_one_or_none()

            if not credential:
                return None

            return {
                "credential_id": credential.credential_id,
                "lambda_id": credential.lambda_id,
                "public_key": credential.public_key,
                "sign_count": credential.sign_count,
                "device_name": credential.device_name,
                "last_used": credential.last_used,
            }

    async def get_credentials_by_lambda_id(self, lambda_id: str) -> list[dict]:
        """Get all credentials for a user"""
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(DBCredential).where(DBCredential.lambda_id == lambda_id)
            )
            credentials = result.scalars().all()

            return [
                {
                    "credential_id": cred.credential_id,
                    "device_name": cred.device_name,
                    "created_at": cred.created_at,
                    "last_used": cred.last_used,
                }
                for cred in credentials
            ]

    async def update_sign_count(self, credential_id: bytes, new_sign_count: int):
        """Update sign count after successful authentication"""
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(DBCredential).where(DBCredential.credential_id == credential_id)
            )
            credential = result.scalar_one_or_none()

            if credential:
                credential.sign_count = new_sign_count
                credential.last_used = datetime.now()
                await db.commit()

    async def delete_credential(self, credential_id: bytes):
        """Delete a credential (device removal)"""
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(DBCredential).where(DBCredential.credential_id == credential_id)
            )
            credential = result.scalar_one_or_none()

            if credential:
                await db.delete(credential)
                await db.commit()
```

---

## Backend Implementation

### Updated API Routes

**File**: `serve/lukhas_team/auth_routes.py`

```python
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import secrets
import base64

from lukhas.identity.webauthn_store_postgres import WebAuthnCredentialStorePostgres
from lukhas.identity.webauthn_verify import verify_assertion
from .database import get_db, AsyncSession
from .models import User, WebAuthnCredential
from .redis_client import redis_client
from .jwt import create_jwt_token

router = APIRouter(prefix="/api/auth", tags=["authentication"])
store = WebAuthnCredentialStorePostgres()

# ============================================================================
# Registration Flow
# ============================================================================

class RegistrationStartRequest(BaseModel):
    email: EmailStr
    display_name: str

class RegistrationStartResponse(BaseModel):
    challenge: str
    lambda_id: str
    rp_id: str
    rp_name: str

@router.post("/register/start", response_model=RegistrationStartResponse)
async def start_registration(
    request: RegistrationStartRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Step 1: Start passkey registration

    Returns WebAuthn challenge for credential creation
    """
    # Check if email already exists
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(400, "Email already registered")

    # Generate Lambda ID
    lambda_id = f"λ{secrets.token_hex(6)}"  # e.g., λa3f2e9b1c4d5

    # Create user (pending passkey creation)
    user = User(
        lambda_id=lambda_id,
        email=request.email,
        display_name=request.display_name,
        is_active=False,  # Activated after passkey creation
    )
    db.add(user)
    await db.commit()

    # Generate challenge
    challenge = secrets.token_bytes(32)
    challenge_b64 = base64.urlsafe_b64encode(challenge).decode().rstrip('=')

    # Store challenge in Redis (60s TTL)
    await redis_client.setex(
        f"webauthn:reg_challenge:{lambda_id}",
        60,
        challenge_b64,
    )

    return {
        "challenge": challenge_b64,
        "lambda_id": lambda_id,
        "rp_id": "lukhas.team",
        "rp_name": "LUKHAS AI",
    }

class RegistrationCompleteRequest(BaseModel):
    lambda_id: str
    credential_id: str  # Base64-encoded
    public_key: str     # Base64-encoded COSE key
    device_name: Optional[str] = None

@router.post("/register/complete")
async def complete_registration(
    request: RegistrationCompleteRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Step 2: Complete passkey registration

    Stores credential after browser creates it
    """
    # Verify challenge exists
    stored_challenge = await redis_client.get(f"webauthn:reg_challenge:{request.lambda_id}")
    if not stored_challenge:
        raise HTTPException(400, "Challenge expired or invalid")

    # Delete challenge (one-time use)
    await redis_client.delete(f"webauthn:reg_challenge:{request.lambda_id}")

    # Decode credential data
    credential_id = base64.urlsafe_b64decode(request.credential_id + '==')
    public_key = base64.urlsafe_b64decode(request.public_key + '==')

    # Save credential to PostgreSQL
    await store.save_credential(
        credential_id=credential_id,
        lambda_id=request.lambda_id,
        public_key=public_key,
        sign_count=0,
        device_name=request.device_name or "Unknown Device",
    )

    # Activate user
    result = await db.execute(
        select(User).where(User.lambda_id == request.lambda_id)
    )
    user = result.scalar_one_or_none()

    if user:
        user.is_active = True
        await db.commit()

    return {
        "lambda_id": request.lambda_id,
        "registered": True,
    }

# ============================================================================
# Authentication Flow
# ============================================================================

class AuthenticationStartRequest(BaseModel):
    email: EmailStr

class AuthenticationStartResponse(BaseModel):
    challenge: str
    allowCredentials: List[dict]

@router.post("/authenticate/start", response_model=AuthenticationStartResponse)
async def start_authentication(
    request: AuthenticationStartRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Step 1: Start passkey authentication

    Returns WebAuthn challenge and list of registered credentials
    """
    # Look up user by email
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(404, "User not found")

    # Get user's registered credentials
    credentials = await store.get_credentials_by_lambda_id(user.lambda_id)

    # Generate challenge
    challenge = secrets.token_bytes(32)
    challenge_b64 = base64.urlsafe_b64encode(challenge).decode().rstrip('=')

    # Store challenge in Redis (60s TTL)
    await redis_client.setex(
        f"webauthn:auth_challenge:{request.email}",
        60,
        challenge_b64,
    )

    # Format credentials for WebAuthn API
    allow_credentials = [
        {
            "id": base64.urlsafe_b64encode(cred["credential_id"]).decode().rstrip('='),
            "type": "public-key",
        }
        for cred in credentials
    ]

    return {
        "challenge": challenge_b64,
        "allowCredentials": allow_credentials,
    }

class AuthenticationCompleteRequest(BaseModel):
    email: EmailStr
    credential_id: str
    authenticator_data: str
    client_data_json: str
    signature: str

@router.post("/authenticate/complete")
async def complete_authentication(
    request: AuthenticationCompleteRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Step 2: Complete passkey authentication

    Verifies assertion and returns JWT session token
    """
    # Verify challenge exists
    stored_challenge = await redis_client.get(f"webauthn:auth_challenge:{request.email}")
    if not stored_challenge:
        raise HTTPException(400, "Challenge expired or invalid")

    # Delete challenge (one-time use)
    await redis_client.delete(f"webauthn:auth_challenge:{request.email}")

    # Decode credential ID
    credential_id = base64.urlsafe_b64decode(request.credential_id + '==')

    # Get credential from database
    credential_data = await store.get_credential(credential_id)
    if not credential_data:
        raise HTTPException(404, "Credential not found")

    # Verify assertion using lukhas.identity
    try:
        assertion_response = {
            "authenticator_data": request.authenticator_data,
            "client_data_json": request.client_data_json,
            "signature": request.signature,
            "origin": "https://lukhas.team",
        }

        result = verify_assertion(
            credential_id=credential_id,
            assertion_response=assertion_response,
            expected_origin="https://lukhas.team",
            expected_rp_id="lukhas.team",
            public_key=credential_data["public_key"],
            current_sign_count=credential_data["sign_count"],
        )

        if not result["verified"]:
            raise HTTPException(401, "Authentication failed")

    except Exception as e:
        raise HTTPException(401, f"Verification failed: {str(e)}")

    # Update sign count
    await store.update_sign_count(credential_id, result["sign_count"])

    # Get user
    result_user = await db.execute(
        select(User).where(User.lambda_id == credential_data["lambda_id"])
    )
    user = result_user.scalar_one_or_none()

    if not user:
        raise HTTPException(404, "User not found")

    # Update last login
    user.last_login = datetime.now()
    await db.commit()

    # Create JWT token
    token = create_jwt_token(lambda_id=user.lambda_id, email=user.email)

    # Store session in Redis (30 days)
    await redis_client.setex(
        f"session:{user.lambda_id}",
        30 * 24 * 60 * 60,  # 30 days
        token,
    )

    return {
        "lambda_id": user.lambda_id,
        "email": user.email,
        "display_name": user.display_name,
        "token": token,
    }

# ============================================================================
# Session Management
# ============================================================================

@router.get("/session")
async def get_session(token: str):
    """Verify session token and return user info"""
    # Decode JWT
    payload = decode_jwt_token(token)
    lambda_id = payload.get("lambda_id")

    # Check if session exists in Redis
    stored_token = await redis_client.get(f"session:{lambda_id}")
    if not stored_token or stored_token != token:
        raise HTTPException(401, "Invalid or expired session")

    # Return user info
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.lambda_id == lambda_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(404, "User not found")

        return {
            "lambda_id": user.lambda_id,
            "email": user.email,
            "display_name": user.display_name,
        }

@router.post("/logout")
async def logout(token: str):
    """Invalidate session token"""
    payload = decode_jwt_token(token)
    lambda_id = payload.get("lambda_id")

    # Delete session from Redis
    await redis_client.delete(f"session:{lambda_id}")

    return {"logged_out": True}
```

---

## Frontend Implementation

### next-auth Configuration

**File**: `lib/auth.ts`

```typescript
import NextAuth from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';
import { startAuthentication, startRegistration } from '@simplewebauthn/browser';

const LUKHAS_API = process.env.NEXT_PUBLIC_LUKHAS_API || 'http://localhost:8000';

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    CredentialsProvider({
      id: 'lambda-id',
      name: 'ΛiD Passkey',
      credentials: {
        email: { label: 'Email', type: 'email' },
        mode: { label: 'Mode', type: 'hidden' }, // 'login' or 'register'
      },

      async authorize(credentials) {
        const email = credentials?.email as string;
        const mode = credentials?.mode as 'login' | 'register';

        if (mode === 'register') {
          return await handleRegistration(email);
        } else {
          return await handleAuthentication(email);
        }
      },
    }),
  ],

  session: {
    strategy: 'jwt',
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },

  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.lambda_id = user.id;
        token.email = user.email;
        token.display_name = user.name;
      }
      return token;
    },

    async session({ session, token }) {
      if (session.user) {
        session.user.lambda_id = token.lambda_id as string;
        session.user.email = token.email as string;
        session.user.name = token.display_name as string;
      }
      return session;
    },
  },

  pages: {
    signIn: '/login',
    error: '/auth/error',
  },
});

// Helper: Registration flow
async function handleRegistration(email: string) {
  try {
    // Step 1: Start registration
    const startResponse = await fetch(`${LUKHAS_API}/api/auth/register/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email,
        display_name: email.split('@')[0], // Default display name
      }),
    });

    if (!startResponse.ok) {
      throw new Error('Registration start failed');
    }

    const { challenge, lambda_id, rp_id, rp_name } = await startResponse.json();

    // Step 2: Browser WebAuthn API (create credential)
    const credential = await startRegistration({
      rp: { id: rp_id, name: rp_name },
      user: {
        id: lambda_id,
        name: email,
        displayName: email.split('@')[0],
      },
      challenge,
      pubKeyCredParams: [{ alg: -7, type: 'public-key' }], // ES256
      authenticatorSelection: {
        authenticatorAttachment: 'platform', // Prefer Touch ID/Face ID
        userVerification: 'required',
        residentKey: 'preferred',
      },
    });

    // Step 3: Complete registration
    const completeResponse = await fetch(`${LUKHAS_API}/api/auth/register/complete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        lambda_id,
        credential_id: credential.id,
        public_key: credential.response.publicKey,
        device_name: navigator.userAgent.includes('Mac') ? 'MacBook' : 'Device',
      }),
    });

    if (!completeResponse.ok) {
      throw new Error('Registration failed');
    }

    const { lambda_id: user_id } = await completeResponse.json();

    return {
      id: user_id,
      email,
      name: email.split('@')[0],
    };
  } catch (error) {
    console.error('Registration error:', error);
    return null;
  }
}

// Helper: Authentication flow
async function handleAuthentication(email: string) {
  try {
    // Step 1: Start authentication
    const startResponse = await fetch(`${LUKHAS_API}/api/auth/authenticate/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    });

    if (!startResponse.ok) {
      throw new Error('Authentication start failed');
    }

    const { challenge, allowCredentials } = await startResponse.json();

    // Step 2: Browser WebAuthn API (get assertion)
    const assertion = await startAuthentication({
      challenge,
      allowCredentials,
      userVerification: 'required',
    });

    // Step 3: Complete authentication
    const completeResponse = await fetch(`${LUKHAS_API}/api/auth/authenticate/complete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email,
        credential_id: assertion.id,
        authenticator_data: assertion.response.authenticatorData,
        client_data_json: assertion.response.clientDataJSON,
        signature: assertion.response.signature,
      }),
    });

    if (!completeResponse.ok) {
      throw new Error('Authentication failed');
    }

    const { lambda_id, email: user_email, display_name } = await completeResponse.json();

    return {
      id: lambda_id,
      email: user_email,
      name: display_name,
    };
  } catch (error) {
    console.error('Authentication error:', error);
    return null;
  }
}
```

### Login Page

**File**: `app/(auth)/login/page.tsx`

```typescript
'use client';

import { signIn } from 'next-auth/react';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState<'login' | 'register'>('login');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const result = await signIn('lambda-id', {
        email,
        mode,
        redirect: true,
        callbackUrl: '/',
      });

      if (result?.error) {
        console.error('Sign in failed:', result.error);
        // Show error toast
      }
    } catch (error) {
      console.error('WebAuthn error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="w-full max-w-md space-y-8 p-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold">λ</h1>
          <h2 className="mt-2 text-2xl font-semibold">lukhas.team</h2>
          <p className="mt-2 text-muted-foreground">
            Passwordless authentication with ΛiD
          </p>
        </div>

        <Tabs value={mode} onValueChange={(v) => setMode(v as 'login' | 'register')}>
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="login">Sign In</TabsTrigger>
            <TabsTrigger value="register">Register</TabsTrigger>
          </TabsList>

          <TabsContent value="login" className="space-y-4">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Input
                  type="email"
                  placeholder="email@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              <Button type="submit" disabled={loading || !email} className="w-full">
                {loading ? 'Authenticating...' : 'Sign in with Passkey'}
              </Button>
            </form>
            <p className="text-sm text-muted-foreground text-center">
              Use Touch ID, Face ID, or your security key
            </p>
          </TabsContent>

          <TabsContent value="register" className="space-y-4">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Input
                  type="email"
                  placeholder="email@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              <Button type="submit" disabled={loading || !email} className="w-full">
                {loading ? 'Creating Passkey...' : 'Create Account with Passkey'}
              </Button>
            </form>
            <p className="text-sm text-muted-foreground text-center">
              Your passkey will be securely stored on this device
            </p>
          </TabsContent>
        </Tabs>

        <div className="pt-4 border-t">
          <p className="text-xs text-muted-foreground text-center">
            Powered by FIDO2 WebAuthn • No passwords, ever
          </p>
        </div>
      </div>
    </div>
  );
}
```

---

## Security Considerations

### 1. Challenge Generation

**CRITICAL**: Challenges MUST be cryptographically random and unpredictable.

```python
import secrets

# ✅ CORRECT: Use secrets module
challenge = secrets.token_bytes(32)  # 256 bits of randomness

# ❌ WRONG: Never use random module for security
import random
challenge = random.randbytes(32)  # Predictable!
```

### 2. Origin Validation

**CRITICAL**: Always verify the origin matches expected value.

```python
def verify_assertion(...):
    # Parse client data JSON
    client_data = json.loads(base64.urlsafe_b64decode(client_data_json))

    # Verify origin
    if client_data["origin"] != expected_origin:
        raise ValueError(f"Invalid origin: {client_data['origin']}")

    # Verify RP ID
    if rp_id_hash != hashlib.sha256(expected_rp_id.encode()).digest():
        raise ValueError("Invalid RP ID")
```

### 3. Sign Count Verification (Replay Attack Prevention)

**CRITICAL**: Sign count MUST increment. Decreasing/static count = replay attack.

```python
async def verify_and_update_sign_count(credential_id, new_sign_count):
    credential = await store.get_credential(credential_id)

    # Check for replay attack
    if new_sign_count <= credential["sign_count"]:
        # CRITICAL: Log this incident
        logger.critical(
            f"Replay attack detected! Credential {credential_id} "
            f"sign_count {new_sign_count} <= {credential['sign_count']}"
        )
        raise SecurityError("Sign count did not increment - possible replay attack")

    # Update sign count
    await store.update_sign_count(credential_id, new_sign_count)
```

### 4. Rate Limiting

**Prevent brute force attacks on authentication**:

```python
from fastapi import Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/authenticate/start")
@limiter.limit("5/minute")  # Max 5 attempts per minute per IP
async def start_authentication(request: Request, ...):
    ...
```

### 5. HTTPS Only

**CRITICAL**: WebAuthn ONLY works over HTTPS (except localhost).

```python
# In production, enforce HTTPS
if request.url.scheme != "https" and not request.url.hostname == "localhost":
    raise HTTPException(400, "WebAuthn requires HTTPS")
```

---

## Testing Strategy

### 1. Unit Tests

**File**: `tests/unit/test_webauthn_flow.py`

```python
import pytest
from unittest.mock import AsyncMock, patch
from serve.lukhas_team.auth_routes import start_registration, complete_registration

@pytest.mark.asyncio
async def test_registration_start_new_user():
    """Test registration start creates new user"""
    mock_db = AsyncMock()

    request = {"email": "test@example.com", "display_name": "Test User"}
    response = await start_registration(request, db=mock_db)

    assert "challenge" in response
    assert "lambda_id" in response
    assert response["rp_id"] == "lukhas.team"

@pytest.mark.asyncio
async def test_registration_start_existing_email():
    """Test registration fails for existing email"""
    mock_db = AsyncMock()
    # Mock existing user
    mock_db.execute.return_value.scalar_one_or_none.return_value = User(email="test@example.com")

    with pytest.raises(HTTPException) as exc:
        await start_registration({"email": "test@example.com"}, db=mock_db)

    assert exc.value.status_code == 400
    assert "already registered" in str(exc.value.detail)

@pytest.mark.asyncio
async def test_authentication_invalid_sign_count():
    """Test replay attack detection"""
    # Mock credential with sign_count = 10
    mock_credential = {"sign_count": 10, ...}

    # Attempt authentication with sign_count = 5 (replay!)
    with pytest.raises(SecurityError) as exc:
        await verify_and_update_sign_count(credential_id, new_sign_count=5)

    assert "replay attack" in str(exc.value)
```

### 2. Integration Tests

**File**: `tests/integration/test_webauthn_e2e.py`

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_full_registration_flow(client: AsyncClient):
    """Test complete registration flow"""

    # Step 1: Start registration
    response = await client.post("/api/auth/register/start", json={
        "email": "newuser@example.com",
        "display_name": "New User",
    })
    assert response.status_code == 200
    data = response.json()
    assert "challenge" in data
    assert "lambda_id" in data

    # Step 2: Complete registration (mock WebAuthn response)
    mock_credential = {
        "lambda_id": data["lambda_id"],
        "credential_id": "mock_credential_id_base64",
        "public_key": "mock_public_key_base64",
        "device_name": "Test Device",
    }

    response = await client.post("/api/auth/register/complete", json=mock_credential)
    assert response.status_code == 200
    assert response.json()["registered"] is True

@pytest.mark.asyncio
async def test_full_authentication_flow(client: AsyncClient, registered_user):
    """Test complete authentication flow"""

    # Step 1: Start authentication
    response = await client.post("/api/auth/authenticate/start", json={
        "email": registered_user.email,
    })
    assert response.status_code == 200
    data = response.json()
    assert "challenge" in data
    assert len(data["allowCredentials"]) > 0

    # Step 2: Complete authentication (mock assertion)
    mock_assertion = {
        "email": registered_user.email,
        "credential_id": "mock_credential_id",
        "authenticator_data": "mock_auth_data",
        "client_data_json": "mock_client_data",
        "signature": "mock_signature",
    }

    response = await client.post("/api/auth/authenticate/complete", json=mock_assertion)
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["lambda_id"] == registered_user.lambda_id
```

---

## Deployment Guide

### Environment Variables

```bash
# .env.production

# Database
DATABASE_URL=postgresql+asyncpg://lukhas:password@db.supabase.co:5432/lukhas_team

# Redis
REDIS_URL=redis://default:password@redis.upstash.io:6379

# JWT Secret
JWT_SECRET=your-256-bit-secret-key-here

# ΛiD Configuration
LAMBDA_ID_RP_ID=lukhas.team
LAMBDA_ID_RP_NAME="LUKHAS AI"
LAMBDA_ID_EXPECTED_ORIGIN=https://lukhas.team

# next-auth
NEXTAUTH_URL=https://lukhas.team
NEXTAUTH_SECRET=your-nextauth-secret-here
```

### Production Checklist

- [ ] PostgreSQL database migrated (`alembic upgrade head`)
- [ ] HTTPS enforced (WebAuthn requirement)
- [ ] CORS configured for lukhas.team only
- [ ] Rate limiting enabled (5 attempts/min)
- [ ] Redis sessions configured (30-day TTL)
- [ ] JWT secret is 256-bit random key
- [ ] Sign count validation enabled
- [ ] Origin validation hardcoded to `https://lukhas.team`
- [ ] Logging/monitoring for replay attacks
- [ ] Backup strategy for PostgreSQL credentials table

---

**Document Version**: 1.0
**Last Updated**: 2025-11-10
**Status**: Integration Guide Complete
**Next Document**: [ICON_DESIGN_SPECIFICATION.md](ICON_DESIGN_SPECIFICATION.md)
