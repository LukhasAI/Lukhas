# Oneiric Core - Project Structure

## Overview
Oneiric Core is a symbolic dream analysis system with identity management, featuring:
- **Backend**: FastAPI with ΛiD (Lukhas ID) identity management
- **Frontend**: Next.js/React with Clerk authentication
- **Database**: PostgreSQL with vector embeddings
- **Features**: Dream generation, symbolic drift tracking, settings overlay, animations

## Architecture

### Backend (FastAPI)
```
oneiric_core/
├── identity/
│   ├── lukhas_id.py           # ΛiD identity protocol
│   └── auth_middleware.py     # JWT verification & user attachment
├── db/
│   ├── db.py                  # Database connection pool
│   └── user_repository.py     # User data access layer
├── analysis/
│   └── drift_score.py         # Symbolic drift calculation
├── migrations/
│   └── versions/
│       └── 20250710_add_users_table.py
├── main.py                    # FastAPI application
└── settings.py                # Configuration
```

### Frontend (Next.js/React)
```
src/
├── app/
│   ├── layout.tsx            # Root layout with providers
│   ├── page.tsx              # Oracle Chat page
│   ├── journal/
│   │   └── page.tsx          # Dream Journal
│   └── symbols/
│       └── page.tsx          # Symbol Explorer
├── components/
│   ├── NavBar.tsx            # Navigation with settings
│   ├── SettingsOverlay.tsx   # Settings modal
│   ├── DreamCard.tsx         # Animated dream cards
│   └── OracleChat.tsx        # Main chat interface
├── context/
│   └── SettingsContext.tsx   # Global settings state
├── lib/
│   ├── api.ts                # API client
│   └── hooks.ts              # React Query hooks
├── types/
│   └── dream.ts              # TypeScript types
└── styles/
    └── globals.css           # Global styles with animations
```

### Database Schema
```sql
-- Users table with symbolic profiles
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    email TEXT,
    tier INTEGER DEFAULT 1,
    lukhas_id TEXT UNIQUE,
    drift_profile JSONB DEFAULT '{}',
    ethics_profile JSONB DEFAULT '{}',
    identity_embedding VECTOR(1536),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## Key Features

### 1. ΛiD Identity System
- Symbolic identity protocol with multi-tier access
- Cryptographic user verification
- Drift tracking for symbolic evolution

### 2. Dream Generation & Analysis
- Multimodal dream synthesis (text, image, audio)
- Symbolic structure analysis
- Drift score calculation

### 3. Settings & Personalization
- Global settings context
- Persistent user preferences
- Dynamic API adaptation

### 4. Animations & UX
- Fade-up animations for dream cards
- Symbolic "resurfacing" effects
- Responsive design

## Environment Variables
```
DATABASE_URL=postgresql://user:password@localhost/oneiric_core
LUKHAS_ID_SECRET=your_hmac_signing_key
CLERK_JWT_VERIFY_URL=https://api.clerk.dev/v1/jwks
```

## Development Workflow
1. Backend: `uvicorn oneiric_core.main:app --reload`
2. Frontend: `npm run dev`
3. Database: `alembic upgrade head`
4. Tests: `pytest -m pg` (with PostgreSQL container)

## Next Steps
- [ ] Complete identity loop integration
- [ ] Add Dream Memory Map visualization
- [ ] Implement admin dashboard
- [ ] Add CI/CD pipeline
- [ ] Deploy to production
