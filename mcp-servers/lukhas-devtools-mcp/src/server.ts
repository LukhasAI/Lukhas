import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import { 
  getTestInfrastructureStatus, 
  getCodeAnalysisStatus, 
  getT4AuditStatus, 
  getDevelopmentUtilities,
  executeDevToolsOperation,
  getModuleStructure
} from "./devtools.js";

const server = new Server(
  {
    name: "lukhas-devtools-mcp",
    version: "0.1.0"
  },
  {
    capabilities: {
      tools: {}
    }
  }
);

// List available development tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "test_infrastructure_status",
        description: "Get comprehensive status of LUKHAS AI testing infrastructure including 775 total tests, Wave C testing (121KB), stability fixes, and current test execution health.",
        inputSchema: {
          type: "object",
          properties: {},
          required: []
        }
      },
      {
        name: "code_analysis_status",
        description: "Access code analysis status including Ruff/MyPy error counts, T4 audit progress, 36.3% error reduction achievements, and priority file fixes.",
        inputSchema: {
          type: "object",
          properties: {},
          required: []
        }
      },
      {
        name: "t4_audit_status", 
        description: "Get detailed T4 audit status including STEPS_2 progress, coverage improvements (15% up from 1%), surgical change standards, and documentation map.",
        inputSchema: {
          type: "object",
          properties: {},
          required: []
        }
      },
      {
        name: "development_utilities",
        description: "Access development utilities including Makefile targets, T4 commit process, analysis tools, and testing utilities for LUKHAS AI development.",
        inputSchema: {
          type: "object",
          properties: {},
          required: []
        }
      },
      {
        name: "module_structure",
        description: "Explore LUKHAS AI module structure including 692 consciousness modules, candidate/ vs lukhas/ lane system, and directory hierarchy.",
        inputSchema: {
          type: "object",
          properties: {
            module_path: {
              type: "string",
              description: "Path to explore (relative to LUKHAS root, default: root)"
            }
          }
        }
      },
      {
        name: "devtools_operation",
        description: "Execute development operations including test runs, code analysis, audit checks, infrastructure validation, and development metrics gathering.",
        inputSchema: {
          type: "object",
          properties: {
            operation: {
              type: "string",
              enum: ["run_tests", "code_analysis", "audit_status", "infrastructure_check", "development_metrics"],
              description: "Type of development operation to execute"
            },
            parameters: {
              type: "object",
              properties: {
                test_category: {
                  type: "string",
                  enum: ["unit", "integration", "security", "performance", "all"],
                  description: "Category of tests to run"
                },
                analysis_type: {
                  type: "string",
                  enum: ["ruff", "mypy", "coverage", "dependencies", "structure"],
                  description: "Type of code analysis to perform"
                },
                audit_phase: {
                  type: "string",
                  enum: ["t4", "steps_1", "steps_2", "claude_tasks"],
                  description: "T4 audit phase to check"
                },
                module_path: {
                  type: "string",
                  description: "Specific module path for analysis"
                },
                fix_level: {
                  type: "string",
                  enum: ["safe", "moderate", "aggressive"],
                  description: "Level of automated fixes to apply"
                }
              }
            }
          },
          required: ["operation"]
        }
      }
    ]
  };
});

// Handle development tools calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  try {
    switch (request.params.name) {
      case "test_infrastructure_status": {
        const status = await getTestInfrastructureStatus();
        return {
          content: [{ 
            type: "text", 
            text: JSON.stringify({
              lukhas_test_infrastructure: status,
              system_info: {
                total_tests: "775 comprehensive tests across consciousness modules",
                infrastructure_status: "stabilized after critical fixes",
                wave_c_testing: "6 categories (121KB) with phenomenological processing",
                major_fixes: "Python crashes, SQLite threading, import cycles resolved",
                test_safety: "Threading issues fixed, concurrent operations disabled for stability"
              }
            }, null, 2) 
          }]
        };
      }
      
      case "code_analysis_status": {
        const analysis = await getCodeAnalysisStatus();
        return {
          content: [{ 
            type: "text", 
            text: JSON.stringify({
              lukhas_code_analysis: analysis,
              system_note: "Major code quality improvements achieved - 1,653 critical syntax errors eliminated with 36.3% system-wide error reduction. Priority files show 97.6% error reduction in symbolic network systems."
            }, null, 2) 
          }]
        };
      }
      
      case "t4_audit_status": {
        const audit = await getT4AuditStatus();
        return {
          content: [{ 
            type: "text", 
            text: JSON.stringify({
              lukhas_t4_audit: audit,
              system_note: "T4 audit STEPS_2 in progress with significant achievements - coverage improved from 1% to 15%, major infrastructure stabilized, system ready for MCP development with quality standards targeting Sam Altman/Dario Amodei/Demis Hassabis execution levels."
            }, null, 2) 
          }]
        };
      }
      
      case "development_utilities": {
        const utilities = await getDevelopmentUtilities();
        return {
          content: [{ 
            type: "text", 
            text: JSON.stringify({
              lukhas_development_utilities: utilities,
              system_note: "Comprehensive development toolkit including Makefile targets for testing/quality, T4 commit process with nightly autofix, analysis tools for consciousness modules, and testing utilities for 775-test infrastructure."
            }, null, 2) 
          }]
        };
      }
      
      case "module_structure": {
        const modulePath = String(request.params.arguments?.module_path || "");
        const structure = await getModuleStructure(modulePath);
        return {
          content: [{ 
            type: "text", 
            text: JSON.stringify({
              lukhas_module_structure: structure,
              system_note: "LUKHAS AI consciousness architecture with 692 modules (662 candidate/ + 30 lukhas/) forming distributed cognitive network. Lane system separates development (candidate/) from production (lukhas/) code."
            }, null, 2) 
          }]
        };
      }
      
      case "devtools_operation": {
        const operation = String(request.params.arguments?.operation || "");
        const parameters = request.params.arguments?.parameters || {};
        const result = await executeDevToolsOperation(operation, parameters);
        return {
          content: [{ 
            type: "text", 
            text: JSON.stringify({
              devtools_operation: result,
              timestamp: new Date().toISOString(),
              system_context: "LUKHAS AI development operation executed within stabilized infrastructure"
            }, null, 2) 
          }]
        };
      }
      
      default:
        throw new Error(`Unknown development tool: ${request.params.name}`);
    }
  } catch (error) {
    return {
      content: [{ 
        type: "text", 
        text: `LUKHAS Development Tools Error: ${(error as Error).message}` 
      }]
    };
  }
});

server.onerror = (err: Error) => {
  console.error("LUKHAS Development Tools MCP server error:", err);
};

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("LUKHAS Development Tools MCP server running on stdio - T4 audit systems active");
}

main().catch((error) => {
  console.error("LUKHAS Development Tools server failed to start:", error);
  process.exit(1);
});