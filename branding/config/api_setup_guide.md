---
status: wip
type: documentation
---
# 🔌 LUKHAS AI Platform API Setup Guide

Complete guide for configuring live social media platform integrations.

## 🚀 Quick Setup

### 1. Environment Variables (Recommended)

Create a `.env` file in your project root:

```bash
# Twitter/𝕏 API v2 (https://developer.twitter.com)
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
TWITTER_BEARER_TOKEN=your_bearer_token_here

# LinkedIn API (https://www.linkedin.com/developers/)
LINKEDIN_CLIENT_ID=your_client_id_here
LINKEDIN_CLIENT_SECRET=your_client_secret_here
LINKEDIN_ACCESS_TOKEN=your_access_token_here

# Reddit API (https://www.reddit.com/prefs/apps)
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password

# Instagram Basic Display API (https://developers.facebook.com)
INSTAGRAM_ACCESS_TOKEN=your_access_token_here
INSTAGRAM_CLIENT_ID=your_client_id_here
INSTAGRAM_CLIENT_SECRET=your_client_secret_here
```

### 2. Install Required Dependencies

```bash
pip install tweepy praw aiohttp requests-oauthlib
```

## 📋 Platform-Specific Setup Instructions

### 🐦 Twitter/𝕏 API v2

1. **Create Developer Account**
   - Visit https://developer.twitter.com
   - Apply for a developer account
   - Create a new project/app

2. **Generate Keys**
   - API Key & Secret (Consumer Keys)
   - Access Token & Secret
   - Bearer Token

3. **Required Permissions**
   - Read and Write tweets
   - Upload media (for images)

### 💼 LinkedIn API

1. **Create LinkedIn App**
   - Visit https://www.linkedin.com/developers/
   - Create a new app
   - Request "Marketing Developer Platform" access

2. **OAuth 2.0 Setup**
   - Configure redirect URIs
   - Generate access token via OAuth flow
   - Required scopes: `w_member_social`, `r_liteprofile`

3. **Note**: LinkedIn requires verification for posting to company pages

### 🤖 Reddit API

1. **Create Reddit App**
   - Visit https://www.reddit.com/prefs/apps
   - Create a "script" type application
   - Note your client ID and secret

2. **User Authentication**
   - Use your Reddit username and password
   - For production, consider OAuth flow

3. **Rate Limits**
   - 60 requests per minute
   - Be respectful of Reddit's community guidelines

### 📸 Instagram Basic Display API

1. **Facebook Developer Setup**
   - Visit https://developers.facebook.com
   - Create a new app
   - Add Instagram Basic Display product

2. **Instagram Business Account Required**
   - Convert personal Instagram to business account
   - Connect to Facebook Page

3. **Graph API for Publishing**
   - Publishing requires Instagram Content Publishing API
   - Requires app review from Facebook

## 🔐 Security Best Practices

### Environment Variables
```bash
# Never commit these to git!
echo "*.env" >> .gitignore
echo "branding/config/api_credentials.json" >> .gitignore
```

### Credential Rotation
- Rotate API keys monthly
- Use separate keys for development/production
- Monitor API usage for unusual activity

### Rate Limiting
- All platforms implement automatic rate limiting
- Twitter: 300 requests per 15 minutes
- LinkedIn: 100 requests per hour
- Reddit: 60 requests per hour
- Instagram: 200 requests per hour

## ⚡ Production Deployment

### Azure Container Apps (Recommended)

```yaml
# container-apps-environment.yaml
apiVersion: app/v1
kind: ContainerApp
metadata:
  name: lukhas-social-media
spec:
  template:
    containers:
    - name: lukhas-ai
      image: lukhas/social-media:latest
      env:
      - name: TWITTER_API_KEY
        secretRef: twitter-api-key
      - name: LINKEDIN_CLIENT_ID
        secretRef: linkedin-client-id
      # ... other environment variables
```

### Docker Deployment

```dockerfile
# Use in Dockerfile
ENV TWITTER_API_KEY=""
ENV LINKEDIN_CLIENT_ID=""
# etc...

# Or use docker-compose.yml with .env file
```

## 🧪 Testing Your Setup

Run the test script:

```bash
cd branding/apis
python platform_integrations.py
```

Expected output:
```
🔌 LUKHAS AI Platform API Integrations
========================================

📊 Platform Status:
   Twitter: Creds ✅ | Client ✅ | Library ✅
   Linkedin: Creds ✅ | Client ✅ | Library ✅
   Reddit: Creds ✅ | Client ✅ | Library ✅
   Instagram: Creds ⚠️ | Client ⚠️ | Library ✅

🧪 Testing twitter posting...
✅ twitter posting successful: https://twitter.com/username/status/123456789
```

## 📊 Monitoring & Analytics

### Platform Analytics Integration

```python
# Built-in analytics tracking
analytics = orchestrator.get_content_analytics()
print(f"Posts published: {analytics['published_content']}")
print(f"Engagement rate: {analytics.get('engagement_rate', 'N/A')}")
```

### Error Monitoring

```python
# Automatic error logging and recovery
result = await api_manager.post_content("twitter", content)
if not result.success:
    logger.error(f"Failed to post: {result.error}")
    # Automatic retry logic built-in
```

## 🚨 Troubleshooting

### Common Issues

1. **"Rate limit exceeded"**
   - Wait for rate limit reset
   - Reduce posting frequency
   - Check rate limit status: `api_manager.get_platform_status()`

2. **"Invalid credentials"**
   - Verify API keys are correct
   - Check token expiration
   - Ensure proper permissions/scopes

3. **"Content rejected"**
   - Check platform content policies
   - Verify character limits
   - Ensure media files are valid formats

### Debug Mode

```python
# Enable detailed logging
import logging
logging.getLogger("LUKHAS_Platform_APIs").setLevel(logging.DEBUG)
```

## 🎯 Ready for Production?

✅ **Requirements Checklist:**
- [ ] All API credentials configured
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Test posting successful
- [ ] Rate limiting configured
- [ ] Error handling tested
- [ ] Content quality validation passing
- [ ] Monitoring/alerting setup

## 🆘 Support

- **Documentation**: See `/branding/apis/platform_integrations.py`
- **Logs**: Check `/branding/logs/platform_apis_*.log`
- **Issues**: Monitor rate limits and error responses

---

⚛️🧠🛡️ **LUKHAS AI Platform Integration**
*Consciousness technology meets social media automation*
