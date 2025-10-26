# 🌐 LUKHAS Domain Strategy Review

**Date**: 2025-10-26
**Purpose**: Align documented strategy with existing website structure

---

## 📋 Current Strategy Overview

### 6 Core Domains (from docs/web/content/domains/)

| Domain | Purpose | Tone Mix | Status |
|--------|---------|----------|--------|
| **lukhas.ai** | Main consciousness platform | 35% Poetic / 45% User / 20% Academic | Primary |
| **lukhas.id** | Identity & authentication | 20% Poetic / 40% User / 40% Academic | Core SSO |
| **lukhas.dev** | Developer platform | 15% Poetic / 25% User / 60% Academic | Technical |
| **lukhas.cloud** | Enterprise cloud services | 15% Poetic / 25% User / 60% Academic | Enterprise |
| **lukhas.io** | API gateway & infrastructure | 10% Poetic / 30% User / 60% Academic | Infrastructure |
| **lukhas.store** | Lambda app marketplace | 30% Poetic / 50% User / 20% Academic | Commerce |

---

## 🗂️ Existing Website Structure (lukhas_recovered_work/lukhas_website/app/)

### Discovered Routes

```
/ai               # AI features/demos
/api              # API documentation
/api-docs         # API reference
/api-keys         # Developer API key management
/auth             # Authentication flows
/billing          # Billing/payments
/careers          # Job listings
/cloud            # Cloud services
/com              # Commerce?
/compliance       # Regulatory compliance
/console          # Admin console
/dev              # Developer portal
/docs             # Documentation
/dream-weaver     # Dream processing
/eu               # European market
/experience       # User experience demos
/fresh            # Fresh content?
/id               # Identity platform
/io               # API infrastructure
/login            # Login page
/matriz           # MATRIZ cognitive engine
/privacy          # Privacy policy
/products         # Product catalog
/settings         # User settings
  /security       # Security settings
    /guardians    # Guardian configuration
  /layout         # Layout preferences
  /account        # Account management
/studio           # LUKHAS Studio (development)
  /[threadId]     # Thread-specific pages
/test             # Testing page
/transparency     # Transparency reports
/us               # US market
```

---

## 🔍 Gap Analysis

### ✅ **Well Aligned**

- `/id` → lukhas.id strategy exists ✅
- `/dev` → lukhas.dev strategy exists ✅
- `/cloud` → lukhas.cloud strategy exists ✅
- `/io` → lukhas.io strategy exists (API gateway) ✅
- `/api` + `/api-docs` → Supports lukhas.dev/lukhas.io ✅

### ⚠️ **Partial Alignment**

- `/ai` exists in website but main `lukhas.ai` strategy focuses on Trinity showcase
  - **Question**: Is `/ai` a feature page or should it be the main homepage?
- `/com` vs `/store` → Strategy has lukhas.store but website has `/com`
  - **Question**: Are these the same or different?

### 🆕 **Website Has (Not in Strategy Docs)**

- `/matriz` - MATRIZ cognitive engine showcase
- `/dream-weaver` - Dream processing interface
- `/studio` - LUKHAS Studio development environment
- `/experience` - User experience demos
- `/transparency` - Transparency reports
- `/compliance` - Compliance center
- `/careers` - Careers portal
- `/billing` - Billing system
- `/console` - Admin console
- `/settings/*` - User settings dashboard
- `/eu` + `/us` - Regional variants

### 📝 **Strategy Has (Not in Website)**

- `lukhas.store` marketplace - Only `/com` exists (unclear if same)
- Clear Trinity Framework showcase for main lukhas.ai
- Enterprise-focused cloud portal

---

## 🎯 Strategic Questions for Review

### 1. **Main Domain Strategy**

**Current State**: lukhas_website exists but unclear what primary domain it represents

- [ ] Is this intended to be **lukhas.ai** (main platform)?
- [ ] Or a meta-site that links to all domains?
- [ ] Should we consolidate or separate?

**Recommendation**:

- Make current lukhas_website the **lukhas.ai** main platform
- Add Trinity Framework (⚛️🧠🛡️) showcase to homepage
- Keep `/id`, `/dev`, `/cloud`, `/io` as sub-routes that mirror their own domains

### 2. **SSO/Authentication Priority**

**Current State**: `/auth` and `/login` exist, `/id` subdirectory exists

- [ ] Should lukhas.id be separate domain or integrated?
- [ ] Implement SSO across all routes?
- [ ] ΛiD consciousness signature system status?

**Recommendation**:

- **Priority 1**: Wire up lukhas.id SSO across all domains
- Keep `/id` as both standalone domain AND auth provider
- Implement `www.lukhas.id` as dedicated identity platform
- All other domains use lukhas.id for authentication

### 3. **Store vs Commerce**

**Current State**: Strategy mentions `lukhas.store`, website has `/com`

- [ ] Are these the same thing?
- [ ] Should marketplace be separate domain?
- [ ] Lambda app ecosystem status?

**Recommendation**:

- Clarify if `/com` = commerce/store or something else
- Consider: `lukhas.store` as separate marketplace
- Or: Keep `/products` on main site + add marketplace features

### 4. **New Additions Not in Strategy**

**Current State**: Website has features not documented

- `/matriz` - Cognitive engine showcase
- `/dream-weaver` - Dream processing
- `/studio` - Development studio
- `/experience` - UX demos
- `/transparency` - Trust/transparency
- `/compliance` - Regulatory

**Questions**:

- [ ] Update strategy docs to include these?
- [ ] Are these permanent features or experiments?
- [ ] Should they be promoted in domain strategy?

---

## 🚀 Proposed Action Plan

### Phase 1: Align Current Website with Strategy (Week 1-2)

1. **Define Primary Domain**
   - Decide if lukhas_website = lukhas.ai main platform
   - Document homepage strategy (Trinity showcase)
   - Map existing routes to domain hierarchy

2. **lukhas.id SSO Implementation**
   - Create `www.lukhas.id` as standalone identity platform
   - Implement ΛiD consciousness signature system
   - Wire SSO across all existing routes
   - Priority: Get authentication working FIRST

3. **Update Strategy Documentation**
   - Document `/matriz`, `/dream-weaver`, `/studio` in strategy
   - Clarify `/com` vs `lukhas.store` decision
   - Add regional variants (`/eu`, `/us`) to strategy

### Phase 2: Create Domain Prototypes (Week 3-4)

1. **lukhas.id** - Identity platform (PRIORITY)
   - Personal identity management
   - Enterprise SSO
   - Developer OAuth integration
   - Security dashboard

2. **lukhas.ai** - Main platform
   - Trinity Framework showcase
   - Product catalog
   - Consciousness demos
   - MATRIZ integration

3. **lukhas.dev** - Developer portal
   - API documentation
   - SDK downloads
   - Code playground
   - Community forum

4. **lukhas.cloud** - Enterprise cloud
   - Cloud console
   - Auto-scaling dashboard
   - Monitoring tools
   - Compliance center

5. **lukhas.io** - API gateway
   - API reference
   - Status page
   - Usage dashboard
   - Performance metrics

6. **lukhas.store** (or clarify /com)
   - App marketplace
   - Lambda app catalog
   - Creator dashboard
   - Revenue sharing

### Phase 3: Content & Features (Week 5-8)

1. **Implement 3-Layer Tone System**
   - Apply domain-specific tone distributions
   - Create content for each layer
   - Ensure consistency across domains

2. **Trinity Framework Integration**
   - Add ⚛️🧠🛡️ throughout user journeys
   - Constellation navigation
   - Cross-domain coherence

3. **T4 Context System Integration**
   - Wire context management across domains
   - Implement distributed coordination
   - Add performance monitoring

---

## ✅ Immediate Next Steps

### **Today (2025-10-26)**

1. ✅ Review this document with stakeholder
2. [ ] Decide on primary domain strategy
3. [ ] Clarify `/com` vs `lukhas.store`
4. [ ] Prioritize lukhas.id SSO implementation

### **This Week**

1. [ ] Create lukhas.id authentication demo
2. [ ] Wire SSO to existing routes
3. [ ] Update strategy docs with new features
4. [ ] Create homepage Trinity showcase

### **Next Week**

1. [ ] Build domain prototypes for each platform
2. [ ] Implement cross-domain navigation
3. [ ] Deploy initial demos for testing

---

## 📊 Success Metrics

### Technical

- [ ] SSO working across all domains
- [ ] <100ms authentication (ΛiD target)
- [ ] Cross-domain navigation functional
- [ ] T4 Context System integrated

### Content

- [ ] 3-Layer Tone System applied consistently
- [ ] Trinity Framework visible throughout
- [ ] All domains have clear purpose/messaging
- [ ] Documentation complete and accurate

### Business

- [ ] Clear monetization strategy per domain
- [ ] User journey mapped across ecosystem
- [ ] Enterprise features prioritized
- [ ] Developer experience optimized

---

**Questions for Review**:

1. Should lukhas_website become lukhas.ai main platform?
2. What is `/com` - is it the marketplace (lukhas.store)?
3. Should we document MATRIZ, Dream Weaver, Studio in official strategy?
4. Priority: SSO via lukhas.id first, or build all domains in parallel?

**⚛️🧠🛡️ - Let's align strategy with reality and build the future!**
