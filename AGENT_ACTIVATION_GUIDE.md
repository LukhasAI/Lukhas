# Agent Activation Guide

**Date:** November 2, 2025  
**Purpose:** Manual activation instructions for all agents

---

## 🤖 Agent Status & Activation

### 1. Jules (@jules / Google Labs)

**Issue:** #858 - Fix F841 unused variables (44 errors)  
**Status:** ✅ Pinged on issue  
**Activation Method:** GitHub issue comment

**Already Done:**
```
Commented on issue #858 with @jules mention
```

**Alternative Activation:**
- Visit: https://jules.google.com/
- Sign in with Google account that has API key
- Create task pointing to issue #858
- Jules will create PR automatically

**API Key Location:** `x-goog-api-key` or similar in Google Cloud Console

---

### 2. Gemini Code Assist (@gemini-code-assist)

**Issue:** #857 - Fix syntax in bridge/ + core/consciousness/  
**Status:** ⏳ Awaiting activation  
**Activation Method:** Google Cloud CLI or IDE extension

**Manual Activation:**

**Option A: Via Google Cloud Console**
```bash
# If you have gcloud CLI configured
gcloud auth login
# Then trigger via Gemini API
```

**Option B: Via IDE (VS Code/IntelliJ)**
- Install "Gemini Code Assist" extension
- Point extension to issue #857
- Let Gemini read commands and execute

**Option C: Manual execution (if Gemini unavailable)**
```bash
# You can run the commands yourself:
black bridge/ core/consciousness/
python3 -m ruff check --select E999 bridge/ core/consciousness/
make smoke
```

---

### 3. GitHub Copilot (@github-copilot)

**Issue:** #859 - Resolve PR #805 M1 conflicts  
**Status:** ⏳ Awaiting activation  
**Activation Method:** GitHub CLI or web interface

**Activation via GitHub CLI:**
```bash
# Check if Copilot CLI is available
gh copilot --version

# If available, you can ask Copilot for help:
gh copilot suggest "resolve conflicts in PR #805"
```

**Alternative:** Manual resolution
- Checkout PR #805: `gh pr checkout 805`
- Rebase on main: `git rebase origin/main`
- Resolve conflicts using editor
- Follow guide: `docs/agents/GITHUB_COPILOT_M1_CONFLICTS_BRIEF.md`

---

### 4. Codex (@codex / ChatGPT)

**Issues:** 
- #848 - W293 whitespace [BLOCKED by syntax]
- #850 - SIM102 nested if [BLOCKED by syntax]
- #851 - E402 imports [BLOCKED by syntax]
- #852 - F821 undefined [BLOCKED by syntax]
- #860 - RUF012 mutable class attrs [READY]
- #861 - RUF006 async comprehensions [READY]

**Status:** ⏳ Awaiting activation (2 tasks ready, 4 blocked)  
**Activation Method:** ChatGPT with Codex integration

**How to Activate:**
1. Visit https://chatgpt.com/
2. Sign in to account with Codex access
3. Navigate to Codex dashboard
4. Point Codex to GitHub issues #860 and #861
5. Codex will create PRs automatically

**Alternative:** Check usage limits
- Visit: https://chatgpt.com/codex/settings/usage
- Verify limits haven't been reached
- If blocked, wait for reset or upgrade plan

**Note:** Issues #848-#852 are blocked until syntax errors are fixed (issue #855)

---

## 📋 Task Priority Order

### Immediate (Can Start Now)
1. ✅ **Jules #858** (15 min) - Already pinged
2. 🟡 **Codex #861** (20 min) - RUF006, not blocked
3. 🔴 **Gemini #857** (30-45 min) - P0 blocker fix

### After Syntax Fixed
4. **Codex #848** - W293 whitespace
5. **Codex #850** - SIM102 nested if
6. **Codex #851** - E402 imports
7. **Codex #852** - F821 undefined names

### Complex Tasks
8. **Codex #860** (2-3h) - RUF012 mutable class attrs
9. **Copilot #859** (2-3h) - PR #805 M1 conflicts

---

## 🚨 Blockers

### P0 Blocker: Syntax Errors
- **Issue:** #855
- **Impact:** Blocks Codex issues #848, #850, #851, #852
- **Resolution:** Gemini #857 + PR #829 (Black formatter)
- **Timeline:** 1-2 days

---

## 📊 Expected Outcomes

### After Quick Wins (Jules + Codex #861)
- **Errors fixed:** 124 (44 F841 + 80 RUF006)
- **Time:** ~35 minutes
- **New count:** 13,376 errors (18.3% reduction)

### After Gemini #857
- **Syntax errors fixed:** ~1,200 in 50 files
- **Impact:** Unblocks 4 Codex tasks
- **New count:** ~12,300 errors (24.8% reduction)

### After All Tasks Complete
- **Total errors fixed:** 2,514
- **New count:** 10,986 errors (33% reduction)
- **Milestone:** On track for 50% goal

---

## 🔑 API Keys & Access

### Jules (Google Labs)
- **Key Type:** `x-goog-api-key` or `api-goog`
- **Location:** Google Cloud Console → APIs & Services → Credentials
- **Docs:** https://jules.google.com/docs

### Gemini Code Assist
- **Key Type:** Google Cloud project credentials
- **Setup:** `gcloud auth application-default login`
- **Docs:** https://cloud.google.com/gemini/docs

### GitHub Copilot
- **Access:** GitHub subscription with Copilot enabled
- **Setup:** `gh extension install github/gh-copilot`
- **Docs:** https://docs.github.com/copilot

### Codex (ChatGPT)
- **Access:** ChatGPT Plus/Enterprise with Codex feature
- **Dashboard:** https://chatgpt.com/codex
- **Check limits:** https://chatgpt.com/codex/settings/usage

---

## 🎯 Manual Fallback

If any agent is unavailable, you can execute their tasks manually:

### Jules #858 (F841)
```bash
python3 -m ruff check --select F841 --fix .
make smoke
git add -A
git commit -m "fix(lint): remove unused variables (F841)"
```

### Codex #861 (RUF006)
```bash
python3 -m ruff check --select RUF006 --fix .
make smoke
git add -A
git commit -m "refactor(lint): remove unnecessary async comprehensions (RUF006)"
```

### Gemini #857 (Syntax)
```bash
black bridge/ core/consciousness/
make smoke
git add bridge/ core/consciousness/
git commit -m "fix(syntax): resolve indentation in bridge/ and core/consciousness/"
```

---

**Last Updated:** November 2, 2025  
**Campaign Tracker:** Issue #847

🤖 Guide by Claude Code
