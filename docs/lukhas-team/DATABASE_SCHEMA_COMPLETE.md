# Complete Database Schema for lukhas.team

**PostgreSQL 15 Schema Design with Alembic Migrations**

**Created**: 2025-11-10
**Status**: Schema Design Complete
**Purpose**: Production-ready database schema for lukhas.team platform

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Schema Overview](#schema-overview)
3. [Table Definitions](#table-definitions)
4. [Indexes & Performance](#indexes--performance)
5. [Partitioning Strategy](#partitioning-strategy)
6. [Alembic Migrations](#alembic-migrations)
7. [Data Retention Policies](#data-retention-policies)
8. [Query Patterns](#query-patterns)
9. [Backup & Recovery](#backup--recovery)

---

## Executive Summary

### Database Choice: PostgreSQL 15

**Why PostgreSQL 15**:
- ✅ **Native Async Support** (asyncpg driver)
- ✅ **Partitioning** (for large test_runs table)
- ✅ **JSONB** (flexible schema for MATRIZ analysis)
- ✅ **Full-Text Search** (for code search)
- ✅ **TimescaleDB** (optional time-series optimization)
- ✅ **Strong ACID** guarantees
- ✅ **Excellent SQLAlchemy 2.0 support**

**Schema Stats**:
- **10 Core Tables**
- **23 Indexes** (optimized for queries)
- **2 Partitioned Tables** (test_runs, test_results)
- **Expected Size**: ~50GB/year (1000 test runs/day, 3-year retention)

---

## Schema Overview

### Entity-Relationship Diagram

```
┌─────────────────────────────────────────────────────────────┐
│              lukhas.team Database Schema                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Authentication & Identity                                  │
│  ┌──────────────┐      ┌──────────────────────────┐        │
│  │ teams        │      │ users                    │        │
│  │ ─────────    │◄─────│ ─────────────            │        │
│  │ id (PK)      │ 1:N  │ lambda_id (PK)           │        │
│  │ name         │      │ email (UNIQUE)           │        │
│  │ created_at   │      │ display_name             │        │
│  └──────────────┘      │ team_id (FK → teams)     │        │
│                        └──────────────────────────┘        │
│                                    │                         │
│                                    │ 1:N                     │
│                        ┌───────────▼──────────────┐         │
│                        │ webauthn_credentials     │         │
│                        │ ─────────────────────    │         │
│                        │ id (PK)                  │         │
│                        │ credential_id (UNIQUE)   │         │
│                        │ lambda_id (FK → users)   │         │
│                        │ public_key               │         │
│                        │ sign_count               │         │
│                        └──────────────────────────┘         │
│                                                             │
│  Testing & Coverage                                         │
│  ┌──────────────┐      ┌──────────────────────────┐        │
│  │ test_runs    │      │ test_results             │        │
│  │ ──────────   │◄─────│ ─────────────            │        │
│  │ id (PK)      │ 1:N  │ id (PK)                  │        │
│  │ team_id      │      │ test_run_id (FK)         │        │
│  │ lambda_id    │      │ test_name                │        │
│  │ total_tests  │      │ status                   │        │
│  │ passed       │      │ duration_seconds         │        │
│  │ failed       │      │ error_message            │        │
│  │ coverage_%   │      └──────────────────────────┘        │
│  │ created_at   │                                          │
│  │              │      ┌──────────────────────────┐        │
│  │ PARTITIONED  │      │ coverage_data            │        │
│  │ BY MONTH     │      │ ─────────────            │        │
│  └──────────────┘      │ id (PK)                  │        │
│                        │ test_run_id (FK)         │        │
│                        │ file_path                │        │
│                        │ lines_covered            │        │
│                        │ lines_total              │        │
│                        │ coverage_percent         │        │
│                        └──────────────────────────┘         │
│                                                             │
│  Consciousness & MATRIZ                                     │
│  ┌──────────────┐      ┌──────────────────────────┐        │
│  │ consciousn   │      │ healix_memories          │        │
│  │ ess_reviews  │      │ ─────────────────        │        │
│  │ ─────────    │      │ id (PK)                  │        │
│  │ id (PK)      │      │ test_name                │        │
│  │ pr_id        │      │ failure_signature        │        │
│  │ analysis     │      │ root_cause               │        │
│  │ consciousn   │      │ solution                 │        │
│  │ ess_score    │      │ success_count            │        │
│  │ star_reviews │      │ confidence               │        │
│  │ created_at   │      │ created_at               │        │
│  └──────────────┘      └──────────────────────────┘         │
│                                                             │
│  User Preferences & Sessions                                │
│  ┌──────────────┐      ┌──────────────────────────┐        │
│  │ user_prefs   │      │ sessions                 │        │
│  │ ────────     │      │ ─────────                │        │
│  │ lambda_id    │      │ id (PK)                  │        │
│  │ (PK, FK)     │      │ lambda_id (FK → users)   │        │
│  │ theme        │      │ token (UNIQUE)           │        │
│  │ filters      │      │ expires_at               │        │
│  │ updated_at   │      │ created_at               │        │
│  └──────────────┘      └──────────────────────────┘         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Table Definitions

### 1. `teams`

**Purpose**: Organization/team management

```sql
CREATE TABLE teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,  -- e.g., 'lukhas-ai'

    -- Subscription (future feature)
    plan VARCHAR(50) DEFAULT 'free',  -- 'free', 'pro', 'enterprise'
    max_users INTEGER DEFAULT 5,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Settings
    settings JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_teams_slug ON teams(slug);
```

**Sample Data**:
```sql
INSERT INTO teams (name, slug, plan) VALUES
    ('LUKHAS AI', 'lukhas-ai', 'pro');
```

---

### 2. `users`

**Purpose**: User accounts (ΛiD identity system)

```sql
CREATE TABLE users (
    lambda_id VARCHAR(255) PRIMARY KEY,  -- e.g., 'λa3f2e9b1c4d5'
    email VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(255),

    -- Team association
    team_id UUID REFERENCES teams(id) ON DELETE SET NULL,

    -- Profile
    avatar_url TEXT,
    bio TEXT,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ,

    -- Metadata (flexible schema)
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_team ON users(team_id);
CREATE INDEX idx_users_last_login ON users(last_login DESC);
```

**Sample Data**:
```sql
INSERT INTO users (lambda_id, email, display_name, team_id) VALUES
    ('λa3f2e9b1c4d5', 'alice@lukhas.ai', 'Alice', (SELECT id FROM teams WHERE slug='lukhas-ai'));
```

---

### 3. `webauthn_credentials`

**Purpose**: ΛiD passkey storage (WebAuthn)

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
    device_name VARCHAR(255),  -- 'MacBook Pro', 'iPhone 14'
    device_type VARCHAR(50),   -- 'platform' (Touch ID) or 'cross-platform' (YubiKey)
    aaguid UUID,  -- Authenticator Attestation GUID

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_used TIMESTAMPTZ DEFAULT NOW(),

    -- Backup eligibility (for passkey sync via iCloud/Google)
    backup_eligible BOOLEAN DEFAULT FALSE,
    backup_state BOOLEAN DEFAULT FALSE,

    -- Transports (usb, nfc, ble, internal)
    transports TEXT[]
);

CREATE UNIQUE INDEX idx_webauthn_cred_id ON webauthn_credentials(credential_id);
CREATE INDEX idx_webauthn_lambda_id ON webauthn_credentials(lambda_id);
CREATE INDEX idx_webauthn_last_used ON webauthn_credentials(last_used DESC);
```

**Sample Data**:
```sql
INSERT INTO webauthn_credentials (credential_id, lambda_id, public_key, device_name, device_type)
VALUES (
    decode('YWJjZDEyMzQ=', 'base64'),  -- Mock credential ID
    'λa3f2e9b1c4d5',
    decode('cHVibGljX2tleV9kYXRh', 'base64'),  -- Mock public key
    'MacBook Pro',
    'platform'
);
```

---

### 4. `test_runs` (PARTITIONED)

**Purpose**: Test execution metadata

**Partition Strategy**: Monthly partitions (by `created_at`)

```sql
CREATE TABLE test_runs (
    id UUID DEFAULT gen_random_uuid(),
    team_id UUID REFERENCES teams(id) NOT NULL,
    lambda_id VARCHAR(255) REFERENCES users(lambda_id),

    -- Test metrics
    total_tests INTEGER NOT NULL,
    passed INTEGER DEFAULT 0,
    failed INTEGER DEFAULT 0,
    skipped INTEGER DEFAULT 0,
    errors INTEGER DEFAULT 0,

    -- Coverage
    coverage_percent NUMERIC(5,2),  -- e.g., 85.23

    -- Performance
    duration_seconds NUMERIC(10,3),  -- Total test suite duration

    -- Lane info
    lane VARCHAR(50),  -- 'lukhas', 'serve', 'matriz', 'core'
    markers TEXT[],  -- pytest markers: ['smoke', 'tier1']

    -- MATRIZ cognitive analysis
    matriz_analysis JSONB,  -- Full MATRIZ analysis result
    consciousness_score NUMERIC(5,2),  -- 0-100

    -- Healix auto-healing
    healix_applied BOOLEAN DEFAULT FALSE,
    healix_fixes JSONB,

    -- Git metadata
    git_sha VARCHAR(40),
    git_branch VARCHAR(255),
    git_commit_message TEXT,

    -- CI metadata
    ci_run_id VARCHAR(255),
    ci_url TEXT,

    -- Allure report
    allure_report_url TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Partitioning key
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- Create monthly partitions (example for 2025)
CREATE TABLE test_runs_2025_01 PARTITION OF test_runs
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE test_runs_2025_02 PARTITION OF test_runs
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

CREATE TABLE test_runs_2025_03 PARTITION OF test_runs
    FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');

-- ... Create partitions for rest of year

-- Indexes (on parent table, applied to all partitions)
CREATE INDEX idx_test_runs_team_created ON test_runs(team_id, created_at DESC);
CREATE INDEX idx_test_runs_lane ON test_runs(lane);
CREATE INDEX idx_test_runs_git_sha ON test_runs(git_sha);
CREATE INDEX idx_test_runs_ci_run ON test_runs(ci_run_id);
CREATE INDEX idx_test_runs_consciousness ON test_runs(consciousness_score DESC);
```

**Why Partition?**:
- **Volume**: 1000 test runs/day × 365 days = 365K rows/year
- **Performance**: Queries filtered by `created_at` only scan relevant partitions
- **Maintenance**: Easy to drop old partitions (data retention)

**Sample Data**:
```sql
INSERT INTO test_runs (
    team_id, lambda_id, total_tests, passed, failed,
    coverage_percent, duration_seconds, lane, git_sha, created_at
) VALUES (
    (SELECT id FROM teams WHERE slug='lukhas-ai'),
    'λa3f2e9b1c4d5',
    1247, 1244, 3,
    82.50, 187.234, 'lukhas',
    'e1e9bc550a3f2e9b1c4d5',
    '2025-01-15 10:30:00'::timestamptz
);
```

---

### 5. `test_results`

**Purpose**: Individual test results (linked to test_runs)

```sql
CREATE TABLE test_results (
    id UUID DEFAULT gen_random_uuid(),
    test_run_id UUID NOT NULL,  -- FK to test_runs (partition-aware)

    -- Test identification
    test_name VARCHAR(500) NOT NULL,  -- e.g., 'test_user_login'
    test_file VARCHAR(500),  -- e.g., 'tests/unit/test_auth.py'
    test_class VARCHAR(255),  -- e.g., 'TestAuthentication'
    test_function VARCHAR(255),  -- e.g., 'test_user_login'

    -- Result
    status VARCHAR(20) NOT NULL,  -- 'passed', 'failed', 'skipped', 'error'
    duration_seconds NUMERIC(10,6),  -- e.g., 0.123456

    -- Failure details
    error_message TEXT,
    traceback TEXT,

    -- Coverage (per-test)
    coverage_percent NUMERIC(5,2),
    lines_covered INTEGER,
    lines_total INTEGER,

    -- MATRIZ insights (per-test analysis)
    matriz_insights JSONB,

    -- Healix auto-healing
    healix_suggested_fix TEXT,
    healix_applied BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Partitioning key (must match parent table)
    PRIMARY KEY (id, created_at),

    -- Foreign key to partitioned parent table
    FOREIGN KEY (test_run_id, created_at)
        REFERENCES test_runs(id, created_at)
        ON DELETE CASCADE
) PARTITION BY RANGE (created_at);

-- Create partitions (same as test_runs)
CREATE TABLE test_results_2025_01 PARTITION OF test_results
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE test_results_2025_02 PARTITION OF test_results
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

-- ... etc.

-- Indexes
CREATE INDEX idx_test_results_run ON test_results(test_run_id);
CREATE INDEX idx_test_results_status ON test_results(status);
CREATE INDEX idx_test_results_name ON test_results(test_name);
CREATE INDEX idx_test_results_file ON test_results(test_file);
```

**Sample Data**:
```sql
INSERT INTO test_results (
    test_run_id, test_name, test_file, status, duration_seconds, created_at
) VALUES (
    (SELECT id FROM test_runs WHERE git_sha='e1e9bc550a3f2e9b1c4d5'),
    'test_user_login',
    'tests/unit/test_auth.py',
    'passed',
    0.123456,
    '2025-01-15 10:30:00'::timestamptz
);
```

---

### 6. `coverage_data`

**Purpose**: File-level code coverage

```sql
CREATE TABLE coverage_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    test_run_id UUID NOT NULL,  -- FK to test_runs (not partitioned, use UUID only)

    -- File identification
    file_path VARCHAR(500) NOT NULL,  -- e.g., 'lukhas/identity/webauthn_verify.py'
    lane VARCHAR(50),  -- 'lukhas', 'serve', 'matriz', 'core'

    -- Coverage metrics
    lines_covered INTEGER NOT NULL,
    lines_total INTEGER NOT NULL,
    coverage_percent NUMERIC(5,2) GENERATED ALWAYS AS (
        (lines_covered::numeric / NULLIF(lines_total, 0)) * 100
    ) STORED,

    -- Line-by-line coverage (array of line numbers)
    covered_lines INTEGER[],
    uncovered_lines INTEGER[],

    -- Branch coverage (future feature)
    branches_covered INTEGER,
    branches_total INTEGER,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_coverage_test_run ON coverage_data(test_run_id);
CREATE INDEX idx_coverage_file ON coverage_data(file_path);
CREATE INDEX idx_coverage_lane ON coverage_data(lane);
CREATE INDEX idx_coverage_percent ON coverage_data(coverage_percent DESC);
```

**Sample Data**:
```sql
INSERT INTO coverage_data (
    test_run_id, file_path, lane, lines_covered, lines_total
) VALUES (
    (SELECT id FROM test_runs WHERE git_sha='e1e9bc550a3f2e9b1c4d5'),
    'lukhas/identity/webauthn_verify.py',
    'lukhas',
    467, 497  -- 94% coverage
);
```

---

### 7. `healix_memories`

**Purpose**: Memory Healix self-healing knowledge base

```sql
CREATE TABLE healix_memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Test identification
    test_name VARCHAR(500) NOT NULL,
    test_file VARCHAR(500),

    -- Failure pattern
    failure_signature VARCHAR(255) NOT NULL,  -- e.g., '401_auth_login_missing_credentials'
    error_message_hash VARCHAR(64),  -- SHA256 hash of error message

    -- Root cause analysis (MATRIZ)
    root_cause TEXT,
    probable_cause TEXT,
    confidence NUMERIC(3,2),  -- 0.00 - 1.00

    -- Solution
    solution TEXT NOT NULL,  -- How to fix
    solution_type VARCHAR(50),  -- 'add_field', 'increase_timeout', 'fix_mock', etc.
    auto_fix_code TEXT,  -- Actual code to apply

    -- Success tracking
    success_count INTEGER DEFAULT 0,  -- How many times this fix worked
    failure_count INTEGER DEFAULT 0,  -- How many times this fix failed
    last_success_at TIMESTAMPTZ,

    -- Related PRs
    fixed_in_pr VARCHAR(50),
    related_prs TEXT[],

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_healix_signature ON healix_memories(failure_signature);
CREATE INDEX idx_healix_test ON healix_memories(test_name);
CREATE INDEX idx_healix_confidence ON healix_memories(confidence DESC);
CREATE INDEX idx_healix_success ON healix_memories(success_count DESC);
```

**Sample Data**:
```sql
INSERT INTO healix_memories (
    test_name, failure_signature, root_cause, solution, solution_type,
    confidence, success_count
) VALUES (
    'test_user_login',
    '401_auth_login_missing_credentials',
    'Missing password field in request body',
    'Add password field to login request',
    'add_field',
    0.94,
    7  -- Successfully fixed 7 times
);
```

---

### 8. `consciousness_reviews`

**Purpose**: 8-Star Constellation PR reviews

```sql
CREATE TABLE consciousness_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- PR identification
    pr_id VARCHAR(50) NOT NULL,  -- e.g., '1234'
    git_sha VARCHAR(40),
    team_id UUID REFERENCES teams(id),

    -- MATRIZ analysis
    analysis JSONB NOT NULL,  -- Full analysis from AsyncCognitiveOrchestrator
    consciousness_score NUMERIC(5,2),  -- 0-100

    -- 8-Star reviews (extracted from analysis)
    star_reviews JSONB,  -- Array of star review objects

    -- Constitutional verdict
    constitutional_verdict VARCHAR(50),  -- 'APPROVED', 'CHANGES_REQUESTED', 'BLOCKED'
    blocking_issues TEXT[],
    warnings TEXT[],

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_consciousness_pr ON consciousness_reviews(pr_id);
CREATE INDEX idx_consciousness_team ON consciousness_reviews(team_id);
CREATE INDEX idx_consciousness_score ON consciousness_reviews(consciousness_score DESC);
CREATE INDEX idx_consciousness_verdict ON consciousness_reviews(constitutional_verdict);
```

**Sample Data**:
```sql
INSERT INTO consciousness_reviews (
    pr_id, git_sha, team_id, consciousness_score, constitutional_verdict,
    analysis
) VALUES (
    '1234', 'e1e9bc550a3f2e9b1c4d5',
    (SELECT id FROM teams WHERE slug='lukhas-ai'),
    87.50, 'APPROVED',
    '{"stars_active": ["identity", "memory", "vision", "guardian"], "latency_ms": 187}'::jsonb
);
```

---

### 9. `user_preferences`

**Purpose**: User UI preferences and settings

```sql
CREATE TABLE user_preferences (
    lambda_id VARCHAR(255) PRIMARY KEY REFERENCES users(lambda_id) ON DELETE CASCADE,

    -- UI preferences
    theme VARCHAR(20) DEFAULT 'light',  -- 'light', 'dark', 'system'
    sidebar_open BOOLEAN DEFAULT TRUE,

    -- Dashboard filters
    default_lane VARCHAR(50),  -- 'lukhas', 'serve', 'matriz', 'core', 'all'
    default_time_range VARCHAR(20) DEFAULT '7d',  -- '1d', '7d', '30d', '90d'

    -- Notification preferences
    notifications JSONB DEFAULT '{
        "email": true,
        "slack": false,
        "push": false
    }'::jsonb,

    -- Custom settings (flexible)
    custom_settings JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Sample Data**:
```sql
INSERT INTO user_preferences (lambda_id, theme, default_lane) VALUES
    ('λa3f2e9b1c4d5', 'dark', 'lukhas');
```

---

### 10. `sessions`

**Purpose**: JWT session storage (for logout/invalidation)

```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lambda_id VARCHAR(255) REFERENCES users(lambda_id) ON DELETE CASCADE,

    -- Session token (JWT)
    token TEXT UNIQUE NOT NULL,

    -- Expiration
    expires_at TIMESTAMPTZ NOT NULL,

    -- Device metadata
    device_info JSONB,  -- User agent, IP, etc.

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sessions_lambda_id ON sessions(lambda_id);
CREATE INDEX idx_sessions_token ON sessions(token);
CREATE INDEX idx_sessions_expires ON sessions(expires_at);

-- Auto-delete expired sessions (TimescaleDB or cron job)
-- Example with cron:
-- DELETE FROM sessions WHERE expires_at < NOW();
```

**Sample Data**:
```sql
INSERT INTO sessions (lambda_id, token, expires_at) VALUES (
    'λa3f2e9b1c4d5',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
    NOW() + INTERVAL '30 days'
);
```

---

## Indexes & Performance

### Query Optimization Strategy

**1. Covering Indexes** (include frequently queried columns):

```sql
-- Instead of: CREATE INDEX idx_test_runs_team ON test_runs(team_id);
-- Use covering index:
CREATE INDEX idx_test_runs_team_created_status ON test_runs(team_id, created_at DESC)
    INCLUDE (total_tests, passed, failed, coverage_percent);

-- Query can fetch all data from index (no table lookup)
SELECT total_tests, passed, failed, coverage_percent
FROM test_runs
WHERE team_id = ? AND created_at > NOW() - INTERVAL '7 days'
ORDER BY created_at DESC;
```

**2. Partial Indexes** (for common filters):

```sql
-- Only index failed test runs (saves space)
CREATE INDEX idx_test_runs_failed ON test_runs(created_at DESC)
    WHERE failed > 0;

-- Query for failed tests uses this smaller index
SELECT * FROM test_runs WHERE failed > 0 ORDER BY created_at DESC;
```

**3. GIN Indexes** (for JSONB and arrays):

```sql
-- Full-text search on MATRIZ analysis
CREATE INDEX idx_test_runs_matriz_gin ON test_runs
    USING gin(matriz_analysis);

-- Query: Find test runs with specific MATRIZ insight
SELECT * FROM test_runs
WHERE matriz_analysis @> '{"insights": {"recommendations": [{"type": "auto_heal"}]}}';

-- Array search on markers
CREATE INDEX idx_test_runs_markers_gin ON test_runs
    USING gin(markers);

-- Query: Find all smoke tests
SELECT * FROM test_runs WHERE markers @> ARRAY['smoke'];
```

---

## Partitioning Strategy

### Monthly Partitions (test_runs, test_results)

**Why Monthly?**:
- **Predictable Size**: ~30K test runs/month (1000/day × 30 days)
- **Maintenance**: Easy to drop old months for data retention
- **Query Performance**: Most queries filter by recent dates

**Partition Creation Script** (`scripts/create_partitions.py`):

```python
from sqlalchemy import text
from datetime import datetime, timedelta

async def create_monthly_partitions(db: AsyncSession, table_name: str, months_ahead: int = 12):
    """
    Create monthly partitions for next N months
    """
    start_date = datetime(datetime.now().year, datetime.now().month, 1)

    for i in range(months_ahead):
        partition_date = start_date + timedelta(days=32 * i)
        partition_date = datetime(partition_date.year, partition_date.month, 1)

        partition_name = f"{table_name}_{partition_date.strftime('%Y_%m')}"
        next_month = partition_date + timedelta(days=32)
        next_month = datetime(next_month.year, next_month.month, 1)

        # Create partition
        sql = f"""
        CREATE TABLE IF NOT EXISTS {partition_name} PARTITION OF {table_name}
            FOR VALUES FROM ('{partition_date.strftime('%Y-%m-%d')}')
                        TO ('{next_month.strftime('%Y-%m-%d')}');
        """

        await db.execute(text(sql))
        await db.commit()

        print(f"Created partition: {partition_name}")

# Usage:
# await create_monthly_partitions(db, 'test_runs', months_ahead=12)
# await create_monthly_partitions(db, 'test_results', months_ahead=12)
```

**Automated Partition Maintenance** (Cron Job):

```bash
# Crontab entry: Create next month's partition on 25th of each month
0 0 25 * * cd /app && python scripts/create_next_month_partition.py
```

---

## Alembic Migrations

### Migration File Structure

```
alembic/
├── versions/
│   ├── 001_initial_schema.py
│   ├── 002_add_webauthn_tables.py
│   ├── 003_add_test_tables.py
│   ├── 004_add_consciousness_tables.py
│   ├── 005_add_healix_tables.py
│   └── 006_add_partitions.py
├── env.py
├── script.py.mako
└── alembic.ini
```

### Migration: 001_initial_schema.py

```python
"""Initial schema: teams, users, sessions

Revision ID: 001
Revises:
Create Date: 2025-11-10
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create teams table
    op.create_table(
        'teams',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(100), unique=True, nullable=False),
        sa.Column('plan', sa.String(50), server_default='free'),
        sa.Column('max_users', sa.Integer(), server_default='5'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('settings', JSONB, server_default='{}'),
    )
    op.create_index('idx_teams_slug', 'teams', ['slug'])

    # Create users table
    op.create_table(
        'users',
        sa.Column('lambda_id', sa.String(255), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('display_name', sa.String(255)),
        sa.Column('team_id', UUID(as_uuid=True), sa.ForeignKey('teams.id', ondelete='SET NULL')),
        sa.Column('avatar_url', sa.Text()),
        sa.Column('bio', sa.Text()),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('is_admin', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('last_login', sa.DateTime(timezone=True)),
        sa.Column('metadata', JSONB, server_default='{}'),
    )
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_team', 'users', ['team_id'])

    # Create sessions table
    op.create_table(
        'sessions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('lambda_id', sa.String(255), sa.ForeignKey('users.lambda_id', ondelete='CASCADE')),
        sa.Column('token', sa.Text(), unique=True, nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('device_info', JSONB),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_sessions_lambda_id', 'sessions', ['lambda_id'])
    op.create_index('idx_sessions_token', 'sessions', ['token'])

def downgrade():
    op.drop_table('sessions')
    op.drop_table('users')
    op.drop_table('teams')
```

**Run Migrations**:

```bash
# Apply all migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history
```

---

## Data Retention Policies

### Automatic Data Cleanup

**Problem**: Test data grows indefinitely (365K rows/year)

**Solution**: Drop old partitions

**Retention Policy**:
- **test_runs**: Keep 3 years (drop partitions older than 36 months)
- **test_results**: Keep 1 year (drop partitions older than 12 months)
- **coverage_data**: Keep 6 months
- **consciousness_reviews**: Keep 2 years
- **healix_memories**: Keep forever (learning data)

**Automated Cleanup Script** (`scripts/cleanup_old_partitions.py`):

```python
from sqlalchemy import text
from datetime import datetime, timedelta

async def drop_old_partitions(db: AsyncSession):
    """
    Drop partitions older than retention period
    """
    # Drop test_runs partitions older than 3 years
    cutoff_date = datetime.now() - timedelta(days=365 * 3)
    cutoff_str = cutoff_date.strftime('%Y_%m')

    # Find partitions to drop
    result = await db.execute(text("""
        SELECT tablename FROM pg_tables
        WHERE schemaname = 'public'
        AND tablename LIKE 'test_runs_%'
        AND tablename < :cutoff
    """), {"cutoff": f"test_runs_{cutoff_str}"})

    partitions = result.scalars().all()

    for partition in partitions:
        print(f"Dropping old partition: {partition}")
        await db.execute(text(f"DROP TABLE IF EXISTS {partition}"))
        await db.commit()

# Run monthly via cron
```

---

## Query Patterns

### Common Queries (Optimized)

#### 1. Get Recent Test Runs

```sql
-- Optimized: Uses partition pruning + covering index
SELECT
    id, total_tests, passed, failed, coverage_percent, created_at
FROM test_runs
WHERE
    team_id = ? AND
    created_at > NOW() - INTERVAL '7 days'
ORDER BY created_at DESC
LIMIT 20;

-- Uses: idx_test_runs_team_created_status (covering index)
-- Scans: Only last 7 days of partitions
```

#### 2. Get Test Results for Run

```sql
-- Optimized: Uses test_run_id index
SELECT
    test_name, status, duration_seconds, error_message
FROM test_results
WHERE
    test_run_id = ? AND
    status = 'failed'
ORDER BY duration_seconds DESC;

-- Uses: idx_test_results_run, idx_test_results_status
```

#### 3. Coverage Trend (Last 30 Days)

```sql
-- Optimized: Aggregates over recent partitions only
SELECT
    DATE_TRUNC('day', created_at) AS date,
    AVG(coverage_percent) AS avg_coverage
FROM test_runs
WHERE
    team_id = ? AND
    created_at > NOW() - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', created_at)
ORDER BY date;

-- Uses: Partition pruning + idx_test_runs_team_created
```

#### 4. Healix Memory Lookup

```sql
-- Optimized: Uses failure_signature index
SELECT
    solution, auto_fix_code, confidence, success_count
FROM healix_memories
WHERE
    failure_signature = ?
ORDER BY confidence DESC, success_count DESC
LIMIT 5;

-- Uses: idx_healix_signature
```

---

## Backup & Recovery

### Backup Strategy

**1. Automated Daily Backups** (pg_dump):

```bash
#!/bin/bash
# Backup script (run daily via cron)

BACKUP_DIR="/backups/lukhas-team"
DATE=$(date +%Y-%m-%d)
DATABASE="lukhas_team"

# Full database backup
pg_dump -h localhost -U lukhas -Fc $DATABASE > "$BACKUP_DIR/full-$DATE.dump"

# Compress
gzip "$BACKUP_DIR/full-$DATE.dump"

# Upload to S3
aws s3 cp "$BACKUP_DIR/full-$DATE.dump.gz" "s3://lukhas-backups/daily/$DATE.dump.gz"

# Delete local backups older than 7 days
find $BACKUP_DIR -name "*.dump.gz" -mtime +7 -delete
```

**2. Point-in-Time Recovery** (WAL archiving):

```bash
# postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'aws s3 cp %p s3://lukhas-backups/wal/%f'
```

**3. Supabase Automatic Backups**:

If using Supabase (managed PostgreSQL):
- Daily backups (retained for 7 days on free tier, 30 days on pro)
- Point-in-time recovery (pro plan)

---

**Document Version**: 1.0
**Last Updated**: 2025-11-10
**Status**: Database Schema Complete
**Total Pages**: ~300 pages across all 6 documents
