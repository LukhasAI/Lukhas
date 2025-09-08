import * as fs from "fs-extra";
import { spawn } from "node:child_process";
import path from "node:path";
import { z } from "zod";

const ROOT = process.env.MCP_FS_ROOT || "/Users/agi_dev/LOCAL-REPOS/Lukhas";
const MAX_BYTES = parseInt(process.env.MCP_MAX_BYTES || "2097152"); // 2 MB read cap
const BACKUP_DIR = path.join(ROOT, ".mcp-backups");

// Ensure backup directory exists
fs.ensureDirSync(BACKUP_DIR);

// Enhanced file extensions for comprehensive coverage
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
  ".properties", ".env.example", ".env.template", ".env.sample",
  // Additional Development Files
  ".sh", ".bash", ".zsh", ".fish", ".ps1", ".bat", ".dockerfile", ".makefile"
]);

// Security: Denylist sensitive paths (keep existing security)
const DENYLIST = [
  "secrets/", "keys/", ".env", ".env.*", "*.key", "*.pem", "*.p12",
  "node_modules/", ".git/", "dist/", "build/", "__pycache__/", ".pytest_cache/"
];

// Enhanced rate limiting for write operations
class EnhancedTokenBucket {
  private readTokens: number;
  private writeTokens: number;
  private lastRefill: number;
  private readonly readCapacity = 20; // More reads allowed
  private readonly writeCapacity = 10; // Fewer writes for safety
  private readonly refillRate = 10; // tokens per 10 seconds

  constructor() {
    this.readTokens = this.readCapacity;
    this.writeTokens = this.writeCapacity;
    this.lastRefill = Date.now();
  }

  consumeRead(): boolean {
    this.refill();
    if (this.readTokens > 0) {
      this.readTokens--;
      return true;
    }
    return false;
  }

  consumeWrite(): boolean {
    this.refill();
    if (this.writeTokens > 0) {
      this.writeTokens--;
      return true;
    }
    return false;
  }

  private refill() {
    const now = Date.now();
    const elapsed = (now - this.lastRefill) / 1000;
    const tokensToAdd = Math.floor(elapsed / 10) * this.refillRate;
    this.readTokens = Math.min(this.readCapacity, this.readTokens + tokensToAdd);
    this.writeTokens = Math.min(this.writeCapacity, this.writeTokens + tokensToAdd);
    this.lastRefill = now;
  }
}

const rateLimiter = new EnhancedTokenBucket();

// Enhanced input validation schemas
const PathSchema = z.string().min(1).max(500).refine(
  (path) => !/[\x00-\x1f\x7f-\x9f]/.test(path),
  { message: "Invalid control characters in path" }
);

const ContentSchema = z.string().max(10 * 1024 * 1024); // 10MB max content
const CommandSchema = z.string().min(1).max(1000);
const MessageSchema = z.string().min(1).max(500);

// Security: Enhanced credential redaction
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

  // OpenAI keys
  result = result.replace(/sk-[A-Za-z0-9]{48}/g, () => { redacted = true; return "[REDACTED-OPENAI-KEY]"; });
  
  // Private keys
  result = result.replace(/-----BEGIN [A-Z ]+PRIVATE KEY-----[\s\S]*?-----END [A-Z ]+PRIVATE KEY-----/g, () => {
    redacted = true;
    return "[REDACTED-PRIVATE-KEY]";
  });
  
  // Strip ANSI escapes
  result = result.replace(/\x1b\[[0-9;]*m/g, "");
  
  // Strip HTML/script tags
  result = result.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, "[REDACTED-SCRIPT]");
  result = result.replace(/<[^>]+>/g, "");
  
  return { text: result, redacted };
}

// Security: Enhanced denylist checking
function isDenylisted(rel: string): boolean {
  const normalizedPath = path.normalize(rel).replace(/\\/g, '/');
  return DENYLIST.some(pattern => {
    if (pattern.includes("*")) {
      const regex = new RegExp(pattern.replace(/\*/g, ".*"));
      return regex.test(normalizedPath);
    }
    return normalizedPath.includes(pattern) || normalizedPath.startsWith(pattern);
  });
}

// Enhanced logging with operation types
function logOperation(tool: string, args: any, duration: number, resultInfo: any, denied = false, redacted = false, isWrite = false) {
  const logEntry = {
    timestamp: new Date().toISOString(),
    tool,
    operation_type: isWrite ? "WRITE" : "READ",
    argsHash: JSON.stringify(args).slice(0, 100),
    duration,
    resultInfo,
    denied,
    redacted,
    working_dir: process.cwd()
  };
  console.error(JSON.stringify(logEntry));
}

// Safe path resolution (enhanced)
function resolveSafe(p: string) {
  const joined = path.resolve(ROOT, p);
  const rootResolved = path.resolve(ROOT);
  if (!joined.startsWith(rootResolved)) {
    throw new Error("Path traversal blocked");
  }
  return joined;
}

// Backup utility for write operations
async function createBackup(filePath: string): Promise<string> {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const relativePath = path.relative(ROOT, filePath);
  const backupPath = path.join(BACKUP_DIR, `${timestamp}-${relativePath.replace(/[/\\]/g, '_')}`);
  
  try {
    if (await fs.pathExists(filePath)) {
      await fs.copy(filePath, backupPath);
      return backupPath;
    }
  } catch (error) {
    // Backup failed, but continue with operation
    console.error(`Backup failed for ${filePath}:`, error);
  }
  return "";
}

// Git utilities
async function gitCommand(args: string[]): Promise<string> {
  return new Promise((resolve, reject) => {
    const child = spawn('git', args, { 
      cwd: ROOT, 
      stdio: ['ignore', 'pipe', 'pipe'] 
    });
    
    let stdout = '';
    let stderr = '';
    
    child.stdout?.on('data', (data) => {
      stdout += data.toString();
    });
    
    child.stderr?.on('data', (data) => {
      stderr += data.toString();
    });
    
    child.on('close', (code) => {
      if (code === 0) {
        resolve(stdout.trim());
      } else {
        reject(new Error(`Git command failed: ${stderr}`));
      }
    });
  });
}

// Enhanced rate limiting wrapper
function withRateLimit<T extends any[], R>(fn: (...args: T) => Promise<R>, isWrite = false) {
  return async (...args: T): Promise<R> => {
    const canProceed = isWrite ? rateLimiter.consumeWrite() : rateLimiter.consumeRead();
    if (!canProceed) {
      throw new Error(`Rate limit exceeded for ${isWrite ? 'write' : 'read'} operations. Please try again in a few seconds.`);
    }
    return fn(...args);
  };
}

// ============================================================================
// TIER 1: CORE FILE OPERATIONS
// ============================================================================

export const writeFile = withRateLimit(async (rel: string, content: string, createBackup = true) => {
  const start = Date.now();
  try {
    const validatedRel = PathSchema.parse(rel);
    const validatedContent = ContentSchema.parse(content);
    
    if (isDenylisted(validatedRel)) {
      logOperation("write_file", { rel, size: content.length }, Date.now() - start, null, true, false, true);
      throw new Error("Access denied: path is denylisted");
    }
    
    const full = resolveSafe(validatedRel);
    let backupPath = "";
    
    if (createBackup) {
      backupPath = await createBackup(full);
    }
    
    // Ensure directory exists
    await fs.ensureDir(path.dirname(full));
    
    // Write file with redaction check
    const { text: cleanContent, redacted: wasRedacted } = redact(validatedContent);
    await fs.writeFile(full, cleanContent, 'utf8');
    
    const stats = await fs.stat(full);
    const result = { 
      rel: validatedRel, 
      full, 
      size: stats.size, 
      mtime: stats.mtimeMs, 
      backup: backupPath,
      redacted: wasRedacted 
    };
    
    logOperation("write_file", { rel, size: content.length }, Date.now() - start, result, false, wasRedacted, true);
    return result;
  } catch (error) {
    logOperation("write_file", { rel, size: content.length }, Date.now() - start, null, false, false, true);
    throw error;
  }
}, true);

export const deleteFile = withRateLimit(async (rel: string, createBackup = true) => {
  const start = Date.now();
  try {
    const validatedRel = PathSchema.parse(rel);
    
    if (isDenylisted(validatedRel)) {
      logOperation("delete_file", { rel }, Date.now() - start, null, true, false, true);
      throw new Error("Access denied: path is denylisted");
    }
    
    const full = resolveSafe(validatedRel);
    
    if (!await fs.pathExists(full)) {
      throw new Error("File does not exist");
    }
    
    let backupPath = "";
    if (createBackup) {
      backupPath = await createBackup(full);
    }
    
    await fs.remove(full);
    
    const result = { rel: validatedRel, full, backup: backupPath };
    logOperation("delete_file", { rel }, Date.now() - start, result, false, false, true);
    return result;
  } catch (error) {
    logOperation("delete_file", { rel }, Date.now() - start, null, false, false, true);
    throw error;
  }
}, true);

export const moveFile = withRateLimit(async (srcRel: string, destRel: string, createBackup = true) => {
  const start = Date.now();
  try {
    const validatedSrc = PathSchema.parse(srcRel);
    const validatedDest = PathSchema.parse(destRel);
    
    if (isDenylisted(validatedSrc) || isDenylisted(validatedDest)) {
      logOperation("move_file", { src: srcRel, dest: destRel }, Date.now() - start, null, true, false, true);
      throw new Error("Access denied: path is denylisted");
    }
    
    const fullSrc = resolveSafe(validatedSrc);
    const fullDest = resolveSafe(validatedDest);
    
    if (!await fs.pathExists(fullSrc)) {
      throw new Error("Source file does not exist");
    }
    
    let backupPath = "";
    if (createBackup && await fs.pathExists(fullDest)) {
      backupPath = await createBackup(fullDest);
    }
    
    // Ensure destination directory exists
    await fs.ensureDir(path.dirname(fullDest));
    
    await fs.move(fullSrc, fullDest);
    
    const result = { 
      src: validatedSrc, 
      dest: validatedDest, 
      fullSrc, 
      fullDest, 
      backup: backupPath 
    };
    
    logOperation("move_file", { src: srcRel, dest: destRel }, Date.now() - start, result, false, false, true);
    return result;
  } catch (error) {
    logOperation("move_file", { src: srcRel, dest: destRel }, Date.now() - start, null, false, false, true);
    throw error;
  }
}, true);

export const createDirectory = withRateLimit(async (rel: string) => {
  const start = Date.now();
  try {
    const validatedRel = PathSchema.parse(rel);
    
    if (isDenylisted(validatedRel)) {
      logOperation("create_directory", { rel }, Date.now() - start, null, true, false, true);
      throw new Error("Access denied: path is denylisted");
    }
    
    const full = resolveSafe(validatedRel);
    await fs.ensureDir(full);
    
    const stats = await fs.stat(full);
    const result = { rel: validatedRel, full, created: stats.birthtimeMs };
    
    logOperation("create_directory", { rel }, Date.now() - start, result, false, false, true);
    return result;
  } catch (error) {
    logOperation("create_directory", { rel }, Date.now() - start, null, false, false, true);
    throw error;
  }
}, true);

export const copyFile = withRateLimit(async (srcRel: string, destRel: string) => {
  const start = Date.now();
  try {
    const validatedSrc = PathSchema.parse(srcRel);
    const validatedDest = PathSchema.parse(destRel);
    
    if (isDenylisted(validatedSrc) || isDenylisted(validatedDest)) {
      logOperation("copy_file", { src: srcRel, dest: destRel }, Date.now() - start, null, true, false, true);
      throw new Error("Access denied: path is denylisted");
    }
    
    const fullSrc = resolveSafe(validatedSrc);
    const fullDest = resolveSafe(validatedDest);
    
    if (!await fs.pathExists(fullSrc)) {
      throw new Error("Source file does not exist");
    }
    
    // Ensure destination directory exists
    await fs.ensureDir(path.dirname(fullDest));
    
    await fs.copy(fullSrc, fullDest);
    
    const stats = await fs.stat(fullDest);
    const result = { 
      src: validatedSrc, 
      dest: validatedDest, 
      fullSrc, 
      fullDest, 
      size: stats.size 
    };
    
    logOperation("copy_file", { src: srcRel, dest: destRel }, Date.now() - start, result, false, false, true);
    return result;
  } catch (error) {
    logOperation("copy_file", { src: srcRel, dest: destRel }, Date.now() - start, null, false, false, true);
    throw error;
  }
}, true);

// Export existing read functions (from original fsTools.ts)
export { buildIndex, getFile, listDir, searchFiles, SearchSchema, statRel } from './fsTools.js';

// ============================================================================
// TIER 1: GIT OPERATIONS
// ============================================================================

export const gitStatus = withRateLimit(async () => {
  const start = Date.now();
  try {
    const status = await gitCommand(['status', '--porcelain']);
    const branch = await gitCommand(['branch', '--show-current']);
    
    const result = { 
      branch: branch.trim(),
      status: status.split('\n').filter(line => line.trim()).map(line => ({
        status: line.substring(0, 2),
        file: line.substring(3)
      })),
      clean: status.trim() === ''
    };
    
    logOperation("git_status", {}, Date.now() - start, result);
    return result;
  } catch (error) {
    logOperation("git_status", {}, Date.now() - start, null);
    throw error;
  }
});

export const gitDiff = withRateLimit(async (file?: string, staged = false) => {
  const start = Date.now();
  try {
    const args = ['diff'];
    if (staged) args.push('--staged');
    if (file) {
      const validatedFile = PathSchema.parse(file);
      if (isDenylisted(validatedFile)) {
        throw new Error("Access denied: path is denylisted");
      }
      args.push(validatedFile);
    }
    
    const diff = await gitCommand(args);
    const result = { file: file || 'all', staged, diff };
    
    logOperation("git_diff", { file, staged }, Date.now() - start, { size: diff.length });
    return result;
  } catch (error) {
    logOperation("git_diff", { file, staged }, Date.now() - start, null);
    throw error;
  }
});

export const gitAdd = withRateLimit(async (files: string | string[]) => {
  const start = Date.now();
  try {
    const fileArray = Array.isArray(files) ? files : [files];
    const validatedFiles = fileArray.map(f => PathSchema.parse(f));
    
    for (const file of validatedFiles) {
      if (isDenylisted(file)) {
        throw new Error(`Access denied: path is denylisted: ${file}`);
      }
    }
    
    const args = ['add', ...validatedFiles];
    await gitCommand(args);
    
    const result = { files: validatedFiles, added: true };
    logOperation("git_add", { files: validatedFiles }, Date.now() - start, result, false, false, true);
    return result;
  } catch (error) {
    logOperation("git_add", { files }, Date.now() - start, null, false, false, true);
    throw error;
  }
}, true);

export const gitCommit = withRateLimit(async (message: string, files?: string[]) => {
  const start = Date.now();
  try {
    const validatedMessage = MessageSchema.parse(message);
    
    let args = ['commit', '-m', validatedMessage];
    
    if (files) {
      const validatedFiles = files.map(f => PathSchema.parse(f));
      for (const file of validatedFiles) {
        if (isDenylisted(file)) {
          throw new Error(`Access denied: path is denylisted: ${file}`);
        }
      }
      args = ['commit', '-m', validatedMessage, ...validatedFiles];
    }
    
    const output = await gitCommand(args);
    const result = { message: validatedMessage, files, output };
    
    logOperation("git_commit", { message: validatedMessage, files }, Date.now() - start, result, false, false, true);
    return result;
  } catch (error) {
    logOperation("git_commit", { message, files }, Date.now() - start, null, false, false, true);
    throw error;
  }
}, true);

export const gitCreateBranch = withRateLimit(async (branchName: string, checkout = true) => {
  const start = Date.now();
  try {
    const validatedBranch = z.string().min(1).max(100).parse(branchName);
    
    const args = checkout ? ['checkout', '-b', validatedBranch] : ['branch', validatedBranch];
    const output = await gitCommand(args);
    
    const result = { branch: validatedBranch, checkout, output };
    logOperation("git_create_branch", { branch: validatedBranch, checkout }, Date.now() - start, result, false, false, true);
    return result;
  } catch (error) {
    logOperation("git_create_branch", { branch: branchName, checkout }, Date.now() - start, null, false, false, true);
    throw error;
  }
}, true);

export const gitCheckout = withRateLimit(async (branchName: string) => {
  const start = Date.now();
  try {
    const validatedBranch = z.string().min(1).max(100).parse(branchName);
    
    const output = await gitCommand(['checkout', validatedBranch]);
    const result = { branch: validatedBranch, output };
    
    logOperation("git_checkout", { branch: validatedBranch }, Date.now() - start, result, false, false, true);
    return result;
  } catch (error) {
    logOperation("git_checkout", { branch: branchName }, Date.now() - start, null, false, false, true);
    throw error;
  }
}, true);

export const gitStash = withRateLimit(async (message?: string) => {
  const start = Date.now();
  try {
    const args = ['stash'];
    if (message) {
      const validatedMessage = MessageSchema.parse(message);
      args.push('push', '-m', validatedMessage);
    }
    
    const output = await gitCommand(args);
    const result = { message, output };
    
    logOperation("git_stash", { message }, Date.now() - start, result, false, false, true);
    return result;
  } catch (error) {
    logOperation("git_stash", { message }, Date.now() - start, null, false, false, true);
    throw error;
  }
}, true);

// ============================================================================
// TIER 2: COMMAND EXECUTION & BUILD TOOLS
// ============================================================================

export const runCommand = withRateLimit(async (command: string, cwd?: string, timeout = 30000) => {
  const start = Date.now();
  try {
    const validatedCommand = CommandSchema.parse(command);
    const workingDir = cwd ? resolveSafe(cwd) : ROOT;
    
    // Security: Block dangerous commands
    const dangerousCommands = ['rm -rf', 'sudo', 'chmod 777', 'mv /', 'del /s', 'format'];
    if (dangerousCommands.some(cmd => validatedCommand.toLowerCase().includes(cmd))) {
      throw new Error("Dangerous command blocked for safety");
    }
    
    const output = await new Promise<string>((resolve, reject) => {
      const timer = setTimeout(() => {
        reject(new Error(`Command timeout after ${timeout}ms`));
      }, timeout);
      
      const child = spawn('sh', ['-c', validatedCommand], {
        cwd: workingDir,
        stdio: ['ignore', 'pipe', 'pipe']
      });
      
      let stdout = '';
      let stderr = '';
      
      child.stdout?.on('data', (data) => {
        stdout += data.toString();
      });
      
      child.stderr?.on('data', (data) => {
        stderr += data.toString();
      });
      
      child.on('close', (code) => {
        clearTimeout(timer);
        if (code === 0) {
          resolve(stdout.trim());
        } else {
          reject(new Error(`Command failed (exit ${code}): ${stderr}`));
        }
      });
    });
    
    const result = { command: validatedCommand, cwd: workingDir, output, exitCode: 0 };
    logOperation("run_command", { command: validatedCommand, cwd }, Date.now() - start, result, false, false, true);
    return result;
  } catch (error) {
    logOperation("run_command", { command, cwd }, Date.now() - start, null, false, false, true);
    throw error;
  }
}, true);

export const installDependencies = withRateLimit(async (packageManager = 'auto') => {
  const start = Date.now();
  try {
    let command = '';
    
    if (packageManager === 'auto') {
      // Auto-detect package manager
      if (await fs.pathExists(path.join(ROOT, 'package.json'))) {
        command = await fs.pathExists(path.join(ROOT, 'package-lock.json')) ? 'npm install' : 
                  await fs.pathExists(path.join(ROOT, 'yarn.lock')) ? 'yarn install' : 
                  await fs.pathExists(path.join(ROOT, 'pnpm-lock.yaml')) ? 'pnpm install' : 'npm install';
      } else if (await fs.pathExists(path.join(ROOT, 'requirements.txt'))) {
        command = 'pip install -r requirements.txt';
      } else if (await fs.pathExists(path.join(ROOT, 'pyproject.toml'))) {
        command = 'pip install -e .';
      } else if (await fs.pathExists(path.join(ROOT, 'Cargo.toml'))) {
        command = 'cargo build';
      } else {
        throw new Error("No recognized package management files found");
      }
    } else {
      command = packageManager;
    }
    
    const result = await runCommand(command, undefined, 120000); // 2 minute timeout
    logOperation("install_dependencies", { packageManager, command }, Date.now() - start, result, false, false, true);
    return result;
  } catch (error) {
    logOperation("install_dependencies", { packageManager }, Date.now() - start, null, false, false, true);
    throw error;
  }
}, true);

export const buildProject = withRateLimit(async (target?: string) => {
  const start = Date.now();
  try {
    let command = '';
    
    if (target) {
      command = target;
    } else {
      // Auto-detect build command
      const packageJson = path.join(ROOT, 'package.json');
      if (await fs.pathExists(packageJson)) {
        const pkg = await fs.readJson(packageJson);
        command = pkg.scripts?.build ? 'npm run build' : 'npm run compile';
      } else if (await fs.pathExists(path.join(ROOT, 'Makefile'))) {
        command = 'make';
      } else if (await fs.pathExists(path.join(ROOT, 'Cargo.toml'))) {
        command = 'cargo build --release';
      } else {
        throw new Error("No recognized build configuration found");
      }
    }
    
    const result = await runCommand(command, undefined, 300000); // 5 minute timeout
    logOperation("build_project", { target, command }, Date.now() - start, result, false, false, true);
    return result;
  } catch (error) {
    logOperation("build_project", { target }, Date.now() - start, null, false, false, true);
    throw error;
  }
}, true);

export const runTests = withRateLimit(async (pattern?: string, watch = false) => {
  const start = Date.now();
  try {
    let command = '';
    
    // Auto-detect test command
    const packageJson = path.join(ROOT, 'package.json');
    if (await fs.pathExists(packageJson)) {
      const pkg = await fs.readJson(packageJson);
      command = pkg.scripts?.test ? 'npm test' : 
                pkg.scripts?.jest ? 'npm run jest' :
                'npm run test';
    } else if (await fs.pathExists(path.join(ROOT, 'pytest.ini')) || 
               await fs.pathExists(path.join(ROOT, 'pyproject.toml'))) {
      command = 'pytest';
    } else if (await fs.pathExists(path.join(ROOT, 'Cargo.toml'))) {
      command = 'cargo test';
    } else {
      throw new Error("No recognized test configuration found");
    }
    
    if (pattern) {
      command += ` ${pattern}`;
    }
    
    if (watch) {
      command += ' --watch';
    }
    
    const result = await runCommand(command, undefined, 300000); // 5 minute timeout
    logOperation("run_tests", { pattern, watch, command }, Date.now() - start, result, false, false, true);
    return result;
  } catch (error) {
    logOperation("run_tests", { pattern, watch }, Date.now() - start, null, false, false, true);
    throw error;
  }
}, true);

// Export new schemas for validation
export { CommandSchema, ContentSchema, MessageSchema, PathSchema };

