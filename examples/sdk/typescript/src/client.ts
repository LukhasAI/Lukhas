/**
 * LUKHAS API TypeScript Client
 * OpenAI-compatible client with full TypeScript support
 */

import axios, { AxiosInstance, AxiosResponse } from 'axios';
import EventSource from 'eventsource';
import {
    ChatCompletionRequest,
    ChatCompletionResponse,
    DreamRequest,
    DreamResponse,
    LukhasConfig,
    LukhasError,
    ResponseObject,
    ResponseRequest,
    SearchRequest,
    SearchResponse,
    StreamChunk,
    TraceHeaders,
} from './types';

export class LukhasClient {
    private client: AxiosInstance;
    private apiKey: string;
    private baseURL: string;

    constructor(config: LukhasConfig) {
        this.apiKey = config.apiKey;
        this.baseURL = config.baseURL || 'https://api.lukhas.ai';

        this.client = axios.create({
            baseURL: this.baseURL,
            timeout: config.timeout || 30000,
            headers: {
                'Authorization': `Bearer ${this.apiKey}`,
                'Content-Type': 'application/json',
                ...config.defaultHeaders,
            },
        });

        // Response interceptor for trace headers
        this.client.interceptors.response.use(
            (response) => {
                // Extract and log trace ID for debugging
                const traceId = response.headers['x-trace-id'];
                if (traceId) {
                    console.log(`[LUKHAS] Trace ID: ${traceId}`);
                }
                return response;
            },
            (error) => {
                // Handle errors with OpenAI-compatible format
                if (error.response) {
                    const lukhasError = error.response.data as LukhasError;
                    const traceId = error.response.headers['x-trace-id'];
                    throw new Error(
                        `LUKHAS API Error [${traceId || 'no-trace'}]: ${lukhasError.error.message} (${lukhasError.error.code})`
                    );
                }
                throw error;
            }
        );
    }

    /**
     * Create a response (text completion)
     * @param request - Response request parameters
     * @returns Promise<ResponseObject>
     */
    async createResponse(request: ResponseRequest): Promise<ResponseObject> {
        const idempotencyKey = `req-${Date.now()}-${Math.random().toString(36).substring(7)}`;

        const response: AxiosResponse<ResponseObject> = await this.client.post(
            '/v1/responses',
            request,
            {
                headers: {
                    'Idempotency-Key': idempotencyKey,
                },
            }
        );

        return response.data;
    }

    /**
     * Create a chat completion
     * @param request - Chat completion request parameters
     * @returns Promise<ChatCompletionResponse>
     */
    async createChatCompletion(request: ChatCompletionRequest): Promise<ChatCompletionResponse> {
        const idempotencyKey = `chat-${Date.now()}-${Math.random().toString(36).substring(7)}`;

        const response: AxiosResponse<ChatCompletionResponse> = await this.client.post(
            '/v1/chat/completions',
            request,
            {
                headers: {
                    'Idempotency-Key': idempotencyKey,
                },
            }
        );

        return response.data;
    }

    /**
     * Search an index for similar vectors
     * @param request - Search request parameters
     * @returns Promise<SearchResponse>
     */
    async searchIndex(request: SearchRequest): Promise<SearchResponse> {
        const response: AxiosResponse<SearchResponse> = await this.client.post(
            '/v1/indexes/search',
            request
        );

        return response.data;
    }

    /**
     * Create a dream (scenario simulation)
     * @param request - Dream request parameters
     * @returns Promise<DreamResponse>
     */
    async createDream(request: DreamRequest): Promise<DreamResponse> {
        const idempotencyKey = `dream-${Date.now()}-${Math.random().toString(36).substring(7)}`;

        const response: AxiosResponse<DreamResponse> = await this.client.post(
            '/v1/dreams',
            request,
            {
                headers: {
                    'Idempotency-Key': idempotencyKey,
                },
            }
        );

        return response.data;
    }

    /**
     * Stream a response (SSE)
     * @param request - Response request with stream=true
     * @param onChunk - Callback for each chunk
     * @param onDone - Callback when stream completes
     * @param onError - Callback for errors
     */
    async streamResponse(
        request: ResponseRequest,
        onChunk: (chunk: StreamChunk) => void,
        onDone?: (traceId?: string) => void,
        onError?: (error: Error) => void
    ): Promise<void> {
        return new Promise((resolve, reject) => {
            const idempotencyKey = `stream-${Date.now()}-${Math.random().toString(36).substring(7)}`;
            const url = `${this.baseURL}/v1/responses`;

            const eventSource = new EventSource(url, {
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`,
                    'Content-Type': 'application/json',
                    'Idempotency-Key': idempotencyKey,
                },
            });

            let traceId: string | undefined;

            eventSource.onmessage = (event) => {
                try {
                    const chunk: StreamChunk = JSON.parse(event.data);
                    onChunk(chunk);

                    // Extract trace ID from first chunk
                    if (!traceId && event.lastEventId) {
                        traceId = event.lastEventId;
                    }
                } catch (error) {
                    const err = error as Error;
                    if (onError) {
                        onError(err);
                    }
                    reject(err);
                }
            };

            eventSource.onerror = (error) => {
                eventSource.close();
                const err = new Error('Stream error');
                if (onError) {
                    onError(err);
                }
                reject(err);
            };

            eventSource.addEventListener('done', () => {
                eventSource.close();
                if (onDone) {
                    onDone(traceId);
                }
                resolve();
            });
        });
    }

    /**
     * Extract trace headers from response
     * @param response - Axios response
     * @returns TraceHeaders
     */
    extractTraceHeaders(response: AxiosResponse): TraceHeaders {
        return {
            'x-trace-id': response.headers['x-trace-id'],
            'x-request-id': response.headers['x-request-id'],
        };
    }

    /**
     * Health check
     * @returns Promise<{ status: string }>
     */
    async health(): Promise<{ status: string }> {
        const response = await this.client.get('/health');
        return response.data;
    }
}

export * from './types';
