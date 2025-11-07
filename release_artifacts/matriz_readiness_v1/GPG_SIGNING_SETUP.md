# GPG Signing Key Setup Guide (Optional)

**Date:** 2025-11-03T14:05:00Z
**Purpose:** Configure GPG signing for commits and tags (optional for MATRIZ flattening)
**Status:** ⏳ OPTIONAL - Not required for dry-run or apply mode

---

## Why GPG Signing? (Optional)

GPG signing provides:
- **Cryptographic proof** of authorship for commits and tags
- **Trust verification** in open-source projects
- **GitHub verified badge** on signed commits

**For MATRIZ flattening:** Non-blocking - you can proceed without it.

---

## Quick Setup (5 minutes)

### Step 1: Check if GPG is installed

```bash
gpg --version
```

**If not installed:**
```bash
# macOS (Homebrew)
brew install gnupg

# Verify
gpg --version
```

---

### Step 2: Generate GPG key

```bash
gpg --full-generate-key
```

**Prompts:**
1. **Key type:** Choose `(1) RSA and RSA` (default)
2. **Key size:** Enter `4096` (stronger than default 3072)
3. **Expiration:** Enter `2y` (2 years) or `0` (never expires)
4. **Real name:** Enter your full name (e.g., "Gonzalo Roberto Dominguez Marchan")
5. **Email:** Use your GitHub email: `gonzalordm@users.noreply.github.com`
6. **Comment:** Optional (e.g., "LUKHAS AI Development")
7. **Passphrase:** Choose a secure passphrase (store in password manager)

**Output:**
```
gpg: key ABCD1234ABCD1234 marked as ultimately trusted
pub   rsa4096 2025-11-03 [SC] [expires: 2027-11-03]
      ABCD1234ABCD1234ABCD1234ABCD1234ABCD1234
uid                      Gonzalo Roberto Dominguez Marchan <gonzalordm@users.noreply.github.com>
sub   rsa4096 2025-11-03 [E] [expires: 2027-11-03]
```

**Save the key ID:** `ABCD1234ABCD1234` (first 16 characters after "key")

---

### Step 3: Configure Git to use GPG key

```bash
# Set your GPG key (replace with your key ID)
git config --global user.signingkey ABCD1234ABCD1234

# Enable automatic signing for all commits
git config --global commit.gpgsign true

# Enable automatic signing for all tags
git config --global tag.gpgsign true

# Verify configuration
git config --global user.signingkey
git config --global commit.gpgsign
git config --global tag.gpgsign
```

**Expected output:**
```
ABCD1234ABCD1234
true
true
```

---

### Step 4: Export public key and add to GitHub

```bash
# Export your GPG public key
gpg --armor --export gonzalordm@users.noreply.github.com > /tmp/gpg_public_key.asc

# Copy to clipboard (macOS)
cat /tmp/gpg_public_key.asc | pbcopy

# Or print to screen
cat /tmp/gpg_public_key.asc
```

**Add to GitHub:**
1. Go to: https://github.com/settings/keys
2. Click: **New GPG key**
3. Paste the public key (starts with `-----BEGIN PGP PUBLIC KEY BLOCK-----`)
4. Click: **Add GPG key**

---

### Step 5: Test signing

```bash
# Create a test signed commit
echo "test" > /tmp/test_signing.txt
git add /tmp/test_signing.txt
git commit -S -m "test: GPG signing verification"

# Verify signature
git log --show-signature -1

# Remove test file
git reset --soft HEAD~1
rm /tmp/test_signing.txt
```

**Expected output:**
```
gpg: Signature made Thu Nov  3 14:05:00 2025 UTC
gpg:                using RSA key ABCD1234ABCD1234
gpg: Good signature from "Gonzalo Roberto Dominguez Marchan <gonzalordm@users.noreply.github.com>" [ultimate]
```

---

## Troubleshooting

### Issue 1: `gpg: signing failed: Inappropriate ioctl for device`

**Fix:**
```bash
export GPG_TTY=$(tty)
echo 'export GPG_TTY=$(tty)' >> ~/.zshrc
source ~/.zshrc
```

### Issue 2: Passphrase prompt every time

**Fix (macOS):**
```bash
# Install pinentry-mac
brew install pinentry-mac

# Configure GPG to use it
echo "pinentry-program $(which pinentry-mac)" >> ~/.gnupg/gpg-agent.conf

# Restart GPG agent
gpgconf --kill gpg-agent
gpgconf --launch gpg-agent
```

### Issue 3: Git doesn't recognize GPG

**Fix:**
```bash
# Add GPG to PATH (if installed via Homebrew)
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Or tell Git where GPG is
git config --global gpg.program $(which gpg)
```

---

## Verifying GitHub Integration

After adding your GPG key to GitHub:

1. **Make a signed commit:**
   ```bash
   git commit --allow-empty -S -m "test: verify GPG signing"
   git push origin main
   ```

2. **Check on GitHub:**
   - Go to your commit on GitHub
   - Look for green **"Verified"** badge next to commit

3. **Clean up test commit:**
   ```bash
   git reset --hard HEAD~1
   git push --force origin main
   ```

---

## For MATRIZ Flattening

### Without GPG Signing (Current State)
```bash
# Commits work fine without signing
git commit -m "refactor(matriz): flatten memory_node.py"
git push origin main
```

### With GPG Signing (Optional)
```bash
# Commits include cryptographic signature
git commit -S -m "refactor(matriz): flatten memory_node.py"
git push origin main
```

**Both are valid for MATRIZ flattening campaign.**

---

## Quick Reference

### List GPG keys
```bash
gpg --list-secret-keys --keyid-format LONG
```

### Export public key
```bash
gpg --armor --export YOUR_KEY_ID
```

### Export private key (backup)
```bash
gpg --armor --export-secret-keys YOUR_KEY_ID > /secure/location/private_key.asc
```

### Import key (restore from backup)
```bash
gpg --import /secure/location/private_key.asc
```

### Delete key
```bash
gpg --delete-secret-keys YOUR_KEY_ID
gpg --delete-keys YOUR_KEY_ID
```

---

## Security Best Practices

1. **Passphrase:** Use a strong passphrase (20+ characters)
2. **Backup:** Export and store private key securely (encrypted USB, password manager)
3. **Expiration:** Set 2-year expiration, extend if needed
4. **Revocation:** Create revocation certificate: `gpg --gen-revoke YOUR_KEY_ID`
5. **Multiple Devices:** Export and import keys to each development machine

---

## Status for MATRIZ Flattening

- **Current:** No GPG key configured
- **Impact:** ⏳ NONE - Commits and tags work without signing
- **Recommendation:** ⏳ OPTIONAL - Set up after GPT-Pro audit if desired
- **Timeline:** 5 minutes setup + 2 minutes GitHub integration

---

**Document Created:** 2025-11-03T14:05:00Z
**Author:** Claude Code (T4 Agent)
**Purpose:** Optional GPG setup guide (non-blocking for MATRIZ flattening)
