/**
 * Lukhas Cognitive AI System Tools
 * TypeScript interfaces and exports for system tools
 */

import { spawn } from 'child_process';
import { join } from 'path';

// Tool paths
const TOOL_PATHS = {
  cli: {
    commandRegistry: join(__dirname, 'cli/command_registry.py'),
    dreamCli: join(__dirname, 'cli/lucasdream_cli.py'),
    speak: join(__dirname, 'cli/speak.py')
  },
  dao: {
    propose: join(__dirname, 'dao/dao_propose.py'),
    vote: join(__dirname, 'dao/dao_vote.py')
  },
  dev: {
    audit: join(__dirname, 'dev/audit_shortcut.sh')
  },
  research: {
    devDashboard: join(__dirname, 'research/dev_dashboard.py'),
    researchDashboard: join(__dirname, 'research/research_dashboard.py')
  },
  security: {
    sessionLogger: join(__dirname, 'security/session_logger.py')
  }
};

// Tool runner interface
interface ToolRunner {
  run: (args?: string[]) => Promise<{ stdout: string; stderr: string }>;
}

// Create tool runner
const createToolRunner = (path: string): ToolRunner => ({
  run: (args: string[] = []): Promise<{ stdout: string; stderr: string }> => {
    return new Promise((resolve, reject) => {
      let stdout = '';
      let stderr = '';

      const process = spawn('python3', [path, ...args]);

      process.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      process.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      process.on('close', (code) => {
        if (code !== 0) {
          reject(new Error(`Tool exited with code ${code}\n${stderr}`));
        } else {
          resolve({ stdout, stderr });
        }
      });
    });
  }
});

// Export tool runners
export const tools = {
  cli: {
    commandRegistry: createToolRunner(TOOL_PATHS.cli.commandRegistry),
    dreamCli: createToolRunner(TOOL_PATHS.cli.dreamCli),
    speak: createToolRunner(TOOL_PATHS.cli.speak)
  },
  dao: {
    propose: createToolRunner(TOOL_PATHS.dao.propose),
    vote: createToolRunner(TOOL_PATHS.dao.vote)
  },
  dev: {
    audit: createToolRunner(TOOL_PATHS.dev.audit)
  },
  research: {
    devDashboard: createToolRunner(TOOL_PATHS.research.devDashboard),
    researchDashboard: createToolRunner(TOOL_PATHS.research.researchDashboard)
  },
  security: {
    sessionLogger: createToolRunner(TOOL_PATHS.security.sessionLogger)
  }
};

export default tools;
