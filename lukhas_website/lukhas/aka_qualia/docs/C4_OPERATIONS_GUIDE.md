---
status: wip
type: documentation
---
# Wave C C4 Memory Operations Guide

## Overview

Wave C C4 provides production-grade memory persistence for the Aka Qualia phenomenological processing pipeline. This guide covers operational tasks for the memory system including database management, GDPR compliance, and troubleshooting.

## Architecture Summary

```
AkaQualia Pipeline
├── PhenomenalScene → GLYPH Mapping → PhenomenalGlyphs
├── Router Priority → Symbolic Signals → Router Dispatch  
├── Memory Persistence → SqlMemory/NoopMemory
└── Oneiric Feedback → Dream Generation
```

### Memory Clients
- **SqlMemory**: Production client with SQLite/PostgreSQL support
- **NoopMemory**: Development/testing client (no persistence)

### Database Schema
- `akaq_scene`: Phenomenological scenes with user context
- `akaq_glyph`: GLYPH mappings linked to scenes
- `akaq_memory_ops`: Audit trail for all memory operations

## CLI Tools

### Database Migration

Initialize or migrate the memory database:

```bash
cd candidate/aka_qualia/
python cli/migrate_memory_db.py --db-url sqlite:///akaq_memory.db --apply
```

Options:
- `--db-url`: Database connection URL
- `--apply`: Apply migrations (default: dry run)
- `--reset`: Drop all tables and recreate

### GDPR Article 17 Erasure

Remove all user data for compliance:

```bash
python cli/gdpr_erase_user.py --user-id user123 --db-url sqlite:///akaq_memory.db
```

Options:
- `--user-id`: User to erase (required)
- `--db-url`: Database connection URL
- `--dry-run`: Show what would be deleted without deleting

## Production Setup

### 1. Database Configuration

For SQLite (development/single instance):
```bash
export DATABASE_URL="sqlite:///data/akaq_memory.db"
```

For PostgreSQL (production):
```bash
export DATABASE_URL="postgresql://user:pass@localhost:5432/akaq_memory"
```

### 2. Initialize Database

```bash
python cli/migrate_memory_db.py --apply
```

### 3. Verify Installation

```bash
python test_simple.py
```

Expected output:
```
✅ NoopMemory working correctly
✅ Basic infrastructure validated
```

## Monitoring & Observability

### Key Metrics

Monitor these metrics in production:
- **Scene Storage Rate**: Scenes/second being persisted
- **Query Response Time**: p95 latency for scene retrieval
- **Memory Usage**: Database size and connection pool
- **GDPR Compliance**: User erasure audit trail

### Health Checks

Basic health check:
```python
from candidate.aka_qualia.memory import SqlMemory
memory = SqlMemory(engine=your_engine, rotate_salt="prod_salt", is_prod=True)
health = memory.health_check()
print(f"Memory System Status: {'✅ Healthy' if health else '❌ Unhealthy'}")
```

### Audit Trail

All memory operations are logged in `akaq_memory_ops`:
```sql
SELECT operation, user_id, timestamp, metadata 
FROM akaq_memory_ops 
ORDER BY timestamp DESC 
LIMIT 100;
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors
```
OperationalError: no such table: akaq_scene
```
**Solution**: Run database migration:
```bash
python cli/migrate_memory_db.py --apply
```

#### 2. Memory Client Configuration
```
AttributeError: 'NoopMemory' object has no attribute 'is_prod'
```
**Solution**: Ensure client initialization with proper parameters:
```python
memory = NoopMemory(is_prod=False)  # Development
memory = SqlMemory(engine=engine, rotate_salt="salt", is_prod=True)  # Production
```

#### 3. GDPR Erasure Verification
Check user data was completely removed:
```sql
SELECT COUNT(*) FROM akaq_scene WHERE user_id = 'target_user';
SELECT COUNT(*) FROM akaq_glyph WHERE scene_id IN (
    SELECT scene_id FROM akaq_scene WHERE user_id = 'target_user'
);
```
Both should return 0 after erasure.

### Performance Tuning

#### Database Indexes
Ensure indexes exist for common queries:
```sql
CREATE INDEX IF NOT EXISTS idx_akaq_scene_user_id ON akaq_scene(user_id);
CREATE INDEX IF NOT EXISTS idx_akaq_scene_created_at ON akaq_scene(created_at);
CREATE INDEX IF NOT EXISTS idx_akaq_glyph_scene_id ON akaq_glyph(scene_id);
```

#### Connection Pool Settings
For PostgreSQL in production:
```python
from sqlalchemy import create_engine
engine = create_engine(
    "postgresql://user:pass@localhost:5432/akaq_memory",
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=300
)
```

## Security Considerations

### PII Protection
Production mode automatically hashes user identifiers:
```python
memory = SqlMemory(engine=engine, rotate_salt="strong_salt", is_prod=True)
# user_id gets SHA3-256 hashed before database storage
```

### Audit Requirements
All memory operations create audit entries:
- Scene storage/retrieval
- User erasure operations
- System health checks
- Migration operations

### Access Control
Recommended database permissions:
- Application user: SELECT, INSERT, UPDATE, DELETE on akaq_* tables
- Migration user: All permissions for schema changes
- Monitoring user: SELECT only on akaq_memory_ops

## Testing

### Unit Tests
```bash
pytest candidate/aka_qualia/tests/test_memory_unit.py -v
```

### Integration Tests
```bash
pytest candidate/aka_qualia/tests/test_memory_integration.py -v
```

### Performance Tests
```bash
pytest candidate/aka_qualia/tests/test_memory_performance.py -v -m perf
```

### Security Tests
```bash
pytest candidate/aka_qualia/tests/test_memory_security.py -v -m security
```

### GDPR Compliance Tests
```bash
pytest candidate/aka_qualia/tests/test_memory_gdpr.py -v -m security
```

## Deployment Checklist

- [ ] Database URL configured
- [ ] Migration applied successfully
- [ ] Health check passes
- [ ] Audit trail enabled
- [ ] Monitoring configured
- [ ] GDPR procedures tested
- [ ] Backup/recovery verified
- [ ] Performance benchmarks meet SLA
- [ ] Security scan completed

## Support

For issues with Wave C memory system:
1. Check this operations guide
2. Review test suite in `candidate/aka_qualia/tests/`
3. Examine audit trail in `akaq_memory_ops` table
4. Run comprehensive test runner: `python run_c44_tests.py`

---

**Wave C C4 Memory System** - Production-grade phenomenological processing with GDPR compliance and comprehensive testing.