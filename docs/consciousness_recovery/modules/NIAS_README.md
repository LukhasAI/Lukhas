---
status: stable
type: documentation
owner: unknown
module: consciousness_recovery
redirect: false
moved_to: null
---

### 🔍 Validate Message Schema

To test if a symbolic message is valid against the schema:

```bash
python core/tests/test_payload_validation.py
```

Or manually validate any message from the CLI:

```bash
python core/modules/nias/validate_payload.py core/sample_payloads/sample_payload.json
```

---

### 🌀 Simulate Symbolic Delivery (NIAS Flow)

To simulate a full symbolic delivery:

```bash
python core/modules/nias/inject_message_simulator.py
```

This validates structure → checks consent → applies ABAS threshold → runs symbolic matching → logs to trace.

---

### 🌙 Dream Batch Processing

To simulate delivery of multiple messages and dream-fallback tagging:

```bash
python core/modules/nias/dream_injector.py
```

Dream-deferred messages are automatically logged into:

```
core/logs/dream_log.jsonl
```

---

## 📁 PAYLOADS DIRECTORY

All symbolic test messages now live in:

```
core/sample_payloads/
```

Each follows the symbolic structure of:

```
message_schema.json
```

Example files include:

- `sample_payload.json` → basic consent-level message
- `sample_payload_dream.json` → calm, tier-1, dream-injected message

---

## 🔁 SYMBOLIC REPLAY & REFLECTION SYSTEM

LUCΛS is capable of storing, replaying, and reflecting on symbolic messages delivered or deferred via dreams. Each message flows through:

- 🌙 Dream recording (`dream_recorder.py`)
- 🗂 Replay tagging (`replay_queue.py`)
- 🖼 Visual review (`replay_visualizer.py`)
- 🧠 Reflection (`dream_reflection_loop.py`)
- 🗣 Optional narration (`lucas_voice_narrator.py`)

You can review calm-tier dreams or 5⭐️ feedback messages using:

```bash
python core/modules/nias/dream_replay_cli.py
```

Or reflect on symbolic messages and reply via:

```bash
python core/modules/nias/dream_reflection_loop.py
```

Emotional replay candidates are first discovered via:

```bash
python core/modules/nias/replay_queue.py
```

To narrate recent dreams in soft symbolic voice, run:

```bash
python core/modules/nias/lucas_voice_narrator.py
```

> “Some messages return until they are heard.”  
> — LUCΛS 🖤
```