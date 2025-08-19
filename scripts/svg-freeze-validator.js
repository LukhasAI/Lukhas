#!/usr/bin/env node

/**
 * SVG Freeze Validator
 * Ensures Λ character is rendered as path elements, not text
 * Prevents font fallback mismatches and rendering inconsistencies
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
      return { 
        securityPolicies: { 
          svgValidation: { 
            pathElements: true, 
            textElementsForbidden: true,
            inlineScriptForbidden: true 
          } 
        } 
      };
    }
  }

  async validate() {
    console.log('🔒 Validating SVG freeze compliance...\n');

    // Find all SVG files
    const svgFiles = glob.sync('branding/assets/**/*.svg', { 
      cwd: process.cwd() 
    });

    for (const svgFile of svgFiles) {
      await this.validateSVGFile(svgFile);
    }

    this.reportResults();
    
    // Exit with error code if violations found
    if (this.violations.length > 0) {
      process.exit(1);
    }
  }

  async validateSVGFile(filePath) {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      const relativePath = path.relative(process.cwd(), filePath);

      // Check for Λ character in text elements (forbidden)
      this.checkLambdaInTextElements(content, relativePath);
      
      // Check for inline JavaScript (security)
      this.checkInlineScripts(content, relativePath);
      
      // Check for proper path elements (required)
      this.checkPathElements(content, relativePath);
      
      // Check for font dependencies
      this.checkFontDependencies(content, relativePath);

    } catch (error) {
      console.error(`Error validating ${filePath}:`, error.message);
    }
  }

  checkLambdaInTextElements(content, filePath) {
    // Check for Λ character in text elements
    const textElementsWithLambda = content.match(/<text[^>]*>[^<]*[λΛ][^<]*<\/text>/gi);
    
    if (textElementsWithLambda) {
      textElementsWithLambda.forEach(match => {
        const lineNumber = this.getLineNumber(content, content.indexOf(match));
        
        this.violations.push({
          file: filePath,
          line: lineNumber,
          message: 'Λ character found in text element. Must use path elements for render-proofing.',
          severity: 'error',
          match: match.trim(),
          type: 'lambda-in-text',
          fix: 'Convert text element to path element using font-to-path conversion'
        });
      });
    }
  }

  checkInlineScripts(content, filePath) {
    // Check for any inline JavaScript
    const inlineScripts = [
      /<script[^>]*>[\s\S]*?<\/script>/gi,
      /on\w+\s*=\s*["'][^"']*["']/gi, // Event handlers
      /javascript:/gi
    ];

    inlineScripts.forEach(pattern => {
      const matches = [...content.matchAll(pattern)];
      
      matches.forEach(match => {
        const lineNumber = this.getLineNumber(content, match.index);
        
        this.violations.push({
          file: filePath,
          line: lineNumber,
          message: 'Inline JavaScript detected in SVG. Violates Content-Security-Policy.',
          severity: 'error',
          match: match[0].substring(0, 50) + '...',
          type: 'inline-script',
          fix: 'Remove inline JavaScript and use CSS-only styling'
        });
      });
    });
  }

  checkPathElements(content, filePath) {
    // Check for proper path elements
    const hasPathElements = /<path[\s\S]*?\/?>/.test(content);
    const hasLambdaReference = /[λΛ]/.test(filePath) || /matriz/i.test(filePath);
    
    if (hasLambdaReference && !hasPathElements) {
      this.warnings.push({
        file: filePath,
        line: 1,
        message: 'MATRIZ wordmark should use path elements for consistent rendering.',
        severity: 'warning',
        type: 'missing-paths',
        fix: 'Convert text to path elements using vector graphics software'
      });
    }
  }

  checkFontDependencies(content, filePath) {
    // Check for external font dependencies that could cause fallback issues
    const fontFaces = [...content.matchAll(/@font-face[\s\S]*?\}/gi)];
    const fontImports = [...content.matchAll(/@import.*fonts\.googleapis\.com/gi)];
    
    if (fontFaces.length > 0 || fontImports.length > 0) {
      this.warnings.push({
        file: filePath,
        line: 1,
        message: 'External font dependency detected. May cause rendering inconsistencies.',
        severity: 'warning',
        type: 'font-dependency',
        fix: 'Convert to path elements to eliminate font dependencies'
      });
    }
  }

  getLineNumber(content, index) {
    return content.substring(0, index).split('\n').length;
  }

  runSVGO(filePath) {
    // In production, this would run SVGO optimization
    console.log(`   🔧 Running SVGO optimization on ${filePath}`);
    
    // Example SVGO command (would be executed via child_process)
    // svgo --config=svgo.config.js input.svg output.svg
    
    return `Optimized: ${filePath}`;
  }

  reportResults() {
    console.log('📊 SVG Freeze Validation Results\n');

    // Report violations (errors)
    if (this.violations.length > 0) {
      console.log(`❌ ${this.violations.length} SVG Violations Found:\n`);
      
      this.violations.forEach((violation, index) => {
        console.log(`${index + 1}. ${violation.file}:${violation.line}`);
        console.log(`   ❌ ${violation.message}`);
        
        if (violation.match) {
          console.log(`   Found: "${violation.match}"`);
        }
        
        if (violation.fix) {
          console.log(`   💡 Fix: ${violation.fix}`);
        }
        
        console.log('');
      });
    }

    // Report warnings
    if (this.warnings.length > 0) {
      console.log(`⚠️  ${this.warnings.length} SVG Optimization Warnings:\n`);
      
      this.warnings.forEach((warning, index) => {
        console.log(`${index + 1}. ${warning.file}:${warning.line}`);
        console.log(`   ⚠️  ${warning.message}`);
        
        if (warning.fix) {
          console.log(`   💡 Fix: ${warning.fix}`);
        }
        
        console.log('');
      });
    }

    // Summary
    if (this.violations.length === 0 && this.warnings.length === 0) {
      console.log('✅ All SVGs are freeze-compliant!');
      console.log('   Λ characters properly rendered as path elements');
      console.log('   No inline scripts or security violations');
    } else {
      console.log('📋 Summary:');
      console.log(`   Critical violations: ${this.violations.length}`);
      console.log(`   Warnings: ${this.warnings.length}`);
      
      if (this.violations.length > 0) {
        console.log('\n🚫 Build blocked due to SVG violations.');
        console.log('   Fix violations above and re-run.');
      }
    }

    console.log('\n🔒 SVG Security & Render-Proofing Guidelines:');
    console.log('   • Λ character must be path elements, never text');
    console.log('   • No inline JavaScript or event handlers');
    console.log('   • Minimize font dependencies for consistency');
    console.log('   • Use Content-Security-Policy compliant styling');
  }
}

// Run if called directly
if (require.main === module) {
  const validator = new SVGFreezeValidator();
  validator.validate().catch(error => {
    console.error('SVG freeze validation failed:', error);
    process.exit(1);
  });
}

module.exports = SVGFreezeValidator;