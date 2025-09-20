# LUKHAS AI - Agent Navigation Guide

**Comprehensive Directory Structure & Component Location Guide for AI Agents**

![Navigation Guide](https://img.shields.io/badge/Guide-Agent_Navigation-blue)
![Updated](https://img.shields.io/badge/Updated-August_2024-green)
![Components](https://img.shields.io/badge/Components-Mapped-brightgreen)

---

## 🎯 **QUICK REFERENCE FOR AI AGENTS**

This guide provides comprehensive navigation for AI agents working within the LUKHAS ecosystem. All paths are relative to the root workspace `/Users/agi_dev/LOCAL-REPOS/Lukhas/`.

---

## 📁 **LUKHAS WEBSITE (`/lukhas_website/`)**

### **Primary Application Structure**
```
lukhas_website/
├── README.md                    # Complete UI implementation guide
├── app/                        # Next.js 14 App Router
│   ├── globals.css             # Glass morphism theme system
│   ├── layout.tsx              # Root layout with providers
│   ├── page.tsx               # Landing page
│   └── studio/                # Main workspace
│       ├── layout.tsx         # Studio layout with mode system
│       ├── page.tsx           # Studio homepage
│       └── [threadId]/        # Dynamic thread pages
├── components/                # 50+ React components
├── packages/                  # SDK modules
└── tests/                     # Test suites (configuration in progress)
```

### **Core UI Components (`/components/`)**

#### **Recently Implemented (August 2024)**
- **`mode-context.tsx`**: Context provider for Email/Doc/Code/Message modes
- **`mode-chips.tsx`**: Mode selection interface with Lucide icons
- **`mode-toolbar.tsx`**: Dynamic toolbars that adapt to selected mode
- **`agent-palette.tsx`**: Command palette with performance timing
- **`settings-tabs.tsx`**: Tabbed settings interface (Privacy/Connectors/Wallet)
- **`empty-canvas.tsx`**: Professional empty states with CTAs

#### **UI Framework Components**
- **`model-dock.tsx`**: AI model selection with status indicators
- **`widget-rail.tsx`**: Sidebar widget system with tier access
- **`settings-modal.tsx`**: Modal system with glass morphism
- **`neural-background.tsx`**: Animated particle background system
- **`theme.ts`**: Centralized theme configuration

#### **Settings System (`/components/settings/`)**
- **`privacy.tsx`**: Privacy settings with consent toggles
- **`connectors.tsx`**: External service integration (Gmail, Drive, Slack)
- **`wallet.tsx`**: Wallet and token tier management
- **`texts.ts`**: Localized setting descriptions

### **SDK Packages (`/packages/`)**
- **`sdk-consent/`**: Consent management system
- **`sdk-identity/`**: Identity & authentication SDK
- **`sdk-qrg/`**: Quantum-Resistant Governance SDK
- **`sdk-wallet/`**: Wallet & token management SDK
- **`agent-commands/`**: Agent command system
- **`orchestrator/`**: Multi-AI orchestration

### **API Routes (`/app/api/`)**
```
api/
├── auth/                      # Authentication endpoints
│   ├── challenge/create/      # WebAuthn challenge generation
│   ├── passkey/authenticate/  # Passkey authentication
│   └── sso/oidc/             # Single Sign-On integration
├── qrg/                      # Quantum-Resistant Governance
│   ├── create/               # QRG creation endpoint
│   └── verify/               # QRG verification endpoint
├── nias/                     # Neural Intelligence Architecture
│   ├── replay/               # NIAS replay functionality
│   └── validate/             # NIAS validation endpoint
├── dast/                     # Distributed Application Security
│   └── route/                # DAST route security testing
└── wallet/                   # Wallet management
    └── pass/issue/           # Digital pass issuance
```

---

## 🧠 **CORE LUKHAS SYSTEMS (Root Workspace)**

### **Identity & Authentication (`/identity/`)**
```
identity/
├── README.md                  # Identity system overview
├── core.py                   # Core identity functionality
├── identity_core.py          # ΛID system implementation
├── webauthn_bootstrap.py     # WebAuthn/Passkey setup
├── auth/                     # Authentication modules
│   ├── cognitive_sync_adapter/
│   ├── cultural_profile_manager/
│   └── entropy_synchronizer/
├── email_templates/          # Email template system
├── enterprise/               # Enterprise authentication
├── qrg_test_suite/          # QRG testing framework
└── vault/                    # Secure storage systems
```

### **QRG (Quantum-Resistant Governance) Locations**
- **Primary**: `/candidate/governance/identity/qrg_schemas/`
- **Core Implementation**: `/candidate/governance/identity/core/qrg/`
- **Website Integration**: `/lukhas_website/app/qrg/` & `/lukhas_website/packages/sdk-qrg/`
- **API Endpoints**: `/lukhas_website/app/api/qrg/`
- **Assets**: `/candidate/governance/identity/assets/qrg-quantum/`
- **Test Suites**: `/identity/qrg_test_suite/`, `/identity/qrg_coverage_integration/`

### **NIAS (Neural Intelligence Architecture System) Locations**
- **Primary Architecture**: `/candidate/core/architectures/nias/`
- **Core Engine**: `/candidate/core/architectures/nias/core/nias_engine.py`
- **Integration Hub**: `/candidate/core/architectures/nias/integration/nias_integration_hub.py`
- **Modules**: `/candidate/core/modules/nias/`
- **Interfaces**: `/candidate/core/interfaces/nias/`
- **Documentation**: `/candidate/core/interfaces/nias/NIAS_Plan.md`
- **Website Integration**: `/lukhas_website/app/api/nias/`

### **DAST (Distributed Application Security Testing) Locations**
- **Primary Architecture**: `/candidate/core/architectures/dast/`
- **Security Orchestration**: `/candidate/core/orchestration/security/dast/`
- **Core Orchestrator**: `/candidate/core/orchestration/security/dast_orchestrator.py`
- **Symbolic Engine**: `/candidate/core/symbolic/dast_engine.py`
- **Agent System**: `/candidate/core/interfaces/as_agent/sys/dast/`
- **Website Integration**: `/lukhas_website/app/api/dast/`

### **Governance & Guardian System (`/governance/`)**
```
governance/
├── README.md                 # Guardian System v1.0.0 overview
├── engine.py                 # Core governance engine
├── ethics/                   # Multi-tiered policy engines (86 components)
├── compliance/               # Regulatory compliance (12 modules)
├── audit_ethics_monitor.py  # Continuous monitoring
├── constitutional_ai.py     # Constitutional AI principles
├── ethical_guardian.py      # Guardian oversight system
└── [280+ additional files]  # Comprehensive safety framework
```

### **Consciousness Systems**
```
consciousness/
├── README.md                 # Consciousness system overview
├── unified/                  # Unified consciousness processing
├── auto_consciousness.py     # Automated consciousness functions
└── [consciousness modules]

vivox/                        # VIVOX consciousness system
├── README.md                 # VIVOX documentation
├── core/                     # ME, MAE, CIL, SRM components
└── integration/              # System integration

memory/                       # Fold-based memory architecture
├── README.md                 # Memory system documentation
├── fold_management.py        # Memory fold operations
└── persistence/              # Memory persistence systems
```

### **Core Processing Systems**
```
core/
├── README.md                 # Core system overview
├── glyph.py                 # GLYPH symbolic processing engine
├── symbolic/                # Symbolic logic systems
├── actor/                   # Actor model implementation
├── integration/             # System integration hubs
└── utilities/               # Core utility functions

orchestration/
├── README.md                # Orchestration system overview
├── brain/                   # Brain integration systems
├── primary_hub.py           # Central processing hub
└── symbolic_kernel_bus.py   # Event routing system

bridge/
├── README.md                # External API bridge overview
├── openai_client.py         # OpenAI API integration
├── anthropic_client.py      # Anthropic API integration
└── google_client.py         # Google Gemini integration
```

---

## 🎖️ **AGENT SYSTEMS & DEPLOYMENT**

### **Agent Configurations (`/agents/`)**
```
agents/
├── AGENT_CONFIGURATION_SUMMARY.md
├── supreme_consciousness_architect_config.json    # Tier 1 General
├── guardian_system_commander_config.json          # Tier 1 General
├── identity_quantum_general_config.json           # Tier 1 General
├── memory_systems_colonel_config.json             # Tier 2 Colonel
├── [15+ additional agent configs]                 # Multi-tier structure
```

### **Claude Army Deployment (`/CLAUDE_ARMY/`)**
```
CLAUDE_ARMY/
├── README.md                               # Agent army overview
├── deploy_claude_max_6_agents.sh          # Core deployment script
├── GPT5_README.md                          # GPT-5 integration guide
├── LUKHAS_Supreme_Claude_Army_Structure.md # Army structure documentation
└── [deployment configurations]             # Agent coordination setup
```

---

## 🔧 **DEVELOPMENT & CONFIGURATION**

### **Configuration Files**
```
config/
├── README.md                    # Configuration overview
├── lukhas_config.yaml          # Main system configuration
├── agent_orchestration.json   # Agent coordination settings
├── consciousness_config.json   # Consciousness module settings
├── integration_config.yaml    # Integration settings
└── [specialized configs]        # Module-specific configurations
```

### **Build & Deployment**
```
├── Makefile                    # Build automation
├── requirements.txt            # Python dependencies
├── package.json               # Node.js dependencies
├── docker-compose.yml         # Container orchestration
├── azure-container-app.yaml   # Azure deployment
└── .github/                   # CI/CD workflows
```

---

## 📊 **DATA & ANALYTICS**

### **System Data (`/data/`)**
```
data/
├── drift_audit_summary.json   # System drift analysis
├── identity_state.json        # Identity system state
├── memory_log.json            # Memory operation logs
├── glyph_map.json             # GLYPH symbolic mappings
└── test_results.json          # Test execution results
```

### **Monitoring & Analytics**
```
analytics/
├── README.md                   # Analytics overview

dashboard/
├── interpretability_dashboard.py  # System interpretability
└── launch_dashboard.sh           # Dashboard launcher
```

### **Development Tools & Dashboards (`/tools/`)**
```
tools/
├── dashboards/                 # Development dashboards (moved from /web/)
│   ├── README.md              # Dashboard documentation
│   ├── approver_ui.html       # Approval workflow interface
│   ├── cockpit.html           # System monitoring cockpit
│   ├── trace_drilldown.html   # Trace analysis visualization
│   └── provenance-client.js   # Provenance client functionality
└── analysis/                  # Analysis tools and utilities
```

---

## 🔒 **SECURITY & COMPLIANCE**

### **Guardian Audit System (`/guardian_audit/`)**
```
guardian_audit/
├── README.md                   # Audit system overview
└── [audit modules]             # Security monitoring
```

### **Security Validation**
- **Security Reports**: `/security_fix_report_20250822_030400.json`
- **Validation Logs**: `/security-validation-20250819-235823.log`
- **Compliance Framework**: Distributed across governance modules

---

## 📚 **DOCUMENTATION & GUIDES**

### **Primary Documentation (`/docs/`)**
```
docs/
├── README.md                   # Documentation index
├── ARCHITECTURE.md             # System architecture overview
├── API_REFERENCE.md           # API documentation
├── QUICK_START.md             # Getting started guide
├── MODULE_INDEX.md            # Complete module reference
├── TRANSPARENCY.md            # System capabilities/limitations
├── domain_strategy/           # Domain & web strategy docs (moved from /web_projects/)
│   ├── README.md              # Domain strategy overview
│   ├── LUKHAS_AI_DOMAIN_STRATEGY.md      # Main domain strategy
│   ├── LUKHAS_AI_WEBSITE_ARCHITECTURE.md # Website architecture
│   ├── LUKHAS_DESIGN_SYSTEM.md           # Design system specs
│   ├── COMPLETE_MONETIZATION_STRATEGY.md # Revenue planning
│   └── [additional strategy docs]         # Comprehensive planning
└── [100+ additional docs]      # Comprehensive documentation
```

### **Specialized Guides**
- **Agent Development**: `/AGENT_DEVELOPMENT_GUIDE.md`
- **Brand Guidelines**: `/branding/BRANDING_GUIDE.md`
- **Constellation Framework**: `/branding/CONSTELLATION_FRAMEWORK.md`
- **Testing Guide**: `/docs/TESTING_GUIDE.md`

---

## 🚀 **QUICK NAVIGATION FOR COMMON TASKS**

### **Working with LUKHAS Website**
- **Start Here**: `/lukhas_website/README.md`
- **Components**: `/lukhas_website/components/`
- **Add New Pages**: `/lukhas_website/app/`
- **API Endpoints**: `/lukhas_website/app/api/`
- **Settings**: `/lukhas_website/components/settings/`

### **Identity & Authentication Work**
- **Start Here**: `/identity/README.md`
- **Core System**: `/identity/identity_core.py`
- **WebAuthn**: `/identity/webauthn_bootstrap.py`
- **Email Templates**: `/identity/email_templates/`

### **QRG System Development**
- **Schemas**: `/candidate/governance/identity/qrg_schemas/`
- **Core Implementation**: `/candidate/governance/identity/core/qrg/`
- **API Integration**: `/lukhas_website/app/api/qrg/`

### **NIAS System Development**
- **Architecture**: `/candidate/core/architectures/nias/`
- **Core Engine**: `/candidate/core/architectures/nias/core/nias_engine.py`
- **API Integration**: `/lukhas_website/app/api/nias/`

### **Agent Configuration**
- **Agent Configs**: `/agents/`
- **Deployment**: `/CLAUDE_ARMY/deploy_claude_max_6_agents.sh`
- **Coordination**: `/config/agent_orchestration.json`

---

## 🎭 **SYSTEM STATUS REFERENCE**

### **Operational Status**
- **LUKHAS Website**: ✅ Production-ready UI, dev server running port 3000
- **Identity System**: ✅ WebAuthn/Passkey implementation complete
- **QRG**: ✅ Core implementation, API endpoints active
- **NIAS**: ✅ Architecture implemented, validation endpoints active
- **DAST**: ✅ Security testing framework operational
- **Agent Army**: ✅ 25 agents deployed and coordinated
- **Guardian System**: ✅ v1.0.0 active with 280+ safety modules

### **Known Issues**
- **Website Tests**: Jest configuration needs TypeScript transformation setup
- **Security Audit**: 30+ API keys in test metadata require cleanup
- **Memory Tests**: Core LUKHAS test suite needs completion

---

## 💡 **AGENT COLLABORATION TIPS**

### **For Testing Work**
- **All Tests**: Consolidated in `/tests/` directory
- **Test Data**: `/tests/data/` (consolidated from root test_data/)
- **Test Results**: `/tests/results/` (consolidated from root test_results/)
- **Test Metadata**: `/tests/metadata/` (consolidated from root test_metadata/)
- **Test Organization**: See `/tests/ORGANIZATION.md`

### **For UI/Frontend Work**
- Focus on `/lukhas_website/` directory
- All UI polish completed August 2024
- Mode system fully implemented with context awareness
- Glass morphism theme in `globals.css`

### **For Backend/API Work**
- API routes in `/lukhas_website/app/api/`
- Core systems in root directories (identity, governance, etc.)
- Configuration in `/config/`

### **For Development Tools & Monitoring**
- **Dashboards**: `/tools/dashboards/` (moved from root /web/)
- **Analysis Tools**: `/tools/analysis/`
- **Development Utilities**: Various tools throughout `/tools/`

### **For Agent Development**
- Agent configs in `/agents/`
- Deployment scripts in `/CLAUDE_ARMY/`
- Coordination settings in `/config/agent_orchestration.json`

### **For Documentation Work**
- Primary docs in `/docs/`
- Domain strategy in `/docs/domain_strategy/` (moved from root /web_projects/)
- Specialized guides at root level
- Component documentation in respective directories

---

**LUKHAS AI Agent Navigation Guide - Complete Directory Structure & Component Mapping**

*Navigate confidently through 200+ modules, 50+ components, and comprehensive system architecture*

## 🔄 **Recent Organization Changes (August 2024)**
- ✅ **Test Consolidation**: All root test directories consolidated into `/tests/` with organized subdirectories
- ✅ **Web Dashboards**: Development dashboards moved from `/web/` to `/tools/dashboards/`
- ✅ **Domain Strategy**: Web strategy docs moved from `/web_projects/` to `/docs/domain_strategy/`
- ✅ **Documentation**: Added organization guides and README files for all moved content

*Last updated: August 2024 - Post UI Polish & Directory Consolidation*
