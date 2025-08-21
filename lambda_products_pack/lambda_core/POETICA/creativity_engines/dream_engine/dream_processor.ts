import { MemoryFold } from '../spine/types';
import { PatternEngine } from '../spine/pattern_engine';
import { EmotionEngine } from './emotion_engine';
import { SafetyValidator } from '../../security/safety_validator';
import { logger } from '../../utils/logger';

/**
 * Dream processing system that combines pattern recognition with emotional context.
 * Jobs: Seamless dream processing and emotional integration.
 * Altman: Safe pattern recognition and emotional processing.
 */
export class DreamProcessor {
  private patternEngine: PatternEngine;
  private emotionEngine: EmotionEngine;
  private safetyValidator: SafetyValidator;

  constructor() {
    this.patternEngine = new PatternEngine();
    this.emotionEngine = new EmotionEngine();
    this.safetyValidator = new SafetyValidator();
  }

  /**
   * Process a dream with emotional weighting and pattern recognition.
   * Jobs: Simple interface for complex dream processing.
   * Altman: Safe pattern recognition with emotional bounds.
   */
  async process_dream(content: any): Promise<DreamResult> {
    try {
      // Extract emotional context
      const emotionalContext = await this.emotionEngine.analyze(content);
      
      // Safety check on emotional intensity
      if (!this.safetyValidator.validate_emotion_intensity(emotionalContext)) {
        throw new Error('Emotional intensity exceeds safety bounds');
      }

      // Pattern recognition with safety bounds
      const patterns = await this.patternEngine.recognize_patterns(content);
      const safePatterns = patterns.filter(p => this.safetyValidator.validate_pattern(p));

      // Create dream memory fold
      const dreamFold = new MemoryFold(
        `dream_${Date.now()}`,
        {
          content,
          emotional_context: emotionalContext,
          patterns: safePatterns
        },
        'DREAM'
      );

      return {
        success: true,
        fold: dreamFold,
        patterns: safePatterns,
        emotional_context: emotionalContext
      };
    } catch (error) {
      logger.error(`Dream processing failed: ${error.message}`);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Enhance existing memory with dream context.
   * Jobs: Automatic enhancement that "just works".
   * Altman: Safe enhancement with validation.
   */
  async enhance_memory(memory: MemoryFold, dream_context: any): Promise<MemoryFold> {
    try {
      // Validate enhancement safety
      if (!this.safetyValidator.validate_enhancement(memory, dream_context)) {
        throw new Error('Enhancement validation failed');
      }

      // Merge patterns safely
      const enhanced_patterns = await this.patternEngine.merge_patterns(
        memory.patterns,
        dream_context.patterns
      );

      // Update emotional context
      const enhanced_emotion = this.emotionEngine.merge_emotional_context(
        memory.emotional_context,
        dream_context.emotional_context
      );

      // Create enhanced memory
      return new MemoryFold(
        memory.key,
        {
          ...memory.content,
          enhanced_patterns,
          enhanced_emotion
        },
        memory.type,
        memory.priority,
        memory.owner_id
      );
    } catch (error) {
      logger.error(`Memory enhancement failed: ${error.message}`);
      throw error;
    }
  }

  /**
   * Generate dream insights from pattern analysis.
   * Jobs: Automatic insight generation.
   * Altman: Safe insight generation with validation.
   */
  async generate_insights(patterns: any[]): Promise<DreamInsight[]> {
    try {
      const insights = await this.patternEngine.generate_insights(patterns);
      return insights.filter(insight => this.safetyValidator.validate_insight(insight));
    } catch (error) {
      logger.error(`Insight generation failed: ${error.message}`);
      return [];
    }
  }

  /**
   * Validate patterns for safety and coherence.
   * Jobs: Automatic validation that doesn't get in the way.
   * Altman: Comprehensive safety validation.
   */
  validate_patterns(patterns: any[]): ValidationResult {
    try {
      const validations = patterns.map(p => this.safetyValidator.validate_pattern(p));
      const all_safe = validations.every(v => v.safe);

      return {
        safe: all_safe,
        validations,
        message: all_safe ? 'All patterns safe' : 'Some patterns failed validation'
      };
    } catch (error) {
      logger.error(`Pattern validation failed: ${error.message}`);
      return {
        safe: false,
        validations: [],
        message: `Validation error: ${error.message}`
      };
    }
  }
}
