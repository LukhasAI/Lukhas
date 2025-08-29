# LUKHAS AI - One-Page Architecture Diagram

## System Overview: TEQ-Governed Commerce Consciousness

```
                ┌─────────────────────────────────────────────────────┐
                │                    TEQ (Gov)                        │
                │ Transparency • DPIA • Model Cards • Audit Receipts  │
                │     Guardian System v1.0.0 (280+ validation)       │
                └─────────────────────────────────────────────────────┘
                                  ▲                 ▲
                                  │                 │ emits audit logs
                                  │                 │
     intent/search                 │          identity & payouts
 ┌─────────────────────────┐      │      ┌───────────────────────────┐
 │          DAST           │──────┼──────│        SIGIL / ΛID        │
 │ providers → Opportunity │      │      │ Consent, Identity, Wallet │
 │  (Claude/Multi-AI)      │      │      │   (Receipt transparency)  │
 └─────────────────────────┘      │      └───────────────────────────┘
             ▲                    │                   ▲
             │  Opportunity[]     │ /plan             │ payout receipts
             │                    │                   │
        ┌───────────────────────────────────────────────────────────┐
        │                 DELIVERY ENGINE (unified)                 │
        │  Contracts: Opportunity • ConsentReceipt • PayoutReceipt  │
        │  Endpoints: /plan • /deliver • /receipts • /abas          │
        │            Attribution Fallback Ladder                    │
        └───────────────────────────────────────────────────────────┘
             │             ▲                     ▲
             │ ABAS gate   │                     │ S2S postback
             ▼             │                     │
      ┌──────────────┐     │             ┌─────────────────┐
      │    NIAS      │     │             │ Merchant/Partner │
      │ cloud render │◄────┘             │  SDK + S2S hook  │
      │   (OpenAI)   │                   │ (auto-escalator) │
      └──────────────┘                   └─────────────────┘
             │
             ▼
      ┌──────────────┐
      │ Publisher SDK │
      │ WordPress etc │
      └──────────────┘
```

## Core Flow: Intent → Opportunity → ABAS → Render → Attribution

### 1. Intent Processing
```
User Intent/Search → DAST Providers (Claude/Multi-AI) → Opportunity[] 
                                                            ↓
                                            Schema validation
                                                            ↓
                                            /plan endpoint
```

### 2. ABAS Attention Boundary Protection
```
Each Opportunity → ABAS Gate → { approved: true/false, reason: "stress_block" | "flow_protection" | ... }
                     ↓
             Filter based on:
             • Safety (driving)
             • Stress levels (>0.8 threshold)
             • Flow state protection
             • Quiet hours (22:00-07:00)
             • Alignment score (<0.3 blocks)
```

### 3. Delivery Modes
```
Approved Opportunities → /deliver endpoint → Mode Selection:
                                                    │
                                    ┌───────────────┼───────────────┐
                                    ▼               ▼               ▼
                            NIAS (cloud)    DAST (widget)    Deferred
                          ephemeral overlay  persistent UI   queue for later
```

### 4. Attribution & Payout
```
User Action → Attribution Fallback Ladder:
              1. Affiliate Link (0.95+ confidence)
              2. S2S Postback (0.85+ confidence)  
              3. Receipt Matching (0.75+ confidence)
              4. Behavioral Inference (0.60+ confidence)
              5. Last Touch (0.40+ confidence)
                              ↓
                    PayoutReceipt → ΛID Wallet
                    Auto-escalator: 40/60 → 80/20
```

## Component Details

### TEQ (Transparency/Ethics/Governance)
- **Guardian System**: 280+ validation rules, 0.15 drift threshold
- **GDPR/CCPA Compliance**: Automated consent management, data subject rights
- **AI Act Compliance**: Limited Risk classification, human oversight
- **Model Cards**: gpt-4.1, dall-e-3, custom fine-tunes
- **Audit Trails**: Every decision logged with cryptographic integrity

### DAST (Dynamic Symbol Tracker) Providers
- **Primary**: Claude with structured JSON output (Anthropic API)
- **Secondary**: GPT-4.1 via OpenAI Responses API
- **Fallback**: Multi-AI consensus (Gemini, Perplexity)
- **Output**: Opportunity[] matching canonical schema
- **Constraints**: Consent-gated, attribution-ready, ABAS-compatible

### Delivery Engine (Unified API)
- **POST /plan**: intent + context + consent → Opportunity[]
- **POST /deliver**: opportunity + mode + user_state → render decision
- **POST /receipts/consent**: consent recording with signatures
- **POST /receipts/payout**: transparent settlement records
- **GET /abas/gate**: real-time attention boundary status

### SIGIL/ΛID (Identity & Wallet)
- **Identity**: Tiered access (guest → visitor → friend → trusted → inner_circle → root_dev)
- **Consent**: Granular scopes (purchase_history.read, recommendations.receive)
- **Wallet**: LKT tokens + fiat integration
- **Receipts**: Cryptographically signed transparency records

### NIAS (Non-Intrusive Advertising System)
- **Creative Generation**: OpenAI gpt-4.1 + dall-e-3
- **Cache Strategy**: Generate once, reuse N times
- **Moderation**: omni-moderation-latest before render
- **Delivery**: Ephemeral overlays, explicit consent required

## Success Metrics & SLAs

### Performance Targets
- **API Latency**: <100ms p95 for /plan and /deliver
- **ABAS Gate**: <10ms decision time
- **Attribution**: 95%+ accuracy across all tiers
- **Uptime**: 99.9% excluding scheduled maintenance

### Business Metrics
- **User Satisfaction**: >4.5/5.0 rating
- **Consent Retention**: >80% after 6 months
- **Merchant ROI**: >300% on platform fees
- **Publisher Revenue**: $500-5000/month range

### Compliance Metrics
- **Guardian Interventions**: <0.1% of decisions
- **Privacy Violations**: 0 incidents
- **Data Subject Response**: <30 days (GDPR requirement)
- **Audit Completeness**: 100% of transactions logged

## Integration Points

### Merchant Integration
```javascript
import { LukhasMerchantSDK } from '@lukhas/merchant-sdk';

const sdk = new LukhasMerchantSDK({
  apiKey: 'sk_merchant_...',
  merchantId: 'merchant_123'
});

// Submit product opportunity
await sdk.submitOpportunity(product, {
  commissionBps: 500, // 5%
  campaignId: 'summer_sale_2024'
});
```

### Publisher Integration
```javascript
import { LukhasPublisherSDK } from '@lukhas/publisher-sdk';

const sdk = new LukhasPublisherSDK({
  apiKey: 'sk_publisher_...',
  publisherId: 'pub_456'  
});

// Request contextual opportunities
const opportunities = await sdk.requestOpportunities({
  contentType: 'article',
  category: 'technology',
  audienceSize: 50000
});
```

## Security & Privacy

### Data Protection
- **Encryption**: AES-256 at rest, TLS 1.3 in transit
- **Access Control**: Role-based with principle of least privilege
- **Consent**: Granular, withdrawable, time-bounded
- **Anonymization**: Differential privacy for analytics

### AI Safety
- **Content Moderation**: Multi-layer (OpenAI + custom rules)
- **Bias Testing**: Quarterly assessments with mitigation
- **Human Oversight**: Required for high-value decisions (>$1000)
- **Transparency**: Algorithmic decision explanations available

## Deployment Architecture

### Production Environment
- **Cloud**: Multi-region (US-East, EU-West, APAC)
- **CDN**: Global edge caching for media assets
- **Database**: PostgreSQL with read replicas
- **Queue**: Redis for deferred/background processing
- **Monitoring**: Real-time metrics, alerts, dashboards

### Development Workflow
- **CI/CD**: GitHub Actions with automatic testing
- **Environments**: dev → staging → prod promotion
- **Feature Flags**: Gradual rollout capability
- **Rollback**: Automated revert on health check failures

This architecture enables transparent, ethical, and profitable AI-powered commerce while maintaining strict user privacy and consent boundaries. The system scales from individual users to enterprise partnerships while ensuring consistent experience and compliance across all touchpoints.