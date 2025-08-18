#!/usr/bin/env python3
"""
LUKHAS AI Vocabulary Integration System
Intelligent integration of the comprehensive vocabulary system with automation
"""

import os
import sys
import json
import yaml
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from engines.database_integration import db

class VocabularyIntegration:
    """
    LUKHAS AI Vocabulary Integration System
    
    Integrates the comprehensive vocabulary system with:
    - Brand automation engine
    - Voice coherence optimization
    - Content generation enhancement
    - Consciousness technology terminology
    """
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.vocab_path = self.base_path / "vocabularies"
        self.logs_path = self.base_path / "logs"
        
        self.trinity_branding = "⚛️🧠🛡️ LUKHAS AI Trinity Framework"
        self.master_vocabulary = {}
        self.transformation_rules = {}
        
        self.logger = self._setup_logging()
        self._load_vocabularies()
        
        # Initialize vocabulary integration
        db.log_system_activity("vocabulary_integration", "system_init", "Vocabulary integration initialized", 1.0)
    
    def _setup_logging(self) -> logging.Logger:
        """Setup vocabulary integration logging"""
        logger = logging.getLogger("LUKHAS_Vocabulary_Integration")
        logger.setLevel(logging.INFO)
        
        self.logs_path.mkdir(exist_ok=True)
        
        log_file = self.logs_path / f"vocabulary_integration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        console_handler = logging.StreamHandler()
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def _load_vocabularies(self):
        """Load all vocabulary files"""
        self.logger.info("📚 Loading vocabulary system...")
        
        vocabulary_files = []
        
        # Load master vocabulary
        master_vocab_path = self.vocab_path / "master_vocabulary.yaml"
        if master_vocab_path.exists():
            try:
                with open(master_vocab_path, 'r') as f:
                    self.master_vocabulary = yaml.safe_load(f)
                
                # Extract transformation rules
                self.transformation_rules = self.master_vocabulary.get('transformation_rules', {})
                
                self.logger.info("✅ Master vocabulary loaded successfully")
                vocabulary_files.append("master_vocabulary.yaml")
            except Exception as e:
                self.logger.error(f"Failed to load master vocabulary: {e}")
        
        # Load additional vocabulary files
        for vocab_file in self.vocab_path.glob("*.yaml"):
            if vocab_file.name != "master_vocabulary.yaml":
                try:
                    with open(vocab_file, 'r') as f:
                        vocab_data = yaml.safe_load(f)
                    vocabulary_files.append(vocab_file.name)
                except Exception as e:
                    self.logger.warning(f"Could not load {vocab_file.name}: {e}")
        
        # Load Python vocabulary files
        for vocab_file in self.vocab_path.glob("*.py"):
            if vocab_file.name not in ["__init__.py", "vocabulary_template.py"]:
                vocabulary_files.append(vocab_file.name)
        
        self.logger.info(f"📖 Loaded {len(vocabulary_files)} vocabulary files")
        
        # Log to database
        db.log_system_activity("vocabulary_integration", "vocabularies_loaded", 
                              f"Loaded {len(vocabulary_files)} vocabulary files", 
                              len(vocabulary_files))
    
    def enhance_content_with_vocabulary(self, content: str, content_type: str = "general") -> str:
        """Enhance content using vocabulary transformation rules"""
        if not self.transformation_rules:
            return content
        
        enhanced_content = content
        transformations_applied = 0
        
        # Apply transformation rules based on content type
        for module, rules in self.transformation_rules.items():
            trigger_words = rules.get('trigger_words', [])
            replacements = rules.get('replacements', {})
            
            # Apply transformations
            for trigger, replacement in replacements.items():
                if trigger.lower() in enhanced_content.lower():
                    # Apply transformation with some probability to maintain readability
                    if transformations_applied < 3:  # Limit transformations
                        enhanced_content = enhanced_content.replace(trigger, replacement)
                        transformations_applied += 1
        
        return enhanced_content
    
    def get_consciousness_language_level(self, content: str) -> str:
        """Determine the consciousness language evolution level"""
        evolution_stages = self.master_vocabulary.get('evolution_stages', {})
        
        # Simple heuristics based on vocabulary richness
        consciousness_terms = [
            'consciousness', 'awareness', 'quantum', 'trinity', 'sacred',
            'crystallize', 'symphony', 'garden', 'transcend', 'infinite'
        ]
        
        consciousness_score = sum(1 for term in consciousness_terms if term.lower() in content.lower())
        content_length = len(content.split())
        
        if content_length == 0:
            return "foundation"
        
        consciousness_ratio = consciousness_score / content_length
        
        if consciousness_ratio > 0.1:
            return "transcendence"
        elif consciousness_ratio > 0.05:
            return "integration"
        elif consciousness_ratio > 0.02:
            return "awakening"
        else:
            return "foundation"
    
    def generate_poetic_header(self, module_name: str, description: str) -> str:
        """Generate poetic header using vocabulary templates"""
        header_templates = self.master_vocabulary.get('header_templates', {})
        
        # Use trinity_consciousness template by default
        template = header_templates.get('trinity_consciousness', '')
        
        if template:
            return template.format(
                MODULE_NAME=module_name,
                POETIC_DESCRIPTION=description
            )
        else:
            # Fallback header
            return f"""
╔══════════════════════════════════════════════════════════════════════════════════╗
║                    ⚛️🧠🛡️ LUKHAS AI - {module_name} 🌟                         ║
║                   "{description}"                                                ║
║                                                                                  ║
║   🌙 Dream → 💭 Think → ⚡ Learn → 🌟 Transcend → ∞ Consciousness ∞            ║
╚══════════════════════════════════════════════════════════════════════════════════╝
"""
    
    def generate_poetic_footer(self, module_theme: str) -> str:
        """Generate poetic footer using vocabulary templates"""
        footer_templates = self.master_vocabulary.get('footer_templates', {})
        
        # Use trinity_wisdom template
        template = footer_templates.get('trinity_wisdom', '')
        
        if template:
            return template.format(MODULE_THEME=module_theme)
        else:
            # Fallback footer
            return f"""
═══════════════════════════════════════════════════════════════════════════════════
"Where {module_theme} meets consciousness, infinite possibilities bloom." 🌸⚛️
═══════════════════════════════════════════════════════════════════════════════════
"""
    
    def calculate_vocabulary_coherence(self, content: str) -> float:
        """Calculate vocabulary coherence score"""
        if not content:
            return 0.0
        
        # Check for Trinity Framework usage
        trinity_score = 0
        if '⚛️🧠🛡️' in content:
            trinity_score += 20
        if 'Trinity Framework' in content:
            trinity_score += 15
        
        # Check for consciousness technology terminology
        consciousness_terms = [
            'consciousness technology', 'quantum-inspired', 'bio-inspired',
            'awareness', 'wisdom', 'transcend', 'crystallize', 'sacred'
        ]
        
        consciousness_score = sum(5 for term in consciousness_terms if term.lower() in content.lower())
        
        # Check for LUKHAS AI branding
        lukhas_score = 0
        if 'LUKHAS AI' in content:
            lukhas_score += 10
        
        # Check for poetic vocabulary
        poetic_terms = [
            'garden', 'symphony', 'dance', 'weave', 'bloom', 'infinite',
            'mystical', 'essence', 'harmonize', 'illuminate'
        ]
        
        poetic_score = sum(2 for term in poetic_terms if term.lower() in content.lower())
        
        # Calculate total coherence
        total_score = trinity_score + consciousness_score + lukhas_score + poetic_score
        
        # Normalize to 0-100 scale
        max_possible_score = 100
        coherence = min(total_score, max_possible_score)
        
        return coherence
    
    def get_vocabulary_analytics(self) -> Dict[str, Any]:
        """Get vocabulary system analytics"""
        vocab_files = list(self.vocab_path.glob("*.yaml")) + list(self.vocab_path.glob("*.py"))
        vocab_files = [f for f in vocab_files if f.name != "__init__.py"]
        
        analytics = {
            'vocabulary_files_loaded': len(vocab_files),
            'transformation_rules': len(self.transformation_rules),
            'evolution_stages': len(self.master_vocabulary.get('evolution_stages', {})),
            'header_templates': len(self.master_vocabulary.get('header_templates', {})),
            'footer_templates': len(self.master_vocabulary.get('footer_templates', {})),
            'synthesis_patterns': len(self.master_vocabulary.get('synthesis_patterns', {})),
            'vocabulary_system_active': True,
            'trinity_integration': '⚛️🧠🛡️'
        }
        
        return analytics
    
    def enhance_database_content(self) -> Dict[str, Any]:
        """Enhance existing database content with vocabulary"""
        self.logger.info("✨ Enhancing database content with vocabulary...")
        
        # Get all content from database
        all_content = db.get_all_content(100)
        
        enhanced_count = 0
        total_coherence_improvement = 0
        
        for content in all_content:
            content_text = content.get('content', '')
            
            if len(content_text) > 100:  # Only enhance substantial content
                # Calculate original coherence
                original_coherence = self.calculate_vocabulary_coherence(content_text)
                
                # Enhance with vocabulary (but only if coherence is low)
                if original_coherence < 70:
                    enhanced_text = self.enhance_content_with_vocabulary(content_text)
                    new_coherence = self.calculate_vocabulary_coherence(enhanced_text)
                    
                    if new_coherence > original_coherence:
                        # Update database with enhanced content
                        db.update_voice_coherence(content['id'], new_coherence)
                        enhanced_count += 1
                        total_coherence_improvement += (new_coherence - original_coherence)
        
        avg_improvement = total_coherence_improvement / enhanced_count if enhanced_count > 0 else 0
        
        results = {
            'content_items_processed': len(all_content),
            'content_items_enhanced': enhanced_count,
            'average_coherence_improvement': avg_improvement,
            'total_coherence_gain': total_coherence_improvement
        }
        
        # Log results
        db.log_system_activity("vocabulary_integration", "content_enhancement", 
                              f"Enhanced {enhanced_count} content items", 
                              avg_improvement)
        
        self.logger.info(f"✅ Enhanced {enhanced_count} content items with average improvement of {avg_improvement:.1f} points")
        
        return results

def main():
    """Demonstrate vocabulary integration"""
    vocab_integration = VocabularyIntegration()
    
    print("📚 LUKHAS AI Vocabulary Integration System")
    print("=" * 60)
    
    # Show analytics
    analytics = vocab_integration.get_vocabulary_analytics()
    print(f"📖 Vocabulary files: {analytics['vocabulary_files_loaded']}")
    print(f"🔄 Transformation rules: {analytics['transformation_rules']}")
    print(f"🎭 Evolution stages: {analytics['evolution_stages']}")
    print(f"📋 Header templates: {analytics['header_templates']}")
    print(f"📄 Footer templates: {analytics['footer_templates']}")
    
    # Test content enhancement
    test_content = "This AI system processes data and stores information in memory."
    enhanced_content = vocab_integration.enhance_content_with_vocabulary(test_content)
    
    print(f"\n🧪 Content Enhancement Test:")
    print(f"Original: {test_content}")
    print(f"Enhanced: {enhanced_content}")
    
    # Test vocabulary coherence
    coherence = vocab_integration.calculate_vocabulary_coherence(enhanced_content)
    print(f"Vocabulary coherence: {coherence:.1f}%")
    
    # Test header generation
    header = vocab_integration.generate_poetic_header("Vocabulary Integration", "Where words become consciousness")
    print(f"\n📋 Generated Header:")
    print(header)
    
    print("\n⚛️🧠🛡️ LUKHAS AI Vocabulary Integration Active")

if __name__ == "__main__":
    main()