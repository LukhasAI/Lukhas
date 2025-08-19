#!/usr/bin/env node

/**
 * Readability Scorer - Flesch-Kincaid Implementation
 * Enforces Grade 6-8 reading level for Plain sections
 * Provides LLM-powered rewrite suggestions for violations
 */

const fs = require('fs');
const path = require('path');

class ReadabilityScorer {
  constructor() {
    this.policyManifest = this.loadPolicyManifest();
    this.maxGradeLevel = this.policyManifest.tone.plain.maxGradeLevel;
    this.violations = [];
  }

  loadPolicyManifest() {
    try {
      const manifestPath = path.join(__dirname, '../branding/policy.manifest.json');
      return JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
    } catch (error) {
      console.error('Failed to load policy manifest:', error.message);
      process.exit(1);
    }
  }

  /**
   * Calculate Flesch-Kincaid Grade Level
   * Formula: 0.39 * (total words / total sentences) + 11.8 * (total syllables / total words) - 15.59
   */
  fleschKincaidGrade(text) {
    if (!text || text.trim().length === 0) return 0;

    // Count sentences (periods, exclamation marks, question marks)
    const sentences = Math.max(1, (text.match(/[.!?]+/g) || []).length);
    
    // Count words (word boundaries)
    const words = Math.max(1, (text.match(/\b[\w''-]+\b/g) || []).length);
    
    // Count syllables (vowel groups)
    const syllables = Math.max(1, this.countSyllables(text));

    const gradeLevel = 0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59;
    
    return Math.max(0, gradeLevel);
  }

  /**
   * Simplified FK Grade function for export
   */
  fkGrade(text) {
    const s = Math.max(1, (text.match(/[.!?]+/g) || []).length);
    const w = Math.max(1, (text.match(/\b[\w''-]+\b/g) || []).length);
    const y = (text.toLowerCase().match(/[aeiouy]{1,2}/g) || []).length;
    return 0.39 * (w / s) + 11.8 * (y / w) - 15.59;
  }

  /**
   * Count syllables in text
   * Simplified algorithm for English text
   */
  countSyllables(text) {
    const cleanText = text.toLowerCase().replace(/[^a-z]/g, '');
    
    // Count vowel groups
    const vowelGroups = cleanText.match(/[aeiouy]{1,2}/g) || [];
    
    // Subtract silent 'e' at word endings
    const silentE = cleanText.match(/\b\w*[^aeiou]e\b/g) || [];
    
    return Math.max(1, vowelGroups.length - silentE.length);
  }

  /**
   * Extract plain tone sections from content
   */
  extractPlainSections(content, filePath) {
    const plainSections = [];
    
    // Pattern for data-tone="plain" sections
    const plainPatterns = [
      /data-tone=["']plain["'][\s\S]*?<\/(section|div|p)>/gi,
      /<section[^>]*plain[\s\S]*?<\/section>/gi,
      /\{\/\* PLAIN \*\/\}([\s\S]*?)\{\/\* \/PLAIN \*\/\}/gi
    ];

    plainPatterns.forEach(pattern => {
      let match;
      while ((match = pattern.exec(content)) !== null) {
        const sectionContent = this.extractPlainText(match[0]);
        const lineNumber = this.getLineNumber(content, match.index);
        
        plainSections.push({
          content: sectionContent,
          raw: match[0],
          line: lineNumber,
          file: filePath
        });
      }
    });

    return plainSections;
  }

  /**
   * Extract plain text from HTML content
   */
  extractPlainText(html) {
    return html
      .replace(/<[^>]*>/g, ' ')          // Remove HTML tags
      .replace(/\s+/g, ' ')             // Normalize whitespace
      .replace(/&\w+;/g, ' ')           // Remove HTML entities
      .trim();
  }

  /**
   * Get line number for content index
   */
  getLineNumber(content, index) {
    return content.substring(0, index).split('\n').length;
  }

  /**
   * Generate LLM-powered rewrite suggestion
   */
  generateRewriteSuggestion(text, currentGrade, targetGrade = 8.0) {
    // This would call an LLM API in production
    // For now, return actionable suggestions
    const suggestions = [];

    if (currentGrade > 12) {
      suggestions.push("Consider breaking long sentences into shorter ones (aim for 15-20 words per sentence)");
    }
    
    if (currentGrade > 10) {
      suggestions.push("Replace complex words with simpler alternatives");
      suggestions.push("Use active voice instead of passive voice");
    }
    
    if (currentGrade > 8) {
      suggestions.push("Remove unnecessary jargon and technical terms");
      suggestions.push("Use concrete examples instead of abstract concepts");
    }

    return {
      currentGrade: Math.round(currentGrade * 10) / 10,
      targetGrade,
      suggestions,
      // In production, this would be an LLM-generated rewrite
      rewriteExample: "Consider simplifying: Focus on clear, direct language that explains outcomes for users."
    };
  }

  /**
   * Analyze file for readability violations
   */
  async analyzeFile(filePath) {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      const relativePath = path.relative(process.cwd(), filePath);
      
      const plainSections = this.extractPlainSections(content, relativePath);
      
      for (const section of plainSections) {
        const gradeLevel = this.fleschKincaidGrade(section.content);
        
        if (gradeLevel > this.maxGradeLevel) {
          const suggestion = this.generateRewriteSuggestion(gradeLevel, this.maxGradeLevel);
          
          this.violations.push({
            file: section.file,
            line: section.line,
            gradeLevel: Math.round(gradeLevel * 10) / 10,
            maxGrade: this.maxGradeLevel,
            content: section.content.substring(0, 200) + '...',
            suggestion,
            severity: 'error',
            type: 'readability-violation'
          });
        }
      }
    } catch (error) {
      console.error(`Error analyzing ${filePath}:`, error.message);
    }
  }

  /**
   * Report readability analysis results
   */
  reportResults() {
    console.log('📚 Readability Analysis Results\n');

    if (this.violations.length === 0) {
      console.log('✅ All Plain sections meet readability requirements!');
      console.log(`   Target: Grade ${this.maxGradeLevel} or below`);
      return;
    }

    console.log(`❌ ${this.violations.length} Readability Violations Found:\n`);

    this.violations.forEach((violation, index) => {
      console.log(`${index + 1}. ${violation.file}:${violation.line}`);
      console.log(`   Grade Level: ${violation.gradeLevel} (max: ${violation.maxGrade})`);
      console.log(`   Content: "${violation.content}"`);
      console.log(`   
   💡 Suggestions:`);
      violation.suggestion.suggestions.forEach(suggestion => {
        console.log(`     • ${suggestion}`);
      });
      console.log(`   
   📝 Rewrite Example: ${violation.suggestion.rewriteExample}`);
      console.log('');
    });

    console.log('📊 Summary:');
    console.log(`   Violations: ${this.violations.length}`);
    console.log(`   Target Grade Level: ${this.maxGradeLevel}`);
    console.log('\n🚫 Build blocked due to readability violations.');
    console.log('   Fix violations above and re-run.');
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
  const scorer = new ReadabilityScorer();
  scorer.analyze().catch(error => {
    console.error('Readability analysis failed:', error);
    process.exit(1);
  });
}

module.exports = ReadabilityScorer;
module.exports.fkGrade = ReadabilityScorer.prototype.fkGrade;