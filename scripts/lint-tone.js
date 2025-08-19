#!/usr/bin/env node

/**
 * Tone Policy Linter
 * Enforces three-layer content system and banned words
 * Checks word count limits and reading level compliance
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

class ToneLinter {
  constructor() {
    this.violations = [];
    this.warnings = [];
    this.policyManifest = this.loadPolicyManifest();
    
    // Load banned words from policy manifest
    this.bannedWords = this.policyManifest.bannedWords?.buildFailures || [
      'guaranteed', 'flawless', 'perfect', 'zero-risk',
      'unlimited', 'unbreakable', 'foolproof', 'bulletproof',
      'revolutionary', 'groundbreaking', 'game-changing',
      'ultimate', 'supreme', 'best-in-class'
    ];

    // Poetic section patterns
    this.poeticPatterns = [
      /data-tone="poetic"[\s\S]*?<\/[^>]+>/gi,
      /<section[^>]*poetic[\s\S]*?<\/section>/gi,
      /\{\/\* POETIC \*\/\}[\s\S]*?\{\/\* \/POETIC \*\/\}/gi
    ];

    // Files to scan
    this.scanPatterns = [
      'lukhas_website/**/*.{tsx,jsx,ts,js,md}',
      'branding/**/*.md',
      '!node_modules/**',
      '!.git/**'
    ];
  }

  loadPolicyManifest() {
    try {
      const manifestPath = path.join(__dirname, '../branding/policy.manifest.json');
      return JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
    } catch (error) {
      console.warn('Warning: Could not load policy manifest, using defaults');
      return { bannedWords: { buildFailures: [] }, toneSystem: { poeticLayer: { wordLimit: 40 } } };
    }
  }

  async scan() {
    console.log('🎭 Scanning for tone policy violations...\n');

    const files = this.getFilesToScan();
    
    for (const filePath of files) {
      await this.scanFile(filePath);
    }

    this.reportResults();
    
    // Exit with error code if violations found
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

      // Check banned words
      this.checkBannedWords(content, relativePath);
      
      // Check poetic sections for word count
      this.checkPoeticWordCount(content, relativePath);
      
      // Check for missing tone layers
      this.checkToneCompleteness(content, relativePath);

      // Check readability for plain sections
      await this.checkReadability(content, relativePath);

    } catch (error) {
      console.error(`Error scanning ${filePath}:`, error.message);
    }
  }

  checkBannedWords(content, filePath) {
    for (const word of this.bannedWords) {
      const regex = new RegExp(`\\b${word}\\b`, 'gi');
      const matches = [...content.matchAll(regex)];
      
      for (const match of matches) {
        const lineNumber = this.getLineNumber(content, match.index);
        
        this.violations.push({
          file: filePath,
          line: lineNumber,
          message: `Banned word "${word}" found. Use precise, factual language instead.`,
          severity: 'error',
          match: match[0],
          type: 'banned-word'
        });
      }
    }
  }

  checkPoeticWordCount(content, filePath) {
    const wordLimit = this.policyManifest.toneSystem?.poeticLayer?.wordLimit || 40;
    
    for (const pattern of this.poeticPatterns) {
      const matches = [...content.matchAll(pattern)];
      
      for (const match of matches) {
        const poeticContent = match[0];
        const plainText = this.extractPlainText(poeticContent);
        const wordCount = this.countWords(plainText);
        
        if (wordCount > wordLimit) {
          const lineNumber = this.getLineNumber(content, match.index);
          
          this.violations.push({
            file: filePath,
            line: lineNumber,
            message: `Poetic section exceeds ${wordLimit} words (${wordCount} words). Trim to meet limit.`,
            severity: 'error',
            match: plainText.substring(0, 100) + '...',
            type: 'word-count',
            actualCount: wordCount,
            maxCount: wordLimit
          });
        }
      }
    }
  }

  checkToneCompleteness(content, filePath) {
    const hasToneSwitch = /ToneSwitch|data-tone=/.test(content);
    const hasPoetic = this.poeticPatterns.some(pattern => pattern.test(content));
    const hasTechnical = /data-tone="technical"|technical=/i.test(content);
    const hasPlain = /data-tone="plain"|plain=/i.test(content);

    // Only check completeness for files that use tone system
    if (hasToneSwitch || hasPoetic) {
      if (!hasTechnical || !hasPlain) {
        this.warnings.push({
          file: filePath,
          line: 1,
          message: 'Incomplete tone system. Ensure Poetic, Technical, and Plain layers are all present.',
          severity: 'warning',
          type: 'incomplete-tone'
        });
      }
    }
  }

  async checkReadability(content, filePath) {
    const maxGradeLevel = this.policyManifest.toneSystem?.plainLayer?.maxGradeLevel || 8.0;
    
    // Extract plain tone sections
    const plainPatterns = [
      /data-tone=["']plain["'][\s\S]*?<\/(section|div|p)>/gi,
      /<section[^>]*plain[\s\S]*?<\/section>/gi,
      /\{\/\* PLAIN \*\/\}([\s\S]*?)\{\/\* \/PLAIN \*\/\}/gi
    ];

    plainPatterns.forEach(pattern => {
      const matches = [...content.matchAll(pattern)];
      
      for (const match of matches) {
        const plainContent = this.extractPlainText(match[0]);
        const gradeLevel = this.fleschKincaidGrade(plainContent);
        
        if (gradeLevel > maxGradeLevel) {
          const lineNumber = this.getLineNumber(content, match.index);
          
          this.violations.push({
            file: filePath,
            line: lineNumber,
            message: `Plain section reading level too high (Grade ${gradeLevel.toFixed(1)}, max: ${maxGradeLevel}). Simplify language.`,
            severity: 'error',
            match: plainContent.substring(0, 100) + '...',
            type: 'readability',
            actualGrade: gradeLevel.toFixed(1),
            maxGrade: maxGradeLevel
          });
        }
      }
    });
  }

  fleschKincaidGrade(text) {
    if (!text || text.trim().length === 0) return 0;

    const sentences = Math.max(1, (text.match(/[.!?]+/g) || []).length);
    const words = Math.max(1, (text.match(/\b[\w''-]+\b/g) || []).length);
    const syllables = Math.max(1, this.countSyllables(text));

    return 0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59;
  }

  countSyllables(text) {
    const cleanText = text.toLowerCase().replace(/[^a-z]/g, '');
    const vowelGroups = cleanText.match(/[aeiouy]{1,2}/g) || [];
    const silentE = cleanText.match(/\b\w*[^aeiou]e\b/g) || [];
    return Math.max(1, vowelGroups.length - silentE.length);
  }

  extractPlainText(html) {
    // Remove HTML tags and extract plain text
    return html
      .replace(/<[^>]*>/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();
  }

  countWords(text) {
    return text
      .split(/\s+/)
      .filter(word => word.length > 0)
      .length;
  }

  getLineNumber(content, index) {
    return content.substring(0, index).split('\n').length;
  }

  reportResults() {
    console.log('📊 Tone Linting Results\n');

    // Group violations by type
    const violationsByType = this.groupBy(this.violations, 'type');
    const warningsByType = this.groupBy(this.warnings, 'type');

    // Report violations
    if (this.violations.length > 0) {
      console.log(`❌ ${this.violations.length} Tone Violations Found:\n`);
      
      if (violationsByType['banned-word']) {
        console.log('🚫 Banned Words:');
        for (const violation of violationsByType['banned-word']) {
          console.log(`  ${violation.file}:${violation.line}`);
          console.log(`    Found: "${violation.match}"`);
        }
        console.log('');
      }

      if (violationsByType['word-count']) {
        console.log('📏 Word Count Violations:');
        for (const violation of violationsByType['word-count']) {
          console.log(`  ${violation.file}:${violation.line}`);
          console.log(`    ${violation.actualCount} words (max: ${violation.maxCount})`);
          console.log(`    Content: "${violation.match}"`);
        }
        console.log('');
      }
    }

    // Report warnings
    if (this.warnings.length > 0) {
      console.log(`⚠️  ${this.warnings.length} Tone Warnings:\n`);
      
      for (const warning of this.warnings) {
        console.log(`${warning.file}:${warning.line}`);
        console.log(`  ⚠️  ${warning.message}`);
        console.log('');
      }
    }

    // Summary
    if (this.violations.length === 0 && this.warnings.length === 0) {
      console.log('✅ No tone policy violations found!');
    } else {
      console.log('📋 Summary:');
      console.log(`  Violations: ${this.violations.length}`);
      console.log(`  Warnings: ${this.warnings.length}`);
      
      if (this.violations.length > 0) {
        console.log('\n🚫 Build blocked due to tone violations.');
        console.log('   Fix violations above and re-run.');
      }
    }

    console.log('\n💡 Tone Guidelines:');
    console.log('  • Poetic: ≤40 words, evocative, no promises');
    console.log('  • Technical: Precise, cite limitations, show uncertainty');
    console.log('  • Plain: Grade 6-8, focus on outcomes');
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
  const linter = new ToneLinter();
  linter.scan().catch(error => {
    console.error('Tone linting failed:', error);
    process.exit(1);
  });
}

module.exports = ToneLinter;