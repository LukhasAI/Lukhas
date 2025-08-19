#!/usr/bin/env node

/**
 * SVG Freeze Validator
 * Ensures Lambda (Λ) is rendered as path elements, not text
 * Validates CSP and SRI compliance for SVG assets
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

class SVGFreezeValidator {
  constructor() {
    this.violations = [];
    this.warnings = [];
    this.policyManifest = this.loadPolicyManifest();
  }

  loadPolicyManifest() {
    try {
      const manifestPath = path.join(__dirname, '../branding/policy.manifest.json');
      return JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
    } catch (error) {
      console.warn('Warning: Could not load policy manifest, using defaults');
      return { visual: { svgTextForbidden: true, lambdaMustBePath: true } };
    }
  }

  async validate(patterns = ['**/*.svg', 'branding/assets/*.svg', 'lukhas_website/public/*.svg']) {
    console.log('🎨 Validating SVG freeze compliance...\n');

    const files = this.getFilesToValidate(patterns);
    
    for (const filePath of files) {
      await this.validateFile(filePath);
    }

    this.reportResults();
    
    // Exit with error code if violations found
    if (this.violations.length > 0) {
      process.exit(1);
    }
  }

  getFilesToValidate(patterns) {
    const files = [];
    
    for (const pattern of patterns) {
      const matches = glob.sync(pattern, { 
        cwd: process.cwd(),
        ignore: ['**/node_modules/**', '**/.git/**', '**/dist/**', '**/build/**']
      });
      files.push(...matches);
    }

    return [...new Set(files)];
  }

  async validateFile(filePath) {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      const relativePath = path.relative(process.cwd(), filePath);

      // Check for Lambda in text elements
      this.checkTextElements(content, relativePath);
      
      // Check for Lambda as path
      this.checkLambdaPath(content, relativePath);
      
      // Check for CSP/SRI attributes if embedded
      this.checkSecurityAttributes(content, relativePath);
      
      // Check for proper viewBox and dimensions
      this.checkSVGAttributes(content, relativePath);

    } catch (error) {
      console.error(`Error validating ${filePath}:`, error.message);
    }
  }

  checkTextElements(content, filePath) {
    // Check if Lambda appears in text elements
    const textPattern = /<text[^>]*>([^<]*[λΛ][^<]*)<\/text>/gi;
    const matches = [...content.matchAll(textPattern)];
    
    for (const match of matches) {
      const lineNumber = this.getLineNumber(content, match.index);
      
      this.violations.push({
        file: filePath,
        line: lineNumber,
        message: 'Lambda (Λ) found in <text> element. Must be rendered as <path> for consistency.',
        severity: 'error',
        match: match[0].substring(0, 100),
        type: 'text-lambda'
      });
    }

    // Also check for Lambda in tspan elements
    const tspanPattern = /<tspan[^>]*>([^<]*[λΛ][^<]*)<\/tspan>/gi;
    const tspanMatches = [...content.matchAll(tspanPattern)];
    
    for (const match of tspanMatches) {
      const lineNumber = this.getLineNumber(content, match.index);
      
      this.violations.push({
        file: filePath,
        line: lineNumber,
        message: 'Lambda (Λ) found in <tspan> element. Must be rendered as <path> for consistency.',
        severity: 'error',
        match: match[0].substring(0, 100),
        type: 'tspan-lambda'
      });
    }
  }

  checkLambdaPath(content, filePath) {
    // Check if file name suggests it should contain Lambda
    const isLambdaFile = /matriz|lukhas|lambda|wordmark/i.test(filePath);
    
    if (isLambdaFile) {
      // Look for path elements that might represent Lambda
      const hasPath = /<path\s/i.test(content);
      const hasText = /<text/i.test(content);
      
      if (!hasPath && hasText) {
        this.warnings.push({
          file: filePath,
          line: 1,
          message: 'SVG appears to use text instead of paths. Consider converting to paths for consistency.',
          severity: 'warning',
          type: 'no-path'
        });
      }
      
      // Check if Lambda character appears anywhere in the SVG
      if (/[λΛ]/.test(content) && !/<path/.test(content)) {
        this.violations.push({
          file: filePath,
          line: 1,
          message: 'Lambda character found but no <path> element. Convert Lambda to path for render consistency.',
          severity: 'error',
          type: 'lambda-not-path'
        });
      }
    }
  }

  checkSecurityAttributes(content, filePath) {
    // Check for inline scripts (security risk)
    if (/<script/i.test(content)) {
      this.violations.push({
        file: filePath,
        line: 1,
        message: 'Inline <script> found in SVG. Remove for CSP compliance.',
        severity: 'error',
        type: 'inline-script'
      });
    }

    // Check for external resource references
    const externalPattern = /xlink:href=["'](?!#)([^"']+)["']/gi;
    const matches = [...content.matchAll(externalPattern)];
    
    for (const match of matches) {
      const lineNumber = this.getLineNumber(content, match.index);
      
      this.warnings.push({
        file: filePath,
        line: lineNumber,
        message: `External resource reference: "${match[1]}". Consider embedding or using SRI hash.`,
        severity: 'warning',
        match: match[0],
        type: 'external-resource'
      });
    }

    // Check for on* event handlers
    const eventPattern = /\son[a-z]+\s*=/gi;
    const eventMatches = [...content.matchAll(eventPattern)];
    
    for (const match of eventMatches) {
      const lineNumber = this.getLineNumber(content, match.index);
      
      this.violations.push({
        file: filePath,
        line: lineNumber,
        message: 'Inline event handler found. Remove for CSP compliance.',
        severity: 'error',
        match: match[0],
        type: 'inline-event'
      });
    }
  }

  checkSVGAttributes(content, filePath) {
    // Check for viewBox
    if (!/<svg[^>]*viewBox=/i.test(content)) {
      this.warnings.push({
        file: filePath,
        line: 1,
        message: 'SVG missing viewBox attribute. Add for responsive scaling.',
        severity: 'warning',
        type: 'missing-viewbox'
      });
    }

    // Check for width/height without viewBox
    const hasWidthHeight = /<svg[^>]*(width|height)=/i.test(content);
    const hasViewBox = /<svg[^>]*viewBox=/i.test(content);
    
    if (hasWidthHeight && !hasViewBox) {
      this.warnings.push({
        file: filePath,
        line: 1,
        message: 'SVG has fixed dimensions without viewBox. Consider using viewBox for responsiveness.',
        severity: 'warning',
        type: 'fixed-dimensions'
      });
    }

    // Check for title element (accessibility)
    if (!/<title>/i.test(content)) {
      this.warnings.push({
        file: filePath,
        line: 1,
        message: 'SVG missing <title> element. Add for accessibility.',
        severity: 'warning',
        type: 'missing-title'
      });
    }
  }

  getLineNumber(content, index) {
    return content.substring(0, index).split('\n').length;
  }

  reportResults() {
    console.log('📊 SVG Validation Results\n');

    // Report violations
    if (this.violations.length > 0) {
      console.log(`❌ ${this.violations.length} SVG Violations Found:\n`);
      
      this.violations.forEach((violation, index) => {
        console.log(`${index + 1}. ${violation.file}:${violation.line}`);
        console.log(`   ❌ ${violation.message}`);
        if (violation.match) {
          console.log(`   Found: "${violation.match}"`);
        }
        console.log('');
      });
    }

    // Report warnings
    if (this.warnings.length > 0) {
      console.log(`⚠️  ${this.warnings.length} SVG Warnings:\n`);
      
      this.warnings.forEach((warning, index) => {
        console.log(`${index + 1}. ${warning.file}:${warning.line}`);
        console.log(`   ⚠️  ${warning.message}`);
        if (warning.match) {
          console.log(`   Found: "${warning.match}"`);
        }
        console.log('');
      });
    }

    // Summary
    if (this.violations.length === 0 && this.warnings.length === 0) {
      console.log('✅ All SVG files pass validation!');
      console.log('   Lambda rendered as paths, CSP compliant');
    } else {
      console.log('📋 Summary:');
      console.log(`   Critical violations: ${this.violations.length}`);
      console.log(`   Warnings: ${this.warnings.length}`);
      
      if (this.violations.length > 0) {
        console.log('\n🚫 Build blocked due to SVG violations.');
        console.log('   Convert Lambda to paths and remove security risks.');
      }
    }

    console.log('\n🎨 SVG Best Practices:');
    console.log('   • Convert text to paths for Lambda (Λ) characters');
    console.log('   • Include viewBox for responsive scaling');
    console.log('   • Add <title> elements for accessibility');
    console.log('   • Avoid inline scripts and event handlers');
    console.log('   • Embed resources or use SRI hashes');
  }
}

// Run if called directly
if (require.main === module) {
  const validator = new SVGFreezeValidator();
  validator.validate().catch(error => {
    console.error('SVG validation failed:', error);
    process.exit(1);
  });
}

module.exports = SVGFreezeValidator;