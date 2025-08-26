#!/usr/bin/env node

/**
 * Poetic Guard - Claims Detection
 * Prevents claims, metrics, and guarantees in Poetic sections
 * Enforces metaphor-only policy for poetic content
 */

const fs = require('fs');
const path = require('path');

class PoeticGuard {
  constructor() {
    this.policyManifest = this.loadPolicyManifest();
    this.maxWords = this.policyManifest.tone.poetic.maxWords;
    this.bannedWords = this.policyManifest.bannedWords || [];
    this.violations = [];

    // Claims detection pattern - using banned words from manifest
    const bannedPattern = this.bannedWords.join('|');
    this.CLAIM = new RegExp(`\\b(${bannedPattern}|certified|endorsed)\\b`, 'i');

    // Additional claim patterns
    this.claimyPatterns = [
      this.CLAIM,
      /\b\d+%\s*(accurate|reliable|success|improvement)\b/i, // Metrics
      /\b(proven|validated|tested|verified)\s+(to|by)\b/i,   // Claims
      /\b(always|never|every|all|none)\s+(works|fails|delivers)\b/i // Absolutes
    ];

    // Metaphor creep patterns (things that sound poetic but make claims)
    this.metaphorCreepPatterns = [
      /\b(transforms?|revolutionize[ds]?|breakthrough)\b/i,
      /\b(seamlessly|effortlessly|instantly)\b/i,
      /\b(the future of|next generation|cutting.edge)\b/i
    ];
  }

  loadPolicyManifest() {
    try {
      const manifestPath = path.join(__dirname, '../branding/policy.manifest.json');
      return JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
    } catch (error) {
      console.error('Failed to load policy manifest:', error.message);
      return { tone: { poetic: { maxWords: 40, noClaims: true } }, bannedWords: [] };
    }
  }

  /**
   * Extract poetic sections from content
   */
  extractPoeticSections(content, filePath) {
    const poeticSections = [];

    // Patterns for data-tone="poetic" sections
    const poeticPatterns = [
      /data-tone=["']poetic["'][\s\S]*?<\/(section|div|p)>/gi,
      /<section[^>]*poetic[\s\S]*?<\/section>/gi,
      /\{\/\* POETIC \*\/\}([\s\S]*?)\{\/\* \/POETIC \*\/\}/gi
    ];

    poeticPatterns.forEach(pattern => {
      let match;
      while ((match = pattern.exec(content)) !== null) {
        const sectionContent = this.extractPlainText(match[0]);
        const lineNumber = this.getLineNumber(content, match.index);

        poeticSections.push({
          content: sectionContent,
          raw: match[0],
          line: lineNumber,
          file: filePath
        });
      }
    });

    return poeticSections;
  }

  /**
   * Extract plain text from HTML content
   */
  extractPlainText(html) {
    return html
      .replace(/<[^>]*>/g, ' ')
      .replace(/\s+/g, ' ')
      .replace(/&\w+;/g, ' ')
      .trim();
  }

  /**
   * Get line number for content index
   */
  getLineNumber(content, index) {
    return content.substring(0, index).split('\n').length;
  }

  /**
   * Assert poetic section is safe from claims
   */
  assertPoeticSafe(section) {
    const violations = [];

    // Check word count
    const wordCount = (section.content.match(/\b[\w''-]+\b/g) || []).length;
    if (wordCount > this.maxWords) {
      violations.push({
        type: 'word-count',
        count: wordCount,
        max: this.maxWords,
        message: `Poetic section exceeds ${this.maxWords} words (has ${wordCount} words)`
      });
    }

    // Check for direct claims
    this.claimyPatterns.forEach(pattern => {
      const matches = [...section.content.matchAll(new RegExp(pattern.source, 'gi'))];
      matches.forEach(match => {
        violations.push({
          type: 'direct-claim',
          pattern: pattern.source,
          match: match[0],
          message: `Direct claim detected in poetic content: "${match[0]}"`
        });
      });
    });

    // Check for metaphor creep
    this.metaphorCreepPatterns.forEach(pattern => {
      const matches = [...section.content.matchAll(new RegExp(pattern.source, 'gi'))];
      matches.forEach(match => {
        violations.push({
          type: 'metaphor-creep',
          pattern: pattern.source,
          match: match[0],
          message: `Metaphor creep detected - implies performance claims: "${match[0]}"`
        });
      });
    });

    // Check patterns from policy manifest
    this.bannedPatterns.forEach(patternStr => {
      const pattern = new RegExp(patternStr, 'gi');
      const matches = [...section.content.matchAll(pattern)];
      matches.forEach(match => {
        violations.push({
          type: 'policy-violation',
          pattern: patternStr,
          match: match[0],
          message: `Policy violation in poetic content: "${match[0]}"`
        });
      });
    });

    return violations;
  }

  /**
   * Generate poetic rewrite suggestions
   */
  generatePoeticSuggestions(violations) {
    const suggestions = [];

    violations.forEach(violation => {
      switch (violation.type) {
        case 'direct-claim':
          suggestions.push(`Replace "${violation.match}" with evocative imagery that doesn't make performance claims`);
          break;
        case 'metaphor-creep':
          suggestions.push(`Rephrase "${violation.match}" as pure metaphor without implied outcomes`);
          break;
        case 'policy-violation':
          suggestions.push(`Remove prohibited term "${violation.match}" - use descriptive imagery instead`);
          break;
      }
    });

    return suggestions;
  }

  /**
   * Analyze file for poetic violations
   */
  async analyzeFile(filePath) {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      const relativePath = path.relative(process.cwd(), filePath);

      const poeticSections = this.extractPoeticSections(content, relativePath);

      for (const section of poeticSections) {
        const sectionViolations = this.assertPoeticSafe(section);

        if (sectionViolations.length > 0) {
          const suggestions = this.generatePoeticSuggestions(sectionViolations);

          this.violations.push({
            file: section.file,
            line: section.line,
            content: section.content.substring(0, 200) + (section.content.length > 200 ? '...' : ''),
            violations: sectionViolations,
            suggestions,
            severity: 'error',
            type: 'poetic-claims-violation'
          });
        }
      }
    } catch (error) {
      console.error(`Error analyzing ${filePath}:`, error.message);
    }
  }

  /**
   * Report poetic guard results
   */
  reportResults() {
    console.log('🎭 Poetic Guard Analysis Results\n');

    if (this.violations.length === 0) {
      console.log('✅ All Poetic sections are claim-free!');
      console.log('   Pure metaphorical content maintained');
      return;
    }

    console.log(`❌ ${this.violations.length} Poetic Violations Found:\n`);

    this.violations.forEach((violation, index) => {
      console.log(`${index + 1}. ${violation.file}:${violation.line}`);
      console.log(`   Content: "${violation.content}"`);
      console.log('\n   Violations:');
      violation.violations.forEach(v => {
        console.log(`     • ${v.message}`);
      });
      console.log('\n   💡 Suggestions:');
      violation.suggestions.forEach(suggestion => {
        console.log(`     • ${suggestion}`);
      });
      console.log('');
    });

    console.log('📊 Summary:');
    console.log(`   Violations: ${this.violations.length}`);
    console.log('   Policy: Poetic sections must be claim-free and metaphorical only');
    console.log('\n🚫 Build blocked due to poetic claims violations.');
    console.log('   Remove claims and rephrase as pure imagery.');
  }

  /**
   * Main analysis function
   */
  async analyze(patterns = ['lukhas_website/**/*.{tsx,jsx,md}', 'branding/**/*.md']) {
    const glob = require('glob');
    const files = [];

    for (const pattern of patterns) {
      const matches = glob.sync(pattern, {
        cwd: process.cwd(),
        ignore: ['**/node_modules/**', '**/.git/**']
      });
      files.push(...matches);
    }

    const uniqueFiles = [...new Set(files)];

    for (const filePath of uniqueFiles) {
      await this.analyzeFile(filePath);
    }

    this.reportResults();

    // Exit with error code if violations found
    if (this.violations.length > 0) {
      process.exit(1);
    }
  }
}

// Run if called directly
if (require.main === module) {
  const guard = new PoeticGuard();
  guard.analyze().catch(error => {
    console.error('Poetic guard analysis failed:', error);
    process.exit(1);
  });
}

// Export simplified assertPoeticSafe function
function assertPoeticSafe(html, file) {
  const blocks = html.match(/data-tone=["']poetic["'][\s\S]*?<\/(section|div)>/gi) || [];
  for (const b of blocks) {
    const guard = new PoeticGuard();
    if (guard.CLAIM.test(b)) {
      throw new Error(`Claims in Poetic layer: ${file}`);
    }
  }
}

module.exports = PoeticGuard;
module.exports.assertPoeticSafe = assertPoeticSafe;
