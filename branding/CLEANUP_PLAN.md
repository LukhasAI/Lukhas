# 🧹 LUKHAS AI Branding Directory Cleanup Plan

## 🎯 Goal
Transform branding from 670 files to essential brand orchestration systems only.

## ✅ What to KEEP in /branding/
1. **Core Orchestration**:
   - `orchestration/` - Elite orchestrators and integrators
   - `engines/` - Unified content platform and doc engine
   
2. **Brand Management**:
   - `analysis/` - Voice coherence analyzer
   - `policy/` - Branding policies and terminology
   - `tone/` - 3-Layer Tone System
   
3. **Integration Systems**:
   - `automation/` - Brand automation
   - `enforcement/` - Real-time validation
   
4. **Essential Documentation**:
   - Brand reports and strategy files (top-level .md)

## 🗑️ What to REMOVE from /branding/
1. **Large Content Dumps**:
   - `content_engines/document_generation/` (research is in database)
   - `content_engines/lambda_bot_enterprise/` (consolidated to engines/)
   - `content_engines/lambda_web_manager/` (consolidated to engines/)
   
2. **Professional Assets**:
   - `professional_assets/` (move to project root)
   - `mobile_applications/` (move to project root)
   - `enterprise_systems/` (move to project root)
   
3. **Databases**:
   - `databases/` (moved to ../data/)

## 📦 Final Clean Structure
```
/branding/ (Brand Orchestration Only)
├── analysis/               ✅ Voice coherence tools
├── automation/             ✅ Brand automation  
├── enforcement/            ✅ Real-time validation
├── engines/                ✅ Unified platforms
├── orchestration/          ✅ System coordinators
├── policy/                 ✅ Brand policies
├── tone/                   ✅ 3-Layer Tone System
└── *.md                    ✅ Strategy documents
```

This reduces from 670 files to ~50 essential brand management files.