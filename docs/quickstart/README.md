# LUKHAS 5-Minute Quickstart

Get from `git clone` to working LUKHAS demo in under 5 minutes.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.9+** ([Download](https://www.python.org/downloads/))
- **Git** ([Download](https://git-scm.com/downloads))
- **Make** (usually pre-installed on macOS/Linux)
- **Docker** (optional, for containerized mode) ([Download](https://www.docker.com/get-started))

### Quick Check

```bash
python3 --version  # Should be 3.9 or higher
git --version
make --version
```

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/LukhasAI/Lukhas.git
cd Lukhas
```

### Step 2: Run Quickstart Script

```bash
bash scripts/quickstart.sh
```

That's it! The script will:

1. ✅ Check prerequisites
2. ✅ Create `.env` with development defaults
3. ✅ Install Python dependencies
4. ✅ Initialize database
5. ✅ Generate demo data
6. ✅ Run validation tests
7. ✅ Start the server at `http://localhost:8000`

**Expected time**: 3-4 minutes on a fresh install

## First Steps

### 1. Run Your First Example

```bash
# Simple greeting (30 seconds)
python3 examples/quickstart/01_hello_lukhas.py

# Visual reasoning trace (1 minute)
python3 examples/quickstart/02_reasoning_trace.py

# Memory persistence demo (1 minute)
python3 examples/quickstart/03_memory_persistence.py

# Ethics and consent (1 minute)
python3 examples/quickstart/04_guardian_ethics.py

# Full workflow (2 minutes)
python3 examples/quickstart/05_full_workflow.py
```

### 2. Use the Guided CLI

```bash
# Interactive setup wizard
lukhas quickstart

# Run a specific demo
lukhas demo hello

# Take the interactive tour
lukhas tour

# Troubleshoot issues
lukhas troubleshoot
```

### 3. Explore the API

```python
from lukhas.api import reasoning_engine

# Simple query
response = reasoning_engine.query(
    prompt="Explain consciousness-inspired AI",
    include_trace=True
)

print(response.content)
print(response.reasoning_trace)
```

## What You Get

### Pre-Configured Examples

All examples are in `examples/quickstart/`:

| Example | Description | Time |
|---------|-------------|------|
| `01_hello_lukhas.py` | Simple greeting and intro | 30s |
| `02_reasoning_trace.py` | Multi-step reasoning visualization | 1m |
| `03_memory_persistence.py` | Context preservation demo | 1m |
| `04_guardian_ethics.py` | Constitutional AI demo | 1m |
| `05_full_workflow.py` | End-to-end example | 2m |

### Interactive Tools

- `lukhas quickstart` - Setup wizard
- `lukhas demo <name>` - Run examples
- `lukhas tour` - Interactive product tour
- `lukhas troubleshoot` - Auto-diagnose issues

### Demo Data

Generated in `demo_data/`:

- **Reasoning traces**: Sample multi-step reasoning
- **Memory folds**: Example context preservation
- **Evidence pages**: Sample verification documents
- **Claims**: Example claims with evidence links

## Troubleshooting

### Common Issues

#### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'lukhas'`

**Solution**:
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Port Already in Use

**Problem**: `Address already in use: localhost:8000`

**Solution**:
```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
PORT=8001 python3 -m lukhas.api.server
```

#### Database Errors

**Problem**: `sqlite3.OperationalError: no such table`

**Solution**:
```bash
# Remove old database and reinitialize
rm lukhas_dev.db
bash scripts/quickstart.sh
```

#### Permission Denied

**Problem**: `Permission denied: './scripts/quickstart.sh'`

**Solution**:
```bash
# Make script executable
chmod +x scripts/quickstart.sh
bash scripts/quickstart.sh
```

### Auto-Diagnosis

Run the troubleshooting assistant for automatic issue detection:

```bash
lukhas troubleshoot
```

This will check:

- ✅ Python version (3.9+ required)
- ✅ Dependencies installed
- ✅ Port availability (8000, 5432, 6379)
- ✅ Docker status (optional)
- ✅ Environment configuration
- ✅ Database initialization

### Still Stuck?

1. **Check the logs**: Look for error messages in the terminal
2. **Read the docs**: [Architecture](../ARCHITECTURE.md) | [API Reference](../API_REFERENCE.md)
3. **Search issues**: [GitHub Issues](https://github.com/LukhasAI/Lukhas/issues)
4. **Ask for help**: [Open a new issue](https://github.com/LukhasAI/Lukhas/issues/new)

## Next Steps

### Learn the Architecture

- **[Architecture Overview](../ARCHITECTURE.md)** - Understand LUKHAS design
- **[MATRIZ Engine](../ARCHITECTURE.md#matriz)** - Consciousness-inspired reasoning
- **[Memory Folds](../ARCHITECTURE.md#memory-folds)** - Bio-inspired memory system
- **[Guardian](../ARCHITECTURE.md#guardian)** - Constitutional AI & ethics

### Dive into the API

- **[API Reference](../API_REFERENCE.md)** - Complete API documentation
- **[Core API](../API_REFERENCE_CORE.md)** - Core module reference
- **[Examples](../../examples/)** - More example code

### Deploy to Production

- **[Deployment Guide](../DEPLOYMENT.md)** - Production deployment
- **[Security Guide](../SECURITY.md)** - Security best practices
- **[Monitoring](../MONITORING.md)** - Observability and metrics

### Join the Community

- **GitHub**: [github.com/LukhasAI/Lukhas](https://github.com/LukhasAI/Lukhas)
- **Documentation**: [lukhas.ai/docs](https://lukhas.ai/docs)
- **Discord**: [Join our community](https://discord.gg/lukhas)
- **Twitter**: [@LukhasAI](https://twitter.com/LukhasAI)

## FAQs

### How is LUKHAS different from other AI systems?

LUKHAS uses **consciousness-inspired** and **bio-inspired** cognitive architecture:

- **Reasoning**: Multi-step reasoning inspired by biological thought processes
- **Memory**: Context preservation with natural forgetting curves (like human memory)
- **Ethics**: Built-in Constitutional AI with consent framework
- **Architecture**: Quantum-inspired and bio-inspired algorithms

### Can I use LUKHAS in production?

Yes! LUKHAS is designed for production use, but ensure you:

1. Review **security best practices** (docs/SECURITY.md)
2. Configure **proper authentication**
3. Use **production database** (PostgreSQL, not SQLite)
4. Enable **monitoring and logging**
5. Follow **GDPR compliance** guidelines

### Do I need API keys?

For the **demo mode**, API keys are optional. LUKHAS uses demo data and simulated responses.

For **production mode**, you'll need:

- **OpenAI API key** (optional, for external model integration)
- **Anthropic API key** (optional, for Claude integration)

Configure in `.env`:
```bash
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here
```

### How do I contribute?

We welcome contributions! See:

- **[Contributing Guide](../../CONTRIBUTING.md)** - How to contribute
- **[Code of Conduct](../../CODE_OF_CONDUCT.md)** - Community standards
- **[Development Setup](../DEVELOPMENT.md)** - Dev environment setup

### Is LUKHAS open source?

Yes! LUKHAS is licensed under **AGPL-3.0-or-later**.

See [LICENSE](../../LICENSE) for full terms.

## Video Walkthrough

_Coming soon: A 5-minute video walkthrough of the quickstart process._

Script outline:

1. **[0:00-0:30]** Introduction to LUKHAS
2. **[0:30-1:30]** Clone repo and run quickstart script
3. **[1:30-2:30]** Run first example (hello_lukhas.py)
4. **[2:30-3:30]** Explore reasoning trace visualization
5. **[3:30-4:30]** Demonstrate memory persistence
6. **[4:30-5:00]** Next steps and resources

## Feedback

We'd love to hear about your experience!

- **What worked well?**
- **What was confusing?**
- **What would you improve?**

[Share your feedback](https://github.com/LukhasAI/Lukhas/discussions)

---

**Ready to build consciousness-inspired AI?** 🚀

Start with [example 01](../../examples/quickstart/01_hello_lukhas.py) and let's go!
