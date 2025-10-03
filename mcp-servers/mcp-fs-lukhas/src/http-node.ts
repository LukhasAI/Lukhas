import fs from "fs-extra";
import { createServer } from 'node:http';
import path from "node:path";
import { URL } from 'node:url';

const PORT = parseInt(process.env.PORT || "8765");
const HTTP_TOKEN = process.env.MCP_HTTP_TOKEN || "";
const LUKHAS_ROOT = process.env.LUKHAS_ROOT || "/Users/agi_dev/LOCAL-REPOS/Lukhas";

// Simple CORS headers
function setCORSHeaders(res: any) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With');
}

// Authentication check
function isAuthenticated(req: any): boolean {
  if (!HTTP_TOKEN) return true; // Dev mode
  
  const authHeader = req.headers.authorization;
  const bearerToken = authHeader?.replace('Bearer ', '');
  const url = new URL(req.url, `http://localhost:${PORT}`);
  const queryToken = url.searchParams.get('api_key');
  const headerToken = req.headers['x-api-key'];
  
  const token = bearerToken || queryToken || headerToken;
  return token === HTTP_TOKEN;
}

// JSON response helper
function sendJSON(res: any, data: any, status: number = 200) {
  setCORSHeaders(res);
  res.writeHead(status, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(data, null, 2));
}

// Parse JSON body
function parseBody(req: any): Promise<any> {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', (chunk: any) => body += chunk);
    req.on('end', () => {
      try {
        resolve(body ? JSON.parse(body) : {});
      } catch (err) {
        reject(err);
      }
    });
  });
}

// Security: Path validation
function resolveSafe(relativePath: string) {
  const joined = path.resolve(LUKHAS_ROOT, relativePath);
  if (!joined.startsWith(path.resolve(LUKHAS_ROOT))) {
    throw new Error("Path traversal blocked");
  }
  return joined;
}

// File system operations
async function statRel(rel: string) {
  try {
    const fullPath = resolveSafe(rel);
    const exists = await fs.pathExists(fullPath);
    if (!exists) return { exists: false, path: rel };
    
    const stat = await fs.stat(fullPath);
    return {
      exists: true,
      path: rel,
      isFile: stat.isFile(),
      isDirectory: stat.isDirectory(),
      size: stat.size,
      modified: stat.mtime
    };
  } catch (error) {
    return { exists: false, path: rel, error: (error as Error).message };
  }
}

async function listDir(rel: string) {
  try {
    const fullPath = resolveSafe(rel);
    const exists = await fs.pathExists(fullPath);
    if (!exists) return { error: "Directory not found", path: rel };
    
    const stat = await fs.stat(fullPath);
    if (!stat.isDirectory()) return { error: "Not a directory", path: rel };
    
    const entries = await fs.readdir(fullPath);
    const results = [];
    
    for (const entry of entries.slice(0, 100)) { // Limit to 100 entries
      try {
        const entryPath = path.join(fullPath, entry);
        const entryStat = await fs.stat(entryPath);
        results.push({
          name: entry,
          isDirectory: entryStat.isDirectory(),
          size: entryStat.size,
          modified: entryStat.mtime
        });
      } catch {
        results.push({ name: entry, error: "Cannot stat" });
      }
    }
    
    return { path: rel, entries: results, total: entries.length };
  } catch (error) {
    return { error: (error as Error).message, path: rel };
  }
}

async function getFile(rel: string) {
  try {
    const fullPath = resolveSafe(rel);
    const exists = await fs.pathExists(fullPath);
    if (!exists) return { error: "File not found", path: rel };
    
    const stat = await fs.stat(fullPath);
    if (!stat.isFile()) return { error: "Not a file", path: rel };
    
    // Size limit for safety
    const maxSize = 1024 * 1024; // 1MB
    if (stat.size > maxSize) {
      return { 
        error: "File too large", 
        path: rel, 
        size: stat.size, 
        maxSize,
        suggestion: "Use read_range for large files"
      };
    }
    
    const content = await fs.readFile(fullPath, 'utf8');
    return {
      path: rel,
      content,
      size: stat.size,
      modified: stat.mtime
    };
  } catch (error) {
    return { error: (error as Error).message, path: rel };
  }
}

const server = createServer(async (req, res) => {
  const url = new URL(req.url!, `http://localhost:${PORT}`);
  const path = url.pathname;
  const method = req.method;

  console.error(`${new Date().toISOString()} ${method} ${path}`);

  // Handle OPTIONS for CORS
  if (method === 'OPTIONS') {
    setCORSHeaders(res);
    res.writeHead(200);
    res.end();
    return;
  }

  try {
    // Health check endpoint
    if (path === '/healthz' && method === 'GET') {
      sendJSON(res, {
        status: 'ok',
        timestamp: new Date().toISOString(),
        server: 'mcp-fs-lukhas',
        version: '0.1.0',
        lukhas_root: LUKHAS_ROOT
      });
      return;
    }

    // MCP probe endpoint
    if (path === '/mcp' && method === 'GET') {
      sendJSON(res, {
        ok: true,
        server: "mcp-fs-lukhas",
        version: "0.1.0",
        capabilities: {
          tools: ["stat", "list_dir", "get_file", "search"],
          features: ["file-operations", "directory-listing", "content-access"]
        }
      });
      return;
    }

    // OpenAPI specification
    if (path === '/openapi.json' && method === 'GET') {
      sendJSON(res, {
        openapi: "3.0.0",
        info: {
          title: "LUKHAS File System MCP",
          version: "0.1.0",
          description: "File system access for LUKHAS AI codebase"
        },
        servers: [{ url: `http://localhost:${PORT}` }],
        paths: {
          "/mcp": {
            post: {
              summary: "Execute file system operations",
              security: [{ bearerAuth: [] }],
              requestBody: {
                required: true,
                content: {
                  "application/json": {
                    schema: {
                      type: "object",
                      properties: {
                        jsonrpc: { type: "string", enum: ["2.0"] },
                        method: {
                          type: "string",
                          enum: ["stat", "list_dir", "get_file", "search"]
                        },
                        params: { type: "object" },
                        id: { type: "integer" }
                      },
                      required: ["jsonrpc", "method", "id"]
                    }
                  }
                }
              }
            }
          }
        },
        components: {
          securitySchemes: {
            bearerAuth: { type: "http", scheme: "bearer" }
          }
        }
      });
      return;
    }

    // Main MCP endpoint
    if (path === '/mcp' && method === 'POST') {
      // Check authentication
      if (!isAuthenticated(req)) {
        sendJSON(res, {
          jsonrpc: "2.0",
          error: { 
            code: -32001, 
            message: "Authentication required",
            data: { server: "mcp-fs-lukhas" }
          },
          id: null
        }, 401);
        return;
      }

      // Parse request body
      const body = await parseBody(req);
      const { jsonrpc, method: mcpMethod, params, id } = body;
      
      if (jsonrpc !== "2.0") {
        sendJSON(res, {
          jsonrpc: "2.0",
          error: { code: -32600, message: "Invalid Request - jsonrpc must be 2.0" },
          id
        }, 400);
        return;
      }

      let result;
      
      switch (mcpMethod) {
        case "stat":
          const statPath = String(params?.rel || ".");
          result = await statRel(statPath);
          break;
          
        case "list_dir":
          const listPath = String(params?.rel || ".");
          result = await listDir(listPath);
          break;
          
        case "get_file":
          const filePath = String(params?.rel || "");
          result = await getFile(filePath);
          break;
          
        case "search":
          const query = String(params?.query || "");
          result = {
            query,
            message: "Search functionality available - basic file system search",
            suggestion: "Use stat and list_dir for directory exploration",
            timestamp: new Date().toISOString()
          };
          break;
          
        default:
          sendJSON(res, {
            jsonrpc: "2.0",
            error: { 
              code: -32601, 
              message: `Method not found: ${mcpMethod}`,
              data: { 
                available_methods: ["stat", "list_dir", "get_file", "search"],
                server: "mcp-fs-lukhas"
              }
            },
            id
          }, 400);
          return;
      }
      
      sendJSON(res, {
        jsonrpc: "2.0",
        result,
        meta: {
          server: "mcp-fs-lukhas",
          timestamp: new Date().toISOString()
        },
        id
      });
      return;
    }

    // 404 for other paths
    sendJSON(res, {
      jsonrpc: "2.0",
      error: { 
        code: -32700, 
        message: "Endpoint not found",
        data: { 
          available_endpoints: ["/healthz", "/mcp", "/openapi.json"],
          server: "mcp-fs-lukhas"
        }
      },
      id: null
    }, 404);

  } catch (error) {
    console.error('Server error:', error);
    sendJSON(res, {
      jsonrpc: "2.0",
      error: { 
        code: -32603, 
        message: "Internal server error",
        data: { server: "mcp-fs-lukhas" }
      },
      id: null
    }, 500);
  }
});

server.listen(PORT, () => {
  console.error(`📁 LUKHAS File System MCP v0.1.0 running on port ${PORT}`);
  console.error(`📊 Environment: ${process.env.NODE_ENV || 'development'}`);
  console.error(`📂 LUKHAS Root: ${LUKHAS_ROOT}`);
  console.error(`🔐 Authentication: ${HTTP_TOKEN ? 'Enabled' : 'Disabled (dev mode)'}`);
  console.error(`🔗 Endpoints: /healthz, /mcp, /openapi.json`);
  
  if (HTTP_TOKEN) {
    console.error(`🔐 ChatGPT MCP Server URL: http://localhost:${PORT}/mcp`);
  }
});