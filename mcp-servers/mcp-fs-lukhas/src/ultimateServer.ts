import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";

// Import all tool categories
import {
    getFile,
    listDir, searchFiles,
    SearchSchema,
    statRel
} from "./fsTools.js";

import {
    buildProject,
    copyFile,
    createDirectory,
    deleteFile,
    gitAdd,
    gitCheckout,
    gitCommit, gitCreateBranch,
    gitDiff,
    gitStash,
    gitStatus,
    installDependencies,
    moveFile,
    runCommand,
    runTests,
    writeFile
} from "./enhancedTools.js";

import {
    analyzeCodeComplexity,
    auditSymbolicVocabulary,
    backupWorkspace,
    createFeatureBranch,
    extractImports,
    findSymbolUsage,
    findTodosFixmes,
    findUnusedCode,
    formatCode,
    runLinter,
    validateTrinityCompliance
} from "./advancedTools.js";

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

// ============================================================================
// LIST ALL TOOLS (All 4 Tiers: Read + Write + Git + Build + Analysis + LUKHAS)
// ============================================================================

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      // TIER 1: CORE READ OPERATIONS (Original Safe Tools)
      {
        name: "stat",
        description: "Get metadata about a file or directory relative to the Lukhas root.",
        inputSchema: {
          type: "object",
          properties: { rel: { type: "string", description: "Relative path from Lukhas root" } },
          required: ["rel"]
        }
      },
      {
        name: "list_dir",
        description: "List entries in a directory under the Lukhas root.",
        inputSchema: {
          type: "object",
          properties: { rel: { type: "string", description: "Relative path to directory" } },
          required: ["rel"]
        }
      },
      {
        name: "search",
        description: "Full-text search across allowed text files within the Lukhas repo.",
        inputSchema: {
          type: "object",
          properties: {
            query: { type: "string", description: "Search query" },
            glob: { type: "string", description: "File pattern to search" },
            limit: { type: "number", description: "Maximum number of results" }
          },
          required: ["query"]
        }
      },
      {
        name: "get_file",
        description: "Retrieve a text file with automatic credential redaction.",
        inputSchema: {
          type: "object",
          properties: { rel: { type: "string", description: "Relative path to file" } },
          required: ["rel"]
        }
      },

      // TIER 1: CORE WRITE OPERATIONS
      {
        name: "write_file",
        description: "Create or overwrite a file with automatic backup and credential redaction.",
        inputSchema: {
          type: "object",
          properties: { 
            rel: { type: "string", description: "Relative path to file" },
            content: { type: "string", description: "File content to write" },
            backup: { type: "boolean", description: "Create backup before overwriting", default: true }
          },
          required: ["rel", "content"]
        }
      },
      {
        name: "delete_file",
        description: "Delete a file with automatic backup for safety.",
        inputSchema: {
          type: "object",
          properties: { 
            rel: { type: "string", description: "Relative path to file" },
            backup: { type: "boolean", description: "Create backup before deletion", default: true }
          },
          required: ["rel"]
        }
      },
      {
        name: "move_file",
        description: "Move or rename a file with automatic backup.",
        inputSchema: {
          type: "object",
          properties: { 
            src: { type: "string", description: "Source relative path" },
            dest: { type: "string", description: "Destination relative path" },
            backup: { type: "boolean", description: "Create backup", default: true }
          },
          required: ["src", "dest"]
        }
      },
      {
        name: "create_directory",
        description: "Create a directory structure.",
        inputSchema: {
          type: "object",
          properties: { rel: { type: "string", description: "Relative path to directory" } },
          required: ["rel"]
        }
      },
      {
        name: "copy_file",
        description: "Copy a file to a new location.",
        inputSchema: {
          type: "object",
          properties: { 
            src: { type: "string", description: "Source relative path" },
            dest: { type: "string", description: "Destination relative path" }
          },
          required: ["src", "dest"]
        }
      },

      // TIER 1: GIT OPERATIONS
      {
        name: "git_status",
        description: "Get current git repository status including branch and changes.",
        inputSchema: { type: "object", properties: {} }
      },
      {
        name: "git_diff",
        description: "Show git diff for specific file or all changes.",
        inputSchema: {
          type: "object",
          properties: { 
            file: { type: "string", description: "Specific file to diff" },
            staged: { type: "boolean", description: "Show staged changes", default: false }
          }
        }
      },
      {
        name: "git_add",
        description: "Stage files for commit.",
        inputSchema: {
          type: "object",
          properties: { 
            files: { 
              oneOf: [
                { type: "string", description: "Single file to add" },
                { type: "array", items: { type: "string" }, description: "Multiple files to add" }
              ]
            }
          },
          required: ["files"]
        }
      },
      {
        name: "git_commit",
        description: "Commit staged changes with a message.",
        inputSchema: {
          type: "object",
          properties: { 
            message: { type: "string", description: "Commit message" },
            files: { type: "array", items: { type: "string" }, description: "Specific files to commit" }
          },
          required: ["message"]
        }
      },
      {
        name: "git_create_branch",
        description: "Create a new git branch, optionally checking it out.",
        inputSchema: {
          type: "object",
          properties: { 
            name: { type: "string", description: "Branch name" },
            checkout: { type: "boolean", description: "Checkout new branch", default: true }
          },
          required: ["name"]
        }
      },
      {
        name: "git_checkout",
        description: "Switch to an existing git branch.",
        inputSchema: {
          type: "object",
          properties: { name: { type: "string", description: "Branch name" } },
          required: ["name"]
        }
      },
      {
        name: "git_stash",
        description: "Stash current changes with optional message.",
        inputSchema: {
          type: "object",
          properties: { message: { type: "string", description: "Stash message" } }
        }
      },

      // TIER 2: BUILD & DEVELOPMENT AUTOMATION
      {
        name: "run_command",
        description: "Execute a shell command safely with timeout protection.",
        inputSchema: {
          type: "object",
          properties: { 
            command: { type: "string", description: "Shell command to execute" },
            cwd: { type: "string", description: "Working directory" },
            timeout: { type: "number", description: "Timeout in milliseconds", default: 30000 }
          },
          required: ["command"]
        }
      },
      {
        name: "install_dependencies",
        description: "Install project dependencies using auto-detected package manager.",
        inputSchema: {
          type: "object",
          properties: { 
            package_manager: { type: "string", description: "Package manager to use", default: "auto" }
          }
        }
      },
      {
        name: "build_project",
        description: "Build the project using auto-detected build system.",
        inputSchema: {
          type: "object",
          properties: { target: { type: "string", description: "Build target" } }
        }
      },
      {
        name: "run_tests",
        description: "Execute test suite with optional pattern matching.",
        inputSchema: {
          type: "object",
          properties: { 
            pattern: { type: "string", description: "Test pattern to match" },
            watch: { type: "boolean", description: "Run in watch mode", default: false }
          }
        }
      },

      // TIER 3: ADVANCED ANALYSIS & INTELLIGENCE
      {
        name: "find_symbol_usage",
        description: "Find all usages of a function, class, or variable across the codebase.",
        inputSchema: {
          type: "object",
          properties: { 
            symbol: { type: "string", description: "Symbol name to find" },
            scope: { type: "string", description: "Search scope" }
          },
          required: ["symbol"]
        }
      },
      {
        name: "extract_imports",
        description: "Analyze import/export dependencies for a specific file.",
        inputSchema: {
          type: "object",
          properties: { file: { type: "string", description: "File to analyze" } },
          required: ["file"]
        }
      },
      {
        name: "run_linter",
        description: "Run linting tools (ESLint, Ruff) with optional auto-fix.",
        inputSchema: {
          type: "object",
          properties: { 
            files: { type: "array", items: { type: "string" }, description: "Files to lint" },
            fix: { type: "boolean", description: "Auto-fix issues", default: false }
          }
        }
      },
      {
        name: "format_code",
        description: "Format code using Prettier, Black, or other formatters.",
        inputSchema: {
          type: "object",
          properties: { 
            files: { type: "array", items: { type: "string" }, description: "Files to format" }
          }
        }
      },
      {
        name: "find_todos_fixmes",
        description: "Extract all TODO, FIXME, HACK, and other technical debt comments.",
        inputSchema: { type: "object", properties: {} }
      },
      {
        name: "analyze_code_complexity",
        description: "Analyze cyclomatic complexity and other metrics for a file.",
        inputSchema: {
          type: "object",
          properties: { file: { type: "string", description: "File to analyze" } },
          required: ["file"]
        }
      },
      {
        name: "find_unused_code",
        description: "Identify potentially unused functions, classes, and variables.",
        inputSchema: { type: "object", properties: {} }
      },

      // TIER 4: LUKHAS-SPECIFIC CONSCIOUSNESS TOOLS
      {
        name: "validate_trinity_compliance",
        description: "Check Trinity Framework (⚛️🧠🛡️) compliance across files.",
        inputSchema: {
          type: "object",
          properties: { 
            files: { type: "array", items: { type: "string" }, description: "Files to validate" }
          }
        }
      },
      {
        name: "audit_symbolic_vocabulary",
        description: "Analyze usage of LUKHAS symbolic vocabulary and consistency.",
        inputSchema: { type: "object", properties: {} }
      },
      {
        name: "create_feature_branch",
        description: "Auto-generate and create a feature branch from task description.",
        inputSchema: {
          type: "object",
          properties: { task_description: { type: "string", description: "Task description" } },
          required: ["task_description"]
        }
      },
      {
        name: "backup_workspace",
        description: "Create a full backup of the workspace excluding large directories.",
        inputSchema: { type: "object", properties: {} }
      }
    ]
  };
});

// ============================================================================
// HANDLE ALL TOOL CALLS (Unified Request Handler)
// ============================================================================

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  try {
    const { name, arguments: args } = request.params;

    switch (name) {
      // TIER 1: CORE READ OPERATIONS
      case "stat": {
        const rel = String(args?.rel || ".");
        const res = await statRel(rel);
        return { content: [{ type: "text", text: JSON.stringify(res, null, 2) }] };
      }

      case "list_dir": {
        const rel = String(args?.rel || ".");
        const res = await listDir(rel);
        return { content: [{ type: "text", text: JSON.stringify(res, null, 2) }] };
      }

      case "search": {
        const parsed = SearchSchema.safeParse({
          query: args?.query,
          glob: args?.glob,
          limit: args?.limit
        });
        if (!parsed.success) {
          return { content: [{ type: "text", text: `Invalid args: ${parsed.error.message}` }] };
        }
        const { query, glob, limit } = parsed.data;
        const res = await searchFiles(query, glob, limit);
        return { content: [{ type: "text", text: JSON.stringify(res, null, 2) }] };
      }

      case "get_file": {
        const rel = String(args?.rel);
        const res = await getFile(rel);
        return { content: [{ type: "text", text: JSON.stringify(res, null, 2) }] };
      }

      // TIER 1: CORE WRITE OPERATIONS
      case "write_file": {
        const rel = String(args?.rel);
        const content = String(args?.content);
        const backup = Boolean(args?.backup ?? true);
        const res = await writeFile(rel, content, backup);
        return { content: [{ type: "text", text: JSON.stringify(res, null, 2) }] };
      }

      case "delete_file": {
        const rel = String(args?.rel);
        const backup = Boolean(args?.backup ?? true);
        const res = await deleteFile(rel, backup);
        return { content: [{ type: "text", text: JSON.stringify(res, null, 2) }] };
      }

      case "move_file": {
        const src = String(args?.src);
        const dest = String(args?.dest);
        const backup = Boolean(args?.backup ?? true);
        const res = await moveFile(src, dest, backup);
        return { content: [{ type: "text", text: JSON.stringify(res, null, 2) }] };
      }

      case "create_directory": {
        const rel = String(args?.rel);
        const res = await createDirectory(rel);
        return { content: [{ type: "text", text: JSON.stringify(res, null, 2) }] };
      }

      case "copy_file": {
        const src = String(args?.src);
        const dest = String(args?.dest);
        const res = await copyFile(src, dest);
        return { content: [{ type: "text", text: JSON.stringify(res, null, 2) }] };
      }

      // TIER 1: GIT OPERATIONS
      case "git_status": {
        const res = await gitStatus();
        return { content: [{ type: "text", text: JSON.stringify(res, null, 2) }] };
      }

      case "git_diff": {
        const file = args?.file ? String(args.file) : undefined;
        const staged = Boolean(args?.staged);
        const res = await gitDiff(file, staged);
        return { content: [{ type: "text", text: JSON.stringify(res, null, 2) }] };
      }

      case "git_add": {
        const res = await gitAdd(args?.files as string | string[]);
        return { content: [{ type: "text", text: JSON.stringify(res, null, 2) }] };
      }

      case "git_commit": {
        const message = String(args?.message);
        const files = args?.files as string[] | undefined;
        const res = await gitCommit(message, files);
        return { content: [{ type: "text", text: JSON.stringify(res, null, 2) }] };
      }

      case "git_create_branch": {
        const name = String(args?.name);
        const checkout = Boolean(args?.checkout ?? true);
        const res = await gitCreateBranch(name, checkout);
        return { content: [{ type: "text", text: JSON.stringify(res, null, 2) }] };
      }

      case "git_checkout": {
        const name = String(args?.name);
        const res = await gitCheckout(name);
        return { content: [{ type: "text", text: JSON.stringify(res, null, 2) }] };
      }

      case "git_stash": {
        const message = args?.message ? String(args.message) : undefined;
        const res = await gitStash(message);
        return { content: [{ type: "text", text: JSON.stringify(res, null, 2) }] };
      }

      // TIER 2: BUILD & DEVELOPMENT AUTOMATION
      case "run_command": {
        const command = String(args?.command);
        const cwd = args?.cwd ? String(args.cwd) : undefined;
        const timeout = Number(args?.timeout || 30000);
        const res = await runCommand(command, cwd, timeout);
        return { content: [{ type: "text", text: JSON.stringify(res, null, 2) }] };
      }

      case "install_dependencies": {
        const packageManager = String(args?.package_manager || "auto");
        const res = await installDependencies(packageManager);
        return { content: [{ type: "text", text: JSON.stringify(res, null, 2) }] };
      }

      case "build_project": {
        const target = args?.target ? String(args.target) : undefined;
        const res = await buildProject(target);
        return { content: [{ type: "text", text: JSON.stringify(res, null, 2) }] };
      }

      case "run_tests": {
        const pattern = args?.pattern ? String(args.pattern) : undefined;
        const watch = Boolean(args?.watch);
        const res = await runTests(pattern, watch);
        return { content: [{ type: "text", text: JSON.stringify(res, null, 2) }] };
      }

      // TIER 3: ADVANCED ANALYSIS & INTELLIGENCE
      case "find_symbol_usage": {
        const symbol = String(args?.symbol);
        const scope = args?.scope ? String(args.scope) : undefined;
        const res = await findSymbolUsage(symbol, scope);
        return { content: [{ type: "text", text: JSON.stringify(res, null, 2) }] };
      }

      case "extract_imports": {
        const file = String(args?.file);
        const res = await extractImports(file);
        return { content: [{ type: "text", text: JSON.stringify(res, null, 2) }] };
      }

      case "run_linter": {
        const files = args?.files as string[] | undefined;
        const fix = Boolean(args?.fix);
        const res = await runLinter(files, fix);
        return { content: [{ type: "text", text: JSON.stringify(res, null, 2) }] };
      }

      case "format_code": {
        const files = args?.files as string[] | undefined;
        const res = await formatCode(files);
        return { content: [{ type: "text", text: JSON.stringify(res, null, 2) }] };
      }

      case "find_todos_fixmes": {
        const res = await findTodosFixmes();
        return { content: [{ type: "text", text: JSON.stringify(res, null, 2) }] };
      }

      case "analyze_code_complexity": {
        const file = String(args?.file);
        const res = await analyzeCodeComplexity(file);
        return { content: [{ type: "text", text: JSON.stringify(res, null, 2) }] };
      }

      case "find_unused_code": {
        const res = await findUnusedCode();
        return { content: [{ type: "text", text: JSON.stringify(res, null, 2) }] };
      }

      // TIER 4: LUKHAS-SPECIFIC CONSCIOUSNESS TOOLS
      case "validate_trinity_compliance": {
        const files = args?.files as string[] | undefined;
        const res = await validateTrinityCompliance(files);
        return { content: [{ type: "text", text: JSON.stringify(res, null, 2) }] };
      }

      case "audit_symbolic_vocabulary": {
        const res = await auditSymbolicVocabulary();
        return { content: [{ type: "text", text: JSON.stringify(res, null, 2) }] };
      }

      case "create_feature_branch": {
        const taskDescription = String(args?.task_description);
        const res = await createFeatureBranch(taskDescription);
        return { content: [{ type: "text", text: JSON.stringify(res, null, 2) }] };
      }

      case "backup_workspace": {
        const res = await backupWorkspace();
        return { content: [{ type: "text", text: JSON.stringify(res, null, 2) }] };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error: any) {
    return {
      content: [{ 
        type: "text", 
        text: `Error: ${error?.message || 'Unknown error'}` 
      }],
      isError: true
    };
  }
});

// ============================================================================
// SERVER STARTUP
// ============================================================================

server.onerror = (err) => {
  console.error("Ultimate MCP server error:", err);
};

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("🚀 Ultimate LUKHAS MCP Server running on stdio - All 4 Tiers Active! ⚛️🧠🛡️");
}

main().catch((error) => {
  console.error("Failed to start server:", error);
  process.exit(1);
});
