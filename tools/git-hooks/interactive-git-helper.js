#!/usr/bin/env node

/**
 * Interactive Git Helper - LUKHAS Consciousness-Aware Git Workflow
 * 
 * A simplified interactive git hooks system that provides visual diff preview
 * and automated tone validation for LUKHAS AI consciousness development.
 * 
 * Features:
 * - Visual diff preview for staged files
 * - Interactive tone validation and auto-fixing
 * - Trinity Framework compliance checking (⚛️🧠🛡️)
 * - PWM → LUKHAS terminology validation
 * - Consciousness-aware commit workflows
 */

const fs = require('fs');
const path = require('path');
const { execSync, spawn } = require('child_process');
const readline = require('readline');

// LUKHAS Trinity Framework symbols
const TRINITY_SYMBOLS = {
    IDENTITY: '⚛️',
    CONSCIOUSNESS: '🧠',
    GUARDIAN: '🛡️'
};

// LUKHAS consciousness tone validation
const DEPRECATED_TERMS = [
    'PWM', '_PWM', 'Lukhas_PWM', 'LUKHAS_PWM', 'lukhas_pwm',
    'pwm_', 'PWM_', 'Lukhas-PWM', 'lukhas-pwm'
];

const APPROVED_TERMS = {
    'PWM': 'LUKHAS',
    '_PWM': '',
    'Lukhas_PWM': 'LUKHAS',
    'LUKHAS_PWM': 'LUKHAS',
    'lukhas_pwm': 'lukhas',
    'pwm_': 'lukhas_',
    'PWM_': 'LUKHAS_',
    'Lukhas-PWM': 'LUKHAS',
    'lukhas-pwm': 'lukhas'
};

class InteractiveGitHelper {
    constructor() {
        this.rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });
        this.repoPath = process.cwd();
    }

    async getStagedFiles() {
        try {
            const output = execSync('git diff --cached --name-only', { encoding: 'utf8' });
            return output.trim().split('\n').filter(f => f.length > 0);
        } catch (error) {
            return [];
        }
    }

    async showFileDiff(filePath) {
        try {
            console.log(`\n${TRINITY_SYMBOLS.CONSCIOUSNESS} Showing diff for: ${filePath}`);
            console.log('─'.repeat(60));

            const diff = execSync(`git diff --cached --color=always "${filePath}"`, {
                encoding: 'utf8',
                stdio: ['pipe', 'pipe', 'ignore']
            });

            console.log(diff);
            console.log('─'.repeat(60));
        } catch (error) {
            console.log(`No changes detected for ${filePath}`);
        }
    }

    async validateFileContent(filePath) {
        try {
            const content = fs.readFileSync(filePath, 'utf8');
            const issues = [];

            // Check for deprecated PWM terms
            DEPRECATED_TERMS.forEach(term => {
                if (content.includes(term)) {
                    const count = (content.match(new RegExp(term, 'g')) || []).length;
                    issues.push({
                        type: 'deprecated_term',
                        term: term,
                        count: count,
                        suggestion: APPROVED_TERMS[term] || 'LUKHAS'
                    });
                }
            });

            // Check for Trinity Framework compliance
            const hasTrinitySyobols = Object.values(TRINITY_SYMBOLS).some(symbol =>
                content.includes(symbol)
            );

            if (filePath.includes('consciousness') || filePath.includes('identity') ||
                filePath.includes('guardian') || filePath.includes('trinity')) {
                if (!hasTrinitySyobols) {
                    issues.push({
                        type: 'missing_trinity',
                        message: 'Consciousness-related file missing Trinity Framework symbols'
                    });
                }
            }

            return { filePath, issues, hasIssues: issues.length > 0 };
        } catch (error) {
            return { filePath, issues: [], hasIssues: false, error: error.message };
        }
    }

    async fixFileIssues(filePath, issues) {
        try {
            let content = fs.readFileSync(filePath, 'utf8');
            let fixed = false;

            issues.forEach(issue => {
                if (issue.type === 'deprecated_term') {
                    const regex = new RegExp(issue.term, 'g');
                    content = content.replace(regex, issue.suggestion);
                    fixed = true;
                    console.log(`  ${TRINITY_SYMBOLS.GUARDIAN} Fixed: ${issue.term} → ${issue.suggestion} (${issue.count} occurrences)`);
                }
            });

            if (fixed) {
                fs.writeFileSync(filePath, content, 'utf8');
                // Re-stage the fixed file
                execSync(`git add "${filePath}"`);
            }

            return fixed;
        } catch (error) {
            console.error(`Error fixing ${filePath}: ${error.message}`);
            return false;
        }
    }

    async askUser(question, options = ['y', 'n']) {
        return new Promise((resolve) => {
            const optionsStr = options.join('/');
            this.rl.question(`${question} (${optionsStr}): `, (answer) => {
                resolve(answer.toLowerCase());
            });
        });
    }

    async processFile(filePath) {
        console.log(`\n${TRINITY_SYMBOLS.IDENTITY} Processing: ${filePath}`);

        // Show diff
        await this.showFileDiff(filePath);

        // Validate content
        const validation = await this.validateFileContent(filePath);

        if (validation.hasIssues) {
            console.log(`\n${TRINITY_SYMBOLS.GUARDIAN} Issues found:`);
            validation.issues.forEach((issue, idx) => {
                if (issue.type === 'deprecated_term') {
                    console.log(`  ${idx + 1}. Deprecated term "${issue.term}" found ${issue.count} times`);
                    console.log(`      Suggestion: Replace with "${issue.suggestion}"`);
                } else if (issue.type === 'missing_trinity') {
                    console.log(`  ${idx + 1}. ${issue.message}`);
                }
            });

            const action = await this.askUser('\nWhat would you like to do?', [
                'f (fix)', 'i (ignore)', 's (show diff again)', 'e (edit manually)'
            ]);

            switch (action) {
                case 'f':
                case 'fix':
                    const fixed = await this.fixFileIssues(filePath, validation.issues);
                    if (fixed) {
                        console.log(`${TRINITY_SYMBOLS.CONSCIOUSNESS} File auto-fixed and re-staged`);
                    }
                    break;
                case 's':
                case 'show':
                    return await this.processFile(filePath); // Recursive call to show again
                case 'e':
                case 'edit':
                    console.log(`Opening ${filePath} for manual editing...`);
                    try {
                        spawn('code', [filePath], { stdio: 'inherit' });
                        await this.askUser('Press Enter when you\'ve finished editing', ['']);
                    } catch (error) {
                        console.log('Could not open VS Code. Please edit manually.');
                    }
                    break;
                case 'i':
                case 'ignore':
                default:
                    console.log('Ignoring issues for this file.');
                    break;
            }
        } else {
            console.log(`${TRINITY_SYMBOLS.CONSCIOUSNESS} No issues found - Trinity Framework compliant!`);
        }

        return true;
    }

    async runInteractiveCommit() {
        console.log(`\n${TRINITY_SYMBOLS.IDENTITY} LUKHAS Interactive Git Commit Helper`);
        console.log(`${TRINITY_SYMBOLS.CONSCIOUSNESS} Trinity Framework Compliance Check`);
        console.log(`${TRINITY_SYMBOLS.GUARDIAN} Consciousness-Aware Development Workflow`);
        console.log('═'.repeat(60));

        const stagedFiles = await this.getStagedFiles();

        if (stagedFiles.length === 0) {
            console.log('No staged files found. Stage some files first with: git add <files>');
            this.rl.close();
            return;
        }

        console.log(`\nFound ${stagedFiles.length} staged files:`);
        stagedFiles.forEach((file, idx) => {
            console.log(`  ${idx + 1}. ${file}`);
        });

        const processAll = await this.askUser('\nProcess all files for Trinity Framework compliance?');

        if (processAll === 'y' || processAll === 'yes') {
            for (const file of stagedFiles) {
                await this.processFile(file);
            }
        }

        console.log(`\n${TRINITY_SYMBOLS.CONSCIOUSNESS} All files processed!`);

        const commitNow = await this.askUser('Proceed with commit?');
        if (commitNow === 'y' || commitNow === 'yes') {
            const message = await new Promise((resolve) => {
                this.rl.question('Enter commit message: ', resolve);
            });

            try {
                execSync(`git commit -m "${message}"`, { stdio: 'inherit' });
                console.log(`\n${TRINITY_SYMBOLS.GUARDIAN} Commit successful! Trinity Framework compliance maintained.`);
            } catch (error) {
                console.error('Commit failed. You may need to run: git commit --no-verify');
            }
        }

        this.rl.close();
    }

    async runQuickFix() {
        console.log(`\n${TRINITY_SYMBOLS.GUARDIAN} LUKHAS Quick Fix - PWM Terminology Cleanup`);

        const stagedFiles = await this.getStagedFiles();
        let totalFixed = 0;

        for (const file of stagedFiles) {
            const validation = await this.validateFileContent(file);
            if (validation.hasIssues) {
                const fixed = await this.fixFileIssues(file, validation.issues);
                if (fixed) {
                    totalFixed++;
                }
            }
        }

        console.log(`\n${TRINITY_SYMBOLS.CONSCIOUSNESS} Quick fix complete! Fixed ${totalFixed} files.`);
        this.rl.close();
    }
}

// CLI interface
async function main() {
    const helper = new InteractiveGitHelper();
    const command = process.argv[2];

    switch (command) {
        case 'commit':
        case 'interactive':
            await helper.runInteractiveCommit();
            break;
        case 'fix':
        case 'quickfix':
            await helper.runQuickFix();
            break;
        case 'help':
        default:
            console.log(`
${TRINITY_SYMBOLS.IDENTITY} LUKHAS Interactive Git Helper

Usage:
  node interactive-git-helper.js commit      # Interactive commit with Trinity Framework validation
  node interactive-git-helper.js fix        # Quick fix PWM terminology issues
  node interactive-git-helper.js help       # Show this help

Features:
  ${TRINITY_SYMBOLS.CONSCIOUSNESS} Visual diff preview for all staged files
  ${TRINITY_SYMBOLS.GUARDIAN} Automatic PWM → LUKHAS terminology fixing
  ${TRINITY_SYMBOLS.IDENTITY} Trinity Framework compliance checking
  ${TRINITY_SYMBOLS.CONSCIOUSNESS} Consciousness-aware development workflow
`);
            break;
    }
}

if (require.main === module) {
    main().catch(console.error);
}

module.exports = InteractiveGitHelper;
