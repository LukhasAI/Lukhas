#!/usr/bin/env node

/**
 * LUKHAS AI Vocabulary Suggestion Script
 * Scans repository for new terms to add to vocabulary system
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

// Load existing vocabulary files
const VOCAB_DIR = path.join(__dirname, '../branding/vocabularies');
const vocabPlain = JSON.parse(fs.readFileSync(path.join(VOCAB_DIR, 'vocabulary_plain.json'), 'utf8'));
const vocabTechnical = JSON.parse(fs.readFileSync(path.join(VOCAB_DIR, 'vocabulary_technical.json'), 'utf8'));
const poeticSeeds = JSON.parse(fs.readFileSync(path.join(VOCAB_DIR, 'poetic_seeds.json'), 'utf8'));
const blocklist = JSON.parse(fs.readFileSync(path.join(VOCAB_DIR, 'terms_blocklist.json'), 'utf8'));

// Colors for console output
const colors = {
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  reset: '\x1b[0m',
  bold: '\x1b[1m'
};

class VocabularySuggester {
  constructor() {
    this.existingTerms = new Set();
    this.suggestions = {
      plain: [],
      technical: [],
      poetic: [],
      blocklist: []
    };
    this.techPatterns = [];
    this.lukhasTerms = [];
    this.poeticPhrases = [];

    this.loadExistingTerms();
    this.setupPatterns();
  }

  log(message, color = colors.reset) {
    console.log(`${color}${message}${colors.reset}`);
  }

  loadExistingTerms() {
    // Load existing vocabulary terms
    vocabPlain.forEach(entry => this.existingTerms.add(entry.term.toLowerCase()));
    vocabTechnical.forEach(entry => this.existingTerms.add(entry.term.toLowerCase()));

    // Load blocked terms
    Object.values(blocklist).flat().forEach(entry => {
      if (entry.term) this.existingTerms.add(entry.term.toLowerCase());
    });

    // Load poetic seeds as context
    Object.values(poeticSeeds).flat().forEach(phrase => {
      this.existingTerms.add(phrase.toLowerCase());
    });
  }

  setupPatterns() {
    // Technical patterns to identify
    this.techPatterns = [
      /\b([a-zA-Z]+[-_]inspired|inspired[-_][a-zA-Z]+)\b/gi,
      /\b(consciousness|awareness|sentience|cognition)[-_]?[a-zA-Z]*\b/gi,
      /\b(quantum|neural|bio|symbolic)[-_]?[a-zA-Z]*\b/gi,
      /\b(trinity|framework|architecture|system|engine|processor)\b/gi,
      /\b(memory|attention|guardian|identity|drift|alignment)\b/gi,
      /\b(VIVOX|ΛiD|GLYPH|LUKHAS)[-_]?[a-zA-Z]*\b/gi,
      /\b([a-zA-Z]*[-_]?(detection|validation|processing|integration))\b/gi,
      /\b([a-zA-Z]*[-_]?(metrics|threshold|optimization|orchestration))\b/gi
    ];

    // LUKHAS-specific terms
    this.lukhasTerms = [
      /\b(LUKHAS|lukhas|Lukhas)\s+[A-Z][a-zA-Z]+\b/g,
      /\b(Trinity|trinity)\s+[A-Z][a-zA-Z]+\b/g,
      /\b(VIVOX|vivox|ΛiD|Lambda|GLYPH|glyph)[A-Z][a-zA-Z]*\b/g,
      /\b(memory|Memory)\s+(fold|crystallization|garden|scroll)[s]?\b/g,
      /\b(consciousness|Consciousness)\s+(flow|stream|state|metric)[s]?\b/g,
      /\b(quantum|Quantum)[-_]?(inspired|entanglement|collapse|superposition)\b/g
    ];

    // Poetic phrase patterns (potential seeds)
    this.poeticPhrases = [
      /\b[a-zA-Z]+\s+(crystalliz|flowing|dancing|weaving|blooming|awakening)[a-zA-Z]*\b/gi,
      /\b(sacred|eternal|infinite|divine|mystical|gentle)\s+[a-zA-Z]+\b/gi,
      /\b[a-zA-Z]+\s+(gardens|streams|threads|waves|paths|realms)\b/gi,
      /\bwhere\s+[a-zA-Z\s]+\s+(meet|dance|flow|converge)[a-zA-Z]*\b/gi,
      /\b(like|as)\s+[a-zA-Z\s]+\s+(in|through|across)\s+[a-zA-Z\s]+\b/gi
    ];
  }

  extractTermsFromContent(content, filename) {
    const suggestions = {
      technical: new Set(),
      lukhas: new Set(),
      poetic: new Set(),
      potential_blocklist: new Set()
    };

    // Extract technical terms
    this.techPatterns.forEach(pattern => {
      const matches = content.match(pattern) || [];
      matches.forEach(match => {
        const term = match.trim().toLowerCase();
        if (!this.existingTerms.has(term) && term.length > 2) {
          suggestions.technical.add(term);
        }
      });
    });

    // Extract LUKHAS-specific terms
    this.lukhasTerms.forEach(pattern => {
      const matches = content.match(pattern) || [];
      matches.forEach(match => {
        const term = match.trim();
        if (!this.existingTerms.has(term.toLowerCase()) && term.length > 2) {
          suggestions.lukhas.add(term);
        }
      });
    });

    // Extract potential poetic phrases
    this.poeticPhrases.forEach(pattern => {
      const matches = content.match(pattern) || [];
      matches.forEach(match => {
        const phrase = match.trim();
        const wordCount = phrase.split(/\s+/).length;
        if (wordCount <= 40 && !this.existingTerms.has(phrase.toLowerCase())) {
          suggestions.poetic.add(phrase);
        }
      });
    });

    // Look for potential problematic terms
    const problematicPatterns = [
      /\b(revolutionary|groundbreaking|ultimate|perfect|flawless|unprecedented)\b/gi,
      /\b(true|real|genuine)\s+(AI|consciousness|intelligence)\b/gi,
      /\b(sentient|conscious)\s+(AI|machine|system)\b/gi,
      /\bAGI\b/g,
      /\b(quantum|biological)\s+(processing|computing)\b/gi
    ];

    problematicPatterns.forEach(pattern => {
      const matches = content.match(pattern) || [];
      matches.forEach(match => {
        suggestions.potential_blocklist.add(match.trim().toLowerCase());
      });
    });

    return suggestions;
  }

  scanRepository() {
    this.log(`\n${colors.bold}Scanning repository for vocabulary suggestions...${colors.reset}`);

    const patterns = [
      '**/*.md',
      '**/*.js',
      '**/*.ts',
      '**/*.jsx',
      '**/*.tsx',
      '**/*.py',
      '**/*.yaml',
      '**/*.yml'
    ];

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
          '**/*spec*/**',
          'branding/vocabularies/**' // Skip existing vocab files
        ],
        cwd: path.join(__dirname, '..')
      })
    );

    const aggregatedSuggestions = {
      technical: new Map(),
      lukhas: new Map(),
      poetic: new Map(),
      potential_blocklist: new Map()
    };

    files.forEach(file => {
      try {
        const fullPath = path.join(__dirname, '..', file);
        const content = fs.readFileSync(fullPath, 'utf8');
        const suggestions = this.extractTermsFromContent(content, file);

        // Aggregate suggestions with frequency counting
        Object.entries(suggestions).forEach(([type, terms]) => {
          terms.forEach(term => {
            if (!aggregatedSuggestions[type].has(term)) {
              aggregatedSuggestions[type].set(term, { count: 0, files: [] });
            }
            const existing = aggregatedSuggestions[type].get(term);
            existing.count++;
            existing.files.push(file);
          });
        });

      } catch (error) {
        this.log(`⚠️ Could not read ${file}: ${error.message}`, colors.yellow);
      }
    });

    return aggregatedSuggestions;
  }

  generateSuggestions() {
    const suggestions = this.scanRepository();

    // Process technical terms
    this.log(`\n${colors.cyan}${colors.bold}📚 Technical Terms Suggestions:${colors.reset}`);
    const sortedTechnical = Array.from(suggestions.technical.entries())
      .filter(([term, data]) => data.count >= 2) // Only suggest terms used multiple times
      .sort((a, b) => b[1].count - a[1].count)
      .slice(0, 20);

    if (sortedTechnical.length === 0) {
      this.log('No new technical terms found');
    } else {
      sortedTechnical.forEach(([term, data]) => {
        this.log(`  • ${term} (used ${data.count}x)`);
        this.suggestions.technical.push({
          term,
          frequency: data.count,
          files: data.files.slice(0, 3), // Show up to 3 example files
          suggested_definition: this.suggestDefinition(term),
          suggested_contexts: this.suggestContexts(term)
        });
      });
    }

    // Process LUKHAS-specific terms
    this.log(`\n${colors.magenta}${colors.bold}⚛️ LUKHAS-Specific Terms:${colors.reset}`);
    const sortedLukhas = Array.from(suggestions.lukhas.entries())
      .sort((a, b) => b[1].count - a[1].count)
      .slice(0, 15);

    if (sortedLukhas.length === 0) {
      this.log('No new LUKHAS terms found');
    } else {
      sortedLukhas.forEach(([term, data]) => {
        this.log(`  • ${term} (used ${data.count}x)`);
        this.suggestions.plain.push({
          term,
          frequency: data.count,
          suggested_preferred: this.suggestPlainAlternative(term),
          files: data.files.slice(0, 2)
        });
      });
    }

    // Process poetic phrases
    this.log(`\n${colors.green}${colors.bold}🌸 Potential Poetic Seeds:${colors.reset}`);
    const sortedPoetic = Array.from(suggestions.poetic.entries())
      .filter(([phrase]) => phrase.split(/\s+/).length >= 4) // At least 4 words
      .sort((a, b) => b[1].count - a[1].count)
      .slice(0, 10);

    if (sortedPoetic.length === 0) {
      this.log('No new poetic phrases found');
    } else {
      sortedPoetic.forEach(([phrase, data]) => {
        const wordCount = phrase.split(/\s+/).length;
        this.log(`  • "${phrase}" (${wordCount} words, used ${data.count}x)`);
        this.suggestions.poetic.push({
          phrase,
          wordCount,
          frequency: data.count,
          suggested_module: this.suggestModule(phrase)
        });
      });
    }

    // Process potential blocklist additions
    this.log(`\n${colors.red}${colors.bold}🚫 Potential Blocklist Additions:${colors.reset}`);
    const sortedBlocklist = Array.from(suggestions.potential_blocklist.entries())
      .sort((a, b) => b[1].count - a[1].count)
      .slice(0, 10);

    if (sortedBlocklist.length === 0) {
      this.log('No problematic terms found');
    } else {
      sortedBlocklist.forEach(([term, data]) => {
        this.log(`  • "${term}" (used ${data.count}x) - Review for compliance`, colors.red);
        this.suggestions.blocklist.push({
          term,
          frequency: data.count,
          reason: 'Found in content - review for brand compliance',
          files: data.files.slice(0, 3)
        });
      });
    }
  }

  suggestDefinition(term) {
    if (term.includes('consciousness')) return 'Awareness-related processing or measurement';
    if (term.includes('quantum')) return 'Quantum-inspired algorithm or processing method';
    if (term.includes('bio')) return 'Bio-inspired system or adaptation mechanism';
    if (term.includes('trinity')) return 'Related to LUKHAS Trinity Framework architecture';
    if (term.includes('memory')) return 'Memory system component or process';
    if (term.includes('guardian')) return 'Ethics and safety validation system';
    return 'Technical term requiring definition';
  }

  suggestContexts(term) {
    const contexts = [];
    if (term.includes('consciousness') || term.includes('awareness')) contexts.push('consciousness processing');
    if (term.includes('quantum')) contexts.push('quantum-inspired algorithms');
    if (term.includes('memory')) contexts.push('memory systems');
    if (term.includes('identity')) contexts.push('identity management');
    if (term.includes('guardian') || term.includes('ethics')) contexts.push('safety systems');
    return contexts.length > 0 ? contexts : ['technical documentation'];
  }

  suggestPlainAlternative(term) {
    if (term.toLowerCase().includes('consciousness')) return term.replace(/consciousness/gi, 'awareness');
    if (term.toLowerCase().includes('neural')) return term.replace(/neural/gi, 'AI');
    if (term.toLowerCase().includes('quantum')) return 'quantum-inspired ' + term.replace(/quantum/gi, '').trim();
    return term.toLowerCase();
  }

  suggestModule(phrase) {
    if (phrase.includes('memory') || phrase.includes('crystal') || phrase.includes('fold')) return 'memory';
    if (phrase.includes('conscious') || phrase.includes('aware') || phrase.includes('neural')) return 'consciousness';
    if (phrase.includes('quantum') || phrase.includes('probability') || phrase.includes('entangle')) return 'quantum';
    if (phrase.includes('guard') || phrase.includes('ethical') || phrase.includes('protect')) return 'guardian';
    if (phrase.includes('identity') || phrase.includes('authentic') || phrase.includes('signature')) return 'identity';
    return 'general';
  }

  exportSuggestions() {
    const timestamp = new Date().toISOString().split('T')[0];
    const outputFile = path.join(__dirname, `../vocab-suggestions-${timestamp}.json`);

    const output = {
      generated: new Date().toISOString(),
      summary: {
        technical: this.suggestions.technical.length,
        plain: this.suggestions.plain.length,
        poetic: this.suggestions.poetic.length,
        blocklist: this.suggestions.blocklist.length
      },
      suggestions: this.suggestions
    };

    fs.writeFileSync(outputFile, JSON.stringify(output, null, 2));
    this.log(`\n💾 Suggestions exported to: ${path.basename(outputFile)}`, colors.blue);
  }

  run() {
    this.log(`${colors.blue}${colors.bold}🔍 LUKHAS AI Vocabulary Suggester${colors.reset}\n`);
    this.log('Scanning repository for new vocabulary terms...');

    this.generateSuggestions();
    this.exportSuggestions();

    // Summary
    this.log(`\n${colors.bold}=== SUGGESTION SUMMARY ===${colors.reset}`);
    this.log(`📚 Technical terms: ${this.suggestions.technical.length}`);
    this.log(`⚛️ LUKHAS terms: ${this.suggestions.plain.length}`);
    this.log(`🌸 Poetic seeds: ${this.suggestions.poetic.length}`);
    this.log(`🚫 Potential blocklist: ${this.suggestions.blocklist.length}`);

    if (this.suggestions.technical.length > 0 || this.suggestions.plain.length > 0) {
      this.log(`\n${colors.green}✨ Review suggestions and update vocabulary files as appropriate.${colors.reset}`);
    } else {
      this.log(`\n${colors.green}✅ No new terms found - vocabulary appears complete.${colors.reset}`);
    }
  }
}

// Run if called directly
if (require.main === module) {
  const suggester = new VocabularySuggester();
  suggester.run();
}

module.exports = VocabularySuggester;
