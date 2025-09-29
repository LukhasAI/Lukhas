# Wave C C4 CLI Tools Reference

Quick reference for Wave C memory system command-line tools.

## 🗄️ Database Migration

**Tool**: `cli/migrate_memory_db.py`

```bash
# Check current status (dry run)
python cli/migrate_memory_db.py --db-url sqlite:///akaq_memory.db

# Apply migrations
python cli/migrate_memory_db.py --db-url sqlite:///akaq_memory.db --apply

# Reset and migrate (DESTRUCTIVE)
python cli/migrate_memory_db.py --db-url sqlite:///akaq_memory.db --reset --apply

# PostgreSQL production
python cli/migrate_memory_db.py \
  --db-url postgresql://user:pass@localhost:5432/akaq_memory \
  --apply
```

## 🛡️ GDPR User Erasure

**Tool**: `cli/gdpr_erase_user.py`

```bash
# Preview erasure (dry run)
python cli/gdpr_erase_user.py \
  --user-id user123 \
  --db-url sqlite:///akaq_memory.db \
  --dry-run

# Execute erasure
python cli/gdpr_erase_user.py \
  --user-id user123 \
  --db-url sqlite:///akaq_memory.db

# Production mode with hashing
python cli/gdpr_erase_user.py \
  --user-id user123 \
  --db-url postgresql://user:pass@localhost:5432/akaq_memory \
  --salt production_salt \
  --prod-mode
```

## 🏥 Health Check

**Tool**: `cli/memory_health_check.py`

```bash
# Basic health check
python cli/memory_health_check.py --db-url sqlite:///akaq_memory.db

# Full health check with performance testing
python cli/memory_health_check.py \
  --db-url sqlite:///akaq_memory.db \
  --full

# Test NoopMemory (no database)
python cli/memory_health_check.py --memory-type noop --full

# Production health check
python cli/memory_health_check.py \
  --db-url postgresql://user:pass@localhost:5432/akaq_memory \
  --full \
  --prod-mode
```

## 🚀 Quick Start Workflow

```bash
# 1. Initialize database
python cli/migrate_memory_db.py --db-url sqlite:///akaq_memory.db --apply

# 2. Verify system health
python cli/memory_health_check.py --db-url sqlite:///akaq_memory.db --full

# 3. Test basic functionality
python test_simple.py

# 4. Run comprehensive tests
python run_c44_tests.py
```

## 💾 Database URLs

### SQLite (Development)
```bash
--db-url sqlite:///akaq_memory.db                    # Relative path
--db-url sqlite:///data/akaq_memory.db              # Absolute path
--db-url sqlite:////tmp/akaq_memory_test.db         # Temporary database
```

### PostgreSQL (Production)
```bash
--db-url postgresql://user:password@localhost:5432/akaq_memory
--db-url postgresql://user:password@db.example.com:5432/akaq_memory
--db-url postgresql://user:password@localhost/akaq_memory  # Default port
```

## ⚠️ Safety Notes

- Always use `--dry-run` first for destructive operations
- `--reset` flag will **permanently delete all data**
- GDPR erasure is **irreversible** - verify user ID before execution
- Production mode enables user ID hashing for privacy
- Health checks create temporary test data that is automatically cleaned up

## 📊 Exit Codes

All tools use standard exit codes:
- `0`: Success
- `1`: Error or failure
- User cancellation returns `1`

## 🔧 Troubleshooting

### Database Connection Issues
```bash
# Test connection manually
python -c "from sqlalchemy import create_engine; create_engine('sqlite:///akaq_memory.db').connect()"
```

### Schema Issues
```bash
# Force schema verification
python cli/migrate_memory_db.py --db-url sqlite:///akaq_memory.db --verify-only
```

### Permission Issues
```bash
# Make tools executable
chmod +x cli/*.py
```