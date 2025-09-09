import express from "express";
import cors from "cors";
import { z } from "zod";
import { getFile, listDir, readRange, searchFiles, SearchSchema, statRel, ReadRangeSchema } from "./fsTools.js";

const app = express();
const PORT = parseInt(process.env.PORT || "8765");
const HTTP_TOKEN = process.env.MCP_HTTP_TOKEN || "";

// Middleware
app.use(cors());
app.use(express.json({ limit: '10mb' }));

// Enhanced request logging
function logRequest(req: express.Request, method: string, hasAuth: boolean, status: number) {
  const logEntry = {
    timestamp: new Date().toISOString(),
    method: req.method,
    path: req.path,
    mcpMethod: method,
    hasAuth,
    queryKeys: Object.keys(req.query),
    status,
    userAgent: req.get('user-agent')?.slice(0, 100),
    origin: req.get('origin')
  };
  console.error(JSON.stringify(logEntry));
}

// Authentication middleware
function authenticate(req: express.Request, res: express.Response, next: express.NextFunction) {
  // Support both Bearer token and query parameter
  const bearerToken = req.headers.authorization?.replace('Bearer ', '');
  const queryToken = req.query.api_key as string;
  const token = bearerToken || queryToken;

  if (!HTTP_TOKEN) {
    // No token configured - allow all requests (development mode)
    return next();
  }

  if (!token || token !== HTTP_TOKEN) {
    logRequest(req, 'auth_failed', false, 401);
    return res.status(401).json({
      jsonrpc: "2.0",
      error: { code: -32001, message: "Authentication required" },
      id: null
    });
  }

  next();
}

// Health check endpoint (public)
app.get('/healthz', (req, res) => {
  logRequest(req, 'health_check', false, 200);
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// MCP probe endpoint (GET /mcp) - for connector validation
app.get('/mcp', (req, res) => {
  logRequest(req, 'mcp_probe', !!req.query.api_key, 200);
  res.json({ 
    ok: true, 
    server: "mcp-fs-lukhas",
    version: "1.0.0",
    capabilities: ["stat", "list_dir", "search", "get_file", "read_range"]
  });
});

// Main MCP JSON-RPC endpoint
app.post('/mcp', authenticate, async (req, res) => {
  const hasAuth = !!(req.headers.authorization || req.query.api_key);
  
  try {
    const { jsonrpc, method, params, id } = req.body;
    
    if (jsonrpc !== "2.0") {
      logRequest(req, method || 'invalid', hasAuth, 400);
      return res.status(400).json({
        jsonrpc: "2.0",
        error: { code: -32600, message: "Invalid Request - jsonrpc must be 2.0" },
        id
      });
    }

    let result;
    
    switch (method) {
      case "stat": {
        const rel = String(params?.rel || ".");
        result = await statRel(rel);
        break;
      }
      
      case "list_dir": {
        const rel = String(params?.rel || ".");
        result = await listDir(rel);
        break;
      }
      
      case "search": {
        const parsed = SearchSchema.safeParse({
          query: params?.query,
          glob: params?.glob,
          limit: params?.limit
        });
        if (!parsed.success) {
          logRequest(req, method, hasAuth, 400);
          return res.status(400).json({
            jsonrpc: "2.0",
            error: { code: -32602, message: `Invalid params: ${parsed.error.message}` },
            id
          });
        }
        const { query, glob, limit } = parsed.data;
        result = await searchFiles(query, glob, limit);
        break;
      }
      
      case "get_file": {
        const rel = String(params?.rel);
        result = await getFile(rel);
        break;
      }
      
      case "read_range": {
        const parsed = ReadRangeSchema.safeParse({
          rel: params?.rel,
          offset: params?.offset,
          length: params?.length
        });
        if (!parsed.success) {
          logRequest(req, method, hasAuth, 400);
          return res.status(400).json({
            jsonrpc: "2.0",
            error: { code: -32602, message: `Invalid params: ${parsed.error.message}` },
            id
          });
        }
        const { rel, offset, length } = parsed.data;
        result = await readRange(rel, offset, length);
        break;
      }
      
      default:
        logRequest(req, method, hasAuth, 400);
        return res.status(400).json({
          jsonrpc: "2.0",
          error: { code: -32601, message: `Method not found: ${method}` },
          id
        });
    }
    
    logRequest(req, method, hasAuth, 200);
    res.json({
      jsonrpc: "2.0",
      result,
      id
    });
    
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    logRequest(req, req.body?.method || 'unknown', hasAuth, 500);
    res.status(500).json({
      jsonrpc: "2.0",
      error: { code: -32603, message: errorMessage },
      id: req.body?.id || null
    });
  }
});

// SSE endpoint (optional - for future SSE clients)
app.get('/sse', authenticate, (req, res) => {
  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Cache-Control'
  });

  const keepAlive = setInterval(() => {
    res.write('data: {"type":"ping"}\n\n');
  }, 30000);

  req.on('close', () => {
    clearInterval(keepAlive);
  });

  logRequest(req, 'sse_connect', true, 200);
  res.write('data: {"type":"connected","server":"mcp-fs-lukhas"}\n\n');
});

// Handle 404s
app.use('*', (req, res) => {
  logRequest(req, 'not_found', false, 404);
  res.status(404).json({
    jsonrpc: "2.0",
    error: { code: -32700, message: "Endpoint not found" },
    id: null
  });
});

// Start server
function main() {
  app.listen(PORT, () => {
    console.error(`🚀 mcp-fs-lukhas HTTP server running on port ${PORT}`);
    console.error(`📊 Environment:`);
    console.error(`   - MCP_FS_ROOT: ${process.env.MCP_FS_ROOT || '/Users/agi_dev/LOCAL-REPOS/Lukhas'}`);
    console.error(`   - MCP_MAX_BYTES: ${process.env.MCP_MAX_BYTES || '2097152'}`);
    console.error(`   - Authentication: ${HTTP_TOKEN ? 'Enabled' : 'Disabled (dev mode)'}`);
    console.error(`🔗 Endpoints:`);
    console.error(`   - Health: http://localhost:${PORT}/healthz`);
    console.error(`   - MCP probe: http://localhost:${PORT}/mcp`);
    console.error(`   - JSON-RPC: POST http://localhost:${PORT}/mcp`);
    console.error(`   - SSE: http://localhost:${PORT}/sse`);
    
    if (HTTP_TOKEN) {
      console.error(`🔐 Test with auth:`);
      console.error(`   curl 'http://localhost:${PORT}/mcp?api_key=${HTTP_TOKEN.slice(0, 8)}...' -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","method":"stat","params":{"rel":"."},"id":1}'`);
    } else {
      console.error(`⚠️  No MCP_HTTP_TOKEN set - running in development mode`);
      console.error(`   Set MCP_HTTP_TOKEN for production use`);
    }
  });
}

main();