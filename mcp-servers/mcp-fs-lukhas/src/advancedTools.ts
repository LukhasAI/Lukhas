import fg from "fast-glob";
import * as fs from "fs-extra";
import { execSync } from "node:child_process";
import path from "node:path";

const ROOT = process.env.MCP_FS_ROOT || "/Users/agi_dev/LOCAL-REPOS/Lukhas";

// ============================================================================
// TIER 3: ADVANCED ANALYSIS & INTELLIGENCE TOOLS
// ============================================================================

export async function findSymbolUsage(symbol: string, scope?: string): Promise<any> {
  const searchPattern = scope ? `${scope}/**/*.{ts,tsx,js,jsx,py}` : "**/*.{ts,tsx,js,jsx,py}";
  const files = await fg(searchPattern, { 
    cwd: ROOT, 
    ignore: ["**/node_modules/**", "**/.git/**", "**/dist/**", "**/build/**"]
  });
  
  const usages: any[] = [];
  
  for (const file of files.slice(0, 100)) { // Limit for performance
    try {
      const content = await fs.readFile(path.join(ROOT, file), 'utf8');
      const lines = content.split('\n');
      
      lines.forEach((line, index) => {
        if (line.includes(symbol)) {
          // Basic symbol detection (could be enhanced with AST parsing)
          const contexts = [
            `function ${symbol}`,
            `class ${symbol}`,
            `const ${symbol}`,
            `let ${symbol}`,
            `var ${symbol}`,
            `${symbol}(`,
            `${symbol}.`,
            `new ${symbol}`,
            `import.*${symbol}`,
            `export.*${symbol}`
          ];
          
          if (contexts.some(pattern => new RegExp(pattern).test(line))) {
            usages.push({
              file,
              line: index + 1,
              content: line.trim(),
              type: line.includes('function') || line.includes('class') ? 'definition' : 'usage'
            });
          }
        }
      });
    } catch (error) {
      // Skip files that can't be read
      continue;
    }
  }
  
  return {
    symbol,
    scope: scope || 'global',
    usages,
    count: usages.length
  };
}

export async function extractImports(file: string): Promise<any> {
  const fullPath = path.resolve(ROOT, file);
  const content = await fs.readFile(fullPath, 'utf8');
  const lines = content.split('\n');
  
  const imports: any[] = [];
  const exports: any[] = [];
  
  lines.forEach((line, index) => {
    // TypeScript/JavaScript imports
    const importMatch = line.match(/^import\s+(.+?)\s+from\s+['"](.+?)['"];?/);
    if (importMatch) {
      imports.push({
        line: index + 1,
        what: importMatch[1].trim(),
        from: importMatch[2],
        raw: line.trim()
      });
    }
    
    // Python imports
    const pythonImportMatch = line.match(/^(?:from\s+(.+?)\s+)?import\s+(.+)/);
    if (pythonImportMatch) {
      imports.push({
        line: index + 1,
        what: pythonImportMatch[2].trim(),
        from: pythonImportMatch[1] || 'builtin',
        raw: line.trim()
      });
    }
    
    // Exports
    const exportMatch = line.match(/^export\s+(.+)/);
    if (exportMatch) {
      exports.push({
        line: index + 1,
        what: exportMatch[1].trim(),
        raw: line.trim()
      });
    }
  });
  
  return {
    file,
    imports,
    exports,
    dependencies: [...new Set(imports.map(imp => imp.from))]
  };
}

export async function runLinter(files?: string[], fix = false): Promise<any> {
  const results: any[] = [];
  
  try {
    // Try ESLint for JS/TS files
    const eslintPattern = files ? files.join(' ') : '.';
    const eslintArgs = fix ? ['--fix'] : [];
    const eslintCmd = `npx eslint ${eslintPattern} ${eslintArgs.join(' ')} --format json`;
    
    try {
      const eslintOutput = execSync(eslintCmd, { cwd: ROOT, encoding: 'utf8' });
      const eslintResults = JSON.parse(eslintOutput);
      results.push({ linter: 'eslint', results: eslintResults });
    } catch (eslintError) {
      // ESLint might not be configured or have errors
      results.push({ linter: 'eslint', error: 'ESLint not configured or errors found' });
    }
    
    // Try Ruff for Python files
    try {
      const ruffCmd = fix ? 'ruff check --fix .' : 'ruff check . --format json';
      const ruffOutput = execSync(ruffCmd, { cwd: ROOT, encoding: 'utf8' });
      results.push({ linter: 'ruff', results: ruffOutput });
    } catch (ruffError) {
      // Ruff might not be installed
      results.push({ linter: 'ruff', error: 'Ruff not available' });
    }
    
  } catch (error: any) {
    results.push({ error: `Linting failed: ${error?.message || 'Unknown error'}` });
  }
  
  return { files: files || ['all'], fix, results };
}

export async function formatCode(files?: string[]): Promise<any> {
  const results: any[] = [];
  
  try {
    // Try Prettier for JS/TS files
    const prettierPattern = files ? files.join(' ') : '.';
    const prettierCmd = `npx prettier --write ${prettierPattern}`;
    
    try {
      const prettierOutput = execSync(prettierCmd, { cwd: ROOT, encoding: 'utf8' });
      results.push({ formatter: 'prettier', output: prettierOutput });
    } catch (prettierError) {
      results.push({ formatter: 'prettier', error: 'Prettier not configured' });
    }
    
    // Try Black for Python files
    try {
      const blackCmd = files ? `black ${files.join(' ')}` : 'black .';
      const blackOutput = execSync(blackCmd, { cwd: ROOT, encoding: 'utf8' });
      results.push({ formatter: 'black', output: blackOutput });
    } catch (blackError) {
      results.push({ formatter: 'black', error: 'Black not available' });
    }
    
  } catch (error: any) {
    results.push({ error: `Formatting failed: ${error?.message || 'Unknown error'}` });
  }
  
  return { files: files || ['all'], results };
}

export async function findTodosFixmes(): Promise<any> {
  const files = await fg("**/*.{ts,tsx,js,jsx,py,md,txt}", { 
    cwd: ROOT, 
    ignore: ["**/node_modules/**", "**/.git/**", "**/dist/**", "**/build/**"]
  });
  
  const todos: any[] = [];
  const patterns = [
    /TODO[:\s]+(.+)/gi,
    /FIXME[:\s]+(.+)/gi,
    /HACK[:\s]+(.+)/gi,
    /BUG[:\s]+(.+)/gi,
    /XXX[:\s]+(.+)/gi
  ];
  
  for (const file of files.slice(0, 200)) { // Limit for performance
    try {
      const content = await fs.readFile(path.join(ROOT, file), 'utf8');
      const lines = content.split('\n');
      
      lines.forEach((line, index) => {
        patterns.forEach(pattern => {
          const matches = line.match(pattern);
          if (matches) {
            todos.push({
              file,
              line: index + 1,
              type: matches[0].split(/[:\s]/)[0].toUpperCase(),
              content: matches[1] || matches[0],
              raw: line.trim()
            });
          }
        });
      });
    } catch (error) {
      continue;
    }
  }
  
  return {
    count: todos.length,
    todos: todos.slice(0, 100), // Limit results
    summary: todos.reduce((acc, todo) => {
      acc[todo.type] = (acc[todo.type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>)
  };
}

export async function analyzeCodeComplexity(file: string): Promise<any> {
  const fullPath = path.resolve(ROOT, file);
  const content = await fs.readFile(fullPath, 'utf8');
  const lines = content.split('\n');
  
  let complexity = 1; // Base complexity
  let functions = 0;
  let classes = 0;
  let loops = 0;
  let conditions = 0;
  let nestingLevel = 0;
  let maxNesting = 0;
  
  lines.forEach(line => {
    const trimmed = line.trim();
    
    // Count functions and classes
    if (trimmed.match(/^(function|def|class)/)) {
      if (trimmed.includes('function') || trimmed.includes('def')) functions++;
      if (trimmed.includes('class')) classes++;
    }
    
    // Count control structures
    if (trimmed.match(/^(if|else if|elif|switch|case)/)) {
      conditions++;
      complexity++;
    }
    
    if (trimmed.match(/^(for|while|do)/)) {
      loops++;
      complexity++;
    }
    
    // Track nesting (simplified)
    if (trimmed.includes('{') || trimmed.endsWith(':')) {
      nestingLevel++;
      maxNesting = Math.max(maxNesting, nestingLevel);
    }
    
    if (trimmed.includes('}')) {
      nestingLevel = Math.max(0, nestingLevel - 1);
    }
  });
  
  return {
    file,
    metrics: {
      lines: lines.length,
      cyclomaticComplexity: complexity,
      functions,
      classes,
      loops,
      conditions,
      maxNestingLevel: maxNesting
    },
    risk: complexity > 20 ? 'high' : complexity > 10 ? 'medium' : 'low'
  };
}

export async function findUnusedCode(): Promise<any> {
  // This is a simplified implementation - a full solution would need AST parsing
  const files = await fg("**/*.{ts,tsx,js,jsx,py}", { 
    cwd: ROOT, 
    ignore: ["**/node_modules/**", "**/.git/**", "**/dist/**", "**/build/**"]
  });
  
  const symbols = new Map<string, { file: string; line: number; type: string }>();
  const usages = new Set<string>();
  
  // Find all symbol definitions
  for (const file of files.slice(0, 50)) { // Limit for performance
    try {
      const content = await fs.readFile(path.join(ROOT, file), 'utf8');
      const lines = content.split('\n');
      
      lines.forEach((line, index) => {
        // Find function/class definitions
        const defMatch = line.match(/(?:function|class|const|let|var)\s+(\w+)/);
        if (defMatch) {
          symbols.set(defMatch[1], { file, line: index + 1, type: 'definition' });
        }
        
        // Find all symbol usages
        const words = line.match(/\b\w+\b/g) || [];
        words.forEach(word => usages.add(word));
      });
    } catch (error) {
      continue;
    }
  }
  
  // Find potentially unused symbols
  const unused = Array.from(symbols.entries())
    .filter(([symbol]) => !usages.has(symbol))
    .map(([symbol, info]) => ({ symbol, ...info }));
  
  return {
    totalSymbols: symbols.size,
    potentiallyUnused: unused.slice(0, 50), // Limit results
    note: "This is a simplified analysis. Use proper AST tools for accuracy."
  };
}

// ============================================================================
// TIER 4: LUKHAS-SPECIFIC CONSCIOUSNESS TOOLS
// ============================================================================

export async function validateTrinityCompliance(files?: string[]): Promise<any> {
  const targetFiles = files || await fg("**/*.{ts,tsx,js,jsx,py,md}", { 
    cwd: ROOT, 
    ignore: ["**/node_modules/**", "**/.git/**", "**/dist/**", "**/build/**"]
  });
  
  const trinityPatterns = {
    identity: ['⚛️', 'identity', 'consciousness', 'ΛID', 'authentic'],
    consciousness: ['🧠', 'memory', 'awareness', 'cognition', 'dream'],
    guardian: ['🛡️', 'ethics', 'safety', 'guardian', 'protection']
  };
  
  const compliance: any[] = [];
  
  for (const file of targetFiles.slice(0, 100)) {
    try {
      const content = await fs.readFile(path.join(ROOT, file), 'utf8');
      const fileCompliance = {
        file,
        trinity: { identity: 0, consciousness: 0, guardian: 0 },
        patterns: [] as Array<{ aspect: string; pattern: string; count: number }>
      };
      
      Object.entries(trinityPatterns).forEach(([aspect, patterns]) => {
        patterns.forEach(pattern => {
          const matches = (content.match(new RegExp(pattern, 'gi')) || []).length;
          fileCompliance.trinity[aspect as keyof typeof fileCompliance.trinity] += matches;
          if (matches > 0) {
            fileCompliance.patterns.push({ aspect, pattern, count: matches });
          }
        });
      });
      
      compliance.push(fileCompliance);
    } catch (error) {
      continue;
    }
  }
  
  const summary = compliance.reduce((acc, file) => {
    acc.identity += file.trinity.identity;
    acc.consciousness += file.trinity.consciousness;
    acc.guardian += file.trinity.guardian;
    return acc;
  }, { identity: 0, consciousness: 0, guardian: 0 });
  
  return {
    files: compliance.filter(f => 
      f.trinity.identity > 0 || f.trinity.consciousness > 0 || f.trinity.guardian > 0
    ),
    summary,
    score: (summary.identity + summary.consciousness + summary.guardian) / compliance.length,
    recommendation: summary.guardian < (summary.identity + summary.consciousness) / 2 ? 
      "Consider adding more Guardian (🛡️) elements for balance" : "Trinity balance looks good"
  };
}

export async function auditSymbolicVocabulary(): Promise<any> {
  const files = await fg("**/*.{ts,tsx,js,jsx,py,md}", { 
    cwd: ROOT, 
    ignore: ["**/node_modules/**", "**/.git/**", "**/dist/**", "**/build/**"]
  });
  
  const symbols = new Map<string, number>();
  const contexts: any[] = [];
  
  // LUKHAS symbolic vocabulary
  const vocabularyPatterns = [
    '⚛️', '🧠', '🛡️', '🎭', '🌈', '🎓', // Trinity + Core
    'ΛID', 'ΛGENT', 'ΛUKHAS', 'Λ-trace', // Lambda symbols
    'EQNOX', 'VIVOX', 'Trinity Framework', // Core systems
    'consciousness', 'symbolic', 'quantum', 'bio-inspired' // Key concepts
  ];
  
  for (const file of files.slice(0, 100)) {
    try {
      const content = await fs.readFile(path.join(ROOT, file), 'utf8');
      
      vocabularyPatterns.forEach(symbol => {
        const matches = content.match(new RegExp(symbol, 'gi')) || [];
        symbols.set(symbol, (symbols.get(symbol) || 0) + matches.length);
        
        if (matches.length > 0) {
          contexts.push({ file, symbol, count: matches.length });
        }
      });
    } catch (error) {
      continue;
    }
  }
  
  return {
    vocabulary: Array.from(symbols.entries())
      .sort(([,a], [,b]) => b - a)
      .map(([symbol, count]) => ({ symbol, count })),
    contexts: contexts.sort((a, b) => b.count - a.count),
    totalUsage: Array.from(symbols.values()).reduce((a, b) => a + b, 0),
    consistency: symbols.size / vocabularyPatterns.length // How many symbols are actually used
  };
}

export async function createFeatureBranch(taskDescription: string): Promise<any> {
  // Auto-generate branch name from task description
  const branchName = taskDescription
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, '')
    .replace(/\s+/g, '-')
    .substring(0, 50);
  
  const timestamp = new Date().toISOString().split('T')[0];
  const fullBranchName = `feature/${timestamp}-${branchName}`;
  
  try {
    // Check git status first
    const status = execSync('git status --porcelain', { cwd: ROOT, encoding: 'utf8' });
    if (status.trim()) {
      // Stash changes if any
      execSync('git stash push -m "Auto-stash before feature branch"', { cwd: ROOT });
    }
    
    // Create and checkout new branch
    execSync(`git checkout -b ${fullBranchName}`, { cwd: ROOT });
    
    return {
      branchName: fullBranchName,
      taskDescription,
      created: new Date().toISOString(),
      stashed: status.trim() !== ''
    };
  } catch (error: any) {
    throw new Error(`Failed to create feature branch: ${error?.message || 'Unknown error'}`);
  }
}

export async function backupWorkspace(): Promise<any> {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const backupPath = path.join(ROOT, '..', `lukhas-backup-${timestamp}`);
  
  try {
    // Create backup excluding large directories
    await fs.copy(ROOT, backupPath, {
      filter: (src) => {
        const relativePath = path.relative(ROOT, src);
        return !relativePath.includes('node_modules') && 
               !relativePath.includes('.git') && 
               !relativePath.includes('dist') &&
               !relativePath.includes('build');
      }
    });
    
    return {
      backupPath,
      timestamp,
      size: await getFolderSize(backupPath)
    };
  } catch (error: any) {
    throw new Error(`Backup failed: ${error?.message || 'Unknown error'}`);
  }
}

async function getFolderSize(folderPath: string): Promise<number> {
  const files = await fg("**/*", { cwd: folderPath, onlyFiles: true });
  let totalSize = 0;
  
  for (const file of files) {
    try {
      const stats = await fs.stat(path.join(folderPath, file));
      totalSize += stats.size;
    } catch (error) {
      // Skip files that can't be read
    }
  }
  
  return totalSize;
}
