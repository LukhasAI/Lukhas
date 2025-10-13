# LUKHAS Feedback System - Complete Overview

## System Architecture

LUKHAS has a **multi-layered, comprehensive feedback system** designed for human-in-the-loop learning, compliance, and continuous AI alignment. The system spans multiple components with different purposes.

---

## 🎯 Core Components

### 1. User Feedback System
**Location**: `products/experience/feedback/core/user_feedback_system.py`

**Purpose**: Real-time multi-modal feedback collection with regulatory compliance

#### Key Features

**Multi-modal feedback types**:
- ⭐ **RATING**: 1-5 star ratings
- 😊 **EMOJI**: Standardized emotion emojis (10 types)
- 💬 **TEXT**: Natural language feedback with sentiment analysis
- 👍 **QUICK**: Thumbs up/down
- 📝 **DETAILED**: Comprehensive feedback
- ✏️ **CORRECTION**: User corrections of AI behavior

**Compliance Management**:
- GDPR (EU)
- CCPA (California)
- PIPEDA (Canada)
- UK GDPR
- Per-region data retention policies (90-365 days)
- Right to deletion, portability, anonymization
- Explicit consent management

**User Rights**:
- Edit feedback with history tracking
- Soft delete (preserves audit trail)
- Export personal data (GDPR compliance)
- View feedback history

**Intelligence Features**:
- Sentiment analysis (positive/negative scores)
- Emoji-to-sentiment mapping
- Rating-to-sentiment conversion
- Common theme extraction from text
- Improvement suggestion detection
- Aggregated action summaries

**Rate Limiting**: 0.05s minimum between submissions (prevents spam)

---

### 2. Feedback Cards System
**Location**: `products/experience/feedback/core/feedback_cards.py`

**Purpose**: Human-in-the-loop fine-tuning with structured feedback cards

#### Feedback Card Types
- **RATING**: 1-5 star ratings
- **COMPARISON**: A vs B preference
- **CORRECTION**: Fix/improve response
- **ANNOTATION**: Add context/explanation
- **VALIDATION**: Yes/No correctness
- **FREEFORM**: Open text feedback

#### Categories
- Accuracy
- Helpfulness
- Safety
- Creativity
- Clarity
- Relevance
- Completeness
- Tone

#### Impact Scoring System
```python
# Calculates feedback value (0.0-1.0)
- Extreme ratings (1 or 5 stars): +0.3
- Corrections: +0.4 (highly valuable)
- Annotations: +0.2
- Safety feedback: 1.5x multiplier
- Accuracy feedback: 1.2x multiplier
- User reputation boost: up to 20%
```

#### User Reputation System
- Consistency score (low variance = better)
- Accuracy validation rate
- Activity level (more feedback = more reliable)
- Quality focus (accuracy feedback valued)
- Recency score (recent activity valued)
- Scale: 0-5.0

#### High-Impact Feedback
- Impact > 0.7: Immediate processing
- Impact > 0.9: Critical alert
- Logged to `high_impact_alerts.jsonl`

**Storage**: SQLite database with full audit trail

---

### 3. Qi Feedback System
**Location**: `products/experience/feedback/qi_feedback/`

**Purpose**: Policy-safe feedback with cryptographic attestation

#### Key Features

**Cryptographic Attestation**:
- Dilithium3 or Ed25519 signatures
- SHA3-512 content hashing
- Public key infrastructure

**Feedback Context**:
- Task type (summarize, classify, etc.)
- Jurisdiction (EU, US, global)
- Policy pack version
- Model version

**Safety Constraints**:
- Ethics boundary enforcement
- Compliance boundary enforcement
- Threshold adjustment limits (±MAX_THRESHOLD_SHIFT)
- Allowed style validation

**Feedback Clustering**:
- Batch processing by task/jurisdiction
- Mean/variance satisfaction scores
- Common issue identification
- Drift detection from baseline

**Change Proposals**:
- HITL approval queue
- Risk assessment (low/medium/high)
- TTL for proposals (default 1 hour)
- Status tracking (pending/approved/rejected/applied)

---

### 4. Symbolic Feedback System
**Location**: `core/orchestration/user_feedback/feedback_collector.py`

**Purpose**: Collect symbolic and natural feedback for introspective modules

**Features**:
- Simple rating + comment collection
- JSON log storage (`logs/symbolic_feedback_log.json`)
- Timestamped feedback
- Module-specific feedback tracking

---

## 🌐 API Endpoints

### Feedback API
**Location**: `api/feedback_api.py`
**Server**: FastAPI on port **8001**

#### Endpoints

```
POST   /feedback/submit       - Submit comprehensive feedback
POST   /feedback/quick        - Quick thumbs up/down
POST   /feedback/emoji        - Emoji reaction
POST   /feedback/text         - Natural language feedback
PUT    /feedback/edit         - Edit existing feedback
DELETE /feedback/{id}         - Delete feedback
GET    /feedback/history/{user_id} - User feedback history
GET    /feedback/summary/{action_id} - Aggregated action summary
POST   /consent               - Update consent preferences
GET    /feedback/export/{user_id} - Export user data (GDPR)
GET    /feedback/report       - Analytics report
GET    /status                - System status
GET    /health                - Health check
```

#### UI Widgets
```
GET    /widget/rating         - Rating widget HTML
GET    /widget/emoji          - Emoji grid HTML
GET    /widget/quick          - Quick feedback HTML
```

---

### Feedback Routes
**Location**: `serve/feedback_routes.py`
**Router**: `/feedback`

#### Endpoints

```
POST   /feedback/capture      - Capture single feedback card
POST   /feedback/batch        - Capture multiple cards
GET    /feedback/report/{user_id} - Learning report
GET    /feedback/metrics      - System metrics
POST   /feedback/trigger-learning - Trigger pattern extraction
GET    /feedback/health       - Health check
```

---

## 📊 Analytics & Learning

### Pattern Extraction
- Identifies common themes from text feedback
- Extracts improvement suggestions
- Keyword frequency analysis
- Sentiment distribution tracking

### Learning Reports
- Per-user satisfaction scores
- Improvement trends
- Preferred styles
- Recommended adjustments

### System Metrics
- Total cards captured
- Patterns identified
- Policies updated
- Validation pass/fail rates
- Average ratings by category
- Impact score distribution

### Feedback Summaries

```
📊 Feedback Summary (Last 7 Days)
================================

Total Cards: X
Completed: Y (Z%)
Average Rating: A.B/5.0

Category Breakdown:
  • accuracy: N cards, X.Y avg
  • helpfulness: N cards, X.Y avg

Impact Analysis:
  • Mean Impact: 0.XX
  • High Impact: N cards
```

---

## 🛡️ Security & Privacy

### Data Protection
- HMAC SHA3-512 hashing for user IDs
- Session ID hashing
- Optional note encryption
- Anonymization for analytics
- Configurable data retention

### Audit Trail
- All feedback logged with timestamps
- Edit history preserved
- Soft deletes (never hard delete)
- Compliance event logging

### Guardian Integration
- Constitutional AI constraints
- Ethical boundary enforcement
- Drift detection
- Policy validation before applying updates

---

## 🎨 UI Components

### FeedbackWidget (Built-in HTML generators)
1. **Rating Widget**: 5-star rating interface
2. **Emoji Grid**: 10 emotion emojis
3. **Quick Feedback**: Thumbs up/down + report button

### FeedbackUI (Card renderers)
- Rating card HTML
- Comparison card HTML
- Custom styling support

---

## 🔄 Feedback Loop Process

```
1. User interacts with AI
     ↓
2. System presents feedback card/widget
     ↓
3. User provides feedback (rating/emoji/text)
     ↓
4. Sentiment analysis + impact scoring
     ↓
5. Store in database with audit trail
     ↓
6. High-impact feedback → immediate processing
     ↓
7. Batch processing → pattern extraction
     ↓
8. Generate policy update proposals
     ↓
9. Guardian validation
     ↓
10. HITL approval (if required)
     ↓
11. Apply to system (fine-tuning/policy updates)
     ↓
12. Track effectiveness → user learning report
```

---

## 📈 Key Metrics Tracked

- **User Satisfaction**: Average rating, sentiment scores
- **System Health**: Completion rate, response time
- **Learning Progress**: Patterns identified, policies updated
- **Compliance**: Consent rates, data retention adherence
- **Impact**: High-impact feedback count, validation rates
- **User Engagement**: Feedback frequency, preferred types

---

## 🧪 Testing

Test files found:
- `tests/unit/candidate/consciousness/dream/test_dream_feedback_controller.py`
- `feedback/tests/test_feedback_unit.py`
- `feedback/tests/test_feedback_integration.py`

---

## 💡 Unique Features

1. **Multi-Tier Feedback System**: From simple emoji reactions to detailed corrections
2. **Cryptographic Attestation**: Quantum-resistant signatures (Dilithium3)
3. **User Reputation System**: Trusted users get higher impact weighting
4. **Real-time Impact Scoring**: Immediate processing of critical feedback
5. **Compliance by Design**: Region-specific policies built-in
6. **Guardian Integration**: Constitutional AI boundaries enforced
7. **Human-in-the-Loop**: Approval queues for policy changes
8. **Feedback Clustering**: Batch processing for efficiency
9. **Learning Reports**: Transparent explanations of what system learned
10. **Privacy-First**: Anonymization, encryption, user control

---

## 🚀 Getting Started

```python
# Initialize feedback system
from products.experience.feedback.core.user_feedback_system import UserFeedbackSystem

system = UserFeedbackSystem(config={
    "enable_emoji": True,
    "min_feedback_interval": 30  # seconds
})

await system.initialize()

# Collect feedback
feedback_id = await system.collect_feedback(
    user_id="user123",
    session_id="session456",
    action_id="decision_789",
    feedback_type=FeedbackType.RATING,
    content={"rating": 5},
    context={"action_type": "recommendation"}
)

# Get summary
summary = await system.get_action_feedback("decision_789")
print(f"Average rating: {summary.average_rating}")
```

---

## 📚 Documentation Files

- `docs/ui/feedback_cards.md`
- `docs/enterprise/ENTERPRISE_FEEDBACK_POETRY.md`
- `manifests/labs/core/orchestration/user_feedback/lukhas_context.md`

---

## Summary

The LUKHAS feedback system is a **production-grade, compliance-ready, human-in-the-loop learning platform** that enables continuous AI alignment through structured, multi-modal user feedback with cryptographic guarantees and privacy protection.
