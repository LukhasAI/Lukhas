import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { CallToolRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import { OAuthValidator, authenticateRequest } from "./auth.js";
import {
    extractImports,
    findSymbolUsage,
    formatCode,
    installDependencies,
    runCommand, runLinter,
    runTests
} from "./devTools.js";
import {
    copyFile,
    createDirectory,
    deleteFile,
    getFile,
    listDir,
    moveFile,
    searchFiles,
    statRel,
    writeFile
} from "./fsTools.js";
import {
    gitAdd,
    gitCheckout,
    gitCommit, gitCreateBranch,
    gitDiff,
    gitStash,
    gitStatus
} from "./gitTools.js";
import {
    analyzeCodeComplexity,
    auditSymbolicVocabulary,
    findTodosFixmes,
    findUnusedCode,
    semanticCodeSearch,
    syncAgentConfigs,
    updateConsciousnessDocs,
    validateTrinityCompliance
} from "./lukhastTools.js";

// Initialize OAuth validator from environment
const authValidator = OAuthValidator.createFromEnv();

const server = new Server(
  {
    name: "mcp-fs-lukhas-ultimate",
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

// Enhanced tool handler with authentication
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  const authHeader = request.meta?.authorization;

  try {
    const result = await withAuth(authHeader, async () => {
      switch (name) {
        // TIER 1: File Operations
        case "stat":
          return await statRel(String(args.rel || "."));
          
        case "list_dir":
          return await listDir(String(args.rel || "."));
          
        case "search":
          return await searchFiles(
            String(args.query),
            String(args.glob || "**/*.{md,txt,ts,tsx,js,jsx,py,json,yaml,yml,toml}"),
            Number(args.limit || 50)
          );
          
        case "get_file":
          return await getFile(String(args.rel));
          
        case "write_file":
          return await writeFile(
            String(args.rel),
            String(args.content),
            args.mode ? String(args.mode) : undefined
          );
          
        case "delete_file":
          return await deleteFile(String(args.rel));
          
        case "move_file":
          return await moveFile(String(args.src), String(args.dest));
          
        case "create_directory":
          return await createDirectory(String(args.rel));
          
        case "copy_file":
          return await copyFile(String(args.src), String(args.dest));

        // TIER 2: Git Operations
        case "git_status":
          return await gitStatus();
          
        case "git_diff":
          return await gitDiff(
            args.file ? String(args.file) : undefined,
            Boolean(args.staged)
          );
          
        case "git_add":
          return await gitAdd(
            Array.isArray(args.files) ? args.files.map(String) : [String(args.files)]
          );
          
        case "git_commit":
          return await gitCommit(
            String(args.message),
            args.files ? (Array.isArray(args.files) ? args.files.map(String) : [String(args.files)]) : undefined
          );
          
        case "git_create_branch":
          return await gitCreateBranch(String(args.name));
          
        case "git_checkout":
          return await gitCheckout(String(args.branch));
          
        case "git_stash":
          return await gitStash(args.message ? String(args.message) : undefined);

        // TIER 3: Development Tools
        case "run_command":
          return await runCommand(
            String(args.cmd),
            args.cwd ? String(args.cwd) : undefined,
            args.timeout ? Number(args.timeout) : undefined
          );
          
        case "run_linter":
          return await runLinter(
            args.files ? (Array.isArray(args.files) ? args.files.map(String) : [String(args.files)]) : undefined,
            Boolean(args.fix)
          );
          
        case "format_code":
          return await formatCode(
            args.files ? (Array.isArray(args.files) ? args.files.map(String) : [String(args.files)]) : undefined
          );
          
        case "run_tests":
          return await runTests(
            args.pattern ? String(args.pattern) : undefined,
            Boolean(args.watch)
          );
          
        case "find_symbol_usage":
          return await findSymbolUsage(
            String(args.symbol),
            args.scope ? String(args.scope) : undefined
          );
          
        case "extract_imports":
          return await extractImports(String(args.file));
          
        case "install_dependencies":
          return await installDependencies(
            args.packageManager ? String(args.packageManager) : undefined
          );

        // TIER 4: LUKHAS-Specific Tools
        case "validate_trinity_compliance":
          return await validateTrinityCompliance(
            args.files ? (Array.isArray(args.files) ? args.files.map(String) : [String(args.files)]) : undefined
          );
          
        case "update_consciousness_docs":
          return await updateConsciousnessDocs();
          
        case "sync_agent_configs":
          return await syncAgentConfigs();
          
        case "audit_symbolic_vocabulary":
          return await auditSymbolicVocabulary();
          
        case "semantic_code_search":
          return await semanticCodeSearch(String(args.query));
          
        case "find_todos_fixmes":
          return await findTodosFixmes();
          
        case "analyze_code_complexity":
          return await analyzeCodeComplexity(
            args.files ? (Array.isArray(args.files) ? args.files.map(String) : [String(args.files)]) : undefined
          );
          
        case "find_unused_code":
          return await findUnusedCode();

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
          args: args 
        }, null, 2) 
      }],
      isError: true
    };
  }
});

server.onerror = (error) => {
  console.error("OAuth-protected MCP server error:", error);
};

await server.start();
console.log(`mcp-fs-lukhas-ultimate running on stdio ${authValidator ? 'with OAuth authentication' : 'without authentication'}`);

if (authValidator) {
  console.log("OAuth Configuration:");
  console.log("- Provider:", process.env.OAUTH_PROVIDER);
  console.log("- Issuer:", process.env.OAUTH_ISSUER);
  console.log("- Audience:", process.env.OAUTH_AUDIENCE);
  console.log("- Required Scopes:", process.env.OAUTH_REQUIRED_SCOPES || 'read:files');
}
