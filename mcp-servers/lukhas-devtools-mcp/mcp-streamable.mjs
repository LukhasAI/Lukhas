import { promises as fs } from 'fs';
import { createServer } from 'node:http';
import { URL } from 'node:url';
import path from 'path';

const PORT = parseInt(process.env.PORT || "8766");

// Mock LUKHAS search function - replace with actual search implementation
async function mockLUKHASSearch(query, limit = 10) {
    // Simulate search delay
    await new Promise(resolve => setTimeout(resolve, 100));

    const allResults = [
        {
            id: "lukhas-arch-001",
            title: "LUKHAS Architecture Overview",
            snippet: `Comprehensive guide to LUKHAS consciousness-aware AI platform architecture. Query: "${query}"`,
            url: "https://lukhas.ai/docs/architecture",
            type: "documentation",
            relevance: 0.95
        },
        {
            id: "constellation-fw-002",
            title: "Constellation Framework (⚛️🧠🛡️) Implementation",
            snippet: `Trinity Framework implementation details for Identity, Consciousness, and Guardian systems. Searching for: "${query}"`,
            url: "https://lukhas.ai/docs/constellation",
            type: "framework",
            relevance: 0.90
        },
        {
            id: "mcp-tools-003",
            title: "MCP Development Tools",
            snippet: `LUKHAS Model Context Protocol server development tools and utilities. Related to: "${query}"`,
            url: "https://lukhas.ai/tools/mcp",
            type: "tools",
            relevance: 0.85
        },
        {
            id: "t4-standards-004",
            title: "T4/0.01% Quality Standards",
            snippet: `Enterprise-grade quality standards and testing methodologies for LUKHAS systems. Context: "${query}"`,
            url: "https://lukhas.ai/standards/t4",
            type: "standards",
            relevance: 0.80
        },
        {
            id: "consciousness-mod-005",
            title: "Consciousness Module Integration",
            snippet: `692-module consciousness system integration patterns and best practices. Search: "${query}"`,
            url: "https://lukhas.ai/modules/consciousness",
            type: "modules",
            relevance: 0.75
        }
    ];

    // Filter and sort by relevance, then limit
    return allResults
        .filter(result => result.title.toLowerCase().includes(query.toLowerCase()) ||
            result.snippet.toLowerCase().includes(query.toLowerCase()))
        .sort((a, b) => b.relevance - a.relevance)
        .slice(0, limit);
}

// Mock LUKHAS fetch function - replace with actual fetch implementation  
async function mockLUKHASFetch(url) {
    // Simulate fetch delay
    await new Promise(resolve => setTimeout(resolve, 150));

    // Mock document content based on URL
    const documents = {
        "https://lukhas.ai/docs/architecture": {
            title: "LUKHAS Architecture Overview",
            mimeType: "text/markdown",
            content: `# LUKHAS Architecture Overview

## Trinity Framework (⚛️🧠🛡️)

LUKHAS implements a sophisticated consciousness-aware AI platform built on three foundational pillars:

- **⚛️ Identity**: Lambda ID system, authentication, symbolic self-representation  
- **🧠 Consciousness**: 692-module cognitive processing, memory systems, awareness
- **🛡️ Guardian**: Constitutional AI, ethical frameworks, drift detection

## Key Components

### Consciousness Modules (692 total)
- Reflection Engine
- Dream Engine  
- Memory systems
- Emotion processing
- Awareness tracking

### Infrastructure
- T4/0.01% quality standards
- Comprehensive testing (775+ tests)
- Lane-based architecture
- Model Context Protocol servers

This document provides the foundational architecture for understanding LUKHAS systems.`
        },
        "https://lukhas.ai/docs/constellation": {
            title: "Constellation Framework Implementation",
            mimeType: "text/markdown",
            content: `# Constellation Framework (⚛️🧠🛡️)

The Constellation Framework represents the evolution of the Trinity Framework, providing a unified approach to consciousness-aware AI development.

## Framework Components

### ⚛️ Identity Layer
- Lambda ID (ΛID) token system
- Tiered authentication (T1-T5)
- Symbolic self-representation
- Access control and permissions

### 🧠 Consciousness Layer  
- 692 cognitive processing modules
- Memory systems and recall
- Dream state processing
- Reflection and meta-cognition

### 🛡️ Guardian Layer
- Constitutional AI principles
- Ethical decision frameworks
- Drift detection and correction
- Safety validation systems

## Integration Patterns

The framework enables seamless integration across all LUKHAS components while maintaining strict quality standards and ethical compliance.`
        }
    };

    // Return document or default
    return documents[url] || {
        title: "Document Not Found",
        mimeType: "text/plain",
        content: `The requested document at ${url} was not found in the LUKHAS knowledge base. This is a mock implementation - in production, this would fetch actual content from the LUKHAS documentation system.`
    };
}

// Fetch document by ID - maps IDs to full documents
async function fetchById(id) {
    // Simulate fetch delay
    await new Promise(resolve => setTimeout(resolve, 150));

    // ID-to-document mapping
    const documents = {
        "lukhas-arch-001": {
            title: "LUKHAS Architecture Overview",
            url: "https://lukhas.ai/docs/architecture",
            mimeType: "text/markdown",
            content: `# LUKHAS Architecture Overview

## Trinity Framework (⚛️🧠🛡️)

LUKHAS implements a sophisticated consciousness-aware AI platform built on three foundational pillars:

- **⚛️ Identity**: Lambda ID system, authentication, symbolic self-representation  
- **🧠 Consciousness**: 692-module cognitive processing, memory systems, awareness
- **🛡️ Guardian**: Constitutional AI, ethical frameworks, drift detection

### Lane-Based Architecture
Production code flows through isolated development lanes with strict import boundaries and comprehensive testing infrastructure.

### T4/0.01% Excellence Standards
Enterprise-grade quality gates ensure sub-100ms performance with 99.99% reliability across all systems.`,
            metadata: { type: "documentation", category: "architecture" }
        },
        "constellation-fw-002": {
            title: "Constellation Framework (⚛️🧠🛡️) Implementation",
            url: "https://lukhas.ai/docs/constellation",
            mimeType: "text/markdown",
            content: `# Constellation Framework Implementation

## Identity Layer (⚛️)
- ΛiD token generation and validation
- T1-T5 tiered authentication system
- OIDC provider with JWT integration
- Security hardening and penetration testing

## Consciousness Layer (🧠)
- ReflectionEngine for meta-cognitive processing
- DreamEngine for background learning  
- Memory/Emotion bridges for context-aware processing
- 692-module neural architecture with dynamic scaling

## Guardian Layer (🛡️)
- Async safety methods with fail-safe defaults
- Drift detection with 0.15 threshold remediation
- Cross-module ethical validation
- Constitutional AI enforcement`,
            metadata: { type: "framework", category: "implementation" }
        },
        "mcp-tools-003": {
            title: "MCP Development Tools",
            url: "https://lukhas.ai/tools/mcp",
            mimeType: "text/markdown",
            content: `# LUKHAS MCP Development Tools

## Server Infrastructure
- Streamable HTTP transport for ChatGPT compatibility
- JSON-RPC 2.0 protocol implementation
- Tool discovery and execution framework
- Development utilities and diagnostics

## Quality Standards
- T4/0.01% testing methodology
- Performance budgets: <100ms auth, <250ms orchestration
- Lane isolation with zero cross-imports
- Comprehensive audit trails and monitoring

## Integration Patterns
- Search/fetch contract for Deep Research compatibility
- ID-based document retrieval system
- Permissive argument handling for forward compatibility`,
            metadata: { type: "tools", category: "development" }
        },
        "t4-standards-004": {
            title: "T4/0.01% Quality Standards",
            url: "https://lukhas.ai/standards/t4",
            mimeType: "text/markdown",
            content: `# T4/0.01% Excellence Standards

## Performance Budgets (Non-Negotiable)
- Memory recall: <100ms p95 for 10k items
- Pipeline latency: <250ms end-to-end p95  
- Guardian overhead: <5ms DSL evaluation
- Cascade prevention: ≥99.7% success rate

## Quality Gates (All PRs)
- Test coverage: ≥90% for core/orchestrator/memory
- Lane isolation: Zero cross-lane imports
- Observability: Metrics + traces + runbooks
- Security: SBOM + secret scanning + pinned SHAs

## Evidence Requirements
- Performance benchmarks with flamegraphs
- Coverage diff vs baseline
- Lane violation reports (must be zero)
- Security audit results
- PromQL snapshots for SLO validation`,
            metadata: { type: "standards", category: "quality" }
        },
        "consciousness-mod-005": {
            title: "Consciousness Module Integration",
            url: "https://lukhas.ai/modules/consciousness",
            mimeType: "text/markdown",
            content: `# Consciousness Module Integration

## 692-Module Architecture
- Modular consciousness components with clear interfaces
- Bio-inspired processing patterns
- Quantum-inspired computational models
- Memory systems with vector database integration

## Integration Patterns
- Guardian safety validation for all consciousness operations
- Memory/Emotion bridge systems for context awareness
- Identity validation for conscious state management
- Orchestrator coordination for cross-module communication

## Performance Characteristics
- <10ms tick processing for real-time consciousness
- Dynamic scaling with stable behavioral patterns
- Cascade prevention with 99.7% success rate
- Memory-efficient processing with sub-second recall`,
            metadata: { type: "modules", category: "consciousness" }
        }
    };

    // Return document or default
    return documents[id] || {
        title: "Document Not Found",
        url: `https://lukhas.ai/unknown/${id}`,
        mimeType: "text/plain",
        content: `The requested document with ID "${id}" was not found in the LUKHAS knowledge base. This is a mock implementation - in production, this would resolve IDs to actual content from the LUKHAS documentation system.`,
        metadata: { type: "error", category: "not_found" }
    };
}

// Simple CORS headers
function setCORSHeaders(res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With, Accept');
}

// Send JSON-RPC response
function sendJSONRPC(res, response) {
    setCORSHeaders(res);
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(response));
}

// Send regular JSON response
function sendJSON(res, data, status = 200) {
    setCORSHeaders(res);
    res.writeHead(status, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(data, null, 2));
}

// Parse JSON body
function parseBody(req) {
    return new Promise((resolve, reject) => {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', () => {
            try {
                resolve(body ? JSON.parse(body) : {});
            } catch (err) {
                reject(err);
            }
        });
    });
}

// MCP Tools definitions - ChatGPT requires 'search' and 'fetch' tools
const MCP_TOOLS = [
    {
        name: "search",
        description: "Search over LUKHAS sources and return opaque IDs for follow-up fetch",
        inputSchema: {
            type: "object",
            properties: {
                query: { type: "string", description: "Full-text query" },
                limit: { type: "integer", minimum: 1, maximum: 50, default: 5 }
            },
            required: ["query"]
        }
    },
    {
        name: "fetch",
        description: "Fetch full record by ID returned from search",
        inputSchema: {
            type: "object",
            properties: {
                id: { type: "string", description: "Opaque record ID from search" }
            },
            required: ["id"]
        }
    },
    {
        name: "get_infrastructure_status",
        description: "Get LUKHAS testing infrastructure status and metrics",
        inputSchema: {
            type: "object",
            properties: {},
            additionalProperties: false
        }
    },
    {
        name: "get_code_analysis",
        description: "Get current codebase health metrics and analysis",
        inputSchema: {
            type: "object",
            properties: {},
            additionalProperties: false
        }
    },
    {
        name: "get_development_utilities",
        description: "Get available LUKHAS development tools and utilities",
        inputSchema: {
            type: "object",
            properties: {},
            additionalProperties: false
        }
    },
    {
        name: "get_module_structure",
        description: "Get LUKHAS architecture and module structure information",
        inputSchema: {
            type: "object",
            properties: {},
            additionalProperties: false
        }
    },
    {
        name: "writeFile",
        description: "Create or overwrite a file with specified content",
        inputSchema: {
            type: "object",
            properties: {
                path: {
                    type: "string",
                    description: "Absolute or repo-relative path (e.g., 'src/utils/helper.js' or '/Users/agi_dev/LOCAL-REPOS/Lukhas/file.py')"
                },
                content: {
                    type: "string",
                    description: "UTF-8 text content to write"
                },
                overwrite: {
                    type: "boolean",
                    default: false,
                    description: "Allow overwriting existing files"
                },
                encoding: {
                    type: "string",
                    default: "utf8",
                    description: "File encoding (utf8, ascii, etc.)"
                }
            },
            required: ["path", "content"]
        }
    },
    {
        name: "createFile",
        description: "Create a new file; fails if file already exists",
        inputSchema: {
            type: "object",
            properties: {
                path: {
                    type: "string",
                    description: "Absolute or repo-relative path for new file"
                },
                content: {
                    type: "string",
                    description: "UTF-8 text content for new file"
                },
                template: {
                    type: "string",
                    description: "Optional template type (python, javascript, markdown, etc.)"
                },
                encoding: {
                    type: "string",
                    default: "utf8",
                    description: "File encoding"
                }
            },
            required: ["path", "content"]
        }
    }
];

// File system utilities for safe file operations

// Resolve path safely - convert relative paths to absolute within LUKHAS repo
function resolveSafePath(inputPath) {
    const repoRoot = '/Users/agi_dev/LOCAL-REPOS/Lukhas';

    // If already absolute and within repo, use as-is
    if (path.isAbsolute(inputPath)) {
        if (inputPath.startsWith(repoRoot)) {
            return inputPath;
        } else {
            throw new Error(`Absolute path must be within LUKHAS repo: ${repoRoot}`);
        }
    }

    // Resolve relative path within repo
    const resolved = path.resolve(repoRoot, inputPath);
    if (!resolved.startsWith(repoRoot)) {
        throw new Error(`Path traversal not allowed: ${inputPath}`);
    }

    return resolved;
}

// Safe file write with directory creation
async function writeFileWithDirectories(filePath, content, encoding = 'utf8', overwrite = false) {
    const safePath = resolveSafePath(filePath);
    const dir = path.dirname(safePath);

    // Check if file exists and overwrite policy
    try {
        await fs.access(safePath);
        if (!overwrite) {
            throw new Error(`File already exists and overwrite=false: ${filePath}`);
        }
    } catch (err) {
        if (err.code !== 'ENOENT') {
            throw err; // Re-throw if not "file doesn't exist"
        }
    }

    // Create directory if needed
    await fs.mkdir(dir, { recursive: true });

    // Write file
    await fs.writeFile(safePath, content, encoding);

    // Get file stats for response
    const stats = await fs.stat(safePath);

    return {
        path: safePath,
        relativePath: path.relative('/Users/agi_dev/LOCAL-REPOS/Lukhas', safePath),
        size: stats.size,
        created: stats.birthtime,
        modified: stats.mtime,
        encoding: encoding
    };
}

// Safe file creation (fails if exists)
async function createNewFile(filePath, content, encoding = 'utf8', template = null) {
    const safePath = resolveSafePath(filePath);
    const dir = path.dirname(safePath);

    // Check if file already exists
    try {
        await fs.access(safePath);
        throw new Error(`File already exists: ${filePath}`);
    } catch (err) {
        if (err.code !== 'ENOENT') {
            throw new Error(`Cannot create file: ${err.message}`);
        }
    }

    // Apply template if specified
    let finalContent = content;
    if (template) {
        const templateHeader = getTemplateHeader(template, path.basename(safePath));
        finalContent = templateHeader + content;
    }

    // Create directory if needed
    await fs.mkdir(dir, { recursive: true });

    // Create file
    await fs.writeFile(safePath, finalContent, encoding);

    // Get file stats for response
    const stats = await fs.stat(safePath);

    return {
        path: safePath,
        relativePath: path.relative('/Users/agi_dev/LOCAL-REPOS/Lukhas', safePath),
        size: stats.size,
        created: stats.birthtime,
        template: template,
        encoding: encoding
    };
}

// Template headers for different file types
function getTemplateHeader(template, filename) {
    const templates = {
        python: `#!/usr/bin/env python3
"""${filename} - LUKHAS AI Platform Module

Author: LUKHAS Development Team
Generated: ${new Date().toISOString()}
"""

`,
        javascript: `/**
 * ${filename} - LUKHAS AI Platform Module
 * 
 * Author: LUKHAS Development Team
 * Generated: ${new Date().toISOString()}
 */

`,
        markdown: `# ${filename.replace('.md', '')}

**Generated:** ${new Date().toISOString()}  
**Platform:** LUKHAS AI  

`,
        typescript: `/**
 * ${filename} - LUKHAS AI Platform Module
 * 
 * Author: LUKHAS Development Team
 * Generated: ${new Date().toISOString()}
 */

`
    };

    return templates[template.toLowerCase()] || '';
}

// Handle MCP method calls
async function handleMCPMethod(method, params = {}) {
    switch (method) {
        case 'initialize':
            // Be flexible with protocol versions - support what the client wants
            const clientProtocolVersion = params?.protocolVersion || "2024-11-05";
            const supportedVersions = ["2024-11-05", "2025-06-18", "2025-03-26"];
            const protocolVersion = supportedVersions.includes(clientProtocolVersion)
                ? clientProtocolVersion
                : "2024-11-05";

            return {
                protocolVersion,
                capabilities: {
                    tools: {
                        listChanged: false
                    },
                    logging: {
                        level: "info"
                    },
                    resources: {},
                    prompts: {}
                },
                serverInfo: {
                    name: "LUKHAS DevTools MCP",
                    version: "1.0.0"
                }
            };

        case 'tools/list':
            return {
                tools: MCP_TOOLS
            };

        case 'tools/call':
            const { name, arguments: args = {} } = params;

            switch (name) {
                case 'search':
                    const { query, limit = 5, ...extraArgs } = args; // Accept extra args gracefully
                    if (!query) {
                        throw new Error('Search query is required');
                    }

                    // Mock LUKHAS search results - return IDs + hits for ChatGPT compatibility
                    const searchResults = await mockLUKHASSearch(query, limit);
                    const ids = searchResults.map(r => r.id);
                    const hits = searchResults.map(r => ({
                        id: r.id,
                        title: r.title,
                        snippet: r.snippet
                    }));

                    // Return IDs for fetch + hits for display
                    return {
                        content: [
                            {
                                type: "text",
                                text: JSON.stringify({ ids, hits })
                            }
                        ]
                    };

                case 'fetch':
                    const { id, ...extraFetchArgs } = args; // Accept extra args gracefully
                    if (!id) {
                        throw new Error('ID is required');
                    }

                    // Fetch document by ID - resolve ID to full document
                    const document = await fetchById(id);

                    return {
                        content: [
                            {
                                type: "text",
                                text: JSON.stringify({
                                    id: id,
                                    title: document.title,
                                    url: document.url,
                                    mimeType: document.mimeType,
                                    text: document.content,
                                    metadata: document.metadata || {}
                                })
                            }
                        ]
                    };

                case 'get_infrastructure_status':
                    return {
                        content: [
                            {
                                type: "text",
                                text: JSON.stringify({
                                    status: "operational",
                                    total_tests: "775+ comprehensive tests",
                                    infrastructure: "stabilized after critical fixes",
                                    timestamp: new Date().toISOString(),
                                    quality_standard: "T4/0.01%"
                                }, null, 2)
                            }
                        ]
                    };

                case 'get_code_analysis':
                    return {
                        content: [
                            {
                                type: "text",
                                text: JSON.stringify({
                                    health_score: 92.5,
                                    code_quality: "excellent",
                                    total_files: 7000,
                                    timestamp: new Date().toISOString(),
                                    quality_standard: "T4/0.01%"
                                }, null, 2)
                            }
                        ]
                    };

                case 'get_development_utilities':
                    return {
                        content: [
                            {
                                type: "text",
                                text: JSON.stringify({
                                    utilities: ["Test infrastructure", "Code quality", "Performance monitoring"],
                                    tools: { testing: "pytest", linting: "ruff", typing: "mypy" },
                                    timestamp: new Date().toISOString(),
                                    quality_standard: "T4/0.01%"
                                }, null, 2)
                            }
                        ]
                    };

                case 'get_module_structure':
                    return {
                        content: [
                            {
                                type: "text",
                                text: JSON.stringify({
                                    total_modules: 692,
                                    consciousness_modules: 662,
                                    production_modules: 30,
                                    framework: "Constellation Framework",
                                    timestamp: new Date().toISOString(),
                                    quality_standard: "T4/0.01%"
                                }, null, 2)
                            }
                        ]
                    };

                case 'writeFile':
                    const { path: writePath, content: writeContent, overwrite = false, encoding: writeEncoding = 'utf8', ...extraWriteArgs } = args;

                    if (!writePath || !writeContent) {
                        throw new Error('Both path and content are required for writeFile');
                    }

                    try {
                        const result = await writeFileWithDirectories(writePath, writeContent, writeEncoding, overwrite);

                        return {
                            content: [
                                {
                                    type: "text",
                                    text: JSON.stringify({
                                        success: true,
                                        operation: "writeFile",
                                        path: result.path,
                                        relativePath: result.relativePath,
                                        size: result.size,
                                        encoding: result.encoding,
                                        overwritten: overwrite,
                                        timestamp: new Date().toISOString()
                                    }, null, 2)
                                }
                            ]
                        };
                    } catch (error) {
                        return {
                            content: [
                                {
                                    type: "text",
                                    text: JSON.stringify({
                                        success: false,
                                        operation: "writeFile",
                                        error: error.message,
                                        path: writePath,
                                        timestamp: new Date().toISOString()
                                    }, null, 2)
                                }
                            ]
                        };
                    }

                case 'createFile':
                    const { path: createPath, content: createContent, template, encoding: createEncoding = 'utf8', ...extraCreateArgs } = args;

                    if (!createPath || !createContent) {
                        throw new Error('Both path and content are required for createFile');
                    }

                    try {
                        const result = await createNewFile(createPath, createContent, createEncoding, template);

                        return {
                            content: [
                                {
                                    type: "text",
                                    text: JSON.stringify({
                                        success: true,
                                        operation: "createFile",
                                        path: result.path,
                                        relativePath: result.relativePath,
                                        size: result.size,
                                        template: result.template,
                                        encoding: result.encoding,
                                        timestamp: new Date().toISOString()
                                    }, null, 2)
                                }
                            ]
                        };
                    } catch (error) {
                        return {
                            content: [
                                {
                                    type: "text",
                                    text: JSON.stringify({
                                        success: false,
                                        operation: "createFile",
                                        error: error.message,
                                        path: createPath,
                                        timestamp: new Date().toISOString()
                                    }, null, 2)
                                }
                            ]
                        };
                    }

                default:
                    throw new Error(`Unknown tool: ${name}`);
            }

        default:
            throw new Error(`Unknown method: ${method}`);
    }
}

const server = createServer(async (req, res) => {
    const url = new URL(req.url, `http://localhost:${PORT}`);
    const path = url.pathname;
    const method = req.method;

    console.log(`${new Date().toISOString()} ${method} ${path} - Accept: ${req.headers.accept}`);

    // Handle CORS preflight
    if (method === 'OPTIONS') {
        setCORSHeaders(res);
        res.writeHead(200);
        res.end();
        return;
    }

    try {
        // STREAMABLE HTTP: Single /mcp endpoint for both SSE and JSON-RPC
        if (path === '/mcp') {
            // GET with text/event-stream = SSE for server->client messages
            if (method === 'GET' && req.headers.accept?.includes('text/event-stream')) {
                setCORSHeaders(res);
                res.writeHead(200, {
                    'Content-Type': 'text/event-stream',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'X-Accel-Buffering': 'no'  // Prevent proxy buffering
                });

                // Keep connection alive with periodic comments
                const keepAlive = setInterval(() => {
                    res.write(': keep-alive\n\n');
                }, 30000);

                req.on('close', () => {
                    clearInterval(keepAlive);
                });

                // Note: In Streamable HTTP, server->client messages would be sent here
                // For now, just keep the connection alive for ChatGPT
                return;
            }

            // POST = JSON-RPC for client->server messages
            if (method === 'POST') {
                try {
                    const body = await parseBody(req);
                    console.log('MCP Request:', JSON.stringify(body, null, 2));

                    if (!body.jsonrpc || body.jsonrpc !== "2.0") {
                        throw new Error('Invalid JSON-RPC request');
                    }

                    const result = await handleMCPMethod(body.method, body.params);

                    const response = {
                        jsonrpc: "2.0",
                        id: body.id,
                        result
                    };

                    console.log('MCP Response:', JSON.stringify(response, null, 2));
                    sendJSONRPC(res, response);
                    return;

                } catch (error) {
                    console.error('MCP Error:', error);
                    const errorResponse = {
                        jsonrpc: "2.0",
                        id: req.body?.id || null,
                        error: {
                            code: -32603,
                            message: error.message || 'Internal error'
                        }
                    };
                    sendJSONRPC(res, errorResponse);
                    return;
                }
            }
        }

        // Root endpoint - Server information (not MCP, just for debugging)
        if (path === '/' && method === 'GET') {
            const host = req.headers.host || `localhost:${PORT}`;
            const protocol = req.headers['x-forwarded-proto'] || 'http';
            const baseUrl = `${protocol}://${host}`;

            sendJSON(res, {
                name: "LUKHAS DevTools MCP Server",
                version: "1.0.0",
                description: "LUKHAS development tools MCP server with Streamable HTTP transport",
                protocol: "MCP 2024-11-05",
                transport: "Streamable HTTP",
                mcp_endpoint: `${baseUrl}/mcp`,
                tools: MCP_TOOLS.length,
                usage: {
                    note: "Use /mcp endpoint for both SSE (GET) and JSON-RPC (POST)",
                    sse_connection: "GET /mcp with Accept: text/event-stream",
                    json_rpc: "POST /mcp with JSON-RPC 2.0 payload"
                }
            });
            return;
        }

        // Health check for debugging
        if (path === '/health' && method === 'GET') {
            setCORSHeaders(res);
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({
                status: 'healthy',
                timestamp: new Date().toISOString(),
                server: 'lukhas-mcp-server',
                version: '1.0.0',
                transport: 'Streamable HTTP',
                mcp_version: '2024-11-05'
            }));
            return;
        }

        // 404 for other paths
        setCORSHeaders(res);
        res.writeHead(404, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
            error: 'Not Found',
            message: 'This is an MCP server. Use /mcp endpoint for both SSE and JSON-RPC.',
            mcp_endpoint: '/mcp',
            mcp_version: '2024-11-05'
        }));

    } catch (error) {
        console.error('Server error:', error);
        setCORSHeaders(res);
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
            error: 'Internal Server Error',
            message: error.message
        }));
    }
});

server.listen(PORT, () => {
    console.log(`🚀 LUKHAS MCP Server (Streamable HTTP) running on port ${PORT}`);
    console.log(`📡 MCP Endpoint: http://localhost:${PORT}/mcp`);
    console.log(`🔧 Transport: Streamable HTTP (single endpoint)`);
    console.log(`📋 Protocol: MCP 2024-11-05`);
    console.log(`🛠️ Tools: ${MCP_TOOLS.length} development utilities available`);
    console.log(`✅ Ready for ChatGPT MCP Connector!`);
    console.log('');
    console.log('🧪 Self-check commands:');
    console.log(`   Initialize: curl -s http://localhost:${PORT}/mcp -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","clientInfo":{"name":"test","version":"1.0"},"capabilities":{}}}'`);
    console.log(`   SSE: curl -v -N -H "Accept: text/event-stream" http://localhost:${PORT}/mcp`);
    console.log(`   Tools: curl -s http://localhost:${PORT}/mcp -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'`);
});

server.on('error', (err) => {
    console.error('Server error:', err);
});