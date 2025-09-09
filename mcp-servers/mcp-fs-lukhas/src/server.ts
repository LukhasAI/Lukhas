import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";
import { statRel, listDir, searchFiles, getFile, SearchSchema, readRange, ReadRangeSchema } from "./fsTools.js";

const server = new Server(
  {
    name: "mcp-fs-lukhas",
    version: "0.1.0"
  },
  {
    capabilities: {
      tools: {}
    }
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "stat",
        description: "Get metadata about a file or directory relative to the Lukhas root.",
        inputSchema: {
          type: "object",
          properties: { 
            rel: { 
              type: "string", 
              description: "Relative path from Lukhas root (e.g., '.', 'src/')" 
            } 
          },
          required: ["rel"]
        }
      },
      {
        name: "list_dir",
        description: "List entries in a directory under the Lukhas root.",
        inputSchema: {
          type: "object",
          properties: { 
            rel: { 
              type: "string",
              description: "Relative path to directory"
            } 
          },
          required: ["rel"]
        }
      },
      {
        name: "search",
        description: "Full-text search across allowed text files within the Lukhas repo.",
        inputSchema: {
          type: "object",
          properties: {
            query: { 
              type: "string",
              description: "Search query"
            },
            glob: { 
              type: "string",
              description: "File pattern to search"
            },
            limit: { 
              type: "number",
              description: "Maximum number of results"
            }
          },
          required: ["query"]
        }
      },
      {
        name: "get_file",
        description: "Retrieve a small text file. Blocks binaries and large files.",
        inputSchema: {
          type: "object",
          properties: { 
            rel: { 
              type: "string",
              description: "Relative path to file"
            } 
          },
          required: ["rel"]
        }
      },
      {
        name: "read_range",
        description: "Read a range of bytes from a text file. For large files, use this instead of get_file.",
        inputSchema: {
          type: "object",
          properties: {
            rel: {
              type: "string",
              description: "Relative path to file"
            },
            offset: {
              type: "number",
              description: "Byte offset to start reading from (>= 0)"
            },
            length: {
              type: "number", 
              description: "Number of bytes to read (0-65536)"
            }
          },
          required: ["rel", "offset", "length"]
        }
      }
    ]
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  try {
    switch (request.params.name) {
      case "stat": {
        const rel = String(request.params.arguments?.rel || ".");
        const res = await statRel(rel);
        return {
          content: [{ type: "text", text: JSON.stringify(res, null, 2) }]
        };
      }
      
      case "list_dir": {
        const rel = String(request.params.arguments?.rel || ".");
        const res = await listDir(rel);
        return {
          content: [{ type: "text", text: JSON.stringify(res, null, 2) }]
        };
      }
      
      case "search": {
        const parsed = SearchSchema.safeParse({
          query: request.params.arguments?.query,
          glob: request.params.arguments?.glob,
          limit: request.params.arguments?.limit
        });
        if (!parsed.success) {
          return {
            content: [{ type: "text", text: `Invalid args: ${parsed.error.message}` }]
          };
        }
        const { query, glob, limit } = parsed.data;
        const res = await searchFiles(query, glob, limit);
        return {
          content: [{ type: "text", text: JSON.stringify(res, null, 2) }]
        };
      }
      
      case "get_file": {
        const rel = String(request.params.arguments?.rel);
        const res = await getFile(rel);
        return {
          content: [{ type: "text", text: JSON.stringify(res, null, 2) }]
        };
      }
      
      case "read_range": {
        const parsed = ReadRangeSchema.safeParse({
          rel: request.params.arguments?.rel,
          offset: request.params.arguments?.offset,
          length: request.params.arguments?.length
        });
        if (!parsed.success) {
          return {
            content: [{ type: "text", text: `Invalid args: ${parsed.error.message}` }]
          };
        }
        const { rel, offset, length } = parsed.data;
        const res = await readRange(rel, offset, length);
        return {
          content: [{ type: "text", text: JSON.stringify(res, null, 2) }]
        };
      }
      
      default:
        throw new Error(`Unknown tool: ${request.params.name}`);
    }
  } catch (error) {
    return {
      content: [{ type: "text", text: `Error: ${(error as Error).message}` }]
    };
  }
});

server.onerror = (err: Error) => {
  console.error("MCP server error:", err);
};

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("mcp-fs-lukhas running on stdio");
}

main().catch((error) => {
  console.error("Server failed to start:", error);
  process.exit(1);
});
