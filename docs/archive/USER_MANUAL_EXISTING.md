# LUKHAS PWM User Manual - Part 1: Existing Features
*For users with limited technical knowledge*

## Table of Contents
1. [What is LUKHAS PWM?](#what-is-lukhas-pwm)
2. [Getting Started](#getting-started)
3. [Core Features](#core-features)
4. [How to Use Each Feature](#how-to-use-each-feature)
5. [Common Tasks](#common-tasks)
6. [Troubleshooting](#troubleshooting)

---

## What is LUKHAS PWM?

LUKHAS PWM (Personal Workspace Manager) is an AI system that adapts its behavior based on various signals like stress, safety concerns, and user feedback. Think of it as a smart assistant that learns how to better help you over time.

### Key Concepts Made Simple
- **Signals**: Like emotions for the AI - they tell it when to be careful, creative, or quick
- **Tools**: Functions the AI can use (like searching, browsing, scheduling)
- **Feedback**: Your ratings that help the AI improve
- **Audit**: A record of everything the AI does for safety and transparency

---

## Getting Started

### 1. Setting Up Your Environment

First, create a file called `.env` in your project folder with these settings:

```bash
# Your API keys (get these from OpenAI, etc.)
OPENAI_API_KEY=your-key-here

# Optional: Set your preferred safety level
LUKHAS_FLAG_STRICT_DEFAULT=false

# Optional: Enable/disable features
FLAG_BROWSER_TOOL=true
FLAG_TOOL_ANALYTICS=true
FLAG_ADMIN_DASHBOARD=true
```

### 2. Starting the System

Open a terminal and run:

```bash
# Start the API server
python -m lukhas.api.app

# The system is now running at http://localhost:8000
```

You should see:
```
INFO: Uvicorn running on http://127.0.0.1:8000
INFO: Application startup complete
```

---

## Core Features

### 1. 🎛️ Smart Response Adjustment (Signal Modulation)

**What it does:** Automatically adjusts how the AI responds based on the situation.

**Example scenarios:**
- **High Risk Detected** → AI becomes more careful, gives shorter, safer responses
- **Creative Task** → AI becomes more exploratory and innovative
- **Time Pressure** → AI gives quick, direct answers

**How it works for you:** You don't need to do anything! The system automatically detects these conditions and adjusts.

### 2. 🛡️ Tool Safety (Governance)

**What it does:** Controls which tools the AI can use to keep you safe.

**Available tools:**
- **Search** 🔍: Look up information
- **Browser** 🌐: Visit websites (can be disabled for safety)
- **Scheduler** 📅: Set reminders
- **Code Execution** 💻: Run code (only when safe)

**Safety modes:**
- **Strict**: Only search and retrieval allowed
- **Balanced**: Most tools available
- **Creative**: All tools available

### 3. 📝 Feedback System

**What it does:** Learns from your ratings to improve responses.

**How to give feedback:**
1. After any AI response, you can rate it 1-5 stars
2. Optionally add a note explaining what you liked/disliked
3. The system adjusts its style (not safety!) based on your preferences

**Example:**
```python
# Give feedback on a response
feedback = {
    "target_action_id": "response-123",
    "rating": 4,
    "note": "Good but could be more detailed"
}
```

### 4. 📊 Audit Trail

**What it does:** Keeps a complete record of all AI actions for transparency.

**What's recorded:**
- Every decision made
- Tools used
- Safety checks performed
- Your feedback

**How to view:** Visit `http://localhost:8000/audit/view/[audit-id]` in your browser

### 5. 🚦 Feature Flags

**What it does:** Lets you turn features on/off without changing code.

**Common flags you can set:**
```bash
# Force strict safety mode always
FLAG_STRICT_DEFAULT=true

# Disable browser tool
FLAG_BROWSER_TOOL=false

# Turn off analytics
FLAG_TOOL_ANALYTICS=false
```

---

## How to Use Each Feature

### Using the AI Assistant

#### Basic Conversation

1. **Send a message:**
```python
response = lukhas.complete(
    message="Help me plan a birthday party",
    safety_level="balanced"  # optional
)
```

2. **The AI responds** with helpful information, automatically adjusted for safety and context

#### Checking What Happened

1. **View the audit log:**
   - Open your browser
   - Go to: `http://localhost:8000/audit/view/[audit-id]`
   - See exactly what the AI did and why

2. **Understanding the audit page:**
   - **Green badge** = Balanced mode (normal)
   - **Red badge** = Strict mode (extra safe)
   - **Blue badge** = Creative mode (exploratory)

### Giving Feedback

#### Through the Web Interface

1. Visit: `http://localhost:8000/feedback`
2. Find the response you want to rate
3. Click the stars (1-5)
4. Add a note if you want
5. Click "Submit"

#### Through Code

```python
from lukhas.feedback import give_feedback

give_feedback(
    response_id="abc-123",
    stars=5,
    comment="Perfect response!"
)
```

### Viewing System Status

#### Admin Dashboard (if enabled)

1. Visit: `http://localhost:8000/admin`
2. You'll see:
   - **Safety Mode Distribution**: How often each mode is used
   - **Tool Usage**: Which tools are being used and how often
   - **Recent Incidents**: Any blocked actions for safety

### Adjusting Behavior

#### Change Safety Preferences

**For one session:**
```python
response = lukhas.complete(
    message="Your question here",
    force_mode="strict"  # or "balanced" or "creative"
)
```

**Permanently (until changed):**
Edit your `.env` file:
```bash
FLAG_STRICT_DEFAULT=true  # Always use strict mode
```

#### Enable/Disable Tools

Edit your `.env` file:
```bash
FLAG_BROWSER_TOOL=false  # Disable web browsing
FLAG_CODE_EXEC=false     # Disable code execution
```

---

## Common Tasks

### Task 1: "I want safer responses"

**Solution:** Enable strict mode by default

1. Edit `.env` file
2. Add: `FLAG_STRICT_DEFAULT=true`
3. Restart the system

### Task 2: "I want to see what the AI is doing"

**Solution:** Check the audit trail

1. After any interaction, note the audit ID (shown in response)
2. Visit: `http://localhost:8000/audit/view/[that-id]`
3. See complete details

### Task 3: "The AI should remember my preferences"

**Solution:** Use the feedback system consistently

1. Rate every response (1-5 stars)
2. Add notes for unusual preferences
3. System learns over 10-20 interactions

### Task 4: "I don't want the AI browsing the web"

**Solution:** Disable the browser tool

1. Edit `.env` file
2. Add: `FLAG_BROWSER_TOOL=false`
3. Restart the system

### Task 5: "Check if everything is working"

**Solution:** Run the health check

```bash
curl http://localhost:8000/feedback/health
```

Should return:
```json
{"ok": true, "status": "healthy"}
```

---

## Troubleshooting

### Problem: "System won't start"

**Check:**
1. Is Python installed? (Need version 3.8+)
2. Are dependencies installed? (`pip install -r requirements.txt`)
3. Is port 8000 free? (Change with `--port 8001` if needed)

### Problem: "AI gives errors about missing API key"

**Solution:**
1. Get an API key from OpenAI
2. Add to `.env`: `OPENAI_API_KEY=sk-...`
3. Restart the system

### Problem: "Responses are too strict/careful"

**Check:**
1. Is `FLAG_STRICT_DEFAULT=true`? Change to `false`
2. Recent high-risk interactions auto-tighten safety (temporary)
3. Wait a few minutes or restart to reset

### Problem: "Feedback isn't working"

**Check:**
1. Is the feedback directory writable? (`.lukhas_feedback/`)
2. Are you using valid ratings? (1-5 only)
3. Check logs for errors: `tail -f .lukhas_audit/audit.jsonl`

### Problem: "Can't access admin dashboard"

**Solution:**
1. Enable in `.env`: `FLAG_ADMIN_DASHBOARD=true`
2. Set an API key: `LUKHAS_API_KEY=your-secret-key`
3. Access with key: `http://localhost:8000/admin?key=your-secret-key`

---

## Quick Reference Card

### Essential Commands

```bash
# Start system
python -m lukhas.api.app

# Check health
curl http://localhost:8000/feedback/health

# View audit
# Browser: http://localhost:8000/audit/view/[id]

# Give feedback (Python)
feedback(response_id="...", rating=4, note="Good")
```

### Key Environment Variables

```bash
# API Keys
OPENAI_API_KEY=sk-...

# Feature Flags
FLAG_STRICT_DEFAULT=true/false
FLAG_BROWSER_TOOL=true/false
FLAG_TOOL_ANALYTICS=true/false
FLAG_ADMIN_DASHBOARD=true/false

# Paths (optional)
LUKHAS_AUDIT_DIR=.lukhas_audit
LUKHAS_FEEDBACK_DIR=.lukhas_feedback
```

### Safety Modes at a Glance

| Mode | Tools Allowed | Best For |
|------|--------------|----------|
| Strict | Search only | Sensitive topics, minors |
| Balanced | Most tools | General use |
| Creative | All tools | Brainstorming, exploration |

---

## Getting Help

### Logs Location
- Audit logs: `.lukhas_audit/audit.jsonl`
- Feedback: `.lukhas_feedback/feedback.jsonl`
- System logs: Check terminal where you started the system

### Support Resources
- GitHub Issues: [Report problems here]
- Documentation: This manual
- API Docs: `http://localhost:8000/docs` (when running)

---

*End of Part 1: Existing Features Manual*