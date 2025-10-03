import cors from "cors";
import express from "express";
import {
    executeConstellationOperation,
    getConsciousnessProcessingSystem,
    getConstellationFramework,
    getConstellationFrameworkStatus,
    getGuardianProtectionSystem,
    getIdentityAnchorSystem
} from "./constellation-tools.js";

const app = express();
const PORT = parseInt(process.env.PORT || "8766");
const HTTP_TOKEN = process.env.MCP_HTTP_TOKEN || "";

// Middleware
app.use(cors({
  origin: '*',
  methods: ['GET', 'POST', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
  credentials: false
}));
app.use(express.json({ limit: '10mb' }));

// Request logging
function logRequest(req: express.Request, method: string, hasAuth: boolean, status: number, duration?: number) {
  const logEntry = {
    timestamp: new Date().toISOString(),
    method: req.method,
    path: req.path,
    mcpMethod: method,
    hasAuth,
    status,
    duration: duration || 0,
    server: 'lukhas-constellation-mcp',
    version: '0.1.0'
  };
  console.error(JSON.stringify(logEntry));
}

// Authentication middleware
function authenticate(req: express.Request, res: express.Response, next: express.NextFunction) {
  const bearerToken = req.headers.authorization?.replace('Bearer ', '');
  const queryToken = req.query.api_key as string;
  const headerToken = req.headers['x-api-key'] as string;
  const token = bearerToken || queryToken || headerToken;

  if (!HTTP_TOKEN) {
    console.warn('⚠️  MCP_HTTP_TOKEN not set - running in development mode');
    return next();
  }

  if (!token || token !== HTTP_TOKEN) {
    logRequest(req, 'auth_failed', false, 401);
    return res.status(401).json({
      jsonrpc: "2.0",
      error: { 
        code: -32001, 
        message: "Authentication required",
        data: { server: "lukhas-constellation-mcp" }
      },
      id: null
    });
  }

  next();
}

// Health check
app.get('/healthz', (req: express.Request, res: express.Response) => {
  const healthData = {
    status: 'ok',
    timestamp: new Date().toISOString(),
    server: 'lukhas-constellation-mcp',
    version: '0.1.0',
    features: ['constellation-framework', 'trinity-coordination', 'matriz-processing', 'consciousness-integration']
  };
  
  logRequest(req, 'health_check', false, 200);
  res.json(healthData);
});

// MCP probe
app.get('/mcp', (req: express.Request, res: express.Response) => {
  const probeData = {
    ok: true,
    server: "lukhas-constellation-mcp",
    version: "0.1.0",
    capabilities: {
      tools: [
        "constellation_status",
        "trinity_framework_info",
        "constellation_operation",
        "identity_system",
        "consciousness_system",
        "guardian_system"
      ],
      features: ["⚛️ Anchor Star", "✦ Trail Star", "🔬 Horizon Star", "🛡️ Watch Star"]
    }
  };
  
  logRequest(req, 'mcp_probe', !!req.query.api_key, 200);
  res.json(probeData);
});

// OpenAPI specification
app.get('/openapi.json', (req: express.Request, res: express.Response) => {
  const openApiSpec = {
    openapi: "3.0.0",
    info: {
      title: "LUKHAS Constellation MCP",
      version: "0.1.0",
      description: "Consciousness Framework and Trinity coordination tools"
    },
    servers: [{ url: `http://localhost:${PORT}` }],
    paths: {
      "/mcp": {
        post: {
          summary: "Execute Constellation Framework operations",
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
                      enum: [
                        "constellation_status",
                        "trinity_framework_info",
                        "constellation_operation",
                        "consciousness_modules",
                        "matriz_processing",
                        "symbolic_analysis"
                      ]
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
  };
  
  logRequest(req, 'openapi_spec', false, 200);
  res.json(openApiSpec);
});

// Main MCP endpoint
app.post('/mcp', authenticate, async (req: express.Request, res: express.Response) => {
  const startTime = Date.now();
  const hasAuth = !!(req.headers.authorization || req.query.api_key || req.headers['x-api-key']);
  
  try {
    const { jsonrpc, method, params, id } = req.body;
    
    if (jsonrpc !== "2.0") {
      const duration = Date.now() - startTime;
      logRequest(req, method || 'invalid', hasAuth, 400, duration);
      return res.status(400).json({
        jsonrpc: "2.0",
        error: { code: -32600, message: "Invalid Request - jsonrpc must be 2.0" },
        id
      });
    }

    let result;
    
    switch (method) {
      case "constellation_status": {
        result = await getConstellationFrameworkStatus();
        break;
      }
      
      case "trinity_framework_info": {
        result = await getConstellationFramework();
        break;
      }
      
      case "constellation_operation": {
        const operation = String(params?.operation || "");
        const operationParams = params?.parameters || {};
        result = await executeConstellationOperation(operation, operationParams);
        break;
      }
      
      case "identity_system": {
        result = await getIdentityAnchorSystem();
        break;
      }
      
      case "consciousness_system": {
        result = await getConsciousnessProcessingSystem();
        break;
      }
      
      case "guardian_system": {
        result = await getGuardianProtectionSystem();
        break;
      }
      
      default:
        const duration = Date.now() - startTime;
        logRequest(req, method, hasAuth, 400, duration);
        return res.status(400).json({
          jsonrpc: "2.0",
          error: { 
            code: -32601, 
            message: `Method not found: ${method}`,
            data: { server: "lukhas-constellation-mcp" }
          },
          id
        });
    }
    
    const duration = Date.now() - startTime;
    logRequest(req, method, hasAuth, 200, duration);
    
    res.json({
      jsonrpc: "2.0",
      result,
      meta: {
        server: "lukhas-constellation-mcp",
        execution_time_ms: duration,
        timestamp: new Date().toISOString()
      },
      id
    });
    
  } catch (error) {
    const duration = Date.now() - startTime;
    const errorMessage = error instanceof Error ? error.message : String(error);
    logRequest(req, req.body?.method || 'unknown', hasAuth, 500, duration);
    
    res.status(500).json({
      jsonrpc: "2.0",
      error: { 
        code: -32603, 
        message: errorMessage,
        data: { server: "lukhas-constellation-mcp" }
      },
      id: req.body?.id || null
    });
  }
});

// 404 handler
app.use('*', (req: express.Request, res: express.Response) => {
  logRequest(req, 'not_found', false, 404);
  res.status(404).json({
    jsonrpc: "2.0",
    error: { 
      code: -32700, 
      message: "Endpoint not found",
      data: { 
        available_endpoints: ["/healthz", "/mcp", "/openapi.json"],
        server: "lukhas-constellation-mcp"
      }
    },
    id: null
  });
});

// Start server
function main() {
  app.listen(PORT, () => {
    console.error(`🌟 LUKHAS Constellation MCP server running on port ${PORT}`);
    console.error(`🧠 Features: Constellation Framework, Trinity coordination, MΛTRIZ processing`);
    console.error(`🔗 Endpoints: /healthz, /mcp, /openapi.json`);
    console.error(`🔐 Authentication: ${HTTP_TOKEN ? 'Enabled' : 'Disabled (dev mode)'}`);
  });
}

main();