/**
 * API client for Dream Engine
 */
import { DreamRequest, DreamResponse } from '../types/dream';

const API_BASE = '/api';

export class DreamAPIError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public response?: any
  ) {
    super(message);
    this.name = 'DreamAPIError';
  }
}

/**
 * Process a dream through the Dream Engine
 */
export const processDream = async (request: DreamRequest): Promise<DreamResponse> => {
  try {
    const response = await fetch(`${API_BASE}/dream/process`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new DreamAPIError(
        error.message || 'Failed to process dream',
        response.status,
        error
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof DreamAPIError) {
      throw error;
    }
    throw new DreamAPIError('Network error: ' + (error as Error).message);
  }
};

/**
 * Stream dream processing with real-time updates
 */
export const streamDreamProcessing = (
  request: DreamRequest,
  onUpdate: (partial: Partial<DreamResponse>) => void,
  onComplete: (result: DreamResponse) => void,
  onError: (error: Error) => void
): (() => void) => {
  const ws = new WebSocket('ws://localhost:8000/dream/stream');

  ws.onopen = () => {
    ws.send(JSON.stringify(request));
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);

      if (data.status === 'complete') {
        onComplete(data.result);
        ws.close();
      } else if (data.status === 'update') {
        onUpdate(data.partial);
      } else if (data.status === 'error') {
        onError(new DreamAPIError(data.message));
        ws.close();
      }
    } catch (error) {
      onError(error as Error);
    }
  };

  ws.onerror = (event) => {
    onError(new DreamAPIError('WebSocket error'));
  };

  // Return cleanup function
  return () => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.close();
    }
  };
};

/**
 * Fetch example dreams for demonstration
 */
export const getExampleDreams = async (): Promise<string[]> => {
  return [
    "I was flying over a vast ocean, feeling completely free and weightless. The water below shimmered with golden light.",
    "In a dark forest, I found a glowing door. When I opened it, I saw my childhood home filled with warm light.",
    "I was solving an impossible puzzle made of stars. Each piece I placed created beautiful music.",
    "Standing at the edge of a cliff, I looked down to see clouds forming the shapes of my memories."
  ];
};
