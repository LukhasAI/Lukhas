---
status: wip
type: documentation
---
# Oneiric Integration Notes

## Integration Status
- **Date**: July 15, 2025
- **Commit**: 84ce357
- **Status**: Successfully integrated as separate module

## Project Structure
```
oneiric/
├── oneiric_core/           # Backend API and analysis engine
│   ├── analysis/          # Dream analysis algorithms
│   ├── db/               # Database models and repositories
│   ├── identity/         # Authentication and user management
│   └── migrations/       # Database migrations
├── frontend/             # React/Next.js dream interface
├── demo/                 # Interactive demo applications
│   └── dreams/             # Dream simulation sandbox and demos
└── tests/               # Test suite
```

## Integration Points

### Current Integration
- **Standalone Module**: Oneiric operates as independent module
- **Database**: Uses SQLAlchemy with Alembic migrations
- **API**: FastAPI backend with dream analysis endpoints
- **Frontend**: React/Next.js interface for dream visualization
- **Dreams Module**: `demo/dreams` now contains simulation hooks and symbolic test flows

### Future Integration Opportunities
1. **Core Integration**: Connect `oneiric_core.analysis` → `core.bio_core.dream`
2. **Identity System**: Integrate with existing `lukhas-id` system
3. **Memory System**: Connect dream analysis to memory traces
4. **Symbolic Processing**: Link dream symbols to symbolic reasoning

## Next Steps for Integration
1. Create API bridges between oneiric and core systems
2. Implement shared authentication with lukhas-id
3. Add dream data to memory system traces
4. Connect symbolic interpretation to reasoning engine
5. Expand `demo/dreams` as a symbolic sandbox for prototyping dream-state scenarios

## File Security
- ✅ `.env` files properly excluded from Git
- ✅ `.DS_Store` files ignored
- ✅ Cache directories excluded
- ✅ Sensitive configuration protected

## Dream System Architecture

The dream system is managed by the `DreamReflectionLoop` class, located in `consciousness/core_consciousness/dream_engine/dream_reflection_loop.py`. This class is responsible for the following:

*   Consolidating memories during idle periods.
*   Extracting insights and recognizing patterns in dreams.
*   Synthesizing dream representations.
*   Tracking symbolic convergence and drift scores.

## Tag Protocols

The following tags are used in the dream system:

*   `# ΛTAG: active_dream_loop`: Indicates the active dream reflection loop module.
*   `# ΛTAG: dream_drift`: Related to dream drift calculations.
*   `# ΛTAG: affect_loop`: Related to affect loop calculations.
*   `# ΛTAG: symbolic_recurrence`: Related to symbolic recurrence calculations.
*   `# ΛLEGACY_DREAM_MODULE: deprecated`: Indicates a deprecated dream module.

## Symbolic Dream API Outline

### Endpoints

*   `POST /dream/start`: Start a new dream cycle.
    *   **Request Body**: `{ "duration_minutes": 10 }`
    *   **Response**: `{ "status": "success", "message": "Dream cycle started" }`
*   `POST /dream/stop`: Stop the current dream cycle.
    *   **Response**: `{ "status": "success", "message": "Dream cycle stopped" }`
*   `GET /dream/state`: Get the current state of the dream system.
    *   **Response**: `{ "dream_state": "active", "cycle_count": 5, ... }`
*   `GET /dream/summary`: Get a summary of the dream synthesis.
    *   **Response**: `{ "total_dream_cycles": 5, ... }`
*   `POST /dream/feedback`: Provide feedback on a dream.
    *   **Request Body**: `{ "dream_id": "...", "feedback": "..." }`
    *   **Response**: `{ "status": "success", "message": "Feedback received" }`
