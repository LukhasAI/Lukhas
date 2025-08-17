# LUKHAS PWM User Manual - Part 2: New Features
*For users with limited technical knowledge*

## Table of Contents
1. [New Features Overview](#new-features-overview)
2. [CI/CD Pipeline](#cicd-pipeline)
3. [Performance Testing](#performance-testing)
4. [SDK Libraries](#sdk-libraries)
5. [Backup & Recovery](#backup--recovery)
6. [Quick Start Guides](#quick-start-guides)

---

## New Features Overview

We've added four major features to make LUKHAS PWM more reliable and easier to use:

1. **Automated Testing & Deployment** - Ensures code quality automatically
2. **Performance Monitoring** - Checks system speed and reliability
3. **Easy Integration Libraries** - Connect from Python or JavaScript/TypeScript apps
4. **Backup System** - Save and restore your data

---

## CI/CD Pipeline

### What is CI/CD?

**CI/CD** stands for Continuous Integration/Continuous Deployment. It's like having a robot that:
- Checks your code for errors every time you make changes
- Runs tests automatically
- Deploys updates safely

### How It Works

Every time code is updated, the system automatically:

1. **Checks for Problems** (Quarantine Guard)
   - Makes sure no experimental code leaks into production
   - Scans for personal information (PII)

2. **Runs Quality Checks** (Linting)
   - Formats code consistently
   - Finds common mistakes

3. **Runs Tests** (Testing)
   - Makes sure everything still works
   - Tests on multiple Python versions (3.8, 3.9, 3.10)

### Viewing CI/CD Results

**On GitHub:**
1. Go to your repository
2. Click "Actions" tab
3. Green checkmark ✅ = All tests passed
4. Red X ❌ = Something needs fixing

**What the badges mean:**
- 🟢 **Green/Passing**: Everything is working
- 🔴 **Red/Failing**: There's a problem to fix
- 🟡 **Yellow/Warning**: Non-critical issues

### Common CI/CD Messages

| Message | What It Means | What To Do |
|---------|--------------|------------|
| "Quarantine imports found" | Experimental code in production | Move code to proper location |
| "PII detected" | Personal info found | Remove sensitive data |
| "Tests failed" | Something broke | Check test results, fix code |
| "Linting failed" | Code style issues | Run `make fix` locally |

---

## Performance Testing

### What is Performance Testing?

It's like a health checkup for your system - measures how fast it responds and how much load it can handle.

### Running Performance Tests

**Basic test (smoke test):**
```bash
# Run a quick 45-second test
k6 run perf/k6_smoke.js

# You'll see results like:
# ✓ 200 health ...... passed
# ✓ 200 tools ....... passed
# Response time: avg=45ms, p95=120ms
```

**What the results mean:**
- **avg=45ms**: Average response time (lower is better)
- **p95=120ms**: 95% of requests finish within 120ms
- **✓ passed**: Endpoint is working correctly
- **✗ failed**: Endpoint has issues

### Understanding Performance Metrics

| Metric | Good | Okay | Bad | What It Means |
|--------|------|------|-----|---------------|
| Health endpoint | <120ms | <200ms | >200ms | Basic system responsiveness |
| Tools endpoint | <200ms | <350ms | >350ms | Tool loading speed |
| Error rate | <1% | <5% | >5% | How often requests fail |

### When to Run Performance Tests

- **Before major updates** - Ensure changes don't slow things down
- **After adding features** - Check impact on performance
- **When users report slowness** - Diagnose performance issues

---

## SDK Libraries

### What are SDKs?

SDKs (Software Development Kits) are pre-built libraries that make it easy to connect to LUKHAS from your own programs.

### Python SDK

#### Installation

```bash
# Copy the SDK file to your project
cp sdk/python/lukhas_client.py your_project/

# Install required package
pip install requests
```

#### Basic Usage

```python
from lukhas_client import LukhasClient

# Connect to LUKHAS
client = LukhasClient()

# Send a message
response = client.complete(
    message="Help me write an email",
    safety_mode="balanced"
)
print(response['response'])

# Give feedback
client.give_feedback(
    target_action_id=response['audit_id'],
    rating=5,
    note="Perfect!"
)
```

#### Interactive Mode

The Python SDK includes an interactive chat mode:

```python
from lukhas_client import LukhasClient

client = LukhasClient()
client.interactive_session()

# Now you can chat:
# You: Hello
# LUKHAS: Hello! How can I help you today?
# You: !signal stress 0.8
# Set stress = 0.8
# You: Help me relax
# LUKHAS: [Adjusted response for high stress...]
```

**Interactive commands:**
- `quit` - Exit the session
- `help` - Show available commands
- `!context add <text>` - Add context
- `!signal <name> <value>` - Set a signal (0.0-1.0)
- `!audit <id>` - View audit details
- `!feedback <id> <rating> [note]` - Give feedback

### TypeScript/JavaScript SDK

#### Installation

```bash
# Copy the SDK file to your project
cp sdk/typescript/lukhas-client.ts your_project/

# For TypeScript projects
npm install --save-dev typescript

# For JavaScript, just use the compiled version
```

#### Basic Usage (TypeScript)

```typescript
import { LukhasClient } from './lukhas-client';

const client = new LukhasClient({
    baseUrl: 'http://localhost:8000',
    apiKey: 'your-api-key'
});

// Send a message
const response = await client.complete({
    message: 'Help me write an email',
    signals: { stress: 0.3 },
    safetyMode: 'balanced'
});

console.log(response.response);

// Give feedback
await client.giveFeedback({
    target_action_id: response.audit_id,
    rating: 4,
    note: 'Good but could be better'
});
```

#### React Integration

```jsx
import { useLukhasClient } from './lukhas-client';

function ChatComponent() {
    const { complete, giveFeedback, checkHealth } = useLukhasClient();
    
    const handleSend = async (message) => {
        const response = await complete(message);
        console.log(response);
    };
    
    const handleRating = async (auditId, rating) => {
        await giveFeedback(auditId, rating);
    };
    
    // Your component UI...
}
```

### SDK Features Comparison

| Feature | Python | TypeScript | Description |
|---------|--------|------------|-------------|
| Basic completion | ✅ | ✅ | Send messages and get responses |
| Feedback | ✅ | ✅ | Rate responses |
| Audit viewing | ✅ | ✅ | See decision details |
| Tool management | ✅ | ✅ | Control available tools |
| Batch processing | ✅ | ✅ | Process multiple messages |
| Interactive mode | ✅ | ❌ | Built-in chat interface |
| React hooks | ❌ | ✅ | Easy React integration |
| Retry logic | ✅ | ✅ | Automatic retry on failure |
| Timeout control | ✅ | ✅ | Set custom timeouts |

---

## Backup & Recovery

### What is Backup & Recovery?

It's like insurance for your data - saves copies of everything important so you can restore if something goes wrong.

### What Gets Backed Up?

1. **Audit logs** - All AI decisions and actions
2. **Feedback data** - Your ratings and preferences
3. **Configuration** - Your settings and API keys
4. **Analytics** - Usage statistics

### Creating Backups

#### Automatic Backup (Recommended)

Set up a daily backup schedule:

```bash
# Add to crontab (runs daily at 2 AM)
crontab -e
# Add this line:
0 2 * * * /path/to/lukhas/scripts/backup.sh
```

#### Manual Backup

```bash
# Simple backup
./scripts/backup.sh

# You'll see:
# [INFO] Starting LUKHAS backup at 2024-01-15 10:30:00
# [INFO] Backing up audit logs...
#   Found 1523 audit entries
# [INFO] Backing up feedback data...
#   Found 89 feedback entries
# [INFO] Backup created: lukhas_backup_20240115_103000.tar.gz (2.3MB)
# [INFO] Backup completed successfully!
```

### Backup to Cloud (S3)

For extra safety, back up to Amazon S3:

```bash
# Set up S3 (one time)
export LUKHAS_S3_BUCKET=my-backups
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret

# Run backup with S3 upload
./scripts/backup.sh

# Files are automatically uploaded to S3
```

### Restoring from Backup

#### List Available Backups

```bash
# Show local backups
./scripts/restore.sh -l

# Output:
# Available local backups:
# -rw-r--r-- 2.3M Jan 15 10:30 lukhas_backup_20240115_103000.tar.gz
# -rw-r--r-- 2.1M Jan 14 02:00 lukhas_backup_20240114_020000.tar.gz
```

#### Restore Latest Backup

```bash
# Restore from local file
./scripts/restore.sh backups/lukhas_backup_20240115_103000.tar.gz

# You'll be asked:
# Found existing data directories: .lukhas_audit .lukhas_feedback
# Overwrite existing data? (y/N): y

# [INFO] Restoring audit logs...
#   Restored 1523 audit entries
# [INFO] Restoring feedback data...
#   Restored 89 feedback entries
# [INFO] Restore completed successfully!
```

#### Restore from S3

```bash
# Download and restore from S3
./scripts/restore.sh -s lukhas-backups/lukhas_backup_20240115_103000.tar.gz
```

#### Verify Backup Without Restoring

```bash
# Just check if backup is valid
./scripts/restore.sh -v backups/lukhas_backup_20240115_103000.tar.gz

# Shows:
# [INFO] Verifying backup integrity...
#   Checksum verified: OK
# [INFO] Backup contents:
#   audit/audit.jsonl
#   feedback/feedback.jsonl
#   config/modulation_policy.yaml
#   ...
```

### Backup Best Practices

1. **Regular Schedule**: Back up daily or weekly
2. **Test Restores**: Periodically test that backups work
3. **Offsite Storage**: Use S3 or similar for safety
4. **Retention Policy**: Keep last 30 days of backups
5. **Before Updates**: Always backup before major changes

### Troubleshooting Backup Issues

| Problem | Solution |
|---------|----------|
| "No space left" | Clean old backups: `find backups/ -mtime +30 -delete` |
| "Permission denied" | Run with sudo or fix permissions |
| "S3 upload failed" | Check AWS credentials and internet connection |
| "Checksum mismatch" | Backup corrupted, use different backup |
| "Restore overwrites data" | Use `-d new_directory` to restore elsewhere |

---

## Quick Start Guides

### Quick Start: Python Developer

```python
# 1. Install SDK
cp sdk/python/lukhas_client.py ./

# 2. Basic script
from lukhas_client import LukhasClient

client = LukhasClient()

# 3. Use it
response = client.complete(
    message="Generate a Python function to sort a list",
    signals={"novelty": 0.7}
)
print(response['response'])

# 4. Interactive mode
client.interactive_session()
```

### Quick Start: Web Developer

```javascript
// 1. Import SDK
import { LukhasClient } from './lukhas-client';

// 2. Initialize
const lukhas = new LukhasClient();

// 3. Use in async function
async function askLukhas() {
    const response = await lukhas.complete({
        message: "Help me with CSS grid",
        safetyMode: "balanced"
    });
    console.log(response.response);
}

// 4. React component
function App() {
    const { complete } = useLukhasClient();
    // Your app...
}
```

### Quick Start: System Administrator

```bash
# 1. Set up automated backup
echo "0 2 * * * $PWD/scripts/backup.sh" | crontab -

# 2. Configure S3 backup (optional)
cat >> .env << EOF
LUKHAS_S3_BUCKET=my-backups
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
EOF

# 3. Test backup
./scripts/backup.sh

# 4. Test restore
./scripts/restore.sh -v backups/lukhas_backup_*.tar.gz

# 5. Monitor performance
k6 run perf/k6_smoke.js
```

### Quick Start: DevOps Engineer

```yaml
# 1. GitHub Actions already configured in .github/workflows/ci.yml
# Just push code and CI/CD runs automatically

# 2. View results at:
# https://github.com/[your-org]/lukhas/actions

# 3. Set up monitoring
k6 run --out json=metrics.json perf/k6_smoke.js

# 4. Configure alerts (example)
if [ $(jq '.metrics.http_req_duration.p95' metrics.json) -gt 200 ]; then
    echo "Performance degraded - alert team"
fi
```

---

## Summary

You now have:

✅ **Automated Quality Checks** - CI/CD pipeline ensures code quality
✅ **Performance Monitoring** - k6 tests measure system speed
✅ **Easy Integration** - Python and TypeScript SDKs for quick development
✅ **Data Protection** - Complete backup and restore system

### Next Steps

1. **Set up daily backups** - Protect your data
2. **Try the SDK** - Build your first integration
3. **Run performance tests** - Establish baseline metrics
4. **Enable CI/CD** - Push code to GitHub to activate

### Getting Help

- **Check logs**: `.lukhas_audit/`, `.lukhas_feedback/`
- **Run tests**: `k6 run perf/k6_smoke.js`
- **Verify backup**: `./scripts/restore.sh -v [backup-file]`
- **Interactive help**: `python -c "from lukhas_client import LukhasClient; LukhasClient().interactive_session()"`

---

*End of Part 2: New Features Manual*