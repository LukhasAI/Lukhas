#!/usr/bin/env node

/**
 * Accessibility Linter for MATRIZ Brand
 * Enforces WCAG 2.1 AA compliance for Λ usage and brand elements
 * Focuses on brand-specific accessibility requirements
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

class A11yLinter {
  constructor() {
    this.violations = [];
    this.warnings = [];
    
    // Critical accessibility patterns
    this.a11yPatterns = [
      {
        pattern: /[λΛ]/g,
        check: this.checkLambdaAccessibility.bind(this),
        message: 'Λ character requires aria-label for screen readers',
        severity: 'error'
      },
      {
        pattern: /<img[^>]*src[^>]*>/gi,
        check: this.checkImageAlt.bind(this),
        message: 'Image missing alt attribute',
        severity: 'error'
      },
      {
        pattern: /<button[^>]*>/gi,
        check: this.checkButtonAccessibility.bind(this),
        message: 'Button missing accessible name',
        severity: 'warning'
      },
      {
        pattern: /<[^>]*aria-label="[^"]*[λΛ][^"]*"/gi,
        check: this.checkAriaLabelLambda.bind(this),
        message: 'aria-label should not contain Λ character',
        severity: 'error'
      }
    ];

    // Files to scan
    this.scanPatterns = [
      'lukhas_website/**/*.{tsx,jsx,html}',
      'branding/**/*.{html,md}',
      '!node_modules/**',
      '!.git/**'
    ];
  }

  async scan() {
    console.log('♿ Scanning for accessibility violations...\n');

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
        ignore: ['node_modules/**', '.git/**']
      });
      files.push(...matches);
    }

    return [...new Set(files)];
  }

  async scanFile(filePath) {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      const relativePath = path.relative(process.cwd(), filePath);

      for (const rule of this.a11yPatterns) {
        const matches = [...content.matchAll(rule.pattern)];
        
        for (const match of matches) {
          const violation = rule.check(content, match, relativePath);
          if (violation) {
            if (rule.severity === 'error') {
              this.violations.push(violation);
            } else {
              this.warnings.push(violation);
            }
          }
        }
      }

      // Additional checks
      this.checkColorContrast(content, relativePath);
      this.checkHeadingStructure(content, relativePath);

    } catch (error) {
      console.error(`Error scanning ${filePath}:`, error.message);
    }
  }

  checkLambdaAccessibility(content, match, filePath) {
    const lambdaIndex = match.index;
    const lineNumber = this.getLineNumber(content, lambdaIndex);
    
    // Look for aria-label in the surrounding context (within 200 chars)
    const contextStart = Math.max(0, lambdaIndex - 200);
    const contextEnd = Math.min(content.length, lambdaIndex + 200);
    const context = content.substring(contextStart, contextEnd);
    
    // Check if Λ is in a context that has aria-label
    const hasAriaLabel = /aria-label\s*=\s*["'][^"']*matriz[^"']*["']/i.test(context);
    
    // Check if it's in alt text or title (which should use plain text)
    const isInAltOrTitle = /(alt|title)\s*=\s*["'][^"']*[λΛ]/i.test(context);
    
    if (isInAltOrTitle) {
      return {
        file: filePath,
        line: lineNumber,
        message: 'Λ character found in alt/title text. Use "Matriz" instead.',
        severity: 'error',
        match: match[0],
        type: 'lambda-alt-text'
      };
    }
    
    if (!hasAriaLabel) {
      return {
        file: filePath,
        line: lineNumber,
        message: 'Λ character requires aria-label="Matriz" for screen readers.',
        severity: 'error',
        match: match[0],
        type: 'lambda-aria-label',
        suggestion: 'Add aria-label="Matriz" to the element containing Λ'
      };
    }
    
    return null;
  }

  checkImageAlt(content, match, filePath) {
    const imgTag = match[0];
    const lineNumber = this.getLineNumber(content, match.index);
    
    // Check if alt attribute is present
    const hasAlt = /alt\s*=/i.test(imgTag);
    
    if (!hasAlt) {
      return {
        file: filePath,
        line: lineNumber,
        message: 'Image missing alt attribute for accessibility.',
        severity: 'error',
        match: imgTag,
        type: 'missing-alt'
      };
    }
    
    // Check if alt text contains Λ
    const altMatch = imgTag.match(/alt\s*=\s*["']([^"']*[λΛ][^"']*)["']/i);
    if (altMatch) {
      return {
        file: filePath,
        line: lineNumber,
        message: 'Alt text contains Λ. Use "Matriz" in alt text for accessibility.',
        severity: 'error',
        match: altMatch[1],
        type: 'lambda-in-alt'
      };
    }
    
    return null;
  }

  checkButtonAccessibility(content, match, filePath) {
    const buttonTag = match[0];
    const lineNumber = this.getLineNumber(content, match.index);
    
    // Find the closing button tag to get full content
    const buttonStart = match.index;
    const buttonEndRegex = /<\/button>/i;
    const buttonEndMatch = buttonEndRegex.exec(content.substring(buttonStart));
    
    if (!buttonEndMatch) return null;
    
    const fullButton = content.substring(buttonStart, buttonStart + buttonEndMatch.index + buttonEndMatch[0].length);
    
    // Check for accessible name (text content, aria-label, or aria-labelledby)
    const hasTextContent = />([^<]*\w[^<]*)</i.test(fullButton);
    const hasAriaLabel = /aria-label\s*=/i.test(fullButton);
    const hasAriaLabelledBy = /aria-labelledby\s*=/i.test(fullButton);
    
    if (!hasTextContent && !hasAriaLabel && !hasAriaLabelledBy) {
      return {
        file: filePath,
        line: lineNumber,
        message: 'Button lacks accessible name. Add text content or aria-label.',
        severity: 'warning',
        match: buttonTag,
        type: 'button-no-name'
      };
    }
    
    return null;
  }

  checkAriaLabelLambda(content, match, filePath) {
    const lineNumber = this.getLineNumber(content, match.index);
    
    return {
      file: filePath,
      line: lineNumber,
      message: 'aria-label contains Λ character. Use "Matriz" in aria-label for screen readers.',
      severity: 'error',
      match: match[0],
      type: 'aria-label-lambda'
    };
  }

  checkColorContrast(content, filePath) {
    // Basic check for potentially problematic color patterns
    const lowContrastPatterns = [
      /color:\s*#[a-f0-9]{6}.*background:\s*#[a-f0-9]{6}/gi,
      /bg-gray-[1-3][^0-9]/g, // Very light backgrounds
      /text-gray-[1-3][^0-9]/g // Very light text
    ];
    
    for (const pattern of lowContrastPatterns) {
      const matches = [...content.matchAll(pattern)];
      
      for (const match of matches) {
        const lineNumber = this.getLineNumber(content, match.index);
        
        this.warnings.push({
          file: filePath,
          line: lineNumber,
          message: 'Potential color contrast issue. Verify WCAG 2.1 AA compliance (4.5:1 ratio).',
          severity: 'warning',
          match: match[0],
          type: 'color-contrast'
        });
      }
    }
  }

  checkHeadingStructure(content, filePath) {
    const headingMatches = [...content.matchAll(/<h([1-6])[^>]*>/gi)];
    
    if (headingMatches.length === 0) return;
    
    let previousLevel = 0;
    
    for (const match of headingMatches) {
      const currentLevel = parseInt(match[1]);
      const lineNumber = this.getLineNumber(content, match.index);
      
      // Check for skipped heading levels
      if (currentLevel > previousLevel + 1) {
        this.warnings.push({
          file: filePath,
          line: lineNumber,
          message: `Heading level skip detected (h${previousLevel} → h${currentLevel}). Use sequential heading levels.`,
          severity: 'warning',
          match: match[0],
          type: 'heading-skip'
        });
      }
      
      previousLevel = currentLevel;
    }
  }

  getLineNumber(content, index) {
    return content.substring(0, index).split('\n').length;
  }

  reportResults() {
    console.log('📊 Accessibility Linting Results\n');

    // Group violations by type
    const violationsByType = this.groupBy(this.violations, 'type');
    const warningsByType = this.groupBy(this.warnings, 'type');

    // Report critical violations
    if (this.violations.length > 0) {
      console.log(`❌ ${this.violations.length} Accessibility Violations Found:\n`);
      
      if (violationsByType['lambda-aria-label']) {
        console.log('🔤 Lambda Accessibility Issues:');
        for (const violation of violationsByType['lambda-aria-label']) {
          console.log(`  ${violation.file}:${violation.line}`);
          console.log(`    ${violation.message}`);
          if (violation.suggestion) {
            console.log(`    💡 ${violation.suggestion}`);
          }
        }
        console.log('');
      }

      if (violationsByType['lambda-in-alt']) {
        console.log('🖼️  Alt Text Issues:');
        for (const violation of violationsByType['lambda-in-alt']) {
          console.log(`  ${violation.file}:${violation.line}`);
          console.log(`    Found: "${violation.match}"`);
          console.log(`    Use "Matriz" instead of Λ in alt text`);
        }
        console.log('');
      }

      if (violationsByType['missing-alt']) {
        console.log('🖼️  Missing Alt Attributes:');
        for (const violation of violationsByType['missing-alt']) {
          console.log(`  ${violation.file}:${violation.line}`);
          console.log(`    ${violation.message}`);
        }
        console.log('');
      }
    }

    // Report warnings
    if (this.warnings.length > 0) {
      console.log(`⚠️  ${this.warnings.length} Accessibility Warnings:\n`);
      
      for (const warning of this.warnings) {
        console.log(`${warning.file}:${warning.line}`);
        console.log(`  ⚠️  ${warning.message}`);
        console.log('');
      }
    }

    // Summary
    if (this.violations.length === 0 && this.warnings.length === 0) {
      console.log('✅ No accessibility violations found!');
    } else {
      console.log('📋 Summary:');
      console.log(`  Critical violations: ${this.violations.length}`);
      console.log(`  Warnings: ${this.warnings.length}`);
      
      if (this.violations.length > 0) {
        console.log('\n🚫 Build blocked due to accessibility violations.');
      }
    }

    console.log('\n♿ Accessibility Guidelines:');
    console.log('  • Λ requires aria-label="Matriz"');
    console.log('  • Use "Matriz" in alt text, never Λ');
    console.log('  • Maintain WCAG 2.1 AA compliance');
    console.log('  • Sequential heading structure (h1→h2→h3)');
  }

  groupBy(array, key) {
    return array.reduce((groups, item) => {
      const group = item[key] || 'other';
      groups[group] = groups[group] || [];
      groups[group].push(item);
      return groups;
    }, {});
  }
}

// Run if called directly
if (require.main === module) {
  const linter = new A11yLinter();
  linter.scan().catch(error => {
    console.error('Accessibility linting failed:', error);
    process.exit(1);
  });
}

module.exports = A11yLinter;