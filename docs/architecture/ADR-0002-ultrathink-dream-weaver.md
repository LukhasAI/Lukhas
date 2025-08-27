# ADR-0002: "Ultrathink" Dream Weaver Architecture

**Status**: Proposed
**Date**: 2025-08-26

## Context

We are building the "Dream Weaver," an advanced feature that allows users to provide a "dream seed" (a word or phrase) and receive a multi-sensory, generative 3D "dream" in response. This feature requires a robust, orchestrated flow that leverages both the internal LUKHAS AI components and external OpenAI services. This document outlines the proposed architecture for this feature.

## Objective

To create a seamless, real-time experience that:
1.  Captures user input (text or voice).
2.  Orchestrates a "Cognitive Cascade" involving LUKHAS and OpenAI services.
3.  Generates a unique, multi-sensory (visual, auditory) dream experience.
4.  Persists the generated dream as a new memory within the LUKHAS system.

## High-Level Data Flow

Here is a step-by-step breakdown of the data flow:

1.  **User Input (Frontend)**: The user provides a "dream seed" (e.g., "a city made of glass") via a text input or voice (transcribed by OpenAI Whisper).
2.  **API Request (Frontend -> Backend)**: The frontend sends the dream seed to the `/api/dream-weaver` endpoint.
3.  **Orchestration (Backend - Dream Orchestrator)**: The API triggers the `dream_orchestrator.py` module.
4.  **Cognitive Cascade (Orchestrator -> Services)**:
    a. **Memory Query**: The orchestrator queries `lukhas/memory` to find concepts related to the dream seed.
    b. **GPT-4 Prompting**: It combines the dream seed and related concepts into a prompt for OpenAI's GPT-4.
    c. **Dream Manifest Generation**: GPT-4 returns a structured JSON object called the "Dream Manifest." This manifest contains parameters for the visualization (e.g., `{"geometry": "shards", "color_palette": ["#a0a0ff", "#ffffff"], "movement": "pulsing"}`) and a short, poetic narrative.
    d. **DALL-E 3 Texture Generation**: The orchestrator uses a part of the narrative to prompt DALL-E 3, generating a unique texture image.
    e. **TTS Audio Generation**: The orchestrator sends the full narrative to OpenAI's TTS service to create a whispered audio track.
    f. **Guardian Check**: The generated text and image URLs are passed to `lukhas/guardian` for a final safety check.
5.  **Response to Frontend (Backend -> Frontend)**: The orchestrator returns the Dream Manifest, the texture URL, and the audio URL to the frontend.
6.  **Dream Rendering (Frontend)**: The frontend uses `react-three-fiber` to render the 3D scene based on the Dream Manifest, applies the DALL-E texture, and plays the audio.
7.  **Memory Persistence (Frontend -> Backend)**: After the dream is viewed, the user can choose to "crystallize" it. This sends the Dream Manifest back to the backend.
8.  **Store Memory (Backend)**: A final API call stores the Dream Manifest as a new, permanent memory in the `lukhas/memory` system.

## Core Components

*   **Frontend**: `lukhas_website` (Next.js, React, react-three-fiber)
*   **Backend API**: `lukhas_website/app/api/dream-weaver/route.ts`
*   **Orchestrator**: `candidate/orchestration/dream_orchestrator.py`
*   **LUKHAS Modules**: `lukhas/memory`, `lukhas/guardian`
*   **OpenAI Services**: Whisper, GPT-4, DALL-E 3, TTS

## Data Models

### Dream Seed (Client -> Server)
```json
{
  "text": "a city made of glass"
}
```

### Dream Manifest (Server -> Client)
```json
{
  "narrative": "In the quiet corners of the mind, a metropolis of crystal rises, its towers catching the light of forgotten stars.",
  "visuals": {
    "geometry": "shards",
    "movement": "slow_pulse",
    "colors": ["#E0E0FF", "#FFFFFF", "#A0A0FF"],
    "particle_count": 500
  },
  "audio_url": "https://cdn.openai.com/.../audio.mp3",
  "texture_url": "https://cdn.openai.com/.../image.png",
  "dream_id": "dream_abc123"
}
```

## Flow Diagram

```
[User] --(1. Dream Seed)--> [Frontend]
   ^                               |
   |--(6. Render Dream)------------+
   |
[Frontend] --(2. API Request)--> [Backend API]
   ^                                    |
   |                                    v
   +----(5. Return Manifest)---- [Dream Orchestrator]
                                        |
                  +---------------------+---------------------+
                  | (4a. Query)         | (4f. Check)         |
                  v                     v                     v (4b,c,d,e. API Calls)
              [LUKHAS Memory]    [LUKHAS Guardian]    [OpenAI Services]
                  ^
                  | (8. Store Memory)
                  +------------------ [Backend API] <--(7. Crystallize)-- [Frontend]

```
