# Oneiric Core - Symbolic Dream Analysis System

A comprehensive symbolic dream analysis platform featuring identity management, multimodal dream generation, and real-time drift tracking.

## 🌟 Features

- **ΛiD Identity System**: Cryptographic symbolic identity protocol with multi-tier access
- **Dream Generation**: AI-powered symbolic dream synthesis with narrative, image, and audio
- **Drift Tracking**: Real-time analysis of symbolic state evolution
- **Multimodal Interface**: React-based frontend with animations and responsive design
- **Authentication**: Clerk-based JWT authentication with tier management
- **Database**: PostgreSQL with vector embeddings and JSONB profiles

## 🏗️ Architecture

### Backend (FastAPI)
- **Identity Layer**: ΛiD protocol with symbolic authentication
- **API Layer**: RESTful endpoints with JWT middleware
- **Database Layer**: PostgreSQL with Alembic migrations
- **Analysis Layer**: Symbolic drift calculation and tracking

### Frontend (Next.js/React)
- **Oracle Chat**: Main dream generation interface
- **Dream Journal**: Animated dream history with rating system
- **Symbol Explorer**: Pattern visualization and analysis
- **Settings Overlay**: User preference management

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 16+
- Docker (optional)

### Backend Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd oneiric_core

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database and API keys

# Run database migrations
alembic upgrade head

# Start the API server
uvicorn oneiric_core.main:app --reload
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your API URL and Clerk keys

# Start development server
npm run dev
```

### Docker Setup (Alternative)

```bash
# Start all services
docker-compose up -d

# Run migrations
docker-compose run migrate

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/oneiric_core
LUKHAS_ID_SECRET=your_secret_key_here
CLERK_JWT_VERIFY_URL=https://api.clerk.dev/v1/jwks
CLERK_SECRET_KEY=sk_test_your_clerk_secret
DEBUG=true
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_clerk_key
```

### Database Setup

1. Create PostgreSQL database:
```sql
CREATE DATABASE oneiric_core;
CREATE USER oneiric_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE oneiric_core TO oneiric_user;
```

2. Run migrations:
```bash
alembic upgrade head
```

## 📚 API Documentation

### Authentication
All protected endpoints require JWT token in Authorization header:
```
Authorization: Bearer <clerk_jwt_token>
```

### Key Endpoints

#### Health Check
```
GET /healthz
Response: {"status": "ok", "user_id": "...", "tier": 1, "lukhas_id": "LUKHAS..."}
```

#### Dream Generation
```
POST /api/generate-dream
Body: {"prompt": "flying through clouds", "recursive": true}
Response: {
  "sceneId": "dream_...",
  "narrativeText": "...",
  "renderedImageUrl": "...",
  "symbolicStructure": {...}
}
```

#### Dreams List
```
GET /api/dreams
Response: {"dreams": [...]}
```

#### Symbols Analysis
```
GET /api/symbols
Response: {"symbols": [...]}
```

## 🧪 Testing

### Backend Tests
```bash
# Run all tests
pytest

# Run database tests only
pytest -m pg

# Run unit tests only
pytest -m unit

# Run with coverage
pytest --cov=oneiric_core
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🏗️ Development

### Project Structure
```
oneiric_core/
├── oneiric_core/           # Backend Python package
│   ├── identity/           # ΛiD identity system
│   ├── db/                 # Database layer
│   ├── analysis/           # Drift calculation
│   ├── migrations/         # Alembic migrations
│   └── main.py            # FastAPI application
├── frontend/              # Next.js frontend
│   ├── src/
│   │   ├── app/           # App router pages
│   │   ├── components/    # React components
│   │   ├── context/       # Global state
│   │   ├── lib/           # API client & hooks
│   │   └── types/         # TypeScript types
│   └── package.json
├── tests/                 # Backend tests
├── docker-compose.yml     # Development environment
└── requirements.txt       # Python dependencies
```

### Adding New Features

1. **Backend Endpoint**: Add to `oneiric_core/main.py`
2. **Database Changes**: Create Alembic migration
3. **Frontend Component**: Add to `frontend/src/components/`
4. **API Integration**: Add hook to `frontend/src/lib/hooks.ts`

### Code Style
- Backend: Follow PEP 8, use type hints
- Frontend: Use TypeScript, follow React best practices
- Database: Use Alembic for all schema changes

## 🔒 Security

### ΛiD Identity System
- Cryptographic user identity with HMAC signing
- Multi-tier access control (1-5)
- Session token management
- Audit logging

### Authentication Flow
1. User signs in via Clerk
2. JWT token verified on each request
3. User record upserted in database
4. ΛiD generated if not exists
5. User attached to request state

## 📊 Monitoring

### Health Checks
- `/health`: Public health check
- `/healthz`: Authenticated health check with user info

### Logging
- Structured logging with correlation IDs
- Error tracking and metrics
- Drift analysis audit trail

## 🚢 Deployment

### Production Checklist
- [ ] Set strong `LUKHAS_ID_SECRET`
- [ ] Configure production database
- [ ] Set up Clerk production keys
- [ ] Enable HTTPS
- [ ] Configure monitoring
- [ ] Set up backup strategy

### Docker Production
```bash
# Build images
docker build -t oneiric-core-api .
docker build -t oneiric-core-frontend ./frontend

# Deploy with production compose
docker-compose -f docker-compose.prod.yml up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with FastAPI and Next.js
- Uses Clerk for authentication
- Powered by PostgreSQL and pgvector
- Styled with Tailwind CSS

---

**Oneiric Core** - Where consciousness meets code in the realm of symbolic dreams. 🌙✨
