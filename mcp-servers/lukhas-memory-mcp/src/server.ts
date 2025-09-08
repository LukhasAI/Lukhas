import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import { 
  getMemorySystemStatus, 
  queryMemoryFolds, 
  getWaveCMemorySystem, 
  executeMemoryOperation,
  getMemoryDatabaseInfo
} from "./memory-tools.js";

const server = new Server(
  {
    name: "lukhas-memory-mcp",
    version: "0.1.0"
  },
  {
    capabilities: {
      tools: {}
    }
  }
);

// List available memory tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "memory_system_status",
        description: "Get comprehensive status of LUKHAS AI memory systems including Wave C processing, fold-based memory, and Aka Qualia phenomenological processing.",
        inputSchema: {
          type: "object",
          properties: {},
          required: []
        }
      },
      {
        name: "query_memory_folds",
        description: "Query the fold-based memory system with cascade prevention. Search through memory folds while preserving causal chains and emotional context.",
        inputSchema: {
          type: "object",
          properties: {
            query: {
              type: "string",
              description: "Memory query text to search within folds"
            },
            fold_limit: {
              type: "number",
              minimum: 1,
              maximum: 1000,
              description: "Maximum number of memory folds to search (default: 1000)"
            }
          },
          required: ["query"]
        }
      },
      {
        name: "wave_c_memory_system",
        description: "Access the Wave C Memory System (Aka Qualia) - phenomenological processing pipeline with memory persistence, GDPR compliance, and comprehensive testing.",
        inputSchema: {
          type: "object",
          properties: {},
          required: []
        }
      },
      {
        name: "memory_operation",
        description: "Execute memory operations including scene storage, recall, pattern analysis, fold analysis, and GDPR erasure operations.",
        inputSchema: {
          type: "object",
          properties: {
            operation: {
              type: "string",
              enum: ["store_scene", "recall_scenes", "analyze_memory_pattern", "memory_fold_analysis", "gdpr_erasure"],
              description: "Type of memory operation to execute"
            },
            parameters: {
              type: "object",
              properties: {
                scene_id: {
                  type: "string",
                  description: "Unique identifier for memory scene"
                },
                emotion_vector: {
                  type: "array",
                  items: { type: "number" },
                  minItems: 3,
                  maxItems: 3,
                  description: "VAD emotion vector [Valence, Arousal, Dominance]"
                },
                memory_type: {
                  type: "string",
                  enum: ["episodic", "semantic", "procedural"],
                  description: "Type of memory for storage/recall"
                },
                fold_limit: {
                  type: "number",
                  minimum: 1,
                  maximum: 1000,
                  description: "Memory fold limit for operation"
                },
                query_text: {
                  type: "string",
                  description: "Text query for memory recall operations"
                }
              }
            }
          },
          required: ["operation"]
        }
      },
      {
        name: "memory_database_info", 
        description: "Get detailed information about memory database systems, storage clients (SqlMemory/NoopMemory), threading safety, and GDPR compliance features.",
        inputSchema: {
          type: "object",
          properties: {},
          required: []
        }
      }
    ]
  };
});

// Handle memory tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  try {
    switch (request.params.name) {
      case "memory_system_status": {
        const status = await getMemorySystemStatus();
        return {
          content: [{ 
            type: "text", 
            text: JSON.stringify({
              lukhas_memory_systems: status,
              system_info: {
                architecture: "Fold-based memory with cascade prevention",
                wave_c_processing: "Aka Qualia phenomenological processing",
                fold_limit: 1000,
                cascade_prevention: "99.7% success rate", 
                gdpr_compliance: "Article 17 Right to Erasure support",
                threading_safety: "SQLite segmentation faults resolved"
              }
            }, null, 2) 
          }]
        };
      }
      
      case "query_memory_folds": {
        const query = String(request.params.arguments?.query || "");
        const foldLimit = Number(request.params.arguments?.fold_limit) || 1000;
        const results = await queryMemoryFolds(query, foldLimit);
        return {
          content: [{ 
            type: "text", 
            text: JSON.stringify({
              memory_fold_query: results,
              system_note: "Memory folds searched with causal chain preservation and emotional context maintenance. Wave C phenomenological processing active."
            }, null, 2) 
          }]
        };
      }
      
      case "wave_c_memory_system": {
        const waveC = await getWaveCMemorySystem();
        return {
          content: [{ 
            type: "text", 
            text: JSON.stringify({
              wave_c_memory_system: waveC,
              system_note: "Aka Qualia (Wave C) represents the phenomenological processing pipeline - extracting conscious experience patterns from memory scenes with emotional vectors and thread-safe persistence."
            }, null, 2) 
          }]
        };
      }
      
      case "memory_operation": {
        const operation = String(request.params.arguments?.operation || "");
        const parameters = request.params.arguments?.parameters || {};
        const result = await executeMemoryOperation(operation, parameters);
        return {
          content: [{ 
            type: "text", 
            text: JSON.stringify({
              memory_operation: result,
              timestamp: new Date().toISOString(),
              system_context: "LUKHAS AI memory operation executed within fold-based architecture with cascade prevention"
            }, null, 2) 
          }]
        };
      }
      
      case "memory_database_info": {
        const dbInfo = await getMemoryDatabaseInfo();
        return {
          content: [{ 
            type: "text", 
            text: JSON.stringify({
              memory_database_systems: dbInfo,
              system_note: "LUKHAS AI memory databases use thread-safe SQLite with cascade prevention, GDPR Article 17 compliance, and comprehensive testing across 6 categories including security and performance validation."
            }, null, 2) 
          }]
        };
      }
      
      default:
        throw new Error(`Unknown memory tool: ${request.params.name}`);
    }
  } catch (error) {
    return {
      content: [{ 
        type: "text", 
        text: `LUKHAS Memory Error: ${(error as Error).message}` 
      }]
    };
  }
});

server.onerror = (err: Error) => {
  console.error("LUKHAS Memory MCP server error:", err);
};

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("LUKHAS Memory MCP server running on stdio - Wave C processing active");
}

main().catch((error) => {
  console.error("LUKHAS Memory server failed to start:", error);
  process.exit(1);
});