---
status: wip
type: documentation
---
# Wave C C4 Memory System

Production-grade memory persistence for the Aka Qualia phenomenological processing pipeline.

## Quick Start

```bash
# 1. Check system health
python3 cli/memory_health_check.py --memory-type noop --full

# 2. Initialize database (SQLite)
python3 cli/migrate_memory_db.py --db-url sqlite:///akaq_memory.db --apply

# 3. Verify database health
python3 cli/memory_health_check.py --db-url sqlite:///akaq_memory.db --full

# 4. Run comprehensive tests
python3 run_c44_tests.py
```

## Memory Clients

### SqlMemory (Production)
- **Database Support**: PostgreSQL, SQLite
- **GDPR Compliance**: Article 17 Right to Erasure
- **Privacy Protection**: User ID hashing in production mode
- **Features**: Vector similarity, audit trails, transaction safety

### NoopMemory (Development)
- **No Persistence**: All operations are no-ops
- **Testing**: Perfect for unit tests and lightweight deployments
- **Statistics**: Operation counting for monitoring

## CLI Tools

### 🗄️ Database Migration
```bash
python3 cli/migrate_memory_db.py --db-url <DATABASE_URL> [--apply] [--reset]
```

### 🛡️ GDPR User Erasure  
```bash
python3 cli/gdpr_erase_user.py --user-id <USER_ID> --db-url <DATABASE_URL> [--dry-run]
```

### 🏥 Health Monitoring
```bash
python3 cli/memory_health_check.py [--db-url <DATABASE_URL>] [--memory-type sql|noop] [--full]
```

## Architecture

```
Wave C C4 Memory System
├── memory.py              # AkaqMemory abstract interface
├── memory_sql.py          # SQL implementation with GDPR compliance
├── memory_noop.py         # No-op implementation for testing
├── cli/                   # Command-line management tools
├── tests/                 # Comprehensive 6-category test suite
└── docs/                  # Operations documentation
```

### Database Schema

- **akaq_scene**: Phenomenological scenes with user context
- **akaq_glyph**: GLYPH mappings linked to scenes  
- **akaq_memory_ops**: Audit trail for compliance
- **akaq_schema_metadata**: Migration version tracking

## Testing

The system includes comprehensive testing across 6 categories:

- **Unit Tests**: Core functionality and interface compliance
- **Integration Tests**: Database operations and SQL queries  
- **Security Tests**: SQL injection prevention and fault tolerance
- **GDPR Tests**: Article 17 Right to Erasure compliance
- **Performance Tests**: 1000 scenes < 3s, query latency < 10ms
- **Contract Tests**: Freud-2025 specification compliance

```bash
# Run all tests
pytest tests/ -v

# Run specific categories
pytest tests/ -v -m unit
pytest tests/ -v -m integration  
pytest tests/ -v -m security
pytest tests/ -v -m perf

# Comprehensive test runner
python3 run_c44_tests.py
```

## Production Deployment

### Environment Setup
```bash
export DATABASE_URL="postgresql://user:pass@localhost:5432/akaq_memory"
export AKAQ_SALT="your_production_salt_here"
```

### Migration
```bash
python3 cli/migrate_memory_db.py --db-url $DATABASE_URL --apply
```

### Health Check
```bash
python3 cli/memory_health_check.py --db-url $DATABASE_URL --full --prod-mode
```

### GDPR Compliance
```bash
# User data erasure
python3 cli/gdpr_erase_user.py \
  --user-id target_user \
  --db-url $DATABASE_URL \
  --salt $AKAQ_SALT \
  --prod-mode
```

## Security Features

- **Privacy Hashing**: User IDs hashed with SHA3-256 in production
- **SQL Injection Prevention**: Parameterized queries throughout
- **Audit Trails**: All operations logged for compliance
- **GDPR Article 17**: Complete user data erasure capability
- **Transaction Safety**: Atomic operations with rollback support

## Performance Targets

- **Scene Storage**: 1000 scenes < 3 seconds
- **Query Latency**: p95 < 10ms for retrieval operations
- **Memory Usage**: Efficient connection pooling
- **Uptime**: 99.9% availability target

---

**Wave C C4 Memory System** - Production-ready phenomenological processing with comprehensive testing and GDPR compliance.

For detailed operations guide, see: `docs/C4_OPERATIONS_GUIDE.md`
For CLI reference, see: `CLI_REFERENCE.md`