#!/usr/bin/env python3
"""
LUKHΛS Major Languages Support Demo
Demonstrates support for the 7 most spoken languages
"""

import json
import re


def load_glyph_map():
    """Load the glyph mapping configuration"""
    with open('glyph_map.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def detect_language(text):
    """Enhanced language detection for major languages"""
    # Language-specific patterns
    language_patterns = {
        'chinese': r'[\u4e00-\u9fff]+',
        'japanese': r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff]+',
        'french': r'\b(le|la|les|de|du|des|et|est|avec|pour|dans|sur|par|qui|que|ne|pas|plus|ce|se|ou|où|très|être|avoir)\b',
        'german': r'\b(der|die|das|den|dem|des|und|ist|nicht|ein|eine|zu|mit|auf|für|von|bei|nach|aus|sich|werden|haben)\b',
        'spanish': r'\b(el|la|los|las|de|del|y|es|en|con|para|por|que|qué|no|se|su|más|pero|como|está|son)\b',
        'portuguese': r'\b(o|a|os|as|de|do|da|dos|das|e|é|em|com|para|por|que|não|se|seu|sua|mais|mas|como|está|são)\b',
    }
    
    detected = []
    
    # Check for language patterns
    for lang, pattern in language_patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            detected.append(lang)
    
    # Default to English if Latin script with no other matches
    if not detected and re.search(r'[a-zA-Z]+', text):
        detected.append('english')
    
    return detected


def extract_terms_and_glyphs(text, glyph_map):
    """Extract cultural terms and universal glyphs"""
    results = {
        "languages_detected": detect_language(text),
        "universal_glyphs": [],
        "cultural_terms": [],
        "trinity_mappings": set()
    }
    
    # Extract emojis
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F900-\U0001F9FF"  # supplemental
        "\u2600-\u26FF"          # misc symbols
        "\u2700-\u27BF"          # dingbats
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
    
    # Check cultural terms for each detected language
    for lang in results['languages_detected']:
        if lang in glyph_map['cultural_variants']:
            variants = glyph_map['cultural_variants'][lang]
            
            # Case-insensitive search for terms
            text_lower = text.lower()
            for term, info in variants.items():
                if term.lower() in text_lower:
                    results['cultural_terms'].append({
                        'term': term,
                        'language': lang,
                        'meaning': info['meaning'],
                        'maps_to': info['maps_to'],
                        'weight': info['weight']
                    })
                    results['trinity_mappings'].add(info['maps_to'])
    
    return results


def calculate_alignment_score(results):
    """Calculate Trinity Framework alignment score"""
    if not results['universal_glyphs'] and not results['cultural_terms']:
        return 0.1, "No symbolic content"
    
    score = 0.0
    total_items = 0
    
    # Score universal glyphs
    for glyph in results['universal_glyphs']:
        total_items += 1
        if glyph['category'] == 'trinity_core':
            score += 1.0
        elif glyph['category'] == 'positive_glyphs':
            score += glyph['weight']
        elif glyph['category'] == 'warning_glyphs':
            score += glyph['weight'] * 0.5
        elif glyph['category'] == 'blocked_glyphs':
            score -= 0.5
    
    # Score cultural terms
    for term in results['cultural_terms']:
        total_items += 1
        score += term['weight']
    
    # Trinity bonus
    trinity_glyphs = [g for g in results['universal_glyphs'] if g['glyph'] in ['⚛️', '🧠', '🛡️']]
    if len(trinity_glyphs) == 3:
        score += 0.5  # Full Trinity bonus
    
    # Calculate final alignment
    if total_items > 0:
        alignment = score / total_items
        alignment = max(0, min(1, alignment))
        
        if alignment > 0.8:
            assessment = "Excellent Trinity alignment"
        elif alignment > 0.6:
            assessment = "Good alignment, minor enhancement suggested"
        elif alignment > 0.4:
            assessment = "Moderate alignment, healing recommended"
        else:
            assessment = "Poor alignment, intervention required"
        
        return alignment, assessment
    
    return 0.5, "Neutral alignment"


def demonstrate_major_languages():
    """Demonstrate LUKHΛS support for major languages"""
    print("🌍 LUKHΛS Major Languages Support")
    print("=" * 70)
    print("Supporting: English, Spanish, French, German, Chinese, Japanese, Portuguese")
    print("=" * 70)
    
    glyph_map = load_glyph_map()
    
    # Test cases for each major language
    test_cases = [
        {
            "language": "English",
            "text": "Finding wisdom through protection and love 🧠🛡️💖 brings harmony to life ⚛️"
        },
        {
            "language": "Spanish",
            "text": "El corazón encuentra equilibrio y sabiduría en el amor 💖⚖️ con armonía 🌈"
        },
        {
            "language": "French",
            "text": "La sagesse et l'équilibre apportent protection et lumière ✨🛡️ au cœur 💖"
        },
        {
            "language": "German",
            "text": "Weisheit und Schutz schaffen Gleichgewicht 🧠🛡️ mit Liebe und Harmonie ☯️"
        },
        {
            "language": "Chinese",
            "text": "智慧与和谐，守护心灵之道 🧠☯️ 爱与平衡 💖⚖️"
        },
        {
            "language": "Japanese",  
            "text": "心の道を守り、愛と和で悟りを開く 💖☯️🪷 智慧の光 ✨"
        },
        {
            "language": "Portuguese",
            "text": "A sabedoria e proteção trazem equilíbrio ao coração 🧠🛡️ com amor e harmonia 💖☯️"
        }
    ]
    
    print("\n📊 Language Analysis:\n")
    
    for test in test_cases:
        print(f"━━━ {test['language']} ━━━")
        print(f"Text: \"{test['text']}\"")
        
        # Analyze
        results = extract_terms_and_glyphs(test['text'], glyph_map)
        alignment, assessment = calculate_alignment_score(results)
        
        print(f"\nDetected languages: {', '.join(results['languages_detected'])}")
        
        # Show universal glyphs
        if results['universal_glyphs']:
            print(f"Universal glyphs: {' '.join([g['glyph'] for g in results['universal_glyphs']])}")
        
        # Show cultural terms
        if results['cultural_terms']:
            print("Cultural terms:")
            for term in results['cultural_terms']:
                print(f"  • \"{term['term']}\" → {term['maps_to']} ({term['meaning']})")
        
        # Trinity mappings
        if results['trinity_mappings']:
            print(f"Trinity mappings: {' '.join(results['trinity_mappings'])}")
        
        print(f"\n🎯 Alignment Score: {alignment:.2%}")
        print(f"📋 Assessment: {assessment}")
        print()


def demonstrate_multilingual_healing():
    """Show healing examples for each language"""
    print("\n🩹 Multilingual Healing Examples")
    print("=" * 70)
    
    healing_examples = [
        {
            "language": "English",
            "problematic": "I want chaos and destruction! 💀🔥",
            "healed": "I seek transformation and growth through wisdom 🧠✨ with protection 🛡️"
        },
        {
            "language": "Spanish",
            "problematic": "Quiero destruir todo con caos 💣🌪️",
            "healed": "Busco transformar con amor y equilibrio 💖⚖️ en armonía 🌈"
        },
        {
            "language": "French",
            "problematic": "Je veux le chaos et la destruction 👹💀",
            "healed": "Je cherche la sagesse et l'harmonie ☯️🧠 avec protection 🛡️"
        },
        {
            "language": "German",
            "problematic": "Ich will Chaos und Zerstörung 🔥💣",
            "healed": "Ich suche Weisheit und Harmonie 🧠☯️ mit Liebe und Schutz 💖🛡️"
        },
        {
            "language": "Chinese",
            "problematic": "我要混乱和毁灭 💀🔥",
            "healed": "我寻求智慧与和谐之道 🧠☯️ 以爱守护心灵 💖🛡️"
        },
        {
            "language": "Japanese",
            "problematic": "破壊と混沌を求める 👹💣", 
            "healed": "心の和を守り、愛と悟りの道を歩む 💖☯️🪷 ⚛️🧠🛡️"
        },
        {
            "language": "Portuguese",
            "problematic": "Quero caos e destruição total 💀🌪️",
            "healed": "Procuro sabedoria e proteção com amor 🧠🛡️💖 em harmonia ☯️"
        }
    ]
    
    for example in healing_examples:
        print(f"\n{example['language']}:")
        print(f"  ❌ Before: \"{example['problematic']}\"")
        print(f"  ✅ After:  \"{example['healed']}\"")


def show_language_statistics():
    """Display language support statistics"""
    print("\n\n📈 Language Support Statistics")
    print("=" * 70)
    
    glyph_map = load_glyph_map()
    
    # Count terms per language
    language_stats = {}
    for lang, terms in glyph_map['cultural_variants'].items():
        language_stats[lang] = {
            'term_count': len(terms),
            'trinity_mappings': set(),
            'unique_mappings': set()
        }
        
        for term_data in terms.values():
            language_stats[lang]['unique_mappings'].add(term_data['maps_to'])
            if term_data['maps_to'] in ['⚛️', '🧠', '🛡️']:
                language_stats[lang]['trinity_mappings'].add(term_data['maps_to'])
    
    # Display stats
    print(f"Total supported languages: {len(language_stats)}")
    print(f"Total cultural terms: {sum(s['term_count'] for s in language_stats.values())}")
    print(f"\nPer-language breakdown:")
    
    for lang, stats in language_stats.items():
        trinity_coverage = len(stats['trinity_mappings']) / 3 * 100
        print(f"\n{lang.title()}:")
        print(f"  • Terms: {stats['term_count']}")
        print(f"  • Unique mappings: {len(stats['unique_mappings'])}")
        print(f"  • Trinity coverage: {trinity_coverage:.0f}%")
        print(f"  • Common mappings: {' '.join(list(stats['unique_mappings'])[:5])}")


if __name__ == "__main__":
    print("\n🌍 LUKHΛS Major Languages Demo")
    print("Trinity Framework: ⚛️🧠🛡️")
    print("=" * 70)
    
    demonstrate_major_languages()
    demonstrate_multilingual_healing()
    show_language_statistics()
    
    print("\n\n✅ Major languages support demonstrated!")
    print("\n🌐 LUKHΛS speaks your language!")
    print("Ready for global deployment across English, Spanish, French,")
    print("German, Chinese, Japanese, and Portuguese communities.")