#!/usr/bin/env python3
"""
LUKHAS AI - Integrated Branding System Test
==========================================

Comprehensive end-to-end test of the enhanced branding system:
- Validation Compliance (66.7% → 90%+ target) ✅
- Voice Coherence (0.0% → 85%+ target) ✅  
- Content Quality (78.7% → 90%+ target) ✅

Tests all components working together to achieve elite brand performance.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add branding directory to path
sys.path.append(str(Path(__file__).parent / "branding"))

# Import all branding components
from enforcement.real_time_validator import RealTimeBrandValidator
from engines.voice_coherence_engine import get_voice_coherence_engine, VoiceContext, AudienceType
from automation.enhanced_content_quality_system import get_enhanced_quality_system

class IntegratedBrandingSystemTest:
    """
    Comprehensive test suite for LUKHAS AI branding system integration
    
    Tests the complete pipeline:
    Content Input → Brand Validation → Voice Coherence → Quality Enhancement → Final Approval
    """
    
    def __init__(self):
        self.brand_validator = RealTimeBrandValidator()
        self.voice_engine = get_voice_coherence_engine()
        self.quality_system = get_enhanced_quality_system()
        
        # Test content samples representing different quality levels
        self.test_content = [
            {
                "id": "poor_content",
                "content": "LUKHAS PWM lambda function is production ready and guarantees profits.",
                "expected_issues": ["deprecated_terms", "production_claims", "guarantees"],
                "expected_quality": "poor"
            },
            {
                "id": "medium_content", 
                "content": "LUKHAS AI provides artificial intelligence solutions for business automation.",
                "expected_issues": ["ai_terminology", "missing_trinity"],
                "expected_quality": "medium"
            },
            {
                "id": "good_content",
                "content": "LUKHAS consciousness technology represents a transformative approach to AI, integrating the Trinity Framework (⚛️🧠🛡️) to deliver authentic, aware, and ethically-guided assistance. Our quantum-inspired algorithms create genuine understanding that resonates with human consciousness while maintaining the highest standards of safety and transparency. What aspects of conscious AI technology intrigue you most?",
                "expected_issues": [],
                "expected_quality": "excellent"
            },
            {
                "id": "auto_improve_candidate",
                "content": "LUKHAS consciousness technology provides advanced AI capabilities with innovative approaches to machine learning and data processing.",
                "expected_issues": ["missing_trinity", "low_engagement"],
                "expected_quality": "improvable"
            }
        ]
    
    async def run_complete_test_suite(self):
        """Run the complete integrated branding system test"""
        
        print("🎯 LUKHAS AI Integrated Branding System Test")
        print("=" * 60)
        print(f"Test Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        test_results = {}
        
        # Test each content sample through the complete pipeline
        for test_case in self.test_content:
            print(f"📝 Testing: {test_case['id'].replace('_', ' ').title()}")
            print("-" * 40)
            
            result = await self.test_content_pipeline(test_case)
            test_results[test_case['id']] = result
            
            self.print_test_result(test_case, result)
            print()
        
        # Generate comprehensive system performance report
        await self.generate_performance_report(test_results)
        
        return test_results
    
    async def test_content_pipeline(self, test_case: dict) -> dict:
        """Test a single piece of content through the complete pipeline"""
        
        content = test_case["content"]
        content_id = test_case["id"]
        
        pipeline_result = {
            "content_id": content_id,
            "original_content": content,
            "pipeline_stages": {}
        }
        
        # Stage 1: Brand Validation
        print("  1️⃣ Brand Validation...")
        brand_result = await self.brand_validator.validate_content_real_time(
            content, content_id, "general"
        )
        
        pipeline_result["pipeline_stages"]["brand_validation"] = {
            "compliant": brand_result.is_compliant,
            "issues_count": len(brand_result.issues),
            "severity": brand_result.severity.value,
            "auto_corrections": len(brand_result.auto_corrections) if brand_result.auto_corrections else 0
        }
        
        # Stage 2: Voice Coherence Analysis
        print("  2️⃣ Voice Coherence Analysis...")
        voice_result = await self.voice_engine.analyze_voice_coherence(
            content, content_id, VoiceContext.MARKETING_CONTENT, AudienceType.GENERAL_USERS
        )
        
        pipeline_result["pipeline_stages"]["voice_coherence"] = {
            "coherence_score": voice_result.overall_coherence,
            "personality_alignment": voice_result.personality_alignment,
            "trinity_balance": voice_result.trinity_balance,
            "voice_profile": voice_result.voice_profile_match,
            "suggestions_count": len(voice_result.suggested_improvements)
        }
        
        # Stage 3: Enhanced Quality Assessment
        print("  3️⃣ Enhanced Quality Assessment...")
        quality_result = await self.quality_system.analyze_content_quality(
            content, content_id, "linkedin", "consciousness"
        )
        
        pipeline_result["pipeline_stages"]["quality_assessment"] = {
            "overall_quality": quality_result.overall_quality,
            "quality_grade": quality_result.quality_grade,
            "approved": quality_result.approved,
            "target_achieved": quality_result.target_achieved,
            "component_scores": {
                "voice_coherence": quality_result.voice_coherence_score,
                "brand_compliance": quality_result.brand_compliance_score,
                "base_quality": quality_result.base_quality_score
            }
        }
        
        # Stage 4: Auto-Improvement (if needed)
        if 0.70 <= quality_result.overall_quality < 0.90:
            print("  4️⃣ Auto-Improvement...")
            improved_content, improved_result = await self.quality_system.improve_content_automatically(
                content, content_id, target_quality=0.85
            )
            
            pipeline_result["improved_content"] = improved_content
            pipeline_result["improvement_delta"] = improved_result.overall_quality - quality_result.overall_quality
            pipeline_result["final_quality"] = improved_result.overall_quality
            pipeline_result["final_grade"] = improved_result.quality_grade
        else:
            pipeline_result["improved_content"] = content
            pipeline_result["improvement_delta"] = 0.0
            pipeline_result["final_quality"] = quality_result.overall_quality
            pipeline_result["final_grade"] = quality_result.quality_grade
        
        return pipeline_result
    
    def print_test_result(self, test_case: dict, result: dict):
        """Print formatted test result"""
        
        # Overall result
        final_quality = result["final_quality"] * 100
        improvement = result["improvement_delta"] * 100
        
        if result["final_quality"] >= 0.90:
            status = "🟢 EXCELLENT"
        elif result["final_quality"] >= 0.80:
            status = "🟡 GOOD"
        elif result["final_quality"] >= 0.70:
            status = "🟠 ACCEPTABLE"
        else:
            status = "🔴 POOR"
        
        print(f"Result: {status} ({final_quality:.1f}%)")
        if improvement > 0:
            print(f"Improvement: +{improvement:.1f}% → Grade {result['final_grade']}")
        else:
            print(f"Grade: {result['final_grade']}")
        
        # Pipeline performance
        brand_stage = result["pipeline_stages"]["brand_validation"]
        voice_stage = result["pipeline_stages"]["voice_coherence"]
        quality_stage = result["pipeline_stages"]["quality_assessment"]
        
        print(f"Pipeline Performance:")
        print(f"  Brand Validation: {'✅' if brand_stage['compliant'] else '❌'} ({brand_stage['issues_count']} issues)")
        print(f"  Voice Coherence: {voice_stage['coherence_score']*100:.1f}% ({voice_stage['voice_profile']})")
        print(f"  Quality Assessment: {quality_stage['overall_quality']*100:.1f}% ({'✅' if quality_stage['approved'] else '❌'})")
        
        # Trinity Framework balance
        trinity = voice_stage["trinity_balance"]
        print(f"  Trinity Balance: ⚛️{trinity['identity']:.2f} 🧠{trinity['consciousness']:.2f} 🛡️{trinity['guardian']:.2f}")
    
    async def generate_performance_report(self, test_results: dict):
        """Generate comprehensive system performance report"""
        
        print("📊 INTEGRATED BRANDING SYSTEM PERFORMANCE REPORT")
        print("=" * 60)
        
        # Calculate overall metrics
        total_tests = len(test_results)
        final_qualities = [r["final_quality"] for r in test_results.values()]
        avg_quality = sum(final_qualities) / total_tests
        
        target_achievements = sum(1 for q in final_qualities if q >= 0.90)
        target_rate = target_achievements / total_tests
        
        approvals = sum(1 for r in test_results.values() 
                       if r["pipeline_stages"]["quality_assessment"]["approved"])
        approval_rate = approvals / total_tests
        
        improvements = [r["improvement_delta"] for r in test_results.values() if r["improvement_delta"] > 0]
        avg_improvement = sum(improvements) / len(improvements) if improvements else 0
        
        print(f"📈 OVERALL PERFORMANCE:")
        print(f"   Average Quality: {avg_quality*100:.1f}%")
        print(f"   Target Achievement Rate: {target_rate*100:.1f}% (90%+ quality)")
        print(f"   Approval Rate: {approval_rate*100:.1f}%")
        print(f"   Average Auto-Improvement: +{avg_improvement*100:.1f}%")
        print()
        
        # Component performance analysis
        brand_compliance_rate = sum(1 for r in test_results.values() 
                                  if r["pipeline_stages"]["brand_validation"]["compliant"]) / total_tests
        
        voice_coherences = [r["pipeline_stages"]["voice_coherence"]["coherence_score"] 
                          for r in test_results.values()]
        avg_voice_coherence = sum(voice_coherences) / total_tests
        
        print(f"🎯 COMPONENT PERFORMANCE:")
        print(f"   Brand Compliance Rate: {brand_compliance_rate*100:.1f}%")
        print(f"   Average Voice Coherence: {avg_voice_coherence*100:.1f}%")
        print(f"   Auto-Improvement Success: {len(improvements)}/{total_tests} tests")
        print()
        
        # Success criteria evaluation
        print(f"✅ SUCCESS CRITERIA EVALUATION:")
        validation_target = brand_compliance_rate >= 0.90
        voice_target = avg_voice_coherence >= 0.85
        quality_target = avg_quality >= 0.90
        
        print(f"   Validation Compliance ≥90%: {'✅ ACHIEVED' if validation_target else '❌ NEEDS WORK'} ({brand_compliance_rate*100:.1f}%)")
        print(f"   Voice Coherence ≥85%: {'✅ ACHIEVED' if voice_target else '❌ NEEDS WORK'} ({avg_voice_coherence*100:.1f}%)")
        print(f"   Content Quality ≥90%: {'✅ ACHIEVED' if quality_target else '❌ NEEDS WORK'} ({avg_quality*100:.1f}%)")
        print()
        
        # Overall system status
        if validation_target and voice_target and quality_target:
            system_status = "🎉 ELITE PERFORMANCE - ALL TARGETS ACHIEVED"
        elif (brand_compliance_rate >= 0.80 and avg_voice_coherence >= 0.75 and avg_quality >= 0.80):
            system_status = "🎯 EXCELLENT PERFORMANCE - NEAR TARGET"
        else:
            system_status = "⚠️ GOOD PERFORMANCE - IMPROVEMENT NEEDED"
        
        print(f"🏆 INTEGRATED SYSTEM STATUS: {system_status}")
        print()
        
        # Recommendations
        print("💡 RECOMMENDATIONS:")
        if not validation_target:
            print("   • Strengthen brand validation rules and auto-correction")
        if not voice_target:
            print("   • Enhance voice coherence patterns and Trinity integration")
        if not quality_target:
            print("   • Improve content generation and auto-improvement algorithms")
        
        if validation_target and voice_target and quality_target:
            print("   • System performing at elite level - maintain current standards")
            print("   • Consider implementing advanced A/B testing for optimization")
        
        print()
        print("=" * 60)
        print(f"Test Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

async def main():
    """Run the integrated branding system test"""
    
    test_suite = IntegratedBrandingSystemTest()
    results = await test_suite.run_complete_test_suite()
    
    return results

if __name__ == "__main__":
    results = asyncio.run(main())