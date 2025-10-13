/**
 * LUKHAS API TypeScript Client Types
 * OpenAI-compatible type definitions
 */

export interface LukhasConfig {
    apiKey: string;
    baseURL?: string;
    timeout?: number;
    defaultHeaders?: Record<string, string>;
}

export interface ResponseRequest {
    prompt: string;
    max_tokens?: number;
    temperature?: number;
    top_p?: number;
    n?: number;
    stream?: boolean;
    stop?: string | string[];
    presence_penalty?: number;
    frequency_penalty?: number;
    user?: string;
}

export interface Choice {
    text: string;
    index: number;
    logprobs?: any | null;
    finish_reason: string;
}

export interface Usage {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
}

export interface ResponseObject {
    id: string;
    object: 'text_completion';
    created: number;
    model: string;
    choices: Choice[];
    usage: Usage;
}

export interface ChatMessage {
    role: 'system' | 'user' | 'assistant';
    content: string;
    name?: string;
}

export interface ChatCompletionRequest {
    model: string;
    messages: ChatMessage[];
    temperature?: number;
    top_p?: number;
    n?: number;
    stream?: boolean;
    stop?: string | string[];
    max_tokens?: number;
    presence_penalty?: number;
    frequency_penalty?: number;
    user?: string;
}

export interface ChatCompletionResponse {
    id: string;
    object: 'chat.completion';
    created: number;
    model: string;
    choices: Array<{
        index: number;
        message: ChatMessage;
        finish_reason: string;
    }>;
    usage: Usage;
}

export interface SearchRequest {
    query: string;
    index_name?: string;
    top_k?: number;
    threshold?: number;
    filter?: Record<string, any>;
}

export interface SearchResult {
    id: string;
    score: number;
    metadata: Record<string, any>;
    content?: string;
}

export interface SearchResponse {
    results: SearchResult[];
    total: number;
    query: string;
    index_name: string;
}

export interface DreamRequest {
    scenario: string;
    num_paths?: number;
    depth?: number;
    temperature?: number;
    guidance?: string[];
}

export interface DreamPath {
    id: string;
    score: number;
    steps: string[];
    outcome: string;
    confidence: number;
}

export interface DreamResponse {
    id: string;
    scenario: string;
    paths: DreamPath[];
    recommended_path?: string;
    insights: string[];
}

export interface LukhasError {
    error: {
        message: string;
        type: string;
        param: string | null;
        code: string;
    };
}

export interface StreamChunk {
    id: string;
    object: 'text_completion.chunk' | 'chat.completion.chunk';
    created: number;
    model: string;
    choices: Array<{
        index: number;
        delta?: {
            content?: string;
            role?: string;
        };
        text?: string;
        finish_reason?: string | null;
    }>;
}

export interface TraceHeaders {
    'x-trace-id'?: string;
    'x-request-id'?: string;
}
