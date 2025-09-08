---
title: Journal Quick Reference
status: review
owner: docs-team
last_review: 2025-09-08
tags: ["consciousness", "architecture", "howto"]
facets:
  layer: ["gateway"]
  domain: ["symbolic", "consciousness", "memory", "quantum"]
  audience: ["dev"]
---

# LUKHAS Journal - Quick Reference Card

## 🚀 Most Used Commands

```bash
./journal quick                    # Quick entry mode (interactive)
./journal standup                  # AI daily standup 🌅
./journal status                   # View stats & daily summary
./journal add "your entry here"    # Add entry quickly
./journal search -q "keyword"      # Search entries
./journal ask "your question"      # Ask AI assistant
./journal celebrate "win"          # Celebrate achievement! 🎉
./journal pair "task"             # AI pair programming 🤝
./journal burnout                 # Check burnout risk 🚨
```

## ✍️ Quick Entry Mode Commands
```
In quick mode:
d: decision text    → Track decision
i: insight text     → Add insight
q: question text    → Add question
l: learning text    → Add learning
exit               → Exit mode
```

## 🏷️ Entry Types
- `decision` - Development decisions
- `insight` - Realizations/observations
- `learning` - Things you learned
- `question` - Things to explore
- `pattern` - Repeated behaviors

## 📝 Common Examples

```bash
# Add with tags and emotions
./journal add "Fixed memory leak" -t insight -g bug performance -e satisfaction:0.9

# Track a decision properly
./journal decision  # (interactive prompts)

# Import your notes
./journal import notes.md
./journal import backup.json

# Ask for help
./journal mentor "I'm stuck on this bug"
./journal ask "How do I optimize memory folds?"

# Track skill progress
./journal track "Python" --level 8

# Export journal
./journal export -o backup.md -d 90
```

## 🎯 Aliases for ~/.zshrc
```bash
alias j="cd /Users/agi_dev/Lukhas && ./journal"
alias jq="cd /Users/agi_dev/Lukhas && ./journal quick"
alias ja="cd /Users/agi_dev/Lukhas && ./journal add"
alias js="cd /Users/agi_dev/Lukhas && ./journal search"
```

## 🤝 Solo Dev Commands
```bash
# Daily workflow
./journal standup              # Morning AI standup
./journal pair "task"          # Get pair programming help
./journal celebrate "win"      # Celebrate achievements
./journal burnout             # Check wellness

# Periodic reviews
./journal weekly              # Weekly architecture review
./journal vision              # Monthly vision check
```

## 🧠 Claude + LUKHAS Integration
```bash
# Consciousness-aware development
./journal conscious "task"     # Start conscious coding session
./journal ritual "intention"   # Create development ritual
./journal metrics             # View consciousness metrics

# Quantum decision making
./journal quantum-decide -o "option1" -o "option2"

# LUKHAS prompts for Claude
./journal prompt -t code_review
./journal lukhas-config       # Generate integration config
```

## 🌟 Power User Tips
- Start day with `./journal standup`
- Use `./journal pair` for complex tasks
- Celebrate wins with `./journal celebrate`
- Check burnout weekly
- Export regularly for backup

## 📊 Emotion Values
0.0 = None, 0.5 = Moderate, 1.0 = Maximum

Common: confidence, curiosity, satisfaction, frustration, excitement

---
*Full guide: /docs/LUKHAS_JOURNAL_USER_GUIDE.md*
