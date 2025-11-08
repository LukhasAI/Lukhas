# LUKHAS AI API Reference

**Last Updated**: 2025-11-08


**Version**: 1.0.0
**Base URL**: `https://api.lukhas.ai/v1`

## Authentication

All API requests require authentication via API key:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" https://api.lukhas.ai/v1/endpoint
```

## Endpoints

This document provides a comprehensive reference for all LUKHAS AI API endpoints.

### Consciousness Chat API

The Consciousness Chat API provides a natural language interface to the LUKHAS consciousness systems.

#### POST /chat

Process a chat message through the consciousness interface.

**Request Body:**

```json
{
  "message": "string",
  "session_id": "string",
  "user_id": "string"
}
```

**Response Body:**

```json
{
  "response": "string",
  "session_id": "string",
  "timestamp": "2025-11-08T12:00:00.000Z",
  "metadata": {}
}
```

**cURL Example:**

```bash
curl -X POST "https://api.lukhas.ai/v1/chat" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "How aware are you right now?",
       "session_id": "session_123",
       "user_id": "user_456"
     }'
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}
data = {
    "message": "How aware are you right now?",
    "session_id": "session_123",
    "user_id": "user_456",
}
response = requests.post("https://api.lukhas.ai/v1/chat", headers=headers, json=data)
print(response.json())
```

---

#### GET /sessions

Get information about all active sessions.

**Response Body:**

```json
[
  {
    "session_id": "string",
    "user_id": "string",
    "turn_count": 0,
    "created_at": "2025-11-08T12:00:00.000Z",
    "last_active": "2025-11-08T12:00:00.000Z",
    "topics": []
  }
]
```

**cURL Example:**

```bash
curl -X GET "https://api.lukhas.ai/v1/sessions" \
     -H "Authorization: Bearer YOUR_API_KEY"
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
headers = {"Authorization": f"Bearer {api_key}"}
response = requests.get("https://api.lukhas.ai/v1/sessions", headers=headers)
print(response.json())
```

---

#### GET /sessions/{session_id}

Get conversation history for a specific session.

**Response Body:**

```json
{
  "session_id": "string",
  "user_id": "string",
  "turns": [],
  "emotional_state": {},
  "topics": []
}
```

**cURL Example:**

```bash
curl -X GET "https://api.lukhas.ai/v1/sessions/session_123" \
     -H "Authorization: Bearer YOUR_API_KEY"
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
session_id = "session_123"
headers = {"Authorization": f"Bearer {api_key}"}
response = requests.get(f"https://api.lukhas.ai/v1/sessions/{session_id}", headers=headers)
print(response.json())
```

---

#### DELETE /sessions/{session_id}

End a conversation session.

**Response Body:**

```json
{
  "message": "string",
  "session_id": "string",
  "total_turns": 0
}
```

**cURL Example:**

```bash
curl -X DELETE "https://api.lukhas.ai/v1/sessions/session_123" \
     -H "Authorization: Bearer YOUR_API_KEY"
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
session_id = "session_123"
headers = {"Authorization": f"Bearer {api_key}"}
response = requests.delete(f"https://api.lukhas.ai/v1/sessions/{session_id}", headers=headers)
print(response.json())
```

---

#### GET /status

Get system status and health information.

**Response Body:**

```json
{
  "operational": true,
  "active_sessions": 0,
  "total_conversations": 0,
  "connected_services": {},
  "uptime_seconds": 0.0
}
```

**cURL Example:**

```bash
curl -X GET "https://api.lukhas.ai/v1/status" \
     -H "Authorization: Bearer YOUR_API_KEY"
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
headers = {"Authorization": f"Bearer {api_key}"}
response = requests.get("https://api.lukhas.ai/v1/status", headers=headers)
print(response.json())
```

---

#### POST /feedback

Submit feedback for a conversation.

**Request Body:**

```json
{
  "session_id": "string",
  "rating": 0,
  "comment": "string"
}
```

**Response Body:**

```json
{
  "message": "string",
  "session_id": "string",
  "rating": 0
}
```

**cURL Example:**

```bash
curl -X POST "https://api.lukhas.ai/v1/feedback" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "session_id": "session_123",
       "rating": 5,
       "comment": "Great response!"
     }'
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}
data = {
    "session_id": "session_123",
    "rating": 5,
    "comment": "Great response!",
}
response = requests.post("https://api.lukhas.ai/v1/feedback", headers=headers, json=data)
print(response.json())
```

---

#### GET /health

Simple health check endpoint.

**Response Body:**

```json
{
  "status": "string",
  "timestamp": "2025-11-08T12:00:00.000Z"
}
```

**cURL Example:**

```bash
curl -X GET "https://api.lukhas.ai/v1/health" \
     -H "Authorization: Bearer YOUR_API_KEY"
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
headers = {"Authorization": f"Bearer {api_key}"}
response = requests.get("https://api.lukhas.ai/v1/health", headers=headers)
print(response.json())
```

### API Expansion

The API Expansion provides endpoints for the Consciousness, Identity, and Guardian systems.

#### Consciousness

##### GET /consciousness/status

Query the current state of consciousness.

**Response Body:**

```json
{
  "state": "string",
  "awareness_level": 0.0,
  "active_processes": []
}
```

**cURL Example:**

```bash
curl -X GET "https://api.lukhas.ai/v1/consciousness/status" \
     -H "Authorization: Bearer YOUR_API_KEY"
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
headers = {"Authorization": f"Bearer {api_key}"}
response = requests.get("https://api.lukhas.ai/v1/consciousness/status", headers=headers)
print(response.json())
```

---

##### GET /consciousness/awareness

Get the current awareness level.

**Response Body:**

```json
{
  "level": 0.0
}
```

**cURL Example:**

```bash
curl -X GET "https://api.lukhas.ai/v1/consciousness/awareness" \
     -H "Authorization: Bearer YOUR_API_KEY"
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
headers = {"Authorization": f"Bearer {api_key}"}
response = requests.get("https://api.lukhas.ai/v1/consciousness/awareness", headers=headers)
print(response.json())
```

---

##### POST /consciousness/awareness

Set a new awareness level.

**Request Body:**

```json
{
  "level": 0.0
}
```

**Response Body:**

```json
{
  "level": 0.0
}
```

**cURL Example:**

```bash
curl -X POST "https://api.lukhas.ai/v1/consciousness/awareness" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "level": 0.9
     }'
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}
data = {"level": 0.9}
response = requests.post("https://api.lukhas.ai/v1/consciousness/awareness", headers=headers, json=data)
print(response.json())
```

---

##### POST /consciousness/memory/query

Interact with the memory system.

**Request Body:**

```json
{
  "query": "string"
}
```

**Response Body:**

```json
{
  "results": []
}
```

**cURL Example:**

```bash
curl -X POST "https://api.lukhas.ai/v1/consciousness/memory/query" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "What is the nature of reality?"
     }'
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}
data = {"query": "What is the nature of reality?"}
response = requests.post("https://api.lukhas.ai/v1/consciousness/memory/query", headers=headers, json=data)
print(response.json())
```

---

##### POST /consciousness/dream/start

Initiate a new dream state.

**Request Body:**

```json
{
  "topic": "string",
  "duration_minutes": 0
}
```

**Response Body:**

```json
{
  "dream_id": "string",
  "status": "string",
  "topic": "string"
}
```

**cURL Example:**

```bash
curl -X POST "https://api.lukhas.ai/v1/consciousness/dream/start" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "topic": "The future of AI",
       "duration_minutes": 10
     }'
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}
data = {
    "topic": "The future of AI",
    "duration_minutes": 10,
}
response = requests.post("https://api.lukhas.ai/v1/consciousness/dream/start", headers=headers, json=data)
print(response.json())
```

---

##### GET /consciousness/dream/status/{dream_id}

Get the status of a dream state.

**Response Body:**

```json
{
  "dream_id": "string",
  "status": "string",
  "topic": "string"
}
```

**cURL Example:**

```bash
curl -X GET "https://api.lukhas.ai/v1/consciousness/dream/status/dream_123" \
     -H "Authorization: Bearer YOUR_API_KEY"
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
dream_id = "dream_123"
headers = {"Authorization": f"Bearer {api_key}"}
response = requests.get(f"https://api.lukhas.ai/v1/consciousness/dream/status/{dream_id}", headers=headers)
print(response.json())
```

---

#### Identity

##### POST /identity/users

Create a new user identity.

**Request Body:**

```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

**Response Body:**

```json
{
  "user_id": "string",
  "username": "string",
  "email": "string",
  "created_at": "2025-11-08T12:00:00.000Z"
}
```

**cURL Example:**

```bash
curl -X POST "https://api.lukhas.ai/v1/identity/users" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "testuser",
       "email": "test@example.com",
       "password": "password123"
     }'
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}
data = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
}
response = requests.post("https://api.lukhas.ai/v1/identity/users", headers=headers, json=data)
print(response.json())
```

---

##### GET /identity/users/{user_id}

Retrieve a user identity.

**Response Body:**

```json
{
  "user_id": "string",
  "username": "string",
  "email": "string",
  "created_at": "2025-11-08T12:00:00.000Z"
}
```

**cURL Example:**

```bash
curl -X GET "https://api.lukhas.ai/v1/identity/users/user_123" \
     -H "Authorization: Bearer YOUR_API_KEY"
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
user_id = "user_123"
headers = {"Authorization": f"Bearer {api_key}"}
response = requests.get(f"https://api.lukhas.ai/v1/identity/users/{user_id}", headers=headers)
print(response.json())
```

---

##### PUT /identity/users/{user_id}

Update a user identity.

**Request Body:**

```json
{
  "username": "string",
  "email": "string"
}
```

**Response Body:**

```json
{
  "user_id": "string",
  "username": "string",
  "email": "string",
  "created_at": "2025-11-08T12:00:00.000Z"
}
```

**cURL Example:**

```bash
curl -X PUT "https://api.lukhas.ai/v1/identity/users/user_123" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "new_username"
     }'
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
user_id = "user_123"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}
data = {"username": "new_username"}
response = requests.put(f"https://api.lukhas.ai/v1/identity/users/{user_id}", headers=headers, json=data)
print(response.json())
```

---

##### DELETE /identity/users/{user_id}

Delete a user identity.

**Response Body:**

```json
{
  "status": "string",
  "message": "string"
}
```

**cURL Example:**

```bash
curl -X DELETE "https://api.lukhas.ai/v1/identity/users/user_123" \
     -H "Authorization: Bearer YOUR_API_KEY"
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
user_id = "user_123"
headers = {"Authorization": f"Bearer {api_key}"}
response = requests.delete(f"https://api.lukhas.ai/v1/identity/users/{user_id}", headers=headers)
print(response.json())
```

---

##### POST /identity/auth/token

Request an authentication token.

**Request Body:**

```json
{
  "username": "string",
  "password": "string"
}
```

**Response Body:**

```json
{
  "access_token": "string",
  "token_type": "string"
}
```

**cURL Example:**

```bash
curl -X POST "https://api.lukhas.ai/v1/identity/auth/token" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "testuser",
       "password": "password123"
     }'
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}
data = {
    "username": "testuser",
    "password": "password123",
}
response = requests.post("https://api.lukhas.ai/v1/identity/auth/token", headers=headers, json=data)
print(response.json())
```

---

##### POST /identity/auth/authorize

Check authorization for a resource.

**Request Body:**

```json
{
  "token": "string",
  "resource": "string"
}
```

**Response Body:**

```json
{
  "allowed": true
}
```

**cURL Example:**

```bash
curl -X POST "https://api.lukhas.ai/v1/identity/auth/authorize" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "token": "dummy_token",
       "resource": "consciousness:dream:start"
     }'
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}
data = {
    "token": "dummy_token",
    "resource": "consciousness:dream:start",
}
response = requests.post("https://api.lukhas.ai/v1/identity/auth/authorize", headers=headers, json=data)
print(response.json())
```

---

##### POST /identity/consolidate

Consolidate multiple identities.

**Request Body:**

```json
{
  "primary_user_id": "string",
  "secondary_user_id": "string"
}
```

**Response Body:**

```json
{
  "user_id": "string",
  "username": "string",
  "email": "string",
  "created_at": "2025-11-08T12:00:00.000Z"
}
```

**cURL Example:**

```bash
curl -X POST "https://api.lukhas.ai/v1/identity/consolidate" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "primary_user_id": "user_123",
       "secondary_user_id": "user_456"
     }'
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}
data = {
    "primary_user_id": "user_123",
    "secondary_user_id": "user_456",
}
response = requests.post("https://api.lukhas.ai/v1/identity/consolidate", headers=headers, json=data)
print(response.json())
```

---

#### Guardian

##### GET /guardian/safety/protocols

Get current safety protocols.

**Response Body:**

```json
{
  "protocols": []
}
```

**cURL Example:**

```bash
curl -X GET "https://api.lukhas.ai/v1/guardian/safety/protocols" \
     -H "Authorization: Bearer YOUR_API_KEY"
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
headers = {"Authorization": f"Bearer {api_key}"}
response = requests.get("https://api.lukhas.ai/v1/guardian/safety/protocols", headers=headers)
print(response.json())
```

---

##### GET /guardian/ethics/monitor

Get real-time ethics monitoring data.

**Response Body:**

```json
{
  "monitoring_status": "string",
  "ethical_concerns": []
}
```

**cURL Example:**

```bash
curl -X GET "https://api.lukhas.ai/v1/guardian/ethics/monitor" \
     -H "Authorization: Bearer YOUR_API_KEY"
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
headers = {"Authorization": f"Bearer {api_key}"}
response = requests.get("https://api.lukhas.ai/v1/guardian/ethics/monitor", headers=headers)
print(response.json())
```

---

##### POST /guardian/compliance/check

Run a compliance check.

**Request Body:**

```json
{
  "system": "string",
  "level": "string"
}
```

**Response Body:**

```json
{
  "compliant": true,
  "details": "string"
}
```

**cURL Example:**

```bash
curl -X POST "https://api.lukhas.ai/v1/guardian/compliance/check" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "system": "all",
       "level": "strict"
     }'
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}
data = {
    "system": "all",
    "level": "strict",
}
response = requests.post("https://api.lukhas.ai/v1/guardian/compliance/check", headers=headers, json=data)
print(response.json())
```

---

##### GET /guardian/audit/trail

Access the audit trail.

**Response Body:**

```json
{
  "logs": []
}
```

**cURL Example:**

```bash
curl -X GET "https://api.lukhas.ai/v1/guardian/audit/trail" \
     -H "Authorization: Bearer YOUR_API_KEY"
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
headers = {"Authorization": f"Bearer {api_key}"}
response = requests.get("https://api.lukhas.ai/v1/guardian/audit/trail", headers=headers)
print(response.json())
```

### Feedback API

The Feedback API allows for the collection of multi-modal user feedback.

#### POST /feedback/submit

Submit comprehensive feedback.

**Request Body:**

```json
{
  "user_id": "string",
  "session_id": "string",
  "action_id": "string",
  "feedback_type": "string",
  "content": {},
  "context": {},
  "region": "string"
}
```

**Response Body:**

```json
{
  "success": true,
  "feedback_id": "string",
  "message": "string",
  "timestamp": "2025-11-08T12:00:00.000Z"
}
```

**cURL Example:**

```bash
curl -X POST "https://api.lukhas.ai/v1/feedback/submit" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "user_123",
       "session_id": "session_456",
       "action_id": "decision_789",
       "feedback_type": "rating",
       "content": {"rating": 5},
       "context": {
         "action_type": "recommendation",
         "decision": "Suggested option A"
       },
       "region": "eu"
     }'
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}
data = {
    "user_id": "user_123",
    "session_id": "session_456",
    "action_id": "decision_789",
    "feedback_type": "rating",
    "content": {"rating": 5},
    "context": {
        "action_type": "recommendation",
        "decision": "Suggested option A",
    },
    "region": "eu",
}
response = requests.post("https://api.lukhas.ai/v1/feedback/submit", headers=headers, json=data)
print(response.json())
```

---

#### POST /feedback/quick

Submit quick thumbs up/down feedback.

**Request Body:**

```json
{
  "user_id": "string",
  "action_id": "string",
  "thumbs_up": true,
  "session_id": "string"
}
```

**Response Body:**

```json
{
  "success": true,
  "feedback_id": "string",
  "message": "string",
  "timestamp": "2025-11-08T12:00:00.000Z"
}
```

**cURL Example:**

```bash
curl -X POST "https://api.lukhas.ai/v1/feedback/quick" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "user_123",
       "action_id": "decision_789",
       "thumbs_up": true
     }'
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}
data = {
    "user_id": "user_123",
    "action_id": "decision_789",
    "thumbs_up": true,
}
response = requests.post("https://api.lukhas.ai/v1/feedback/quick", headers=headers, json=data)
print(response.json())
```

---

#### POST /feedback/emoji

Submit emoji reaction feedback.

**Request Body:**

```json
{
  "user_id": "string",
  "session_id": "string",
  "action_id": "string",
  "emoji": "string",
  "context": {}
}
```

**Response Body:**

```json
{
  "success": true,
  "feedback_id": "string",
  "message": "string",
  "timestamp": "2025-11-08T12:00:00.000Z"
}
```

**cURL Example:**

```bash
curl -X POST "https://api.lukhas.ai/v1/feedback/emoji" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "user_123",
       "session_id": "session_456",
       "action_id": "decision_789",
       "emoji": "👍"
     }'
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}
data = {
    "user_id": "user_123",
    "session_id": "session_456",
    "action_id": "decision_789",
    "emoji": "👍",
}
response = requests.post("https://api.lukhas.ai/v1/feedback/emoji", headers=headers, json=data)
print(response.json())
```

---

#### POST /feedback/text

Submit natural language feedback.

**Request Body:**

```json
{
  "user_id": "string",
  "session_id": "string",
  "action_id": "string",
  "text": "string",
  "context": {}
}
```

**Response Body:**

```json
{
  "success": true,
  "feedback_id": "string",
  "message": "string",
  "timestamp": "2025-11-08T12:00:00.000Z"
}
```

**cURL Example:**

```bash
curl -X POST "https://api.lukhas.ai/v1/feedback/text" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "user_123",
       "session_id": "session_456",
       "action_id": "decision_789",
       "text": "This was a great suggestion."
     }'
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}
data = {
    "user_id": "user_123",
    "session_id": "session_456",
    "action_id": "decision_789",
    "text": "This was a great suggestion.",
}
response = requests.post("https://api.lukhas.ai/v1/feedback/text", headers=headers, json=data)
print(response.json())
```

---

#### PUT /feedback/edit

Edit existing feedback.

**Request Body:**

```json
{
  "feedback_id": "string",
  "user_id": "string",
  "new_content": {}
}
```

**Response Body:**

```json
{
  "success": true,
  "feedback_id": "string",
  "message": "string",
  "timestamp": "2025-11-08T12:00:00.000Z"
}
```

**cURL Example:**

```bash
curl -X PUT "https://api.lukhas.ai/v1/feedback/edit" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "feedback_id": "feedback_123",
       "user_id": "user_123",
       "new_content": {"rating": 4}
     }'
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}
data = {
    "feedback_id": "feedback_123",
    "user_id": "user_123",
    "new_content": {"rating": 4},
}
response = requests.put("https://api.lukhas.ai/v1/feedback/edit", headers=headers, json=data)
print(response.json())
```

---

#### DELETE /feedback/{feedback_id}

Delete feedback.

**Response Body:**

```json
{
  "success": true,
  "feedback_id": "string",
  "message": "string",
  "timestamp": "2025-11-08T12:00:00.000Z"
}
```

**cURL Example:**

```bash
curl -X DELETE "https://api.lukhas.ai/v1/feedback/feedback_123?user_id=user_123" \
     -H "Authorization: Bearer YOUR_API_KEY"
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
feedback_id = "feedback_123"
user_id = "user_123"
headers = {"Authorization": f"Bearer {api_key}"}
response = requests.delete(f"https://api.lukhas.ai/v1/feedback/{feedback_id}?user_id={user_id}", headers=headers)
print(response.json())
```

---

#### GET /feedback/history/{user_id}

Get user's feedback history.

**Response Body:**

```json
{
  "user_id": "string",
  "feedback_items": [],
  "total_count": 0
}
```

**cURL Example:**

```bash
curl -X GET "https://api.lukhas.ai/v1/feedback/history/user_123" \
     -H "Authorization: Bearer YOUR_API_KEY"
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
user_id = "user_123"
headers = {"Authorization": f"Bearer {api_key}"}
response = requests.get(f"https://api.lukhas.ai/v1/feedback/history/{user_id}", headers=headers)
print(response.json())
```

---

#### GET /feedback/summary/{action_id}

Get aggregated feedback summary for an action.

**Response Body:**

```json
{
  "action_id": "string",
  "total_feedback": 0,
  "average_rating": 0.0,
  "sentiment_distribution": {},
  "emoji_distribution": {},
  "common_themes": [],
  "improvement_suggestions": []
}
```

**cURL Example:**

```bash
curl -X GET "https://api.lukhas.ai/v1/feedback/summary/decision_789" \
     -H "Authorization: Bearer YOUR_API_KEY"
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
action_id = "decision_789"
headers = {"Authorization": f"Bearer {api_key}"}
response = requests.get(f"https://api.lukhas.ai/v1/feedback/summary/{action_id}", headers=headers)
print(response.json())
```

---

#### POST /consent

Update user consent preferences.

**Request Body:**

```json
{
  "user_id": "string",
  "consent_given": true,
  "region": "string",
  "allow_anonymized_usage": true,
  "data_retention_days": 0
}
```

**Response Body:**

```json
{
  "success": true,
  "message": "string",
  "user_id": "string",
  "consent_given": true
}
```

**cURL Example:**

```bash
curl -X POST "https://api.lukhas.ai/v1/consent" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "user_123",
       "consent_given": true,
       "region": "eu"
     }'
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}
data = {
    "user_id": "user_123",
    "consent_given": true,
    "region": "eu",
}
response = requests.post("https://api.lukhas.ai/v1/consent", headers=headers, json=data)
print(response.json())
```

---

#### GET /feedback/export/{user_id}

Export all user feedback data.

**cURL Example:**

```bash
curl -X GET "https://api.lukhas.ai/v1/feedback/export/user_123" \
     -H "Authorization: Bearer YOUR_API_KEY"
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
user_id = "user_123"
headers = {"Authorization": f"Bearer {api_key}"}
response = requests.get(f"https://api.lukhas.ai/v1/feedback/export/{user_id}", headers=headers)
print(response.json())
```

---

#### GET /feedback/report

Generate feedback analytics report.

**cURL Example:**

```bash
curl -X GET "https://api.lukhas.ai/v1/feedback/report?start_date=2025-11-01T00:00:00Z&end_date=2025-11-08T00:00:00Z" \
     -H "Authorization: Bearer YOUR_API_KEY"
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
headers = {"Authorization": f"Bearer {api_key}"}
params = {
    "start_date": "2025-11-01T00:00:00Z",
    "end_date": "2025-11-08T00:00:00Z",
}
response = requests.get("https://api.lukhas.ai/v1/feedback/report", headers=headers, params=params)
print(response.json())
```

---

#### GET /status

Get feedback system status.

**cURL Example:**

```bash
curl -X GET "https://api.lukhas.ai/v1/status" \
     -H "Authorization: Bearer YOUR_API_KEY"
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
headers = {"Authorization": f"Bearer {api_key}"}
response = requests.get("https://api.lukhas.ai/v1/status", headers=headers)
print(response.json())
```

---

#### GET /health

Health check endpoint.

**cURL Example:**

```bash
curl -X GET "https://api.lukhas.ai/v1/health" \
     -H "Authorization: Bearer YOUR_API_KEY"
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
headers = {"Authorization": f"Bearer {api_key}"}
response = requests.get("https://api.lukhas.ai/v1/health", headers=headers)
print(response.json())
```

### Universal Language API

The Universal Language API provides endpoints for multi-modal language processing and high-entropy password generation.

#### POST /api/v1/symbols/understand

Understand multi-modal symbolic input.

**Request Body:**

```json
{
  "input": {
    "text": "string",
    "emoji": "string",
    "image_url": "string",
    "audio_url": "string",
    "gesture_sequence": []
  },
  "context": {},
  "user_id": "string"
}
```

**Response Body:**

```json
{
  "meaning": "string",
  "confidence": 0.0,
  "universal_symbol": "string",
  "entropy_bits": 0.0,
  "metadata": {}
}
```

**cURL Example:**

```bash
curl -X POST "https://api.lukhas.ai/v1/api/v1/symbols/understand" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "input": {
         "text": "Hello, world!"
       },
       "user_id": "user_123"
     }'
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}
data = {
    "input": {
        "text": "Hello, world!"
    },
    "user_id": "user_123",
}
response = requests.post("https://api.lukhas.ai/v1/api/v1/symbols/understand", headers=headers, json=data)
print(response.json())
```

---

#### POST /api/v1/password/generate

Generate high-entropy password using multi-modal elements.

**Request Body:**

```json
{
  "entropy_bits": 0,
  "modalities": [],
  "memorability_score": 0.0,
  "user_preferences": {}
}
```

**Response Body:**

```json
{
  "password_elements": {},
  "entropy_bits": 0.0,
  "memorability_score": 0.0,
  "strength_rating": "string",
  "cracking_time_estimate": "string"
}
```

**cURL Example:**

```bash
curl -X POST "https://api.lukhas.ai/v1/api/v1/password/generate" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "entropy_bits": 128
     }'
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}
data = {"entropy_bits": 128}
response = requests.post("https://api.lukhas.ai/v1/api/v1/password/generate", headers=headers, json=data)
print(response.json())
```

---

#### POST /api/v1/exchange/initiate

Initiate privacy-preserving symbol exchange.

**Request Body:**

```json
{
  "participants": [],
  "protocol": "string",
  "privacy_level": "string"
}
```

**Response Body:**

```json
{
  "session_id": "string",
  "participants": [],
  "protocol": "string",
  "privacy_level": "string",
  "status": "string"
}
```

**cURL Example:**

```bash
curl -X POST "https://api.lukhas.ai/v1/api/v1/exchange/initiate" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "participants": ["user_123", "user_456"]
     }'
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}
data = {"participants": ["user_123", "user_456"]}
response = requests.post("https://api.lukhas.ai/v1/api/v1/exchange/initiate", headers=headers, json=data)
print(response.json())
```

---

#### POST /api/v1/language/build

Build universal language element from multi-modal inputs.

**Request Body:**

```json
{
  "words": [],
  "symbols": [],
  "images": [],
  "sounds": [],
  "gestures": [],
  "target_meaning": "string"
}
```

**Response Body:**

```json
{
  "target_meaning": "string",
  "universal_symbol": "string",
  "confidence": 0.0,
  "entropy_contribution": 0.0,
  "input_modalities": 0,
  "status": "string"
}
```

**cURL Example:**

```bash
curl -X POST "https://api.lukhas.ai/v1/api/v1/language/build" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "words": ["love", "compassion"],
       "symbols": ["❤️"],
       "target_meaning": "Unconditional positive regard"
     }'
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}
data = {
    "words": ["love", "compassion"],
    "symbols": ["❤️"],
    "target_meaning": "Unconditional positive regard",
}
response = requests.post("https://api.lukhas.ai/v1/api/v1/language/build", headers=headers, json=data)
print(response.json())
```

---

#### POST /api/v1/colony/consensus

Request colony consensus on a proposal.

**Request Body:**

```json
{
  "proposal": "string",
  "method": "string",
  "urgency": 0.0,
  "participants": []
}
```

**Response Body:**

```json
{
  "proposal": "string",
  "decision": "string",
  "confidence": 0.0,
  "method_used": "string",
  "urgency_level": 0.0,
  "processing_time": 0.0,
  "consensus_reached": true
}
```

**cURL Example:**

```bash
curl -X POST "https://api.lukhas.ai/v1/api/v1/colony/consensus" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "proposal": "Adopt new ethical guideline"
     }'
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}
data = {"proposal": "Adopt new ethical guideline"}
response = requests.post("https://api.lukhas.ai/v1/api/v1/colony/consensus", headers=headers, json=data)
print(response.json())
```

---

#### GET /api/v1/stats

Get system statistics.

**cURL Example:**

```bash
curl -X GET "https://api.lukhas.ai/v1/api/v1/stats" \
     -H "Authorization: Bearer YOUR_API_KEY"
```

**Python Example:**

```python
import requests

api_key = "YOUR_API_KEY"
headers = {"Authorization": f"Bearer {api_key}"}
response = requests.get("https://api.lukhas.ai/v1/api/v1/stats", headers=headers)
print(response.json())
```

## Error Codes

| Code | Description |
|---|---|
| 400 | Bad Request -- The request was improperly formatted. |
| 401 | Unauthorized -- The request requires user authentication. |
| 403 | Forbidden -- The authenticated user does not have access to the specified resource. |
| 404 | Not Found -- The requested resource does not exist. |
| 429 | Too Many Requests -- The user has sent too many requests in a given amount of time. |
| 500 | Internal Server Error -- An unexpected condition was encountered. |
