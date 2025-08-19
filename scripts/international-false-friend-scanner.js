#!/usr/bin/env node

/**
 * International False-Friend Scanner
 * Detects brand-risky terms in multiple languages (ES/PT/FR)
 * Provides human review workflow for ambiguous matches
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

class InternationalFalseFriendScanner {
  constructor() {
    this.violations = [];
    this.humanReviewRequired = [];
    this.policyManifest = this.loadPolicyManifest();
    
    // Load false friends from policy manifest
    this.falseFriends = this.policyManifest.internationalization?.falseFriends || this.getDefaultFalseFriends();
    
    // Extended false friend dictionary
    this.extendedDictionary = {
      spanish: {
        direct: ['matada', 'matadas', 'matado', 'matados'], // Direct matches (critical)
        contextual: [ // Need human review
          'mata', 'matar', 'matando', 'matará', 'mataría', 
          'matanza', 'matadero', 'matador'
        ],
        phrases: [ // Phrase-level matches
          'mata el tiempo', 'mata las ganas', 'se mata trabajando'
        ]
      },
      portuguese: {
        direct: ['matada', 'matadas', 'matado', 'matados'],
        contextual: ['mata', 'matar', 'matando', 'matará'],
        phrases: ['mata o tempo', 'mata a fome']
      },
      french: {
        direct: [], // No direct false friends identified
        contextual: ['matée', 'mater'], // Context-dependent
        phrases: []
      },
      italian: {
        direct: [],
        contextual: ['matta', 'matto'], // Context-dependent  
        phrases: []
      }
    };

    // Files to scan
    this.scanPatterns = [
      'lukhas_website/locales/**/*.json',
      'lukhas_website/**/*.{tsx,jsx,md}',
      'branding/**/*.md',
      '!**/node_modules/**',
      '!.git/**'
    ];
  }

  loadPolicyManifest() {
    try {
      const manifestPath = path.join(__dirname, '../branding/policy.manifest.json');
      return JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
    } catch (error) {
      console.warn('Warning: Could not load policy manifest, using defaults');
      return { internationalization: { falseFriends: {} } };
    }
  }

  getDefaultFalseFriends() {
    return {
      spanish: ['matada', 'matadas', 'matado', 'matados'],
      portuguese: ['matada', 'matadas'],
      french: [],
      action: 'human-review-required'
    };
  }

  async scan() {
    console.log('🌍 Scanning for international false friends...\n');

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
      
      // Detect language context from file path
      const language = this.detectLanguage(relativePath);

      // Scan for false friends in each language
      Object.entries(this.extendedDictionary).forEach(([lang, dictionary]) => {
        this.scanLanguage(content, relativePath, lang, dictionary, language);
      });

    } catch (error) {
      console.error(`Error scanning ${filePath}:`, error.message);
    }
  }

  detectLanguage(filePath) {
    // Extract language from file path
    const langPatterns = {
      es: /\/(es|spanish)\//i,
      pt: /\/(pt|portuguese)\//i,
      fr: /\/(fr|french)\//i,
      it: /\/(it|italian)\//i
    };

    for (const [lang, pattern] of Object.entries(langPatterns)) {
      if (pattern.test(filePath)) {
        return lang;
      }
    }

    // Check file extension/name
    if (filePath.includes('es.json')) return 'es';
    if (filePath.includes('pt.json')) return 'pt'; 
    if (filePath.includes('fr.json')) return 'fr';
    if (filePath.includes('it.json')) return 'it';

    return 'unknown';
  }

  scanLanguage(content, filePath, lang, dictionary, fileLanguage) {
    // Check direct matches (critical violations)
    dictionary.direct?.forEach(term => {
      const pattern = new RegExp(`\\b${this.escapeRegex(term)}\\b`, 'gi');
      const matches = [...content.matchAll(pattern)];
      
      matches.forEach(match => {
        const lineNumber = this.getLineNumber(content, match.index);
        const context = this.getContext(content, match.index, 50);
        
        this.violations.push({
          file: filePath,
          line: lineNumber,
          language: lang,
          term: match[0],
          context: context,
          severity: 'error',
          type: 'direct-false-friend',
          message: `Direct false friend "${match[0]}" detected in ${lang} context`,
          action: 'immediate-fix-required'
        });
      });
    });

    // Check contextual matches (human review required)
    dictionary.contextual?.forEach(term => {
      const pattern = new RegExp(`\\b${this.escapeRegex(term)}\\b`, 'gi');
      const matches = [...content.matchAll(pattern)];
      
      matches.forEach(match => {
        const lineNumber = this.getLineNumber(content, match.index);
        const context = this.getContext(content, match.index, 100);
        const riskScore = this.assessContextualRisk(context, term, lang);
        
        this.humanReviewRequired.push({
          file: filePath,
          line: lineNumber,
          language: lang,
          term: match[0],
          context: context,
          severity: riskScore > 0.7 ? 'high' : riskScore > 0.4 ? 'medium' : 'low',
          type: 'contextual-false-friend',
          message: `Potential false friend "${match[0]}" requires human review`,
          riskScore: Math.round(riskScore * 100) / 100,
          action: 'human-review-required'
        });
      });
    });

    // Check phrase-level matches
    dictionary.phrases?.forEach(phrase => {
      const pattern = new RegExp(this.escapeRegex(phrase), 'gi');
      const matches = [...content.matchAll(pattern)];
      
      matches.forEach(match => {
        const lineNumber = this.getLineNumber(content, match.index);
        const context = this.getContext(content, match.index, 80);
        
        this.humanReviewRequired.push({
          file: filePath,
          line: lineNumber,
          language: lang,
          term: match[0],
          context: context,
          severity: 'medium',
          type: 'phrase-false-friend',
          message: `Phrase-level false friend "${match[0]}" detected`,
          action: 'human-review-required'
        });
      });
    });
  }

  assessContextualRisk(context, term, language) {
    // Simple risk assessment based on surrounding words
    const riskIndicators = {
      spanish: ['muerte', 'violencia', 'acabar', 'destruir', 'eliminar'],
      portuguese: ['morte', 'violência', 'acabar', 'destruir'],
      french: ['mort', 'violence', 'tuer', 'détruire'],
      italian: ['morte', 'violenza', 'uccidere', 'distruggere']
    };

    const indicators = riskIndicators[language] || [];
    const contextLower = context.toLowerCase();
    
    let riskScore = 0.3; // Base risk
    
    indicators.forEach(indicator => {
      if (contextLower.includes(indicator)) {
        riskScore += 0.2;
      }
    });

    // Brand context increases risk
    if (contextLower.includes('lukhas') || contextLower.includes('matriz')) {
      riskScore += 0.3;
    }

    return Math.min(1.0, riskScore);
  }

  escapeRegex(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  getContext(content, index, radius) {
    const start = Math.max(0, index - radius);
    const end = Math.min(content.length, index + radius);
    return content.substring(start, end).replace(/\s+/g, ' ').trim();
  }

  getLineNumber(content, index) {
    return content.substring(0, index).split('\n').length;
  }

  generateHumanReviewReport() {
    if (this.humanReviewRequired.length === 0) return '';

    let report = '\n📋 Human Review Required:\n\n';
    
    // Group by language
    const byLanguage = this.groupBy(this.humanReviewRequired, 'language');
    
    Object.entries(byLanguage).forEach(([lang, items]) => {
      report += `### ${lang.toUpperCase()} Language:\n\n`;
      
      items.forEach((item, index) => {
        report += `${index + 1}. **${item.file}:${item.line}**\n`;
        report += `   Term: "${item.term}"\n`;
        report += `   Risk: ${item.severity} (${item.riskScore ? item.riskScore * 100 : 'N/A'}%)\n`;
        report += `   Context: "${item.context}"\n`;
        report += `   Action: Manual review needed to determine if term is problematic in context\n\n`;
      });
    });

    return report;
  }

  groupBy(array, key) {
    return array.reduce((groups, item) => {
      const group = item[key] || 'other';
      groups[group] = groups[group] || [];
      groups[group].push(item);
      return groups;
    }, {});
  }

  reportResults() {
    console.log('📊 International False Friend Analysis Results\n');

    // Report critical violations
    if (this.violations.length > 0) {
      console.log(`❌ ${this.violations.length} Critical False Friend Violations:\n`);
      
      this.violations.forEach((violation, index) => {
        console.log(`${index + 1}. ${violation.file}:${violation.line} (${violation.language})`);
        console.log(`   ❌ ${violation.message}`);
        console.log(`   Term: "${violation.term}"`);
        console.log(`   Context: "${violation.context}"`);
        console.log(`   Action: ${violation.action}`);
        console.log('');
      });
    }

    // Report human review items
    if (this.humanReviewRequired.length > 0) {
      console.log(`⚠️  ${this.humanReviewRequired.length} Terms Require Human Review:\n`);
      
      const byLanguage = this.groupBy(this.humanReviewRequired, 'language');
      
      Object.entries(byLanguage).forEach(([lang, items]) => {
        console.log(`📍 ${lang.toUpperCase()}:`);
        
        items.slice(0, 5).forEach(item => { // Show first 5 per language
          console.log(`   ${item.file}:${item.line} - "${item.term}" (${item.severity} risk)`);
        });
        
        if (items.length > 5) {
          console.log(`   ... and ${items.length - 5} more`);
        }
        console.log('');
      });
    }

    // Summary
    if (this.violations.length === 0 && this.humanReviewRequired.length === 0) {
      console.log('✅ No international false friends detected!');
    } else {
      console.log('📋 Summary:');
      console.log(`   Critical violations: ${this.violations.length}`);
      console.log(`   Human review required: ${this.humanReviewRequired.length}`);
      
      if (this.violations.length > 0) {
        console.log('\n🚫 Build blocked due to critical false friend violations.');
      }

      // Generate detailed review report
      const reviewReport = this.generateHumanReviewReport();
      if (reviewReport) {
        console.log(reviewReport);
      }
    }

    console.log('🌍 International Brand Guidelines:');
    console.log('   • Direct false friends block builds automatically');  
    console.log('   • Contextual matches require human editorial review');
    console.log('   • Consider cultural sensitivities in all languages');
    console.log('   • Maintain brand-safe terminology across locales');
  }
}

// Run if called directly
if (require.main === module) {
  const scanner = new InternationalFalseFriendScanner();
  scanner.scan().catch(error => {
    console.error('International false friend scanning failed:', error);
    process.exit(1);
  });
}

module.exports = InternationalFalseFriendScanner;