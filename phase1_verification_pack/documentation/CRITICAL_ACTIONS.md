# CRITICAL ACTIONS REQUIRED

## 🚨 IMMEDIATE: Rotate Exposed API Keys

The following API keys were previously exposed in the repository and MUST be rotated immediately:

### 1. OpenAI API Key
- **Provider**: https://platform.openai.com/api-keys
- **Action**:
  1. Log into OpenAI platform
  2. Revoke the exposed key starting with `sk-proj-m2WLTymv8xlc...`
  3. Generate new API key
  4. Update local .env file (NOT .env.example)

### 2. Anthropic API Key
- **Provider**: https://console.anthropic.com/
- **Action**:
  1. Log into Anthropic Console
  2. Revoke the exposed key starting with `sk-ant-api03-38V9ev3p...`
  3. Generate new API key
  4. Update local .env file

### 3. Google API Key
- **Provider**: https://console.cloud.google.com/
- **Action**:
  1. Log into Google Cloud Console
  2. Revoke the exposed key starting with `AIzaSyCCbG4p4HlK...`
  3. Generate new API key
  4. Update local .env file

### 4. Perplexity API Key
- **Provider**: https://www.perplexity.ai/settings/api
- **Action**:
  1. Log into Perplexity settings
  2. Revoke the exposed key starting with `pplx-qoQPJ2agcoK0...`
  3. Generate new API key
  4. Update local .env file

## ⚠️ Security Best Practices

### Never Commit Secrets
- ✅ .env is in .gitignore
- ✅ Use .env.example for templates
- ✅ All real keys in local .env only

### Verify Security
```bash
# Check no secrets in git
git log --all -- .env
# Should return nothing

# Check .env is ignored
git status --ignored | grep .env
# Should show .env as ignored
```

## 📋 Post-Rotation Checklist

- [ ] OpenAI key rotated and updated locally
- [ ] Anthropic key rotated and updated locally
- [ ] Google key rotated and updated locally
- [ ] Perplexity key rotated and updated locally
- [ ] Test new keys work:
  ```bash
  python3 -c "import os; print('Keys loaded' if os.getenv('OPENAI_API_KEY') else 'No keys')"
  ```
- [ ] Old keys confirmed revoked at providers
- [ ] Team notified of rotation

## 🔒 Prevention

The following measures are now in place to prevent future exposure:
1. **.env in .gitignore**: Prevents accidental commits
2. **AST acceptance gate**: Catches security issues
3. **CI/CD checks**: Validates no secrets in code
4. **.env.example**: Safe template without real keys
5. **Dry-run mode default**: No API calls without explicit enablement

## Timeline

**IMMEDIATE**: Complete key rotation within 24 hours of receiving this document.

**Why Critical**: Exposed keys can be scraped by bots and used for unauthorized access, potentially incurring costs or accessing private data.

## Confirmation

After rotating all keys, update this section:

```
Rotation Completed: [DATE]
Completed By: [NAME]
All Keys Verified Working: [YES/NO]
```

---

**This is the most critical action from Phase 1. Do not proceed to Phase 3 until all keys are rotated.**
