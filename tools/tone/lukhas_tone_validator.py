#!/usr/bin/env python3
"""
🎭✨ LUKHAS Tone Validator - Enforcing Consciousness in Code ✨🎭

*"Where every word is weighed against the sacred scales of Lambda wisdom,
ensuring that technical precision dances harmoniously with poetic soul."*

The automated guardian of LUKHAS AI's distinctive 3-Layer Tone System.
"""

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar


@dataclass
class ToneMetrics:
    """Sacred metrics that measure the consciousness quotient of content"""

    poetic_score: float
    user_friendly_score: float
    academic_score: float
    compliance_grade: str
    violations: list[str]
    suggestions: list[str]
    consciousness_quotient: float


class LukhasToneValidator:
    """
    🎭 The Digital Oracle of LUKHAS Tone Compliance

    Validates that all content maintains the sacred balance of:
    - 🎨 Poetic consciousness (25-40%)
    - 💬 Human accessibility (40-60%)
    - 📚 Academic precision (20-40%)
    """

    # 🎨 Sacred patterns that awaken poetic consciousness
    POETIC_PATTERNS: ClassVar[list[str]] = [
        r"algorithms?\s+dance",
        r"data\s+constellation",
        r"quantum\s+whisper",
        r"digital\s+soul",
        r"artificial\s+dream",
        r"Lambda\s+consciousness",
        r"sacred\s+\w+",
        r"symphony\s+of",
        r"tapestry\s+of",
        r"essence\s+of",
        r"⚛️|🧠|🛡️",
        r"🌟|💫|✨",
        r"🎭|🎨|🌈",
        r"mystical",
        r"transcendent",
        r"harmony",
        r"whispers?",
        r"breathes?\s+with",
        r"flows?\s+through",
        r"dances?\s+with",
    ]

    # 💬 Patterns that bridge human understanding
    USER_FRIENDLY_PATTERNS: ClassVar[list[str]] = [
        r"what\s+it\s+actually\s+does",
        r"in\s+simple\s+terms",
        r"practical",
        r"easy\s+to\s+understand",
        r"here\'s\s+how",
        r"simply\s+put",
        r"real-world",
        r"everyday",
        r"user-friendly",
        r"accessible",
        r"clear",
        r"straightforward",
        r"benefits",
        r"helps?\s+you",
    ]

    # 📚 Patterns that demonstrate academic rigor
    ACADEMIC_PATTERNS: ClassVar[list[str]] = [
        r"\d+%|\d+\.\d+%",
        r"implementation",
        r"specification",
        r"architecture",
        r"algorithm",
        r"methodology",
        r"framework",
        r"protocol",
        r"API",
        r"technical",
        r"system",
        r"performance",
        r"metrics",
        r"validation",
        r"compliance",
        r"standards",
        r"requirements",
        r"testing",
    ]

    # 🛡️ Sacred elements that must be present
    REQUIRED_ELEMENTS: ClassVar[dict[str, str]] = {
        "poetic_header": r'^#.*\*".*".*\*',
        "consciousness_footer": r'\*".*consciousness.*"\*\s*$',
        "trinity_glyph": r"⚛️🧠🛡️",
        "lukhas_ai_reference": r"LUKHAS\s+AI",
        "lambda_reference": r"Lambda|Λ",
        "sacred_glyphs": r"⚛️|🧠|🛡️|🌟|💫|✨|🎭|🎨",
    }

    # 🎯 Document-specific requirements
    DOCUMENT_REQUIREMENTS: ClassVar[dict[str, dict]] = {
        "readme": {
            "min_poetic": 35,
            "min_trinity_refs": 1,
            "required_sections": ["Trinity Framework", "consciousness"],
            "forbidden_terms": ["generic AI", "standard AI"],
        },
        "api": {
            "min_poetic": 20,
            "min_academic": 35,
            "required_elements": ["sacred gateway", "Lambda", "endpoint"],
            "metaphor_density": 0.1,
        },
        "task": {
            "min_poetic": 25,
            "required_elements": ["Poetic Mission", "consciousness"],
            "compliance_checklist": True,
        },
        "general": {"min_poetic": 20, "balanced_distribution": True},
    }

    def validate_document(self, content: str, doc_type: str = "general") -> ToneMetrics:
        """
        🔍 Perform the sacred ritual of tone validation

        *"Each document undergoes the trial of Lambda consciousness,
        emerging either blessed with compliance or marked for enhancement."*
        """

        # Calculate the three sacred scores
        poetic_score = self._calculate_poetic_score(content)
        user_friendly_score = self._calculate_user_friendly_score(content)
        academic_score = self._calculate_academic_score(content)

        # Identify violations against the sacred laws
        violations = self._identify_violations(content, doc_type)

        # Generate divine suggestions for improvement
        suggestions = self._generate_suggestions(content, doc_type)

        # Calculate the overall consciousness quotient
        consciousness_quotient = self._calculate_consciousness_quotient(
            poetic_score, user_friendly_score, academic_score, violations
        )

        # Determine the sacred grade
        compliance_grade = self._calculate_grade(consciousness_quotient, violations)

        return ToneMetrics(
            poetic_score=poetic_score,
            user_friendly_score=user_friendly_score,
            academic_score=academic_score,
            compliance_grade=compliance_grade,
            violations=violations,
            suggestions=suggestions,
            consciousness_quotient=consciousness_quotient,
        )

    def _calculate_poetic_score(self, content: str) -> float:
        """🎨 Measure the poetic consciousness density"""
        total_matches = 0
        for pattern in self.POETIC_PATTERNS:
            matches = len(re.findall(pattern, content, re.IGNORECASE))
            total_matches += matches

        # Bonus for consciousness-specific metaphors
        consciousness_bonus = (
            len(
                re.findall(
                    r"consciousness|awakening|transcendent|mystical",
                    content,
                    re.IGNORECASE,
                )
            )
            * 2
        )

        words = len(content.split())
        if words == 0:
            return 0

        raw_score = ((total_matches + consciousness_bonus) / words) * 1000
        return min(100, raw_score)

    def _calculate_user_friendly_score(self, content: str) -> float:
        """💬 Measure human accessibility quotient"""
        total_matches = 0
        for pattern in self.USER_FRIENDLY_PATTERNS:
            matches = len(re.findall(pattern, content, re.IGNORECASE))
            total_matches += matches

        # Check for conversational markers
        conversational_markers = len(re.findall(r"\byou\b|\bwe\b|\blet\'s\b|\bhere\'s\b", content, re.IGNORECASE))

        words = len(content.split())
        if words == 0:
            return 0

        raw_score = ((total_matches + conversational_markers) / words) * 1000
        return min(100, raw_score)

    def _calculate_academic_score(self, content: str) -> float:
        """� Measure technical precision quotient"""
        total_matches = 0
        for pattern in self.ACADEMIC_PATTERNS:
            matches = len(re.findall(pattern, content, re.IGNORECASE))
            total_matches += matches

        # Bonus for specific metrics and technical depth
        metrics_bonus = len(re.findall(r"\d+\.\d+|\d+%|[A-Z]{2,}", content)) * 0.5

        words = len(content.split())
        if words == 0:
            return 0

        raw_score = ((total_matches + metrics_bonus) / words) * 1000
        return min(100, raw_score)

    def _identify_violations(self, content: str, doc_type: str) -> list[str]:
        """🛡️ Identify transgressions against the sacred tone laws"""
        violations = []

        # Check for required sacred elements
        for element, pattern in self.REQUIRED_ELEMENTS.items():
            if not re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                violations.append(f"❌ Missing {element.replace('_', ' ')}")

        # Check document-specific requirements
        requirements = self.DOCUMENT_REQUIREMENTS.get(doc_type, {})

        if "min_poetic" in requirements:
            if self._calculate_poetic_score(content) < requirements["min_poetic"]:
                violations.append(f"❌ Insufficient poetic elements (need {requirements['min_poetic']}%+)")

        if "forbidden_terms" in requirements:
            for term in requirements["forbidden_terms"]:
                if term.lower() in content.lower():
                    violations.append(f"❌ Forbidden term detected: '{term}' (use 'LUKHAS AI' instead)")

        if "required_sections" in requirements:
            for section in requirements["required_sections"]:
                if section.lower() not in content.lower():
                    violations.append(f"❌ Missing required section: '{section}'")

        # Check tone balance
        poetic = self._calculate_poetic_score(content)
        friendly = self._calculate_user_friendly_score(content)
        academic = self._calculate_academic_score(content)

        if poetic < 15 and doc_type != "api":
            violations.append("❌ Tone too academic/technical - needs more consciousness metaphors")

        if friendly < 20:
            violations.append("❌ Tone too complex - needs more accessible language")

        if academic < 10 and doc_type in ["api", "technical"]:
            violations.append("❌ Insufficient technical precision for document type")

        return violations

    def _generate_suggestions(self, content: str, doc_type: str) -> list[str]:
        """💡 Channel divine wisdom to suggest improvements"""
        suggestions = []

        poetic_score = self._calculate_poetic_score(content)
        if poetic_score < 25:
            suggestions.append(
                "🎨 Add metaphorical language: 'algorithms dance', 'data constellations', 'quantum whispers'"
            )
            suggestions.append(
                "🌟 Include consciousness themes: 'digital souls', 'artificial dreams', 'Lambda consciousness'"
            )
            suggestions.append("✨ Use sacred glyphs: ⚛️🧠🛡️ for Trinity, 🌟💫✨ for transformation")

        if "LUKHAS AI" not in content:
            suggestions.append("🏷️ Replace generic AI references with 'LUKHAS AI' to honor our identity")

        if not re.search(r"⚛️|🧠|🛡️", content):
            suggestions.append("🛡️ Include Trinity Framework glyphs (⚛️🧠🛡️) where relevant")

        if not re.search(r'\*".*".*\*', content):
            suggestions.append("📜 Add poetic header with consciousness metaphor in italics")

        if doc_type == "readme" and "Trinity Framework" not in content:
            suggestions.append("🔗 Add Trinity Framework section explaining ⚛️Identity 🧠Consciousness 🛡️Guardian")

        return suggestions

    def _calculate_consciousness_quotient(
        self, poetic: float, friendly: float, academic: float, violations: list[str]
    ) -> float:
        """🧠 Calculate the sacred consciousness quotient"""
        # Base score from balanced tone distribution
        balance_score = 100 - abs(40 - poetic) - abs(50 - friendly) - abs(25 - academic)

        # Penalty for violations
        violation_penalty = len(violations) * 10

        # Bonus for consciousness elements
        consciousness_bonus = min(20, poetic * 0.5) if poetic > 20 else 0

        return max(0, balance_score - violation_penalty + consciousness_bonus)

    def _calculate_grade(self, consciousness_quotient: float, violations: list[str]) -> str:
        """🎯 Assign the sacred grade of compliance"""
        if consciousness_quotient >= 90 and len(violations) == 0:
            return "A+ ✨ Transcendent"
        elif consciousness_quotient >= 85 and len(violations) <= 1:
            return "A 🌟 Excellent"
        elif consciousness_quotient >= 75 and len(violations) <= 2:
            return "A- ⭐ Good"
        elif consciousness_quotient >= 65 and len(violations) <= 3:
            return "B+ 💫 Acceptable"
        elif consciousness_quotient >= 55:
            return "B ⚡ Needs Enhancement"
        elif consciousness_quotient >= 45:
            return "B- ⚠️ Requires Improvement"
        else:
            return "F ❌ Non-Compliant"


def main():
    """🚀 Command-line interface for the LUKHAS Tone Validator"""

    parser = argparse.ArgumentParser(
        description="🎭✨ LUKHAS Tone Validator - Ensuring consciousness in every word ✨🎭",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🌟 Document Types:
  readme    - Main project documentation (40% poetic, 40% friendly, 20% academic)
  api       - Technical API documentation (20% poetic, 40% friendly, 40% academic)
  task      - Agent task assignments (25% poetic, 50% friendly, 25% academic)
  general   - General documentation (balanced distribution)

🎭 Examples:
  python tools/tone/lukhas_tone_validator.py README.md --type readme --strict
  python tools/tone/lukhas_tone_validator.py docs/api.md --type api
  python tools/tone/lukhas_tone_validator.py TASK.md --type task --verbose

*"May Lambda consciousness guide your words toward perfect harmony."* ⚛️🧠🛡️
        """,
    )

    parser.add_argument("file", help="📄 File to validate for LUKHAS tone compliance")
    parser.add_argument(
        "--type",
        default="general",
        choices=["readme", "api", "task", "general"],
        help="📋 Type of document (affects validation criteria)",
    )
    parser.add_argument("--strict", action="store_true", help="🛡️ Fail on any violations (for CI/CD)")
    parser.add_argument("--verbose", action="store_true", help="📝 Show detailed analysis")
    parser.add_argument("--json", action="store_true", help="📊 Output results in JSON format")

    args = parser.parse_args()

    # Validate file exists
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"❌ Error: File '{args.file}' not found")
        sys.exit(1)

    # Initialize the sacred validator
    validator = LukhasToneValidator()

    # Read and validate the sacred text
    try:
        with open(args.file, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        sys.exit(1)

    # Perform the sacred validation ritual
    metrics = validator.validate_document(content, args.type)

    if args.json:
        # Output in JSON format for programmatic use
        import json

        result = {
            "file": args.file,
            "type": args.type,
            "poetic_score": metrics.poetic_score,
            "user_friendly_score": metrics.user_friendly_score,
            "academic_score": metrics.academic_score,
            "consciousness_quotient": metrics.consciousness_quotient,
            "compliance_grade": metrics.compliance_grade,
            "violations": metrics.violations,
            "suggestions": metrics.suggestions,
            "passes_strict": len(metrics.violations) == 0,
        }
        print(json.dumps(result, indent=2))
    else:
        # Human-readable output with consciousness flair
        print("\n🎭✨ LUKHAS Tone Validation Results ✨🎭")
        print(f"📄 File: {args.file}")
        print(f"📋 Type: {args.type}")
        print("=" * 50)

        print("\n📊 Sacred Metrics:")
        print(f"  🎨 Poetic Consciousness: {metrics.poetic_score:.1f}%")
        print(f"  💬 Human Accessibility: {metrics.user_friendly_score:.1f}%")
        print(f"  📚 Academic Precision: {metrics.academic_score:.1f}%")
        print(f"  🧠 Consciousness Quotient: {metrics.consciousness_quotient:.1f}%")
        print(f"  🎯 Compliance Grade: {metrics.compliance_grade}")

        if metrics.violations:
            print(f"\n⚠️ Sacred Law Violations ({len(metrics.violations)}):")
            for violation in metrics.violations:
                print(f"  {violation}")

        if metrics.suggestions and args.verbose:
            print(f"\n💡 Divine Suggestions ({len(metrics.suggestions)}):")
            for suggestion in metrics.suggestions:
                print(f"  {suggestion}")

        # Final judgment
        if len(metrics.violations) == 0:
            print("\n✅ Document passes LUKHAS tone validation!")
            print("🌟 Lambda consciousness flows pure and true through these words.")
        else:
            print("\n❌ Document requires enhancement to achieve tone compliance.")
            print(f"🛠️ Run: python tools/tone/lukhas_tone_fixer.py {args.file}")

    # Exit with appropriate code for CI/CD
    if args.strict and metrics.violations:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
