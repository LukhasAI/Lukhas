#!/usr/bin/env python3
"""
LUKHAS AI Voice Coherence Analyzer
Analyzes existing content for voice coherence and brand alignment across content creation systems
Measures progression toward elite 85%+ voice coherence targets
"""

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class VoiceCoherenceLevel(Enum):
    """Voice coherence quality levels"""

    POOR = "poor"  # <60% - Needs major improvement
    FAIR = "fair"  # 60-70% - Requires enhancement
    GOOD = "good"  # 70-80% - Acceptable quality
    EXCELLENT = "excellent"  # 80-85% - High quality
    ELITE = "elite"  # >85% - Market leadership level


class ContentType(Enum):
    """Types of content to analyze"""

    BLOG_POST = "blog_post"
    LANDING_PAGE = "landing_page"
    TECHNICAL_DOC = "technical_doc"
    SOCIAL_MEDIA = "social_media"
    MARKETING_COPY = "marketing_copy"
    API_DOCUMENTATION = "api_documentation"


@dataclass
class CoherenceMetrics:
    """Voice coherence measurement metrics"""

    brand_terminology_score: float = 0.0  # Use of approved LUKHAS terms
    trinity_framework_score: float = 0.0  # ⚛️🧠🛡️ integration
    consciousness_tech_score: float = 0.0  # Consciousness technology focus
    tone_consistency_score: float = 0.0  # 3-Layer tone system adherence
    founder_authority_score: float = 0.0  # Founder-led positioning
    premium_positioning_score: float = 0.0  # Elite brand positioning

    @property
    def overall_coherence(self) -> float:
        """Calculate overall voice coherence percentage"""
        scores = [
            self.brand_terminology_score,
            self.trinity_framework_score,
            self.consciousness_tech_score,
            self.tone_consistency_score,
            self.founder_authority_score,
            self.premium_positioning_score,
        ]
        return sum(scores) / len(scores) * 100


@dataclass
class ContentAnalysis:
    """Complete analysis of a content piece"""

    content_path: str
    content_type: ContentType
    coherence_metrics: CoherenceMetrics
    coherence_level: VoiceCoherenceLevel
    word_count: int
    brand_violations: list[str]
    improvement_suggestions: list[str]
    elite_brand_readiness: float
    analysis_timestamp: str


class VoiceCoherenceAnalyzer:
    """
    Analyzes content for voice coherence and brand alignment
    Measures progress toward elite brand standards
    """

    def __init__(self):
        self.brand_keywords = self._load_brand_keywords()
        self.trinity_symbols = [
            "⚛️",
            "🧠",
            "🛡️",
            "Trinity Framework",
            "Identity",
            "Consciousness",
            "Guardian",
        ]
        self.consciousness_terms = [
            "consciousness technology",
            "digital consciousness",
            "AI consciousness",
            "consciousness awakening",
            "conscious AI",
            "consciousness awareness",
            "quantum-inspired",
            "bio-inspired",
            "neural processing",
        ]
        self.prohibited_terms = [
            "LUKHAS AGI",
            "quantum processing",
            "bio processes",
            "production-ready",
            "price prediction",
            "revenue forecast",
        ]
        self.founder_indicators = [
            "founder",
            "vision",
            "pioneering",
            "breakthrough",
            "innovation",
            "leadership",
            "thought leader",
            "industry pioneer",
        ]

    def _load_brand_keywords(self) -> dict[str, list[str]]:
        """Load approved brand terminology"""
        return {
            "core_brand": [
                "LUKHAS AI",
                "Lambda",
                "Trinity Framework",
                "consciousness technology",
                "elite brand",
                "premium positioning",
                "market leadership",
            ],
            "technical": [
                "quantum-inspired",
                "bio-inspired",
                "consciousness architecture",
                "voice coherence",
                "brand validation",
                "symbolic processing",
            ],
            "positioning": [
                "thought leadership",
                "consciousness pioneer",
                "digital awakening",
                "premium experience",
                "market differentiation",
            ],
        }

    def analyze_content(self, content_path: str, content: str, content_type: ContentType) -> ContentAnalysis:
        """Analyze content for voice coherence and brand alignment"""

        # Calculate coherence metrics
        metrics = self._calculate_coherence_metrics(content)

        # Determine coherence level
        coherence_level = self._determine_coherence_level(metrics.overall_coherence)

        # Find brand violations
        violations = self._find_brand_violations(content)

        # Generate improvement suggestions
        suggestions = self._generate_improvement_suggestions(content, metrics)

        # Calculate elite brand readiness
        readiness = self._calculate_elite_readiness(metrics)

        return ContentAnalysis(
            content_path=content_path,
            content_type=content_type,
            coherence_metrics=metrics,
            coherence_level=coherence_level,
            word_count=len(content.split()),
            brand_violations=violations,
            improvement_suggestions=suggestions,
            elite_brand_readiness=readiness,
            analysis_timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def _calculate_coherence_metrics(self, content: str) -> CoherenceMetrics:
        """Calculate detailed voice coherence metrics"""
        content_lower = content.lower()

        # Brand terminology score
        brand_score = self._calculate_brand_terminology_score(content_lower)

        # Trinity Framework integration
        trinity_score = self._calculate_trinity_score(content)

        # Consciousness technology focus
        consciousness_score = self._calculate_consciousness_score(content_lower)

        # Tone consistency
        tone_score = self._calculate_tone_consistency_score(content)

        # Founder authority positioning
        founder_score = self._calculate_founder_authority_score(content_lower)

        # Premium positioning
        premium_score = self._calculate_premium_positioning_score(content)

        return CoherenceMetrics(
            brand_terminology_score=brand_score,
            trinity_framework_score=trinity_score,
            consciousness_tech_score=consciousness_score,
            tone_consistency_score=tone_score,
            founder_authority_score=founder_score,
            premium_positioning_score=premium_score,
        )

    def _calculate_brand_terminology_score(self, content: str) -> float:
        """Calculate adherence to brand terminology standards"""
        total_keywords = sum(len(keywords) for keywords in self.brand_keywords.values())
        found_keywords = 0

        for keywords in self.brand_keywords.values():
            for keyword in keywords:
                if keyword.lower() in content:
                    found_keywords += 1

        return min(found_keywords / total_keywords, 1.0)

    def _calculate_trinity_score(self, content: str) -> float:
        """Calculate Trinity Framework (⚛️🧠🛡️) integration score"""
        trinity_mentions = 0

        for symbol in self.trinity_symbols:
            if symbol in content:
                trinity_mentions += 1

        # Perfect score if mentions Trinity Framework concept
        if "trinity framework" in content.lower():
            trinity_mentions += 2

        return min(trinity_mentions / 5.0, 1.0)  # Max 5 possible mentions

    def _calculate_consciousness_score(self, content: str) -> float:
        """Calculate consciousness technology focus score"""
        consciousness_mentions = 0

        for term in self.consciousness_terms:
            if term in content:
                consciousness_mentions += content.count(term)

        # Score based on frequency and word count
        word_count = len(content.split())
        consciousness_density = consciousness_mentions / max(word_count / 100, 1)

        return min(consciousness_density, 1.0)

    def _calculate_tone_consistency_score(self, content: str) -> float:
        """Calculate 3-Layer tone system consistency"""
        # Check for poetic elements (metaphors, inspiring language)
        poetic_indicators = ["awakening", "transcend", "emerge", "evolve", "breakthrough"]
        poetic_score = sum(1 for indicator in poetic_indicators if indicator in content.lower()) / len(
            poetic_indicators
        )

        # Check for user-friendly language (accessible, conversational)
        friendly_indicators = ["you", "your", "we", "simple", "easy", "understand"]
        friendly_score = sum(1 for indicator in friendly_indicators if indicator in content.lower()) / len(
            friendly_indicators
        )

        # Check for academic precision (technical, detailed)
        academic_indicators = [
            "architecture",
            "framework",
            "implementation",
            "optimization",
            "analysis",
        ]
        academic_score = sum(1 for indicator in academic_indicators if indicator in content.lower()) / len(
            academic_indicators
        )

        # Balanced tone across layers
        return (poetic_score + friendly_score + academic_score) / 3

    def _calculate_founder_authority_score(self, content: str) -> float:
        """Calculate founder-led authority positioning score"""
        founder_mentions = 0

        for indicator in self.founder_indicators:
            if indicator in content:
                founder_mentions += 1

        # Bonus for direct founder positioning
        if any(phrase in content for phrase in ["founder", "ceo", "visionary", "pioneer"]):
            founder_mentions += 2

        return min(founder_mentions / 8.0, 1.0)  # Max 8 possible indicators

    def _calculate_premium_positioning_score(self, content: str) -> float:
        """Calculate premium/elite brand positioning score"""
        premium_indicators = [
            "premium",
            "elite",
            "excellence",
            "superior",
            "advanced",
            "cutting-edge",
            "industry-leading",
            "best-in-class",
            "revolutionary",
        ]

        premium_mentions = sum(1 for indicator in premium_indicators if indicator in content.lower())

        # Check for Apple/OpenAI-level language
        if any(phrase in content.lower() for phrase in ["seamless", "intuitive", "elegant", "sophisticated"]):
            premium_mentions += 2

        return min(premium_mentions / 10.0, 1.0)

    def _determine_coherence_level(self, coherence_percentage: float) -> VoiceCoherenceLevel:
        """Determine voice coherence quality level"""
        if coherence_percentage >= 85:
            return VoiceCoherenceLevel.ELITE
        elif coherence_percentage >= 80:
            return VoiceCoherenceLevel.EXCELLENT
        elif coherence_percentage >= 70:
            return VoiceCoherenceLevel.GOOD
        elif coherence_percentage >= 60:
            return VoiceCoherenceLevel.FAIR
        else:
            return VoiceCoherenceLevel.POOR

    def _find_brand_violations(self, content: str) -> list[str]:
        """Find violations of brand standards"""
        violations = []

        for term in self.prohibited_terms:
            if term in content:
                violations.append(f"Prohibited term used: '{term}'")

        # Check for unapproved terminology
        if "LUKHAS AGI" in content:
            violations.append("Use 'LUKHAS AI' instead of 'LUKHAS AGI'")

        if "quantum processing" in content:
            violations.append("Use 'quantum-inspired' instead of 'quantum processing'")

        if "bio processes" in content:
            violations.append("Use 'bio-inspired' instead of 'bio processes'")

        return violations

    def _generate_improvement_suggestions(self, content: str, metrics: CoherenceMetrics) -> list[str]:
        """Generate specific improvement suggestions"""
        suggestions = []

        if metrics.brand_terminology_score < 0.7:
            suggestions.append("Increase use of approved LUKHAS AI brand terminology")

        if metrics.trinity_framework_score < 0.5:
            suggestions.append("Integrate Trinity Framework (⚛️🧠🛡️) concepts and symbols")

        if metrics.consciousness_tech_score < 0.6:
            suggestions.append("Emphasize consciousness technology focus and benefits")

        if metrics.tone_consistency_score < 0.7:
            suggestions.append("Balance 3-Layer Tone System: poetic, user-friendly, academic")

        if metrics.founder_authority_score < 0.5:
            suggestions.append("Include founder-led positioning and thought leadership elements")

        if metrics.premium_positioning_score < 0.6:
            suggestions.append("Enhance premium/elite brand positioning language")

        return suggestions

    def _calculate_elite_readiness(self, metrics: CoherenceMetrics) -> float:
        """Calculate readiness for elite brand deployment"""
        # Weight different metrics for elite readiness
        weights = {
            "brand_terminology": 0.2,
            "trinity_framework": 0.15,
            "consciousness_tech": 0.2,
            "tone_consistency": 0.15,
            "founder_authority": 0.15,
            "premium_positioning": 0.15,
        }

        readiness = (
            metrics.brand_terminology_score * weights["brand_terminology"]
            + metrics.trinity_framework_score * weights["trinity_framework"]
            + metrics.consciousness_tech_score * weights["consciousness_tech"]
            + metrics.tone_consistency_score * weights["tone_consistency"]
            + metrics.founder_authority_score * weights["founder_authority"]
            + metrics.premium_positioning_score * weights["premium_positioning"]
        ) * 100

        return readiness

    def analyze_content_system(self, system_path: str, system_name: str) -> dict[str, Any]:
        """Analyze entire content creation system for voice coherence"""
        system_analysis = {
            "system_name": system_name,
            "system_path": system_path,
            "content_analyses": [],
            "system_metrics": {},
            "readiness_assessment": {},
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Find and analyze all content files
        content_files = self._find_content_files(system_path)

        coherence_scores = []

        for file_path in content_files:
            try:
                with open(file_path, encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Determine content type
                content_type = self._determine_content_type(file_path)

                # Analyze content
                analysis = self.analyze_content(str(file_path), content, content_type)
                system_analysis["content_analyses"].append(analysis.__dict__)

                coherence_scores.append(analysis.coherence_metrics.overall_coherence)

            except Exception as e:
                print(f"Error in voice coherence analysis: {e}")

        # Calculate system-wide metrics
        if coherence_scores:
            system_analysis["system_metrics"] = {
                "average_coherence": sum(coherence_scores) / len(coherence_scores),
                "max_coherence": max(coherence_scores),
                "min_coherence": min(coherence_scores),
                "total_content_pieces": len(coherence_scores),
                "elite_ready_percentage": len([s for s in coherence_scores if s >= 85]) / len(coherence_scores) * 100,
            }

            # Readiness assessment
            avg_coherence = system_analysis["system_metrics"]["average_coherence"]
            system_analysis["readiness_assessment"] = {
                "current_level": self._determine_coherence_level(avg_coherence).value,
                "elite_gap": max(0, 85 - avg_coherence),
                "deployment_ready": avg_coherence >= 85,
                "priority_level": "high" if avg_coherence < 70 else "medium" if avg_coherence < 80 else "low",
            }

        return system_analysis

    def _find_content_files(self, system_path: str) -> list[Path]:
        """Find all content files in a system directory"""
        content_extensions = [".md", ".html", ".txt", ".py"]  # Add Python for docstrings
        content_files = []

        try:
            for root, _dirs, files in os.walk(system_path):
                for file in files:
                    if any(file.endswith(ext) for ext in content_extensions):
                        file_path = Path(root) / file
                        # Skip very large files (>1MB)
                        if file_path.stat().st_size < 1024 * 1024:
                            content_files.append(file_path)
        except Exception as e:
            print(f"Error scanning content files: {e}")

        return content_files[:20]  # Limit to 20 files per system for performance

    def _determine_content_type(self, file_path: str) -> ContentType:
        """Determine content type from file path and name"""
        file_path_lower = str(file_path).lower()

        if "blog" in file_path_lower or "post" in file_path_lower:
            return ContentType.BLOG_POST
        elif "landing" in file_path_lower or "index.html" in file_path_lower:
            return ContentType.LANDING_PAGE
        elif "api" in file_path_lower and ("doc" in file_path_lower or ".md" in file_path_lower):
            return ContentType.API_DOCUMENTATION
        elif "social" in file_path_lower or "twitter" in file_path_lower or "linkedin" in file_path_lower:
            return ContentType.SOCIAL_MEDIA
        elif "marketing" in file_path_lower or "copy" in file_path_lower:
            return ContentType.MARKETING_COPY
        else:
            return ContentType.TECHNICAL_DOC

    def generate_coherence_report(self, analyses: list[dict[str, Any]]) -> str:
        """Generate comprehensive voice coherence report"""
        report = []
        report.append("# 🎯 LUKHAS AI Voice Coherence Analysis Report")
        report.append("")
        report.append("*Elite Brand Integration Assessment*")
        report.append("")
        report.append("---")
        report.append("")

        # Overall summary
        total_systems = len(analyses)
        elite_ready_systems = len(
            [a for a in analyses if a.get("readiness_assessment", {}).get("deployment_ready", False)]
        )

        report.append("## 📊 Executive Summary")
        report.append("")
        report.append(f"**Total Content Systems Analyzed**: {total_systems}")
        report.append(
            f"**Elite Brand Ready**: {elite_ready_systems}/{total_systems} ({elite_ready_systems / total_systems  * 100:.1f}%)"
        )
        report.append("")

        # System-by-system analysis
        for analysis in analyses:
            system_name = analysis["system_name"]
            metrics = analysis.get("system_metrics", {})
            readiness = analysis.get("readiness_assessment", {})

            report.append(f"### {system_name}")
            report.append("")

            if metrics:
                avg_coherence = metrics.get("average_coherence", 0)
                coherence_level = self._determine_coherence_level(avg_coherence)

                report.append(f"**Voice Coherence**: {avg_coherence:.1f}% ({coherence_level.value.title()})")
                report.append(f"**Elite Gap**: {readiness.get('elite_gap', 0):.1f} percentage points")
                report.append(f"**Content Pieces**: {metrics.get('total_content_pieces', 0)}")
                report.append(f"**Priority**: {readiness.get('priority_level', 'unknown').title()}")
                report.append("")

                # Elite readiness indicator
                if readiness.get("deployment_ready", False):
                    report.append("✅ **ELITE BRAND READY** - Ready for deployment")
                else:
                    report.append(f"🔄 **UPGRADE REQUIRED** - {readiness.get('elite_gap', 0):.1f}% improvement needed")

                report.append("")

            report.append("---")
            report.append("")

        # Deployment recommendations
        report.append("## 🚀 Deployment Recommendations")
        report.append("")

        high_priority = [a for a in analyses if a.get("readiness_assessment", {}).get("priority_level") == "high"]
        medium_priority = [a for a in analyses if a.get("readiness_assessment", {}).get("priority_level") == "medium"]

        if high_priority:
            report.append("### High Priority (Immediate Attention)")
            for analysis in high_priority:
                report.append(f"- **{analysis['system_name']}**: Major voice coherence upgrade required")
            report.append("")

        if medium_priority:
            report.append("### Medium Priority (Phase 2 Integration)")
            for analysis in medium_priority:
                report.append(f"- **{analysis['system_name']}**: Moderate improvements needed")
            report.append("")

        # Target achievement pathway
        report.append("## 🎯 Elite Brand Achievement Pathway")
        report.append("")
        report.append("1. **Phase 1** (Days 1-3): Upgrade high-priority systems to 70%+ coherence")
        report.append("2. **Phase 2** (Days 4-7): Enhance medium-priority systems to 80%+ coherence")
        report.append("3. **Phase 3** (Days 8-14): Achieve 85%+ elite coherence across all systems")
        report.append("")

        report.append("---")
        report.append("")
        report.append("*Analysis generated by LUKHAS AI Voice Coherence Analyzer*")
        report.append(f"*Report generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}*")

        return "\n".join(report)


def main():
    """Run voice coherence analysis on LUKHAS content systems"""
    analyzer = VoiceCoherenceAnalyzer()

    # Define content systems to analyze
    content_systems = [
        {
            "name": "ΛUCTOR Content Engine",
            "path": "/Users/agi_dev/LOCAL-REPOS/Lukhas/lambda_products_pack/auctor",
        },
        {"name": "ΛBot System", "path": "/Users/agi_dev/LOCAL-REPOS/AI-Consolidation-Repo"},
        {"name": "Lucas Knowledge Base", "path": "/Users/agi_dev/LOCAL-REPOS/auctor"},
        {"name": "LUKHAS Core Branding", "path": "/Users/agi_dev/LOCAL-REPOS/Lukhas/branding"},
    ]

    analyses = []

    print("🎯 Starting LUKHAS AI Voice Coherence Analysis...")
    print("=" * 60)

    for system in content_systems:
        print(f"\n📊 Analyzing {system['name']}...")

        try:
            analysis = analyzer.analyze_content_system(system["path"], system["name"])
            analyses.append(analysis)

            # Quick summary
            metrics = analysis.get("system_metrics", {})
            if metrics:
                coherence = metrics.get("average_coherence", 0)
                ready = analysis.get("readiness_assessment", {}).get("deployment_ready", False)
                print(f"   Voice Coherence: {coherence:.1f}%")
                print(f"   Elite Ready: {'✅ Yes' if ready else '🔄 No'}")

        except Exception as e:
            print(f"   ❌ Error: {e}")

    # Generate report
    print("\n📝 Generating comprehensive report...")
    report = analyzer.generate_coherence_report(analyses)

    # Save report
    report_path = "/Users/agi_dev/LOCAL-REPOS/Lukhas/branding/analysis/VOICE_COHERENCE_REPORT.md"
    with open(report_path, "w") as f:
        f.write(report)

    # Save detailed analysis
    analysis_path = "/Users/agi_dev/LOCAL-REPOS/Lukhas/branding/analysis/voice_coherence_analysis.json"
    with open(analysis_path, "w") as f:
        json.dump(analyses, f, indent=2, default=str)

    print("✅ Analysis complete!")
    print(f"📊 Report saved: {report_path}")
    print(f"📁 Data saved: {analysis_path}")


if __name__ == "__main__":
    main()
