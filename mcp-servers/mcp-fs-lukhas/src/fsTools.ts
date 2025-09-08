import fg from "fast-glob";
import fs from "fs-extra";
import lunr from "lunr";
import path from "node:path";
import stripBom from "strip-bom";
import { z } from "zod";

const ROOT = process.env.MCP_FS_ROOT || "/Users/agi_dev/LOCAL-REPOS/Lukhas";
const MAX_BYTES = parseInt(process.env.MCP_MAX_BYTES || "2097152"); // 2 MB read cap
const TEXT_EXT = new Set([
  // Documentation & Text
  ".md", ".txt", ".rst", ".adoc",
  // Source Code
  ".ts", ".tsx", ".js", ".jsx", ".py", ".rs", ".go", ".java", ".cpp", ".c", ".h",
  // Configuration Files
  ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf", ".config",
  // Web & Styling
  ".css", ".scss", ".sass", ".less", ".html", ".htm", ".xml", ".svg",
  // Build & Package Configs
  ".lock", ".gitignore", ".gitattributes", ".editorconfig", ".prettierrc",
  // Other Config Extensions
  ".properties", ".env.example", ".env.template", ".env.sample"
]);

// Security: Denylist sensitive paths
const DENYLIST = ["secrets/", "keys/", ".env", ".env.*", "*.key", "*.pem", "*.p12"];

// Rate limiting: Simple token bucket
class TokenBucket {
  private tokens: number;
  private lastRefill: number;
  private readonly capacity = 10;
  private readonly refillRate = 10; // tokens per 10 seconds

  constructor() {
    this.tokens = this.capacity;
    this.lastRefill = Date.now();
  }

  consume(): boolean {
    this.refill();
    if (this.tokens > 0) {
      this.tokens--;
      return true;
    }
    return false;
  }

  private refill() {
    const now = Date.now();
    const elapsed = (now - this.lastRefill) / 1000;
    const tokensToAdd = Math.floor(elapsed / 10) * this.refillRate;
    this.tokens = Math.min(this.capacity, this.tokens + tokensToAdd);
    this.lastRefill = now;
  }
}

const rateLimiter = new TokenBucket();

// Input validation schemas
const PathSchema = z.string().min(1).max(500).refine(
  (path) => !/[\x00-\x1f\x7f-\x9f]/.test(path),
  { message: "Invalid control characters in path" }
);

const QuerySchema = z.string().min(1).max(1000).refine(
  (query) => !/[\x00-\x1f\x7f-\x9f]/.test(query),
  { message: "Invalid control characters in query" }
);

// Security: Credential redaction
function redact(text: string): { text: string; redacted: boolean } {
  let redacted = false;
  let result = text;
  
  // AWS keys
  result = result.replace(/AKIA[0-9A-Z]{16}/g, () => { redacted = true; return "[REDACTED-AWS-KEY]"; });
  
  // GitHub tokens
  result = result.replace(/ghp_[A-Za-z0-9]{36,}/g, () => { redacted = true; return "[REDACTED-GITHUB-TOKEN]"; });
  
  // Generic API keys
  result = result.replace(/api[_-]?key\s*[:=]\s*["\']?[A-Za-z0-9_\-]{16,}["\']?/gi, () => { 
    redacted = true; 
    return "[REDACTED-API-KEY]"; 
  });
  
  // Strip ANSI escapes
  result = result.replace(/\x1b\[[0-9;]*m/g, "");
  
  // Strip HTML/script tags
  result = result.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, "[REDACTED-SCRIPT]");
  result = result.replace(/<[^>]+>/g, "");
  
  return { text: result, redacted };
}

// Security: Check denylist
function isDenylisted(rel: string): boolean {
  return DENYLIST.some(pattern => {
    if (pattern.includes("*")) {
      const regex = new RegExp(pattern.replace(/\*/g, ".*"));
      return regex.test(rel);
    }
    return rel.includes(pattern);
  });
}

// Logging helper
function logOperation(tool: string, args: any, duration: number, resultInfo: any, denied = false, redacted = false) {
  const logEntry = {
    timestamp: new Date().toISOString(),
    tool,
    argsHash: JSON.stringify(args).slice(0, 100),
    duration,
    resultInfo,
    denied,
    redacted
  };
  console.error(JSON.stringify(logEntry));
}

function resolveSafe(p: string) {
  const joined = path.resolve(ROOT, p);
  if (!joined.startsWith(path.resolve(ROOT))) {
    throw new Error("Path traversal blocked");
  }
  return joined;
}

function withRateLimit<T extends any[], R>(fn: (...args: T) => Promise<R>) {
  return async (...args: T): Promise<R> => {
    if (!rateLimiter.consume()) {
      throw new Error("Rate limit exceeded. Please try again in a few seconds.");
    }
    return fn(...args);
  };
}

export const statRel = withRateLimit(async (rel: string) => {
  const start = Date.now();
  try {
    const validatedRel = PathSchema.parse(rel || ".");
    
    if (isDenylisted(validatedRel)) {
      logOperation("stat", { rel }, Date.now() - start, null, true);
      throw new Error("Access denied: path is denylisted");
    }
    
    const full = resolveSafe(validatedRel);
    const st = await fs.stat(full);
    const result = { rel: validatedRel, full, isFile: st.isFile(), isDir: st.isDirectory(), size: st.size, mtime: st.mtimeMs };
    
    logOperation("stat", { rel }, Date.now() - start, { size: st.size });
    return result;
  } catch (error) {
    logOperation("stat", { rel }, Date.now() - start, null, false, false);
    throw error;
  }
});

export const listDir = withRateLimit(async (rel: string) => {
  const start = Date.now();
  try {
    const validatedRel = PathSchema.parse(rel || ".");
    
    if (isDenylisted(validatedRel)) {
      logOperation("list_dir", { rel }, Date.now() - start, null, true);
      throw new Error("Access denied: path is denylisted");
    }
    
    const full = resolveSafe(validatedRel);
    const st = await fs.stat(full);
    if (!st.isDirectory()) throw new Error("Not a directory");
    
    const entries = await fs.readdir(full);
    const meta = await Promise.all(entries.map(async (name: string) => {
      const p = path.join(full, name);
      const s = await fs.stat(p);
      const entryRel = path.relative(ROOT, p);
      return { name, rel: entryRel, isFile: s.isFile(), isDir: s.isDirectory(), size: s.size, mtime: s.mtimeMs };
    }));
    
    // Filter out denylisted entries
    const filteredMeta = meta.filter((entry: any) => !isDenylisted(entry.rel));
    
    logOperation("list_dir", { rel }, Date.now() - start, { count: filteredMeta.length });
    return filteredMeta;
  } catch (error) {
    logOperation("list_dir", { rel }, Date.now() - start, null, false, false);
    throw error;
  }
});

export const SearchSchema = z.object({
  query: QuerySchema,
  glob: z.string().default("**/*.{md,txt,ts,tsx,js,jsx,py,json,yaml,yml,toml}"),
  limit: z.number().int().positive().max(200).default(50)
});

export async function buildIndex(globPattern: string) {
  const base = path.resolve(ROOT);
  const files = await fg(globPattern, { 
    cwd: base, 
    dot: false, 
    onlyFiles: true, 
    ignore: [
      "**/node_modules/**", 
      "**/.git/**", 
      "**/.next/**", 
      "**/.venv/**", 
      "**/dist/**", 
      "**/build/**", 
      "**/*.ipynb_checkpoints/**"
    ] 
  });
  
  const docs: { id: string; rel: string; text: string }[] = [];

  for (const rel of files) {
    if (isDenylisted(rel)) continue;
    
    const full = resolveSafe(rel);
    try {
      const ext = path.extname(full).toLowerCase();
      if (!TEXT_EXT.has(ext)) continue;
      const buf = await fs.readFile(full);
      if (buf.byteLength > MAX_BYTES) continue;
      const text = stripBom(buf.toString("utf8"));
      if (!text.trim()) continue;
      docs.push({ id: rel, rel, text });
    } catch { /* skip */ }
  }

  const idx = lunr(function (this: any) {
    this.ref("id");
    this.field("text");
    for (const d of docs) this.add(d);
  });

  const map = new Map(docs.map(d => [d.id, d]));
  return { idx, map };
}

export const searchFiles = withRateLimit(async (query: string, globPattern: string, limit: number) => {
  const start = Date.now();
  try {
    const { idx, map } = await buildIndex(globPattern);
    const results = idx.search(query).slice(0, limit);
    const output = results.map((r: any) => {
      const d = map.get(r.ref)!;
      return { rel: d.rel, score: Number(r.score.toFixed(4)) };
    });
    
    logOperation("search", { query: query.slice(0, 50) }, Date.now() - start, { count: output.length });
    return output;
  } catch (error) {
    logOperation("search", { query: query.slice(0, 50) }, Date.now() - start, null, false, false);
    throw error;
  }
});

export const getFile = withRateLimit(async (rel: string) => {
  const start = Date.now();
  try {
    const validatedRel = PathSchema.parse(rel);
    
    if (isDenylisted(validatedRel)) {
      logOperation("get_file", { rel }, Date.now() - start, null, true);
      throw new Error("Access denied: path is denylisted");
    }
    
    const full = resolveSafe(validatedRel);
    const st = await fs.stat(full);
    if (!st.isFile()) throw new Error("Not a file");
    if (st.size > MAX_BYTES) throw new Error(`File too large (> ${MAX_BYTES} bytes)`);
    const ext = path.extname(full).toLowerCase();
    if (!TEXT_EXT.has(ext)) throw new Error("Binary or unsupported text type blocked");
    
    const text = stripBom(await fs.readFile(full, "utf8"));
    const { text: cleanText, redacted: wasRedacted } = redact(text);
    
    const result = { rel: validatedRel, size: st.size, mtime: st.mtimeMs, text: cleanText, redacted: wasRedacted };
    
    logOperation("get_file", { rel }, Date.now() - start, { size: st.size }, false, wasRedacted);
    return result;
  } catch (error) {
    logOperation("get_file", { rel }, Date.now() - start, null, false, false);
    throw error;
  }
});
