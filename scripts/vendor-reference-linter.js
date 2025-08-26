#!/usr/bin/env node

/**
 * Vendor Reference Linter
 * Enforces neutral vendor phrasing and provides auto-fix suggestions
 * Prevents implied endorsements and maintains vendor neutrality
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

class VendorReferenceLinter {
  constructor() {
    this.violations = [];
    this.warnings = [];
    this.policyManifest = this.loadPolicyManifest();

    // Load vendor phrasing rules from policy manifest
    this.vendorRules = this.policyManifest.vendorPhrases || this.getDefaultRules();

    // Additional vendor neutrality rules
    this.neutralityRules = [
      {
        pattern: /\b(powered by|built on|based on)\s+(OpenAI|Anthropic|Google|Perplexity)\b/gi,
        replacement: 'uses $2 APIs',
        severity: 'error',
        message: 'Avoid "powered by" language - use neutral integration phrasing'
      },
      {
        pattern: /\b(partner(ed)?|partnering|partnership)\s+with\s+(OpenAI|Anthropic|Google|Perplexity)\b/gi,
        replacement: 'integrates with $3',
        severity: 'error',
        message: 'Avoid partnership language - use neutral integration terms'
      },
      {
        pattern: /\b(endorsed by|approved by|certified by)\s+(OpenAI|Anthropic|Google)\b/gi,
        replacement: 'compatible with $2',
        severity: 'error',
        message: 'Remove endorsement claims - use compatibility language'
      },
      {
        pattern: /\b(the best|leading|top|premier)\s+(OpenAI|Anthropic|Google)\s+(solution|integration|approach)\b/gi,
        replacement: '$2 integration',
        severity: 'warning',
        message: 'Avoid superlative vendor descriptions'
      },
      {
        pattern: /\b(exclusively|only|solely)\s+(uses?|works?\s+with)\s+(OpenAI|Anthropic|Google)\b/gi,
        replacement: 'primarily uses $3',
        severity: 'warning',
        message: 'Avoid exclusive vendor claims'
      }
    ];

    // Files to scan
    this.scanPatterns = [
      'lukhas_website/**/*.{tsx,jsx,ts,js,md}',
      'branding/**/*.md',
      '!**/node_modules/**',
      '!.git/**',
      '!dist/**',
      '!build/**',
      '!**/.next/**'
    ];
  }

  loadPolicyManifest() {
    try {
      const manifestPath = path.join(__dirname, '../branding/policy.manifest.json');
      return JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
    } catch (error) {
      console.warn('Warning: Could not load policy manifest, using defaults');
      return { bannedWords: { vendorPhrasing: [] } };
    }
  }

  getDefaultRules() {
    return [
      {
        pattern: "powered by (OpenAI|Anthropic|Google)",
        replace: "uses $1 APIs"
      },
      {
        pattern: "partner(ed)? with (OpenAI|Anthropic|Google)",
        replace: "integrates with $1 APIs"
      }
    ];
  }

  async scan() {
    console.log('🤝 Scanning for vendor reference violations...\n');

    const files = this.getFilesToScan();

    for (const filePath of files) {
      await this.scanFile(filePath);
    }

    this.reportResults();

    // Exit with error code if critical violations found
    if (this.violations.length > 0) {
      process.exit(1);
    }
  }

  getFilesToScan() {
    const files = [];

    for (const pattern of this.scanPatterns) {
      const matches = glob.sync(pattern, {
        cwd: process.cwd(),
        ignore: ['**/node_modules/**', '**/.git/**']
      });
      files.push(...matches);
    }

    return [...new Set(files)];
  }

  async scanFile(filePath) {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      const relativePath = path.relative(process.cwd(), filePath);

      // Check policy manifest vendor rules
      this.checkPolicyVendorRules(content, relativePath);

      // Check built-in neutrality rules
      this.checkNeutralityRules(content, relativePath);

    } catch (error) {
      console.error(`Error scanning ${filePath}:`, error.message);
    }
  }

  checkPolicyVendorRules(content, filePath) {
    this.vendorRules.forEach(rule => {
      const pattern = new RegExp(rule.pattern, 'gi');
      const matches = [...content.matchAll(pattern)];

      for (const match of matches) {
        const lineNumber = this.getLineNumber(content, match.index);

        // Generate replacement suggestion
        const suggestion = match[0].replace(pattern, rule.replace);

        this.violations.push({
          file: filePath,
          line: lineNumber,
          message: `Vendor phrasing violation: "${match[0]}"`,
          severity: 'error',
          match: match[0],
          suggestion: suggestion,
          type: 'vendor-phrasing',
          rule: rule.pattern
        });
      }
    });
  }

  checkNeutralityRules(content, filePath) {
    this.neutralityRules.forEach(rule => {
      const matches = [...content.matchAll(rule.pattern)];

      for (const match of matches) {
        const lineNumber = this.getLineNumber(content, match.index);

        // Generate replacement suggestion
        const suggestion = match[0].replace(rule.pattern, rule.replacement);

        const violation = {
          file: filePath,
          line: lineNumber,
          message: rule.message,
          severity: rule.severity,
          match: match[0],
          suggestion: suggestion,
          type: 'vendor-neutrality',
          rule: rule.pattern.source
        };

        if (rule.severity === 'error') {
          this.violations.push(violation);
        } else {
          this.warnings.push(violation);
        }
      }
    });
  }

  getLineNumber(content, index) {
    return content.substring(0, index).split('\n').length;
  }

  generateFixItPatch(violation) {
    return `
-    ${violation.match}
+    ${violation.suggestion}`;
  }

  reportResults() {
    console.log('📊 Vendor Reference Linting Results\n');

    // Report violations (errors)
    if (this.violations.length > 0) {
      console.log(`❌ ${this.violations.length} Vendor Reference Violations Found:\n`);

      this.violations.forEach((violation, index) => {
        console.log(`${index + 1}. ${violation.file}:${violation.line}`);
        console.log(`   ❌ ${violation.message}`);
        console.log(`   Found: "${violation.match}"`);
        console.log(`
   💡 Suggested Fix: "${violation.suggestion}"`);
        console.log(`
   📝 Diff:${this.generateFixItPatch(violation)}`);
        console.log('');
      });
    }

    // Report warnings
    if (this.warnings.length > 0) {
      console.log(`⚠️  ${this.warnings.length} Vendor Reference Warnings:\n`);

      this.warnings.forEach((warning, index) => {
        console.log(`${index + 1}. ${warning.file}:${warning.line}`);
        console.log(`   ⚠️  ${warning.message}`);
        console.log(`   Found: "${warning.match}"`);
        console.log(`   Suggested: "${warning.suggestion}"`);
        console.log('');
      });
    }

    // Summary
    if (this.violations.length === 0 && this.warnings.length === 0) {
      console.log('✅ No vendor reference violations found!');
      console.log('   All vendor mentions follow neutrality guidelines.');
    } else {
      console.log('📋 Summary:');
      console.log(`   Critical violations: ${this.violations.length}`);
      console.log(`   Warnings: ${this.warnings.length}`);

      if (this.violations.length > 0) {
        console.log('\n🚫 Build blocked due to vendor reference violations.');
        console.log('   Apply suggested fixes above and re-run.');
      }
    }

    console.log('\n🤝 Vendor Neutrality Guidelines:');
    console.log('   • Use "integrates with" instead of "partnered with"');
    console.log('   • Use "uses [Vendor] APIs" instead of "powered by [Vendor]"');
    console.log('   • Avoid endorsement or certification claims');
    console.log('   • Maintain factual, neutral descriptions of integrations');
  }
}

// Run if called directly
if (require.main === module) {
  const linter = new VendorReferenceLinter();
  linter.scan().catch(error => {
    console.error('Vendor reference linting failed:', error);
    process.exit(1);
  });
}

// Export lintVendors function for use in other scripts
function lintVendors(text, file) {
  const manifest = JSON.parse(fs.readFileSync(path.join(__dirname, '../branding/policy.manifest.json'), 'utf8'));
  for (const r of manifest.vendorPhrases) {
    const re = new RegExp(r.pattern, 'gi');
    if (re.test(text)) {
      throw new Error(`Vendor phrasing in ${file}. Use: "${r.replace}".`);
    }
  }
}

module.exports = VendorReferenceLinter;
module.exports.lintVendors = lintVendors;
