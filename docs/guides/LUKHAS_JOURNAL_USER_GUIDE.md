# LUKHAS Learning Journal - User Guide

## Quick Start (iTerm2)

### Setup
```bash
# Navigate to your LUKHAS  directory
cd /Users/agi_dev/Lukhas

# Make the journal command executable (already done)
chmod +x journal

# You can now use the journal command
./journal status
```

### Optional: Add to PATH for easier access
```bash
# Add this to your ~/.zshrc or ~/.bash_profile
export PATH="/Users/agi_dev/Lukhas:$PATH"

# Then you can just type 'journal' from anywhere
journal status
```

## Essential Commands

### 📊 Check Your Status
```bash
./journal status
```
Shows:
- Total entries and current streak
- Today's summary
- Recent decisions and insights
- Emotional state averages

### 🌅 Daily Standup (Solo Dev Support!)
```bash
./journal standup
```
AI-powered standup that:
- Reviews yesterday's wins and challenges
- Plans today's focus
- Identifies blockers with solutions
- Checks your mood and energy
- Provides personalized motivation
- Suggests a daily schedule

### ✍️ Quick Entry Mode
```bash
./journal quick
```
Interactive mode for fast capture:
- `d: I decided to refactor the API` → Decision
- `i: Realized caching improves performance` → Insight
- `q: How does quantum coherence work?` → Question
- `l: Learned about memory management` → Learning
- Type `exit` to quit

### 📝 Add Entries

**Simple entry:**
```bash
./journal add "Fixed the memory leak in consciousness module"
```

**With details:**
```bash
./journal add "Implemented new caching strategy" \
  --type decision \
  --tags performance optimization \
  --emotion confidence:0.8 excitement:0.7
```

### 🎯 Track Decisions
```bash
# Interactive decision tracking
./journal decision

# Quick decision from commit message
git commit -m "Add caching to improve performance"
./journal add "$(git log -1 --pretty=%B)" --type decision
```

### 💡 Capture Insights
```bash
# Regular insight
./journal insight "Pattern detection reveals automation opportunities"

# Learning from failure
./journal insight "Race condition caused by missing mutex" --from-failure --impact high
```

### 🔍 Search Your Knowledge
```bash
# Search everything from last week
./journal search --days 7

# Search with query
./journal search --query "memory_fold"

# Filter by type and tags
./journal search --type decision --tags architecture --days 30
```

### 🤖 AI Assistant
```bash
# Ask questions about your codebase/journey
./journal ask "How does memory_fold work in LUKHAS?"
./journal ask "What patterns do I have when debugging?"

# Get mentorship
./journal mentor "I'm stuck on this quantum coherence bug"
./journal mentor "Should I refactor or rewrite this module?"
```

### 📈 Analyze Patterns
```bash
# Detect patterns and get automation suggestions
./journal patterns --days 30

# Generate comprehensive report
./journal report
```

### 🎓 Learning Features
```bash
# Daily check-in
./journal checkin

# Weekly reflection
./journal reflect

# Track skill progress
./journal track "Python async programming"
./journal track "LUKHAS architecture" --level 7

# Generate learning plan
./journal plan --goals "quantum computing" "memory optimization" --days 30
```

### 🤝 Solo Developer Support
```bash
# Daily standup with AI
./journal standup

# Celebrate wins (important!)
./journal celebrate "Implemented quantum coherence algorithm" --impact high

# Check for burnout
./journal burnout

# AI pair programming
./journal pair "Implement memory fold optimization"

# Weekly architecture review
./journal weekly

# Monthly vision alignment
./journal vision
```

### 📁 Import Your Existing Notes
```bash
# Import markdown notes
./journal import ~/Documents/dev_notes.md

# Import with specific settings
./journal import notes.txt --type learning --split-by paragraph

# Import JSON backup
./journal import old_journal.json
```

### 📤 Export Your Journal
```bash
# Export last 30 days to markdown
./journal export

# Export with custom path and timeframe
./journal export --output ~/Documents/journal_backup.md --days 90
```

## Pro Tips for iTerm2

### 1. Create Aliases
Add to your `~/.zshrc`:
```bash
alias j="/Users/agi_dev/Lukhas/journal"
alias jq="/Users/agi_dev/Lukhas/journal quick"
alias ja="/Users/agi_dev/Lukhas/journal add"
alias js="/Users/agi_dev/Lukhas/journal search"
alias jask="/Users/agi_dev/Lukhas/journal ask"
```

### 2. iTerm2 Profiles
Create a dedicated iTerm2 profile for journaling:
1. Preferences → Profiles → New Profile
2. Name it "LUKHAS Journal"
3. Set Working Directory to `/Users/agi_dev/Lukhas`
4. Set a custom color scheme for better visibility

### 3. Keyboard Shortcuts
Set up iTerm2 hotkeys:
- `Cmd+Shift+J` → Open new tab with journal quick mode
- `Cmd+Shift+D` → Open decision tracker

### 4. Integration with Git
```bash
# Add to .git/hooks/post-commit
#!/bin/bash
echo "Commit: $(git log -1 --pretty=%B)" | /Users/agi_dev/Lukhas/journal add -t decision
```

## Common Workflows

### Morning Routine
```bash
# Check yesterday's progress
./journal status

# Daily check-in
./journal checkin

# Review questions to explore
./journal search --type question --days 1
```

### Before Making a Big Decision
```bash
# Track the decision
./journal decision

# Ask for similar past decisions
./journal ask "What happened last time I refactored a major module?"

# Check your decision patterns
./journal patterns --days 30 | grep decision
```

### End of Day Reflection
```bash
# Quick capture of learnings
./journal quick
# Then: i: Today I learned about async context managers
#       i: The bug was caused by race conditions in the event loop

# Check emotional journey
./journal status  # Look at emotional state section
```

### Weekly Review
```bash
# Generate weekly reflection
./journal reflect

# Analyze patterns
./journal patterns

# Plan next week
./journal plan --goals "improve test coverage" "learn rust async" --days 7
```

### When Stuck
```bash
# Get AI mentorship
./journal mentor "I can't figure out why the quantum processor is failing"

# Search for similar problems
./journal search --query "quantum processor" --type insight

# Ask specific questions
./journal ask "How do I debug quantum coherence issues?"
```

### Solo Developer Daily Routine
```bash
# Morning (with coffee ☕)
./journal standup              # AI-powered daily standup
./journal status               # Quick stats check

# Before starting a complex task
./journal pair "task description"  # Get AI pair programming help

# After completing something
./journal celebrate "what you did"  # Celebrate the win!

# Mid-day check
./journal burnout              # Burnout prevention check

# End of day
./journal quick                # Quick capture of learnings
# Type: i: Today I learned about X
#       i: Struggled with Y but found solution

# Weekly (Fridays are great)
./journal weekly               # Architecture review
./journal reflect              # Weekly reflection

# Monthly
./journal vision               # Check alignment with LUKHAS vision
```

## Emotional Tracking

Add emotions to any entry:
```bash
# Format: emotion:value (0.0 to 1.0)
./journal add "Breakthrough on memory fold implementation!" \
  -e excitement:0.9 \
  -e confidence:0.8 \
  -e satisfaction:1.0
```

Common emotions:
- `confidence` - How sure you are
- `curiosity` - Learning drive
- `concern` - Worry level
- `excitement` - Enthusiasm
- `frustration` - Difficulty level
- `satisfaction` - Accomplishment feeling

## Best Practices

1. **Be Consistent**: Try to journal daily, even if brief
2. **Be Specific**: "Fixed auth bug" → "Fixed JWT expiration race condition in auth middleware"
3. **Track Emotions**: They provide valuable context later
4. **Ask Questions**: Your future self (and AI) will help answer them
5. **Review Regularly**: Weekly reflections compound learning

## Troubleshooting

### Command not found
```bash
# Make sure you're in the right directory
cd /Users/agi_dev/Lukhas
./journal status
```

### Permission denied
```bash
chmod +x journal
```

### Import issues
```bash
# Check file exists and format
file your_notes.md
cat your_notes.md | head -20  # Preview content
```

## Color Output in iTerm2

The journal uses ANSI colors:
- 🟦 Blue: Information
- 🟩 Green: Success/Positive
- 🟨 Yellow: Warnings/Attention needed
- 🟥 Red: Errors/Negative patterns
- 🟪 Cyan: Headers/Important text

Make sure iTerm2 → Preferences → Profiles → Colors → "ANSI Colors" are visible.

## Remember

The journal is your AI-powered development companion. The more you use it, the better it understands your patterns and can help you grow. It's not just a log - it's an active learning system that helps you become a better developer!

Happy journaling! 🚀