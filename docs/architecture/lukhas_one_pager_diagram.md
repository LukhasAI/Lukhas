# LUKHAS Delivery Engine Architecture

## System Overview

```
                ┌─────────────────────────────────────────────────────┐
                │                    TEQ (Gov)                        │
                │ Transparency • DPIA • Model Cards • Audit Receipts  │
                └─────────────────────────────────────────────────────┘
                                  ▲                 ▲
                                  │                 │ emits audit logs
                                  │                 │
     intent/search                 │          identity & payouts
 ┌─────────────────────────┐      │      ┌───────────────────────────┐
 │          DAST           │──────┼──────│        SIGIL / ΛID        │
 │ providers → Opportunity │      │      │ Consent, Identity, Wallet │
 └─────────────────────────┘      │      └───────────────────────────┘
             ▲                    │                   ▲
             │  Opportunity[]     │ /plan             │ payout receipts
             │                    │                   │
        ┌───────────────────────────────────────────────────────────┐
        │                   DELIVERY ENGINE (one)                   │
        │  Contracts: Opportunity • ConsentReceipt • PayoutReceipt  │
        │  Endpoints: /plan • /deliver • /receipts                  │
        └───────────────────────────────────────────────────────────┘
             │             ▲                     ▲
             │ ABAS gate   │                     │ affiliate S2S
             ▼             │                     │
      ┌──────────────┐     │             ┌─────────────────┐
      │    NIAS      │     │             │ Merchant/Partner │
      │ cloud render │◄────┘             │  SDK + S2S hook  │
      └──────────────┘                     └─────────────────┘
```

**Modes:** 
- **NIAS** = ephemeral "cloud" overlays
- **DAST** = persistent sidebar widgets
- **ABAS** is enforced for *both* modes before any render

## Flow Sequence

```
1. User Intent → DAST Context Analysis → Opportunity[]
2. /plan → ABAS Gate → Approved Opportunities
3. /deliver → Mode Selection (cloud/widget) → Render
4. User Action → Affiliate S2S → PayoutReceipt
5. All Events → TEQ Audit Trail → Compliance
```

## Key Differentiators

- **Single Delivery Engine**: One contract, two render modes
- **ABAS Gate**: Every delivery passes through attention protection
- **Transparent Receipts**: Human-readable consent and payout proofs
- **Cache-First**: Generate once, render many, cost-efficient
- **Partner SDKs**: Weekend integration for merchants and publishers