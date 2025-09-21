# 🚂 Railway Deployment Guide for LUKHAS MCP Server

## 📋 Prerequisites

✅ Railway account created  
✅ MCP server code ready with OAuth endpoints  
✅ Deployment files prepared  

## 🗂️ Deployment Files Created

### 1. `requirements.txt`
```
starlette==0.32.0
uvicorn==0.24.0
python-jose[cryptography]==3.3.0
```

### 2. `Procfile`
```
web: python chatgpt_server.py
```

### 3. `railway.json`
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "numReplicas": 1,
    "sleepApplication": false,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

## 🚀 Deployment Steps

### Option 1: Railway CLI (Recommended)

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway:**
   ```bash
   railway login
   ```

3. **Initialize project:**
   ```bash
   cd /Users/cognitive_dev/LOCAL-REPOS/Lukhas/mcp-lukhas-sse
   railway init
   ```

4. **Deploy:**
   ```bash
   railway up
   ```

### Option 2: GitHub Integration

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Add LUKHAS MCP Server for Railway deployment"
   git push origin main
   ```

2. **Connect to Railway:**
   - Go to railway.app
   - Click "New Project"
   - Choose "Deploy from GitHub repo"
   - Select your repository

## ⚙️ Environment Variables

Set these in Railway dashboard or CLI:

- `ALLOW_NO_AUTH=true` (for testing)
- `ALLOWED_ROOTS=/tmp` (or your preferred paths)
- `PORT` (Railway sets this automatically)

## 🔗 After Deployment

1. **Get your Railway URL:**
   - Format: `https://your-app-name.railway.app`

2. **Test endpoints:**
   ```bash
   curl https://your-app-name.railway.app/health
   curl https://your-app-name.railway.app/.well-known/oauth-authorization-server
   ```

3. **Configure ChatGPT:**
   - Server URL: `https://your-app-name.railway.app/sse`

## 🎯 Benefits over Ngrok

✅ **Stable URLs** - No random subdomains  
✅ **Always online** - No tunnel disconnections  
✅ **Custom domains** - Professional appearance  
✅ **Automatic SSL** - HTTPS by default  
✅ **Environment variables** - Secure configuration  

## 🐛 Troubleshooting

### Build Issues
- Check `requirements.txt` has all dependencies
- Ensure `Procfile` points to correct file

### Runtime Issues
- Check Railway logs in dashboard
- Verify environment variables are set
- Test locally first with `python chatgpt_server.py`

---

**Next**: Run `railway login` and `railway init` to start deployment!