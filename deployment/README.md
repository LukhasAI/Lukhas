# 🚀 LUKHAS AI Deployment Infrastructure

This directory contains all deployment-related files for the LUKHAS AI consciousness development platform.

## 📁 Directory Structure

### **Deployment Scripts (`scripts/`)**
- `deploy.sh` - Main deployment script
- `deploy-fresh.sh` - Fresh environment deployment
- `setup_newrelic.sh` - New Relic APM setup
- `migrate_web_projects.sh` - Web project migration utility

### **Docker Infrastructure (`docker/`)**
- `Dockerfile` - Main container build configuration
- `docker-compose.yml` - Multi-container orchestration

### **Cloud Deployments (`cloud/`)**
- `azure-container-app.yaml` - Azure Container Apps configuration
- `azure-production-deploy.yml` - Azure production pipeline

## 🚀 Deployment Workflows

### **Local Development**
```bash
# Build and run locally
cd deployment/docker/
docker-compose up -d

# Fresh deployment
cd deployment/scripts/
./deploy-fresh.sh
```

### **Production Deployment**
```bash
# Azure deployment
cd deployment/cloud/
az deployment group create --resource-group lukhas-ai \
  --template-file azure-container-app.yaml

# With monitoring
cd deployment/scripts/
./setup_newrelic.sh
./deploy.sh production
```

## 🏗️ Infrastructure Standards

### **Container Standards**
- ✅ Multi-stage Docker builds for optimization
- ✅ Security scanning before deployment
- ✅ Health checks and monitoring
- ✅ Resource limits and scaling rules

### **Cloud Deployment Principles**
- 🌍 Infrastructure as Code (IaC)
- 🔒 Zero-trust security model
- 📊 Comprehensive monitoring and logging
- 🔄 Automated rollback capabilities

---

**Professional deployment infrastructure - Consolidated August 2025**
