# 🎭 Agent Communication Channels

## Primary Channels

### 1. Coordination Dashboard
**Location**: `CLAUDE_ARMY/tasks/coordination_dashboard.md`
**Purpose**: Central status tracking and progress monitoring
**Update Frequency**: Daily

### 2. Interface Contracts
**Location**: `CLAUDE_ARMY/coordination/contracts/`
**Purpose**: Define API contracts between agents
**Review Frequency**: On changes

### 3. Integration Points
**Location**: `tests/integration/test_agent_coordination.py`
**Purpose**: Validate inter-agent communication
**Test Frequency**: On commit

## Communication Protocol

### Async Messaging
- Use context bus for event-driven communication
- Publish events for state changes
- Subscribe to relevant agent events

### Sync API Calls
- Use defined contracts for direct calls
- Include capability tokens for authorization
- Emit Λ-trace for all operations

### Status Updates
- Update task files with progress
- Mark blockers immediately
- Request help via coordination dashboard

## Escalation Path
1. Try to resolve within agent pair
2. Escalate to testing-devops-specialist for integration issues
3. Update coordination dashboard with blockers
4. Request user intervention if needed
