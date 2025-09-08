import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import { authenticateRequest, OAuthValidator } from "./auth.js";
import { getFile, listDir, searchFiles, SearchSchema, statRel } from "./fsTools.js";

// Initialize OAuth validator from environment
const authValidator = OAuthValidator.createFromEnv();

const server = new Server(
  {
    name: "mcp-fs-lukhas-oauth",
    version: "1.0.0"
  },
  {
    capabilities: {
      tools: {}
    }
  }
);

// Authentication middleware wrapper
async function withAuth<T>(
  authHeader: string | undefined,
  operation: () => Promise<T>
): Promise<T> {
  const authResult = await authenticateRequest(authValidator, authHeader);
  
  if (!authResult.authorized) {
    throw new Error(`Authentication failed: ${authResult.error}`);
  }
  
  return operation();
}

// Enhanced tool handler with OAuth authentication
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  
  // Extract auth header from request headers (if available)
  // Note: MCP protocol may handle auth differently - this is a conceptual implementation
  const authHeader = process.env.MCP_AUTH_HEADER || 
    (typeof request.params._meta?.authorization === 'string' ? request.params._meta.authorization : undefined);

  try {
    const result = await withAuth(authHeader, async () => {
      // Ensure args exists
      const safeArgs = args || {};
      
      switch (name) {
        case "stat":
          return await statRel(String(safeArgs.rel || "."));
          
        case "list_dir":
          return await listDir(String(safeArgs.rel || "."));
          
        case "search":
          const parsed = SearchSchema.safeParse({
            query: safeArgs.query,
            glob: safeArgs.glob,
            limit: safeArgs.limit
          });
          if (!parsed.success) {
            throw new Error(`Invalid search args: ${parsed.error.message}`);
          }
          const { query, glob, limit } = parsed.data;
          return await searchFiles(query, glob, limit);
          
        case "get_file":
          return await getFile(String(safeArgs.rel));

        default:
          throw new Error(`Unknown tool: ${name}`);
      }
    });

    return {
      content: [{ type: "text", text: JSON.stringify(result, null, 2) }]
    };

  } catch (error) {
    return {
      content: [{ 
        type: "text", 
        text: JSON.stringify({ 
          error: error instanceof Error ? error.message : String(error),
          tool: name,
          authenticated: !!authValidator,
          timestamp: new Date().toISOString()
        }, null, 2) 
      }],
      isError: true
    };
  }
});

server.onerror = (error) => {
  console.error("OAuth-protected MCP server error:", error);
};

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error(`mcp-fs-lukhas-oauth running on stdio ${authValidator ? 'with OAuth authentication' : 'without authentication'}`);

  if (authValidator) {
    console.error("OAuth Configuration:");
    console.error("- Provider:", process.env.OAUTH_PROVIDER);
    console.error("- Issuer:", process.env.OAUTH_ISSUER);
    console.error("- Audience:", process.env.OAUTH_AUDIENCE);
    console.error("- Required Scopes:", process.env.OAUTH_REQUIRED_SCOPES || 'read:files');
  } else {
    console.error("OAuth not configured - server running without authentication");
    console.error("Set OAUTH_PROVIDER, OAUTH_JWKS_URL, OAUTH_ISSUER, and OAUTH_AUDIENCE to enable OAuth");
  }
}

main().catch((error) => {
  console.error("OAuth server failed to start:", error);
  process.exit(1);
});
