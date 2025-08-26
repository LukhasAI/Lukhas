# API Specification: Voice-Reactive AI Interface

## Overview
This document defines the API specifications for the voice-reactive AI interface system, including voice processing, AI integration, shape generation, and real-time communication.

## Base URL
```
Production: https://api.voicereactive.ai/v1
Staging: https://staging-api.voicereactive.ai/v1
Development: http://localhost:3000/v1
```

## Authentication
All API requests require authentication using API keys or JWT tokens.

### Headers
```
Authorization: Bearer <jwt_token>
X-API-Key: <api_key>
Content-Type: application/json
```

## Core Endpoints

### 1. Voice Processing API

#### 1.1 Start Voice Session
```http
POST /voice/session/start
```

**Request Body:**
```json
{
  "deviceId": "string",
  "platform": "ios|android|web|desktop",
  "audioConfig": {
    "sampleRate": 44100,
    "channels": 1,
    "bitDepth": 16
  },
  "voiceAnalysis": {
    "emotionDetection": true,
    "pitchAnalysis": true,
    "speechRecognition": true
  }
}
```

**Response:**
```json
{
  "sessionId": "uuid",
  "status": "active",
  "websocketUrl": "wss://api.voicereactive.ai/voice/stream",
  "expiresAt": "2024-12-31T23:59:59Z"
}
```

#### 1.2 Stream Voice Data
```http
WebSocket /voice/stream
```

**Message Format:**
```json
{
  "type": "voice_data",
  "sessionId": "uuid",
  "timestamp": "2024-01-01T12:00:00Z",
  "audioData": "base64_encoded_audio",
  "metadata": {
    "volume": 0.75,
    "pitch": 0.6,
    "speechRate": 0.8
  }
}
```

**Response:**
```json
{
  "type": "voice_analysis",
  "sessionId": "uuid",
  "timestamp": "2024-01-01T12:00:00Z",
  "analysis": {
    "emotion": "happy",
    "confidence": 0.85,
    "pitch": 0.6,
    "volume": 0.75,
    "speechRate": 0.8,
    "transcription": "Hello, how are you?"
  }
}
```

#### 1.3 End Voice Session
```http
POST /voice/session/{sessionId}/end
```

**Response:**
```json
{
  "sessionId": "uuid",
  "status": "ended",
  "summary": {
    "duration": 300,
    "totalWords": 150,
    "emotions": ["happy", "excited", "calm"],
    "averagePitch": 0.65
  }
}
```

### 2. AI Integration API

#### 2.1 Send Message to AI
```http
POST /ai/chat
```

**Request Body:**
```json
{
  "sessionId": "uuid",
  "message": "string",
  "context": {
    "conversationHistory": [
      {
        "role": "user",
        "content": "Hello",
        "timestamp": "2024-01-01T12:00:00Z"
      }
    ],
    "voiceContext": {
      "emotion": "happy",
      "pitch": 0.6,
      "volume": 0.75
    },
    "shapeContext": {
      "currentShape": "sphere",
      "currentEmotion": "calm"
    }
  },
  "aiProvider": "openai|claude|azure|gemini",
  "options": {
    "stream": true,
    "maxTokens": 150,
    "temperature": 0.7
  }
}
```

**Response (Streaming):**
```json
{
  "type": "ai_response",
  "sessionId": "uuid",
  "messageId": "uuid",
  "content": "I'm doing great! How about you?",
  "shapeParameters": {
    "shapeType": "bounce",
    "scale": 1.2,
    "color": "#FFD700",
    "animation": "bounce",
    "emotion": "happy"
  },
  "metadata": {
    "aiProvider": "openai",
    "model": "gpt-4",
    "tokens": 25,
    "cost": 0.00075
  }
}
```

#### 2.2 Get AI Providers Status
```http
GET /ai/providers/status
```

**Response:**
```json
{
  "providers": [
    {
      "name": "openai",
      "status": "active",
      "responseTime": 1200,
      "costPer1kTokens": 0.03,
      "rateLimit": {
        "remaining": 95,
        "resetAt": "2024-01-01T13:00:00Z"
      }
    }
  ]
}
```

### 3. Shape Generation API

#### 3.1 Generate Shape Parameters
```http
POST /shapes/generate
```

**Request Body:**
```json
{
  "sessionId": "uuid",
  "context": {
    "aiResponse": "I'm excited to help you!",
    "voiceEmotion": "excited",
    "conversationMood": "positive"
  },
  "constraints": {
    "maxComplexity": 1000,
    "preferredShapes": ["bounce", "expand", "spiral"],
    "colorPalette": ["warm", "bright"]
  }
}
```

**Response:**
```json
{
  "shapeId": "uuid",
  "parameters": {
    "type": "bounce",
    "scale": 1.3,
    "color": "#FF6B6B",
    "animation": "bounce",
    "duration": 2.0,
    "complexity": 500
  },
  "metadata": {
    "generationTime": 150,
    "confidence": 0.92
  }
}
```

#### 3.2 Get Shape Library
```http
GET /shapes/library
```

**Response:**
```json
{
  "shapes": [
    {
      "id": "bounce",
      "name": "Bounce",
      "category": "emotional",
      "complexity": 300,
      "preview": "data:image/png;base64,..."
    }
  ],
  "categories": ["emotional", "geometric", "organic", "abstract"]
}
```

### 4. Real-time Communication API

#### 4.1 Join Chat Room
```http
POST /chat/rooms/{roomId}/join
```

**Request Body:**
```json
{
  "userId": "uuid",
  "sessionId": "uuid",
  "capabilities": {
    "voice": true,
    "shapeControl": true,
    "aiAccess": true
  }
}
```

**Response:**
```json
{
  "roomId": "uuid",
  "participants": [
    {
      "userId": "uuid",
      "username": "string",
      "capabilities": ["voice", "shapeControl"]
    }
  ],
  "websocketUrl": "wss://api.voicereactive.ai/chat/stream"
}
```

#### 4.2 Chat Stream
```http
WebSocket /chat/stream
```

**Message Types:**
```json
// Voice message
{
  "type": "voice_message",
  "roomId": "uuid",
  "userId": "uuid",
  "audioData": "base64_encoded_audio",
  "timestamp": "2024-01-01T12:00:00Z"
}

// AI response
{
  "type": "ai_response",
  "roomId": "uuid",
  "userId": "uuid",
  "content": "string",
  "shapeParameters": {...},
  "timestamp": "2024-01-01T12:00:00Z"
}

// Shape change
{
  "type": "shape_change",
  "roomId": "uuid",
  "userId": "uuid",
  "shapeParameters": {...},
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 5. User Management API

#### 5.1 Create User
```http
POST /users
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "string",
  "platform": "ios|android|web|desktop",
  "preferences": {
    "aiProvider": "openai",
    "voiceSensitivity": 0.7,
    "shapeComplexity": "medium"
  }
}
```

**Response:**
```json
{
  "userId": "uuid",
  "apiKey": "string",
  "status": "active",
  "createdAt": "2024-01-01T12:00:00Z"
}
```

#### 5.2 Get User Profile
```http
GET /users/{userId}
```

**Response:**
```json
{
  "userId": "uuid",
  "email": "user@example.com",
  "username": "string",
  "stats": {
    "totalSessions": 150,
    "totalVoiceTime": 7200,
    "favoriteShapes": ["bounce", "spiral"],
    "aiInteractions": 500
  },
  "preferences": {
    "aiProvider": "openai",
    "voiceSensitivity": 0.7,
    "shapeComplexity": "medium"
  }
}
```

### 6. Analytics API

#### 6.1 Get Usage Analytics
```http
GET /analytics/usage
```

**Query Parameters:**
- `startDate`: ISO date string
- `endDate`: ISO date string
- `granularity`: hour|day|week|month

**Response:**
```json
{
  "period": {
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-01-31T23:59:59Z"
  },
  "metrics": {
    "totalSessions": 1500,
    "totalVoiceTime": 72000,
    "aiRequests": 5000,
    "shapeGenerations": 3000,
    "averageSessionDuration": 480
  },
  "costs": {
    "totalCost": 150.50,
    "costByProvider": {
      "openai": 120.30,
      "claude": 30.20
    }
  }
}
```

## Data Models

### VoiceData
```typescript
interface VoiceData {
  sessionId: string;
  timestamp: string;
  audioData: string; // base64 encoded
  metadata: {
    volume: number; // 0-1
    pitch: number; // 0-1
    speechRate: number; // 0-1
    emotion?: string;
    transcription?: string;
  };
}
```

### AIResponse
```typescript
interface AIResponse {
  messageId: string;
  sessionId: string;
  content: string;
  shapeParameters: ShapeParameters;
  metadata: {
    aiProvider: string;
    model: string;
    tokens: number;
    cost: number;
    responseTime: number;
  };
}
```

### ShapeParameters
```typescript
interface ShapeParameters {
  type: string;
  scale: number; // 0.5-2.0
  color: string; // hex color
  animation: string;
  duration: number; // seconds
  complexity: number; // vertices
  emotion?: string;
}
```

### ChatMessage
```typescript
interface ChatMessage {
  messageId: string;
  roomId: string;
  userId: string;
  type: 'voice' | 'text' | 'ai_response' | 'shape_change';
  content?: string;
  audioData?: string;
  shapeParameters?: ShapeParameters;
  timestamp: string;
}
```

## Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {},
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### Common Error Codes
- `AUTH_REQUIRED`: Authentication required
- `INVALID_API_KEY`: Invalid API key
- `RATE_LIMITED`: Rate limit exceeded
- `VOICE_PROCESSING_ERROR`: Voice processing failed
- `AI_PROVIDER_ERROR`: AI provider error
- `SHAPE_GENERATION_ERROR`: Shape generation failed
- `SESSION_EXPIRED`: Session expired
- `INVALID_REQUEST`: Invalid request format

## Rate Limiting

### Limits
- **Voice API**: 100 requests/minute per user
- **AI API**: 50 requests/minute per user
- **Shape API**: 200 requests/minute per user
- **Chat API**: 1000 messages/minute per room

### Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## WebSocket Events

### Connection Events
```javascript
// Connect
socket.emit('connect', { sessionId: 'uuid' });

// Disconnect
socket.on('disconnect', (reason) => {
  console.log('Disconnected:', reason);
});

// Error
socket.on('error', (error) => {
  console.error('WebSocket error:', error);
});
```

### Voice Events
```javascript
// Send voice data
socket.emit('voice_data', {
  sessionId: 'uuid',
  audioData: 'base64_encoded_audio',
  metadata: { volume: 0.75, pitch: 0.6 }
});

// Receive voice analysis
socket.on('voice_analysis', (data) => {
  console.log('Voice analysis:', data);
});
```

### Chat Events
```javascript
// Join room
socket.emit('join_room', { roomId: 'uuid' });

// Send message
socket.emit('send_message', {
  roomId: 'uuid',
  type: 'voice',
  audioData: 'base64_encoded_audio'
});

// Receive message
socket.on('message', (data) => {
  console.log('New message:', data);
});
```

## SDK Examples

### JavaScript/TypeScript
```javascript
import { VoiceReactiveAPI } from '@voicereactive/sdk';

const api = new VoiceReactiveAPI({
  apiKey: 'your-api-key',
  baseUrl: 'https://api.voicereactive.ai/v1'
});

// Start voice session
const session = await api.voice.startSession({
  deviceId: 'device-123',
  platform: 'web'
});

// Send AI message
const response = await api.ai.sendMessage({
  sessionId: session.sessionId,
  message: 'Hello, how are you?'
});

// Generate shape
const shape = await api.shapes.generate({
  sessionId: session.sessionId,
  context: { aiResponse: response.content }
});
```

### Swift (iOS)
```swift
import VoiceReactiveSDK

let api = VoiceReactiveAPI(apiKey: "your-api-key")

// Start voice session
let session = try await api.voice.startSession(
  deviceId: "device-123",
  platform: .ios
)

// Send AI message
let response = try await api.ai.sendMessage(
  sessionId: session.sessionId,
  message: "Hello, how are you?"
)

// Generate shape
let shape = try await api.shapes.generate(
  sessionId: session.sessionId,
  context: ["aiResponse": response.content]
)
```

### Kotlin (Android)
```kotlin
import com.voicereactive.sdk.VoiceReactiveAPI

val api = VoiceReactiveAPI(apiKey = "your-api-key")

// Start voice session
val session = api.voice.startSession(
  deviceId = "device-123",
  platform = Platform.ANDROID
)

// Send AI message
val response = api.ai.sendMessage(
  sessionId = session.sessionId,
  message = "Hello, how are you?"
)

// Generate shape
val shape = api.shapes.generate(
  sessionId = session.sessionId,
  context = mapOf("aiResponse" to response.content)
)
```

## Testing

### Postman Collection
Download the complete Postman collection: [VoiceReactive API Collection](https://api.voicereactive.ai/docs/postman-collection.json)

### Test Environment
- **Base URL**: https://staging-api.voicereactive.ai/v1
- **Test API Key**: `test_key_123456789`
- **Test User ID**: `test_user_123`

### Example Test Requests
```bash
# Test voice session
curl -X POST https://staging-api.voicereactive.ai/v1/voice/session/start \
  -H "Authorization: Bearer test_key_123456789" \
  -H "Content-Type: application/json" \
  -d '{
    "deviceId": "test-device",
    "platform": "web",
    "audioConfig": {
      "sampleRate": 44100,
      "channels": 1,
      "bitDepth": 16
    }
  }'
```

## Versioning

### API Versioning
- **Current Version**: v1
- **Version Header**: `X-API-Version: 1`
- **Deprecation Policy**: 6 months notice for breaking changes

### Changelog
- **v1.0.0**: Initial release
- **v1.1.0**: Added real-time collaboration features
- **v1.2.0**: Enhanced voice analysis capabilities

## Support

### Documentation
- **API Docs**: https://api.voicereactive.ai/docs
- **SDK Docs**: https://docs.voicereactive.ai
- **Examples**: https://github.com/voicereactive/examples

### Support Channels
- **Email**: api-support@voicereactive.ai
- **Discord**: https://discord.gg/voicereactive
- **GitHub Issues**: https://github.com/voicereactive/api/issues
