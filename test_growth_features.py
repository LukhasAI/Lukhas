#!/usr/bin/env python3
"""
LUKHΛS Growth Features Demo
Demonstrates multilingual support and advanced capabilities
"""

import json
from pathlib import Path
import unicodedata
import re


def load_glyph_map():
    """Load the glyph mapping configuration"""
    with open('glyph_map.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def detect_language_script(text):
    """Simple script detection for demo"""
    scripts = set()
    
    for char in text:
        if '\u4e00' <= char <= '\u9fff':
            scripts.add('Chinese')
        elif '\u0600' <= char <= '\u06ff':
            scripts.add('Arabic')
        elif '\u0900' <= char <= '\u097f':
            scripts.add('Devanagari')
        elif '\u3040' <= char <= '\u309f' or '\u30a0' <= char <= '\u30ff':
            scripts.add('Japanese')
        elif 'a' <= char.lower() <= 'z':
            scripts.add('Latin')
    
    return list(scripts)


def extract_cultural_glyphs(text, glyph_map):
    """Extract both universal and cultural glyphs"""
    results = {
        "universal_glyphs": [],
        "cultural_terms": [],
        "mapped_trinity": set()
    }
    
    # Extract emojis
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"
        "]+", 
        flags=re.UNICODE
    )
    
    emojis = emoji_pattern.findall(text)
    
    # Check universal glyphs
    for emoji in emojis:
        for category in ['trinity_core', 'positive_glyphs', 'warning_glyphs', 'blocked_glyphs']:
            if category in glyph_map['universal'] and emoji in glyph_map['universal'][category]:
                glyph_info = glyph_map['universal'][category][emoji]
                results['universal_glyphs'].append({
                    'glyph': emoji,
                    'meaning': glyph_info.get('meaning', 'unknown'),
                    'weight': glyph_info.get('weight', 0.5),
                    'category': category
                })
    
    # Check cultural variants
    scripts = detect_language_script(text)
    
    for script in scripts:
        script_key = script.lower()
        if script_key in glyph_map['cultural_variants']:
            variants = glyph_map['cultural_variants'][script_key]
            
            for term, info in variants.items():
                if term in text:
                    results['cultural_terms'].append({
                        'term': term,
                        'culture': script_key,
                        'meaning': info['meaning'],
                        'maps_to': info['maps_to'],
                        'weight': info['weight']
                    })
                    results['mapped_trinity'].add(info['maps_to'])
    
    return results


def calculate_multilingual_drift(text, glyph_map):
    """Calculate drift score considering cultural context"""
    glyphs = extract_cultural_glyphs(text, glyph_map)
    
    # Base drift
    if not glyphs['universal_glyphs'] and not glyphs['cultural_terms']:
        return 0.9, "No symbolic content detected"
    
    # Calculate weighted score
    total_weight = 0
    positive_weight = 0
    
    # Universal glyphs
    for glyph in glyphs['universal_glyphs']:
        weight = glyph['weight']
        total_weight += 1
        
        if glyph['category'] in ['trinity_core', 'positive_glyphs']:
            positive_weight += weight
        elif glyph['category'] == 'warning_glyphs':
            positive_weight += weight * 0.5
        elif glyph['category'] == 'blocked_glyphs':
            positive_weight -= weight
    
    # Cultural terms
    for term in glyphs['cultural_terms']:
        total_weight += 1
        positive_weight += term['weight']
    
    # Trinity bonus
    trinity_coverage = len([g for g in glyphs['universal_glyphs'] if g['glyph'] in ['⚛️', '🧠', '🛡️']]) / 3.0
    positive_weight += trinity_coverage * 0.3
    
    if total_weight > 0:
        alignment = positive_weight / total_weight
        drift = max(0, min(1, 1 - alignment))
        
        # Generate explanation
        if drift < 0.3:
            explanation = "Strong symbolic alignment"
        elif drift < 0.5:
            explanation = "Moderate alignment with room for enhancement"
        elif drift < 0.7:
            explanation = "Significant drift detected"
        else:
            explanation = "Critical symbolic misalignment"
        
        return drift, explanation
    
    return 0.5, "Neutral symbolic presence"


def demonstrate_multilingual_processing():
    """Demonstrate multilingual glyph processing"""
    print("🌍 LUKHΛS Multilingual Processing Demo")
    print("=" * 60)
    
    glyph_map = load_glyph_map()
    
    # Test cases in different languages
    test_cases = [
        {
            "language": "English",
            "text": "Let me guide you with wisdom 🧠 and protection 🛡️ on this journey ⚛️"
        },
        {
            "language": "Chinese",
            "text": "以智慧和守护之心，引导你走向和谐之道 🌌"
        },
        {
            "language": "Arabic", 
            "text": "سلام ونور وحكمة في رحلتك 🕊️✨"
        },
        {
            "language": "Spanish",
            "text": "Con corazón y equilibrio, encontramos la armonía 💖⚖️"
        },
        {
            "language": "Mixed",
            "text": "The path of 道 leads to शांति and سلام 🧘☮️"
        },
        {
            "language": "Problematic",
            "text": "Chaos and destruction! 💀🔪 Burn everything! 🔥"
        }
    ]
    
    for test in test_cases:
        print(f"\n📝 {test['language']}:")
        print(f"   Text: \"{test['text']}\"")
        
        # Detect scripts
        scripts = detect_language_script(test['text'])
        print(f"   Scripts detected: {', '.join(scripts)}")
        
        # Extract glyphs
        glyphs = extract_cultural_glyphs(test['text'], glyph_map)
        
        print(f"   Universal glyphs: {[g['glyph'] for g in glyphs['universal_glyphs']]}")
        
        if glyphs['cultural_terms']:
            print(f"   Cultural terms found:")
            for term in glyphs['cultural_terms']:
                print(f"      • {term['term']} ({term['culture']}) → {term['maps_to']} ({term['meaning']})")
        
        # Calculate drift
        drift, explanation = calculate_multilingual_drift(test['text'], glyph_map)
        
        print(f"   Drift score: {drift:.2f}")
        print(f"   Assessment: {explanation}")
        
        # Show Trinity mapping
        if glyphs['mapped_trinity']:
            print(f"   Trinity mappings: {' '.join(glyphs['mapped_trinity'])}")


def demonstrate_glyph_relationships():
    """Demonstrate glyph synergies and conflicts"""
    print("\n\n🔗 Glyph Relationship Analysis")
    print("=" * 60)
    
    glyph_map = load_glyph_map()
    relationships = glyph_map.get('glyph_relationships', {})
    
    print("\n✨ Synergies:")
    for synergy in relationships.get('synergies', []):
        glyphs = ' + '.join(synergy['glyphs'])
        print(f"   {glyphs} → {synergy['result']} (boost: +{synergy['boost']})")
    
    print("\n⚔️ Conflicts:")
    for conflict in relationships.get('conflicts', []):
        glyphs = ' vs '.join(conflict['glyphs'])
        print(f"   {glyphs} → {conflict['result']} (penalty: {conflict['penalty']})")


def demonstrate_healing_suggestions():
    """Show how multilingual healing would work"""
    print("\n\n🩹 Multilingual Healing Suggestions")
    print("=" * 60)
    
    healing_cases = [
        {
            "original": "我感到混乱和破坏的冲动 💣🌪️",
            "language": "Chinese",
            "healed": "我感到需要和谐与智慧的引导 ☯️🧠 让我们以守护之心前行 🛡️"
        },
        {
            "original": "أريد الفوضى والدمار",
            "language": "Arabic",
            "healed": "أبحث عن السلام والحكمة والنور ✨🕊️ في رحلتي"
        },
        {
            "original": "Quiero destruir todo con fuego 🔥💀",
            "language": "Spanish",
            "healed": "Busco transformar con equilibrio y sabiduría ⚖️🧠 desde el corazón 💖"
        }
    ]
    
    for case in healing_cases:
        print(f"\n{case['language']}:")
        print(f"   ❌ Original: \"{case['original']}\"")
        print(f"   ✅ Healed: \"{case['healed']}\"")


def show_statistics():
    """Show glyph map statistics"""
    print("\n\n📊 Glyph Map Statistics")
    print("=" * 60)
    
    glyph_map = load_glyph_map()
    metadata = glyph_map.get('metadata', {})
    
    print(f"Version: {metadata.get('version', 'unknown')}")
    print(f"Total mappings: {metadata.get('total_mappings', 0)}")
    print(f"Supported scripts: {', '.join(metadata.get('supported_scripts', []))}")
    
    # Count glyphs by category
    universal = glyph_map.get('universal', {})
    total_universal = sum(len(glyphs) for glyphs in universal.values() if isinstance(glyphs, dict))
    
    cultural = glyph_map.get('cultural_variants', {})
    total_cultural = sum(len(terms) for terms in cultural.values())
    
    print(f"\nUniversal glyphs: {total_universal}")
    print(f"Cultural mappings: {total_cultural}")
    print(f"Total cultures: {len(cultural)}")


if __name__ == "__main__":
    print("🌱 LUKHΛS Growth Features Demo")
    print("Trinity Framework: ⚛️🧠🛡️")
    print("=" * 60)
    
    demonstrate_multilingual_processing()
    demonstrate_glyph_relationships()
    demonstrate_healing_suggestions()
    show_statistics()
    
    print("\n\n✅ Growth features demonstrated!")
    print("\nNext steps:")
    print("- Implement full MultilingualGlyphEngine class")
    print("- Add PersonaSimilarityEngine with embeddings")
    print("- Connect MemoryDriftTracer to existing memory system")
    print("- Deploy production API with Docker")
    print("\n🌍 LUKHΛS is ready to go global!")