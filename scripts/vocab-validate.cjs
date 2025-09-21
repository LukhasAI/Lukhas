#!/usr/bin/env node

/**
 * LUKHAS AI Vocabulary Validation Script
 * Validates content against 3-Layer Tone System standards
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

// Load vocabulary files
const VOCAB_DIR = path.join(__dirname, '../branding/vocabularies');
const vocabPlain = JSON.parse(fs.readFileSync(path.join(VOCAB_DIR, 'vocabulary_plain.json'), 'utf8'));
const vocabTechnical = JSON.parse(fs.readFileSync(path.join(VOCAB_DIR, 'vocabulary_technical.json'), 'utf8'));
const poeticSeeds = JSON.parse(fs.readFileSync(path.join(VOCAB_DIR, 'poetic_seeds.json'), 'utf8'));
const blocklist = JSON.parse(fs.readFileSync(path.join(VOCAB_DIR, 'terms_blocklist.json'), 'utf8'));
const allowlist = JSON.parse(fs.readFileSync(path.join(VOCAB_DIR, 'terms_allowlist.json'), 'utf8'));

// Configuration
const MAX_POETIC_WORDS = 40;
const TARGET_READING_LEVEL = { min: 6, max: 8 };

// Colors for console output
const colors = {
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  reset: '\x1b[0m',
  bold: '\x1b[1m'
};

class VocabularyValidator {
  constructor() {
    this.errors = [];
    this.warnings = [];
    this.passed = 0;
  }

  log(message, color = colors.reset) {
    console.log(`${color}${message}${colors.reset}`);
  }

  error(message, file = null, line = null) {
    const location = file && line ? ` (${path.basename(file)}:${line})` : '';
    this.errors.push(`${message}${location}`);
    this.log(`❌ ERROR: ${message}${location}`, colors.red);
  }

  warning(message, file = null, line = null) {
    const location = file && line ? ` (${path.basename(file)}:${line})` : '';
    this.warnings.push(`${message}${location}`);
    this.log(`⚠️  WARNING: ${message}${location}`, colors.yellow);
  }

  pass(message) {
    this.passed++;
    this.log(`✅ ${message}`, colors.green);
  }

  // Validate poetic expressions are ≤40 words
  validatePoeticWordCount() {
    this.log(`\n${colors.bold}Validating poetic expression word counts...${colors.reset}`);

    Object.entries(poeticSeeds).forEach(([module, expressions]) => {
      expressions.forEach((expression, index) => {
        const wordCount = expression.split(/\s+/).length;

        if (wordCount > MAX_POETIC_WORDS) {
          this.error(
            `Poetic expression exceeds ${MAX_POETIC_WORDS} words (${wordCount}): "${expression}"`,
            `poetic_seeds.json`,
            `${module}[${index}]`
          );
        } else {
          this.pass(`${module}[${index}]: ${wordCount} words (✓)`);
        }
      });
    });
  }

  // Check for blocked terms in content
  validateBlockedTerms(content, filename) {
    let violations = [];

    // Check superlatives
    blocklist.superlatives.forEach(item => {
      const regex = new RegExp(`\\b${item.term}\\b`, 'gi');
      if (regex.test(content)) {
        violations.push({
          term: item.term,
          reason: item.reason,
          alternatives: item.alternatives,
          category: 'superlative'
        });
      }
    });

    // Check misleading claims
    blocklist.misleading_claims.forEach(item => {
      const regex = new RegExp(`\\b${item.term}\\b`, 'gi');
      if (regex.test(content)) {
        violations.push({
          term: item.term,
          reason: item.reason,
          alternatives: item.alternatives,
          category: 'misleading'
        });
      }
    });

    // Check technical inaccuracies
    blocklist.inaccurate_technical.forEach(item => {
      const regex = new RegExp(`\\b${item.term}\\b`, 'gi');
      if (regex.test(content)) {
        violations.push({
          term: item.term,
          reason: item.reason,
          alternatives: item.alternatives,
          category: 'technical'
        });
      }
    });

    // Check deprecated terms
    blocklist.deprecated_lukhas_terms.forEach(item => {
      const regex = new RegExp(`\\b${item.term}\\b`, 'gi');
      if (regex.test(content)) {
        violations.push({
          term: item.term,
          reason: item.reason,
          alternatives: item.alternatives,
          category: 'deprecated'
        });
      }
    });

    return violations;
  }

  // Validate Trinity Framework terminology
  validateTrinityTerms(content, filename) {
    const trinityViolations = [];

    // Check for correct Trinity Framework usage
    if (content.includes('Trinity System') || content.includes('Trinity Architecture')) {
      constellationViolations.push('Use "Constellation Framework" not "Trinity System" or "Trinity Architecture"');
    }

    // Check for correct LUKHAS AI branding
    if (content.includes('LUKHAS AGI') || content.includes('Lukhas AI') || content.includes('lukhas ai')) {
      trinityViolations.push('Use "LUKHAS AI" with exact capitalization');
    }

    // Check for correct quantum terminology
    if (content.includes('quantum processing') && !content.includes('quantum-inspired')) {
      trinityViolations.push('Use "quantum-inspired processing" not "quantum processing"');
    }

    // Check for correct bio terminology
    if (content.includes('biological processing') && !content.includes('bio-inspired')) {
      trinityViolations.push('Use "bio-inspired processing" not "biological processing"');
    }

    return trinityViolations;
  }

  // Basic reading level estimation (Flesch-Kincaid approximation)
  estimateReadingLevel(text) {
    const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);
    const words = text.split(/\s+/).filter(w => w.length > 0);
    const syllables = words.reduce((count, word) => {
      // Simple syllable count approximation
      const vowels = (word.toLowerCase().match(/[aeiouy]+/g) || []).length;
      return count + Math.max(1, vowels);
    }, 0);

    if (sentences.length === 0 || words.length === 0) return 0;

    const avgWordsPerSentence = words.length / sentences.length;
    const avgSyllablesPerWord = syllables / words.length;

    // Simplified Flesch-Kincaid formula
    const readingLevel = (0.39 * avgWordsPerSentence) + (11.8 * avgSyllablesPerWord) - 15.59;
    return Math.max(0, readingLevel);
  }

  // Validate files against vocabulary standards
  validateFiles(patterns = ['**/*.md', '**/*.js', '**/*.ts', '**/*.json']) {
    this.log(`\n${colors.bold}Scanning files for vocabulary violations...${colors.reset}`);

    const files = patterns.flatMap(pattern =>
      glob.sync(pattern, {
        ignore: [
          'node_modules/**',
          '.git/**',
          'dist/**',
          'build/**',
          '.next/**',
          'coverage/**',
          '**/*test*/**',
          '**/*spec*/**'
        ],
        cwd: path.join(__dirname, '..')
      })
    );

    files.forEach(file => {
      const fullPath = path.join(__dirname, '..', file);

      // Skip if it's a directory
      if (fs.statSync(fullPath).isDirectory()) {
        return;
      }

      const content = fs.readFileSync(fullPath, 'utf8');

      // Check blocked terms
      const blockedViolations = this.validateBlockedTerms(content, file);
      blockedViolations.forEach(violation => {
        this.error(
          `Blocked term "${violation.term}" (${violation.category}): ${violation.reason}. Use: ${violation.alternatives.join(', ')}`,
          file
        );
      });

      // Check Trinity terminology
      const trinityViolations = this.validateTrinityTerms(content, file);
      trinityViolations.forEach(violation => {
        this.error(violation, file);
      });

      // Check reading level for markdown files
      if (file.endsWith('.md')) {
        const readingLevel = this.estimateReadingLevel(content);
        if (readingLevel > TARGET_READING_LEVEL.max + 2) {
          this.warning(
            `Reading level may be too high (${readingLevel.toFixed(1)}). Target: ${TARGET_READING_LEVEL.min}-${TARGET_READING_LEVEL.max}`,
            file
          );
        }
      }

      if (blockedViolations.length === 0 && trinityViolations.length === 0) {
        this.pass(`${file}: Clean vocabulary ✓`);
      }
    });
  }

  // Validate vocabulary files themselves
  validateVocabularyFiles() {
    this.log(`\n${colors.bold}Validating vocabulary file structure...${colors.reset}`);

    // Check plain vocabulary structure
    vocabPlain.forEach((entry, index) => {
      if (!entry.term || !entry.preferred || !entry.readingLevel) {
        this.error(`Plain vocabulary entry ${index} missing required fields`);
      } else {
        this.pass(`Plain vocabulary[${index}]: Complete structure ✓`);
      }
    });

    // Check technical vocabulary structure
    vocabTechnical.forEach((entry, index) => {
      if (!entry.term || !entry.definition || !entry.citations) {
        this.error(`Technical vocabulary entry ${index} missing required fields`);
      } else {
        this.pass(`Technical vocabulary[${index}]: Complete structure ✓`);
      }
    });

    // Check allowlist evidence
    Object.values(allowlist).flat().forEach((entry, index) => {
      if (!entry.evidence || !entry.usage) {
        this.error(`Allowlist entry ${index} missing evidence or usage`);
      } else {
        this.pass(`Allowlist[${index}]: Evidence provided ✓`);
      }
    });
  }

  // Run all validations
  run() {
    this.log(`${colors.blue}${colors.bold}🧠 LUKHAS AI Vocabulary Validator${colors.reset}\n`);

    this.validatePoeticWordCount();
    this.validateVocabularyFiles();
    this.validateFiles();

    // Summary
    this.log(`\n${colors.bold}=== VALIDATION SUMMARY ===${colors.reset}`);
    this.log(`✅ Passed: ${this.passed}`, colors.green);
    this.log(`⚠️  Warnings: ${this.warnings.length}`, colors.yellow);
    this.log(`❌ Errors: ${this.errors.length}`, colors.red);

    if (this.errors.length > 0) {
      this.log(`\n${colors.bold}Vocabulary validation failed!${colors.reset}`, colors.red);
      process.exit(1);
    } else if (this.warnings.length > 0) {
      this.log(`\n${colors.bold}Vocabulary validation passed with warnings${colors.reset}`, colors.yellow);
      process.exit(0);
    } else {
      this.log(`\n${colors.bold}🎉 All vocabulary validations passed!${colors.reset}`, colors.green);
      process.exit(0);
    }
  }
}

// Run if called directly
if (require.main === module) {
  const validator = new VocabularyValidator();
  validator.run();
}

module.exports = VocabularyValidator;
