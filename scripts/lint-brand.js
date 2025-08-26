#!/usr/bin/env node

/**
 * Brand Policy Linter
 * Detects violations of MATRIZ brand guidelines
 * Blocks builds on critical violations
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

class BrandLinter {
  constructor() {
    this.violations = [];
    this.warnings = [];
    this.policyManifest = this.loadPolicyManifest();

    // Critical violations that block builds
    this.criticalPatterns = [
      {
        pattern: /\bMATADA\b/g,
        message: 'Public MATADA usage detected. Use "Matriz" in user-facing content.',
        severity: 'error',
        excludeFiles: ['schema', 'internal', '.md', 'next.config.js', 'config']
      },
      {
        pattern: /\/m[λΛ]triz/gi,
        message: 'Λ character in URL/path. Use "/matriz" instead.',
        severity: 'error',
        excludeFiles: ['next.config.js', 'config']
      },
      {
        pattern: /alt="[^"]*[λΛ]/gi,
        message: 'Λ character in alt text. Use plain "Matriz".',
        severity: 'error'
      },
      {
        pattern: /<meta[^>]*content="[^"]*[λΛ]/gi,
        message: 'Λ character in meta content. Use plain "Matriz".',
        severity: 'error'
      }
    ];

    // Warning patterns
    this.warningPatterns = [
      {
        pattern: /[λΛ]/g,
        message: 'Λ usage detected. Ensure aria-label is present for accessibility.',
        severity: 'warning',
        context: 'Check for aria-label="Matriz" when Λ is used in display text.'
      },
      {
        pattern: /\bAGI\b/g,
        message: 'AGI reference found. Consider if this should be "AI".',
        severity: 'warning'
      }
    ];

    // Files to scan
    this.scanPatterns = [
      'lukhas_website/**/*.{tsx,jsx,ts,js,html,md}',
      'branding/**/*.md'
    ];

    // Directories to ignore
    this.ignorePatterns = [
      '**/node_modules/**',
      '**/.git/**',
      '**/dist/**',
      '**/build/**',
      '**/.next/**',
      '**/coverage/**',
      '**/.cache/**'
    ];
  }

  loadPolicyManifest() {
    try {
      const manifestPath = path.join(__dirname, '../branding/policy.manifest.json');
      return JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
    } catch (error) {
      console.warn('Warning: Could not load policy manifest, using defaults');
      return { i18n: { falseFriendsES: ['matada'] }, brand: {} };
    }
  }

  async scan() {
    console.log('🔍 Scanning for brand policy violations...\n');

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
        ignore: this.ignorePatterns
      });
      files.push(...matches);
    }

    return [...new Set(files)]; // Remove duplicates
  }

  async scanFile(filePath) {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      const relativePath = path.relative(process.cwd(), filePath);

      // Check critical violations
      for (const rule of this.criticalPatterns) {
        if (this.shouldSkipFile(filePath, rule.excludeFiles)) {
          continue;
        }

        const matches = [...content.matchAll(rule.pattern)];

        for (const match of matches) {
          const lineNumber = this.getLineNumber(content, match.index);

          this.violations.push({
            file: relativePath,
            line: lineNumber,
            message: rule.message,
            severity: rule.severity,
            match: match[0]
          });
        }
      }

      // Check Lambda usage outside display contexts
      this.checkLambdaUsage(content, relativePath);

      // Check for international false friends
      this.checkFalseFriends(content, relativePath);

      // Check warnings
      for (const rule of this.warningPatterns) {
        const matches = [...content.matchAll(rule.pattern)];

        for (const match of matches) {
          const lineNumber = this.getLineNumber(content, match.index);

          this.warnings.push({
            file: relativePath,
            line: lineNumber,
            message: rule.message,
            severity: rule.severity,
            match: match[0],
            context: rule.context
          });
        }
      }

    } catch (error) {
      console.error(`Error scanning ${filePath}:`, error.message);
    }
  }

  shouldSkipFile(filePath, excludePatterns = []) {
    if (!excludePatterns) return false;

    return excludePatterns.some(pattern =>
      filePath.toLowerCase().includes(pattern.toLowerCase())
    );
  }

  getLineNumber(content, index) {
    return content.substring(0, index).split('\n').length;
  }

  checkLambdaUsage(content, filePath) {
    // Check if Lambda appears outside of display contexts
    const lambdaPattern = /[λΛ]/g;
    const matches = [...content.matchAll(lambdaPattern)];

    for (const match of matches) {
      const lineNumber = this.getLineNumber(content, match.index);
      const lineStart = content.lastIndexOf('\n', match.index) + 1;
      const lineEnd = content.indexOf('\n', match.index);
      const line = content.substring(lineStart, lineEnd === -1 ? undefined : lineEnd);

      // Check if it's in a display context
      const isDisplay = /aria-label=["'].*Matriz/i.test(line);
      const isHeader = /<h[1-6]/i.test(line);
      const isLogo = /logo|wordmark|brand/i.test(line);

      if (!isDisplay && !isHeader && !isLogo) {
        // Check if it's in body text or SEO-sensitive areas
        const isInBody = /<p|<span|<div|<li/i.test(line);
        const isInMeta = /<meta|<title|alt=|title=/i.test(line);
        const isInUrl = /href=|path=|url=/i.test(line);

        if (isInBody || isInMeta || isInUrl) {
          this.violations.push({
            file: filePath,
            line: lineNumber,
            message: `Λ used outside display context. ${this.policyManifest.brand?.requireAriaForLambda ? 'Add aria-label="Matriz" or' : ''} use plain "Matriz" instead.`,
            severity: 'error',
            match: line.trim().substring(0, 100)
          });
        }
      }
    }
  }

  checkFalseFriends(content, filePath) {
    // Check for international false friends
    const falseFriends = {
      ES: this.policyManifest.i18n?.falseFriendsES || ['matada'],
      PT: this.policyManifest.i18n?.falseFriendsPT || ['matada'],
      FR: this.policyManifest.i18n?.falseFriendsFR || ['matrice'],
      IT: this.policyManifest.i18n?.falseFriendsIT || ['matrice']
    };

    for (const [locale, words] of Object.entries(falseFriends)) {
      for (const word of words) {
        const pattern = new RegExp(`\\b${word}\\b`, 'gi');
        const matches = [...content.matchAll(pattern)];

        for (const match of matches) {
          const lineNumber = this.getLineNumber(content, match.index);

          // Check if it's in a locale-specific context
          const isLocaleFile = filePath.includes(`.${locale.toLowerCase()}.`) ||
                               filePath.includes(`/${locale.toLowerCase()}/`);

          if (isLocaleFile) {
            this.violations.push({
              file: filePath,
              line: lineNumber,
              message: `False friend "${word}" detected in ${locale} locale. This word has different meaning in ${locale}.`,
              severity: 'error',
              match: match[0]
            });
          } else {
            this.warnings.push({
              file: filePath,
              line: lineNumber,
              message: `Potential false friend "${word}" (problematic in ${locale}). Consider alternative wording.`,
              severity: 'warning',
              match: match[0]
            });
          }
        }
      }
    }
  }

  reportResults() {
    console.log('📊 Brand Linting Results\n');

    // Report violations (errors)
    if (this.violations.length > 0) {
      console.log(`❌ ${this.violations.length} Critical Violations Found:\n`);

      for (const violation of this.violations) {
        console.log(`${violation.file}:${violation.line}`);
        console.log(`  ❌ ${violation.message}`);
        console.log(`  Found: "${violation.match}"`);
        console.log('');
      }
    }

    // Report warnings
    if (this.warnings.length > 0) {
      console.log(`⚠️  ${this.warnings.length} Warnings:\n`);

      for (const warning of this.warnings) {
        console.log(`${warning.file}:${warning.line}`);
        console.log(`  ⚠️  ${warning.message}`);
        console.log(`  Found: "${warning.match}"`);
        if (warning.context) {
          console.log(`  Context: ${warning.context}`);
        }
        console.log('');
      }
    }

    // Summary
    if (this.violations.length === 0 && this.warnings.length === 0) {
      console.log('✅ No brand policy violations found!');
    } else {
      console.log('📋 Summary:');
      console.log(`  Critical violations: ${this.violations.length}`);
      console.log(`  Warnings: ${this.warnings.length}`);

      if (this.violations.length > 0) {
        console.log('\n🚫 Build blocked due to critical violations.');
        console.log('   Fix violations above and re-run.');
      }
    }
  }
}

// Run if called directly
if (require.main === module) {
  const linter = new BrandLinter();
  linter.scan().catch(error => {
    console.error('Brand linting failed:', error);
    process.exit(1);
  });
}

module.exports = BrandLinter;
